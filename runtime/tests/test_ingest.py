"""Tests for source ingest idempotency and FK-preserving UPSERTs."""
from __future__ import annotations

import urllib.error
from unittest.mock import patch

from theme_runtime import ingest
from theme_runtime.context import ThemeContext
from theme_runtime.db import connect, init_schema


URL = "https://example.com/source"


def _ctx_with_source(tmp_path):
    (tmp_path / "sources.txt").write_text(f"{URL}\n")
    return ThemeContext(
        theme_id="ai-infrastructure",
        theme_name="AI Infrastructure",
        root=tmp_path,
        min_text_len=10,
    )


def _seed_source_with_claim(ctx):
    init_schema(ctx.db_path)
    db = connect(ctx.db_path)
    cur = db.execute(
        "INSERT INTO sources (url, fetched_at, raw_text, processed) "
        "VALUES (?, '2000-01-01 00:00:00', ?, 1)",
        (URL, "old text"),
    )
    source_id = cur.lastrowid
    db.execute(
        "INSERT INTO claims (source_id, claim, category, date_of_evidence) "
        "VALUES (?, 'existing claim', 'market', '2026-05-01')",
        (source_id,),
    )
    db.commit()
    db.close()
    return source_id


def test_ingest_upsert_preserves_source_id_with_existing_claim(tmp_path):
    ctx = _ctx_with_source(tmp_path)
    source_id = _seed_source_with_claim(ctx)

    with patch.object(ingest, "_fetch", return_value="fresh source text " * 5):
        summary = ingest.run(ctx)

    assert summary == {"urls": 1, "fetched": 1, "skipped": 0, "failed": 0}

    db = connect(ctx.db_path)
    row = db.execute(
        "SELECT id, raw_text, processed, error FROM sources WHERE url=?",
        (URL,),
    ).fetchone()
    claim_source_id = db.execute("SELECT source_id FROM claims").fetchone()[0]
    db.close()

    assert row[0] == source_id
    assert row[1] == "fresh source text " * 5
    assert row[2] == 0
    assert row[3] is None
    assert claim_source_id == source_id


def test_ingest_error_upsert_preserves_source_id_with_existing_claim(tmp_path):
    ctx = _ctx_with_source(tmp_path)
    source_id = _seed_source_with_claim(ctx)

    with patch.object(ingest, "_fetch", side_effect=urllib.error.URLError("boom")):
        summary = ingest.run(ctx)

    assert summary == {"urls": 1, "fetched": 0, "skipped": 0, "failed": 1}

    db = connect(ctx.db_path)
    row = db.execute(
        "SELECT id, raw_text, processed, error FROM sources WHERE url=?",
        (URL,),
    ).fetchone()
    claim_source_id = db.execute("SELECT source_id FROM claims").fetchone()[0]
    db.close()

    assert row[0] == source_id
    assert row[1] is None
    assert row[2] == 1
    assert "boom" in row[3]
    assert claim_source_id == source_id
