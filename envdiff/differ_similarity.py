"""Compute pairwise similarity scores across multiple env file comparisons."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from envdiff.comparator import DiffResult
from envdiff.scorer import score_diff, DiffScore


@dataclass
class PairSimilarity:
    label_a: str
    label_b: str
    score: DiffScore

    def __repr__(self) -> str:
        return f"<PairSimilarity {self.label_a}↔{self.label_b} {self.score.similarity:.2f}>"

    def as_dict(self) -> dict:
        return {
            "label_a": self.label_a,
            "label_b": self.label_b,
            "similarity": self.score.similarity,
            "grade": self.score.grade,
            "matching": self.score.matching,
            "total": self.score.total,
        }


@dataclass
class SimilarityMatrix:
    pairs: List[PairSimilarity] = field(default_factory=list)

    def most_similar(self) -> PairSimilarity | None:
        if not self.pairs:
            return None
        return max(self.pairs, key=lambda p: p.score.similarity)

    def least_similar(self) -> PairSimilarity | None:
        if not self.pairs:
            return None
        return min(self.pairs, key=lambda p: p.score.similarity)

    def average_similarity(self) -> float:
        if not self.pairs:
            return 1.0
        return sum(p.score.similarity for p in self.pairs) / len(self.pairs)

    def as_dict(self) -> dict:
        return {
            "pairs": [p.as_dict() for p in self.pairs],
            "average_similarity": self.average_similarity(),
        }


def build_similarity_matrix(
    results: Dict[str, DiffResult]
) -> SimilarityMatrix:
    """Given a mapping of label -> DiffResult, compute all pairwise similarities."""
    labels = list(results.keys())
    pairs: List[PairSimilarity] = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            la, lb = labels[i], labels[j]
            # Merge the two results into a combined view for scoring
            combined = _merge_for_scoring(results[la], results[lb])
            sc = score_diff(combined)
            pairs.append(PairSimilarity(label_a=la, label_b=lb, score=sc))
    return SimilarityMatrix(pairs=pairs)


def _merge_for_scoring(a: DiffResult, b: DiffResult) -> DiffResult:
    """Combine two DiffResults so their union of differing keys is visible."""
    return DiffResult(
        only_in_a=a.only_in_a | b.only_in_a,
        only_in_b=a.only_in_b | b.only_in_b,
        mismatched={**a.mismatched, **b.mismatched},
        matching={**a.matching, **b.matching},
    )
