import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_anomaly import detect_anomalies, AnomalyReport, AnomalyEntry


def _result(only_a=(), only_b=(), mismatched=()) -> DiffResult:
    return DiffResult(
        only_in_a=list(only_a),
        only_in_b=list(only_b),
        mismatched={k: ("x", "y") for k in mismatched},
    )


def test_empty_results_gives_empty_report():
    report = detect_anomalies([])
    assert report.entries == []
    assert report.anomalies() == []


def test_single_result_key_has_frequency_one():
    report = detect_anomalies([_result(only_a=["FOO"])], threshold=0.5)
    assert len(report.entries) == 1
    assert report.entries[0].key == "FOO"
    assert report.entries[0].frequency == 1.0


def test_key_in_all_results_not_anomalous():
    results = [_result(only_a=["FOO"]) for _ in range(5)]
    report = detect_anomalies(results, threshold=0.2)
    assert all(e.key != "FOO" or e.frequency == 1.0 for e in report.entries)
    anomaly_keys = {e.key for e in report.anomalies()}
    assert "FOO" not in anomaly_keys


def test_rare_key_is_anomalous():
    results = [_result(only_a=["RARE"])] + [_result(only_a=["COMMON"]) for _ in range(9)]
    report = detect_anomalies(results, threshold=0.2)
    anomaly_keys = {e.key for e in report.anomalies()}
    assert "RARE" in anomaly_keys
    assert "COMMON" not in anomaly_keys


def test_mismatched_keys_counted():
    results = [_result(mismatched=["DB_URL"]), _result(mismatched=["DB_URL"])]
    report = detect_anomalies(results, threshold=0.5)
    entry = next(e for e in report.entries if e.key == "DB_URL")
    assert entry.occurrences == 2
    assert entry.frequency == 1.0


def test_entries_sorted_by_occurrences_ascending():
    results = [
        _result(only_a=["A", "B"]),
        _result(only_a=["B"]),
    ]
    report = detect_anomalies(results, threshold=1.0)
    keys = [e.key for e in report.entries]
    assert keys.index("A") < keys.index("B")


def test_as_dict_contains_expected_keys():
    report = detect_anomalies([_result(only_a=["X"])], threshold=0.3)
    d = report.as_dict()
    assert "threshold" in d
    assert "entries" in d
    assert "anomalies" in d


def test_frequency_zero_when_total_is_zero():
    entry = AnomalyEntry(key="K", occurrences=0, total=0)
    assert entry.frequency == 0.0
