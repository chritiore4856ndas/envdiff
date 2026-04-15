"""Tests for envdiff.redactor."""
from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.redactor import REDACTED, _is_sensitive, redact_diff


@pytest.fixture()
def rich_result() -> DiffResult:
    return DiffResult(
        only_in_a={"ONLY_A"},
        only_in_b={"ONLY_B"},
        mismatches={
            "DB_PASSWORD": ("hunter2", "s3cr3t"),
            "API_KEY": ("abc123", "xyz789"),
            "APP_NAME": ("dev", "prod"),
            "AUTH_TOKEN": ("tok_a", "tok_b"),
            "DEBUG": ("true", "false"),
        },
    )


class TestIsSensitive:
    def test_password_key_is_sensitive(self):
        assert _is_sensitive("DB_PASSWORD") is True

    def test_secret_key_is_sensitive(self):
        assert _is_sensitive("APP_SECRET") is True

    def test_token_key_is_sensitive(self):
        assert _is_sensitive("ACCESS_TOKEN") is True

    def test_api_key_is_sensitive(self):
        assert _is_sensitive("API_KEY") is True

    def test_plain_key_is_not_sensitive(self):
        assert _is_sensitive("APP_NAME") is False

    def test_debug_is_not_sensitive(self):
        assert _is_sensitive("DEBUG") is False

    def test_extra_pattern_matches(self):
        assert _is_sensitive("MY_PRIVATE_STUFF", extra_patterns=[r"private"]) is True

    def test_extra_pattern_does_not_affect_unrelated(self):
        assert _is_sensitive("APP_NAME", extra_patterns=[r"private"]) is False


class TestRedactDiff:
    def test_sensitive_mismatch_values_are_redacted(self, rich_result: DiffResult):
        redacted = redact_diff(rich_result)
        a_val, b_val = redacted.mismatches["DB_PASSWORD"]
        assert a_val == REDACTED
        assert b_val == REDACTED

    def test_non_sensitive_values_are_unchanged(self, rich_result: DiffResult):
        redacted = redact_diff(rich_result)
        assert redacted.mismatches["APP_NAME"] == ("dev", "prod")

    def test_api_key_redacted(self, rich_result: DiffResult):
        redacted = redact_diff(rich_result)
        assert redacted.mismatches["API_KEY"] == (REDACTED, REDACTED)

    def test_auth_token_redacted(self, rich_result: DiffResult):
        redacted = redact_diff(rich_result)
        assert redacted.mismatches["AUTH_TOKEN"] == (REDACTED, REDACTED)

    def test_only_in_a_and_b_unchanged(self, rich_result: DiffResult):
        redacted = redact_diff(rich_result)
        assert redacted.only_in_a == rich_result.only_in_a
        assert redacted.only_in_b == rich_result.only_in_b

    def test_none_value_stays_none(self):
        result = DiffResult(
            only_in_a=set(),
            only_in_b=set(),
            mismatches={"DB_PASSWORD": (None, "secret_val")},
        )
        redacted = redact_diff(result)
        a_val, b_val = redacted.mismatches["DB_PASSWORD"]
        assert a_val is None
        assert b_val == REDACTED

    def test_extra_pattern_redacts_custom_key(self, rich_result: DiffResult):
        result = DiffResult(
            only_in_a=set(),
            only_in_b=set(),
            mismatches={"STRIPE_LIVE": ("val_a", "val_b")},
        )
        redacted = redact_diff(result, extra_patterns=[r"stripe"])
        assert redacted.mismatches["STRIPE_LIVE"] == (REDACTED, REDACTED)
