"""Live CWSO MCP contract snapshot checks for Task T201."""
from __future__ import annotations

import json
import unittest

from implementation.runtime.cwso.mcp_client import (
    CwsoHttpError,
    CwsoMcpClient,
    CwsoRpcError,
    live_contract_tests_enabled,
)
from tests._helpers.repo import repo_root


class TestCwsoMcpContractSnapshot(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not live_contract_tests_enabled():
            raise unittest.SkipTest("set CWSO_LIVE_CONTRACT_TEST=1 to run live MCP snapshot test")
        cls.client = CwsoMcpClient.from_env()

    def test_tools_list_matches_snapshot_for_orchestrator_and_worker(self):
        snapshot = json.loads(
            (
                repo_root()
                / "tests"
                / "fixtures"
                / "cwso"
                / "tools_list_snapshot_v1.json"
            ).read_text(encoding="utf-8")
        )
        expected_tools = sorted(snapshot["expectedTools"])

        orchestrator_tools = sorted(
            tool["name"] for tool in self.client.normalized_tools(self.client.list_tools(role="orchestrator"))
        )
        worker_tools = sorted(
            tool["name"] for tool in self.client.normalized_tools(self.client.list_tools(role="worker"))
        )

        self.assertEqual(orchestrator_tools, expected_tools)
        self.assertEqual(worker_tools, expected_tools)

    def test_planner_role_rejected_with_403(self):
        with self.assertRaises(CwsoHttpError) as context:
            self.client.list_tools(role="planner")
        self.assertEqual(context.exception.status_code, 403)
        self.assertIn("unrecognised role", context.exception.body)

    def test_orchestrator_cannot_call_worker_tier_commit_shadow(self):
        with self.assertRaises(CwsoRpcError) as context:
            self.client.call_tool(
                role="orchestrator",
                name="commit_shadow",
                arguments={
                    "workspace_uuid": "00000000-0000-0000-0000-000000000000",
                    "message": "permission-check",
                },
            )
        self.assertEqual(context.exception.code, -32002)
        self.assertIn('role "orchestrator" may not invoke tool "commit_shadow"', context.exception.message)


if __name__ == "__main__":
    unittest.main()
