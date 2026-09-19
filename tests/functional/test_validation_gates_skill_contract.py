# maturity-evidence: skill/validation-gates
"""Contract tests for the `validation-gates` skill (T433).

Proves the skill's documented Gate Types table stays honest against the real
knowledge base rather than drifting silently: every named "Executor" must be
a real, registered agent id, and the skill's own Verdict Rules table must
stay internally consistent with the shared PASS/CONDITIONAL_PASS/FAIL
vocabulary every other gate-producing agent (`tech-lead`, `qa-engineer`,
`security-engineer`) also documents in its own VERDICT format section.
"""
from __future__ import annotations

import re
import unittest

from tests._helpers.repo import knowledge_root


def _skill_text() -> str:
    path = knowledge_root() / "skills" / "validation-gates" / "SKILL.md"
    return path.read_text(encoding="utf-8")


def _agent_ids() -> set[str]:
    agents_dir = knowledge_root() / "agents"
    return {p.stem for p in agents_dir.glob("*.md")}


class TestValidationGatesSkillContract(unittest.TestCase):
    def test_gate_executors_are_real_registered_agents(self):
        text = _skill_text()
        table_match = re.search(r"## Gate Types\n\n(.*?)\n\n", text, re.DOTALL)
        self.assertIsNotNone(table_match, "Gate Types table must exist")
        rows = [
            line for line in table_match.group(1).splitlines()
            if line.startswith("|") and "---" not in line and "Gate" not in line
        ]
        self.assertGreaterEqual(len(rows), 5, "expected 5 documented gate types")
        agent_ids = _agent_ids()
        name_to_id = {
            "Tech Lead": "tech-lead",
            "QA Agent": "qa-engineer",
            "Security Agent": "security-engineer",
            "Release Manager": "release-manager",
        }
        for row in rows:
            cells = [c.strip() for c in row.strip("|").split("|")]
            executor_name = cells[1]
            resolved = name_to_id.get(executor_name)
            self.assertIsNotNone(
                resolved, f"unrecognized executor name in Gate Types table: {executor_name}"
            )
            self.assertIn(
                resolved, agent_ids, f"executor {resolved} is not a real registered agent id"
            )

    def test_verdict_vocabulary_matches_downstream_agents(self):
        text = _skill_text()
        for verdict in ("PASS", "CONDITIONAL_PASS", "FAIL"):
            self.assertIn(verdict, text)

        for agent_id in ("tech-lead", "qa-engineer", "security-engineer"):
            agent_text = (knowledge_root() / "agents" / f"{agent_id}.md").read_text(
                encoding="utf-8"
            )
            for verdict in ("PASS", "CONDITIONAL_PASS", "FAIL"):
                self.assertIn(
                    verdict,
                    agent_text,
                    f"{agent_id} must document the same {verdict} vocabulary as validation-gates",
                )


if __name__ == "__main__":
    unittest.main()
