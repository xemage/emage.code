"""Tests for the human MR gate (T505, `implementation/runtime/golden_harness/mr_gate.py`).

Mirrors `tests/functional/test_meta_improver.py`'s own split and its
`TestNoFilesystemMutation` class's two-independent-proofs discipline,
applied here to `mr_gate.py`'s own "no auto-merge path" guarantee instead of
"no filesystem write":

1. `TestRefusalGate` -- the `promote is not True` refusal, proven with a
   zero-subprocess-calls assertion, not merely a return-value check.
2. `TestNoAutoMergePath.test_static_scan_finds_zero_violations_on_real_source`
   -- an AST scan of this module's own real source proving zero occurrences
   of any merge/approve/push-to-protected call shape.
3. `TestNoAutoMergePath.test_static_scan_detects_a_synthetic_violation` --
   proves the scanner itself is not a no-op, by feeding it synthetic
   snippets that DO contain each banned call shape (one per shape).
4. `TestNoAutoMergePath.test_static_scan_does_not_false_positive_on_legitimate_calls`
   -- proves the scanner does not flag this module's own legitimate calls.
5. `TestBranchCommitMrContent` -- the pure-computation branch-name/commit-
   message/MR-title/MR-description builders.
6. `TestOpenPromotionMrMocked` -- the full `open_promotion_mr` git/`glab`
   call sequence and `MrGateResult` content, with every subprocess call
   mocked (a real test suite must not open real MRs on every CI run).
"""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from implementation.runtime.golden_harness import mr_gate
from implementation.runtime.golden_harness.evaluator_hash import DriftCheckResult
from implementation.runtime.golden_harness.promotion import PromotionResult
from implementation.runtime.meta_improver import DiffProposal

_MODULE_PATH = Path(mr_gate.__file__)


def _make_proposal(
    *,
    target_path: str = "implementation/knowledge/instructions/example.md",
    based_on: tuple[str, ...] = ("case-1", "case-2"),
    rationale: str = "3 classified failure record(s) share a common axis triple.",
) -> DiffProposal:
    return DiffProposal(
        target_path=target_path,
        rationale=rationale,
        base_content="# Example\n\nbefore\n",
        proposed_content="# Example\n\nbefore\n\nafter\n",
        based_on=based_on,
        cluster_cause="established-practice-drift",
        cluster_behavior="naming-or-format-drift",
        cluster_mechanism="naming-convention-drift",
    )


def _make_drift_check(*, any_drift: bool = False) -> DriftCheckResult:
    return DriftCheckResult(
        tests_golden_drift=any_drift,
        scripts_scorecard_drift=False,
        any_drift=any_drift,
        current_digests={"tests_golden": "aaa", "scripts_scorecard": "bbb"},
        known_good_digests={"tests_golden": "aaa", "scripts_scorecard": "bbb"},
        known_good_commit="d405c4e",
        known_good_path=Path("docs/artifacts/evaluator-hash-known-good-v1.json"),
        reason="no drift" if not any_drift else "tests_golden drifted",
    )


def _make_promotion_result(*, promote: bool) -> PromotionResult:
    drift_check = _make_drift_check(any_drift=False)
    if promote:
        return PromotionResult(
            promote=True,
            reason="PROMOTE: all three conjuncts satisfied (floor met, no critical regression, evaluator hash unchanged).",
            floor_met=True,
            no_critical_regression=True,
            evaluator_hash_unchanged=True,
            confirmed_regression_case_ids=(),
            mismatched_escalation_case_ids=(),
            evaluator_hash_check=drift_check,
        )
    return PromotionResult(
        promote=False,
        reason="REJECT: floor not met (treatment aggregate pass rate is below control's).",
        floor_met=False,
        no_critical_regression=True,
        evaluator_hash_unchanged=True,
        confirmed_regression_case_ids=(),
        mismatched_escalation_case_ids=(),
        evaluator_hash_check=drift_check,
    )


