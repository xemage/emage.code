"""T455 — retrieval eval sub-suite: real, end-to-end scorecard run.

Measures precision@k, recall@k, irrelevant-context rate, and p95 latency of the real
`ContextRetriever.query()` surface (`implementation/runtime/memory/context_retriever.py`,
T454) against T455's own labeled corpus/query set (`tests/eval/memory_retrieval/
labeled_dataset.py`), then writes the published scorecard artifacts
(`tests/eval/memory_retrieval/scorecard-v1.json`/`.md`) — the artifact
`docs/artifacts/retrieval-eval-v1.md` reports on.

Gated behind the optional embedding dependency and an explicit opt-in env var, mirroring
`tests/performance/test_hybrid_retrieval_latency.py` exactly: this test downloads/uses a
real local embedding model (no network egress once the model cache is warm — see
`hybrid-retrieval-v1.md` §6) and must not run in `python3 tests/run.py`'s default
(stdlib+PyYAML-only) invocation. No fenced code blocks appear anywhere in this corpus
(`labeled_dataset.py`'s own docstring), so unlike the T453 latency benchmark this test
needs only `fastembed`, not `tree-sitter`.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.eval.memory_retrieval import labeled_dataset as ld  # noqa: E402
from tests.eval.memory_retrieval import metrics  # noqa: E402

_OPT_IN = "EMAGE_MEMORY_RETRIEVAL_EVAL"
_PLATFORM = "claude-code"
_SCORECARD_JSON = REPO_ROOT / "tests" / "eval" / "memory_retrieval" / "scorecard-v1.json"
_SCORECARD_MD = REPO_ROOT / "tests" / "eval" / "memory_retrieval" / "scorecard-v1.md"


def _deps_available() -> bool:
    try:
        import fastembed  # noqa: F401
    except ImportError:
        return False
    return True


@unittest.skipUnless(_deps_available(), "fastembed not installed — see requirements.txt")
@unittest.skipUnless(
    os.environ.get(_OPT_IN) == "1",
    f"set {_OPT_IN}=1 to run T455's real-embedding retrieval-quality scorecard",
)
class RetrievalEvalScorecardTests(unittest.TestCase):
    """The real, end-to-end scorecard run — real index, real embeddings, real
    `ContextRetriever.query()` calls, against the labeled query set."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        tmp_root = Path(cls._tmp.name)
        cls.workspace, cls.platform_root, cls.index_dir = _build_fixture_tree(tmp_root)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_precision_recall_irrelevant_rate_and_latency(self) -> None:
        from implementation.runtime.memory.context_retriever import ContextRetriever
        from implementation.runtime.memory.retrieve import MemoryIndex

        retriever = ContextRetriever(self.index_dir)
        index = MemoryIndex.load(self.index_dir)
        path_to_chunk_id = _path_to_chunk_id_map(index)

        scores, durations_ms = _run_labeled_queries(retriever, self.workspace,
                                                      self.platform_root, path_to_chunk_id)

        report = {
            "k": ld.DEFAULT_K,
            "aggregate": metrics.aggregate_query_scores(scores),
            "latency_ms": metrics.summarize_latencies_ms(durations_ms),
            "per_query": [_score_to_dict(s) for s in scores],
        }
        _write_scorecard(report)
        _assert_report_is_well_formed(self, report)


def _build_fixture_tree(tmp_root: Path) -> tuple[Path, Path, Path]:
    """Real corpus -> real T452 build_index -> real on-disk index, plus a real temp
    workspace (git remote) and platform root (`.generated-manifest.json`) — the same
    `ContextRetriever.query()` inputs a real caller would supply."""
    from implementation.runtime.memory.build import BuildConfig, build_index
    from implementation.runtime.memory.index_writer import write_index

    corpus_root = ld.generate_labeled_corpus(tmp_root / "corpus")
    output_dir = tmp_root / "index"
    config = BuildConfig(project_id=ld.PROJECT_ID, own_repo_root=corpus_root,
                          general_repo_root=corpus_root, output_dir=output_dir)
    result = build_index(config)
    write_index(output_dir, result.chunks, result.rejections, result.manifest)

    workspace = tmp_root / "workspace"
    _init_git_repo(workspace, f"git@gitlab.com:{ld.PROJECT_ID}.git")
    platform_root = tmp_root / ".claude"
    _write_generated_manifest(platform_root, _PLATFORM)
    return workspace, platform_root, output_dir


