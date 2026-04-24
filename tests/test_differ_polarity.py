import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_polarity import polarity_diff, PolarityEntry, PolarityReport


def _result(
    matching=None,
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        matching=matching or {},
        only_in_a=only_in_a or {},
        only_in_b=only_in_b or {},
        mismatched=mismatched or {},
    )


def test_empty_results_gives_empty_report():
    report = polarity_diff([])
    assert isinstance(report, PolarityReport)
    assert report.entries == []


def test_single_result_matching_key_is_positive():
    r = _result(matching={"KEY": "val"})
    report = polarity_diff([r])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.key == "KEY"
    assert entry.positive == 1
    assert entry.negative == 0
    assert entry.dominant == "positive"


def test_single_result_missing_key_is_negative():
    r = _result(only_in_a={"KEY": "val"})
    report = polarity_diff([r])
    entry = report.entries[0]
    assert entry.dominant == "negative"
    assert entry.polarity_ratio == 0.0


def test_mismatched_key_counts_as_negative():
    r = _result(mismatched={"KEY": ("a", "b")})
    report = polarity_diff([r])
    entry = report.entries[0]
    assert entry.negative == 1
    assert entry.positive == 0


def test_key_always_matching_across_snapshots_is_positive():
    results = [_result(matching={"K": str(i)}) for i in range(4)]
    report = polarity_diff(results)
    entry = report.entries[0]
    assert entry.positive == 4
    assert entry.dominant == "positive"


def test_key_half_positive_half_negative_is_neutral():
    results = [
        _result(matching={"K": "v"}),
        _result(matching={"K": "v"}),
        _result(only_in_a={"K": "v"}),
        _result(only_in_a={"K": "v"}),
    ]
    report = polarity_diff(results)
    entry = report.entries[0]
    assert entry.dominant == "neutral"
    assert entry.polarity_ratio == pytest.approx(0.5)


def test_positive_negative_neutral_grouping():
    results = [
        _result(matching={"GOOD": "v"}, only_in_a={"BAD": "v"}, mismatched={"MID": ("a", "b")}),
        _result(matching={"GOOD": "v"}, only_in_a={"BAD": "v"}, matching2={"MID": "a"}) if False
        else _result(matching={"GOOD": "v", "MID": "a"}, only_in_a={"BAD": "v"}),
        _result(matching={"GOOD": "v"}, only_in_a={"BAD": "v"}, mismatched={"MID": ("a", "b")}),
        _result(matching={"GOOD": "v"}, only_in_a={"BAD": "v"}, matching2={"MID": "a"}) if False
        else _result(matching={"GOOD": "v", "MID": "a"}, only_in_a={"BAD": "v"}),
    ]
    report = polarity_diff(results)
    keys = {e.key: e for e in report.entries}
    assert keys["GOOD"].dominant == "positive"
    assert keys["BAD"].dominant == "negative"


def test_as_dict_contains_expected_fields():
    r = _result(matching={"X": "1"})
    report = polarity_diff([r])
    d = report.as_dict()
    assert "entries" in d
    assert "positive_count" in d
    assert "negative_count" in d
    assert "neutral_count" in d


def test_entry_as_dict_structure():
    entry = PolarityEntry(key="FOO", positive=3, negative=1, total=4)
    d = entry.as_dict()
    assert d["key"] == "FOO"
    assert d["polarity_ratio"] == pytest.approx(0.75)
    assert d["dominant"] == "positive"


def test_entries_sorted_by_key():
    r = _result(matching={"Z": "1", "A": "2", "M": "3"})
    report = polarity_diff([r])
    keys = [e.key for e in report.entries]
    assert keys == sorted(keys)
