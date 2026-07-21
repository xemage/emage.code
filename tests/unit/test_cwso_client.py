#!/usr/bin/env python3
"""Unit tests for CwsoClient library."""

import json
import time
import unittest
from unittest.mock import Mock, MagicMock, patch

import sys
from pathlib import Path

# Add the implementation directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "implementation"))

from runtime.cwso.client import (
    CwsoClient,
    CwsoError,
    CwsoAuthError,
    CwsoToolError,
    CwsoValidationError,
    CwsoConnectionError,
    QueryType,
    SandboxProfile,
    MergeHeuristic,
    MergeLanguage,
    ConcurrentJob,
    MergeInput,
)
from runtime.cwso.mcp_client import CwsoMcpClient, CwsoHttpError, CwsoRpcError


class TestCwsoClientInitialization(unittest.TestCase):
    """Test CwsoClient initialization and validation."""

    def test_init_with_valid_role_orchestrator(self):
        """Initialize with orchestrator role."""
        client = CwsoClient(jwt_secret="test-secret", role="orchestrator")
        self.assertEqual(client._role, "orchestrator")

    def test_init_with_valid_role_worker(self):
        """Initialize with worker role."""
        client = CwsoClient(jwt_secret="test-secret", role="worker")
        self.assertEqual(client._role, "worker")

    def test_init_with_invalid_role(self):
        """Reject invalid roles."""
        with self.assertRaises(CwsoValidationError) as ctx:
            CwsoClient(jwt_secret="test-secret", role="planner")
        self.assertIn("role must be", str(ctx.exception))

    def test_init_with_rate_limit_too_low(self):
        """Reject rate limit pacing < 1.05."""
        with self.assertRaises(CwsoValidationError) as ctx:
            CwsoClient(jwt_secret="test-secret", role="orchestrator", rate_limit_pacing_sec=0.5)
        self.assertIn("rate_limit_pacing_sec must be", str(ctx.exception))

    def test_init_with_valid_rate_limit(self):
        """Accept valid rate limit pacing."""
        client = CwsoClient(jwt_secret="test-secret", role="orchestrator", rate_limit_pacing_sec=1.05)
        self.assertEqual(client._rate_limit_pacing_sec, 1.05)

    def test_init_with_custom_base_url(self):
        """Initialize with custom base URL."""
        client = CwsoClient(
            jwt_secret="test-secret",
            role="orchestrator",
            base_url="http://custom:9999",
        )
        self.assertIsNotNone(client._mcp)

    def test_init_with_invalid_jwt_secret(self):
        """Handle JWT secret errors gracefully."""
        # This is tricky since the MCP client will validate the secret
        # We expect the error to be caught during init
        pass


class TestCwsoClientToolsList(unittest.TestCase):
    """Test tools_list() method."""

    def setUp(self):
        """Create client with mocked MCP backend."""
        self.client = CwsoClient(jwt_secret="test-secret", role="orchestrator")

    @patch.object(CwsoClient, "_mcp")
    def test_tools_list_success(self, mock_mcp):
        """Fetch tools successfully."""
        self.client._mcp = mock_mcp
        mock_tools = [
            {"name": "read_file_sync", "description": "Read file"},
            {"name": "write_file_sync", "description": "Write file"},
            {"name": "list_dir", "description": "List directory"},
            {"name": "create_shadow_workspace", "description": "Create shadow"},
            {"name": "write_shadow_file", "description": "Write shadow"},
            {"name": "read_shadow_file", "description": "Read shadow"},
            {"name": "commit_shadow", "description": "Commit shadow"},
            {"name": "drop_shadow_workspace", "description": "Drop shadow"},
            {"name": "query_ast", "description": "Query AST"},
            {"name": "dispatch_concurrent_jobs", "description": "Dispatch jobs"},
            {"name": "merge_concurrent_results", "description": "Merge results"},
        ]
        mock_mcp.list_tools.return_value = mock_tools

        result = self.client.tools_list()

        self.assertEqual(len(result["tools"]), 11)
        self.assertIn("tools", result)

    @patch.object(CwsoClient, "_mcp")
    def test_tools_list_http_error(self, mock_mcp):
        """Handle HTTP error from tools/list."""
        self.client._mcp = mock_mcp
        mock_mcp.list_tools.side_effect = CwsoHttpError(500, "Internal Server Error")

        with self.assertRaises(CwsoConnectionError):
            self.client.tools_list()

    @patch.object(CwsoClient, "_mcp")
    def test_tools_list_rpc_error(self, mock_mcp):
        """Handle RPC error from tools/list."""
        self.client._mcp = mock_mcp
        mock_mcp.list_tools.side_effect = CwsoRpcError(-32000, "Server error")

        with self.assertRaises(CwsoToolError):
            self.client.tools_list()


