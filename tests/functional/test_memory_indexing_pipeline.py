"""T452 — knowledge-vault indexing pipeline.

Covers acceptance criteria 1 (enrichment fields), 2 (write-time-only scope
validation, reject-not-default), 3 (structural project-scope unreachability),
4 (shared-scope reachability via the identical mechanism), 5 (rebuild
determinism), and 6 (no embeddings-provider credential/network egress
required).

Mirrors this repo's existing convention (`test_sync_determinism.py`,
`test_t223_sia_harness_capture.py`, etc.) of `unittest.SkipTest` for
environment-dependent heavier checks, so `python3 tests/run.py` stays
runnable with only this repo's stdlib+PyYAML baseline dependency set — the
optional `implementation/runtime/memory/requirements.txt` deps are only
needed to exercise the code-chunking and embedding stages for real.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

FIXTURES = REPO_ROOT / "tests" / "fixtures" / "memory"

from tests._helpers.memory_fixtures import materialize_git_repo  # noqa: E402


def _tree_sitter_available() -> bool:
    try:
        import tree_sitter  # noqa: F401
        import tree_sitter_python  # noqa: F401
    except ImportError:
        return False
    return True


def _fastembed_available() -> bool:
    try:
        import fastembed  # noqa: F401
    except ImportError:
        return False
    return True


class _FileAccessAudit:
    """Records every `open`/directory-scan the process performs while active.

    Used to prove acceptance criterion 3 structurally: not "the final index
    doesn't contain X" (a filter could satisfy that) but "the filesystem
    call that would have read X's directory never happened at all."
    """

    _WATCHED = {"open", "os.scandir", "os.listdir"}

    def __init__(self) -> None:
        self.paths: list[str] = []
        self._active = False
        sys.addaudithook(self._hook)

    def _hook(self, event: str, args: tuple) -> None:
        if not self._active or event not in self._WATCHED or not args:
            return
        self.paths.append(str(args[0]))

    def __enter__(self) -> "_FileAccessAudit":
        self.paths = []
        self._active = True
        return self

    def __exit__(self, *exc) -> None:
        self._active = False


class WriteTimeValidationTests(unittest.TestCase):
    """Acceptance criterion 2 — §5, in isolation from the filesystem."""

    def _fm(self, raw: dict):
        from implementation.runtime.memory.validate import to_entry_frontmatter
        return to_entry_frontmatter(raw)

    def _reason(self, raw: dict):
        from implementation.runtime.memory.validate import validate_entry
        return validate_entry(self._fm(raw))

    def test_reject_missing_scope(self):
        self.assertIsNotNone(self._reason({"title": "x"}))

    def test_reject_empty_scope(self):
        self.assertIsNotNone(self._reason({"scope": ""}))

    def test_reject_invalid_scope_literal(self):
        self.assertIsNotNone(self._reason({"scope": "GENERAL"}))
        self.assertIsNotNone(self._reason({"scope": "public"}))

    def test_reject_project_missing_project_id(self):
        self.assertIsNotNone(self._reason({"scope": "project"}))

    def test_reject_shared_missing_platforms(self):
        raw = {"scope": "shared", "shared_consumers": {"projects": ["p"]}}
        self.assertIsNotNone(self._reason(raw))

    def test_reject_shared_empty_projects_list(self):
        raw = {"scope": "shared", "shared_consumers": {"projects": [], "platforms": ["claude-code"]}}
        self.assertIsNotNone(self._reason(raw))

    def test_accept_valid_general(self):
        self.assertIsNone(self._reason({"scope": "general"}))

    def test_accept_valid_project(self):
        self.assertIsNone(self._reason({"scope": "project", "project_id": "org/repo"}))

    def test_accept_valid_shared_wildcard(self):
        raw = {"scope": "shared", "shared_consumers": {"projects": ["*"], "platforms": ["*"]}}
        self.assertIsNone(self._reason(raw))

    def test_no_default_scope_ever_assigned(self):
        """Reject-not-default: a missing scope must never resolve to a truthy value."""
        fm = self._fm({"title": "x"})
        self.assertIsNone(fm.scope)


class ChunkerProseTests(unittest.TestCase):
    """Prose (section-aware) chunking — no optional deps required."""

    def test_headings_produce_symbol_and_parents(self):
        from implementation.runtime.memory.chunker import chunk_body
        body = "# Top\n\nIntro text.\n\n## Sub\n\nMore text.\n"
        chunks = chunk_body(body)
        self.assertEqual([c.content_type for c in chunks], ["prose", "prose"])
        self.assertEqual(chunks[0].symbol, "Top")
        self.assertEqual(chunks[0].parents, ())
        self.assertEqual(chunks[1].symbol, "Sub")
        self.assertEqual(chunks[1].parents, ("Top",))

    def test_prose_has_no_ast_type_or_imports(self):
        """Documents acceptance criterion 1's "no prose equivalent" fields."""
        from implementation.runtime.memory.chunker import chunk_body
        chunks = chunk_body("# T\n\nSome text.\n")
        self.assertIsNone(chunks[0].ast_type)
        self.assertEqual(chunks[0].imports, ())


