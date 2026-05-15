from pathlib import Path

from corpus_validator.validator import scan_secrets, validate_repo


ROOT = Path(__file__).resolve().parents[3]


def test_repo_validates():
    assert validate_repo(ROOT) == []


def test_secret_scan_has_no_findings():
    assert scan_secrets(ROOT) == []

