# Artifact: conditional-pass-semantics-v3.md

> Filename: `conditional-pass-semantics-v3.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T580 (P2, P39), third version
- **Created**: 2026-10-02
- **Based on**:
  - `docs/artifacts/conditional-pass-semantics-v2.md` (superseded by this version) and, through it, v1;
  - the Security Engineer's **delta re-review of v2: CONDITIONAL_PASS**. SEC-001 and SEC-002 are met. MEDIUM items
    SEC-009, SEC-010 and SEC-012 remain, with LOW items SEC-011 and SEC-013 to SEC-017. The orchestrator relayed the
    reviewer's After texts; I did not read the review record;
  - the orchestrator's verification of v2: all 17 edits apply exactly once on `develop`;
  - the orchestrator's decision to **widen scope to the Release-gate executor (SEC-012)**;
  - `docs/decisions/ADR-008-knowledge-document-authority.md`, **Accepted** (header: "The user approved it on 2026-10-02").
    It was merged into `develop` at `5eff98e`, and I read it in the primary checkout. This worktree is at `dd7703b`,
    which predates the merge, so the ADR is cited by path and section;
  - the orchestrator's verified facts for SEC-012 (§8);
  - the user decisions Q1–Q4 of 2026-10-02 (§1.6) and the P39 rule (§1.1);
  - `ADR-007` (Accepted); `poc-contract-resolution-v1.md` §9.2; `gate-verdict-consistency-v1.md` §§6–7, 13.3;
    `poc-security-reviewer-blocking-v3.md`;
  - source files, all at `dd7703b`:
    - `release-manager.md`, read in full;
    - `commands/prepare-release.md`, read in full;
    - the files listed in v1's Metadata.
- **Supersedes**: `conditional-pass-semantics-v2.md`. v1 and v2 stay unchanged. **Where they differ, v3 governs. FU-1
  applies v3 only.**
- **Decision references**: P39; the user's Q1–Q4; ADR-007 branch 1 (commands); ADR-008 Step A, Step B (P1) and
  § Scope (recorded user decisions govern); the T542/FU-C precedent. No new ADR.

## 0. What this document is, and what it did not do

This is the complete, standalone ruling for P39, with exact edits for FU-1. §15 lists every v2→v3 change. **It changed
no agent, skill, command, instruction or golden case.**

**Method and limits.**
- **No shell.** Unverifiable claims are marked **(unverified)** (§13).
- **Golden access.** Only the v1 grant was used: `code-review-conditional-pass-conditions-gap/{brief.md,expect.py}`.
  Nothing else under `tests/golden/` was opened, and nothing under `held-out/`.
- **Before texts.** Every `Before:` carried from v2 is byte-identical. The **new** Befores are:
  - B2b, which v2 already listed as optional and v3 makes required;
  - R1–R5 (`release-manager.md:45, :181, :222`; `prepare-release.md:69, :61`).

  Each new Before was copied from the file as read in full, and is unique in that file. **Apply by text, not by line
  number.**
- **Characters and fences.** `—` is U+2014 and `§` is U+00A7. One four-backtick fence per edit, each beginning
  `Before:`.

## 1. Authority basis

### 1.1 The user's P39 rule (2026-10-02, verbatim)

> "CONDITIONAL_PASS allows merge with conditions tracked (closed before the next gate on production; PoC debt due by
> handoff). FAIL blocks. Security HIGH/CRITICAL and constraint breaches never qualify for CONDITIONAL_PASS. The
> experimental /code-review command and tech-lead agent get amended to match AGENTS.md." The user chose: **"Adopt it
> (Recommended)"**.

### 1.2 `AGENTS.md`

- § Validation Gates `:54–55`: "`FAIL` blocks progression." "`CONDITIONAL_PASS` proceeds with tracked conditions added
  to the task list."
- § Task Protocol `:18`: "Only orchestrators create/transition tasks."

### 1.3 Commands: ADR-007 branch 1

Branch 1: "Does the clause contradict `AGENTS.md`, a `stable` instruction, or another clause of the same command file? If
yes, the command is wrong regardless of what the corpus does." ADR-008 P1(d): "For a command, P1 *is* ADR-007 branch 1,
unchanged."

| Command edit | Prong | Contradiction, quoted from both sides |
|---|---|---|
| A4 `/code-review:51–52` | `AGENTS.md` | `:55` "proceeds with tracked conditions" against "conditions that must be met before merge", at a gate that is "before merge" (`validation-gates:26`) |
| B2–B4, B2b `/security-audit:44,45,67,73` | stable instruction | `security-guidelines:182` "`CRITICAL` and `HIGH` findings block merge until resolved"; `:183` "`MEDIUM` findings must have a remediation plan before merge" against FAIL for CRITICAL only, HIGH "fix within current sprint", and MEDIUM "schedule for next sprint" |
| R4 `/prepare-release:69` | `AGENTS.md`; stable instruction | `:54` "`FAIL` blocks progression" against "If a quality gate has failed … (or `CONDITIONAL_PASS` …)". `security-guidelines:153` (constraints "cannot be overridden by any agent, configuration, or runtime decision") against a blocker carried as a condition |
| R5 `/prepare-release:61` | `AGENTS.md` | `:55` "proceeds" against "conditions that must be met before deployment". At the Release gate, proceeding is shipping |

ADR-007 §5 (no relaxing) is respected. Each command edit keeps or tightens what the command forbids. The only latitude R5
grants, shipping with conditions, is Q4's.

### 1.4 Agents: ADR-008 Step B (P1), and the T542/FU-C precedent

- **`tech-lead` (A1–A3).** Step A fails. One decision, "may this merge?", gets two values:
  - `tech-lead:97`: "Merge is blocked until conditions are resolved";
  - `AGENTS.md:55`: proceed.

  **Step B (P1) fires.** `AGENTS.md` "declares no scope narrower than the repository" (ADR-008 D2). The lower document
  is amended toward tier 1. This is the T542/FU-C precedent, now standing as P1. The self-subordination at `:29–30` and
  `:68` corroborates it, and the user named this agent.
- **`tech-lead:111` (C4) and `release-manager` (R1–R3).** See §1.5.

### 1.5 Skills, the waiver and the Release gate: Step A, then recorded user decisions

ADR-008 § Scope, "Not covered": "A question already settled by an accepted ADR or a recorded user decision. That
decision governs, and documents are amended to it."

| Site | Step A | What governs |
|---|---|---|
| `validation-gates:55, 66–68, 75, 131–132` (A5–A8); `testing-strategy:240` (B1) | The "documented mitigations" permission and the `security-guidelines` `:182`/`:153` prohibitions are jointly satisfiable by withholding the permission for security findings. The track and due-point clauses ("before the next gate" with no track split) fail Step A against the user's rule | **P39, Q2, Q3, Q4** (§ Scope). The security exclusion also restates tier 1, so Step B applies to it if Step A is read strictly (ADR-008 P40 worked example, slice S1) |
| `code-review:150, :159` (C1, C3); `tech-lead:111` (C4) | The waiver is a permission and `:182`/`:153` are prohibitions, so Step A holds | **Q1**: "Keep it, except for security". Step A allows "a note stating the relationship". Q1 makes the carve-out a rule |
| `release-manager:45, :181, :222` (R1–R3) | Risk acceptance of a `conditional_pass` (`:45`) cannot reach a security HIGH/CRITICAL finding once A6 and B1 apply, so Step A holds for those. For a security MEDIUM at the Release gate, Step A fails against Q4 ("never applies to security findings") | **Q4** (§ Scope), plus Step A notes for the HIGH/CRITICAL/constraint parts. The orchestrator widened the scope to these files (SEC-012) |

**P4: maturity is not relied on anywhere.** The maturity of each touched file is recorded in §8 for blast radius only.

### 1.6 User decisions (2026-10-02, verbatim)

| Question | Decision | Applied in |
|---|---|---|
| Q1: keep the Tech Lead waiver for non-security FAILs? | **"Keep it, except for security (Recommended)"** | A4, C1, C3, C4 |
| Q2: PoC "debt due by handoff" | **"Recorded by handoff (Recommended)"**. A PoC CONDITIONAL_PASS condition must be in the debt ledger and scorecard by the production handoff and is fixed in production. Security breaches can never be debt. Where `poc-orchestrator` § Security Findings and `poc-security-engineer:23` set a security-MEDIUM fix deadline "no later than the production handoff", that more specific rule governs. | A1, A3–A6, A8, C2 |
| Q3: does the omitted/removed/disabled/weakened class apply on production too? | **"Both tracks (Recommended)"**. It is scoped to the controls `security-guidelines.md` requires for the code under review. Pre-existing gaps outside the change are graded at their own severity and tracked, so older code doesn't deadlock. | A3, A4, A6, B1, B3, B4, C1, C3, C4, R1 |
| Q4: when do Release-gate conditions close? | **"Next release cycle"**. A Release-gate CONDITIONAL_PASS may ship, with its conditions tracked as tasks for the next release cycle. This never applies to security findings. | A5, A6, A8, R1–R5 |

### 1.7 Defined terms

- **Security finding.** Any finding in the security category, whichever gate or executor raises it, graded on the
  `security-guidelines.md` § Security Review Workflow scale. **A finding about a control that `security-guidelines.md`
  requires is a security finding, whatever category it is filed under** (SEC-016).
- **The security exclusion.** These never qualify for CONDITIONAL_PASS, are never waived, are never risk-accepted and are
  never recorded as debt:
  - a security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH`;
  - a breach of an Immutable Security Constraint;
  - a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed,
    disabled or weakened, tagged or not.
