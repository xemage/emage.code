#!/usr/bin/env python3
"""Unit tests for Task T212 concurrent merge orchestration."""

import unittest
from unittest.mock import Mock

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "implementation"))

from runtime.cwso.client import MergeHeuristic, MergeLanguage
from runtime.cwso.concurrent_merge import (
    ConcurrentMergeOrchestrator,
    FileEdit,
    WorkerEditSet,
)


class TestConcurrentMergeOrchestrator(unittest.TestCase):
    def setUp(self) -> None:
        self.client = Mock()
        self.orchestrator = ConcurrentMergeOrchestrator(self.client)

    def test_requires_at_least_two_workers(self) -> None:
        with self.assertRaises(ValueError):
            self.orchestrator.run(
                [
                    WorkerEditSet(
                        agent_role="backend-developer",
                        commit_message="single worker",
                        files=[FileEdit(path="/a.py", content="print(1)", language=MergeLanguage.PYTHON)],
                    )
                ]
            )

    def test_happy_path_generates_audit_and_merge(self) -> None:
        self.client.create_shadow_workspace.side_effect = [
            {"workspace_uuid": "ws-1", "base_tree_oid": "base-1"},
            {"workspace_uuid": "ws-2", "base_tree_oid": "base-2"},
        ]
        self.client.commit_shadow.side_effect = [
            {"commit_oid": "c1", "tree_oid": "t1"},
            {"commit_oid": "c2", "tree_oid": "t2"},
        ]
        self.client.merge_concurrent_results.return_value = {
            "outcome": "success",
            "results": [{"path": "/main.py", "status": "merged"}],
            "conflict_count": 0,
        }

        worker_edits = [
            WorkerEditSet(
                agent_role="backend-developer",
                commit_message="worker 1 changes",
                files=[FileEdit(path="/main.py", content="print('one')", language=MergeLanguage.PYTHON)],
            ),
            WorkerEditSet(
                agent_role="frontend-developer",
                commit_message="worker 2 changes",
                files=[FileEdit(path="/main.py", content="print('two')", language=MergeLanguage.PYTHON)],
            ),
        ]

        result = self.orchestrator.run(
            worker_edits=worker_edits,
            merge_heuristic=MergeHeuristic.AST_SEMANTIC_ONLY,
        )

        self.assertEqual(result.merge_response["outcome"], "success")
        self.assertEqual(len(result.audit_records), 2)
        self.assertEqual(len(result.unresolved_conflicts), 0)

        self.client.merge_concurrent_results.assert_called_once()
        self.client.drop_shadow_workspace.assert_any_call(workspace_uuid="ws-1")
        self.client.drop_shadow_workspace.assert_any_call(workspace_uuid="ws-2")

    def test_conflict_response_is_structured_real_results_shape(self) -> None:
        """_extract_conflicts parses the real 'outcome'/'results'-list shape."""
        self.client.create_shadow_workspace.side_effect = [
            {"workspace_uuid": "ws-1", "base_tree_oid": "base-1"},
            {"workspace_uuid": "ws-2", "base_tree_oid": "base-2"},
        ]
        self.client.commit_shadow.side_effect = [
            {"commit_oid": "c1", "tree_oid": "t1"},
            {"commit_oid": "c2", "tree_oid": "t2"},
        ]
        self.client.merge_concurrent_results.return_value = {
            "outcome": "conflict",
            "results": [
                {
                    "path": "/main.py",
                    "status": "conflict",
                    "reason_code": "SEMANTIC_CONFLICT",
                    "message": "semantic_conflict",
                },
            ],
            "conflict_count": 1,
        }

        worker_edits = [
            WorkerEditSet(
                agent_role="backend-developer",
                commit_message="worker 1 changes",
                files=[FileEdit(path="/main.py", content="print('a')", language=MergeLanguage.PYTHON)],
            ),
            WorkerEditSet(
                agent_role="frontend-developer",
                commit_message="worker 2 changes",
                files=[FileEdit(path="/main.py", content="print('b')", language=MergeLanguage.PYTHON)],
            ),
        ]

        result = self.orchestrator.run(worker_edits=worker_edits)

        self.assertEqual(len(result.unresolved_conflicts), 1)
        self.assertEqual(result.unresolved_conflicts[0].path, "/main.py")
        self.assertEqual(result.unresolved_conflicts[0].reason, "semantic_conflict")

    def test_conflict_extraction_falls_back_to_reason_code_when_message_absent(self) -> None:
        """When 'message' is absent, use 'reason_code' as the reason."""
        merge_response = {
            "outcome": "conflict",
            "results": [
                {"path": "/a.py", "status": "conflict", "reason_code": "ARITY_MISMATCH"},
                {"path": "/b.py", "status": "merged"},
            ],
            "conflict_count": 1,
        }

        conflicts = self.orchestrator._extract_conflicts(merge_response)

        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].path, "/a.py")
        self.assertEqual(conflicts[0].reason, "ARITY_MISMATCH")

    def test_conflict_extraction_only_includes_conflict_status_entries(self) -> None:
        """Entries with status 'merged' are not treated as conflicts."""
        merge_response = {
            "outcome": "success",
            "results": [
                {"path": "/a.py", "status": "merged"},
                {"path": "/b.py", "status": "merged"},
            ],
            "conflict_count": 0,
        }

        conflicts = self.orchestrator._extract_conflicts(merge_response)

        self.assertEqual(conflicts, [])

    def test_conflict_extraction_legacy_unresolved_conflicts_fallback(self) -> None:
        """Defensive fallback: old top-level 'unresolved_conflicts' shape still parses."""
        merge_response = {
            "merge_status": "conflict",
            "unresolved_conflicts": [
                {"path": "/main.py", "reason": "semantic_conflict"},
            ],
        }

        conflicts = self.orchestrator._extract_conflicts(merge_response)

        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].path, "/main.py")
        self.assertEqual(conflicts[0].reason, "semantic_conflict")


if __name__ == "__main__":
    unittest.main()
