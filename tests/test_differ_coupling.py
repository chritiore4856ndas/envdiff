import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_coupling import coupling_report, CouplingPair, CouplingReport


def _result(only_a=(), only_b=(), mismatched=None) -> DiffResult:
    return DiffResult(
        only_in_a=set(only_a),
        only_in_b=set(only_b),
        mismatched=mismatched or {},
    )


def test_empty_results_gives_empty_report():
    report = coupling_report([])
    assert report.pairs == []
    assert report.total_snapshots == 0


def test_single_result_no_pairs_for_single_key():
    report = coupling_report([_result(only_a=["KEY_A"])])
    assert report.pairs == []


def test_two_keys_always_together_full_coupling():
    results = [
        _result(only_a=["A", "B"]),
        _result(only_a=["A", "B"]),
    ]
    report = coupling_report(results)
    assert len(report.pairs) == 1
    pair = report.pairs[0]
    assert pair.key_a == "A"
    assert pair.key_b == "B"
    assert pair.co_changes == 2
    assert pair.coupling_ratio() == 1.0


def test_keys_never_together_no_pair():
    results = [
        _result(only_a=["A"]),
        _result(only_a=["B"]),
    ]
    report = coupling_report(results)
    assert all(p.co_changes == 0 or (p.key_a != "A" or p.key_b != "B") for p in report.pairs)
    # A and B never appear together
    ab = [(p.key_a, p.key_b) for p in report.pairs]
    assert ("A", "B") not in ab


def test_partial_coupling_ratio():
    results = [
        _result(only_a=["X", "Y"]),
        _result(only_a=["X"]),
        _result(only_a=["X", "Y"]),
        _result(only_a=["X"]),
    ]
    report = coupling_report(results)
    xy = next((p for p in report.pairs if p.key_a == "X" and p.key_b == "Y"), None)
    assert xy is not None
    assert xy.coupling_ratio() == pytest.approx(0.5)


def test_strong_filters_by_threshold():
    results = [_result(only_a=["A", "B"])] * 5 + [_result(only_a=["A"])] * 5
    report = coupling_report(results)
    strong = report.strong(threshold=0.6)
    assert all(p.coupling_ratio() >= 0.6 for p in strong)


def test_as_dict_structure():
    results = [_result(mismatched={"K1": ("v1", "v2"), "K2": ("a", "b")})]
    report = coupling_report(results)
    d = report.as_dict()
    assert "total_snapshots" in d
    assert "pairs" in d
    assert d["total_snapshots"] == 1


def test_total_snapshots_matches_input():
    results = [_result(only_a=["A", "B"])] * 7
    report = coupling_report(results)
    assert report.total_snapshots == 7
