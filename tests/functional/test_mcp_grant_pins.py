"""T673 (SEC-T657-07, SEC-T660-06) -- pin every MCP grant that is not a Playwright grant, and the counts the docs state.

`test_mcp_package_pins.py` pins the Playwright grants (`PlaywrightGrantSetTests`) and the named GitLab sets
(`GitLabGrantSetTests`). This file adds what was left open:

- the grants of every other server (`memory`, `sequential-thinking`, `security-audit`, `poc-security-audit`,
  `context-retriever`), exactly, per agent, and that each named tool exists on the server that registers it;
- the roles that the security guidelines call read-only hold no MCP tool that writes, and the set of agents that
  can write through MCP at all is pinned, so a write tool added to one more agent fails here;
- the GitLab registry snapshot (275 names of `@zereight/mcp-gitlab@2.2.5`) classified by verb: every granted
  mutating tool is a pinned write, and the forbidden-name pattern covers every other mutating tool;
- the counts and name lists that the four documents state, read from the sentence that states them and compared
  with the agent sources.

Every check is a function of its input; `*MutationTests` break the property on an in-memory copy and require the
function to notice. Static inspection of sources and documents; no network, no subprocess.
"""
from __future__ import annotations

import ast
import json
import re
import unittest

import yaml

from tests._helpers.frontmatter import parse_file
from tests._helpers.repo import implementation_root, knowledge_root, repo_root
# Constants and the pinned sets only; no test class is imported, so nothing is collected twice.
from tests.functional.test_mcp_package_pins import (
    EXPECTED_GITLAB_GRANTS,
    EXPECTED_PLAYWRIGHT_GRANTS,
    GITLAB_EXPECTED_WRITES,
    GITLAB_FORBIDDEN_NAME,
    PLAYWRIGHT_0_0_83_DEFAULT_TOOLS,
    PLAYWRIGHT_EXCLUDED,
)

REPO = repo_root()
IMPL = implementation_root()
AGENTS_DIR = knowledge_root() / "agents"
SERVERS_YAML = knowledge_root() / "mcp" / "servers.yaml"
SNAPSHOT = REPO / "tests" / "_baselines" / "gitlab-mcp-tool-names.json"
DOCS = {
    "wiki": REPO / "docs" / "wiki" / "mcp-servers.md",
    "prerequisites": IMPL / "PREREQUISITES.md",
    "agents-root": REPO / "AGENTS.md",
    "agents-impl": IMPL / "AGENTS.md",
}
GITLAB_PARAGRAPH_DOCS = ("wiki", "agents-root", "agents-impl")

# --- SEC-T657-07: the grants of the servers that are neither GitLab nor Playwright, pinned per agent ----------------
SECURITY_AUDIT = {f"mcp__security-audit__{t}" for t in
                  ("run_npm_audit", "run_pip_audit", "run_dotnet_list_vulnerable", "grep_content")}
POC_SECURITY_AUDIT = {f"mcp__poc-security-audit__{t}" for t in ("scan_secrets", "ref_containment")}
EXPECTED_OTHER_MCP_GRANTS = {
    # team memory and decomposition: the two orchestrators hold the whole `memory` and `sequential-thinking` servers
    "orchestrator": {"mcp__memory", "mcp__sequential-thinking"},
    "poc-orchestrator": {"mcp__memory", "mcp__sequential-thinking"},
    "solution-architect": {"mcp__sequential-thinking"},
    "security-engineer": set(SECURITY_AUDIT),
    "poc-security-engineer": {"mcp__security-audit__grep_content"} | POC_SECURITY_AUDIT,
    "context-retriever": {"mcp__context-retriever__retrieve"},
}
# The tool each fixed-command server registers, read from its source with `ast` (no import, nothing is run).
SERVER_SOURCES = {
    "security-audit": IMPL / "runtime" / "security" / "audit_server.py",
    "poc-security-audit": IMPL / "runtime" / "security" / "poc_audit_server.py",
    "context-retriever": IMPL / "runtime" / "memory" / "context_retriever_mcp_server" / "server.py",
}
# Roles that hold no write MCP tool: the read-only roles of security-guidelines.md (Tech Lead, Security Engineer,
# Product Owner), the PoC security engineer, and the retriever (its server states that it exposes no write tool).
READ_ONLY_ROLES = {"tech-lead", "security-engineer", "poc-security-engineer", "product-owner", "context-retriever"}
# The only MCP tools a read-only role may hold: the fixed-command audit tools (a fixed argv per tool, no
# free-form command, no write) and the single retrieval tool.
READ_ONLY_MCP_ALLOWLIST = SECURITY_AUDIT | POC_SECURITY_AUDIT | {"mcp__context-retriever__retrieve"}
# Who can write through MCP at all (a GitLab write, the memory server, or an interactive Playwright tool).
WRITE_CAPABLE_AGENTS = {
    "qa-engineer", "scrum-master", "orchestrator", "poc-orchestrator", "release-manager",  # GitLab writes, memory
    "frontend-developer", "poc-qa-engineer", "demo-agent",                                  # page interaction
}
# Whole servers with no persistent side effect; every other whole-server grant is treated as a write grant.
NO_EFFECT_SERVERS = {"sequential-thinking"}
PLAYWRIGHT_INTERACTIVE = {"browser_click", "browser_type", "browser_fill_form", "browser_press_key",
                          "browser_select_option", "browser_handle_dialog"}

