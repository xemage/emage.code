# maturity-evidence: agent/context-retriever
# maturity-evidence: agent/data-mockup-agent
# maturity-evidence: agent/database-engineer
# maturity-evidence: agent/demo-agent
# maturity-evidence: agent/evaluation-agent
# maturity-evidence: agent/feasibility-agent
# maturity-evidence: agent/frontend-developer
# maturity-evidence: agent/integration-agent
# maturity-evidence: agent/poc-devops-engineer
# maturity-evidence: agent/poc-orchestrator
# maturity-evidence: agent/poc-qa-engineer
# maturity-evidence: agent/poc-security-engineer
# maturity-evidence: agent/poc-technical-writer
# maturity-evidence: agent/product-owner
# maturity-evidence: agent/scaffolding-agent
# maturity-evidence: agent/scrum-master
# maturity-evidence: agent/solution-architect
# maturity-evidence: agent/technical-debt-narrator
# maturity-evidence: agent/technology-scout
# maturity-evidence: agent/ux-designer
"""Cross-consistency tests for each agent's blocker-escalation path (T434, Wave 2).

Every agent's `### Blocker Reporting` section names an escalation target ("the
orchestrator" or "the PoC orchestrator"). This module proves that claim is not
just prose: for PoC-track agents, it cross-checks the claimed escalation
target (`poc-orchestrator`) actually lists that agent id in its own `agents:`
frontmatter roster (a real, bidirectional consistency check — catches an
agent claiming PoC-orchestrator escalation while poc-orchestrator itself has
no record of coordinating it, or vice versa); for production-track agents, it
proves the named escalation target resolves to a real, registered agent id.
`poc-orchestrator` itself is proven differently: every `@<agent-id>` mention
in its own `## PoC Workflow` section (the concrete delegation sequence it
follows) is proven to resolve to a real, registered agent id — the same
"named executor must be a real registered agent" shape T433 already used for
one of its own skills' Gate Types table (see phase3-wave1-promotion-v1.md,
not repeated here by id), applied here to an agent's own delegation roster
instead of a skill's gate table.
"""
from __future__ import annotations

import re
import unittest

from tests._helpers.repo import knowledge_root


def _agent_text(agent_id: str) -> str:
    path = knowledge_root() / "agents" / f"{agent_id}.md"
    return path.read_text(encoding="utf-8")


def _registered_agent_ids() -> set[str]:
    agents_dir = knowledge_root() / "agents"
    return {p.stem for p in agents_dir.glob("*.md")}


def _poc_orchestrator_roster() -> set[str]:
    text = _agent_text("poc-orchestrator")
    match = re.search(r'^agents:\s*\[(.*?)\]\s*$', text, re.MULTILINE)
    assert match is not None, "poc-orchestrator.md must declare an `agents:` frontmatter roster"
    return {item.strip() for item in match.group(1).split(",") if item.strip()}


POC_TRACK_AGENTS = (
    "data-mockup-agent",
    "demo-agent",
    "evaluation-agent",
    "feasibility-agent",
    "integration-agent",
    "poc-devops-engineer",
    "poc-qa-engineer",
    "poc-security-engineer",
    "poc-technical-writer",
    "scaffolding-agent",
    "technical-debt-narrator",
    "technology-scout",
)

PRODUCTION_TRACK_AGENTS = (
    "context-retriever",
    "database-engineer",
    "frontend-developer",
    "product-owner",
    "scrum-master",
    "solution-architect",
    "ux-designer",
)


class TestPocTrackEscalationMatchesRoster(unittest.TestCase):
    """Each PoC-track agent's claimed escalation target really coordinates it."""

    def test_roster_covers_all_poc_track_agents(self):
        roster = _poc_orchestrator_roster()
        for agent_id in POC_TRACK_AGENTS:
            self.assertIn(
                agent_id, roster,
                f"{agent_id} claims PoC-orchestrator escalation but is not listed in "
                f"poc-orchestrator.md's own `agents:` roster",
            )

    def test_each_poc_track_agent_names_poc_orchestrator(self):
        for agent_id in POC_TRACK_AGENTS:
            with self.subTest(agent=agent_id):
                text = _agent_text(agent_id)
                self.assertIn(
                    "The PoC orchestrator will handle escalation", text,
                    f"{agent_id}'s Blocker Reporting section must name the PoC orchestrator "
                    f"as its escalation target",
                )


class TestProductionTrackEscalationResolves(unittest.TestCase):
    """Each production-track agent's claimed escalation target is a real agent id."""

    def test_each_agent_names_orchestrator(self):
        registered = _registered_agent_ids()
        self.assertIn("orchestrator", registered)
        for agent_id in PRODUCTION_TRACK_AGENTS:
            with self.subTest(agent=agent_id):
                text = _agent_text(agent_id)
                self.assertIn(
                    "The orchestrator will handle escalation", text,
                    f"{agent_id}'s Blocker Reporting section must name the orchestrator "
                    f"as its escalation target",
                )

    def test_production_track_agents_are_not_poc_roster_only(self):
        # Sanity check that the two classifications above are drawn from disjoint,
        # deliberately-curated lists, not accidentally overlapping.
        self.assertEqual(set(), set(PRODUCTION_TRACK_AGENTS) & set(POC_TRACK_AGENTS))


class TestPocOrchestratorWorkflowMentionsResolve(unittest.TestCase):
    """Every `@<agent-id>` poc-orchestrator delegates to in its own workflow is real."""

    def test_workflow_mentions_are_real_registered_agents(self):
        text = _agent_text("poc-orchestrator")
        section_match = re.search(
            r"## PoC Workflow\n(.*?)\n## ", text, re.DOTALL
        )
        self.assertIsNotNone(section_match, "poc-orchestrator.md must have a ## PoC Workflow section")
        mentions = set(re.findall(r"@([a-z][a-z0-9-]*)", section_match.group(1)))
        self.assertGreaterEqual(
            len(mentions), 10, "expected at least 10 distinct @-mentioned agents in the workflow"
        )
        registered = _registered_agent_ids()
        for agent_id in mentions:
            with self.subTest(agent=agent_id):
                self.assertIn(
                    agent_id, registered,
                    f"poc-orchestrator's PoC Workflow mentions @{agent_id}, which is not a "
                    f"real registered agent id",
                )

    def test_workflow_roster_matches_frontmatter_roster(self):
        text = _agent_text("poc-orchestrator")
        section_match = re.search(r"## PoC Workflow\n(.*?)\n## ", text, re.DOTALL)
        self.assertIsNotNone(section_match)
        mentions = set(re.findall(r"@([a-z][a-z0-9-]*)", section_match.group(1)))
        roster = _poc_orchestrator_roster()
        # Every workflow-mentioned specialist (excluding the shared production
        # developers, who are briefed rather than owned exclusively) must be
        # declared in the agent's own `agents:` frontmatter roster.
        specialists = mentions - {"backend-developer", "frontend-developer"}
        self.assertTrue(specialists, "expected at least one PoC specialist mention")
        for agent_id in specialists:
            with self.subTest(agent=agent_id):
                self.assertIn(agent_id, roster)


if __name__ == "__main__":
    unittest.main()