- **The pre-existing-gap rule (Q3, SEC-015).** A required control missing only from code outside the change under review
  is graded at its own severity and tracked. A change that adds or alters code which the missing control should protect
  is code under review for that control.
- **The track rule.**

  | Case | When the condition closes |
  |---|---|
  | Production | Before the next gate |
  | Release gate | Tasks for the next release cycle; the release may ship after the risk acceptance `release-manager` requires |
  | PoC | Recorded as debt by the production handoff; fixed in production |
  | Security finding graded medium | Fixed before the next gate. At the Release gate, before the release ships. On PoC, by its remediation-plan deadline, no later than the handoff |
  | Security finding graded low | Not a condition. Tracked as technical debt |

## 2. Ruling on the `validation-gates:67` security nuance

Amend `validation-gates` itself (A5–A8):
- **Where the rule is read.** `validation-gates` is the mandatory skill at every gate (`AGENTS.md:67`).
- **Mitigation route.** "Documented mitigations" covers high findings outside the security category only.
- **The security exclusion** (§1.7) is FAIL until resolved, on both tracks.
- **PASS** requires none of: a security finding graded critical or high, a security finding graded medium, or an
  excluded finding (SEC-009).
- **Medium.** A security finding graded medium yields at best CONDITIONAL_PASS. Its plan is recorded before the affected
  work's next merge, and its fix is due under the track rule.
- **Low.** A security finding graded low is not a condition (SEC-014).

**Observation.** `:74` places "security vulnerability" in `critical`. The tier misalignment with
`security-engineer.md:81–83` is SEC-008, a follow-up only (FU-6).

## 3. Batch A: required

### A1: `tech-lead.md:82` (unchanged from v2)

````
Before:
- [ ] [Condition 1 — must be resolved before merge]

After:
- [ ] [Condition 1 — owner; due point: before the next gate (production track), or recorded as debt in the debt ledger and scorecard by the production handoff (PoC track); a security finding also carries its remediation plan (owner, fix, deadline)]
````

### A2: `tech-lead.md:90` (unchanged from v2)

````
Before:
- Merge permitted: [Yes | Yes, after conditions met | No]

After:
- Merge permitted: [Yes | Yes, with conditions tracked | No]
````

### A3: `tech-lead.md:97`

````
Before:
- **CONDITIONAL_PASS**: Code is acceptable with listed conditions that must be addressed before merge. Merge is blocked until conditions are resolved.

After:
- **CONDITIONAL_PASS**: Code is acceptable with listed conditions, and merge is permitted with the conditions tracked (`AGENTS.md` § Validation Gates: "`CONDITIONAL_PASS` proceeds with tracked conditions added to the task list"). List each condition with an owner and a due point; the orchestrator adds it to the task list (`AGENTS.md` § Task Protocol). On the production track a condition is resolved before the next gate. On the PoC track it becomes a debt item, recorded in the debt ledger (skill `technical-debt-tracking`) and in `POC-DEBT-SCORECARD.md` (`poc-guidelines.md` § Debt Scorecard) by the production handoff, and fixed in production; where `poc-orchestrator` § Security Findings sets a security finding's fix deadline no later than the production handoff, that more specific rule governs. A security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH` (`security-guidelines.md` § Security Review Workflow), whoever raised it, a breach of an Immutable Security Constraint in `security-guidelines.md`, and a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, tagged or not, never qualify for CONDITIONAL_PASS and are never recorded as debt: the verdict is FAIL until each is resolved, and no waiver applies (§ Merge and Architecture Authority). A required control missing only from code outside the change under review is graded at its own severity and tracked like any other finding of that grade. A change that adds or alters code which the missing control should protect is code under review for that control. A security finding listed as a condition carries its remediation plan (owner, fix, deadline) (`security-guidelines.md` § Security Review Workflow).
````

