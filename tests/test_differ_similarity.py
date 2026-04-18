"""Tests for differ_similarity module."""
import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_similarity import (
    build_similarity_matrix,
    PairSimilarity,
    SimilarityMatrix,
)


def _clean() -> DiffResult:
    return DiffResult(only_in_a=set(), only_in_b=set(), mismatched={}, matching={"KEY": "val"})


def _diff_a() -> DiffResult:
    return DiffResult(only_in_a={"EXTRA"}, only_in_b=set(), mismatched={}, matching={"KEY": "val"})


def _diff_b() -> DiffResult:
    return DiffResult(only_in_a=set(), only_in_b={"OTHER"}, mismatched={}, matching={"KEY": "val"})


def test_empty_results_gives_empty_matrix():
    matrix = build_similarity_matrix({})
    assert matrix.pairs == []


def test_single_result_gives_empty_pairs():
    matrix = build_similarity_matrix({"prod": _clean()})
    assert matrix.pairs == []


def test_two_identical_results_perfect_similarity():
    matrix = build_similarity_matrix({"a": _clean(), "b": _clean()})
    assert len(matrix.pairs) == 1
    assert matrix.pairs[0].score.similarity == pytest.approx(1.0)


def test_two_differing_results_lower_similarity():
    matrix = build_similarity_matrix({"a": _diff_a(), "b": _clean()})
    assert matrix.pairs[0].score.similarity < 1.0


def test_three_results_gives_three_pairs():
    results = {"a": _clean(), "b": _diff_a(), "c": _diff_b()}
    matrix = build_similarity_matrix(results)
    assert len(matrix.pairs) == 3


def test_most_similar_returns_highest():
    results = {"a": _clean(), "b": _clean(), "c": _diff_a()}
    matrix = build_similarity_matrix(results)
    best = matrix.most_similar()
    assert best is not None
    assert best.score.similarity == pytest.approx(1.0)


def test_least_similar_returns_lowest():
    results = {"a": _clean(), "b": _clean(), "c": _diff_a()}
    matrix = build_similarity_matrix(results)
    worst = matrix.least_similar()
    assert worst is not None
    assert worst.score.similarity < 1.0


def test_average_similarity_empty_is_one():
    matrix = SimilarityMatrix(pairs=[])
    assert matrix.average_similarity() == pytest.approx(1.0)


def test_as_dict_contains_pairs_and_average():
    matrix = build_similarity_matrix({"a": _clean(), "b": _diff_a()})
    d = matrix.as_dict()
    assert "pairs" in d
    assert "average_similarity" in d
    assert isinstance(d["pairs"], list)


def test_pair_repr_contains_labels():
    matrix = build_similarity_matrix({"staging": _clean(), "prod": _clean()})
    r = repr(matrix.pairs[0])
    assert "staging" in r
    assert "prod" in r
