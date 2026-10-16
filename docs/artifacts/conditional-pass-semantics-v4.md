# Artifact: conditional-pass-semantics-v4.md

> Filename: `conditional-pass-semantics-v4.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T580 (P2, P39), fourth version
- **Created**: 2026-10-02
- **Based on**:
  - `docs/artifacts/conditional-pass-semantics-v3.md` (superseded by this version) and, through it, v1 and v2;
  - the Security Engineer's **phrase check of v3: CONDITIONAL_PASS**. Every v2 condition is adopted. Two required items
    remain, SEC-018 and SEC-019, plus SEC-020 and SEC-021 to include. The orchestrator relayed them and diffed v3
    against the relayed After texts: verbatim. I did not read the review record itself;
  - the **user decisions on Q7 and Q8** (2026-10-02, relayed verbatim; §1.6);
  - the orchestrator's verified golden finding for `prepare-release-conditional-pass-conditions-gap` (§8);
  - `docs/decisions/ADR-008-knowledge-document-authority.md`: Accepted, merged on `develop` at `5eff98e`. I read it in
    the primary checkout and cite it by path and section; this worktree is at `dd7703b`;
  - `ADR-007` (Accepted); `poc-contract-resolution-v1.md` §9.2; the user's P39 rule and Q1–Q4 decisions;
  - source files at `dd7703b`, as listed in v1 and v3 Metadata.
- **Supersedes**: `conditional-pass-semantics-v3.md`. v1, v2 and v3 stay unchanged. **Where they differ, v4 governs.
  FU-1 applies v4 only.**
- **Decision references**: P39; the user's Q1–Q4, Q7 and Q8; ADR-007 branch 1; ADR-008 Step A, Step B (P1) and § Scope;
  the T542/FU-C precedent. No new ADR.

## 0. What this document is, and what it did not do

This is the complete, standalone ruling for P39, with exact edits for FU-1. §15 lists every v3→v4 change. **It changed
no agent, skill, command, instruction or golden case.**

**Method and limits.**
- **No shell.** Unverified claims are marked **(unverified)** (§13).
- **Golden.** I opened only `code-review-conditional-pass-conditions-gap/{brief.md,expect.py}`, under the v1 grant.
  Nothing else under `tests/golden/`, and nothing under `held-out/`.
- **Before texts.** Every `Before:` is byte-identical to v3, and v4 adds no new Before. Apply each edit by its text, not
  by line number. Line numbers are at `dd7703b`.
- **Characters and fences.** `—` is U+2014 and `§` is U+00A7. There is one four-backtick fence per edit, each beginning
  `Before:`.

## 1. Authority basis

### 1.1 The user's P39 rule (2026-10-02, verbatim)

> "CONDITIONAL_PASS allows merge with conditions tracked (closed before the next gate on production; PoC debt due by
> handoff). FAIL blocks. Security HIGH/CRITICAL and constraint breaches never qualify for CONDITIONAL_PASS. The
> experimental /code-review command and tech-lead agent get amended to match AGENTS.md." The user chose: **"Adopt it
> (Recommended)"**.

### 1.2 `AGENTS.md`

- § Validation Gates `:54–55`: "`FAIL` blocks progression." and "`CONDITIONAL_PASS` proceeds with tracked conditions
  added to the task list."
- § Task Protocol `:18`: "Only orchestrators create/transition tasks."

### 1.3 Commands: ADR-007 branch 1 (= ADR-008 P1(d))

Branch 1 asks: "Does the clause contradict `AGENTS.md`, a `stable` instruction, or another clause of the same command
file? If yes, the command is wrong regardless of what the corpus does."

| Command edit | Prong | Contradiction, quoted from both sides |
|---|---|---|
| A4 `/code-review:51–52` | `AGENTS.md` | `:55` says "proceeds with tracked conditions". The command says "conditions that must be met before merge", at a gate that sits "before merge" (`validation-gates:26`). |
| B2, B2b, B3, B4 `/security-audit:44,45,67,73` | stable instruction | `security-guidelines:182–183` against: FAIL for CRITICAL only; HIGH "fix within current sprint"; MEDIUM "schedule for next sprint". |
| R4 `/prepare-release:69` | `AGENTS.md`; stable instruction | `:54` "`FAIL` blocks progression" against "a quality gate has failed … (or `CONDITIONAL_PASS` …)". `security-guidelines:153` against a blocker carried as a condition. |
| R5 `/prepare-release:61` | `AGENTS.md`; same file | `:55` "proceeds" against "conditions that must be met before deployment" (at this gate, proceeding is shipping). It is also incoherent with R4. |

ADR-007 §5 ("never relax a check") is respected. The only latitude granted is the user's Q4, which lets a release ship
with non-security conditions.

### 1.4 Agents: ADR-008 Step B (P1), which is the T542/FU-C precedent

`tech-lead:97` says "Merge is blocked until conditions are resolved". `AGENTS.md:55` says proceed. That is one merge
decision with two values, so Step A fails. **Step B fires**: `AGENTS.md` "declares no scope narrower than the
repository" (ADR-008 D2). The lower document is amended toward tier 1. `tech-lead:29–30` and `:68` corroborate this.

### 1.5 Skills, the waiver and the Release gate: Step A, then the recorded user decisions

ADR-008 § Scope, "Not covered", says: "A question already settled by an accepted ADR or a recorded user decision. That
decision governs, and documents are amended to it."

| Site | Step A | What governs |
|---|---|---|
| `validation-gates` (A5–A8); `testing-strategy:240` (B1) | The security permission ("documented mitigations") and `security-guidelines` `:153`/`:182` are jointly satisfiable by withholding the permission. The untracked due points fail. | P39, Q2–Q4, Q7 (§ Scope). Step A notes for security. |
| `code-review:150, 159`; `tech-lead:111` (C1, C3, C4) | The waiver is a permission and the instruction a prohibition, so Step A holds. | Q1 (§ Scope). |
| `release-manager:45, 181, 222` (R1–R3) | Fails for a security MEDIUM against Q4. Holds for HIGH/CRITICAL once A6 applies. | Q4 (§ Scope). Step A notes. |

**P4.** Maturity is not relied on anywhere.

### 1.6 User decisions (2026-10-02, verbatim)

| Question | Decision | Applied in |
|---|---|---|
| Q1: keep the Tech Lead waiver for non-security FAILs? | **"Keep it, except for security (Recommended)"** | A4, C1, C3, C4 |
| Q2: what does PoC "debt due by handoff" mean? | **"Recorded by handoff (Recommended)"**: in the debt ledger and scorecard by the production handoff, and fixed in production. Security breaches are never debt. The `poc-orchestrator` § Security Findings and `poc-security-engineer:23` security-MEDIUM deadline governs as the more specific rule. | A1, A3–A6, A8, C2 |
| Q3: does the omitted-control class apply on production too? | **"Both tracks (Recommended)"**. It is scoped to the code under review. Pre-existing gaps outside the change are graded at their own severity and tracked. | A3, A4, A6, B1, B3, B4, C1, C3, C4, R1, R5 |
| Q4: when do Release-gate conditions close? | **"Next release cycle"**. A Release-gate CONDITIONAL_PASS may ship, with its conditions tracked as tasks for the next release cycle. This never applies to security findings. | A5, A6, A8, R1–R5 |
| Q7: what is the code under review for a full-project `/security-audit` with no diff? | **"Whole project (Recommended)"**. With no change under review, the audit's scope is the code under review. A missing required control anywhere blocks the audit verdict. | §1.7; A6, B3, B4 |
| Q8: does a pre-existing security HIGH in untouched code block an unrelated MR? | **"Yes, block (Recommended)"**. The fail-safe default stands as written: "graded HIGH … whoever raised it", with no scope limit. | No text change (§12) |

### 1.7 Defined terms

- **Security finding.** Any finding in the security category, whichever gate or executor raises it, graded on the
  `security-guidelines.md` § Security Review Workflow scale. A finding about a control that `security-guidelines.md`
  requires is a security finding, whatever category it is filed under.
- **The security exclusion.** These items never qualify for CONDITIONAL_PASS. They are never waived, never
  risk-accepted, never recorded as debt, and never shipped:
  - a security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH`, wherever it is in the code (Q8);
  - a breach of an Immutable Security Constraint;
  - a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed,
    disabled or weakened, whatever its grade, tagged or not.
