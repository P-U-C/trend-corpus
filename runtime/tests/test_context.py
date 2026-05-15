"""Tests for ThemeContext load_context + path resolution + Telegram resolution."""
from __future__ import annotations

import os

import yaml

from theme_runtime.context import ThemeContext, load_context


def test_load_context_minimal(tmp_path):
    cfg = tmp_path / "theme-config.yaml"
    runtime_root = tmp_path / "runtime-root"
    runtime_root.mkdir()
    cfg.write_text(yaml.safe_dump({
        "theme_id": "ai-infrastructure",
        "theme_name": "AI Infrastructure",
        "root": str(runtime_root),
    }))
    ctx = load_context(cfg)
    assert ctx.theme_id == "ai-infrastructure"
    assert ctx.theme_name == "AI Infrastructure"
    assert ctx.root == runtime_root.resolve()
    assert ctx.db_path == runtime_root.resolve() / "db.sqlite"
    assert ctx.prompts_dir == runtime_root.resolve() / "prompts"
    assert ctx.extract_model == "sonnet"
    assert ctx.packet_model == "opus"


def test_load_context_relative_root(tmp_path):
    cfg = tmp_path / "theme-config.yaml"
    (tmp_path / "rt").mkdir()
    cfg.write_text(yaml.safe_dump({
        "theme_id": "x",
        "theme_name": "X",
        "root": "rt",
    }))
    ctx = load_context(cfg)
    assert ctx.root == (tmp_path / "rt").resolve()


def test_load_context_missing_required(tmp_path):
    cfg = tmp_path / "bad.yaml"
    cfg.write_text(yaml.safe_dump({"theme_id": "x"}))
    try:
        load_context(cfg)
        assert False, "should have raised"
    except ValueError as e:
        assert "theme_name" in str(e) or "root" in str(e)


def test_resolve_telegram_from_env(tmp_path, monkeypatch):
    ctx = ThemeContext(theme_id="t", theme_name="T", root=tmp_path)
    monkeypatch.setenv("TG_BOT_TOKEN", "tok1")
    monkeypatch.setenv("TG_CHAT_ID", "555")
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    token, chat = ctx.resolve_telegram()
    assert token == "tok1"
    assert chat == "555"


def test_resolve_telegram_from_env_file(tmp_path, monkeypatch):
    envfile = tmp_path / ".env"
    envfile.write_text("TG_BOT_TOKEN=fromfile\nTG_CHAT_ID=999\n")
    monkeypatch.delenv("TG_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TG_CHAT_ID", raising=False)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    ctx = ThemeContext(
        theme_id="t", theme_name="T", root=tmp_path, telegram_env_file=envfile
    )
    token, chat = ctx.resolve_telegram()
    assert token == "fromfile"
    assert chat == "999"


def test_resolve_telegram_env_overrides_file(tmp_path, monkeypatch):
    envfile = tmp_path / ".env"
    envfile.write_text("TG_BOT_TOKEN=fromfile\nTG_CHAT_ID=fromfile\n")
    monkeypatch.setenv("TG_BOT_TOKEN", "fromenv")
    monkeypatch.setenv("TG_CHAT_ID", "envid")
    ctx = ThemeContext(
        theme_id="t", theme_name="T", root=tmp_path, telegram_env_file=envfile
    )
    token, chat = ctx.resolve_telegram()
    assert token == "fromenv"
    assert chat == "envid"
