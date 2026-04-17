"""Tests for envdiff.cli_snapshot via a lightweight dummy Click command."""
from __future__ import annotations

import json
from pathlib import Path

import click
from click.testing import CliRunner
import pytest

from envdiff.cli_snapshot import snapshot_options, apply_snapshot


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def _write(p: Path, content: str) -> str:
    p.write_text(content)
    return str(p)


def _cmd(runner: CliRunner, args, tmp_path: Path):
    @click.command()
    @click.argument("file_a", default="")
    @click.argument("file_b", default="")
    @snapshot_options
    @click.pass_context
    def cmd(ctx, file_a, file_b, snapshot_save, snapshot_diff, snapshot_store):
        apply_snapshot(ctx, file_a, file_b, snapshot_save, snapshot_diff, snapshot_store)

    store = str(tmp_path / "store")
    return runner.invoke(cmd, args + ["--snapshot-store", store], catch_exceptions=False)


def test_save_snapshot_prints_confirmation(runner: CliRunner, tmp_path: Path) -> None:
    env = _write(tmp_path / ".env", "KEY=val\n")
    result = _cmd(runner, [env, "", "--snapshot-save", "prod"], tmp_path)
    assert "saved" in result.output
    assert result.exit_code == 0


def test_snapshot_diff_clean_exits_zero(runner: CliRunner, tmp_path: Path) -> None:
    env = _write(tmp_path / ".env", "KEY=val\n")
    _cmd(runner, [env, "", "--snapshot-save", "prod"], tmp_path)
    result = _cmd(runner, [env, "", "--snapshot-diff", "prod"], tmp_path)
    data = json.loads(result.output)
    assert data["clean"] is True
    assert result.exit_code == 0


def test_snapshot_diff_dirty_exits_one(runner: CliRunner, tmp_path: Path) -> None:
    snap_env = _write(tmp_path / "snap.env", "KEY=val\nEXTRA=x\n")
    _cmd(runner, [snap_env, "", "--snapshot-save", "prod"], tmp_path)
    cur_env = _write(tmp_path / "cur.env", "KEY=val\n")
    result = _cmd(runner, [cur_env, "", "--snapshot-diff", "prod"], tmp_path)
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["clean"] is False
