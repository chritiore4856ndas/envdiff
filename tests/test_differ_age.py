"""Tests for envdiff.differ_age."""
import json
import os
import pytest

from envdiff.differ_age import (
    AgeEntry,
    AgeReport,
    load_age_data,
    record_age,
    _age_path,
)


@pytest.fixture
def age_file(tmp_path):
    return str(tmp_path / "test.env")


def test_record_creates_age_file(age_file):
    record_age(age_file, {"KEY": "val"})
    assert os.path.exists(_age_path(age_file))


def test_record_content_is_valid_json(age_file):
    record_age(age_file, {"KEY": "val"})
    with open(_age_path(age_file)) as f:
        data = json.load(f)
    assert "KEY" in data


def test_new_key_change_count_is_one(age_file):
    report = record_age(age_file, {"KEY": "val"})
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.change_count == 1


def test_unchanged_value_does_not_increment_count(age_file):
    record_age(age_file, {"KEY": "val"})
    report = record_age(age_file, {"KEY": "val"})
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.change_count == 1


def test_changed_value_increments_count(age_file):
    record_age(age_file, {"KEY": "old"})
    report = record_age(age_file, {"KEY": "new"})
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.change_count == 2


def test_stale_returns_keys_below_threshold(age_file):
    report = record_age(age_file, {"A": "x", "B": "y"})
    stale = report.stale(min_changes=2)
    keys = [e.key for e in stale]
    assert "A" in keys
    assert "B" in keys


def test_stale_excludes_frequently_changed_keys(age_file):
    record_age(age_file, {"A": "v1"})
    record_age(age_file, {"A": "v2"})
    report = record_age(age_file, {"A": "v3"})
    stale = report.stale(min_changes=3)
    assert all(e.key != "A" for e in stale)


def test_as_dict_contains_entries(age_file):
    report = record_age(age_file, {"KEY": "val"})
    d = report.as_dict()
    assert "entries" in d
    assert d["entries"][0]["key"] == "KEY"


def test_multiple_keys_all_tracked(age_file):
    report = record_age(age_file, {"X": "1", "Y": "2", "Z": None})
    keys = {e.key for e in report.entries}
    assert keys == {"X", "Y", "Z"}
