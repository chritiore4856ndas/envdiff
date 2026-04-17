import json
import pytest
from click.testing import CliRunner
from envdiff.cli_cascade import apply_cascade
import click


@pytest.fixture()
def runner():
    return CliRunner()


def _write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


@click.command()
@click.pass_context
def _cmd(ctx):
    """Dummy command that calls apply_cascade via context."""
    pass


def test_no_cascade_flag_returns_false(tmp_path):
    result = apply_cascade(cascade=[], cascade_json=False)
    assert result is False


def test_cascade_clean_output(tmp_path, runner):
    a = _write(tmp_path, "a.env", "KEY=1\n")
    b = _write(tmp_path, "b.env", "KEY=1\n")
    result = apply_cascade(cascade=[a, b], cascade_json=False)
    assert result is True


def test_cascade_json_output(tmp_path, capsys):
    a = _write(tmp_path, "a.env", "KEY=1\n")
    b = _write(tmp_path, "b.env", "KEY=2\n")
    # wrap in a click context so echo works
    @click.command()
    def _inner():
        apply_cascade(cascade=[a, b], cascade_json=True)

    r = CliRunner().invoke(_inner, [])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert "steps" in data
    assert data["clean"] is False


def test_cascade_text_output_shows_diff(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=1\nSECRET=x\n")
    b = _write(tmp_path, "b.env", "KEY=2\n")

    @click.command()
    def _inner():
        apply_cascade(cascade=[a, b], cascade_json=False)

    r = CliRunner().invoke(_inner, [])
    assert "KEY" in r.output or "SECRET" in r.output


def test_cascade_requires_two_files(tmp_path):
    a = _write(tmp_path, "a.env", "KEY=1\n")
    with pytest.raises(Exception):
        apply_cascade(cascade=[a], cascade_json=False)
