"""T693 -- text pins for the release self-review ruling (P112-P41-O1, option A+).

Implements `docs/artifacts/ruling-p112-p41-o1-release-self-review-v1.md` section 5.1, hunks E1 to E3:

- E1: `release-manager.md` Release Gate Policy item 5 (independent check of the release document);
- E2: `release-manager.md` Gate Inputs row `Release document, independent check (commit: [sha])`;
- E3: `orchestrator.md` Release-gate pointer bullet.

Each hunk is pinned verbatim, at its place (directly after its Before line), in the knowledge source and in
every generated agent projection. The section references the new text relies on (`validation-gates`
§ Guidelines, `release-manager` § Release Gate Policy and `orchestrator` Core Workflow, Phase 5, step 2)
are checked to resolve. Pure text tests: no subprocess, no generator run.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests._helpers.repo import implementation_root, knowledge_root  # noqa: E402

AGENTS = knowledge_root() / "agents"
RM_PATH = AGENTS / "release-manager.md"
OR_PATH = AGENTS / "orchestrator.md"
VG_PATH = knowledge_root() / "skills" / "validation-gates" / "SKILL.md"

RM_MIRRORS = (
    ".claude/agents/release-manager.md",
    ".gemini/agents/release-manager.md",
    ".github/agents/release-manager.agent.md",
    ".opencode/agents/release-manager.md",
    ".pi/agents/release-manager.md",
)
OR_MIRRORS = tuple(p.replace("release-manager", "orchestrator") for p in RM_MIRRORS)

E1_BEFORE = "4. Track blocker metadata in release notes: blocker ID, owner, ETA, mitigation."
E1_LINE = (
    "5. Independent check of what you authored. This verdict aggregates the verdicts of other executors; the "
    "release document you prepare (version markers, changelog, release notes, rollback plan) is your own work, "
    "and `validation-gates` § Guidelines says gate executors should not review their own work. Do not issue a "
    "PASS or CONDITIONAL_PASS on that document alone: record in the Gate Inputs table who checked it "
    "independently (the `tech-lead` review by area, or the top-level session's own verification) and the "
    "commit that check covered. The check covers the document at the recorded commit; after it, only the "
    "`## RELEASE VERDICT` section and the `Release:` line under `## Gate Verdicts` may change. Any other "
    "change makes the check stale: report a blocker and have the same independent party re-run it on the new "
    "commit; "
    "never re-run it yourself. Your verdict is an input to the top-level session's verification before the "
    "merge and to the user's approval of the tag, not a substitute for either."
)
# SEC-T693-01 (user decision "fix 01", 2026-10-31): the sentence this replaced must not return.
E1_OLD_SENTENCE = "If the document changed after that commit, the check is stale: report it as a blocker or re-run it."
E2_BEFORE = "| Performance Check | PASS/FAIL | `perf-report-vN.md` |"
E2_LINE = (
    "| Release document, independent check (commit: [sha]) | PASS/CONDITIONAL_PASS/FAIL | "
    "[reviewer artifact, or the top-level session's recorded verification] |"
)
E3_BEFORE = '- Delegate to `@release-manager`: "Verify release readiness. Produce VERDICT."'
E3_LINE = (
    "- The release manager prepares `docs/releases/vX.Y.Z.md` (Core Workflow, Phase 5, step 2), so obtain the "
    "independent check of that document first (a `@tech-lead` review by area, or your own verification) and "
    "give the release manager its artifact and commit; `release-manager` § Release Gate Policy item 5 "
    "requires it."
)
# The line E3's "(Core Workflow, Phase 5, step 2)" points at (ruling section 1.1, `orchestrator.md:259` as read).
CORE_P5_STEP2 = "2. Delegate to **@release-manager** for versioning, changelog, release preparation"


def _lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _section(lines: list[str], heading: str) -> list[str]:
    """Lines under `heading` up to the next heading of the same or a higher level."""
    level = len(heading) - len(heading.lstrip("#"))
    start = lines.index(heading)
    out = []
    for line in lines[start + 1:]:
        stripped = line.lstrip("#")
        if line.startswith("#") and stripped.startswith(" ") and len(line) - len(stripped) <= level:
            break
        out.append(line)
    return out


class _HunkMixin:
    def assert_hunk(self, lines: list[str], before: str, added: str, where: str) -> None:
        self.assertEqual(lines.count(before), 1, f"{where}: Before line must occur exactly once")
        self.assertEqual(lines.count(added), 1, f"{where}: added line must occur exactly once")
        i = lines.index(before)
        self.assertEqual(lines[i + 1], added, f"{where}: added line must follow its Before line directly")


class ReleaseManagerHunks(_HunkMixin, unittest.TestCase):
    def _files(self):
        yield "knowledge/agents/release-manager.md", RM_PATH
        for rel in RM_MIRRORS:
            yield rel, implementation_root() / rel

    def test_e1_policy_item_5(self):
        for where, path in self._files():
            with self.subTest(file=where):
                lines = _lines(path)
                self.assert_hunk(lines, E1_BEFORE, E1_LINE, where)
                self.assertNotIn(E1_OLD_SENTENCE, "\n".join(lines), f"{where}: SEC-T693-01 sentence came back")
                policy = _section(lines, "### Release Gate Policy")
                self.assertIn(E1_LINE, policy, f"{where}: item 5 must sit in § Release Gate Policy")
                items = [ln for ln in policy if ln[:2] in {f"{n}." for n in range(1, 10)}]
                self.assertEqual([ln[:2] for ln in items], ["1.", "2.", "3.", "4.", "5."],
                                 f"{where}: Release Gate Policy must be items 1 to 5")

    def test_e2_gate_inputs_row(self):
        for where, path in self._files():
            with self.subTest(file=where):
                lines = _lines(path)
                self.assert_hunk(lines, E2_BEFORE, E2_LINE, where)
                gate_inputs = _section(lines, "### Gate Inputs")
                self.assertIn(E2_LINE, gate_inputs, f"{where}: the row must sit in the Gate Inputs table")


class OrchestratorHunk(_HunkMixin, unittest.TestCase):
    def test_e3_release_gate_pointer(self):
        files = [("knowledge/agents/orchestrator.md", OR_PATH)]
        files += [(rel, implementation_root() / rel) for rel in OR_MIRRORS]
        for where, path in files:
            with self.subTest(file=where):
                lines = _lines(path)
                self.assert_hunk(lines, E3_BEFORE, E3_LINE, where)
                i = lines.index(E3_BEFORE)
                self.assertEqual(lines[i - 1], "**RELEASE GATE** (before deployment):",
                                 f"{where}: the pointer must sit under the Release gate")


class ReferencedSectionsResolve(unittest.TestCase):
    def test_validation_gates_guidelines_self_review_rule(self):
        guidelines = _section(_lines(VG_PATH), "## Guidelines")
        self.assertIn("- Gate executors should not review their own work. Cross-agent review is mandatory.",
                      guidelines)

    def test_orchestrator_core_workflow_phase_5_step_2(self):
        core = _section(_lines(OR_PATH), "## Core Workflow")
        phase5 = _section(core, next(ln for ln in core if ln.startswith("### Phase 5:")))
        self.assertIn(CORE_P5_STEP2, phase5, "E3's (Core Workflow, Phase 5, step 2) must name the preparation step")

    def test_release_manager_policy_heading_exists(self):
        self.assertEqual(_lines(RM_PATH).count("### Release Gate Policy"), 1)


if __name__ == "__main__":
    unittest.main()
