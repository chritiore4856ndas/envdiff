"""Integration tests for baseline CLI options."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.cli import main


@pytest.fixture()
def runner():
    return CliRunner()


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_save_baseline_creates_file(runner, tmp_path):
    a = _write(tmp_path / ".env.a", "KEY=hello\nEXTRA=yes\n")
    b = _write(tmp_path / ".env.b", "KEY=hello\n")
    baseline = tmp_path / "bl.json"
    result = runner.invoke(
        main, [str(a), str(b), "--save-baseline", str(baseline)]
    )
    assert result.exit_code == 0
    assert baseline.exists()
    data = json.loads(baseline.read_text())
    assert "EXTRA" in data["only_in_a"]


def test_baseline_suppresses_known_diff(runner, tmp_path):
    a = _write(tmp_path / ".env.a", "KEY=hello\nEXTRA=yes\n")
    b = _write(tmp_path / ".env.b", "KEY=hello\n")
    baseline = tmp_path / "bl.json"
    # First run: save baseline
    runner.invoke(main, [str(a), str(b), "--save-baseline", str(baseline)])
    # Second run: diff against baseline — no new differences
    result = runner.invoke(
        main, [str(a), str(b), "--baseline", str(baseline)]
    )
    assert result.exit_code == 0
    assert "No new differences" in result.output or "No new differences" in (result.stderr or "")


def test_baseline_shows_new_diff(runner, tmp_path):
    a = _write(tmp_path / ".env.a", "KEY=hello\n")
    b = _write(tmp_path / ".env.b", "KEY=hello\n")
    baseline = tmp_path / "bl.json"
    runner.invoke(main, [str(a), str(b), "--save-baseline", str(baseline)])

    # Now introduce a new difference
    _write(tmp_path / ".env.a", "KEY=hello\nNEW_KEY=surprise\n")
    result = runner.invoke(
        main, [str(tmp_path / ".env.a"), str(b), "--baseline", str(baseline)]
    )
    assert "NEW_KEY" in result.output


def test_missing_baseline_file_exits_with_code_2(runner, tmp_path):
    a = _write(tmp_path / ".env.a", "KEY=1\n")
    b = _write(tmp_path / ".env.b", "KEY=1\n")
    result = runner.invoke(
        main, [str(a), str(b), "--baseline", str(tmp_path / "no_such.json")]
    )
    assert result.exit_code == 2
