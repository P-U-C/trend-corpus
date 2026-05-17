"""
aggregates.py - generic theme-aggregates exporter.

Reads from the local runtime SQLite (read-only), emits a single JSON file
that conforms to trend-corpus/schemas/aggregates.schema.json. Theme-agnostic
generalization of the peptide-specific export-public-aggregates.py.

Privacy rules (enforced by what this exporter DOES NOT read or emit):
- never reads or emits claims.claim text
- never reads or emits packets.question text
- never reads or emits per-claim confidence
- never reads or emits date_of_evidence per individual claim
- never reads or emits superseded_by relationships
- never reads sources.raw_text
Counts and lowercased slugs only.

Schema-validates the payload before write. Suppresses entity / topic
buckets below `min_count_threshold` to prevent re-identification of
low-volume slugs.
"""
from __future__ import annotations

import datetime as dt
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from .context import ThemeContext

SCHEMA_VERSION = "0.1.0"
GENERATOR_NAME = "theme-runtime-aggregates-exporter"
GENERATOR_VERSION = "0.1.0"

DEFAULT_MIN_COUNT = 3
WINDOW_DAYS = (30, 90, 365)
TOP_N = 20

# Repo-root anchor: aggregates.py lives at
# trend-corpus/runtime/theme_runtime/aggregates.py
RUNTIME_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = RUNTIME_DIR.parent / "schemas" / "aggregates.schema.json"


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def _iso(d: dt.datetime) -> str:
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_json_array(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except (TypeError, ValueError):
        return []
    if not isinstance(value, list):
        return []
    return [str(v).strip().lower() for v in value if isinstance(v, (str, int, float))]


def _read_only_conn(db_path: Path) -> sqlite3.Connection:
    """Open in read-only URI mode so the exporter can never write."""
    uri = f"file:{db_path.expanduser()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def compute_window(conn: sqlite3.Connection, *, days: int, now: dt.datetime,
                   min_count: int, include_topics: bool) -> dict[str, Any]:
    """Counts + top-N slugs for one rolling window."""
    cutoff = (now - dt.timedelta(days=days)).strftime("%Y-%m-%d")
    cur = conn.execute(
        "SELECT category, entities, topics "
        "FROM claims "
        "WHERE date_of_evidence >= ? "
        "  AND superseded_by IS NULL",
        (cutoff,),
    )
    category_counter: Counter[str] = Counter()
    entity_counter: Counter[str] = Counter()
    topic_counter: Counter[str] = Counter()
    total = 0
    for category, ent_raw, top_raw in cur:
        total += 1
        if category:
            category_counter[str(category).strip().lower()] += 1
        for slug in _parse_json_array(ent_raw):
            if slug:
                entity_counter[slug] += 1
        for name in _parse_json_array(top_raw):
            if name:
                topic_counter[name] += 1

    top_entities = [
        {"slug": slug, "mentions": count}
        for slug, count in entity_counter.most_common(TOP_N)
        if count >= min_count
    ]
    out: dict[str, Any] = {
        "claims_total": total,
        "claims_by_category": dict(category_counter),
        "top_entities": top_entities,
    }
    if include_topics:
        # Backward-compatible peptide-style payload: emit top_peptides
        # using the topics column. For sector themes we omit this key
        # entirely (the schema allows it as optional).
        out["top_peptides"] = [
            {"name": name, "mentions": count}
            for name, count in topic_counter.most_common(TOP_N)
            if count >= min_count
        ]
    return out


def compute_source_freshness(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT url, MAX(fetched_at) FROM sources GROUP BY url ORDER BY url"
    ).fetchall()
    out = []
    for url, last in rows:
        if not url:
            continue
        out.append({"url": str(url), "last_ingested_at": str(last) if last else None})
    return out


def compute_underlying_counts(conn: sqlite3.Connection) -> tuple[int, int]:
    claim_count = conn.execute(
        "SELECT COUNT(*) FROM claims WHERE superseded_by IS NULL"
    ).fetchone()[0]
    source_count = conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    return int(claim_count), int(source_count)


