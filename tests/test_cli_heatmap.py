import pytest
from click.testing import CliRunner
from envdiff.comparator import DiffResult
from envdiff.cli_heatmap import apply_heatmap
import click


@pytest.fixture
def runner():
    return CliRunner()


def _result(only_a=None, only_b=None, mismatched=None) -> DiffResult:
    return DiffResult(
        only_in_a=only_a or {},
        only_in_b=only_b or {},
        mismatched=mismatched or {},
    )


def _run(results, heatmap=True, heatmap_top=10):
    """Helper to capture apply_heatmap output via a dummy Click command."""
    runner = CliRunner()

    @click.command()
    def cmd():
        apply_heatmap(results, heatmap=heatmap, heatmap_top=heatmap_top)

    return runner.invoke(cmd, [])


def test_no_heatmap_flag_produces_no_output():
    r = _result(only_a={"FOO": "bar"})
    result = _run([r], heatmap=False)
    assert result.output == ""


def test_empty_results_shows_no_keys_message():
    result = _run([], heatmap=True)
    assert "no differing keys" in result.output


def test_key_appears_in_heatmap():
    r = _result(only_a={"MY_KEY": "val"})
    result = _run([r], heatmap=True)
    assert "MY_KEY" in result.output


def test_count_shown_in_output():
    r1 = _result(mismatched={"DB_URL": ("a", "b")})
    r2 = _result(only_a={"DB_URL": "a"})
    result = _run([r1, r2], heatmap=True)
    assert "(2)" in result.output


def test_heatmap_top_limits_output():
    keys = {f"KEY_{i}": str(i) for i in range(20)}
    r = _result(only_a=keys)
    result = _run([r], heatmap=True, heatmap_top=3)
    # Each entry line starts with spaces; count lines containing '#'
    lines = [l for l in result.output.splitlines() if "#" in l]
    assert len(lines) == 3