**Authority:** ADR-008 Step B (P1) against `AGENTS.md:55`, which is the T542/FU-C precedent; P39; Q2, Q3; SEC-003,
SEC-007, SEC-015.

### A4: `commands/code-review.md:51–52`

````
Before:
If CONDITIONAL_PASS, list the conditions that must be met before merge.
If FAIL, include blocker details, owner, and retry attempt guidance.

After:
If CONDITIONAL_PASS, list the conditions, each with an owner and a due point. A security finding listed as a condition carries its remediation plan (owner, fix, deadline) (`security-guidelines.md` § Security Review Workflow). CONDITIONAL_PASS permits the merge, with each condition tracked in the task list (`AGENTS.md` § Validation Gates): on the production track a condition is resolved before the next gate; on the PoC track it becomes a debt item, recorded in the debt ledger and in `POC-DEBT-SCORECARD.md` by the production handoff and fixed in production (`poc-guidelines.md` § Mandatory Debt Tracking, § Debt Scorecard), except where `poc-orchestrator` § Security Findings sets a security finding's fix deadline no later than the production handoff, which governs.
A security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH` (`security-guidelines.md` § Security Review Workflow), whoever raised it, a breach of an Immutable Security Constraint in `security-guidelines.md`, or a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, tagged or not, never yields CONDITIONAL_PASS and is never recorded as debt: the status is FAIL until it is resolved. A required control missing only from code outside the change under review is graded at its own severity and tracked. A change that adds or alters code which the missing control should protect is code under review for that control.
If FAIL, the merge is blocked; a Tech Lead waiver may lift a FAIL only when no security finding excluded above is among its causes (skill `code-review` § Review as Validation Gate), and a waiver that lifts a FAIL with a security finding graded `SECURITY:MEDIUM` among its causes does not lift that finding's remediation plan (owner, fix, deadline), which is recorded as a tracked condition before merge. Include blocker details, owner, and retry attempt guidance.
````

**Authority:** ADR-007 branch 1, `AGENTS.md` prong; Q1–Q3; SEC-003, SEC-007, SEC-011 (in substance), SEC-015. A4 names
no `**Conditions**:` field and no list format, so the open case's `capability_gap` premise holds (§8).

### A5: `validation-gates/SKILL.md:55`

````
Before:
- [ ] <condition that must be met before proceeding>

After:
- [ ] <condition> — owner: <who>; due: before the next gate (production track; at the Release gate, the next release cycle, except a security finding, which is fixed before the release ships) | recorded as debt in the debt ledger and scorecard by the production handoff (PoC track; a security finding graded medium is fixed by its remediation-plan deadline, no later than the handoff); a security finding also carries its remediation plan (owner, fix, deadline)
````

**Source:** SEC-013, verbatim.

### A6: `validation-gates/SKILL.md:66–68`

````
Before:
| **PASS** | No critical or high findings. Medium/low findings noted but non-blocking. |
| **CONDITIONAL_PASS** | No critical findings. High findings have documented mitigations. Medium/low with clear remediation plan. All conditions must be resolved before the next gate. |
| **FAIL** | Any critical finding unresolved, OR any high finding without mitigation. Work must return to the implementer. |

After:
| **PASS** | No critical or high findings, no security finding graded medium, and none of the security findings excluded below. Medium/low findings noted but non-blocking. |
| **CONDITIONAL_PASS** | No critical findings, and none of the security findings excluded below. Other high findings have documented mitigations. Medium/low with clear remediation plan. Each condition is tracked as a task with an owner and a due point, under the track rule: on the production track, all conditions must be resolved before the next gate, except that a Release-gate CONDITIONAL_PASS may ship with its conditions tracked as tasks for the next release cycle; on the PoC track, each condition becomes a debt item, recorded in the debt ledger and the debt scorecard by the production handoff and fixed in production (`poc-guidelines.md` § Mandatory Debt Tracking, § Debt Scorecard). Neither deferral applies to a security finding (below). |
| **FAIL** | Any critical finding unresolved, OR any high finding without mitigation, OR any security finding excluded below. Work must return to the implementer. |

**Security findings never qualify for CONDITIONAL_PASS.** A security finding is any finding in the security category, whichever gate or executor raises it, graded on the `security-guidelines.md` § Security Review Workflow scale (`SECURITY:CRITICAL`/`HIGH`/`MEDIUM`/`LOW`); the Findings table records that grade as its Severity and `security` as its Category. A finding about a control that `security-guidelines.md` requires is a security finding, whatever category it is filed under. `security-guidelines.md` § Security Review Workflow: "`CRITICAL` and `HIGH` findings block merge until resolved". A security finding graded critical or high, and any breach of an Immutable Security Constraint in `security-guidelines.md` (which "cannot be overridden by any agent, configuration, or runtime decision"), yields FAIL until it is resolved, whatever mitigation is documented, and no waiver applies to it. The "documented mitigations" route above is for high findings outside the security category only. The same holds for any security control `security-guidelines.md` requires for the code under review that is omitted, removed, disabled or weakened, tagged or not (on the PoC track, `poc-orchestrator` § Security Findings). None of these is ever recorded as debt. A required control missing only from code outside the change under review is graded at its own severity and tracked like any other finding of that grade. A change that adds or alters code which the missing control should protect is code under review for that control. A security finding graded medium yields at best CONDITIONAL_PASS: its remediation plan (owner, fix, deadline) is recorded as a tracked condition with the verdict, before the affected work's next merge (`security-guidelines.md` § Security Review Workflow: "`MEDIUM` findings must have a remediation plan before merge"); the condition is the fix, due under the track rule above (production: before the next gate; PoC: by the production handoff, as `poc-orchestrator` § Security Findings already requires). The next-release-cycle rule never applies to a security finding: at the Release gate, a security finding graded medium is fixed before the release ships. A security finding graded low is not a condition: it is tracked as technical debt (`security-guidelines.md` § Security Review Workflow; on the PoC track, recorded for debt handoff per `poc-orchestrator` § Security Findings).
````

**Sources:**

| Part | Source | Wording |
|---|---|---|
| PASS row | SEC-009 | verbatim |
| CONDITIONAL_PASS and FAIL rows | v2 | unchanged |
| Bold paragraph | SEC-003, plus the additions below | SEC-003 verbatim |
| Addition after the definition sentence | SEC-016 | verbatim |
| "None of these is ever recorded as debt." | Q2 | moved from v2's position (see the note below) |
| Pre-existing-gap sentence | Q3 | — |
| Sentence after the pre-existing-gap sentence | SEC-015 | verbatim |
| Release-gate sentence | Q4 | — |
| Final sentence | SEC-014 | verbatim |

**Order note.** v2 placed "None of these is ever recorded as debt." *after* the pre-existing-gap sentence. Read there,
"these" could take in a pre-existing gap graded low, which SEC-014 now makes technical debt. v3 places the sentence
directly after the exclusion classes, which is what it refers to.

### A7: `validation-gates/SKILL.md:75` (unchanged from v2)

````
Before:
| `high` | Significant defect or design flaw. Must be addressed before release. |

After:
| `high` | Significant defect or design flaw. Must be addressed before release; a security finding graded high blocks merge until resolved (§ Verdict Rules). |
````

### A8: `validation-gates/SKILL.md:131–132`

````
Before:
1. Proceed with work, but track all conditions as tasks.
2. Conditions MUST be resolved before the next gate in the pipeline.

After:
1. Proceed with work, but track all conditions as tasks, each with an owner and a due point. At the Implementation gate, proceeding includes the merge; at the Release gate, it includes shipping the release, with the explicit risk acceptance `release-manager` § Release Gate Policy requires.
2. On the production track, conditions MUST be resolved before the next gate in the pipeline; at the Release gate, which has no next gate, they are tracked as tasks for the next release cycle. On the PoC track, each condition instead becomes a debt item, recorded in the debt ledger and the debt scorecard by the production handoff and fixed in production (`poc-guidelines.md` § Mandatory Debt Tracking, § Debt Scorecard). Neither deferral applies to a security finding (§ Verdict Rules): one graded medium is fixed before the next gate on the production track (at the Release gate, before the release ships), and on the PoC track by its remediation-plan deadline, no later than the production handoff (`poc-orchestrator` § Security Findings).
````

**Source:** v2, with the SEC-012 clause appended to item 1.

## 4. Batch B: required

### B1: `testing-strategy/SKILL.md:240`

````
Before:
| **Security scan** | No critical/high findings | No critical; high findings have mitigations | Any critical finding |

After:
| **Security scan** | No critical, high or medium findings, and nothing in the FAIL column | No critical or high findings and nothing in the FAIL column; each medium finding has a remediation plan (`security-guidelines.md` § Security Review Workflow) | Any critical or high finding, any breach of an Immutable Security Constraint (`security-guidelines.md`), or any security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, whatever its grade (a control missing only from code outside the change is graded at its own severity) |
````

**Source:** SEC-010, verbatim. It replaces SEC-005. The reviewer's parenthetical stands in for the pre-existing-gap
sentence, and SEC-015 was not listed for B1.

### B2: `commands/security-audit.md:44` (unchanged from v2)

````
Before:
   - **HIGH**: Exploitable with moderate effort, fix within current sprint

After:
   - **HIGH**: Exploitable with moderate effort; blocks merge until resolved (`security-guidelines.md` § Security Review Workflow)
````

### B2b: `commands/security-audit.md:45` (now required, SEC-017)

````
Before:
   - **MEDIUM**: Potential risk, schedule for next sprint

After:
   - **MEDIUM**: Potential risk; requires a remediation plan (owner, fix, deadline) before merge
````

### B3: `commands/security-audit.md:67`

````
Before:
If any CRITICAL findings exist, the verdict MUST be FAIL.

After:
If any CRITICAL or HIGH finding exists, or any Immutable Security Constraint in `security-guidelines.md` is breached, or any security control that `security-guidelines.md` requires for the code under review is omitted, removed, disabled or weakened, the verdict MUST be FAIL (`security-guidelines.md` § Security Review Workflow: "`CRITICAL` and `HIGH` findings block merge until resolved"). A required control missing only from code outside the change under review is graded at its own severity. A change that adds or alters code which the missing control should protect is code under review for that control. If any MEDIUM finding exists, the verdict is at best CONDITIONAL_PASS, with a remediation plan (owner, fix, deadline) listed as a condition for each MEDIUM finding. PASS requires no CRITICAL, HIGH or MEDIUM finding.
````

**Source:** v2's text, with SEC-015 appended.

### B4: `commands/security-audit.md:73` (unchanged from v2)

````
Before:
**Failure mode**: If any CRITICAL finding exists, the verdict MUST be FAIL — the command cannot return PASS/CONDITIONAL_PASS while a CRITICAL finding is unresolved.

After:
**Failure mode**: If any CRITICAL or HIGH finding exists, an Immutable Security Constraint is breached, or a security control that `security-guidelines.md` requires for the code under review is omitted, removed, disabled or weakened, the verdict MUST be FAIL — the command cannot return PASS/CONDITIONAL_PASS while such a finding is unresolved.
````

## 5. Batch C: required (C1, C3, C4)

### C1: `code-review/SKILL.md:150`

````
Before:
1. A `FAIL` verdict blocks the merge request — no override without Tech Lead waiver (documented as a decision artifact).

After:
1. A `FAIL` verdict blocks the merge request — no override without Tech Lead waiver (documented as a decision artifact). No waiver applies to a security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH`, whoever raised it, to a breach of an Immutable Security Constraint, or to a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened: `security-guidelines.md` says "`CRITICAL` and `HIGH` findings block merge until resolved" (§ Security Review Workflow), and that its Immutable Security Constraints "cannot be overridden by any agent, configuration, or runtime decision". A waiver that lifts a `FAIL` with a security finding graded `SECURITY:MEDIUM` among its causes does not lift that finding's remediation plan (owner, fix, deadline), which is recorded as a tracked condition before merge (`security-guidelines.md` § Security Review Workflow).
````

