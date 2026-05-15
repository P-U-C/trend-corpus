import json
from pathlib import Path

from corpus_validator.validator import scan_secrets, validate_references, validate_theme


ROOT = Path(__file__).resolve().parents[1]


def test_every_schema_parses():
    for path in (ROOT / "schemas").glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))


def test_every_theme_directory_validates():
    for theme_dir in (ROOT / "trends").iterdir():
        if theme_dir.is_dir():
            errors, _ = validate_theme(ROOT, theme_dir)
            assert errors == []


def test_every_reference_resolves():
    assert validate_references(ROOT) == []


def test_no_secret_pattern_hits():
    assert scan_secrets(ROOT) == []


def test_decision_packets_have_invalidation_conditions():
    for path in (ROOT / "trends").glob("*/decision-packets/*"):
        if path.suffix not in {".yaml", ".yml", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        assert "invalidation_conditions:" in text
