#!/usr/bin/env python3
"""Unit tests for CwsoMcpClient MCP tool-result envelope unwrapping (Task T314).

The real, live CWSO MCP server wraps every `tools/call` result in the standard
MCP tool-result envelope `{"content": [{"type": "text", "text":
"<json-encoded-payload>"}]}` rather than returning the payload
(e.g. `workspace_uuid`, `blob_oid`) as top-level keys. These tests mock the
HTTP transport (`urllib.request.urlopen`) directly so that `CwsoMcpClient.rpc()`
/`call_tool()` are exercised end-to-end against a realistic response shape,
rather than mocking `call_tool` itself (as `tests/unit/test_cwso_client.py`
does at the `CwsoClient` boundary).
"""

import json
import sys
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "implementation"))

from runtime.cwso.mcp_client import CwsoMcpClient


class _FakeHttpResponse:
    """Minimal stand-in for the context-managed object urlopen() returns."""

    def __init__(self, payload: dict) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "_FakeHttpResponse":
        return self

    def __exit__(self, *exc_info) -> None:
        return None

    def read(self) -> bytes:
        return self._body


def _rpc_envelope(result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": 1, "result": result}


class TestCwsoMcpClientEnvelopeUnwrap(unittest.TestCase):
    """Verify call_tool() unwraps the MCP tool-result envelope."""

    def setUp(self) -> None:
        self.client = CwsoMcpClient(base_url="http://127.0.0.1:8080", jwt_secret="test-secret")

    @patch("runtime.cwso.mcp_client.request.urlopen")
    def test_call_tool_unwraps_content_text_envelope(self, mock_urlopen):
        """A tools/call result wrapped in {'content': [{'type': 'text', ...}]}
        is unwrapped to the parsed JSON payload."""
        enveloped_result = {
            "content": [{"type": "text", "text": json.dumps({"workspace_uuid": "abc"})}]
        }
        mock_urlopen.return_value = _FakeHttpResponse(_rpc_envelope(enveloped_result))

        result = self.client.call_tool(role="orchestrator", name="create_shadow_workspace", arguments={})

        self.assertEqual(result, {"workspace_uuid": "abc"})
        self.assertNotIn("content", result)

    @patch("runtime.cwso.mcp_client.request.urlopen")
    def test_call_tool_passes_through_already_flat_result(self, mock_urlopen):
        """Defensive fallback: a result with no 'content' key (already flat,
        e.g. a future server version) passes through unchanged."""
        flat_result = {"status": "ok", "blob_oid": "def456"}
        mock_urlopen.return_value = _FakeHttpResponse(_rpc_envelope(flat_result))

        result = self.client.call_tool(role="orchestrator", name="write_shadow_file", arguments={})

        self.assertEqual(result, flat_result)

    @patch("runtime.cwso.mcp_client.request.urlopen")
    def test_call_tool_passes_through_when_content_text_not_json(self, mock_urlopen):
        """Defensive fallback: content[0].text is not valid JSON -> return
        the raw result unmodified rather than raising."""
        enveloped_result = {"content": [{"type": "text", "text": "not json at all"}]}
        mock_urlopen.return_value = _FakeHttpResponse(_rpc_envelope(enveloped_result))

        result = self.client.call_tool(role="orchestrator", name="query_ast", arguments={})

        self.assertEqual(result, enveloped_result)

    @patch("runtime.cwso.mcp_client.request.urlopen")
    def test_call_tool_passes_through_when_content_not_list(self, mock_urlopen):
        """Defensive fallback: 'content' present but not a non-empty list of
        text items -> return the raw result unmodified."""
        odd_result = {"content": "not-a-list", "status": "ok"}
        mock_urlopen.return_value = _FakeHttpResponse(_rpc_envelope(odd_result))

        result = self.client.call_tool(role="orchestrator", name="drop_shadow_workspace", arguments={})

        self.assertEqual(result, odd_result)


if __name__ == "__main__":
    unittest.main()