- **Code under review** (Q3, SEC-015, Q7).
  - It is the change under review.
  - A change that adds or alters code which a missing control should protect is code under review for that control.
  - **With no change under review (for example a full-project `/security-audit`), the whole project is the code under
    review.**
  - A required control missing only from code outside the change under review is graded at its own severity and
    tracked.
  - **Consequence (Q7):** older projects may need a remediation pass before a full-project audit can give PASS.
- **The track rule.**

  | Situation | Rule |
  |---|---|
  | Production | Conditions close before the next gate. |
  | Release gate | Conditions become tasks for the next release cycle, after `release-manager`'s risk acceptance. |
  | PoC | Conditions are recorded as debt by the production handoff and fixed in production. |
  | Security finding graded medium | Fixed before the next gate. At the Release gate, before the release ships. On PoC, by its plan deadline, no later than the handoff. |
  | Security finding graded low | Not a condition. Tracked as technical debt. |

## 2. Ruling on the `validation-gates:67` security nuance

**Amend `validation-gates` itself** (A5–A8).
- **Documented mitigations.** That route covers only high findings outside the security category.
- **The security exclusion** (§1.7). It yields FAIL until resolved, with no waiver, on both tracks (SEC-021).
- **PASS.** PASS requires none of the following: a critical or high finding, a security finding graded medium, or an
  excluded finding.
- **A security finding graded medium** yields at best CONDITIONAL_PASS. Its plan is recorded before the affected work's
  next merge. Its fix is due under the track rule.
- **A security finding graded low** is not a condition.
- **Q7.** With no change under review, the whole project is under review.

`:74`'s tier misalignment is a follow-up only (FU-6).

## 3. Batch A: required

### A1: `tech-lead.md:82`

````
Before:
- [ ] [Condition 1 — must be resolved before merge]

After:
- [ ] [Condition 1 — owner; due point: before the next gate (production track), or recorded as debt in the debt ledger and scorecard by the production handoff (PoC track); a security finding also carries its remediation plan (owner, fix, deadline)]
````

### A2: `tech-lead.md:90`

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

**Authority:** ADR-008 Step B (P1), which is the T542/FU-C precedent; P39; Q2, Q3. Unchanged from v3.

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

