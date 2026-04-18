"""Tests for envdiff.differ_signature."""
import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_signature import SignatureReport, SignatureEntry, signature_results


def _result(
    matching=None,
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        matching=matching or {},
        only_in_a=only_in_a or [],
        only_in_b=only_in_b or [],
        mismatched=mismatched or {},
    )


def test_empty_results_gives_empty_report():
    report = signature_results([])
    assert isinstance(report, SignatureReport)
    assert report.entries == []


def test_matching_key_is_stable():
    r = _result(matching={"PORT": "8080"})
    report = signature_results([r])
    entry = next(e for e in report.entries if e.key == "PORT")
    assert entry.stable is True
    assert entry.value_set == ["8080"]


def test_mismatched_key_is_unstable():
    r = _result(mismatched={"DB": ("postgres", "mysql")})
    report = signature_results([r])
    entry = next(e for e in report.entries if e.key == "DB")
    assert entry.stable is False
    assert "postgres" in entry.value_set
    assert "mysql" in entry.value_set


def test_signature_is_hex_string():
    r = _result(matching={"KEY": "val"})
    report = signature_results([r])
    entry = report.entries[0]
    assert len(entry.signature) == 12
    assert all(c in "0123456789abcdef" for c in entry.signature)


def test_same_value_across_results_is_stable():
    r1 = _result(matching={"X": "1"})
    r2 = _result(matching={"X": "1"})
    report = signature_results([r1, r2])
    entry = next(e for e in report.entries if e.key == "X")
    assert entry.stable is True


def test_different_value_across_results_is_unstable():
    r1 = _result(matching={"X": "1"})
    r2 = _result(matching={"X": "2"})
    report = signature_results([r1, r2])
    entry = next(e for e in report.entries if e.key == "X")
    assert entry.stable is False


def test_stable_and_unstable_counts():
    r = _result(
        matching={"A": "1"},
        mismatched={"B": ("x", "y")},
    )
    report = signature_results([r])
    assert len(report.stable) == 1
    assert len(report.unstable) == 1


def test_as_dict_keys():
    r = _result(matching={"K": "v"})
    d = signature_results([r]).as_dict()
    assert "total" in d
    assert "stable_count" in d
    assert "unstable_count" in d
    assert "entries" in d


def test_entry_as_dict():
    r = _result(matching={"K": "v"})
    report = signature_results([r])
    d = report.entries[0].as_dict()
    assert d["key"] == "K"
    assert d["stable"] is True
