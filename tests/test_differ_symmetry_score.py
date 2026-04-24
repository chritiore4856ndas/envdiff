"""Tests for envdiff.differ_symmetry_score."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_symmetry_score import (
    SymmetryScoreReport,
    symmetry_score_results,
)


def _result(
    only_a=(),
    only_b=(),
    mismatched=(),
    matching=(),
) -> DiffResult:
    return DiffResult(
        only_in_a=list(only_a),
        only_in_b=list(only_b),
        mismatched={k: ("x", "y") for k in mismatched},
        matching=list(matching),
    )


def test_empty_results_gives_empty_report():
    report = symmetry_score_results([])
    assert isinstance(report, SymmetryScoreReport)
    assert report.entries == []


def test_empty_results_average_score_is_one():
    report = symmetry_score_results([])
    assert report.average_score() == 1.0


def test_empty_results_lowest_is_none():
    report = symmetry_score_results([])
    assert report.lowest() is None


def test_fully_matching_result_has_score_one():
    r = _result(matching=["A", "B", "C"])
    report = symmetry_score_results([r])
    assert len(report.entries) == 1
    assert report.entries[0].symmetry_score == pytest.approx(1.0)


def test_all_missing_in_b_has_score_zero():
    r = _result(only_a=["X", "Y"])
    report = symmetry_score_results([r])
    assert report.entries[0].symmetry_score == pytest.approx(0.0)


def test_half_matching_has_half_score():
    r = _result(matching=["A", "B"], only_a=["C", "D"])
    report = symmetry_score_results([r])
    assert report.entries[0].symmetry_score == pytest.approx(0.5)


def test_labels_applied_to_entries():
    r1 = _result(matching=["A"])
    r2 = _result(only_a=["B"])
    report = symmetry_score_results([r1, r2], labels=["prod-vs-staging", "dev-vs-qa"])
    assert report.entries[0].env_pair == "prod-vs-staging"
    assert report.entries[1].env_pair == "dev-vs-qa"


def test_default_labels_generated_when_none_provided():
    r = _result(matching=["K"])
    report = symmetry_score_results([r])
    assert report.entries[0].env_pair == "env_0"


def test_lowest_returns_entry_with_minimum_score():
    r1 = _result(matching=["A", "B", "C"])
    r2 = _result(only_a=["X", "Y"], matching=["Z"])
    report = symmetry_score_results([r1, r2], labels=["full", "partial"])
    lowest = report.lowest()
    assert lowest is not None
    assert lowest.env_pair == "partial"


def test_average_score_across_multiple_entries():
    r1 = _result(matching=["A"])  # score 1.0
    r2 = _result(matching=["B"], only_a=["C"])  # score 0.5
    report = symmetry_score_results([r1, r2])
    assert report.average_score() == pytest.approx(0.75)


def test_as_dict_structure():
    r = _result(matching=["A", "B"], only_b=["C"])
    report = symmetry_score_results([r], labels=["alpha"])
    d = report.as_dict()
    assert "average_score" in d
    assert "entries" in d
    entry = d["entries"][0]
    assert entry["env_pair"] == "alpha"
    assert entry["total_keys"] == 3
    assert entry["shared_keys"] == 2
    assert "symmetry_score" in entry


def test_mismatched_keys_reduce_score():
    r = _result(matching=["A"], mismatched=["B"])
    report = symmetry_score_results([r])
    # total=2, shared=1 → 0.5
    assert report.entries[0].symmetry_score == pytest.approx(0.5)
