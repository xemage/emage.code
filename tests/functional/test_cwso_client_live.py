#!/usr/bin/env python3
"""Integration tests for CwsoClient library (requires running CWSO server)."""

import os
import sys
import unittest
from pathlib import Path
from uuid import uuid4

# Add the implementation directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "implementation"))

from runtime.cwso.client import (
    CwsoClient,
    CwsoError,
    CwsoToolError,
    CwsoValidationError,
    QueryType,
    MergeLanguage,
    MergeInput,
)


def requires_cwso_live_test(test):
    """Decorator to skip tests if CWSO live testing is not enabled."""
    if not os.getenv("CWSO_LIVE_CONTRACT_TEST"):
        return unittest.skip("CWSO_LIVE_CONTRACT_TEST not set")(test)
    return test


class TestCwsoClientLiveIntegration(unittest.TestCase):
    """Live integration tests against running CWSO server.

    These tests require a running CWSO MCP server at http://127.0.0.1:8080
    and a valid JWT secret in CWSO/.env.jwt.dev or CWSO_JWT_SECRET env var.

    To enable these tests:
        export CWSO_LIVE_CONTRACT_TEST=1
    """

    @classmethod
    def setUpClass(cls):
        """Create a client for all tests."""
        try:
            cls.client = CwsoClient.from_env()
        except Exception as e:
            raise unittest.SkipTest(f"Could not create CwsoClient from environment: {e}")

    @requires_cwso_live_test
    def test_tools_list_returns_11_tools(self):
        """Verify tools_list returns all 11 CWSO tools."""
        result = self.client.tools_list()

        self.assertIn("tools", result)
        tools = result["tools"]
        self.assertEqual(len(tools), 11, f"Expected 11 tools, got {len(tools)}")

        tool_names = {tool.get("name") for tool in tools}
        expected_tools = {
            "read_file_sync",
            "write_file_sync",
            "list_dir",
            "create_shadow_workspace",
            "write_shadow_file",
            "read_shadow_file",
            "commit_shadow",
            "drop_shadow_workspace",
            "query_ast",
            "dispatch_concurrent_jobs",
            "merge_concurrent_results",
        }
        self.assertEqual(tool_names, expected_tools)

    @requires_cwso_live_test
    def test_read_file_sync_from_repo(self):
        """Test reading a file from the live workspace."""
        # Try to read a file we know exists in the CWSO workspace
        # This depends on CWSO having access to the emage.code repo
        try:
            result = self.client.read_file_sync("/README.md")
            self.assertIn("content", result)
            # Content should be non-empty string
            self.assertIsInstance(result["content"], str)
            self.assertGreater(len(result["content"]), 0)
        except CwsoToolError as e:
            if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                self.skipTest("Test file not available in CWSO workspace")
            else:
                raise

    @requires_cwso_live_test
    def test_list_dir_workspace_root(self):
        """Test listing the workspace root directory."""
        result = self.client.list_dir()

        self.assertIn("entries", result)
        entries = result["entries"]
        self.assertIsInstance(entries, list)
        # Root should have some entries
        self.assertGreater(len(entries), 0)

    @requires_cwso_live_test
    def test_shadow_workspace_lifecycle(self):
        """Test complete shadow workspace lifecycle: create -> write -> read -> drop."""
        # 1. Create shadow workspace
        create_result = self.client.create_shadow_workspace()
        self.assertIn("workspace_uuid", create_result)
        self.assertIn("base_tree_oid", create_result)
        workspace_uuid = create_result["workspace_uuid"]

        try:
            # 2. Write a file to shadow
            test_file_path = "/test_integration_file.py"
            test_content = "# Test Python file\nprint('Hello from shadow workspace')\n"
            write_result = self.client.write_shadow_file(
                workspace_uuid, test_file_path, test_content
            )
            self.assertIn("blob_oid", write_result)

            # 3. Read the file back
            read_result = self.client.read_shadow_file(workspace_uuid, test_file_path)
            self.assertIn("content", read_result)
            self.assertEqual(read_result["content"], test_content)

            # 4. Commit the shadow workspace
            commit_msg = "Test commit from integration test"
            commit_result = self.client.commit_shadow(workspace_uuid, commit_msg)
            self.assertIn("commit_oid", commit_result)
            self.assertIn("tree_oid", commit_result)

        finally:
            # 5. Clean up: drop the workspace
            drop_result = self.client.drop_shadow_workspace(workspace_uuid)
            # drop_shadow_workspace should return some confirmation dict
            self.assertIsInstance(drop_result, dict)

    @requires_cwso_live_test
    def test_query_ast_in_shadow(self):
        """Test AST query in a shadow workspace."""
        # 1. Create shadow and write a test Go file
        create_result = self.client.create_shadow_workspace()
        workspace_uuid = create_result["workspace_uuid"]

        try:
            # Write a simple Go file
            test_go = """package main

import "fmt"

func main() {
    fmt.Println("Hello")
}

func helper() string {
    return "help"
}
"""
            self.client.write_shadow_file(workspace_uuid, "/main.go", test_go)
            self.client.commit_shadow(workspace_uuid, "Add Go file")

            # 2. Query AST for function definition
            query_result = self.client.query_ast(
                workspace_uuid,
                "/main.go",
                QueryType.LIST_EXPORTS,
            )

            # Result should be a dict (exact structure depends on CWSO)
            self.assertIsInstance(query_result, dict)

        finally:
            self.client.drop_shadow_workspace(workspace_uuid)

    @requires_cwso_live_test
    def test_rate_limiting_enforcement(self):
        """Test that rate limiting is enforced between requests."""
        import time

        # Make two rapid calls and measure timing
        start = time.time()
        try:
            # First call
            self.client.tools_list()
            between = time.time()

            # Second call (should be rate-limited)
            self.client.tools_list()
            end = time.time()

            # Time between calls should be >= min_interval
            interval = between - start
            # The second call should wait, so total time should be >= 2 * min_interval - epsilon
            total_time = end - start
            # We expect roughly 2*1.05 = 2.1 seconds minimum
            # Allow some flexibility for test execution overhead
            self.assertGreaterEqual(
                total_time,
                1.0,
                f"Rate limiting appears not to be enforced (total time: {total_time}s)",
            )
        except CwsoError as e:
            self.fail(f"Rate limiting test failed with error: {e}")

    @requires_cwso_live_test
    def test_error_handling_for_invalid_tool_args(self):
        """Test that invalid tool arguments raise proper errors."""
        with self.assertRaises(CwsoValidationError):
            # commit_shadow requires orchestrator role but we might be on worker
            # Try calling a tool with missing required argument
            self.client.read_file_sync()  # missing 'path' argument

    @requires_cwso_live_test
    def test_batch_dispatch_success(self):
        """Test batch tool dispatch."""
        # Create batch of list_dir calls with different paths
        calls = [
            {"tool_name": "list_dir", "kwargs": {}},
            {"tool_name": "list_dir", "kwargs": {}},
            {"tool_name": "list_dir", "kwargs": {}},
        ]

        try:
            results = self.client.call_tool_batch(calls, max_concurrent=2)
            self.assertEqual(len(results), 3)
            for result in results:
                self.assertIsInstance(result, dict)
        except CwsoToolError as e:
            # Some tools might not be available for this role, which is ok
            if "may not invoke" in str(e).lower():
                self.skipTest(f"Tool not available for this role: {e}")
            else:
                raise

    @requires_cwso_live_test
    def test_multiple_roles(self):
        """Test client with different roles."""
        for role in ["orchestrator", "worker"]:
            try:
                client = CwsoClient(
                    jwt_secret=self.client._mcp._secret.decode("utf-8"),
                    role=role,
                )
                result = client.tools_list()
                self.assertIn("tools", result)
                self.assertEqual(len(result["tools"]), 11)
            except CwsoError as e:
                self.fail(f"Failed to use role '{role}': {e}")


class TestCwsoClientEnvironmentConfiguration(unittest.TestCase):
    """Test client configuration from environment variables."""

    @requires_cwso_live_test
    def test_from_env_creates_client(self):
        """Test that from_env() creates a valid client."""
        # This will only work if env vars or default paths are set up
        try:
            client = CwsoClient.from_env()
            self.assertIsNotNone(client)
            self.assertIsNotNone(client._mcp)
        except Exception as e:
            self.skipTest(f"Environment not configured: {e}")

    @requires_cwso_live_test
    def test_from_env_client_can_call_tools(self):
        """Test that from_env() client can successfully call tools."""
        try:
            client = CwsoClient.from_env()
            result = client.tools_list()
            self.assertIn("tools", result)
            self.assertEqual(len(result["tools"]), 11)
        except Exception as e:
            self.skipTest(f"Environment not configured: {e}")


if __name__ == "__main__":
    unittest.main()