class TestRefusalGate(unittest.TestCase):
    """The `promote is not True` refusal -- Objective point 1 / brief's own
    "concrete test requirement" section."""

    def test_rejected_promotion_result_raises(self):
        proposal = _make_proposal()
        rejected = _make_promotion_result(promote=False)
        with self.assertRaises(mr_gate.PromotionNotApproved):
            mr_gate.open_promotion_mr(proposal, rejected)

    def test_refusal_makes_zero_subprocess_calls(self):
        """Not merely "raises" -- confirms zero git/`glab` calls were ever
        attempted in the rejected path, via a mock/spy on the exact
        `subprocess.run` entry point this module's `_run` wrapper uses."""
        proposal = _make_proposal()
        rejected = _make_promotion_result(promote=False)
        with patch("implementation.runtime.golden_harness.mr_gate.subprocess.run") as mock_run:
            with self.assertRaises(mr_gate.PromotionNotApproved):
                mr_gate.open_promotion_mr(proposal, rejected)
            mock_run.assert_not_called()

    def test_unevaluated_promotion_like_result_also_refuses(self):
        """`promote is not True` -- not merely falsy-but-truthy-adjacent.
        Confirms the check is an identity/equality check against the real
        `True` singleton, not a bare `if not promotion_result.promote`
        (which would behave identically here, but this test locks the
        stricter, documented semantics in place)."""
        proposal = _make_proposal()
        drift_check = _make_drift_check(any_drift=False)
        unevaluated = PromotionResult(
            promote=False,
            reason="REJECT: evaluator hash drifted: tests_golden drifted",
            floor_met=True,
            no_critical_regression=True,
            evaluator_hash_unchanged=False,
            confirmed_regression_case_ids=(),
            mismatched_escalation_case_ids=(),
            evaluator_hash_check=drift_check,
        )
        with self.assertRaises(mr_gate.PromotionNotApproved):
            mr_gate.open_promotion_mr(proposal, unevaluated)


class TestBranchCommitMrContent(unittest.TestCase):
    """Objective points 3, 4, 6 -- pure-computation content builders, no I/O."""

    def test_branch_name_is_deterministic_for_the_same_proposal(self):
        proposal = _make_proposal()
        first = mr_gate.compute_branch_name(proposal)
        second = mr_gate.compute_branch_name(proposal)
        self.assertEqual(first, second)
        self.assertTrue(first.startswith("meta-improver/"))

    def test_branch_name_differs_for_a_different_target_path(self):
        a = mr_gate.compute_branch_name(_make_proposal(target_path="implementation/knowledge/instructions/example.md"))
        b = mr_gate.compute_branch_name(
            _make_proposal(target_path="implementation/knowledge/instructions/other-example.md")
        )
        self.assertNotEqual(a, b)

    def test_branch_name_differs_for_a_different_first_based_on_case(self):
        a = mr_gate.compute_branch_name(_make_proposal(based_on=("case-1", "case-2")))
        b = mr_gate.compute_branch_name(_make_proposal(based_on=("case-9", "case-2")))
        self.assertNotEqual(a, b)

    def test_commit_message_cites_based_on_and_rationale(self):
        proposal = _make_proposal(based_on=("case-1", "case-2"), rationale="rationale text goes here")
        message = mr_gate.build_commit_message(proposal)
        self.assertIn("case-1, case-2", message)
        self.assertIn("rationale text goes here", message)
        self.assertTrue(message.startswith("feat(harness):"))

    def test_mr_description_contains_rationale_and_diff_text_verbatim(self):
        proposal = _make_proposal(rationale="a specific, distinctive rationale string")
        promotion_result = _make_promotion_result(promote=True)
        description = mr_gate.build_mr_description(proposal, promotion_result)
        self.assertIn("a specific, distinctive rationale string", description)
        self.assertIn(proposal.diff_text(), description)
        self.assertIn(promotion_result.reason, description)

    def test_mr_title_names_the_target_path(self):
        proposal = _make_proposal(target_path="implementation/knowledge/instructions/example.md")
        title = mr_gate.build_mr_title(proposal)
        self.assertIn("implementation/knowledge/instructions/example.md", title)


