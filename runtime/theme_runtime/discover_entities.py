"""
discover_entities - find entity slugs in claims that aren't yet defined in
trend-corpus/trends/<theme>/entities/, and draft new entity YAMLs via
Claude.

Output: draft YAML files at /tmp/trt-discover/<theme>/ent_<slug>.yaml.
The operator reviews and commits the keeper drafts into trend-corpus by
hand; nothing is auto-merged.

Read-only on the live db. Read-only on the trend-corpus checkout. Only
side-effect is the temp draft files.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

from .claude_cli import AuthError, run_claude
from .context import ThemeContext
from .db import connect

DRAFTS_ROOT = Path("/tmp/trt-discover")
ENTITY_SLUG_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def _gather_known_slugs(theme_dir: Path) -> set[str]:
    """Read trend-corpus/trends/<theme>/entities/*.yaml and collect their slugs."""
    if yaml is None or not theme_dir.is_dir():
        return set()
    known: set[str] = set()
    for path in (theme_dir / "entities").glob("*.yaml"):
        try:
            d = yaml.safe_load(path.read_text()) or {}
        except Exception:
            continue
        slug = d.get("slug")
        if not slug:
            obj_id = d.get("id", "")
            if obj_id.startswith("ent_"):
                slug = obj_id[len("ent_") :]
        if slug:
            known.add(str(slug).strip().lower())
    return known


def _seen_slugs_from_db(db_path: Path) -> set[str]:
    """Pull all distinct entity slugs from active claims."""
    conn = connect(db_path)
    try:
        rows = conn.execute(
            "SELECT entities FROM claims WHERE superseded_by IS NULL"
        ).fetchall()
    finally:
        conn.close()
    seen: set[str] = set()
    for (entities_json,) in rows:
        try:
            arr = json.loads(entities_json or "[]")
        except Exception:
            continue
        if not isinstance(arr, list):
            continue
        for slug in arr:
            if isinstance(slug, str) and slug.strip():
                seen.add(slug.strip().lower())
    return seen


def _build_prompt(slugs: list[str], theme_id: str) -> str:
    """Build a single Claude prompt that asks for entity info on N slugs."""
    return f"""You are helping classify entity slugs that appeared in claims about
the {theme_id} sector but are not yet defined in our public entity list.

For each slug below, decide whether the entity is a PUBLIC TRADABLE
COMPANY. If yes, return its primary ticker, exchange, and a one-line
role in the sector. If no, return type ('regulator', 'private_company',
'government_agency', 'industry_group', 'individual', 'other') and a
one-line note.

Output: JSONL, one object per slug. No preamble, no postamble, no code
fences.

Each JSON object must have exactly these fields:
  {{
    "slug": "<the slug>",
    "tradable": <bool>,
    "ticker": "<symbol or null>",
    "exchange": "<NYSE|NASDAQ|TSX|SIX|LSE|TWSE|OSE|HKEX|null>",
    "entity_type": "<one of: public_company, regulator, private_company, government_agency, industry_group, individual, other>",
    "name": "<company or entity legal name>",
    "role": "<short phrase describing role in {theme_id}>",
    "confidence": <float 0-1>
  }}

Use confidence < 0.5 if you cannot find a reliable answer; the operator
will discard low-confidence rows.

SLUGS TO CLASSIFY:
{chr(10).join('  - ' + s for s in slugs)}
"""


def _parse_drafts(output: str) -> list[dict]:
    drafts: list[dict] = []
    for line in output.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        if "slug" not in obj:
            continue
        drafts.append(obj)
    return drafts


def _draft_to_yaml(draft: dict, theme_id: str) -> str:
    """Turn a draft dict into the trend-corpus entity YAML shape."""
    slug = str(draft["slug"]).strip().lower()
    out: dict[str, Any] = {
        "id": f"ent_{slug}",
        "name": draft.get("name") or slug.replace("_", " ").title(),
        "entity_type": draft.get("entity_type") or "other",
        "schema_version": 1,
        "slug": slug,
    }
    ticker = draft.get("ticker") if draft.get("tradable") else None
    if ticker and isinstance(ticker, str) and ticker not in ("null", ""):
        exchange = draft.get("exchange") or ""
        out["identifiers"] = {"ticker": ticker, "exchange": exchange}
        out["ticker_exposures"] = [
            {
                "ticker": ticker,
                "direction": "ambiguous",
                "exposure_strength": 0.5,
                "basis": ["other"],
                "tradable": True,
            }
        ]
        out["tickers"] = [ticker]
        if exchange:
            out["exchanges"] = [exchange]
    out["notes"] = (
        f"Auto-drafted by theme_runtime discover-entities. "
        f"Role: {draft.get('role', '(unspecified)')}. "
        f"Confidence: {draft.get('confidence', 'n/a')}. "
        f"REVIEW BEFORE COMMITTING."
    )
    return yaml.safe_dump(out, sort_keys=False)


def run(
    ctx: ThemeContext,
    trend_corpus_root: Path,
    model: str | None = None,
) -> dict[str, Any]:
    """Discover entity slugs not in trend-corpus/trends/<theme>/entities/."""
    if yaml is None:
        raise RuntimeError("PyYAML is required for discover-entities")
    root = Path(trend_corpus_root).expanduser().resolve()
    theme_dir = root / "trends" / ctx.theme_id
    known = _gather_known_slugs(theme_dir)
    seen = _seen_slugs_from_db(ctx.db_path)
    # Filter to well-formed slugs the entity schema can accept
    unknown = sorted(
        s for s in (seen - known) if ENTITY_SLUG_RE.match(s)
    )
    print(
        f"discover-entities({ctx.theme_id}): "
        f"known={len(known)} seen={len(seen)} unknown={len(unknown)}"
    )
    if not unknown:
        return {
            "theme_id": ctx.theme_id,
            "unknown_count": 0,
            "drafts": [],
            "drafts_dir": None,
        }
    drafts_dir = DRAFTS_ROOT / ctx.theme_id
    drafts_dir.mkdir(parents=True, exist_ok=True)
    prompt = _build_prompt(unknown, ctx.theme_id)
    chosen_model = model or ctx.extract_model
    try:
        output = run_claude(prompt, model=chosen_model, timeout=300)
    except AuthError as e:
        print(f"\nFATAL: {e}", file=sys.stderr)
        sys.exit(2)
    except (subprocess.TimeoutExpired, RuntimeError) as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(3)
    drafts = _parse_drafts(output)
    written_paths: list[str] = []
    for d in drafts:
        slug = str(d.get("slug", "")).strip().lower()
        if not slug or not ENTITY_SLUG_RE.match(slug):
            continue
        body = _draft_to_yaml(d, ctx.theme_id)
        path = drafts_dir / f"ent_{slug}.yaml"
        path.write_text(body)
        written_paths.append(str(path))
    summary = {
        "theme_id": ctx.theme_id,
        "unknown_count": len(unknown),
        "unknown_slugs": unknown,
        "drafts": written_paths,
        "drafts_dir": str(drafts_dir),
    }
    print(
        f"discover-entities({ctx.theme_id}): "
        f"wrote {len(written_paths)} drafts to {drafts_dir}"
    )
    return summary
