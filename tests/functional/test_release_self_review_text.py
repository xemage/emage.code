"""T693/T721 -- text pins for the release self-review ruling and the batch D rulings.

T693 implemented `docs/artifacts/ruling-p112-p41-o1-release-self-review-v1.md` section 5.1, hunks E1 to E3.
T720 rewrote those three lines under `docs/artifacts/rulings-batch-d-v1.md` (R1 to R3); T721 re-pins them and
adds the pins SEC-T693-08 asked for (`docs/artifacts/security-review-t693-release-self-review-v1.md`):

- E1 (R1): `release-manager.md` Release Gate Policy item 5, verbatim, plus its decisive clauses one by one
  (the effect of a missing, stale or FAIL check row, the CONDITIONAL_PASS cap, the one name of the checker,
  "the release files", and the closed list of fields that may change after the check);
- E2 (R2): `release-manager.md` Gate Inputs row `Release files, independent check (commit: [sha])`;
- E3 (R3): `orchestrator.md` Release-gate pointer bullet;
- R4: `### Issued at commit` in the release-manager verdict block;
- R10: `Issued at commit` and `Independent check` in the `/prepare-release` verdict block and in
  `docs/releases/_template.md`;
- SEC-T693-08: the release-manager no-merge/no-tag constraint and the orchestrator tag preflight.

Each pin is checked in the knowledge source and in every generated projection. The projection list is
checked against the `fileMap` of the platform manifests that `sync.mjs` reads. `MutationProof` restores the
old text (or breaks a clause) in a temporary copy and shows that the pins fail on it. Pure text tests: no
subprocess, no generator run.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests._helpers.repo import docs_root, implementation_root, knowledge_root  # noqa: E402

AGENTS = knowledge_root() / "agents"
RM_PATH = AGENTS / "release-manager.md"
OR_PATH = AGENTS / "orchestrator.md"
PR_PATH = knowledge_root() / "commands" / "prepare-release.md"
TPL_PATH = docs_root() / "releases" / "_template.md"
VG_PATH = knowledge_root() / "skills" / "validation-gates" / "SKILL.md"
RULINGS_PATH = docs_root() / "artifacts" / "rulings-batch-d-v1.md"
PLATFORMS = implementation_root() / "platforms"

# Confirmed against `implementation/platforms/*.json` `fileMap.agents` / `fileMap.commands` (T721, item c);
# `cline.json` maps neither, so no `.cline` projection exists. `ProjectionList` keeps this in step.
RM_MIRRORS = (
    ".claude/agents/release-manager.md",
    ".gemini/agents/release-manager.md",
    ".github/agents/release-manager.agent.md",
    ".opencode/agents/release-manager.md",
    ".pi/agents/release-manager.md",
)
OR_MIRRORS = tuple(p.replace("release-manager", "orchestrator") for p in RM_MIRRORS)
PR_MIRRORS = (
    ".claude/commands/prepare-release.md",
    ".gemini/commands/prepare-release.md",
    ".github/prompts/prepare-release.prompt.md",
    ".opencode/commands/prepare-release.md",
    ".pi/prompts/prepare-release.md",
)

# --- E1 (R1) ---------------------------------------------------------------------------------------------
E1_BEFORE = "4. Track blocker metadata in release notes: blocker ID, owner, ETA, mitigation."
E1_SCOPE = (
    "the release files you prepare (the version files, the changelog, and `docs/releases/vX.Y.Z.md` with its "
    "release notes and rollback plan) are your own work"
)
E1_CHECKER = (
    "(the `tech-lead` review by area, the orchestrator's recorded verification, or the top-level session's "
    "recorded verification; name which one)"
)
E1_FAIL = "If that row is missing or stale, or its status is FAIL, your verdict is FAIL;"
E1_CAP = (
    "if its status is CONDITIONAL_PASS, your verdict is at most CONDITIONAL_PASS and the check's conditions "
    "are conditions of your verdict (item 2)."
)
E1_COVERS = "The check covers the release files at the recorded commit."
E1_FIELDS = (
    "Status", "Open blockers", "Quality gates passed", "Quality gates failed", "Blocker IDs", "Timestamp",
    "Issued at commit", "Independent check",
)
E1_MAY_CHANGE = (
    "After it, only these may change: the `Release:` line under `## Gate Verdicts`; in `## RELEASE VERDICT`, "
    "the values of " + ", ".join(E1_FIELDS[:-1]) + " and " + E1_FIELDS[-1] + "; and the verdict text of that "
    "section, which is its opening paragraph and what you add below the field list (Gate Inputs, "
    "Justification, Conditions, Blockers, and the user's decisions as recorded)."
)
E1_STALE = (
    "Any other change, including Version or the Features, Fixes or Breaking changes counts, makes the check "
    "stale: report a blocker and have the same independent party re-run it on the new commit; never re-run "
    "it yourself."
)
E1_LINE = (
    "5. Independent check of what you authored. This verdict aggregates the verdicts of other executors; "
    + E1_SCOPE + ", and `validation-gates` § Guidelines says gate executors should not review their own "
    "work. Do not issue a PASS or CONDITIONAL_PASS on those files alone: record in the Gate Inputs table who "
    "checked them independently " + E1_CHECKER + " and the commit that check covered. " + E1_FAIL + " "
    + E1_CAP + " " + E1_COVERS + " " + E1_MAY_CHANGE + " " + E1_STALE + " Your verdict is an input to the "
    "top-level session's verification before the merge and to the user's approval of the tag, not a "
    "substitute for either. A check made by the top-level session does not replace its own verification "
    "before the merge."
)
E1_CLAUSES = {
    "scope (the release files)": E1_SCOPE, "checker name": E1_CHECKER, "FAIL effect": E1_FAIL,
    "CONDITIONAL_PASS cap": E1_CAP, "coverage": E1_COVERS, "closed field list": E1_MAY_CHANGE,
    "stale rule": E1_STALE,
}
# Fields of the `/prepare-release` verdict block that the check freezes (R1: "Any other change ...").
FROZEN_FIELDS = ("Version", "Features included", "Fixes included", "Breaking changes", "Release manager")

# --- E2 (R2), E3 (R3), R4, R10 ----------------------------------------------------------------------------
E2_BEFORE = "| Performance Check | PASS/FAIL | `perf-report-vN.md` |"
E2_LINE = (
    "| Release files, independent check (commit: [sha]) | PASS/CONDITIONAL_PASS/FAIL | "
    "[artifact; checker: tech-lead, orchestrator or top-level session] |"
)
E3_BEFORE = '- Delegate to `@release-manager`: "Verify release readiness. Produce VERDICT."'
E3_CHECKER = (
    "(a `@tech-lead` review by area, or your own recorded verification, named as the orchestrator's, or as "
    "the top-level session's when you run as the top-level session)"
)
E3_LINE = (
    "- The release manager prepares the release files (Core Workflow, Phase 5, step 2): the version files, "
    "the changelog and `docs/releases/vX.Y.Z.md`. Obtain the independent check of those files first "
    + E3_CHECKER + " and give the release manager its artifact and commit; `release-manager` § Release Gate "
    "Policy item 5 requires it. That check does not replace the top-level session's own verification before "
    "the merge."
)
R4_BEFORE = "### Version: [vX.Y.Z]"
R4_LINE = "### Issued at commit: [sha the release files were at when you issued this verdict, before you wrote it]"
R4_BLOCK_START = "## RELEASE VERDICT: [PASS | CONDITIONAL_PASS | FAIL]"
R10_BEFORE = "- **Timestamp**: <ISO-8601>"
R10_LINES = (
    "- **Issued at commit**: <sha the release files were at when the verdict was issued>",
    "- **Independent check**: <PASS | CONDITIONAL_PASS | FAIL> at <sha>, by "
    "<tech-lead | orchestrator | top-level session>",
)

# --- SEC-T693-08 ------------------------------------------------------------------------------------------
NO_MERGE_LINE = (
    "- DO NOT merge a merge request, create or push a tag, or create a GitLab release: the top-level session "
    "does these with the user's approval, whatever the shell and the token would allow."
)
PREFLIGHT_HEADING = "## Release Workflow Preflights"
PREFLIGHT_LINE = "**MANDATORY** before a release tag is cut (the top-level session cuts it, with the user's approval):"

# --- Old text that must not return ------------------------------------------------------------------------
# SEC-T693-01 (user decision "fix 01", 2026-10-31).
E1_OLD_SENTENCE = "If the document changed after that commit, the check is stale: report it as a blocker or re-run it."
# The T693 wording that R1 to R3 replaced (as pinned by this file before T721).
OLD_E1_LINE = (
    "5. Independent check of what you authored. This verdict aggregates the verdicts of other executors; the "
    "release document you prepare (version markers, changelog, release notes, rollback plan) is your own work, "
    "and `validation-gates` § Guidelines says gate executors should not review their own work. Do not issue a "
    "PASS or CONDITIONAL_PASS on that document alone: record in the Gate Inputs table who checked it "
    "independently (the `tech-lead` review by area, or the top-level session's own verification) and the "
    "commit that check covered. The check covers the document at the recorded commit; after it, only the "
    "`## RELEASE VERDICT` section and the `Release:` line under `## Gate Verdicts` may change. Any other "
    "change makes the check stale: report a blocker and have the same independent party re-run it on the new "
    "commit; never re-run it yourself. Your verdict is an input to the top-level session's verification before "
    "the merge and to the user's approval of the tag, not a substitute for either."
)
OLD_E2_LINE = (
    "| Release document, independent check (commit: [sha]) | PASS/CONDITIONAL_PASS/FAIL | "
    "[reviewer artifact, or the top-level session's recorded verification] |"
)
OLD_E3_LINE = (
    "- The release manager prepares `docs/releases/vX.Y.Z.md` (Core Workflow, Phase 5, step 2), so obtain the "
    "independent check of that document first (a `@tech-lead` review by area, or your own verification) and "
    "give the release manager its artifact and commit; `release-manager` § Release Gate Policy item 5 "
    "requires it."
)
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


def _files(knowledge: Path, mirrors: tuple[str, ...]) -> list[tuple[str, Path]]:
    files = [(str(knowledge.relative_to(knowledge_root().parent)), knowledge)]
    return files + [(rel, implementation_root() / rel) for rel in mirrors]


def _hunk_errors(lines: list[str], before: str, added: str, gap: int = 0) -> list[str]:
    """`added` occurs once, `gap` blank lines after the one `before` line."""
    errors = []
    if lines.count(before) != 1:
        errors.append(f"Before line must occur exactly once: {before[:60]!r}")
    if lines.count(added) != 1:
        errors.append(f"added line must occur exactly once: {added[:60]!r}")
    if errors:
        return errors
    i = lines.index(before)
    if lines[i + 1:i + 1 + gap] != [""] * gap or lines[i + 1 + gap] != added:
        errors.append(f"added line must follow its Before line ({gap} blank between): {added[:60]!r}")
    return errors


def _absent_errors(lines: list[str], *old: str) -> list[str]:
    text = "\n".join(lines)
    return [f"old text came back: {o[:60]!r}" for o in old if o in text]


def _e1_errors(lines: list[str]) -> list[str]:
    errors = _hunk_errors(lines, E1_BEFORE, E1_LINE)
    errors += _absent_errors(lines, E1_OLD_SENTENCE, OLD_E1_LINE)
    item5 = next((ln for ln in lines if ln.startswith("5. Independent check of what you authored.")), "")
    errors += [f"E1 clause missing: {name}" for name, clause in E1_CLAUSES.items() if clause not in item5]
    if "### Release Gate Policy" not in lines:
        return errors + ["§ Release Gate Policy is missing"]
    policy = _section(lines, "### Release Gate Policy")
    if E1_LINE not in policy:
        errors.append("item 5 must sit in § Release Gate Policy")
    items = [ln[:2] for ln in policy if ln[:2] in {f"{n}." for n in range(1, 10)}]
    if items != ["1.", "2.", "3.", "4.", "5."]:
        errors.append("Release Gate Policy must be items 1 to 5")
    return errors


def _e2_errors(lines: list[str]) -> list[str]:
    errors = _hunk_errors(lines, E2_BEFORE, E2_LINE) + _absent_errors(lines, OLD_E2_LINE)
    if "### Gate Inputs" in lines and E2_LINE not in _section(lines, "### Gate Inputs"):
        errors.append("the row must sit in the Gate Inputs table")
    return errors


def _e3_errors(lines: list[str]) -> list[str]:
    errors = _hunk_errors(lines, E3_BEFORE, E3_LINE) + _absent_errors(lines, OLD_E3_LINE)
    for name, clause in (("checker name", E3_CHECKER), ("scope", "prepares the release files")):
        if not any(clause in ln for ln in lines):
            errors.append(f"E3 clause missing: {name}")
    if not errors and lines[lines.index(E3_BEFORE) - 1] != "**RELEASE GATE** (before deployment):":
        errors.append("the pointer must sit under the Release gate")
    return errors


def _r4_errors(lines: list[str]) -> list[str]:
    errors = _hunk_errors(lines, R4_BEFORE, R4_LINE, gap=1)
    if errors:
        return errors
    if lines.count(R4_BLOCK_START) != 1 or lines.index(R4_BLOCK_START) > lines.index(R4_BEFORE):
        errors.append("Issued at commit must sit in the agent's RELEASE VERDICT block")
    return errors


def _r10_errors(lines: list[str]) -> list[str]:
    errors = _hunk_errors(lines, R10_BEFORE, R10_LINES[0]) + _hunk_errors(lines, R10_LINES[0], R10_LINES[1])
    if not errors and "## RELEASE VERDICT" not in lines[:lines.index(R10_BEFORE)]:
        errors.append("the R10 fields must sit in the ## RELEASE VERDICT block")
    return errors


def _no_merge_errors(lines: list[str]) -> list[str]:
    if lines.count(NO_MERGE_LINE) != 1:
        return ["the no-merge/no-tag/no-release constraint must occur exactly once, verbatim"]
    if "## Constraints" not in lines or NO_MERGE_LINE not in _section(lines, "## Constraints"):
        return ["the no-merge/no-tag/no-release constraint must sit in § Constraints"]
    return []


def _preflight_errors(lines: list[str]) -> list[str]:
    if lines.count(PREFLIGHT_LINE) != 1:
        return ["the tag preflight line must occur exactly once, verbatim"]
    i = lines.index(PREFLIGHT_LINE)
    if lines[i - 2:i] != [PREFLIGHT_HEADING, ""]:
        return ["the tag preflight line must open § Release Workflow Preflights"]
    return []


def _verdict_block_fields(lines: list[str]) -> list[str]:
    """Field names of the `## RELEASE VERDICT` block, up to its closing fence or the next heading."""
    start = lines.index("## RELEASE VERDICT")
    fields = []
    for line in lines[start + 1:]:
        if line.startswith("```") or line.startswith("## "):
            break
        if line.startswith("- **") and "**:" in line:
            fields.append(line[4:line.index("**:")])
    return fields


def _field_list_errors(rm_lines: list[str], pr_lines: list[str]) -> list[str]:
    """R1's closed list and the frozen fields partition the published verdict block's fields."""
    block = _verdict_block_fields(pr_lines)
    errors = [f"R1 lists a field the verdict block lacks: {f}" for f in E1_FIELDS if f not in block]
    unlisted = sorted(f for f in block if f not in E1_FIELDS)
    if unlisted != sorted(FROZEN_FIELDS):
        errors.append(f"fields outside R1's list must be the frozen ones, got {unlisted}")
    if not any(E1_MAY_CHANGE in ln for ln in rm_lines):
        errors.append("R1's closed field list is missing from release-manager.md")
    return errors


class _PinMixin:
    def assert_pins(self, files: list[tuple[str, Path]], *checkers) -> None:
        for where, path in files:
            with self.subTest(file=where):
                lines = _lines(path)
                errors = [e for check in checkers for e in check(lines)]
                self.assertEqual(errors, [], where)


class ReleaseManagerPins(_PinMixin, unittest.TestCase):
    def test_e1_policy_item_5(self):
        self.assert_pins(_files(RM_PATH, RM_MIRRORS), _e1_errors)

    def test_e2_gate_inputs_row(self):
        self.assert_pins(_files(RM_PATH, RM_MIRRORS), _e2_errors)

    def test_r4_issued_at_commit_in_verdict_block(self):
        self.assert_pins(_files(RM_PATH, RM_MIRRORS), _r4_errors)

    def test_sec_t693_08_no_merge_no_tag_constraint(self):
        self.assert_pins(_files(RM_PATH, RM_MIRRORS), _no_merge_errors)


class OrchestratorPins(_PinMixin, unittest.TestCase):
    def test_e3_release_gate_pointer(self):
        self.assert_pins(_files(OR_PATH, OR_MIRRORS), _e3_errors)

    def test_sec_t693_08_tag_preflight(self):
        self.assert_pins(_files(OR_PATH, OR_MIRRORS), _preflight_errors)


class PrepareReleasePins(_PinMixin, unittest.TestCase):
    def test_r10_fields_in_command_verdict_block(self):
        self.assert_pins(_files(PR_PATH, PR_MIRRORS), _r10_errors)

    def test_r10_fields_in_release_template(self):
        self.assert_pins([("docs/releases/_template.md", TPL_PATH)], _r10_errors)
        lines = _lines(TPL_PATH)
        i = lines.index(R10_LINES[1])
        self.assertEqual(lines[i + 1:i + 3], ["", "## Rollback Plan"], "R10b: before the blank and Rollback Plan")

    def test_r1_closed_field_list_matches_verdict_block(self):
        self.assertEqual(_field_list_errors(_lines(RM_PATH), _lines(PR_PATH)), [])
        self.assertEqual(_verdict_block_fields(_lines(TPL_PATH)), _verdict_block_fields(_lines(PR_PATH)),
                         "the template's verdict fields must match the command's")


class PinsMatchRulings(unittest.TestCase):
    def test_pinned_lines_are_the_ruled_text(self):
        ruled = RULINGS_PATH.read_text(encoding="utf-8").splitlines()
        for name, line in (("R1", E1_LINE), ("R2", E2_LINE), ("R3", E3_LINE), ("R4", R4_LINE),
                           ("R10a", R10_LINES[0]), ("R10b", R10_LINES[1])):
            with self.subTest(ruling=name):
                self.assertIn(line, ruled, f"{name}: pin differs from rulings-batch-d-v1.md")


def _manifest_paths(kind: str, base_name: str) -> set[str]:
    """`<outputDir>/<fileMap[kind].dir>/<base_name><ext>` for each platform manifest that maps `kind`."""
    paths = set()
    for manifest in sorted(PLATFORMS.glob("*.json")):
        if manifest.name.startswith("_"):
            continue
        data = json.loads(manifest.read_text(encoding="utf-8"))
        file_map = data.get("fileMap", {}).get(kind)
        if file_map:
            paths.add(f"{data['outputDir']}/{file_map['dir']}/{base_name}{file_map['ext']}")
    return paths


class ProjectionList(unittest.TestCase):
    """SEC-T693-08 / T721 item c: the mirror lists are what `sync.mjs` generates (`fileMap`)."""

    def test_agent_mirrors_match_manifests(self):
        self.assertEqual(set(RM_MIRRORS), _manifest_paths("agents", "release-manager"))
        self.assertEqual(set(OR_MIRRORS), _manifest_paths("agents", "orchestrator"))

    def test_command_mirrors_match_manifests(self):
        self.assertEqual(set(PR_MIRRORS), _manifest_paths("commands", "prepare-release"))

    def test_every_mirror_exists(self):
        for rel in RM_MIRRORS + OR_MIRRORS + PR_MIRRORS:
            with self.subTest(file=rel):
                self.assertTrue((implementation_root() / rel).is_file())


# label -> (source, text now in it, text the mutation puts there, checker, expected error fragment)
MUTATIONS = {
    "E1 restored": (RM_PATH, E1_LINE, OLD_E1_LINE, _e1_errors, "added line must occur exactly once"),
    "E1 FAIL effect dropped": (RM_PATH, E1_FAIL + " ", "", _e1_errors, "E1 clause missing: FAIL effect"),
    "E1 cap loosened": (RM_PATH, "at most CONDITIONAL_PASS", "at most PASS", _e1_errors,
                        "E1 clause missing: CONDITIONAL_PASS cap"),
    "E1 checker renamed": (RM_PATH, "the orchestrator's recorded verification, ", "", _e1_errors,
                           "E1 clause missing: checker name"),
    "E1 scope narrowed": (RM_PATH, "the release files you prepare", "the release document you prepare",
                          _e1_errors, "E1 clause missing: scope (the release files)"),
    "E1 field list widened": (RM_PATH, "the values of Status,", "the values of Version, Status,", _e1_errors,
                              "E1 clause missing: closed field list"),
    "E2 restored": (RM_PATH, E2_LINE, OLD_E2_LINE, _e2_errors, "added line must occur exactly once"),
    "E3 restored": (OR_PATH, E3_LINE, OLD_E3_LINE, _e3_errors, "E3 clause missing: checker name"),
    "R4 removed": (RM_PATH, R4_LINE + "\n\n", "", _r4_errors, "added line must occur exactly once"),
    "R10 removed (command)": (PR_PATH, R10_LINES[0] + "\n", "", _r10_errors, "added line must occur"),
    "R10 removed (template)": (TPL_PATH, R10_LINES[1] + "\n", "", _r10_errors, "added line must occur"),
    "no-merge weakened": (RM_PATH, "create or push a tag, or ", "", _no_merge_errors, "exactly once"),
    "preflight weakened": (OR_PATH, ", with the user's approval):", "):", _preflight_errors, "exactly once"),
}


class MutationProof(unittest.TestCase):
    """T721 item d: the pins fail on a temporary copy that restores the old text or breaks a clause."""

    def test_pins_fail_on_mutated_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            for n, (label, (source, now, mutated, check, expected)) in enumerate(MUTATIONS.items()):
                with self.subTest(mutation=label):
                    text = source.read_text(encoding="utf-8")
                    self.assertIn(now, text, f"{label}: the current text to mutate is missing")
                    copy = Path(tmp) / f"mutation-{n}.md"
                    copy.write_text(text.replace(now, mutated, 1), encoding="utf-8")
                    errors = check(_lines(copy))
                    self.assertTrue(any(expected in e for e in errors), f"{label}: pins passed: {errors}")
                    self.assertEqual(check(_lines(source)), [], f"{label}: the unmutated source must pass")

    def test_field_list_check_fails_on_widened_block(self):
        pr = _lines(PR_PATH)
        i = pr.index(R10_LINES[1])
        widened = pr[:i + 1] + ["- **Signed off by**: <name>"] + pr[i + 1:]
        errors = _field_list_errors(_lines(RM_PATH), widened)
        self.assertTrue(any("frozen ones" in e for e in errors), errors)


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
