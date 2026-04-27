"""Forecast future diff counts based on historical trend data."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from envdiff.differ_trend import TrendEntry


@dataclass
class ForecastPoint:
    step: int
    predicted_total: float

    def __repr__(self) -> str:
        return f"ForecastPoint(step={self.step}, predicted={self.predicted_total:.2f})"

    def as_dict(self) -> dict:
        return {"step": self.step, "predicted_total": round(self.predicted_total, 4)}


@dataclass
class ForecastReport:
    history: List[float]
    forecast: List[ForecastPoint]
    slope: float
    intercept: float

    @property
    def is_improving(self) -> bool:
        return self.slope < 0

    @property
    def is_worsening(self) -> bool:
        return self.slope > 0

    @property
    def is_stable(self) -> bool:
        """Return True when the slope is effectively zero (no meaningful trend)."""
        return self.slope == 0.0

    def as_dict(self) -> dict:
        return {
            "slope": round(self.slope, 4),
            "intercept": round(self.intercept, 4),
            "is_improving": self.is_improving,
            "is_stable": self.is_stable,
            "forecast": [p.as_dict() for p in self.forecast],
        }


def _linear_regression(ys: List[float]):
    """Fit a simple linear regression to the sequence *ys* and return (slope, intercept)."""
    n = len(ys)
    if n < 2:
        return 0.0, ys[0] if ys else 0.0
    xs = list(range(n))
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    den = sum((x - x_mean) ** 2 for x in xs)
    slope = num / den if den else 0.0
    intercept = y_mean - slope * x_mean
    return slope, intercept


def forecast_trend(entries: List[TrendEntry], steps: int = 3) -> ForecastReport:
    """Generate a linear forecast from *entries* for the next *steps* time steps.

    Args:
        entries: Historical trend snapshots produced by ``compute_trend``.
        steps:   Number of future steps to predict (must be >= 1).

    Returns:
        A :class:`ForecastReport` containing the fitted line and predicted points.

    Raises:
        ValueError: If *steps* is less than 1.
    """
    if steps < 1:
        raise ValueError(f"steps must be >= 1, got {steps}")

    history = [float(e.missing_in_b + e.missing_in_a + e.mismatched) for e in entries]
    slope, intercept = _linear_regression(history)
    n = len(history)
    forecast = [
        ForecastPoint(step=n + i, predicted_total=max(0.0, intercept + slope * (n + i)))
        for i in range(steps)
    ]
    return ForecastReport(history=history, forecast=forecast, slope=slope, intercept=intercept)
