#!/usr/bin/env python3
"""Turn a discovered source into a claim the corpus can actually use.

The corpus has three layers and only the outer two were ever automated.
Sources arrive (now), scores and briefs are generated from claims (already),
and in between sat a stage that had been done exactly once, by hand, in May:
reading a source and writing down what it says.

That gap is why a publication with working ingestion, scoring, rendering,
signing and distribution went two months without saying anything new. Fresh
sources cannot reach a brief on their own -- something has to read them.

What this writes is a proposal, never a fact. Every claim lands as
`review_state: pending` with the source it came from and the date that source
carries, so a person accepting it is accepting something they can check in one
click. That was true of the fifty claims written by hand and it stays true of
these.

Usage:
  promote_claims.py --dry-run
  promote_claims.py --themes edge-ai --limit 3
  promote_claims.py --commit
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request

import runner
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path.home() / "trend-corpus"
TRENDS = ROOT / "trends"

PER_THEME = 4

CATEGORIES = ["corporate", "market", "regulatory", "technical", "capital"]

PROMPT = """Read this source and state what it establishes, for a market-intelligence corpus.

THEME: {theme}
TITLE: {title}
URL: {url}
PUBLISHED: {published}

Write ONE claim. Rules:
- Only what this source actually establishes. No inference, no forecasting, no
  "this suggests". If the source does not support a specific, checkable
  statement, output exactly: SKIP
- Name the companies, figures, dates and instruments involved. A claim with no
  proper nouns in it is not worth keeping.
- 2 to 4 sentences. Dense. No hedging language, no adjectives that carry no
  information.
- The category must be one of: {categories}

