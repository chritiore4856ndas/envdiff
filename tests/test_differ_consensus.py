"""Tests for envdiff.differ_consensus."""
import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_consensus import ConsensusEntry, ConsensusReport, consensus_results


def _result(
    matching=None,
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        matching=matching or {},
        only_in_a=only_in_a or {},
        only_in_b=only_in_b or {},
        mismatched=mismatched or {},
    )


def test_empty_results_gives_empty_report():
    report = consensus_results([])
    assert report.entries == []
    assert report.agreed() == []
    assert report.contested() == []


def test_single_result_matching_key_has_full_agreement():
    r = _result(matching={"HOST": "localhost"})
    report = consensus_results([r])
    assert len(report.entries) == 1
    e = report.entries[0]
    assert e.key == "HOST"
    assert e.majority_value == "localhost"
    assert e.agreement_ratio == 1.0
    assert e.has_consensus is True


def test_majority_value_wins():
    r1 = _result(matching={"PORT": "8080"})
    r2 = _result(matching={"PORT": "8080"})
    r3 = _result(matching={"PORT": "9090"})
    report = consensus_results([r1, r2, r3])
    e = report.entries[0]
    assert e.majority_value == "8080"
    assert e.agreement_count == 2
    assert e.total == 3
    assert e.has_consensus is True


def test_even_split_no_consensus():
    r1 = _result(matching={"KEY": "a"})
    r2 = _result(matching={"KEY": "b"})
    report = consensus_results([r1, r2])
    e = report.entries[0]
    assert e.agreement_ratio == 0.5
    assert e.has_consensus is False


def test_missing_key_counts_as_none():
    r1 = _result(matching={"X": "1"})
    r2 = _result(only_in_b={"X": "1"})  # X missing in a side
    report = consensus_results([r1, r2])
    assert any(e.key == "X" for e in report.entries)


def test_contested_and_agreed_split_correctly():
    r1 = _result(matching={"A": "1", "B": "x"})
    r2 = _result(matching={"A": "1", "B": "y"})
    report = consensus_results([r1, r2])
    agreed_keys = {e.key for e in report.agreed()}
    contested_keys = {e.key for e in report.contested()}
    assert "A" in agreed_keys
    assert "B" in contested_keys


def test_as_dict_structure():
    r = _result(matching={"K": "v"})
    report = consensus_results([r])
    d = report.as_dict()
    assert "total_keys" in d
    assert "agreed" in d
    assert "contested" in d
    assert "entries" in d
    assert d["entries"][0]["key"] == "K"


def test_dissenting_values_populated():
    r1 = _result(matching={"ENV": "prod"})
    r2 = _result(matching={"ENV": "prod"})
    r3 = _result(matching={"ENV": "staging"})
    report = consensus_results([r1, r2, r3])
    e = report.entries[0]
    assert "staging" in e.dissenting_values
    assert len(e.dissenting_values) == 1
