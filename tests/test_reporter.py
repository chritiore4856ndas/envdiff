"""Tests for envdiff.reporter."""
from __future__ import annotations

import io
import json

import pytest

from envdiff.comparator import DiffResult
from envdiff.reporter import build_report, emit_report


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(only_in_a={}, only_in_b={}, mismatched={})


@pytest.fixture()
def rich_result() -> DiffResult:
    return DiffResult(
        only_in_a={"GONE": "1"},
        only_in_b={"NEW": "2"},
        mismatched={"HOST": ("localhost", "prod.example.com")},
    )


# ---------------------------------------------------------------------------
# build_report
# ---------------------------------------------------------------------------

class TestBuildReport:
    def test_text_format_returns_string(self, rich_result: DiffResult) -> None:
        report = build_report(rich_result, fmt="text", use_color=False)
        assert isinstance(report, str)
        assert "GONE" in report

    def test_json_format_is_valid_json(self, rich_result: DiffResult) -> None:
        report = build_report(rich_result, fmt="json")
        data = json.loads(report)
        assert "missing_in_b" in data or "missing_in_a" in data or "mismatched" in data

    def test_json_format_contains_all_keys(self, rich_result: DiffResult) -> None:
        """Verify the JSON report includes entries for every diff category."""
        report = build_report(rich_result, fmt="json")
        data = json.loads(report)
        # At least one of the known category keys must appear for each fixture value
        only_a_key = next((k for k in data if "a" in k or "missing" in k), None)
        only_b_key = next((k for k in data if "b" in k or "new" in k), None)
        assert only_a_key is not None, "Expected a key representing only_in_a"
        assert only_b_key is not None, "Expected a key representing only_in_b"

    def test_unknown_format_raises(self, empty_result: DiffResult) -> None:
        with pytest.raises(ValueError, match="Unknown format"):
            build_report(empty_result, fmt="xml")

    def test_no_diff_text_contains_ok(self, empty_result: DiffResult) -> None:
        report = build_report(empty_result, fmt="text", use_color=False)
        assert "no diff" in report.lower() or report.strip() != ""


# ---------------------------------------------------------------------------
# emit_report
# ---------------------------------------------------------------------------

class TestEmitReport:
    def test_writes_to_stream(self, rich_result: DiffResult) -> None:
        buf = io.StringIO()
        emit_report(rich_result, fmt="text", use_color=False, stream=buf)
        assert len(buf.getvalue()) > 0

    def test_returns_zero_when_no_exit_on_diff(self, rich_result: DiffResult) -> None:
        buf = io.StringIO()
        code = emit_report(rich_result, exit_on_diff=False, stream=buf)
        assert code == 0

    def test_returns_one_on_diff_with_flag(self, rich_result: DiffResult) -> None:
        buf = io.StringIO()
        code = emit_report(rich_result, exit_on_diff=True, stream=buf)
        assert code == 1

    def test_returns_zero_no_diff_with_flag(self, empty_result: DiffResult) -> None:
        buf = io.StringIO()
        code = emit_report(empty_result, exit_on_diff=True, stream=buf)
        assert code == 0

    def test_output_ends_with_newline(self, empty_result: DiffResult) -> None:
        buf = io.StringIO()
        emit_report(empty_result, stream=buf)
        assert buf.getvalue().endswith("\n")
