import pytest
from envdiff.differ_timeline import build_timeline, TimelineEntry, TimelineReport


def _snap(*pairs):
    return dict(pairs)


def test_empty_snapshots_returns_empty_report():
    report = build_timeline([])
    assert isinstance(report, TimelineReport)
    assert report.entries == []
    assert report.labels == []


def test_single_snapshot_all_stable():
    report = build_timeline([_snap(("KEY", "val"))], labels=["v1"])
    assert len(report.entries) == 1
    assert not report.entries[0].changed()


def test_stable_key_detected():
    snaps = [_snap(("A", "1")), _snap(("A", "1")), _snap(("A", "1"))]
    report = build_timeline(snaps)
    assert len(report.stable_keys()) == 1
    assert len(report.changed_keys()) == 0


def test_changed_key_detected():
    snaps = [_snap(("A", "1")), _snap(("A", "2"))]
    report = build_timeline(snaps)
    assert len(report.changed_keys()) == 1
    assert report.changed_keys()[0].key == "A"


def test_absent_key_counts_as_changed():
    snaps = [_snap(("A", "1")), {}]
    report = build_timeline(snaps)
    assert report.entries[0].changed()


def test_labels_assigned_correctly():
    snaps = [_snap(("X", "a")), _snap(("X", "b"))]
    report = build_timeline(snaps, labels=["prod", "staging"])
    assert report.labels == ["prod", "staging"]


def test_labels_fallback_to_indices_when_mismatched():
    snaps = [_snap(("X", "a")), _snap(("X", "b"))]
    report = build_timeline(snaps, labels=["only-one"])
    assert report.labels == ["0", "1"]


def test_key_order_preserved():
    snaps = [_snap(("B", "1"), ("A", "2")), _snap(("B", "1"), ("A", "2"))]
    report = build_timeline(snaps)
    assert [e.key for e in report.entries] == ["B", "A"]


def test_as_dict_contains_expected_keys():
    snaps = [_snap(("K", "v1")), _snap(("K", "v2"))]
    report = build_timeline(snaps, labels=["a", "b"])
    d = report.as_dict()
    assert "labels" in d
    assert "entries" in d
    assert d["entries"][0]["changed"] is True


def test_values_list_length_matches_snapshots():
    snaps = [_snap(("K", "1")), _snap(("K", "2")), _snap(("K", "3"))]
    report = build_timeline(snaps)
    assert len(report.entries[0].values) == 3
