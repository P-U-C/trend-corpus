"""
sync - pull theme content from a trend-corpus checkout into the live runtime.

What gets synced:
  - sources.txt is rebuilt from trend-corpus/trends/<theme>/sources/*.yaml
    (URL field of each source object; titles preserved as comments).
  - prompts/{extract.md, packet.md, validate.md} are rebuilt by splitting
    trend-corpus/trends/<theme>/docs/prompts.md on the section headers.

What stays host-local:
  - db.sqlite (the corpus state).
  - out/packets/ (generated artifacts).
  - .theme-runtime.env (credentials).
  - theme-config.yaml (operator-tuned; sync never overwrites it).

The function is idempotent and writes atomically. A diff summary is
returned so callers can log "added N, removed M" cleanly.
"""
from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

from .context import ThemeContext

PROMPT_SECTION_RE = re.compile(r"^##\s+([a-z]+\.md)\s*$")


def _load_yaml(path: Path) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML is required for sync")
    return yaml.safe_load(path.read_text()) or {}


def _gather_sources(theme_dir: Path) -> list[tuple[str, str]]:
    """Return [(title, url), ...] from trends/<theme>/sources/*.yaml.

    Prefers `url` then `public_locator`. Skips objects that have neither.
    Stable order: by source filename.
    """
    out: list[tuple[str, str]] = []
    sources_dir = theme_dir / "sources"
    if not sources_dir.is_dir():
        return out
    for path in sorted(sources_dir.glob("*.yaml")):
        try:
            d = _load_yaml(path)
        except Exception:
            continue
        url = d.get("url") or d.get("public_locator")
        if not url or not isinstance(url, str):
            continue
        title = d.get("title") or url
        out.append((title, url))
    return out


def _split_prompts_md(text: str) -> dict[str, str]:
    """Split a prompts.md doc into {extract.md, packet.md, validate.md} bodies.

    The trend-corpus prompts.md uses '## <name>.md' section headers and
    triple-backtick fences around the body. The split strips the fences
    and returns just the prompt content for each section.
    """
    sections: dict[str, list[str]] = {}
    current: str | None = None
    buf: list[str] = []
    for line in text.splitlines():
        match = PROMPT_SECTION_RE.match(line)
        if match:
            if current:
                sections[current] = buf
            current = match.group(1)
            buf = []
            continue
        if current is None:
            continue
        # Strip fence markers
        if line.strip() == "```":
            continue
        buf.append(line)
    if current:
        sections[current] = buf
    return {name: ("\n".join(lines).strip("\n") + "\n") for name, lines in sections.items()}


def _atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content)
    os.replace(tmp, path)


def _read_current_urls(sources_path: Path) -> set[str]:
    if not sources_path.exists():
        return set()
    out: set[str] = set()
    for line in sources_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.add(line)
    return out


def run(ctx: ThemeContext, trend_corpus_root: Path) -> dict[str, Any]:
    """Sync ctx.theme_id from trend_corpus_root into the runtime files.

    Returns a diff summary:
      {theme_id, sources_total, sources_added[], sources_removed[],
       prompts_written[]}
    """
    root = Path(trend_corpus_root).expanduser().resolve()
    theme_dir = root / "trends" / ctx.theme_id
    if not theme_dir.is_dir():
        raise FileNotFoundError(f"theme not in trend-corpus: {theme_dir}")

    # ---- sources ----
    pairs = _gather_sources(theme_dir)
    new_urls = [url for _, url in pairs]
    new_set = set(new_urls)
    old_set = _read_current_urls(ctx.sources_path)

    lines = [
        f"# sources for {ctx.theme_id} runtime",
        f"# synced from {root} on {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
    ]
    for title, url in pairs:
        lines.append(f"# {title}")
        lines.append(url)
        lines.append("")
    _atomic_write(ctx.sources_path, "\n".join(lines))

    # ---- prompts ----
    prompts_md = theme_dir / "docs" / "prompts.md"
    prompts_written: list[str] = []
    if prompts_md.exists():
        ctx.prompts_dir.mkdir(parents=True, exist_ok=True)
        sections = _split_prompts_md(prompts_md.read_text())
        for name, body in sections.items():
            target = ctx.prompts_dir / name
            _atomic_write(target, body)
            prompts_written.append(name)

    summary = {
        "theme_id": ctx.theme_id,
        "trend_corpus_root": str(root),
        "sources_total": len(new_urls),
        "sources_added": sorted(new_set - old_set),
        "sources_removed": sorted(old_set - new_set),
        "prompts_written": sorted(prompts_written),
    }
    print(
        f"sync({ctx.theme_id}): "
        f"{len(new_urls)} urls (+{len(summary['sources_added'])}/-{len(summary['sources_removed'])}), "
        f"{len(prompts_written)} prompts written"
    )
    return summary


