import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_coherence import CoherenceEntry, CoherenceReport, coherence_diff


def _result(
    matching=None,
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        matching=matching or {},
        only_in_a=set(only_in_a or []),
        only_in_b=set(only_in_b or []),
        mismatched=mismatched or {},
    )


def test_empty_results_gives_empty_report():
    report = coherence_diff([])
    assert report.entries == []


def test_empty_results_average_rate_is_one():
    report = coherence_diff([])
    assert report.average_rate() == 1.0


def test_empty_results_most_coherent_is_none():
    report = coherence_diff([])
    assert report.most_coherent() is None


def test_empty_results_least_coherent_is_none():
    report = coherence_diff([])
    assert report.least_coherent() is None


def test_single_result_matching_key_has_full_coherence():
    r = _result(matching={"KEY": "val"})
    report = coherence_diff([r])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.key == "KEY"
    assert entry.appearances == 1
    assert entry.matching == 1
    assert entry.coherence_rate() == 1.0


def test_single_result_missing_key_has_zero_coherence():
    r = _result(only_in_a=["MISSING"])
    report = coherence_diff([r])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.key == "MISSING"
    assert entry.matching == 0
    assert entry.coherence_rate() == 0.0


def test_key_matching_in_half_results_has_half_rate():
    r1 = _result(matching={"KEY": "v"})
    r2 = _result(mismatched={"KEY": ("v", "x")})
    report = coherence_diff([r1, r2])
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.appearances == 2
    assert entry.matching == 1
    assert entry.coherence_rate() == pytest.approx(0.5)


def test_is_coherent_default_threshold():
    e = CoherenceEntry(key="K", appearances=10, matching=9)
    assert e.is_coherent() is True


def test_is_not_coherent_below_threshold():
    e = CoherenceEntry(key="K", appearances=10, matching=5)
    assert e.is_coherent(threshold=0.8) is False


def test_incoherent_filters_entries():
    r1 = _result(matching={"STABLE": "v", "FLAKY": "v"})
    r2 = _result(matching={"STABLE": "v"}, only_in_a=["FLAKY"])
    report = coherence_diff([r1, r2])
    incoherent_keys = {e.key for e in report.incoherent(threshold=0.9)}
    assert "FLAKY" in incoherent_keys
    assert "STABLE" not in incoherent_keys


def test_as_dict_contains_expected_keys():
    r = _result(matching={"A": "1"}, only_in_b=["B"])
    report = coherence_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert "average_rate" in d
    assert "incoherent_count" in d


def test_entry_as_dict_structure():
    e = CoherenceEntry(key="X", appearances=4, matching=3)
    d = e.as_dict()
    assert d["key"] == "X"
    assert d["appearances"] == 4
    assert d["matching"] == 3
    assert "coherence_rate" in d
    assert "is_coherent" in d
