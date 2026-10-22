"""T663 (SEC-T658-01, SEC-T657-04) -- per-agent tool denials in every generated Opencode agent file.

T658 added a server-level denial (a top-level `permission` of `opencode.json`). Opencode applies the
LAST matching rule and an agent's own rules come after the global ones, so a global deny does not
survive an allow written later in an agent. A per-agent `false` entry (`tools: { x: false }` in the
agent file) is the form that does. `sync.mjs` now writes, into EVERY Opencode agent file:

* `playwright_<tool>: false` for each `denyTools` entry of the `playwright` server (six names);
* `<server>_*: false` for each agent that holds no token of a server, for EVERY server the manifest
  carries (`denyUnlessGranted: true` on every `servers.yaml` entry, SEC-T663-01);
* `<server>_*: false` FIRST in the map for an agent that holds only NAMED tools of a server (for
  example qa-engineer and scrum-master for `gitlab`), so that file order makes its named allows the
  only tools of that server it can call;
* nothing new for an agent that holds the whole server.

The other denies are written LAST in the `tools` map. Mechanism, sources and verified/unverified status:
docs/artifacts/mcp-agent-denials-v1.md. This file pins:

- the single source (servers.yaml flags) and the manifest opt-in;
- what is emitted per agent class (a holder, a named-subset holder, a non-holder, a Playwright agent);
- the invariants over all shipped agent files: no name allowed and denied, denies last, no duplicate key;
- the Opencode evaluation order (defaults, global config, then the agent's rules in file order; last
  match wins), as a MODEL written independently from the vendor source quoted in the artifact. It is a
  model, not the vendor code: the live evidence is docs/artifacts/mcp-agent-denials-evidence-v1.md.
  Deny assertions run under both default behaviours the vendor source shows (allow-all, as the legacy
  runtime; no rule, which falls back to `ask`, as the current core);
- the generator on a fixture root (including the guard that refuses an allow and a deny of one name);
- `install.sh --update` replaces agent files wholesale;
- the documentation statements.

Static inspection plus local `node`, `python3` and `bash` runs on temporary directories; no network.
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
from tests.functional.test_mcp_server_denials import (
    DENIED,
    GRANTED_LOOKALIKE,
    opencode_effect,
    opencode_rules,
    opencode_wildcard,
)

REPO = repo_root()
IMPL = implementation_root()
SYNC = IMPL / "scripts" / "sync.mjs"
INSTALLER = REPO / "scripts" / "install.sh"
ARTIFACT = REPO / "docs" / "artifacts" / "mcp-agent-denials-v1.md"
SERVERS_YAML = knowledge_root() / "mcp" / "servers.yaml"
OPENCODE_AGENTS = IMPL / ".opencode" / "agents"
SOURCE_AGENTS = knowledge_root() / "agents"

# Pinned as literals, independently of the generator: the agents that hold GitLab tools.
# T666/T667: no agent holds the whole `gitlab` server any more; all seven holders hold named tools only, so the
# wildcard-first rule (`gitlab_*: false` before their named allows) applies to every one of them.
GITLAB_NAMED_SUBSET = {
    "qa-engineer", "scrum-master", "orchestrator", "poc-orchestrator",
    "devops-engineer", "release-manager", "poc-devops-engineer",
}
GITLAB_HOLDERS = GITLAB_NAMED_SUBSET
PLAYWRIGHT_HOLDERS = {"qa-engineer", "frontend-developer", "poc-qa-engineer", "demo-agent"}

# Pinned per server: (agents holding the bare `mcp__<server>`, agents holding only named tokens).
# Every other agent holds nothing of the server. A server that is not listed is held by nobody.
EXPECTED_HOLDERS = {
    "gitlab": (set(), GITLAB_NAMED_SUBSET),
    "playwright": (set(), PLAYWRIGHT_HOLDERS),
    "memory": ({"orchestrator", "poc-orchestrator"}, set()),
    "sequential-thinking": ({"orchestrator", "poc-orchestrator", "solution-architect"}, set()),
    "security-audit": (set(), {"security-engineer", "poc-security-engineer"}),
    "poc-security-audit": (set(), {"poc-security-engineer"}),
    "context-retriever": (set(), {"context-retriever"}),
}
# Servers the Opencode manifest carries (tags core and extended), pinned: adding a server to
# servers.yaml must add it here, so its denial is a deliberate decision.
OPENCODE_SERVERS = [
    "gitlab", "playwright", "memory", "sequential-thinking", "brave", "context7", "hindsight", "cwso",
    "hf-mcp-server", "context-retriever", "security-audit", "poc-security-audit", "filesystem",
    "git", "supabase", "toolradar",
]
# User decision of 2026-10-16 (AskUserQuestion, option label "Exempt the read/search servers
# (Recommended)"): these six declare `denyUnlessGranted: false` and are NOT denied per agent, so a generated
# agent (for example the orchestrator as the primary agent) keeps search, documentation and memory-layer
# access. Every other server declares `true`.
EXEMPT_SERVERS = ["brave", "context7", "hindsight", "cwso", "hf-mcp-server", "toolradar"]
DENIED_SERVERS = [s for s in OPENCODE_SERVERS if s not in EXEMPT_SERVERS]


def cleaned(server: str) -> str:
    """packages/core/src/tool/mcp.ts `namespace`: anything outside [a-zA-Z0-9_-] becomes `_`."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", server)


def wildcard(server: str) -> str:
    return f"{cleaned(server)}_*"


SIX_FALSE = [f"playwright_{t}" for t in DENIED]

# A sample of GitLab tools, write and read, by their registered Opencode names (`gitlab_<tool>`).
# `execute_graphql` and `gitlab_api_request` are in the vendor's readOnlyTools set although they can
# write: an exact "write tool" list built from that set would miss them.
GITLAB_WRITE_SAMPLE = [
    "merge_merge_request", "push_files", "delete_branch", "create_branch", "approve_merge_request",
    "create_pipeline", "delete_pipeline", "update_issue", "execute_graphql", "gitlab_api_request",
]
GITLAB_READ_SAMPLE = ["get_issue", "list_merge_requests", "get_pipeline"]

# The two default behaviours the vendor source shows for a name that no rule matches: the legacy runtime
# starts every agent from `"*": "allow"`; the current core has no such default and falls back to `ask`
# (packages/core/src/permission.ts `evaluate`). Every deny assertion must hold under both.
DEFAULT_VARIANTS = ([("*", "allow")], [])
OPENCODE_DEFAULTS = DEFAULT_VARIANTS[0]


def raw_tools_lines(path: Path) -> list[tuple[str, str]]:
    """The `tools:` block of an agent file as ordered (key, value) text pairs, duplicates preserved."""
    text = path.read_text(encoding="utf-8")
    block = re.match(r"^---\n(.*?)\n---\n", text, re.S).group(1).split("\n")
    pairs: list[tuple[str, str]] = []
    inside = False
    for line in block:
        if line == "tools:":
            inside = True
            continue
        if inside:
            m = re.fullmatch(r"  (\S+): (true|false)", line)
            if not m:
                break
            pairs.append((m.group(1), m.group(2)))
    return pairs