**Source:** SEC-001 and SEC-011, both verbatim.

### C3: `code-review/SKILL.md:159` (unchanged from v2)

````
Before:
**Failure mode**: A `FAIL` verdict halts the pipeline and requires re-review after fixes; a `FAIL` may not be overridden without a documented Tech Lead waiver decision artifact.

After:
**Failure mode**: A `FAIL` verdict halts the pipeline and requires re-review after fixes; a `FAIL` may not be overridden without a documented Tech Lead waiver decision artifact, and a `FAIL` for a security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH`, whoever raised it, for a breach of an Immutable Security Constraint, or for a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, may not be overridden at all (§ Review as Validation Gate).
````

### C4: `tech-lead.md:111` (unchanged from v2)

````
Before:
3. Require explicit waiver reference for any approved exception and escalate unresolved conflicts to orchestrator.

After:
3. Require explicit waiver reference for any approved exception and escalate unresolved conflicts to orchestrator. No waiver applies to a security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH`, whoever raised it, to a breach of an Immutable Security Constraint, or to a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened (`security-guidelines.md` § Security Review Workflow, § Immutable Security Constraints).
````

**C1, C3 and C4 authority:** Q1 (ADR-008 § Scope: the recorded user decision governs). The Step A relationship is
stated against `security-guidelines` `:153` and `:182`. The precedent is v3 E11 of the O1 ruling
(`rapid-prototyping:74`).

