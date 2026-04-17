"""Tests for envdiff.differ_patch."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_patch import PatchLine, PatchReport, build_patch


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(only_in_a={}, only_in_b={}, mismatched={})


@pytest.fixture()
def rich_result() -> DiffResult:
    return DiffResult(
        only_in_a={"ALPHA": "1", "BETA": None},
        only_in_b={"GAMMA": "3"},
        mismatched={"DELTA": ("old", "new")},
    )


def test_empty_result_gives_empty_patch(empty_result):
    report = build_patch(empty_result)
    assert report.is_empty()


def test_patch_b_includes_missing_in_b_keys(rich_result):
    report = build_patch(rich_result, target="b")
    keys = [l.key for l in report.lines]
    assert "ALPHA" in keys
    assert "BETA" in keys


def test_patch_b_excludes_only_in_b_keys(rich_result):
    report = build_patch(rich_result, target="b")
    keys = [l.key for l in report.lines]
    assert "GAMMA" not in keys


def test_patch_b_includes_mismatch_with_a_value(rich_result):
    report = build_patch(rich_result, target="b")
    delta = next(l for l in report.lines if l.key == "DELTA")
    assert delta.value == "old"
    assert delta.reason == "mismatch"


def test_patch_a_includes_missing_in_a_keys(rich_result):
    report = build_patch(rich_result, target="a")
    keys = [l.key for l in report.lines]
    assert "GAMMA" in keys


def test_patch_a_mismatch_uses_b_value(rich_result):
    report = build_patch(rich_result, target="a")
    delta = next(l for l in report.lines if l.key == "DELTA")
    assert delta.value == "new"


def test_none_value_renders_empty_in_env_line(rich_result):
    report = build_patch(rich_result, target="b")
    beta = next(l for l in report.lines if l.key == "BETA")
    assert beta.as_env_line() == "BETA="


def test_as_env_lines_returns_list_of_strings(rich_result):
    report = build_patch(rich_result, target="b")
    env_lines = report.as_env_lines()
    assert all(isinstance(s, str) for s in env_lines)
    assert any("=" in s for s in env_lines)


def test_for_reason_filters_correctly(rich_result):
    report = build_patch(rich_result, target="b")
    missing = report.for_reason("missing_in_b")
    assert all(l.reason == "missing_in_b" for l in missing)


def test_as_dict_has_patch_key(rich_result):
    report = build_patch(rich_result, target="b")
    d = report.as_dict()
    assert "patch" in d
    assert isinstance(d["patch"], list)
