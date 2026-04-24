import pytest
from click.testing import CliRunner
from envdiff.comparator import DiffResult
from envdiff.cli_saturation import _format_report, apply_saturation, saturation_options
from envdiff.differ_saturation import saturation_diff


def _result(only_in_a=None, only_in_b=None, mismatched=None, matching=None):
    return DiffResult(
        only_in_a=only_in_a or [],
        only_in_b=only_in_b or [],
        mismatched=mismatched or [],
        matching=matching or [],
    )


def test_apply_saturation_returns_false_when_flag_off():
    r = _result(matching=["A"])
    result = apply_saturation([r], ["dev", "prod"], saturation=False, saturation_threshold=0.8)
    assert result is False


def test_apply_saturation_returns_true_when_flag_on(capsys):
    r = _result(matching=["A"])
    result = apply_saturation([r], ["dev", "prod"], saturation=True, saturation_threshold=0.8)
    assert result is True


def test_format_report_empty():
    report = saturation_diff([])
    text = _format_report(report, threshold=0.8)
    assert "No saturation data" in text


def test_format_report_shows_env_name():
    r = _result(matching=["X", "Y"])
    report = saturation_diff([r], env_names=["alpha", "beta"])
    text = _format_report(report, threshold=0.8)
    assert "alpha" in text
    assert "beta" in text


def test_format_report_flags_low_saturation():
    r = _result(only_in_a=["K1", "K2", "K3"], matching=["K4"])
    report = saturation_diff([r], env_names=["rich", "sparse"])
    text = _format_report(report, threshold=0.9)
    assert "[LOW]" in text


def test_format_report_no_flag_when_above_threshold():
    r = _result(matching=["K1", "K2", "K3"])
    report = saturation_diff([r], env_names=["a", "b"])
    text = _format_report(report, threshold=0.5)
    assert "[LOW]" not in text
