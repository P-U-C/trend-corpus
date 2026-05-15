from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


class ValidationError(Exception):
    pass


OBJECT_TYPES = {
    "sources": ("src_", "source.schema.json"),
    "claims": ("clm_", "claim.schema.json"),
    "entities": ("ent_", "entity.schema.json"),
    "events": ("evt_", "event.schema.json"),
    "theses": ("ths_", "thesis.schema.json"),
    "decision-packets": ("dp_", "decision-packet.schema.json"),
    "watchlists": ("wl_", "watchlist.schema.json"),
}

REFERENCE_FIELDS = {
    "source_ids",
    "supporting_claims",
    "supporting_theses",
    "related_entities",
    "related_events",
}

SECRET_PATTERNS = [
    r"OPENAI_API_KEY",
    r"ANTHROPIC_API_KEY",
    r"GITHUB_TOKEN",
    r"TELEGRAM_BOT_TOKEN",
    r"AWS_(ACCESS_KEY_ID|SECRET_ACCESS_KEY)",
    r"IBKR",
    r"PRIVATE_KEY",
    r"MNEMONIC",
    r"ghp_[A-Za-z0-9_]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"sk-[A-Za-z0-9]{20,}",
    r"xox[baprs]-[A-Za-z0-9-]{10,}",
    r"-----BEGIN (RSA|OPENSSH|EC|DSA|PGP) PRIVATE KEY-----",
    r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"][^'\"]+['\"]",
]

SECRET_EXCLUDED = {
    Path("SECURITY.md"),
    Path("packages/corpus-validator/corpus_validator/validator.py"),
}


def load_data(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    if path.suffix in {".yaml", ".yml"}:
        if yaml is None:
            raise ValidationError(f"{path}: PyYAML is required for YAML files")
        return yaml.safe_load(text)
    raise ValidationError(f"{path}: unsupported file extension")


def load_schema(repo: Path, schema_name: str) -> dict[str, Any]:
    return load_data(repo / "schemas" / schema_name)


def _type_ok(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    return True


def check_schema(data: Any, schema: dict[str, Any], path: Path) -> list[str]:
    errors: list[str] = []
    if not _type_ok(data, schema.get("type", "object")):
        return [f"{path}: expected {schema.get('type')}"]
    if not isinstance(data, dict):
        return errors

    for field in schema.get("required", []):
        if field not in data:
            errors.append(f"{path}: missing required field {field}")

    properties = schema.get("properties", {})
    for key, rules in properties.items():
        if key not in data:
            continue
        value = data[key]
        expected = rules.get("type")
        if expected and not _type_ok(value, expected):
            errors.append(f"{path}: field {key} expected {expected}")
            continue
        if "enum" in rules and value not in rules["enum"]:
            errors.append(f"{path}: field {key} value {value!r} not in enum")
        if "pattern" in rules and isinstance(value, str) and not re.search(rules["pattern"], value):
            errors.append(f"{path}: field {key} does not match {rules['pattern']}")
        if "minItems" in rules and isinstance(value, list) and len(value) < rules["minItems"]:
            errors.append(f"{path}: field {key} must have at least {rules['minItems']} items")
    return errors


def iter_object_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix in {".yaml", ".yml", ".json"}
    )


def validate_schemas_parse(repo: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted((repo / "schemas").glob("*.json")):
        try:
            load_data(path)
        except Exception as exc:
            errors.append(f"{path}: schema parse failed: {exc}")
    return errors


def validate_theme(repo: Path, theme_dir: Path) -> tuple[list[str], dict[str, dict[str, Any]]]:
    errors: list[str] = []
    index: dict[str, dict[str, Any]] = {}
    trend_path = theme_dir / "trend.yaml"
    if not trend_path.exists():
        return [f"{theme_dir}: missing trend.yaml"], index

    trend = load_data(trend_path)
    errors.extend(check_schema(trend, load_schema(repo, "trend.schema.json"), trend_path))
    if trend.get("id") != theme_dir.name and theme_dir.name != "_template":
        errors.append(f"{trend_path}: id must match directory name")

    objects = trend.get("objects", {})
    for object_type, (prefix, schema_name) in OBJECT_TYPES.items():
        folder_name = objects.get(object_type)
        if not folder_name:
            errors.append(f"{trend_path}: objects missing {object_type}")
            continue
        folder = theme_dir / folder_name
        if not folder.is_dir():
            errors.append(f"{trend_path}: declared folder does not exist: {folder_name}")
            continue
        schema = load_schema(repo, schema_name)
        for path in iter_object_files(folder):
            obj = load_data(path)
            errors.extend(check_schema(obj, schema, path))
            obj_id = obj.get("id")
            if not isinstance(obj_id, str) or not obj_id.startswith(prefix):
                errors.append(f"{path}: id must start with {prefix}")
            elif obj_id in index:
                errors.append(f"{path}: duplicate id {obj_id}")
            else:
                index[obj_id] = {"object": obj, "path": path, "type": object_type}
            if object_type == "decision-packets":
                if obj.get("execution_state") == "approved_for_private_execution":
                    errors.append(f"{path}: public corpus forbids approved_for_private_execution")
                if not obj.get("invalidation_conditions"):
                    errors.append(f"{path}: decision-packet requires invalidation_conditions")

    for item in index.values():
        obj = item["object"]
        path = item["path"]
        for field in REFERENCE_FIELDS:
            refs = obj.get(field, [])
            if isinstance(refs, str):
                refs = [refs]
            if not refs:
                continue
            if not isinstance(refs, list):
                errors.append(f"{path}: reference field {field} must be a list")
                continue
            for ref in refs:
                if ref not in index:
                    errors.append(f"{path}: unresolved reference {ref} in {field}")

    return errors, index


def validate_references(repo: Path) -> list[str]:
    errors: list[str] = []
    for theme_dir in sorted((repo / "trends").iterdir()):
        if theme_dir.is_dir():
            theme_errors, _ = validate_theme(repo, theme_dir)
            errors.extend(theme_errors)
    return errors


def scan_secrets(repo: str | Path) -> list[str]:
    repo = Path(repo).resolve()
    findings: list[str] = []
    compiled = [re.compile(pattern) for pattern in SECRET_PATTERNS]
    for path in sorted(repo.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(repo)
        if rel in SECRET_EXCLUDED or ".git" in rel.parts or "__pycache__" in rel.parts:
            continue
        if path.suffix.lower() in {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".zip", ".tar", ".gz"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in compiled:
            if pattern.search(text):
                findings.append(f"{rel}: matched secret pattern")
                break
    return findings


def validate_repo(repo: str | Path) -> list[str]:
    root = Path(repo).resolve()
    errors: list[str] = []
    errors.extend(validate_schemas_parse(root))
    errors.extend(validate_references(root))
    for finding in scan_secrets(root):
        errors.append(f"secret scan: {finding}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="corpus_validator")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("repo", nargs="?", default=".")
    args = parser.parse_args(argv)

    if args.command == "validate":
        errors = validate_repo(args.repo)
        if errors:
            for error in errors:
                print(error)
            return 1
        print("validation passed")
        return 0
    return 1
