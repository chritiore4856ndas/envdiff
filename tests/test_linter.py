"""Tests for envdiff.linter."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.linter import lint_env_file


@pytest.fixture()
def tmp_env(tmp_path: Path):
    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(content)
        return p

    return _write


def test_clean_file_has_no_issues(tmp_env):
    p = tmp_env("DATABASE_URL=postgres://localhost/db\nSECRET_KEY=abc123\n")
    result = lint_env_file(p)
    assert result.ok
    assert result.errors == []
    assert result.warnings == []


def test_missing_equals_is_error(tmp_env):
    p = tmp_env("BADLINE\n")
    result = lint_env_file(p)
    assert not result.ok
    assert any("missing '='" in i.message for i in result.errors)


def test_duplicate_key_is_warning(tmp_env):
    p = tmp_env("FOO=1\nFOO=2\n")
    result = lint_env_file(p)
    assert any("Duplicate" in i.message for i in result.warnings)


def test_lowercase_key_is_warning(tmp_env):
    p = tmp_env("my_key=value\n")
    result = lint_env_file(p)
    assert any("uppercase" in i.message for i in result.warnings)


def test_key_with_spaces_is_error(tmp_env):
    p = tmp_env("MY KEY=value\n")
    result = lint_env_file(p)
    assert any("spaces" in i.message for i in result.errors)


def test_empty_value_is_warning(tmp_env):
    p = tmp_env("EMPTY_KEY=\n")
    result = lint_env_file(p)
    assert any("no value" in i.message for i in result.warnings)


def test_comments_and_blanks_are_ignored(tmp_env):
    p = tmp_env("# comment\n\nVALID=yes\n")
    result = lint_env_file(p)
    assert result.ok


def test_missing_file_is_error():
    result = lint_env_file("/nonexistent/path/.env")
    assert not result.ok
    assert any("not found" in i.message.lower() for i in result.errors)


def test_lint_result_path_matches_input(tmp_env):
    p = tmp_env("KEY=val\n")
    result = lint_env_file(p)
    assert result.path == str(p)


def test_multiple_issues_collected(tmp_env):
    # lowercase key + empty value — two separate warnings
    p = tmp_env("lower_key=\n")
    result = lint_env_file(p)
    assert len(result.issues) >= 2
