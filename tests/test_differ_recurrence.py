"""Tests for envdiff.differ_recurrence."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_recurrence import RecurrenceEntry, RecurrenceReport, recurrence_diff


def _result(
    only_in_a=(), only_in_b=(), mismatched=(), matching=()
) -> DiffResult:
    return DiffResult(
        only_in_a=list(only_in_a),
        only_in_b=list(only_in_b),
        mismatched={k: ("x", "y") for k in mismatched},
        matching=list(matching),
    )


def test_empty_results_gives_empty_report():
    report = recurrence_diff([])
    assert report.entries == []
    assert report.total_snapshots == 0


def test_single_result_missing_key_counted():
    report = recurrence_diff([_result(only_in_a=["FOO"])])
    assert len(report.entries) == 1
    assert report.entries[0].key == "FOO"
    assert report.entries[0].occurrences == 1


def test_key_in_all_results_has_rate_one():
    results = [_result(only_in_a=["BAR"]) for _ in range(4)]
    report = recurrence_diff(results)
    entry = next(e for e in report.entries if e.key == "BAR")
    assert entry.recurrence_rate == 1.0
    assert entry.is_recurrent is True


def test_key_in_half_results_has_half_rate():
    results = [
        _result(only_in_a=["KEY"]),
        _result(matching=["KEY"]),
        _result(only_in_a=["KEY"]),
        _result(matching=["KEY"]),
    ]
    report = recurrence_diff(results)
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.recurrence_rate == pytest.approx(0.5)
    assert entry.is_recurrent is True


def test_key_below_threshold_is_not_recurrent():
    results = [
        _result(only_in_a=["RARE"]),
        _result(matching=["RARE"]),
        _result(matching=["RARE"]),
        _result(matching=["RARE"]),
    ]
    report = recurrence_diff(results)
    entry = next(e for e in report.entries if e.key == "RARE")
    assert entry.recurrence_rate == pytest.approx(0.25)
    assert entry.is_recurrent is False


def test_matching_key_not_counted():
    report = recurrence_diff([_result(matching=["STABLE"])])
    assert all(e.key != "STABLE" for e in report.entries)


def test_total_snapshots_matches_input_length():
    results = [_result(only_in_a=["A"]) for _ in range(7)]
    report = recurrence_diff(results)
    assert report.total_snapshots == 7


def test_entries_sorted_descending_by_occurrences():
    results = [
        _result(only_in_a=["COMMON", "RARE"]),
        _result(only_in_a=["COMMON"]),
        _result(only_in_a=["COMMON"]),
    ]
    report = recurrence_diff(results)
    rates = [e.occurrences for e in report.entries]
    assert rates == sorted(rates, reverse=True)


def test_recurrent_filters_low_rate_keys():
    results = [
        _result(only_in_a=["HIGH", "LOW"]),
        _result(only_in_a=["HIGH"]),
    ]
    report = recurrence_diff(results)
    recurrent_keys = {e.key for e in report.recurrent()}
    assert "HIGH" in recurrent_keys
    assert "LOW" not in recurrent_keys


def test_as_dict_structure():
    results = [_result(only_in_a=["X"])]
    report = recurrence_diff(results)
    d = report.as_dict()
    assert "total_snapshots" in d
    assert "entries" in d
    assert d["entries"][0]["key"] == "X"
