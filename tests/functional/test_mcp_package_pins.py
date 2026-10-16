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


# T657 (SEC-T655-01): the named, non-"unsafe" Playwright tools each of the four agents holds. The
# agent bodies name no Playwright tool, so each set follows the role: E2E and acceptance checks
# (qa-engineer), responsive and accessibility checks (frontend-developer), happy-path smoke tests
# (poc-qa-engineer), staged demo flows (demo-agent). A tool added here must be added in the agent
# source in the same change; `browser_run_code_unsafe` (host code execution), `browser_evaluate`,
# `browser_file_upload`, `browser_drag`, `browser_drop` and `browser_network_request` (full
# headers and bodies) are deliberately outside every set.
_COMMON_READ = {"browser_navigate", "browser_snapshot", "browser_take_screenshot", "browser_wait_for", "browser_close"}
_INTERACT = {"browser_click", "browser_type", "browser_fill_form", "browser_press_key"}
EXPECTED_PLAYWRIGHT_GRANTS = {
    "qa-engineer": _COMMON_READ | _INTERACT | {
        "browser_navigate_back", "browser_find", "browser_select_option", "browser_hover", "browser_handle_dialog",
        "browser_console_messages", "browser_network_requests", "browser_resize", "browser_tabs"},
    "frontend-developer": _COMMON_READ | _INTERACT | {
        "browser_navigate_back", "browser_find", "browser_select_option", "browser_hover",
        "browser_console_messages", "browser_network_requests", "browser_emulate_media", "browser_resize",
        "browser_tabs"},
    "poc-qa-engineer": _COMMON_READ | _INTERACT | {
        "browser_find", "browser_select_option", "browser_handle_dialog", "browser_console_messages"},
    "demo-agent": _COMMON_READ | _INTERACT | {"browser_navigate_back", "browser_hover", "browser_resize"},
}
# The 25 tools `@playwright/mcp@0.0.83` registers by default (no --caps), read from a live
# `tools/list` and from the README at tag v0.0.83 (docs/artifacts/mcp-tool-name-mapping-v1.md).
PLAYWRIGHT_0_0_83_DEFAULT_TOOLS = {
    "browser_click", "browser_close", "browser_console_messages", "browser_drag", "browser_drop",
    "browser_emulate_media", "browser_evaluate", "browser_file_upload", "browser_fill_form", "browser_find",
    "browser_handle_dialog", "browser_hover", "browser_navigate", "browser_navigate_back",
    "browser_network_request", "browser_network_requests", "browser_press_key", "browser_resize",
    "browser_run_code_unsafe", "browser_select_option", "browser_snapshot", "browser_tabs",
    "browser_take_screenshot", "browser_type", "browser_wait_for",
}
PLAYWRIGHT_SERVER_FORMS = ("mcp__playwright", "mcp__playwright__*", "playwright/*", "playwright_*")
PLAYWRIGHT_EXCLUDED = {
    "browser_run_code_unsafe", "browser_evaluate", "browser_file_upload", "browser_drag", "browser_drop",
    "browser_network_request",
}


def _is_deny_line(line: str) -> bool:
    """An indented `<name>: false` entry of an Opencode `tools:` map (T663 per-agent deny)."""
    return re.fullmatch(r"\s+\S+: false", line) is not None


def _playwright_grants(slug: str) -> set[str]:
    prefix = "mcp__playwright__"
    return {t[len(prefix):] for t in _agent_tools(slug) if t.startswith(prefix)}


