"""Tests for envdiff.differ_momentum."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_momentum import MomentumEntry, MomentumReport, momentum_diff


def _result(
    only_in_a=(),
    only_in_b=(),
    mismatched=(),
    matching=(),
) -> DiffResult:
    return DiffResult(
        only_in_a=dict.fromkeys(only_in_a),
        only_in_b=dict.fromkeys(only_in_b),
        mismatched={k: ("x", "y") for k in mismatched},
        matching=dict.fromkeys(matching),
    )


def test_empty_results_gives_empty_report():
    report = momentum_diff([])
    assert isinstance(report, MomentumReport)
    assert report.entries == []


def test_single_result_gives_empty_report():
    """Need at least two results to form windows."""
    r = _result(only_in_a=["KEY"])
    report = momentum_diff([r])
    assert report.entries == []


def test_no_differing_keys_gives_empty_report():
    r1 = _result(matching=["A", "B"])
    r2 = _result(matching=["A", "B"])
    report = momentum_diff([r1, r2])
    assert report.entries == []


def test_constant_change_rate_zero_acceleration():
    """Key changes in every result → equal counts per window → accel ≈ 0."""
    r = _result(only_in_a=["KEY"])
    results = [r, r, r, r]
    report = momentum_diff(results, window=2)
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.acceleration == pytest.approx(0.0, abs=1e-9)


def test_increasing_change_rate_positive_acceleration():
    """Key goes from 0 changes in window-1 to 2 in window-2 → positive accel."""
    clean = _result(matching=["KEY"])
    dirty = _result(only_in_a=["KEY"])
    # window=2: window0=[clean,clean] → 0 changes, window1=[dirty,dirty] → 2
    results = [clean, clean, dirty, dirty]
    report = momentum_diff(results, window=2)
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.acceleration > 0
    assert entry in report.accelerating()


def test_decreasing_change_rate_negative_acceleration():
    """Key goes from 2 changes in window-1 to 0 in window-2 → negative accel."""
    clean = _result(matching=["KEY"])
    dirty = _result(only_in_a=["KEY"])
    results = [dirty, dirty, clean, clean]
    report = momentum_diff(results, window=2)
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.acceleration < 0
    assert entry in report.decelerating()


def test_entries_sorted_by_key():
    r = _result(only_in_a=["ZEBRA", "ALPHA"])
    results = [r, r, r, r]
    report = momentum_diff(results, window=2)
    keys = [e.key for e in report.entries]
    assert keys == sorted(keys)


def test_as_dict_structure():
    r = _result(only_in_a=["K"])
    results = [r, r, r, r]
    report = momentum_diff(results, window=2)
    d = report.as_dict()
    assert "entries" in d
    assert "accelerating" in d
    assert "decelerating" in d
    assert isinstance(d["entries"], list)


def test_entry_as_dict_has_required_fields():
    r = _result(only_in_a=["K"])
    results = [r, r, r, r]
    report = momentum_diff(results, window=2)
    ed = report.entries[0].as_dict()
    assert "key" in ed
    assert "change_counts" in ed
    assert "acceleration" in ed
