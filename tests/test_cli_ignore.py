from click.testing import CliRunner
import click
import pytest

from envdiff.comparator import DiffResult
from envdiff.cli_ignore import apply_ignore_options


@pytest.fixture
def rich_result():
    return DiffResult(
        only_in_a={"SECRET_KEY"},
        only_in_b={"NEW_FLAG"},
        mismatched={"API_TOKEN": ("a", "b")},
        matching={"DEBUG": "true"},
    )


def test_no_patterns_unchanged(rich_result, tmp_path):
    result = apply_ignore_options(rich_result, ignore_file=str(tmp_path / "none"), ignore_patterns=[])
    assert "SECRET_KEY" in result.only_in_a
    assert "API_TOKEN" in result.mismatched


def test_inline_pattern_removes_key(rich_result, tmp_path):
    result = apply_ignore_options(rich_result, ignore_file=str(tmp_path / "none"), ignore_patterns=["SECRET_KEY"])
    assert "SECRET_KEY" not in result.only_in_a


def test_ignore_file_patterns_applied(rich_result, tmp_path):
    f = tmp_path / ".envdiffignore"
    f.write_text("*TOKEN*\n")
    result = apply_ignore_options(rich_result, ignore_file=str(f), ignore_patterns=[])
    assert "API_TOKEN" not in result.mismatched


def test_inline_and_file_patterns_combined(rich_result, tmp_path):
    f = tmp_path / ".envdiffignore"
    f.write_text("NEW_FLAG\n")
    result = apply_ignore_options(rich_result, ignore_file=str(f), ignore_patterns=["SECRET_KEY"])
    assert "SECRET_KEY" not in result.only_in_a
    assert "NEW_FLAG" not in result.only_in_b