## 6. Batch R: Release-gate executor (required, SEC-012)

### R1: `release-manager.md:45`

````
Before:
2. Require explicit risk acceptance for any `conditional_pass` prior to production deployment.

After:
2. Require explicit risk acceptance for any `conditional_pass` prior to production deployment. Risk acceptance never covers a security finding (skill `validation-gates` § Verdict Rules): a `SECURITY:CRITICAL` or `SECURITY:HIGH` finding, a breach of an Immutable Security Constraint, or a required security control omitted, removed, disabled or weakened blocks the release (item 1), and a `SECURITY:MEDIUM` finding is fixed before the release ships. Other risk-accepted conditions are tracked as tasks for the next release cycle.
````

### R2: `release-manager.md:181`

````
Before:
- [Gate/Finding]: risk_accepted_by=@[who], mitigation=[what], deadline=[when]

After:
- [Gate/Finding — never a security finding]: risk_accepted_by=@[who], mitigation=[what], deadline=[next release cycle or earlier]
````

### R3: `release-manager.md:222`

````
Before:
- DO NOT release when unresolved critical QA or security findings remain

After:
- DO NOT release when unresolved critical QA findings, or any unresolved security finding graded CRITICAL, HIGH or MEDIUM, remain
````

**R1–R3 source:** SEC-012, verbatim.

**R1–R3 authority:**
- Q4, "This never applies to security findings" (ADR-008 § Scope: the recorded user decision governs, and documents are
  amended to it).
- For the CRITICAL, HIGH and constraint parts, an ADR-008 Step A note stating their relationship to `security-guidelines`
  `:153`/`:182` and to A6. These parts can no longer reach a `conditional_pass`.
- No ranking is used. `release-manager` is `stable`, and that is not relied on (P4).

**R1, "(item 1)".** This refers to `:44`, "1. Block release when QA gate or Security gate is `fail`." It is within the
same numbered list (`:44–47`), so the reference resolves.

### R4: `commands/prepare-release.md:69`

````
Before:
**Failure mode**: If a quality gate has failed or a blocker is open, the VERDICT is `FAIL` (or `CONDITIONAL_PASS` with listed conditions) rather than a silent `PASS`.

After:
**Failure mode**: If a quality gate has failed, the VERDICT is `FAIL`. If a blocker is open, the VERDICT is `FAIL`, or `CONDITIONAL_PASS` with listed conditions only when no security finding is among them (skill `validation-gates` § Verdict Rules), rather than a silent `PASS`.
````

**Source:** SEC-012's sentence, verbatim. The Failure mode label and "rather than a silent `PASS`" are kept from the
line. **Authority:** ADR-007 branch 1 (§1.3: `AGENTS.md:54`; `security-guidelines:153`); Q4.

### R5: `commands/prepare-release.md:61` (new site, my finding)

````
Before:
9. If CONDITIONAL_PASS, list conditions that must be met before deployment

After:
9. If CONDITIONAL_PASS, list the conditions. The release may ship with each condition tracked as a task for the next release cycle, after the explicit risk acceptance `release-manager` § Release Gate Policy requires. A security finding is never such a condition: it blocks the release, or, graded medium, is fixed before the release ships (skill `validation-gates` § Verdict Rules).
````

**Why:**
- Without R5, the edited command would still say Release-gate conditions "must be met before deployment". That
  contradicts Q4 ("may ship, with its conditions tracked as tasks for the next release cycle").
- It would also contradict `AGENTS.md:55`, since at this gate "proceeds" means shipping. That is ADR-007 branch 1, on
  the `AGENTS.md` prong.
- It would conflict with the command's own `:69` after R4 (same-file coherence).

**Authority:** Q4 (ADR-008 § Scope); ADR-007 branch 1. **Not in the orchestrator's SEC-012 list.** I include it as
required because leaving it would keep a live Q4 contradiction in a file FU-1 already edits. The orchestrator may defer
it, but then `/prepare-release` is internally inconsistent (§12, Q9).

## 7. Optional

### C2: `code-review/SKILL.md:151` (unchanged from v2)

````
Before:
2. A `CONDITIONAL_PASS` verdict allows merge but **requires** that each should-fix item is logged as a task in `docs/tasks/active-tasks.md` with an assigned owner and target sprint.

After:
2. A `CONDITIONAL_PASS` verdict allows merge but **requires** that each should-fix item is logged as a task in `docs/tasks/active-tasks.md` with an assigned owner and target sprint. On the production track the item is resolved before the next gate; on the PoC track it becomes a debt item, recorded in the debt ledger and the debt scorecard by the production handoff and fixed in production (`poc-guidelines.md` § Mandatory Debt Tracking, § Debt Scorecard), unless `poc-orchestrator` § Security Findings sets a security finding's fix deadline no later than the production handoff, which governs.
````

## 8. Golden coupling and blast radius

**Known coupling** (results unchanged in every case):

- **`code-review-conditional-pass-conditions-gap`** (read under grant).
  - **What goes stale:** `brief.md:11–12` and `expect.py:4–5` quote `/code-review:51`. A4 makes them stale.
  - **Why the result is unchanged:** `check()` reads only the fixture.
  - **Premise:** holds, because A4 names no field and no list format.
- **`security-audit-critical-not-fail`** (orchestrator-verified; not read by me).
  - **What goes stale:** `brief.md:13`, the `expect.py:5` docstring and the `case.yaml` `known_failing_reason` quote "If
    any CRITICAL findings exist, the verdict MUST be FAIL". B3 makes all three stale.
  - **Why the result is unchanged:** `check()` reads only the fixture (CRITICAL: 1, Status: CONDITIONAL_PASS).
  - **Premise:** holds.
- **`validate-workflow-gate-verdict-sources`** (not read).
  - **What goes stale:** its fixture copy of `validation-gates` stops being byte-identical to source.
  - **Why the result should not change:** the lines its `expect.py` reads are not touched **(unverified)**.

**`/prepare-release` and `release-manager`.**
- **Verified by the orchestrator:**
  - `release-manager.md` is `stable`, and `commands/prepare-release.md` is `experimental`.
  - No open golden case quotes `prepare-release.md:69`.
  - The two `/prepare-release` cases, `prepare-release-conditional-pass-conditions-gap` and
    `prepare-release-real-verdict-missing`, are both `known_failing`, and neither references `:69`.
  - The only test that mentions `release-manager` is `test_validation_gates_skill_contract.py`. It maps Gate Types
    executor names, and does not touch `:45`, `:181` or `:222`.
