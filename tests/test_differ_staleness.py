import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_staleness import staleness_diff, StalenessReport


def _result(matching=None, only_in_a=None, only_in_b=None, mismatched=None):
    return DiffResult(
        matching=matching or {},
        only_in_a=only_in_a or {},
        only_in_b=only_in_b or {},
        mismatched=mismatched or {},
    )


def test_empty_results_gives_empty_report():
    report = staleness_diff([])
    assert report.entries == []


def test_single_result_matching_key_is_stale():
    r = _result(matching={"FOO": "bar"})
    report = staleness_diff([r])
    entry = next(e for e in report.entries if e.key == "FOO")
    assert entry.is_stale is True


def test_key_with_changing_values_is_active():
    r1 = _result(matching={"FOO": "v1"})
    r2 = _result(mismatched={"FOO": ("v1", "v2")})
    report = staleness_diff([r1, r2])
    entry = next(e for e in report.entries if e.key == "FOO")
    assert entry.is_stale is False


def test_key_same_across_all_snapshots_is_stale():
    results = [_result(matching={"DB_HOST": "localhost"}) for _ in range(4)]
    report = staleness_diff(results)
    entry = next(e for e in report.entries if e.key == "DB_HOST")
    assert entry.is_stale is True
    assert entry.snapshots_seen == 4


def test_missing_key_not_stale():
    r1 = _result(only_in_a={"SECRET": "abc"})
    r2 = _result(only_in_b={"SECRET": "abc"})
    report = staleness_diff([r1, r2])
    entry = next((e for e in report.entries if e.key == "SECRET"), None)
    assert entry is not None
    assert entry.is_stale is False


def test_stale_helper_filters_correctly():
    r1 = _result(matching={"STABLE": "x", "CHANGING": "a"})
    r2 = _result(matching={"STABLE": "x"}, mismatched={"CHANGING": ("a", "b")})
    report = staleness_diff([r1, r2])
    stale_keys = {e.key for e in report.stale()}
    active_keys = {e.key for e in report.active()}
    assert "STABLE" in stale_keys
    assert "CHANGING" in active_keys


def test_as_dict_contains_entries():
    r = _result(matching={"X": "1"})
    report = staleness_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert d["entries"][0]["key"] == "X"


def test_repr_shows_status():
    r = _result(matching={"K": "v"})
    report = staleness_diff([r])
    entry = report.entries[0]
    assert "stale" in repr(entry)
