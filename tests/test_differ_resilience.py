"""Tests for differ_resilience."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_resilience import ResilienceEntry, ResilienceReport, resilience_diff


def _result(
    matching=None,
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        matching=matching or {},
        only_in_a=only_in_a or {},
        only_in_b=only_in_b or {},
        mismatched=mismatched or {},
    )


def test_empty_results_gives_empty_report():
    report = resilience_diff([])
    assert report.entries == []


def test_single_result_matching_key_is_fully_resilient():
    r = _result(matching={"KEY": "val"})
    report = resilience_diff([r])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.key == "KEY"
    assert entry.resilience_rate() == 1.0
    assert entry.is_resilient()


def test_single_result_missing_key_has_zero_resilience():
    r = _result(only_in_a={"KEY": "val"})
    report = resilience_diff([r])
    entry = report.entries[0]
    assert entry.issue_count == 1
    assert entry.resilience_rate() == 0.0
    assert not entry.is_resilient()


def test_mismatched_key_reduces_resilience():
    r = _result(mismatched={"KEY": ("a", "b")})
    report = resilience_diff([r])
    entry = report.entries[0]
    assert entry.issue_count == 1
    assert entry.resilience_rate() == 0.0


def test_key_stable_across_all_results_has_rate_one():
    results = [_result(matching={"KEY": "v"}) for _ in range(5)]
    report = resilience_diff(results)
    assert len(report.entries) == 1
    assert report.entries[0].resilience_rate() == 1.0


def test_key_problematic_in_half_results_has_half_rate():
    good = _result(matching={"KEY": "v"})
    bad = _result(only_in_a={"KEY": "v"})
    report = resilience_diff([good, good, bad, bad])
    entry = report.entries[0]
    assert entry.appearances == 4
    assert entry.issue_count == 2
    assert entry.resilience_rate() == 0.5


def test_fragile_returns_entries_below_threshold():
    good = _result(matching={"KEY": "v"})
    bad = _result(only_in_a={"KEY": "v"})
    report = resilience_diff([good, bad, bad, bad])
    fragile = report.fragile(threshold=0.8)
    assert len(fragile) == 1
    assert fragile[0].key == "KEY"


def test_most_resilient_returns_highest_rate():
    r1 = _result(matching={"A": "1"}, only_in_a={"B": "2"})
    report = resilience_diff([r1])
    best = report.most_resilient()
    assert best is not None
    assert best.key == "A"


def test_least_resilient_returns_lowest_rate():
    r1 = _result(matching={"A": "1"}, only_in_a={"B": "2"})
    report = resilience_diff([r1])
    worst = report.least_resilient()
    assert worst is not None
    assert worst.key == "B"


def test_as_dict_contains_entries():
    r = _result(matching={"X": "y"})
    report = resilience_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert d["entries"][0]["key"] == "X"
    assert "resilience_rate" in d["entries"][0]


def test_empty_report_most_resilient_is_none():
    report = ResilienceReport()
    assert report.most_resilient() is None
    assert report.least_resilient() is None
