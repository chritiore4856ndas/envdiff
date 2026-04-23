"""Tests for envdiff.differ_cohesion."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_cohesion import CohesionEntry, CohesionReport, cohesion_diff


def _result(
    only_a=(),
    only_b=(),
    mismatched=None,
    matching=None,
) -> DiffResult:
    return DiffResult(
        only_in_a=list(only_a),
        only_in_b=list(only_b),
        mismatched=mismatched or {},
        matching=matching or {},
    )


def test_empty_results_gives_empty_report():
    report = cohesion_diff([])
    assert report.entries == []


def test_single_result_matching_key_full_cohesion():
    r = _result(matching={"KEY": "val"})
    report = cohesion_diff([r])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.key == "KEY"
    assert entry.appearances == 1
    assert entry.total == 1
    assert entry.cohesion_ratio == 1.0
    assert entry.is_cohesive is True


def test_key_missing_in_half_snapshots_is_fragile():
    r1 = _result(matching={"KEY": "val"})
    r2 = _result(matching={"OTHER": "x"})  # KEY absent here
    report = cohesion_diff([r1, r2])
    by_key = {e.key: e for e in report.entries}
    assert by_key["KEY"].appearances == 1
    assert by_key["KEY"].total == 2
    assert pytest.approx(by_key["KEY"].cohesion_ratio) == 0.5
    assert by_key["KEY"].is_cohesive is False


def test_key_in_all_snapshots_is_cohesive():
    results = [_result(matching={"STABLE": "v"}) for _ in range(5)]
    report = cohesion_diff(results)
    assert len(report.entries) == 1
    assert report.entries[0].is_cohesive is True
    assert report.entries[0].cohesion_ratio == 1.0


def test_fragile_returns_only_non_cohesive_entries():
    r1 = _result(matching={"COMMON": "v", "RARE": "x"})
    r2 = _result(matching={"COMMON": "v"})
    r3 = _result(matching={"COMMON": "v"})
    r4 = _result(matching={"COMMON": "v"})
    r5 = _result(matching={"COMMON": "v"})
    report = cohesion_diff([r1, r2, r3, r4, r5])
    fragile = report.fragile()
    keys = [e.key for e in fragile]
    assert "RARE" in keys
    assert "COMMON" not in keys


def test_only_in_a_key_counted():
    r = _result(only_a=["MISSING_B"])
    report = cohesion_diff([r])
    assert any(e.key == "MISSING_B" for e in report.entries)


def test_only_in_b_key_counted():
    r = _result(only_b=["EXTRA_B"])
    report = cohesion_diff([r])
    assert any(e.key == "EXTRA_B" for e in report.entries)


def test_as_dict_structure():
    r = _result(matching={"X": "1"})
    report = cohesion_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert isinstance(d["entries"], list)
    entry_dict = d["entries"][0]
    assert "key" in entry_dict
    assert "cohesion_ratio" in entry_dict
    assert "is_cohesive" in entry_dict


def test_entries_sorted_alphabetically():
    r = _result(matching={"ZEBRA": "z", "ALPHA": "a", "MIDDLE": "m"})
    report = cohesion_diff([r])
    keys = [e.key for e in report.entries]
    assert keys == sorted(keys)
