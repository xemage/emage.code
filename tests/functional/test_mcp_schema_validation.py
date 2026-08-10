"""Validate generated MCP config output against confirmed, live-fetched official schemas.

Per T384's Step 0 research (2026-08-10), only two of the seven platforms this repo
projects MCP config to publish a genuine, citable JSON Schema for the exact config file
`implementation/scripts/sync.mjs`'s `emitMcp()` generates. Both were confirmed by fetching
the schema directly (not from training-data memory) and cross-checking it defines the
`mcp`/`mcpServers` property this repo's generated file actually uses:

- **Gemini CLI** — official `google-gemini/gemini-cli` GitHub repository,
  `schemas/settings.schema.json`, fetched live from
  https://raw.githubusercontent.com/google-gemini/gemini-cli/main/schemas/settings.schema.json
  A vendored copy is checked in at `tests/fixtures/mcp-schemas/gemini-cli-settings.schema.json`
  to avoid a network dependency in CI. Its `$defs.MCPServerConfig` defines the `httpUrl`
  field this repo emits for remote servers (`context7`, `hf-mcp-server`) plus
  `command`/`args`/`env` for stdio servers.
- **Opencode** — vendor-published schema at https://opencode.ai/config.json, which is the
  exact schema this repo's own generated `implementation/.opencode/opencode.json` already
  references via its `"$schema"` field. A vendored copy is checked in at
  `tests/fixtures/mcp-schemas/opencode-config.schema.json`. Its `$defs.mcp` property
  (`McpLocalConfig` / `McpRemoteConfig`) defines the `{"type": "local", "command": [...]}`
  and `{"type": "remote", "url": "…"}` shapes this repo emits.

Every other platform (`vscode`/`github`, `cursor`, `pi`, `claude-code`, `cline`) was
researched and found to have no officially published, citable JSON Schema for its
MCP/settings config file — see the "Runtime verification checklist" section of
`docs/wiki/mcp-servers.md` for the documented manual verification steps used there
instead. Do not add schema validation for those platforms without an independently
confirmed, cited, live-fetched official schema source (see `docs/tasks/task-T384.md`).
"""
from __future__ import annotations

import json
import unittest

import jsonschema

from tests._helpers.repo import implementation_root, repo_root


def _load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class TestGeminiMcpSchema(unittest.TestCase):
    """implementation/.gemini/settings.json against gemini-cli's official settings schema."""

    def test_generated_settings_json_matches_official_schema(self):
        schema = _load_json(
            repo_root() / "tests" / "fixtures" / "mcp-schemas" / "gemini-cli-settings.schema.json"
        )
        generated = _load_json(implementation_root() / ".gemini" / "settings.json")
        jsonschema.validate(generated, schema)

    def test_remote_servers_use_http_url_field(self):
        """Sanity check the fixture actually exercises the remote-server shape (T364)."""
        generated = _load_json(implementation_root() / ".gemini" / "settings.json")
        for name in ("context7", "hf-mcp-server"):
            with self.subTest(server=name):
                self.assertIn("httpUrl", generated["mcpServers"][name])


class TestOpencodeMcpSchema(unittest.TestCase):
    """implementation/.opencode/opencode.json against opencode.ai's official config schema."""

    def test_generated_config_matches_official_schema(self):
        schema = _load_json(
            repo_root() / "tests" / "fixtures" / "mcp-schemas" / "opencode-config.schema.json"
        )
        generated = _load_json(implementation_root() / ".opencode" / "opencode.json")
        jsonschema.validate(generated, schema)

    def test_remote_servers_use_type_and_url_fields(self):
        """Sanity check the fixture actually exercises the remote-server shape (T364)."""
        generated = _load_json(implementation_root() / ".opencode" / "opencode.json")
        for name in ("context7", "hf-mcp-server"):
            with self.subTest(server=name):
                self.assertEqual(generated["mcp"][name].get("type"), "remote")
                self.assertIn("url", generated["mcp"][name])


if __name__ == "__main__":
    unittest.main()
