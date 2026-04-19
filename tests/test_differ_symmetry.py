import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_symmetry import SymmetryReport, symmetry_diff


def _result(
    only_a=None, only_b=None, mismatched=None, matching=None
) -> DiffResult:
    return DiffResult(
        only_in_a=only_a or {},
        only_in_b=only_b or {},
        mismatched=mismatched or {},
        matching=matching or {},
    )


def test_empty_result_perfect_symmetry():
    r = symmetry_diff(_result())
    assert r.symmetry_ratio == 1.0
    assert r.is_symmetric
    assert r.total_issues == 0


def test_only_in_a_reduces_ratio():
    r = symmetry_diff(_result(only_a={"KEY": "val"}, matching={"X": "1"}))
    assert r.symmetry_ratio < 1.0
    assert "KEY" in r.only_in_a


def test_only_in_b_reduces_ratio():
    r = symmetry_diff(_result(only_b={"KEY": "val"}, matching={"X": "1"}))
    assert r.symmetry_ratio < 1.0
    assert "KEY" in r.only_in_b


def test_mismatched_reduces_ratio():
    r = symmetry_diff(_result(mismatched={"KEY": ("a", "b")}, matching={"X": "1"}))
    assert r.symmetry_ratio < 1.0
    assert "KEY" in r.mismatched


def test_symmetric_when_equal_missing_counts():
    r = symmetry_diff(_result(only_a={"A": "1"}, only_b={"B": "2"}))
    assert r.is_symmetric


def test_not_symmetric_when_unequal_missing_counts():
    r = symmetry_diff(_result(only_a={"A": "1", "C": "3"}, only_b={"B": "2"}))
    assert not r.is_symmetric


def test_total_issues_counts_all_problem_keys():
    r = symmetry_diff(_result(
        only_a={"A": "1"},
        only_b={"B": "2"},
        mismatched={"C": ("x", "y")},
    ))
    assert r.total_issues == 3


def test_as_dict_contains_expected_keys():
    r = symmetry_diff(_result())
    d = r.as_dict()
    assert "symmetry_ratio" in d
    assert "is_symmetric" in d
    assert "only_in_a" in d
    assert "only_in_b" in d
    assert "mismatched" in d
    assert "total_issues" in d


def test_ratio_clamped_between_zero_and_one():
    r = symmetry_diff(_result(
        only_a={str(i): str(i) for i in range(10)},
    ))
    assert 0.0 <= r.symmetry_ratio <= 1.0
