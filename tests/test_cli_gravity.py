"""Tests for envdiff.cli_gravity."""
from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.cli_gravity import _format_report, apply_gravity
from envdiff.differ_gravity import gravity_diff


def _result(matching=None, only_in_a=None, only_in_b=None, mismatched=None):
    return DiffResult(
        matching=matching or {},
        only_in_a=only_in_a or {},
        only_in_b=only_in_b or {},
        mismatched=mismatched or {},
    )


@pytest.fixture
def _results():
    return [
        _result(only_in_a={"HEAVY_KEY": "x"}),
        _result(only_in_a={"HEAVY_KEY": "x"}, matching={"STABLE": "y"}),
        _result(matching={"HEAVY_KEY": "x", "STABLE": "y"}),
    ]


def test_apply_gravity_returns_false_when_flag_off(_results):
    result = apply_gravity(
        _results,
        gravity=False,
        gravity_heavy_only=False,
        gravity_top=0,
    )
    assert result is False


def test_apply_gravity_returns_true_when_flag_on(_results, capsys):
    result = apply_gravity(
        _results,
        gravity=True,
        gravity_heavy_only=False,
        gravity_top=0,
    )
    assert result is True
    captured = capsys.readouterr()
    assert "Gravity Report" in captured.out


def test_format_report_empty():
    report = gravity_diff([])
    text = _format_report(report, heavy_only=False, top_n=0)
    assert "No gravity" in text


def test_format_report_shows_key():
    r = _result(only_in_a={"MY_KEY": "v"})
    report = gravity_diff([r])
    text = _format_report(report, heavy_only=False, top_n=0)
    assert "MY_KEY" in text


def test_format_report_heavy_only_hides_stable():
    r = _result(only_in_a={"BAD": "x"}, matching={"GOOD": "y"})
    report = gravity_diff([r])
    text = _format_report(report, heavy_only=True, top_n=0)
    assert "BAD" in text
    assert "GOOD" not in text


def test_format_report_top_limits_entries():
    r = _result(only_in_a={"A": "1", "B": "2", "C": "3"})
    report = gravity_diff([r])
    text = _format_report(report, heavy_only=False, top_n=2)
    # Only 2 key lines (plus header + separator = 4 lines total)
    lines = [l for l in text.splitlines() if l.strip() and not l.startswith("-") and "Gravity" not in l]
    assert len(lines) == 2