def source_tokens(slug: str) -> list[str]:
    fm, _ = parse_file(SOURCE_AGENTS / f"{slug}.md")
    return list(fm.get("tools", []))


def source_holds_gitlab(slug: str) -> bool:
    return any(t == "mcp__gitlab" or t.startswith("mcp__gitlab__") for t in source_tokens(slug))


def source_holders(server: str) -> tuple[set[str], set[str]]:
    """(whole-server holders, named-only holders) derived from the agent sources."""
    whole, named = set(), set()
    for path in SOURCE_AGENTS.glob("*.md"):
        tokens = [t for t in source_tokens(path.stem) if t == f"mcp__{server}" or t.startswith(f"mcp__{server}__")]
        if any(t == f"mcp__{server}" or t == f"mcp__{server}__*" for t in tokens):
            whole.add(path.stem)
        elif tokens:
            named.add(path.stem)
    return whole, named


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.servers = yaml.safe_load(SERVERS_YAML.read_text(encoding="utf-8"))["servers"]

    def test_every_opencode_server_declares_the_flag_explicitly_and_the_exemptions_are_pinned(self):
        self.assertEqual(sorted(self.servers), sorted(OPENCODE_SERVERS))
        for name, server in self.servers.items():
            with self.subTest(server=name):
                # the flag is declared on every entry: `false` is an explicit choice, never an omission
                self.assertIn("denyUnlessGranted", server)
                self.assertIs(server["denyUnlessGranted"], name not in EXEMPT_SERVERS)
                self.assertTrue(set(server["tags"]) & {"core", "extended"})
        text = SERVERS_YAML.read_text(encoding="utf-8")
        for name in EXEMPT_SERVERS:
            block = text.split(f"\n  {name}:\n", 1)[1].split("\n\n", 1)[0]
            self.assertIn("# User decision 2026-10-16 (T663)", block, f"{name}: a one-line comment says why")

    def test_gitlab_has_no_exact_tool_list(self):
        self.assertNotIn("denyTools", self.servers["gitlab"], "a hand-kept list of 275 tools would go stale")

    def test_playwright_keeps_its_exact_six_next_to_the_flag(self):
        self.assertEqual(self.servers["playwright"]["denyTools"], DENIED)
        self.assertEqual({k for k, v in self.servers.items() if "denyTools" in v}, {"playwright"})

    def test_the_opencode_manifest_opts_in_and_no_other_platform_does(self):
        for path in sorted(p for p in (IMPL / "platforms").glob("*.json") if p.name != "_manifest.schema.json"):
            agents = json.loads(path.read_text(encoding="utf-8"))["frontmatter"].get("agents", {})
            with self.subTest(platform=path.stem):
                self.assertEqual(agents.get("mcpAgentDenies"), True if path.stem == "opencode" else None)

    def test_the_holder_sets_match_the_agent_sources(self):
        derived = {p.stem for p in SOURCE_AGENTS.glob("*.md") if source_holds_gitlab(p.stem)}
        self.assertEqual(derived, GITLAB_HOLDERS)
        playwright = {p.stem for p in SOURCE_AGENTS.glob("*.md")
                      if any(t.startswith("mcp__playwright") for t in source_tokens(p.stem))}
        self.assertEqual(playwright, PLAYWRIGHT_HOLDERS)

    def test_the_pinned_holders_of_every_server_match_the_agent_sources(self):
        for server in OPENCODE_SERVERS:
            with self.subTest(server=server):
                self.assertEqual(source_holders(server), EXPECTED_HOLDERS.get(server, (set(), set())))

    def test_names_are_not_hand_copied_into_the_generator(self):
        text = SYNC.read_text(encoding="utf-8")
        for needle in ("gitlab", "playwright"):
            self.assertNotIn(needle, text.replace("playwright-local", ""), f"`{needle}` lives in servers.yaml only")


