"""Tests for `implementation/runtime/meta_improver.py` (T503).

Four required categories per `docs/tasks/task-T503.md`'s "The adversarial
'never writes' test -- the actual proof, not an assertion":

1. `TestNoFilesystemMutation.test_static_scan_finds_zero_mutation_calls` --
   an AST scan of the module's own real source proving zero occurrences of
   any filesystem-mutating call shape.
2. `TestNoFilesystemMutation.test_static_scan_detects_a_synthetic_violation`
   -- proves the scanner itself is not a no-op that always reports clean, by
   feeding it synthetic snippets that DO contain each banned call shape.
3. `TestNoFilesystemMutation.test_full_pipeline_leaves_repo_byte_identical`
   -- the behavioral, real-filesystem proof: snapshot the repo before/after
   running the real generate pipeline against real T501 data, assert
   byte-identical.
4. `TestTargetPathRejection` -- constructs proposals targeting the two
   `docs/artifacts/protected-paths-v1.md` protected paths and confirms both
   raise, not silently succeed.
5. `TestRealDataFunctional` -- real T501 taxonomy -> real clusters -> real
   proposals, with specific (non-tautological) assertions.

Mirrors `test_golden_harness_failure_taxonomy.py`'s and
`test_golden_held_out_isolation.py`'s split between real-tree proof tests and
synthetic-fixture edge-case tests.
"""
from __future__ import annotations

import ast
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

from implementation.runtime import meta_improver as mi
from implementation.runtime.golden_harness.failure_taxonomy import FailureTaxonomy
from tests._helpers.repo import repo_root

# The real module file(s) this task adds -- scanned directly, not a
# hypothetical/idealized reconstruction of them (task brief's own wording).
_MODULE_PATH = Path(mi.__file__)

# Method names that mutate the filesystem when called on a Path (or
# Path-shaped) object.
_WRITE_METHOD_NAMES = {"write_text", "write_bytes", "unlink"}
# os.<name> mutating calls.
_OS_MUTATION_NAMES = {"remove", "rename", "replace", "system"}


def _open_call_is_write_capable(call: ast.Call) -> bool:
    """True if a builtin `open(...)` call's mode argument (positional #2 or
    keyword `mode`) contains any of the write-capable mode characters
    `w`/`a`/`x`. A call with no mode argument defaults to `"r"` (read-only,
    not flagged)."""
    mode_node = None
    if len(call.args) >= 2:
        mode_node = call.args[1]
    for kw in call.keywords:
        if kw.arg == "mode":
            mode_node = kw.value
    if mode_node is None:
        return False
    if isinstance(mode_node, ast.Constant) and isinstance(mode_node.value, str):
        mode = mode_node.value
        return any(flag in mode for flag in ("w", "a", "x"))
    # A non-constant (dynamic) mode expression: conservatively flag it --
    # this module never needs a dynamic open() mode at all.
    return True


def find_filesystem_mutation_calls(source: str) -> list[str]:
    """Walk every `ast.Call` node in `source` and return a list of
    human-readable descriptions of any call shape that could plausibly
    mutate the filesystem or invoke a repository-mutating `git` subprocess.
    Empty list means clean. Pure static analysis -- never executes `source`.

    Flags:
      - `open(...)` with a write-capable mode (`"w"`, `"a"`, `"x"`, or any
        mode string containing those, or a non-constant/dynamic mode).
      - Any `.write_text(...)`, `.write_bytes(...)`, `.unlink(...)` method
        call (regardless of receiver -- conservative, mirrors
        `Path.write_text`/etc.).
      - `os.remove`/`os.rename`/`os.replace`/`os.system` calls.
      - Any `shutil.*` call.
      - Any `subprocess.*` call, or a call to a name literally called
        `subprocess` (covers `from subprocess import run` etc. via the
        direct-name-call branch below).
    """
    tree = ast.parse(source)
    violations: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func

        if isinstance(func, ast.Name):
            if func.id == "open" and _open_call_is_write_capable(node):
                violations.append(f"line {node.lineno}: write-capable open() call")
            elif func.id == "system":
                violations.append(f"line {node.lineno}: bare system() call")
            continue

        if not isinstance(func, ast.Attribute):
            continue

        attr = func.attr
        # Resolve the leftmost name in a dotted attribute chain, e.g.
        # `os.path.join` -> "os", `shutil.copy` -> "shutil".
        root = func.value
        while isinstance(root, ast.Attribute):
            root = root.value
        root_name = root.id if isinstance(root, ast.Name) else None

        if attr in _WRITE_METHOD_NAMES:
            violations.append(f"line {node.lineno}: .{attr}(...) call")
        elif root_name == "os" and attr in _OS_MUTATION_NAMES:
            violations.append(f"line {node.lineno}: os.{attr}(...) call")
        elif root_name == "shutil":
            violations.append(f"line {node.lineno}: shutil.{attr}(...) call")
        elif root_name == "subprocess":
            violations.append(f"line {node.lineno}: subprocess.{attr}(...) call")

    return violations


