"""T453 — hybrid retrieval latency benchmark.

Acceptance criterion 5: `<500ms` p95 retrieval on a 100K LOC (or larger)
repo, MEASURED not asserted. See `docs/artifacts/hybrid-retrieval-v1.md`
"Latency benchmark methodology and results" for the full write-up (corpus
size, query set, raw numbers) this test reproduces.

Gated behind the optional embedding dependency and an explicit opt-in env
var, mirroring `test_memory_indexing_pipeline.py::FullPipelineTests` — this
test builds a real ~100K-LOC synthetic index (a multi-minute one-time cost)
and downloads/uses a real local embedding model, so it must not run in
`python3 tests/run.py`'s default (stdlib+PyYAML-only) invocation.
"""
from __future__ import annotations

import os
import statistics
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests._helpers.synthetic_memory_corpus import estimate_total_loc, generate_synthetic_corpus  # noqa: E402

_OPT_IN = "EMAGE_MEMORY_RETRIEVAL_LATENCY_TEST"
_PROJECT_ID = "fixture-org/benchmark-repo"
_NUM_MODULES = 50
_FUNCTIONS_PER_MODULE = 260
_P95_BUDGET_MS = 500.0

_QUERY_SET = [
    "load_config helper function",
    "module_12_function_45",
    "how does value validation work for negative results",
    "checksum computation for module 30",
    "module_3_function_100 transform",
    "raise ValueError negative result",
    "synthetic benchmark module 7",
    "module_45_function_200",
    "helper that multiplies value and validates it",
    "os and json imports at top of module",
    "function that processes value and returns processed",
    "module_0_function_0",
]


def _deps_available() -> bool:
    try:
        import fastembed  # noqa: F401
        import tree_sitter  # noqa: F401
        import tree_sitter_python  # noqa: F401
    except ImportError:
        return False
    return True


@unittest.skipUnless(_deps_available(), "fastembed/tree-sitter not installed — see requirements.txt")
@unittest.skipUnless(
    os.environ.get(_OPT_IN) == "1",
    f"set {_OPT_IN}=1 to run the ~100K-LOC retrieval latency benchmark "
    "(builds a real index; multi-minute one-time cost)",
)
class RetrievalLatencyTests(unittest.TestCase):
    """Acceptance criterion 5, measured directly against a real index."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        tmp_root = Path(cls._tmp.name)
        corpus_root = generate_synthetic_corpus(
            tmp_root / "corpus", _PROJECT_ID, _NUM_MODULES, _FUNCTIONS_PER_MODULE,
        )
        cls.total_loc = estimate_total_loc(_NUM_MODULES, _FUNCTIONS_PER_MODULE)
        cls.index, cls.chunk_count, cls.build_seconds = _build_index(corpus_root, tmp_root / "index")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_p95_latency_under_budget(self) -> None:
        from implementation.runtime.memory.retrieve import Retriever
        from implementation.runtime.memory.scope_filter import RequestingContext

        retriever = Retriever(self.index)  # loads LocalEmbedder once, outside the timed loop
        context = RequestingContext(project_id=_PROJECT_ID, platform="claude-code")
        durations_ms = _time_queries(retriever, context)

        report = _summarize(durations_ms)
        print(
            f"\n[T453 latency benchmark] corpus: {self.total_loc} LOC, "
            f"{self.chunk_count} chunks, build {self.build_seconds:.1f}s\n"
            f"[T453 latency benchmark] queries: {len(durations_ms)}, "
            f"p50={report['p50']:.1f}ms p95={report['p95']:.1f}ms "
            f"p99={report['p99']:.1f}ms max={report['max']:.1f}ms"
        )
        self.assertGreaterEqual(self.total_loc, 100_000, "corpus must be >=100K LOC per acceptance criterion 5")
        self.assertLessEqual(
            report["p95"], _P95_BUDGET_MS,
            f"p95 latency {report['p95']:.1f}ms exceeds the {_P95_BUDGET_MS}ms budget "
            f"(ADR-005 Validation section) — real measured number, not adjusted to pass",
        )


def _build_index(corpus_root: Path, output_dir: Path):
    """Build + write + load, exercising the real T452->T453 handoff path
    (on-disk JSONL, not an in-memory shortcut) so the benchmark measures
    what a real deployment would actually do.
    """
    from implementation.runtime.memory.build import BuildConfig, build_index
    from implementation.runtime.memory.index_writer import write_index
    from implementation.runtime.memory.retrieve import MemoryIndex

    config = BuildConfig(
        project_id=_PROJECT_ID, own_repo_root=corpus_root, general_repo_root=corpus_root,
        output_dir=output_dir,
    )
    start = time.perf_counter()
    result = build_index(config)
    write_index(output_dir, result.chunks, result.rejections, result.manifest)
    index = MemoryIndex.load(output_dir)
    elapsed = time.perf_counter() - start
    return index, len(index.chunks), elapsed


def _time_queries(retriever, context) -> list[float]:
    retriever.search(_QUERY_SET[0], context, top_k=10)  # warm-up, excluded from measurement
    durations = []
    for query_text in _QUERY_SET * 3:  # repeat the set for a more stable p95 estimate
        start = time.perf_counter()
        retriever.search(query_text, context, top_k=10)
        durations.append((time.perf_counter() - start) * 1000)
    return durations


def _summarize(durations_ms: list[float]) -> dict:
    ordered = sorted(durations_ms)
    return {
        "p50": statistics.median(ordered),
        "p95": ordered[min(int(len(ordered) * 0.95), len(ordered) - 1)],
        "p99": ordered[min(int(len(ordered) * 0.99), len(ordered) - 1)],
        "max": ordered[-1],
    }


if __name__ == "__main__":
    unittest.main()
