"""Tests for envdiff.differ_pivot."""
import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_pivot import pivot_results, PivotReport, PivotRow


def _make(only_a=(), only_b=None, mismatched=None, matching=None):
    return DiffResult(
        only_in_a=dict.fromkeys(only_a, None),
        only_in_b=only_b or {},
        mismatched=mismatched or {},
        matching=matching or {},
    )


def test_empty_results_gives_empty_report():
    report = pivot_results({})
    assert isinstance(report, PivotReport)
    assert report.rows == []
    assert report.env_names == []


def test_single_env_matching_key():
    dr = _make(matching={"FOO": "bar"})
    report = pivot_results({"staging": dr})
    assert report.env_names == ["staging"]
    assert len(report.rows) == 1
    row = report.rows[0]
    assert row.key == "FOO"
    assert row.statuses["staging"] == "match"
    assert row.values["staging"] == "bar"


def test_missing_key_shows_missing_status():
    dr = _make(only_a=["SECRET"])
    report = pivot_results({"prod": dr})
    row = report.rows[0]
    assert row.statuses["prod"] == "missing"
    assert row.values["prod"] is None


def test_only_in_b_shows_only_here_status():
    dr = _make(only_b={"NEW_KEY": "value"})
    report = pivot_results({"dev": dr})
    row = report.rows[0]
    assert row.statuses["dev"] == "only_here"
    assert row.values["dev"] == "value"


def test_mismatched_key_shows_mismatch_status():
    dr = _make(mismatched={"PORT": ("8080", "9090")})
    report = pivot_results({"staging": dr})
    row = report.rows[0]
    assert row.statuses["staging"] == "mismatch"
    assert row.values["staging"] == "9090"


def test_multiple_envs_all_keys_present():
    dr_a = _make(matching={"A": "1"}, only_a=["B"])
    dr_b = _make(matching={"A": "1"}, only_b={"C": "3"})
    report = pivot_results({"env1": dr_a, "env2": dr_b})
    keys = [r.key for r in report.rows]
    assert "A" in keys
    assert "B" in keys
    assert "C" in keys


def test_rows_sorted_alphabetically():
    dr = _make(matching={"ZEBRA": "z", "APPLE": "a", "MANGO": "m"})
    report = pivot_results({"e": dr})
    keys = [r.key for r in report.rows]
    assert keys == sorted(keys)


def test_as_dict_structure():
    dr = _make(matching={"X": "1"})
    report = pivot_results({"env": dr})
    d = report.as_dict()
    assert "envs" in d
    assert "rows" in d
    assert d["rows"][0]["key"] == "X"
    assert "values" in d["rows"][0]
    assert "statuses" in d["rows"][0]
