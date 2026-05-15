import json
from pathlib import Path

import yaml

from corpus_validator.validator import check_schema, load_schema, validate_theme


ROOT = Path(__file__).resolve().parents[3]


def load_object(path):
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def assert_valid(data, schema_name):
    errors = check_schema(data, load_schema(ROOT, schema_name), Path(schema_name))
    assert errors == []


def test_provider_observation_schema_parses_and_validates_example():
    json.loads((ROOT / "schemas/provider-observation.schema.json").read_text(encoding="utf-8"))
    example = {
        "id": "obs_swell_provider_x_2026_05_15_0001",
        "type": "provider_observation",
        "theme_id": "swell_checker",
        "provider": "provider_x",
        "query_ref": "glp1_channel_availability",
        "fetched_at": "2026-05-15T06:30:00Z",
        "raw_locator": "private://provider_x/2026-05-15/0001.json",
        "normalized_fields": {},
        "quality_status": "dirty",
        "quality_errors": ["missing_required_field:price", "inconsistent_timestamp"],
        "usable_for_scoring": False,
        "visibility": {"classification": "semi_private"},
    }
    assert_valid(example, "provider-observation.schema.json")


def test_scanner_seed_schema_parses_and_validates_plan_example():
    json.loads((ROOT / "schemas/scanner-seed.schema.json").read_text(encoding="utf-8"))
    example = {
        "schema_version": "1",
        "generated_at": "2026-05-15T06:30:00Z",
        "generator": {"name": "theme-opportunity-generator", "version": "0.1.0"},
        "themes": [{"theme_id": "peptides", "theme_name": "Peptides", "status": "emerging"}],
        "scores": [
            {
                "ticker": "BANB",
                "theme_id": "peptides",
                "theme": "Peptides",
                "score": 0.74,
                "tier": "HIGH",
                "status": "emerging",
                "row_sources": ["theme_opportunity_generator"],
                "source_claim_ids": ["clm_peptides_capacity_cdmo_2026_05_15"],
                "source_capture_ids": [],
                "score_components": {
                    "evidence_strength": 0.82,
                    "freshness_weight": 0.76,
                    "exposure_strength": 0.91,
                    "catalyst_weight": 0.65,
                    "tradability_weight": 0.60,
                    "data_quality_weight": 1.00,
                },
            }
        ],
    }
    assert_valid(example, "scanner-seed.schema.json")


def test_scanner_output_schema_parses_and_validates_minimal_dashboard_shape():
    json.loads((ROOT / "schemas/scanner-output.schema.json").read_text(encoding="utf-8"))
    example = {"scan_meta": {}, "results": [], "convergence": []}
    assert_valid(example, "scanner-output.schema.json")


def test_entity_with_ticker_exposures_validates():
    entity = {
        "id": "ent_example",
        "name": "Example Company",
        "entity_type": "public_company",
        "schema_version": 1,
        "identifiers": {"ticker": "EXM", "exchange": "NYSE"},
        "ticker_exposures": [
            {
                "ticker": "EXM",
                "direction": "beneficiary",
                "exposure_strength": 0.75,
                "basis": ["revenue_segment", "demand_channel"],
                "tradable": True,
            }
        ],
    }
    assert_valid(entity, "entity.schema.json")


def test_claim_with_visibility_validates():
    claim = {
        "id": "clm_example_visibility",
        "claim": "Example claim text for a public visibility test.",
        "category": "manufacturing",
        "source_ids": ["src_example"],
        "date_of_evidence": "2026-05-15",
        "confidence": 0.8,
        "visibility": {"classification": "public_full", "strategy_leakage_risk": "low"},
        "schema_version": 1,
    }
    assert_valid(claim, "claim.schema.json")


def test_existing_peptides_entities_validate_with_backward_compat_fields():
    schema = load_schema(ROOT, "entity.schema.json")
    for entity_path in sorted((ROOT / "trends/peptides/entities").glob("*.yaml")):
        entity = load_object(entity_path)
        errors = check_schema(entity, schema, entity_path)
        assert errors == []


def test_regression_existing_themes_validate():
    for theme in ("peptides", "llm-convergence"):
        errors, _ = validate_theme(ROOT, ROOT / "trends" / theme)
        assert errors == []
