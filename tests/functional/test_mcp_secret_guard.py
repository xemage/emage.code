"""Guard against literal (non-placeholder) secret values in generated MCP output.

Defense-in-depth for the class of leak recorded in
implementation/knowledge/mcp/servers.yaml's toolradar entry (v1 leaked a live
TOOLRADAR_API_KEY value directly into three generated files before the fix to
env-var placeholder syntax). This test asserts every credential-bearing `env`
block value in every generated MCP/settings output file is the generator's
own placeholder syntax, never a literal string.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root

# ${env:VAR} (vscode/cursor/gemini/pi/cline/claude-code) or {env:VAR} (opencode).
ALLOWED_ENV_VALUE_RE = re.compile(r"^\$?\{env:[A-Z][A-Z0-9_]*\}$")

GENERATED_MCP_FILES = [
    "implementation/.vscode/mcp.json",
    "implementation/.cursor/mcp.json",
    "implementation/.gemini/settings.json",
    "implementation/.opencode/opencode.json",
    "implementation/.pi/mcp.json",
    "implementation/.cline/mcp.json",
    "implementation/.mcp.json",
    ".vscode/mcp.json",
    ".cursor/mcp.json",
    ".gemini/settings.json",
    ".opencode/opencode.json",
    ".pi/mcp.json",
    ".cline/mcp.json",
    ".mcp.json",
]


def find_literal_env_values(data) -> list[tuple[str, str]]:
    """Recursively find (key, value) pairs inside any 'env' dict whose value
    is not the generator's placeholder syntax. Returns a list of violations."""
    violations: list[tuple[str, str]] = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "env" and isinstance(value, dict):
                    for env_key, env_value in value.items():
                        if isinstance(env_value, str) and not ALLOWED_ENV_VALUE_RE.match(env_value):
                            violations.append((env_key, env_value))
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return violations


class TestMcpSecretGuard(unittest.TestCase):
    def test_no_literal_secrets_in_generated_mcp_output(self):
        for rel_path in GENERATED_MCP_FILES:
            path = repo_root() / rel_path
            if not path.is_file():
                self.fail(f"expected generated MCP file missing: {rel_path}")
            with self.subTest(file=rel_path):
                data = json.loads(path.read_text(encoding="utf-8"))
                violations = find_literal_env_values(data)
                self.assertEqual(
                    violations, [],
                    msg=f"{rel_path} has literal (non-placeholder) env value(s): {violations}",
                )

    def test_guard_detects_injected_literal_secret(self):
        fixture = {
            "mcpServers": {
                "toolradar": {
                    "command": "npx",
                    "args": ["-y", "toolradar-mcp"],
                    "env": {"TOOLRADAR_API_KEY": "tr_live_FAKEVALUEFORTESTONLYNOTREAL"},
                }
            }
        }
        violations = find_literal_env_values(fixture)
        self.assertEqual(
            violations, [("TOOLRADAR_API_KEY", "tr_live_FAKEVALUEFORTESTONLYNOTREAL")],
            msg="guard must detect a deliberately-injected literal secret-shaped value",
        )

    def test_guard_allows_placeholder_syntax(self):
        fixture = {
            "mcpServers": {
                "gitlab": {"env": {"GITLAB_PERSONAL_ACCESS_TOKEN": "${env:GITLAB_PERSONAL_ACCESS_TOKEN}"}},
                "brave": {"env": {"BRAVE_API_KEY": "${env:BRAVE_API_KEY}"}},
            },
            "mcp": {
                "toolradar": {"env": {"TOOLRADAR_API_KEY": "{env:TOOLRADAR_API_KEY}"}},
            },
        }
        violations = find_literal_env_values(fixture)
        self.assertEqual(violations, [], msg="legitimate placeholder syntax must not false-positive")


if __name__ == "__main__":
    unittest.main()
