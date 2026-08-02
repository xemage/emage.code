#!/usr/bin/env python3
"""Live Pattern A 4-scenario integration test for CWSO (Task T214).

Runs the four scenarios from docs/tasks/task-T214.md's Acceptance Criteria
(as re-confirmed binding by the "Addendum (Plan 016, 2026-07-31)" section)
against the REAL, LIVE CWSO stack (deploy/docker-compose-t226.yml) via the
real MCP endpoint, using the already-implemented CwsoClient,
AstConflictChecker, and merge_concurrent_results/MergeInput primitives.

This file follows the same live-gating convention as
tests/functional/test_cwso_client_live.py: tests are skipped unless
CWSO_LIVE_CONTRACT_TEST=1 is set, and CwsoClient.from_env() is used to read
CWSO_JWT_SECRET / CWSO_BASE_URL from the environment (the JWT secret is
never printed, logged, or persisted by this file).

To run (against a healthy live stack):
    export CWSO_LIVE_CONTRACT_TEST=1
    python3 tests/functional/test_pattern_a_integration_live.py -v
    # or: pytest -s tests/functional/test_pattern_a_integration_live.py

IMPORTANT -- role split required by the live server's permission model
(confirmed empirically, see Finding BUG-A in task-T214.md's execution
notes): a single-role CwsoClient CANNOT run this whole flow. 'worker' may
create/write/commit/query_ast/drop shadow workspaces but may NOT call
merge_concurrent_results; 'orchestrator' may create workspaces, call
merge_concurrent_results, and drop workspaces, but may NOT write_shadow_file
or commit_shadow. This test therefore builds two role-scoped CwsoClient
instances from one shared JWT secret.

This test file intentionally asserts against the DOCUMENTED acceptance
criteria in task-T214.md (e.g. pre-check severity MEDIUM/HIGH for scenarios
2/3), not against whatever the current (possibly buggy) library code
actually returns. Where the real, live behavior does not match the
documented AC, the assertion is expected to fail -- this is the correct,
honest regression-test signal for the underlying defect, per the project's
anti-fabrication rule (no weakening ACs to force a pass). Every real
API response is printed to stdout as it is captured, so evidence is visible
in the test log regardless of which assertions pass or fail. All shadow
workspaces created by every scenario are dropped in a `finally` block, so
no workspace is left orphaned even when an assertion fails partway through
a scenario.
"""

from __future__ import annotations

import os
import re
import sys
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "implementation"))
# ast_conflict_check.py (T213) uses an absolute `from implementation.runtime.cwso...`
# import internally (inconsistent with the rest of the package's relative-import
# style -- see task-T214.md Finding "BUG-H: dual module identity"), so the repo
# root must ALSO be on sys.path for that module to import successfully.
sys.path.insert(0, str(_REPO_ROOT))

from runtime.cwso.client import (  # noqa: E402
    CwsoClient,
    MergeHeuristic,
    MergeInput,
    MergeLanguage,
)
from runtime.cwso.ast_conflict_check import AstConflictChecker, ConflictSeverity  # noqa: E402


def requires_cwso_live_test(test):
    """Decorator to skip tests if CWSO live testing is not enabled."""
    if not os.getenv("CWSO_LIVE_CONTRACT_TEST"):
        return unittest.skip("CWSO_LIVE_CONTRACT_TEST not set")(test)
    return test