class EmittedPerAgentClassTests(unittest.TestCase):
    """Literal examples of what each class of agent receives."""

    def tools(self, slug: str) -> dict[str, bool]:
        fm, _ = parse_file(OPENCODE_AGENTS / f"{slug}.md")
        return fm["tools"]

    def falses(self, slug: str) -> list[str]:
        return [k for k, v in self.tools(slug).items() if v is False]

    def test_no_agent_holds_the_whole_gitlab_server_so_none_gets_the_allow_all_entry(self):
        """T667: `gitlab_*: true` appears in no generated agent file; every holder has the deny first."""
        self.assertEqual(source_holders("gitlab")[0], set())
        for path in sorted(OPENCODE_AGENTS.glob("*.md")):
            with self.subTest(agent=path.stem):
                self.assertIsNot(self.tools(path.stem).get("gitlab_*"), True)
        for slug in sorted(GITLAB_NAMED_SUBSET - PLAYWRIGHT_HOLDERS):
            with self.subTest(agent=slug):
                self.assertEqual([k for k in self.falses(slug) if k.startswith("playwright_")],
                                 ["playwright_*"] + SIX_FALSE)

    def test_a_whole_server_holder_of_another_server_gets_no_deny_of_that_server(self):
        """The whole-server class still exists for memory and sequential-thinking (orchestrators)."""
        for slug in ("orchestrator", "poc-orchestrator"):
            with self.subTest(agent=slug):
                self.assertTrue(self.tools(slug)["memory_*"] is True)
                self.assertNotIn("memory_*", self.falses(slug))

    def test_a_named_subset_gitlab_holder_gets_the_wildcard_first_then_its_named_allows(self):
        for slug in sorted(GITLAB_NAMED_SUBSET):
            with self.subTest(agent=slug):
                tools = self.tools(slug)
                keys = list(tools)
                self.assertIn("gitlab_*", keys[:3], "the wildcard deny is in the leading deny block")
                self.assertFalse(tools["gitlab_*"])
                named = [k for k in keys if k.startswith("gitlab_") and k != "gitlab_*"]
                self.assertGreaterEqual(len(named), 6)
                self.assertTrue(all(tools[k] is True for k in named))
                self.assertLess(keys.index("gitlab_*"), min(keys.index(k) for k in named))

    def test_a_non_holder_of_everything_gets_every_server_wildcard_then_the_six(self):
        held = set().union(*(w | n for w, n in EXPECTED_HOLDERS.values()))
        slugs = sorted(p.stem for p in OPENCODE_AGENTS.glob("*.md") if p.stem not in held)
        self.assertGreaterEqual(len(slugs), 10)
        # servers.yaml order; for `playwright` the wildcard precedes its six exact names
        expected = []
        for server in DENIED_SERVERS:
            expected.append(wildcard(server))
            if server == "playwright":
                expected += SIX_FALSE
        for slug in slugs:
            with self.subTest(agent=slug):
                self.assertEqual(self.falses(slug), expected)
                self.assertEqual([k for k, v in self.tools(slug).items() if v is True and "_" in k], [])

    def test_the_24_agents_without_a_playwright_tool_get_the_wildcard_and_the_six(self):
        slugs = sorted(p.stem for p in OPENCODE_AGENTS.glob("*.md") if p.stem not in PLAYWRIGHT_HOLDERS)
        self.assertEqual(len(slugs), 24)
        for slug in slugs:
            with self.subTest(agent=slug):
                f = self.falses(slug)
                self.assertIn("playwright_*", f)
                self.assertEqual([k for k in f if k.startswith("playwright_") and k != "playwright_*"], SIX_FALSE)
                self.assertLess(f.index("playwright_*"), f.index(SIX_FALSE[0]))

    def test_a_playwright_agent_gets_the_wildcard_first_its_named_allows_and_the_six_last(self):
        for slug in sorted(PLAYWRIGHT_HOLDERS):
            with self.subTest(agent=slug):
                tools = self.tools(slug)
                keys = list(tools)
                allowed = [k for k, v in tools.items() if v is True and k.startswith("playwright_")]
                self.assertGreaterEqual(len(allowed), 12)
                self.assertIn("playwright_browser_click", allowed)
                self.assertFalse(tools["playwright_*"])
                self.assertLess(keys.index("playwright_*"), min(keys.index(k) for k in allowed))
                self.assertEqual([k for k, v in tools.items() if v is False and k.startswith("playwright_")
                                  and k != "playwright_*"], SIX_FALSE)
                trues = [i for i, k in enumerate(keys) if tools[k] is True]
                self.assertEqual([k for k in keys if k in SIX_FALSE], SIX_FALSE)
                self.assertGreater(min(keys.index(k) for k in SIX_FALSE), max(trues))

    def test_literal_example_of_a_non_holder_file(self):
        text = (OPENCODE_AGENTS / "tech-lead.md").read_text(encoding="utf-8")
        head = text.split("\n---\n", 1)[0]
        self.assertTrue(head.endswith(
            "  web: true\n"
            "  gitlab_*: false\n"
            "  playwright_*: false\n"
            "  playwright_browser_run_code_unsafe: false\n"
            "  playwright_browser_evaluate: false\n"
            "  playwright_browser_file_upload: false\n"
            "  playwright_browser_drag: false\n"
            "  playwright_browser_drop: false\n"
            "  playwright_browser_network_request: false\n"
            "  memory_*: false\n"
            "  sequential-thinking_*: false\n"
            "  context-retriever_*: false\n"
            "  security-audit_*: false\n"
            "  poc-security-audit_*: false\n"
            "  filesystem_*: false\n"
            "  git_*: false\n"
            "  supabase_*: false"), head)

    def test_the_exempt_servers_get_no_entry_of_any_kind_in_any_agent_file(self):
        for path in sorted(OPENCODE_AGENTS.glob("*.md")):
            names = [n for n, _ in raw_tools_lines(path)]
            for server in EXEMPT_SERVERS:
                with self.subTest(agent=path.stem, server=server):
                    self.assertEqual([n for n in names if n.startswith(cleaned(server) + "_")], [])

    def test_the_agent_body_is_unchanged_by_the_denies(self):
        for path in sorted(OPENCODE_AGENTS.glob("*.md")):
            _, body = parse_file(path)
            _, source_body = parse_file(SOURCE_AGENTS / f"{path.stem}.md")
            with self.subTest(agent=path.stem):
                self.assertEqual(body, source_body)

    def test_other_platforms_carry_no_false_tool_entry_and_no_gitlab_wildcard(self):
        for platform, pattern in ((".github", "*.agent.md"), (".pi", "*.md"), (".claude", "*.md"),
                                  (".gemini", "*.md")):
            files = sorted((IMPL / platform / "agents").glob(pattern))
            self.assertGreaterEqual(len(files), 28, platform)
            for path in files:
                text = path.read_text(encoding="utf-8")
                with self.subTest(platform=platform, agent=path.name):
                    self.assertNotRegex(text.split("\n---\n", 1)[0], r"(?m)^\s+\S+: false$")
                    self.assertNotIn("gitlab_*", text.split("\n---\n", 1)[0])