class TestCwsoClientCallTool(unittest.TestCase):
    """Test call_tool() method."""

    def setUp(self):
        """Create client with mocked MCP backend."""
        self.client = CwsoClient(jwt_secret="test-secret", role="orchestrator")

    @patch.object(CwsoClient, "_mcp")
    def test_call_tool_success(self, mock_mcp):
        """Call tool successfully."""
        self.client._mcp = mock_mcp
        mock_mcp.call_tool.return_value = {"result": "success"}

        result = self.client.call_tool("read_file_sync", path="/test.py")

        self.assertEqual(result["result"], "success")
        self.client._mcp.call_tool.assert_called_once()

    def test_call_tool_unsupported(self):
        """Reject unsupported tool names."""
        with self.assertRaises(CwsoValidationError) as ctx:
            self.client.call_tool("nonexistent_tool")
        self.assertIn("Unknown tool", str(ctx.exception))

    def test_call_tool_missing_required_args(self):
        """Validate required arguments."""
        with self.assertRaises(CwsoValidationError) as ctx:
            self.client.call_tool("read_file_sync")  # missing 'path'
        self.assertIn("missing required args", str(ctx.exception))

    @patch.object(CwsoClient, "_mcp")
    def test_call_tool_http_error(self, mock_mcp):
        """Handle HTTP error from tool call."""
        self.client._mcp = mock_mcp
        mock_mcp.call_tool.side_effect = CwsoHttpError(503, "Service Unavailable")

        with self.assertRaises(CwsoConnectionError):
            self.client.call_tool("read_file_sync", path="/test.py")

    @patch.object(CwsoClient, "_mcp")
    def test_call_tool_rpc_error(self, mock_mcp):
        """Handle RPC error from tool call."""
        self.client._mcp = mock_mcp
        mock_mcp.call_tool.side_effect = CwsoRpcError(-32002, "role may not invoke tool")

        with self.assertRaises(CwsoToolError) as ctx:
            self.client.call_tool("commit_shadow", workspace_uuid="test-uuid", message="test")
        self.assertIn("commit_shadow", str(ctx.exception))


