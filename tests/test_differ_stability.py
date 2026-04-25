"""Tests for envdiff.differ_stability."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_stability import StabilityEntry, StabilityReport, stability_diff


def _result(
    matching=None,
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        matching=matching or {},
        only_in_a=set(only_in_a or []),
        only_in_b=set(only_in_b or []),
        mismatched=mismatched or {},
    )


def test_empty_results_gives_empty_report():
    report = stability_diff([])
    assert report.entries == []


def test_single_result_matching_key_is_stable():
    r = _result(matching={"FOO": "bar"})
    report = stability_diff([r])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.key == "FOO"
    assert entry.stability_rate == 1.0
    assert entry.is_stable is True


def test_single_result_missing_key_is_unstable():
    r = _result(only_in_a=["MISSING"])
    report = stability_diff([r])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.key == "MISSING"
    assert entry.stability_rate == 0.0
    assert entry.is_stable is False


def test_key_stable_in_all_results_has_rate_one():
    results = [_result(matching={"KEY": "val"}) for _ in range(5)]
    report = stability_diff(results)
    assert len(report.entries) == 1
    assert report.entries[0].stability_rate == 1.0


def test_key_unstable_in_all_results_has_rate_zero():
    results = [_result(only_in_a=["GONE"]) for _ in range(4)]
    report = stability_diff(results)
    assert report.entries[0].stability_rate == 0.0


def test_key_stable_in_half_results_has_half_rate():
    stable = _result(matching={"X": "1"})
    unstable = _result(only_in_a=["X"])
    report = stability_diff([stable, unstable, stable, unstable])
    assert len(report.entries) == 1
    assert report.entries[0].stability_rate == pytest.approx(0.5)


def test_unstable_filter_returns_only_unstable_entries():
    r1 = _result(matching={"GOOD": "ok"})
    r2 = _result(only_in_a=["BAD"])
    report = stability_diff([r1, r2])
    unstable = report.unstable()
    keys = {e.key for e in unstable}
    assert "BAD" in keys
    assert "GOOD" not in keys


def test_stable_filter_returns_only_stable_entries():
    r1 = _result(matching={"GOOD": "ok"})
    r2 = _result(only_in_a=["BAD"])
    report = stability_diff([r1, r2])
    stable = report.stable()
    keys = {e.key for e in stable}
    assert "GOOD" in keys
    assert "BAD" not in keys


def test_as_dict_contains_entries_list():
    r = _result(matching={"A": "1"}, only_in_b=["B"])
    report = stability_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert isinstance(d["entries"], list)
    assert len(d["entries"]) == 2


def test_entry_repr_contains_key_and_rate():
    e = StabilityEntry(key="FOO", stable_count=3, total_count=4)
    r = repr(e)
    assert "FOO" in r
    assert "rate=" in r