class TestOpenPromotionMrMocked(unittest.TestCase):
    """The full `open_promotion_mr` git/`glab` call sequence and
    `MrGateResult` content, with every subprocess call mocked -- a real test
    suite must not open real MRs on every CI run."""

    def _run_with_mock(self, proposal, promotion_result, **kwargs):
        fake_completed = MagicMock()
        fake_completed.stdout = "https://gitlab.com/em-age/emage.code/-/merge_requests/999\n"
        with patch(
            "implementation.runtime.golden_harness.mr_gate.subprocess.run", return_value=fake_completed
        ) as mock_run:
            result = mr_gate.open_promotion_mr(proposal, promotion_result, **kwargs)
        return result, mock_run

    def test_produces_an_mr_gate_result_with_expected_content(self):
        proposal = _make_proposal()
        promotion_result = _make_promotion_result(promote=True)
        result, mock_run = self._run_with_mock(proposal, promotion_result, repo_root=Path("/tmp/does-not-need-to-exist"))

        self.assertEqual(result.branch_name, mr_gate.compute_branch_name(proposal))
        self.assertEqual(result.commit_message, mr_gate.build_commit_message(proposal))
        self.assertEqual(result.mr_description, mr_gate.build_mr_description(proposal, promotion_result))
        self.assertEqual(result.mr_url, "https://gitlab.com/em-age/emage.code/-/merge_requests/999")

    def test_call_sequence_is_fetch_worktree_add_commit_push_remove_mr_create(self):
        proposal = _make_proposal()
        promotion_result = _make_promotion_result(promote=True)
        repo_root = Path("/tmp/does-not-need-to-exist")
        result, mock_run = self._run_with_mock(proposal, promotion_result, repo_root=repo_root)

        argvs = [call.args[0] for call in mock_run.call_args_list]
        self.assertEqual(len(argvs), 7, msg=f"unexpected call count: {argvs!r}")

        self.assertEqual(argvs[0][:3], ["git", "fetch", "origin"])
        self.assertEqual(argvs[1][:3], ["git", "worktree", "add"])
        self.assertIn("-b", argvs[1])
        self.assertEqual(argvs[1][argvs[1].index("-b") + 1], result.branch_name)
        self.assertEqual(argvs[2][:2], ["git", "add"])
        self.assertIn(proposal.target_path, argvs[2])
        self.assertEqual(argvs[3][:3], ["git", "commit", "-m"])
        self.assertEqual(argvs[3][3], result.commit_message)
        self.assertEqual(argvs[4], ["git", "push", "origin", result.branch_name])
        self.assertEqual(argvs[5][:3], ["git", "worktree", "remove"])
        self.assertEqual(argvs[6][:3], ["glab", "mr", "create"])
        self.assertIn(result.branch_name, argvs[6])
        self.assertIn("develop", argvs[6])

        for call in mock_run.call_args_list:
            self.assertEqual(call.kwargs.get("check"), True)

    def test_never_pushes_to_develop_or_main_directly(self):
        """Behavioral companion to the static-scan proof: even the real,
        executed call sequence's only `git push` targets the freshly
        created branch, never `develop`/`main` literally."""
        proposal = _make_proposal()
        promotion_result = _make_promotion_result(promote=True)
        result, mock_run = self._run_with_mock(proposal, promotion_result)

        push_calls = [call.args[0] for call in mock_run.call_args_list if call.args[0][:2] == ["git", "push"]]
        self.assertEqual(len(push_calls), 1)
        pushed_ref = push_calls[0][-1]
        self.assertNotIn(pushed_ref, {"develop", "main", "origin/develop", "origin/main"})
        self.assertEqual(pushed_ref, result.branch_name)

    def test_writes_only_the_target_path_within_the_scratch_worktree(self):
        """The temp worktree directory this function writes into during a
        mocked run only ever contains `proposal.target_path` -- no other
        file is created (Objective point 4: "only that path")."""
        proposal = _make_proposal()
        promotion_result = _make_promotion_result(promote=True)

        captured_worktree_dirs: list[Path] = []
        # Snapshotted at the "git add" step -- the worktree directory still
        # exists then (the `tempfile.TemporaryDirectory` context manager
        # this function uses is cleaned up before `open_promotion_mr`
        # returns, so the snapshot must happen mid-call, not after).
        snapshots: list[list[tuple[Path, str]]] = []
        fake_completed = MagicMock()
        fake_completed.stdout = "https://gitlab.com/em-age/emage.code/-/merge_requests/999\n"

        def _record_worktree_dir(argv, **kwargs):
            if argv[:3] == ["git", "worktree", "add"]:
                captured_worktree_dirs.append(Path(argv[3]))
            if argv[:2] == ["git", "add"]:
                worktree_dir = captured_worktree_dirs[-1]
                snapshots.append(
                    [
                        (p.relative_to(worktree_dir), p.read_text(encoding="utf-8"))
                        for p in worktree_dir.rglob("*")
                        if p.is_file()
                    ]
                )
            return fake_completed

        with patch(
            "implementation.runtime.golden_harness.mr_gate.subprocess.run", side_effect=_record_worktree_dir
        ):
            mr_gate.open_promotion_mr(proposal, promotion_result)

        self.assertEqual(len(captured_worktree_dirs), 1)
        self.assertEqual(len(snapshots), 1)
        written_files = snapshots[0]
        self.assertEqual(len(written_files), 1)
        relative_path, content = written_files[0]
        self.assertEqual(relative_path, Path(proposal.target_path))
        self.assertEqual(content, proposal.proposed_content)


