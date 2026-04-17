"""Tests for envdiff.differ_snapshot."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.differ_snapshot import (
    SnapshotReport,
    diff_against_snapshot,
    load_snapshot,
    save_snapshot,
)


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def _write(p: Path, content: str) -> str:
    p.write_text(content)
    return str(p)


def test_save_creates_file(store: Path, tmp_path: Path) -> None:
    env = _write(tmp_path / ".env", "KEY=val\n")
    dest = save_snapshot(store, "prod", [env])
    assert dest.exists()


def test_save_content_is_valid_json(store: Path, tmp_path: Path) -> None:
    env = _write(tmp_path / ".env", "KEY=val\n")
    dest = save_snapshot(store, "prod", [env])
    data = json.loads(dest.read_text())
    assert data["KEY"] == "val"


def test_load_roundtrip(store: Path, tmp_path: Path) -> None:
    env = _write(tmp_path / ".env", "FOO=bar\n")
    save_snapshot(store, "staging", [env])
    loaded = load_snapshot(store, "staging")
    assert loaded["FOO"] == "bar"


def test_load_missing_raises(store: Path) -> None:
    store.mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        load_snapshot(store, "nonexistent")


def test_diff_clean_when_identical(store: Path, tmp_path: Path) -> None:
    env = _write(tmp_path / ".env", "KEY=val\n")
    save_snapshot(store, "prod", [env])
    report = diff_against_snapshot(store, "prod", [env])
    assert report.is_clean()


def test_diff_detects_missing_key(store: Path, tmp_path: Path) -> None:
    snap_env = _write(tmp_path / "snap.env", "KEY=val\nEXTRA=x\n")
    save_snapshot(store, "prod", [snap_env])
    cur_env = _write(tmp_path / "cur.env", "KEY=val\n")
    report = diff_against_snapshot(store, "prod", [cur_env])
    assert not report.is_clean()
    entry = report.entries[0]
    assert "EXTRA" in entry.diff.only_in_a


def test_diff_detects_mismatch(store: Path, tmp_path: Path) -> None:
    snap_env = _write(tmp_path / "snap.env", "KEY=old\n")
    save_snapshot(store, "prod", [snap_env])
    cur_env = _write(tmp_path / "cur.env", "KEY=new\n")
    report = diff_against_snapshot(store, "prod", [cur_env])
    assert not report.is_clean()
    assert "KEY" in report.entries[0].diff.mismatched


def test_as_dict_structure(store: Path, tmp_path: Path) -> None:
    env = _write(tmp_path / ".env", "A=1\n")
    save_snapshot(store, "prod", [env])
    report = diff_against_snapshot(store, "prod", [env])
    d = report.as_dict()
    assert "clean" in d
    assert "entries" in d
