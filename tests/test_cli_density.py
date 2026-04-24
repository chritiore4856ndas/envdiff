import json
import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_density import DensityReport, density_results
from envdiff.cli_density import _format_report, apply_density
from click.testing import CliRunner
import click


def _result(
    only_in_a=(),
    only_in_b=(),
    mismatched=None,
    matching=None,
) -> DiffResult:
    return DiffResult(
        only_in_a=set(only_in_a),
        only_in_b=set(only_in_b),
        mismatched=dict(mismatched or {}),
        matching=dict(matching or {}),
    )


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def _results():
    return [
        _result(matching={"A": "1", "B": "2", "C": "3"}),
        _result(only_in_b={"B", "C"}, matching={"A": "1"}),
    ]


def test_apply_density_returns_false_when_flag_off(_results):
    activated = apply_density(_results, ["prod", "dev"], False, 0.8, False)
    assert activated is False


def test_apply_density_returns_true_when_flag_on(_results, runner, capsys):
    with runner.isolated_filesystem():
        activated = apply_density(_results, ["prod", "dev"], True, 0.8, False)
    assert activated is True


def test_format_report_empty():
    report = DensityReport(entries=[])
    out = _format_report(report, 0.8)
    assert "no density data" in out


def test_format_report_shows_env_name(_results):
    report = density_results(_results, names=["prod", "dev"])
    out = _format_report(report, 0.8)
    assert "prod" in out
    assert "dev" in out


def test_format_report_marks_sparse(_results):
    report = density_results(_results, names=["prod", "dev"])
    out = _format_report(report, 0.8)
    assert "SPARSE" in out


def test_format_report_all_dense():
    r = _result(matching={"A": "1", "B": "2"})
    report = density_results([r], names=["full"])
    out = _format_report(report, 0.8)
    assert "All environments meet" in out


def test_apply_density_json_output(_results, runner):
    @click.command()
    def cmd():
        apply_density(_results, ["prod", "dev"], True, 0.8, True)

    result = runner.invoke(cmd)
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "entries" in data
    assert len(data["entries"]) == 2
