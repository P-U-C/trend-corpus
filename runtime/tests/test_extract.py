"""Tests for the extract pipeline with the claude CLI mocked out."""
from __future__ import annotations

import json
from unittest.mock import patch

from theme_runtime import extract
from theme_runtime.context import ThemeContext
from theme_runtime.db import connect, init_schema


def _ctx_with_prompt(tmp_path):
    (tmp_path / "prompts").mkdir()
    (tmp_path / "prompts" / "extract.md").write_text(
        "EXTRACT prompt -- url={url} date={source_date} text-len={text}"
    )
    return ThemeContext(theme_id="ai-infrastructure", theme_name="AI Infra", root=tmp_path)


def _seed_one_source(ctx):
    init_schema(ctx.db_path)
    db = connect(ctx.db_path)
    db.execute(
        "INSERT INTO sources (url, raw_text, processed) VALUES (?, ?, 0)",
        ("https://example.com/x", "a fairly long body " * 30),
    )
    db.commit()
    db.close()


def test_extract_inserts_claims_and_marks_processed(tmp_path):
    ctx = _ctx_with_prompt(tmp_path)
    _seed_one_source(ctx)
    fake_output = "\n".join([
        json.dumps({
            "claim": "BIS export controls reduce China-bound advanced AI chip volume.",
            "category": "regulatory",
            "entities": ["nvidia", "bis"],
            "topics": ["export_controls", "accelerator"],
            "date_of_evidence": "2026-05-01",
            "half_life_days": 90,
            "confidence": 0.85,
        }),
        "",  # stray blank
        "not a json line",
        json.dumps({
            "claim": "HBM3e supply remains tight through 2026.",
            "category": "manufacturing",
            "entities": ["micron", "sk_hynix"],
            "topics": ["hbm"],
            "date_of_evidence": "2026-04-20",
            "confidence": 0.78,
        }),
    ])
    with patch.object(extract, "run_claude", return_value=fake_output):
        summary = extract.run(ctx, limit=10, model="sonnet")
    assert summary["sources_processed"] == 1
    assert summary["claims_inserted"] == 2

    db = connect(ctx.db_path)
    rows = db.execute(
        "SELECT category, entities, topics, half_life_days, confidence FROM claims"
    ).fetchall()
    assert len(rows) == 2
    cats = sorted(r[0] for r in rows)
    assert cats == ["manufacturing", "regulatory"]
    # legacy peptides field also accepted -- inject through the parser
    db.close()


def test_extract_accepts_legacy_peptides_field(tmp_path):
    ctx = _ctx_with_prompt(tmp_path)
    _seed_one_source(ctx)
    fake_output = json.dumps({
        "claim": "Legacy-style row with peptides field.",
        "category": "regulatory",
        "entities": ["fda"],
        "peptides": ["semaglutide"],   # legacy key name
        "date_of_evidence": "2026-05-01",
        "confidence": 0.8,
    })
    with patch.object(extract, "run_claude", return_value=fake_output):
        extract.run(ctx, limit=1)
    db = connect(ctx.db_path)
    topics = db.execute("SELECT topics FROM claims").fetchone()[0]
    assert json.loads(topics) == ["semaglutide"]
    db.close()


def test_extract_drops_malformed_rows(tmp_path):
    ctx = _ctx_with_prompt(tmp_path)
    _seed_one_source(ctx)
    fake_output = "\n".join([
        json.dumps({"claim": "ok claim", "category": "regulatory",
                    "date_of_evidence": "2026-05-01"}),
        json.dumps({"missing": "required fields"}),
        json.dumps({"claim": "no category", "date_of_evidence": "2026-05-01"}),
        "not even json",
        "{not valid json}",
    ])
    with patch.object(extract, "run_claude", return_value=fake_output):
        summary = extract.run(ctx, limit=1)
    assert summary["claims_inserted"] == 1


def test_extract_uses_default_half_life_from_context(tmp_path):
    ctx = _ctx_with_prompt(tmp_path)
    _seed_one_source(ctx)
    # Claim omits half_life_days; context default for 'regulatory' is 90
    fake_output = json.dumps({
        "claim": "Regulatory claim without explicit half life.",
        "category": "regulatory",
        "date_of_evidence": "2026-05-01",
    })
    with patch.object(extract, "run_claude", return_value=fake_output):
        extract.run(ctx, limit=1)
    db = connect(ctx.db_path)
    hl = db.execute("SELECT half_life_days FROM claims").fetchone()[0]
    assert hl == 90
    db.close()
