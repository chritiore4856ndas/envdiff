"""Tests for envdiff.differ_uniformity."""
from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_uniformity import UniformityEntry, UniformityReport, uniformity_diff


def _result(
    matching=(),
    only_in_a=(),
    only_in_b=(),
    mismatched=(),
) -> DiffResult:
    return DiffResult(
        matching=set(matching),
        only_in_a=set(only_in_a),
        only_in_b=set(only_in_b),
        mismatched=set(mismatched),
    )


def test_empty_results_gives_empty_report():
    report = uniformity_diff([])
    assert report.entries == []


def test_single_result_matching_key_has_rate_one():
    r = _result(matching=["KEY"])
    report = uniformity_diff([r])
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.uniformity_rate() == 1.0


def test_single_result_missing_key_has_rate_zero():
    r = _result(only_in_a=["MISSING"])
    report = uniformity_diff([r])
    entry = next(e for e in report.entries if e.key == "MISSING")
    assert entry.uniformity_rate() == 0.0


def test_key_in_half_results_has_half_rate():
    r1 = _result(matching=["KEY"])
    r2 = _result(only_in_a=["KEY"])
    report = uniformity_diff([r1, r2])
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.uniformity_rate() == pytest.approx(0.5)


def test_mismatched_key_counts_as_appearance():
    r = _result(mismatched=["KEY"])
    report = uniformity_diff([r])
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.appearances == 1
    assert entry.uniformity_rate() == 1.0


def test_non_uniform_filters_below_threshold():
    r1 = _result(matching=["STABLE"])
    r2 = _result(matching=["STABLE"], only_in_a=["FLAKY"])
    r3 = _result(matching=["STABLE"], only_in_a=["FLAKY"])
    # FLAKY appears 0 times as matching/mismatched out of 3 -> rate 0.0
    report = uniformity_diff([r1, r2, r3], threshold=0.8)
    non_uni = report.non_uniform(threshold=0.8)
    keys = {e.key for e in non_uni}
    assert "FLAKY" in keys
    assert "STABLE" not in keys


def test_is_uniform_default_threshold():
    entry = UniformityEntry(key="K", appearances=9, total=10)
    assert entry.is_uniform()  # 0.9 >= 0.8


def test_is_not_uniform_below_threshold():
    entry = UniformityEntry(key="K", appearances=5, total=10)
    assert not entry.is_uniform()  # 0.5 < 0.8


def test_as_dict_contains_expected_keys():
    entry = UniformityEntry(key="K", appearances=3, total=5)
    d = entry.as_dict()
    assert set(d.keys()) == {"key", "appearances", "total", "uniformity_rate", "is_uniform"}


def test_report_as_dict_entries_list():
    r = _result(matching=["A", "B"])
    report = uniformity_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert isinstance(d["entries"], list)


def test_entries_sorted_by_rate_ascending():
    r1 = _result(matching=["GOOD"])
    r2 = _result(only_in_a=["BAD"])
    report = uniformity_diff([r1, r2])
    rates = [e.uniformity_rate() for e in report.entries]
    assert rates == sorted(rates)
