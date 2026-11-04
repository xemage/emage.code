# plan-133 — LOW batch H: release-gate text and ADR-011 follow-ups

**Created:** 2026-11-04
**Based on:**
- `docs/artifacts/tracked-debt-register-v6.md` § 5, batch H (11 ids).
- `docs/artifacts/security-review-t718-t720-batch-d-v1.md` § 3, which has the findings and the reviewer's fixes.
- `docs/decisions/ADR-011-user-accepted-medium-at-release.md`.
- The user's answers of 2026-11-04, verbatim:
  - "H go"
  - SEC-T720-02 and -03: "Add it as ADR-012 (Recommended)"
  - The parked golden remarks: "Grant it for batch H"
  - The root refresh: "Yes, refresh in this MR (Recommended)"

**Scopes:** `T734`, `T735`, `T736`.

## Goal

The next release must re-accept four Medium findings under ADR-011, and it ships T725's change to `/prepare-release`. Close the text gaps that would shape that release before it starts.

## The golden grant was not needed

The user granted a protected-path edit for P14, P15 and the remarks of CT rows T539 and T565. The orchestrator re-read the open cases before dispatching anything, and all four are already fixed. Registers v1 to v6 and plan-127 carried them as parked without re-reading them.

| Remark | What it said | State now | Fixed by |
|---|---|---|---|
| T539 (P13) | The handoff fixture embeds the pre-T529 schema | The fixture's `schema-v1.json` is byte-identical to the live one | T560, `a6be07c6` |
| P14 | Consolidate-memory Promote rows name "Never use" targets; the `expect.py` docstring says step 4 has no declared artifact | The rows name `docs/` targets, and the docstring describes the T549 clause | T560, `a6be07c6` |
| P15 | The skillify `known_failing_reason` carries a stale path | The key no longer exists; the case is `expected_pass` | T560, then T668 |
| T565 | The new-poc `expect.py` docstring calls P11 parked | It reads "P11 (the plan path) is resolved" | T583, `8dec82f3` |

So this plan edits nothing under `tests/golden/`, and baseline v22 stands. The T547 remark that v5 and v6 mark **(unverified)** is the list of four findings T547 parked in plan-084, which is P9 to P12, and those are accounted for.

## Task Decomposition

1. **T734** (orchestrator): write `docs/decisions/ADR-012-medium-acceptance-record.md`, Accepted by the user's answer above, replacing rows A1, A8 and A12 of ADR-011 in part. It holds the exact text T735 applies. Add the replacement link to ADR-011's header, which `AGENTS.md` § Decision Log requires.
2. **T735** (technical-writer): the knowledge edits below, under `implementation/knowledge/` only.
   - **SEC-T720-02 and SEC-T720-03:** rows B1 to B3 of ADR-012, exactly.
   - **SEC-T720-04**, `agents/release-manager.md:46`. Replace "which is its opening paragraph and what you add below the field list (Gate Inputs, Justification, Conditions, Blockers, and the user's decisions as recorded)." with "which is its opening paragraph and, below the field list, only Gate Inputs, Justification, Conditions, Blockers, and the user's decisions as recorded. No other text may be added after the check."
   - **SEC-T720-05**, `agents/orchestrator.md:262`. Replace "after the Release Gate verdict is PASS or CONDITIONAL_PASS" with "after the Release Gate verdict is PASS, or CONDITIONAL_PASS with the explicit risk acceptance `release-manager` § Release Gate Policy item 2 requires recorded in the verdict".
   - **SEC-T720-06 and TD-T720-01**, `skills/release-workflow/SKILL.md`.
     - Line 117: "- [ ] No `Critical` or `High` bugs (`/bug-report` § Severity) open for this release".
     - Line 171: "├── Confirm the issue is eligible: graded critical or high on its own scale (next line), or, whatever its grade, a breach of an Immutable Security Constraint or a required security control omitted, removed, disabled or weakened (`security-guidelines.md`)".
     - Line 233: "- Hotfixes are for issues graded critical or high on their own scale (§ 5, step 1), and for a breach of an Immutable Security Constraint or a required security control omitted, removed, disabled or weakened, whatever its grade. Other medium or low issues wait for the next regular release."
   - **SEC-T720-07**, `skills/validation-gates/SKILL.md:70`. The opening sentence becomes "**Security findings never qualify for CONDITIONAL_PASS, except one graded medium as stated below.**"
     - Then check that sentence against what the paragraph goes on to say, and report any mismatch. `agents/tech-lead.md:100` also holds the phrase: report what it says, and change it only if it contradicts the rule.
   - **SEC-T720-08**, two places. `agents/release-manager.md:46`: after "name which one) and the commit that check covered." add "The checker has not authored or edited the release files at the checked commit." `agents/orchestrator.md:218`: after "named as the orchestrator's, or as the top-level session's when you run as the top-level session)" add ", by a checker who has not authored or edited those files at the checked commit,".
   - **TD-T725-01:** knowledge that ships to targets must not send a target project to `/prepare-release`, which targets no longer receive.
     - `commands/validate-tasks.md:16`: "Before a release".
     - `commands/validate-workflow.md:20` and `skills/testing-strategy/SKILL.md:168`: keep the name, marked `prepare-release` (authoring repository only).
     - `skills/release-workflow/SKILL.md:132`: name the command as the authoring repository's.
     - `agents/release-manager.md` is not on the debt item's list, but it also names the command. Report each use, and reword only one that assumes a target project has it.
   - **TD-T671-legacy, P10**, `skills/plan-approve-execute/SKILL.md`, § Handling Responses. Add below the table: "`/new-project` records the same three answers as `APPROVED` (Approve), `APPROVED_WITH_CHANGES` (Revise: apply the changes and present the plan again) and `REJECTED` (Reject). No answer other than Approve or `APPROVED` starts execution." `commands/new-project.md` does not change (ADR-007).
   - **SEC-T693-07:** no edit, by ruling (plan-127).
   - *Acceptance:* each edit is made as written, or reported with the reason. No file outside `implementation/knowledge/` changes.