- **R5 (`:61`) is not covered by that check (unverified).**
  - The case name `prepare-release-conditional-pass-conditions-gap` mirrors `code-review-conditional-pass-conditions-gap`.
    That case quotes the `/code-review` counterpart of `:61` ("list the conditions that must be met before merge").
  - So this case probably quotes `:61` ("list conditions that must be met before deployment"). If it does, R5 makes the
    quote stale.
  - **Expected:** the result is unchanged, if its `check()` reads only its fixture, as the `/code-review` sibling's does.
    This is reasoned by analogy, not read.
  - **Search** that case's `brief.md`, `expect.py` and `case.yaml` for `must be met before deployment`. Add any hit to
    FU-2.
- **Held-out:** detected only through `scripts/scorecard.py --check`.

**Other searches (unverified).** Run v1 §5's list, plus `schedule for next sprint` and `Potential risk`.

**Files edited:**

| File | Edits | Maturity (not relied on, P4) |
|---|---|---|
| `implementation/knowledge/agents/tech-lead.md` | A1, A2, A3, C4 | experimental |
| `implementation/knowledge/commands/code-review.md` | A4 | experimental |
| `implementation/knowledge/skills/validation-gates/SKILL.md` | A5–A8 | stable |
| `implementation/knowledge/skills/testing-strategy/SKILL.md` | B1 | stable |
| `implementation/knowledge/commands/security-audit.md` | B2, B2b, B3, B4 | stable |
| `implementation/knowledge/skills/code-review/SKILL.md` | C1, C3 (+ C2) | stable |
| `implementation/knowledge/agents/release-manager.md` | R1, R2, R3 | stable |
| `implementation/knowledge/commands/prepare-release.md` | R4, R5 | experimental |

**Mechanics.**
- **Edit count:** 21 required edits, plus optional C2, across 8 files.
- **Regenerate:** run `sync.mjs --root implementation` and `generate-registry.py`, each with `--check`.
- **Root drift:** declare exactly what `--print-drift` reports. That is up to 8 × 7 paths **(count unverified)**.
- **Maturity:** none expected at P2. **Affects:** `—`.

**Unchanged:**
- `AGENTS.md`, `security-guidelines.md`, `poc-guidelines.md`, `orchestrator.md`;
- `poc-orchestrator.md`, `poc-security-engineer.md`, `rapid-prototyping`, `security-engineer.md`;
- `release-workflow`, `receiving-code-review`;
- `tests/golden/**`.

**Behavioural consequences (unchanged from v2, plus R).**

| Track / gate | Before | After |
|---|---|---|
| Production security gate | Medium omitted control in the code under review: CONDITIONAL_PASS | FAIL |
| Release | Any `conditional_pass` shipped after risk acceptance (`release-manager:45`) | A `SECURITY:MEDIUM` finding must be fixed before shipping; other conditions are risk-accepted and deferred to the next release cycle |

## 9. Follow-ups

| ID | Covers | Files | `tests/golden/**` grant? | Owner (suggested) | Priority | Depends on / verify |
|---|---|---|---|---|---|---|
| **FU-0**: phrase check of v3 | SEC-009 … SEC-017 adoption; R5 (not a reviewer text) | this artifact | No | Security Engineer, or the orchestrator by phrase check | P2 | R5 is my wording. If the reviewer wants to see it, a delta look is needed |
| **FU-1**: apply P39 per **v3** | 21 required edits (A1–A8, B1–B4, B2b, C1, C3, C4, R1–R5); C2 optional | §8 table; mirrors; registry; root drift | **No** | Backend Developer | P2 | FU-0. ADR-008 is on `develop` (`5eff98e`), so dispatch from a `develop` that includes it. Verify as below |
| **FU-2**: refresh stale golden quotes | `code-review-conditional-pass-conditions-gap` `brief.md:11–12`, `expect.py:4–5`; `security-audit-critical-not-fail` `brief.md:13`, `expect.py:5`, `case.yaml` `known_failing_reason`; `prepare-release-conditional-pass-conditions-gap`, if the §8 search finds it quoting `:61` | those files only | **Yes** (`protected-paths-v1.md` §5, scoped per case directory); a baseline authorization if an `expect.py` changes | QA Engineer | P2 | After FU-1. Results unchanged. Not ruled |
| **FU-3**: `validate-workflow` fixture copy of `validation-gates` | Provenance | that case's fixture copy and brief | **Yes** | QA Engineer | P2 | Only if byte-identity must hold or is test-enforced |
| **FU-5** *(candidate)*: a structured `**Conditions**:` field in `/code-review` | Closes the capability gap | command; case classification | **Yes** | Solution Architect, then QA | P2 | A separate ADR-007 decision |
| **FU-6** (SEC-008) | `security-engineer.md:81–83` SLA table against `security-guidelines:182–183`; `validation-gates:74` tiers; `security-engineer.md:152–153` not naming the Q3 omitted-control class | `security-engineer.md`; `validation-gates/SKILL.md:74` | No | Solution Architect, then Backend Developer | P2 | Follow-up only |
| **FU-7** (tracked follow-up, not a v3 edit) | `receiving-code-review:86`. Proposed text, from the reviewer: "Escalation never lifts a `FAIL` caused by a finding that skill `code-review` § Review as Validation Gate excludes from waiver." | `receiving-code-review/SKILL.md` | No | Orchestrator scopes it | P2 | After FU-1 (C1 defines the exclusion it cites) |
| **D1** (P40) | P40's remaining slices | — | — | — | — | Now schedulable under ADR-008. **Slice S1** (security findings at any gate) **is settled by P39 as applied here** (A6, B1). S2–S4 remain, including `code-review:96`/`:128` against a security MEDIUM at the code-review gate |

**FU-1 verification:**

1. **Exactly one match each.** Each of the 21 required `Before:` texts, and C2's if it is applied, matches **exactly
   once by text** on `develop` at dispatch.
2. **Zero hits** under `implementation/knowledge/` for each of these:
   - `Merge is blocked until conditions are resolved`
   - `Yes, after conditions met`
   - `must be resolved before merge`
   - `conditions that must be met before merge`
   - `must be met before proceeding`
   - `High findings have documented mitigations`
   - `high findings have mitigations`
   - `If any CRITICAL findings exist`
   - `Exploitable with moderate effort, fix within current sprint`
   - `Potential risk, schedule for next sprint`
   - `conditions that must be met before deployment`
   - `unresolved critical QA or security findings remain`
   - `(or \`CONDITIONAL_PASS\` with listed conditions)`
