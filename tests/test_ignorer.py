import pytest
from envdiff.comparator import DiffResult
from envdiff.ignorer import load_ignore_patterns, apply_ignore


@pytest.fixture
def rich_result():
    return DiffResult(
        only_in_a={"SECRET_KEY", "DB_HOST"},
        only_in_b={"NEW_FLAG"},
        mismatched={"PORT": ("8080", "9090"), "API_TOKEN": ("abc", "xyz")},
        matching={"DEBUG": "true"},
    )


def test_no_patterns_returns_same(rich_result):
    result = apply_ignore(rich_result, [])
    assert result.only_in_a == rich_result.only_in_a
    assert result.only_in_b == rich_result.only_in_b
    assert result.mismatched == rich_result.mismatched


def test_exact_key_removed_from_only_in_a(rich_result):
    result = apply_ignore(rich_result, ["SECRET_KEY"])
    assert "SECRET_KEY" not in result.only_in_a
    assert "DB_HOST" in result.only_in_a


def test_glob_removes_matching_keys(rich_result):
    result = apply_ignore(rich_result, ["*TOKEN*"])
    assert "API_TOKEN" not in result.mismatched
    assert "PORT" in result.mismatched


def test_pattern_removes_from_only_in_b(rich_result):
    result = apply_ignore(rich_result, ["NEW_FLAG"])
    assert "NEW_FLAG" not in result.only_in_b


def test_matching_keys_also_filtered(rich_result):
    result = apply_ignore(rich_result, ["DEBUG"])
    assert "DEBUG" not in result.matching


def test_load_ignore_patterns_missing_file(tmp_path):
    patterns = load_ignore_patterns(tmp_path / ".envdiffignore")
    assert patterns == []


def test_load_ignore_patterns_reads_file(tmp_path):
    f = tmp_path / ".envdiffignore"
    f.write_text("# comment\nSECRET_KEY\n*TOKEN*\n\nDEBUG\n")
    patterns = load_ignore_patterns(f)
    assert patterns == ["SECRET_KEY", "*TOKEN*", "DEBUG"]


def test_load_ignore_skips_blank_lines(tmp_path):
    f = tmp_path / ".envdiffignore"
    f.write_text("\n   \nKEY\n")
    patterns = load_ignore_patterns(f)
    assert patterns == ["KEY"]
