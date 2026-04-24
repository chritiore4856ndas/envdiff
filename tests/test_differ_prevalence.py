"""Tests for envdiff.differ_prevalence."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_prevalence import PrevalenceEntry, PrevalenceReport, prevalence_diff


def _result(
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
    matching=None,
) -> DiffResult:
    return DiffResult(
        only_in_a=only_in_a or {},
        only_in_b=only_in_b or {},
        mismatched=mismatched or {},
        matching=matching or {},
    )


def test_empty_results_gives_empty_report():
    report = prevalence_diff([])
    assert report.entries == []


def test_single_result_missing_key_has_appearance_one():
    r = _result(only_in_a={"FOO": "bar"})
    report = prevalence_diff([r])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.key == "FOO"
    assert entry.appearances == 1
    assert entry.total == 1


def test_key_in_all_results_has_rate_one():
    results = [
        _result(only_in_a={"KEY": "v"}),
        _result(only_in_a={"KEY": "v"}),
        _result(mismatched={"KEY": ("a", "b")}),
    ]
    report = prevalence_diff(results)
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.appearances == 3
    assert entry.prevalence_rate == 1.0


def test_key_in_half_results_has_half_rate():
    results = [
        _result(only_in_a={"KEY": "v"}),
        _result(matching={"KEY": "v"}),
    ]
    report = prevalence_diff(results)
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.appearances == 1
    assert entry.total == 2
    assert entry.prevalence_rate == 0.5


def test_entries_sorted_descending_by_appearances():
    results = [
        _result(only_in_a={"RARE": "x"}),
        _result(only_in_a={"COMMON": "x"}),
        _result(only_in_a={"COMMON": "x"}),
    ]
    report = prevalence_diff(results)
    assert report.entries[0].key == "COMMON"
    assert report.entries[1].key == "RARE"


def test_prevalent_filters_above_threshold():
    results = [
        _result(only_in_a={"A": "1"}),
        _result(only_in_a={"A": "1", "B": "2"}),
    ]
    report = prevalence_diff(results)
    prevalent_keys = {e.key for e in report.prevalent()}
    assert "A" in prevalent_keys
    assert "B" not in prevalent_keys


def test_rare_filters_below_threshold():
    results = [
        _result(only_in_a={"A": "1"}),
        _result(only_in_a={"A": "1", "B": "2"}),
    ]
    report = prevalence_diff(results)
    rare_keys = {e.key for e in report.rare()}
    assert "B" in rare_keys
    assert "A" not in rare_keys


def test_as_dict_contains_entries():
    r = _result(only_in_b={"X": "1"})
    report = prevalence_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert d["entries"][0]["key"] == "X"
    assert d["entries"][0]["prevalence_rate"] == 1.0
