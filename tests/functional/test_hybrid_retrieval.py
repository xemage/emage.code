"""T453 — hybrid retrieval (semantic + lexical + structural).

Covers acceptance criteria 1 (fusion changes top result vs. pure-semantic
ranking), 2 (mandatory query-time scope filter, filter-before-rank call
order), 3 (cross-project unreachability at query time, including the
"merged index" adversarial case), 4 (shared-scope reachability via the
identical mechanism), and 6 (no network/credential needed — proven for real
in the gated `FullRetrievalPipelineTests` below, mirroring
`test_memory_indexing_pipeline.py::FullPipelineTests`'s convention).

Everything except `FullRetrievalPipelineTests` runs with no optional
dependency installed (`scope_filter.py`/`lexical.py`/`structural.py`/
`rank.py` are pure stdlib; `retrieve.py` is exercised here via a
`FakeEmbedder`, and its `_semantic_scores`/`MemoryIndex.vector_matrix`
transparently fall back to a pure-Python cosine-similarity computation when
numpy isn't installed — see `retrieve.py`'s own module docstring and
`_import_numpy` — so these tests stay in `python3 tests/run.py`'s default,
dependency-light run).
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

FIXTURES = REPO_ROOT / "tests" / "fixtures" / "memory"

from tests._helpers.memory_fixtures import materialize_git_repo  # noqa: E402


class FakeEmbedder:
    """Returns a fixed vector for any query text — deterministic, no ML
    dependency, so AC1's fusion-changes-ranking example is exact and
    reproducible without requiring `fastembed`.
    """

    def __init__(self, vector: tuple[float, ...]) -> None:
        self.vector = vector
        self.model_name = "fake-test-embedder"

    def embed_texts(self, texts: list[str]) -> list[tuple[float, ...]]:
        return [self.vector for _ in texts]


def _chunk(**overrides) -> dict:
    base = {
        "chunk_id": "fixture::chunk0",
        "text": "generic chunk body text",
        "vector": [1.0, 0.0],
        "embedding_model": "fake-test-embedder",
        "embedding_dim": 2,
        "path": "implementation/knowledge/memory/project/example.md",
        "repo_id": "fixture-org/repo",
        "commit": "deadbeef",
        "content_type": "prose",
        "language": None,
        "symbol": None,
        "ast_type": None,
        "parents": [],
        "imports": [],
        "line_range": [1, 1],
        "title": "Fixture entry",
        "tags": [],
        "scope": "project",
        "project_id": "fixture-org/repo",
        "shared_consumers": None,
    }
    base.update(overrides)
    return base


class ScopeFilterTests(unittest.TestCase):
    """Acceptance criteria 2/3/4's core predicate, in isolation."""

    def _context(self, project_id="fixture-org/repo-p2", platform="claude-code"):
        from implementation.runtime.memory.scope_filter import RequestingContext
        return RequestingContext(project_id=project_id, platform=platform)

    def test_general_always_visible(self):
        from implementation.runtime.memory.scope_filter import is_visible
        chunk = _chunk(scope="general", project_id=None)
        self.assertTrue(is_visible(chunk, self._context()))

    def test_project_scope_visible_only_to_own_project(self):
        from implementation.runtime.memory.scope_filter import is_visible
        chunk = _chunk(scope="project", project_id="fixture-org/repo-p1")
        self.assertFalse(is_visible(chunk, self._context(project_id="fixture-org/repo-p2")))
        self.assertTrue(is_visible(chunk, self._context(project_id="fixture-org/repo-p1")))

    def test_shared_scope_requires_project_and_platform_match(self):
        from implementation.runtime.memory.scope_filter import is_visible
        shared = {"projects": ["fixture-org/repo-p2"], "platforms": ["claude-code"]}
        chunk = _chunk(scope="shared", project_id=None, shared_consumers=shared)
        self.assertTrue(is_visible(chunk, self._context(project_id="fixture-org/repo-p2", platform="claude-code")))
        self.assertFalse(is_visible(chunk, self._context(project_id="fixture-org/repo-p3", platform="claude-code")))
        self.assertFalse(is_visible(chunk, self._context(project_id="fixture-org/repo-p2", platform="github")))

    def test_shared_scope_wildcards(self):
        from implementation.runtime.memory.scope_filter import is_visible
        shared = {"projects": ["*"], "platforms": ["*"]}
        chunk = _chunk(scope="shared", project_id=None, shared_consumers=shared)
        self.assertTrue(is_visible(chunk, self._context(project_id="anyone/anything", platform="cline")))

    def test_unknown_scope_denies_by_default(self):
        from implementation.runtime.memory.scope_filter import is_visible
        chunk = _chunk(scope="not-a-real-scope")
        self.assertFalse(is_visible(chunk, self._context()))

    def test_requesting_context_requires_both_fields(self):
        from implementation.runtime.memory.scope_filter import RequestingContext
        with self.assertRaises(ValueError):
            RequestingContext(project_id="", platform="claude-code")
        with self.assertRaises(ValueError):
            RequestingContext(project_id="org/repo", platform="")


