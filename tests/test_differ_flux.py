"""Tests for envdiff.differ_flux."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_flux import FluxEntry, FluxReport, flux_diff


def _result(
    only_in_a=(),
    only_in_b=(),
    mismatched=None,
    matching=None,
) -> DiffResult:
    return DiffResult(
        only_in_a=list(only_in_a),
        only_in_b=list(only_in_b),
        mismatched=mismatched or {},
        matching=matching or {},
    )


def test_empty_results_gives_empty_report():
    report = flux_diff([])
    assert report.entries == []


def test_empty_results_average_flux_is_zero():
    assert flux_diff([]).average_flux == 0.0


def test_empty_results_most_volatile_is_none():
    assert flux_diff([]).most_volatile is None


def test_single_result_no_transitions():
    r = _result(only_in_a=["KEY"])
    report = flux_diff([r])
    assert len(report.entries) == 1
    assert report.entries[0].change_count == 0
    assert report.entries[0].flux_rate == 0.0


def test_stable_key_has_zero_flux():
    r1 = _result(matching={"KEY": "val"})
    r2 = _result(matching={"KEY": "val"})
    report = flux_diff([r1, r2])
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.change_count == 0
    assert entry.flux_rate == 0.0


def test_key_changing_every_transition_has_rate_one():
    r1 = _result(only_in_a=["KEY"])
    r2 = _result(matching={"KEY": "v"})
    r3 = _result(only_in_a=["KEY"])
    report = flux_diff([r1, r2, r3])
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.change_count == 2
    assert entry.total_transitions == 2
    assert entry.flux_rate == 1.0


def test_high_flux_filters_above_half():
    r1 = _result(only_in_a=["UNSTABLE"])
    r2 = _result(matching={"UNSTABLE": "x"})
    r3 = _result(only_in_a=["UNSTABLE"])
    report = flux_diff([r1, r2, r3])
    assert any(e.key == "UNSTABLE" for e in report.high_flux)


def test_stable_key_not_in_high_flux():
    r1 = _result(matching={"STABLE": "v"})
    r2 = _result(matching={"STABLE": "v"})
    report = flux_diff([r1, r2])
    assert not any(e.key == "STABLE" for e in report.high_flux)


def test_most_volatile_returns_highest_rate_key():
    r1 = _result(only_in_a=["FAST"], matching={"SLOW": "v"})
    r2 = _result(matching={"FAST": "v", "SLOW": "v"})
    r3 = _result(only_in_a=["FAST"], matching={"SLOW": "v"})
    report = flux_diff([r1, r2, r3])
    assert report.most_volatile is not None
    assert report.most_volatile.key == "FAST"


def test_as_dict_contains_expected_keys():
    report = flux_diff([])
    d = report.as_dict()
    assert "entries" in d
    assert "average_flux" in d
    assert "most_volatile" in d


def test_entry_as_dict_shape():
    entry = FluxEntry(key="X", change_count=2, total_transitions=4)
    d = entry.as_dict()
    assert d["key"] == "X"
    assert d["flux_rate"] == 0.5
    assert d["is_flux"] is False
