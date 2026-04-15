"""Integration tests for --exclude / --include CLI flags."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.cli import main


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_exclude_hides_key(runner: CliRunner, tmp_path: Path) -> None:
    a = tmp_path / ".env.a"
    b = tmp_path / ".env.b"
    _write(a, "SECRET=abc\nDEBUG=true\n")
    _write(b, "DEBUG=true\n")

    result = runner.invoke(main, [str(a), str(b), "--exclude", "SECRET"])
    assert result.exit_code == 0
    assert "SECRET" not in result.output


def test_exclude_missing_key_suppresses_diff(runner: CliRunner, tmp_path: Path) -> None:
    a = tmp_path / ".env.a"
    b = tmp_path / ".env.b"
    _write(a, "ONLY_A=1\n")
    _write(b, "ONLY_B=2\n")

    # Exclude both differing keys → no diff reported
    result = runner.invoke(main, [str(a), str(b), "--exclude", "ONLY_A", "--exclude", "ONLY_B"])
    assert "no differences" in result.output.lower() or result.exit_code == 0


def test_include_shows_only_matching(runner: CliRunner, tmp_path: Path) -> None:
    a = tmp_path / ".env.a"
    b = tmp_path / ".env.b"
    _write(a, "LOG_LEVEL=info\nSECRET=abc\n")
    _write(b, "LOG_LEVEL=debug\nSECRET=abc\n")

    result = runner.invoke(main, [str(a), str(b), "--include", "LOG_LEVEL"])
    assert "LOG_LEVEL" in result.output
    assert "SECRET" not in result.output


def test_exclude_regex_wildcard(runner: CliRunner, tmp_path: Path) -> None:
    a = tmp_path / ".env.a"
    b = tmp_path / ".env.b"
    _write(a, "AWS_KEY=x\nAWS_SECRET=y\nAPP=z\n")
    _write(b, "APP=z\n")

    result = runner.invoke(main, [str(a), str(b), "--exclude", "AWS_.*"])
    assert "AWS_" not in result.output
