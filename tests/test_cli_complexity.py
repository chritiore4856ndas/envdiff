"""Tests for envdiff.cli_complexity."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.cli_complexity import _format_report, apply_complexity
from envdiff.differ_complexity import complexity_diff


def _result(
    matching=None,
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        matching=matching or {},
        only_in_a=only_in_a or {},
        only_in_b=only_in_b or {},
        mismatched=mismatched or {},
    )


def test_apply_complexity_returns_false_when_flag_off():
    r = _result(matching={"K": "v"})
    result = apply_complexity([r], ["dev"], complexity=False)
    assert result is False


def test_apply_complexity_returns_true_when_flag_on(capsys):
    r = _result(matching={"K": "v"})
    result = apply_complexity([r], ["dev"], complexity=True)
    assert result is True
    out = capsys.readouterr().out
    assert "complexity" in out


def test_format_report_empty():
    report = complexity_diff([])
    text = _format_report(report)
    assert "no data" in text


def test_format_report_shows_env_name():
    r = _result(matching={"A": "1"})
    report = complexity_diff([r], labels=["production"])
    text = _format_report(report)
    assert "production" in text


def test_format_report_shows_complex_flag():
    r = _result(only_in_a={"A": "1"}, only_in_b={"B": "2"}, mismatched={"C": ("x", "y")})
    report = complexity_diff([r], labels=["chaos"])
    text = _format_report(report, threshold=0.4)
    assert "[COMPLEX]" in text


def test_format_report_no_complex_flag_for_clean_env():
    r = _result(matching={"A": "1", "B": "2"})
    report = complexity_diff([r], labels=["clean"])
    text = _format_report(report)
    assert "[COMPLEX]" not in text


def test_format_report_shows_average_score():
    r = _result(matching={"A": "1"})
    report = complexity_diff([r], labels=["env"])
    text = _format_report(report)
    assert "average score" in text


def test_format_report_shows_most_complex():
    r1 = _result(matching={"A": "1"})
    r2 = _result(only_in_a={"B": "2"}, only_in_b={"C": "3"})
    report = complexity_diff([r1, r2], labels=["alpha", "beta"])
    text = _format_report(report)
    assert "most complex" in text
    assert "beta" in text
