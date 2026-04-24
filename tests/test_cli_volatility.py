"""Tests for envdiff.cli_volatility."""
import json
import pytest
from click.testing import CliRunner
import click

from envdiff.comparator import DiffResult
from envdiff.cli_volatility import apply_volatility, volatility_options, _format_report
from envdiff.differ_volatility import volatility_diff


def _result(matching=None, only_in_a=None, only_in_b=None, mismatched=None):
    return DiffResult(
        matching=matching or {},
        only_in_a=only_in_a or {},
        only_in_b=only_in_b or {},
        mismatched=mismatched or {},
    )


def test_apply_volatility_returns_false_when_flag_off():
    results = [_result(matching={"A": "1"})]
    out = apply_volatility(results, volatility=False, volatility_top=0, volatility_json=False)
    assert out is False


def test_apply_volatility_returns_true_when_flag_on(capsys):
    results = [_result(matching={"A": "1"})]
    out = apply_volatility(results, volatility=True, volatility_top=0, volatility_json=False)
    assert out is True


def test_format_report_empty():
    report = volatility_diff([])
    text = _format_report(report)
    assert "no keys tracked" in text


def test_format_report_shows_volatile_key():
    results = [_result(only_in_a={"FLAKY": "x"})]
    report = volatility_diff(results)
    text = _format_report(report)
    assert "FLAKY" in text
    assert "VOLATILE" in text


def test_format_report_top_limits_entries():
    results = [
        _result(
            mismatched={"A": ("1", "2"), "B": ("1", "2"), "C": ("1", "2")},
        )
    ]
    report = volatility_diff(results)
    text = _format_report(report, top=2)
    # Only 2 entries should appear in detail lines (after header)
    detail_lines = [l for l in text.splitlines() if "rate=" in l]
    assert len(detail_lines) == 2


def test_volatility_json_output_is_valid_json():
    runner = CliRunner()

    @click.command()
    @volatility_options
    def cmd(**kwargs):
        results = [_result(mismatched={"K": ("a", "b")})]
        apply_volatility(results, **kwargs)

    result = runner.invoke(cmd, ["--volatility", "--volatility-json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "entries" in data
    assert "volatile_count" in data


def test_volatility_top_flag_via_cli():
    runner = CliRunner()

    @click.command()
    @volatility_options
    def cmd(**kwargs):
        results = [
            _result(mismatched={"X": ("a", "b"), "Y": ("c", "d")}),
        ]
        apply_volatility(results, **kwargs)

    result = runner.invoke(cmd, ["--volatility", "--volatility-top", "1"])
    assert result.exit_code == 0
    detail_lines = [l for l in result.output.splitlines() if "rate=" in l]
    assert len(detail_lines) == 1