def publish_aggregates(ctx, trend_corpus_dir, *, src):
    """Copy an aggregates JSON into the trend-corpus checkout, commit, push.

    Mirrors the secret-scan + diff-vs-current discipline of
    pf-scout-bot/deploy/sync-peptides-aggregates.sh, but runs from inside
    the runtime user (self-publishing) rather than pulling over scp.

    Idempotent: if the staged file is byte-identical to what's already on
    disk, no commit. Always git-pulls first so 14 concurrent runtimes
    don't fight over fast-forward; one push-retry on conflict.

    Returns a dict suitable for printing / Telegram reporting.
    """
    import json as _json
    import re as _re
    import subprocess as _sp

    src = Path(src).expanduser()
    if not src.exists():
        return {"theme_id": ctx.theme_id, "error": f"src missing: {src}"}

    root = Path(trend_corpus_dir).expanduser()
    if not (root / ".git").exists():
        return {"theme_id": ctx.theme_id, "error": f"not a git checkout: {root}"}

    dest = root / "trends" / ctx.theme_id / "aggregates" / f"{ctx.theme_id}-aggregates.json"
    raw = src.read_text()

    # Schema validation at the publish boundary.
    from . import aggregates as _agg
    try:
        payload = _json.loads(raw)
    except _json.JSONDecodeError as exc:
        return {"theme_id": ctx.theme_id, "error": f"invalid JSON: {exc}"}
    if payload.get("theme_id") != ctx.theme_id:
        return {"theme_id": ctx.theme_id,
                "error": f"theme_id mismatch: {payload.get('theme_id')!r} vs {ctx.theme_id!r}"}
    try:
        _agg.validate_payload(payload)
    except Exception as exc:
        return {"theme_id": ctx.theme_id, "error": f"schema validation failed: {exc}"}

    # Secret-pattern scan -- same set the peptide sync script uses.
    secret_patterns = [
        r"OPENAI_API_KEY", r"ANTHROPIC_API_KEY", r"GITHUB_TOKEN",
        r"TELEGRAM_BOT_TOKEN", r"AWS_(ACCESS_KEY_ID|SECRET_ACCESS_KEY)",
        r"PRIVATE_KEY", r"MNEMONIC",
        r"ghp_[A-Za-z0-9_]{20,}", r"github_pat_[A-Za-z0-9_]{40,}",
        r"sk-[A-Za-z0-9]{20,}", r"xox[baprs]-[A-Za-z0-9-]{10,}",
        r"-----BEGIN (RSA|OPENSSH|EC|DSA|PGP) PRIVATE KEY-----",
        r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"][^'\"]+['\"]",
        r"\b505841972\b",
    ]
    hits = [p for p in secret_patterns if _re.search(p, raw)]
    if hits:
        return {"theme_id": ctx.theme_id, "error": f"secret pattern hits: {hits}"}

    # Diff vs current; no-op if unchanged.
    if dest.exists() and dest.read_text() == raw:
        return {"theme_id": ctx.theme_id, "noop": True, "dest": str(dest)}

    # Pull first so we don't fight other runtimes on push.
    _sp.run(["git", "-C", str(root), "pull", "--quiet", "--rebase"],
            check=True, capture_output=True)

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(raw)

    # Stage by exact path; never `git add -A`.
    rel_path = str(dest.relative_to(root))
    _sp.run(["git", "-C", str(root), "add", "--", rel_path],
            check=True, capture_output=True)

    staged = _sp.run(["git", "-C", str(root), "diff", "--cached", "--quiet"],
                     capture_output=True)
    if staged.returncode == 0:
        return {"theme_id": ctx.theme_id, "noop": True, "dest": str(dest),
                "reason": "git diff --cached empty after add"}

    summary_text = (
        f"claims={payload['underlying_claim_count']} "
        f"sources={payload['underlying_source_count']} "
        f"generated_at={payload['generated_at']}"
    )
    commit_msg = f"aggregates({ctx.theme_id}): {summary_text}"
    _sp.run(["git", "-C", str(root), "commit", "-m", commit_msg],
            check=True, capture_output=True)

    push = _sp.run(["git", "-C", str(root), "push", "origin", "HEAD:main"],
                   capture_output=True)
    if push.returncode != 0:
        # One retry after rebase, in case another runtime pushed in between.
        _sp.run(["git", "-C", str(root), "pull", "--rebase", "--quiet"],
                check=True, capture_output=True)
        push = _sp.run(["git", "-C", str(root), "push", "origin", "HEAD:main"],
                       capture_output=True)
    if push.returncode != 0:
        return {"theme_id": ctx.theme_id,
                "error": f"git push failed: {push.stderr.decode(errors='replace')[:400]}"}

    head = _sp.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
                   capture_output=True, text=True).stdout.strip()
    return {"theme_id": ctx.theme_id, "dest": str(dest),
            "commit": head, "summary": summary_text}