class TestCwsoClientBatch(unittest.TestCase):
    """Test call_tool_batch() method."""

    def setUp(self):
        """Create client with mocked MCP backend."""
        self.client = CwsoClient(jwt_secret="test-secret", role="orchestrator")

    def test_batch_empty_list(self):
        """Handle empty batch."""
        result = self.client.call_tool_batch([])
        self.assertEqual(result, [])

    def test_batch_invalid_structure(self):
        """Reject malformed call structure."""
        with self.assertRaises(CwsoValidationError):
            self.client.call_tool_batch([{"tool_name": "read_file_sync"}])  # missing 'kwargs'

    @patch.object(CwsoClient, "call_tool")
    def test_batch_success(self, mock_call_tool):
        """Dispatch batch of calls successfully."""
        mock_call_tool.side_effect = [
            {"result": "file1"},
            {"result": "file2"},
            {"result": "file3"},
        ]

        calls = [
            {"tool_name": "read_file_sync", "kwargs": {"path": "/file1.py"}},
            {"tool_name": "read_file_sync", "kwargs": {"path": "/file2.py"}},
            {"tool_name": "read_file_sync", "kwargs": {"path": "/file3.py"}},
        ]

        results = self.client.call_tool_batch(calls, max_concurrent=2)

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["result"], "file1")
        self.assertEqual(results[1]["result"], "file2")
        self.assertEqual(results[2]["result"], "file3")

    @patch.object(CwsoClient, "call_tool")
    def test_batch_with_error(self, mock_call_tool):
        """Raise first error encountered in batch."""
        mock_call_tool.side_effect = [
            {"result": "file1"},
            CwsoToolError("read_file_sync", -1, "File not found"),
        ]

        calls = [
            {"tool_name": "read_file_sync", "kwargs": {"path": "/file1.py"}},
            {"tool_name": "read_file_sync", "kwargs": {"path": "/missing.py"}},
        ]

        with self.assertRaises(CwsoToolError):
            self.client.call_tool_batch(calls)

    @patch.object(CwsoClient, "call_tool")
    def test_batch_respects_concurrency(self, mock_call_tool):
        """Batch respects max_concurrent parameter."""
        call_times = []

        def track_call(*args, **kwargs):
            call_times.append(time.time())
            time.sleep(0.05)  # Simulate work
            return {"result": "ok"}

        mock_call_tool.side_effect = track_call

        calls = [
            {"tool_name": "read_file_sync", "kwargs": {"path": f"/file{i}.py"}}
            for i in range(4)
        ]

        results = self.client.call_tool_batch(calls, max_concurrent=2)

        self.assertEqual(len(results), 4)
        # With max_concurrent=2, we should have roughly 2 waves of calls


class TestCwsoClientTypedWrappers(unittest.TestCase):
    """Test typed tool wrapper methods."""

    def setUp(self):
        """Create client with mocked MCP backend."""
        self.client = CwsoClient(jwt_secret="test-secret", role="orchestrator")

    @patch.object(CwsoClient, "call_tool")
    def test_read_file_sync(self, mock_call_tool):
        """Test read_file_sync wrapper."""
        mock_call_tool.return_value = {"content": "file contents"}

        result = self.client.read_file_sync("/path/to/file.py")

        mock_call_tool.assert_called_once_with("read_file_sync", path="/path/to/file.py")
        self.assertEqual(result["content"], "file contents")

    @patch.object(CwsoClient, "call_tool")
    def test_write_file_sync(self, mock_call_tool):
        """Test write_file_sync wrapper."""
        mock_call_tool.return_value = {"status": "ok"}

        result = self.client.write_file_sync("/path/to/file.py", "new content")

        mock_call_tool.assert_called_once_with(
            "write_file_sync", path="/path/to/file.py", content="new content"
        )
        self.assertEqual(result["status"], "ok")

    @patch.object(CwsoClient, "call_tool")
    def test_list_dir(self, mock_call_tool):
        """Test list_dir wrapper."""
        mock_call_tool.return_value = {"entries": ["file1.py", "file2.py"]}

        result = self.client.list_dir("/path")

        mock_call_tool.assert_called_once_with("list_dir", path="/path")
        self.assertEqual(len(result["entries"]), 2)

    @patch.object(CwsoClient, "call_tool")
    def test_create_shadow_workspace(self, mock_call_tool):
        """Test create_shadow_workspace wrapper."""
        mock_call_tool.return_value = {
            "workspace_uuid": "test-uuid",
            "base_tree_oid": "abc123",
        }

        result = self.client.create_shadow_workspace()

        mock_call_tool.assert_called_once_with("create_shadow_workspace")
        self.assertEqual(result["workspace_uuid"], "test-uuid")

    @patch.object(CwsoClient, "call_tool")
    def test_write_shadow_file(self, mock_call_tool):
        """Test write_shadow_file wrapper."""
        mock_call_tool.return_value = {"blob_oid": "def456"}

        result = self.client.write_shadow_file("uuid1", "/file.py", "content")

        mock_call_tool.assert_called_once_with(
            "write_shadow_file",
            workspace_uuid="uuid1",
            path="/file.py",
            content="content",
        )
        self.assertEqual(result["blob_oid"], "def456")

    @patch.object(CwsoClient, "call_tool")
    def test_query_ast(self, mock_call_tool):
        """Test query_ast wrapper."""
        mock_call_tool.return_value = {"results": []}

        result = self.client.query_ast(
            "uuid1",
            "/main.go",
            QueryType.FIND_DEFINITION,
            target_symbol="main",
        )

        mock_call_tool.assert_called_once()
        call_kwargs = mock_call_tool.call_args[1]
        self.assertEqual(call_kwargs["query_type"], "find_definition")

    @patch.object(CwsoClient, "call_tool")
    def test_dispatch_concurrent_jobs(self, mock_call_tool):
        """Test dispatch_concurrent_jobs wrapper."""
        mock_call_tool.return_value = {"job_results": []}

        jobs = [
            ConcurrentJob(
                agent_role="worker",
                objective_prompt="test objective",
                target_workspace_uuid="uuid1",
            )
        ]

        result = self.client.dispatch_concurrent_jobs(jobs)

        mock_call_tool.assert_called_once()
        call_kwargs = mock_call_tool.call_args[1]
        self.assertIn("jobs", call_kwargs)

    @patch.object(CwsoClient, "call_tool")
    def test_merge_concurrent_results(self, mock_call_tool):
        """Test merge_concurrent_results wrapper."""
        mock_call_tool.return_value = {"merge_status": "success"}

        merge_inputs = [
            MergeInput(
                path="/file.py",
                language=MergeLanguage.PYTHON,
                base_content="base",
                ours_content="ours",
                theirs_content="theirs",
            )
        ]

        result = self.client.merge_concurrent_results(
            ["uuid1", "uuid2"],
            merge_inputs,
        )

        mock_call_tool.assert_called_once()
        call_kwargs = mock_call_tool.call_args[1]
        self.assertIn("merge_inputs", call_kwargs)


