import pytest
from click.testing import CliRunner
from envdiff.comparator import DiffResult
from envdiff.differ_lifecycle import lifecycle_diff, LifecycleReport
from envdiff.cli_lifecycle import apply_lifecycle, _format_report


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


def test_apply_lifecycle_returns_false_when_flag_off():
    r = _result(matching={"K": "v"})
    result = apply_lifecycle([r], lifecycle=False, lifecycle_verbose=False)
    assert result is False


def test_apply_lifecycle_returns_true_when_flag_on(capsys):
    r0 = _result(mismatched={"BAD": ("a", "b")})
    r1 = _result(mismatched={"BAD": ("a", "c")})
    result = apply_lifecycle([r0, r1], lifecycle=True, lifecycle_verbose=False)
    assert result is True


def test_format_report_hides_stable_by_default():
    r = _result(matching={"STABLE_KEY": "v"})
    report = lifecycle_diff([r])
    output = _format_report(report, verbose=False)
    assert "STABLE_KEY" not in output


def test_format_report_shows_stable_when_verbose():
    r = _result(matching={"STABLE_KEY": "v"})
    report = lifecycle_diff([r])
    output = _format_report(report, verbose=True)
    assert "STABLE_KEY" in output


def test_format_report_shows_degrading_key():
    r0 = _result(mismatched={"BAD": ("a", "b")})
    r1 = _result(mismatched={"BAD": ("a", "c")})
    report = lifecycle_diff([r0, r1])
    output = _format_report(report, verbose=False)
    assert "BAD" in output
    assert "degrading" in output


def test_format_report_empty_when_all_stable_and_not_verbose():
    r = _result(matching={"A": "1", "B": "2"})
    report = lifecycle_diff([r])
    output = _format_report(report, verbose=False)
    assert output == ""


def test_format_report_shows_new_marker():
    r0 = _result(matching={"A": "v"})
    r1 = _result(matching={"A": "v", "B": "v"})
    report = lifecycle_diff([r0, r1])
    output = _format_report(report, verbose=False)
    assert "[+]" in output
    assert "B" in output