3. **Exact hit counts:**

   | Phrase | Expected hits |
   |---|---|
   | `Security findings never qualify for CONDITIONAL_PASS` | 1 (`validation-gates`) |
   | `Yes, with conditions tracked` | 1 (`tech-lead`) |
   | `whoever raised it` | `tech-lead.md` 2; `commands/code-review.md` 1; `skills/code-review/SKILL.md` 2 |
   | `next release cycle` | `validation-gates` 3 (A5, A6 row, A8); `release-manager.md` 2 (R1, R2); `prepare-release.md` 1 (R5) |
   | `A change that adds or alters code which the missing control should protect` | 1 each in `tech-lead.md`, `commands/code-review.md`, `validation-gates`, `security-audit.md` |
   | `A finding about a control that` | 1 (`validation-gates`) |
   | `A security finding graded low is not a condition` | 1 (`validation-gates`) |
   | `A waiver that lifts a` | 1 (`skills/code-review`) |
   | `Risk acceptance never covers a security finding` | 1 (`release-manager.md`) |
   | `A security finding listed as a condition carries its remediation plan` | 1 each in `tech-lead.md` and `commands/code-review.md` |
4. **Byte-unchanged:** `AGENTS.md`, `security-guidelines.md`, `poc-guidelines.md`, the PoC agents,
   `security-engineer.md`, `release-workflow`, `receiving-code-review` and `tests/golden/**`.
5. **Generators and drift:** `sync.mjs --check` and `generate-registry.py --check` are clean, and the root parity gate is
   green.
6. **Scorecard:** `scripts/scorecard.py --check` is unchanged against the current baseline. A regression is held-out
   coupling: stop and report it.
7. **Maturity:** `check-maturity.py --root implementation` reports 0 failing.
8. **Tasks and tests:** `validate-tasks.py` passes. For `tests/run.py`, check the exit code and redirect the output to a
   file.
9. **Fixture copy:** report `cmp` of the `validate-workflow` fixture copy of `validation-gates`. A difference is
   expected; the case result must be unchanged.

## 10. ADR-008 D5 records (for the rulings that cite it)

| Ruling | Subject (D3) | Clauses | Step A | Step that fired | Declared scope relied on | Amendment | Maturity |
|---|---|---|---|---|---|---|---|
| A1–A3 | Merge effect of CONDITIONAL_PASS at the code-review gate | `tech-lead:82, 90, 97` vs `AGENTS.md:55` | Fails: one merge decision gets two values | **B (P1)** | `AGENTS.md`: no scope narrower than the repository (D2); `tech-lead:29–30`, `:68` | Agent amended toward `AGENTS.md`, citing it | Not relied on |
| C4, C1, C3 | Waiver of a security FAIL | `tech-lead:111`, `code-review:150, 159` vs `security-guidelines:153, 182` | Holds (a permission against a prohibition) | **§ Scope**: Q1 governs; Step A note | `security-guidelines` Rails `:15–24`, `applyTo: "**"` | Carve-out stated, citing the instruction | Not relied on |
| A5–A8, B1 | Verdict criteria and due points | `validation-gates:55, 66–68, 75, 131–132`; `testing-strategy:240` vs P39, Q2–Q4, `security-guidelines:153, 182–183` | Holds for the security permission; fails for the untracked due points | **§ Scope**: P39 and Q2–Q4 govern; Step A note for security (Step B if Step A is read strictly, as in P40 slice S1) | as above | Skills amended to the decisions | Not relied on |
| R1–R3 | Release-gate risk acceptance of security findings | `release-manager:45, 181, 222` vs Q4 | Fails for a security MEDIUM against Q4; holds for HIGH/CRITICAL once A6 applies | **§ Scope**: Q4 governs; Step A note | — | Agent amended to Q4 | Not relied on |
| A4, B2–B4, B2b, R4, R5 | Command clauses | §1.3 table | Fails | **B (P1) = ADR-007 branch 1**; Q4 for R4 and R5 | `AGENTS.md`; `security-guidelines` | Commands amended toward tier 1 and the decisions | Not relied on |

## 11. Corrections to the brief (unchanged from v2)

All are `unclear_requirements`, severity `minor`.

- **C1.** `tech-lead` also contradicts the user's rule at `:82` and `:90`.
- **C2.** `validation-gates` `:55`, `:67`, `:75` and `:132` do not fully agree with the rule.
- **C3.** There are further routes that let a security HIGH through. v3 now makes all of them required edits.
- **C4.** At the code-review gate, `code-review:96` is in tension with the rule for a security MEDIUM. This is P40 (D1).
- **C5.** The brief was verified at `1682077`; the worktree is at `dd7703b`.

## 12. Open questions and dependencies

- **Settled.**
  - Q1–Q4 were settled by the user.
  - v1's Q5 was settled by SEC-003.
  - v2's Q6 (does a security MEDIUM at the Release gate get fixed before shipping?) is settled. The orchestrator's
    SEC-012 scope decision and the reviewer texts (SEC-012, SEC-013) adopt "fixed before the release ships".
- **Q7 (open, for the user; not decided).** What is "the change under review" in a full-project `/security-audit`? The
  command's scope may be "full project", and SEC-015 defines code under review only relative to a change. B3 and B4 use
  the user's wording unchanged.
- **Q8 (open, minor).** Does a pre-existing gap graded HIGH, in code the change does not touch, block an unrelated
  change? SEC-015 covers adjacent code. Unrelated code is still governed by `security-guidelines:180–182` as written.
- **Q9 (for the orchestrator, minor).** Should R5 stay in FU-1? It is outside the SEC-012 list. My recommendation is to
  keep it (§6).
- **D1 (P40).** P40 is now schedulable under ADR-008. Slice S1 is settled here; S2–S4 remain. Nothing in v3 depends on
  them.

**Blockers:** none.

## 13. Unverified claims (need a shell)

