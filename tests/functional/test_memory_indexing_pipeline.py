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


_MIXED_CASE_ENTRY = """---
scope: project
project_id: Fixture-Org/Repo-P2
title: mixed case
---
BODY-MARKER-T790 must never reach stderr.
"""


class ProjectIdFormTests(unittest.TestCase):
    """T790 (QA-T760-02): the build takes only the project id the server derives (lower case,
    `<org>/<repo>`). `scope_filter.is_visible` compares exactly, so an index built under another
    spelling answered nothing, without an error."""

    def _run_main(self, project_id: str, root: Path) -> tuple[int, str]:
        import contextlib
        import io

        from implementation.runtime.memory import build
        argv = ["--project-id", project_id, "--own-repo-root", str(root), "--general-repo-root", str(root),
                "--output-dir", str(root / "out")]
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as caught:
            build.main(argv)
        return caught.exception.code, stderr.getvalue()

    def test_a_mixed_case_project_id_is_refused_with_a_non_zero_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            for refused in ("Acme/Widget", "acme/Widget", "acme", "group/sub/repo", "acme/widget.git", " acme/widget"):
                with self.subTest(project_id=refused):
                    code, stderr = self._run_main(refused, Path(tmp))
                    self.assertNotEqual(code, 0)
                    self.assertIn("lower-case <org>/<repo>", stderr)
                    self.assertFalse((Path(tmp) / "out").exists(), "a refused build wrote an index")

    def test_the_refusal_also_holds_without_the_cli(self):
        from implementation.runtime.memory.build import BuildConfig
        with self.assertRaisesRegex(ValueError, "lower-case <org>/<repo>"):
            BuildConfig(project_id="Acme/Widget", own_repo_root=Path("."), general_repo_root=Path("."),
                        output_dir=Path("unused"))

    def test_the_accepted_form_is_exactly_what_the_server_derives(self):
        from implementation.runtime.memory.build import project_id_problem
        from implementation.runtime.memory.context_retriever import normalize_remote_to_project_id
        for remote in ("git@gitlab.com:em-age/emage.code.git", "https://gitlab.com/Acme/Widget.git",
                       "https://gitlab.com/group/sub/repo.git"):
            with self.subTest(remote=remote):
                self.assertIsNone(project_id_problem(normalize_remote_to_project_id(remote)))
        self.assertIn("got 'Acme/Widget'", project_id_problem("Acme/Widget"))

    def test_an_entry_differing_only_by_case_is_named_by_path_and_stays_invisible(self):
        from implementation.runtime.memory import build, scanner
        from implementation.runtime.memory.enrich import build_chunk_records
        from implementation.runtime.memory.scope_filter import RequestingContext, is_visible
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entry_path = root / scanner.VAULT_SUBDIR / "project" / "mixed.md"
            entry_path.parent.mkdir(parents=True)
            entry_path.write_text(_MIXED_CASE_ENTRY, encoding="utf-8")
            config = build.BuildConfig(project_id="fixture-org/repo-p2", own_repo_root=root, general_repo_root=root,
                                       output_dir=root / "out")
            own = scanner.ScanRoot(root, config.project_id)
            entries, rejections = build.collect_entries(own, scanner.ScanRoot(root, "general-harness-source"), config)
        self.assertEqual(rejections, [])
        rel_path = str(entry_path.relative_to(root))
        self.assertEqual(build.case_mismatched_paths(entries, config.project_id), [rel_path])
        self.assertEqual(build.case_mismatched_paths(entries, "other-org/other-repo"), [])

        chunk = build_chunk_records(entries[0], build.chunk_body(entries[0].body))[0]
        context = RequestingContext(project_id=config.project_id, platform="claude-code")
        self.assertFalse(is_visible({"scope": chunk.scope, "project_id": chunk.project_id}, context))

        import contextlib
        import io
        stderr = io.StringIO()
        result = build.BuildResult(chunks=[], rejections=[], manifest={}, case_mismatched_paths=[rel_path])
        with contextlib.redirect_stderr(stderr):
            build._warn_project_id_mismatches(result, config.project_id)
        self.assertIn(repr(rel_path), stderr.getvalue())
        self.assertIn("only by letter case", stderr.getvalue())
        self.assertNotIn("BODY-MARKER-T790", stderr.getvalue())
        self.assertNotIn("is not --project-id", stderr.getvalue())

    def _collect(self, root: Path, files: dict[str, str]):
        from implementation.runtime.memory import build, scanner
        for name, text in files.items():
            path = root / scanner.VAULT_SUBDIR / "project" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        config = build.BuildConfig(project_id="fixture-org/repo-p2", own_repo_root=root, general_repo_root=root,
                                   output_dir=root / "out")
        own = scanner.ScanRoot(root, config.project_id)
        entries, rejections = build.collect_entries(own, scanner.ScanRoot(root, "general-harness-source"), config)
        self.assertEqual(rejections, [])
        return config, entries

    def _warnings(self, result, project_id: str) -> str:
        import contextlib
        import io
        from implementation.runtime.memory import build
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            build._warn_project_id_mismatches(result, project_id)
        return stderr.getvalue()

    def test_an_entry_naming_another_project_is_named_by_path_and_stays_invisible(self):
        """T795 (SEC-T791-02): any other difference than letter case was indexed, never returned, unnamed."""
        from implementation.runtime.memory import build
        from implementation.runtime.memory.enrich import build_chunk_records
        from implementation.runtime.memory.scope_filter import RequestingContext, is_visible
        foreign_ids = {"typo.md": "fixture-org/repo-p3", "suffix.md": "fixture-org/repo-p2.git",
                       "nested.md": "fixture-org/sub/repo-p2", "mixed-typo.md": "Fixture-Org/Repo-P3"}
        files = {name: _MIXED_CASE_ENTRY.replace("Fixture-Org/Repo-P2", pid) for name, pid in foreign_ids.items()}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config, entries = self._collect(root, files)
            expected = sorted(e.location.relative_path for e in entries)
        self.assertEqual(len(entries), len(foreign_ids), "every entry stays indexed; nothing is dropped or rewritten")
        self.assertEqual(sorted(build.foreign_project_paths(entries, config.project_id)), expected)
        self.assertEqual(build.case_mismatched_paths(entries, config.project_id), [])
        context = RequestingContext(project_id=config.project_id, platform="claude-code")
        for entry in entries:
            chunk = build_chunk_records(entry, build.chunk_body(entry.body))[0]
            self.assertFalse(is_visible({"scope": chunk.scope, "project_id": chunk.project_id}, context))

        result = build.BuildResult(chunks=[], rejections=[], manifest={}, foreign_project_paths=expected)
        warnings = self._warnings(result, config.project_id)
        for rel_path in expected:
            self.assertIn(f"warning: {rel_path!r}: its project_id is not --project-id 'fixture-org/repo-p2'; "
                          "retrieve will not return this entry\n", warnings)
        self.assertNotIn("BODY-MARKER-T790", warnings)
        for pid in foreign_ids.values():
            self.assertNotIn(pid, warnings, "the warning names the path, never the entry's own fields")
        self.assertNotIn("letter case", warnings)

    def test_a_matching_entry_gets_no_warning_and_a_case_only_one_keeps_its_wording(self):
        """Negative cases for T795: an exact match is silent; a case-only difference is not double-reported."""
        from implementation.runtime.memory import build
        matching = _MIXED_CASE_ENTRY.replace("Fixture-Org/Repo-P2", "fixture-org/repo-p2")
        with tempfile.TemporaryDirectory() as tmp:
            config, entries = self._collect(Path(tmp), {"match.md": matching, "mixed.md": _MIXED_CASE_ENTRY})
        case_only = build.case_mismatched_paths(entries, config.project_id)
        self.assertEqual([Path(p).name for p in case_only], ["mixed.md"])
        self.assertEqual(build.foreign_project_paths(entries, config.project_id), [])
        result = build.BuildResult(chunks=[], rejections=[], manifest={}, case_mismatched_paths=case_only,
                                   foreign_project_paths=[])
        warnings = self._warnings(result, config.project_id)
        self.assertEqual(warnings.count("warning:"), 1)
        self.assertIn("only by letter case; retrieve will not return this entry", warnings)
        self.assertNotIn("match.md", warnings)


