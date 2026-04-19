"""CLI integration for diff forecast."""
from __future__ import annotations

import json
from typing import Callable

import click

from envdiff.differ_trend import load_trend
from envdiff.differ_forecast import forecast_trend


def forecast_options(f: Callable) -> Callable:
    f = click.option(
        "--forecast",
        "forecast_path",
        default=None,
        help="Path to trend file; print forecast and exit.",
    )(f)
    f = click.option(
        "--forecast-steps",
        default=3,
        show_default=True,
        help="Number of steps to forecast ahead.",
    )(f)
    f = click.option(
        "--forecast-json",
        is_flag=True,
        default=False,
        help="Output forecast as JSON.",
    )(f)
    return f


def apply_forecast(ctx_params: dict) -> bool:
    """Return True if forecast was handled and caller should exit."""
    path = ctx_params.get("forecast_path")
    if not path:
        return False

    steps = ctx_params.get("forecast_steps", 3)
    as_json = ctx_params.get("forecast_json", False)

    entries = load_trend(path)
    report = forecast_trend(entries, steps=steps)

    if as_json:
        click.echo(json.dumps(report.as_dict(), indent=2))
    else:
        direction = "worsening" if report.is_worsening else ("improving" if report.is_improving else "stable")
        click.echo(f"Trend: {direction}  (slope={report.slope:+.3f})")
        for p in report.forecast:
            click.echo(f"  step {p.step}: {p.predicted_total:.1f} issues")

    return True
