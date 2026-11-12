# plan-157 — The Security Engineer's confirmation as a fourth validity condition

**Created:** 2026-11-12
**Based on:** `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md` (Accepted; § Decision Rule 1, O4; § Files and lines rows C1 and C2); `docs/artifacts/security-review-t802-adr-015-apply-v1.md` (findings SEC-T802-01 to SEC-T802-04); `docs/plans/plan-156-apply-adr-015.md` (§ Outcome).
**Scopes:** `T804`, `T805`, `T806`.

## User decision (2026-11-12, verbatim)

The orchestrator wrote, at the end of plan-156: "One decision is still open with you: whether the Security Engineer's confirmation should become a fourth validity condition for a "none possible in the harness" plan (SEC-T802-03). It is tracked as LOW debt until you decide." Earlier in the same session it had described the finding as: "Today the text requires the Security Engineer's confirmation that no harness fix exists, but does not say an acceptance fails without it. Making it a fourth validity condition changes the rule you accepted, so I have left it as tracked debt until you decide."

The user's answer, verbatim:

> confirmation should become a fourth validity condition

**The orchestrator's reading:** the user decided SEC-T802-03: under ADR-015 Rule 1, the Security Engineer's review confirming that no harness fix exists becomes a fourth condition of a valid "none possible in the harness" plan, beside the three that ADR-015 names; without it the plan is not valid and the acceptance does not hold. The user did not say anything about SEC-T802-01, -02 or -04.

## User decisions on ADR-016 (2026-11-12, AskUserQuestion; verbatim)

**Question 1 as shown:** "ADR-016 is drafted as Proposed. It records your ruling: a "none possible in the harness" plan is valid only when four conditions hold (names an outside closer, says plainly no harness fix exists, sets a review date, and the Security Engineer's review confirms no harness fix exists); a plan lacking any one is not valid and the acceptance does not hold. Your words left four details open (O-A to O-D); the architect recommends an answer for each. Accept ADR-016?"

- The user's answer: "Accept with all recommendations (Recommended)"
- The option's description as shown: "O-A: citing the review in the question to you stays a separate duty, not part of the condition. O-B: the review must exist before you are asked. O-C: at a later release an earlier review does not serve unseen; a new review or a dated statement that it still holds. O-D: applies to every verdict issued after acceptance, so SEC-T660-01 and SEC-T665-01 need a confirming review on record before the v11.0.0 gate."
- The other options were "Accept, but citing is part of the condition", "Accept the fourth condition only" and "I want to read it first".

**Question 2 as shown:** "Three wording-only fixes sit in the same paragraph (LOW findings from the T802 review; they keep the rule). W1 (SEC-T802-01): the review-date outcome says what it covers ("whether a harness fix now exists and whether the outside closer is still right; a fix that now exists is a changed fix"). W2 (SEC-T802-02): "It covers only the release" becomes "An acceptance covers only the release". W3 (SEC-T802-04): the gate-input line gains "and its plan's deadline". Which should go into the same change?"

- The user's answer (multiple choice): "W1 (SEC-T802-01),W2 (SEC-T802-02),W3 (SEC-T802-04)"
- The other option was "None" ("Leave all three as tracked LOW debt.").

## Goal

Record the decision, apply it, and pin it. ADR-015 is accepted and immutable, and this changes its Rule 1, so it needs a new ADR that supersedes ADR-015 in part; only the user accepts it. It is not a release, a tag or a root refresh; the root drift it causes is declared, and the refresh needs the user's approval at that moment.

## Scope choice (the orchestrator's, disclosed)

SEC-T802-01, -02 and -04 are LOW wording gaps in the same paragraph and the same test file. ADR-015 allows a wording change that keeps the rule, so they need no ADR. The orchestrator includes them in T805, because a separate change later would edit the same line, the same pins and cause a second root drift. The architect lists their wording in the ADR's follow-up table as "wording only, not part of the decision", so the user sees the exact text before accepting, and can strike them.

## Task Decomposition

