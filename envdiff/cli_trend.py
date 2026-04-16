"""CLI integration for diff trend tracking."""
from __future__ import annotations

import functools
from typing import Callable

import click

from envdiff.differ_trend import record_entry, load_trend, format_trend

_DEFAULT_TREND_FILE = ".envdiff_trend.json"


def trend_options(cmd: Callable) -> Callable:
    @click.option("--trend-record", is_flag=True, default=False, help="Record this run to trend history.")
    @click.option("--trend-show", is_flag=True, default=False, help="Print trend history and exit.")
    @click.option("--trend-file", default=_DEFAULT_TREND_FILE, show_default=True, help="Path to trend history file.")
    @functools.wraps(cmd)
    def wrapper(*args, trend_record: bool, trend_show: bool, trend_file: str, **kwargs):
        return cmd(*args, trend_record=trend_record, trend_show=trend_show, trend_file=trend_file, **kwargs)
    return wrapper


def apply_trend(grouped, *, trend_record: bool, trend_show: bool, trend_file: str) -> bool:
    """Record or display trend data.

    Returns True if the caller should exit early (--trend-show consumed the run).
    """
    if trend_show:
        report = load_trend(trend_file)
        click.echo(format_trend(report))
        return True

    if trend_record:
        entry = record_entry(grouped, trend_file)
        click.echo(
            f"[trend] recorded: missing_in_b={entry.missing_in_b} "
            f"missing_in_a={entry.missing_in_a} mismatched={entry.mismatched} "
            f"total={entry.total}"
        )

    return False