class LexicalScoringTests(unittest.TestCase):
    def test_exact_term_outranks_no_overlap(self):
        from implementation.runtime.memory.lexical import score_lexical
        chunks = [
            _chunk(text="def load_config(path): return json.load(path)", symbol="load_config"),
            _chunk(text="completely unrelated prose about something else entirely"),
        ]
        scores = score_lexical(chunks, "load_config")
        self.assertGreater(scores[0], scores[1])
        self.assertEqual(scores[1], 0.0)

    def test_no_query_terms_yields_zero_scores(self):
        from implementation.runtime.memory.lexical import score_lexical
        scores = score_lexical([_chunk()], "   ")
        self.assertEqual(scores, [0.0])


class StructuralScoringTests(unittest.TestCase):
    def test_exact_symbol_match_scores_highest(self):
        from implementation.runtime.memory.structural import score_structural
        exact = _chunk(symbol="load_config")
        unrelated = _chunk(symbol="unrelated_symbol")
        self.assertGreater(score_structural(exact, "load_config"), score_structural(unrelated, "load_config"))

    def test_parent_and_path_and_tag_contribute(self):
        from implementation.runtime.memory.structural import score_structural
        chunk = _chunk(symbol=None, parents=["ConfigCache"], path="implementation/config_cache.py",
                        tags=["python"])
        self.assertGreater(score_structural(chunk, "ConfigCache python"), 0.0)


class RankFusionTests(unittest.TestCase):
    def test_negative_semantic_similarity_is_clipped(self):
        from implementation.runtime.memory.rank import RankWeights, fuse_scores
        weights = RankWeights()
        clipped = fuse_scores(-0.9, 0.0, 0.0, weights)
        self.assertEqual(clipped, 0.0)

    def test_weights_sum_to_one_by_default(self):
        from implementation.runtime.memory.rank import RankWeights
        w = RankWeights()
        self.assertAlmostEqual(w.semantic + w.lexical + w.structural, 1.0)