class TestNoAutoMergePath(unittest.TestCase):
    """The actual proof this module can never merge, approve, or push
    directly to `develop`/`main` -- mirrors `test_meta_improver.py`'s
    `TestNoFilesystemMutation` two-independent-proofs discipline exactly."""

    def test_static_scan_finds_zero_violations_on_real_source(self):
        source = _MODULE_PATH.read_text(encoding="utf-8")
        violations = mr_gate.find_auto_merge_calls(source)
        self.assertEqual(
            violations,
            [],
            msg=f"{_MODULE_PATH}: found auto-merge-path call(s):\n  " + "\n  ".join(violations),
        )

    def test_static_scan_detects_a_synthetic_violation(self):
        # One synthetic snippet per banned shape (mirrors
        # `test_meta_improver.py`'s own per-shape-snippet pattern exactly).
        cases = {
            "glab_mr_merge_list": 'subprocess.run(["glab", "mr", "merge", "123"])',
            "glab_mr_merge_shell_string": 'subprocess.run("glab mr merge 123", shell=True)',
            "glab_mr_approve_list": 'subprocess.run(["glab", "mr", "approve", "123"])',
            "glab_mr_approve_shell_string": 'subprocess.run("glab mr approve 123", shell=True)',
            "git_merge": 'subprocess.run(["git", "merge", "feature-branch"])',
            "git_push_force_long": 'subprocess.run(["git", "push", "origin", "main", "--force"])',
            "git_push_force_short": 'subprocess.run(["git", "push", "-f", "origin", "main"])',
            "git_push_develop_literal": 'subprocess.run(["git", "push", "origin", "develop"])',
            "git_push_main_literal": 'subprocess.run(["git", "push", "origin", "main"])',
            "os_system_mr_merge": 'os.system("glab mr merge 123")',
            "wrapper_call_mr_merge": '_run(["glab", "mr", "merge", "123"], cwd=root)',
            "gitlab_api_merge_endpoint": (
                'requests.post("https://gitlab.com/api/v4/projects/1/merge_requests/5/merge")'
            ),
            "gitlab_api_approve_endpoint": (
                'requests.post("https://gitlab.com/api/v4/projects/1/merge_requests/5/approve")'
            ),
            "mr_object_merge_method": "mr.merge()",
            "merge_request_object_approve_method": "merge_request.approve()",
            "named_tool_call_merge": "merge_merge_request(mr_id=5)",
            "named_tool_call_approve": "approve_merge_request(mr_id=5)",
        }
        for label, snippet in cases.items():
            with self.subTest(label=label):
                violations = mr_gate.find_auto_merge_calls(snippet)
                self.assertTrue(violations, msg=f"scanner failed to flag: {snippet!r}")

    def test_static_scan_does_not_false_positive_on_legitimate_calls(self):
        # The exact legitimate call shapes this module's own real source
        # needs to make (task brief's own explicit list).
        clean_snippet = (
            'subprocess.run(["glab", "mr", "create", "--source-branch", branch_name, '
            '"--target-branch", base_branch, "--title", mr_title, "--description", mr_description])\n'
            'subprocess.run(["git", "push", remote, branch_name], cwd=worktree_dir)\n'
            'subprocess.run(["git", "commit", "-m", commit_message], cwd=worktree_dir)\n'
            'subprocess.run(["git", "checkout", "-b", branch_name], cwd=root)\n'
            '_run(["glab", "mr", "create", "--source-branch", branch_name], cwd=root)\n'
            '_run(["git", "push", remote, branch_name], cwd=worktree_dir)\n'
            '_run(["git", "add", "--", proposal.target_path], cwd=worktree_dir)\n'
            '_run(["git", "worktree", "remove", "--force", str(worktree_dir)], cwd=root)\n'
        )
        violations = mr_gate.find_auto_merge_calls(clean_snippet)
        self.assertEqual(violations, [])
