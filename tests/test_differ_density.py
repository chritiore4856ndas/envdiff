import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_density import DensityEntry, DensityReport, density_results


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


def test_empty_results_gives_empty_report():
    report = density_results([])
    assert report.entries == []


def test_single_result_all_keys_present():
    r = _result(matching={"A": "1", "B": "2"})
    report = density_results([r], names=["prod"])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.env_name == "prod"
    assert entry.present == 2
    assert entry.total == 2
    assert entry.density_rate() == 1.0


def test_missing_key_reduces_density():
    # only_in_b means the key is absent from env "a"
    r = _result(only_in_b={"MISSING"}, matching={"A": "1"})
    report = density_results([r], names=["staging"])
    entry = report.entries[0]
    # total = 2 (MISSING + A), present = 1 (A only)
    assert entry.total == 2
    assert entry.present == 1
    assert entry.density_rate() == pytest.approx(0.5)


def test_is_dense_default_threshold():
    e = DensityEntry(env_name="x", present=9, total=10)
    assert e.is_dense() is True

    e2 = DensityEntry(env_name="y", present=7, total=10)
    assert e2.is_dense() is False


def test_sparse_filters_below_threshold():
    r1 = _result(matching={"A": "1", "B": "2", "C": "3"})
    r2 = _result(only_in_b={"B", "C"}, matching={"A": "1"})
    report = density_results([r1, r2], names=["full", "sparse"])
    sparse = report.sparse(threshold=0.8)
    assert any(e.env_name == "sparse" for e in sparse)
    assert all(e.env_name != "full" for e in sparse)


def test_default_names_used_when_none_provided():
    r = _result(matching={"K": "v"})
    report = density_results([r])
    assert report.entries[0].env_name == "env0"


def test_as_dict_keys():
    e = DensityEntry(env_name="dev", present=3, total=4)
    d = e.as_dict()
    assert set(d.keys()) == {"env", "present", "total", "density_rate", "is_dense"}
    assert d["density_rate"] == pytest.approx(0.75, abs=1e-4)


def test_report_as_dict():
    r = _result(matching={"X": "1"})
    report = density_results([r], names=["env"])
    d = report.as_dict()
    assert "entries" in d
    assert isinstance(d["entries"], list)


def test_zero_total_returns_rate_one():
    e = DensityEntry(env_name="empty", present=0, total=0)
    assert e.density_rate() == 1.0
