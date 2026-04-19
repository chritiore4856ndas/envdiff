import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_graph import build_graph, GraphReport


def _result(only_a=(), only_b=(), mismatched=None) -> DiffResult:
    return DiffResult(
        only_in_a=list(only_a),
        only_in_b=list(only_b),
        mismatched=dict(mismatched or {}),
        matching=[],
    )


def test_empty_results_gives_empty_report():
    report = build_graph([])
    assert report.nodes == []
    assert report.edges == []


def test_single_result_missing_key_creates_node():
    r = _result(only_a=["DB_HOST"])
    report = build_graph([r])
    assert len(report.nodes) == 1
    assert report.nodes[0].key == "DB_HOST"
    assert report.nodes[0].frequency == 1


def test_key_in_multiple_results_has_higher_frequency():
    r1 = _result(only_a=["DB_HOST"])
    r2 = _result(mismatched={"DB_HOST": ("a", "b")})
    report = build_graph([r1, r2])
    node = report.nodes[0]
    assert node.key == "DB_HOST"
    assert node.frequency == 2


def test_two_keys_in_same_result_create_edge():
    r = _result(only_a=["KEY_A", "KEY_B"])
    report = build_graph([r])
    assert len(report.edges) == 1
    edge = report.edges[0]
    assert {edge.key_a, edge.key_b} == {"KEY_A", "KEY_B"}
    assert edge.co_occurrences == 1


def test_edge_co_occurrence_increments_across_results():
    r1 = _result(only_a=["KEY_A", "KEY_B"])
    r2 = _result(mismatched={"KEY_A": ("x", "y"), "KEY_B": ("1", "2")})
    report = build_graph([r1, r2])
    assert report.edges[0].co_occurrences == 2


def test_no_edge_for_single_key_per_result():
    r = _result(only_a=["SOLO"])
    report = build_graph([r])
    assert report.edges == []


def test_statuses_recorded_correctly():
    r = _result(only_a=["A"], only_b=["B"], mismatched={"C": ("x", "y")})
    report = build_graph([r])
    by_key = {n.key: n for n in report.nodes}
    assert "missing_in_b" in by_key["A"].statuses
    assert "missing_in_a" in by_key["B"].statuses
    assert "mismatched" in by_key["C"].statuses


def test_as_dict_returns_serialisable_structure():
    r = _result(only_a=["X", "Y"])
    report = build_graph([r])
    d = report.as_dict()
    assert "nodes" in d
    assert "edges" in d
    assert isinstance(d["nodes"][0]["key"], str)