def _path_to_chunk_id_map(index) -> dict[str, str]:
    """Ground truth is authored in terms of corpus topic ids (`labeled_dataset.py`), not
    internal chunk ids — resolve each topic file's real assigned `chunk_id` from the built
    index by matching on its known, deterministic vault path (one prose chunk per file,
    per `labeled_dataset.py`'s own corpus design)."""
    mapping: dict[str, str] = {}
    for chunk in index.chunks:
        for entry_id in ld.all_entry_ids():
            if chunk["path"].endswith(f"/{entry_id}.md"):
                mapping[entry_id] = chunk["chunk_id"]
    missing = ld.all_entry_ids() - mapping.keys()
    if missing:
        raise AssertionError(f"corpus entries missing from built index: {sorted(missing)}")
    return mapping


def _run_labeled_queries(retriever, workspace: Path, platform_root: Path,
                          path_to_chunk_id: dict[str, str]) -> tuple[list, list[float]]:
    scores = []
    durations_ms = []
    retriever.query(ld.QUERIES[0]["query_text"], workspace, platform_root,
                     top_k=ld.DEFAULT_K)  # warm-up, excluded from latency measurement
    for query in ld.QUERIES:
        relevant = frozenset(path_to_chunk_id[rid] for rid in query["relevant_ids"])
        start = time.perf_counter()
        results = retriever.query(query["query_text"], workspace, platform_root, top_k=ld.DEFAULT_K)
        durations_ms.append((time.perf_counter() - start) * 1000)
        retrieved_ids = [r["chunk_id"] for r in results]
        scores.append(metrics.score_query(query["query_text"], retrieved_ids, relevant, ld.DEFAULT_K))
    return scores, durations_ms


def _score_to_dict(score: metrics.QueryScore) -> dict:
    return {
        "query_text": score.query_text,
        "precision_at_k": score.precision_at_k,
        "recall_at_k": score.recall_at_k,
        "irrelevant_rate_at_k": score.irrelevant_rate_at_k,
    }


def _assert_report_is_well_formed(test: unittest.TestCase, report: dict) -> None:
    """Sanity bounds only — this test does NOT assert a retrieval-quality threshold.
    Per this task's own Blocker Protocol, a genuinely poor result is not a failure
    condition for this test; it is reported plainly in the published scorecard/
    `retrieval-eval-v1.md` with an explicit recommendation instead."""
    for metric_name in ("precision_at_k", "recall_at_k", "irrelevant_rate_at_k"):
        for stat in ("mean", "median", "min", "max"):
            value = report["aggregate"][metric_name][stat]
            test.assertGreaterEqual(value, 0.0)
            test.assertLessEqual(value, 1.0)
    test.assertGreater(report["latency_ms"]["p95"], 0.0)
    test.assertEqual(len(report["per_query"]), len(ld.QUERIES))


def _write_scorecard(report: dict) -> None:
    _SCORECARD_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    _SCORECARD_MD.write_text(_render_markdown(report), encoding="utf-8")


def _render_markdown(report: dict) -> str:
    agg = report["aggregate"]
    lat = report["latency_ms"]
    lines = [
        "# T455 Retrieval Eval Scorecard — v1",
        "",
        f"k = {report['k']}, {agg['num_queries']} labeled queries, real "
        "`ContextRetriever.query()` calls against a real built index (real "
        "`nomic-embed-text-v1.5` embeddings, no FakeEmbedder).",
        "",
        "| Metric | Mean | Median | Min | Max |",
        "|---|---|---|---|---|",
    ]
    for name, key in (("Precision@k", "precision_at_k"), ("Recall@k", "recall_at_k"),
                       ("Irrelevant-context rate@k", "irrelevant_rate_at_k")):
        d = agg[key]
        lines.append(f"| {name} | {d['mean']:.3f} | {d['median']:.3f} | {d['min']:.3f} | {d['max']:.3f} |")
    lines += [
        "",
        "| Latency | p50 | p95 | p99 | max |",
        "|---|---|---|---|---|",
        f"| ms | {lat['p50']:.1f} | {lat['p95']:.1f} | {lat['p99']:.1f} | {lat['max']:.1f} |",
        "",
        "See `docs/artifacts/retrieval-eval-v1.md` for methodology and interpretation.",
    ]
    return "\n".join(lines) + "\n"


def _init_git_repo(dest_dir: Path, remote_url: str) -> None:
    import subprocess
    dest_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=str(dest_dir), check=True, capture_output=True)
    subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=str(dest_dir),
                    check=True, capture_output=True)


def _write_generated_manifest(platform_root: Path, platform: str) -> None:
    platform_root.mkdir(parents=True, exist_ok=True)
    (platform_root / ".generated-manifest.json").write_text(
        json.dumps({"generatedFrom": "knowledge/", "platform": platform,
                    "generatedAt": "<deterministic>", "files": []}, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