**Authority:** ADR-007 branch 1, `AGENTS.md` prong; Q1–Q3. Unchanged from v3.

**Why no Q7 sentence here.** `/code-review` reviews files or a diff. Its own `{{input}}` names "files or describe what to
review", so there is always a review target. Where that target has no diff, the target's files are the code under
review. The Q7 sentence goes where an audit can run with no change at all: A6, B3 and B4.

### A5: `validation-gates/SKILL.md:55`

````
Before:
- [ ] <condition that must be met before proceeding>

After:
- [ ] <condition> — owner: <who>; due: before the next gate (production track; at the Release gate, the next release cycle, except a security finding, which is fixed before the release ships) | recorded as debt in the debt ledger and scorecard by the production handoff (PoC track; a security finding graded medium is fixed by its remediation-plan deadline, no later than the handoff); a security finding also carries its remediation plan (owner, fix, deadline)
````

**Unchanged from v3.**

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

**Security findings never qualify for CONDITIONAL_PASS.** A security finding is any finding in the security category, whichever gate or executor raises it, graded on the `security-guidelines.md` § Security Review Workflow scale (`SECURITY:CRITICAL`/`HIGH`/`MEDIUM`/`LOW`); the Findings table records that grade as its Severity and `security` as its Category. A finding about a control that `security-guidelines.md` requires is a security finding, whatever category it is filed under. `security-guidelines.md` § Security Review Workflow: "`CRITICAL` and `HIGH` findings block merge until resolved". A security finding graded critical or high, and any breach of an Immutable Security Constraint in `security-guidelines.md` (which "cannot be overridden by any agent, configuration, or runtime decision"), yields FAIL until it is resolved, whatever mitigation is documented, and no waiver applies to it. The "documented mitigations" route above is for high findings outside the security category only. The same FAIL rule, with no waiver, holds for any security control `security-guidelines.md` requires for the code under review that is omitted, removed, disabled or weakened, tagged or not (on the PoC track, `poc-orchestrator` § Security Findings). None of these is ever recorded as debt. A required control missing only from code outside the change under review is graded at its own severity and tracked like any other finding of that grade. A change that adds or alters code which the missing control should protect is code under review for that control. With no change under review (for example a full-project `/security-audit`), the whole project is the code under review. A security finding graded medium yields at best CONDITIONAL_PASS: its remediation plan (owner, fix, deadline) is recorded as a tracked condition with the verdict, before the affected work's next merge (`security-guidelines.md` § Security Review Workflow: "`MEDIUM` findings must have a remediation plan before merge"); the condition is the fix, due under the track rule above (production: before the next gate; PoC: by the production handoff, as `poc-orchestrator` § Security Findings already requires). The next-release-cycle rule never applies to a security finding: at the Release gate, a security finding graded medium is fixed before the release ships. A security finding graded low is not a condition: it is tracked as technical debt (`security-guidelines.md` § Security Review Workflow; on the PoC track, recorded for debt handoff per `poc-orchestrator` § Security Findings).
````

**v3→v4 changes in A6:**
- **SEC-021, verbatim.** "The same holds" becomes "The same FAIL rule, with no waiver, holds".
- **The Q7 sentence**, inserted after the SEC-015 sentence.

**Why A6 gets the Q7 sentence, as well as B3 and B4 (stated equivalent).** The orchestrator named §1.7 and B3/B4. A6
also needs it because `validation-gates` § Security Gate takes "Full codebase scan results" as an input (`:100`). Without
the sentence, a Security-gate verdict on a full scan would leave "the change under review" undefined, which is exactly the
Q7 gap. The sentence is the user-decision example sentence, unchanged. **The orchestrator can drop it from A6 without
affecting any other edit.** The FU-1 count for `the whole project is the code under review` in `validation-gates` then
becomes 0.

### A7: `validation-gates/SKILL.md:75`

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

## 4. Batch B: required

### B1: `testing-strategy/SKILL.md:240`

````
Before:
| **Security scan** | No critical/high findings | No critical; high findings have mitigations | Any critical finding |

After:
| **Security scan** | No critical, high or medium findings, and nothing in the FAIL column | No critical or high findings and nothing in the FAIL column; each medium finding has a remediation plan (`security-guidelines.md` § Security Review Workflow) | Any critical or high finding, any breach of an Immutable Security Constraint (`security-guidelines.md`), or any security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, whatever its grade (a control missing only from code outside the change is graded at its own severity; a change that adds or alters code which the missing control should protect is code under review for that control) |
````

**Source:** SEC-010 with SEC-019's parenthetical, both verbatim.

**Why there is no Q7 sentence in B1.** The QA security scan runs at the integration gate, "after feature merge"
(`validation-gates:27`), on a change. The orchestrator did not list B1 for Q7. If a full-project scan is ever run there,
A6's sentence covers it.

### B2: `commands/security-audit.md:44`

````
Before:
   - **HIGH**: Exploitable with moderate effort, fix within current sprint

After:
   - **HIGH**: Exploitable with moderate effort; blocks merge until resolved (`security-guidelines.md` § Security Review Workflow)
````

