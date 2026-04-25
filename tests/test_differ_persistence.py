"""Tests for envdiff.differ_persistence."""
from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_persistence import PersistenceEntry, PersistenceReport, persistence_diff


def _result(
    matching: dict | None = None,
    only_in_a: set | None = None,
    only_in_b: set | None = None,
    mismatched: dict | None = None,
) -> DiffResult:
    return DiffResult(
        matching=matching or {},
        only_in_a=only_in_a or set(),
        only_in_b=only_in_b or set(),
        mismatched=mismatched or {},
    )


def test_empty_results_gives_empty_report():
    report = persistence_diff([])
    assert isinstance(report, PersistenceReport)
    assert report.entries == []


def test_single_result_matching_key_has_full_persistence():
    r = _result(matching={"KEY": "val"})
    report = persistence_diff([r])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.key == "KEY"
    assert entry.unchanged_runs == 1
    assert entry.total_runs == 1
    assert entry.persistence_rate == 1.0
    assert entry.is_persistent is True


def test_single_result_missing_key_has_zero_persistence():
    r = _result(only_in_a={"GONE"})
    report = persistence_diff([r])
    entry = report.entries[0]
    assert entry.unchanged_runs == 0
    assert entry.persistence_rate == 0.0
    assert entry.is_persistent is False


def test_key_stable_across_all_results_is_persistent():
    results = [_result(matching={"DB_HOST": "localhost"}) for _ in range(5)]
    report = persistence_diff(results)
    entry = report.entries[0]
    assert entry.unchanged_runs == 5
    assert entry.persistence_rate == 1.0
    assert entry.is_persistent is True


def test_key_changing_in_every_result_is_volatile():
    results = [_result(mismatched={"API_KEY": ("old", "new")}) for _ in range(5)]
    report = persistence_diff(results)
    entry = report.entries[0]
    assert entry.unchanged_runs == 0
    assert entry.persistence_rate == 0.0
    assert entry.is_persistent is False


def test_volatile_returns_non_persistent_entries():
    results = [
        _result(matching={"STABLE": "x", "FLAKY": "a"}),
        _result(matching={"STABLE": "x"}, mismatched={"FLAKY": ("a", "b")}),
        _result(matching={"STABLE": "x"}, mismatched={"FLAKY": ("b", "c")}),
        _result(matching={"STABLE": "x"}, mismatched={"FLAKY": ("c", "d")}),
        _result(matching={"STABLE": "x"}, mismatched={"FLAKY": ("d", "e")}),
    ]
    report = persistence_diff(results)
    volatile_keys = [e.key for e in report.volatile()]
    assert "FLAKY" in volatile_keys
    assert "STABLE" not in volatile_keys


def test_persistent_returns_stable_entries():
    results = [
        _result(matching={"ROCK_SOLID": "1"}),
        _result(matching={"ROCK_SOLID": "1"}),
    ]
    report = persistence_diff(results)
    persistent_keys = [e.key for e in report.persistent()]
    assert "ROCK_SOLID" in persistent_keys


def test_as_dict_contains_expected_keys():
    r = _result(matching={"X": "y"})
    report = persistence_diff([r])
    d = report.as_dict()
    assert "entries" in d
    entry_dict = d["entries"][0]
    for field in ("key", "unchanged_runs", "total_runs", "persistence_rate", "is_persistent", "last_value"):
        assert field in entry_dict


def test_last_value_reflects_b_side_of_mismatch():
    r = _result(mismatched={"PORT": ("8080", "9090")})
    report = persistence_diff([r])
    assert report.entries[0].last_value == "9090"
