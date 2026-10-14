"""T638 -- lock the MCP server package pin policy of `servers.yaml` (audit SEC-002).

Spec: docs/artifacts/mcp-server-packages-v1.md (§4, §9) and the user decisions of 2026-10-15.
Static inspection of the source of truth and of the generated claude-code projection; no
subprocess, no network, no package is installed or run.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import yaml  # noqa: E402

SERVERS_YAML = REPO_ROOT / "implementation" / "knowledge" / "mcp" / "servers.yaml"
CLAUDE_MCP = REPO_ROOT / "implementation" / ".mcp.json"
# Every generated MCP projection (one per platform; .vscode carries the core servers only).
PROJECTIONS = [
    REPO_ROOT / "implementation" / rel
    for rel in (
        ".mcp.json",
        ".gemini/settings.json",
        ".opencode/opencode.json",
        ".cursor/mcp.json",
        ".cline/mcp.json",
        ".pi/mcp.json",
        ".vscode/mcp.json",
    )
]

EXACT_VERSION = re.compile(r"^(@[a-z0-9-]+/)?[a-z0-9._-]+@\d+\.\d+\.\d+$")
APPROVED_NPX_PINS = {
    "gitlab": "@zereight/mcp-gitlab@2.2.5",
    "playwright": "@playwright/mcp@0.0.83",
    "fetch": "mcp-fetch-server@1.1.2",
    "memory": "@modelcontextprotocol/server-memory@1.0.0",
    "sequential-thinking": "@modelcontextprotocol/server-sequential-thinking@1.0.0",
    "brave": "@brave/brave-search-mcp-server@2.1.4",
    "filesystem": "@modelcontextprotocol/server-filesystem@1.0.0",
    "supabase": "@supabase/mcp-server-supabase@0.13.0",
    "toolradar": "toolradar-mcp@2.1.0",
}
REMOVED_OR_NONEXISTENT = (
    "@anthropic/mcp-filesystem",
    "@github/mcp-github",
    "@modelcontextprotocol/mcp-git",
    "@supabase/mcp\"",
    "@latest",
    "docker-mcp",
    "postgres-mcp",
)


class McpPackagePinTests(unittest.TestCase):
    def setUp(self):
        self.servers = yaml.safe_load(SERVERS_YAML.read_text(encoding="utf-8"))["servers"]

    def test_every_npx_entry_carries_an_exact_approved_pin(self):
        seen = set()
        for key, entry in self.servers.items():
            if entry.get("command") != "npx":
                continue
            seen.add(key)
            pkgs = [a for a in entry["args"] if not a.startswith("-") and a != "."]
            self.assertEqual(len(pkgs), 1, key)
            self.assertRegex(pkgs[0], EXACT_VERSION, key)
            self.assertNotIn("@latest", pkgs[0], key)
            self.assertEqual(pkgs[0], APPROVED_NPX_PINS[key], key)
            self.assertEqual(entry["args"][0], "-y", key)
        self.assertEqual(seen, set(APPROVED_NPX_PINS))

    def test_git_is_a_pinned_uvx_launch(self):
        git = self.servers["git"]
        self.assertEqual(git["command"], "uvx")
        self.assertRegex(git["args"][0], r"^mcp-server-git@\d+\.\d+\.\d+$")

    def test_github_is_a_digest_pinned_container_with_token_by_name(self):
        gh = self.servers["github"]
        self.assertEqual(gh["command"], "docker")
        self.assertEqual(gh["args"][:5], ["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN"])
        self.assertRegex(gh["args"][5], r"^ghcr\.io/github/github-mcp-server@sha256:[0-9a-f]{64}$")
        self.assertEqual(len(gh["args"]), 6)
        token = gh["env"]["GITHUB_PERSONAL_ACCESS_TOKEN"]
        self.assertTrue(token["secret"])
        self.assertEqual(token["fromEnv"], "GITHUB_PERSONAL_ACCESS_TOKEN")

    def test_filesystem_and_git_take_the_launch_directory_as_dot(self):
        self.assertEqual(self.servers["filesystem"]["args"][-1], ".")
        self.assertEqual(self.servers["filesystem"]["args"].count("."), 1)
        git_args = self.servers["git"]["args"]
        self.assertEqual(git_args[1:], ["--repository", "."])

    def test_supabase_is_read_only_with_token_from_env_not_argv(self):
        sb = self.servers["supabase"]
        self.assertIn("--read-only", sb["args"])
        self.assertFalse([a for a in sb["args"] if "access-token" in a])
        self.assertTrue(sb["env"]["SUPABASE_ACCESS_TOKEN"]["secret"])

    def test_docker_and_postgresql_entries_are_removed(self):
        self.assertNotIn("docker", self.servers)
        self.assertNotIn("postgresql", self.servers)

    def test_no_nonexistent_or_removed_package_in_source_or_any_projection(self):
        texts = {SERVERS_YAML: SERVERS_YAML.read_text(encoding="utf-8")}
        for path in PROJECTIONS:
            self.assertTrue(path.is_file(), path)
            texts[path] = path.read_text(encoding="utf-8")
        for path, text in texts.items():
            for needle in REMOVED_OR_NONEXISTENT:
                self.assertNotIn(needle, text, f"{needle} in {path.relative_to(REPO_ROOT)}")

    def test_removed_server_keys_absent_and_new_launchers_present_in_every_projection(self):
        for path in PROJECTIONS:
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(REPO_ROOT)
            for key in ("docker-mcp", "postgres-mcp", '"docker":', '"postgresql":'):
                self.assertNotIn(key, text, f"{key} in {rel}")
            self.assertIn("@playwright/mcp@0.0.83", text, rel)
            if path.parts[-2:] == (".vscode", "mcp.json"):
                continue  # core servers only on the github platform
            self.assertIn("@modelcontextprotocol/server-filesystem@1.0.0", text, rel)
            self.assertIn("mcp-server-git@2026.10.10", text, rel)
            self.assertIn("--repository", text, rel)
            self.assertIn("--read-only", text, rel)
            self.assertIn("ghcr.io/github/github-mcp-server@sha256:", text, rel)

if __name__ == "__main__":
    unittest.main()