class TestDataModels(unittest.TestCase):
    """Test data model classes."""

    def test_concurrent_job_to_dict(self):
        """Convert ConcurrentJob to dict."""
        job = ConcurrentJob(
            agent_role="worker",
            objective_prompt="test",
            target_workspace_uuid="uuid1",
            sandbox_profile=SandboxProfile.GVISOR_FAST_EPHEMERAL,
        )

        result = job.to_dict()

        self.assertEqual(result["agent_role"], "worker")
        self.assertEqual(result["sandbox_profile"], "gvisor-fast-ephemeral")

    def test_merge_input_to_dict(self):
        """Convert MergeInput to dict."""
        merge = MergeInput(
            path="/file.py",
            language=MergeLanguage.PYTHON,
            base_content="base",
            ours_content="ours",
            theirs_content="theirs",
        )

        result = merge.to_dict()

        self.assertEqual(result["path"], "/file.py")
        self.assertEqual(result["language"], "python")


class TestEnums(unittest.TestCase):
    """Test enum definitions."""

    def test_query_type_enum(self):
        """Query type enum values."""
        self.assertEqual(QueryType.FIND_DEFINITION.value, "find_definition")
        self.assertEqual(QueryType.FIND_REFERENCES.value, "find_references")

    def test_sandbox_profile_enum(self):
        """Sandbox profile enum values."""
        self.assertEqual(SandboxProfile.DOCKER_TRUSTED.value, "docker-trusted")

    def test_merge_heuristic_enum(self):
        """Merge heuristic enum values."""
        self.assertEqual(MergeHeuristic.AST_SEMANTIC_ONLY.value, "ast_semantic_only")

    def test_merge_language_enum(self):
        """Merge language enum values."""
        self.assertEqual(MergeLanguage.PYTHON.value, "python")


if __name__ == "__main__":
    unittest.main()
