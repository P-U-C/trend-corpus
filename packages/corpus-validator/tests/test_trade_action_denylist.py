"""
Tests for the trade-action field denylist in the public corpus validator.

Public corpus objects must not declare fields that imply trade execution
(place_order, order_type, limit_price, stop_price, account_id,
quantity_to_trade). The validator must reject these whether they appear
at the top level, nested inside another field, or inside a list element.
"""
from pathlib import Path

from corpus_validator.validator import (
    TRADE_ACTION_DENYLIST,
    find_trade_action_keys,
    validate_repo,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_denylist_contents():
    """The denylist must match what the docs and the secret-scan also enforce."""
    assert "place_order" in TRADE_ACTION_DENYLIST
    assert "order_type" in TRADE_ACTION_DENYLIST
    assert "limit_price" in TRADE_ACTION_DENYLIST
    assert "stop_price" in TRADE_ACTION_DENYLIST
    assert "account_id" in TRADE_ACTION_DENYLIST
    assert "quantity_to_trade" in TRADE_ACTION_DENYLIST


def test_find_trade_action_keys_top_level():
    obj = {"id": "dp_x", "place_order": True}
    assert find_trade_action_keys(obj) == ["place_order"]


def test_find_trade_action_keys_nested():
    obj = {"id": "dp_x", "execution": {"limit_price": 10.0, "stop_price": 8.0}}
    hits = find_trade_action_keys(obj)
    assert "execution.limit_price" in hits
    assert "execution.stop_price" in hits


def test_find_trade_action_keys_inside_list():
    obj = {"id": "dp_x", "orders": [{"order_type": "limit"}, {"account_id": "U1"}]}
    hits = find_trade_action_keys(obj)
    assert "orders[0].order_type" in hits
    assert "orders[1].account_id" in hits


def test_clean_object_has_no_hits():
    obj = {
        "id": "dp_clean",
        "question": "Should we watch?",
        "verdict": "watchlist_candidate",
        "execution_state": "human_review_required",
        "supporting_theses": ["ths_a"],
        "invalidation_conditions": ["a", "b"],
        "schema_version": 1,
    }
    assert find_trade_action_keys(obj) == []


def test_real_repo_has_no_denylist_hits():
    """The shipped trend-corpus must not contain any denylisted field."""
    errors = validate_repo(REPO_ROOT)
    trade_action_errors = [e for e in errors if "trade-action field" in e]
    assert trade_action_errors == [], trade_action_errors
