"""Track diff results over time and report trends."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envdiff.sorter import GroupedDiff

_DEFAULT_TREND_FILE = ".envdiff_trend.json"


@dataclass
class TrendEntry:
    timestamp: float
    missing_in_b: int
    missing_in_a: int
    mismatched: int
    total: int

    def as_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "missing_in_b": self.missing_in_b,
            "missing_in_a": self.missing_in_a,
            "mismatched": self.mismatched,
            "total": self.total,
        }


@dataclass
class TrendReport:
    entries: List[TrendEntry] = field(default_factory=list)

    def improving(self) -> bool:
        if len(self.entries) < 2:
            return False
        return self.entries[-1].total < self.entries[-2].total

    def worsening(self) -> bool:
        if len(self.entries) < 2:
            return False
        return self.entries[-1].total > self.entries[-2].total


def _trend_path(path: str) -> Path:
    return Path(path)


def record_entry(grouped: GroupedDiff, trend_file: str = _DEFAULT_TREND_FILE) -> TrendEntry:
    entry = TrendEntry(
        timestamp=time.time(),
        missing_in_b=len(grouped.missing_in_b),
        missing_in_a=len(grouped.missing_in_a),
        mismatched=len(grouped.mismatched),
        total=len(grouped.missing_in_b) + len(grouped.missing_in_a) + len(grouped.mismatched),
    )
    p = _trend_path(trend_file)
    existing: list = []
    if p.exists():
        existing = json.loads(p.read_text())
    existing.append(entry.as_dict())
    p.write_text(json.dumps(existing, indent=2))
    return entry


def load_trend(trend_file: str = _DEFAULT_TREND_FILE) -> TrendReport:
    p = _trend_path(trend_file)
    if not p.exists():
        return TrendReport()
    raw = json.loads(p.read_text())
    entries = [TrendEntry(**r) for r in raw]
    return TrendReport(entries=entries)


def format_trend(report: TrendReport) -> str:
    if not report.entries:
        return "No trend data recorded yet."
    lines = ["Trend history:", f"  {'Timestamp':<22} {'Missing-B':>10} {'Missing-A':>10} {'Mismatch':>10} {'Total':>8}"]
    for e in report.entries:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e.timestamp))
        lines.append(f"  {ts:<22} {e.missing_in_b:>10} {e.missing_in_a:>10} {e.mismatched:>10} {e.total:>8}")
    if report.improving():
        lines.append("\nTrend: improving ✓")
    elif report.worsening():
        lines.append("\nTrend: worsening ✗")
    else:
        lines.append("\nTrend: stable")
    return "\n".join(lines)
