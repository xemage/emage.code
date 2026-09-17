"""Cross-reference integrity:

- Every agent listed under another agent's `agents:` field must exist
- Every `mcp__<server>` tool referenced by an agent must be declared in mcp/servers.yaml
- The orchestrator's `agents` list must mention every agent that exists
  (warns rather than fails — keeps room for read-only / specialist-only agents)
"""
from __future__ import annotations

import re
import unittest

import yaml

from tests._helpers.frontmatter import parse_file
from tests._helpers.repo import knowledge_root, list_agents


MCP_TOOL_RE = re.compile(r"^mcp__([a-zA-Z0-9_-]+)$")


def _load_servers() -> set[str]:
    raw = yaml.safe_load((knowledge_root() / "mcp" / "servers.yaml").read_text())
    # servers.yaml structure: { servers: { <name>: { ... } } } OR top-level mapping
    if isinstance(raw, dict) and "servers" in raw:
        servers = raw["servers"]
    else:
        servers = raw
    if not isinstance(servers, dict):
        raise RuntimeError(f"servers.yaml: unexpected top-level shape {type(servers).__name__}")
    return set(servers.keys())


def _agent_slugs() -> set[str]:
    return {p.stem for p in list_agents()}


class TestCrossReferences(unittest.TestCase):
    def setUp(self):
        self.agents = _agent_slugs()
        self.servers = _load_servers()

    def test_agent_references_resolve(self):
        for path in list_agents():
            fm, _ = parse_file(path)
            referenced = fm.get("agents") or []
            for ref in referenced:
                with self.subTest(agent=path.stem, references=ref):
                    self.assertIn(
                        ref, self.agents,
                        msg=f"{path.stem} references unknown agent '{ref}'",
                    )

    def test_no_self_reference(self):
        for path in list_agents():
            fm, _ = parse_file(path)
            referenced = fm.get("agents") or []
            with self.subTest(agent=path.stem):
                self.assertNotIn(
                    path.stem, referenced,
                    msg=f"{path.stem}: agent references itself in `agents` list",
                )

    def test_mcp_tool_references_resolve(self):
        for path in list_agents():
            fm, _ = parse_file(path)
            tools = fm.get("tools") or []
            for tool in tools:
                m = MCP_TOOL_RE.match(tool)
                if not m:
                    continue
                body = m.group(1)
                # Two token shapes both currently in use: a bare server reference
                # (`mcp__fetch`, `mcp__sequential_thinking` -> sequential-thinking) and,
                # since T495, Claude Code's own exact-MCP-tool-name form
                # (`mcp__<server>__<tool>`, e.g. `mcp__context-retriever__retrieve` --
                # scoped-execution-primitive-v1.md §1.3/§1.4). Try the whole body as a
                # server name first (bare form); if that doesn't resolve and the body
                # contains "__", split off the trailing `__<tool>` segment and try the
                # server-name prefix instead -- this only validates that the referenced
                # *server* is declared, exactly as before, not that the server actually
                # exposes that specific tool name.
                candidates = {body, body.replace("_", "-")}
                if "__" in body:
                    server_part, _, _tool_part = body.rpartition("__")
                    candidates.add(server_part)
                    candidates.add(server_part.replace("_", "-"))
                with self.subTest(agent=path.stem, tool=tool):
                    self.assertTrue(
                        any(c in self.servers for c in candidates),
                        msg=(
                            f"{path.stem} requests tool '{tool}' but no candidate server name "
                            f"{sorted(candidates)} is declared in mcp/servers.yaml. "
                            f"Known: {sorted(self.servers)}"
                        ),
                    )

    def test_orchestrator_agent_list_covers_engineering_team(self):
        """The orchestrator should know about the core engineering agents.
        This catches the regression where a new specialist is added but never
        wired into the orchestrator's delegation list."""
        orch_path = knowledge_root() / "agents" / "orchestrator.md"
        fm, _ = parse_file(orch_path)
        delegated = set(fm.get("agents") or [])
        must_know = {
            "product-owner",
            "solution-architect",
            "tech-lead",
            "backend-developer",
            "frontend-developer",
            "qa-engineer",
            "security-engineer",
            "devops-engineer",
        }
        missing = must_know - delegated
        self.assertFalse(
            missing,
            msg=f"orchestrator missing core agents in delegation list: {sorted(missing)}",
        )

    def test_no_orphan_agents(self):
        """Every agent should be referenced by at least one orchestrator/agent
        OR appear in a command's `agent:` field. Pure orphans suggest dead code."""
        referenced = set()
        for path in list_agents():
            fm, _ = parse_file(path)
            referenced.update(fm.get("agents") or [])
        # Also scan commands
        for path in (knowledge_root() / "commands").glob("*.md"):
            fm, _ = parse_file(path)
            if fm.get("agent"):
                referenced.add(fm["agent"])
        # Orchestrators are user-facing entrypoints — exempt them
        exempt = {"orchestrator", "poc-orchestrator"}
        orphans = self.agents - referenced - exempt
        self.assertFalse(
            orphans,
            msg=(
                f"Orphan agents (not referenced by any orchestrator, agent, "
                f"or command): {sorted(orphans)}. Either wire them in or "
                f"remove them."
            ),
        )


if __name__ == "__main__":
    unittest.main()