class ShippedInvariantTests(unittest.TestCase):
    """Invariants over all 28 shipped Opencode agent files."""

    @staticmethod
    def pairs(slug):
        return raw_tools_lines(OPENCODE_AGENTS / f"{slug}.md")

    def test_the_file_count_floor(self):
        self.assertGreaterEqual(len(list(OPENCODE_AGENTS.glob("*.md"))), 28)

    def test_no_agent_lists_a_name_both_allowed_and_denied(self):
        for path in sorted(OPENCODE_AGENTS.glob("*.md")):
            pairs = raw_tools_lines(path)
            self.assertTrue(pairs, path.name)
            names = [n for n, _ in pairs]
            with self.subTest(agent=path.stem):
                self.assertEqual(len(names), len(set(names)), "a duplicate key: YAML would keep only the last")
                allowed = {n for n, v in pairs if v == "true"}
                denied = {n for n, v in pairs if v == "false"}
                self.assertFalse(allowed & denied, allowed & denied)

    def test_the_rule_for_every_server_and_every_agent_follows_the_holder_class(self):
        """For each server: a non-holder gets `<server>_*: false` after the allows, a whole-server holder
        none, a named-only holder the wildcard BEFORE every allow of that server (and before all allows)."""
        for server in DENIED_SERVERS:
            whole, named = source_holders(server)
            prefix = cleaned(server) + "_"
            for path in sorted(OPENCODE_AGENTS.glob("*.md")):
                slug = path.stem
                pairs = raw_tools_lines(path)
                names = [n for n, _ in pairs]
                values = dict(pairs)
                first_allow = min(i for i, (_, v) in enumerate(pairs) if v == "true")
                last_allow = max(i for i, (_, v) in enumerate(pairs) if v == "true")
                with self.subTest(server=server, agent=slug):
                    if slug in whole:
                        self.assertNotIn(wildcard(server), [n for n, v in pairs if v == "false"])
                        self.assertEqual(values.get(wildcard(server)), "true")
                    elif slug in named:
                        self.assertEqual(values[wildcard(server)], "false")
                        w = names.index(wildcard(server))
                        self.assertLess(w, first_allow, "the wildcard deny precedes every allow")
                        own = [i for i, (n, v) in enumerate(pairs) if n.startswith(prefix) and v == "true"]
                        self.assertTrue(own)
                        self.assertTrue(all(i > w for i in own))
                    else:
                        self.assertEqual(values[wildcard(server)], "false")
                        self.assertGreater(names.index(wildcard(server)), last_allow)
                        self.assertFalse([n for n in names if n.startswith(prefix) and n != wildcard(server)
                                          and values[n] == "true"])

    def test_denies_come_after_every_allow_except_the_leading_block_of_named_holders(self):
        # Last match wins: a deny written after every allow survives any broader allow of the same agent.
        # The deliberate exception is the leading block of `<server>_*: false` entries of an agent that
        # holds only NAMED tools of those servers: the named allows after it win over it.
        for path in sorted(OPENCODE_AGENTS.glob("*.md")):
            pairs = raw_tools_lines(path)
            lead = 0
            while lead < len(pairs) and pairs[lead][1] == "false":
                lead += 1
            leading = [n for n, _ in pairs[:lead]]
            expected = [wildcard(s) for s in DENIED_SERVERS if path.stem in source_holders(s)[1]]
            with self.subTest(agent=path.stem):
                self.assertEqual(leading, expected)
                rest = [v for _, v in pairs[lead:]]
                self.assertNotIn("true", rest[rest.index("false"):])

    def test_every_named_allow_comes_after_the_wildcard_deny_of_its_server(self):
        """Ordering, not distinct names, is what makes `<server>_*: false` plus named allows safe
        (SEC-T663 ordering invariant; pinned for every named holder of every server)."""
        for server in OPENCODE_SERVERS:
            for slug in sorted(source_holders(server)[1]):
                names = [n for n, _ in self.pairs(slug)]
                w = names.index(wildcard(server))
                named = [i for i, n in enumerate(names) if n.startswith(cleaned(server) + "_") and n != wildcard(server)]
                with self.subTest(server=server, agent=slug):
                    self.assertTrue(named)
                    self.assertTrue(all(i > w for i in named))

    def test_regression_only_the_six_exact_names_resolve_to_deny_for_every_agent(self):
        # REGRESSION-ONLY: this re-evaluates the generator's own output with the model in this file.
        # It cannot show that Opencode behaves this way (that is the artifact's source reading and the
        # resolver evidence); it catches a later edit that reorders or drops the entries.
        for path in sorted(OPENCODE_AGENTS.glob("*.md")):
            rules = opencode_rules(parse_file(path)[0]["tools"])
            for name in SIX_FALSE:
                for defaults in DEFAULT_VARIANTS:
                    with self.subTest(agent=path.stem, tool=name, defaults=bool(defaults)):
                        self.assertEqual(opencode_effect(name, defaults, rules), "deny")

    def test_no_agent_grants_a_denied_exact_name(self):
        for path in sorted(OPENCODE_AGENTS.glob("*.md")):
            for name, value in raw_tools_lines(path):
                if name in SIX_FALSE:
                    with self.subTest(agent=path.stem, tool=name):
                        self.assertEqual(value, "false")

    def test_every_false_entry_is_a_server_wildcard_or_one_of_the_six(self):
        allowed_false = set(SIX_FALSE) | {wildcard(s) for s in DENIED_SERVERS}
        for path in sorted(OPENCODE_AGENTS.glob("*.md")):
            with self.subTest(agent=path.stem):
                self.assertLessEqual({n for n, v in raw_tools_lines(path) if v == "false"}, allowed_false)


