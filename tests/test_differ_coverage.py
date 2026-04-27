"""Tests for differ_coverage module."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_coverage import CoverageEntry, CoverageReport, coverage_diff


def _result(
    only_in_a=(),
    only_in_b=(),
    matching=(),
    mismatched=(),
) -> DiffResult:
    return DiffResult(
        only_in_a=dict.fromkeys(only_in_a),
        only_in_b=dict.fromkeys(only_in_b),
        matching=dict.fromkeys(matching),
        mismatched={k: ("x", "y") for k in mismatched},
    )


def test_empty_results_gives_empty_report():
    report = coverage_diff([])
    assert report.entries == []


def test_empty_results_average_rate_is_one():
    report = coverage_diff([])
    assert report.average_rate() == 1.0


def test_empty_results_least_covered_is_none():
    report = coverage_diff([])
    assert report.least_covered() is None


def test_empty_results_most_covered_is_none():
    report = coverage_diff([])
    assert report.most_covered() is None


def test_single_result_all_matching_full_coverage():
    r = _result(matching=("KEY_A", "KEY_B"))
    report = coverage_diff([r])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.coverage_rate() == 1.0
    assert entry.missing_keys == []


def test_missing_key_reduces_coverage():
    r = _result(only_in_b=("MISSING_KEY",), matching=("KEY_A",))
    report = coverage_diff([r])
    entry = report.entries[0]
    assert entry.total_keys == 2
    assert entry.present_keys == 1
    assert entry.coverage_rate() == pytest.approx(0.5)
    assert "MISSING_KEY" in entry.missing_keys


def test_custom_env_names_applied():
    r = _result(matching=("KEY",))
    report = coverage_diff([r], env_names=["production"])
    assert report.entries[0].env_name == "production"


def test_default_env_names_generated():
    r = _result(matching=("KEY",))
    report = coverage_diff([r])
    assert report.entries[0].env_name == "env_0"


def test_least_covered_returns_correct_entry():
    r1 = _result(matching=("A", "B"))
    r2 = _result(only_in_b=("A",), matching=("B",))
    report = coverage_diff([r1, r2], env_names=["full", "partial"])
    assert report.least_covered().env_name == "partial"


def test_most_covered_returns_correct_entry():
    r1 = _result(matching=("A", "B"))
    r2 = _result(only_in_b=("A",), matching=("B",))
    report = coverage_diff([r1, r2], env_names=["full", "partial"])
    assert report.most_covered().env_name == "full"


def test_average_rate_across_entries():
    r1 = _result(matching=("A", "B"))
    r2 = _result(only_in_b=("A",), matching=("B",))
    report = coverage_diff([r1, r2])
    # r1 => 2/2=1.0, r2 => 1/2=0.5 => avg=0.75
    assert report.average_rate() == pytest.approx(0.75)


def test_is_complete_default_threshold():
    entry = CoverageEntry(env_name="e", total_keys=2, present_keys=2)
    assert entry.is_complete() is True


def test_is_complete_below_threshold():
    entry = CoverageEntry(env_name="e", total_keys=2, present_keys=1)
    assert entry.is_complete() is False


def test_as_dict_contains_expected_keys():
    r = _result(matching=("KEY",))
    report = coverage_diff([r])
    d = report.as_dict()
    assert "average_coverage_rate" in d
    assert "entries" in d
    assert d["entries"][0]["env"] == "env_0"
