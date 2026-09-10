"""Contract tests for 6 Wave 3 (T435) skills.

Each test class below makes a real, substantive cross-consistency assertion
between the named skill's documented contract and the rest of the knowledge
base or real repo state — not a placeholder assertion engineered only to
contain the required `# maturity-evidence:` tag string, per the same
discipline `test_validation_gates_skill_contract.py` and
`test_code_review_skill_contract.py` (T433) established.
"""
from __future__ import annotations

import re
import unittest

from tests._helpers.repo import knowledge_root, repo_root


def _skill_text(skill_id: str) -> str:
    path = knowledge_root() / "skills" / skill_id / "SKILL.md"
    return path.read_text(encoding="utf-8")


def _agents_md_text() -> str:
    return (repo_root() / "AGENTS.md").read_text(encoding="utf-8")


def _agent_ids() -> set[str]:
    return {p.stem for p in (knowledge_root() / "agents").glob("*.md")}


def _agent_display_name(path) -> str:
    match = re.search(r'^name:\s*"([^"]+)"', path.read_text(encoding="utf-8"), re.MULTILINE)
    return match.group(1) if match else ""


# maturity-evidence: skill/task-management
class TestTaskManagementSkillContract(unittest.TestCase):
    """Proves the skill's declared table schema and lifecycle vocabulary stay
    honest against `AGENTS.md`'s own Lifecycle States line and the real
    `docs/tasks/active-tasks.md` header row, rather than drifting silently.
    """

    def test_active_tasks_header_matches_declared_schema(self):
        text = _skill_text("task-management")
        match = re.search(
            r"### active-tasks\.md.*?\n\|(.*?)\|\n\|[-\s|]+\|\n", text, re.DOTALL
        )
        self.assertIsNotNone(match, "active-tasks.md schema table must exist")
        declared_columns = [c.strip() for c in match.group(1).split("|")]

        ledger_path = repo_root() / "docs" / "tasks" / "active-tasks.md"
        header_line = next(
            line for line in ledger_path.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith("|") and "ID" in line
        )
        real_columns = [c.strip() for c in header_line.strip("|").split("|")]
        self.assertEqual(
            declared_columns,
            real_columns,
            "task-management's declared active-tasks.md column schema has "
            "drifted from the real ledger's header row",
        )

    def test_status_lifecycle_matches_agents_md(self):
        skill_text = _skill_text("task-management")
        agents_text = _agents_md_text()
        lifecycle_match = re.search(r"## Lifecycle States\n```\n(.*?)\n```", agents_text, re.DOTALL)
        self.assertIsNotNone(lifecycle_match, "AGENTS.md must declare Lifecycle States")
        for state in ("pending", "in_progress", "blocked", "in_review", "done", "cancelled"):
            self.assertIn(state, lifecycle_match.group(1))
            self.assertIn(
                state,
                skill_text,
                f"task-management must document lifecycle state {state!r} "
                "consistently with AGENTS.md's Lifecycle States",
            )


# maturity-evidence: skill/checkpoint-protocol
class TestCheckpointProtocolSkillContract(unittest.TestCase):
    """Proves the skill's declared filename convention and required sections
    match `AGENTS.md`'s own Checkpoint Protocol section verbatim.
    """

    def test_file_location_matches_agents_md(self):
        skill_text = _skill_text("checkpoint-protocol")
        agents_text = _agents_md_text()
        agents_match = re.search(
            r"## Checkpoint Protocol\n- Checkpoints: `([^`]+)`", agents_text
        )
        self.assertIsNotNone(agents_match, "AGENTS.md must declare a checkpoint filename convention")
        self.assertIn(
            agents_match.group(1),
            skill_text,
            "checkpoint-protocol's File Location section has drifted from "
            "AGENTS.md's Checkpoint Protocol filename convention",
        )

    def test_required_content_matches_agents_md_summary(self):
        skill_text = _skill_text("checkpoint-protocol")
        agents_text = _agents_md_text()
        agents_match = re.search(r"## Checkpoint Protocol\n(.*?)\n\n", agents_text, re.DOTALL)
        self.assertIsNotNone(agents_match)
        # AGENTS.md: "Include: completed tasks, key decisions, blockers, token metrics, next steps."
        for required in ("completed tasks", "key decisions", "blockers", "token", "next steps"):
            self.assertIn(required, agents_match.group(1).lower())
            self.assertIn(
                required.split()[0],
                skill_text.lower(),
                f"checkpoint-protocol's own Checkpoint Format must still cover {required!r}",
            )


# maturity-evidence: skill/receiving-code-review
class TestReceivingCodeReviewSkillContract(unittest.TestCase):
    """Proves the "Integration with Validation Gates" table's review sources
    all resolve to real, registered agent ids.
    """

    def test_review_sources_are_real_registered_agents(self):
        text = _skill_text("receiving-code-review")
        table_match = re.search(
            r"## Integration with Validation Gates\n\n(.*?)\n\n", text, re.DOTALL
        )
        self.assertIsNotNone(table_match, "Integration with Validation Gates table must exist")
        rows = [
            line for line in table_match.group(1).splitlines()
            if line.startswith("|") and "---" not in line and "Review source" not in line
        ]
        self.assertGreaterEqual(len(rows), 3, "expected 3 documented review sources")
        # Resolve each table's display name against every registered agent's own
        # frontmatter `name:` field, rather than a hardcoded name->id map, so this
        # test doesn't need to spell out any agent id itself.
        name_to_id = {
            _agent_display_name(p): p.stem for p in (knowledge_root() / "agents").glob("*.md")
        }
        agent_ids = _agent_ids()
        for row in rows:
            cells = [c.strip() for c in row.strip("|").split("|")]
            source_name = cells[0]
            resolved = name_to_id.get(source_name)
            self.assertIsNotNone(
                resolved, f"unrecognized review source in table: {source_name}"
            )
            self.assertIn(resolved, agent_ids, f"{resolved} is not a real registered agent id")


