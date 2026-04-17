"""Tests for envdiff.differ_cluster."""
import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_cluster import ClusterEntry, ClusterReport, cluster_diff


def _result(
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
    matching=None,
) -> DiffResult:
    return DiffResult(
        only_in_a=set(only_in_a or []),
        only_in_b=set(only_in_b or []),
        mismatched=dict(mismatched or {}),
        matching=dict(matching or {}),
    )


def test_empty_results_gives_empty_report():
    report = cluster_diff([])
    assert report.clusters == {}


def test_missing_in_b_key_clustered_correctly():
    r = _result(only_in_a=["FOO"])
    report = cluster_diff([r])
    assert "FOO" in report.keys_in("missing_in_b")


def test_missing_in_a_key_clustered_correctly():
    r = _result(only_in_b=["BAR"])
    report = cluster_diff([r])
    assert "BAR" in report.keys_in("missing_in_a")


def test_mismatched_key_clustered_correctly():
    r = _result(mismatched={"KEY": ("v1", "v2")})
    report = cluster_diff([r])
    assert "KEY" in report.keys_in("mismatched")


def test_ok_key_clustered_correctly():
    r = _result(matching={"STABLE": "value"})
    report = cluster_diff([r])
    assert "STABLE" in report.keys_in("ok")


def test_dominant_pattern_wins_across_results():
    # KEY missing in b 3 times, mismatched once → dominant = missing_in_b
    results = [
        _result(only_in_a=["KEY"]),
        _result(only_in_a=["KEY"]),
        _result(only_in_a=["KEY"]),
        _result(mismatched={"KEY": ("a", "b")}),
    ]
    report = cluster_diff(results)
    assert "KEY" in report.keys_in("missing_in_b")


def test_entries_sorted_by_count_descending():
    results = [
        _result(only_in_a=["ALPHA", "BETA"]),
        _result(only_in_a=["ALPHA"]),
    ]
    report = cluster_diff(results)
    entries = report.clusters.get("missing_in_b", [])
    counts = [e.count for e in entries]
    assert counts == sorted(counts, reverse=True)


def test_as_dict_returns_serialisable_structure():
    r = _result(only_in_a=["X"], mismatched={"Y": ("1", "2")})
    report = cluster_diff([r])
    d = report.as_dict()
    assert isinstance(d, dict)
    for pattern, items in d.items():
        assert isinstance(items, list)
        for item in items:
            assert "key" in item and "count" in item


def test_keys_in_unknown_pattern_returns_empty():
    report = ClusterReport()
    assert report.keys_in("nonexistent") == []
