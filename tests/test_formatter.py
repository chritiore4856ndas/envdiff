"""Tests for envdiff.formatter."""

import json

import pytest

from envdiff.comparator import DiffResult
from envdiff.formatter import format_json, format_table, format_text


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(only_in_a=set(), only_in_b=set(), mismatched={})


@pytest.fixture()
def rich_result() -> DiffResult:
    return DiffResult(
        only_in_a={"SECRET_KEY"},
        only_in_b={"NEW_FLAG"},
        mismatched={"DB_HOST": ("localhost", "db.prod")},
    )


def test_text_no_diff(empty_result: DiffResult) -> None:
    out = format_text(empty_result, color=False)
    assert "No differences" in out


def test_text_shows_missing_key(rich_result: DiffResult) -> None:
    out = format_text(rich_result, color=False)
    assert "SECRET_KEY" in out
    assert "only in A" in out


def test_text_shows_extra_key(rich_result: DiffResult) -> None:
    out = format_text(rich_result, color=False)
    assert "NEW_FLAG" in out
    assert "only in B" in out


def test_text_shows_mismatch(rich_result: DiffResult) -> None:
    out = format_text(rich_result, color=False)
    assert "DB_HOST" in out
    assert "localhost" in out
    assert "db.prod" in out


def test_text_header_counts(rich_result: DiffResult) -> None:
    out = format_text(rich_result, color=False)
    assert "1 missing" in out
    assert "1 extra" in out
    assert "1 mismatched" in out


def test_json_no_diff(empty_result: DiffResult) -> None:
    out = format_json(empty_result)
    data = json.loads(out)
    assert data["only_in_a"] == []
    assert data["only_in_b"] == []
    assert data["mismatched"] == {}


def test_json_rich_result(rich_result: DiffResult) -> None:
    out = format_json(rich_result)
    data = json.loads(out)
    assert "SECRET_KEY" in data["only_in_a"]
    assert "NEW_FLAG" in data["only_in_b"]
    assert data["mismatched"]["DB_HOST"] == {"a": "localhost", "b": "db.prod"}


def test_table_no_diff(empty_result: DiffResult) -> None:
    out = format_table(empty_result, color=False)
    assert "No differences" in out


def test_table_has_header(rich_result: DiffResult) -> None:
    out = format_table(rich_result, color=False)
    assert "KEY" in out
    assert "STATUS" in out


def test_table_shows_all_keys(rich_result: DiffResult) -> None:
    out = format_table(rich_result, color=False)
    assert "SECRET_KEY" in out
    assert "NEW_FLAG" in out
    assert "DB_HOST" in out
