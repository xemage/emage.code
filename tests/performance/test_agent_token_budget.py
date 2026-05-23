"""Per-agent and per-skill content size budgets.

Why this matters: every agent prompt is loaded into the LLM's context every
time the agent is invoked. Bloated prompts waste context budget and degrade
reasoning. We treat the per-agent character/token count as a hard budget.
"""
from __future__ import annotations

import json
import unittest

from tests._helpers.frontmatter import parse_file
from tests._helpers.repo import list_agents, list_skills, repo_root
from tests._helpers.tokens import estimate_tokens


def _baselines() -> dict:
    return json.loads((repo_root() / "tests" / "_baselines" / "sync-timings.json").read_text())


class TestAgentTokenBudget(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.budgets = _baselines()

    def test_agent_prompts_fit_budget(self):
        char_max = self.budgets["agent_max_chars"]
        token_max = self.budgets["agent_max_estimated_tokens"]
        report = []
        offenders = []
        for path in list_agents():
            text = path.read_text(encoding="utf-8")
            chars = len(text)
            tokens = estimate_tokens(text)
            report.append((path.stem, chars, tokens))
            if chars > char_max or tokens > token_max:
                offenders.append(
                    f"{path.stem}: {chars} chars ≈ {tokens} tokens "
                    f"(budget: {char_max} chars / {token_max} tokens)"
                )
        # Always print the size profile so reviewers can see growth trends
        report.sort(key=lambda r: -r[1])
        print("\n[agent-size-profile] top 5 by chars:")
        for name, c, t in report[:5]:
            print(f"  {name:<30} {c:>6} chars ≈ {t:>5} tokens")
        self.assertFalse(
            offenders,
            msg="Agent prompts exceed budget:\n  " + "\n  ".join(offenders),
        )

    def test_skills_fit_budget(self):
        char_max = self.budgets["skill_max_chars"]
        token_max = self.budgets["skill_max_estimated_tokens"]
        offenders = []
        for path in list_skills():
            text = path.read_text(encoding="utf-8")
            chars = len(text)
            tokens = estimate_tokens(text)
            if chars > char_max or tokens > token_max:
                offenders.append(
                    f"{path.parent.name}: {chars} chars ≈ {tokens} tokens "
                    f"(budget: {char_max} chars / {token_max} tokens)"
                )
        self.assertFalse(
            offenders,
            msg="Skill prompts exceed budget:\n  " + "\n  ".join(offenders),
        )

    def test_no_empty_agent_bodies(self):
        """Frontmatter is not enough — every agent must have actual instructions."""
        for path in list_agents():
            _, body = parse_file(path)
            with self.subTest(agent=path.stem):
                self.assertGreater(
                    len(body.strip()), 200,
                    f"{path.stem}: body is suspiciously short ({len(body.strip())} chars)",
                )


if __name__ == "__main__":
    unittest.main()
