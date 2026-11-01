"""T690 (K-3, D-4 b) -- the `security-audit` and `poc-security-audit` servers on GitHub Copilot.

Before T690 the `github` platform (`mcp.tags: ["core"]`) emitted only the core servers into
`.vscode/mcp.json`, so the PoC security scan had no server on Copilot and the agent's rule made that a
`FAIL`. T690 adds a per-server platform list to `servers.yaml` (`extraPlatforms: [github]`) and a
`cwd: workspace` key (rendered `"cwd": "${workspaceFolder}"` for the vscode format only). This file pins:

- the generated `.vscode/mcp.json` and its provenance sidecar carry exactly the core servers plus those two,
  and no other `extended` server (`cwso`, `hf-mcp-server`, `context-retriever`, `filesystem`, `git`,
  `supabase`, `toolradar`);
- the two entries are the same local Python launchers as on the other platforms, with a workspace `cwd`,
  no `env` block and no secret;
- the Copilot agent files hold the tools in Copilot's `<server>/<tool>` form, and only the two agents that
  hold them on every other platform (`security-engineer`, `poc-security-engineer`) list them;
- the generator refuses an unknown or misspelled platform name (and a bad `cwd`) before it writes a file,
  honours `skipFormats` over `extraPlatforms`, and does not leak an `extended` server to `github`;
- the K-3 limitation sentences are gone from the live documentation and the new statement is there.

Local `node` runs on temporary directories; no network, no token, no VS Code (a live VS Code run was not made).
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

from tests._helpers.frontmatter import parse_file
from tests._helpers.repo import implementation_root, knowledge_root, repo_root

REPO = repo_root()
IMPL = implementation_root()
SYNC = IMPL / "scripts" / "sync.mjs"
SERVERS_YAML = knowledge_root() / "mcp" / "servers.yaml"

CORE_ON_COPILOT = {"gitlab", "playwright", "memory", "sequential-thinking", "brave", "context7", "hindsight"}
SECURITY_SERVERS = {"security-audit", "poc-security-audit"}
# Pinned as literals, independently of the generator: every other `extended` server stays off Copilot.
EXTENDED_NOT_ON_COPILOT = {
    "cwso", "hf-mcp-server", "context-retriever", "filesystem", "git", "supabase", "toolradar",
}
SECURITY_ENGINEER_TOOLS = {
    "security-audit/run_npm_audit", "security-audit/run_pip_audit",
    "security-audit/run_dotnet_list_vulnerable", "security-audit/grep_content",
}
POC_SECURITY_ENGINEER_TOOLS = {
    "security-audit/grep_content", "poc-security-audit/scan_secrets", "poc-security-audit/ref_containment",
}
EXPECTED_HOLDERS = {
    "security-engineer": SECURITY_ENGINEER_TOOLS,
    "poc-security-engineer": POC_SECURITY_ENGINEER_TOOLS,
}

OTHER_PLATFORM_FILES = (
    (".mcp.json", "mcpServers"), (".gemini/settings.json", "mcpServers"),
    (".opencode/opencode.json", "mcp"), (".pi/mcp.json", "mcpServers"), (".cline/mcp.json", "mcpServers"),
)


def _servers_yaml() -> dict:
    return yaml.safe_load(SERVERS_YAML.read_text(encoding="utf-8"))["servers"]


def _vscode() -> dict:
    return json.loads((IMPL / ".vscode" / "mcp.json").read_text(encoding="utf-8"))["servers"]


def _copilot_tools(slug: str) -> list[str]:
    fm, _ = parse_file(IMPL / ".github" / "agents" / f"{slug}.agent.md")
    return list(fm.get("tools") or [])


class GeneratedVscodeConfigTests(unittest.TestCase):
    def test_servers_yaml_lists_github_for_exactly_the_two_security_servers(self):
        servers = _servers_yaml()
        listed = {n for n, s in servers.items() if "extraPlatforms" in s}
        self.assertEqual(listed, SECURITY_SERVERS)
        for name in SECURITY_SERVERS:
            self.assertEqual(servers[name]["extraPlatforms"], ["github"], name)
            self.assertEqual(servers[name]["cwd"], "workspace", name)
            self.assertEqual(servers[name]["tags"], ["extended"], name)  # still extended: the other platforms are unchanged
        self.assertEqual({n for n, s in servers.items() if "cwd" in s}, SECURITY_SERVERS)

    def test_vscode_config_carries_the_core_servers_and_exactly_the_two_security_servers(self):
        servers = _vscode()
        self.assertEqual(set(servers), CORE_ON_COPILOT | SECURITY_SERVERS)

    def test_no_other_extended_server_leaks_into_vscode_or_its_sidecar(self):
        servers = _vscode()
        sidecar = json.loads((IMPL / ".vscode" / "mcp.json.provenance.json").read_text(encoding="utf-8"))
        for name in EXTENDED_NOT_ON_COPILOT:
            self.assertNotIn(name, servers)
            self.assertNotIn(name, sidecar["generatorOwnedKeys"])

    def test_the_expected_set_equals_what_servers_yaml_selects_for_github(self):
        manifest = json.loads((IMPL / "platforms" / "github.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["mcp"]["tags"], ["core"], "github still opts in to no `extended` server as a whole")
        selected = {n for n, s in _servers_yaml().items()
                    if set(s["tags"]) & set(manifest["mcp"]["tags"]) or "github" in s.get("extraPlatforms", [])}
        self.assertEqual(selected, CORE_ON_COPILOT | SECURITY_SERVERS)
        sidecar = json.loads((IMPL / ".vscode" / "mcp.json.provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(sidecar["generatorOwnedKeys"], sorted(selected))

    def test_the_two_entries_are_the_other_platforms_launchers_with_a_workspace_cwd_and_nothing_else(self):
        servers = _vscode()
        claude = json.loads((IMPL / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]
        for name in SECURITY_SERVERS:
            entry = servers[name]
            self.assertEqual(set(entry), {"command", "args", "cwd"}, name)
            self.assertEqual(entry["cwd"], "${workspaceFolder}", name)
            self.assertEqual(entry["command"], claude[name]["command"], name)
            self.assertEqual(entry["args"], claude[name]["args"], name)
        self.assertEqual(servers["security-audit"]["args"], ["-m", "implementation.runtime.security.audit_server"])
        self.assertEqual(
            servers["poc-security-audit"]["args"],
            ["-m", "implementation.runtime.security.poc_audit_server", "--allowed-root", "."],
        )

    def test_placeholders_only_and_no_secret_in_the_two_entries(self):
        for name in SECURITY_SERVERS:
            text = json.dumps(_vscode()[name])
            self.assertNotIn("env", _vscode()[name], name)
            for needle in ("token", "TOKEN", "secret", "SECRET", "password", "Bearer", "://", "KEY"):
                self.assertNotIn(needle, text, f"{name}: {needle}")
            # the only `$` is the VS Code workspace variable
            self.assertEqual(re.findall(r"\$\{[^}]*\}", text), ["${workspaceFolder}"], name)

    def test_cwd_is_written_for_vscode_only(self):
        for rel, wrapper in OTHER_PLATFORM_FILES:
            data = json.loads((IMPL / rel).read_text(encoding="utf-8"))[wrapper]
            for name in SECURITY_SERVERS:
                with self.subTest(file=rel, server=name):
                    self.assertIn(name, data)
                    self.assertNotIn("cwd", json.dumps(data[name]))

    def test_the_other_platforms_are_unchanged_in_which_extended_servers_they_carry(self):
        for rel, wrapper in OTHER_PLATFORM_FILES:
            data = json.loads((IMPL / rel).read_text(encoding="utf-8"))[wrapper]
            with self.subTest(file=rel):
                if rel == ".pi/mcp.json":
                    continue  # Pi leaves hindsight and cwso out (skipFormats), pinned in test_pi_optional_variables.py
                self.assertTrue((CORE_ON_COPILOT | SECURITY_SERVERS | EXTENDED_NOT_ON_COPILOT) <= set(data))


class CopilotAgentGrantTests(unittest.TestCase):
    def test_the_two_security_agents_hold_exactly_their_tools_in_copilots_form(self):
        for slug, expected in EXPECTED_HOLDERS.items():
            with self.subTest(agent=slug):
                held = {t for t in _copilot_tools(slug) if t.split("/", 1)[0] in SECURITY_SERVERS}
                self.assertEqual(held, expected)

    def test_no_other_copilot_agent_lists_either_server_and_nobody_holds_a_whole_server(self):
        files = sorted((IMPL / ".github" / "agents").glob("*.agent.md"))
        self.assertGreaterEqual(len(files), 28)
        for path in files:
            slug = path.name[: -len(".agent.md")]
            tools = _copilot_tools(slug)
            with self.subTest(agent=slug):
                for tool in tools:
                    self.assertNotIn("mcp__", tool, "the source form must not reach a Copilot agent")
                    if tool.split("/", 1)[0] in SECURITY_SERVERS:
                        self.assertIn(slug, EXPECTED_HOLDERS)
                        self.assertNotIn("*", tool)
                if slug not in EXPECTED_HOLDERS:
                    self.assertFalse([t for t in tools if t.startswith(tuple(f"{s}/" for s in SECURITY_SERVERS))])

    def test_the_copilot_holders_are_the_agents_that_hold_the_tools_on_every_other_platform(self):
        claude_form = re.compile(r"mcp__((?:poc-)?security-audit)__([a-z_]+)")
        copilot_form = re.compile(r"((?:poc-)?security-audit)/([a-z_]+)")
        claude: dict[str, set[str]] = {}
        for path in sorted((IMPL / ".claude" / "agents").glob("*.md")):
            front = path.read_text(encoding="utf-8").split("---", 2)[1]
            tools = {f"{s}/{t}" for s, t in claude_form.findall(front)}
            if tools:
                claude[path.stem] = tools
        copilot: dict[str, set[str]] = {}
        for path in sorted((IMPL / ".github" / "agents").glob("*.agent.md")):
            front = path.read_text(encoding="utf-8").split("---", 2)[1]
            tools = {f"{s}/{t}" for s, t in copilot_form.findall(front)}
            if tools:
                copilot[path.name[: -len(".agent.md")]] = tools
        self.assertEqual(claude, copilot)
        self.assertEqual(copilot, EXPECTED_HOLDERS)


class _Scratch(unittest.TestCase):
    """A temporary generator root with a probe servers.yaml and the real platform manifests."""

    def run_sync(self, servers_text: str, *extra: str) -> tuple[Path, subprocess.CompletedProcess]:
        if shutil.which("node") is None:
            self.skipTest("node is not installed")
        root = Path(tempfile.mkdtemp(prefix="t690-sync-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        (root / "platforms").mkdir()
        for path in (IMPL / "platforms").glob("*.json"):
            shutil.copy(path, root / "platforms" / path.name)
        shutil.copytree(IMPL / "_extras", root / "_extras")
        for kind in ("mcp", "agents", "commands", "instructions", "skills"):
            (root / "knowledge" / kind).mkdir(parents=True)
        (root / "knowledge" / "mcp" / "servers.yaml").write_text(servers_text, encoding="utf-8")
        proc = subprocess.run(["node", str(SYNC), "--root", str(root), *extra], capture_output=True, text=True, check=False)
        return root, proc

    @staticmethod
    def names(root: Path, rel: str) -> set[str]:
        data = json.loads((root / rel).read_text(encoding="utf-8"))
        for wrapper in ("mcpServers", "servers", "mcp"):
            if wrapper in data:
                return set(data[wrapper])
        raise AssertionError(rel)


def _probe(**extra: str) -> str:
    lines = [
        "servers:",
        "  coreprobe:", "    tags: [core]", "    transport: stdio", "    command: npx", '    args: ["-y", "x@1.0.0"]',
        "  listed:", "    tags: [extended]", "    EXTRA_LISTED", "    transport: stdio", "    command: python3",
        '    args: ["-m", "listed"]',
        "  unlisted:", "    tags: [extended]", "    transport: stdio", "    command: python3", '    args: ["-m", "unlisted"]',
    ]
    text = "\n".join(lines) + "\n"
    return text.replace("    EXTRA_LISTED\n", "".join(f"    {k}: {v}\n" for k, v in extra.items()))


class GeneratorPlatformListTests(_Scratch):
    def test_a_listed_extended_server_reaches_github_and_an_unlisted_one_does_not(self):
        root, proc = self.run_sync(_probe(extraPlatforms="[github]", cwd="workspace"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(self.names(root, ".vscode/mcp.json"), {"coreprobe", "listed"})
        sidecar = json.loads((root / ".vscode" / "mcp.json.provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(sidecar["generatorOwnedKeys"], ["coreprobe", "listed"])
        listed = json.loads((root / ".vscode" / "mcp.json").read_text(encoding="utf-8"))["servers"]["listed"]
        self.assertEqual(listed["cwd"], "${workspaceFolder}")
        self.assertEqual(list(listed), ["command", "args", "cwd"])
        for rel in (".mcp.json", ".gemini/settings.json", ".opencode/opencode.json", ".cline/mcp.json", ".pi/mcp.json"):
            with self.subTest(file=rel):
                self.assertEqual(self.names(root, rel), {"coreprobe", "listed", "unlisted"})
                self.assertNotIn("cwd", (root / rel).read_text(encoding="utf-8"))

    def test_without_the_key_no_extended_server_reaches_github(self):
        root, proc = self.run_sync(_probe())
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(self.names(root, ".vscode/mcp.json"), {"coreprobe"})
        self.assertNotIn("cwd", (root / ".vscode" / "mcp.json").read_text(encoding="utf-8"))

    def test_skip_formats_still_wins_over_the_platform_list(self):
        root, proc = self.run_sync(_probe(extraPlatforms="[github]", skipFormats="[vscode]"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(self.names(root, ".vscode/mcp.json"), {"coreprobe"})
        sidecar = json.loads((root / ".vscode" / "mcp.json.provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(sidecar["generatorOwnedKeys"], ["coreprobe"])

    def test_the_platform_list_adds_no_server_to_a_platform_that_is_not_named(self):
        # `claude-code` already carries every extended server; a list that names it changes nothing there,
        # and `github` still gets nothing.
        root, proc = self.run_sync(_probe(extraPlatforms="[claude-code]"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(self.names(root, ".vscode/mcp.json"), {"coreprobe"})


class GeneratorRefusalTests(_Scratch):
    """A bad value stops the run with a non-zero exit before any file is written."""

    def assert_refused(self, servers_text: str, needle: str, *extra: str) -> None:
        root, proc = self.run_sync(servers_text, *extra)
        self.assertNotEqual(proc.returncode, 0, proc.stdout)
        self.assertIn(needle, proc.stderr)
        written = [p for p in root.iterdir() if p.name not in {"platforms", "_extras", "knowledge"}]
        self.assertEqual(written, [], "nothing may be written when the run is refused")

    def test_an_unknown_platform_name_is_refused_before_any_write(self):
        self.assert_refused(_probe(extraPlatforms="[githb]"), "names a platform without a manifest: githb")

    def test_a_misspelled_platform_name_is_refused_even_when_one_platform_is_selected(self):
        self.assert_refused(_probe(extraPlatforms="[github, Copilot]"), "extraPlatforms", "--platform", "github")

    def test_a_misspelled_key_is_refused(self):
        self.assert_refused(_probe(extraPlatform="[github]"), "unknown key: extraPlatform")

    def test_empty_duplicate_and_non_name_values_are_refused(self):
        for value in ("[github, github]", "github", "[GitHub]", "[../github]"):
            with self.subTest(value=value):
                self.assert_refused(_probe(extraPlatforms=value), "extraPlatforms must be a non-empty array of distinct platform names")
        # an empty inline array is already refused by the servers.yaml reader
        self.assert_refused(_probe(extraPlatforms="[]"), "an empty inline array `[]` is not supported")

    def test_only_the_workspace_value_is_accepted_for_cwd(self):
        for value in ("elsewhere", "'${workspaceFolder}'", "/tmp", "true"):
            with self.subTest(value=value):
                self.assert_refused(_probe(cwd=value), "cwd must be one of: workspace")


DOC_FILES = (
    "README.md", "AGENTS.md", "implementation/AGENTS.md", "implementation/PREREQUISITES.md",
    "implementation/README.md", "implementation/SECURITY.md", "docs/wiki/mcp-servers.md",
    "docs/wiki/quick-start.md", "docs/wiki/implementation-guide.md",
    "implementation/knowledge/agents/security-engineer.md", "implementation/knowledge/agents/poc-security-engineer.md",
    "implementation/knowledge/mcp/servers.yaml",
)
# The wording of the K-3 limitation as it stood in the live documents before T690.
K3_PATTERNS = (
    r"does not carry it",
    r"has no server\s+to call there",
    r"not\*\* in GitHub Copilot",
    r"not in GitHub Copilot",
    r"because `extended` servers are not emitted to the `github` platform",
    r"On Copilot the reviewer's scan has no server",
    r"every platform except GitHub Copilot",
    r"all except `github`",
    r"Known issue K-3",
)


def k3_findings(name: str, text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text)
    return [f"{name}: {p}" for p in K3_PATTERNS if re.search(p, flat)]


class K3LimitationGoneTests(unittest.TestCase):
    def test_no_live_document_states_the_limitation_any_more(self):
        found = []
        for rel in DOC_FILES:
            found += k3_findings(rel, (REPO / rel).read_text(encoding="utf-8"))
        self.assertEqual(found, [])

    def test_the_detector_notices_the_old_sentences(self):
        for old in (
            "GitHub Copilot's `.vscode/mcp.json` does not carry it, so the scan has no server",
            "It is **not** in GitHub Copilot's `.vscode/mcp.json`",
            "Its config is generated for every platform except GitHub Copilot",
            "platforms whose manifest opts in (all except `github`: `gemini`)",
            "(Known issue K-3)",
        ):
            self.assertTrue(k3_findings("probe", old), old)

    def test_the_new_statement_is_in_the_wiki_readme_and_prerequisites(self):
        wiki = re.sub(r"\s+", " ", (REPO / "docs/wiki/mcp-servers.md").read_text(encoding="utf-8"))
        self.assertIn("since T690, GitHub Copilot's `.vscode/mcp.json`", wiki)
        self.assertIn("`extraPlatforms: [github]` on `security-audit` and `poc-security-audit` and on no other entry", wiki)
        self.assertIn('"cwd": "${workspaceFolder}"', wiki)
        self.assertIn("(unverified)", wiki.split("The VS Code entries differ", 1)[1].split("## Per-platform output", 1)[0])
        readme = re.sub(r"\s+", " ", (REPO / "README.md").read_text(encoding="utf-8"))
        self.assertIn("Cline and GitHub Copilot (`.vscode/mcp.json`", readme)
        prereq = (REPO / "implementation/PREREQUISITES.md").read_text(encoding="utf-8")
        self.assertIn("GitHub Copilot's `.vscode/mcp.json` included since T690", prereq)

    def test_the_extended_row_of_both_agents_files_names_the_exception(self):
        for rel in ("AGENTS.md", "implementation/AGENTS.md"):
            text = (REPO / rel).read_text(encoding="utf-8")
            row = next(line for line in text.splitlines() if line.startswith("| `extended` |"))
            with self.subTest(file=rel):
                self.assertIn("`github` opts in to no `extended` server as a whole", row)
                self.assertIn("`security-audit` and `poc-security-audit`", row)
                self.assertIn("`extraPlatforms`", row)
        self.assertEqual((REPO / "AGENTS.md").read_text().count("| `extended` |"), 1)

    def test_the_fail_rule_for_an_incomplete_scan_is_kept(self):
        wiki = (REPO / "docs/wiki/mcp-servers.md").read_text(encoding="utf-8")
        self.assertIn("treats a scan that did not complete (tool unavailable, error, timeout or `truncated`) as a blocker with the verdict `FAIL`", wiki)


if __name__ == "__main__":
    unittest.main()
