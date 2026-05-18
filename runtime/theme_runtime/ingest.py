"""
ingest - fetch sources listed in sources.txt, strip HTML, insert into db.

Skips sources fetched in the last 24h. Idempotent. Theme-agnostic; takes
a ThemeContext.
"""
from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from html.parser import HTMLParser

from .context import ThemeContext
from .db import connect

TIMEOUT = 30


class _TextExtractor(HTMLParser):
    """Strip scripts/styles/nav, collapse whitespace, return body text."""

    SKIP_TAGS = {"script", "style", "nav", "footer", "header", "aside", "form", "noscript"}

    def __init__(self) -> None:
        super().__init__()
        self.skip_depth = 0
        self.chunks: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS and self.skip_depth > 0:
            self.skip_depth -= 1

    def handle_data(self, data):
        if self.skip_depth == 0:
            self.chunks.append(data)

    def text(self) -> str:
        raw = " ".join(self.chunks)
        return re.sub(r"\s+", " ", raw).strip()


def _fetch(url: str, ctx: ThemeContext) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": f"trend-runtime/{ctx.theme_id} (research)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        raw = resp.read().decode(charset, errors="replace")
    parser = _TextExtractor()
    parser.feed(raw)
    return parser.text()[: ctx.max_text_len]


def _load_urls(ctx: ThemeContext) -> list[str]:
    if not ctx.sources_path.exists():
        raise FileNotFoundError(f"sources.txt not found: {ctx.sources_path}")
    urls = []
    for line in ctx.sources_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(line)
    return urls


def run(ctx: ThemeContext) -> dict:
    """Fetch every URL in sources.txt; insert into sources table.

    Returns a small summary dict {urls, fetched, skipped, failed}.
    """
    db = connect(ctx.db_path)
    cutoff = (datetime.utcnow() - timedelta(hours=24)).isoformat(sep=" ")
    urls = _load_urls(ctx)
    print(f"ingest({ctx.theme_id}): {len(urls)} urls in {ctx.sources_path.name}")
    fetched = skipped = failed = 0
    for url in urls:
        row = db.execute(
            "SELECT COUNT(*) FROM sources WHERE url=? AND fetched_at > ?",
            (url, cutoff),
        ).fetchone()
        if row[0] > 0:
            skipped += 1
            continue
        # Use UPSERT (ON CONFLICT ... DO UPDATE) instead of INSERT OR REPLACE.
        # INSERT OR REPLACE deletes the row and re-inserts it, which trips
        # the FK constraint when claims.source_id references the existing id.
        # The UPSERT keeps the row id stable so existing claims stay linked.
        try:
            text = _fetch(url, ctx)
        except (urllib.error.URLError, urllib.error.HTTPError, Exception) as e:
            failed += 1
            db.execute(
                "INSERT INTO sources (url, raw_text, processed, error) "
                "VALUES (?, NULL, 1, ?) "
                "ON CONFLICT(url) DO UPDATE SET "
                "raw_text=NULL, processed=1, error=excluded.error, "
                "fetched_at=CURRENT_TIMESTAMP",
                (url, str(e)[:500]),
            )
            db.commit()
            print(f"  FAIL {url}: {e}", file=sys.stderr)
            continue
        if len(text) < ctx.min_text_len:
            failed += 1
            print(f"  SHORT ({len(text)}ch) {url}", file=sys.stderr)
            continue
        db.execute(
            "INSERT INTO sources (url, raw_text, processed, error) "
            "VALUES (?, ?, 0, NULL) "
            "ON CONFLICT(url) DO UPDATE SET "
            "raw_text=excluded.raw_text, processed=0, error=NULL, "
            "fetched_at=CURRENT_TIMESTAMP",
            (url, text),
        )
        db.commit()
        fetched += 1
        print(f"  ok  ({len(text)}ch) {url}")
    db.close()
    summary = {"urls": len(urls), "fetched": fetched, "skipped": skipped, "failed": failed}
    print(f"ingest({ctx.theme_id}): {summary}")
    return summary
