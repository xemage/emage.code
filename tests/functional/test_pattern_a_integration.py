#!/usr/bin/env python3
"""Functional integration-style tests for Pattern A concurrent merge orchestration.

These tests validate multi-worker orchestration semantics with a mocked CWSO
client so they are deterministic and CI-friendly.
"""

from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from implementation.runtime.cwso.ast_conflict_check import (
    ConflictSeverity,
    PreCheckResult,
)
from implementation.runtime.cwso.client import MergeHeuristic, MergeLanguage
from implementation.runtime.cwso.concurrent_merge import (
    ConcurrentMergeOrchestrator,
    FileEdit,
    WorkerEditSet,
)


class TestPatternAIntegration(unittest.TestCase):
    """Validate end-to-end Pattern A orchestration flow with three workers."""

    def setUp(self) -> None:
        # The mock doesn't enforce role restrictions, so the same mock object
        # can stand in for both roles here.
        self.client = Mock()
        self.orchestrator = ConcurrentMergeOrchestrator(self.client, self.client)

    def _setup_workspace_lifecycle(self, worker_count: int) -> None:
        self.client.create_shadow_workspace.side_effect = [
            {
                "workspace_uuid": f"ws-{idx}",
                "base_tree_oid": f"base-{idx}",
            }
            for idx in range(worker_count)
        ]
        self.client.commit_shadow.side_effect = [
            {
                "commit_oid": f"c-{idx}",
                "tree_oid": f"t-{idx}",
            }
            for idx in range(worker_count)
        ]

    @staticmethod
    def _worker(agent_role: str, path: str, content: str) -> WorkerEditSet:
        return WorkerEditSet(
            agent_role=agent_role,
            commit_message=f"{agent_role} update",
            files=[
                FileEdit(
                    path=path,
                    content=content,
                    language=MergeLanguage.PYTHON,
                    base_content="def foo():\n    pass\n",
                )
            ],
        )

    def test_three_agent_independent_edits_merge_success(self) -> None:
        """Three independent edits (distinct paths) merge without unresolved conflicts.

        Note: paths are distinct per worker (rather than all three sharing
        "/main.py" as in the pre-BUG-F version of this test) because 3+
        workers editing the *same* path now raises ValueError (BUG-F fix,
        see test_cwso_concurrent_merge.py's dedicated collision regression
        test) instead of silently dropping the middle worker's edit.
        """
        self._setup_workspace_lifecycle(worker_count=3)
        self.client.merge_concurrent_results.return_value = {
            "merge_status": "success",
            "unresolved_conflicts": [],
        }

        workers = [
            self._worker("backend-developer", "/main.py", "def foo():\n    return 1\n"),
            self._worker("frontend-developer", "/baz.py", "def baz():\n    return 2\n"),
            self._worker("database-engineer", "/qux.py", "def qux():\n    return 3\n"),
        ]

        result = self.orchestrator.run(worker_edits=workers)

        self.assertEqual(result.merge_response["merge_status"], "success")
        self.assertEqual(len(result.audit_records), 3)
        self.assertEqual(len(result.unresolved_conflicts), 0)
        self.client.merge_concurrent_results.assert_called_once()
        self.client.drop_shadow_workspace.assert_any_call(workspace_uuid="ws-0")
        self.client.drop_shadow_workspace.assert_any_call(workspace_uuid="ws-1")
        self.client.drop_shadow_workspace.assert_any_call(workspace_uuid="ws-2")

    def test_precheck_is_invoked_when_enabled(self) -> None:
        """AST pre-check is executed when run_ast_precheck=True.

        Uses distinct paths per worker (see BUG-F note in
        test_three_agent_independent_edits_merge_success above) since
        `_build_merge_inputs` now raises for 3+ workers sharing a path, and
        that call happens before the pre-check runs.
        """
        self._setup_workspace_lifecycle(worker_count=3)
        self.client.merge_concurrent_results.return_value = {
            "merge_status": "success",
            "unresolved_conflicts": [],
        }

        workers = [
            self._worker("backend-developer", "/main.py", "def foo():\n    return 1\n"),
            self._worker("frontend-developer", "/baz.py", "def foo():\n    return 2\n"),
            self._worker("database-engineer", "/qux.py", "def foo():\n    return 3\n"),
        ]

        precheck_result = PreCheckResult(
            all_files=[],
            overall_severity=ConflictSeverity.LOW,
            file_heuristics={"/main.py": MergeHeuristic.AST_SEMANTIC_ONLY},
            files_with_conflicts=[],
            safe_to_merge=True,
            summary="safe",
        )

        with patch.object(
            self.orchestrator,
            "ast_precheck",
            return_value=precheck_result,
        ) as mock_precheck:
            self.orchestrator.run(
                worker_edits=workers,
                run_ast_precheck=True,
                base_workspace_uuid="base-ws",
            )

        mock_precheck.assert_called_once_with(
            file_paths=["/main.py", "/baz.py", "/qux.py"],
            base_workspace_uuid="base-ws",
            ours_workspace_uuid="ws-0",
            theirs_workspace_uuid="ws-1",
        )

    def test_conflicting_merge_is_reported(self) -> None:
        """Conflict responses are surfaced as structured unresolved conflicts.

        Reduced to two workers on the shared path (a conflict on a single
        path is inherently a 2-way base/ours/theirs concept, and 3+ workers
        on the same path now raises ValueError per BUG-F -- see the
        dedicated collision regression test in test_cwso_concurrent_merge.py).
        """
        self._setup_workspace_lifecycle(worker_count=2)
        self.client.merge_concurrent_results.return_value = {
            "merge_status": "conflict",
            "unresolved_conflicts": [
                {
                    "path": "/main.py",
                    "reason": "simultaneous_symbol_add",
                }
            ],
        }

        workers = [
            self._worker("backend-developer", "/main.py", "def helper():\n    return 1\n"),
            self._worker("frontend-developer", "/main.py", "def helper():\n    return 2\n"),
        ]

        result = self.orchestrator.run(worker_edits=workers)

        self.assertEqual(result.merge_response["merge_status"], "conflict")
        self.assertEqual(len(result.unresolved_conflicts), 1)
        self.assertEqual(result.unresolved_conflicts[0].path, "/main.py")
        self.assertEqual(
            result.unresolved_conflicts[0].reason,
            "simultaneous_symbol_add",
        )

    def test_merge_input_build_is_deterministic(self) -> None:
        """Identical worker inputs produce identical merge-input tuples.

        Uses distinct paths per worker (see BUG-F note above) since 3+
        workers sharing a path now raises ValueError instead of building a
        (silently lossy) merge input.
        """
        workers = [
            self._worker("backend-developer", "/main.py", "def foo():\n    return 1\n"),
            self._worker("frontend-developer", "/baz.py", "def baz():\n    return 2\n"),
            self._worker("database-engineer", "/qux.py", "def qux():\n    return 3\n"),
        ]

        first = ConcurrentMergeOrchestrator._build_merge_inputs(workers)
        second = ConcurrentMergeOrchestrator._build_merge_inputs(workers)

        first_projection = [
            (item.path, item.ours_content, item.theirs_content) for item in first
        ]
        second_projection = [
            (item.path, item.ours_content, item.theirs_content) for item in second
        ]

        self.assertEqual(first_projection, second_projection)


if __name__ == "__main__":
    unittest.main()
