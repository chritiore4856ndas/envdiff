import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_fidelity import FidelityEntry, FidelityReport, fidelity_diff


def _result(
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
    matching=None,
) -> DiffResult:
    return DiffResult(
        only_in_a=only_in_a or [],
        only_in_b=only_in_b or [],
        mismatched=mismatched or [],
        matching=matching or [],
    )


def test_empty_results_gives_empty_report():
    report = fidelity_diff([], [])
    assert report.entries == []


def test_empty_results_average_rate_is_one():
    report = fidelity_diff([], [])
    assert report.average_rate() == 1.0


def test_empty_results_most_faithful_is_none():
    report = fidelity_diff([], [])
    assert report.most_faithful() is None


def test_single_clean_result_has_full_fidelity():
    r = _result(matching=["KEY_A", "KEY_B"])
    report = fidelity_diff([r], ["prod"])
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.fidelity_rate() == 1.0
    assert entry.is_faithful()


def test_missing_key_reduces_fidelity():
    r = _result(only_in_a=["MISSING"], matching=["KEY_A"])
    report = fidelity_diff([r], ["staging"])
    entry = report.entries[0]
    # total keys = 2 (MISSING + KEY_A), matching = 1
    assert entry.total_keys == 2
    assert entry.matching_keys == 1
    assert entry.fidelity_rate() == pytest.approx(0.5)


def test_extra_key_reduces_fidelity():
    r = _result(only_in_b=["EXTRA"], matching=["KEY_A"])
    report = fidelity_diff([r], ["dev"])
    entry = report.entries[0]
    assert entry.extra_keys == 1
    assert entry.fidelity_rate() < 1.0


def test_mismatched_key_counted():
    r = _result(mismatched=["DB_URL"], matching=["KEY_A"])
    report = fidelity_diff([r], ["qa"])
    entry = report.entries[0]
    assert entry.mismatched_keys == 1


def test_most_faithful_returns_highest_rate():
    r1 = _result(matching=["A", "B"])
    r2 = _result(only_in_a=["A"], matching=["B"])
    report = fidelity_diff([r1, r2], ["prod", "staging"])
    assert report.most_faithful().env_name == "prod"


def test_least_faithful_returns_lowest_rate():
    r1 = _result(matching=["A", "B"])
    r2 = _result(only_in_a=["A"], matching=["B"])
    report = fidelity_diff([r1, r2], ["prod", "staging"])
    assert report.least_faithful().env_name == "staging"


def test_average_rate_across_entries():
    r1 = _result(matching=["A", "B"])        # rate = 1.0
    r2 = _result(only_in_a=["A"], matching=["B"])  # rate = 0.5
    report = fidelity_diff([r1, r2], ["prod", "staging"])
    assert report.average_rate() == pytest.approx(0.75)


def test_as_dict_contains_expected_keys():
    r = _result(matching=["A"])
    report = fidelity_diff([r], ["prod"])
    d = report.as_dict()
    assert "entries" in d
    assert "average_fidelity_rate" in d
    assert "most_faithful" in d
    assert "least_faithful" in d


def test_entry_as_dict_shape():
    r = _result(matching=["A"], mismatched=["B"])
    report = fidelity_diff([r], ["prod"])
    entry_dict = report.entries[0].as_dict()
    assert entry_dict["env"] == "prod"
    assert "fidelity_rate" in entry_dict
    assert "is_faithful" in entry_dict


def test_is_faithful_threshold():
    entry = FidelityEntry(
        env_name="dev",
        total_keys=10,
        matching_keys=7,
        missing_keys=2,
        extra_keys=1,
        mismatched_keys=0,
    )
    assert entry.is_faithful(threshold=0.7)
    assert not entry.is_faithful(threshold=0.8)
