"""Tests for envdiff.scorer."""

from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.scorer import DiffScore, format_score, score_diff


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(only_in_a={}, only_in_b={}, mismatched={}, matching={})


@pytest.fixture()
def rich_result() -> DiffResult:
    return DiffResult(
        only_in_a={"MISSING_B": "1"},
        only_in_b={"MISSING_A": "2"},
        mismatched={"HOST": ("localhost", "prod.example.com")},
        matching={"PORT": "8080", "DEBUG": "false"},
    )


def test_empty_result_perfect_similarity(empty_result):
    score = score_diff(empty_result)
    assert score.similarity == 1.0
    assert score.grade == "A"
    assert score.total_keys == 0


def test_matching_keys_counted(rich_result):
    score = score_diff(rich_result)
    assert score.matching == 2


def test_total_keys_is_union(rich_result):
    score = score_diff(rich_result)
    # MISSING_B, MISSING_A, HOST, PORT, DEBUG
    assert score.total_keys == 5


def test_similarity_ratio(rich_result):
    score = score_diff(rich_result)
    # 2 matching out of 5 total
    assert score.similarity == pytest.approx(0.4, abs=1e-4)


def test_grade_d_for_low_similarity(rich_result):
    score = score_diff(rich_result)
    assert score.grade == "D"


def test_grade_a_for_perfect():
    result = DiffResult(
        only_in_a={},
        only_in_b={},
        mismatched={},
        matching={"A": "1", "B": "2"},
    )
    score = score_diff(result)
    assert score.grade == "A"


def test_missing_counts(rich_result):
    score = score_diff(rich_result)
    assert score.missing_in_b == 1
    assert score.missing_in_a == 1
    assert score.mismatched == 1


def test_format_score_contains_similarity(rich_result):
    score = score_diff(rich_result)
    output = format_score(score)
    assert "Similarity" in output
    assert "40.0%" in output
    assert "Grade" not in output  # label is lowercase 'grade'
    assert "grade" in output


def test_format_score_shows_all_sections(rich_result):
    score = score_diff(rich_result)
    output = format_score(score)
    for label in ("Total keys", "Matching", "Mismatched", "Only in A", "Only in B"):
        assert label in output
