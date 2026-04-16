"""Tests for envdiff.differ_overlap."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_overlap import compute_overlap, OverlapReport


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(only_in_a={}, only_in_b={}, mismatched={})


@pytest.fixture()
def rich_result() -> DiffResult:
    return DiffResult(
        only_in_a={"GONE": "1"},
        only_in_b={"NEW": "2"},
        mismatched={"HOST": ("localhost", "prod.example.com"), "PORT": ("5432", "5433")},
    )


def test_empty_result_gives_perfect_ratios(empty_result):
    report = compute_overlap(empty_result)
    assert report.overlap_ratio == 1.0
    assert report.match_ratio == 1.0


def test_empty_result_all_sets_empty(empty_result):
    report = compute_overlap(empty_result)
    assert report.shared_keys == set()
    assert report.only_in_a == set()
    assert report.only_in_b == set()


def test_only_in_a_counted(rich_result):
    report = compute_overlap(rich_result)
    assert "GONE" in report.only_in_a


def test_only_in_b_counted(rich_result):
    report = compute_overlap(rich_result)
    assert "NEW" in report.only_in_b


def test_mismatched_in_shared_keys(rich_result):
    report = compute_overlap(rich_result)
    assert "HOST" in report.shared_keys
    assert "PORT" in report.shared_keys


def test_mismatched_not_in_matching(rich_result):
    report = compute_overlap(rich_result)
    assert "HOST" not in report.matching
    assert "PORT" not in report.matching


def test_total_keys_correct(rich_result):
    report = compute_overlap(rich_result)
    # GONE, NEW, HOST, PORT
    assert report.total_keys == 4


def test_overlap_ratio_less_than_one(rich_result):
    report = compute_overlap(rich_result)
    assert 0.0 < report.overlap_ratio < 1.0


def test_match_ratio_zero_when_all_shared_mismatch(rich_result):
    report = compute_overlap(rich_result)
    # all shared keys (HOST, PORT) are mismatched
    assert report.match_ratio == 0.0


def test_as_dict_keys(rich_result):
    d = compute_overlap(rich_result).as_dict()
    for key in ("shared_keys", "only_in_a", "only_in_b", "mismatched", "matching",
                "total_keys", "overlap_ratio", "match_ratio"):
        assert key in d
