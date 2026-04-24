import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_resonance import resonance_diff, ResonanceEntry, ResonanceReport


def _result(
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
    matching=None,
) -> DiffResult:
    return DiffResult(
        only_in_a=only_in_a or {},
        only_in_b=only_in_b or {},
        mismatched=mismatched or {},
        matching=matching or {},
    )


def test_empty_results_gives_empty_report():
    report = resonance_diff([])
    assert isinstance(report, ResonanceReport)
    assert report.entries == []


def test_single_result_missing_key_counted():
    r = _result(only_in_a={"FOO": "bar"})
    report = resonance_diff([r])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.key == "FOO"
    assert entry.co_occurrences == 1
    assert entry.total_pairs == 1
    assert entry.resonance_ratio == 1.0


def test_key_in_all_results_has_ratio_one():
    results = [
        _result(only_in_a={"KEY": "v"}),
        _result(only_in_a={"KEY": "v"}),
        _result(mismatched={"KEY": ("a", "b")}),
    ]
    report = resonance_diff(results)
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.co_occurrences == 3
    assert entry.resonance_ratio == 1.0


def test_key_in_half_results_has_half_ratio():
    results = [
        _result(only_in_a={"KEY": "v"}),
        _result(matching={"KEY": "v"}),
    ]
    report = resonance_diff(results)
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.co_occurrences == 1
    assert entry.total_pairs == 2
    assert entry.resonance_ratio == pytest.approx(0.5)


def test_matching_only_key_not_in_report():
    r = _result(matching={"STABLE": "val"})
    report = resonance_diff([r])
    keys = [e.key for e in report.entries]
    assert "STABLE" not in keys


def test_resonant_filters_by_threshold():
    results = [
        _result(only_in_a={"HIGH": "x"}),
        _result(only_in_a={"HIGH": "x"}),
        _result(only_in_a={"LOW": "y"}),
        _result(matching={"LOW": "y"}),
    ]
    report = resonance_diff(results)
    resonant = report.resonant(threshold=0.6)
    keys = [e.key for e in resonant]
    assert "HIGH" in keys
    assert "LOW" not in keys


def test_entries_sorted_descending_by_co_occurrences():
    results = [
        _result(only_in_a={"A": "1", "B": "2"}),
        _result(only_in_a={"A": "1"}),
    ]
    report = resonance_diff(results)
    ratios = [e.co_occurrences for e in report.entries]
    assert ratios == sorted(ratios, reverse=True)


def test_as_dict_contains_expected_keys():
    r = _result(only_in_a={"X": "1"})
    report = resonance_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert d["entries"][0]["key"] == "X"
    assert "resonance_ratio" in d["entries"][0]
