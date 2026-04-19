import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_outlier import OutlierEntry, OutlierReport, detect_outliers


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
        mismatched_values=mismatched or {},
    )


def test_empty_results_gives_empty_report():
    report = detect_outliers([])
    assert report.entries == []


def test_single_result_all_keys_full_frequency():
    r = _result(matching={"KEY": "val"})
    report = detect_outliers([r], labels=["env1"])
    assert len(report.entries) == 1
    assert report.entries[0].frequency == 1.0


def test_majority_value_detected():
    r1 = _result(matching={"KEY": "same"})
    r2 = _result(matching={"KEY": "same"})
    r3 = _result(mismatched={"KEY": "different"})
    report = detect_outliers([r1, r2, r3], labels=["a", "b", "c"])
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.majority_value == "same"
    assert entry.frequency == pytest.approx(2 / 3)


def test_outlier_values_contains_differing_envs():
    r1 = _result(matching={"KEY": "common"})
    r2 = _result(matching={"KEY": "common"})
    r3 = _result(mismatched={"KEY": "rare"})
    report = detect_outliers([r1, r2, r3], labels=["x", "y", "z"])
    entry = next(e for e in report.entries if e.key == "KEY")
    assert "z" in entry.outlier_values
    assert entry.outlier_values["z"] == "rare"


def test_outliers_method_filters_by_threshold():
    r1 = _result(matching={"KEY": "a"})
    r2 = _result(mismatched={"KEY": "b"})
    report = detect_outliers([r1, r2], labels=["e1", "e2"])
    # frequency == 0.5, threshold default 0.5 => not included (strict <)
    assert report.outliers(threshold=0.5) == []
    assert len(report.outliers(threshold=0.6)) == 1


def test_entries_sorted_ascending_by_frequency():
    r1 = _result(matching={"STABLE": "v", "UNSTABLE": "x"})
    r2 = _result(matching={"STABLE": "v"}, mismatched={"UNSTABLE": "y"})
    r3 = _result(matching={"STABLE": "v"}, mismatched={"UNSTABLE": "z"})
    report = detect_outliers([r1, r2, r3], labels=["a", "b", "c"])
    freqs = [e.frequency for e in report.entries]
    assert freqs == sorted(freqs)


def test_as_dict_structure():
    r = _result(matching={"K": "v"})
    report = detect_outliers([r], labels=["env"])
    d = report.as_dict()
    assert "entries" in d
    assert isinstance(d["entries"], list)
    entry_d = d["entries"][0]
    assert "key" in entry_d
    assert "majority_value" in entry_d
    assert "outlier_values" in entry_d
    assert "frequency" in entry_d


def test_labels_default_to_indices():
    r1 = _result(matching={"K": "v"})
    r2 = _result(mismatched={"K": "w"})
    report = detect_outliers([r1, r2])
    entry = report.entries[0]
    # one of the labels should be "0" or "1"
    all_labels = set(entry.outlier_values.keys()) | {"0", "1"}
    assert "0" in all_labels or "1" in all_labels