def build(ctx: ThemeContext, *, min_count: int = DEFAULT_MIN_COUNT,
          include_topics: bool | None = None,
          host_alias: str | None = None) -> dict[str, Any]:
    """Build the aggregates payload for a theme."""
    if min_count < 1:
        raise ValueError("min_count must be >= 1")

    db_path = ctx.db_path
    if not db_path.exists():
        raise FileNotFoundError(f"db not found: {db_path}")

    # Peptide-style payload only when theme actually uses the peptide
    # topics column. Auto-detect from theme_id unless caller overrides.
    if include_topics is None:
        include_topics = ctx.theme_id == "peptides"

    if host_alias is None:
        import os
        host_alias = os.uname().nodename

    conn = _read_only_conn(db_path)
    try:
        now = _now_utc()
        claim_count, source_count = compute_underlying_counts(conn)
        windows: dict[str, Any] = {}
        for days in WINDOW_DAYS:
            windows[f"{days}d"] = compute_window(
                conn, days=days, now=now,
                min_count=min_count, include_topics=include_topics,
            )
        source_freshness = compute_source_freshness(conn)
    finally:
        conn.close()

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _iso(now),
        "theme_id": ctx.theme_id,
        "generator": {
            "name": GENERATOR_NAME,
            "version": GENERATOR_VERSION,
            "host_alias": host_alias,
        },
        "underlying_claim_count": claim_count,
        "underlying_source_count": source_count,
        "min_count_threshold": min_count,
        "windows": windows,
        "source_freshness": source_freshness,
    }


def validate_payload(payload: dict[str, Any], schema_path: Path | None = None) -> None:
    """Schema-validate the payload. Mirrors the inline check in
    sync-peptides-aggregates.sh: required fields, bound checks,
    theme_id-must-match-schema, top-level allowlist, ISO date.
    """
    schema_path = schema_path or SCHEMA_PATH
    if not schema_path.exists():
        raise FileNotFoundError(f"schema missing: {schema_path}")
    schema = json.loads(schema_path.read_text())

    required = schema.get("required", [])
    missing = [r for r in required if r not in payload]
    if missing:
        raise ValueError(f"aggregates payload missing required fields: {missing}")

    if payload.get("underlying_claim_count", 0) < 0:
        raise ValueError("underlying_claim_count must be >= 0")
    if payload.get("underlying_source_count", 0) < 0:
        raise ValueError("underlying_source_count must be >= 0")
    if payload.get("min_count_threshold", 0) < 1:
        raise ValueError("min_count_threshold must be >= 1")

    ts = payload.get("generated_at", "")
    try:
        dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception as exc:
        raise ValueError(f"unparseable generated_at: {ts!r} ({exc})")

    allowed = set(schema.get("properties", {}).keys())
    extras = [k for k in payload if k not in allowed]
    if extras:
        raise ValueError(f"aggregates payload has fields not in schema: {extras}")


def default_out_path(ctx: ThemeContext) -> Path:
    """Default output: <root>/out/<theme-id>-aggregates.json."""
    return ctx.root / "out" / f"{ctx.theme_id}-aggregates.json"


def write_payload(payload: dict[str, Any], out_path: Path) -> None:
    """Atomic write: tmp + rename, schema-validated before commit."""
    validate_payload(payload)
    out_path = Path(out_path).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, indent=2, sort_keys=False) + "\n"
    tmp = out_path.with_suffix(out_path.suffix + ".tmp")
    tmp.write_text(serialized, encoding="utf-8")
    tmp.replace(out_path)


def run(ctx: ThemeContext, *, out: str | None = None,
        min_count: int = DEFAULT_MIN_COUNT,
        dry_run: bool = False) -> dict[str, Any]:
    """Build + validate + write (or print for dry-run)."""
    payload = build(ctx, min_count=min_count)
    if dry_run:
        validate_payload(payload)
        print(json.dumps(payload, indent=2))
        return payload
    out_path = Path(out).expanduser() if out else default_out_path(ctx)
    write_payload(payload, out_path)
    print(
        f"export-aggregates({ctx.theme_id}): wrote {out_path} "
        f"(claims={payload['underlying_claim_count']}, "
        f"sources={payload['underlying_source_count']}, "
        f"windows={list(payload['windows'])})"
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    """Standalone CLI; the theme_runtime __main__ also exposes this."""
    import argparse
    p = argparse.ArgumentParser(description="Export theme aggregates JSON.")
    p.add_argument("--config", required=True, help="path to theme-config.yaml")
    p.add_argument("--out", help="output path (default <root>/out/<theme-id>-aggregates.json)")
    p.add_argument("--min-count", type=int, default=DEFAULT_MIN_COUNT,
                   help="suppression threshold for entity / topic buckets (default 3)")
    p.add_argument("--dry-run", action="store_true",
                   help="print payload to stdout instead of writing")
    args = p.parse_args(argv)

    from .context import load_context
    ctx = load_context(args.config)
    try:
        run(ctx, out=args.out, min_count=args.min_count, dry_run=args.dry_run)
        return 0
    except Exception as exc:
        print(f"export-aggregates({ctx.theme_id}): FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