1. No other contradicting text exists under `implementation/knowledge/` (v1 §9 #1 lists the unread files).
2. No golden case quotes or asserts the amended text (§8 search lists, with `held-out` pruned). The orchestrator has
   already settled `security-audit-critical-not-fail`.
3. Whether `prepare-release-conditional-pass-conditions-gap` quotes `:61`. The orchestrator has settled `:69` and the
   `release-manager` lines (§8).
4. No test outside `tests/golden/` asserts text in the eight files. The orchestrator has settled this for
   `release-manager`.
5. The `validate-workflow` case is unaffected, and nothing enforces byte-identity of its fixture copy.
6. The root-projection count.
7. Q2's "debt ledger" is `docs/artifacts/debt-ledger-v<N>.md`, as `technical-debt-tracking` defines it.
8. *(Settled by the orchestrator.)* ADR-008 is merged at `5eff98e`. I re-read its header and § Scope in the primary
   checkout, and they match what §§1.4–1.5 and §10 cite.

## 14. Summary

| Site | Ruling | Edits | Required? | Authority |
|---|---|---|---|---|
| `tech-lead:82, 90, 97` | Merge with tracked conditions; track rule; security exclusion; plan carried; SEC-015 adjacency | A1–A3 | Yes | ADR-008 B (P1) / T542-FU-C; P39; Q2, Q3 |
| `/code-review:51–52` | Same; non-security waiver only; MEDIUM plan survives a waiver | A4 | Yes | ADR-007 b1; Q1–Q3; SEC-011 |
| `validation-gates:55, 66–68, 75, 131–132` | PASS excludes the exclusion and medium; full security rule; Release-gate risk acceptance | A5–A8 | Yes | P39; Q2–Q4; SEC-003, SEC-009, SEC-013–SEC-016 |
| `testing-strategy:240` | Exclusion, with omitted controls | B1 | Yes | SEC-010; Q3 |
| `/security-audit:44, 45, 67, 73` | HIGH, constraint breach or omitted control → FAIL; MEDIUM plan; PASS strict | B2, B2b, B3, B4 | Yes | ADR-007 b1; SEC-002, SEC-017; Q3 |
| `code-review:150, 159`; `tech-lead:111` | No waiver for the exclusion; MEDIUM plan survives a waiver | C1, C3, C4 | Yes | Q1; SEC-001, SEC-011 |
| `release-manager:45, 181, 222` | No risk acceptance of a security finding; MEDIUM fixed before shipping; others deferred to the next cycle | R1–R3 | Yes | Q4; SEC-012 |
| `/prepare-release:61, 69` | Failed gate → FAIL; no security condition; Q4 shipping | R4, R5 | Yes | ADR-007 b1; Q4; SEC-012 (R4) |
| `code-review:151` | Due points | C2 | Optional | Q2 |
| `receiving-code-review:86` | Escalation never lifts an excluded FAIL | FU-7 | Follow-up | Reviewer |

## 15. Change log v2 → v3

| # | Item | Severity / source | v3 change | Where | Verbatim? |
|---|---|---|---|---|---|
| 1 | **SEC-009**: PASS row | MEDIUM | PASS now also requires "none of the security findings excluded below" | A6 | Yes |
| 2 | **SEC-010**: B1 | MEDIUM | Replaces SEC-005's After. It adds "nothing in the FAIL column" and the Q3 omitted-control class, "whatever its grade", with the pre-existing-gap parenthetical | B1 | Yes |
| 3 | **SEC-012**: Release-gate executor | MEDIUM; orchestrator widened scope | New edits R1, R2, R3 (`release-manager:45, 181, 222`) and R4 (`prepare-release:69`). A8 item 1 gains "with the explicit risk acceptance `release-manager` § Release Gate Policy requires". Authority is quoted for each (§1.3, §1.5, §10) | §6; A8 | Yes for R1–R4 and the A8 clause |
| 4 | **R5**: `prepare-release:61` | My finding, in SEC-012's scope | New edit. "conditions that must be met before deployment" contradicted Q4, `AGENTS.md:55`, and R4 within the same file | §6 R5; §12 Q9 | My wording, so FU-0 should see it |
| 5 | **SEC-011**: MEDIUM plan survives a waiver | LOW | Appended to C1 verbatim. Carried in substance into A4's FAIL line | C1, A4 | C1 yes; A4 in substance |
| 6 | **SEC-013**: A5 template | LOW | A5's After is replaced | A5 | Yes |
| 7 | **SEC-014**: low security findings | LOW | Appended to A6's bold paragraph | A6 | Yes |
| 8 | **SEC-015**: adjacency | LOW | Appended after the pre-existing-gap sentence in A3, A4, A6 and B3. **Q7 is recorded as open for the user, not decided** | A3, A4, A6, B3; §12 | Yes |
| 9 | **SEC-016**: control findings are security findings | LOW | Inserted after A6's definition sentence; also added to §1.7 | A6; §1.7 | Yes |
| 10 | **SEC-017**: B2b required | LOW | B2b moves from optional to Batch B. FU-1 checks for 0 hits of `Potential risk, schedule for next sprint` | B2b; §9 | Yes |
| 11 | **FU-7** | LOW | Added as a tracked follow-up with the reviewer's text. It is **not** an edit | §9 | Yes |
| 12 | **FU-6** (SEC-008) | LOW | Kept as a follow-up | §9 | — |
| 13 | A6 sentence order | Mine (precision) | "None of these is ever recorded as debt." moves before the pre-existing-gap sentence, so that "these" cannot take in a low-graded pre-existing gap, which SEC-014 makes debt | A6 | Content unchanged |
| 14 | **ADR-008 Accepted** | Orchestrator | The authority basis now cites ADR-008: Step B (P1) for `tech-lead` A1–A3; § Scope ("recorded user decision governs") for Q1–Q4 edits; Step A notes for security; P4 (maturity not relied on). D5 records added (§10). ADR-008 is merged at `5eff98e` and cited by path and section | §1.4, §1.5, §10, §9 | — |
| 15 | P40 | — | Slice S1 is recorded as settled by P39 as applied here. S2–S4 remain (D1) | §9, §12 | — |
| 16 | `/prepare-release` and `release-manager` golden/tests | Orchestrator-verified | Maturities and the absence of coupling to `:69` and to `release-manager:45, 181, 222` are recorded as verified. `prepare-release-conditional-pass-conditions-gap` probably quotes `:61` (R5): **unverified**, a search is given, and it is added to FU-2 if it hits | §8, §9 | — |
| 17 | Verification | — | 21 required Befores. New 0-hit patterns (`conditions that must be met before deployment`, `unresolved critical QA or security findings remain`, `(or \`CONDITIONAL_PASS\` with listed conditions)`). New counts (`next release cycle` in `release-manager` and `prepare-release`, adjacency sentence ×4, `A finding about a control that`, `A security finding graded low is not a condition`, `A waiver that lifts a`, `Risk acceptance never covers a security finding`) | §9 | — |
| 18 | Q6 | — | Recorded as settled by SEC-012 and SEC-013 | §12 | — |
| 19 | **Unchanged from v2** | — | Every v2 `Before:`; the Afters of A1, A2, A7, B2, B4, C2, C3 and C4; A6's CONDITIONAL_PASS and FAIL rows; §11 C1–C5; FU-3; FU-5 | — | — |