@unittest.skipUnless(
    _tree_sitter_available(),
    "tree-sitter + grammar packages not installed — "
    "pip install -r implementation/runtime/memory/requirements.txt",
)
class ChunkerCodeTests(unittest.TestCase):
    """Acceptance criterion 1 — tree-sitter code-chunking path."""

    def test_python_fence_produces_per_symbol_chunks(self):
        from implementation.runtime.memory.chunker import chunk_body
        body = (
            "```python\nimport os\n\n\ndef foo():\n    return 1\n\n\n"
            "class Bar:\n    def baz(self):\n        return 2\n```\n"
        )
        chunks = chunk_body(body)
        code_chunks = [c for c in chunks if c.content_type == "code"]
        symbols = {c.symbol for c in code_chunks}
        self.assertEqual(symbols, {"foo", "Bar", "baz"})

        foo = next(c for c in code_chunks if c.symbol == "foo")
        self.assertEqual(foo.ast_type, "function_definition")
        self.assertIn("import os", foo.imports)
        self.assertEqual(foo.parents, ())

        baz = next(c for c in code_chunks if c.symbol == "baz")
        self.assertEqual(baz.parents, ("Bar",))

    def test_unsupported_language_falls_back_to_whole_block(self):
        from implementation.runtime.memory.chunker import chunk_body
        chunks = chunk_body("```text\nplain content\n```\n")
        self.assertEqual(len(chunks), 1)
        self.assertIsNone(chunks[0].ast_type)
        self.assertEqual(chunks[0].language, "text")


