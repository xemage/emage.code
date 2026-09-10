# maturity-evidence: skill/code-review
"""Contract tests for the `code-review` skill (T433).

Proves the skill's documented severity guide (Must Fix / Should Fix / Nice
to Have) and structured VERDICT format stay consistent with the two other
places this repo documents code review: the `/code-review` command's own
Verdict Output section, and `tech-lead.md`'s Review Verdict Format section
(the agent that actually executes this skill). A drift here (e.g. one place
renaming a severity level or a verdict value) is a real, catchable defect,
not a hypothetical one -- this repeats the exact duplication risk the skill
file's own "Protocol-Aware Enhancements" section was added to address.
"""
from __future__ import annotations

import unittest

from tests._helpers.repo import knowledge_root


def _read(*parts: str) -> str:
    return (knowledge_root().joinpath(*parts)).read_text(encoding="utf-8")


class TestCodeReviewSkillContract(unittest.TestCase):
    def test_severity_guide_matches_across_skill_and_agent(self):
        skill_text = _read("skills", "code-review", "SKILL.md")
        agent_text = _read("agents", "tech-lead.md")
        # The skill's four-level severity guide and the agent's own review
        # feedback format must agree on "must/should/nice" framing, not
        # silently diverge into incompatible vocabularies.
        for marker in ("Must Fix", "Should Fix", "Nice to Have"):
            self.assertIn(marker, skill_text)
        self.assertIn("Critical (must fix)", agent_text)
        self.assertIn("Important (should fix)", agent_text)
        self.assertIn("Suggestion (nice to have)", agent_text)

    def test_verdict_values_match_command_and_agent(self):
        skill_text = _read("skills", "code-review", "SKILL.md")
        command_text = _read("commands", "code-review.md")
        agent_text = _read("agents", "tech-lead.md")
        for verdict in ("PASS", "CONDITIONAL_PASS", "FAIL"):
            self.assertIn(verdict, skill_text)
            self.assertIn(verdict, command_text)
            self.assertIn(verdict, agent_text)

    def test_command_declares_its_owning_agent_as_tech_lead(self):
        command_text = _read("commands", "code-review.md")
        self.assertIn('agent: "tech-lead"', command_text)


if __name__ == "__main__":
    unittest.main()