class RemoteProjectIdTests(unittest.TestCase):
    """T828 (QA-T818-03): the CLI refuses a well-formed `--project-id` that is not the id the server
    derives from the git remote `origin` of `--own-repo-root`. Before T828 `acme/other` beside a remote
    `Acme/Widget` built an index (exit 0) that the server filtered to nothing."""

    def setUp(self):
        from unittest import mock
        # The user's own git config (an `insteadOf` rewrite, say) must not change what these tests see.
        patcher = mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"})
        patcher.start()
        self.addCleanup(patcher.stop)
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "repo"
        self.root.mkdir()
        self._git("init", "-q")

    def _git(self, *args: str) -> None:
        import subprocess
        subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True, text=True)

    def _main(self, project_id: str) -> tuple[int, str, list]:
        """`build.main` with the build and the write replaced, so no embedding model is needed; returns the
        exit code, stderr and the configs `build_index` was called with."""
        import contextlib
        import io
        from unittest import mock

        from implementation.runtime.memory import build
        argv = ["--project-id", project_id, "--own-repo-root", str(self.root), "--general-repo-root",
                str(self.root), "--output-dir", str(self.root / "out")]
        empty = build.BuildResult(chunks=[], rejections=[], manifest={})
        stderr = io.StringIO()
        with mock.patch.object(build, "build_index", return_value=empty) as built, \
                mock.patch.object(build, "write_index") as written, contextlib.redirect_stderr(stderr), \
                contextlib.redirect_stdout(io.StringIO()):
            code = build.main(argv)
        if code != 0:
            written.assert_not_called()
        return code, stderr.getvalue(), [c.args[0] for c in built.call_args_list]

    def test_a_well_formed_id_that_is_not_the_remotes_is_refused(self):
        self._git("remote", "add", "origin", "https://gitlab.com/Acme/Widget.git")
        code, stderr, built = self._main("acme/other")
        self.assertEqual(code, 2)
        self.assertEqual(built, [], "a refused build ran")
        self.assertIn("'acme/other'", stderr)
        self.assertIn("'acme/widget'", stderr)
        self.assertFalse((self.root / "out").exists())

    def test_the_id_derived_from_the_remote_is_accepted(self):
        self._git("remote", "add", "origin", "git@gitlab.com:Acme/Widget.git")
        code, stderr, built = self._main("acme/widget")
        self.assertEqual((code, stderr), (0, ""))
        self.assertEqual([c.project_id for c in built], ["acme/widget"])

    def test_without_an_origin_remote_every_id_is_refused(self):
        self._git("remote", "add", "upstream", "https://gitlab.com/acme/widget.git")  # not 'origin'
        code, stderr, built = self._main("acme/widget")
        self.assertEqual(code, 2)
        self.assertEqual(built, [])
        self.assertIn("gives no project id", stderr)
        self.assertIn("set it and re-run", stderr)
        self.assertEqual(stderr.count(str(self.root)), 1, "the path is named once")

    def test_a_remote_without_an_org_repo_path_is_refused(self):
        self._git("remote", "add", "origin", "https://gitlab.com/widget.git")
        code, stderr, _ = self._main("acme/widget")
        self.assertEqual(code, 2)
        self.assertIn("no <org>/<repo> path", stderr)

    def test_the_refusal_never_repeats_remote_userinfo(self):
        """SEC-T796-01: neither the mismatch message nor a resolution error shows `user:token@`."""
        for remote, project_id in (("https://bob:S3cr3t-T828@gitlab.com/Acme/Widget.git", "acme/other"),
                                   ("https://bob:S3cr3t-T828@gitlab.com/widget", "acme/widget")):
            with self.subTest(remote=remote):
                if "origin" in self._remotes():
                    self._git("remote", "remove", "origin")
                self._git("remote", "add", "origin", remote)
                code, stderr, _ = self._main(project_id)
                self.assertEqual(code, 2)
                self.assertNotIn("S3cr3t-T828", stderr)
                self.assertNotIn("bob", stderr)

    def _remotes(self) -> list[str]:
        import subprocess
        out = subprocess.run(["git", "-C", str(self.root), "remote"], check=True, capture_output=True, text=True)
        return out.stdout.split()

    def test_the_given_value_is_compared_as_given(self):
        """Compared exactly, never rewritten: `Acme/Widget` and `acme/widget ` are refused where the
        remote gives `acme/widget`."""
        self._git("remote", "add", "origin", "https://gitlab.com/Acme/Widget.git")
        from implementation.runtime.memory import build
        self.assertIsNone(build.remote_project_id_problem("acme/widget", self.root))
        self.assertIsNotNone(build.remote_project_id_problem("Acme/Widget", self.root))
        self.assertIsNotNone(build.remote_project_id_problem("acme/widget ", self.root))


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
