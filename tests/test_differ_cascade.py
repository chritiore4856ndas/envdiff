import pytest
from pathlib import Path
from envdiff.differ_cascade import cascade_diff, CascadeReport, CascadeStep


@pytest.fixture()
def tmp_envs(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_requires_at_least_two_files(tmp_envs):
    f = tmp_envs("a.env", "KEY=1\n")
    with pytest.raises(ValueError):
        cascade_diff([f])


def test_two_identical_files_is_clean(tmp_envs):
    a = tmp_envs("a.env", "KEY=1\nFOO=bar\n")
    b = tmp_envs("b.env", "KEY=1\nFOO=bar\n")
    report = cascade_diff([a, b])
    assert report.is_clean()
    assert len(report.steps) == 1


def test_two_files_mismatch_detected(tmp_envs):
    a = tmp_envs("a.env", "KEY=1\n")
    b = tmp_envs("b.env", "KEY=2\n")
    report = cascade_diff([a, b])
    assert not report.is_clean()
    assert "KEY" in report.steps[0].result.mismatched


def test_three_files_two_steps(tmp_envs):
    a = tmp_envs("a.env", "KEY=1\n")
    b = tmp_envs("b.env", "KEY=1\nEXTRA=yes\n")
    c = tmp_envs("c.env", "KEY=2\nEXTRA=yes\n")
    report = cascade_diff([a, b, c])
    assert len(report.steps) == 2


def test_missing_key_in_one_step(tmp_envs):
    a = tmp_envs("a.env", "KEY=1\nSECRET=x\n")
    b = tmp_envs("b.env", "KEY=1\n")
    report = cascade_diff([a, b])
    assert "SECRET" in report.steps[0].result.only_in_a


def test_all_drifting_keys_counts_across_steps(tmp_envs):
    a = tmp_envs("a.env", "KEY=1\n")
    b = tmp_envs("b.env", "KEY=2\n")
    c = tmp_envs("c.env", "KEY=3\n")
    report = cascade_diff([a, b, c])
    drifting = report.all_drifting_keys()
    assert drifting["KEY"] == 2


def test_as_dict_structure(tmp_envs):
    a = tmp_envs("a.env", "A=1\n")
    b = tmp_envs("b.env", "A=2\n")
    d = cascade_diff([a, b]).as_dict()
    assert "clean" in d
    assert "steps" in d
    assert "drifting_keys" in d
    assert d["clean"] is False


def test_step_as_dict_has_expected_keys(tmp_envs):
    a = tmp_envs("a.env", "X=1\n")
    b = tmp_envs("b.env", "X=1\n")
    report = cascade_diff([a, b])
    step_dict = report.steps[0].as_dict()
    assert "from" in step_dict
    assert "to" in step_dict
    assert "only_in_a" in step_dict
    assert "mismatched" in step_dict