class OpencodeEvaluationTests(unittest.TestCase):
    """Effective permission per agent under the order the vendor source and the resolver show:
    built-in defaults, then the global config, then the agent's own rules in file order; last match wins.
    This is a MODEL of that behaviour (see the module docstring); every deny/allow assertion holds under
    both default behaviours (allow-all, and no default which falls back to ask)."""

    @classmethod
    def setUpClass(cls):
        cfg = json.loads((IMPL / ".opencode" / "opencode.json").read_text(encoding="utf-8"))
        cls.global_rules = opencode_rules(cfg["permission"])
        cls.agents = {p.stem: opencode_rules(parse_file(p)[0]["tools"]) for p in sorted(OPENCODE_AGENTS.glob("*.md"))}

    def effects(self, slug, name, global_extra=None, agent_extra=None):
        g = opencode_rules(global_extra or {})
        a = opencode_rules(agent_extra or {})
        return {opencode_effect(name, d, self.global_rules, g, self.agents[slug], a) for d in DEFAULT_VARIANTS}

    def effect(self, slug, name, global_extra=None, agent_extra=None):
        found = self.effects(slug, name, global_extra, agent_extra)
        self.assertEqual(len(found), 1, f"{slug} {name}: the result depends on the default behaviour: {found}")
        return next(iter(found))

    def holds(self, slug, server):
        whole, named = source_holders(server)
        return slug in whole, slug in named

    def test_a_non_holder_cannot_call_any_tool_of_any_server(self):
        samples = {"gitlab": GITLAB_WRITE_SAMPLE + GITLAB_READ_SAMPLE, "memory": ["create_entities"],
                   "git": ["git_commit"], "filesystem": ["write_file"],
                   "supabase": ["execute_sql"], "security-audit": ["run_npm_audit"],
                   "playwright": ["browser_click"]}
        for server, tools in samples.items():
            for slug in sorted(self.agents):
                if any(self.holds(slug, server)):
                    continue
                for tool in tools:
                    with self.subTest(server=server, agent=slug, tool=tool):
                        self.assertEqual(self.effect(slug, f"{cleaned(server)}_{tool}"), "deny")

    def test_a_non_holder_stays_denied_when_the_user_allows_the_server_globally(self):
        # The agent's rules come after the global config, so the user's global allow loses.
        for global_allow in ({"gitlab_*": "allow"}, {"*": "allow"}, {"gitlab_merge_merge_request": "allow"}):
            for slug in ("tech-lead", "backend-developer", "security-engineer"):
                with self.subTest(agent=slug, user_global=global_allow):
                    self.assertEqual(self.effect(slug, "gitlab_merge_merge_request", global_extra=global_allow), "deny")

    def test_the_exempt_servers_are_not_denied_for_any_agent(self):
        """User decision 2026-10-16: search, documentation and memory-layer servers stay reachable."""
        for server in EXEMPT_SERVERS:
            for slug in sorted(self.agents):
                with self.subTest(server=server, agent=slug):
                    self.assertNotIn("deny", self.effects(slug, f"{cleaned(server)}_some_tool"))
                    self.assertEqual(self.effect(slug, f"{cleaned(server)}_some_tool",
                                                 global_extra={f"{cleaned(server)}_*": "allow"}), "allow")

    def test_a_whole_server_holder_keeps_every_tool_of_that_server(self):
        for server in OPENCODE_SERVERS:
            for slug in sorted(source_holders(server)[0]):
                # no whole-server GitLab holder exists (T667): this loop runs for memory and sequential-thinking
                tools = ["any_tool"]
                for tool in tools:
                    with self.subTest(server=server, agent=slug, tool=tool):
                        self.assertEqual(self.effect(slug, f"{cleaned(server)}_{tool}"), "allow")

    def test_a_named_holder_can_call_only_its_named_tools_of_every_server(self):
        for server in OPENCODE_SERVERS:
            for slug in sorted(source_holders(server)[1]):
                prefix = cleaned(server) + "_"
                tools = parse_file(OPENCODE_AGENTS / f"{slug}.md")[0]["tools"]
                held = [k[len(prefix):] for k, v in tools.items() if v is True and k.startswith(prefix)]
                self.assertTrue(held)
                for tool in held:
                    for hostile in (None, {wildcard(server): "allow"}, {"*": "allow"}):
                        with self.subTest(server=server, agent=slug, tool=tool, user_global=hostile):
                            self.assertEqual(self.effect(slug, prefix + tool, global_extra=hostile), "allow")
                not_held = ["merge_merge_request", "push_files", "gitlab_api_request", "execute_graphql",
                            "delete_branch", "browser_evaluate", "write_file", "some_new_tool"]
                for tool in not_held:
                    if tool in held:
                        continue
                    for hostile in (None, {wildcard(server): "allow"}, {"*": "allow"}, {prefix + tool: "allow"}):
                        with self.subTest(server=server, agent=slug, not_held=tool, user_global=hostile):
                            self.assertEqual(self.effect(slug, prefix + tool, global_extra=hostile), "deny")

    def test_the_six_playwright_tools_are_denied_for_every_agent_even_after_a_user_allow(self):
        for slug in sorted(self.agents):
            for name in SIX_FALSE:
                for hostile in ({"playwright_*": "allow"}, {"*": "allow"}, {name: "allow"}):
                    with self.subTest(agent=slug, tool=name, user_global=hostile):
                        self.assertEqual(self.effect(slug, name, global_extra=hostile), "deny")

    def test_a_later_allow_in_the_same_agent_beats_the_per_agent_false_when_it_is_written_after_it(self):
        """The ordering rule the generator relies on: this is why the denies go last."""
        for defaults in DEFAULT_VARIANTS:
            rules = opencode_rules({"playwright_browser_evaluate": False, "playwright_*": True})
            self.assertEqual(opencode_effect("playwright_browser_evaluate", defaults, rules), "allow")
            rules = opencode_rules({"playwright_*": True, "playwright_browser_evaluate": False})
            self.assertEqual(opencode_effect("playwright_browser_evaluate", defaults, rules), "deny")

    def test_the_granted_playwright_tools_stay_allowed_and_the_lookalike_is_not_caught(self):
        for slug in sorted(PLAYWRIGHT_HOLDERS):
            granted = [k for k, v in parse_file(OPENCODE_AGENTS / f"{slug}.md")[0]["tools"].items()
                       if v is True and k.startswith("playwright_")]
            for name in granted:
                with self.subTest(agent=slug, tool=name):
                    self.assertEqual(self.effect(slug, name), "allow")
        self.assertEqual(self.effect("qa-engineer", f"playwright_{GRANTED_LOOKALIKE}"), "allow")
        self.assertEqual(self.effect("qa-engineer", "playwright_browser_network_request"), "deny")

    def test_sec_t657_04_a_users_global_deny_or_ask_of_a_held_tool_is_overridden_by_the_agents_allow(self):
        """Documented, unchanged: the agent's `true` is later than the global config and wins."""
        self.assertEqual(self.effect("qa-engineer", "playwright_browser_click",
                                     global_extra={"playwright_browser_click": "deny"}), "allow")
        self.assertEqual(self.effect("qa-engineer", "playwright_browser_click",
                                     global_extra={"playwright_*": "ask"}), "allow")
        # T667: no agent holds the whole server, so the GitLab example is a NAMED tool held by three agents
        for slug in ("orchestrator", "poc-orchestrator", "release-manager"):
            for user_rule in ("ask", "deny"):
                with self.subTest(agent=slug, user_rule=user_rule):
                    self.assertEqual(self.effect(slug, "gitlab_create_merge_request",
                                                 global_extra={"gitlab_create_merge_request": user_rule}), "allow")
        # ... while no agent holds the merge tool: the user's own `allow` does not reach it either
        for slug in sorted(GITLAB_HOLDERS):
            with self.subTest(agent=slug, tool="merge"):
                self.assertEqual(self.effect(slug, "gitlab_merge_merge_request",
                                             global_extra={"gitlab_merge_merge_request": "allow"}), "deny")
        # A tool the agent does not hold keeps the user's rule... except where the generator denies anyway
        self.assertEqual(self.effect("tech-lead", "playwright_browser_click",
                                     global_extra={"playwright_browser_click": "deny"}), "deny")

    def test_a_user_owned_agent_rule_written_after_the_generated_file_still_wins(self):
        """Documented residual: another config source or an agent file of the user's own comes later."""
        self.assertEqual(self.effect("tech-lead", "gitlab_merge_merge_request", agent_extra={"gitlab_*": "allow"}), "allow")

    def test_user_owned_servers_are_not_caught_by_the_wildcards(self):
        for server in ("playwright-local", "gitlab-ee", "mygitlab", "gitx"):
            with self.subTest(server=server):
                self.assertNotIn("deny", self.effects("tech-lead", f"{server}_get_issue"))
        # Documented caveat: a server whose cleaned name starts with `gitlab_` / `git_` IS caught (fail closed).
        self.assertEqual(self.effect("tech-lead", "gitlab_ee_get_issue"), "deny")
        self.assertEqual(self.effect("tech-lead", "git_hub_x"), "deny")

    def test_wildcard_model_matches_the_vendor_examples(self):
        self.assertTrue(opencode_wildcard("gitlab_merge_merge_request", "gitlab_*"))
        self.assertTrue(opencode_wildcard("gitlab_gitlab_api_request", "gitlab_*"))
        self.assertFalse(opencode_wildcard("gitlab-ee_x", "gitlab_*"))
        self.assertFalse(opencode_wildcard("gitlab", "gitlab_*"))
        self.assertFalse(opencode_wildcard("github_x", "git_*"))


