"""Tests for envdiff.differ_drift."""
import json
import pytest
from pathlib import Path

from envdiff.comparator import DiffResult
from envdiff.differ_drift import (
    DriftReport,
    save_snapshot,
    load_snapshot,
    detect_drift,
)


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "drift_store"


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(only_in_a=set(), only_in_b=set(), mismatched={})


@pytest.fixture()
def rich_result() -> DiffResult:
    return DiffResult(
        only_in_a={"GONE_KEY"},
        only_in_b={"NEW_KEY"},
        mismatched={"DB_URL": ("old", "new")},
    )


def test_save_creates_file(store, rich_result):
    path = save_snapshot(rich_result, store, "prod")
    assert path.exists()


def test_save_content_is_valid_json(store, rich_result):
    path = save_snapshot(rich_result, store, "prod")
    data = json.loads(path.read_text())
    assert "only_in_a" in data
    assert "only_in_b" in data
    assert "mismatched" in data


def test_load_returns_none_when_missing(store):
    assert load_snapshot(store, "nonexistent") is None


def test_load_roundtrip(store, rich_result):
    save_snapshot(rich_result, store, "prod")
    loaded = load_snapshot(store, "prod")
    assert loaded is not None
    assert loaded.only_in_a == rich_result.only_in_a
    assert loaded.only_in_b == rich_result.only_in_b
    assert loaded.mismatched == rich_result.mismatched


def test_detect_drift_clean_when_identical(rich_result):
    report = detect_drift(rich_result, rich_result)
    assert report.is_clean


def test_detect_drift_appeared_key(empty_result, rich_result):
    report = detect_drift(empty_result, rich_result)
    assert "GONE_KEY" in report.appeared
    assert "NEW_KEY" in report.appeared
    assert "DB_URL" in report.appeared


def test_detect_drift_resolved_key(rich_result, empty_result):
    report = detect_drift(rich_result, empty_result)
    assert "GONE_KEY" in report.resolved
    assert "NEW_KEY" in report.resolved


def test_detect_drift_changed_value(store):
    prev = DiffResult(only_in_a=set(), only_in_b=set(), mismatched={"HOST": ("a", "b")})
    curr = DiffResult(only_in_a=set(), only_in_b=set(), mismatched={"HOST": ("a", "c")})
    report = detect_drift(prev, curr)
    assert "HOST" in report.changed
    assert report.changed["HOST"] == (("a", "b"), ("a", "c"))


def test_as_dict_structure(rich_result, empty_result):
    report = detect_drift(empty_result, rich_result)
    d = report.as_dict()
    assert isinstance(d["appeared"], list)
    assert isinstance(d["resolved"], list)
    assert isinstance(d["changed"], dict)
