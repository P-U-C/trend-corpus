#!/usr/bin/env python3
"""Find sources the corpus has never seen, so that everything below it can move.

Every source in this corpus was added by hand between 15 and 17 May 2026, with
thirteen more on 5 June when biomechanics was added. Nothing since. The runtime
producers re-fetch those same URLs every day, which is why the claim counts
climb -- edge-ai passed 7,454 -- while nothing new enters. It is re-reading the
same pages and counting the re-reads.

Starved at the top, everything downstream is starved too: no new sources, no
claims worth curating, no new theses or decision packets, an alpha gate that
cannot be satisfied, and two months of the same three essays published under a
masthead promising a cross-sector brief.

So this adds sources. It does not curate, score or publish; those stages exist
and work. It only ends the drought at the top.

Two things it refuses to do:

  * invent. Every URL is fetched before it is written. A link the model
    produced but that does not resolve is dropped, silently and always, which
    turns "the model might make one up" from a worry into a non-event.
  * decide. Everything lands as review_state: pending. A source is a claim
    about what is worth reading, and that has been a human judgement here from
    the beginning.

Usage:
  discover_sources.py --dry-run                 # show what it would add
  discover_sources.py --themes edge-ai --limit 5
  discover_sources.py --commit                  # write, commit and push
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path.home() / "trend-corpus"
TRENDS = ROOT / "trends"

# Enough to matter, few enough that a bad run is cheap to throw away.
PER_THEME = 6
WINDOW_DAYS = 45

# What counts as a source worth having. Ordered: the further down, the weaker
# the evidence, and the prompt says so.
SOURCE_TYPES = [
    "company_ir",        # investor relations, press releases, earnings
    "regulatory",        # filings, agency actions, standards bodies
    "primary_research",  # papers, technical reports, benchmarks
    "trade_press",       # credible sector reporting
]

PROMPT = """Find recent, real, citable sources about this market theme.

THEME: {title}

WHAT THE THEME COVERS:
{summary}

Rules:
- Published within the last {window} days. Today is {today}. Recency is the
  entire point of this request -- an older but excellent source is useless here.
- Prefer primary sources in this order: {types}.
- Each must be a specific article, release or filing. Never a homepage, index,
  search page, tag page or PDF listing.
- Do NOT return any of these URLs, which are already held:
{known}

Return at most {limit} lines, nothing else. No preamble, no numbering, no
commentary. One line each, pipe-separated, exactly:

URL | TITLE | SOURCE_TYPE | PUBLISHED_YYYY-MM-DD

