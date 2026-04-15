"""Tests for envdiff.annotator."""

from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.annotator import annotate, AnnotatedDiff, Annotation


@pytest.fixture()
def rich_result() -> DiffResult:
    return DiffResult(
        only_in_a={"ONLY_A"},
        only_in_b={"ONLY_B"},
        mismatched={"SHARED"},
        values_a={"ONLY_A": "foo", "SHARED": "old"},
        values_b={"ONLY_B": "bar", "SHARED": "new"},
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(
        only_in_a=set(),
        only_in_b=set(),
        mismatched=set(),
        values_a={},
        values_b={},
    )


def test_empty_result_gives_empty_annotated_diff(empty_result):
    annotated = annotate(empty_result)
    assert isinstance(annotated, AnnotatedDiff)
    assert annotated.annotations == {}


def test_only_in_a_has_missing_in_b_status(rich_result):
    annotated = annotate(rich_result)
    ann = annotated.annotations["ONLY_A"]
    assert ann.status == "missing_in_b"
    assert ann.value_a == "foo"
    assert ann.value_b is None


def test_only_in_b_has_missing_in_a_status(rich_result):
    annotated = annotate(rich_result)
    ann = annotated.annotations["ONLY_B"]
    assert ann.status == "missing_in_a"
    assert ann.value_b == "bar"
    assert ann.value_a is None


def test_mismatched_key_has_mismatch_status(rich_result):
    annotated = annotate(rich_result)
    ann = annotated.annotations["SHARED"]
    assert ann.status == "mismatch"
    assert ann.value_a == "old"
    assert ann.value_b == "new"


def test_note_contains_description_when_provided(rich_result):
    descs = {"ONLY_A": "Database URL for service A."}
    annotated = annotate(rich_result, descriptions=descs)
    assert "Database URL for service A." in annotated.annotations["ONLY_A"].note


def test_note_without_description_is_still_meaningful(rich_result):
    annotated = annotate(rich_result)
    assert annotated.annotations["ONLY_A"].note != ""


def test_by_status_filters_correctly(rich_result):
    annotated = annotate(rich_result)
    mismatches = annotated.by_status("mismatch")
    assert len(mismatches) == 1
    assert mismatches[0].key == "SHARED"


def test_all_keys_returns_sorted(rich_result):
    annotated = annotate(rich_result)
    keys = annotated.all_keys()
    assert keys == sorted(keys)
    assert set(keys) == {"ONLY_A", "ONLY_B", "SHARED"}
