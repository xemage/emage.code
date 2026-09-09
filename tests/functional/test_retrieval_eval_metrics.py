"""T455 — retrieval eval sub-suite: metric-correctness + labeled-dataset-validity tests.

Runs in this repo's default, dependency-light tier (no `fastembed`/`tree-sitter` needed —
`tests/eval/memory_retrieval/metrics.py` has no retriever/embedder dependency at all).
Proves Expected Output #5 ("tests wired into `python3 tests/run.py` ... proving the eval
code itself is correct") with planted, known relevance data: a query with a known planted
relevant chunk scores it correctly, a query with no relevant match in the top-k correctly
reports zero recall / full irrelevant-rate contribution, etc.

`tests/performance/test_retrieval_eval_scorecard.py` (opt-in, real embeddings) is the
sibling test that runs this same metrics module against a real `ContextRetriever` — this
file only proves the metrics/dataset *logic* itself, independent of any real retrieval.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.eval.memory_retrieval import labeled_dataset as ld  # noqa: E402
from tests.eval.memory_retrieval import metrics  # noqa: E402


class PrecisionAtKTests(unittest.TestCase):
    def test_all_top_k_relevant_is_perfect_precision(self):
        self.assertEqual(metrics.precision_at_k(["a", "b"], frozenset({"a", "b", "c"}), k=2), 1.0)

    def test_none_relevant_is_zero_precision(self):
        self.assertEqual(metrics.precision_at_k(["x", "y"], frozenset({"a"}), k=2), 0.0)

    def test_partial_overlap(self):
        self.assertEqual(metrics.precision_at_k(["a", "x", "b", "y"], frozenset({"a", "b"}), k=4), 0.5)

    def test_empty_retrieved_is_zero_not_a_division_error(self):
        self.assertEqual(metrics.precision_at_k([], frozenset({"a"}), k=5), 0.0)

    def test_k_smaller_than_retrieved_list_only_considers_top_k(self):
        self.assertEqual(metrics.precision_at_k(["a", "x", "x", "x"], frozenset({"a"}), k=1), 1.0)


class RecallAtKTests(unittest.TestCase):
    def test_known_planted_relevant_chunk_is_found(self):
        """A query with a known, planted relevant chunk actually scores it correctly
        (Expected Output #5's own named example)."""
        self.assertEqual(metrics.recall_at_k(["a", "b", "c"], frozenset({"b"}), k=3), 1.0)

    def test_relevant_chunk_outside_top_k_is_zero_recall(self):
        self.assertEqual(metrics.recall_at_k(["x", "y", "z"], frozenset({"b"}), k=3), 0.0)

    def test_only_some_relevant_ids_found_gives_partial_recall(self):
        self.assertEqual(metrics.recall_at_k(["a", "x"], frozenset({"a", "b"}), k=2), 0.5)

    def test_empty_relevant_ids_raises(self):
        with self.assertRaises(ValueError):
            metrics.recall_at_k(["a"], frozenset(), k=5)


class IrrelevantContextRateTests(unittest.TestCase):
    def test_no_relevant_match_is_full_irrelevant_rate(self):
        """A query with no relevant match correctly reports zero recall contribution
        and full irrelevant-context rate (Expected Output #5's second named example)."""
        retrieved = ["x", "y", "z"]
        relevant = frozenset({"only-relevant-not-retrieved"})
        self.assertEqual(metrics.recall_at_k(retrieved, relevant, k=3), 0.0)
        self.assertEqual(metrics.irrelevant_context_rate(retrieved, relevant, k=3), 1.0)

    def test_all_relevant_is_zero_irrelevant_rate(self):
        self.assertEqual(metrics.irrelevant_context_rate(["a", "b"], frozenset({"a", "b"}), k=2), 0.0)

    def test_irrelevant_rate_is_one_minus_precision(self):
        retrieved, relevant, k = ["a", "x", "b", "y", "z"], frozenset({"a", "b"}), 5
        precision = metrics.precision_at_k(retrieved, relevant, k)
        irrelevant = metrics.irrelevant_context_rate(retrieved, relevant, k)
        self.assertAlmostEqual(precision + irrelevant, 1.0)

    def test_empty_retrieved_is_zero_not_a_division_error(self):
        self.assertEqual(metrics.irrelevant_context_rate([], frozenset({"a"}), k=5), 0.0)


class ScoreQueryAndAggregateTests(unittest.TestCase):
    def test_score_query_bundles_all_three_metrics(self):
        score = metrics.score_query("q", ["a", "x"], frozenset({"a", "b"}), k=2)
        self.assertEqual(score.precision_at_k, 0.5)
        self.assertEqual(score.recall_at_k, 0.5)
        self.assertEqual(score.irrelevant_rate_at_k, 0.5)
        self.assertEqual(score.retrieved_count, 2)

    def test_aggregate_reports_mean_and_does_not_hide_a_bad_tail(self):
        """Distribution, not just a mean that could hide a bad tail (this task's own
        Objective section) — one perfect query and one zero-precision query must show
        up as min=0.0/max=1.0, not just an averaged-away mean=0.5."""
        good = metrics.score_query("good", ["a"], frozenset({"a"}), k=1)
        bad = metrics.score_query("bad", ["x"], frozenset({"a"}), k=1)
        agg = metrics.aggregate_query_scores([good, bad])
        self.assertEqual(agg["num_queries"], 2)
        self.assertEqual(agg["precision_at_k"]["mean"], 0.5)
        self.assertEqual(agg["precision_at_k"]["min"], 0.0)
        self.assertEqual(agg["precision_at_k"]["max"], 1.0)

    def test_aggregate_requires_at_least_one_score(self):
        with self.assertRaises(ValueError):
            metrics.aggregate_query_scores([])


class SummarizeLatenciesTests(unittest.TestCase):
    def test_p50_p95_p99_max_over_known_values(self):
        durations = [float(x) for x in range(1, 101)]  # 1..100
        report = metrics.summarize_latencies_ms(durations)
        self.assertEqual(report["p50"], 50.5)
        self.assertEqual(report["p95"], 96.0)
        self.assertEqual(report["max"], 100.0)

    def test_single_value(self):
        report = metrics.summarize_latencies_ms([42.0])
        self.assertEqual(report, {"p50": 42.0, "p95": 42.0, "p99": 42.0, "max": 42.0})

    def test_empty_list_raises(self):
        with self.assertRaises(ValueError):
            metrics.summarize_latencies_ms([])


class LabeledDatasetValidityTests(unittest.TestCase):
    """The labeled query set's own internal consistency — every query's relevant_ids
    must reference a real corpus entry, ids must be unique, and every query must have
    at least one relevant id (metrics.recall_at_k's own precondition)."""

    def test_topic_and_decoy_ids_are_unique(self):
        all_ids = [entry["id"] for entry in (*ld.TOPICS, *ld.DECOYS)]
        self.assertEqual(len(all_ids), len(set(all_ids)), "duplicate corpus entry id found")

    def test_every_query_has_at_least_one_relevant_id(self):
        for query in ld.QUERIES:
            self.assertTrue(query["relevant_ids"], msg=f"no relevant_ids for: {query['query_text']!r}")

    def test_every_query_relevant_id_references_a_real_corpus_entry(self):
        known_ids = ld.all_entry_ids()
        for query in ld.QUERIES:
            for rid in query["relevant_ids"]:
                self.assertIn(rid, known_ids,
                               msg=f"query {query['query_text']!r} references unknown id {rid!r}")

    def test_at_least_one_decoy_is_never_the_relevant_answer_to_any_query(self):
        """Decoys exist to make irrelevant-context rate meaningful — sanity-check that
        no decoy accidentally became a query's own labeled-relevant answer."""
        decoy_ids = {entry["id"] for entry in ld.DECOYS}
        referenced = {rid for query in ld.QUERIES for rid in query["relevant_ids"]}
        self.assertTrue(decoy_ids.isdisjoint(referenced))

    def test_queries_and_corpus_are_non_trivially_sized(self):
        self.assertGreaterEqual(len(ld.TOPICS) + len(ld.DECOYS), 20)
        self.assertGreaterEqual(len(ld.QUERIES), 20)


if __name__ == "__main__":
    unittest.main()
