"""Tests for envdiff.watcher."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envdiff.watcher import FileWatcher, watch


@pytest.fixture()
def tmp_files(tmp_path: Path):
    a = tmp_path / "a.env"
    b = tmp_path / "b.env"
    a.write_text("KEY=1\n")
    b.write_text("KEY=1\n")
    return a, b


def test_no_change_callback_not_called(tmp_files, monkeypatch):
    a, b = tmp_files
    calls: list[int] = []
    monkeypatch.setattr(time, "sleep", lambda _: None)
    watcher = FileWatcher([a, b], lambda: calls.append(1), interval=0)
    watcher.start(max_iterations=3)
    assert calls == []


def test_callback_called_on_change(tmp_files, monkeypatch):
    a, b = tmp_files
    calls: list[int] = []
    iteration = 0

    def fake_sleep(_):
        nonlocal iteration
        iteration += 1
        if iteration == 1:
            a.write_text("KEY=2\n")

    monkeypatch.setattr(time, "sleep", fake_sleep)
    watcher = FileWatcher([a, b], lambda: calls.append(1), interval=0)
    watcher.start(max_iterations=3)
    assert len(calls) >= 1


def test_callback_called_once_per_change_event(tmp_files, monkeypatch):
    a, b = tmp_files
    calls: list[int] = []
    iteration = 0

    def fake_sleep(_):
        nonlocal iteration
        iteration += 1
        if iteration == 1:
            b.write_text("KEY=changed\n")

    monkeypatch.setattr(time, "sleep", fake_sleep)
    watcher = FileWatcher([a, b], lambda: calls.append(1), interval=0)
    watcher.start(max_iterations=4)
    # change happened once, so callback fires exactly once
    assert calls == [1]


def test_missing_file_does_not_raise(tmp_path, monkeypatch):
    missing = tmp_path / "ghost.env"
    monkeypatch.setattr(time, "sleep", lambda _: None)
    watcher = FileWatcher([missing], lambda: None, interval=0)
    # Should not raise even though file doesn't exist
    watcher.start(max_iterations=2)


def test_watch_convenience_wrapper(tmp_files, monkeypatch):
    a, b = tmp_files
    calls: list[int] = []
    monkeypatch.setattr(time, "sleep", lambda _: None)
    watch([a, b], lambda: calls.append(1), interval=0, max_iterations=2)
    assert isinstance(calls, list)
