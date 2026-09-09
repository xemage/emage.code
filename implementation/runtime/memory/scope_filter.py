"""Query-time scope pre-filter — T453, `memory-scope-model-v1.md` §4.2.

Defense in depth: applies the same `include(entry, P)` predicate T452 applies
*structurally* at build time (§4.1, `build.py::_is_includable`), independently,
at query time, against the `scope`/`project_id`/`shared_consumers` metadata
T452 persists on every chunk (§2.1 of `indexing-pipeline-v1.md`). This filter
must run even if T452's own build-time guarantee were somehow bypassed (e.g. a
hand-assembled/merged index) — see `docs/artifacts/hybrid-retrieval-v1.md`
"Query-time filter" for the adversarial test that proves this independence.

No caller may skip this: `RequestingContext` is a required, non-defaultable
argument everywhere it is consumed (`retrieve.query`). There is no query mode
that omits it.
"""
from __future__ import annotations

from dataclasses import dataclass

_WILDCARD = "*"


@dataclass(frozen=True)
class RequestingContext:
    """Trusted, non-user-editable session identity (§4.2).

    Derived from the calling session's own workspace/platform identity —
    never from query text or other free-form user input (§4.2, §9 point 2).
    """

    project_id: str
    platform: str

    def __post_init__(self) -> None:
        if not self.project_id or not self.platform:
            raise ValueError("RequestingContext requires non-empty project_id and platform")


def is_visible(chunk: dict, context: RequestingContext) -> bool:
    """The `include(chunk_metadata, requesting_context)` predicate (§4.2).

    Same branch structure as T452's build-time `include(entry, P)` (§4.1):
    `general` always visible, `project` visible only to its own project,
    `shared` visible only to explicitly named consumers. Unknown/malformed
    `scope` values deny by default (never reached in a T452-built index,
    since §5 rejects those at build time — but a defense-in-depth filter
    must not assume its only input is a well-formed index).
    """
    scope = chunk.get("scope")
    if scope == "general":
        return True
    if scope == "project":
        return chunk.get("project_id") == context.project_id
    if scope == "shared":
        return _shared_visible(chunk.get("shared_consumers"), context)
    return False


def _shared_visible(shared_consumers: dict | None, context: RequestingContext) -> bool:
    """`shared_consumers.projects`/`.platforms` allowlist match, or `["*"]`.

    §4.1's own predicate only names the `projects` allowlist (it has no
    platform identity at build time); this query-time filter also checks
    `platforms`, since `requesting_context` carries that dimension and
    §3's frontmatter schema defines `shared_consumers.platforms` as a
    REQUIRED, individually-enforced sub-field precisely so it has a
    consumer — see `hybrid-retrieval-v1.md` "Query-time filter" for this
    documented extension of §4.1's literal predicate.
    """
    if not shared_consumers:
        return False
    projects = shared_consumers.get("projects") or []
    platforms = shared_consumers.get("platforms") or []
    project_ok = context.project_id in projects or projects == [_WILDCARD]
    platform_ok = context.platform in platforms or platforms == [_WILDCARD]
    return project_ok and platform_ok


def filter_candidates(chunks: list[dict], context: RequestingContext) -> list[dict]:
    """Mandatory pre-filter — must run BEFORE any ranking signal is computed
    (see `retrieve.query`'s call order). Removes excluded chunks from the
    candidate pool entirely, so they can never resurface via a later
    ranking-stage bug or a top-K spillover (§4.2's own reasoning for why
    this is a pre-filter, not a post-filter).
    """
    return [chunks[i] for i in filter_indices(chunks, context)]


def filter_indices(chunks: list[dict], context: RequestingContext) -> list[int]:
    """Same predicate as `filter_candidates`, returning positions into
    `chunks` rather than copies of the chunk dicts — lets a caller (e.g.
    `retrieve.Retriever`) gather from other per-chunk-precomputed,
    index-aligned structures (a vector matrix, cached token bags) without
    an extra chunk-identity lookup, while still applying the identical
    filter-before-rank predicate.
    """
    return [i for i, chunk in enumerate(chunks) if is_visible(chunk, context)]