class MandatoryScopeFilterCallOrderTests(unittest.TestCase):
    """Acceptance criterion 2: filter runs BEFORE any ranking signal."""

    def _index(self):
        from implementation.runtime.memory.retrieve import MemoryIndex
        chunks = [_chunk(chunk_id="c1", scope="general", project_id=None)]
        return MemoryIndex(chunks, "fake-test-embedder")

    def test_search_requires_requesting_context(self):
        from implementation.runtime.memory.retrieve import Retriever
        retriever = Retriever(self._index(), embedder=FakeEmbedder((1.0, 0.0)))
        with self.assertRaises(TypeError):
            retriever.search("query text")  # no requesting_context supplied — must fail, not default

    def test_filter_runs_before_embedding_and_lexical_scoring(self):
        from implementation.runtime.memory import retrieve
        from implementation.runtime.memory.scope_filter import RequestingContext

        call_order: list[str] = []
        real_filter = retrieve.filter_indices
        real_lexical = retrieve.score_lexical_precomputed

        def spy_filter(chunks, context):
            call_order.append("filter")
            return real_filter(chunks, context)

        def spy_lexical(bags, lengths, query_text):
            call_order.append("lexical")
            return real_lexical(bags, lengths, query_text)

        embedder = FakeEmbedder((1.0, 0.0))
        real_embed = embedder.embed_texts

        def spy_embed(texts):
            call_order.append("embed")
            return real_embed(texts)

        embedder.embed_texts = spy_embed
        retriever = retrieve.Retriever(self._index(), embedder=embedder)
        context = RequestingContext(project_id="fixture-org/repo", platform="claude-code")

        with mock.patch.object(retrieve, "filter_indices", side_effect=spy_filter), \
             mock.patch.object(retrieve, "score_lexical_precomputed", side_effect=spy_lexical):
            retriever.search("query", context)

        self.assertEqual(call_order[0], "filter", call_order)
        self.assertLess(call_order.index("filter"), call_order.index("embed"))
        self.assertLess(call_order.index("filter"), call_order.index("lexical"))


class FusionChangesTopResultTests(unittest.TestCase):
    """Acceptance criterion 1, concrete worked example: a chunk that is
    lexically/structurally an exact match but only weakly semantically
    similar outranks a chunk that is strongly semantically similar but has
    no lexical/structural overlap at all, once all three signals are fused
    — demonstrating ranking is not semantic-alone.
    """

    def test_lexical_structural_signal_flips_the_top_result(self):
        from implementation.runtime.memory.retrieve import MemoryIndex, Retriever
        from implementation.runtime.memory.scope_filter import RequestingContext

        query_vector = (1.0, 0.0)
        semantic_winner = _chunk(
            chunk_id="semantic-winner",
            text="This section explains configuration loading, caching, and validation for settings.",
            symbol="explain_configuration",
            vector=[1.0, 0.0],  # cosine(query, this) == 1.0 -- perfect semantic match
        )
        lexical_structural_winner = _chunk(
            chunk_id="lexical-structural-winner",
            text="def load_config(path):\n    return json.load(open(path))",
            symbol="load_config",  # exact symbol == query text
            vector=[0.6, 0.8],  # cosine(query, this) == 0.6 -- weaker semantic match
        )
        index = MemoryIndex([semantic_winner, lexical_structural_winner], "fake-test-embedder")
        retriever = Retriever(index, embedder=FakeEmbedder(query_vector))
        context = RequestingContext(project_id="fixture-org/repo", platform="claude-code")

        results = retriever.search("load_config", context, top_k=2)

        by_semantic = sorted(results, key=lambda r: r.semantic_score, reverse=True)
        self.assertEqual(by_semantic[0].chunk["chunk_id"], "semantic-winner",
                          "sanity check: semantic_winner really is ahead on the semantic signal alone")
        self.assertEqual(results[0].chunk["chunk_id"], "lexical-structural-winner",
                          "fused ranking must promote the exact lexical/structural match over "
                          "the purely-semantic match — ranking is not semantic-alone")
        self.assertGreater(results[0].lexical_score, 0.0)
        self.assertGreater(results[0].structural_score, 0.0)


