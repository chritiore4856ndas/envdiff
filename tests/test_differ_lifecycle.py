import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_lifecycle import LifecycleEntry, LifecycleReport, lifecycle_diff


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
    report = lifecycle_diff([])
    assert report.entries == []


def test_single_result_stable_key():
    r = _result(matching={"KEY": "val"})
    report = lifecycle_diff([r])
    assert len(report.entries) == 1
    assert report.entries[0].key == "KEY"
    assert report.entries[0].stage == "stable"


def test_key_only_in_first_snapshot_is_new():
    r0 = _result(matching={"KEY": "v"})
    r1 = _result(matching={"OTHER": "v"})
    report = lifecycle_diff([r0, r1])
    stages = {e.key: e.stage for e in report.entries}
    # KEY appears in snapshot 0 but not 1 -> removed
    assert stages["KEY"] == "removed"


def test_key_appearing_only_in_last_snapshot_is_new():
    r0 = _result(matching={"OLD": "v"})
    r1 = _result(matching={"OLD": "v", "NEW": "v"})
    report = lifecycle_diff([r0, r1])
    stages = {e.key: e.stage for e in report.entries}
    assert stages["NEW"] == "new"


def test_consistently_problematic_key_is_degrading():
    r0 = _result(mismatched={"BAD": ("a", "b")})
    r1 = _result(mismatched={"BAD": ("a", "c")})
    r2 = _result(mismatched={"BAD": ("a", "d")})
    report = lifecycle_diff([r0, r1, r2])
    stages = {e.key: e.stage for e in report.entries}
    assert stages["BAD"] == "degrading"


def test_key_fixed_in_last_snapshot_is_recovered():
    r0 = _result(mismatched={"FIXED": ("a", "b")})
    r1 = _result(mismatched={"FIXED": ("a", "b")})
    r2 = _result(matching={"FIXED": "a"})
    report = lifecycle_diff([r0, r1, r2])
    stages = {e.key: e.stage for e in report.entries}
    assert stages["FIXED"] == "recovered"


def test_new_keys_helper():
    r0 = _result(matching={"A": "v"})
    r1 = _result(matching={"A": "v", "B": "v"})
    report = lifecycle_diff([r0, r1])
    new = report.new_keys()
    assert any(e.key == "B" for e in new)


def test_removed_keys_helper():
    r0 = _result(matching={"A": "v", "B": "v"})
    r1 = _result(matching={"A": "v"})
    report = lifecycle_diff([r0, r1])
    removed = report.removed_keys()
    assert any(e.key == "B" for e in removed)


def test_as_dict_contains_entries():
    r = _result(matching={"K": "v"})
    report = lifecycle_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert d["entries"][0]["key"] == "K"


def test_issue_count_tracked():
    r0 = _result(mismatched={"X": ("1", "2")})
    r1 = _result(matching={"X": "1"})
    report = lifecycle_diff([r0, r1])
    entry = next(e for e in report.entries if e.key == "X")
    assert entry.issue_count == 1
