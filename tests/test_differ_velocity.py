import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_velocity import VelocityEntry, VelocityReport, velocity_results


def _result(only_a=(), only_b=(), mismatched=()) -> DiffResult:
    return DiffResult(
        only_in_a=list(only_a),
        only_in_b=list(only_b),
        mismatched={k: ("x", "y") for k in mismatched},
    )


def test_empty_results_gives_empty_report():
    report = velocity_results([])
    assert report.entries == []


def test_single_result_missing_key_counted():
    report = velocity_results([_result(only_a=["FOO"])])
    assert len(report.entries) == 1
    assert report.entries[0].key == "FOO"
    assert report.entries[0].change_count == 1


def test_key_in_all_results_has_rate_one():
    results = [_result(only_a=["KEY"]) for _ in range(4)]
    report = velocity_results(results)
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.rate == 1.0


def test_key_in_half_results_has_half_rate():
    results = [_result(only_a=["KEY"]), _result(), _result(only_a=["KEY"]), _result()]
    report = velocity_results(results)
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.rate == 0.5


def test_mismatched_key_counted():
    report = velocity_results([_result(mismatched=["DB_URL"])])
    entry = report.entries[0]
    assert entry.key == "DB_URL"
    assert entry.change_count == 1


def test_entries_sorted_descending_by_change_count():
    results = [
        _result(only_a=["A", "B"]),
        _result(only_a=["A"]),
    ]
    report = velocity_results(results)
    rates = [e.change_count for e in report.entries]
    assert rates == sorted(rates, reverse=True)


def test_fastest_returns_top_n():
    results = [_result(only_a=["A", "B", "C", "D", "E", "F"])]
    report = velocity_results(results)
    assert len(report.fastest(3)) == 3


def test_as_dict_contains_entries_key():
    report = velocity_results([_result(only_a=["X"])])
    d = report.as_dict()
    assert "entries" in d
    assert d["entries"][0]["key"] == "X"


def test_velocity_entry_repr():
    e = VelocityEntry(key="FOO", change_count=2, total_snapshots=4)
    assert "FOO" in repr(e)
    assert "0.50" in repr(e)