### B2b: `commands/security-audit.md:45`

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
If any CRITICAL or HIGH finding exists, or any Immutable Security Constraint in `security-guidelines.md` is breached, or any security control that `security-guidelines.md` requires for the code under review is omitted, removed, disabled or weakened, the verdict MUST be FAIL (`security-guidelines.md` § Security Review Workflow: "`CRITICAL` and `HIGH` findings block merge until resolved"). A required control missing only from code outside the change under review is graded at its own severity. A change that adds or alters code which the missing control should protect is code under review for that control. With no change under review (for example a full-project `/security-audit`), the whole project is the code under review. If any MEDIUM finding exists, the verdict is at best CONDITIONAL_PASS, with a remediation plan (owner, fix, deadline) listed as a condition for each MEDIUM finding. PASS requires no CRITICAL, HIGH or MEDIUM finding.
````

**Source:** v3, with the Q7 sentence inserted.

### B4: `commands/security-audit.md:73`

````
Before:
**Failure mode**: If any CRITICAL finding exists, the verdict MUST be FAIL — the command cannot return PASS/CONDITIONAL_PASS while a CRITICAL finding is unresolved.

After:
**Failure mode**: If any CRITICAL or HIGH finding exists, an Immutable Security Constraint is breached, or a security control that `security-guidelines.md` requires for the code under review is omitted, removed, disabled or weakened, the verdict MUST be FAIL — the command cannot return PASS/CONDITIONAL_PASS while such a finding is unresolved. With no change under review (for example a full-project `/security-audit`), the whole project is the code under review.
````

**Source:** v3, with the Q7 sentence appended.

**B2–B4 authority:** ADR-007 branch 1, stable-instruction prong; Q3; Q7.

## 5. Batch C: required (C1, C3, C4)

### C1: `code-review/SKILL.md:150`

````
Before:
1. A `FAIL` verdict blocks the merge request — no override without Tech Lead waiver (documented as a decision artifact).

After:
1. A `FAIL` verdict blocks the merge request — no override without Tech Lead waiver (documented as a decision artifact). No waiver applies to a security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH`, whoever raised it, to a breach of an Immutable Security Constraint, or to a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened: `security-guidelines.md` says "`CRITICAL` and `HIGH` findings block merge until resolved" (§ Security Review Workflow), and that its Immutable Security Constraints "cannot be overridden by any agent, configuration, or runtime decision". A waiver that lifts a `FAIL` with a security finding graded `SECURITY:MEDIUM` among its causes does not lift that finding's remediation plan (owner, fix, deadline), which is recorded as a tracked condition before merge (`security-guidelines.md` § Security Review Workflow).
````

### C3: `code-review/SKILL.md:159`

````
Before:
**Failure mode**: A `FAIL` verdict halts the pipeline and requires re-review after fixes; a `FAIL` may not be overridden without a documented Tech Lead waiver decision artifact.

After:
**Failure mode**: A `FAIL` verdict halts the pipeline and requires re-review after fixes; a `FAIL` may not be overridden without a documented Tech Lead waiver decision artifact, and a `FAIL` for a security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH`, whoever raised it, for a breach of an Immutable Security Constraint, or for a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, may not be overridden at all (§ Review as Validation Gate).
````

### C4: `tech-lead.md:111`

````
Before:
3. Require explicit waiver reference for any approved exception and escalate unresolved conflicts to orchestrator.