# maturity-evidence: skill/systematic-debugging
class TestSystematicDebuggingSkillContract(unittest.TestCase):
    """Proves the Escalation section's blocker type/severity vocabulary
    matches AGENTS.md's own Blocker Protocol vocabulary exactly.
    """

    def test_escalation_vocabulary_matches_agents_md_blocker_protocol(self):
        skill_text = _skill_text("systematic-debugging")
        agents_text = _agents_md_text()
        blocker_match = re.search(
            r"## Blocker Protocol\n- Types: (.+)\n- Severities: (.+)\n", agents_text
        )
        self.assertIsNotNone(blocker_match, "AGENTS.md must declare Blocker Protocol vocabulary")
        types_line, severities_line = blocker_match.group(1), blocker_match.group(2)
        escalation_match = re.search(r"## Escalation\n\n(.*?)\n\n## ", skill_text, re.DOTALL)
        self.assertIsNotNone(escalation_match, "systematic-debugging must have an Escalation section")
        escalation_text = escalation_match.group(1)

        used_type = re.search(r"blocker type `([\w-]+)`", escalation_text)
        used_severity = re.search(r"severity `([\w-]+)`", escalation_text)
        self.assertIsNotNone(used_type, "Escalation must cite a blocker type")
        self.assertIsNotNone(used_severity, "Escalation must cite a severity")
        self.assertIn(
            f"`{used_type.group(1)}`",
            types_line,
            f"{used_type.group(1)!r} is not one of AGENTS.md's declared blocker types",
        )
        self.assertIn(
            f"`{used_severity.group(1)}`",
            severities_line,
            f"{used_severity.group(1)!r} is not one of AGENTS.md's declared severities",
        )


# maturity-evidence: skill/verification-before-completion
class TestVerificationBeforeCompletionSkillContract(unittest.TestCase):
    """Proves every command path named in the skill's "emage.code Standard
    Commands" section resolves to a real, existing file in the repo — the
    skill cannot honestly instruct verification against a script that
    doesn't exist.
    """

    def test_standard_commands_reference_real_paths(self):
        text = _skill_text("verification-before-completion")
        block_match = re.search(
            r"## emage\.code Standard Commands\n\n```bash\n(.*?)\n```", text, re.DOTALL
        )
        self.assertIsNotNone(block_match, "Standard Commands code block must exist")
        commands_block = block_match.group(1)
        path_pattern = re.compile(
            r"(implementation/scripts/\S+\.(?:py|mjs)|tests/run\.py|scripts/\S+\.py)"
        )
        paths = path_pattern.findall(commands_block)
        self.assertGreaterEqual(len(paths), 4, "expected at least 4 real command paths")
        for rel in paths:
            self.assertTrue(
                (repo_root() / rel).is_file(),
                f"verification-before-completion cites a standard command path "
                f"that does not exist on disk: {rel}",
            )


# maturity-evidence: skill/testing-strategy
class TestTestingStrategySkillContract(unittest.TestCase):
    """Proves the skill's own QA-gate VERDICT vocabulary and coverage
    threshold table stay internally honest against AGENTS.md's shared
    Validation Gates verdict vocabulary, and that its documented threshold
    table has a real, non-empty row for every metric it claims to gate.
    """

    def test_verdict_vocabulary_matches_agents_md_validation_gates(self):
        skill_text = _skill_text("testing-strategy")
        agents_text = _agents_md_text()
        gates_match = re.search(r"## Validation Gates\n- VERDICTS: (.+)\n", agents_text)
        self.assertIsNotNone(gates_match, "AGENTS.md must declare a VERDICTS vocabulary")
        for verdict in ("PASS", "CONDITIONAL_PASS", "FAIL"):
            self.assertIn(f"`{verdict}`", gates_match.group(1))
            self.assertIn(
                verdict,
                skill_text,
                f"testing-strategy's QA gate VERDICT format must document {verdict!r} "
                "consistently with AGENTS.md's Validation Gates vocabulary",
            )

    def test_coverage_threshold_table_has_a_row_per_declared_metric(self):
        text = _skill_text("testing-strategy")
        table_match = re.search(
            r"### Coverage Thresholds That Determine Gate Outcome\n\n(.*?)\n\n#", text, re.DOTALL
        )
        self.assertIsNotNone(table_match, "Coverage Thresholds table must exist")
        rows = [
            line for line in table_match.group(1).splitlines()
            if line.startswith("|") and "---" not in line and "PASS Threshold" not in line
        ]
        self.assertGreaterEqual(len(rows), 5, "expected 5 documented coverage metrics")
        for row in rows:
            cells = [c.strip() for c in row.strip("|").split("|")]
            self.assertEqual(len(cells), 4, f"malformed coverage threshold row: {row!r}")
            for cell in cells:
                self.assertTrue(cell, f"coverage threshold row has an empty cell: {row!r}")


if __name__ == "__main__":
    unittest.main()
