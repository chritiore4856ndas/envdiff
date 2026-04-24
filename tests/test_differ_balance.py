import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_balance import BalanceEntry, BalanceReport, balance_results


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
    report = balance_results([])
    assert report.entries == []


def test_single_clean_result_is_balanced():
    report = balance_results([("prod", _result())])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.is_balanced
    assert entry.balance_score == 1.0


def test_missing_key_reduces_balance():
    r = _result(only_in_a=["MISSING_KEY"])
    report = balance_results([("staging", r)])
    entry = report.entries[0]
    assert not entry.is_balanced
    assert entry.balance_score < 1.0


def test_extra_key_reduces_balance():
    r = _result(only_in_b=["EXTRA_KEY"])
    report = balance_results([("dev", r)])
    entry = report.entries[0]
    assert not entry.is_balanced
    assert entry.balance_score < 1.0


def test_mismatch_reduces_balance():
    r = _result(mismatched={"PORT": ("8080", "9090")})
    report = balance_results([("test", r)])
    entry = report.entries[0]
    assert not entry.is_balanced


def test_multiple_entries_tracked():
    r1 = _result()
    r2 = _result(only_in_a=["KEY_A"], only_in_b=["KEY_B"])
    report = balance_results([("prod", r1), ("staging", r2)])
    assert len(report.entries) == 2


def test_unbalanced_filters_correctly():
    r1 = _result()
    r2 = _result(only_in_a=["X"])
    report = balance_results([("prod", r1), ("staging", r2)])
    unbalanced = report.unbalanced()
    assert len(unbalanced) == 1
    assert unbalanced[0].env_name == "staging"


def test_as_dict_contains_expected_keys():
    r = _result(only_in_a=["A"], mismatched={"B": ("1", "2")})
    report = balance_results([("qa", r)])
    d = report.as_dict()
    assert "entries" in d
    entry_dict = d["entries"][0]
    for key in ("env_name", "total_keys", "missing_keys", "extra_keys", "mismatch_keys", "balance_score", "is_balanced"):
        assert key in entry_dict


def test_balance_score_clamped_to_zero():
    # More issues than total_keys shouldn't produce negative score
    r = _result(only_in_a=["A", "B"], only_in_b=["C", "D"], mismatched={"E": ("1", "2")})
    report = balance_results([("env", r)])
    assert report.entries[0].balance_score >= 0.0
