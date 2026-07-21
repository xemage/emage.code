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
            "merge_status": "success",
            "unresolved_conflicts": [],
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

        self.assertEqual(result.merge_response["merge_status"], "success")
        self.assertEqual(len(result.audit_records), 2)
        self.assertEqual(len(result.unresolved_conflicts), 0)

        self.client.merge_concurrent_results.assert_called_once()
        self.client.drop_shadow_workspace.assert_any_call(workspace_uuid="ws-1")
        self.client.drop_shadow_workspace.assert_any_call(workspace_uuid="ws-2")

    def test_conflict_response_is_structured(self) -> None:
        self.client.create_shadow_workspace.side_effect = [
            {"workspace_uuid": "ws-1", "base_tree_oid": "base-1"},
            {"workspace_uuid": "ws-2", "base_tree_oid": "base-2"},
        ]
        self.client.commit_shadow.side_effect = [
            {"commit_oid": "c1", "tree_oid": "t1"},
            {"commit_oid": "c2", "tree_oid": "t2"},
        ]
        self.client.merge_concurrent_results.return_value = {
            "merge_status": "conflict",
            "unresolved_conflicts": [
                {"path": "/main.py", "reason": "semantic_conflict"},
            ],
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


if __name__ == "__main__":
    unittest.main()
