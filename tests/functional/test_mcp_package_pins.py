"""T638/T655 -- lock the MCP server package pin policy of `servers.yaml` (audit SEC-002).

Spec: docs/artifacts/mcp-server-packages-v1.md (§4, §9) and the user decisions of 2026-10-15.
T655 adds: the `fetch` server is removed everywhere, and the `playwright` entry carries the
hardened arguments of docs/artifacts/fetch-replacement-evaluation-v1.md §5.2 byte for byte in
every generated projection (one argument, never split or expanded).
Static inspection of the source of truth and of the generated projections; the only subprocess
is the local `scripts/merge-mcp-json.py`; no network, no package is installed or run.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
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
    "memory": "@modelcontextprotocol/server-memory@1.0.0",
    "sequential-thinking": "@modelcontextprotocol/server-sequential-thinking@1.0.0",
    "brave": "@brave/brave-search-mcp-server@2.1.4",
    "filesystem": "@modelcontextprotocol/server-filesystem@1.0.0",
    "supabase": "@supabase/mcp-server-supabase@0.13.0",
    "toolradar": "toolradar-mcp@2.1.0",
}

# T655: the hardened Playwright arguments. The --blocked-origins value is built from its parts so
# that the two brace lists are checked against the ranges they stand for: 100.64.0.0/10 (carrier
# grade NAT) is 100.64 to 100.127 and 172.16.0.0/12 (private) is 172.16 to 172.31.
_CGNAT = ",".join(str(n) for n in range(64, 128))
_PRIVATE_172 = ",".join(str(n) for n in range(16, 32))
BLOCKED_ORIGINS = ";".join([
    "localhost", "localhost:*", "localhost.", "localhost.:*", "*.localhost", "*.localhost:*",
    "127.*", "0.*", "10.*", "100.{" + _CGNAT + "}.*", "169.254.*", "172.{" + _PRIVATE_172 + "}.*",
    "192.168.*", "[::]", "[::]:*", "[::1]", "[::1]:*", "[::ffff:*", "[fc*", "[fd*", "[fe80:*", "*@*",
])
PLAYWRIGHT_ARGS = [
    "-y", "@playwright/mcp@0.0.83", "--headless", "--isolated", "--browser", "chromium",
    "--sandbox", "--block-service-workers", "--no-webmcp", "--blocked-origins", BLOCKED_ORIGINS,
]
PLAYWRIGHT_ENTRY_PATHS = {
    ".mcp.json": ("mcpServers", "str"),
    ".cursor/mcp.json": ("mcpServers", "str"),
    ".vscode/mcp.json": ("servers", "str"),
    ".gemini/settings.json": ("mcpServers", "str"),
    ".opencode/opencode.json": ("mcp", "list"),
    ".pi/mcp.json": ("mcpServers", "str"),
    ".cline/mcp.json": ("mcpServers", "str"),
}
REMOVED_OR_NONEXISTENT = (
    "@anthropic/mcp-filesystem",
    "@github/mcp-github",
    "@modelcontextprotocol/mcp-git",
    "@supabase/mcp\"",
    "@latest",
    "mcp-fetch-server",
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
            # args[0] is `-y`, args[1] the package; later items are flags, flag values and `.`
            # (T655: the playwright entry carries flag values such as `chromium`).
            self.assertEqual(entry["args"][0], "-y", key)
            pkgs = [entry["args"][1]]
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

    def test_fetch_server_is_removed_from_source_and_every_projection(self):
        self.assertNotIn("fetch", self.servers)
        for rel in PLAYWRIGHT_ENTRY_PATHS:
            path = REPO_ROOT / "implementation" / rel
            data = json.loads(path.read_text(encoding="utf-8"))
            servers = data[PLAYWRIGHT_ENTRY_PATHS[rel][0]]
            self.assertNotIn("fetch", servers, rel)
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("mcp-fetch-server", text, rel)
            sidecar = json.loads((path.parent / (path.name + ".provenance.json")).read_text(encoding="utf-8"))
            self.assertNotIn("fetch", sidecar["generatorOwnedKeys"], rel)

    def test_blocked_origins_expectation_is_complete(self):
        # T656 (SEC-T655-10): compare the YAML-parsed shipped value with the independently built
        # expectation, then check the two brace lists against the ranges they stand for. The
        # previous version only counted separators in the expectation itself.
        args = self.servers["playwright"]["args"]
        self.assertEqual(args.count("--blocked-origins"), 1)
        shipped = args[args.index("--blocked-origins") + 1]
        self.assertEqual(shipped, BLOCKED_ORIGINS)
        entries = shipped.split(";")
        self.assertEqual(len(entries), 22)
        self.assertEqual(len(set(entries)), 22, "no duplicate entry")
        cgnat = next(e for e in entries if e.startswith("100.{"))
        private = next(e for e in entries if e.startswith("172.{"))
        self.assertEqual(sorted(int(n) for n in cgnat[5:cgnat.index("}")].split(",")), list(range(64, 128)))
        self.assertEqual(sorted(int(n) for n in private[5:private.index("}")].split(",")), list(range(16, 32)))
        for required in ("localhost", "localhost:*", "localhost.", "localhost.:*", "*.localhost",
                         "*.localhost:*", "127.*", "0.*", "10.*", "169.254.*", "192.168.*", "[::]",
                         "[::1]", "[::ffff:*", "[fc*", "[fd*", "[fe80:*", "*@*"):
            self.assertIn(required, entries)

    def test_playwright_source_entry_has_the_hardened_args(self):
        pw = self.servers["playwright"]
        self.assertEqual(pw["command"], "npx")
        self.assertEqual(pw["args"], PLAYWRIGHT_ARGS)
        self.assertEqual(self.servers["playwright"]["args"].count("--blocked-origins"), 1)

    def test_playwright_hardened_args_are_identical_in_every_generated_config(self):
        for rel, (wrapper, shape) in PLAYWRIGHT_ENTRY_PATHS.items():
            data = json.loads((REPO_ROOT / "implementation" / rel).read_text(encoding="utf-8"))
            entry = data[wrapper]["playwright"]
            if shape == "list":  # Opencode: one `command` array, no shell
                self.assertEqual(entry["type"], "local", rel)
                self.assertEqual(entry["command"], ["npx"] + PLAYWRIGHT_ARGS, rel)
            else:
                self.assertEqual(entry["command"], "npx", rel)
                self.assertEqual(entry["args"], PLAYWRIGHT_ARGS, rel)
            argv = entry["command"] if shape == "list" else [entry["command"]] + entry["args"]
            # The origin list is exactly one argument: nothing split on `;` or `,`, nothing expanded.
            self.assertEqual(argv.count(BLOCKED_ORIGINS), 1, rel)
            self.assertEqual(argv[argv.index("--blocked-origins") + 1], BLOCKED_ORIGINS, rel)
            self.assertNotIn("env", entry, rel)  # no secret, no variable reference in this entry

    def test_blocked_origins_has_no_placeholder_syntax_a_client_would_expand(self):
        # Claude Code and Gemini expand ${VAR}; Cursor and VS Code expand ${env:VAR}; Opencode
        # expands {env:VAR} and {file:path}. The value must contain none of these openers.
        for opener in ("${", "$(", "{env:", "{file:", "`", "~"):
            self.assertNotIn(opener, BLOCKED_ORIGINS)

    def test_merge_script_keeps_the_hardened_args_and_prunes_the_retired_fetch_entry(self):
        old = {"mcpServers": {
            "fetch": {"command": "npx", "args": ["-y", "mcp-fetch-server@1.1.2"]},
            "playwright": {"command": "npx", "args": ["-y", "@playwright/mcp@0.0.83"]},
            "mine": {"command": "x", "args": []},
        }}
        gen = REPO_ROOT / "implementation" / ".mcp.json"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dest = tmp_path / "mcp.json"
            dest.write_text(json.dumps(old), encoding="utf-8")
            old_sidecar = tmp_path / "mcp.json.provenance.json"
            old_sidecar.write_text(json.dumps({"schemaVersion": 1, "generatorOwnedKeys": ["fetch", "playwright"]}), encoding="utf-8")
            new_sidecar = REPO_ROOT / "implementation" / ".mcp.json.provenance.json"
            result = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "merge-mcp-json.py"), "--source", str(gen),
                 "--dest", str(dest), "--old-sidecar", str(old_sidecar), "--new-sidecar", str(new_sidecar)],
                capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            merged = json.loads(dest.read_text(encoding="utf-8"))["mcpServers"]
        self.assertNotIn("fetch", merged)
        self.assertIn("mine", merged)
        self.assertEqual(merged["playwright"]["args"], PLAYWRIGHT_ARGS)


AGENTS_DIR = REPO_ROOT / "implementation" / "knowledge" / "agents"
# The four agents that hold the Playwright server (T655 review, SEC-T655-01).
PLAYWRIGHT_AGENTS = {"qa-engineer", "frontend-developer", "poc-qa-engineer", "demo-agent"}
# The agents that held the removed `fetch` server (T654 evaluation §1.1 lists ten; frontend-developer
# is one of them and also one of the four above, by its own earlier grant). The other nine must
# never hold a Playwright tool: it would hand them `browser_run_code_unsafe`.
FORMER_FETCH_AGENTS_WITHOUT_PLAYWRIGHT = {
    "solution-architect", "devops-engineer", "tech-lead", "security-engineer", "feasibility-agent",
    "technology-scout", "poc-orchestrator", "integration-agent", "backend-developer",
}


def _agent_tools(slug: str) -> list[str]:
    text = (AGENTS_DIR / f"{slug}.md").read_text(encoding="utf-8")
    front = text.split("---", 2)[1]
    return list(yaml.safe_load(front).get("tools") or [])


class PlaywrightGrantSetTests(unittest.TestCase):
    """T656 (SEC-T655-10): pin who holds a Playwright tool.

    T656 could not narrow the four holders to named `mcp__playwright__<tool>` entries: the
    generated names are not honoured by every platform (Copilot expects `server/tool`, Opencode
    `server_tool`, Gemini drops the tools line, Cline has no agent files). So this pins the state
    that exists: exactly four agents list the Playwright server, no other agent lists any
    Playwright tool, and nobody lists the unsafe tool. A later task that narrows the grants edits
    PLAYWRIGHT_AGENTS' expectation below together with the agent files.
    """

    def test_every_expected_agent_file_exists(self):
        for slug in PLAYWRIGHT_AGENTS | FORMER_FETCH_AGENTS_WITHOUT_PLAYWRIGHT:
            self.assertTrue((AGENTS_DIR / f"{slug}.md").is_file(), slug)

    def test_exactly_the_four_agents_hold_a_playwright_grant(self):
        holders = {
            path.stem for path in AGENTS_DIR.glob("*.md")
            if any(t.startswith("mcp__playwright") for t in _agent_tools(path.stem))
        }
        self.assertEqual(holders, PLAYWRIGHT_AGENTS)

    def test_no_former_fetch_agent_holds_any_playwright_tool(self):
        for slug in sorted(FORMER_FETCH_AGENTS_WITHOUT_PLAYWRIGHT):
            tools = _agent_tools(slug)
            self.assertEqual([t for t in tools if "playwright" in t], [], slug)
            self.assertFalse([t for t in tools if t.startswith("mcp__fetch")], slug)

    def test_nobody_lists_the_unsafe_tool_or_a_wildcard_playwright_grant(self):
        for path in AGENTS_DIR.glob("*.md"):
            for tool in _agent_tools(path.stem):
                self.assertNotIn("browser_run_code_unsafe", tool, path.stem)
                if tool.startswith("mcp__playwright"):
                    self.assertRegex(tool, r"^mcp__playwright(__[a-z_]+)?$", path.stem)


class MergeScriptPruneTests(unittest.TestCase):
    """T656 (SEC-T655-10, SEC-T655-02, SEC-T655-09): merge-mcp-json.py behaviour that the docs state."""

    def _merge(self, dest_servers: dict, *extra: str, with_sidecars: bool = False):
        gen = REPO_ROOT / "implementation" / ".mcp.json"
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "mcp.json"
            dest.write_text(json.dumps({"mcpServers": dest_servers}), encoding="utf-8")
            cmd = [sys.executable, str(REPO_ROOT / "scripts" / "merge-mcp-json.py"),
                   "--source", str(gen), "--dest", str(dest)]
            if with_sidecars:
                old = Path(tmp) / "mcp.json.provenance.json"
                old.write_text(json.dumps({"schemaVersion": 1, "generatorOwnedKeys": ["playwright", "gitlab"]}), encoding="utf-8")
                cmd += ["--old-sidecar", str(old),
                        "--new-sidecar", str(REPO_ROOT / "implementation" / ".mcp.json.provenance.json")]
            result = subprocess.run(cmd + list(extra), capture_output=True, text=True, check=False)
            return result, json.loads(dest.read_text(encoding="utf-8"))["mcpServers"]

    def test_force_prune_keys_fetch_removes_a_leftover_fetch_entry(self):
        fetch = {"command": "npx", "args": ["-y", "mcp-fetch-server@1.1.2"]}
        result, merged = self._merge({"fetch": fetch, "mine": {"command": "x", "args": []}},
                                     "--force-prune-keys", "fetch")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("fetch", merged)
        self.assertIn("mine", merged)
        self.assertEqual(merged["playwright"]["args"], PLAYWRIGHT_ARGS)

    def test_without_force_prune_and_without_sidecar_a_leftover_fetch_entry_stays(self):
        fetch = {"command": "npx", "args": ["-y", "mcp-fetch-server@1.1.2"]}
        result, merged = self._merge({"fetch": fetch})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(merged["fetch"], fetch)

    def test_combined_force_prune_refuses_when_one_name_is_already_gone_and_writes_nothing(self):
        fetch = {"command": "npx", "args": ["-y", "mcp-fetch-server@1.1.2"]}
        result, merged = self._merge({"fetch": fetch}, "--force-prune-keys", "docker,postgresql,fetch")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("docker", result.stderr)
        self.assertEqual(merged, {"fetch": fetch}, "a refused run must not write the destination")

    def test_per_key_form_works_when_the_other_names_are_already_gone(self):
        fetch = {"command": "npx", "args": ["-y", "mcp-fetch-server@1.1.2"]}
        result, merged = self._merge({"fetch": fetch}, "--force-prune-keys", "fetch")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("fetch", merged)

    def test_user_owned_playwright_local_entry_survives_the_merge(self):
        local = {"command": "npx", "args": ["-y", "@playwright/mcp@0.0.83", "--headless"]}
        old_fetch = {"command": "npx", "args": ["-y", "mcp-fetch-server@1.1.2"]}
        for with_sidecars in (False, True):
            result, merged = self._merge({"playwright-local": local, "fetch": old_fetch},
                                         with_sidecars=with_sidecars)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(merged["playwright-local"], local, with_sidecars)
            self.assertEqual(merged["playwright"]["args"], PLAYWRIGHT_ARGS, with_sidecars)


if __name__ == "__main__":
    unittest.main()
