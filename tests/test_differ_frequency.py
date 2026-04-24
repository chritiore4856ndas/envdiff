"""Tests for differ_frequency module."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_frequency import FrequencyEntry, FrequencyReport, frequency_diff


def _result(
    only_in_a=(), only_in_b=(), mismatched=(), matching=()
) -> DiffResult:
    return DiffResult(
        only_in_a=dict.fromkeys(only_in_a),
        only_in_b=dict.fromkeys(only_in_b),
        mismatched={k: ("x", "y") for k in mismatched},
        matching=dict.fromkeys(matching),
    )


def test_empty_results_gives_empty_report():
    report = frequency_diff([])
    assert report.entries == []


def test_single_result_missing_key_counted():
    r = _result(only_in_a=["FOO"])
    report = frequency_diff([r])
    assert len(report.entries) == 1
    assert report.entries[0].key == "FOO"
    assert report.entries[0].appearances == 1
    assert report.entries[0].total == 1


def test_key_in_all_results_has_rate_one():
    r1 = _result(only_in_a=["KEY"])
    r2 = _result(mismatched=["KEY"])
    report = frequency_diff([r1, r2])
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.frequency_rate == 1.0


def test_key_in_half_results_has_half_rate():
    r1 = _result(only_in_a=["KEY"])
    r2 = _result(only_in_b=["OTHER"])
    report = frequency_diff([r1, r2])
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.frequency_rate == 0.5


def test_entries_sorted_descending_by_appearances():
    r1 = _result(only_in_a=["A", "B"])
    r2 = _result(only_in_a=["A"])
    report = frequency_diff([r1, r2])
    rates = [e.appearances for e in report.entries]
    assert rates == sorted(rates, reverse=True)


def test_common_threshold_filters_correctly():
    r1 = _result(only_in_a=["COMMON"])
    r2 = _result(only_in_a=["COMMON"])
    r3 = _result(only_in_a=["RARE"])
    report = frequency_diff([r1, r2, r3])
    common = report.common(threshold=0.6)
    assert any(e.key == "COMMON" for e in common)
    assert not any(e.key == "RARE" for e in common)


def test_rare_threshold_filters_correctly():
    r1 = _result(only_in_a=["COMMON"])
    r2 = _result(only_in_a=["COMMON"])
    r3 = _result(only_in_a=["RARE"])
    report = frequency_diff([r1, r2, r3])
    rare = report.rare(threshold=0.6)
    assert any(e.key == "RARE" for e in rare)
    assert not any(e.key == "COMMON" for e in rare)


def test_as_dict_contains_expected_keys():
    r = _result(only_in_a=["X"])
    report = frequency_diff([r])
    d = report.as_dict()
    assert "entries" in d
    entry_dict = d["entries"][0]
    assert set(entry_dict.keys()) == {"key", "appearances", "total", "frequency_rate"}


def test_frequency_rate_zero_when_no_total():
    entry = FrequencyEntry(key="K", appearances=0, total=0)
    assert entry.frequency_rate == 0.0
