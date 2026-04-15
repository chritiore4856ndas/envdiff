"""Watch .env files for changes and re-run comparison automatically."""

from __future__ import annotations

import time
import os
from pathlib import Path
from typing import Callable


class FileWatcher:
    """Poll a set of files and invoke a callback when any of them change."""

    def __init__(self, paths: list[Path], callback: Callable[[], None], interval: float = 1.0) -> None:
        self.paths = paths
        self.callback = callback
        self.interval = interval
        self._mtimes: dict[Path, float] = {}

    def _snapshot(self) -> dict[Path, float]:
        result: dict[Path, float] = {}
        for p in self.paths:
            try:
                result[p] = os.path.getmtime(p)
            except FileNotFoundError:
                result[p] = -1.0
        return result

    def _changed(self, current: dict[Path, float]) -> bool:
        return current != self._mtimes

    def start(self, max_iterations: int | None = None) -> None:
        """Begin polling loop.  *max_iterations* is used in tests to avoid infinite loops."""
        self._mtimes = self._snapshot()
        iterations = 0
        while True:
            time.sleep(self.interval)
            current = self._snapshot()
            if self._changed(current):
                self._mtimes = current
                self.callback()
            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                break


def watch(paths: list[Path], callback: Callable[[], None], interval: float = 1.0, max_iterations: int | None = None) -> None:
    """Convenience wrapper around :class:`FileWatcher`."""
    watcher = FileWatcher(paths, callback, interval=interval)
    watcher.start(max_iterations=max_iterations)
