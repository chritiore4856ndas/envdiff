"""Integration tests for --export-format / --output CLI options."""
from __future__ import annotations

import json
import os

import pytest
from click.testing import CliRunner

from envdiff.cli import main


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def _write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(content)


def test_export_json_stdout(runner: CliRunner, tmp_path) -> None:
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("FOO=bar\nONLY_A=1\n")
    b.write_text("FOO=bar\nONLY_B=2\n")
    result = runner.invoke(main, [str(a), str(b), "--export-format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "ONLY_A" in data["missing_in_b"]
    assert "ONLY_B" in data["missing_in_a"]


def test_export_csv_stdout(runner: CliRunner, tmp_path) -> None:
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("KEY=one\n")
    b.write_text("KEY=two\n")
    result = runner.invoke(main, [str(a), str(b), "--export-format", "csv"])
    assert result.exit_code == 0
    assert "key,status" in result.output
    assert "mismatched" in result.output


def test_export_markdown_stdout(runner: CliRunner, tmp_path) -> None:
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("ALPHA=1\n")
    b.write_text("ALPHA=1\n")
    result = runner.invoke(main, [str(a), str(b), "--export-format", "markdown"])
    assert result.exit_code == 0
    assert "| Key | Status |" in result.output


def test_export_to_file(runner: CliRunner, tmp_path) -> None:
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    out = tmp_path / "report.json"
    a.write_text("X=1\n")
    b.write_text("X=2\n")
    result = runner.invoke(
        main,
        [str(a), str(b), "--export-format", "json", "--output", str(out)],
    )
    assert result.exit_code == 0
    assert out.exists()
    data = json.loads(out.read_text())
    assert "mismatched" in data


def test_no_export_format_uses_normal_output(runner: CliRunner, tmp_path) -> None:
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("FOO=bar\n")
    b.write_text("FOO=bar\n")
    result = runner.invoke(main, [str(a), str(b)])
    assert result.exit_code == 0
    # Normal text output, not JSON
    assert result.output == "" or "missing" not in result.output