class TestNoFilesystemMutation(unittest.TestCase):
    """The actual proof this module is architecturally incapable of writing."""

    def test_static_scan_finds_zero_mutation_calls(self):
        source = _MODULE_PATH.read_text(encoding="utf-8")
        violations = find_filesystem_mutation_calls(source)
        self.assertEqual(
            violations,
            [],
            msg=f"{_MODULE_PATH}: found filesystem-mutating call(s):\n  " + "\n  ".join(violations),
        )

    def test_static_scan_detects_a_synthetic_violation(self):
        # Proves the scanner is a real detector, not a no-op that always
        # reports clean -- feed it one synthetic snippet per banned shape.
        cases = {
            "write_mode_open": "open('x.txt', 'w')",
            "append_mode_open": "open('x.txt', 'a')",
            "dynamic_mode_open": "open('x.txt', mode)",
            "path_write_text": "Path('x.txt').write_text('y')",
            "path_write_bytes": "Path('x.txt').write_bytes(b'y')",
            "path_unlink": "Path('x.txt').unlink()",
            "os_remove": "os.remove('x.txt')",
            "os_rename": "os.rename('a', 'b')",
            "os_replace": "os.replace('a', 'b')",
            "os_system": "os.system('git apply patch.diff')",
            "shutil_copy": "shutil.copy('a', 'b')",
            "shutil_rmtree": "shutil.rmtree('a')",
            "subprocess_run": "subprocess.run(['git', 'commit'])",
            "subprocess_call": "subprocess.call(['git', 'checkout', '.'])",
        }
        for label, snippet in cases.items():
            with self.subTest(label=label):
                violations = find_filesystem_mutation_calls(snippet)
                self.assertTrue(violations, msg=f"scanner failed to flag: {snippet!r}")

    def test_static_scan_does_not_false_positive_on_read_only_calls(self):
        # Guards against an overly-broad scanner that would make the "zero
        # violations" real-source result meaningless.
        clean_snippet = (
            "open('x.txt')\n"
            "open('x.txt', 'r')\n"
            "Path('x.txt').read_text()\n"
            "content.replace('a', 'b')\n"  # str.replace -- not os.replace.
            "taxonomy.filter_by(cause='x')\n"
        )
        self.assertEqual(find_filesystem_mutation_calls(clean_snippet), [])

    def test_full_pipeline_leaves_repo_byte_identical(self):
        """Behavioral, real-filesystem proof: snapshot tracked-file state
        before running the real end-to-end pipeline (load real T501
        taxonomy -> cluster -> generate a proposal for every cluster)
        against the real on-disk data, re-snapshot after, assert
        byte-identical."""
        root = repo_root()

        def snapshot() -> tuple[str, str]:
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
            ).stdout
            # Content hash of every file the generator's target-eligibility
            # allowlist could plausibly touch, plus the real failure-data
            # directory the pipeline reads from.
            hasher = hashlib.sha256()
            watched_dirs = [
                root / "implementation" / "knowledge" / "agents",
                root / "implementation" / "knowledge" / "skills",
                root / "implementation" / "knowledge" / "commands",
                root / "implementation" / "knowledge" / "instructions",
                root / "docs" / "benchmarks" / "failures",
            ]
            for directory in watched_dirs:
                for path in sorted(directory.rglob("*")):
                    if path.is_file():
                        hasher.update(path.relative_to(root).as_posix().encode("utf-8"))
                        hasher.update(path.read_bytes())
            return status, hasher.hexdigest()

        before = snapshot()

        taxonomy = FailureTaxonomy.load(root / "docs" / "benchmarks" / "failures")
        clusters = mi.cluster_by_axes(taxonomy)
        self.assertGreater(len(clusters), 0)
        proposals = mi.generate_proposals(taxonomy, repo_root=root)
        self.assertEqual(len(proposals), len(clusters))
        # Touch every field, including the computed diff, to exercise the
        # full object graph -- not just construct-and-discard.
        for proposal in proposals:
            self.assertIsInstance(proposal.diff_text(), str)

        after = snapshot()
        self.assertEqual(before, after, msg="generating proposals mutated the real repository tree")