If you cannot find sources that are genuinely within the window, return fewer
lines. Returning nothing is a valid and useful answer; padding is not."""


def slugify(text: str, limit: int = 48) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    return s[:limit].strip("_") or "untitled"


# The same story arrives wearing different clothes: an AMP copy, a syndicated
# reprint, a tracked share link. Comparing raw URLs treats those as four
# sources and quietly quadruples the weight of one press release.
_AMP = re.compile(r"(?:^amp\.|/amp(?:/|$)|\.amp(?:/|$)|[?&]outputType=amp)")


def canonical(url: str) -> str:
    """For comparison only -- what makes two links the same link."""
    u = (url or "").strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^(?:www|m|amp)\.", "", u)
    u = u.split("#")[0].split("?")[0]
    u = _AMP.sub("/", u)
    return re.sub(r"/{2,}", "/", u).rstrip("/")


# Where a claim comes from is most of what it is worth. A company's own
# investor-relations page and a syndicated aggregator can carry identical text
# and are not the same evidence, so the tier travels with the source rather
# than being re-derived by whoever reads it later.
PRIMARY_HOSTS = (
    "sec.gov", "globenewswire.com", "businesswire.com", "prnewswire.com",
    "federalregister.gov", "bis.doc.gov", "europa.eu", "arxiv.org",
)
PRIMARY_PREFIXES = ("investor.", "investors.", "ir.")


def publisher_tier(url: str) -> str:
    host = canonical(url).split("/")[0]
    if host.endswith(".gov") or any(host.endswith(h) for h in PRIMARY_HOSTS):
        return "primary"
    if any(host.startswith(pre) for pre in PRIMARY_PREFIXES):
        return "primary"
    return "secondary"


def known_urls(theme_dir: Path) -> set[str]:
    found = set()
    for path in (theme_dir / "sources").glob("*.yaml"):
        for line in path.read_text(errors="replace").splitlines():
            m = re.match(r"\s*(?:url|public_locator):\s*(\S+)", line)
            if m:
                found.add(canonical(m.group(1).strip('"\'')))
    return found


def theme_meta(theme_dir: Path) -> tuple[str, str]:
    text = (theme_dir / "trend.yaml").read_text(errors="replace")
    title = ""
    m = re.search(r"^title:\s*(.+)$", text, re.M)
    if m:
        title = m.group(1).strip().strip('"\'')
    summary = ""
    m = re.search(r"^summary:\s*>\s*\n((?:\s{2,}.*\n)+)", text, re.M)
    if m:
        summary = re.sub(r"\s+", " ", m.group(1)).strip()
    return title or theme_dir.name, summary[:1800]


def ask(prompt: str, model: str, timeout: int) -> str:
    result = subprocess.run(
        ["claude", "-p", prompt, "--model", model,
         "--output-format", "text", "--allowed-tools", "WebSearch"],
        capture_output=True, text=True, timeout=timeout,
    )
    if result.returncode != 0:
        blob = ((result.stdout or "") + " " + (result.stderr or "")).lower()
        if any(m in blob for m in ("authenticate", "oauth", "revoked", "401", "login")):
            # Same failure that cost the swell corpus fifty days. Stop the run
            # rather than write a day of empty results and exit 0.
            raise SystemExit("claude auth failed — this run would find nothing "
                             "and report success. Fix the login first.")
        raise RuntimeError((result.stderr or result.stdout or "")[:300])
    return result.stdout


def parse(text: str) -> list[dict]:
    out = []
    for line in (text or "").splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            continue
        # Models wrap URLs in markdown even when told not to, and a stray
        # backtick turns a real investor-relations link into a DNS failure that
        # reads like a dead source. Strip the decoration before judging it.
        url = parts[0].strip().strip("`<>\"'").strip()
        url = re.sub(r"^\[.*?\]\(", "", url).rstrip(")")
        url = re.sub(r"^https?://[`'\"]+", "https://", url)
        if not re.match(r"^https?://", url):
            url = "https://" + url.lstrip("`")
        if "." not in url.split("//", 1)[-1].split("/")[0]:
            continue
        out.append({
            "url": url,
            "title": parts[1][:200],
            "source_type": parts[2] if parts[2] in SOURCE_TYPES else "trade_press",
            "published": parts[3][:10] if len(parts) > 3 else "",
        })
    return out


_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
_STOP = {"the", "a", "an", "and", "or", "of", "to", "for", "in", "on", "with",
         "at", "by", "from", "its", "new", "inc", "corp", "ltd", "plc"}


def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]{3,}", (text or "").lower())
            if w not in _STOP}


def verify(url: str, claimed_title: str, timeout: int = 25,
           attempts: int = 2) -> tuple[bool, str]:
    """Does this page exist, and is it the page we were told it was?

    Two separate questions, and the second is the one that matters. A status of
    200 proves a server answered, not that the link is what it claimed -- it can
    be a paywall stub, a redirect to a section front, or a page about something
    else entirely. So the title is read back and compared.

    Retries, and generously. The first version timed out at 15 seconds and threw
    away 19 of 23 candidates, almost all of them GlobeNewswire, BusinessWire and
    investor-relations pages: the highest-quality primary sources in the set,
    discarded for being slow. A verification step that preferentially rejects
    the best evidence is worse than none, because it looks like diligence.
    """
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; trend-corpus source check)",
        "Accept": "text/html,application/xhtml+xml,*/*",
    })
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=timeout * (attempt + 1)) as r:
                if not (200 <= r.status < 400):
                    return False, f"status {r.status}"
                body = r.read(200_000).decode("utf-8", "replace")
            m = _TITLE.search(body)
            page_title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ",
                                                    m.group(1))).strip() if m else ""
            if not page_title:
                # No title to check against. The page exists; say so and let a
                # human decide, rather than inventing confidence either way.
                return True, ""
            want, got = _tokens(claimed_title), _tokens(page_title)
            if want and len(want & got) < max(2, len(want) // 4):
                return False, f"title mismatch: page says {page_title[:70]!r}"
            return True, page_title[:180]
        except urllib.error.HTTPError as e:
            # A paywall or a bot wall is a real page behind an unfriendly door.
            if e.code in (401, 402, 403, 405, 429):
                return True, ""
            return False, f"HTTP {e.code}"
        except Exception as exc:
            if attempt + 1 >= attempts:
                return False, type(exc).__name__
    return False, "unreachable"


def write_source(theme_dir: Path, theme_id: str, item: dict) -> Path | None:
    sid = f"src_{slugify(theme_id, 16)}_{slugify(item['title'], 40)}"
    path = theme_dir / "sources" / f"{sid}.yaml"
    if path.exists():
        return None
    body = [
        f"id: {sid}",
        "type: source",
        f"theme_id: {theme_id}",
        f"title: {json.dumps(item['title'])}",
        f"url: {item['url']}",
        f"public_locator: {item['url']}",
        f"source_type: {item['source_type']}",
        f'accessed_at: "{date.today().isoformat()}"',
        "schema_version: 1",
        f"tags: [{theme_id}, auto-discovered]",
        "discovery: auto",
        "review_state: pending",
        f"publisher_tier: {item.get('publisher_tier', 'secondary')}",
    ]
    if item.get("verified_title"):
        body.append(f"verified_title: {json.dumps(item['verified_title'])}")
    if item.get("published"):
        body.append(f'published_at: "{item["published"]}"')
    body += [
        "notes: >",
        "  Found by scripts/discover_sources.py and verified to resolve. Not yet",
        "  reviewed: a source is a claim about what is worth reading, and that",
        "  judgement has been a human one here since the corpus was seeded.",
    ]
    path.write_text("\n".join(body) + "\n")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--themes", default="", help="comma-separated; default all")
    ap.add_argument("--limit", type=int, default=PER_THEME)
    ap.add_argument("--window", type=int, default=WINDOW_DAYS)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--commit", action="store_true")
    args = ap.parse_args()

    wanted = [t.strip() for t in args.themes.split(",") if t.strip()]
    themes = sorted(
        d for d in TRENDS.iterdir()
        if d.is_dir() and not d.name.startswith("_") and (d / "trend.yaml").exists()
        and (not wanted or d.name in wanted)
    )

    added_total = 0
    written: list[Path] = []
    for theme_dir in themes:
        theme_id = theme_dir.name
        title, summary = theme_meta(theme_dir)
        known = known_urls(theme_dir)
        prompt = PROMPT.format(
            title=title, summary=summary, window=args.window,
            today=date.today().isoformat(), types=", ".join(SOURCE_TYPES),
            known="\n".join(f"  - {u}" for u in sorted(known)[:60]) or "  (none)",
            limit=args.limit,
        )
        try:
            raw = ask(prompt, args.model, args.timeout)
        except (subprocess.TimeoutExpired, RuntimeError) as exc:
            print(f"{theme_id}: search failed ({exc})", file=sys.stderr)
            continue

        candidates = parse(raw)
        fresh = [c for c in candidates if canonical(c["url"]) not in known]
        # Deduplicate within the batch too; the same release often surfaces twice.
        seen, unique = set(), []
        for c in fresh:
            key = canonical(c["url"])
            if key not in seen:
                seen.add(key)
                unique.append(c)

        kept = []
        for c in unique[: args.limit]:
            ok, detail = verify(c["url"], c["title"])
            if ok:
                c["verified_title"] = detail
                c["publisher_tier"] = publisher_tier(c["url"])
                kept.append(c)
            else:
                print(f"  {theme_id}: dropped {c['url'][:70]} ({detail})",
                      file=sys.stderr)

        print(f"{theme_id:<22} proposed={len(candidates):<3} new={len(unique):<3} "
              f"verified={len(kept)}")
        if args.dry_run:
            for c in kept:
                print(f"    + [{c['source_type']}] {c['published']} {c['title'][:70]}")
                print(f"      {c['url']}")
            continue

        for c in kept:
            path = write_source(theme_dir, theme_id, c)
            if path:
                written.append(path)
                added_total += 1

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"\n{added_total} source(s) written across {len(themes)} theme(s) at {stamp}")

    if args.commit and written:
        subprocess.run(["git", "-C", str(ROOT), "add", "--", *map(str, written)],
                       check=False)
        subprocess.run(
            ["git", "-C", str(ROOT), "-c", "user.name=discovery",
             "-c", "user.email=zeroexzoz@gmail.com", "commit", "-q", "-m",
             f"sources: {added_total} discovered, pending review ({stamp})"],
            check=False)
        push = subprocess.run(["git", "-C", str(ROOT), "push", "-q"],
                              capture_output=True, text=True)
        print("pushed" if push.returncode == 0 else f"push failed: {push.stderr[:200]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