class PlaywrightGrantSetTests(unittest.TestCase):
    """T656/T657 (SEC-T655-01, SEC-T655-10): pin who holds which Playwright tool.

    The source form stays `mcp__playwright__<tool>`; sync.mjs renders it per platform (see
    test_mcp_tool_name_mapping.py). Exactly four agents hold named tools, nobody holds the whole
    server, and nobody holds an excluded tool, in the sources and in every generated projection.
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
        self.assertEqual(set(EXPECTED_PLAYWRIGHT_GRANTS), PLAYWRIGHT_AGENTS)

    def test_no_former_fetch_agent_holds_any_playwright_tool(self):
        for slug in sorted(FORMER_FETCH_AGENTS_WITHOUT_PLAYWRIGHT):
            tools = _agent_tools(slug)
            self.assertEqual([t for t in tools if "playwright" in t], [], slug)
            self.assertFalse([t for t in tools if t.startswith("mcp__fetch")], slug)

    def test_nobody_holds_the_bare_playwright_server(self):
        """The four agents must not regain the whole-server grant `mcp__playwright`."""
        for path in AGENTS_DIR.glob("*.md"):
            tools = _agent_tools(path.stem)
            self.assertNotIn("mcp__playwright", tools, path.stem)
            self.assertNotIn("mcp__playwright__*", tools, path.stem)

    def test_each_agent_holds_exactly_its_named_grant_set(self):
        for slug, expected in EXPECTED_PLAYWRIGHT_GRANTS.items():
            with self.subTest(agent=slug):
                tools = _agent_tools(slug)
                self.assertEqual(len(tools), len(set(tools)), "duplicate tool entry")
                self.assertEqual(_playwright_grants(slug), expected)

    def test_grants_are_real_tools_and_exclude_the_dangerous_ones(self):
        for slug, expected in EXPECTED_PLAYWRIGHT_GRANTS.items():
            with self.subTest(agent=slug):
                self.assertLessEqual(expected, PLAYWRIGHT_0_0_83_DEFAULT_TOOLS)
                self.assertFalse(expected & PLAYWRIGHT_EXCLUDED)

    def test_nobody_lists_the_unsafe_tool_or_a_wildcard_playwright_grant(self):
        for path in AGENTS_DIR.glob("*.md"):
            for tool in _agent_tools(path.stem):
                self.assertNotIn("browser_run_code_unsafe", tool, path.stem)
                if tool.startswith("mcp__playwright"):
                    self.assertRegex(tool, r"^mcp__playwright__[a-z_]+$", path.stem)

    def test_projections_hold_no_whole_server_playwright_form_and_no_excluded_tool(self):
        """Claude Code, Copilot, Opencode, Pi and Cursor projections of every agent."""
        root = REPO_ROOT / "implementation"
        files = (list((root / ".claude" / "agents").glob("*.md")) + list((root / ".github" / "agents").glob("*.agent.md"))
                 + list((root / ".opencode" / "agents").glob("*.md")) + list((root / ".pi" / "agents").glob("*.md"))
                 + list((root / ".cursor" / "agents").glob("*.mdc")))
        self.assertGreaterEqual(len(files), 5 * 20)
        for path in files:
            front = path.read_text(encoding="utf-8").split("---", 2)[1]
            # T663: an Opencode `name: false` line is a generated per-agent deny, not a grant; its names
            # are pinned in test_mcp_agent_denials.py
            tokens = re.findall(r"[A-Za-z0-9_./*-]+", "\n".join(
                l for l in front.splitlines() if not l.startswith(("name:", "description:")) and not _is_deny_line(l)))
            with self.subTest(file=path.relative_to(root).as_posix()):
                for token in tokens:
                    self.assertNotIn(token, PLAYWRIGHT_SERVER_FORMS)
                    for excluded in PLAYWRIGHT_EXCLUDED:
                        self.assertFalse(token.endswith(excluded), token)

    def test_server_level_denial_list_equals_the_six_excluded_tools(self):
        """T658 (SEC-T657-01): the denial emitted for Opencode and Gemini CLI is the excluded set, pinned."""
        servers = yaml.safe_load(SERVERS_YAML.read_text(encoding="utf-8"))["servers"]
        deny = servers["playwright"]["denyTools"]
        self.assertEqual(len(deny), 6)
        self.assertEqual(len(set(deny)), 6, "no duplicate")
        self.assertEqual(set(deny), PLAYWRIGHT_EXCLUDED)
        self.assertLessEqual(set(deny), PLAYWRIGHT_0_0_83_DEFAULT_TOOLS)
        for slug, granted in EXPECTED_PLAYWRIGHT_GRANTS.items():
            self.assertFalse(granted & set(deny), f"{slug} is granted a tool that the server-level denial removes")
        # the singular is denied, the plural stays grantable
        self.assertIn("browser_network_request", deny)
        self.assertNotIn("browser_network_requests", deny)
        self.assertTrue(any("browser_network_requests" in g for g in EXPECTED_PLAYWRIGHT_GRANTS.values()))

    def test_generated_denial_equals_the_list_on_opencode_and_gemini_only(self):
        root = REPO_ROOT / "implementation"
        gemini = json.loads((root / ".gemini" / "settings.json").read_text(encoding="utf-8"))
        self.assertEqual(set(gemini["mcpServers"]["playwright"]["excludeTools"]), PLAYWRIGHT_EXCLUDED)
        opencode = json.loads((root / ".opencode" / "opencode.json").read_text(encoding="utf-8"))
        self.assertEqual(set(opencode["permission"]), {f"playwright_{t}" for t in PLAYWRIGHT_EXCLUDED})
        self.assertEqual(set(opencode["permission"].values()), {"deny"})
        for rel in (".mcp.json", ".cursor/mcp.json", ".vscode/mcp.json", ".pi/mcp.json", ".cline/mcp.json"):
            text = (root / rel).read_text(encoding="utf-8")
            self.assertNotIn("excludeTools", text, rel)
            self.assertNotIn('"permission"', text, rel)


# T660 (SEC-T657-02): who holds which GitLab tool. Five agents keep the whole `gitlab` server; qa-engineer
# and scrum-master hold the named tools below, taken from the 275 tools that `@zereight/mcp-gitlab@2.2.5`
# registers (`build/tools/registry.js` of the npm tarball; docs/artifacts/security-review-t657-tool-name-mapping-v1.md).
# `discover_tools` is in both: the server's default `core` toolset omits milestones, label writes, issue links
# and pipelines, and only `discover_tools` (or GITLAB_TOOLSETS) exposes them. It changes the session's tool
# list and no GitLab data.
GITLAB_WHOLE_SERVER_HOLDERS = {
    "devops-engineer", "orchestrator", "release-manager", "poc-devops-engineer", "poc-orchestrator",
}
EXPECTED_GITLAB_GRANTS = {
    # sprint planning and board sync: issues, notes, links, labels, milestones, read-only MR lookups
    "scrum-master": {
        "create_issue", "update_issue", "list_issues", "get_issue", "list_issue_discussions", "create_issue_note",
        "create_issue_link", "list_issue_links", "get_issue_link",
        "list_labels", "get_label", "create_label", "update_label",
        "list_milestones", "get_milestone", "create_milestone", "edit_milestone", "get_milestone_issue",
        "get_milestone_merge_requests", "get_milestone_burndown_events",
        "list_merge_requests", "get_merge_request", "list_project_members", "discover_tools"},
    # bug reports and test reports: create issues and notes, read issues, MRs, pipelines and jobs
    "qa-engineer": {
        "create_issue", "create_issue_note", "get_issue", "list_issues", "list_issue_discussions", "list_labels",
        "list_merge_requests", "get_merge_request", "list_merge_request_changed_files", "get_merge_request_file_diff",
        "mr_discussions", "list_merge_request_pipelines",
        "list_pipelines", "get_pipeline", "list_pipeline_jobs", "get_pipeline_job", "get_pipeline_job_output",
        "get_pipeline_test_report", "get_pipeline_test_report_summary", "discover_tools"},
}
# Name patterns the two roles must never hold: merge, approval, push and file writes, delete/erase/purge,
# branch/tag/release/repository/group creation, protection changes, pipeline trigger/retry/cancel/play/create,
# variables, webhooks, deployments, raw API and GraphQL.
GITLAB_FORBIDDEN_NAME = re.compile(
    r"merge_merge_request|approve|push_files|create_or_update_file|delete|erase|purge|create_branch|create_tag|"
    r"create_release|create_repository|create_group$|fork_repository|protect|update_default_branch|update_project$|"
    r"trigger|retry|cancel|play_|create_pipeline|update_pipeline|variable|webhook|deployment|environment|"
    r"gitlab_api_request|execute_graphql|upload|download|create_commit_status|create_snippet|wiki|promote|"
    r"create_note$|move_work_item|dismiss|confirm|resolve")
GITLAB_WHOLE_SERVER_FORMS = ("mcp__gitlab", "mcp__gitlab__*", "gitlab/*", "gitlab_*")


def _gitlab_names(slug: str) -> set[str]:
    """Source form: `mcp__gitlab` (whole server, returned as `*`) or `mcp__gitlab__<tool>`."""
    names = set()
    for token in _agent_tools(slug):
        if token == "mcp__gitlab":
            names.add("*")
        elif token.startswith("mcp__gitlab__"):
            names.add(token[len("mcp__gitlab__"):])
    return names


class GitLabGrantSetTests(unittest.TestCase):
    """T660 (SEC-T657-02): exactly seven roles hold GitLab access; two of them only named, non-destructive tools."""

    def test_exactly_the_seven_roles_hold_gitlab_access(self):
        holders = {p.stem for p in AGENTS_DIR.glob("*.md") if _gitlab_names(p.stem)}
        self.assertEqual(holders, GITLAB_WHOLE_SERVER_HOLDERS | set(EXPECTED_GITLAB_GRANTS))
        self.assertEqual(len(holders), 7)

    def test_the_five_holders_keep_exactly_the_whole_server(self):
        for slug in sorted(GITLAB_WHOLE_SERVER_HOLDERS):
            with self.subTest(agent=slug):
                self.assertEqual(_gitlab_names(slug), {"*"})
                self.assertEqual(_agent_tools(slug).count("mcp__gitlab"), 1)

    def test_qa_engineer_and_scrum_master_hold_exactly_their_named_tools(self):
        for slug, expected in EXPECTED_GITLAB_GRANTS.items():
            with self.subTest(agent=slug):
                tools = _agent_tools(slug)
                self.assertEqual(len(tools), len(set(tools)), "duplicate tool entry")
                self.assertNotIn("*", _gitlab_names(slug))
                self.assertNotIn("mcp__gitlab", tools)
                self.assertNotIn("mcp__gitlab__*", tools)
                self.assertEqual(_gitlab_names(slug), expected)
                self.assertGreaterEqual(len(expected), 15)

    def test_named_tools_are_not_destructive_and_writes_are_pinned(self):
        for slug, expected in EXPECTED_GITLAB_GRANTS.items():
            with self.subTest(agent=slug):
                for name in sorted(expected):
                    self.assertRegex(name, r"^[a-z_]+$")
                    self.assertIsNone(GITLAB_FORBIDDEN_NAME.search(name), name)
        write_prefixes = ("create_", "update_", "edit_")
        qa_writes = {n for n in EXPECTED_GITLAB_GRANTS["qa-engineer"] if n.startswith(write_prefixes)}
        self.assertEqual(qa_writes, {"create_issue", "create_issue_note"})
        sm_writes = {n for n in EXPECTED_GITLAB_GRANTS["scrum-master"] if n.startswith(write_prefixes)}
        self.assertEqual(sm_writes, {
            "create_issue", "update_issue", "create_issue_note", "create_issue_link", "create_label",
            "update_label", "create_milestone", "edit_milestone"})

    def test_forbidden_pattern_does_catch_the_dangerous_names(self):
        for name in ("merge_merge_request", "push_files", "delete_branch", "delete_issue", "create_branch",
                     "create_tag", "create_release", "gitlab_api_request", "execute_graphql", "trigger_pipeline",
                     "retry_pipeline", "cancel_pipeline_job", "play_pipeline_job", "create_or_update_file",
                     "approve_merge_request", "create_pipeline", "erase_pipeline_job", "download_job_artifacts"):
            self.assertIsNotNone(GITLAB_FORBIDDEN_NAME.search(name), name)

    def test_every_projection_renders_the_same_sets(self):
        """Claude Code and Cursor keep the source form; Pi, Copilot and Opencode render it (T657 mapping)."""
        root = REPO_ROOT / "implementation"
        seven = GITLAB_WHOLE_SERVER_HOLDERS | set(EXPECTED_GITLAB_GRANTS)
        # platform -> (agent file suffix, prefix of a named tool, form of the whole server)
        platforms = {
            ".claude": (".md", "mcp__gitlab__", "mcp__gitlab"),
            ".cursor": (".mdc", "mcp__gitlab__", "mcp__gitlab"),
            ".pi": (".md", "mcp__gitlab__", "mcp__gitlab__*"),
            ".github": (".agent.md", "gitlab/", "gitlab/*"),
            ".opencode": (".md", "gitlab_", "gitlab_*"),
        }
        for platform, (suffix, prefix, whole_form) in platforms.items():
            files = sorted((root / platform / "agents").glob("*" + suffix))
            self.assertGreaterEqual(len(files), 20, platform)
            for path in files:
                slug = path.name[: -len(suffix)]
                front = path.read_text(encoding="utf-8").split("---", 2)[1]
                # T663: a generated `gitlab_*: false` (Opencode, agents without a GitLab tool) is a deny, not a grant
                tokens = set(re.findall(r"[A-Za-z0-9_./*-]+", "\n".join(
                    l for l in front.splitlines()
                    if not l.startswith(("name:", "description:")) and not _is_deny_line(l))))
                whole = {t for t in tokens if t in GITLAB_WHOLE_SERVER_FORMS}
                named = {t[len(prefix):] for t in tokens if t.startswith(prefix) and t not in GITLAB_WHOLE_SERVER_FORMS}
                with self.subTest(platform=platform, agent=slug):
                    if slug in GITLAB_WHOLE_SERVER_HOLDERS:
                        self.assertEqual(whole, {whole_form})
                        self.assertEqual(named, set())
                    elif slug in EXPECTED_GITLAB_GRANTS:
                        self.assertEqual(whole, set())
                        self.assertEqual(named, EXPECTED_GITLAB_GRANTS[slug])
                    else:
                        self.assertEqual(whole, set())
                        self.assertEqual(named, set())
            self.assertEqual({p.name[: -len(suffix)] for p in files} & seven, seven, platform)


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
