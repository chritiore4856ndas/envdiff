import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_heatmap import build_heatmap, HeatmapReport


def _result(only_a=None, only_b=None, mismatched=None) -> DiffResult:
    return DiffResult(
        only_in_a=only_a or {},
        only_in_b=only_b or {},
        mismatched=mismatched or {},
    )


def test_empty_results_gives_empty_report():
    report = build_heatmap([])
    assert isinstance(report, HeatmapReport)
    assert report.entries == []


def test_single_result_missing_key_counted():
    r = _result(only_a={"FOO": "bar"})
    report = build_heatmap([r])
    assert report.as_dict() == {"FOO": 1}


def test_key_in_multiple_results_has_higher_count():
    r1 = _result(only_a={"FOO": "bar"})
    r2 = _result(mismatched={"FOO": ("bar", "baz")})
    report = build_heatmap([r1, r2])
    assert report.as_dict()["FOO"] == 2


def test_entries_sorted_descending():
    r1 = _result(only_a={"A": "1"})
    r2 = _result(only_a={"A": "1", "B": "2"})
    r3 = _result(only_a={"A": "1", "B": "2", "C": "3"})
    report = build_heatmap([r1, r2, r3])
    counts = [e.count for e in report.entries]
    assert counts == sorted(counts, reverse=True)


def test_top_returns_limited_entries():
    keys = {f"KEY_{i}": str(i) for i in range(20)}
    r = _result(only_a=keys)
    report = build_heatmap([r])
    assert len(report.top(5)) == 5


def test_top_default_is_ten():
    keys = {f"KEY_{i}": str(i) for i in range(15)}
    r = _result(only_a=keys)
    report = build_heatmap([r])
    assert len(report.top()) == 10


def test_as_dict_returns_mapping():
    r = _result(only_b={"X": "1"}, mismatched={"Y": ("a", "b")})
    report = build_heatmap([r])
    d = report.as_dict()
    assert d["X"] == 1
    assert d["Y"] == 1