class StructuralScanTests(unittest.TestCase):
    """Acceptance criteria 2, 3, 4 — scan + validate stage, no embedding needed."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        tmp_root = Path(cls._tmp.name)
        cls.general_root = materialize_git_repo(FIXTURES / "general-source", tmp_root / "general-source")
        cls.p1_root = materialize_git_repo(FIXTURES / "repo-p1", tmp_root / "repo-p1")
        cls.p2_root = materialize_git_repo(FIXTURES / "repo-p2", tmp_root / "repo-p2")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def _roots(self):
        from implementation.runtime.memory import scanner
        own = scanner.ScanRoot(self.p2_root, "fixture-org/repo-p2")
        general = scanner.ScanRoot(self.general_root, "general-harness-source")
        return own, general

    def _config(self, shared_roots=()):
        from implementation.runtime.memory.build import BuildConfig
        return BuildConfig(
            project_id="fixture-org/repo-p2",
            own_repo_root=self.p2_root,
            general_repo_root=self.general_root,
            output_dir=Path(self._tmp.name) / "out",
            shared_source_roots=shared_roots,
        )

    def test_rejection_cases_present_and_excluded_from_entries(self):
        """P2 is configured as its own shared source here (a valid, if unusual,
        operator choice) purely so the shared_consumers rejection fixtures —
        which live under P2's own `shared/` subtree — are actually scanned;
        per §4.1 a project's own repo only contributes `project`-scope
        entries by default, `shared/` is only ever read via an explicit
        shared-source configuration (see `test_shared_scope_reachability_...`
        for the cross-repo case).
        """
        from implementation.runtime.memory.build import collect_entries
        from implementation.runtime.memory import scanner
        own, general = self._roots()
        p2_as_shared_source = scanner.ScanRoot(self.p2_root, "fixture-org/repo-p2")
        entries, rejections = collect_entries(own, general, self._config(shared_roots=(p2_as_shared_source,)))

        reasons_by_file = {r.source_path: r.reason for r in rejections}
        expect_rejected = {
            "implementation/knowledge/memory/project/reject-missing-scope.md",
            "implementation/knowledge/memory/project/reject-missing-project-id.md",
            "implementation/knowledge/memory/shared/reject-incomplete-shared-missing-platforms.md",
            "implementation/knowledge/memory/shared/reject-incomplete-shared-empty-projects.md",
        }
        self.assertTrue(expect_rejected.issubset(reasons_by_file.keys()), reasons_by_file)

        entry_paths = {e.location.relative_path for e in entries}
        self.assertFalse(expect_rejected & entry_paths)

    def test_valid_entries_carry_scope_metadata(self):
        from implementation.runtime.memory.build import collect_entries
        own, general = self._roots()
        entries, _ = collect_entries(own, general, self._config())

        p2_entry = next(e for e in entries if "p2-own-entry.md" in e.location.relative_path)
        self.assertEqual(p2_entry.frontmatter.scope, "project")
        self.assertEqual(p2_entry.frontmatter.project_id, "fixture-org/repo-p2")
        self.assertNotEqual(p2_entry.location.commit, "no-git-commit-available")

        general_entry = next(e for e in entries if "example-general-entry.md" in e.location.relative_path)
        self.assertEqual(general_entry.frontmatter.scope, "general")

    def test_cross_project_unreachability_is_structural(self):
        """Acceptance criterion 3."""
        from implementation.runtime.memory.build import collect_entries
        own, general = self._roots()
        audit = _FileAccessAudit()
        with audit:
            entries, _ = collect_entries(own, general, self._config(shared_roots=()))

        touched_p1 = [p for p in audit.paths if str(self.p1_root) in p]
        self.assertEqual(
            touched_p1, [],
            "P1's tree was opened/scanned while building P2 without P1 configured as a "
            "shared source — this must be structurally impossible, not merely filtered.",
        )
        all_text = "\n".join(e.body for e in entries)
        self.assertNotIn("FIXTURE-CANARY-P1-ONLY-CONTENT-4172", all_text)

    def test_shared_scope_reachability_same_mechanism(self):
        """Acceptance criterion 4 — positive outcome, plus criterion 3's negative
        outcome re-checked even while P1 IS a configured shared source.
        """
        from implementation.runtime.memory.build import collect_entries
        from implementation.runtime.memory import scanner
        own, general = self._roots()
        p1_shared_source = scanner.ScanRoot(self.p1_root, "fixture-org/repo-p1")

        audit = _FileAccessAudit()
        with audit:
            entries, _ = collect_entries(own, general, self._config(shared_roots=(p1_shared_source,)))

        all_text = "\n".join(e.body for e in entries)
        self.assertIn("FIXTURE-CANARY-SHARED-P1-TO-P2-8891", all_text)
        self.assertNotIn("FIXTURE-CANARY-P1-ONLY-CONTENT-4172", all_text)

        p1_project_dir = str(self.p1_root / "implementation" / "knowledge" / "memory" / "project")
        touched_p1_project = [p for p in audit.paths if p.startswith(p1_project_dir)]
        self.assertEqual(
            touched_p1_project, [],
            "P1's project/ subtree must never be read even when P1 is configured as a "
            "shared source for this build — only its shared/ subtree may be scanned.",
        )


def _model_cache_dir() -> Path:
    default = Path.home() / ".cache" / "emage-memory-embeddings"
    return Path(os.environ.get("EMAGE_MEMORY_MODEL_CACHE", str(default)))


_FULL_PIPELINE_OPT_IN = "EMAGE_MEMORY_FULL_PIPELINE_TEST"


@unittest.skipUnless(_fastembed_available(), "fastembed not installed — see requirements.txt")
@unittest.skipUnless(
    os.environ.get(_FULL_PIPELINE_OPT_IN) == "1",
    f"set {_FULL_PIPELINE_OPT_IN}=1 to run the full embedding + rebuild-determinism test "
    "(uses/downloads a local embedding model; see docs/artifacts/indexing-pipeline-v1.md)",
)
class FullPipelineTests(unittest.TestCase):
    """Acceptance criteria 5 (rebuild determinism) and 6 (no network/credential
    needed for the embedding step to produce real vector output).
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        tmp_root = Path(cls._tmp.name)
        cls.general_root = materialize_git_repo(FIXTURES / "general-source", tmp_root / "general-source")
        cls.p2_root = materialize_git_repo(FIXTURES / "repo-p2", tmp_root / "repo-p2")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def _config(self):
        from implementation.runtime.memory.build import BuildConfig
        return BuildConfig(
            project_id="fixture-org/repo-p2",
            own_repo_root=self.p2_root,
            general_repo_root=self.general_root,
            output_dir=Path(self._tmp.name) / "unused",
        )

    def test_rebuild_is_functionally_equivalent(self):
        from implementation.runtime.memory.build import build_index
        from implementation.runtime.memory.index_writer import diff_index_dirs, write_index

        config = self._config()
        result_a = build_index(config)
        result_b = build_index(config)

        out_a, out_b = Path(self._tmp.name) / "a", Path(self._tmp.name) / "b"
        write_index(out_a, result_a.chunks, result_a.rejections, result_a.manifest)
        write_index(out_b, result_b.chunks, result_b.rejections, result_b.manifest)

        diffs = diff_index_dirs(out_a, out_b)
        self.assertEqual(diffs, [], f"rebuild not functionally-equivalent: {diffs}")

    def test_embedding_runs_with_no_network_egress_or_credential(self):
        """Acceptance criterion 6, demonstrated directly: warm the model cache
        once (this may use the network), then re-run with HF Hub forced
        offline and every HTTP(S) proxy pointed at an unreachable address —
        confirms the actual embedding call needs neither.
        """
        from implementation.runtime.memory.embed import LocalEmbedder

        LocalEmbedder(cache_dir=_model_cache_dir())  # warm cache if not already present

        saved_env = {k: os.environ.get(k) for k in (
            "HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE",
            "HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
        )}
        try:
            os.environ["HF_HUB_OFFLINE"] = "1"
            os.environ["TRANSFORMERS_OFFLINE"] = "1"
            for var in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
                os.environ[var] = "http://127.0.0.1:1"  # nothing listens here
            os.environ.pop("OPENAI_API_KEY", None)

            embedder = LocalEmbedder(cache_dir=_model_cache_dir())
            vectors = embedder.embed_texts(["offline embedding, no network egress"])
        finally:
            for key, value in saved_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        self.assertEqual(len(vectors), 1)
        self.assertEqual(len(vectors[0]), embedder.dim)
        norm = sum(x * x for x in vectors[0]) ** 0.5
        self.assertAlmostEqual(norm, 1.0, places=5)


if __name__ == "__main__":
    unittest.main()
