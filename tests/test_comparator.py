"""Tests for envdiff.comparator."""

from envdiff.comparator import compare, DiffResult


def test_identical_envs_no_diff():
    env = {"KEY": "value", "PORT": "8080"}
    result = compare(env, env.copy())
    assert not result.has_diff
    assert sorted(result.matching) == ["KEY", "PORT"]


def test_key_only_in_a():
    result = compare({"EXTRA": "yes", "SHARED": "x"}, {"SHARED": "x"})
    assert result.only_in_a == ["EXTRA"]
    assert result.only_in_b == []
    assert result.has_diff


def test_key_only_in_b():
    result = compare({"SHARED": "x"}, {"NEW_KEY": "value", "SHARED": "x"})
    assert result.only_in_b == ["NEW_KEY"]
    assert result.only_in_a == []
    assert result.has_diff


def test_mismatched_values():
    env_a = {"DB_HOST": "localhost", "PORT": "5432"}
    env_b = {"DB_HOST": "db.prod.example.com", "PORT": "5432"}
    result = compare(env_a, env_b)
    assert "DB_HOST" in result.mismatched
    assert result.mismatched["DB_HOST"] == ("localhost", "db.prod.example.com")
    assert "PORT" in result.matching
    assert result.has_diff


def test_none_value_mismatch():
    """A key set to empty vs a key with a real value should be mismatched."""
    result = compare({"SECRET": None}, {"SECRET": "abc"})
    assert "SECRET" in result.mismatched
    assert result.mismatched["SECRET"] == (None, "abc")


def test_both_none_values_match():
    result = compare({"EMPTY": None}, {"EMPTY": None})
    assert not result.has_diff
    assert "EMPTY" in result.matching


def test_empty_envs():
    result = compare({}, {})
    assert not result.has_diff
    assert result == DiffResult()
