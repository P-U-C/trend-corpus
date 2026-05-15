"""
extract - process unprocessed sources through Claude CLI, insert claims.

Reads prompts/extract.md from the theme's runtime root and feeds each
unprocessed source text into it. Tolerant of stray text in the LLM
output; only well-formed JSON objects with the minimal required fields
are kept.
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from datetime import datetime

from .claude_cli import AuthError, run_claude
from .context import ThemeContext
from .db import connect


def _load_prompt(ctx: ThemeContext) -> str:
    path = ctx.prompts_dir / "extract.md"
    if not path.exists():
        raise FileNotFoundError(f"extract prompt not found: {path}")
    return path.read_text()


def _parse_claims(output: str) -> list[dict]:
    """Parse JSONL output, tolerating blank lines and stray text."""
    claims: list[dict] = []
    for line in output.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not all(k in obj for k in ("claim", "category", "date_of_evidence")):
            continue
        claims.append(obj)
    return claims


def _topics_field(obj: dict) -> list:
    """Accept either 'topics' (new generic) or 'peptides' (legacy) array."""
    if "topics" in obj:
        return obj.get("topics") or []
    return obj.get("peptides") or []


def _insert_claim(db, source_id: int, obj: dict, ctx: ThemeContext) -> None:
    half_life = int(obj.get("half_life_days", ctx.half_life_defaults.get(obj["category"], 90)))
    db.execute(
        "INSERT INTO claims (source_id, claim, category, entities, topics, "
        " date_of_evidence, half_life_days, confidence) VALUES (?,?,?,?,?,?,?,?)",
        (
            source_id,
            obj["claim"],
            obj["category"],
            json.dumps(obj.get("entities", [])),
            json.dumps(_topics_field(obj)),
            obj["date_of_evidence"],
            half_life,
            float(obj.get("confidence", 0.7)),
        ),
    )


def run(ctx: ThemeContext, limit: int = 20, model: str | None = None) -> dict:
    """Process unprocessed sources -> claims via the configured extract prompt.

    Returns a small summary dict {sources_processed, claims_inserted}.
    """
    model = model or ctx.extract_model
    prompt_template = _load_prompt(ctx)
    db = connect(ctx.db_path)
    rows = db.execute(
        "SELECT id, url, raw_text, fetched_at FROM sources "
        "WHERE processed=0 AND raw_text IS NOT NULL "
        "ORDER BY fetched_at ASC LIMIT ?",
        (limit,),
    ).fetchall()
    print(f"extract({ctx.theme_id}): {len(rows)} sources to process, model={model}")
    total_claims = 0
    for sid, url, text, fetched_at in rows:
        source_date = (
            fetched_at.split(" ")[0] if fetched_at else datetime.utcnow().strftime("%Y-%m-%d")
        )
        prompt = (
            prompt_template
            .replace("{url}", url)
            .replace("{source_date}", source_date)
            .replace("{text}", (text or "")[: ctx.source_text_cap])
        )
        try:
            output = run_claude(prompt, model=model)
        except AuthError as e:
            print(f"\nFATAL: {e}", file=sys.stderr)
            print("Aborting run -- log in once as this user and retry.", file=sys.stderr)
            db.close()
            sys.exit(2)
        except (subprocess.TimeoutExpired, RuntimeError) as e:
            print(f"  FAIL source {sid}: {e}", file=sys.stderr)
            db.execute("UPDATE sources SET error=? WHERE id=?", (str(e)[:500], sid))
            db.commit()
            continue
        claims = _parse_claims(output)
        for c in claims:
            try:
                _insert_claim(db, sid, c, ctx)
            except (sqlite3.IntegrityError, ValueError, KeyError) as e:
                print(f"  skip claim: {e}", file=sys.stderr)
        db.execute("UPDATE sources SET processed=1, error=NULL WHERE id=?", (sid,))
        db.commit()
        total_claims += len(claims)
        print(f"  ok  source {sid}: {len(claims)} claims  [{url[:60]}]")
    db.close()
    summary = {"sources_processed": len(rows), "claims_inserted": total_claims}
    print(f"extract({ctx.theme_id}): {summary}")
    return summary
