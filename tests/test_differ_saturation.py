import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_saturation import (
    SaturationEntry,
    SaturationReport,
    saturation_diff,
)


def _result(
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
    matching=None,
) -> DiffResult:
    return DiffResult(
        only_in_a=only_in_a or [],
        only_in_b=only_in_b or [],
        mismatched=mismatched or [],
        matching=matching or [],
    )


def test_empty_results_gives_empty_report():
    report = saturation_diff([])
    assert report.entries == []


def test_single_result_identical_envs_both_saturated():
    r = _result(matching=["A", "B", "C"])
    report = saturation_diff([r], env_names=["dev", "prod"])
    assert len(report.entries) == 2
    for entry in report.entries:
        assert entry.is_saturated
        assert entry.saturation_rate == 1.0


def test_missing_key_reduces_saturation():
    r = _result(only_in_a=["MISSING_IN_B"], matching=["SHARED"])
    report = saturation_diff([r], env_names=["dev", "prod"])
    dev = next(e for e in report.entries if e.env_name == "dev")
    prod = next(e for e in report.entries if e.env_name == "prod")
    assert dev.saturation_rate == 1.0
    assert prod.saturation_rate < 1.0


def test_total_is_union_of_all_keys():
    r = _result(only_in_a=["X"], only_in_b=["Y"], matching=["Z"])
    report = saturation_diff([r], env_names=["a", "b"])
    for entry in report.entries:
        assert entry.total == 3


def test_least_saturated_ordering():
    r = _result(only_in_a=["K1", "K2"], matching=["K3"])
    report = saturation_diff([r], env_names=["full", "partial"])
    ordered = report.least_saturated()
    assert ordered[0].saturation_rate <= ordered[-1].saturation_rate


def test_as_dict_has_expected_keys():
    r = _result(matching=["A"])
    report = saturation_diff([r], env_names=["x", "y"])
    d = report.as_dict()
    assert "entries" in d
    entry_dict = d["entries"][0]
    assert "env" in entry_dict
    assert "present" in entry_dict
    assert "total" in entry_dict
    assert "saturation_rate" in entry_dict
    assert "is_saturated" in entry_dict


def test_repr_contains_env_name():
    entry = SaturationEntry(env_name="staging", present=3, total=4)
    assert "staging" in repr(entry)


def test_zero_total_returns_rate_one():
    entry = SaturationEntry(env_name="empty", present=0, total=0)
    assert entry.saturation_rate == 1.0
    assert entry.is_saturated
