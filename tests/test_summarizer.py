"""Tests for envdiff.summarizer."""
from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.sorter import GroupedDiff, group_diff
from envdiff.summarizer import DiffSummary, format_summary, summarize


@pytest.fixture()
def empty_grouped() -> GroupedDiff:
    result = DiffResult(only_in_a={}, only_in_b={}, mismatched={})
    return group_diff(result)


@pytest.fixture()
def rich_grouped() -> GroupedDiff:
    result = DiffResult(
        only_in_a={"GONE": "old"},
        only_in_b={"NEW": "fresh"},
        mismatched={"PORT": ("8080", "9090")},
    )
    return group_diff(result)


def test_empty_grouped_is_clean(empty_grouped):
    summary = summarize(empty_grouped)
    assert summary.clean is True
    assert summary.total_keys == 0


def test_empty_grouped_all_counts_zero(empty_grouped):
    summary = summarize(empty_grouped)
    assert summary.missing_in_b == 0
    assert summary.missing_in_a == 0
    assert summary.mismatched == 0


def test_rich_grouped_not_clean(rich_grouped):
    summary = summarize(rich_grouped)
    assert summary.clean is False


def test_rich_grouped_counts(rich_grouped):
    summary = summarize(rich_grouped)
    assert summary.missing_in_b == 1
    assert summary.missing_in_a == 1
    assert summary.mismatched == 1
    assert summary.total_keys == 3


def test_as_dict_keys(rich_grouped):
    d = summarize(rich_grouped).as_dict()
    assert set(d.keys()) == {"missing_in_b", "missing_in_a", "mismatched", "total_keys", "clean"}


def test_format_summary_clean(empty_grouped):
    text = format_summary(summarize(empty_grouped))
    assert text == "No differences found."


def test_format_summary_contains_counts(rich_grouped):
    text = format_summary(summarize(rich_grouped), label_a="dev", label_b="prod")
    assert "1 key(s) only in dev" in text
    assert "1 key(s) only in prod" in text
    assert "1 key(s) with mismatched values" in text
    assert "3 total differing key(s)" in text


def test_format_summary_header(rich_grouped):
    text = format_summary(summarize(rich_grouped))
    assert text.startswith("Diff summary:")


def test_format_summary_only_mismatched():
    result = DiffResult(only_in_a={}, only_in_b={}, mismatched={"X": ("1", "2")})
    grouped = group_diff(result)
    text = format_summary(summarize(grouped))
    assert "mismatched" in text
    assert "missing" not in text
