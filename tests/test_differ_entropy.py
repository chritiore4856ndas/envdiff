"""Tests for envdiff.differ_entropy."""
import math
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_entropy import EntropyEntry, EntropyReport, entropy_diff, _shannon


def _result(
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        only_in_a=only_in_a or [],
        only_in_b=only_in_b or [],
        mismatched=mismatched or {},
    )


def test_empty_results_gives_empty_report():
    report = entropy_diff([])
    assert report.entries == []


def test_shannon_uniform_is_zero():
    assert _shannon([5]) == 0.0


def test_shannon_two_equal_is_one_bit():
    assert abs(_shannon([1, 1]) - 1.0) < 1e-9


def test_single_result_mismatched_key_has_nonzero_entropy():
    r = _result(mismatched={"KEY": ("val_a", "val_b")})
    report = entropy_diff([r])
    assert len(report.entries) == 1
    assert report.entries[0].key == "KEY"
    assert report.entries[0].entropy > 0


def test_only_in_a_key_appears_in_report():
    r = _result(only_in_a=["MISSING_KEY"])
    report = entropy_diff([r])
    keys = [e.key for e in report.entries]
    assert "MISSING_KEY" in keys


def test_only_in_b_key_appears_in_report():
    r = _result(only_in_b=["EXTRA_KEY"])
    report = entropy_diff([r])
    keys = [e.key for e in report.entries]
    assert "EXTRA_KEY" in keys


def test_uniform_keys_returns_zero_entropy_entries():
    # same mismatch pair repeated -> two identical values each time -> entropy 0
    r1 = _result(mismatched={"STABLE": ("x", "x")})
    r2 = _result(mismatched={"STABLE": ("x", "x")})
    report = entropy_diff([r1, r2])
    uniform = report.uniform_keys()
    assert any(e.key == "STABLE" for e in uniform)


def test_most_diverse_returns_top_n():
    r = _result(mismatched={"A": ("1", "2"), "B": ("3", "4"), "C": ("5", "6")})
    report = entropy_diff([r])
    top = report.most_diverse(n=2)
    assert len(top) == 2


def test_entries_sorted_descending_by_entropy():
    r1 = _result(mismatched={"VARIES": ("a", "b")})
    r2 = _result(mismatched={"VARIES": ("c", "d")})
    r3 = _result(mismatched={"STABLE": ("x", "x")})
    report = entropy_diff([r1, r2, r3])
    entropies = [e.entropy for e in report.entries]
    assert entropies == sorted(entropies, reverse=True)


def test_as_dict_contains_entries_key():
    report = entropy_diff([])
    d = report.as_dict()
    assert "entries" in d
    assert isinstance(d["entries"], list)


def test_entry_as_dict_has_expected_keys():
    entry = EntropyEntry(key="FOO", unique_values=2, total_seen=4, entropy=1.0)
    d = entry.as_dict()
    assert set(d.keys()) == {"key", "unique_values", "total_seen", "entropy"}