Output exactly two lines and nothing else:
CATEGORY: <one of the categories>
CLAIM: <the claim text on a single line>"""

# Same question, with the page already read. The model sees exactly what
# WebFetch would have shown it; the difference is that it costs one turn
# instead of three.
PROMPT_INLINE = PROMPT.replace(
    "PUBLISHED: {published}",
    "PUBLISHED: {published}\n\nSOURCE TEXT (already retrieved -- do not fetch "
    "anything, and judge only what is below):\n{body}",
)


# `confidence` is required by schemas/claim.schema.json, and a claim written
# here is single-source and unreviewed, so it must sit below the floor of the
# hand-curated claims (which run 0.65-0.90). Tier is the only signal we have at
# write time. A reviewer raising this is the promotion out of `review_state:
# pending`; nothing else reads it -- aggregates deliberately ignore per-claim
# confidence -- so these values do not move any score.
UNREVIEWED_CONFIDENCE = {"primary": 0.5, "secondary": 0.4}


def slugify(text: str, limit: int = 44) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    return s[:limit].strip("_") or "untitled"


def read_yaml_field(text: str, field: str) -> str:
    m = re.search(rf"^{field}:\s*(.+)$", text, re.M)
    return m.group(1).strip().strip('"\'') if m else ""


def pending_sources(theme_dir: Path) -> list[dict]:
    """Discovered sources nothing has read yet."""
    cited = set()
    for path in (theme_dir / "claims").glob("*.yaml"):
        cited.update(re.findall(r"-\s*(src_\w+)", path.read_text(errors="replace")))
    out = []
    for path in sorted((theme_dir / "sources").glob("*.yaml")):
        text = path.read_text(errors="replace")
        if read_yaml_field(text, "discovery") != "auto":
            continue
        sid = read_yaml_field(text, "id") or path.stem
        if sid in cited:
            continue
        out.append({
            "id": sid,
            "title": read_yaml_field(text, "verified_title")
                     or read_yaml_field(text, "title"),
            "url": read_yaml_field(text, "url"),
            "published": read_yaml_field(text, "published_at")
                         or read_yaml_field(text, "accessed_at"),
            "tier": read_yaml_field(text, "publisher_tier") or "secondary",
        })
    return out


_TAGS = re.compile(r"<(script|style|noscript)[^>]*>.*?</\1>", re.S | re.I)


def fetch_text(url: str, timeout: int = 25, cap: int = 24_000) -> str:
    """Pull the readable body of a page here, so the model does not have to.

    Handing a model a URL and a fetch tool turns a one-turn question into a
    three-turn session: fetch, read, answer. Every one of those turns re-reads
    the entire context, and the fixed preamble on the Claude path is ~39k
    tokens before a single word of the article -- so the retrieval cost several
    times what the judgement did. Measured 2026-08-26: 64 of these ran in one
    burst and spent 7.2M tokens, most of it re-reading preamble while the model
    waited for a page Python could have handed it.

    Returns "" on any failure, and the caller lets the model go and get it. A
    bot wall is a real page behind an unfriendly door, and a browser-shaped
    fetcher gets through some that urllib does not.
    """
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; trend-corpus reader)",
        "Accept": "text/html,application/xhtml+xml,*/*",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if not (200 <= r.status < 400):
                return ""
            raw = r.read(400_000).decode("utf-8", "replace")
    except Exception:
        return ""
    body = _TAGS.sub(" ", raw)
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"&nbsp;?", " ", body)
    body = re.sub(r"\s+", " ", body).strip()
    # Under a few hundred characters is a cookie wall or a JS shell, not an
    # article. Say nothing rather than ask the model to judge boilerplate.
    return body[:cap] if len(body) > 400 else ""


def parse(text: str) -> dict | None:
    if "SKIP" in (text or "")[:200] and "CLAIM:" not in (text or ""):
        return None
    category = ""
    claim = ""
    for line in (text or "").splitlines():
        if line.upper().startswith("CATEGORY:"):
            category = line.split(":", 1)[1].strip().lower()
        elif line.upper().startswith("CLAIM:"):
            claim = line.split(":", 1)[1].strip()
    if not claim or len(claim) < 80:
        return None
    if not re.search(r"[A-Z][a-zA-Z]{2,}", claim):
        return None  # no proper nouns: not a claim, just a sentence
    return {"category": category if category in CATEGORIES else "market",
            "claim": claim}


def write_claim(theme_dir: Path, theme_id: str, source: dict, parsed: dict) -> Path | None:
    cid = f"clm_{slugify(theme_id, 14)}_{slugify(source['title'], 40)}"
    path = theme_dir / "claims" / f"{cid}.yaml"
    if path.exists():
        return None
    when = source["published"][:10] or date.today().isoformat()
    body = [
        f"id: {cid}",
        "type: claim",
        f"theme_id: {theme_id}",
        f"claim: {json.dumps(parsed['claim'])}",
        f"category: {parsed['category']}",
        "source_ids:",
        f"  - {source['id']}",
        f'date_of_evidence: "{when}"',
        f'evidence_at: "{when}"',
        "schema_version: 1",
        f"confidence: {UNREVIEWED_CONFIDENCE.get(source['tier'], 0.4)}",
        "discovery: auto",
        "review_state: pending",
        f"publisher_tier: {source['tier']}",
        "notes: >",
        "  Written by scripts/promote_claims.py from the single source cited",
        "  above and not yet reviewed. It states only what that source",
        "  establishes; anything beyond it is a defect, not a feature.",
    ]
    path.write_text("\n".join(body) + "\n")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--themes", default="")
    ap.add_argument("--limit", type=int, default=PER_THEME)
    ap.add_argument("--model", default="sonnet",
                    help="model for the claude fallback path only")
    ap.add_argument("--engine", default=None,
                    choices=["auto", "pfterminal", "claude"],
                    help="default is pfterminal; auto explicitly falls back to "
                         "claude")
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--shard", default="",
                    help="i/n -- take every nth theme starting at i. Lets cron "
                         "spread the fleet across hours instead of firing every "
                         "session inside one rate-limit window.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--commit", action="store_true")
    args = ap.parse_args()

    wanted = [t.strip() for t in args.themes.split(",") if t.strip()]
    themes = sorted(
        d for d in TRENDS.iterdir()
        if d.is_dir() and not d.name.startswith("_") and (d / "trend.yaml").exists()
        and (not wanted or d.name in wanted)
    )
    if args.shard:
        i, _, n = args.shard.partition("/")
        themes = themes[int(i)::int(n)]

    written: list[Path] = []
    skipped = 0
    for theme_dir in themes:
        theme_id = theme_dir.name
        sources = pending_sources(theme_dir)[: args.limit]
        if not sources:
            continue
        made = 0
        for src in sources:
            body = fetch_text(src["url"])
            if body:
                prompt = PROMPT_INLINE.format(
                    theme=theme_id, title=src["title"], url=src["url"],
                    published=src["published"], body=body,
                    categories=", ".join(CATEGORIES),
                )
            else:
                prompt = PROMPT.format(
                    theme=theme_id, title=src["title"], url=src["url"],
                    published=src["published"], categories=", ".join(CATEGORIES),
                )
            try:
                parsed = parse(runner.ask(
                    prompt, stage="promote", web=not body, engine=args.engine,
                    effort="low", claude_model=args.model, timeout=args.timeout))
            except runner.AuthFailure:
                raise
            except (subprocess.TimeoutExpired, RuntimeError) as exc:
                print(f"  {theme_id}/{src['id']}: {exc}", file=sys.stderr)
                continue
            if not parsed:
                skipped += 1
                continue
            if args.dry_run:
                print(f"  [{parsed['category']}] {parsed['claim'][:150]}")
                made += 1
                continue
            path = write_claim(theme_dir, theme_id, src, parsed)
            if path:
                written.append(path)
                made += 1
        print(f"{theme_id:<22} sources={len(sources):<3} claims={made}")

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"\n{len(written)} claim(s) written, {skipped} source(s) supported none")

    if args.commit and written:
        subprocess.run(["git", "-C", str(ROOT), "add", "--", *map(str, written)],
                       check=False)
        subprocess.run(
            ["git", "-C", str(ROOT), "-c", "user.name=discovery",
             "-c", "user.email=zeroexzoz@gmail.com", "commit", "-q", "-m",
             f"claims: {len(written)} promoted from discovered sources, "
             f"pending review ({stamp})"], check=False)
        push = subprocess.run(["git", "-C", str(ROOT), "push", "-q"],
                              capture_output=True, text=True)
        print("pushed" if push.returncode == 0 else f"push failed: {push.stderr[:200]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
