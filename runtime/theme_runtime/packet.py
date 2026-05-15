"""
packet - generate a Decision Packet for a question.

Pulls fresh active claims, sends to Claude with prompts/packet.md,
writes a timestamped markdown to out/packets/, records the packet in
the packets table.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone

from .claude_cli import AuthError, run_claude
from .context import ThemeContext
from .db import connect


def _load_prompt(ctx: ThemeContext) -> str:
    path = ctx.prompts_dir / "packet.md"
    if not path.exists():
        raise FileNotFoundError(f"packet prompt not found: {path}")
    return path.read_text()


def _pull_claims(db, limit: int = 200, filter_kv: tuple[str, str] | None = None):
    """Return list of dicts of fresh active claims, optionally filtered."""
    sql = (
        "SELECT id, claim, category, entities, topics, "
        "  date_of_evidence, confidence, source_url FROM fresh_claims "
    )
    params: list = []
    if filter_kv:
        field, value = filter_kv
        if field == "category":
            sql += "WHERE category = ? "
            params.append(value)
        elif field in ("entities", "topics"):
            sql += f"WHERE {field} LIKE ? "
            params.append(f'%"{value.lower()}"%')
    sql += "ORDER BY date_of_evidence DESC, confidence DESC LIMIT ?"
    params.append(limit)
    rows = db.execute(sql, params).fetchall()
    return [
        {
            "id": f"C-{r[0]}",
            "claim": r[1],
            "category": r[2],
            "entities": json.loads(r[3] or "[]"),
            "topics": json.loads(r[4] or "[]"),
            "date": r[5],
            "confidence": r[6],
            "source": r[7],
        }
        for r in rows
    ]


def _format_claims(claims):
    lines = []
    for c in claims:
        ents = ",".join(c["entities"]) if c["entities"] else "-"
        tops = ",".join(c["topics"]) if c["topics"] else "-"
        lines.append(
            f"[{c['id']}] ({c['category']}, {c['date']}, conf={c['confidence']:.2f}, "
            f"ents={ents}, topics={tops}) {c['claim']}"
        )
    return "\n".join(lines)


def _parse_filter(s: str | None) -> tuple[str, str] | None:
    if not s:
        return None
    if ":" not in s:
        raise ValueError("--filter must be field:value, e.g. topics:hbm")
    field, value = s.split(":", 1)
    if field not in ("topics", "entities", "category"):
        raise ValueError("filter field must be topics, entities, or category")
    return (field, value)


_VERDICT_TOKENS = ("PURSUE", "WATCH", "AVOID", "KILL")


def _extract_verdict(text: str) -> str | None:
    for line in text.splitlines():
        upper = line.upper()
        for v in _VERDICT_TOKENS:
            if v in upper and "##" not in line:
                return v
    return None


def run(
    ctx: ThemeContext,
    question: str,
    limit: int = 200,
    model: str | None = None,
    filter_expr: str | None = None,
) -> dict:
    model = model or ctx.packet_model
    filter_kv = _parse_filter(filter_expr)
    db = connect(ctx.db_path)
    claims = _pull_claims(db, limit=limit, filter_kv=filter_kv)
    if not claims:
        print("WARNING: no active claims found. Run ingest + extract first.", file=sys.stderr)
    now = datetime.now(timezone.utc)
    prompt_template = _load_prompt(ctx)
    prompt = (
        prompt_template
        .replace("{question}", question)
        .replace("{date}", now.strftime("%Y-%m-%d"))
        .replace("{claims}", _format_claims(claims) if claims else "(none)")
    )
    print(
        f"packet({ctx.theme_id}): question={question!r} claims={len(claims)} model={model}"
    )
    try:
        packet_text = run_claude(prompt, model=model, timeout=600)
    except AuthError as e:
        print(f"FATAL: {e}", file=sys.stderr)
        db.close()
        sys.exit(2)
    except (subprocess.TimeoutExpired, RuntimeError) as e:
        print(f"FAIL: {e}", file=sys.stderr)
        db.close()
        sys.exit(3)
    ctx.packets_dir.mkdir(parents=True, exist_ok=True)
    slug = "-".join(question.lower().split())[:60]
    slug = "".join(ch if ch.isalnum() or ch == "-" else "" for ch in slug).strip("-")
    ts = now.strftime("%Y%m%dT%H%M%SZ")
    out_path = ctx.packets_dir / f"{ts}_{slug}.md"
    out_path.write_text(packet_text)
    verdict = _extract_verdict(packet_text)
    db.execute(
        "INSERT INTO packets (question, verdict, packet_path) VALUES (?,?,?)",
        (question, verdict, str(out_path)),
    )
    db.commit()
    db.close()
    print(f"packet({ctx.theme_id}): {out_path}  verdict={verdict}")
    return {"path": str(out_path), "verdict": verdict, "claims_count": len(claims)}
