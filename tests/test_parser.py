"""Tests for envdiff.parser."""

import textwrap
from pathlib import Path

import pytest

from envdiff.parser import parse_env_file, _strip_quotes


@pytest.fixture()
def tmp_env(tmp_path):
    """Helper that writes content to a temp .env file and returns its path."""
    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(textwrap.dedent(content), encoding="utf-8")
        return p
    return _write


def test_basic_key_value(tmp_env):
    path = tmp_env("""
        APP_ENV=production
        PORT=8080
    """)
    result = parse_env_file(path)
    assert result == {"APP_ENV": "production", "PORT": "8080"}


def test_ignores_comments_and_blanks(tmp_env):
    path = tmp_env("""
        # this is a comment
        DEBUG=true

        # another comment
        SECRET=abc123
    """)
    result = parse_env_file(path)
    assert "DEBUG" in result
    assert "SECRET" in result
    assert len(result) == 2


def test_empty_value_returns_none(tmp_env):
    path = tmp_env("EMPTY_KEY=\n")
    result = parse_env_file(path)
    assert result["EMPTY_KEY"] is None


def test_quoted_values(tmp_env):
    path = tmp_env("""
        SINGLE='hello world'
        DOUBLE="hello world"
    """)
    result = parse_env_file(path)
    assert result["SINGLE"] == "hello world"
    assert result["DOUBLE"] == "hello world"


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_env_file("/nonexistent/.env")


def test_invalid_syntax_raises(tmp_env):
    path = tmp_env("THIS IS INVALID\n")
    with pytest.raises(ValueError, match="Invalid syntax"):
        parse_env_file(path)


def test_invalid_syntax_includes_line_number(tmp_env):
    """Error message should mention the offending line number."""
    path = tmp_env("""
        VALID=ok
        THIS IS INVALID
        ALSO_VALID=yes
    """)
    with pytest.raises(ValueError, match="line 2"):
        parse_env_file(path)


@pytest.mark.parametrize("value,expected", [
    ('"quoted"', "quoted"),
    ("'quoted'", "quoted"),
    ("unquoted", "unquoted"),
    ('"mismatched\'', '"mismatched\''),
])
def test_strip_quotes(value, expected):
    assert _strip_quotes(value) == expected
