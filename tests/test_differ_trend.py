"""Tests for envdiff.differ_trend."""
import json
import time
from pathlib import Path

import pytest

from envdiff.comparator import DiffResult
from envdiff.sorter import GroupedDiff, group_diff
from envdiff.differ_trend import (
    TrendEntry,
    TrendReport,
    record_entry,
    load_trend,
    format_trend,
)


@pytest.fixture()
def trend_file(tmp_path: Path) -> str:
    return str(tmp_path / "trend.json")


@pytest.fixture()
def grouped() -> GroupedDiff:
    result = DiffResult(
        only_in_a={"FOO": "1"},
        only_in_b={"BAR": "2"},
        mismatched={"BAZ": ("x", "y")},
        matching={},
    )
    return group_diff(result)


def test_record_creates_file(trend_file, grouped):
    record_entry(grouped, trend_file)
    assert Path(trend_file).exists()


def test_record_content_is_valid_json(trend_file, grouped):
    record_entry(grouped, trend_file)
    data = json.loads(Path(trend_file).read_text())
    assert isinstance(data, list)
    assert len(data) == 1


def test_record_counts_match_grouped(trend_file, grouped):
    entry = record_entry(grouped, trend_file)
    assert entry.missing_in_b == 1
    assert entry.missing_in_a == 1
    assert entry.mismatched == 1
    assert entry.total == 3


def test_multiple_records_appended(trend_file, grouped):
    record_entry(grouped, trend_file)
    record_entry(grouped, trend_file)
    data = json.loads(Path(trend_file).read_text())
    assert len(data) == 2


def test_load_trend_empty_when_no_file(trend_file):
    report = load_trend(trend_file)
    assert report.entries == []


def test_load_trend_roundtrip(trend_file, grouped):
    record_entry(grouped, trend_file)
    report = load_trend(trend_file)
    assert len(report.entries) == 1
    assert isinstance(report.entries[0], TrendEntry)


def test_improving_when_total_decreases(trend_file):
    report = TrendReport(entries=[
        TrendEntry(timestamp=1.0, missing_in_b=2, missing_in_a=1, mismatched=1, total=4),
        TrendEntry(timestamp=2.0, missing_in_b=1, missing_in_a=0, mismatched=1, total=2),
    ])
    assert report.improving() is True
    assert report.worsening() is False


def test_worsening_when_total_increases():
    report = TrendReport(entries=[
        TrendEntry(timestamp=1.0, missing_in_b=1, missing_in_a=0, mismatched=0, total=1),
        TrendEntry(timestamp=2.0, missing_in_b=2, missing_in_a=1, mismatched=1, total=4),
    ])
    assert report.worsening() is True


def test_format_trend_no_data():
    report = TrendReport()
    assert "No trend" in format_trend(report)


def test_format_trend_shows_improving(trend_file, grouped):
    report = TrendReport(entries=[
        TrendEntry(timestamp=time.time() - 10, missing_in_b=3, missing_in_a=2, mismatched=1, total=6),
        TrendEntry(timestamp=time.time(), missing_in_b=1, missing_in_a=0, mismatched=0, total=1),
    ])
    out = format_trend(report)
    assert "improving" in out
