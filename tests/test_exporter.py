"""Tests for envdiff.exporter."""
from __future__ import annotations

import csv
import io
import json

import pytest

from envdiff.sorter import GroupedDiff
from envdiff.exporter import export_diff, export_json, export_csv, export_markdown


@pytest.fixture()
def empty_grouped() -> GroupedDiff:
    return GroupedDiff(missing_in_b=set(), missing_in_a=set(), mismatched={})


@pytest.fixture()
def rich_grouped() -> GroupedDiff:
    return GroupedDiff(
        missing_in_b={"ONLY_A"},
        missing_in_a={"ONLY_B"},
        mismatched={"SHARED": ("old", "new")},
    )


# --- JSON ---

def test_json_empty(empty_grouped: GroupedDiff) -> None:
    result = json.loads(export_json(empty_grouped))
    assert result["missing_in_b"] == []
    assert result["missing_in_a"] == []
    assert result["mismatched"] == []


def test_json_rich(rich_grouped: GroupedDiff) -> None:
    result = json.loads(export_json(rich_grouped))
    assert "ONLY_A" in result["missing_in_b"]
    assert "ONLY_B" in result["missing_in_a"]
    assert result["mismatched"] == [{"key": "SHARED", "value_a": "old", "value_b": "new"}]


# --- CSV ---

def test_csv_has_header(rich_grouped: GroupedDiff) -> None:
    output = export_csv(rich_grouped)
    reader = csv.reader(io.StringIO(output))
    header = next(reader)
    assert header == ["key", "status", "value_a", "value_b"]


def test_csv_rows(rich_grouped: GroupedDiff) -> None:
    output = export_csv(rich_grouped)
    reader = csv.DictReader(io.StringIO(output))
    rows = {r["key"]: r for r in reader}
    assert rows["ONLY_A"]["status"] == "missing_in_b"
    assert rows["ONLY_B"]["status"] == "missing_in_a"
    assert rows["SHARED"]["status"] == "mismatched"
    assert rows["SHARED"]["value_a"] == "old"
    assert rows["SHARED"]["value_b"] == "new"


# --- Markdown ---

def test_markdown_has_header_row(rich_grouped: GroupedDiff) -> None:
    output = export_markdown(rich_grouped)
    assert "| Key | Status |" in output


def test_markdown_contains_keys(rich_grouped: GroupedDiff) -> None:
    output = export_markdown(rich_grouped)
    assert "`ONLY_A`" in output
    assert "`ONLY_B`" in output
    assert "`SHARED`" in output


# --- dispatch ---

def test_export_diff_unknown_format(rich_grouped: GroupedDiff) -> None:
    with pytest.raises(ValueError, match="Unknown export format"):
        export_diff(rich_grouped, "xml")  # type: ignore[arg-type]


def test_export_diff_dispatches_json(rich_grouped: GroupedDiff) -> None:
    result = export_diff(rich_grouped, "json")
    assert json.loads(result)  # valid JSON


def test_export_diff_dispatches_csv(rich_grouped: GroupedDiff) -> None:
    result = export_diff(rich_grouped, "csv")
    assert "key,status" in result


def test_export_diff_dispatches_markdown(rich_grouped: GroupedDiff) -> None:
    result = export_diff(rich_grouped, "markdown")
    assert "|" in result