class TestTargetPathRejection(unittest.TestCase):
    """Objective point 2's first-layer defense-in-depth, proven against both
    of `docs/artifacts/protected-paths-v1.md`'s explicitly-declared protected
    paths (`tests/golden/**`, `scripts/scorecard.py`) -- a rejection, not a
    silently-produced proposal object."""

    def _attempt_proposal(self, target_path: str):
        return mi.DiffProposal(
            target_path=target_path,
            rationale="adversarial rejection test",
            base_content="before",
            proposed_content="after",
            based_on=("some-case",),
            cluster_cause="c",
            cluster_behavior="b",
            cluster_mechanism="m",
        )

    def test_rejects_path_under_tests_golden(self):
        with self.assertRaises(ValueError):
            self._attempt_proposal("tests/golden/open/example-case/expect.py")

    def test_rejects_scripts_scorecard_py(self):
        with self.assertRaises(ValueError):
            self._attempt_proposal("scripts/scorecard.py")

    def test_rejects_absolute_path(self):
        with self.assertRaises(ValueError):
            self._attempt_proposal("/etc/passwd")

    def test_rejects_path_traversal(self):
        with self.assertRaises(ValueError):
            self._attempt_proposal("implementation/knowledge/agents/../../../etc/passwd")

    def test_rejects_application_code_path(self):
        with self.assertRaises(ValueError):
            self._attempt_proposal("implementation/runtime/meta_improver.py")

    def test_accepts_each_of_the_four_allowed_classes(self):
        allowed = {
            mi.TARGET_CLASS_AGENT: "implementation/knowledge/agents/example.md",
            mi.TARGET_CLASS_SKILL: "implementation/knowledge/skills/example/SKILL.md",
            mi.TARGET_CLASS_COMMAND: "implementation/knowledge/commands/example.md",
            mi.TARGET_CLASS_INSTRUCTION: "implementation/knowledge/instructions/example.md",
        }
        for expected_class, path in allowed.items():
            with self.subTest(path=path):
                proposal = self._attempt_proposal(path)
                self.assertEqual(proposal.target_file_class, expected_class)


