"""Tests for envdiff.schema."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.schema import (
    SchemaRule,
    SchemaViolation,
    load_schema,
    validate,
)


@pytest.fixture()
def schema_file(tmp_path: Path) -> Path:
    data = {
        "keys": [
            {"key": "DATABASE_URL", "required": True, "pattern": "postgres://.+"},
            {"key": "DEBUG", "required": True, "pattern": "true|false"},
            {"key": "OPTIONAL_KEY", "required": False},
        ]
    }
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(data))
    return p


def test_load_schema_returns_rules(schema_file: Path) -> None:
    rules = load_schema(schema_file)
    assert len(rules) == 3
    assert rules[0].key == "DATABASE_URL"
    assert rules[0].required is True
    assert rules[0].pattern == "postgres://.+"


def test_load_schema_optional_key(schema_file: Path) -> None:
    rules = load_schema(schema_file)
    optional = next(r for r in rules if r.key == "OPTIONAL_KEY")
    assert optional.required is False


def test_validate_all_good() -> None:
    rules = [
        SchemaRule(key="DATABASE_URL", required=True, pattern="postgres://.+"),
        SchemaRule(key="DEBUG", required=True, pattern="true|false"),
    ]
    env = {"DATABASE_URL": "postgres://localhost/db", "DEBUG": "true"}
    result = validate(env, rules)
    assert result.ok
    assert result.violations == []


def test_validate_missing_required_key() -> None:
    rules = [SchemaRule(key="SECRET_KEY", required=True)]
    result = validate({}, rules)
    assert not result.ok
    assert result.violations[0].reason == "missing"
    assert result.violations[0].key == "SECRET_KEY"


def test_validate_missing_optional_key_no_violation() -> None:
    rules = [SchemaRule(key="OPTIONAL", required=False)]
    result = validate({}, rules)
    assert result.ok


def test_validate_pattern_mismatch() -> None:
    rules = [SchemaRule(key="PORT", required=True, pattern=r"\d+")]
    result = validate({"PORT": "not-a-number"}, rules)
    assert not result.ok
    v = result.violations[0]
    assert v.reason == "pattern_mismatch"
    assert v.key == "PORT"
    assert v.actual_value == "not-a-number"
    assert v.expected_pattern == r"\d+"


def test_validate_pattern_match_passes() -> None:
    rules = [SchemaRule(key="PORT", required=True, pattern=r"\d+")]
    result = validate({"PORT": "5432"}, rules)
    assert result.ok


def test_validate_none_value_counts_as_missing_for_required() -> None:
    rules = [SchemaRule(key="API_KEY", required=True)]
    result = validate({"API_KEY": None}, rules)
    assert not result.ok
    assert result.violations[0].reason == "missing"
