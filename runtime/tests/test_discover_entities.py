"""Tests for theme_runtime.discover_entities."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import yaml

from theme_runtime import discover_entities
from theme_runtime.context import ThemeContext
from theme_runtime.db import connect, init_schema


def _make_corpus(tmp_path: Path, known_entities: list[str]) -> Path:
    """Build a tiny trend-corpus checkout with entities/."""
    theme_dir = tmp_path / "tc" / "trends" / "x"
    (theme_dir / "entities").mkdir(parents=True)
    for slug in known_entities:
        body = {
            "id": f"ent_{slug}",
            "name": slug.title(),
            "entity_type": "public_company",
            "schema_version": 1,
            "slug": slug,
        }
        (theme_dir / "entities" / f"ent_{slug}.yaml").write_text(yaml.safe_dump(body))
    return tmp_path / "tc"


def _ctx_with_claims(tmp_path: Path, claim_entities: list[list[str]]) -> ThemeContext:
    """Build a runtime context with seeded claims."""
    root = tmp_path / "rt"
    root.mkdir()
    ctx = ThemeContext(theme_id="x", theme_name="X", root=root)
    init_schema(ctx.db_path)
    db = connect(ctx.db_path)
    for i, ents in enumerate(claim_entities):
        db.execute(
            "INSERT INTO sources (url) VALUES (?)", (f"https://s.example/{i}",)
        )
        db.execute(
            "INSERT INTO claims (source_id, claim, category, entities, date_of_evidence) "
            "VALUES (?, ?, ?, ?, ?)",
            (i + 1, f"claim {i}", "regulatory", json.dumps(ents), "2026-05-01"),
        )
    db.commit()
    db.close()
    return ctx


def test_no_unknown_when_db_empty(tmp_path):
    repo = _make_corpus(tmp_path, ["nvidia"])
    ctx = _ctx_with_claims(tmp_path, [])
    summary = discover_entities.run(ctx, repo)
    assert summary["unknown_count"] == 0
    assert summary["drafts"] == []


def test_no_unknown_when_all_known(tmp_path):
    repo = _make_corpus(tmp_path, ["nvidia", "broadcom"])
    ctx = _ctx_with_claims(tmp_path, [["nvidia"], ["broadcom"]])
    summary = discover_entities.run(ctx, repo)
    assert summary["unknown_count"] == 0


def test_drafts_only_unknown_slugs(tmp_path):
    repo = _make_corpus(tmp_path, ["nvidia"])
    ctx = _ctx_with_claims(tmp_path, [["nvidia", "credo", "marvell"]])
    fake_jsonl = "\n".join([
        json.dumps({
            "slug": "credo", "tradable": True, "ticker": "CRDO",
            "exchange": "NASDAQ", "entity_type": "public_company",
            "name": "Credo Technology", "role": "AI interconnects",
            "confidence": 0.9,
        }),
        json.dumps({
            "slug": "marvell", "tradable": True, "ticker": "MRVL",
            "exchange": "NASDAQ", "entity_type": "public_company",
            "name": "Marvell Technology", "role": "Custom AI silicon",
            "confidence": 0.95,
        }),
    ])
    with patch.object(discover_entities, "run_claude", return_value=fake_jsonl) as mock:
        summary = discover_entities.run(ctx, repo)
    assert mock.called
    # Only credo + marvell should be in the prompt -- nvidia is already known
    sent_prompt = mock.call_args[0][0]
    assert "credo" in sent_prompt
    assert "marvell" in sent_prompt
    assert "nvidia" not in sent_prompt.lower().split("slugs to classify:")[1]

    assert summary["unknown_count"] == 2
    assert sorted(summary["unknown_slugs"]) == ["credo", "marvell"]
    assert len(summary["drafts"]) == 2
    # Verify a draft was written properly
    draft = yaml.safe_load(Path(summary["drafts"][0]).read_text())
    assert draft["id"] in {"ent_credo", "ent_marvell"}
    assert draft["entity_type"] == "public_company"
    assert "ticker_exposures" in draft
    assert "REVIEW BEFORE COMMITTING" in draft["notes"]


def test_drops_drafts_with_malformed_slug(tmp_path):
    repo = _make_corpus(tmp_path, [])
    ctx = _ctx_with_claims(tmp_path, [["foo"]])
    fake_jsonl = "\n".join([
        json.dumps({
            "slug": "foo", "tradable": False, "ticker": None,
            "exchange": None, "entity_type": "private_company",
            "name": "Foo", "role": "test",
            "confidence": 0.8,
        }),
        json.dumps({"slug": "1invalid", "tradable": True}),
        "not a json line",
    ])
    with patch.object(discover_entities, "run_claude", return_value=fake_jsonl):
        summary = discover_entities.run(ctx, repo)
    # Only 'foo' survives; '1invalid' rejected by ENTITY_SLUG_RE
    assert len(summary["drafts"]) == 1


def test_known_entity_inferred_from_id_when_slug_missing(tmp_path):
    """Some peptides entities don't have an explicit `slug` field but the id starts with ent_."""
    theme_dir = tmp_path / "tc" / "trends" / "x"
    (theme_dir / "entities").mkdir(parents=True)
    body = {"id": "ent_lilly", "name": "Eli Lilly",
            "entity_type": "public_company", "schema_version": 1}
    (theme_dir / "entities" / "ent_lilly.yaml").write_text(yaml.safe_dump(body))
    ctx = _ctx_with_claims(tmp_path, [["lilly"]])  # known via id-suffix inference
    with patch.object(discover_entities, "run_claude") as mock:
        summary = discover_entities.run(ctx, tmp_path / "tc")
    # Should NOT call claude -- lilly inferred as known
    assert not mock.called
    assert summary["unknown_count"] == 0
