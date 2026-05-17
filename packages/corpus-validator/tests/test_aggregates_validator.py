"""Validator-side checks for the aggregates files dropped under
trends/<theme>/aggregates/."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from corpus_validator.validator import validate_aggregates


ROOT = Path(__file__).resolve().parents[3]


def _mini_repo(tmp_path: Path, theme: str = "ai-infrastructure") -> Path:
    """Build a tiny repo skeleton with just schemas/ and trends/<theme>/aggregates/."""
    repo = tmp_path / "repo"
    (repo / "schemas").mkdir(parents=True)
    (repo / "trends" / theme / "aggregates").mkdir(parents=True)
    shutil.copy(ROOT / "schemas" / "aggregates.schema.json", repo / "schemas")
    return repo


def _good_payload(theme: str = "ai-infrastructure") -> dict:
    return {
        "schema_version": "0.1.0",
        "generated_at": "2026-05-17T00:00:00Z",
        "theme_id": theme,
        "generator": {
            "name": "theme-runtime-aggregates-exporter",
            "version": "0.1.0",
            "host_alias": "test-host",
        },
        "underlying_claim_count": 0,
        "underlying_source_count": 0,
        "min_count_threshold": 3,
        "windows": {
            "30d": {"claims_total": 0, "claims_by_category": {}, "top_entities": []},
            "90d": {"claims_total": 0, "claims_by_category": {}, "top_entities": []},
            "365d": {"claims_total": 0, "claims_by_category": {}, "top_entities": []},
        },
        "source_freshness": [],
    }


def test_good_aggregates_passes(tmp_path):
    repo = _mini_repo(tmp_path)
    out = repo / "trends" / "ai-infrastructure" / "aggregates" / "ai-infrastructure-aggregates.json"
    out.write_text(json.dumps(_good_payload()))
    assert validate_aggregates(repo) == []


def test_no_aggregates_dir_passes(tmp_path):
    repo = _mini_repo(tmp_path)
    # leave the aggregates dir empty
    assert validate_aggregates(repo) == []


def test_theme_id_mismatch_caught(tmp_path):
    repo = _mini_repo(tmp_path)
    out = repo / "trends" / "ai-infrastructure" / "aggregates" / "ai-infrastructure-aggregates.json"
    payload = _good_payload(theme="solid-state-battery")  # wrong on purpose
    out.write_text(json.dumps(payload))
    errors = validate_aggregates(repo)
    assert any("theme_id" in e for e in errors)


def test_missing_required_field_caught(tmp_path):
    repo = _mini_repo(tmp_path)
    out = repo / "trends" / "ai-infrastructure" / "aggregates" / "ai-infrastructure-aggregates.json"
    payload = _good_payload()
    payload.pop("theme_id")
    out.write_text(json.dumps(payload))
    errors = validate_aggregates(repo)
    assert any("missing required" in e for e in errors)


def test_extra_top_level_field_caught(tmp_path):
    repo = _mini_repo(tmp_path)
    out = repo / "trends" / "ai-infrastructure" / "aggregates" / "ai-infrastructure-aggregates.json"
    payload = _good_payload()
    payload["raw_claims"] = ["sensitive!"]
    out.write_text(json.dumps(payload))
    errors = validate_aggregates(repo)
    assert any("not in schema" in e for e in errors)


def test_negative_counts_caught(tmp_path):
    repo = _mini_repo(tmp_path)
    out = repo / "trends" / "ai-infrastructure" / "aggregates" / "ai-infrastructure-aggregates.json"
    payload = _good_payload()
    payload["underlying_claim_count"] = -1
    out.write_text(json.dumps(payload))
    errors = validate_aggregates(repo)
    assert any("underlying_claim_count" in e for e in errors)


def test_invalid_json_caught(tmp_path):
    repo = _mini_repo(tmp_path)
    out = repo / "trends" / "ai-infrastructure" / "aggregates" / "ai-infrastructure-aggregates.json"
    out.write_text("{not valid json")
    errors = validate_aggregates(repo)
    assert any("invalid JSON" in e for e in errors)
