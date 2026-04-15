"""Integration tests for the envdiff CLI."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.cli import main


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_identical_files_exits_zero(tmp_path: Path, runner: CliRunner) -> None:
    a = _write(tmp_path / ".env.a", "KEY=value\nFOO=bar\n")
    b = _write(tmp_path / ".env.b", "KEY=value\nFOO=bar\n")
    result = runner.invoke(main, [str(a), str(b), "--no-color"])
    assert result.exit_code == 0
    assert "No differences" in result.output


def test_diff_reported_in_text(tmp_path: Path, runner: CliRunner) -> None:
    a = _write(tmp_path / ".env.a", "SECRET=abc\nDB=local\n")
    b = _write(tmp_path / ".env.b", "DB=prod\n")
    result = runner.invoke(main, [str(a), str(b), "--no-color"])
    assert result.exit_code == 0
    assert "SECRET" in result.output
    assert "DB" in result.output


def test_exit_code_flag_triggers_on_diff(tmp_path: Path, runner: CliRunner) -> None:
    a = _write(tmp_path / ".env.a", "KEY=1\n")
    b = _write(tmp_path / ".env.b", "OTHER=2\n")
    result = runner.invoke(main, [str(a), str(b), "--exit-code", "--no-color"])
    assert result.exit_code == 1


def test_exit_code_flag_zero_on_no_diff(tmp_path: Path, runner: CliRunner) -> None:
    a = _write(tmp_path / ".env.a", "KEY=1\n")
    b = _write(tmp_path / ".env.b", "KEY=1\n")
    result = runner.invoke(main, [str(a), str(b), "--exit-code", "--no-color"])
    assert result.exit_code == 0


def test_json_format_output(tmp_path: Path, runner: CliRunner) -> None:
    a = _write(tmp_path / ".env.a", "SECRET=abc\n")
    b = _write(tmp_path / ".env.b", "SECRET=xyz\n")
    result = runner.invoke(main, [str(a), str(b), "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["mismatched"]["SECRET"] == {"a": "abc", "b": "xyz"}


def test_table_format_output(tmp_path: Path, runner: CliRunner) -> None:
    a = _write(tmp_path / ".env.a", "MISSING_KEY=1\n")
    b = _write(tmp_path / ".env.b", "OTHER=2\n")
    result = runner.invoke(main, [str(a), str(b), "--format", "table", "--no-color"])
    assert result.exit_code == 0
    assert "KEY" in result.output
    assert "STATUS" in result.output
