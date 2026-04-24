"""Tests for envdiff.differ_cadence."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_cadence import CadenceEntry, CadenceReport, cadence_diff


def _result(
    only_a=(),
    only_b=(),
    mismatched=None,
    matching=None,
) -> DiffResult:
    return DiffResult(
        only_in_a=set(only_a),
        only_in_b=set(only_b),
        mismatched=dict(mismatched or {}),
        matching=dict(matching or {}),
    )


# ---------------------------------------------------------------------------
# empty input
# ---------------------------------------------------------------------------

def test_empty_results_gives_empty_report():
    report = cadence_diff([])
    assert isinstance(report, CadenceReport)
    assert report.entries == []


# ---------------------------------------------------------------------------
# single snapshot
# ---------------------------------------------------------------------------

def test_single_result_matching_key_has_zero_changes():
    r = _result(matching={"KEY": "val"})
    report = cadence_diff([r])
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.change_count == 0
    assert entry.cadence_rate == 0.0


def test_single_result_missing_key_has_one_change():
    r = _result(only_a=("GONE",))
    report = cadence_diff([r])
    entry = next(e for e in report.entries if e.key == "GONE")
    assert entry.change_count == 1
    assert entry.cadence_rate == 1.0


# ---------------------------------------------------------------------------
# multiple snapshots
# ---------------------------------------------------------------------------

def test_key_changing_in_every_result_has_rate_one():
    results = [
        _result(mismatched={"DB_URL": ("a", "b")}),
        _result(mismatched={"DB_URL": ("b", "c")}),
        _result(mismatched={"DB_URL": ("c", "d")}),
    ]
    report = cadence_diff(results)
    entry = next(e for e in report.entries if e.key == "DB_URL")
    assert entry.change_count == 3
    assert entry.cadence_rate == pytest.approx(1.0)
    assert entry.is_regular is True


def test_key_stable_across_all_has_rate_zero():
    results = [
        _result(matching={"STABLE": "x"}),
        _result(matching={"STABLE": "x"}),
        _result(matching={"STABLE": "x"}),
    ]
    report = cadence_diff(results)
    entry = next(e for e in report.entries if e.key == "STABLE")
    assert entry.cadence_rate == pytest.approx(0.0)
    assert entry.is_regular is False


def test_key_in_half_results_has_half_rate():
    results = [
        _result(mismatched={"HALF": ("a", "b")}),
        _result(matching={"HALF": "b"}),
        _result(mismatched={"HALF": ("b", "c")}),
        _result(matching={"HALF": "c"}),
    ]
    report = cadence_diff(results)
    entry = next(e for e in report.entries if e.key == "HALF")
    assert entry.cadence_rate == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# regular / irregular split
# ---------------------------------------------------------------------------

def test_regular_and_irregular_partitioned_correctly():
    results = [
        _result(mismatched={"FAST": ("a", "b")}, matching={"SLOW": "x"}),
        _result(mismatched={"FAST": ("b", "c")}, matching={"SLOW": "x"}),
        _result(mismatched={"FAST": ("c", "d")}, matching={"SLOW": "x"}),
    ]
    report = cadence_diff(results)
    regular_keys = {e.key for e in report.regular()}
    irregular_keys = {e.key for e in report.irregular()}
    assert "FAST" in regular_keys
    assert "SLOW" in irregular_keys


# ---------------------------------------------------------------------------
# as_dict
# ---------------------------------------------------------------------------

def test_as_dict_contains_expected_fields():
    r = _result(mismatched={"X": ("1", "2")})
    report = cadence_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert "regular_count" in d
    assert "irregular_count" in d
    entry_dict = d["entries"][0]
    assert "key" in entry_dict
    assert "cadence_rate" in entry_dict
    assert "is_regular" in entry_dict
