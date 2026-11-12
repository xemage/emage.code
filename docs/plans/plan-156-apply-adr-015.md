# plan-156 — Apply ADR-015 to the knowledge sources

**Created:** 2026-11-12
**Based on:** `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md` (Accepted; § Files and lines, rows C1 to C4, and the checks listed under them); `docs/plans/plan-155-v11-release-decisions.md` (§ Outcome, "Not done here"); `docs/decisions/ADR-012-medium-acceptance-record.md` (rows B1 and B3). The user's word of 2026-11-12, verbatim: "Continue", in answer to the orchestrator's "Say "continue" and I'll start with item 1", where item 1 read: "Apply ADR-015 to the two knowledge sources and their test pins, with a security review. This will declare root drift, and the root refresh needs your approval."
**Scopes:** `T801`, `T802`.

## Goal

ADR-015 is accepted but not applied: the skill and the release-manager verdict block still state the accepted-MEDIUM rule as ADR-012 left it. This plan makes the two source edits ADR-015 names, pins them by test, regenerates the mirrors and the registry, and has the result reviewed. SEC-T762-04 and TL-T761-10 are fixed when this merges. It is not a release, a tag or a root refresh; the root drift it causes is declared, and the refresh needs the user's approval at that moment.

## Facts (the orchestrator's record)

- The orchestrator ran the search ADR-015 asks for, on develop `2731ab3a`: `grep -rn -l --exclude-dir=held-out -E 'remediation plan \(owner, fix, deadline\)|passes before the release ships|counts as moved later'` over `implementation/knowledge`, `docs/wiki`, `tests/functional` and `tests/golden`. Hits outside ADR-015's table: `implementation/knowledge/commands/code-review.md`, `commands/security-audit.md`, `skills/receiving-code-review/SKILL.md`, `skills/code-review/SKILL.md`, `agents/tech-lead.md`, and the fixture copy `tests/golden/open/validate-workflow-gate-verdict-sources/fixture/implementation/knowledge/skills/validation-gates/SKILL.md`. T801 reads each hit and says whether it is a pointer or a copy of the rule.
- That fixture copy already differs from the source (`cmp` exit 1), so it is a frozen fixture and is not edited. `tests/golden/` is a protected path; T801 does not touch it.
- `docs/releases/_template.md` has no `risk_accepted_by` line, so it does not copy the Conditions line.
- `tests/functional/test_release_self_review_text.py:169-207` pins B1 clause by clause and B3 verbatim (`B3_LINE`).

## Task Decomposition

1. **T801** (backend-developer): apply C1 and C2, update and add the text pins, regenerate. Brief: `docs/tasks/task-T801.md`.
2. **T802** (security-engineer), after T801: review the diff against ADR-015. Brief written when T801 reports. Read-only; the orchestrator commits the review text.
3. **The orchestrator:** verifies (gates, the full suite in a clean worktree, the pipeline), opens the merge request and merges it pinned. Root drift is declared in the merge request; the refresh is asked of the user afterwards.

## Outcome

- **T801** done (`23de85b9` sources and pins, `9b9ab6d1` mirrors, registry and drift baseline). C1 is in `implementation/knowledge/skills/validation-gates/SKILL.md:70` and C2 in `implementation/knowledge/agents/release-manager.md:183`. The orchestrator compared both by word diff with ADR-015 § Files and lines: verbatim. `tests/functional/test_release_self_review_text.py` pins every element (`C1_CLAUSES`, `C2_CLAUSES`, `B3_LINE`, and `B3_LINE_ADR_012` for the unchanged ADR-012 text); its mutation table grew from 44 to 73 entries (19 for C1, 10 for C2). The other search hits are pointers or merge-gate rules and were not edited; the golden fixture copy was not touched.
- **T802** done: `docs/artifacts/security-review-t802-adr-015-apply-v1.md`, verdict PASS, four LOW findings. The role has no write tool, so the orchestrator committed the returned text unchanged. The review's note that "44 to 73" did not match its count is a misreading: 73 is the new total and its 29 entries for T801 are the difference.
- **Statuses for register v16:**
  - SEC-T762-04, TL-T761-10: fixed by this plan.
  - SEC-T802-01 (O3 in short form), SEC-T802-02 ("It covers" now follows the passed-deadline sentence; the sentence is unpinned), SEC-T802-04 (the gate-input line at `validation-gates/SKILL.md:120` lacks the old plan's deadline): LOW, tracked; wording edits that keep the rule.
  - SEC-T802-03 (the Security Engineer's confirmation stands outside "only when"; no text says an acceptance fails without it): LOW, tracked. Its proposed wording makes O4 a fourth validity condition, which changes the rule and needs the user's word.
- **Root drift declared**, 7 paths in `tests/_baselines/root-install-drift.json`: the installed copies of the skill (`.claude`, `.cline`, `.github`, `.opencode`) and of the release-manager agent (`.claude`, `.github`, `.opencode`). The refresh needs the user's approval.
- **Disclosures:** T801 used about 111k tokens against 120k. T802 used about 126k against 60k and was interrupted once by the usage limit; the user said "Resume" and the same agent continued. T802 did not open ADR-011, plan-155, plan-156 or the mirrors, and read only one wiki line; its artifact lists this.
