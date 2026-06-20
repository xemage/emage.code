#!/usr/bin/env python3
"""Reusable CWSO MPC client library for emage.code orchestration.

This module provides a typed, high-level Python client for the CWSO MPC tools,
built on top of the low-level CwsoMcpClient. It supports:
- JWT minting (HS256, role-based)
- All 11 CWSO tools with typed interfaces
- Rate limiting (≥1.05 sec between requests)
- Error handling with descriptive CwsoError exceptions
- Batch dispatch with concurrency control
"""

from __future__ import annotations

import concurrent.futures
import logging
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from .mcp_client import CwsoMcpClient, CwsoMcpError, CwsoHttpError, CwsoRpcError

logger = logging.getLogger(__name__)


# ============================================================================
# Exceptions
# ============================================================================


class CwsoError(Exception):
    """Base exception for CWSO client errors."""

    pass


class CwsoAuthError(CwsoError):
    """Raised when JWT generation or authentication fails."""

    pass


class CwsoRateLimitError(CwsoError):
    """Raised when rate limit is exceeded or cannot be recovered from."""

    pass


class CwsoToolError(CwsoError):
    """Raised when a tool call fails or returns an error."""

    def __init__(self, tool_name: str, error_code: Optional[int], message: str, data: Optional[Any] = None):
        self.tool_name = tool_name
        self.error_code = error_code
        self.message = message
        self.data = data
        super().__init__(f"Tool {tool_name} failed: {message}")


class CwsoConnectionError(CwsoError):
    """Raised when HTTP connection or transport fails."""

    pass


class CwsoValidationError(CwsoError):
    """Raised when tool arguments fail validation."""

    pass


# ============================================================================
# Enums and Type Definitions
# ============================================================================


class QueryType(str, Enum):
    """AST query type for query_ast tool."""

    FIND_DEFINITION = "find_definition"
    FIND_REFERENCES = "find_references"
    EXTRACT_SIGNATURE = "extract_signature"
    LIST_EXPORTS = "list_exports"
    DETECT_ENTRYPOINTS = "detect_entrypoints"


class SandboxProfile(str, Enum):
    """Sandbox profile for dispatch_concurrent_jobs."""

    DOCKER_TRUSTED = "docker-trusted"
    GVISOR_FAST_EPHEMERAL = "gvisor-fast-ephemeral"
    FIRECRACKER_SECURE_ISOLATION = "firecracker-secure-isolation"


class MergeHeuristic(str, Enum):
    """Merge heuristic for merge_concurrent_results."""

    AST_SEMANTIC_ONLY = "ast_semantic_only"
    PREFER_THEIRS = "prefer_theirs"
    PREFER_OURS = "prefer_ours"
    FAIL_RAPIDLY_ON_CONFLICT = "fail_rapidly_on_conflict"


class MergeLanguage(str, Enum):
    """Programming language for merge_concurrent_results."""

    GO = "go"
    RUST = "rust"
    PYTHON = "python"
    TYPESCRIPT = "typescript"


# ============================================================================
# Tool Input/Output Models
# ============================================================================


@dataclass
class ConcurrentJob:
    """Represents a single concurrent job for dispatch_concurrent_jobs."""

    agent_role: str
    objective_prompt: str
    target_workspace_uuid: str
    sandbox_profile: Optional[SandboxProfile] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to CWSO API dict."""
        result = {
            "agent_role": self.agent_role,
            "objective_prompt": self.objective_prompt,
            "target_workspace_uuid": self.target_workspace_uuid,
        }
        if self.sandbox_profile:
            result["sandbox_profile"] = self.sandbox_profile.value
        return result


@dataclass
class MergeInput:
    """Represents a single file merge for merge_concurrent_results."""

    path: str
    language: MergeLanguage
    base_content: str
    ours_content: str
    theirs_content: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to CWSO API dict."""
        return {
            "path": self.path,
            "language": self.language.value,
            "base_content": self.base_content,
            "ours_content": self.ours_content,
            "theirs_content": self.theirs_content,
        }


