"""Tests for theme_runtime.aggregates."""
from __future__ import annotations

import json
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pytest

from theme_runtime import aggregates, db
from theme_runtime.context import ThemeContext


def _runtime_ctx(tmp_path: Path, theme_id: str = "ai-infrastructure") -> ThemeContext:
    root = tmp_path / "runtime"
    root.mkdir()
    return ThemeContext(theme_id=theme_id, theme_name="X", root=root)


def _seed_db(db_path: Path, *, rows: list[tuple[str, list[str], list[str], int]]) -> None:
    """Initialize schema and insert claims. Each row is (category, entities,
    topics, days_ago_for_date_of_evidence)."""
    db.init_schema(db_path)
    conn = sqlite3.connect(str(db_path))
    try:
        # One source so the FK lines up.
        conn.execute("INSERT INTO sources (url, processed) VALUES ('https://x.test/', 1)")
        sid = conn.execute("SELECT id FROM sources").fetchone()[0]
        for cat, ents, tops, days_ago in rows:
            d = (date.today() - timedelta(days=days_ago)).isoformat()
            conn.execute(
                "INSERT INTO claims (source_id, claim, category, entities, topics, "
                "date_of_evidence) VALUES (?, ?, ?, ?, ?, ?)",
                (sid, "redacted", cat, json.dumps(ents), json.dumps(tops), d),
            )
        conn.commit()
    finally:
        conn.close()


def test_build_empty_db_produces_valid_payload(tmp_path):
    ctx = _runtime_ctx(tmp_path)
    db.init_schema(ctx.db_path)
    payload = aggregates.build(ctx, min_count=1)
    aggregates.validate_payload(payload)
    assert payload["theme_id"] == "ai-infrastructure"
    assert payload["underlying_claim_count"] == 0
    assert payload["underlying_source_count"] == 0
    assert set(payload["windows"]) == {"30d", "90d", "365d"}
    for window in payload["windows"].values():
        assert window["claims_total"] == 0
        assert window["top_entities"] == []
        # sector themes omit top_peptides
        assert "top_peptides" not in window


def test_window_counts_and_top_entities(tmp_path):
    ctx = _runtime_ctx(tmp_path)
    # 5 claims this week mentioning AMBA; 1 claim 100 days ago mentioning SYNA.
    _seed_db(ctx.db_path, rows=[
        ("market",    ["amba"], [], 3),
        ("market",    ["amba"], [], 5),
        ("supply",    ["amba", "tsmc"], [], 10),
        ("supply",    ["amba"], [], 15),
        ("regulatory", ["amba", "bis"], [], 20),
        ("research", ["syna"], [], 100),
    ])
    payload = aggregates.build(ctx, min_count=2)
    aggregates.validate_payload(payload)

    w30 = payload["windows"]["30d"]
    assert w30["claims_total"] == 5
    assert w30["claims_by_category"] == {"market": 2, "supply": 2, "regulatory": 1}
    # amba mentioned 5 times in 30d window, passes min_count=2
    amba_row = next(e for e in w30["top_entities"] if e["slug"] == "amba")
    assert amba_row["mentions"] == 5
    # tsmc and bis only mentioned once, below threshold of 2 -- suppressed
    assert all(e["slug"] not in {"tsmc", "bis"} for e in w30["top_entities"])

    w365 = payload["windows"]["365d"]
    assert w365["claims_total"] == 6
    # syna only mentioned once -- still suppressed at min_count=2
    assert all(e["slug"] != "syna" for e in w365["top_entities"])


def test_peptide_theme_emits_top_peptides(tmp_path):
    ctx = _runtime_ctx(tmp_path, theme_id="peptides")
    _seed_db(ctx.db_path, rows=[
        ("clinical", ["lly"],  ["tirzepatide"], 5),
        ("clinical", ["nvo"],  ["tirzepatide"], 6),
        ("clinical", ["lly"],  ["tirzepatide"], 7),
    ])
    payload = aggregates.build(ctx, min_count=2)
    aggregates.validate_payload(payload)
    assert payload["theme_id"] == "peptides"
    w30 = payload["windows"]["30d"]
    assert "top_peptides" in w30
    tirz = next(p for p in w30["top_peptides"] if p["name"] == "tirzepatide")
    assert tirz["mentions"] == 3


def test_min_count_must_be_positive(tmp_path):
    ctx = _runtime_ctx(tmp_path)
    db.init_schema(ctx.db_path)
    with pytest.raises(ValueError):
        aggregates.build(ctx, min_count=0)


def test_validate_payload_rejects_missing_field(tmp_path):
    bad = {
        "schema_version": "0.1.0",
        # theme_id intentionally missing
        "generated_at": "2026-05-17T00:00:00Z",
        "underlying_claim_count": 0,
        "underlying_source_count": 0,
        "min_count_threshold": 3,
        "windows": {},
    }
    with pytest.raises(ValueError, match="missing required"):
        aggregates.validate_payload(bad)


def test_validate_payload_rejects_extra_top_level_field(tmp_path):
    ctx = _runtime_ctx(tmp_path)
    db.init_schema(ctx.db_path)
    payload = aggregates.build(ctx, min_count=1)
    payload["extra_key"] = "not allowed"
    with pytest.raises(ValueError, match="not in schema"):
        aggregates.validate_payload(payload)


def test_write_payload_atomic(tmp_path):
    ctx = _runtime_ctx(tmp_path)
    db.init_schema(ctx.db_path)
    payload = aggregates.build(ctx, min_count=1)
    out = tmp_path / "out" / "ai-infrastructure-aggregates.json"
    aggregates.write_payload(payload, out)
    assert out.exists()
    loaded = json.loads(out.read_text())
    assert loaded["theme_id"] == "ai-infrastructure"
    # tmp sidecar cleaned up
    assert not (out.parent / (out.name + ".tmp")).exists()


def test_default_out_path_matches_spec(tmp_path):
    ctx = _runtime_ctx(tmp_path)
    p = aggregates.default_out_path(ctx)
    assert p == ctx.root / "out" / "ai-infrastructure-aggregates.json"
