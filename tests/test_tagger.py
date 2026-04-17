"""Tests for envdiff.tagger."""

from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.tagger import TaggedDiff, tag_diff


@pytest.fixture()
def rich_result() -> DiffResult:
    return DiffResult(
        missing_in_b=["DB_HOST", "DB_PORT"],
        missing_in_a=["REDIS_URL"],
        mismatched={"SECRET_KEY": ("abc", "xyz"), "AWS_TOKEN": ("old", "new")},
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(missing_in_b=[], missing_in_a=[], mismatched={})


def test_empty_result_gives_empty_tags(empty_result):
    tagged = tag_diff(empty_result, {"db": ["DB_*"]})
    assert tagged.tags == {}


def test_matching_glob_assigns_tag(rich_result):
    tagged = tag_diff(rich_result, {"db": ["DB_*"]})
    assert "db" in tagged.tags["DB_HOST"]
    assert "db" in tagged.tags["DB_PORT"]


def test_non_matching_key_gets_no_tag(rich_result):
    tagged = tag_diff(rich_result, {"db": ["DB_*"]})
    assert "db" not in tagged.tags.get("REDIS_URL", set())


def test_multiple_tags_on_same_key(rich_result):
    tagged = tag_diff(
        rich_result,
        {"secret": ["SECRET_*", "*TOKEN*"], "aws": ["AWS_*"]},
    )
    assert "secret" in tagged.tags["SECRET_KEY"]
    assert "secret" in tagged.tags["AWS_TOKEN"]
    assert "aws" in tagged.tags["AWS_TOKEN"]


def test_keys_for_tag_returns_correct_keys(rich_result):
    tagged = tag_diff(rich_result, {"db": ["DB_*"]})
    db_keys = tagged.keys_for_tag("db")
    assert set(db_keys) == {"DB_HOST", "DB_PORT"}


def test_keys_for_unknown_tag_returns_empty(rich_result):
    tagged = tag_diff(rich_result, {"db": ["DB_*"]})
    assert tagged.keys_for_tag("nonexistent") == []


def test_tags_for_key_returns_set(rich_result):
    tagged = tag_diff(rich_result, {"db": ["DB_*"]})
    result = tagged.tags_for_key("DB_HOST")
    assert isinstance(result, set)
    assert "db" in result


def test_tags_for_missing_key_returns_empty_set(rich_result):
    tagged = tag_diff(rich_result, {"db": ["DB_*"]})
    assert tagged.tags_for_key("NOT_A_KEY") == set()


def test_wildcard_pattern_matches_all(rich_result):
    tagged = tag_diff(rich_result, {"all": ["*"]})
    for key in tagged.tags:
        assert "all" in tagged.tags[key]


def test_empty_tag_rules_gives_empty_tags(rich_result):
    """When no tag rules are provided, no keys should be tagged."""
    tagged = tag_diff(rich_result, {})
    assert tagged.tags == {}
