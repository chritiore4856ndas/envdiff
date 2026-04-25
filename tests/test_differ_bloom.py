import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_bloom import bloom_diff, BloomReport, BloomEntry


def _result(
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
    matching=None,
) -> DiffResult:
    return DiffResult(
        only_in_a=only_in_a or [],
        only_in_b=only_in_b or [],
        mismatched=mismatched or {},
        matching=matching or [],
    )


def test_empty_results_gives_empty_report():
    report = bloom_diff([])
    assert report.entries == []
    assert report.total_snapshots == 0


def test_single_result_all_keys_have_frequency_one():
    r = _result(only_in_a=["A"], only_in_b=["B"], matching=["C"])
    report = bloom_diff([r])
    freqs = {e.key: e.frequency for e in report.entries}
    assert freqs["A"] == 1.0
    assert freqs["B"] == 1.0
    assert freqs["C"] == 1.0


def test_key_in_half_snapshots_has_half_frequency():
    r1 = _result(only_in_a=["X"])
    r2 = _result(matching=["Y"])
    report = bloom_diff([r1, r2])
    freqs = {e.key: e.frequency for e in report.entries}
    assert freqs["X"] == 0.5
    assert freqs["Y"] == 0.5


def test_total_snapshots_matches_input_length():
    results = [_result(matching=["K"]) for _ in range(5)]
    report = bloom_diff(results)
    assert report.total_snapshots == 5


def test_entries_sorted_descending_by_count():
    r1 = _result(matching=["common"])
    r2 = _result(matching=["common"], only_in_a=["rare"])
    report = bloom_diff([r1, r2])
    keys = [e.key for e in report.entries]
    assert keys[0] == "common"
    assert keys[1] == "rare"


def test_rare_filters_below_threshold():
    r1 = _result(matching=["always"])
    r2 = _result(matching=["always"], only_in_a=["sometimes"])
    r3 = _result(matching=["always"])
    report = bloom_diff([r1, r2, r3])
    rare = report.rare(threshold=0.5)
    rare_keys = {e.key for e in rare}
    assert "sometimes" in rare_keys
    assert "always" not in rare_keys


def test_common_filters_above_threshold():
    r1 = _result(matching=["always"])
    r2 = _result(matching=["always"], only_in_b=["once"])
    r3 = _result(matching=["always"])
    report = bloom_diff([r1, r2, r3])
    common = report.common(threshold=0.9)
    assert any(e.key == "always" for e in common)
    assert all(e.key != "once" for e in common)


def test_as_dict_structure():
    r = _result(matching=["K"])
    report = bloom_diff([r])
    d = report.as_dict()
    assert "total_snapshots" in d
    assert "entries" in d
    assert d["entries"][0]["key"] == "K"
    assert "frequency" in d["entries"][0]


def test_mismatched_keys_are_included_in_entries():
    """Keys that appear in mismatched should also be tracked by bloom_diff."""
    r1 = _result(mismatched={"PORT": ("8080", "9090")})
    r2 = _result(mismatched={"PORT": ("8080", "9090")})
    r3 = _result(matching=["PORT"])
    report = bloom_diff([r1, r2, r3])
    freqs = {e.key: e.frequency for e in report.entries}
    assert "PORT" in freqs
    assert freqs["PORT"] == 1.0
