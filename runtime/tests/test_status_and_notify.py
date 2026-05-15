"""Tests for status summary + notify message formatting (no network)."""
from __future__ import annotations

from unittest.mock import patch

from theme_runtime import notify, status
from theme_runtime.context import ThemeContext
from theme_runtime.db import connect, init_schema


def _ctx(tmp_path):
    return ThemeContext(theme_id="ai-infrastructure", theme_name="AI Infra", root=tmp_path)


def _seed(ctx):
    init_schema(ctx.db_path)
    db = connect(ctx.db_path)
    db.execute("INSERT INTO sources (url, raw_text, processed) VALUES (?,?,1)",
               ("https://a.example/", "body"))
    db.execute("INSERT INTO sources (url, raw_text, processed, error) VALUES (?,?,1,?)",
               ("https://b.example/", None, "fetch failed"))
    db.execute(
        "INSERT INTO claims (source_id, claim, category, topics, date_of_evidence, "
        " half_life_days, confidence) VALUES (?,?,?,?,?,?,?)",
        (1, "fresh claim", "regulatory", "[]", "2026-05-15", 90, 0.85),
    )
    db.execute(
        "INSERT INTO claims (source_id, claim, category, topics, date_of_evidence, "
        " half_life_days, confidence, superseded_by) VALUES (?,?,?,?,?,?,?,?)",
        (1, "superseded", "market", "[]", "2026-04-01", 60, 0.7, 1),
    )
    db.commit()
    db.close()


def test_status_summary(tmp_path):
    ctx = _ctx(tmp_path)
    _seed(ctx)
    s = status.summary(ctx)
    assert s["theme_id"] == "ai-infrastructure"
    assert s["sources_total"] == 2
    assert s["sources_processed"] == 2
    assert s["sources_errored"] == 1
    assert s["claims_total"] == 2
    assert s["claims_active"] == 1


def test_notify_alert_skips_silently_without_creds(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("TG_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TG_CHAT_ID", raising=False)
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    ctx = _ctx(tmp_path)
    assert notify.alert(ctx, "something broke") is False


def test_notify_alert_sends_with_creds(tmp_path, monkeypatch):
    monkeypatch.setenv("TG_BOT_TOKEN", "x")
    monkeypatch.setenv("TG_CHAT_ID", "1")
    ctx = _ctx(tmp_path)
    ctx.message_prefix = "[ai-infra]"

    captured = {}
    class FakeResp:
        status = 200
        def __enter__(self): return self
        def __exit__(self, *a): pass
    def fake_urlopen(url, data=None, timeout=None):
        captured["url"] = url
        captured["data"] = data
        return FakeResp()
    with patch("theme_runtime.notify.urllib.request.urlopen", side_effect=fake_urlopen):
        assert notify.alert(ctx, "BOOM") is True
    assert "api.telegram.org/botx" in captured["url"]
    assert b"chat_id=1" in captured["data"]
    assert b"%5Bai-infra%5D" in captured["data"]  # [ai-infra] urlencoded
    assert b"BOOM" in captured["data"]


def test_notify_digest_shape(tmp_path, monkeypatch):
    monkeypatch.setenv("TG_BOT_TOKEN", "x")
    monkeypatch.setenv("TG_CHAT_ID", "1")
    ctx = _ctx(tmp_path)
    _seed(ctx)

    sent = {}
    class FakeResp:
        status = 200
        def __enter__(self): return self
        def __exit__(self, *a): pass
    def fake_urlopen(url, data=None, timeout=None):
        sent["data"] = data
        return FakeResp()
    with patch("theme_runtime.notify.urllib.request.urlopen", side_effect=fake_urlopen):
        assert notify.digest(ctx) is True
    body = sent["data"].decode()
    assert "ai-infrastructure" in body
    assert "active" in body