1. **T804** (solution-architect): ADR-016, Proposed, superseding ADR-015 in part (Rule 1, O4, row C1; row C2 only if its text must change). Brief: `docs/tasks/task-T804.md`. The orchestrator commits; the user accepts or changes it.
2. **T805** (backend-developer), after the user accepts ADR-016: apply its rows to `implementation/knowledge/skills/validation-gates/SKILL.md` (and `release-manager.md` if a row says so), update the pins in `tests/functional/test_release_self_review_text.py`, regenerate mirrors and registry, declare root drift. Brief written when ADR-016 is accepted.
3. **T806** (security-engineer), after T805: read-only review; the orchestrator commits the text. Brief written when T805 reports.
4. **The orchestrator:** verifies (gates, the full suite in a clean worktree, the pipeline), merges pinned. The root refresh is asked of the user afterwards.

## Outcome

**Done on 2026-11-12.** The Security Engineer's confirming review is now a fourth validity condition of a "none possible in the harness" plan, in the one definition (`implementation/knowledge/skills/validation-gates/SKILL.md`, § Verdict Rules), and the three wording fixes the user included are applied.

- **T804** (solution-architect): `docs/decisions/ADR-016-security-engineer-confirmation-as-validity-condition.md`, accepted by the user (§ User decisions on ADR-016). ADR-015 carries a header note that ADR-016 supersedes it in part.
- **T805** (backend-developer), commits `97e1c0b4` and `946a2a9a`: rows D1, D2, W1 and W2 in `SKILL.md:70` and W3 in `SKILL.md:120`, each word for word from ADR-016; `release-manager.md:183` unchanged (row D3); pins in `tests/functional/test_release_self_review_text.py` (`ADR_016_CLAUSES`, 18 entries; `MUTATIONS` 73 to 95; 27 to 30 tests); mirrors and registry regenerated.
- **T806** (security-engineer): `docs/artifacts/security-review-t806-adr-016-apply-v1.md`, **PASS**. Three new LOW findings, tracked as debt for register v16: SEC-T806-01 (D2 does not itself say the dated statement comes before the user is asked; it follows only from D1), SEC-T806-02 (the release document's `mitigation` slot does not carry the review's date or the dated statement), SEC-T806-03 (the "An acceptance never covers…" sentence has no pin in this test file).

**Status of findings, for register v16:** SEC-T802-01, -02, -03 and -04 fixed by this plan. SEC-T806-01 to -03 new, LOW, tracked.

**The orchestrator's own verification:** D1, D2, W1, W2 and W3 each occur exactly once in the skill source and once in ADR-016; the word diff of the skill source shows only those five changes; the gates (validate-tasks, link integrity, team health, scorecard, sync `--check`, registry `--check`) exit 0; the full suite in a clean worktree and the pipeline at the merged commit are recorded in the merge request.

**Root drift declared, root not refreshed:** the four installed copies of `validation-gates/SKILL.md` (`.claude/`, `.cline/`, `.github/`, `.opencode/`). The refresh is a separate step that needs the user's approval at that moment.

**For the v11.0.0 release plan (O-D; the note in the T806 review):** SEC-T660-01 and SEC-T665-01 need a confirming Security Engineer review on record before the user is asked. Whether one existed before the question of 2026-11-12 is not yet checked; if none did, the plan commissions the review first and puts the question to the user again afterwards. No agent treats the earlier answer as carried over. T806 is not that review.

**Disclosures:**
- Token budgets: T804 about 117k against 80k (the architect's first revision was reported as done but its writes had been refused; the orchestrator found a clean worktree and sent it back). T805 about 107k against 120k. T806 about 111k against 60k (the 953-line pin file was read in full).
- T806 did not open the mirrors, the registry, the drift baseline, ADR-011, ADR-012 or this plan; those points rest on the orchestrator's gate results and are listed in the review.
- The pin for the superseded ADR-015 sentence in ADR-016 checks presence, not a count of one, because ADR-016 quotes it twice (T806: sound).
- At `97e1c0b4` alone the pin test fails, because the mirrors are regenerated in the next commit; the merge is squashed.
