import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_lineage import build_lineage, LineageReport


def _result(matching=None, only_a=None, only_b=None, mismatched=None):
    return DiffResult(
        matching=matching or {},
        only_in_a=only_a or {},
        only_in_b=only_b or {},
        mismatched=mismatched or {},
    )


def test_empty_results_gives_empty_report():
    report = build_lineage([])
    assert report.entries == {}


def test_single_result_matching_key():
    r = _result(matching={"KEY": "val"})
    report = build_lineage([r])
    assert "KEY" in report.entries
    assert report.entries["KEY"].status_history == ["match"]
    assert report.entries["KEY"].first_seen == 0
    assert report.entries["KEY"].last_seen == 0


def test_key_missing_in_b_gets_correct_status():
    r = _result(only_a={"SECRET": "x"})
    report = build_lineage([r])
    assert report.entries["SECRET"].status_history == ["missing_b"]


def test_key_spans_multiple_results():
    r1 = _result(matching={"FOO": "1"})
    r2 = _result(mismatched={"FOO": ("1", "2")})
    r3 = _result(matching={"FOO": "2"})
    report = build_lineage([r1, r2, r3])
    entry = report.entries["FOO"]
    assert entry.first_seen == 0
    assert entry.last_seen == 2
    assert entry.status_history == ["match", "mismatch", "match"]


def test_ephemeral_returns_short_lived_keys():
    r1 = _result(only_a={"TMP": "v"})
    r2 = _result(matching={"STABLE": "v"})
    r3 = _result(matching={"STABLE": "v"})
    report = build_lineage([r1, r2, r3])
    eph = report.ephemeral(max_lifespan=1)
    keys = [e.key for e in eph]
    assert "TMP" in keys
    assert "STABLE" not in keys


def test_persistent_returns_long_lived_keys():
    r1 = _result(matching={"STABLE": "v"})
    r2 = _result(matching={"STABLE": "v"})
    r3 = _result(only_a={"ONCE": "v"})
    report = build_lineage([r1, r2, r3])
    pers = report.persistent(min_lifespan=2)
    keys = [e.key for e in pers]
    assert "STABLE" in keys
    assert "ONCE" not in keys


def test_as_dict_includes_lifespan():
    r1 = _result(matching={"K": "v"})
    r2 = _result(matching={"K": "v"})
    report = build_lineage([r1, r2])
    d = report.as_dict()
    assert d["K"]["lifespan"] == 2


def test_key_only_in_second_result_has_correct_first_seen():
    r1 = _result(matching={"A": "1"})
    r2 = _result(only_b={"NEW": "x"})
    report = build_lineage([r1, r2])
    assert report.entries["NEW"].first_seen == 1
