import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_dispersion import DispersionEntry, DispersionReport, dispersion_diff


def _result(
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
    matching=None,
) -> DiffResult:
    return DiffResult(
        only_in_a=only_in_a or {},
        only_in_b=only_in_b or {},
        mismatched=mismatched or {},
        matching=matching or {},
    )


def test_empty_results_gives_empty_report():
    report = dispersion_diff([])
    assert report.entries == []
    assert report.total_snapshots == 0


def test_single_result_missing_key_counted():
    r = _result(only_in_a={"FOO": "bar"})
    report = dispersion_diff([r])
    assert len(report.entries) == 1
    assert report.entries[0].key == "FOO"
    assert report.entries[0].appearances == 1
    assert report.entries[0].dispersion_rate == 1.0


def test_key_in_all_results_has_rate_one():
    results = [_result(only_in_a={"KEY": "v"}) for _ in range(4)]
    report = dispersion_diff(results)
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.dispersion_rate == 1.0


def test_key_in_half_results_has_half_rate():
    results = [
        _result(only_in_a={"KEY": "v"}),
        _result(only_in_a={"KEY": "v"}),
        _result(matching={"KEY": ("v", "v")}),
        _result(matching={"KEY": ("v", "v")}),
    ]
    report = dispersion_diff(results)
    entry = next(e for e in report.entries if e.key == "KEY")
    assert entry.dispersion_rate == pytest.approx(0.5)


def test_spread_threshold_filters_entries():
    results = [
        _result(only_in_a={"RARE": "x"}),
        _result(only_in_a={"COMMON": "y"}),
        _result(only_in_a={"COMMON": "y"}),
        _result(only_in_a={"COMMON": "y"}),
    ]
    report = dispersion_diff(results)
    spread = report.spread(threshold=0.5)
    keys = {e.key for e in spread}
    assert "COMMON" in keys
    assert "RARE" not in keys


def test_mismatched_keys_counted():
    r = _result(mismatched={"DB_URL": ("a", "b")})
    report = dispersion_diff([r])
    keys = {e.key for e in report.entries}
    assert "DB_URL" in keys


def test_entries_sorted_descending_by_appearances():
    results = [
        _result(only_in_a={"A": "1", "B": "2"}),
        _result(only_in_a={"A": "1"}),
    ]
    report = dispersion_diff(results)
    rates = [e.appearances for e in report.entries]
    assert rates == sorted(rates, reverse=True)


def test_as_dict_contains_expected_keys():
    r = _result(only_in_a={"X": "1"})
    report = dispersion_diff([r])
    d = report.as_dict()
    assert "total_snapshots" in d
    assert "entries" in d
    assert d["entries"][0]["dispersion_rate"] == 1.0
