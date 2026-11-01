"""T658 (SEC-T657-01) -- server-level denial of the unsafe Playwright tools on Opencode and Gemini CLI.

Opencode and Gemini CLI do not restrict MCP tools by an agent's tool list, so the narrowed
Playwright grants (T657) are not enforced there. Both platforms document a server-level
denial, and `sync.mjs` now emits it from ONE list (`denyTools` of the `playwright` entry in
knowledge/mcp/servers.yaml):

* Opencode: a top-level `permission` entry `playwright_<tool>: deny` in `.opencode/opencode.json`;
* Gemini CLI: `mcpServers.playwright.excludeTools` in `.gemini/settings.json`.

Mechanism, sources and verified/unverified status: docs/artifacts/mcp-server-denials-v1.md.
This file pins:

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

import ast
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


# Two default behaviours for a name that no rule matches, both read from the vendor source (SEC-T663-05):
# the legacy runtime (v1.19.0 agent/agent.ts) starts an agent from `"*": "allow"`; the current core has no
# such default and `evaluate` falls back to `ask` (core/src/permission.ts). The global config rules are
# appended after the defaults and each agent's own rules after those. Deny assertions below run under both.
OPENCODE_DEFAULT_VARIANTS = ([("*", "allow")], [])
OPENCODE_DEFAULTS = OPENCODE_DEFAULT_VARIANTS[0]


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
        for platform in ("claude-code", "github", "pi", "cline"):
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
        """The effect under both default behaviours; a single word when they agree, else `a/b`."""
        found = sorted({opencode_effect(f"{server}_{tool}", d, self.global_rules, agent_rules)
                        for d in OPENCODE_DEFAULT_VARIANTS})
        return "/".join(found)

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
        # An agent rule that matches a denied name would come later than the global deny and win,
        # unless it is itself a deny (T663: the generated per-agent `false` entries are).
        for agent, rules in self.agents.items():
            for pattern, effect in rules:
                for tool in DENIED:
                    if effect == "deny":
                        continue
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
                self.assertNotIn("deny", self.effect([], tool, server="playwright-local"))
                for agent, rules in self.agents.items():
                    self.assertNotIn("deny", self.effect(rules, tool, server="playwright-local"), agent)

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
        for platform in ("claude-code", "github", "pi", "cline"):
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


# --- T673 (SEC-T658-06): documentation assertions anchored to the paragraph they protect ---------------------
#
# The earlier tests matched the whole file, so a statement in another paragraph satisfied them (a "not observed"
# in the per-agent text for the server-level one; the variable `union` for the merge rule's documentation), and
# the forbidden sentence they refused was one that only one of the four documents had ever carried. Each check is
# now a pure function of one text, applied to the block that carries the statement, with in-suite mutation tests
# (`DocumentationAnchorTests`) that break the property on an in-memory copy and require the function to notice.

def section_of(text: str, heading: str) -> str | None:
    """The heading line and everything up to the next heading of the same or a higher level; None if absent."""
    lines = text.splitlines()
    level = len(heading) - len(heading.lstrip("#"))
    for i, line in enumerate(lines):
        if line.startswith(heading):
            body = [line]
            for nxt in lines[i + 1:]:
                if re.match(r"#{1,%d} " % level, nxt):
                    break
                body.append(nxt)
            return "\n".join(body)
    return None


def line_starting(text: str, prefix: str) -> str | None:
    found = [line for line in text.splitlines() if line.startswith(prefix)]
    return found[0] if len(found) == 1 else None


def sentences(block: str) -> list[str]:
    return [part for part in re.split(r"(?<=\.)\s+", block) if part]


def clauses(block: str) -> list[str]:
    """Sentences, further split at a semicolon: one statement per item."""
    return [part for part in re.split(r"(?<=[.;])\s+", block) if part]


def t658_block(key: str, text: str) -> str | None:
    """The part of a document that states the server-level denial (T658), before the per-agent text (T663)."""
    if key == "wiki":
        section = section_of(text, "## Server-level denial of six Playwright tools")
        return None if section is None else section.split("\n### ", 1)[0]
    if key == "prerequisites":
        bullet = line_starting(text, "- **Server-level denial of six tools (T658):**")
        return None if bullet is None else bullet.split("Since T663", 1)[0]
    paragraph = next((l for l in text.splitlines() if "so since T658 the generator denies exactly six" in l), None)
    if paragraph is None:
        return None
    return paragraph[paragraph.index("so since T658 the generator denies exactly six"):].split("Since T663", 1)[0]


def local_block(key: str, text: str) -> str | None:
    """The block that says what the user-owned `playwright-local` entry does and does not get."""
    if key == "wiki":
        return line_starting(text, "- **`playwright-local` is not covered.**")
    if key == "prerequisites":
        return line_starting(text, "- **Tool names and agents:**")
    return next((l for l in text.splitlines() if "so since T658 the generator denies exactly six" in l), None)


GAP_SENTENCE = re.compile(r"(?i)agent file of your own that allows[^.]*overrides the denial")
OBSERVED_SENTENCE = re.compile(r"(?i)(vendor|documentation)[^.]*not (been )?observed in a live run")
LOCAL_NOT_DENIED = re.compile(r"(?i)`playwright-local` is \*{0,2}not\*{0,2} (denied|covered)|`playwright-local` entry is another server name and is not denied")


def denial_findings(key: str, text: str) -> list[str]:
    """What the T658 block of one document fails to state; empty when it states all of it."""
    block = t658_block(key, text)
    if block is None:
        return ["the T658 block is missing"]
    found = [f"{tool} is not named in the T658 block" for tool in DENIED if tool not in block]
    found += [f"{needle} is not named in the T658 block" for needle in ("`permission`", "`excludeTools`")
              if needle not in block]
    if not any(OBSERVED_SENTENCE.search(sentence) for sentence in sentences(block)):
        found.append("no sentence of the T658 block says the denial was documented and read, not observed live")
    if key != "prerequisites" and not any(GAP_SENTENCE.search(s) for s in sentences(block)):
        found.append("the T658 block does not say an agent file of the user's own that re-allows overrides the denial")
    return found


def local_findings(key: str, text: str) -> list[str]:
    block = local_block(key, text)
    if block is None:
        return ["the playwright-local block is missing"]
    found = []
    if not any(LOCAL_NOT_DENIED.search(s) for s in sentences(block)):
        found.append("no sentence of the playwright-local block says it is not denied")
    if key in ("wiki", "prerequisites") and "browser_run_code_unsafe" not in block:
        found.append("the playwright-local block does not warn that it still holds browser_run_code_unsafe")
    return found


def unqualified_open_claims(text: str) -> list[str]:
    """Sentences that put Opencode or Gemini CLI among the platforms where every agent can call every tool of
    every configured server, without the qualifier that the six tools are denied server-wide (T658)."""
    return [s for s in clauses(text)
            if re.search(r"(?i)every tool of every configured (MCP )?server", s)
            and re.search(r"Opencode|Gemini", s) and "not denied" not in s]


def merge_rule_findings(script: str) -> list[str]:
    """The documentation of the T658 merge rule in `merge-mcp-json.py`: the module docstring bullets and the two
    function docstrings, not any occurrence of the words in the code (`union` is also a variable name)."""
    tree = ast.parse(script)
    doc = ast.get_docstring(tree) or ""
    exclude = re.search(r"- `excludeTools`.*?(?=\n- |\n\n)", doc, re.S)
    permission = re.search(r"- top-level `permission`.*?(?=\n- |\n\n)", doc, re.S)
    found = []
    if not exclude or "union" not in exclude.group(0) or "never dropped" not in exclude.group(0):
        found.append("the module docstring does not say that excludeTools is a union and a user entry is never dropped")
    if not permission or "LAST matching rule" not in permission.group(0) or "moved to the end" not in permission.group(0):
        found.append("the module docstring does not say that generated permission keys go last (LAST matching rule)")
    functions = {n.name: ast.get_docstring(n) or "" for n in tree.body if isinstance(n, ast.FunctionDef)}
    if "Union" not in functions.get("merge_exclude_tools", ""):
        found.append("merge_exclude_tools has no docstring that says Union")
    if "generated rules last" not in functions.get("merge_permission", ""):
        found.append("merge_permission has no docstring that says generated rules last")
    return found


# Where the artifact may name the unsafe tool, and what the line must say there. A line that names it anywhere
# else, or in one of these places without its marker, fails.
ARTIFACT_UNSAFE_CONTEXTS = (
    ("## 1. Result", r"holds exactly the six tools that no agent holds"),
    ("## 2. Per-platform result", r'^\| Opencode \(.*"playwright_browser_run_code_unsafe": "deny"'),
    ("## 2. Per-platform result", r'^\| Gemini CLI \(.*"excludeTools": \["browser_run_code_unsafe"'),
    ("## 3. What is emitted, and from where", r"`denyTools: \[browser_run_code_unsafe,"),
    ("## 4. The playwright-local exception", r"is \*\*not\*\* denied on either platform, and it still contains `browser_run_code_unsafe`"),
)


RECOMMENDING_WORD = re.compile(r"(?i)\b(grant|recommend\w*|enable|give)\b")  # not "granted": the lookalike is granted


def unsafe_tool_findings(text: str) -> list[str]:
    heading, found, seen = None, [], set()
    for line in text.splitlines():
        if line.startswith("#"):
            heading = line
        if "browser_run_code_unsafe" not in line:
            continue
        hits = [i for i, (h, marker) in enumerate(ARTIFACT_UNSAFE_CONTEXTS)
                if heading == h and re.search(marker, line)]
        if hits and RECOMMENDING_WORD.search(line):
            found.append(f"a line that names the tool also recommends or grants it: {line[:80]}")
        elif hits:
            seen.update(hits)
        else:
            found.append(f"unanchored mention under {heading!r}: {line[:80]}")
    found += [f"expected context {ARTIFACT_UNSAFE_CONTEXTS[i][1][:50]!r} is missing"
              for i in range(len(ARTIFACT_UNSAFE_CONTEXTS)) if i not in seen]
    return found


def artifact_row_findings(text: str) -> list[str]:
    """Per-platform rows of the artifact: each carries its own status, mechanism, source and the not-observed note."""
    metadata = section_of(text, "## Metadata") or ""
    result = section_of(text, "## 1. Result") or ""
    emitted = section_of(text, "## 3. What is emitted, and from where") or ""
    found = []
    if "Based on: security-review-t657-tool-name-mapping-v1.md" not in metadata:
        found.append("the Metadata section does not carry the Based-on line")
    for tool in DENIED:
        if tool not in result:
            found.append(f"{tool} is not in section 1")
        if tool not in emitted:
            found.append(f"{tool} is not in section 3")
    rows = {
        "Opencode": ("| Opencode (", ("**verified**", "not observed live", "`permission`",
                                        "anomalyco/opencode@81200db2a3a8", "https://opencode.ai/docs/permissions",
                                        "last matching rule")),
        "Gemini CLI": ("| Gemini CLI (", ("**verified**", "not observed live", "`excludeTools`",
                                           "google-gemini/gemini-cli@06d329873703",
                                           "https://geminicli.com/docs/tools/mcp-server")),
        "Cursor": ("| Cursor (", ("**unverified, no mechanism found; nothing emitted**",)),
    }
    for name, (prefix, needles) in rows.items():
        row = line_starting(text, prefix)
        if row is None:
            found.append(f"the {name} row is missing or not unique")
            continue
        found += [f"the {name} row lacks {needle!r}" for needle in needles if needle not in row]
    return found


def override_findings(text: str) -> list[str]:
    section = section_of(text, "### 2.1 Opencode")
    if section is None:
        return ["section 2.1 is missing"]
    body = section.split("\n", 1)[1].lstrip()
    found = []
    if not body.startswith("**No.**"):
        found.append("section 2.1 does not answer No to whether the explicit deny overrides the agent allow")
    if not re.search(r"(?s)agent-level rule.{0,400}written after the global deny wins", section):
        found.append("section 2.1 does not say an agent-level rule written after the global deny wins")
    if not re.search(r"per-agent `false` \(deny\) entry is the only form that survives", section):
        found.append("section 2.1 does not name the per-agent false entry as the only form that survives")
    return found


CLAIM_DOCS = ("wiki", "agents-root", "agents-impl")


class DocumentationTests(unittest.TestCase):
    DOCS = {
        "wiki": REPO / "docs" / "wiki" / "mcp-servers.md",
        "prerequisites": IMPL / "PREREQUISITES.md",
        "agents-root": REPO / "AGENTS.md",
        "agents-impl": IMPL / "AGENTS.md",
    }

    def text(self, key: str) -> str:
        return self.DOCS[key].read_text(encoding="utf-8")

    def test_artifact_rows_sections_and_sources(self):
        self.assertEqual(artifact_row_findings(ARTIFACT.read_text(encoding="utf-8")), [])

    def test_artifact_section_2_1_says_the_agent_level_allow_overrides_the_global_deny(self):
        self.assertEqual(override_findings(ARTIFACT.read_text(encoding="utf-8")), [])

    def test_artifact_names_the_unsafe_tool_only_where_it_excludes_it(self):
        text = ARTIFACT.read_text(encoding="utf-8")
        self.assertEqual(unsafe_tool_findings(text), [])
        self.assertEqual(len([l for l in text.splitlines() if "browser_run_code_unsafe" in l]),
                         len(ARTIFACT_UNSAFE_CONTEXTS), "one line per anchored context")

    def test_every_doc_states_the_server_level_denial_where_it_describes_it(self):
        for key in self.DOCS:
            with self.subTest(doc=key):
                self.assertEqual(denial_findings(key, self.text(key)), [])

    def test_every_doc_says_playwright_local_is_not_denied_where_it_describes_it(self):
        for key in self.DOCS:
            with self.subTest(doc=key):
                self.assertEqual(local_findings(key, self.text(key)), [])

    def test_no_doc_claims_the_denial_is_absent_on_opencode_and_gemini(self):
        # PREREQUISITES.md is left out: it never carried a sentence of this shape (the pre-T658 text passes), so
        # the check cannot fail there. The wiki and both AGENTS.md files did carry it.
        for key in CLAIM_DOCS:
            with self.subTest(doc=key):
                self.assertEqual(unqualified_open_claims(self.text(key)), [])

    def test_install_merge_rule_is_documented_where_the_merge_is(self):
        self.assertEqual(merge_rule_findings(MERGER.read_text(encoding="utf-8")), [])


class DocumentationAnchorTests(unittest.TestCase):
    """Each anchored check must notice the property it protects being broken on an in-memory copy. The old
    whole-file assertion is evaluated on the same copy where it is cited, to show it could not tell."""

    def text(self, key: str) -> str:
        return DocumentationTests.DOCS[key].read_text(encoding="utf-8")

    def test_removing_the_not_observed_statement_of_the_t658_block_is_noticed_in_every_doc(self):
        for key in DocumentationTests.DOCS:
            text = self.text(key)
            block = t658_block(key, text)
            mutated_block, count = re.subn(r"not (been )?observed in a live run", "been confirmed in a live run", block)
            self.assertGreaterEqual(count, 1, key)
            mutated = text.replace(block, mutated_block, 1)
            self.assertNotEqual(mutated, text, key)
            with self.subTest(doc=key):
                self.assertEqual(denial_findings(key, text), [])
                self.assertTrue(any("not observed live" in f for f in denial_findings(key, mutated)))
                # the earlier whole-file assertion still passed: another paragraph says "not observed" too
                self.assertRegex(mutated, r"(?i)not (been )?observed")

    def test_dropping_a_tool_name_or_a_mechanism_from_the_t658_block_is_noticed(self):
        for key in DocumentationTests.DOCS:
            text = self.text(key)
            block = t658_block(key, text)
            for needle in ("browser_drag", "`excludeTools`", "`permission`"):
                with self.subTest(doc=key, dropped=needle):
                    self.assertIn(needle, block)
                    mutated = text.replace(block, block.replace(needle, "REDACTED"), 1)
                    self.assertTrue(denial_findings(key, mutated))

    def test_dropping_the_agent_file_override_gap_is_noticed(self):
        for key in ("wiki", "agents-root", "agents-impl"):
            text = self.text(key)
            block = t658_block(key, text)
            mutated = text.replace(block, GAP_SENTENCE.sub("An agent file of your own is irrelevant here", block), 1)
            self.assertNotEqual(mutated, text, key)
            with self.subTest(doc=key):
                self.assertTrue(any("overrides" in f for f in denial_findings(key, mutated)))

    def test_turning_playwright_local_into_a_denied_server_is_noticed(self):
        for key in DocumentationTests.DOCS:
            text = self.text(key)
            block = local_block(key, text)
            mutated_block = re.sub(r"is \*{0,2}not\*{0,2} (denied|covered)", "is denied", block)
            mutated_block = mutated_block.replace("entry is another server name and is not denied by",
                                                  "entry is another server name and is denied by")
            self.assertNotEqual(mutated_block, block, key)
            with self.subTest(doc=key):
                self.assertTrue(local_findings(key, text.replace(block, mutated_block, 1)))

    def test_losing_the_unsafe_tool_warning_of_the_playwright_local_block_is_noticed(self):
        for key in ("wiki", "prerequisites"):
            text = self.text(key)
            block = local_block(key, text)
            with self.subTest(doc=key):
                self.assertTrue(local_findings(key, text.replace(block, block.replace("browser_run_code_unsafe", "the tool"), 1)))

    def test_the_unqualified_claim_is_found_when_the_qualifier_is_removed(self):
        for key in CLAIM_DOCS:
            text = self.text(key)
            qualified = [s for s in clauses(text) if re.search(r"(?i)every tool of every configured (MCP )?server", s)
                         and re.search(r"Opencode|Gemini", s)]
            with self.subTest(doc=key):
                for sentence in qualified:  # the shipped sentences carry the qualifier
                    self.assertIn("not denied", sentence)
                    mutated = text.replace(sentence, sentence.replace("not denied", "denied"), 1)
                    self.assertEqual(len(unqualified_open_claims(mutated)), 1)

    def test_the_pre_t658_wording_is_found(self):
        old = ("The narrowing is not in force on Opencode, Gemini CLI and Cursor, where an agent's tool list does "
               "not restrict MCP tools and every agent can call every tool of every configured server (`docs/wiki`).")
        self.assertEqual(len(unqualified_open_claims(old)), 1)
        # SEC-T678-01: Cursor is gone from the docs; the check does not depend on the word (and none is asserted
        # absent: the historical artifacts keep it, ADR-010)
        cursor_free = ("The narrowing is not in force on Opencode and Gemini CLI, where an agent's tool list does "
                       "not restrict MCP tools and every agent can call every tool of every configured server.")
        self.assertEqual(len(unqualified_open_claims(cursor_free)), 1)
        self.assertEqual(unqualified_open_claims(cursor_free.replace("server.", "server that is not denied server-wide.")), [])
        wiki_old = ("On the platforms where it is not in force (Opencode, Gemini CLI, Cursor) an agent's tool list does "
                    "not restrict MCP tools: every agent can call every tool of every configured MCP server, including "
                    "the GitLab write tools elsewhere.")
        self.assertEqual(len(unqualified_open_claims(wiki_old)), 1)

    def test_an_unanchored_or_recommending_mention_of_the_unsafe_tool_is_found(self):
        text = ARTIFACT.read_text(encoding="utf-8")
        self.assertEqual(unsafe_tool_findings(text), [])
        # a table row that recommends the tool still said "not observed live", so the old word test passed it
        row = line_starting(text, "| Opencode (")
        bad = text.replace(row, row + " Grant `browser_run_code_unsafe` to the QA agent.", 1)
        self.assertRegex(bad.splitlines()[bad.splitlines().index(row + " Grant `browser_run_code_unsafe` to the QA agent.")]
                         .replace("browser_run_code_unsafe", ""), r"(?i)\b(never|excluded|denied|deny|not|no)\b")
        self.assertTrue(unsafe_tool_findings(bad))
        extra = text + "\nGrant `browser_run_code_unsafe` to the QA agent; we have not observed a problem.\n"
        self.assertTrue(unsafe_tool_findings(extra))
        self.assertRegex(extra.splitlines()[-1].replace("browser_run_code_unsafe", ""), r"(?i)\b(never|excluded|denied|deny|not|no)\b")
        gone = text.replace("`denyTools: [browser_run_code_unsafe,", "`denyTools: [x,")
        self.assertTrue(unsafe_tool_findings(gone))

    def test_each_artifact_row_and_section_is_noticed_when_it_loses_its_statement(self):
        text = ARTIFACT.read_text(encoding="utf-8")
        self.assertEqual(artifact_row_findings(text), [])
        for name, prefix, needle in (("Opencode", "| Opencode (", "https://opencode.ai/docs/permissions"),
                                     ("Gemini", "| Gemini CLI (", "not observed live"),
                                     ("Cursor", "| Cursor (", "**unverified, no mechanism found; nothing emitted**")):
            row = line_starting(text, prefix)
            with self.subTest(row=name):
                self.assertTrue(artifact_row_findings(text.replace(row, row.replace(needle, "x", 1), 1)))
        # a source URL that is only in another row no longer satisfies the Opencode row
        opencode = line_starting(text, "| Opencode (")
        gemini = line_starting(text, "| Gemini CLI (")
        swapped = text.replace(opencode, opencode.replace("https://opencode.ai/docs/permissions", ""), 1)
        swapped = swapped.replace(gemini, gemini + " https://opencode.ai/docs/permissions", 1)
        self.assertRegex(swapped, "https://opencode.ai/docs/permissions")
        self.assertTrue(artifact_row_findings(swapped))

    def test_the_section_2_1_answer_and_rule_are_noticed(self):
        text = ARTIFACT.read_text(encoding="utf-8")
        self.assertEqual(override_findings(text), [])
        self.assertTrue(override_findings(text.replace("**No.** The global deny", "**Yes.** The global deny", 1)))
        self.assertTrue(override_findings(text.replace("written after the global deny wins", "written after the global deny loses", 1)))
        self.assertTrue(override_findings(text.replace("is the only form that survives", "is one form that survives", 1)))

    def test_the_merge_script_documentation_is_noticed_when_only_the_code_keeps_the_words(self):
        script = MERGER.read_text(encoding="utf-8")
        self.assertEqual(merge_rule_findings(script), [])
        # the earlier assertIn("union", script) is satisfied by the variable of merge_exclude_tools
        no_docs = script.replace("the result is the union", "the result is the merge").replace("Union of two", "Merge of two")
        self.assertIn("union", no_docs)
        self.assertIn("excludeTools", no_docs)
        self.assertTrue(merge_rule_findings(no_docs))
        self.assertTrue(merge_rule_findings(script.replace("LAST matching rule", "last matching rule")))
        self.assertTrue(merge_rule_findings(script.replace("moved to the end", "left in place")))
        self.assertTrue(merge_rule_findings(script.replace("put generated rules last", "put generated rules first")))


if __name__ == "__main__":
    unittest.main()
