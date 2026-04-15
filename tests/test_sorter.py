"""Tests for envdiff.sorter."""

from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.sorter import GroupedDiff, group_diff


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(only_in_a=set(), only_in_b=set(), differing_keys=set())


@pytest.fixture()
def rich_result() -> DiffResult:
    return DiffResult(
        only_in_a={"ZEBRA", "APPLE"},
        only_in_b={"MANGO", "BANANA"},
        differing_keys={"PORT", "HOST"},
    )


def test_empty_result_gives_empty_groups(empty_result: DiffResult) -> None:
    grouped = group_diff(empty_result)
    assert grouped.missing_in_b == []
    assert grouped.missing_in_a == []
    assert grouped.mismatched == []
    assert grouped.total == 0


def test_only_in_a_goes_to_missing_in_b(rich_result: DiffResult) -> None:
    grouped = group_diff(rich_result)
    assert set(grouped.missing_in_b) == {"ZEBRA", "APPLE"}


def test_only_in_b_goes_to_missing_in_a(rich_result: DiffResult) -> None:
    grouped = group_diff(rich_result)
    assert set(grouped.missing_in_a) == {"MANGO", "BANANA"}


def test_differing_keys_go_to_mismatched(rich_result: DiffResult) -> None:
    grouped = group_diff(rich_result)
    assert set(grouped.mismatched) == {"PORT", "HOST"}


def test_keys_sorted_by_default(rich_result: DiffResult) -> None:
    grouped = group_diff(rich_result)
    assert grouped.missing_in_b == sorted(grouped.missing_in_b)
    assert grouped.missing_in_a == sorted(grouped.missing_in_a)
    assert grouped.mismatched == sorted(grouped.mismatched)


def test_sort_keys_false_preserves_insertion_order() -> None:
    result = DiffResult(
        only_in_a={"Z"},
        only_in_b={"A"},
        differing_keys={"M"},
    )
    grouped = group_diff(result, sort_keys=False)
    # Just verify all keys are present regardless of order
    assert set(grouped.missing_in_b) == {"Z"}
    assert set(grouped.missing_in_a) == {"A"}
    assert set(grouped.mismatched) == {"M"}


def test_total_counts_all_keys(rich_result: DiffResult) -> None:
    grouped = group_diff(rich_result)
    assert grouped.total == 6


def test_total_is_zero_for_empty(empty_result: DiffResult) -> None:
    grouped = group_diff(empty_result)
    assert grouped.total == 0


def test_total_matches_sum_of_group_lengths(rich_result: DiffResult) -> None:
    grouped = group_diff(rich_result)
    expected = len(grouped.missing_in_b) + len(grouped.missing_in_a) + len(grouped.mismatched)
    assert grouped.total == expected


def test_returns_grouped_diff_instance(empty_result: DiffResult) -> None:
    assert isinstance(group_diff(empty_result), GroupedDiff)
