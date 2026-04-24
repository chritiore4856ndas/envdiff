import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_affinity import AffinityPair, AffinityReport, affinity_diff, _problematic_keys


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
        matching=matching or {},
    )


def test_empty_results_gives_empty_report():
    report = affinity_diff([])
    assert report.pairs == []
    assert report.total_snapshots == 0


def test_single_result_single_key_no_pairs():
    r = _result(only_in_a=["KEY_A"])
    report = affinity_diff([r])
    assert report.pairs == []
    assert report.total_snapshots == 1


def test_two_keys_always_co_problematic_full_affinity():
    r1 = _result(only_in_a=["KEY_A", "KEY_B"])
    r2 = _result(mismatched={"KEY_A": ("x", "y"), "KEY_B": ("p", "q")})
    report = affinity_diff([r1, r2])
    assert len(report.pairs) == 1
    pair = report.pairs[0]
    assert pair.key_a == "KEY_A"
    assert pair.key_b == "KEY_B"
    assert pair.co_occurrences == 2
    assert pair.affinity_ratio() == 1.0


def test_keys_never_co_problematic_no_pair():
    r1 = _result(only_in_a=["KEY_A"])
    r2 = _result(only_in_b=["KEY_B"])
    report = affinity_diff([r1, r2])
    # KEY_A and KEY_B never appear together in the same snapshot
    assert report.pairs == []


def test_partial_co_occurrence_gives_half_ratio():
    r1 = _result(only_in_a=["KEY_A", "KEY_B"])
    r2 = _result(only_in_a=["KEY_A"])
    report = affinity_diff([r1, r2])
    assert len(report.pairs) == 1
    pair = report.pairs[0]
    assert pair.co_occurrences == 1
    assert pair.total == 2
    assert pair.affinity_ratio() == 0.5


def test_strong_filters_by_threshold():
    r1 = _result(only_in_a=["KEY_A", "KEY_B"])
    r2 = _result(only_in_a=["KEY_A", "KEY_B"])
    r3 = _result(only_in_a=["KEY_A"])
    report = affinity_diff([r1, r2, r3])
    # co_occurrences=2, total=3 => ratio ~0.67, below 0.8
    assert report.strong(threshold=0.8) == []
    assert len(report.strong(threshold=0.6)) == 1


def test_problematic_keys_union():
    r = _result(only_in_a=["A"], only_in_b=["B"], mismatched={"C": ("x", "y")})
    assert _problematic_keys(r) == {"A", "B", "C"}


def test_matching_keys_not_included_in_problematic():
    r = _result(matching={"KEY": "value"})
    assert _problematic_keys(r) == set()


def test_as_dict_structure():
    r1 = _result(only_in_a=["KEY_A", "KEY_B"])
    report = affinity_diff([r1])
    d = report.as_dict()
    assert "total_snapshots" in d
    assert "pairs" in d
    assert d["total_snapshots"] == 1


def test_pair_as_dict_fields():
    pair = AffinityPair(key_a="A", key_b="B", co_occurrences=3, total=5)
    d = pair.as_dict()
    assert d["key_a"] == "A"
    assert d["key_b"] == "B"
    assert d["co_occurrences"] == 3
    assert d["total"] == 5
    assert d["affinity_ratio"] == 0.6


def test_pairs_sorted_descending_by_co_occurrences():
    r1 = _result(only_in_a=["A", "B", "C"])
    r2 = _result(only_in_a=["A", "B", "C"])
    r3 = _result(only_in_a=["A", "C"])
    report = affinity_diff([r1, r2, r3])
    ratios = [p.co_occurrences for p in report.pairs]
    assert ratios == sorted(ratios, reverse=True)
