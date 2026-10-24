"""T692 -- text pin for where `TECHNICAL-DEBT.md` lives (RO621-N-2).

The user ruled (2026-10-24): the narrative debt register lives in the PoC root, next to `POC-DEBT-SCORECARD.md`,
with one file per PoC. The sentence is stated in `poc-guidelines.md` (section "Narrative Debt Register") and in the
`technical-debt-narrator` agent's output line; both sources and all their projections under `implementation/` must
carry it. Pure text test: no subprocess.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests._helpers.repo import implementation_root, knowledge_root  # noqa: E402

GUIDE_SENTENCE = (
    "`TECHNICAL-DEBT.md` lives in the PoC root, next to `POC-DEBT-SCORECARD.md` (the top-level directory of the "
    "PoC's code: the repository root when the PoC has its own repository, otherwise the directory that the PoC plan "
    "names as the PoC root), and each PoC has its own file."
)
NARRATOR_SENTENCE = (
    "The file lives in the PoC root, next to `POC-DEBT-SCORECARD.md` (the top-level directory of the PoC's code: the "
    "repository root when the PoC has its own repository, otherwise the directory that the PoC plan names as the "
    "PoC root), and each PoC has its own file."
)
GUIDE_HEAD = "## Narrative Debt Register (`TECHNICAL-DEBT.md`)"

GUIDE_PATHS = (
    "knowledge/instructions/poc-guidelines.md",
    ".claude/rules/poc-guidelines.md",
    ".clinerules/poc-guidelines.md",
    ".gemini/instructions/poc-guidelines.md",
    ".github/instructions/poc-guidelines.instructions.md",
    ".opencode/instructions/poc-guidelines.md",
    ".pi/instructions/poc-guidelines.md",
)
NARRATOR_PATHS = (
    "knowledge/agents/technical-debt-narrator.md",
    ".claude/agents/technical-debt-narrator.md",
    ".gemini/agents/technical-debt-narrator.md",
    ".github/agents/technical-debt-narrator.agent.md",
    ".opencode/agents/technical-debt-narrator.md",
    ".pi/agents/technical-debt-narrator.md",
)


def _read(rel: str) -> str:
    return (implementation_root() / rel).read_text(encoding="utf-8")


def _section(text: str) -> str:
    start = text.index(GUIDE_HEAD)
    end = text.find("\n## ", start + 1)
    return text[start:] if end == -1 else text[start:end]


class TechnicalDebtLocationTests(unittest.TestCase):
    def test_guidelines_and_projections_state_location_once_in_the_section(self):
        for rel in GUIDE_PATHS:
            with self.subTest(path=rel):
                text = _read(rel)
                self.assertEqual(text.count(GUIDE_SENTENCE), 1)
                self.assertIn(GUIDE_SENTENCE, _section(text))

    def test_narrator_and_projections_state_location_once_in_the_output_line(self):
        for rel in NARRATOR_PATHS:
            with self.subTest(path=rel):
                text = _read(rel)
                self.assertEqual(text.count(NARRATOR_SENTENCE), 1)
                line = next(ln for ln in text.splitlines() if ln.startswith("- TECHNICAL-DEBT.md with categorized debt"))
                self.assertIn(NARRATOR_SENTENCE, line)

    def test_sources_exist_in_knowledge_root(self):
        self.assertTrue((knowledge_root() / "instructions" / "poc-guidelines.md").is_file())
        self.assertTrue((knowledge_root() / "agents" / "technical-debt-narrator.md").is_file())


if __name__ == "__main__":
    unittest.main()
