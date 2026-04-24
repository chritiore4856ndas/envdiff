import pytest
from envdiff.comparator import DiffResult
from envdiff.differ_dominance import DominanceEntry, DominanceReport, dominance_diff


def _result(
    only_in_a=None,
    only_in_b=None,
    mismatched=None,
    matching=None,
) -> DiffResult:
    return DiffResult(
        only_in_a=only_in_a or [],
        only_in_b=only_in_b or [],
        mismatched=mismatched or {},
        matching=matching or {},
    )


def test_empty_results_gives_empty_report():
    report = dominance_diff([])
    assert report.entries == []
    assert report.total_contested_keys == 0
    assert report.dominant_env() is None


def test_single_result_missing_key_counted():
    r = _result(only_in_a=["KEY"])
    report = dominance_diff([r], env_names=["prod"])
    assert report.total_contested_keys == 1
    assert len(report.entries) == 1
    assert report.entries[0].env == "prod"


def test_dominant_env_is_env_with_most_dominated_keys():
    r1 = _result(mismatched={"DB": ("postgres", "sqlite"), "HOST": ("a.com", "b.com")})
    r2 = _result(mismatched={"DB": ("postgres", "mysql")})
    report = dominance_diff([r1, r2], env_names=["alpha", "beta"])
    # alpha provides "postgres" for DB in both -> majority value
    dominant = report.dominant_env()
    assert dominant is not None
    assert isinstance(dominant, str)


def test_dominance_ratio_between_zero_and_one():
    r = _result(mismatched={"A": ("x", "y"), "B": ("p", "q")})
    report = dominance_diff([r], env_names=["env_a"])
    for entry in report.entries:
        assert 0.0 <= entry.dominance_ratio <= 1.0


def test_env_names_default_to_env_index():
    r = _result(only_in_a=["X"])
    report = dominance_diff([r])
    assert report.entries[0].env == "env_0"


def test_as_dict_contains_required_keys():
    r = _result(only_in_a=["KEY"])
    report = dominance_diff([r], env_names=["staging"])
    d = report.as_dict()
    assert "dominant_env" in d
    assert "total_contested_keys" in d
    assert "entries" in d
    assert isinstance(d["entries"], list)


def test_entry_as_dict_structure():
    r = _result(only_in_a=["FOO"])
    report = dominance_diff([r], env_names=["qa"])
    entry_dict = report.entries[0].as_dict()
    assert entry_dict["env"] == "qa"
    assert "dominated_keys" in entry_dict
    assert "dominated_count" in entry_dict
    assert "dominance_ratio" in entry_dict


def test_entries_sorted_descending_by_count():
    r1 = _result(mismatched={"A": ("1", "2"), "B": ("1", "2"), "C": ("1", "2")})
    r2 = _result(mismatched={"A": ("1", "3")})
    report = dominance_diff([r1, r2], env_names=["e1", "e2"])
    counts = [e.dominated_count for e in report.entries]
    assert counts == sorted(counts, reverse=True)


def test_no_contested_keys_gives_zero_ratio():
    r = _result(matching={"SAFE": "value"})
    report = dominance_diff([r], env_names=["prod"])
    assert report.total_contested_keys == 0
    for entry in report.entries:
        assert entry.dominance_ratio == 0.0
