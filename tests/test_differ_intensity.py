"""Tests for envdiff.differ_intensity."""
from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_intensity import IntensityEntry, IntensityReport, intensity_diff


def _result(
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
    matching=None,
) -> DiffResult:
    return DiffResult(
        only_in_a=only_in_a or [],
        only_in_b=only_in_b or [],
        mismatched=mismatched or {},
        matching=matching or {},
    )


def test_empty_results_gives_empty_report():
    report = intensity_diff([], [])
    assert report.entries == []


def test_empty_results_average_rate_is_zero():
    report = intensity_diff([], [])
    assert report.average_rate == 0.0


def test_empty_results_most_intense_is_none():
    report = intensity_diff([], [])
    assert report.most_intense is None


def test_single_clean_result_has_zero_intensity():
    r = _result(matching={"KEY": "val"})
    report = intensity_diff([r], ["dev", "prod"])
    for entry in report.entries:
        assert entry.intensity_rate == 0.0
        assert entry.issue_count == 0


def test_missing_in_b_increments_first_env():
    r = _result(only_in_a=["MISSING_KEY"])
    report = intensity_diff([r], ["dev", "prod"])
    dev = next(e for e in report.entries if e.env_name == "dev")
    assert dev.issue_count == 1


def test_missing_in_a_increments_last_env():
    r = _result(only_in_b=["EXTRA_KEY"])
    report = intensity_diff([r], ["dev", "prod"])
    prod = next(e for e in report.entries if e.env_name == "prod")
    assert prod.issue_count == 1


def test_mismatched_key_increments_all_envs():
    r = _result(mismatched={"SHARED": ("a", "b")})
    report = intensity_diff([r], ["dev", "prod"])
    for entry in report.entries:
        assert entry.issue_count == 1


def test_intensity_rate_between_zero_and_one():
    r = _result(only_in_a=["A"], only_in_b=["B"], matching={"C": "v"})
    report = intensity_diff([r], ["dev", "prod"])
    for entry in report.entries:
        assert 0.0 <= entry.intensity_rate <= 1.0


def test_most_intense_returns_highest_entry():
    r = _result(only_in_a=["A", "B", "C"], matching={"D": "v"})
    report = intensity_diff([r], ["dev", "prod"])
    assert report.most_intense is not None
    assert report.most_intense.env_name == "dev"


def test_as_dict_contains_expected_keys():
    r = _result(only_in_a=["X"])
    report = intensity_diff([r], ["dev", "prod"])
    d = report.as_dict()
    assert "entries" in d
    assert "average_rate" in d
    assert "most_intense" in d


def test_entry_as_dict_structure():
    entry = IntensityEntry(env_name="staging", total_keys=10, issue_count=3)
    d = entry.as_dict()
    assert d["env"] == "staging"
    assert d["total_keys"] == 10
    assert d["issue_count"] == 3
    assert d["intensity_rate"] == pytest.approx(0.3, abs=1e-4)


def test_average_rate_across_entries():
    r1 = _result(only_in_a=["A"], matching={"B": "v"})
    r2 = _result(matching={"C": "v"})
    report = intensity_diff([r1, r2], ["dev", "prod"])
    assert report.average_rate >= 0.0