# ============================================================================
# Main CwsoClient
# ============================================================================


class CwsoClient:
    """High-level, typed CWSO MPC client for emage.code orchestration.

    This client provides:
    - Authenticated tool dispatch with JWT minting
    - Rate-limited requests (≥1.05 sec between calls)
    - Batch operations with concurrency control
    - Typed interfaces for all 11 CWSO tools
    - Comprehensive error handling

    Example:
        >>> client = CwsoClient(jwt_secret="my-secret", role="orchestrator")
        >>> tools = client.tools_list()
        >>> result = client.read_file_sync("/path/to/file.py")
    """

    # Define the 11 CWSO tools that this client supports
    SUPPORTED_TOOLS = {
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

    # Class-level attribute kept for unittest patching via patch.object(CwsoClient, "_mcp").
    _mcp: Optional[CwsoMcpClient] = None

    def __init__(
        self,
        jwt_secret: str,
        role: str,
        base_url: str = "http://127.0.0.1:8080",
        rate_limit_pacing_sec: float = 1.05,
        timeout_seconds: float = 30.0,
        verify_ssl: bool = True,
    ):
        """Initialize CwsoClient.

        Args:
            jwt_secret: HS256 secret for JWT minting (never logged)
            role: Role for JWT claims ('orchestrator' or 'worker')
            base_url: Base URL of CWSO MCP server
            rate_limit_pacing_sec: Minimum seconds between requests (≥1.05)
            timeout_seconds: HTTP timeout per request
            verify_ssl: Whether to verify SSL certificates (dev: False)

        Raises:
            CwsoValidationError: If role is invalid or pacing < 1.05
            CwsoAuthError: If JWT secret is invalid
        """
        if rate_limit_pacing_sec < 1.05:
            raise CwsoValidationError(f"rate_limit_pacing_sec must be >= 1.05, got {rate_limit_pacing_sec}")

        if role not in {"orchestrator", "worker"}:
            raise CwsoValidationError(f"role must be 'orchestrator' or 'worker', got {role}")

        self._role = role
        self._rate_limit_pacing_sec = rate_limit_pacing_sec
        self._timeout_seconds = timeout_seconds

        # Initialize underlying MCP client
        try:
            self._mcp = CwsoMcpClient(
                base_url=base_url,
                jwt_secret=jwt_secret,
                min_interval_seconds=rate_limit_pacing_sec,
                timeout_seconds=timeout_seconds,
            )
        except ValueError as e:
            raise CwsoAuthError(f"Failed to initialize JWT: {e}") from e

        # Rate limiting state
        self._rate_limit_lock = threading.Lock()
        self._last_request_time = 0.0
        self._cached_tools: Optional[list[dict[str, Any]]] = None

    @classmethod
    def from_env(cls) -> CwsoClient:
        """Create a CwsoClient from environment variables.

        Environment variables:
        - CWSO_JWT_SECRET: JWT secret (or CWSO_JWT_SECRET_FILE)
        - CWSO_BASE_URL: Base URL (default: http://127.0.0.1:8080)
        - CWSO_ROLE: JWT role (default: orchestrator)
        - CWSO_RATE_LIMIT_PACING_SEC: Pacing interval (default: 1.05)
        - CWSO_TIMEOUT_SECONDS: HTTP timeout (default: 30.0)
        - CWSO_VERIFY_SSL: Verify SSL certs (default: true)
        """
        mcp_client = CwsoMcpClient.from_env()
        import os

        role = os.getenv("CWSO_ROLE", "orchestrator")
        base_url = os.getenv("CWSO_BASE_URL", "http://127.0.0.1:8080")
        pacing = float(os.getenv("CWSO_RATE_LIMIT_PACING_SEC", "1.05"))
        timeout = float(os.getenv("CWSO_TIMEOUT_SECONDS", "30.0"))
        verify_ssl = os.getenv("CWSO_VERIFY_SSL", "true").lower() not in {"0", "false", "no"}

        # Extract secret from the created mcp_client
        secret = mcp_client._secret.decode("utf-8") if isinstance(mcp_client._secret, bytes) else str(mcp_client._secret)

        return cls(
            jwt_secret=secret,
            role=role,
            base_url=base_url,
            rate_limit_pacing_sec=pacing,
            timeout_seconds=timeout,
            verify_ssl=verify_ssl,
        )

    def tools_list(self) -> dict[str, Any]:
        """Fetch the list of available CWSO tools.

        Returns:
            Dict with 'tools' key containing list of tool descriptions

        Raises:
            CwsoConnectionError: If HTTP/network error occurs
            CwsoToolError: If CWSO returns an error
        """
        try:
            tools = self._mcp.list_tools(role=self._role)
            if not isinstance(tools, list):
                raise CwsoConnectionError("tools/list returned a non-list payload")

            # Validate that we got the expected 11 tools
            tool_names = {tool.get("name") for tool in tools if isinstance(tool, dict)}
            if len(tool_names) != 11 or not tool_names.issubset(self.SUPPORTED_TOOLS):
                logger.warning(f"Unexpected tool list: {sorted(tool_names)}")

            self._cached_tools = tools
            return {"tools": tools}
        except CwsoHttpError as e:
            raise CwsoConnectionError(f"HTTP error fetching tools: {e.status_code} {e.body}") from e
        except CwsoRpcError as e:
            raise CwsoToolError("tools/list", e.code, e.message, e.data) from e
        except CwsoMcpError as e:
            raise CwsoConnectionError(f"Failed to fetch tools: {e}") from e

    def call_tool(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """Call a single CWSO tool with keyword arguments.

        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool-specific arguments (passed as 'arguments' to MCP)

        Returns:
            Tool result dict from CWSO

        Raises:
            CwsoValidationError: If tool_name is not supported
            CwsoToolError: If tool execution fails
            CwsoConnectionError: If network error occurs
        """
        if tool_name not in self.SUPPORTED_TOOLS:
            raise CwsoValidationError(f"Unknown tool: {tool_name}. Supported: {self.SUPPORTED_TOOLS}")

        # Validate common required args based on tool
        self._validate_tool_args(tool_name, kwargs)

        try:
            result = self._mcp.call_tool(role=self._role, name=tool_name, arguments=kwargs)
            return result
        except CwsoHttpError as e:
            raise CwsoConnectionError(f"HTTP error calling {tool_name}: {e.status_code}") from e
        except CwsoRpcError as e:
            raise CwsoToolError(tool_name, e.code, e.message, e.data) from e
        except CwsoMcpError as e:
            raise CwsoConnectionError(f"Failed to call {tool_name}: {e}") from e

    def call_tool_batch(
        self,
        calls: list[dict[str, Any]],
        max_concurrent: int = 3,
    ) -> list[dict[str, Any]]:
        """Dispatch multiple tool calls with concurrency control.

        Each call dict must have 'tool_name' and 'kwargs' keys.
        Rate limiting is enforced across the batch.

        Args:
            calls: List of {"tool_name": str, "kwargs": dict}
            max_concurrent: Maximum concurrent requests (default 3)

        Returns:
            List of results in same order as calls

        Raises:
            CwsoValidationError: If calls are malformed
            CwsoToolError: If any tool execution fails (first failure raised)
            CwsoRateLimitError: If pacing cannot be enforced
        """
        if not calls:
            return []

        # Validate call structure
        for i, call in enumerate(calls):
            if not isinstance(call, dict):
                raise CwsoValidationError(f"call[{i}] is not a dict: {type(call)}")
            if "tool_name" not in call:
                raise CwsoValidationError(f"call[{i}] missing 'tool_name'")
            if "kwargs" not in call:
                raise CwsoValidationError(f"call[{i}] missing 'kwargs'")

        results: list[Optional[dict[str, Any]]] = [None] * len(calls)
        errors: list[Optional[Exception]] = [None] * len(calls)

        def execute_call(index: int, call: dict[str, Any]) -> None:
            """Execute a single call and store result or error."""
            try:
                results[index] = self.call_tool(call["tool_name"], **call["kwargs"])
            except Exception as e:
                errors[index] = e

        # Use ThreadPoolExecutor to manage concurrency with rate limiting
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = []
            for i, call in enumerate(calls):
                future = executor.submit(execute_call, i, call)
                futures.append(future)

            # Wait for all to complete
            concurrent.futures.wait(futures)

        # Check for errors
        for i, error in enumerate(errors):
            if error:
                raise error

        return results  # type: ignore


    # ========================================================================
    # Typed Tool Wrappers (11 CWSO Tools)
    # ========================================================================

    def read_file_sync(self, path: str) -> dict[str, Any]:
        """Read file from workspace root.

        Args:
            path: File path relative to workspace root

        Returns:
            Dict with 'content' key (file contents)
        """
        return self.call_tool("read_file_sync", path=path)

    def write_file_sync(self, path: str, content: str) -> dict[str, Any]:
        """Write file to workspace root.

        Args:
            path: File path relative to workspace root
            content: File contents to write

        Returns:
            Dict with write confirmation
        """
        return self.call_tool("write_file_sync", path=path, content=content)

    def list_dir(self, path: str = "") -> dict[str, Any]:
        """List directory contents.

        Args:
            path: Directory path (default: workspace root)

        Returns:
            Dict with 'entries' key (list of directory entries)
        """
        kwargs = {}
        if path:
            kwargs["path"] = path
        return self.call_tool("list_dir", **kwargs)

    def create_shadow_workspace(self, base_commit_sha: Optional[str] = None) -> dict[str, Any]:
        """Create a shadow (in-memory) workspace.

        Args:
            base_commit_sha: Specific commit to base workspace on (optional)

        Returns:
            Dict with 'workspace_uuid' and 'base_tree_oid' keys
        """
        kwargs = {}
        if base_commit_sha:
            kwargs["base_commit_sha"] = base_commit_sha
        return self.call_tool("create_shadow_workspace", **kwargs)

    def write_shadow_file(self, workspace_uuid: str, path: str, content: str) -> dict[str, Any]:
        """Write file to shadow workspace.

        Args:
            workspace_uuid: UUID of shadow workspace
            path: File path in workspace
            content: File contents to write

        Returns:
            Dict with 'blob_oid' key
        """
        return self.call_tool("write_shadow_file", workspace_uuid=workspace_uuid, path=path, content=content)

    def read_shadow_file(self, workspace_uuid: str, path: str) -> dict[str, Any]:
        """Read file from shadow workspace.

        Args:
            workspace_uuid: UUID of shadow workspace
            path: File path in workspace

        Returns:
            Dict with 'content' key (file contents)
        """
        return self.call_tool("read_shadow_file", workspace_uuid=workspace_uuid, path=path)

    def commit_shadow(self, workspace_uuid: str, message: str) -> dict[str, Any]:
        """Commit staged changes in shadow workspace.

        Args:
            workspace_uuid: UUID of shadow workspace
            message: Commit message

        Returns:
            Dict with 'commit_oid' and 'tree_oid' keys
        """
        return self.call_tool("commit_shadow", workspace_uuid=workspace_uuid, message=message)

    def drop_shadow_workspace(self, workspace_uuid: str) -> dict[str, Any]:
        """Free a shadow workspace.

        Args:
            workspace_uuid: UUID of shadow workspace to drop

        Returns:
            Dict with drop confirmation
        """
        return self.call_tool("drop_shadow_workspace", workspace_uuid=workspace_uuid)

    def query_ast(
        self,
        workspace_uuid: str,
        path: str,
        query_type: QueryType,
        target_symbol: Optional[str] = None,
    ) -> dict[str, Any]:
        """Query AST in shadow workspace.

        Args:
            workspace_uuid: UUID of shadow workspace
            path: File path in workspace
            query_type: Type of AST query
            target_symbol: Symbol to query (optional, required for some query types)

        Returns:
            Dict with AST query results
        """
        kwargs = {
            "workspace_uuid": workspace_uuid,
            "path": path,
            "query_type": query_type.value,
        }
        if target_symbol:
            kwargs["target_symbol"] = target_symbol
        return self.call_tool("query_ast", **kwargs)

    def dispatch_concurrent_jobs(
        self,
        jobs: list[ConcurrentJob],
        execution_timeout_seconds: int = 300,
    ) -> dict[str, Any]:
        """Dispatch concurrent agent jobs.

        Args:
            jobs: List of ConcurrentJob objects
            execution_timeout_seconds: Timeout for job execution (default 300)

        Returns:
            Dict with job execution results
        """
        job_dicts = [job.to_dict() for job in jobs]
        kwargs = {
            "jobs": job_dicts,
            "execution_timeout_seconds": execution_timeout_seconds,
        }
        return self.call_tool("dispatch_concurrent_jobs", **kwargs)

    def merge_concurrent_results(
        self,
        source_workspace_uuids: list[str],
        merge_inputs: list[MergeInput],
        auto_resolve_heuristic: MergeHeuristic = MergeHeuristic.AST_SEMANTIC_ONLY,
        target_branch_ref: Optional[str] = None,
        rollout_session_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Merge results from concurrent workspaces.

        Args:
            source_workspace_uuids: List of workspace UUIDs to merge from
            merge_inputs: List of MergeInput objects (files to merge)
            auto_resolve_heuristic: Merge conflict resolution strategy
            target_branch_ref: Target branch reference (default: main)
            rollout_session_id: Session ID for reward attachment (optional)

        Returns:
            Dict with merge results and conflict info
        """
        merge_input_dicts = [mi.to_dict() for mi in merge_inputs]
        kwargs = {
            "source_workspace_uuids": source_workspace_uuids,
            "merge_inputs": merge_input_dicts,
            "auto_resolve_heuristic": auto_resolve_heuristic.value,
        }
        if target_branch_ref:
            kwargs["target_branch_ref"] = target_branch_ref
        if rollout_session_id:
            kwargs["rollout_session_id"] = rollout_session_id
        return self.call_tool("merge_concurrent_results", **kwargs)

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _validate_tool_args(self, tool_name: str, kwargs: dict[str, Any]) -> None:
        """Validate tool arguments based on tool requirements.

        Raises:
            CwsoValidationError: If required args are missing
        """
        required_args = {
            "read_file_sync": {"path"},
            "write_file_sync": {"path", "content"},
            "list_dir": set(),  # optional args only
            "create_shadow_workspace": set(),  # optional args only
            "write_shadow_file": {"workspace_uuid", "path", "content"},
            "read_shadow_file": {"workspace_uuid", "path"},
            "commit_shadow": {"workspace_uuid", "message"},
            "drop_shadow_workspace": {"workspace_uuid"},
            "query_ast": {"workspace_uuid", "path", "query_type"},
            "dispatch_concurrent_jobs": {"jobs"},
            "merge_concurrent_results": {"source_workspace_uuids", "merge_inputs"},
        }

        required = required_args.get(tool_name, set())
        missing = required - set(kwargs.keys())
        if missing:
            raise CwsoValidationError(f"Tool {tool_name} missing required args: {missing}")


# ============================================================================
# Convenience Functions
# ============================================================================


def create_client(
    jwt_secret: str,
    role: str = "orchestrator",
    base_url: str = "http://127.0.0.1:8080",
) -> CwsoClient:
    """Create a CwsoClient with common defaults.

    Args:
        jwt_secret: HS256 secret for JWT minting
        role: Role for JWT claims
        base_url: Base URL of CWSO MPC server

    Returns:
        Initialized CwsoClient
    """
    return CwsoClient(jwt_secret=jwt_secret, role=role, base_url=base_url)