3. **T736** (devops-engineer), after T735:
   - Re-pin `tests/functional/test_release_self_review_text.py` to the new text, and add a pin for each of ADR-012's B1 and B3. A pin must fail if the clause is removed.
   - Regenerate: `node implementation/scripts/sync.mjs --root implementation`, `python3 implementation/scripts/generate-registry.py`.
   - Declare the root drift in `tests/_baselines/root-install-drift.json`. Do not refresh the root; the orchestrator does that.
   - *Acceptance:* all gates and the full suite pass, including `scripts/scorecard.py --check`. If a golden case fails on the new text, stop and report it: the user's grant does not cover it.

T735 then T736, and a Security Engineer reviews the batch. The orchestrator then runs the root refresh, which the user approved for this merge request.

## Changes after the first security review

The review gave CONDITIONAL_PASS. The user's answers of 2026-11-04, verbatim: "Record it, no new question (Recommended)"; "Add the sentence (Recommended)"; "Fix the three now (Recommended)". They change the text above as follows, and these sentences are the final text:

- **SEC-T735-01 and SEC-T735-02:** ADR-012 § Decision and rows B1 to B3, as now written there.
- **SEC-T735-03**, `agents/release-manager.md:46`: "The checker has not authored or edited the release files for this release; if the checker has, the row counts as missing." The stale rule adds "or another eligible checker if that party edited the files". `agents/orchestrator.md:218`: ", by a checker who has not authored or edited those files for this release,".
- **SEC-T735-04**, `skills/release-workflow/SKILL.md`: the issue must be present in the released version, `@security-engineer` confirms a breach or a weakened control, a fix with design impact does not take the fast track, and the Security gate is always required for an issue eligible as a breach or a weakened control.
- **SEC-T735-05**, `docs/releases/_template.md`: a sentence below the fields points to the Conditions format of the `release-manager` verdict block. `commands/prepare-release.md` does not change (ADR-008).
- **Added by the orchestrator in T735, beyond item 2 above (SEC-T736-02):** the closed list in `agents/release-manager.md:46` also names "Changelog Preview (a summary of the checked changelog, nothing new)", because that block requires the section, and the hotfix intro and severity lines of `release-workflow/SKILL.md:167, 172` were aligned with the wider eligibility.

## Not changed in this plan

- **SEC-T693-07** stays tracked: the independent check is a duty in the role text, not an enforced control. SEC-T720-08 narrows it and does not close it.
- **`tests/golden/**`, `scripts/scorecard.py` and the evaluator baseline.**
- **The two batch N fixes** (SEC-T731-07, SEC-T731-09(a)). The user's answer was "H go".

## Constraints

- Subagents never merge, tag or release. The orchestrator merges on `mergeable` with a green pipeline and a pinned sha.
- Never open `tests/golden/held-out/`. Read no `.env*` or credential file.

## Outcome (2026-11-04)

- **Tasks.** T734 to T736 are done.
- **User decisions** (AskUserQuestion, verbatim): listed under Based on and in § Changes after the first security review.
- **Batch-H ids.**
  - Closed: SEC-T720-02 to -08; TD-T720-01; TD-T725-01; TD-T671-legacy, whose last item P10 is closed here and whose four parked remarks were already fixed (§ The golden grant was not needed).
  - Unchanged: SEC-T693-07. SEC-T720-08 and SEC-T735-03 narrow it and do not close it.
- **The golden grant was given and not used.** Nothing under `tests/golden/` changed, and baseline v22 stands.
- **Security review.** `docs/artifacts/security-review-t734-t736-batch-h-v1.md` gives PASS. The first review was CONDITIONAL_PASS on one MEDIUM, SEC-T735-01, which was the orchestrator's own ADR text and which the user's answer resolved. Of 10 LOW findings, 5 are resolved and 5 are tracked: SEC-T735-06, -07, -08, -09 and the rest of SEC-T736-01. **SEC-T735-08 and -09 are due before the next release.**
- **New for the next release document:**
  - An acceptance names the release, records the plan as shown, and needs a deadline still ahead when the user is asked (SEC-T735-08).
  - The Conditions block has `grade=` and `release=` slots.
  - Remove the template's pointer sentence before the independent check, or leave it (SEC-T735-09).
  - The checker must not have authored or edited the release files for this release, so `@tech-lead` is the practical default.
- **Root refresh** (the user: "Yes, refresh in this MR (Recommended)"). The 49 changed paths equal the 49 declared, and the drift list is empty.
- **Token use against budget** (the harness's counts, which include context):

  | Task | Used | Budget |
  |---|---|---|
  | T734 | the orchestrator's own | - |
  | T735 | about 73k | 40k |
  | T736 | about 138k | 50k, plus 40k for the follow-up |
  | Security review | about 192k | 60k, plus 30k for the re-check |
