"""
notify - Telegram notifications for a theme runtime.

Three modes:
  alert   - critical failure (cron wrapper, health check)
  digest  - daily summary of new claims + packets
  packet  - announce a newly-generated decision packet

Credentials come from the ThemeContext (env var or config-pointed .env).
Fails silently (log to stderr) if credentials missing -- never blocks the
pipeline.
"""
from __future__ import annotations

import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

from .context import ThemeContext
from .db import connect

MAX_MSG = 3800


def _send(ctx: ThemeContext, text: str) -> bool:
    token, chat = ctx.resolve_telegram()
    if not token or not chat:
        print(f"notify: TG creds missing for {ctx.theme_id}; skipping", file=sys.stderr)
        return False
    if ctx.message_prefix:
        text = f"{ctx.message_prefix}\n{text}"
    if len(text) > MAX_MSG:
        text = text[: MAX_MSG] + "\n...[truncated]"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode(
        {"chat_id": chat, "text": text, "disable_web_page_preview": "true"}
    ).encode()
    try:
        with urllib.request.urlopen(url, data=data, timeout=15) as resp:
            return resp.status == 200
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"notify: telegram send failed: {e}", file=sys.stderr)
        return False


def alert(ctx: ThemeContext, message: str) -> bool:
    host = os.uname().nodename
    return _send(ctx, f"ALERT {ctx.theme_id} ({host})\n{message}")


def digest(ctx: ThemeContext) -> bool:
    if not ctx.db_path.exists():
        return _send(ctx, f"{ctx.theme_id} digest: db.sqlite missing")
    db = connect(ctx.db_path)
    yesterday = (datetime.utcnow() - timedelta(hours=24)).isoformat(sep=" ")
    new_claims = db.execute(
        "SELECT COUNT(*) FROM claims WHERE created_at > ?", (yesterday,)
    ).fetchone()[0]
    active = db.execute(
        "SELECT COUNT(*) FROM claims WHERE superseded_by IS NULL"
    ).fetchone()[0]
    fresh = db.execute("SELECT COUNT(*) FROM fresh_claims").fetchone()[0]
    new_sources = db.execute(
        "SELECT COUNT(*) FROM sources WHERE fetched_at > ?", (yesterday,)
    ).fetchone()[0]
    errored = db.execute(
        "SELECT COUNT(*) FROM sources WHERE error IS NOT NULL"
    ).fetchone()[0]
    new_packets = db.execute(
        "SELECT COUNT(*) FROM packets WHERE created_at > ?", (yesterday,)
    ).fetchone()[0]
    top = db.execute(
        "SELECT id, category, substr(claim, 1, 120), confidence FROM claims "
        "WHERE created_at > ? AND superseded_by IS NULL "
        "ORDER BY confidence DESC, id DESC LIMIT 3",
        (yesterday,),
    ).fetchall()
    by_cat = db.execute(
        "SELECT category, COUNT(*) FROM claims WHERE created_at > ? "
        "GROUP BY category ORDER BY COUNT(*) DESC",
        (yesterday,),
    ).fetchall()
    db.close()
    lines = [f"{ctx.theme_id} 24h digest"]
    lines.append(f"claims: +{new_claims} new, {active} active, {fresh} fresh")
    lines.append(f"sources: +{new_sources} fetched, {errored} errored")
    lines.append(f"packets: +{new_packets} generated")
    if by_cat:
        lines.append("\nby category (24h):")
        for cat, n in by_cat:
            lines.append(f"  {cat}: {n}")
    if top:
        lines.append("\ntop new claims:")
        for cid, cat, claim, conf in top:
            lines.append(f"  [C-{cid}] ({cat}, conf={conf:.2f}) {claim}")
    return _send(ctx, "\n".join(lines))


def packet(ctx: ThemeContext, packet_path: str) -> bool:
    p = Path(packet_path)
    if not p.exists():
        return _send(ctx, f"{ctx.theme_id} packet mode: file not found: {packet_path}")
    content = p.read_text()
    verdict = "?"
    for line in content.splitlines():
        upper = line.upper()
        for v in ("PURSUE", "WATCH", "AVOID", "KILL"):
            if v in upper and not line.startswith("#"):
                verdict = v
                break
        if verdict != "?":
            break
    title = "(untitled)"
    for line in content.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    claim_refs = len(set(re.findall(r"C-\d+", content)))
    msg = (
        f"new decision packet: {verdict}\n\n"
        f"{title}\n"
        f"cites {claim_refs} claims\n"
        f"file: {p.name}"
    )
    return _send(ctx, msg)
