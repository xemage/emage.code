"""Structural scoring — T453's third retrieval signal.

Boosts based on T452's enrichment metadata (`symbol`, `parents`, `path`,
`language`, `tags` — indexing-pipeline-v1.md §2.1), rather than free-text
similarity. This is what lets an exact symbol/file-name match outrank a
chunk that only "reads similarly" to the query — see
`docs/artifacts/hybrid-retrieval-v1.md` "Fusion strategy" for the worked
example this signal is designed to produce.
"""
from __future__ import annotations

from implementation.runtime.memory.lexical import tokenize

# A query naming a chunk's own `symbol` exactly is the strongest, most
# specific enrichment-field signal available; enclosing-scope (`parents`),
# file path, and language/tag matches are progressively weaker corroborating
# signals. Contributions are additive, capped at 1.0.
_SYMBOL_BOOST = 1.0
_PARENT_BOOST = 0.6
_PATH_BOOST = 0.5
_LANGUAGE_TAG_BOOST = 0.3


def score_structural(chunk: dict, query_text: str) -> float:
    """Score in `[0, 1]` from `chunk`'s enrichment metadata vs. `query_text`.

    Convenience wrapper that tokenizes `query_text` fresh each call (used by
    tests and any one-off caller). `retrieve.Retriever` tokenizes the query
    exactly once per `.search()` call and passes the resulting term set to
    `score_structural_terms` for every candidate, instead of re-tokenizing
    the same short query string once per candidate.
    """
    return score_structural_terms(chunk, set(tokenize(query_text)))


def score_structural_terms(chunk: dict, terms: set[str]) -> float:
    if not terms:
        return 0.0
    score = 0.0
    score += _SYMBOL_BOOST if _matches(chunk.get("symbol"), terms) else 0.0
    score += _PARENT_BOOST if _any_matches(chunk.get("parents"), terms) else 0.0
    score += _PATH_BOOST if _matches(_path_stem(chunk.get("path")), terms) else 0.0
    score += _LANGUAGE_TAG_BOOST if _language_or_tag_match(chunk, terms) else 0.0
    return min(score, 1.0)


def _matches(value: str | None, terms: set[str]) -> bool:
    if not value:
        return False
    return bool(set(tokenize(str(value))) & terms)


def _any_matches(values, terms: set[str]) -> bool:
    return any(_matches(v, terms) for v in values or [])


def _path_stem(path: str | None) -> str:
    if not path:
        return ""
    return path.rsplit("/", 1)[-1].rsplit(".", 1)[0]


def _language_or_tag_match(chunk: dict, terms: set[str]) -> bool:
    language = chunk.get("language")
    if language and language.lower() in terms:
        return True
    return _any_matches(chunk.get("tags"), terms)
