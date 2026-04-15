"""Tests for envdiff.cli_schema."""
from __future__ import annotations

import json
import pathlib

import pytest
from click.testing import CliRunner
import click

from envdiff.cli_schema import schema_options, apply_schema


@pytest.fixture()
def runner():
    return CliRunner()


def _write(path: pathlib.Path, content: str) -> str:
    path.write_text(content)
    return str(path)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_schema(tmp_path: pathlib.Path, rules: list[dict]) -> str:
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(rules))
    return str(p)


# ---------------------------------------------------------------------------
# apply_schema unit tests (called directly, not via Click)
# ---------------------------------------------------------------------------

def test_no_schema_path_is_noop(tmp_path, capsys):
    env = _write(tmp_path / ".env", "KEY=val\n")
    apply_schema(None, env, exit_on_violation=False)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_valid_env_prints_passed(tmp_path, capsys):
    schema = _make_schema(tmp_path, [{"key": "KEY", "required": True}])
    env = _write(tmp_path / ".env", "KEY=value\n")
    apply_schema(schema, env, exit_on_violation=False)
    captured = capsys.readouterr()
    assert "passed" in captured.out


def test_missing_required_key_prints_violation(tmp_path, capsys):
    schema = _make_schema(tmp_path, [{"key": "REQUIRED_KEY", "required": True}])
    env = _write(tmp_path / ".env", "OTHER=x\n")
    apply_schema(schema, env, exit_on_violation=False)
    captured = capsys.readouterr()
    assert "REQUIRED_KEY" in captured.out
    assert "[missing]" in captured.out


def test_violation_exits_with_code_2(tmp_path):
    schema = _make_schema(tmp_path, [{"key": "MUST_EXIST", "required": True}])
    env = _write(tmp_path / ".env", "")
    with pytest.raises(SystemExit) as exc_info:
        apply_schema(schema, env, exit_on_violation=True)
    assert exc_info.value.code == 2


# ---------------------------------------------------------------------------
# schema_options decorator wires up the --schema flag
# ---------------------------------------------------------------------------

def test_schema_options_adds_flag(runner, tmp_path):
    schema = _make_schema(tmp_path, [{"key": "K", "required": True}])
    env = _write(tmp_path / ".env", "K=1\n")

    @schema_options
    @click.command()
    @click.argument("env_file")
    @click.pass_context
    def cmd(ctx, env_file, schema_path):
        apply_schema(schema_path, env_file, exit_on_violation=False)

    result = runner.invoke(cmd, ["--schema", schema, env])
    assert result.exit_code == 0
    assert "passed" in result.output
