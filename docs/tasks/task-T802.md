# T802 — Security review of T801 against ADR-015

**ID:** T802
**Owner:** security-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** T801
**Affects:** —
**Created:** 2026-11-12
**Completed:** 2026-11-12
**Based on:**
- `docs/plans/plan-156-apply-adr-015.md` (task T802)
- `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md`

## 1. What and why

Review T801's diff: does the text in the skill and in the release-manager verdict block state ADR-015's two rules and O1 to O7 as ruled, no more and no less; do the pins hold each element; did anything weaken ADR-011 or ADR-012 (one release only, only the user accepts, no agent carries an acceptance over).

## 2. Output

The text of `docs/artifacts/security-review-t802-adr-015-apply-v1.md`, returned to the orchestrator, who commits it. Verdict `PASS` | `CONDITIONAL_PASS` | `FAIL`; findings graded `SECURITY:*`.

## 3. Constraints

Read-only; no source is modified. The orchestrator fills in the commit range and the evidence when T801 reports. Never read secret paths or `tests/golden/held-out/`.

## 4. Acceptance criteria

Each finding has a file and line; each claim not verified is marked **(unverified)**.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).

## 6. Commit range and evidence (filled in by the orchestrator, 2026-11-12)

- Range: `218f86b2..9b9ab6d1` on `agent/backend-developer/T801` (worktree `../worktrees/agent-backend-developer-T801`): `23de85b9` (sources and pins), `9b9ab6d1` (mirrors, registry, drift baseline).
- Sources: `implementation/knowledge/skills/validation-gates/SKILL.md:70` (C1), `implementation/knowledge/agents/release-manager.md:183` (C2). The orchestrator compared both by word diff with ADR-015 § Files and lines rows C1 and C2: verbatim.
- Pins: `tests/functional/test_release_self_review_text.py` (`C1_CLAUSES`, `C2_CLAUSES`, `B3_LINE`, `B3_LINE_ADR_012`, `test_c1_and_c2_are_the_text_of_adr_015`, `MUTATIONS` 44 to 73); 26 tests OK.
- Gates at `9b9ab6d1`, run by the orchestrator: `validate-tasks`, link integrity, team health, scorecard, `sync.mjs --check`, `generate-registry.py --check` all exit 0; `--print-drift` prints exactly the 7 declared paths. No path under `tests/golden/` and no top-level platform folder is in the diff.
- T801 asks the reviewer to check one reading: `B3_LINE_ADR_012` (the Conditions line without the two C2 insertions) is what the test now compares with ADR-012, because ADR-012 is "superseded in part by ADR-015" and its own text was not edited.
- T801's classification of other hits as pointers, not copies of the rule (none edited): `tech-lead.md:85,100,114`, `commands/code-review.md:51,53`, `commands/security-audit.md:45,69`, `receiving-code-review/SKILL.md:86`, `code-review/SKILL.md:155`, `validation-gates/SKILL.md:55`, `docs/wiki/severity-and-grade-scales.md:34`.