class CrossProjectUnreachabilityAtQueryTimeTests(unittest.TestCase):
    """Acceptance criterion 3, adversarial: hostile query targeting a
    foreign project-scoped chunk's exact content, including the "merged
    index" case where that chunk IS present in the candidate index (the
    query-time filter, not any ingestion-time exclusion, must be what
    blocks it here).
    """

    def test_hostile_query_against_merged_index_yields_zero_hits_for_foreign_project(self):
        from implementation.runtime.memory.retrieve import MemoryIndex, Retriever
        from implementation.runtime.memory.scope_filter import RequestingContext

        canary_text = "FIXTURE-CANARY-P1-ONLY-CONTENT-4172 secret project-only implementation detail"
        p1_secret = _chunk(
            chunk_id="p1-secret", scope="project", project_id="fixture-org/repo-p1",
            text=canary_text, symbol="p1_secret_function", vector=[1.0, 0.0],
        )
        p2_own = _chunk(
            chunk_id="p2-own", scope="project", project_id="fixture-org/repo-p2",
            text="p2's own unrelated content", symbol="p2_helper", vector=[0.0, 1.0],
        )
        # Simulate a merged/shared index: BOTH projects' chunks are present
        # in the same candidate pool T453 queries against.
        index = MemoryIndex([p1_secret, p2_own], "fake-test-embedder")
        # Hostile query: exact canary text (maximal lexical match) AND an
        # embedder tuned to return P1's own vector (maximal semantic match)
        # -- if the scope filter were not applied first, P1's secret would
        # win on every signal.
        retriever = Retriever(index, embedder=FakeEmbedder((1.0, 0.0)))
        p2_context = RequestingContext(project_id="fixture-org/repo-p2", platform="claude-code")

        results = retriever.search(canary_text, p2_context, top_k=10)

        hit_ids = {r.chunk["chunk_id"] for r in results}
        self.assertNotIn("p1-secret", hit_ids,
                          "P1's project-scoped chunk must be unreachable from a P2-context query "
                          "even when present in the candidate index and targeted by a hostile query")

    def test_shared_scope_reachable_by_named_consumer_same_mechanism(self):
        """Acceptance criterion 4 — positive outcome, identical mechanism."""
        from implementation.runtime.memory.retrieve import MemoryIndex, Retriever
        from implementation.runtime.memory.scope_filter import RequestingContext

        shared_entry = _chunk(
            chunk_id="p1-shared-for-p2", scope="shared", project_id=None,
            shared_consumers={"projects": ["fixture-org/repo-p2"], "platforms": ["claude-code"]},
            text="FIXTURE-CANARY-SHARED-P1-TO-P2-8891 reusable methodology",
            symbol="shared_methodology", vector=[1.0, 0.0],
        )
        index = MemoryIndex([shared_entry], "fake-test-embedder")
        retriever = Retriever(index, embedder=FakeEmbedder((1.0, 0.0)))

        p2_context = RequestingContext(project_id="fixture-org/repo-p2", platform="claude-code")
        p3_context = RequestingContext(project_id="fixture-org/repo-p3", platform="claude-code")

        p2_results = retriever.search("reusable methodology", p2_context, top_k=10)
        p3_results = retriever.search("reusable methodology", p3_context, top_k=10)

        self.assertIn("p1-shared-for-p2", {r.chunk["chunk_id"] for r in p2_results})
        self.assertNotIn("p1-shared-for-p2", {r.chunk["chunk_id"] for r in p3_results})


class MemoryIndexLoadTests(unittest.TestCase):
    def test_mismatched_embedding_model_is_rejected(self):
        from implementation.runtime.memory.retrieve import MemoryIndex, MismatchedEmbeddingModelError

        with tempfile.TemporaryDirectory() as tmp:
            index_dir = Path(tmp)
            chunk_a = _chunk(chunk_id="a", embedding_model="model-a")
            chunk_b = _chunk(chunk_id="b", embedding_model="model-b")
            (index_dir / "index.jsonl").write_text(
                json.dumps(chunk_a) + "\n" + json.dumps(chunk_b) + "\n", encoding="utf-8",
            )
            (index_dir / "manifest.json").write_text(json.dumps({"embedding_model": "model-a"}), encoding="utf-8")

            with self.assertRaises(MismatchedEmbeddingModelError):
                MemoryIndex.load(index_dir)