def _banner(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


class TestPatternAIntegrationLive(unittest.TestCase):
    """Pattern A (T214) 4-scenario live integration suite."""

    @classmethod
    def setUpClass(cls):
        try:
            env_client = CwsoClient.from_env()
        except Exception as e:  # pragma: no cover - environment guard
            raise unittest.SkipTest(f"Could not build CwsoClient from environment: {e}")

        # Never print/log the secret itself -- only pass it in-memory.
        secret = (
            env_client._mcp._secret.decode("utf-8")
            if isinstance(env_client._mcp._secret, bytes)
            else str(env_client._mcp._secret)
        )
        base_url = env_client._mcp.base_url

        cls.worker = CwsoClient(jwt_secret=secret, role="worker", base_url=base_url)
        cls.orch = CwsoClient(jwt_secret=secret, role="orchestrator", base_url=base_url)
        cls.checker = AstConflictChecker(cls.worker)

    # ------------------------------------------------------------------
    # Helpers (all print real, literal evidence as they execute)
    # ------------------------------------------------------------------

    def _create_ws(self, label: str) -> str:
        resp = self.worker.create_shadow_workspace()
        workspace_uuid = str(resp["workspace_uuid"])
        print(f"  create_shadow_workspace[{label}] -> workspace_uuid={workspace_uuid} "
              f"base_tree_oid={resp.get('base_tree_oid')!r}")
        return workspace_uuid

    @staticmethod
    def _extract_blob_oid(write_resp: dict) -> str | None:
        """Extract blob_oid from a write_shadow_file response.

        NOTE (real finding -- see task-T214.md evidence, "BUG-E"): the live
        server returns a *non-JSON* plain-text message for write_shadow_file
        ("wrote N bytes (blob <oid>)") wrapped in the standard MCP envelope.
        CwsoMcpClient._unwrap_tool_result only unwraps `content[0]["text"]`
        when it parses as JSON, so for this tool the raw envelope is
        returned unchanged and there is no top-level 'blob_oid' key --
        contradicting CwsoClient.write_shadow_file's own docstring
        ("Returns: Dict with 'blob_oid' key"). We parse it out of the text
        message here purely to capture the requested evidence.
        """
        if "blob_oid" in write_resp:
            return write_resp["blob_oid"]
        try:
            text = write_resp["content"][0]["text"]
            match = re.search(r"\(blob ([0-9a-f]+)\)", text)
            if match:
                return match.group(1)
        except Exception:
            pass
        return None

    def _write(self, ws: str, label: str, path: str, content: str) -> str | None:
        resp = self.worker.write_shadow_file(ws, path, content)
        blob_oid = self._extract_blob_oid(resp)
        print(f"  write_shadow_file[{label}] path={path!r} -> raw={resp!r} "
              f"parsed_blob_oid={blob_oid}")
        return blob_oid

    def _commit(self, ws: str, label: str, message: str) -> dict:
        resp = self.worker.commit_shadow(ws, message)
        print(f"  commit_shadow[{label}] -> commit_oid={resp.get('commit_oid')} "
              f"tree_oid={resp.get('tree_oid')}")
        return resp

    def _drop(self, ws: str, label: str) -> dict:
        resp = self.worker.drop_shadow_workspace(ws)
        print(f"  drop_shadow_workspace[{label}] uuid={ws} -> {resp!r}")
        return resp

    def _drop_all(self, workspaces: dict[str, str]) -> None:
        for label, ws in workspaces.items():
            try:
                self._drop(ws, label)
            except Exception as e:  # pragma: no cover - cleanup best-effort
                print(f"  drop_shadow_workspace[{label}] uuid={ws} -> ERROR: {e}")

    def _precheck(self, label: str, paths: list[str], base_ws: str, ours_ws: str, theirs_ws: str):
        result = self.checker.run(
            file_paths=paths, base_workspace=base_ws, ours_workspace=ours_ws, theirs_workspace=theirs_ws
        )
        print(f"  AST precheck[{label}] overall_severity={result.overall_severity.value} "
              f"safe_to_merge={result.safe_to_merge} summary={result.summary!r}")
        for fa in result.all_files:
            print(f"    path={fa.path} base_symbols={sorted(fa.base_symbols)} "
                  f"ours_symbols={sorted(fa.ours_symbols)} theirs_symbols={sorted(fa.theirs_symbols)} "
                  f"diverging_symbols={fa.diverging_symbols} "
                  f"conflicting_edits={fa.conflicting_edits} "
                  f"severity={fa.severity.value} recommended_heuristic={fa.recommended_heuristic.value}")
        return result

    def _merge(self, label: str, source_uuids: list[str], merge_inputs: list[MergeInput],
               heuristic: MergeHeuristic, target_branch_ref: str) -> dict:
        resp = self.orch.merge_concurrent_results(
            source_workspace_uuids=source_uuids,
            merge_inputs=merge_inputs,
            auto_resolve_heuristic=heuristic,
            target_branch_ref=target_branch_ref,
        )
        print(f"  merge_concurrent_results[{label}] heuristic={heuristic.value} -> {resp!r}")
        return resp

    # ------------------------------------------------------------------
    # Scenario 1: Independent edits (LOW severity -> merge success)
    # ------------------------------------------------------------------

    @requires_cwso_live_test
    def test_scenario_1_independent_edits_low_severity_merge_success(self):
        _banner("SCENARIO 1: Independent edits (3 agents) -- expect LOW severity, clean merge")
        path = "scenario1/ops.py"
        baseline = "def foo(): pass\ndef bar(): pass\n"
        content_a = "def foo(): return 1\ndef bar(): pass\n"  # A: modify foo only
        content_b = "def foo(): pass\ndef bar(): pass\ndef baz(): return 2\n"  # B: add baz
        content_c = "def foo(): pass\ndef bar(): pass\ndef qux(): return 3\n"  # C: add qux

        workspaces: dict[str, str] = {}
        try:
            workspaces["base"] = self._create_ws("base")
            workspaces["A"] = self._create_ws("A")
            workspaces["B"] = self._create_ws("B")
            workspaces["C"] = self._create_ws("C")

            self._write(workspaces["base"], "base", path, baseline)
            self._commit(workspaces["base"], "base", "baseline: foo+bar")

            self._write(workspaces["A"], "A", path, content_a)
            self._commit(workspaces["A"], "A", "agent A: modify foo body")

            self._write(workspaces["B"], "B", path, content_b)
            self._commit(workspaces["B"], "B", "agent B: add baz")

            self._write(workspaces["C"], "C", path, content_c)
            self._commit(workspaces["C"], "C", "agent C: add qux")

            print("\n-- Pairwise AST pre-check (3 agents => 3 pairs) --")
            precheck_ab = self._precheck("A-vs-B", [path], workspaces["base"], workspaces["A"], workspaces["B"])
            precheck_ac = self._precheck("A-vs-C", [path], workspaces["base"], workspaces["A"], workspaces["C"])
            precheck_bc = self._precheck("B-vs-C", [path], workspaces["base"], workspaces["B"], workspaces["C"])

            print("\n-- Merge (composed as two real 2-way merge_concurrent_results calls, "
                  "since the live merge_concurrent_results/MergeInput schema is base/ours/theirs "
                  "i.e. strictly 2-way; see task-T214.md Finding BUG-F for why "
                  "ConcurrentMergeOrchestrator itself cannot be used unmodified for a 3-way case) --")

            step1_heuristic = precheck_ab.file_heuristics.get(path, MergeHeuristic.AST_SEMANTIC_ONLY)
            mi_step1 = MergeInput(
                path=path, language=MergeLanguage.PYTHON,
                base_content=baseline, ours_content=content_a, theirs_content=content_b,
            )
            resp1 = self._merge(
                "step1(A+B)", [workspaces["A"], workspaces["B"]], [mi_step1],
                step1_heuristic, "refs/heads/t214-scenario1-step1",
            )
            self.assertEqual(resp1.get("outcome"), "success", f"step1 merge did not succeed: {resp1}")
            merged_ab = resp1["results"][0]["merged_content"]
            print(f"  step1 merged_content: {merged_ab!r}")

            step2_heuristic = precheck_ac.file_heuristics.get(path, MergeHeuristic.AST_SEMANTIC_ONLY)
            mi_step2 = MergeInput(
                path=path, language=MergeLanguage.PYTHON,
                base_content=baseline, ours_content=merged_ab, theirs_content=content_c,
            )
            resp2 = self._merge(
                "step2((A+B)+C)", [workspaces["B"], workspaces["C"]], [mi_step2],
                step2_heuristic, "refs/heads/t214-scenario1-step2",
            )
            self.assertEqual(resp2.get("outcome"), "success", f"step2 merge did not succeed: {resp2}")
            final_content = resp2["results"][0]["merged_content"]
            print(f"  FINAL merged content (all 3 agents): {final_content!r}")

            for symbol in ("def foo(): return 1", "def bar(): pass", "def baz(): return 2", "def qux(): return 3"):
                self.assertIn(symbol, final_content, f"expected symbol text {symbol!r} missing from final merge")

            # Documented AC: pre-check severity LOW for all 3 pairs (this genuinely holds,
            # since these edits really are independent and the bug in AstConflictChecker's
            # empty-symbol-set fallback happens to coincide with the correct LOW answer here).
            for label, precheck in (("A-vs-B", precheck_ab), ("A-vs-C", precheck_ac), ("B-vs-C", precheck_bc)):
                self.assertEqual(
                    precheck.overall_severity, ConflictSeverity.LOW,
                    f"expected LOW severity for {label}, got {precheck.overall_severity}",
                )
        finally:
            self._drop_all(workspaces)

    # ------------------------------------------------------------------
    # Scenario 2: Simultaneous same-symbol addition (MEDIUM -> blocked)
    # ------------------------------------------------------------------

    @requires_cwso_live_test
    def test_scenario_2_simultaneous_symbol_addition_medium_severity_blocked(self):
        _banner("SCENARIO 2: Simultaneous same-symbol addition -- expect MEDIUM severity, merge blocked")
        path = "scenario2/helper_mod.py"
        baseline = "def foo(): pass\n"
        content_a = "def foo(): pass\ndef helper(): return 1\n"
        content_b = "def foo(): pass\ndef helper(): return 2\n"

        workspaces: dict[str, str] = {}
        try:
            workspaces["base"] = self._create_ws("base")
            workspaces["A"] = self._create_ws("A")
            workspaces["B"] = self._create_ws("B")

            self._write(workspaces["base"], "base", path, baseline)
            self._commit(workspaces["base"], "base", "baseline: foo only")

            self._write(workspaces["A"], "A", path, content_a)
            self._commit(workspaces["A"], "A", "agent A: add helper() return 1")

            self._write(workspaces["B"], "B", path, content_b)
            self._commit(workspaces["B"], "B", "agent B: add helper() return 2")

            precheck = self._precheck("A-vs-B", [path], workspaces["base"], workspaces["A"], workspaces["B"])
            heuristic = precheck.file_heuristics.get(path, MergeHeuristic.AST_SEMANTIC_ONLY)

            mi = MergeInput(
                path=path, language=MergeLanguage.PYTHON,
                base_content=baseline, ours_content=content_a, theirs_content=content_b,
            )
            resp = self._merge(
                "scenario2", [workspaces["A"], workspaces["B"]], [mi],
                heuristic, "refs/heads/t214-scenario2",
            )

            # This part of the AC genuinely holds against the live stack: the server's
            # own semantic merge engine independently detects and blocks this conflict
            # regardless of which client-chosen heuristic is passed (confirmed by a
            # side experiment with both AST_SEMANTIC_ONLY and FAIL_RAPIDLY_ON_CONFLICT
            # -- see task-T214.md Finding notes).
            self.assertEqual(resp.get("outcome"), "conflict", f"expected merge to be blocked, got: {resp}")
            file_result = resp["results"][0]
            self.assertEqual(file_result.get("status"), "conflict")
            print(f"  ACTUAL conflict reason text (verbatim): {file_result.get('message')!r} "
                  f"reason_code={file_result.get('reason_code')!r}")

            # Documented AC: pre-check severity MEDIUM ("both add same symbol").
            # EXPECTED TO FAIL against the live stack -- see task-T214.md Finding
            # BUG-B/BUG-C: AstConflictChecker._query_exports()/_query_signatures()
            # look for result["exports"]/result["signature"], but the live server's
            # query_ast response shape is {"hits": [...]}; the checker therefore
            # always sees empty symbol sets and reports LOW regardless of real content.
            self.assertEqual(
                precheck.overall_severity, ConflictSeverity.MEDIUM,
                f"expected MEDIUM severity per task-T214.md AC, got {precheck.overall_severity} "
                f"(this mismatch is the real, live-confirmed AstConflictChecker defect -- "
                f"see BUG-B/BUG-C in task-T214.md)",
            )
        finally:
            self._drop_all(workspaces)

    # ------------------------------------------------------------------
    # Scenario 3: Diverging function signatures (HIGH -> blocked)
    # ------------------------------------------------------------------

    @requires_cwso_live_test
    def test_scenario_3_diverging_signatures_high_severity_blocked(self):
        _banner("SCENARIO 3: Diverging function signatures -- expect HIGH severity, merge blocked")
        path = "scenario3/compute_mod.py"
        baseline = "def compute(x): return x * 2\n"
        content_a = "def compute(x, y): return x * y\n"  # A: arity changes
        content_b = "def compute(x): return x + 1\n"  # B: body only, same arity

        workspaces: dict[str, str] = {}
        try:
            workspaces["base"] = self._create_ws("base")
            workspaces["A"] = self._create_ws("A")
            workspaces["B"] = self._create_ws("B")

            self._write(workspaces["base"], "base", path, baseline)
            self._commit(workspaces["base"], "base", "baseline: compute(x)")

            self._write(workspaces["A"], "A", path, content_a)
            self._commit(workspaces["A"], "A", "agent A: compute(x, y) arity change")

            self._write(workspaces["B"], "B", path, content_b)
            self._commit(workspaces["B"], "B", "agent B: compute(x) body change")

            precheck = self._precheck("A-vs-B", [path], workspaces["base"], workspaces["A"], workspaces["B"])
            heuristic = precheck.file_heuristics.get(path, MergeHeuristic.AST_SEMANTIC_ONLY)

            mi = MergeInput(
                path=path, language=MergeLanguage.PYTHON,
                base_content=baseline, ours_content=content_a, theirs_content=content_b,
            )
            resp = self._merge(
                "scenario3", [workspaces["A"], workspaces["B"]], [mi],
                heuristic, "refs/heads/t214-scenario3",
            )

            self.assertEqual(resp.get("outcome"), "conflict", f"expected merge to be blocked, got: {resp}")
            file_result = resp["results"][0]
            self.assertEqual(file_result.get("status"), "conflict")
            print(f"  ACTUAL conflict reason text (verbatim): {file_result.get('message')!r} "
                  f"reason_code={file_result.get('reason_code')!r}")

            # Documented AC: pre-check severity HIGH ("diverging signatures").
            # EXPECTED TO FAIL against the live stack for the same reason as Scenario 2
            # (BUG-B/BUG-C): the checker never sees real symbol/signature data from the
            # live query_ast response shape, so it can never detect a diverging signature.
            self.assertEqual(
                precheck.overall_severity, ConflictSeverity.HIGH,
                f"expected HIGH severity per task-T214.md AC, got {precheck.overall_severity} "
                f"(real, live-confirmed AstConflictChecker defect -- see BUG-B/BUG-C in task-T214.md)",
            )
        finally:
            self._drop_all(workspaces)

    # ------------------------------------------------------------------
    # Scenario 4: Multi-file, mixed severities in one merge_concurrent_results call
    # ------------------------------------------------------------------

    @requires_cwso_live_test
    def test_scenario_4_multi_file_mixed_severities(self):
        _banner("SCENARIO 4: Multi-file mixed severities -- File1 LOW/merges, File2 MEDIUM/blocked, ONE merge call")
        path1 = "scenario4/file1.py"
        path2 = "scenario4/file2.py"

        base1 = "def foo(): pass\ndef bar(): pass\n"
        a1 = "def foo(): return 1\ndef bar(): pass\n"
        b1 = "def foo(): pass\ndef bar(): pass\ndef baz(): return 2\n"

        base2 = "def qux(): pass\n"
        a2 = "def qux(): pass\ndef helper(): return 1\n"
        b2 = "def qux(): pass\ndef helper(): return 2\n"

        workspaces: dict[str, str] = {}
        try:
            workspaces["base"] = self._create_ws("base")
            workspaces["A"] = self._create_ws("A")
            workspaces["B"] = self._create_ws("B")

            self._write(workspaces["base"], "base/file1", path1, base1)
            self._write(workspaces["base"], "base/file2", path2, base2)
            self._commit(workspaces["base"], "base", "baseline: file1+file2")

            self._write(workspaces["A"], "A/file1", path1, a1)
            self._write(workspaces["A"], "A/file2", path2, a2)
            self._commit(workspaces["A"], "A", "agent A: file1 modify foo, file2 add helper()->1")

            self._write(workspaces["B"], "B/file1", path1, b1)
            self._write(workspaces["B"], "B/file2", path2, b2)
            self._commit(workspaces["B"], "B", "agent B: file1 add baz, file2 add helper()->2")

            precheck = self._precheck(
                "A-vs-B (both files)", [path1, path2], workspaces["base"], workspaces["A"], workspaces["B"]
            )
            heuristic_file1 = precheck.file_heuristics.get(path1, MergeHeuristic.AST_SEMANTIC_ONLY)
            heuristic_file2 = precheck.file_heuristics.get(path2, MergeHeuristic.AST_SEMANTIC_ONLY)
            # merge_concurrent_results takes a single auto_resolve_heuristic for the whole
            # call (not per-file); use File 2's recommendation (the more conservative of
            # the two) so the call is routed per the pre-check's own logic.
            call_heuristic = heuristic_file2

            mi1 = MergeInput(path=path1, language=MergeLanguage.PYTHON, base_content=base1, ours_content=a1, theirs_content=b1)
            mi2 = MergeInput(path=path2, language=MergeLanguage.PYTHON, base_content=base2, ours_content=a2, theirs_content=b2)

            resp = self._merge(
                "scenario4", [workspaces["A"], workspaces["B"]], [mi1, mi2],
                call_heuristic, "refs/heads/t214-scenario4",
            )

            print(f"  merged_count={resp.get('merged_count')} conflict_count={resp.get('conflict_count')} "
                  f"outcome={resp.get('outcome')}")
            results_by_path = {r["path"]: r for r in resp.get("results", [])}
            self.assertIn(path1, results_by_path)
            self.assertIn(path2, results_by_path)

            print(f"  File1 ({path1}) result: {results_by_path[path1]!r}")
            print(f"  File2 ({path2}) result: {results_by_path[path2]!r}")

            self.assertEqual(results_by_path[path1].get("status"), "merged",
                              f"expected File1 to merge cleanly, got: {results_by_path[path1]}")
            self.assertEqual(results_by_path[path2].get("status"), "conflict",
                              f"expected File2 to be blocked, got: {results_by_path[path2]}")

            # Documented AC (per-file pre-check severities): File1 LOW (holds), File2
            # MEDIUM (EXPECTED TO FAIL live -- same BUG-B/BUG-C root cause as Scenarios 2/3).
            file1_analysis = next(fa for fa in precheck.all_files if fa.path == path1)
            file2_analysis = next(fa for fa in precheck.all_files if fa.path == path2)
            self.assertEqual(file1_analysis.severity, ConflictSeverity.LOW)
            self.assertEqual(
                file2_analysis.severity, ConflictSeverity.MEDIUM,
                f"expected File2 MEDIUM severity per task-T214.md AC, got {file2_analysis.severity} "
                f"(real, live-confirmed AstConflictChecker defect -- see BUG-B/BUG-C in task-T214.md)",
            )
        finally:
            self._drop_all(workspaces)


if __name__ == "__main__":
    unittest.main(verbosity=2)
