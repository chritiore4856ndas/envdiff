"""Tests for envdiff.cli_flux."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.cli_flux import _format_report, apply_flux
from envdiff.differ_flux import flux_diff


def _result(
    only_in_a=(),
    only_in_b=(),
    mismatched=None,
    matching=None,
) -> DiffResult:
    return DiffResult(
        only_in_a=list(only_in_a),
        only_in_b=list(only_in_b),
        mismatched=mismatched or {},
        matching=matching or {},
    )


def test_apply_flux_returns_false_when_flag_off():
    results = [_result(only_in_a=["KEY"])]
    assert apply_flux(results, flux=False, flux_threshold=0.5) is False


def test_apply_flux_returns_true_when_flag_on(capsys):
    results = [_result(matching={"K": "v"})]
    result = apply_flux(results, flux=True, flux_threshold=0.5)
    assert result is True


def test_apply_flux_prints_header(capsys):
    results = [_result(matching={"K": "v"})]
    apply_flux(results, flux=True, flux_threshold=0.5)
    out = capsys.readouterr().out
    assert "Flux Analysis" in out


def test_apply_flux_prints_average_rate(capsys):
    r1 = _result(only_in_a=["X"])
    r2 = _result(matching={"X": "v"})
    apply_flux([r1, r2], flux=True, flux_threshold=0.0)
    out = capsys.readouterr().out
    assert "Average flux rate" in out


def test_apply_flux_shows_most_volatile(capsys):
    r1 = _result(only_in_a=["FAST"])
    r2 = _result(matching={"FAST": "v"})
    r3 = _result(only_in_a=["FAST"])
    apply_flux([r1, r2, r3], flux=True, flux_threshold=0.0)
    out = capsys.readouterr().out
    assert "FAST" in out


def test_format_report_empty_gives_placeholder():
    report = flux_diff([])
    text = _format_report(report)
    assert "no keys" in text


def test_format_report_shows_high_flux_key():
    r1 = _result(only_in_a=["HOT"])
    r2 = _result(matching={"HOT": "v"})
    r3 = _result(only_in_a=["HOT"])
    report = flux_diff([r1, r2, r3])
    text = _format_report(report, threshold=0.5)
    assert "HOT" in text


def test_format_report_hides_low_flux_key():
    r1 = _result(matching={"CALM": "v"})
    r2 = _result(matching={"CALM": "v"})
    report = flux_diff([r1, r2])
    text = _format_report(report, threshold=0.5)
    assert "CALM" not in text
