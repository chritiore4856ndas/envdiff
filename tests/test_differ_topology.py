"""Tests for envdiff.differ_topology."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_topology import TopologyEntry, TopologyReport, topology_diff


def _result(
    matching=None,
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        matching=matching or [],
        only_in_a=only_in_a or [],
        only_in_b=only_in_b or [],
        mismatched=mismatched or [],
    )


def test_empty_results_gives_empty_report():
    report = topology_diff({})
    assert report.entries == []
    assert report.universal_keys == []
    assert report.fragmented_keys == []
    assert report.most_absent is None


def test_single_result_matching_key_is_universal():
    results = {"prod": _result(matching=["KEY"])}
    report = topology_diff(results)
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.key == "KEY"
    assert entry.is_universal is True
    assert entry.presence_rate == 1.0


def test_single_result_missing_key_still_present_in_one():
    results = {"prod": _result(only_in_a=["MISSING"])}
    report = topology_diff(results)
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert "prod" in entry.present_in
    assert entry.absent_in == []


def test_key_absent_in_one_env_is_fragmented():
    r_prod = _result(matching=["KEY"])
    r_staging = _result(only_in_b=["OTHER"])
    report = topology_diff({"prod": r_prod, "staging": r_staging})
    key_entry = next(e for e in report.entries if e.key == "KEY")
    assert "prod" in key_entry.present_in
    assert "staging" in key_entry.absent_in
    assert key_entry.is_universal is False
    assert key_entry in report.fragmented_keys


def test_universal_key_appears_in_all_envs():
    r1 = _result(matching=["SHARED"])
    r2 = _result(matching=["SHARED"])
    report = topology_diff({"a": r1, "b": r2})
    entry = next(e for e in report.entries if e.key == "SHARED")
    assert entry.is_universal is True
    assert entry in report.universal_keys


def test_most_absent_returns_lowest_presence_rate():
    r1 = _result(matching=["COMMON", "RARE"])
    r2 = _result(matching=["COMMON"])
    r3 = _result(matching=["COMMON"])
    report = topology_diff({"a": r1, "b": r2, "c": r3})
    assert report.most_absent is not None
    assert report.most_absent.key == "RARE"


def test_as_dict_contains_expected_keys():
    report = topology_diff({"env": _result(matching=["X"])})
    d = report.as_dict()
    assert "entries" in d
    assert "universal_count" in d
    assert "fragmented_count" in d


def test_entry_as_dict_structure():
    entry = TopologyEntry(key="FOO", present_in=["a", "b"], absent_in=["c"])
    d = entry.as_dict()
    assert d["key"] == "FOO"
    assert d["present_in"] == ["a", "b"]
    assert d["absent_in"] == ["c"]
    assert 0.0 <= d["presence_rate"] <= 1.0
    assert isinstance(d["is_universal"], bool)


def test_presence_rate_zero_when_fully_absent():
    entry = TopologyEntry(key="GONE", present_in=[], absent_in=["a", "b"])
    assert entry.presence_rate == 0.0
