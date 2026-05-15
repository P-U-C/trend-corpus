"""Tests for theme_runtime.sync."""
from __future__ import annotations

import textwrap
from pathlib import Path

import yaml

from theme_runtime import sync
from theme_runtime.context import ThemeContext


def _fake_trend_corpus(tmp_path: Path, theme_id: str, sources: list[tuple[str, str]],
                      prompts_md: str | None = None) -> Path:
    """Build a minimal trend-corpus checkout containing one theme."""
    theme_dir = tmp_path / "trend-corpus" / "trends" / theme_id
    (theme_dir / "sources").mkdir(parents=True)
    (theme_dir / "docs").mkdir(parents=True)
    for idx, (title, url) in enumerate(sources):
        d = {
            "id": f"src_{theme_id}_{idx}",
            "type": "source",
            "title": title,
            "url": url,
            "accessed_at": "2026-05-15",
            "schema_version": 1,
        }
        (theme_dir / "sources" / f"src_{idx:03d}.yaml").write_text(yaml.safe_dump(d))
    if prompts_md is not None:
        (theme_dir / "docs" / "prompts.md").write_text(prompts_md)
    return tmp_path / "trend-corpus"


def _runtime_ctx(tmp_path: Path, theme_id: str) -> ThemeContext:
    root = tmp_path / "runtime"
    root.mkdir()
    return ThemeContext(theme_id=theme_id, theme_name="X", root=root)


def test_sync_writes_sources_with_diff(tmp_path):
    repo = _fake_trend_corpus(tmp_path, "x", [
        ("Alpha", "https://a.example/"),
        ("Beta",  "https://b.example/"),
    ])
    ctx = _runtime_ctx(tmp_path, "x")
    ctx.sources_path.write_text("# pre-existing\nhttps://old.example/\n")

    summary = sync.run(ctx, repo)
    assert summary["sources_total"] == 2
    assert "https://a.example/" in summary["sources_added"]
    assert "https://old.example/" in summary["sources_removed"]
    assert "https://b.example/" in summary["sources_added"]

    body = ctx.sources_path.read_text()
    assert "https://a.example/" in body
    assert "https://b.example/" in body
    assert "https://old.example/" not in body
    # Titles preserved as comments
    assert "# Alpha" in body


def test_sync_writes_prompts(tmp_path):
    prompts_md = textwrap.dedent("""\
        # Prompts

        Some preamble.

        ## extract.md

        ```
        EXTRACT BODY {url}
        ```

        ## packet.md

        ```
        PACKET BODY {question}
        ```

        ## validate.md

        ```
        VALIDATE BODY
        ```
    """)
    repo = _fake_trend_corpus(tmp_path, "x", [("A", "https://a.example/")],
                              prompts_md=prompts_md)
    ctx = _runtime_ctx(tmp_path, "x")
    summary = sync.run(ctx, repo)
    assert sorted(summary["prompts_written"]) == ["extract.md", "packet.md", "validate.md"]
    assert "EXTRACT BODY {url}" in (ctx.prompts_dir / "extract.md").read_text()
    assert "PACKET BODY {question}" in (ctx.prompts_dir / "packet.md").read_text()
    assert "VALIDATE BODY" in (ctx.prompts_dir / "validate.md").read_text()


def test_sync_is_idempotent(tmp_path):
    repo = _fake_trend_corpus(tmp_path, "x", [("A", "https://a.example/")])
    ctx = _runtime_ctx(tmp_path, "x")
    sync.run(ctx, repo)
    summary = sync.run(ctx, repo)
    assert summary["sources_added"] == []
    assert summary["sources_removed"] == []


def test_sync_missing_theme_raises(tmp_path):
    repo = _fake_trend_corpus(tmp_path, "x", [])
    ctx = _runtime_ctx(tmp_path, "y")   # different theme
    try:
        sync.run(ctx, repo)
        assert False, "should have raised"
    except FileNotFoundError as e:
        assert "trends/y" in str(e)
