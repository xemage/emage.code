"""Signal fusion — T453.

Weighted linear combination of the semantic (`embed.py` + cosine similarity),
lexical (`lexical.py`, BM25), and structural (`structural.py`, enrichment-
metadata boosts) scores into one ranking score. See
`docs/artifacts/hybrid-retrieval-v1.md` "Fusion strategy" for why weighted
linear combination was chosen over reciprocal rank fusion or a learned
re-ranker, and for how the default weights below were picked.
"""
from __future__ import annotations

from dataclasses import dataclass

# Semantic similarity is the primary signal (captures paraphrase/meaning,
# which BM25/structural matching cannot), lexical is a strong secondary
# signal for exact-term/identifier queries, structural is the smallest but
# most precise signal (only fires on an exact enrichment-field match).
DEFAULT_SEMANTIC_WEIGHT = 0.45
DEFAULT_LEXICAL_WEIGHT = 0.35
DEFAULT_STRUCTURAL_WEIGHT = 0.20


@dataclass(frozen=True)
class RankWeights:
    semantic: float = DEFAULT_SEMANTIC_WEIGHT
    lexical: float = DEFAULT_LEXICAL_WEIGHT
    structural: float = DEFAULT_STRUCTURAL_WEIGHT


def fuse_scores(semantic: float, lexical: float, structural: float, weights: RankWeights) -> float:
    """Combine the three per-candidate signals into one fused score.

    `semantic` is cosine similarity of two unit-length vectors (`embed.py`
    guarantees L2-unit normalization), so it is already in `[-1, 1]`;
    clipped to `[0, 1]` here since a negative cosine similarity is not a
    positive retrieval signal and would otherwise let a very lexically/
    structurally strong but semantically opposed chunk score unnaturally
    low. `lexical`/`structural` are already normalized to `[0, 1]` by their
    own scoring functions.
    """
    semantic_clipped = max(0.0, semantic)
    return (
        weights.semantic * semantic_clipped
        + weights.lexical * lexical
        + weights.structural * structural
    )
