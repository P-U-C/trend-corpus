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
