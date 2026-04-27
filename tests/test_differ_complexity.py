"""Tests for envdiff.differ_complexity."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_complexity import (
    ComplexityEntry,
    ComplexityReport,
    complexity_diff,
)


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
    report = complexity_diff([])
    assert report.entries == []


def test_empty_results_average_score_is_zero():
    report = complexity_diff([])
    assert report.average_score() == 0.0


def test_empty_results_most_complex_is_none():
    report = complexity_diff([])
    assert report.most_complex() is None


def test_single_clean_result_has_zero_complexity():
    r = _result(matching={"KEY": "val"})
    report = complexity_diff([r], labels=["prod"])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.complexity_score == 0.0
    assert entry.issues == 0


def test_single_result_missing_key_has_nonzero_complexity():
    r = _result(only_in_a={"MISSING": "x"})
    report = complexity_diff([r])
    entry = report.entries[0]
    assert entry.complexity_score > 0.0
    assert entry.issues == 1


def test_all_keys_are_issues_gives_score_one():
    r = _result(only_in_a={"A": "1"}, only_in_b={"B": "2"}, mismatched={"C": ("x", "y")})
    report = complexity_diff([r])
    entry = report.entries[0]
    assert entry.total_keys == 3
    assert entry.issues == 3
    assert entry.complexity_score == 1.0


def test_labels_applied_to_entries():
    r = _result(matching={"K": "v"})
    report = complexity_diff([r], labels=["staging"])
    assert report.entries[0].env_label == "staging"


def test_default_label_when_no_labels_provided():
    r = _result(matching={"K": "v"})
    report = complexity_diff([r])
    assert report.entries[0].env_label == "env_0"


def test_most_complex_returns_highest_score():
    r1 = _result(matching={"A": "1"})
    r2 = _result(only_in_a={"B": "2"}, only_in_b={"C": "3"})
    report = complexity_diff([r1, r2], labels=["clean", "messy"])
    assert report.most_complex().env_label == "messy"


def test_average_score_across_entries():
    r1 = _result(matching={"A": "1"})  # score 0.0
    r2 = _result(only_in_a={"B": "2"})  # score 1.0
    report = complexity_diff([r1, r2])
    assert report.average_score() == pytest.approx(0.5)


def test_is_complex_default_threshold():
    entry = ComplexityEntry(env_label="x", total_keys=10, issues=5, complexity_score=0.5)
    assert entry.is_complex() is True


def test_is_complex_below_threshold():
    entry = ComplexityEntry(env_label="x", total_keys=10, issues=1, complexity_score=0.1)
    assert entry.is_complex() is False


def test_as_dict_contains_expected_keys():
    r = _result(matching={"K": "v"}, only_in_a={"X": "1"})
    report = complexity_diff([r], labels=["dev"])
    d = report.as_dict()
    assert "entries" in d
    assert "average_score" in d
    assert "most_complex" in d
    assert d["entries"][0]["env"] == "dev"
