"""Build a dependency/co-occurrence graph from multiple diff results."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Dict, List, Set
from envdiff.comparator import DiffResult


@dataclass
class GraphNode:
    key: str
    frequency: int  # how many results this key appears in
    statuses: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"GraphNode({self.key!r}, freq={self.frequency})"

    def as_dict(self) -> dict:
        return {"key": self.key, "frequency": self.frequency, "statuses": self.statuses}


@dataclass
class GraphEdge:
    key_a: str
    key_b: str
    co_occurrences: int  # results where both keys appear with a diff

    def __repr__(self) -> str:
        return f"GraphEdge({self.key_a!r} -- {self.key_b!r}, co={self.co_occurrences})"

    def as_dict(self) -> dict:
        return {"key_a": self.key_a, "key_b": self.key_b, "co_occurrences": self.co_occurrences}


@dataclass
class GraphReport:
    nodes: List[GraphNode]
    edges: List[GraphEdge]

    def as_dict(self) -> dict:
        return {
            "nodes": [n.as_dict() for n in self.nodes],
            "edges": [e.as_dict() for e in self.edges],
        }


def _diff_keys(result: DiffResult) -> Set[str]:
    return set(result.only_in_a) | set(result.only_in_b) | set(result.mismatched)


def build_graph(results: List[DiffResult]) -> GraphReport:
    freq: Dict[str, int] = defaultdict(int)
    statuses: Dict[str, List[str]] = defaultdict(list)
    co: Dict[tuple, int] = defaultdict(int)

    for r in results:
        keys = _diff_keys(r)
        for k in keys:
            freq[k] += 1
            if k in r.only_in_a:
                statuses[k].append("missing_in_b")
            elif k in r.only_in_b:
                statuses[k].append("missing_in_a")
            else:
                statuses[k].append("mismatched")
        key_list = sorted(keys)
        for i, ka in enumerate(key_list):
            for kb in key_list[i + 1:]:
                co[(ka, kb)] += 1

    nodes = [GraphNode(k, freq[k], statuses[k]) for k in sorted(freq)]
    edges = [GraphEdge(ka, kb, c) for (ka, kb), c in sorted(co.items())]
    return GraphReport(nodes=nodes, edges=edges)
