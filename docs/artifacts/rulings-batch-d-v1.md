# Artifact: rulings-batch-d-v1.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/tasks/task-T718.md`; `docs/plans/plan-127-batch-d-knowledge-and-rulings.md` (task T718; the user's "D go", 2026-11-01); `docs/checkpoints/checkpoint-040-release-v9.0.0.md` § 3; `docs/artifacts/tracked-debt-register-v4.md` (batch D rows), `-v3.md` § 3.6, `-v2.md` § 3.15; `docs/artifacts/security-review-t693-release-self-review-v1.md` (findings table and Re-check). Requirements and architecture artifacts: none apply (a ruling on knowledge text). Decision IDs referenced: ADR-007, ADR-008, ADR-011 (all Accepted). ADR-011 decides TD-T713-01 only (section 3); no ruling in sections 1 and 2 relies on it.

## Metadata

- **Producer**: solution-architect, task T718. **Date**: 2026-11-01.
- **Tree read**: worktree `agent-solution-architect-T718`. I had no shell, so I do not know the commit. Every line number below was read in that worktree with the file tool.
- **Not opened**: `tests/golden/` (held-out or not), any `.env*` or credential file, the user's `.claude/settings*.json` and `.vscode/mcp.json`.
- **Could not open**: ADR-010 (I had no directory listing, and its file name is not in the brief). I followed the form of ADR-008 and `docs/decisions/_template.md` instead.
- **No search tool**: I could only read files I named. Where a ruling says "every place", it means every place in the files I read; the orchestrator should grep before T720 (section 4).
- **Maturity**: no ruling relies on a `maturity:` value (ADR-008 P4).
- **Scope**: this artifact writes no knowledge file. T720 applies the rulings; T721 updates the pins.
- **Revision before merge** (2026-11-01, on the orchestrator's instruction, on top of commit `210057cf`; v1 was not yet merged): the user decided on 2026-11-01 (AskUserQuestion, option labels verbatim): "(a) Time-bound acceptance (Recommended)", "Until the next release" and "O1: both fields (Recommended)". Option O1 is now ruling R10 (section 1.5), R1 lists the two new fields, and sections 0, 3, 4 and 5 record the decisions. No other ruling changed.

## 0. Summary

| Id | Ruling in one line | File:line replaced | Authority |
|---|---|---|---|
| SEC-T693-02 | A missing, stale or FAIL independent-check row makes the release verdict FAIL; a CONDITIONAL_PASS row caps it at CONDITIONAL_PASS. | `release-manager.md:46` (R1); `validation-gates/SKILL.md:118` (R5, insert) | Same-file coherence (ADR-008 § Scope); ADR-008 Step A for R5 |
| SEC-T693-03 | One name for the checker: the `tech-lead` review by area, or the orchestrator's or the top-level session's recorded verification, named. That check does not replace the top-level session's verification before the merge. | `release-manager.md:46` (R1), `:175` (R2); `orchestrator.md:218` (R3) | ADR-008 Step A (state the relationship) |
| SEC-T693-04 | Knowledge part: the agent's verdict block records `Issued at commit`. Command part: the published verdict records `Issued at commit` and `Independent check`. | `release-manager.md:165` (R4, insert); `prepare-release.md:58` and `docs/releases/_template.md:86` (R10, insert) | ADR-008 Step A, D4 (R4); the user's decision under ADR-007, "O1: both fields (Recommended)" (R10) |
| SEC-T693-05 | "The document" becomes "the release files": the version files, the changelog and `docs/releases/vX.Y.Z.md`. | `release-manager.md:46` (R1); `orchestrator.md:218` (R3) | Same-file coherence; ADR-008 Step A |
| SEC-T693-06 | Phase 5: run the Release Gate (step 3) before production deployment (step 4). | `orchestrator.md:261-262` (R6) | Same-file coherence (`orchestrator.md:216`); ADR-008 Step A fails against `validation-gates/SKILL.md:29`, so the agent is amended |
| SEC-T693-09 | List what may change after the check: the `Release:` line, six named verdict fields and the verdict text; Version, the three counts and the rest stay as checked. | `release-manager.md:46` (R1) | Same-file coherence; tightens the user's "fix 01" text and loosens nothing |
| TD-T687-02 | `qa-engineer` bug priority is `P0`, `P1`, `P2`, the task priority of `AGENTS.md`. | `qa-engineer.md:60` (R7) | ADR-008 Step B (P1): `AGENTS.md` § Task Protocol |
| TD-T687-03 | The hotfix severity names its scale: S2 for a bug, S5 for a security finding. | `release-workflow/SKILL.md:171`, `:232` (R8) | ADR-008 Step A (state the relationship) |
| TD-T687-04 | `security-engineer` report: S5 and V1 written as tier 1 and its own other sections write them. | `security-engineer.md:96-98`, `:103` (R9) | ADR-008 Step B (P1): `AGENTS.md` § Validation Gates, `security-guidelines.md:181`; same-file coherence |
| TD-T713-01 | Decided by the user through ADR-011 (Accepted 2026-11-01): option (a), an acceptance covers only the release it was given for. Not ruled here. | ADR-011 § Files, rows A1-A13 | The user's decision (ADR-011; ADR-008 P5) |

All paths are under `implementation/knowledge/` (`agents/`, `skills/`, `commands/`).

## 1. Release-gate wording (SEC-T693-02 to -06, -09)

SEC-T693-02, -03, -05 and -09 all fall on one line, `release-manager.md:46` (Release Gate Policy item 5). R1 gives that line once, in full, so that T720 makes one edit.

### R1. `implementation/knowledge/agents/release-manager.md:46` (SEC-T693-02, -03, -05, -09)

**Replace the whole line with:**

```text
5. Independent check of what you authored. This verdict aggregates the verdicts of other executors; the release files you prepare (the version files, the changelog, and `docs/releases/vX.Y.Z.md` with its release notes and rollback plan) are your own work, and `validation-gates` § Guidelines says gate executors should not review their own work. Do not issue a PASS or CONDITIONAL_PASS on those files alone: record in the Gate Inputs table who checked them independently (the `tech-lead` review by area, the orchestrator's recorded verification, or the top-level session's recorded verification; name which one) and the commit that check covered. If that row is missing or stale, or its status is FAIL, your verdict is FAIL; if its status is CONDITIONAL_PASS, your verdict is at most CONDITIONAL_PASS and the check's conditions are conditions of your verdict (item 2). The check covers the release files at the recorded commit. After it, only these may change: the `Release:` line under `## Gate Verdicts`; in `## RELEASE VERDICT`, the values of Status, Open blockers, Quality gates passed, Quality gates failed, Blocker IDs, Timestamp, Issued at commit and Independent check; and the verdict text of that section, which is its opening paragraph and what you add below the field list (Gate Inputs, Justification, Conditions, Blockers, and the user's decisions as recorded). Any other change, including Version or the Features, Fixes or Breaking changes counts, makes the check stale: report a blocker and have the same independent party re-run it on the new commit; never re-run it yourself. Your verdict is an input to the top-level session's verification before the merge and to the user's approval of the tag, not a substitute for either. A check made by the top-level session does not replace its own verification before the merge.
```

What each part closes:

| Sentence or phrase | Id | Before (quoted from `:46`) |
|---|---|---|
| "the release files you prepare (the version files, the changelog, and `docs/releases/vX.Y.Z.md` ...)"; "on those files alone"; "covers the release files" | -05 | "the release document you prepare (version markers, changelog, release notes, rollback plan)"; "on that document alone"; "covers the document" |
| "(the `tech-lead` review by area, the orchestrator's recorded verification, or the top-level session's recorded verification; name which one)"; the last sentence | -03 | "(the `tech-lead` review by area, or the top-level session's own verification)" |
| "If that row is missing or stale, or its status is FAIL, your verdict is FAIL; if its status is CONDITIONAL_PASS ..." | -02 | (no sentence) |
| "only these may change: the `Release:` line ...; ... the values of Status, Open blockers, ...; and the verdict text ..." | -09 | "only the `## RELEASE VERDICT` section and the `Release:` line under `## Gate Verdicts` may change" |

**Record (ADR-008 D5).**
- *Subject*: what item 5 requires of the independent check (its scope, its checker, its effect, and what may change after it).
- *Clauses*: all in `release-manager.md:46`, plus `:175` and `orchestrator.md:218`. No clause of another document says otherwise. This is a same-file gap, which ADR-008 § Scope ("A document that contradicts itself") leaves to same-file coherence.
- *Same-file basis*: -05: the item names "version markers, changelog" and then calls them "the document", while `orchestrator.md:218` names only `docs/releases/vX.Y.Z.md`. -02: "Do not issue a PASS or CONDITIONAL_PASS on that document alone" leaves FAIL as the only verdict without the row; the new sentence says so. "Report a blocker" for a stale check already blocks; FAIL now says it in the verdict's own terms. -09: the item says "after it, only the `## RELEASE VERDICT` section ... may change"; that section holds Version and the counts (`docs/releases/_template.md:76`, `:78-80`), which the check exists to cover.
- *User decisions*: item 5 comes from ruling A+ ("T693 go", 2026-10-31) and its stale rule from "fix 01" (2026-10-31). R1 keeps every decided point. It makes more edits stale, never fewer, so it tightens and does not loosen the decided text.
- *Departure from the reviewer's wording (-09)*: the reviewer proposed "allow no added line". I allow the verdict text (opening paragraph, Gate Inputs, Justification, Conditions, Blockers, the user's decisions). The verdict needs the check's result, so its justification can only be written after the check. v9.0.0 shows this: its Gate Inputs table and Justification cite the check at `a47d982d` (`docs/releases/v9.0.0.md:281-283`). The facts the check exists to cover (Version, the three counts, the rest of the document) stay frozen.
- *R10 fields*: R1 lists `Issued at commit` and `Independent check` among the fields that may change after the check, because R10 adds them to the published verdict (the user's "O1: both fields (Recommended)"). Their values are only known after the check.

### R2. `implementation/knowledge/agents/release-manager.md:175` (SEC-T693-03, -05)

**Replace the row with:**

```text
| Release files, independent check (commit: [sha]) | PASS/CONDITIONAL_PASS/FAIL | [artifact; checker: tech-lead, orchestrator or top-level session] |
```

Authority: same-file coherence with R1 (one name for the scope and the checker).

### R3. `implementation/knowledge/agents/orchestrator.md:218` (SEC-T693-03, -05)

**Replace the line with:**

```text
- The release manager prepares the release files (Core Workflow, Phase 5, step 2): the version files, the changelog and `docs/releases/vX.Y.Z.md`. Obtain the independent check of those files first (a `@tech-lead` review by area, or your own recorded verification, named as the orchestrator's, or as the top-level session's when you run as the top-level session) and give the release manager its artifact and commit; `release-manager` § Release Gate Policy item 5 requires it. That check does not replace the top-level session's own verification before the merge.
```

**Record.** *Subject*: the name of the checker and the scope of the check. *Clauses*: `orchestrator.md:218` "(a `@tech-lead` review by area, or your own verification)" against `release-manager.md:46` "(the `tech-lead` review by area, or the top-level session's own verification)". *Step A*: holds. Both can be obeyed, but when the orchestrator runs as a subagent, "your own verification" would be recorded as the top-level session's (SEC-T693-03). The remedy is the Step A remedy: state the relationship where readers will see it (ADR-008 P3a). The line keeps "(Core Workflow, Phase 5, step 2)" and its place under `**RELEASE GATE** (before deployment):`, which `tests/functional/test_release_self_review_text.py:133-146` checks.

### R4. `implementation/knowledge/agents/release-manager.md:165` (SEC-T693-04, knowledge part)

**Insert after line 165** (`### Version: [vX.Y.Z]`) one blank line and this line:

```text
### Issued at commit: [sha the release files were at when you issued this verdict, before you wrote it]
```

**Record.** *Subject*: the fields of the agent's verdict block. *Clauses*: `release-manager.md:160` places this block beside the command's rendering: "this block does not replace it and is not a second `## RELEASE VERDICT` section in that document". `/prepare-release` step 7 (`prepare-release.md:45-59`) fixes the published block. *Step A*: holds. The new field is in the agent's own block, which is not rendered into the release document, so it competes with no field of the command (ADR-008 D4, "adds fields ... that compete with none"). No command text changes.

### R5. `implementation/knowledge/skills/validation-gates/SKILL.md:118` (SEC-T693-02)

**Insert after line 118** (`- Rollback plan`, in § Gate Input Requirements, Release Gate):

```text
- The independent check of the release files, with its commit (`release-manager` § Release Gate Policy item 5)
```

**Record.** *Subject*: the Release gate's inputs. *Clauses*: `validation-gates/SKILL.md:114` "All prior gate verdicts (must be PASS or CONDITIONAL_PASS with conditions resolved)"; the independent check is not a gate verdict (SEC-T693-02). *Step A*: holds; the bullet points to the agent and copies no rule (ADR-008 P3b remedy: "point ... Do not copy").

### 1.5 R10. SEC-T693-04, command part (the user's decision under ADR-007)

The published `## RELEASE VERDICT` is the declared output of `/prepare-release` step 7. Under ADR-007 a command's declared contract changes only if it contradicts `AGENTS.md`, a stable instruction or itself (branch 1). None of these applies, so the change was the user's to decide; ADR-008 P2 adds that a command "is never amended on the strength of a skill or agent". **The user decided on 2026-11-01: "O1: both fields (Recommended)".** That recorded decision is the authority for R10 ("that decision governs, and documents are amended to it", ADR-008 § Scope).

**R10a. `implementation/knowledge/commands/prepare-release.md:58`.** Insert after line 58 (`- **Timestamp**: <ISO-8601>`), inside the code block, before the closing fence on line 59:

```text
- **Issued at commit**: <sha the release files were at when the verdict was issued>
- **Independent check**: <PASS | CONDITIONAL_PASS | FAIL> at <sha>, by <tech-lead | orchestrator | top-level session>
```

**R10b. `docs/releases/_template.md:86`.** Insert the same two lines after line 86 (`- **Timestamp**: <ISO-8601>`), before the blank line and `## Rollback Plan`, so that the scaffold matches the command. This file is not a knowledge file; it is the command's scaffold (`prepare-release.md:40-41`).

R1 already lists both fields among those that may change after the check.

- *Why*: the stale comparison then has both sides in the published document (SEC-T693-04), and `scripts/verify-release-docs.py` could check the fields later.
- *Not relaxation*: R10 adds fields and removes none (ADR-007 § 5).
- *Values*: `Independent check` carries the same status, commit and checker as the Gate Inputs row of R1 and R2; they record one check, so they carry the same values.
- *Risk* **(unverified)**: golden cases for `/prepare-release` (for example `prepare-release-conditional-pass-conditions-gap`) may check the block's field list. A hand-authored fixture may then need the new fields, which is a protected-path edit and needs a grant (`docs/artifacts/protected-paths-v1.md`). I did not open `tests/golden/`. The orchestrator should run `scripts/scorecard.py --check` after T720.

### R6. `implementation/knowledge/agents/orchestrator.md:261-262` (SEC-T693-06)

**Replace lines 261 and 262 with:**

```text
3. Run **Release Gate**
4. Delegate to **@devops-engineer** for production deployment, after the Release Gate verdict is PASS or CONDITIONAL_PASS
```

**Record.** *Subject*: the order of the Release Gate and deployment. *Clauses*: `orchestrator.md:261-262` (deploy at step 3, gate at step 4) against the same file's `:216` "**RELEASE GATE** (before deployment)" and `validation-gates/SKILL.md:29` (Release, trigger "Before deployment"). *Step A*: fails (one order). *Same-file coherence*: the clause that the rest of the file disagrees with is the defective one, so the agent is amended. Step 2 (`orchestrator.md:260`) is unchanged, so the test's `CORE_P5_STEP2` pin still holds.

## 2. Severity-scale gaps (TD-T687-02 to -04)

### R7. `implementation/knowledge/agents/qa-engineer.md:60` (TD-T687-02)

**Replace the line with:**

```text
### Priority: [P0 | P1 | P2] (the task priority of `AGENTS.md` § Task Protocol)
```

**Record.** *Subject*: the value set of the `P<n>` priority on a QA bug report. *Tier-1 clause*: `AGENTS.md` § Task Protocol: "Priorities: `P0` (critical path), `P1`, `P2`." *Agent clause*: `qa-engineer.md:60` "### Priority: [P0 | P1 | P2 | P3]". *Reach*: `AGENTS.md` declares no scope narrower than the repository (ADR-008 D2). The bug's priority is the priority of its fix task: `/bug-report` § Task Creation maps bug severity to `P0` to `P2`, as `docs/wiki/severity-and-grade-scales.md` Table 2 row "S2 and S3" cites it (I did not re-read `/bug-report`: **unverified**). *Step A*: fails; `P3` cannot be carried into the ledger. *Step B (P1)* fires: amend the agent toward `AGENTS.md`, and cite it.

### R8. `implementation/knowledge/skills/release-workflow/SKILL.md:171` and `:232` (TD-T687-03)

**Replace line 171 with** (keep the tree characters and indentation):

```text
   └── Assign a severity on the issue's own scale, and name it: `Critical` or `High` for a bug (`/bug-report` § Severity), `SECURITY:CRITICAL` or `SECURITY:HIGH` for a security finding (`security-guidelines.md` § Security Review Workflow)
```

**Replace line 232 with:**

```text
- Hotfixes are for issues graded critical or high on their own scale (§ 5, step 1) only. Medium/low issues wait for the next regular release.
```

**Record.** *Subject*: which scale "critical or high" means in a hotfix. *Clauses*: `release-workflow/SKILL.md:171` "Assign a severity (must be critical or high)" and `:232` "Hotfixes are for critical/high issues only". *Step A*: holds; no clause contradicts another, but no scale is named. The remedy names the defining documents (ADR-008 P3a: "amends at most to state the relationship"). *Defining documents*: S2, `/bug-report` § Severity (with `qa-engineer` § Bug Report Format); S5, `security-guidelines.md` § Security Review Workflow (`:180-184`). The values are written as each source writes them. `/bug-report` was not re-read by me **(unverified)**; the wiki Table 1 row S2 cites it.

### R9. `implementation/knowledge/agents/security-engineer.md:96-98` and `:103` (TD-T687-04)

**Replace lines 96 to 98 with:**

```text
- **Risk Level**: [CRITICAL | HIGH | MEDIUM | LOW]
- **Findings**: [X CRITICAL, Y HIGH, Z MEDIUM, W LOW]
- **Status**: [PASS | CONDITIONAL_PASS | FAIL]
```

**Replace line 103 with:**

```text
- **Severity**: SECURITY:CRITICAL | SECURITY:HIGH | SECURITY:MEDIUM | SECURITY:LOW
```

**Record.**
- *Line 98 (V1)*: `AGENTS.md` § Validation Gates: "VERDICTS: `PASS` | `CONDITIONAL_PASS` | `FAIL`". "Conditional Pass" is not in that set as written, and no document says values compare case-insensitively (wiki § Known gaps item 3). *Step A* fails on the closed set; *Step B (P1)* fires.
- *Line 103 (S5, per finding)*: `security-guidelines.md:181`: "Security Engineer flags findings as `SECURITY:CRITICAL`, `SECURITY:HIGH`, `SECURITY:MEDIUM`, or `SECURITY:LOW`". The per-finding Severity is that flag. *Step B (P1)* fires.
- *Lines 96-97 (S5, summary)*: same-file coherence with § Findings Classification (`:81-84`) and the VERDICT Findings Summary (`:172-175`), which write `CRITICAL` to `LOW`. `validation-gates/SKILL.md:85` already equates those with the `SECURITY:` grades.
- *Not ruled*: the lower-case `pass`, `conditional_pass`, `fail` of `security-engineer.md:155` and `qa-engineer.md:117`. They are outside TD-T687-04 and the wiki already records them (Table 1, note V1).

### 2.1 Wiki text for T720 (not a knowledge file)

`docs/wiki/severity-and-grade-scales.md` is descriptive: "If a row differs from its source, the source wins and this page is the defect" (`:11`). After R7 to R9 are applied:

- **Replace § Known gaps item 3 (`:78`) with:**
  `3. **Casing (SC634-4).** The same values appear in different casing: S4 (\`Critical\` in the scorecard, \`critical\` in the ledger), S5 (\`SECURITY:HIGH\`, \`HIGH\`), V1 (\`PASS\`, \`pass\`). No document read says that values are compared case-insensitively.`
- **Replace § Known gaps item 5 (`:80-83`) with:**
  `5. **Also found while writing this page.** Closed by \`docs/artifacts/rulings-batch-d-v1.md\` (TD-T687-02 to -04) and applied in T720: agent \`qa-engineer\` § Bug Report Format lists \`P0\` to \`P2\`; skill \`release-workflow\` § Hotfix Workflow names the scale of each severity; agent \`security-engineer\` § Security Review Report Format writes S5 and V1 as its other sections and tier 1 write them.`

## 3. TD-T713-01

Not ruled here. It is a policy choice between the text of Release Gate Policy item 2 and two releases that shipped a `SECURITY:MEDIUM` by the user's recorded decision. No document ranks a user's per-release decision against an agent's policy text, so ADR-008 P5 applies: it goes to an ADR and the user. The ADR is `docs/decisions/ADR-011-user-accepted-medium-at-release.md`.

**Decided.** The user accepted ADR-011 on 2026-11-01: "(a) Time-bound acceptance (Recommended)", with the end date "Until the next release". ADR-011 is now Accepted, and it decides TD-T713-01. A `SECURITY:MEDIUM` ships only under the user's acceptance for that release, recorded with a remediation plan; the acceptance covers that release only. T720 applies ADR-011 rows A1-A13 and its wiki line. No ruling in sections 1 and 2 relies on ADR-011.

## 4. Notes for T720 and T721

1. **The pins break on purpose.** `tests/functional/test_release_self_review_text.py:41-53`, `:57-60` and `:62-67` pin E1, E2 and E3 word for word in the source and five projections. R1, R2 and R3 change all three. T720 and the pin update of T721 must land in the same merge request, or the suite fails between them.
2. **Release Gate Policy stays items 1 to 5.** No ruling here adds an item (the test checks this at `:111-113`).
3. **Grep before T720** (I had no search tool): in `implementation/knowledge/`, search for "the top-level session's own verification", "your own verification", "release document", "Conditional Pass", "P3", and "critical or high". Report any hit outside the lines above as a new finding rather than editing it under this artifact.
4. **ADR-011 lines.** ADR-011 is Accepted, so T720 also applies its rows A1-A13. They touch `release-manager.md:43`, `:181` and `:222` and `prepare-release.md:62` and `:70`, which R1 to R10 do not touch. Insertions shift later lines: R4 adds two lines after `release-manager.md:165` (`:175` becomes `:177`, `:181` becomes `:183`, `:222` becomes `:224`); R10a adds two lines after `prepare-release.md:58` (`:62` becomes `:64`, `:70` becomes `:72`); R5 adds one line after `validation-gates/SKILL.md:118` (`:140` becomes `:141`, `:151` becomes `:152`). T720 should apply edits from the bottom of each file up, or re-read the lines.
5. **Unverified in this artifact**: `/bug-report` § Task Creation and § Severity (R7, R8; cited from the wiki); the golden cases of `/prepare-release` (R10); ADR-010 (not opened).

## 5. The user's decisions (2026-11-01)

Recorded verbatim (AskUserQuestion, option labels):

1. **TD-T713-01** (ADR-011): "(a) Time-bound acceptance (Recommended)". End date: "Until the next release" (the 90-day option was not chosen). ADR-011 is Accepted with that end date.
2. **SEC-T693-04, command part** (ADR-007): "O1: both fields (Recommended)". Ruled as R10 (section 1.5).

No decision for the user remains open in this artifact.

## 6. Review mode and references

- Produced by the solution architect; no knowledge file, task file or Status line was edited.
- Inputs: `release-manager.md:41-46`, `:158-189`, `:218-229`; `orchestrator.md:127-146`, `:197-263`; `validation-gates/SKILL.md` (whole); `prepare-release.md` (whole); `security-guidelines.md:9-26`, `:180-184`; `qa-engineer.md:50-125`; `security-engineer.md:60-199`; `release-workflow/SKILL.md` (whole); `docs/releases/_template.md`; `docs/releases/v8.0.0.md:246-306`; `docs/releases/v9.0.0.md:244-295`; `docs/wiki/severity-and-grade-scales.md`; ADR-007; ADR-008; `docs/decisions/_template.md`; `tests/functional/test_release_self_review_text.py`.