class GeneratorFixtureTests(unittest.TestCase):
    """The real generator on a fixture root: servers `gl` (denyUnlessGranted) and `pw` (denyTools)."""

    SERVERS = (
        "servers:\n"
        "  gl:\n"
        "    tags: [core]\n"
        "    transport: stdio\n"
        "    command: python\n"
        "    args: [\"-m\", \"gl_server\"]\n"
        "    denyUnlessGranted: true\n"
        "  pw:\n"
        "    tags: [core]\n"
        "    transport: stdio\n"
        "    command: python\n"
        "    args: [\"-m\", \"pw_server\"]\n"
        "    denyTools: [bad_one, bad_two]\n"
        "  skip:\n"
        "    tags: [other]\n"
        "    transport: stdio\n"
        "    command: python\n"
        "    args: [\"-m\", \"skip_server\"]\n"
        "    denyTools: [skip_bad]\n"
        "    denyUnlessGranted: true\n"
    )
    AGENTS = {
        "holder": "[read, mcp__gl]",
        "named": "[read, mcp__gl__list_x]",
        "both": "[read, mcp__gl, mcp__gl__list_x]",
        "plain": "[read]",
        "pwhole": "[read, mcp__pw]",
    }

    @staticmethod
    def build(root: Path, servers_text: str, agents: dict[str, str | None], mutate_platform=None) -> None:
        (root / "platforms").mkdir()
        for path in (IMPL / "platforms").glob("*.json"):
            target = root / "platforms" / path.name
            shutil.copy(path, target)
            if mutate_platform and path.stem == "opencode":
                data = json.loads(target.read_text(encoding="utf-8"))
                mutate_platform(data)
                target.write_text(json.dumps(data, indent=2), encoding="utf-8")
        shutil.copytree(IMPL / "_extras", root / "_extras")
        (root / "knowledge" / "mcp").mkdir(parents=True)
        (root / "knowledge" / "mcp" / "servers.yaml").write_text(servers_text, encoding="utf-8")
        for kind in ("commands", "instructions", "skills"):
            (root / "knowledge" / kind).mkdir()
        (root / "knowledge" / "agents").mkdir()
        for slug, tools in agents.items():
            line = "" if tools is None else f"tools: {tools}\n"
            (root / "knowledge" / "agents" / f"{slug}.md").write_text(
                f"---\nname: \"{slug}\"\ndescription: \"fixture\"\n{line}---\n\nbody\n", encoding="utf-8")

    def run_sync(self, servers=None, agents=None, mutate_platform=None):
        if shutil.which("node") is None:
            self.skipTest("node is not installed")
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.build(root, servers or self.SERVERS, agents if agents is not None else self.AGENTS, mutate_platform)
        result = subprocess.run(["node", str(SYNC), "--root", str(root)], capture_output=True, text=True, check=False)
        return root, result

    def tools(self, root: Path, slug: str) -> list[tuple[str, str]]:
        return raw_tools_lines(root / ".opencode" / "agents" / f"{slug}.md")

    def test_output_per_agent_class(self):
        root, result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        six = [("pw_bad_one", "false"), ("pw_bad_two", "false")]
        # servers are visited in servers.yaml order (gl, pw); `skip` has a tag Opencode does not carry
        self.assertEqual(self.tools(root, "holder"), [("read", "true"), ("gl_*", "true")] + six)
        self.assertEqual(self.tools(root, "named"), [("gl_*", "false"), ("read", "true"), ("gl_list_x", "true")] + six)
        # a bare `mcp__gl` token makes the agent a whole-server holder even if named tokens are present
        self.assertEqual(self.tools(root, "both"), [("read", "true"), ("gl_*", "true"), ("gl_list_x", "true")] + six)
        self.assertEqual(self.tools(root, "plain"), [("read", "true"), ("gl_*", "false")] + six)
        self.assertEqual(self.tools(root, "pwhole"), [("read", "true"), ("pw_*", "true"), ("gl_*", "false")] + six)

    def test_an_agent_without_a_tools_line_still_receives_the_denies(self):
        root, result = self.run_sync(agents={"bare": None})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.tools(root, "bare"),
                         [("gl_*", "false"), ("pw_bad_one", "false"), ("pw_bad_two", "false")])

    def test_other_platforms_are_unchanged_by_the_flags(self):
        root, result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for rel in (".github/agents/plain.agent.md", ".pi/agents/plain.md", ".claude/agents/plain.md"):
            text = (root / rel).read_text(encoding="utf-8")
            with self.subTest(file=rel):
                self.assertNotIn("false", text)
                self.assertNotIn("gl_*", text)

    def test_the_global_denial_is_still_emitted(self):
        root, result = self.run_sync()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        permission = json.loads((root / ".opencode" / "opencode.json").read_text(encoding="utf-8"))["permission"]
        self.assertEqual(permission, {"pw_bad_one": "deny", "pw_bad_two": "deny"})

    def test_an_agent_that_grants_a_denied_exact_name_stops_the_run(self):
        for token in ("mcp__pw__bad_one", "mcp__pw__bad_two"):
            with self.subTest(token=token):
                root, result = self.run_sync(agents={"clash": f"[read, {token}]"})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("both grants and denies", result.stderr)

    def test_a_wildcard_allow_with_exact_denies_after_it_is_accepted(self):
        root, result = self.run_sync(agents={"pwhole": "[mcp__pw]"})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        names = [n for n, _ in self.tools(root, "pwhole")]
        self.assertLess(names.index("pw_*"), names.index("pw_bad_one"))

    def test_a_server_name_with_odd_characters_is_cleaned_like_opencode_does(self):
        servers = self.SERVERS.replace("  gl:", "  my.git:").replace("\n  pw:", "\n  pw:")
        root, result = self.run_sync(servers=servers, agents={"plain": "[read]", "hold": "[read, mcp__my.git]"})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(("my_git_*", "false"), self.tools(root, "plain"))
        self.assertNotIn(("my_git_*", "false"), self.tools(root, "hold"))

    def test_an_invalid_flag_stops_the_run_before_anything_is_written(self):
        for label, value in {"yes": "yes", "number": "1", "text": "gitlab"}.items():
            with self.subTest(value=label):
                root, result = self.run_sync(servers=self.SERVERS.replace("denyUnlessGranted: true\n  pw:", f"denyUnlessGranted: {value}\n  pw:"))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("denyUnlessGranted", result.stderr)
                self.assertFalse((root / ".opencode").exists())

    def test_an_invalid_manifest_opt_in_stops_the_run(self):
        cases = {
            "string": lambda d: d["frontmatter"]["agents"].__setitem__("mcpAgentDenies", "yes"),
            "no style": lambda d: d["frontmatter"]["agents"].pop("mcpToolNames"),
            "wrong style": lambda d: d["frontmatter"]["agents"].__setitem__("mcpToolNames", "slash"),
            "array tools": lambda d: d["frontmatter"]["agents"].__setitem__("tools", "array"),
        }
        for label, mutate in cases.items():
            with self.subTest(case=label):
                root, result = self.run_sync(mutate_platform=mutate)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("mcpAgentDenies", result.stderr)

    def test_a_server_with_both_the_flag_and_exact_denies_gets_wildcard_then_exacts(self):
        servers = self.SERVERS.replace("    denyTools: [bad_one, bad_two]\n", "    denyTools: [bad_one, bad_two]\n    denyUnlessGranted: true\n")
        root, result = self.run_sync(servers=servers, agents={
            "plain": "[read]", "named": "[read, mcp__pw__list_x]", "whole": "[read, mcp__pw]"})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        exact = [("pw_bad_one", "false"), ("pw_bad_two", "false")]
        self.assertEqual(self.tools(root, "plain"), [("read", "true"), ("gl_*", "false"), ("pw_*", "false")] + exact)
        self.assertEqual(self.tools(root, "named"),
                         [("pw_*", "false"), ("read", "true"), ("pw_list_x", "true"), ("gl_*", "false")] + exact)
        self.assertEqual(self.tools(root, "whole"), [("read", "true"), ("pw_*", "true"), ("gl_*", "false")] + exact)

    def test_the_flag_false_is_an_explicit_exemption_and_emits_nothing_for_that_server(self):
        servers = self.SERVERS.replace("    denyUnlessGranted: true\n  pw:", "    denyUnlessGranted: false\n  pw:", 1)
        root, result = self.run_sync(servers=servers, agents={
            "plain": "[read]", "named": "[read, mcp__gl__list_x]", "whole": "[read, mcp__gl]"})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        six = [("pw_bad_one", "false"), ("pw_bad_two", "false")]
        self.assertEqual(self.tools(root, "plain"), [("read", "true")] + six)
        self.assertEqual(self.tools(root, "named"), [("read", "true"), ("gl_list_x", "true")] + six)
        self.assertEqual(self.tools(root, "whole"), [("read", "true"), ("gl_*", "true")] + six)

    def test_a_misspelled_server_key_stops_the_run_before_anything_is_written(self):
        for bad in ("denyUnlessGrant: true", "denyTool: [x]", "denyunlessgranted: true", "description: x"):
            with self.subTest(key=bad):
                root, result = self.run_sync(servers=self.SERVERS.replace("    denyUnlessGranted: true\n", f"    {bad}\n", 1))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("unknown key", result.stderr)
                self.assertFalse((root / ".opencode").exists())

    def test_every_manifest_is_validated_before_the_first_file_is_written(self):
        root, result = self.run_sync(mutate_platform=lambda d: d["frontmatter"]["agents"].__setitem__("mcpAgentDenies", "yes"))
        self.assertNotEqual(result.returncode, 0)
        # claude-code sorts before opencode and used to be written before the bad manifest was read
        for folder in (".claude", ".github", ".gemini", ".opencode", ".pi"):
            self.assertFalse((root / folder).exists(), folder)

    def test_the_shipped_servers_yaml_passes_the_key_check(self):
        result = subprocess.run(["node", str(SYNC), "--root", str(IMPL), "--check"], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_no_flags_means_no_false_entries(self):
        servers = "servers:\n  plain:\n    tags: [core]\n    transport: stdio\n    command: python\n    args: [\"-m\", \"x\"]\n"
        root, result = self.run_sync(servers=servers)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.tools(root, "plain"), [("read", "true")])

    def test_regeneration_is_deterministic(self):
        first, r1 = self.run_sync()
        second, r2 = self.run_sync()
        self.assertEqual((r1.returncode, r2.returncode), (0, 0))
        for slug in self.AGENTS:
            self.assertEqual((first / ".opencode" / "agents" / f"{slug}.md").read_bytes(),
                             (second / ".opencode" / "agents" / f"{slug}.md").read_bytes(), slug)