# --- SEC-T660-06: the registry snapshot classified by verb -------------------------------------------------------
READ_VERBS = {"get", "list", "search", "whoami", "my", "health", "verify", "validate", "wait", "orbit", "discover", "mr"}
MUTATING_VERBS = {
    "approve", "bulk", "cancel", "confirm", "convert", "create", "delete", "dismiss", "download", "edit", "erase",
    "execute", "fork", "gitlab", "mark", "merge", "move", "play", "promote", "protect", "publish", "purge", "push",
    "resolve", "retry", "stop", "take", "trigger", "unapprove", "unprotect", "update", "upload",
}


def agent_tokens(agents_dir=AGENTS_DIR) -> dict[str, list[str]]:
    return {p.stem: list(parse_file(p)[0].get("tools") or []) for p in sorted(agents_dir.glob("*.md"))}


def other_mcp_grants(tokens: dict[str, list[str]]) -> dict[str, set[str]]:
    return {slug: {t for t in toks if t.startswith("mcp__") and not t.startswith(("mcp__gitlab", "mcp__playwright"))}
            for slug, toks in tokens.items()}


def verb(tool: str) -> str:
    return tool.split("_", 1)[0]


def is_mutating_gitlab_tool(tool: str) -> bool:
    return verb(tool) not in READ_VERBS  # an unclassified verb is treated as mutating: fail closed


def write_mcp_tokens(toks: list[str]) -> list[str]:
    """The tokens of one agent that can write through MCP: any whole-server grant but the no-effect ones, a mutating
    GitLab tool, an interactive Playwright tool, or any server this function does not know (fail closed)."""
    out = []
    for token in toks:
        if not token.startswith("mcp__"):
            continue
        server, _, tool = token[len("mcp__"):].partition("__")
        if tool in ("", "*"):
            if server not in NO_EFFECT_SERVERS:
                out.append(token)
        elif server == "gitlab":
            if is_mutating_gitlab_tool(tool):
                out.append(token)
        elif server == "playwright":
            if tool in PLAYWRIGHT_INTERACTIVE or tool in PLAYWRIGHT_EXCLUDED:
                out.append(token)
        elif token not in READ_ONLY_MCP_ALLOWLIST:
            out.append(token)
    return out