After:
3. Require explicit waiver reference for any approved exception and escalate unresolved conflicts to orchestrator. No waiver applies to a security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH`, whoever raised it, to a breach of an Immutable Security Constraint, or to a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened (`security-guidelines.md` § Security Review Workflow, § Immutable Security Constraints). A waiver that lifts a `FAIL` with a security finding graded `SECURITY:MEDIUM` among its causes does not lift that finding's remediation plan (owner, fix, deadline), which is recorded as a tracked condition before merge.
````

**Source:** v3, with SEC-020 appended verbatim.

**C1, C3, C4 authority:** Q1 (ADR-008 § Scope), with the Step A relationship to `security-guidelines` `:153` and `:182`.
The precedent is `rapid-prototyping:74`.

## 6. Batch R: Release-gate executor (required)

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

**R1–R3 authority:** Q4 (ADR-008 § Scope), with Step A notes. `release-manager` is `stable`; maturity is not relied on.

### R4: `commands/prepare-release.md:69`

````
Before:
**Failure mode**: If a quality gate has failed or a blocker is open, the VERDICT is `FAIL` (or `CONDITIONAL_PASS` with listed conditions) rather than a silent `PASS`.

After:
**Failure mode**: If a quality gate has failed, the VERDICT is `FAIL`. If a blocker is open, the VERDICT is `FAIL`, or `CONDITIONAL_PASS` with listed conditions only when no security finding is among them (skill `validation-gates` § Verdict Rules), rather than a silent `PASS`.
````

### R5: `commands/prepare-release.md:61`

````
Before:
9. If CONDITIONAL_PASS, list conditions that must be met before deployment

After:
9. If CONDITIONAL_PASS, list the conditions. The release may ship with each condition tracked as a task for the next release cycle, after the explicit risk acceptance `release-manager` § Release Gate Policy requires. A security finding is never such a condition (skill `validation-gates` § Verdict Rules): a `SECURITY:CRITICAL` or `SECURITY:HIGH` finding blocks the release, and so does a breach of an Immutable Security Constraint or a required security control omitted, removed, disabled or weakened, whatever its grade; a `SECURITY:MEDIUM` finding is fixed before the release ships; a `SECURITY:LOW` finding is not a condition and is tracked as technical debt.
````

**Source:** SEC-018, verbatim. It replaces v3's R5, which routed by grade alone and so got two cases wrong:
- a security LOW blocked the release;
- a MEDIUM-graded constraint breach or omitted control fell into "fixed before ships" instead of blocking.

**R4, R5 authority:** ADR-007 branch 1 (§1.3); Q4. R5 also restores same-file coherence with R4.

## 7. Optional

### C2: `code-review/SKILL.md:151`

````
Before:
2. A `CONDITIONAL_PASS` verdict allows merge but **requires** that each should-fix item is logged as a task in `docs/tasks/active-tasks.md` with an assigned owner and target sprint.

After:
2. A `CONDITIONAL_PASS` verdict allows merge but **requires** that each should-fix item is logged as a task in `docs/tasks/active-tasks.md` with an assigned owner and target sprint. On the production track the item is resolved before the next gate; on the PoC track it becomes a debt item, recorded in the debt ledger and the debt scorecard by the production handoff and fixed in production (`poc-guidelines.md` § Mandatory Debt Tracking, § Debt Scorecard), unless `poc-orchestrator` § Security Findings sets a security finding's fix deadline no later than the production handoff, which governs.
````

## 8. Golden coupling and blast radius

**Known coupling.** In every case below, the result is unchanged because `check()` reads only the fixture.

| Case | Stale quotes | Edit | Verified by |
|---|---|---|---|
| `code-review-conditional-pass-conditions-gap` | `brief.md:11–12`; `expect.py:4–5` docstring | A4 | Me, under grant |
| `security-audit-critical-not-fail` | `brief.md:13`; `expect.py:5` docstring; `case.yaml` `known_failing_reason` | B3 | Orchestrator |
| `prepare-release-conditional-pass-conditions-gap` | `case.yaml:6–7`; `brief.md:12`; `expect.py:6` docstring (quoting `:61`, "list conditions that must be met before deployment") | R5 | Orchestrator |

**Premises.** In all three cases the premise still holds.
- **A4 and R5** name no `**Conditions**:` field and no list format. R5 adds per-condition rules, not a schema
  **(R5's premise is reasoned; I did not read that case)**.
- **B3** still forces FAIL for CRITICAL.

**Fixture copy.** In `validate-workflow-gate-verdict-sources`, the fixture copy of `validation-gates` will no longer be
byte-identical to the source. The lines it reads are untouched **(unverified)**.

**Verified by the orchestrator:**
- `release-manager.md` is `stable` and `prepare-release.md` is `experimental`.
- No open case quotes `prepare-release.md:69`.
- The only test mentioning `release-manager`, `test_validation_gates_skill_contract.py`, does not touch `:45`, `:181`
  or `:222`.

**Held-out cases** are covered only through `scripts/scorecard.py --check`.

**Files:**

| File | Edits | Maturity (not relied on) |
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
- There are 21 required edits plus optional C2, in 8 files.
- Run `sync.mjs --root implementation` and `generate-registry.py`, each with `--check`.
- Declare the root drift exactly as `--print-drift` reports it **(count unverified, up to 8 × 7)**.
- Expect no maturity effect at P2. **Affects:** `—`.

**Unchanged:** `AGENTS.md`, `security-guidelines.md`, `poc-guidelines.md`, `orchestrator.md`, the PoC agents,
`rapid-prototyping`, `security-engineer.md`, `release-workflow`, `receiving-code-review`, `tests/golden/**`.

**Behavioural consequences:**
- **Production security gate.** An omitted control graded medium in the code under review now yields FAIL.
- **Release.** A `SECURITY:MEDIUM` finding is fixed before shipping. Other conditions are risk-accepted and deferred to
  the next release cycle. A `SECURITY:LOW` finding is technical debt.
- **Q7.** A full-project `/security-audit` treats the whole project as the code under review. **An older project may
  need a remediation pass before it gets PASS.**
- **Q8.** A pre-existing security HIGH blocks unrelated MRs until it is resolved.

## 9. Follow-ups

| ID | Covers | Files | `tests/golden/**` grant? | Owner (suggested) | Priority | Depends on / verify |
|---|---|---|---|---|---|---|
| **FU-0**: phrase check of v4 | SEC-018 … SEC-021; the Q7 sentence in A6, B3, B4 | this artifact | No | Security Engineer or orchestrator | P2 | A6's Q7 placement is my stated equivalent (§3 A6) |
| **FU-1**: apply P39 per **v4** | 21 required edits (A1–A8, B1–B4, B2b, C1, C3, C4, R1–R5); C2 optional | §8 table; mirrors; registry; root drift | **No** | Backend Developer | P2 | FU-0; dispatch from a `develop` that includes ADR-008 (`5eff98e`). Verify as below |
| **FU-2**: refresh stale golden quotes | The three cases in §8 | Only the files named there | **Yes** (`protected-paths-v1.md` §5, scoped to these three case directories); a baseline authorization if an `expect.py` changes | QA Engineer | P2 | After FU-1. Results unchanged. Not ruled |
| **FU-3**: `validate-workflow` fixture copy of `validation-gates` | Provenance | That case's fixture copy and brief | **Yes** | QA Engineer | P2 | Only if byte-identity must hold or is test-enforced |
| **FU-5** *(candidate)*: structured `**Conditions**:` field | `/code-review`, `/prepare-release` capability gaps | Commands; case classification | **Yes** | Solution Architect, then QA | P2 | A separate ADR-007 decision |
| **FU-6** (SEC-008) | `security-engineer.md:81–83` SLA table; `validation-gates:74` tiers; `security-engineer.md:152–153` not naming the Q3 class or Q7 scope | `security-engineer.md`; `validation-gates/SKILL.md:74` | No | Solution Architect, then Backend Developer | P2 | Follow-up only |
| **FU-7** | `receiving-code-review:86`: "Escalation never lifts a `FAIL` caused by a finding that skill `code-review` § Review as Validation Gate excludes from waiver." | `receiving-code-review/SKILL.md` | No | Orchestrator scopes it | P2 | After FU-1 |
| **D1** (P40) | Slices S2–S4 (S1 settled by P39 here) | — | — | — | — | Schedulable under ADR-008 |

**FU-1 verification:**

1. **Each Before matches once.** Each of the 21 required `Before:` texts, and C2's if applied, matches **exactly once by
   text** on `develop` at dispatch.

2. **Zero hits** under `implementation/knowledge/` for:
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
   - `` (or `CONDITIONAL_PASS` with listed conditions) ``

3. **Exact hit counts** (case-sensitive):

   | Phrase | Expected hits |
   |---|---|
   | `Security findings never qualify for CONDITIONAL_PASS` | 1 (`validation-gates`) |
   | `The same FAIL rule, with no waiver` | 1 (`validation-gates`) |
   | `Yes, with conditions tracked` | 1 (`tech-lead`) |
   | `whoever raised it` | `tech-lead.md` 2; `commands/code-review.md` 1; `skills/code-review/SKILL.md` 2 |
   | `next release cycle` | `validation-gates` 3 (A5, A6 row, A8); `release-manager.md` 2 (R1, R2); `prepare-release.md` 1 (R5) |
   | `adds or alters code which the missing control should protect` | 1 each in `tech-lead.md`, `commands/code-review.md`, `validation-gates`, `security-audit.md`, `testing-strategy` |
   | `the whole project is the code under review` | `security-audit.md` 2 (B3, B4); `validation-gates` 1 (A6; 0 if the orchestrator drops it from A6) |
   | `A finding about a control that` | 1 (`validation-gates`) |
   | `A security finding graded low is not a condition` | 1 (`validation-gates`) |
   | `A waiver that lifts a` | `skills/code-review/SKILL.md` 1 (C1); `tech-lead.md` 1 (C4). A4's lowercase "a waiver that lifts a FAIL" is not counted. |
   | `Risk acceptance never covers a security finding` | 1 (`release-manager.md`) |
   | `A security finding is never such a condition` | 1 (`prepare-release.md`) |
   | `whatever its grade` | 1 each in `testing-strategy` and `prepare-release.md` |
   | `A security finding listed as a condition carries its remediation plan` | 1 each in `tech-lead.md` and `commands/code-review.md` |

4. **Byte-unchanged:** `AGENTS.md`, `security-guidelines.md`, `poc-guidelines.md`, the PoC agents,
   `security-engineer.md`, `release-workflow`, `receiving-code-review`, `tests/golden/**`.
5. **Generators clean.** `sync.mjs --check` and `generate-registry.py --check` pass, and the root parity gate is green.
6. **Scorecard unchanged.** `scripts/scorecard.py --check` matches the current baseline. A regression means held-out
   coupling: stop and report it.
7. **Maturity clean.** `check-maturity.py --root implementation` reports 0 failing.
8. **Task and test runs.** `validate-tasks.py` passes. For `tests/run.py`, check the exit code and redirect its output to
   a file.
9. **Fixture copy.** Report a `cmp` of the `validate-workflow` fixture copy of `validation-gates`. A difference is
   expected; the case result must be unchanged.

## 10. ADR-008 D5 records

| Ruling | Subject (D3) | Clauses | Step A | Step fired | Declared scope relied on | Amendment | Maturity |
|---|---|---|---|---|---|---|---|
| A1–A3 | Merge effect of CONDITIONAL_PASS at the code-review gate | `tech-lead:82, 90, 97` vs `AGENTS.md:55` | Fails (one merge decision, two values) | **B (P1)** | `AGENTS.md` (repository-wide, D2); `tech-lead:29–30`, `:68` | Agent amended toward `AGENTS.md`, citing it | Not relied on |
| C1, C3, C4 | Waiver of a security FAIL; the MEDIUM plan surviving a waiver | `code-review:150, 159`; `tech-lead:111` vs `security-guidelines:153, 182–183` | Holds (a permission against a prohibition) | **§ Scope**: Q1; Step A note | `security-guidelines` Rails `:15–24`, `applyTo: "**"` | Carve-out stated, citing the instruction | Not relied on |
| A5–A8, B1 | Verdict criteria, due points, code under review | `validation-gates:55, 66–68, 75, 131–132`; `testing-strategy:240` vs P39, Q2–Q4, Q7 and `security-guidelines` | Holds for the security permission; fails for the untracked due points | **§ Scope**: P39, Q2–Q4, Q7; Step A note (Step B if read strictly, P40 S1) | As above | Skills amended to the decisions | Not relied on |
| R1–R3 | Release-gate risk acceptance of security findings | `release-manager:45, 181, 222` vs Q4 | Fails for a security MEDIUM against Q4 | **§ Scope**: Q4; Step A note | — | Agent amended to Q4 | Not relied on |
| A4, B2–B4, B2b, R4, R5 | Command clauses | §1.3 table | Fails | **B (P1) = ADR-007 branch 1**; Q4 (R4, R5); Q7 (B3, B4) | `AGENTS.md`; `security-guidelines` | Commands amended toward tier 1 and the decisions | Not relied on |

## 11. Corrections to the brief (unchanged)

These are `unclear_requirements`, severity `minor`.

- **C1.** `tech-lead` also contradicts the rule at `:82` and `:90`.
- **C2.** `validation-gates` `:55`, `:67`, `:75` and `:132` do not fully agree.
- **C3.** There are further routes for a security HIGH; v4 covers all of them.
- **C4.** `code-review:96` is in tension with the brief's statement for a security MEDIUM; this is P40 (D1).
- **C5.** The brief was verified at `1682077`; the worktree is at `dd7703b`.

## 12. Open questions and dependencies

**Settled:**
- Q1–Q4 and Q7 by the user.
- Q8 by the user ("Yes, block (Recommended)"). The fail-safe default stands, with no text change: "graded … `SECURITY:HIGH` …,
  whoever raised it" carries no scope limit, so a pre-existing security HIGH in untouched code blocks an unrelated MR.
- v1's Q5 by SEC-003.
- Q6 by SEC-012 and SEC-013.
- Q9 (keep R5) by the reviewer's SEC-018 After text for R5.

**Open:**
- **D1 (P40).** Slices S2–S4, including `code-review:96`/`:128` against a security MEDIUM at the code-review gate.
  Nothing in v4 depends on them.

**Blockers:** none.

## 13. Unverified claims (need a shell)

1. No other contradicting text exists under `implementation/knowledge/`. v1 §9 #1 lists the files I did not read.
2. No other golden case quotes the amended text. The three cases in §8 are settled; held-out is covered only by
   `scorecard.py --check`.
3. No test outside `tests/golden/` asserts text in the eight files. This is settled for `release-manager`.
4. The `validate-workflow` case is unaffected, and nothing enforces byte-identity of its fixture copy.
5. The root-projection count.
6. The "debt ledger" is `docs/artifacts/debt-ledger-v<N>.md` (`technical-debt-tracking`).
7. `prepare-release-conditional-pass-conditions-gap`'s premise survives R5. Its result is unchanged (orchestrator); the
   premise is reasoned by analogy.

## 14. Summary

| Site | Ruling | Edits | Required? | Authority |
|---|---|---|---|---|
| `tech-lead:82, 90, 97` | Merge with tracked conditions; track rule; security exclusion; plan carried; adjacency | A1–A3 | Yes | ADR-008 B (P1), which is T542/FU-C; P39; Q2, Q3 |
| `/code-review:51–52` | Same; non-security waiver only; MEDIUM plan survives a waiver | A4 | Yes | ADR-007 b1; Q1–Q3 |
| `validation-gates:55, 66–68, 75, 131–132` | Full security rule ("same FAIL rule, with no waiver"); Q7 scope; Release-gate risk acceptance | A5–A8 | Yes | P39; Q2–Q4, Q7; SEC-003, SEC-009, SEC-013–SEC-016, SEC-021 |
| `testing-strategy:240` | Exclusion with omitted controls and adjacency | B1 | Yes | SEC-010, SEC-019; Q3 |
| `/security-audit:44, 45, 67, 73` | HIGH, constraint breach or omitted control → FAIL; Q7 whole project; MEDIUM plan; PASS strict | B2, B2b, B3, B4 | Yes | ADR-007 b1; SEC-002, SEC-017; Q3, Q7 |
| `code-review:150, 159`; `tech-lead:111` | No waiver for the exclusion; MEDIUM plan survives a waiver | C1, C3, C4 | Yes | Q1; SEC-001, SEC-011, SEC-020 |
| `release-manager:45, 181, 222` | No risk acceptance of a security finding | R1–R3 | Yes | Q4; SEC-012 |
| `/prepare-release:61, 69` | Failed gate → FAIL; security exclusion blocks whatever its grade; MEDIUM fixed before shipping; LOW is debt; Q4 shipping | R4, R5 | Yes | ADR-007 b1; Q4; SEC-012, SEC-018 |
| `code-review:151` | Due points | C2 | Optional | Q2 |
| `receiving-code-review:86` | Escalation never lifts an excluded FAIL | FU-7 | Follow-up | Reviewer |

## 15. Change log v3 → v4

| # | Item | Source | v4 change | Where | Verbatim? |
|---|---|---|---|---|---|
| 1 | **SEC-018** (required) | Reviewer | R5's After is replaced. Security findings are sorted by class, then grade: a constraint breach or omitted control blocks whatever its grade, a MEDIUM is fixed before shipping, and a LOW is technical debt, not a condition | R5 | Yes |
| 2 | **SEC-019** (required) | Reviewer | B1's FAIL-column parenthetical gains the adjacency rule | B1 | Yes |
| 3 | **SEC-020** | Reviewer | Appended to C4: the MEDIUM remediation plan survives a waiver | C4 | Yes |
| 4 | **SEC-021** | Reviewer | A6: "The same holds" becomes "The same FAIL rule, with no waiver, holds" | A6 | Yes |
| 5 | **Q7** (user: "Whole project (Recommended)") | User | "With no change under review (for example a full-project `/security-audit`), the whole project is the code under review." Added to §1.7, B3, B4 and (my stated equivalent; the orchestrator may drop it) A6. The consequence for older projects (a remediation pass before PASS) is recorded in §1.7 and §8 | §1.6, §1.7, A6, B3, B4, §8 | The user's example sentence, unchanged |
| 6 | **Q8** (user: "Yes, block (Recommended)") | User | Recorded as decided. No text change: the fail-safe default stands. Noted in §1.7 and §8 | §1.6, §1.7, §8, §12 | — |
| 7 | **FU-2 widened** | Orchestrator-verified | Adds `prepare-release-conditional-pass-conditions-gap` (`case.yaml:6–7`, `brief.md:12`, `expect.py:6` docstring). Result unchanged. v3's unverified item on this case is settled | §8, §9, §13 | — |
| 8 | **Verification counts** | — | New: `The same FAIL rule, with no waiver` (1); `the whole project is the code under review` (security-audit 2, validation-gates 1); `adds or alters code which the missing control should protect` now also in `testing-strategy` (5 files); `A waiver that lifts a` now also in `tech-lead.md` (C4); `A security finding is never such a condition` (1); `whatever its grade` (testing-strategy 1, prepare-release 1). `next release cycle` in `prepare-release` stays 1, as the reviewer said | §9 | — |
| 9 | Q9 (keep R5) | — | Settled by the reviewer's SEC-018 text for R5 | §12 | — |
| 10 | FU-5 | — | Notes that `/prepare-release` has the same capability-gap shape | §9 | — |
| 11 | **Unchanged from v3** | — | Every `Before:`; the Afters of A1–A5, A7, A8, B2, B2b, C1, C2, C3, R1–R4; A6's three table rows; B1's columns other than the FAIL parenthetical; the authority legs; D5 records (Q7 added to two rows); §11; FU-3, FU-6, FU-7, D1 | — | — |

## 16. Orchestrator verification and rulings (added before commit, 2026-10-07)

*Added by the orchestrator, not the producing agent, on `develop` `5eff98e`. §§0–15 are unchanged. The producing
agent was stopped by a usage limit after writing v4 and before its hand-back, so the orchestrator verified v4
directly.*

**16.1 Verified**

- **All edits apply.** v4 has 22 edits, the same IDs as v3: A1–A8, B1–B4, B2b, C1–C4 and R1–R5. C2 is optional.
  Each Before text occurs **exactly once** on `develop` `5eff98e`.
- **Only the expected edits changed.** v4 differs from v3 in exactly A6 (SEC-021), B1 (SEC-019), B3 and B4 (Q7),
  C4 (SEC-020) and R5 (SEC-018). The other edits are byte-identical.
- **The reviewer's After texts are verbatim.** These were checked byte for byte:
  - SEC-018 (R5), SEC-019, SEC-020 and SEC-021 in v4;
  - SEC-001, SEC-009 to SEC-011, SEC-012 (R1–R3), SEC-014 to SEC-016 in v3, carried into v4.
- **No old wording survives.** After all edits are applied, none of these texts remains: "Merge is blocked until
  conditions", "If any CRITICAL findings exist, the verdict MUST be FAIL.", "high findings have mitigations",
  "Potential risk, schedule for next sprint", "must be met before deployment" and "deadline=[when]".
- **The user decisions are recorded**: Q1–Q4, Q7 ("Whole project (Recommended)") and Q8 ("Yes, block
  (Recommended)").
- **Golden coupling.** Searched in `tests/golden/open/` with `held-out` pruned. Three cases quote amended lines:
  `code-review-conditional-pass-conditions-gap` (`:51`), `security-audit-critical-not-fail` (`:67`) and
  `prepare-release-conditional-pass-conditions-gap` (`:61`). Each `check()` reads only its fixture, as confirmed
  for all three, so **no result changes**. Their quotes go stale; refreshing them is FU-2, which needs a grant and a
  user-authorized baseline. Held-out coupling is detected by `scorecard.py --check` in FU-1.
- **Tests outside golden.** `test_code_review_skill_contract` and `test_validation_gates_skill_contract` assert only
  verdict tokens, markers and the Gate Types executor mapping. v4 keeps all of them.

**16.2 Rulings**

- **v4 is accepted as written**, with C2 optional. FU-1 is `T582`.
- **Reviews.** Round 1: FAIL as scoped. Round 2: CONDITIONAL_PASS. Round 3: CONDITIONAL_PASS. v4 meets every
  condition, and the reviewer said a phrase check would suffice in place of another review. The record is in
  `security-review-conditional-pass-semantics-v1.md`.
- **Scope widening** to `release-manager` and `/prepare-release` (SEC-012, plus the architect's R5) is accepted: it
  only adds restrictions, and it is what makes the user's Q4 security exclusion hold at the Release gate.
- **P40 slice S1** (security verdict criteria) is settled by these edits, as v4 records. Slices S2–S4 remain under
  ADR-008.
- **Parked:**
  - FU-2 (golden quote refresh; protected path, user baseline);
  - FU-6 (SEC-008: `security-engineer` SLA table and `validation-gates:74` tiers);
  - FU-7 (`receiving-code-review:86`).
