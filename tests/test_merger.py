"""Tests for envdiff.merger."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.merger import MergeResult, merge


@pytest.fixture
def empty_result():
    return DiffResult(
        only_in_a={}, only_in_b={}, matching={}, mismatched={}
    )


@pytest.fixture
def rich_result():
    return DiffResult(
        only_in_a={"ALPHA": "1"},
        only_in_b={"BETA": "2"},
        matching={"SHARED": "ok"},
        mismatched={"HOST": ("localhost", "prod.example.com")},
    )


def test_empty_result_gives_empty_merge(empty_result):
    mr = merge(empty_result)
    assert mr.resolved == {}
    assert mr.conflicts == {}
    assert not mr.has_conflicts


def test_only_in_a_included(rich_result):
    mr = merge(rich_result)
    assert "ALPHA" in mr.resolved
    assert mr.resolved["ALPHA"] == "1"


def test_only_in_b_included(rich_result):
    mr = merge(rich_result)
    assert "BETA" in mr.resolved
    assert mr.resolved["BETA"] == "2"


def test_matching_included(rich_result):
    mr = merge(rich_result)
    assert mr.resolved["SHARED"] == "ok"


def test_prefer_a_on_mismatch(rich_result):
    mr = merge(rich_result, prefer="a")
    assert mr.resolved["HOST"] == "localhost"


def test_prefer_b_on_mismatch(rich_result):
    mr = merge(rich_result, prefer="b")
    assert mr.resolved["HOST"] == "prod.example.com"


def test_conflicts_recorded(rich_result):
    mr = merge(rich_result)
    assert "HOST" in mr.conflicts
    assert mr.conflicts["HOST"] == ("localhost", "prod.example.com")
    assert mr.has_conflicts


def test_skip_conflicts_omits_mismatched_keys(rich_result):
    mr = merge(rich_result, skip_conflicts=True)
    assert "HOST" not in mr.resolved
    assert "HOST" in mr.conflicts


def test_invalid_prefer_raises(rich_result):
    with pytest.raises(ValueError, match="prefer must be"):
        merge(rich_result, prefer="c")


def test_as_env_lines_format(rich_result):
    mr = merge(rich_result, prefer="a", skip_conflicts=False)
    lines = mr.as_env_lines()
    assert all("=" in line for line in lines)
    keys = [line.split("=", 1)[0] for line in lines]
    assert "ALPHA" in keys
    assert "BETA" in keys
    assert "SHARED" in keys