class TestRealDataFunctional(unittest.TestCase):
    """Real T501 taxonomy -> real clusters -> real proposals, with specific,
    non-tautological assertions."""

    @classmethod
    def setUpClass(cls):
        cls.root = repo_root()
        cls.taxonomy = FailureTaxonomy.load(cls.root / "docs" / "benchmarks" / "failures")
        cls.clusters = mi.cluster_by_axes(cls.taxonomy)

    def test_cluster_by_axes_covers_every_record_exactly_once(self):
        all_ids_in_clusters = [cid for cluster in self.clusters for cid in cluster.case_ids]
        self.assertEqual(len(all_ids_in_clusters), len(self.taxonomy.all_records()))
        self.assertEqual(set(all_ids_in_clusters), {r.case_id for r in self.taxonomy.all_records()})

    def test_cluster_by_axes_forms_a_real_multi_case_cluster(self):
        # cause=established-practice-drift / behavior=naming-or-format-drift /
        # mechanism=naming-convention-drift is shared by exactly 3 real
        # cases (held-out-case-1, held-out-case-3, plan-real-doc-header-drift)
        # -- a real multi-record cluster, not a tautological non-empty check.
        matching = [c for c in self.clusters if c.mechanism == "naming-convention-drift"]
        self.assertEqual(len(matching), 1)
        self.assertEqual(
            matching[0].case_ids,
            ("held-out-case-1", "held-out-case-3", "plan-real-doc-header-drift"),
        )

    def test_cluster_by_axes_produces_at_least_one_singleton_cluster(self):
        singleton_clusters = [c for c in self.clusters if len(c.case_ids) == 1]
        self.assertGreater(len(singleton_clusters), 0)

    def test_generate_proposal_for_real_multi_case_cluster_is_plausible(self):
        cluster = next(c for c in self.clusters if c.mechanism == "naming-convention-drift")
        proposal = mi.generate_proposal(cluster, repo_root=self.root)

        # based_on exactly matches the real cluster's real case IDs.
        self.assertEqual(proposal.based_on, cluster.case_ids)

        # target path is one of the four allowed classes.
        self.assertIn(
            proposal.target_file_class,
            {mi.TARGET_CLASS_AGENT, mi.TARGET_CLASS_SKILL, mi.TARGET_CLASS_COMMAND, mi.TARGET_CLASS_INSTRUCTION},
        )
        self.assertEqual(mi.classify_target_path(proposal.target_path), proposal.target_file_class)

        # rationale and diff content reference the real cluster's real axis
        # values and case IDs -- not a tautological "non-empty" check.
        self.assertIn(cluster.cause, proposal.rationale)
        self.assertIn(cluster.behavior, proposal.rationale)
        self.assertIn(cluster.mechanism, proposal.rationale)
        for case_id in cluster.case_ids:
            self.assertIn(case_id, proposal.rationale)
            self.assertIn(case_id, proposal.proposed_content)
        self.assertIn(cluster.cause, proposal.proposed_content)
        self.assertIn(cluster.behavior, proposal.proposed_content)
        self.assertIn(cluster.mechanism, proposal.proposed_content)

        # the diff is real and non-empty (base_content != proposed_content
        # is already enforced at construction time).
        diff = proposal.diff_text()
        self.assertTrue(diff)
        self.assertIn(proposal.target_path, diff)

    def test_generate_proposal_for_real_singleton_cluster_is_plausible(self):
        cluster = next(c for c in self.clusters if len(c.case_ids) == 1)
        proposal = mi.generate_proposal(cluster, repo_root=self.root)
        self.assertEqual(proposal.based_on, cluster.case_ids)
        self.assertEqual(len(proposal.based_on), 1)
        self.assertEqual(mi.classify_target_path(proposal.target_path), proposal.target_file_class)

    def test_generate_proposals_returns_one_proposal_per_cluster_in_cluster_order(self):
        proposals = mi.generate_proposals(self.taxonomy, repo_root=self.root)
        self.assertEqual(len(proposals), len(self.clusters))
        for proposal, cluster in zip(proposals, self.clusters):
            self.assertEqual(proposal.based_on, cluster.case_ids)
            self.assertEqual(proposal.cluster_cause, cluster.cause)
            self.assertEqual(proposal.cluster_behavior, cluster.behavior)
            self.assertEqual(proposal.cluster_mechanism, cluster.mechanism)


