import pytest
from click.testing import CliRunner
from envdiff.comparator import DiffResult
from envdiff.cli_variance import apply_variance
import click


@pytest.fixture
def runner():
    return CliRunner()


def _result(matching=None, mismatched=None, only_in_a=None, only_in_b=None):
    return DiffResult(
        matching=matching or {},
        only_in_a=set(only_in_a or []),
        only_in_b=set(only_in_b or []),
        mismatched=mismatched or {},
    )


def _cmd(results, variance=True, unstable_only=False):
    @click.command()
    def cmd():
        apply_variance(results, variance=variance, variance_unstable_only=unstable_only)
    return cmd


def test_no_variance_flag_returns_false(runner):
    r = _result(matching={"K": "v"})
    result = runner.invoke(_cmd([r], variance=False))
    assert result.exit_code == 0
    assert result.output == ""


def test_all_stable_prints_stable_message(runner):
    r = _result(matching={"K": "v"})
    result = runner.invoke(_cmd([r], variance=True))
    assert "stable" in result.output


def test_unstable_key_appears_in_output(runner):
    r1 = _result(matching={"K": "v1"})
    r2 = _result(matching={"K": "v2"})
    result = runner.invoke(_cmd([r1, r2], variance=True))
    assert "K" in result.output
    assert "unstable" in result.output


def test_unstable_only_hides_stable_keys(runner):
    r1 = _result(matching={"STABLE": "x", "UNSTABLE": "a"})
    r2 = _result(matching={"STABLE": "x", "UNSTABLE": "b"})
    result = runner.invoke(_cmd([r1, r2], variance=True, unstable_only=True))
    assert "UNSTABLE" in result.output
    assert "STABLE" not in result.output
