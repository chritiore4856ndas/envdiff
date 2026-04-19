"""Tests for differ_correlation."""
import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_correlation import correlate_results, CorrelationReport, CorrelationPair


def _result(only_a=(), only_b=(), mismatched=(), matching=()) -> DiffResult:
    return DiffResult(
        only_in_a=list(only_a),
        only_in_b=list(only_b),
        mismatched={k: ("x", "y") for k in mismatched},
        matching=list(matching),
    )


def test_empty_results_gives_empty_report():
    report = correlate_results([])
    assert report.pairs == []
    assert report.total_snapshots == 0


def test_single_result_single_key_no_pairs():
    report = correlate_results([_result(only_a=["KEY_A"])])
    assert report.pairs == []


def test_two_keys_always_co_change_full_correlation():
    results = [
        _result(only_a=["A", "B"]),
        _result(only_a=["A", "B"]),
    ]
    report = correlate_results(results)
    assert len(report.pairs) == 1
    pair = report.pairs[0]
    assert pair.key_a == "A"
    assert pair.key_b == "B"
    assert pair.co_changes == 2
    assert pair.correlation_ratio == 1.0


def test_keys_never_co_change_zero_correlation():
    results = [
        _result(only_a=["A"]),
        _result(only_a=["B"]),
    ]
    report = correlate_results(results)
    assert report.pairs == []


def test_partial_co_change_ratio():
    results = [
        _result(only_a=["A", "B"]),
        _result(only_a=["A"]),
        _result(only_a=["A", "B"]),
        _result(only_a=["A"]),
    ]
    report = correlate_results(results)
    assert len(report.pairs) == 1
    pair = report.pairs[0]
    assert pair.co_changes == 2
    assert pair.total_snapshots == 4
    assert pair.correlation_ratio == 0.5


def test_mismatched_keys_counted_as_changed():
    results = [_result(mismatched=["X", "Y"])]
    report = correlate_results(results)
    assert len(report.pairs) == 1
    assert report.pairs[0].key_a == "X"
    assert report.pairs[0].key_b == "Y"


def test_strongest_returns_top_n():
    results = [
        _result(only_a=["A", "B", "C"]),
        _result(only_a=["A", "B"]),
    ]
    report = correlate_results(results)
    top = report.strongest(n=1)
    assert len(top) == 1
    assert top[0].correlation_ratio == pytest.approx(1.0)


def test_as_dict_structure():
    results = [_result(only_a=["A", "B"])]
    report = correlate_results(results)
    d = report.as_dict()
    assert "total_snapshots" in d
    assert "pairs" in d
    assert d["pairs"][0]["correlation_ratio"] == 1.0
