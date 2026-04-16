import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_rank import RankReport, RankedKey, rank_diffs, format_rank


def _result(only_a=(), only_b=(), mismatched=()) -> DiffResult:
    return DiffResult(
        only_in_a=list(only_a),
        only_in_b=list(only_b),
        mismatched={k: ("x", "y") for k in mismatched},
    )


def test_empty_results_gives_empty_report():
    report = rank_diffs([])
    assert report.ranked == []
    assert report.top is None


def test_single_result_missing_key():
    report = rank_diffs([_result(only_a=["FOO"])])
    assert len(report.ranked) == 1
    assert report.ranked[0].key == "FOO"
    assert report.ranked[0].count == 1


def test_key_appearing_in_multiple_results_has_higher_count():
    r1 = _result(only_a=["FOO"])
    r2 = _result(mismatched=["FOO"])
    r3 = _result(only_b=["BAR"])
    report = rank_diffs([r1, r2, r3])
    top = report.top
    assert top is not None
    assert top.key == "FOO"
    assert top.count == 2


def test_rank_is_sorted_descending():
    r1 = _result(only_a=["A", "B"])
    r2 = _result(only_a=["A"])
    report = rank_diffs([r1, r2])
    assert report.ranked[0].key == "A"
    assert report.ranked[0].count == 2
    assert report.ranked[1].key == "B"
    assert report.ranked[1].count == 1


def test_key_counted_once_per_result_even_if_in_multiple_categories():
    # only_a and mismatched both contain KEY — should count once per result
    r = _result(only_a=["KEY"], mismatched=["KEY"])
    report = rank_diffs([r])
    assert report.ranked[0].count == 1


def test_as_dict_returns_list_of_dicts():
    report = RankReport(ranked=[RankedKey("FOO", 3), RankedKey("BAR", 1)])
    d = report.as_dict()
    assert d == [{"key": "FOO", "count": 3}, {"key": "BAR", "count": 1}]


def test_format_rank_empty():
    assert format_rank(RankReport()) == "No differing keys found."


def test_format_rank_shows_keys():
    report = RankReport(ranked=[RankedKey("SECRET", 5), RankedKey("DB_URL", 2)])
    out = format_rank(report)
    assert "SECRET" in out
    assert "5 occurrence" in out
    assert "DB_URL" in out