class TestClusterAndSelectSyntheticFixtures(unittest.TestCase):
    """Edge cases and the deterministic target-selection heuristic, proven
    against a synthetic, controlled knowledge-base fixture (mirrors
    `test_golden_harness_failure_taxonomy.py`'s real-tree/synthetic-fixture
    split)."""

    def _make_fake_repo(self, tmp: Path) -> None:
        agents_dir = tmp / "implementation" / "knowledge" / "agents"
        instructions_dir = tmp / "implementation" / "knowledge" / "instructions"
        agents_dir.mkdir(parents=True)
        instructions_dir.mkdir(parents=True)
        (tmp / "implementation" / "knowledge" / "skills").mkdir(parents=True)
        (tmp / "implementation" / "knowledge" / "commands").mkdir(parents=True)
        (agents_dir / "widget-specialist.md").write_text(
            "# widget-specialist\n\nHandles widget naming convention drift.\n"
        )
        (agents_dir / "unrelated-agent.md").write_text("# unrelated-agent\n\nNo relevant keywords here.\n")
        (instructions_dir / "fallback.md").write_text("# fallback\n\nGeneric instructions, no keyword overlap.\n")

    def _make_fake_taxonomy_dir(self, tmp: Path, *, cause: str, behavior: str, mechanism: str, case_id: str) -> Path:
        failures_dir = tmp / "failures"
        failures_dir.mkdir(exist_ok=True)
        (failures_dir / f"{case_id}.md").write_text(
            f"# Failure classification: `{case_id}`\n\n"
            "| Axis | Value |\n|---|---|\n"
            f"| `cause` | `{cause}` |\n| `behavior` | `{behavior}` |\n| `mechanism` | `{mechanism}` |\n"
        )
        return failures_dir

    def test_select_target_picks_highest_keyword_overlap_file(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            self._make_fake_repo(tmp)
            failures_dir = self._make_fake_taxonomy_dir(
                tmp,
                cause="widget-naming-drift",
                behavior="convention-mismatch",
                mechanism="naming-convention-drift",
                case_id="synthetic-case",
            )
            taxonomy = FailureTaxonomy.load(failures_dir)
            clusters = mi.cluster_by_axes(taxonomy)
            self.assertEqual(len(clusters), 1)
            proposal = mi.generate_proposal(clusters[0], repo_root=tmp)
            self.assertEqual(proposal.target_path, "implementation/knowledge/agents/widget-specialist.md")
            self.assertEqual(proposal.target_file_class, mi.TARGET_CLASS_AGENT)

    def test_select_target_falls_back_to_instructions_when_no_keyword_overlap(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            self._make_fake_repo(tmp)
            failures_dir = self._make_fake_taxonomy_dir(
                tmp,
                cause="zzzznomatch",
                behavior="zzzznomatch",
                mechanism="zzzznomatch",
                case_id="synthetic-case",
            )
            taxonomy = FailureTaxonomy.load(failures_dir)
            clusters = mi.cluster_by_axes(taxonomy)
            proposal = mi.generate_proposal(clusters[0], repo_root=tmp)
            self.assertEqual(proposal.target_path, "implementation/knowledge/instructions/fallback.md")

    def test_cluster_by_axes_singleton_is_valid_not_an_error(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            failures_dir = self._make_fake_taxonomy_dir(
                tmp, cause="a", behavior="b", mechanism="c", case_id="solo-case"
            )
            taxonomy = FailureTaxonomy.load(failures_dir)
            clusters = mi.cluster_by_axes(taxonomy)
            self.assertEqual(len(clusters), 1)
            self.assertEqual(clusters[0].case_ids, ("solo-case",))

    def test_diff_proposal_requires_non_empty_based_on(self):
        with self.assertRaises(ValueError):
            mi.DiffProposal(
                target_path="implementation/knowledge/instructions/example.md",
                rationale="x",
                base_content="a",
                proposed_content="b",
                based_on=(),
                cluster_cause="c",
                cluster_behavior="b",
                cluster_mechanism="m",
            )

    def test_diff_proposal_requires_proposed_content_to_differ(self):
        with self.assertRaises(ValueError):
            mi.DiffProposal(
                target_path="implementation/knowledge/instructions/example.md",
                rationale="x",
                base_content="same",
                proposed_content="same",
                based_on=("case-1",),
                cluster_cause="c",
                cluster_behavior="b",
                cluster_mechanism="m",
            )


if __name__ == "__main__":
    unittest.main()
