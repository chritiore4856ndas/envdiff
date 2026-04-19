import pytest
from envdiff.differ_trend import TrendEntry
from envdiff.differ_forecast import ForecastPoint, ForecastReport, forecast_trend


def _entry(missing_b=0, missing_a=0, mismatched=0):
    return TrendEntry(
        timestamp="2024-01-01T00:00:00",
        missing_in_b=missing_b,
        missing_in_a=missing_a,
        mismatched=mismatched,
    )


def test_empty_entries_gives_empty_history():
    report = forecast_trend([])
    assert report.history == []
    assert report.forecast == []


def test_single_entry_slope_is_zero():
    report = forecast_trend([_entry(missing_b=2, mismatched=1)])
    assert report.slope == 0.0


def test_forecast_default_three_steps():
    entries = [_entry(mismatched=i) for i in range(5)]
    report = forecast_trend(entries)
    assert len(report.forecast) == 3


def test_forecast_custom_steps():
    entries = [_entry(mismatched=i) for i in range(4)]
    report = forecast_trend(entries, steps=5)
    assert len(report.forecast) == 5


def test_increasing_trend_is_worsening():
    entries = [_entry(mismatched=i * 2) for i in range(5)]
    report = forecast_trend(entries)
    assert report.is_worsening
    assert not report.is_improving


def test_decreasing_trend_is_improving():
    entries = [_entry(mismatched=10 - i * 2) for i in range(5)]
    report = forecast_trend(entries)
    assert report.is_improving
    assert not report.is_worsening


def test_forecast_step_indices_start_after_history():
    entries = [_entry(mismatched=i) for i in range(4)]
    report = forecast_trend(entries, steps=3)
    steps = [p.step for p in report.forecast]
    assert steps == [4, 5, 6]


def test_predicted_total_never_negative():
    entries = [_entry(mismatched=max(0, 5 - i * 3)) for i in range(5)]
    report = forecast_trend(entries, steps=5)
    for p in report.forecast:
        assert p.predicted_total >= 0.0


def test_as_dict_contains_expected_keys():
    entries = [_entry(mismatched=i) for i in range(3)]
    d = forecast_trend(entries).as_dict()
    assert "slope" in d
    assert "intercept" in d
    assert "forecast" in d
    assert "is_improving" in d


def test_forecast_point_repr():
    p = ForecastPoint(step=2, predicted_total=3.5)
    assert "2" in repr(p)
    assert "3.50" in repr(p)