def registered_tools(path) -> set[str]:
    """Names of the functions decorated `@<x>.tool(...)` in a server module (the tool name is the function name)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for deco in node.decorator_list:
                call = deco.func if isinstance(deco, ast.Call) else deco
                if isinstance(call, ast.Attribute) and call.attr == "tool":
                    names.add(node.name)
    return names


def other_grant_findings(tokens: dict[str, list[str]]) -> list[str]:
    grants = other_mcp_grants(tokens)
    found = [f"{slug} holds {sorted(held)}, expected {sorted(EXPECTED_OTHER_MCP_GRANTS.get(slug, set()))}"
             for slug, held in grants.items() if held != EXPECTED_OTHER_MCP_GRANTS.get(slug, set())]
    found += [f"{slug} is pinned but has no agent source" for slug in EXPECTED_OTHER_MCP_GRANTS if slug not in tokens]
    return found


def read_only_findings(tokens: dict[str, list[str]]) -> list[str]:
    found = []
    for slug in sorted(READ_ONLY_ROLES):
        if slug not in tokens:
            found.append(f"{slug} has no agent source")
            continue
        writes = write_mcp_tokens(tokens[slug])
        extra = [t for t in tokens[slug] if t.startswith("mcp__") and t not in READ_ONLY_MCP_ALLOWLIST]
        if writes or extra:
            found.append(f"{slug} holds {sorted(set(writes) | set(extra))}")
    return found


class OtherServerGrantTests(unittest.TestCase):
    def setUp(self):
        self.tokens = agent_tokens()

    def test_every_agent_holds_exactly_its_pinned_non_playwright_non_gitlab_grants(self):
        self.assertGreaterEqual(len(self.tokens), 28, "an empty glob must not pass")
        self.assertEqual(other_grant_findings(self.tokens), [])

    def test_every_pinned_server_is_a_server_of_servers_yaml_and_every_named_tool_is_registered_by_it(self):
        servers = yaml.safe_load(SERVERS_YAML.read_text(encoding="utf-8"))["servers"]
        named = {}
        for slug, held in EXPECTED_OTHER_MCP_GRANTS.items():
            for token in held:
                server, _, tool = token[len("mcp__"):].partition("__")
                self.assertIn(server, servers, f"{slug}: {token}")
                if tool:
                    named.setdefault(server, set()).add(tool)
        self.assertEqual(set(named), set(SERVER_SOURCES))
        for server, tools in named.items():
            with self.subTest(server=server):
                registered = registered_tools(SERVER_SOURCES[server])
                self.assertTrue(registered, "the server module registers at least one tool")
                self.assertEqual(tools - registered, set(), "a granted name the server does not register grants nothing")

    def test_the_fixed_command_servers_register_exactly_the_tools_that_are_granted(self):
        # security-audit: four tools (the module and servers.yaml say so); poc-security-audit: two; retriever: one
        self.assertEqual(registered_tools(SERVER_SOURCES["security-audit"]), {t.rsplit("__", 1)[1] for t in SECURITY_AUDIT})
        self.assertEqual(registered_tools(SERVER_SOURCES["poc-security-audit"]), {t.rsplit("__", 1)[1] for t in POC_SECURITY_AUDIT})
        self.assertEqual(registered_tools(SERVER_SOURCES["context-retriever"]), {"retrieve"})

    def test_whole_server_memory_is_held_by_the_two_orchestrators_only(self):
        holders = {slug for slug, toks in self.tokens.items() if "mcp__memory" in toks or "mcp__memory__*" in toks}
        self.assertEqual(holders, {"orchestrator", "poc-orchestrator"})
        for slug, toks in self.tokens.items():
            self.assertFalse([t for t in toks if t.startswith("mcp__memory__")], f"{slug}: no named memory tool is granted")


class ReadOnlyRoleTests(unittest.TestCase):
    def setUp(self):
        self.tokens = agent_tokens()

    def test_read_only_roles_hold_no_write_mcp_tool_and_only_allowlisted_tools(self):
        self.assertEqual(read_only_findings(self.tokens), [])

    def test_the_allowlisted_tools_are_not_classified_as_writes(self):
        self.assertEqual(write_mcp_tokens(sorted(READ_ONLY_MCP_ALLOWLIST)), [])

    def test_exactly_the_pinned_agents_can_write_through_mcp(self):
        writers = {slug for slug, toks in self.tokens.items() if write_mcp_tokens(toks)}
        self.assertEqual(writers, WRITE_CAPABLE_AGENTS)
        self.assertEqual(READ_ONLY_ROLES & WRITE_CAPABLE_AGENTS, set())

    def test_the_classifier_sees_the_write_tools_it_exists_to_find(self):
        self.assertEqual(write_mcp_tokens(["mcp__memory"]), ["mcp__memory"])
        self.assertEqual(write_mcp_tokens(["mcp__gitlab__create_issue"]), ["mcp__gitlab__create_issue"])
        self.assertEqual(write_mcp_tokens(["mcp__gitlab__merge_merge_request"]), ["mcp__gitlab__merge_merge_request"])
        self.assertEqual(write_mcp_tokens(["mcp__gitlab__get_issue", "mcp__gitlab__validate_ci_lint"]), [])
        self.assertEqual(write_mcp_tokens(["mcp__playwright__browser_click"]), ["mcp__playwright__browser_click"])
        self.assertEqual(write_mcp_tokens(["mcp__playwright__browser_snapshot"]), [])
        self.assertEqual(write_mcp_tokens(["mcp__unknown__thing"]), ["mcp__unknown__thing"])
        self.assertEqual(write_mcp_tokens(["mcp__sequential-thinking", "read", "edit"]), [])


class GrantMutationTests(unittest.TestCase):
    """Break the grants on an in-memory copy of the agent sources; the functions must notice."""

    def setUp(self):
        self.tokens = agent_tokens()
        self.assertEqual(other_grant_findings(self.tokens), [])
        self.assertEqual(read_only_findings(self.tokens), [])

    def mutated(self, slug: str, *add: str, remove: tuple[str, ...] = (), **kw) -> dict[str, list[str]]:
        add = tuple(add) + tuple(kw.get("add", ()))
        copy = {k: list(v) for k, v in self.tokens.items()}
        copy[slug] = [t for t in copy[slug] if t not in remove] + list(add)
        return copy

    def test_a_new_non_playwright_grant_on_any_agent_is_noticed(self):
        for slug in ("backend-developer", "tech-lead", "qa-engineer", "orchestrator"):
            with self.subTest(agent=slug):
                self.assertTrue(other_grant_findings(self.mutated(slug, "mcp__filesystem")))

    def test_a_dropped_or_narrowed_grant_is_noticed(self):
        self.assertTrue(other_grant_findings(self.mutated("orchestrator", remove=("mcp__memory",))))
        self.assertTrue(other_grant_findings(self.mutated("security-engineer", remove=("mcp__security-audit__run_npm_audit",))))
        widened = self.mutated("security-engineer", remove=("mcp__security-audit__run_pip_audit",), add=("mcp__security-audit",))
        self.assertTrue(other_grant_findings(widened))

    def test_a_write_tool_on_a_read_only_role_is_noticed(self):
        for slug in sorted(READ_ONLY_ROLES):
            for add in ("mcp__memory", "mcp__gitlab__create_issue", "mcp__gitlab__get_issue", "mcp__playwright__browser_click",
                        "mcp__security-audit"):
                with self.subTest(agent=slug, added=add):
                    self.assertTrue(read_only_findings(self.mutated(slug, add)))

    def test_a_write_tool_on_another_agent_changes_the_pinned_writer_set(self):
        for slug, add in (("devops-engineer", "mcp__gitlab__create_pipeline"), ("tech-lead", "mcp__memory"),
                          ("security-engineer", "mcp__gitlab__create_issue_note"), ("backend-developer", "mcp__gitlab__update_issue")):
            copy = self.mutated(slug, add)
            writers = {s for s, toks in copy.items() if write_mcp_tokens(toks)}
            with self.subTest(agent=slug):
                self.assertNotEqual(writers, WRITE_CAPABLE_AGENTS)


class GitLabRegistryClassificationTests(unittest.TestCase):
    """SEC-T660-06: the verb classes of the 275-name snapshot, not a hand-picked sample, decide what is a write."""

    def setUp(self):
        self.names = json.loads(SNAPSHOT.read_text(encoding="utf-8"))["tools"]
        self.allowed_writes = set().union(*GITLAB_EXPECTED_WRITES.values())

    def test_every_verb_of_the_registry_is_classified_read_or_mutating(self):
        verbs = {verb(n) for n in self.names}
        self.assertEqual(verbs - READ_VERBS - MUTATING_VERBS, set(), "a pin bump that adds a verb must classify it")
        self.assertEqual(READ_VERBS & MUTATING_VERBS, set())
        self.assertEqual((READ_VERBS | MUTATING_VERBS) - verbs, set(), "no stale verb in the classification")

    def test_the_mutating_tools_that_are_granted_are_exactly_the_pinned_writes(self):
        granted = set()
        for slug, toks in agent_tokens().items():
            granted |= {t[len("mcp__gitlab__"):] for t in toks if t.startswith("mcp__gitlab__")}
        self.assertEqual({n for n in granted if is_mutating_gitlab_tool(n)}, self.allowed_writes)
        self.assertEqual(granted - set(self.names), set())

    def test_the_forbidden_pattern_covers_every_mutating_tool_except_the_pinned_writes(self):
        uncovered = {n for n in self.names if is_mutating_gitlab_tool(n) and not GITLAB_FORBIDDEN_NAME.search(n)}
        self.assertEqual(uncovered, self.allowed_writes)

    def test_the_forbidden_pattern_matches_no_granted_name(self):
        for slug, names in EXPECTED_GITLAB_GRANTS.items():
            with self.subTest(agent=slug):
                self.assertEqual({n for n in names if GITLAB_FORBIDDEN_NAME.search(n)}, set())

    def test_the_classification_catches_a_new_mutating_tool_that_the_pattern_misses(self):
        extra = self.names + ["rotate_project_token", "archive_project"]
        self.assertEqual(
            {n for n in extra if is_mutating_gitlab_tool(n) and not GITLAB_FORBIDDEN_NAME.search(n)},
            self.allowed_writes | {"rotate_project_token", "archive_project"})
        self.assertEqual({verb(n) for n in extra} - READ_VERBS - MUTATING_VERBS, {"rotate", "archive"})


# --- documented counts and name lists, read from the sentence that states them ---------------------------------------
NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def number(word: str) -> int:
    return NUMBER_WORDS[word.lower()] if word.lower() in NUMBER_WORDS else int(word)


def gitlab_paragraph(text: str) -> str | None:
    lines = [l for l in text.splitlines() if l.startswith(("GitLab grants:", "**GitLab grants.**"))]
    return lines[0] if len(lines) == 1 else None


def role_counts(paragraph: str) -> dict[str, int]:
    """`<role> (<n> tools` pairs; the look-behind keeps `orchestrator` from matching inside `poc-orchestrator`."""
    return {m.group(1): int(m.group(2)) for m in re.finditer(r"(?<![\w-])([a-z]+(?:-[a-z]+)*) \((\d+) tools", paragraph)}


def actual_gitlab_counts(tokens: dict[str, list[str]]) -> dict[str, int]:
    counts = {slug: len([t for t in toks if t.startswith("mcp__gitlab__")]) for slug, toks in tokens.items()}
    return {slug: n for slug, n in counts.items() if n}


def holders_of(tokens: dict[str, list[str]], tool: str) -> set[str]:
    return {slug for slug, toks in tokens.items() if f"mcp__gitlab__{tool}" in toks}


def gitlab_count_findings(label: str, text: str, tokens: dict[str, list[str]], registry_size: int) -> list[str]:
    paragraph = gitlab_paragraph(text)
    if paragraph is None:
        return [f"{label}: the GitLab grants paragraph is missing or not unique"]
    found = []
    if role_counts(paragraph) != actual_gitlab_counts(tokens):
        found.append(f"{label}: per-role counts {role_counts(paragraph)} differ from {actual_gitlab_counts(tokens)}")
    m = re.search(r"registers (\d+) tools", paragraph)
    if not m or int(m.group(1)) != registry_size:
        found.append(f"{label}: the registry size is not {registry_size}")
    m = re.search(r"(\w+) of the seven roles hold `execute`", paragraph)
    execute = len([s for s in actual_gitlab_counts(tokens) if "execute" in tokens[s]])
    if not m or number(m.group(1)) != execute:
        found.append(f"{label}: the number of roles that hold `execute` is not {execute}")
    if not re.search(r"\bseven agents hold named tools only\b", paragraph) or len(actual_gitlab_counts(tokens)) != 7:
        found.append(f"{label}: 'seven agents hold named tools only' does not match {len(actual_gitlab_counts(tokens))} holders")
    return found


def merge_request_holder_findings(label: str, text: str, tokens: dict[str, list[str]]) -> list[str]:
    """`the three agents that hold it (orchestrator, poc-orchestrator, release-manager)` in the override sentence."""
    holders = holders_of(tokens, "create_merge_request")
    matches = list(re.finditer(r"the (\w+) agents that hold it \(([^)]*)\)", text))
    if not matches:
        return [f"{label}: the sentence about the holders of gitlab_create_merge_request is missing"]
    found = []
    for m in matches:
        named = set(re.findall(r"[a-z]+(?:-[a-z]+)*", m.group(2)))
        if number(m.group(1)) != len(holders) or named != holders:
            found.append(f"{label}: '{m.group(0)}' differs from {sorted(holders)}")
    return found


def seven_holder_list_findings(label: str, text: str, tokens: dict[str, list[str]]) -> list[str]:
    holders = set(actual_gitlab_counts(tokens))
    matches = list(re.finditer(r"seven GitLab holders[^:(]*[:(]([^;)]*)[;)]", text))
    if not matches:
        return [f"{label}: no list of the seven GitLab holders"]
    found = []
    for m in matches:
        named = set(re.findall(r"[a-z]+(?:-[a-z]+)*", m.group(1))) & set(tokens)  # agent slugs only
        if named != holders:
            found.append(f"{label}: the list of seven holders names {sorted(named)}, the sources hold {sorted(holders)}")
    return found


class DocumentedGitLabCountTests(unittest.TestCase):
    def setUp(self):
        self.tokens = agent_tokens()
        self.registry = len(json.loads(SNAPSHOT.read_text(encoding="utf-8"))["tools"])

    def text(self, key: str) -> str:
        return DOCS[key].read_text(encoding="utf-8")

    def test_the_counts_in_the_grants_paragraph_equal_the_agent_sources(self):
        for key in GITLAB_PARAGRAPH_DOCS:
            with self.subTest(doc=key):
                self.assertEqual(gitlab_count_findings(key, self.text(key), self.tokens, self.registry), [])

    def test_the_three_agents_that_hold_create_merge_request_are_the_ones_the_docs_name(self):
        for key in DOCS:
            with self.subTest(doc=key):
                self.assertEqual(merge_request_holder_findings(key, self.text(key), self.tokens), [])

    def test_the_lists_of_seven_holders_name_the_holders_in_the_sources(self):
        for key in DOCS:
            with self.subTest(doc=key):
                self.assertEqual(seven_holder_list_findings(key, self.text(key), self.tokens), [])


class DocumentedGitLabCountMutationTests(unittest.TestCase):
    def setUp(self):
        self.tokens = agent_tokens()
        self.registry = len(json.loads(SNAPSHOT.read_text(encoding="utf-8"))["tools"])

    def text(self, key: str) -> str:
        return DOCS[key].read_text(encoding="utf-8")

    def test_a_changed_role_count_is_noticed_even_when_another_role_has_the_same_number(self):
        for key in GITLAB_PARAGRAPH_DOCS:
            text = self.text(key)
            with self.subTest(doc=key):
                for old, new in (("scrum-master (24 tools", "scrum-master (23 tools"),
                                 ("poc-devops-engineer (6 tools", "poc-devops-engineer (7 tools"),
                                 ("registers 275 tools", "registers 274 tools"),
                                 ("Six of the seven roles hold `execute`", "Five of the seven roles hold `execute`"),
                                 ("seven agents hold named tools only", "eight agents hold named tools only")):
                    self.assertIn(old, text)
                    self.assertTrue(gitlab_count_findings(key, text.replace(old, new, 1), self.tokens, self.registry), new)

    def test_a_role_that_is_dropped_from_the_sentence_is_noticed(self):
        # `orchestrator (16 tools` removed: the old regex `orchestrator \((\d+) tools` would have matched inside
        # `poc-orchestrator (8 tools` and reported a mismatch only because the numbers differ
        text = self.text("wiki")
        mutated = text.replace("orchestrator (16 tools", "orchestrator (8 tools", 1)
        self.assertTrue(gitlab_count_findings("wiki", mutated, self.tokens, self.registry))
        dropped = text.replace(", orchestrator (16 tools", ", ", 1)
        self.assertNotEqual(dropped, text)
        self.assertTrue(gitlab_count_findings("wiki", dropped, self.tokens, self.registry))

    def test_a_changed_holder_list_is_noticed(self):
        for key in DOCS:
            text = self.text(key)
            with self.subTest(doc=key):
                self.assertTrue(merge_request_holder_findings(
                    key, text.replace("the three agents that hold it", "the four agents that hold it"), self.tokens))
                self.assertTrue(merge_request_holder_findings(
                    key, text.replace("(orchestrator, poc-orchestrator, release-manager)",
                                      "(orchestrator, poc-orchestrator, devops-engineer)"), self.tokens))
                changed = re.sub(r"(seven GitLab holders[^:(]*[:(][^;)]*?)qa-engineer", r"\1qa-lead", text, count=1)
                self.assertNotEqual(changed, text)
                self.assertTrue(seven_holder_list_findings(key, changed, self.tokens))

    def test_a_source_that_gains_or_loses_a_gitlab_tool_or_execute_is_noticed(self):
        text = self.text("wiki")
        more = {k: list(v) for k, v in self.tokens.items()}
        more["qa-engineer"].append("mcp__gitlab__list_branches")
        self.assertTrue(gitlab_count_findings("wiki", text, more, self.registry))
        less = {k: [t for t in v if t != "execute"] for k, v in self.tokens.items()}
        self.assertTrue(gitlab_count_findings("wiki", text, less, self.registry))
        new_holder = {k: list(v) for k, v in self.tokens.items()}
        new_holder["tech-lead"].append("mcp__gitlab__get_issue")
        self.assertTrue(gitlab_count_findings("wiki", text, new_holder, self.registry))
        self.assertTrue(seven_holder_list_findings("wiki", text, new_holder))


# --- the Playwright and Opencode counts of the wiki, read from the sentence that states them --------------------------
def playwright_count_findings(text: str) -> list[str]:
    sizes = [len(g) for g in EXPECTED_PLAYWRIGHT_GRANTS.values()]
    found = []
    m = re.search(r"\((\d+) of the (\d+) default tools exist outside the denial list; the four agents hold between "
                  r"(\d+) and (\d+) of them\)", text)
    if not m:
        return ["the wiki sentence about the default Playwright tools is missing"]
    want = (len(PLAYWRIGHT_0_0_83_DEFAULT_TOOLS) - len(PLAYWRIGHT_EXCLUDED), len(PLAYWRIGHT_0_0_83_DEFAULT_TOOLS), min(sizes), max(sizes))
    if tuple(int(g) for g in m.groups()) != want:
        found.append(f"the wiki says {m.groups()}, the pinned sets give {want}")
    return found


def server_and_agent_count_findings(text: str, server_count: int, agent_count: int, holder_count: int) -> list[str]:
    found = []
    m = re.search(r"\((\d+) servers? the Opencode manifest carries\)|the (\d+) servers the Opencode manifest carries", text)
    if not m or int(next(g for g in m.groups() if g)) != server_count:
        found.append(f"the number of servers the Opencode manifest carries is not {server_count}")
    m = re.search(r"For `gitlab` that is (\d+) of the (\d+) agents", text)
    if not m or (int(m.group(1)), int(m.group(2))) != (agent_count - holder_count, agent_count):
        found.append(f"the number of agents without the GitLab server is not {agent_count - holder_count} of {agent_count}")
    return found


class DocumentedPlaywrightAndOpencodeCountTests(unittest.TestCase):
    def setUp(self):
        self.wiki = DOCS["wiki"].read_text(encoding="utf-8")
        self.servers = yaml.safe_load(SERVERS_YAML.read_text(encoding="utf-8"))["servers"]
        self.tokens = agent_tokens()

    def test_the_wiki_playwright_counts_equal_the_pinned_sets(self):
        self.assertEqual(playwright_count_findings(self.wiki), [])

    def test_the_wiki_server_and_agent_counts_equal_servers_yaml_and_the_agent_sources(self):
        carried = [n for n, s in self.servers.items() if set(s["tags"]) & {"core", "extended"}]
        holders = len(actual_gitlab_counts(self.tokens))
        self.assertEqual(server_and_agent_count_findings(self.wiki, len(carried), len(self.tokens), holders), [])

    def test_a_changed_count_is_noticed(self):
        for old, new in (("19 of the 25 default tools", "20 of the 25 default tools"),
                         ("between 12 and 18 of them", "between 12 and 19 of them")):
            self.assertIn(old, self.wiki)
            self.assertTrue(playwright_count_findings(self.wiki.replace(old, new, 1)), new)
        carried, holders = len(self.servers), len(actual_gitlab_counts(self.tokens))
        for old, new in (("the 17 servers the Opencode manifest carries", "the 16 servers the Opencode manifest carries"),
                         ("For `gitlab` that is 21 of the 28 agents", "For `gitlab` that is 22 of the 28 agents")):
            self.assertIn(old, self.wiki)
            self.assertTrue(server_and_agent_count_findings(self.wiki.replace(old, new, 1), carried, len(self.tokens), holders), new)


if __name__ == "__main__":
    unittest.main()
