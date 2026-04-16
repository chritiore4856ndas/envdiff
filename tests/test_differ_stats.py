"""Tests for envdiff.differ_stats."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.differ_stats import KeyStats, StatsResult, compute_stats, format_stats


@pytest.fixture
def results():
    return [
        DiffResult(
            only_in_a={"DB_HOST", "SECRET"},
            only_in_b={"NEW_KEY"},
            mismatched={"PORT"},
        ),
        DiffResult(
            only_in_a={"DB_HOST"},
            only_in_b=set(),
            mismatched={"PORT"},
        ),
    ]


def test_empty_results_gives_empty_stats():
    result = compute_stats([])
    assert result.key_stats == {}
    assert result.total_issues == 0


def test_missing_in_b_counted(results):
    stats = compute_stats(results)
    assert stats.key_stats["DB_HOST"].times_missing_in_b == 2


def test_missing_in_a_counted(results):
    stats = compute_stats(results)
    assert stats.key_stats["NEW_KEY"].times_missing_in_a == 1


def test_mismatched_counted(results):
    stats = compute_stats(results)
    assert stats.key_stats["PORT"].times_mismatched == 2


def test_total_issues_sums_all(results):
    stats = compute_stats(results)
    # DB_HOST: 2, SECRET: 1, NEW_KEY: 1, PORT: 2 => 6
    assert stats.total_issues == 6


def test_most_problematic_ordered(results):
    stats = compute_stats(results)
    top = stats.most_problematic(2)
    assert top[0].total_issues >= top[1].total_issues


def test_most_problematic_respects_n(results):
    stats = compute_stats(results)
    assert len(stats.most_problematic(2)) == 2


def test_format_stats_empty():
    stats = StatsResult()
    assert format_stats(stats) == "No issues recorded."


def test_format_stats_contains_key(results):
    stats = compute_stats(results)
    output = format_stats(stats)
    assert "DB_HOST" in output
    assert "Total issues" in output
