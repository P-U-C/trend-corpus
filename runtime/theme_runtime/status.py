"""
status - quick health look at a theme's corpus.
"""
from __future__ import annotations

import sqlite3
import sys

from .context import ThemeContext
from .db import connect


def summary(ctx: ThemeContext) -> dict:
    db = connect(ctx.db_path)
    out = {
        "theme_id": ctx.theme_id,
        "sources_total": db.execute("SELECT COUNT(*) FROM sources").fetchone()[0],
        "sources_processed": db.execute(
            "SELECT COUNT(*) FROM sources WHERE processed=1"
        ).fetchone()[0],
        "sources_errored": db.execute(
            "SELECT COUNT(*) FROM sources WHERE error IS NOT NULL"
        ).fetchone()[0],
        "claims_total": db.execute("SELECT COUNT(*) FROM claims").fetchone()[0],
        "claims_active": db.execute(
            "SELECT COUNT(*) FROM claims WHERE superseded_by IS NULL"
        ).fetchone()[0],
        "claims_fresh": db.execute("SELECT COUNT(*) FROM fresh_claims").fetchone()[0],
        "packets": db.execute("SELECT COUNT(*) FROM packets").fetchone()[0],
    }
    db.close()
    return out


def print_summary(ctx: ThemeContext) -> None:
    s = summary(ctx)
    print(f"== {s['theme_id']} status ==")
    print(
        f"sources: {s['sources_total']} total, "
        f"{s['sources_processed']} processed, {s['sources_errored']} errored"
    )
    print(
        f"claims:  {s['claims_total']} total, "
        f"{s['claims_active']} active, {s['claims_fresh']} fresh"
    )
    print(f"packets: {s['packets']} generated")


def print_recent_claims(ctx: ThemeContext, n: int = 10) -> None:
    db = connect(ctx.db_path)
    rows = db.execute(
        "SELECT id, category, date_of_evidence, confidence, substr(claim, 1, 100) "
        "FROM claims WHERE superseded_by IS NULL "
        "ORDER BY created_at DESC LIMIT ?",
        (n,),
    ).fetchall()
    for r in rows:
        print(f"C-{r[0]:<5} {r[1]:<14} {r[2]}  conf={r[3]:.2f}  {r[4]}")
    db.close()


def run_sql(ctx: ThemeContext, sql: str) -> None:
    db = connect(ctx.db_path)
    try:
        rows = db.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"SQL error: {e}", file=sys.stderr)
        sys.exit(1)
    for row in rows:
        print("\t".join(str(c) for c in row))
    db.close()
