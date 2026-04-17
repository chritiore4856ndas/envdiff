"""Tests for envdiff.differ_fingerprint."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_fingerprint import (
    Fingerprint,
    fingerprint_diff,
    fingerprints_match,
)


def _make(only_a=None, only_b=None, mismatched=None) -> DiffResult:
    return DiffResult(
        only_in_a=only_a or [],
        only_in_b=only_b or [],
        mismatched=mismatched or {},
    )


def test_fingerprint_returns_fingerprint_instance():
    result = fingerprint_diff(_make())
    assert isinstance(result, Fingerprint)


def test_empty_result_has_hex():
    fp = fingerprint_diff(_make())
    assert len(fp.hex) == 16


def test_identical_results_same_fingerprint():
    a = _make(only_a=["FOO"], mismatched={"BAR": ("x", "y")})
    b = _make(only_a=["FOO"], mismatched={"BAR": ("x", "y")})
    assert fingerprint_diff(a) == fingerprint_diff(b)


def test_different_only_in_a_gives_different_fingerprint():
    a = _make(only_a=["FOO"])
    b = _make(only_a=["BAR"])
    assert fingerprint_diff(a) != fingerprint_diff(b)


def test_different_only_in_b_gives_different_fingerprint():
    a = _make(only_b=["X"])
    b = _make(only_b=["Y"])
    assert fingerprint_diff(a) != fingerprint_diff(b)


def test_different_mismatched_gives_different_fingerprint():
    a = _make(mismatched={"K": ("v1", "v2")})
    b = _make(mismatched={"K": ("v1", "v3")})
    assert fingerprint_diff(a) != fingerprint_diff(b)


def test_components_keys_present():
    fp = fingerprint_diff(_make(only_a=["A"]))
    assert set(fp.components) == {"only_in_a", "only_in_b", "mismatched"}


def test_as_dict_contains_hex():
    fp = fingerprint_diff(_make())
    d = fp.as_dict()
    assert "hex" in d and "components" in d


def test_fingerprints_match_true_for_equal():
    a = _make(only_a=["FOO"])
    b = _make(only_a=["FOO"])
    assert fingerprints_match(a, b) is True


def test_fingerprints_match_false_for_different():
    a = _make(only_a=["FOO"])
    b = _make(only_b=["FOO"])
    assert fingerprints_match(a, b) is False


def test_order_of_only_in_a_does_not_matter():
    a = _make(only_a=["A", "B"])
    b = _make(only_a=["B", "A"])
    assert fingerprint_diff(a) == fingerprint_diff(b)