def _fastembed_and_tree_sitter_available() -> bool:
    try:
        import fastembed  # noqa: F401
        import tree_sitter  # noqa: F401
        import tree_sitter_python  # noqa: F401
    except ImportError:
        return False
    return True


_FULL_PIPELINE_OPT_IN = "EMAGE_MEMORY_FULL_PIPELINE_TEST"


@unittest.skipUnless(_fastembed_and_tree_sitter_available(), "fastembed/tree-sitter not installed")
@unittest.skipUnless(
    os.environ.get(_FULL_PIPELINE_OPT_IN) == "1",
    f"set {_FULL_PIPELINE_OPT_IN}=1 to run the real-embedding end-to-end retrieval test",
)
class FullRetrievalPipelineTests(unittest.TestCase):
    """Acceptance criteria 3/4/6 against a REAL T452-built index with real,
    non-stub embeddings — not the `FakeEmbedder` used above. Mirrors
    `test_memory_indexing_pipeline.py::FullPipelineTests`'s no-network
    demonstration, applied to the query-time (not build-time) embedding
    call this task adds.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        tmp_root = Path(cls._tmp.name)
        cls.general_root = materialize_git_repo(FIXTURES / "general-source", tmp_root / "general-source")
        cls.p1_root = materialize_git_repo(FIXTURES / "repo-p1", tmp_root / "repo-p1")
        cls.p2_root = materialize_git_repo(FIXTURES / "repo-p2", tmp_root / "repo-p2")
        cls.index_dir = tmp_root / "index"
        cls._build_p2_index_with_p1_as_shared_source()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    @classmethod
    def _build_p2_index_with_p1_as_shared_source(cls) -> None:
        from implementation.runtime.memory import scanner
        from implementation.runtime.memory.build import BuildConfig, build_index
        from implementation.runtime.memory.index_writer import write_index

        p1_as_shared_source = scanner.ScanRoot(cls.p1_root, "fixture-org/repo-p1")
        config = BuildConfig(
            project_id="fixture-org/repo-p2", own_repo_root=cls.p2_root, general_repo_root=cls.general_root,
            output_dir=cls.index_dir, shared_source_roots=(p1_as_shared_source,),
        )
        result = build_index(config)
        write_index(cls.index_dir, result.chunks, result.rejections, result.manifest)

    def test_real_embeddings_and_query_time_scope_filter_no_network(self):
        """Acceptance criterion 6 (offline, no proxy reachable) combined
        with criteria 3/4 (unreachability/reachability) against a real
        index built with P1 configured as a shared source for P2 — proving
        the query-time filter, not ingestion, is what keeps P1's
        project-scope canary out of P2's retrieval results.
        """
        from implementation.runtime.memory.retrieve import MemoryIndex, Retriever
        from implementation.runtime.memory.scope_filter import RequestingContext

        saved_env = {k: os.environ.get(k) for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy")}
        try:
            for var in saved_env:
                os.environ[var] = "http://127.0.0.1:1"  # nothing listens here
            index = MemoryIndex.load(self.index_dir)
            retriever = Retriever(index)
            context = RequestingContext(project_id="fixture-org/repo-p2", platform="claude-code")

            unreachable = retriever.search("FIXTURE-CANARY-P1-ONLY-CONTENT-4172", context, top_k=10)
            reachable = retriever.search("FIXTURE-CANARY-SHARED-P1-TO-P2-8891", context, top_k=10)
        finally:
            for key, value in saved_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        self.assertFalse(any("p1-only-secret" in r.chunk["path"] for r in unreachable))
        self.assertTrue(any("shared-for-p2" in r.chunk["path"] for r in reachable))
        self.assertGreater(reachable[0].semantic_score, 0.0, "must be a real, non-stub similarity score")


if __name__ == "__main__":
    unittest.main()
