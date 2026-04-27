"""Tests for envdiff.differ_exposure."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_exposure import ExposureEntry, ExposureReport, exposure_diff


def _result(
    matching=None,
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        matching=matching or {},
        only_in_a=only_in_a or {},
        only_in_b=only_in_b or {},
        mismatched=mismatched or {},
    )


def test_empty_results_gives_empty_report():
    report = exposure_diff([])
    assert report.entries == []


def test_empty_results_most_exposed_is_none():
    report = exposure_diff([])
    assert report.most_exposed() is None


def test_single_result_matching_key_has_zero_exposure():
    r = _result(matching={"KEY": "val"})
    report = exposure_diff([r])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.key == "KEY"
    assert entry.exposures == 0
    assert entry.exposure_rate == 0.0


def test_single_result_missing_key_has_full_exposure():
    r = _result(only_in_a={"MISSING": "v"})
    report = exposure_diff([r])
    entry = next(e for e in report.entries if e.key == "MISSING")
    assert entry.exposures == 1
    assert entry.exposure_rate == 1.0


def test_mismatched_key_counted_as_exposure():
    r = _result(mismatched={"PORT": ("8080", "9090")})
    report = exposure_diff([r])
    entry = next(e for e in report.entries if e.key == "PORT")
    assert entry.exposures == 1
    assert entry.exposure_rate == 1.0


def test_key_in_half_results_has_half_exposure_rate():
    r1 = _result(mismatched={"DB": ("a", "b")})
    r2 = _result(matching={"DB": "a"})
    report = exposure_diff([r1, r2])
    entry = next(e for e in report.entries if e.key == "DB")
    assert entry.appearances == 2
    assert entry.exposures == 1
    assert entry.exposure_rate == pytest.approx(0.5)


def test_most_exposed_returns_highest_rate_entry():
    r1 = _result(mismatched={"X": ("1", "2")}, matching={"Y": "val"})
    report = exposure_diff([r1])
    top = report.most_exposed()
    assert top is not None
    assert top.key == "X"


def test_exposed_filters_by_threshold():
    r1 = _result(mismatched={"A": ("1", "2")}, matching={"B": "val"})
    report = exposure_diff([r1])
    exposed = report.exposed(threshold=0.5)
    keys = [e.key for e in exposed]
    assert "A" in keys
    assert "B" not in keys


def test_as_dict_contains_entries_list():
    r = _result(only_in_b={"NEW": "v"})
    report = exposure_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert isinstance(d["entries"], list)
    assert d["entries"][0]["key"] == "NEW"