@unittest.skipUnless(shutil.which("bash"), "bash is not installed")
class InstallReplacesAgentFilesWholesaleTests(unittest.TestCase):
    """`install.sh` does not merge agent files: a user edit is replaced by the generated file, so the
    per-agent denies come back with every --update (only the MCP config file is merged)."""

    def install(self, target: Path, update: bool = False):
        args = ["bash", str(INSTALLER), "--target", str(target), "--platform", "opencode"]
        if update:
            args.append("--update")
        return subprocess.run(args, cwd=REPO, capture_output=True, text=True, check=False)

    def test_fresh_install_ships_the_denies_and_update_restores_an_edited_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            first = self.install(target)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            agent = target / ".opencode" / "agents" / "tech-lead.md"
            shipped = (OPENCODE_AGENTS / "tech-lead.md").read_bytes()
            self.assertEqual(agent.read_bytes(), shipped)
            # the user removes the denies and adds an allow of a denied tool, then updates
            edited = agent.read_text(encoding="utf-8").replace("  gitlab_*: false\n", "").replace(
                "  playwright_browser_evaluate: false\n", "  playwright_browser_evaluate: true\n")
            agent.write_text(edited, encoding="utf-8")
            extra = target / ".opencode" / "agents" / "my-own-agent.md"
            extra.write_text("---\nname: \"mine\"\ndescription: \"x\"\ntools:\n  read: true\n---\nbody\n", encoding="utf-8")
            second = self.install(target, update=True)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(agent.read_bytes(), shipped, "the agent file is replaced wholesale, not merged")
            self.assertFalse(extra.exists(), "agents/ is replaced as a tree (rsync --delete): an own agent file is removed")

    def test_the_mcp_config_merge_is_unchanged_by_the_per_agent_denies(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self.assertEqual(self.install(target).returncode, 0)
            cfg_path = target / ".opencode" / "opencode.json"
            self.assertEqual(cfg_path.read_bytes(), (IMPL / ".opencode" / "opencode.json").read_bytes())
            before = cfg_path.read_bytes()
            self.assertEqual(self.install(target, update=True).returncode, 0)
            self.assertEqual(cfg_path.read_bytes(), before)


EVIDENCE = REPO / "docs" / "artifacts" / "mcp-agent-denials-evidence-v1.md"
EVIDENCE_DIR = REPO / "docs" / "artifacts" / "mcp-agent-denials-evidence-v1"


def lines_with(text: str, *needles: str) -> list[str]:
    return [line for line in text.splitlines() if all(n in line for n in needles)]


class DocumentationTests(unittest.TestCase):
    DOCS = {
        "wiki": REPO / "docs" / "wiki" / "mcp-servers.md",
        "prerequisites": IMPL / "PREREQUISITES.md",
        "agents-root": REPO / "AGENTS.md",
        "agents-impl": IMPL / "AGENTS.md",
    }

    @classmethod
    def setUpClass(cls):
        cls.artifact = ARTIFACT.read_text(encoding="utf-8")

    def test_artifact_header_and_status_rows(self):
        self.assertIn("Based on: mcp-server-denials-v1.md", self.artifact)
        for needle in ("T663", "verified", "unverified", "not observed", "denyUnlessGranted", "wholesale",
                       "tools: { x: false }", "last matching rule", "SEC-T657-04", "SEC-T658-01"):
            self.assertIn(needle, self.artifact, needle)
        for source in ("https://opencode.ai/docs/agents", "https://opencode.ai/docs/mcp-servers",
                       "packages/core/src/permission.ts", "packages/core/src/v1/config/agent.ts",
                       "packages/core/src/util/wildcard.ts", "/websites/opencode_ai"):
            self.assertIn(source, self.artifact, source)

    def test_artifact_wording_after_the_review(self):
        # SEC-T663-04: the over-claim is gone; SEC-T663-02: row 1 states what is and is not documented
        self.assertNotIn("Nothing unverified is shipped", self.artifact)
        self.assertIn("deprecated", self.artifact)
        row = lines_with(self.artifact, "| 1 |", "tools: { x: false }")
        self.assertEqual(len(row), 1)
        self.assertIn("verified from source and resolver", row[0])
        self.assertIn("do not state key order", row[0])
        self.assertRegex(self.artifact.lower(), r"tracked debt: `tools:` is the deprecated form")
        self.assertIn("`permission:` block", self.artifact)

    def test_artifact_names_the_residuals(self):
        lower = self.artifact.lower()
        for needle in ("qa-engineer", "scrum-master", "gitlab_*", "user-owned agent file",
                       "named-subset rule", "opencode debug agent", "built-in agents", "hindsight",
                       "tracked debt", "every server"):
            self.assertIn(needle, lower, needle)

    def test_artifact_section_7_no_longer_lists_a_subset_of_servers_as_open(self):
        section = self.artifact.split("## 7.", 1)[1].split("## 8.", 1)[0]
        self.assertNotIn("memory", section)
        self.assertIn("closed by section 3a", section)

    def test_every_doc_states_the_per_agent_denial_and_that_it_is_not_observed_live(self):
        for label, path in self.DOCS.items():
            text = path.read_text(encoding="utf-8")
            # anchored to the T663 paragraph: a line that names both T663 and per-agent
            anchored = lines_with(text, "T663", "per-agent")
            with self.subTest(doc=label):
                self.assertTrue(anchored, "no T663 per-agent paragraph")
                self.assertTrue(any(("not observed" in l or "has not been observed" in l)
                                    and "mcp-agent-denials-v1.md" in l for l in anchored), anchored[0][:120])

    def test_wiki_documents_every_server_wildcard_and_the_named_subset_rule(self):
        text = self.DOCS["wiki"].read_text(encoding="utf-8")
        self.assertIn("denyUnlessGranted", text)
        self.assertIn("Named-subset rule", text)
        self.assertIn("**Servers that no agent holds and that are not exempt**", text)
        self.assertNotIn("stay open there (tracked debt)", text)
        self.assertNotIn("qa-engineer and scrum-master still have a gap", text)

    def test_no_doc_says_the_named_holders_can_still_call_other_gitlab_tools_on_opencode(self):
        for label, path in self.DOCS.items():
            with self.subTest(doc=label):
                self.assertNotRegex(path.read_text(encoding="utf-8"),
                                    r"qa-engineer and scrum-master can still call the GitLab tools they do not hold")

    def test_wiki_no_longer_says_the_generator_does_not_write_a_per_agent_false(self):
        text = self.DOCS["wiki"].read_text(encoding="utf-8")
        self.assertNotIn("the generator does not write it because no shipped agent re-allows these tools", text)

    def test_sec_t657_04_sentence_with_the_gitlab_merge_example_is_in_every_doc(self):
        """SEC-T663-03: both AGENTS.md files (and the wiki and PREREQUISITES) state the override with the
        merge example and say whether a way to keep a prompt exists."""
        for label, path in self.DOCS.items():
            text = path.read_text(encoding="utf-8")
            hits = lines_with(text, "gitlab_merge_merge_request", "silently overridden")
            with self.subTest(doc=label):
                self.assertTrue(hits)
                line = hits[0]
                for needle in ("no agent holds the whole `gitlab` server", "`gitlab_create_merge_request`",
                               "No supported way", "OPENCODE_CONFIG_CONTENT"):
                    self.assertIn(needle, line)
                self.assertNotIn("whole-server GitLab holders", line)

    def test_sec_t663_04_sentences_are_in_every_doc(self):
        for label, path in self.DOCS.items():
            text = path.read_text(encoding="utf-8")
            with self.subTest(doc=label):
                self.assertRegex(text, r"`gitlab_ee`[^\n]{0,200}`gitlab_\*`")  # (a) over-match
                self.assertRegex(text, r"(?i)saved \"always\" approvals[^\n]{0,300}`denied\(\)`")  # (b)
                self.assertRegex(text, r"(?i)built-in agents \(build, plan, general, explore")  # (c)

    def test_used_by_rows_do_not_claim_agents_that_hold_no_token(self):
        for label in ("wiki", "agents-root", "agents-impl"):
            text = self.DOCS[label].read_text(encoding="utf-8")
            with self.subTest(doc=label):
                for server in ("brave", "context7", "hindsight"):
                    rows = [l for l in text.splitlines() if l.startswith(f"| `{server}` |")]
                    self.assertEqual(len(rows), 1, server)
                    self.assertIn("No agent lists its tools", rows[0])

    def test_user_decisions_are_recorded_verbatim_and_documented_everywhere(self):
        self.assertIn('"Exempt the read/search servers (Recommended)"', self.artifact)
        self.assertIn('"No, document the gap only (Recommended)"', self.artifact)
        for label, path in self.DOCS.items():
            text = path.read_text(encoding="utf-8")
            with self.subTest(doc=label):
                self.assertIn("denyUnlessGranted: false", text)
                for server in EXEMPT_SERVERS:
                    self.assertIn(server, text)
                self.assertIn("2026-10-16", text)
                self.assertRegex(text, r"(?s)built-in agents \(build, plan, general, explore[^\n]{0,600}decision of the user")

    def test_evidence_artifact_and_raw_files(self):
        import hashlib
        text = EVIDENCE.read_text(encoding="utf-8")
        self.assertIn("Based on: mcp-agent-denials-v1.md", text)
        for needle in ("opencode-ai@1.19.2", "opencode debug agent", "hostile global", "OPENCODE_CONFIG_CONTENT",
                       "No tool call was made"):
            self.assertIn(needle, text, needle)
        raws = sorted(EVIDENCE_DIR.glob("raw-*.json"))
        self.assertGreaterEqual(len(raws), 6)
        for raw in raws:
            digest = hashlib.sha256(raw.read_bytes()).hexdigest()
            with self.subTest(raw=raw.name):
                self.assertIn(digest, text, "the recorded sha256 must match the stored raw file")
                self.assertEqual(json.loads(raw.read_text(encoding="utf-8"))["name"] in
                                 {"Tech Lead", "QA Engineer", "Demo Agent", "Orchestrator"}, True)
        # the stored raw output of the required agents shows the generated rule order (rules 0-11 defaults,
        # 12-22 global config, 23 onwards the agent's own rules)
        def own(slug):
            rules = json.loads((EVIDENCE_DIR / f"raw-{slug}.json").read_text(encoding="utf-8"))["permission"]
            return [(r["permission"], r["action"]) for r in rules[23:]]

        self.assertEqual(own("qa-engineer")[:2], [("gitlab_*", "deny"), ("playwright_*", "deny")])
        self.assertEqual(own("demo-agent")[0], ("playwright_*", "deny"))
        self.assertIn(("gitlab_*", "deny"), own("tech-lead"))
        self.assertEqual(own("tech-lead")[0], ("read", "allow"))
        self.assertLess(own("qa-engineer").index(("gitlab_get_issue", "allow")), own("qa-engineer").index(("playwright_browser_evaluate", "deny")))


if __name__ == "__main__":
    unittest.main()
