"""Tests for envdiff.filter."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.filter import filter_diff


@pytest.fixture()
def rich_result() -> DiffResult:
    return DiffResult(
        only_in_a={"SECRET_KEY": "abc", "DEBUG": "true"},
        only_in_b={"DATABASE_URL": "postgres://"},
        mismatched={"LOG_LEVEL": ("info", "debug"), "AWS_REGION": ("us-east-1", "eu-west-1")},
        common_keys={"APP_NAME"},
    )


def test_no_filters_returns_same_keys(rich_result: DiffResult) -> None:
    filtered = filter_diff(rich_result)
    assert filtered.only_in_a == rich_result.only_in_a
    assert filtered.only_in_b == rich_result.only_in_b
    assert filtered.mismatched == rich_result.mismatched
    assert filtered.common_keys == rich_result.common_keys


def test_exclude_pattern_removes_matching_keys(rich_result: DiffResult) -> None:
    filtered = filter_diff(rich_result, exclude_patterns=["SECRET_KEY", "AWS_.*"])
    assert "SECRET_KEY" not in filtered.only_in_a
    assert "AWS_REGION" not in filtered.mismatched
    assert "DEBUG" in filtered.only_in_a


def test_exclude_does_not_affect_unmatched(rich_result: DiffResult) -> None:
    filtered = filter_diff(rich_result, exclude_patterns=["NOPE"])
    assert len(filtered.only_in_a) == 2
    assert len(filtered.mismatched) == 2


def test_include_pattern_keeps_only_matching(rich_result: DiffResult) -> None:
    filtered = filter_diff(rich_result, include_patterns=["LOG_LEVEL", "DEBUG"])
    assert filtered.only_in_a == {"DEBUG": "true"}
    assert filtered.only_in_b == {}
    assert filtered.mismatched == {"LOG_LEVEL": ("info", "debug")}


def test_include_and_exclude_combined(rich_result: DiffResult) -> None:
    # include AWS_.* but then exclude AWS_REGION
    filtered = filter_diff(
        rich_result,
        include_patterns=["AWS_.*", "DEBUG"],
        exclude_patterns=["AWS_REGION"],
    )
    assert "AWS_REGION" not in filtered.mismatched
    assert "DEBUG" in filtered.only_in_a


def test_common_keys_also_filtered(rich_result: DiffResult) -> None:
    filtered = filter_diff(rich_result, exclude_patterns=["APP_NAME"])
    assert "APP_NAME" not in filtered.common_keys


def test_empty_result_stays_empty() -> None:
    empty = DiffResult(only_in_a={}, only_in_b={}, mismatched={}, common_keys=set())
    filtered = filter_diff(empty, exclude_patterns=[".*"])
    assert not filtered.only_in_a
    assert not filtered.only_in_b
    assert not filtered.mismatched
    assert not filtered.common_keys
