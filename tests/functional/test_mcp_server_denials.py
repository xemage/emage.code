"""T658 (SEC-T657-01) -- server-level denial of the unsafe Playwright tools on Opencode and Gemini CLI.

Opencode, Gemini CLI and Cursor do not restrict MCP tools by an agent's tool list, so the narrowed
Playwright grants (T657) are not enforced there. Two of the three platforms document a server-level
denial, and `sync.mjs` now emits it from ONE list (`denyTools` of the `playwright` entry in
knowledge/mcp/servers.yaml):

* Opencode: a top-level `permission` entry `playwright_<tool>: deny` in `.opencode/opencode.json`;
* Gemini CLI: `mcpServers.playwright.excludeTools` in `.gemini/settings.json`.

Mechanism, sources and verified/unverified status: docs/artifacts/mcp-server-denials-v1.md.
Cursor documents no such mechanism and stays open. This file pins:

- the single source list and its six names;
- the generator output per platform, with literal examples from the vendor documentation;
- the Opencode evaluation order (last matching rule wins, global rules before agent rules), modelled
  independently from the vendor source quoted in the artifact;
- the install merge (`scripts/merge-mcp-json.py`, and `install.sh --update`) with and without the
  provenance sidecar: the denial survives, a user's own entries are kept;
- the negative case: a user-owned `playwright-local` entry is another server name and is not denied;
- the documentation statements.

Static inspection plus local `node`, `python3` and `bash` runs on temporary directories; no network.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from tests._helpers.frontmatter import parse_file
from tests._helpers.repo import implementation_root, knowledge_root, repo_root

REPO = repo_root()
IMPL = implementation_root()
SYNC = IMPL / "scripts" / "sync.mjs"
MERGER = REPO / "scripts" / "merge-mcp-json.py"
INSTALLER = REPO / "scripts" / "install.sh"
ARTIFACT = REPO / "docs" / "artifacts" / "mcp-server-denials-v1.md"
SERVERS_YAML = knowledge_root() / "mcp" / "servers.yaml"

# The six tools no agent holds (docs/artifacts/mcp-tool-name-mapping-v1.md section 4). Pinned here as
# a literal, independently of servers.yaml: changing the shipped list must change this file too.
DENIED = [
    "browser_run_code_unsafe",
    "browser_evaluate",
    "browser_file_upload",
    "browser_drag",
    "browser_drop",
    "browser_network_request",
]
# `browser_network_request` is a prefix of the granted `browser_network_requests`: exact matching matters.
GRANTED_LOOKALIKE = "browser_network_requests"

GENERATED_MCP = {
    "claude-code": (".mcp.json", "mcpServers"),
    "cursor": (".cursor/mcp.json", "mcpServers"),
    "github": (".vscode/mcp.json", "servers"),
    "pi": (".pi/mcp.json", "mcpServers"),
    "cline": (".cline/mcp.json", "mcpServers"),
    "gemini": (".gemini/settings.json", "mcpServers"),
    "opencode": (".opencode/opencode.json", "mcp"),
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


# ---- independent model of the Opencode permission evaluation (vendor source, see the artifact) ----

def opencode_wildcard(text: str, pattern: str) -> bool:
    """packages/core/src/util/wildcard.ts: `*` is `.*`, `?` is `.`, other regex characters are literal."""
    text = text.replace("\\", "/")
    escaped = re.sub(r"[.+^${}()|\[\]\\]", lambda m: "\\" + m.group(0), pattern.replace("\\", "/"))
    escaped = escaped.replace("*", ".*").replace("?", ".")
    if escaped.endswith(" .*"):
        escaped = escaped[:-3] + "( .*)?"
    return re.fullmatch(escaped, text, re.S) is not None


def opencode_effect(action: str, *rulesets: list[tuple[str, str]]) -> str:
    """packages/core/src/permission.ts `evaluate`: the LAST matching rule wins; no match asks."""
    rules = [rule for ruleset in rulesets for rule in ruleset]
    for pattern, effect in reversed(rules):
        if opencode_wildcard(action, pattern):
            return effect
    return "ask"


def opencode_rules(permission) -> list[tuple[str, str]]:
    """A `permission` / `tools` map as ordered (pattern, effect) rules, string values only."""
    if isinstance(permission, str):
        return [("*", permission)]
    out = []
    for key, value in (permission or {}).items():
        if isinstance(value, bool):
            out.append((key, "allow" if value else "deny"))
        elif isinstance(value, str):
            out.append((key, value))
    return out


# Opencode's built-in agents start from `"*": "allow"`; the global config rules are appended after
# them and each agent's own rules after those (core/src/plugin/agent.ts and
# core/src/config/plugin/agent.ts at the commit named in the artifact).
OPENCODE_DEFAULTS = [("*", "allow")]


class SourceListTests(unittest.TestCase):
    def setUp(self):
        self.servers = yaml.safe_load(SERVERS_YAML.read_text(encoding="utf-8"))["servers"]

    def test_the_single_source_list_is_exactly_the_six_tools(self):
        self.assertEqual(self.servers["playwright"]["denyTools"], DENIED)

    def test_no_other_server_carries_a_deny_list(self):
        self.assertEqual({k for k, v in self.servers.items() if "denyTools" in v}, {"playwright"})

    def test_the_deny_list_is_not_hand_copied_into_the_generator(self):
        text = SYNC.read_text(encoding="utf-8")
        for name in DENIED:
            self.assertNotIn(name, text, "the tool names live in servers.yaml only")


class ShippedProjectionTests(unittest.TestCase):
    def test_opencode_denies_exactly_the_six_tools_at_top_level(self):
        cfg = _json(IMPL / ".opencode" / "opencode.json")
        self.assertEqual(cfg["permission"], {f"playwright_{t}": "deny" for t in DENIED})
        self.assertEqual(list(cfg["permission"]), [f"playwright_{t}" for t in DENIED])
        self.assertIn("playwright", cfg["mcp"], "the permission key names the registered server")

    def test_opencode_permission_has_no_wildcard_and_no_allow(self):
        for key, value in _json(IMPL / ".opencode" / "opencode.json")["permission"].items():
            self.assertNotIn("*", key)
            self.assertEqual(value, "deny")

    def test_gemini_excludes_exactly_the_six_tools_on_the_playwright_entry(self):
        servers = _json(IMPL / ".gemini" / "settings.json")["mcpServers"]
        self.assertEqual(servers["playwright"]["excludeTools"], DENIED)
        self.assertNotIn("includeTools", servers["playwright"])
        for name, entry in servers.items():
            if name != "playwright":
                self.assertNotIn("excludeTools", entry, name)

    def test_gemini_names_are_the_names_the_server_reports_not_fully_qualified_names(self):
        for tool in _json(IMPL / ".gemini" / "settings.json")["mcpServers"]["playwright"]["excludeTools"]:
            self.assertRegex(tool, r"^browser_[a-z_]+$")
            self.assertFalse(tool.startswith("mcp_"), tool)

    def test_other_platforms_carry_no_denial_and_are_documented_as_open_or_enforced_elsewhere(self):
        for platform in ("claude-code", "cursor", "github", "pi", "cline"):
            rel, wrapper = GENERATED_MCP[platform]
            text = (IMPL / rel).read_text(encoding="utf-8")
            with self.subTest(platform=platform):
                self.assertNotIn("excludeTools", text)
                self.assertNotIn('"permission"', text)
                self.assertNotIn('"deny"', text)

    def test_the_hardened_playwright_launch_is_unchanged_by_the_denial(self):
        for platform, (rel, wrapper) in GENERATED_MCP.items():
            entry = _json(IMPL / rel)[wrapper]["playwright"]
            with self.subTest(platform=platform):
                argv = entry["command"] if isinstance(entry["command"], list) else [entry["command"], *entry["args"]]
                self.assertEqual(argv.count("--blocked-origins"), 1)
                self.assertIn("--no-webmcp", argv)

    def test_the_provenance_sidecars_are_unchanged_in_shape(self):
        for platform in ("opencode", "gemini"):
            rel, _ = GENERATED_MCP[platform]
            sidecar = _json(IMPL / (rel + ".provenance.json"))
            self.assertEqual(set(sidecar), {"schemaVersion", "generatorOwnedKeys"})


class OpencodeEvaluationTests(unittest.TestCase):
    """The deny must win for every shipped agent, and the contrast cases must behave as documented."""

    @classmethod
    def setUpClass(cls):
        cfg = _json(IMPL / ".opencode" / "opencode.json")
        cls.global_rules = opencode_rules(cfg["permission"])
        cls.agents = {}
        for path in sorted((IMPL / ".opencode" / "agents").glob("*.md")):
            fm, _ = parse_file(path)
            cls.agents[path.stem] = opencode_rules(fm.get("tools"))

    def effect(self, agent_rules, tool: str, server: str = "playwright") -> str:
        return opencode_effect(f"{server}_{tool}", OPENCODE_DEFAULTS, self.global_rules, agent_rules)

    def test_wildcard_model_matches_the_vendor_examples(self):
        self.assertTrue(opencode_wildcard("mymcp_search", "mymcp_*"))
        self.assertTrue(opencode_wildcard("mymcp_search", "mymcp_search"))
        self.assertFalse(opencode_wildcard("playwright_browser_network_requests", "playwright_browser_network_request"))
        self.assertTrue(opencode_wildcard("playwright_browser_network_request", "playwright_browser_network_request"))
        self.assertFalse(opencode_wildcard("playwright-local_browser_evaluate", "playwright_browser_evaluate"))
        self.assertTrue(opencode_wildcard("grep pattern file.txt", "grep *"))

    def test_the_six_tools_are_denied_for_every_shipped_agent(self):
        self.assertGreaterEqual(len(self.agents), 28)
        for agent, rules in self.agents.items():
            for tool in DENIED:
                with self.subTest(agent=agent, tool=tool):
                    self.assertEqual(self.effect(rules, tool), "deny")

    def test_the_six_tools_are_denied_for_a_built_in_agent_that_has_no_rules_of_its_own(self):
        for tool in DENIED:
            self.assertEqual(self.effect([], tool), "deny", tool)

    def test_no_shipped_agent_rule_can_override_the_denial(self):
        # An agent rule that matches a denied name would come later than the global deny and win.
        for agent, rules in self.agents.items():
            for pattern, _effect in rules:
                for tool in DENIED:
                    with self.subTest(agent=agent, pattern=pattern, tool=tool):
                        self.assertFalse(opencode_wildcard(f"playwright_{tool}", pattern),
                                         f"{agent} has a rule `{pattern}` that matches a denied tool")

    def test_the_granted_tools_of_the_four_agents_stay_allowed(self):
        for agent in ("qa-engineer", "frontend-developer", "poc-qa-engineer", "demo-agent"):
            granted = [p for p, e in self.agents[agent] if p.startswith("playwright_") and e == "allow"]
            self.assertGreaterEqual(len(granted), 12, agent)
            for pattern in granted:
                with self.subTest(agent=agent, tool=pattern):
                    self.assertEqual(opencode_effect(pattern, OPENCODE_DEFAULTS, self.global_rules, self.agents[agent]),
                                     "allow")

    def test_the_lookalike_granted_tool_is_not_caught_by_its_prefix_entry(self):
        rules = self.agents["qa-engineer"]
        self.assertEqual(self.effect(rules, GRANTED_LOOKALIKE), "allow")
        self.assertEqual(self.effect(rules, "browser_network_request"), "deny")

    def test_a_later_agent_level_allow_overrides_the_global_deny(self):
        """Documented limit: agent rules come after the global rules and the last match wins."""
        for allow in ({"playwright_browser_evaluate": True}, {"playwright_*": True}, {"*": True}):
            with self.subTest(agent_rule=allow):
                self.assertEqual(self.effect(opencode_rules(allow), "browser_evaluate"), "allow")

    def test_a_per_agent_false_entry_denies_even_after_a_broader_allow(self):
        rules = opencode_rules({"playwright_*": True, "playwright_browser_evaluate": False})
        self.assertEqual(self.effect(rules, "browser_evaluate"), "deny")
        self.assertEqual(self.effect(rules, "browser_click"), "allow")

    def test_a_user_owned_playwright_local_server_is_not_denied(self):
        for tool in DENIED:
            with self.subTest(tool=tool):
                self.assertEqual(self.effect([], tool, server="playwright-local"), "allow")
                for agent, rules in self.agents.items():
                    self.assertNotEqual(self.effect(rules, tool, server="playwright-local"), "deny", agent)

    def test_the_generated_agent_files_never_allow_a_denied_tool(self):
        for agent, rules in self.agents.items():
            for tool in DENIED:
                self.assertNotIn((f"playwright_{tool}", "allow"), rules, agent)


class GeneratorFixtureTests(unittest.TestCase):
    """Run the real generator on a fixture root with the vendor documentation's own example names."""

    SERVERS = (
        "servers:\n"
        "  filteredServer:\n"
        "    tags: [core]\n"
        "    transport: stdio\n"
        "    command: python\n"
        "    args: [\"-m\", \"my_mcp_server\"]\n"
        "    denyTools: [dangerous_tool, file_deleter]\n"
        "  plain:\n"
        "    tags: [core]\n"
        "    transport: stdio\n"
        "    command: python\n"
        "    args: [\"-m\", \"other\"]\n"
        "  hosted:\n"
        "    tags: [core]\n"
        "    transport: remote\n"
        "    url: \"https://example.invalid/mcp\"\n"
        "    denyTools: [remote_tool]\n"
    )

    @staticmethod
    def build(root: Path, servers_text: str) -> None:
        (root / "platforms").mkdir()
        for path in (IMPL / "platforms").glob("*.json"):
            shutil.copy(path, root / "platforms" / path.name)
        shutil.copytree(IMPL / "_extras", root / "_extras")
        (root / "knowledge" / "mcp").mkdir(parents=True)
        (root / "knowledge" / "mcp" / "servers.yaml").write_text(servers_text, encoding="utf-8")
        for kind in ("agents", "commands", "instructions", "skills"):
            (root / "knowledge" / kind).mkdir()

    def run_sync(self, servers_text: str):
        if shutil.which("node") is None:
            self.skipTest("node is not installed")
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.build(root, servers_text)
        result = subprocess.run(["node", str(SYNC), "--root", str(root)], capture_output=True, text=True, check=False)
        return root, result

    def test_vendor_example_names_render_per_platform(self):
        root, result = self.run_sync(self.SERVERS)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        gemini = _json(root / ".gemini" / "settings.json")["mcpServers"]
        # docs/tools/mcp-server.md of gemini-cli: "excludeTools": ["dangerous_tool", "file_deleter"]
        self.assertEqual(gemini["filteredServer"]["excludeTools"], ["dangerous_tool", "file_deleter"])
        self.assertNotIn("excludeTools", gemini["plain"])
        self.assertEqual(gemini["hosted"]["excludeTools"], ["remote_tool"])
        opencode = _json(root / ".opencode" / "opencode.json")
        # opencode.ai/docs/agents: permission keys are the registered tool names `<server>_<tool>`
        self.assertEqual(opencode["permission"], {
            "filteredServer_dangerous_tool": "deny",
            "filteredServer_file_deleter": "deny",
            "hosted_remote_tool": "deny",
        })

    def test_a_server_name_with_odd_characters_is_cleaned_like_opencode_does(self):
        text = self.SERVERS.replace("filteredServer", "my.server")
        root, result = self.run_sync(text)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        permission = _json(root / ".opencode" / "opencode.json")["permission"]
        self.assertIn("my_server_dangerous_tool", permission)

    def test_other_platforms_ignore_the_list(self):
        root, result = self.run_sync(self.SERVERS)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for platform in ("claude-code", "cursor", "github", "pi", "cline"):
            rel, _ = GENERATED_MCP[platform]
            self.assertNotIn("dangerous_tool", (root / rel).read_text(encoding="utf-8"), platform)

    def test_without_any_deny_list_no_permission_key_and_no_excludeTools_are_emitted(self):
        text = "servers:\n  plain:\n    tags: [core]\n    transport: stdio\n    command: python\n    args: [\"-m\", \"x\"]\n"
        root, result = self.run_sync(text)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("permission", _json(root / ".opencode" / "opencode.json"))
        self.assertNotIn("excludeTools", (root / ".gemini" / "settings.json").read_text(encoding="utf-8"))

    def test_an_invalid_deny_list_stops_the_run_before_anything_is_written(self):
        bad_lists = {
            "wildcard": "[browser_*]",
            "bare star": "[\"*\"]",
            "space": "[\"two words\"]",
            "dot": "[\"a.b\"]",
            "duplicate": "[a, a]",
            "empty": "[]",
            "slash": "[\"a/b\"]",
        }
        for label, value in bad_lists.items():
            with self.subTest(case=label):
                root, result = self.run_sync(self.SERVERS.replace("[dangerous_tool, file_deleter]", value))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("denyTools", result.stderr)
                self.assertFalse((root / ".opencode").exists())

    def test_a_scalar_deny_list_stops_the_run(self):
        root, result = self.run_sync(self.SERVERS.replace("[dangerous_tool, file_deleter]", "browser_evaluate"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("denyTools", result.stderr)

    def test_regeneration_is_deterministic(self):
        first, r1 = self.run_sync(self.SERVERS)
        second, r2 = self.run_sync(self.SERVERS)
        self.assertEqual(r1.returncode, 0)
        self.assertEqual(r2.returncode, 0)
        for rel in (".opencode/opencode.json", ".gemini/settings.json"):
            self.assertEqual((first / rel).read_bytes(), (second / rel).read_bytes(), rel)


def run_merge(source: Path, dest: Path, old_sidecar: Path | None = None, new_sidecar: Path | None = None):
    cmd = [sys.executable, str(MERGER), "--source", str(source), "--dest", str(dest)]
    if old_sidecar is not None and new_sidecar is not None:
        cmd += ["--old-sidecar", str(old_sidecar), "--new-sidecar", str(new_sidecar)]
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


class MergeTests(unittest.TestCase):
    """merge-mcp-json.py keeps the generated denial and a user's own entries, with and without a sidecar."""

    def merge(self, platform: str, dest_data: dict, with_sidecar: bool):
        rel, _ = GENERATED_MCP[platform]
        source = IMPL / rel
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        dest = Path(tmp.name) / source.name
        dest.write_text(json.dumps(dest_data, indent=2) + "\n", encoding="utf-8")
        old = new = None
        if with_sidecar:
            old = Path(tmp.name) / (source.name + ".provenance.json")
            old.write_text(json.dumps({"schemaVersion": 1, "generatorOwnedKeys": ["playwright", "gitlab"]}), encoding="utf-8")
            new = IMPL / (rel + ".provenance.json")
        result = run_merge(source, dest, old, new)
        self.assertEqual(result.returncode, 0, result.stderr)
        # a second run must change nothing (the merge is a fixed point)
        first = dest.read_bytes()
        again = run_merge(source, dest, old, new)
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual(dest.read_bytes(), first, "a second merge changed the file")
        return json.loads(first.decode("utf-8"))

    # -- Gemini CLI: excludeTools --

    def test_gemini_union_keeps_the_users_tools_and_adds_the_generated_ones(self):
        for with_sidecar in (False, True):
            with self.subTest(sidecar=with_sidecar):
                user = {"mcpServers": {
                    "playwright": {"command": "npx", "args": ["-y", "x"], "excludeTools": ["my_tool", "browser_evaluate"]},
                    "mine": {"command": "x", "excludeTools": ["only_mine"], "includeTools": ["a"]},
                }, "theme": "dark"}
                merged = self.merge("gemini", user, with_sidecar)
                self.assertEqual(merged["mcpServers"]["playwright"]["excludeTools"],
                                 ["my_tool", "browser_evaluate"] + [t for t in DENIED if t != "browser_evaluate"])
                self.assertEqual(merged["mcpServers"]["mine"], user["mcpServers"]["mine"])
                self.assertEqual(merged["theme"], "dark")

    def test_gemini_user_entry_without_a_list_receives_the_generated_list(self):
        for with_sidecar in (False, True):
            with self.subTest(sidecar=with_sidecar):
                merged = self.merge("gemini", {"mcpServers": {"playwright": {"command": "npx", "args": []}}}, with_sidecar)
                self.assertEqual(merged["mcpServers"]["playwright"]["excludeTools"], DENIED)

    def test_gemini_a_fresh_file_gets_the_list(self):
        for with_sidecar in (False, True):
            with self.subTest(sidecar=with_sidecar):
                merged = self.merge("gemini", {"unrelated": True}, with_sidecar)
                self.assertEqual(merged["mcpServers"]["playwright"]["excludeTools"], DENIED)

    def test_gemini_a_non_list_value_is_replaced_by_the_generated_list(self):
        for bad in ("browser_evaluate", None, {"a": 1}, 3):
            with self.subTest(value=bad):
                merged = self.merge("gemini", {"mcpServers": {"playwright": {"excludeTools": bad}}}, False)
                self.assertEqual(merged["mcpServers"]["playwright"]["excludeTools"], DENIED)

    def test_gemini_an_element_the_generator_no_longer_ships_stays_fail_closed(self):
        merged = self.merge("gemini", {"mcpServers": {"playwright": {"excludeTools": ["browser_retired_tool"]}}}, True)
        self.assertEqual(merged["mcpServers"]["playwright"]["excludeTools"], ["browser_retired_tool"] + DENIED)

    def test_gemini_the_playwright_local_entry_is_not_denied(self):
        local = {"command": "npx", "args": ["-y", "@playwright/mcp@0.0.83", "--headless"]}
        for with_sidecar in (False, True):
            with self.subTest(sidecar=with_sidecar):
                merged = self.merge("gemini", {"mcpServers": {"playwright-local": dict(local)}}, with_sidecar)
                self.assertEqual(merged["mcpServers"]["playwright-local"], local)
                self.assertNotIn("excludeTools", merged["mcpServers"]["playwright-local"])
                self.assertEqual(merged["mcpServers"]["playwright"]["excludeTools"], DENIED)

    # -- Opencode: permission --

    def merged_effect(self, merged: dict, tool: str, server: str = "playwright") -> str:
        return opencode_effect(f"{server}_{tool}", OPENCODE_DEFAULTS, opencode_rules(merged.get("permission")))

    def test_opencode_user_rules_are_kept_and_the_generated_denials_come_last(self):
        for with_sidecar in (False, True):
            with self.subTest(sidecar=with_sidecar):
                user = {"mcp": {"mine": {"type": "local", "command": ["x"]}},
                        "permission": {"bash": {"*": "ask", "git *": "allow"}, "playwright_*": "allow",
                                       "playwright_browser_evaluate": "allow", "edit": "deny"}}
                merged = self.merge("opencode", user, with_sidecar)
                perm = merged["permission"]
                self.assertEqual(perm["bash"], {"*": "ask", "git *": "allow"})
                self.assertEqual(perm["edit"], "deny")
                self.assertEqual(list(perm)[-len(DENIED):], [f"playwright_{t}" for t in DENIED])
                self.assertEqual(list(perm)[:3], ["bash", "playwright_*", "edit"])
                for tool in DENIED:
                    self.assertEqual(perm[f"playwright_{tool}"], "deny")
                    self.assertEqual(self.merged_effect(merged, tool), "deny")
                self.assertEqual(self.merged_effect(merged, "browser_click"), "allow", "the user's wildcard still applies")
                self.assertEqual(merged["mcp"]["mine"], user["mcp"]["mine"])

    def test_opencode_a_string_shorthand_permission_is_kept_as_a_star_rule(self):
        for shorthand in ("allow", "ask", "deny"):
            for with_sidecar in (False, True):
                with self.subTest(shorthand=shorthand, sidecar=with_sidecar):
                    merged = self.merge("opencode", {"permission": shorthand}, with_sidecar)
                    perm = merged["permission"]
                    self.assertEqual(next(iter(perm.items())), ("*", shorthand))
                    for tool in DENIED:
                        self.assertEqual(self.merged_effect(merged, tool), "deny")
                    self.assertEqual(self.merged_effect(merged, "browser_click"), shorthand)

    def test_opencode_a_fresh_file_and_an_old_generated_file_receive_the_denials(self):
        old_generated = _json(IMPL / ".opencode" / "opencode.json")
        old_generated.pop("permission")
        for label, dest in (("fresh", {"theme": "x"}), ("old generated", old_generated)):
            for with_sidecar in (False, True):
                with self.subTest(case=label, sidecar=with_sidecar):
                    merged = self.merge("opencode", dest, with_sidecar)
                    self.assertEqual(merged["permission"], {f"playwright_{t}": "deny" for t in DENIED})
                    if label == "old generated":
                        self.assertEqual(merged["mcp"], _json(IMPL / ".opencode" / "opencode.json")["mcp"])

    def test_opencode_an_unusable_permission_value_is_replaced(self):
        for bad in (None, 5, ["allow"]):
            with self.subTest(value=bad):
                merged = self.merge("opencode", {"permission": bad}, False)
                self.assertEqual(merged["permission"], {f"playwright_{t}": "deny" for t in DENIED})

    def test_opencode_a_user_ask_for_another_tool_is_untouched(self):
        merged = self.merge("opencode", {"permission": {"playwright_browser_click": "ask"}}, True)
        self.assertEqual(merged["permission"]["playwright_browser_click"], "ask")
        self.assertEqual(self.merged_effect(merged, "browser_click"), "ask")

    def test_opencode_playwright_local_is_not_denied(self):
        user = {"mcp": {"playwright-local": {"type": "local", "command": ["npx", "-y", "@playwright/mcp@0.0.83"]}}}
        for with_sidecar in (False, True):
            with self.subTest(sidecar=with_sidecar):
                merged = self.merge("opencode", user, with_sidecar)
                self.assertIn("playwright-local", merged["mcp"])
                for tool in DENIED:
                    self.assertNotEqual(self.merged_effect(merged, tool, server="playwright-local"), "deny")
                    self.assertNotIn(f"playwright-local_{tool}", merged["permission"])

    def test_the_shipped_files_are_a_fixed_point_of_the_merge(self):
        for platform in ("opencode", "gemini"):
            rel, _ = GENERATED_MCP[platform]
            for with_sidecar in (False, True):
                with self.subTest(platform=platform, sidecar=with_sidecar):
                    merged = self.merge(platform, _json(IMPL / rel), with_sidecar)
                    self.assertEqual(merged, _json(IMPL / rel))

    def test_a_permission_or_excludeTools_key_elsewhere_is_not_special(self):
        # Only the top-level `permission` and an `excludeTools` list are merged specially.
        merged = self.merge("gemini", {"mcpServers": {"x": {"permission": "a"}}, "permission": "b"}, False)
        self.assertEqual(merged["permission"], "b")
        self.assertEqual(merged["mcpServers"]["x"], {"permission": "a"})


@unittest.skipUnless(shutil.which("bash"), "bash is not installed")
class InstallUpdateTests(unittest.TestCase):
    """End to end through install.sh: fresh install, then --update over a file the user edited."""

    def install(self, target: Path, platform: str, update: bool = False):
        args = ["bash", str(INSTALLER), "--target", str(target), "--platform", platform]
        if update:
            args.append("--update")
        env = dict(os.environ)
        return subprocess.run(args, cwd=REPO, capture_output=True, text=True, check=False, env=env)

    def test_opencode_fresh_install_then_update_keeps_denial_and_user_rules(self):
        for drop_sidecar in (False, True):
            with self.subTest(sidecar_dropped=drop_sidecar), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "project"
                target.mkdir()
                first = self.install(target, "opencode")
                self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
                cfg_path = target / ".opencode" / "opencode.json"
                self.assertEqual(_json(cfg_path)["permission"], {f"playwright_{t}": "deny" for t in DENIED})
                cfg = _json(cfg_path)
                cfg["permission"] = {"bash": "ask", "playwright_*": "allow", **cfg["permission"]}
                cfg["permission"]["playwright_browser_evaluate"] = "allow"  # the user re-allows one tool
                cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
                if drop_sidecar:
                    (target / ".opencode" / "opencode.json.provenance.json").unlink()
                second = self.install(target, "opencode", update=True)
                self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
                perm = _json(cfg_path)["permission"]
                self.assertEqual(perm["bash"], "ask")
                self.assertEqual(perm["playwright_*"], "allow")
                self.assertEqual(list(perm)[-len(DENIED):], [f"playwright_{t}" for t in DENIED])
                for tool in DENIED:
                    self.assertEqual(opencode_effect(f"playwright_{tool}", OPENCODE_DEFAULTS, opencode_rules(perm)), "deny")

    def test_gemini_fresh_install_then_update_keeps_denial_and_user_list(self):
        for drop_sidecar in (False, True):
            with self.subTest(sidecar_dropped=drop_sidecar), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "project"
                target.mkdir()
                first = self.install(target, "gemini")
                self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
                cfg_path = target / ".gemini" / "settings.json"
                self.assertEqual(_json(cfg_path)["mcpServers"]["playwright"]["excludeTools"], DENIED)
                cfg = _json(cfg_path)
                cfg["mcpServers"]["playwright"]["excludeTools"] = ["my_tool"]  # user dropped the generated six
                cfg["mcpServers"]["playwright-local"] = {"command": "npx", "args": ["-y", "@playwright/mcp@0.0.83"]}
                cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
                if drop_sidecar:
                    (target / ".gemini" / "settings.json.provenance.json").unlink()
                second = self.install(target, "gemini", update=True)
                self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
                merged = _json(cfg_path)["mcpServers"]
                self.assertEqual(merged["playwright"]["excludeTools"], ["my_tool"] + DENIED)
                self.assertNotIn("excludeTools", merged["playwright-local"])


class DocumentationTests(unittest.TestCase):
    DOCS = {
        "wiki": REPO / "docs" / "wiki" / "mcp-servers.md",
        "prerequisites": IMPL / "PREREQUISITES.md",
        "agents-root": REPO / "AGENTS.md",
        "agents-impl": IMPL / "AGENTS.md",
    }

    def text(self, key: str) -> str:
        return self.DOCS[key].read_text(encoding="utf-8")

    def test_artifact_records_both_platforms_with_status_and_sources(self):
        text = ARTIFACT.read_text(encoding="utf-8")
        self.assertIn("Based on: security-review-t657-tool-name-mapping-v1.md", text)
        for needle in ("Opencode", "Gemini CLI", "Cursor", "**verified**", "unverified", "permission",
                       "excludeTools", "last matching rule", "anomalyco/opencode@81200db2a3a8",
                       "google-gemini/gemini-cli@06d329873703", "https://opencode.ai/docs/permissions",
                       "https://geminicli.com/docs/tools/mcp-server"):
            self.assertIn(needle, text)
        for tool in DENIED:
            self.assertIn(tool, text)

    def test_artifact_states_that_an_agent_level_allow_overrides_the_global_deny(self):
        text = ARTIFACT.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?is)agent-level.{0,400}(overrid|wins)")
        self.assertRegex(text, r"(?i)per-agent `?(false|deny)")

    def test_artifact_never_recommends_the_unsafe_tool(self):
        text = ARTIFACT.read_text(encoding="utf-8")
        for line in text.splitlines():
            if "browser_run_code_unsafe" in line:
                self.assertRegex(line.replace("browser_run_code_unsafe", ""), r"(?i)\b(never|excluded|denied|deny|not|no)\b", line)

    def test_every_doc_names_both_mechanisms_the_gaps_and_the_playwright_local_exception(self):
        for key in self.DOCS:
            text = self.text(key)
            with self.subTest(doc=key):
                self.assertIn("excludeTools", text)
                self.assertRegex(text, r"`permission`")
                self.assertRegex(text, r"(?i)not (been )?observed")
                self.assertRegex(text, r"(?i)cursor")
                for tool in DENIED:
                    self.assertIn(tool, text)

    def test_docs_say_playwright_local_is_not_denied(self):
        for key in ("wiki", "prerequisites", "agents-root", "agents-impl"):
            text = self.text(key)
            with self.subTest(doc=key):
                self.assertRegex(text, r"(?is)(playwright-local[^.]{0,200}\b(not|no)\b[^.]{0,120}(denied|covered|denial)"
                                       r"|(denial|deny|denied|excludeTools)[^.]{0,200}playwright-local[^.]{0,120}\bnot\b)")

    def test_docs_no_longer_claim_the_narrowing_is_absent_on_opencode_and_gemini_without_the_denial(self):
        for key in self.DOCS:
            text = self.text(key)
            with self.subTest(doc=key):
                self.assertNotRegex(
                    text,
                    r"(?i)not in force on Opencode, Gemini CLI and Cursor, where an agent's tool list does not restrict MCP tools and every agent can call every tool of every configured server")

    def test_install_merge_rule_is_documented_where_the_merge_is(self):
        script = MERGER.read_text(encoding="utf-8")
        self.assertIn("excludeTools", script)
        self.assertIn("union", script)
        self.assertIn("LAST matching rule", script)


if __name__ == "__main__":
    unittest.main()
