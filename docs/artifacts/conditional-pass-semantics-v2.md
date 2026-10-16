# Artifact: conditional-pass-semantics-v2.md

> Filename: `conditional-pass-semantics-v2.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T580 (P2, P39), second version
- **Created**: 2026-10-02
- **Based on**:
  - `docs/artifacts/conditional-pass-semantics-v1.md` (superseded by this version);
  - the Security Engineer's read-only review of v1, **VERDICT: FAIL as scoped**, with findings SEC-001 … SEC-008 and
    their After texts. The orchestrator relayed them; I did not read the review record itself;
  - the **user decisions of 2026-10-02 on Q1–Q4**, relayed verbatim by the orchestrator (§1.6);
  - the orchestrator's verified golden finding for `security-audit-critical-not-fail` (§7);
  - `docs/tasks/task-T580.md`; `docs/plans/plan-100-conditional-pass-and-authority-adr.md` §1;
    `docs/artifacts/gate-verdict-consistency-v1.md` §§6–7, 13.3; `docs/decisions/ADR-007-command-contract-authority.md`
    (Accepted); `docs/artifacts/poc-contract-resolution-v1.md` §9.2; `docs/artifacts/poc-security-reviewer-blocking-v3.md`;
  - the source files listed in v1 Metadata, read at worktree `develop` `dd7703b`.
- **Supersedes**: `conditional-pass-semantics-v1.md`, which stays unchanged as the historical record. **Where they
  differ, v2 governs. FU-1 applies v2 only.**
- **Decision references**: P39 and the user's Q1–Q4 answers. No new ADR is minted. No ADR-008 (P34b) ranking is used.

## 0. What this document is, and what it did not do

This is the complete, standalone ruling for P39, with exact edits for FU-1. It takes in the security review and the
user's four answers. §13 lists every v1→v2 change. **It changed no agent, skill, command, instruction or golden case.**

**Method and limits.**
- **No shell.** Claims that need one are marked **(unverified)** (§11).
- **Golden access.** Only `tests/golden/open/code-review-conditional-pass-conditions-gap/{brief.md,expect.py}` was read,
  for v1. I opened nothing else under `tests/golden/`, and nothing under `held-out/`. The coupling of
  `security-audit-critical-not-fail` is the orchestrator's finding, quoted in §7.
- **Apply by text.** Line numbers are at `dd7703b`. **Every `Before:` text is byte-identical to v1.** The only new
  Before is B2b (`security-audit.md:45`), and it is unique in its file.
- **Characters.** `—` is U+2014 and `§` is U+00A7, as in the source.
- **Fences.** Each edit is one four-backtick fence beginning `Before:`.

## 1. Authority basis

### 1.1 The user's P39 rule (2026-10-02, verbatim)

> "CONDITIONAL_PASS allows merge with conditions tracked (closed before the next gate on production; PoC debt due by
> handoff). FAIL blocks. Security HIGH/CRITICAL and constraint breaches never qualify for CONDITIONAL_PASS. The
> experimental /code-review command and tech-lead agent get amended to match AGENTS.md." The user chose: **"Adopt it
> (Recommended)"**.

### 1.2 `AGENTS.md`

- § Validation Gates (`:54–55`): "`FAIL` blocks progression. Orchestrator creates fix tasks and re-routes."
  "`CONDITIONAL_PASS` proceeds with tracked conditions added to the task list."
- § Task Protocol (`:18`): "Only orchestrators create/transition tasks." A reviewer therefore lists conditions, and the
  orchestrator adds them to the task list.

### 1.3 Commands: ADR-007 branch 1

> "Does the clause contradict `AGENTS.md`, a `stable` instruction, or another clause of the same command file? If yes,
> the command is wrong regardless of what the corpus does. … a command may specialise it but may not create a rival
> convention for the same thing."

- **`/code-review:51` (A4), `AGENTS.md` prong.** Compare `AGENTS.md:55` ("proceeds with tracked conditions") with
  "list the conditions that must be met before merge". The gate sits "before merge" (`validation-gates:26`). The
  conflict can be quoted from both texts, as ADR-007 § Risks requires.
- **`/security-audit:44,:67,:73` (B2–B4), stable-instruction prong.** Compare `security-guidelines.md:182`
  ("`CRITICAL` and `HIGH` findings block merge until resolved") with `:67`, which forces FAIL only for CRITICAL.
- **ADR-007 § Decision 5 is respected.** Every command edit tightens the contract: B3 keeps "exist", and PASS gets
  stricter.

### 1.4 The agent: the T542/FU-C precedent

`poc-contract-resolution-v1.md` §9.2 applies ADR-007 branch 1 by analogy to an agent that contradicts a higher text and
"subordinates itself in its own words". `tech-lead` qualifies on both counts:
- **It contradicts `AGENTS.md:55`.** `tech-lead.md:97` reads "Merge is blocked until conditions are resolved".
- **It subordinates itself in its own words**, twice. `:29–30` points to skill `code-review`, whose `:151` says
  "allows merge". `:68` makes its block "the same verdict" as the `validation-gates` block.
- **The user named it.**

### 1.5 Skills and the security exclusion

`validation-gates`, `testing-strategy` and `code-review` are stable skills, which ADR-007 does not reach. Their edits
rest on three things:
1. **The user's rule and answers** (§1.1, §1.6).
2. **`security-guidelines.md`** (stable, `applyTo: "**"`):
   - Rails `:15–20`: "Does not grant any agent authority to disable a security control 'temporarily,' even in PoC or
     development mode".
   - Rails `:22–24`: CRITICAL/HIGH "block merge … until resolved"; MEDIUM "require a documented remediation plan before
     merge".
   - `:153`: Immutable Security Constraints "cannot be overridden by any agent, configuration, or runtime decision".
   - `:182–183`.
3. **Joint satisfiability.** The amended clauses are permissions: "documented mitigations" and the Tech Lead waiver.
   The instruction is a prohibition. Withholding the permission in the security cases obeys both. **No ADR-008 ranking
   is needed.**

### 1.6 User decisions on v1's open questions (2026-10-02, verbatim)

| Question | Decision | Applied in |
|---|---|---|
| Q1: keep the Tech Lead waiver for non-security FAILs? | **"Keep it, except for security (Recommended)"** | C1, C3, C4 required; non-security waiver kept; A4's FAIL line |
| Q2: PoC "debt due by handoff" | **"Recorded by handoff (Recommended)"**. A PoC CONDITIONAL_PASS condition must be in the debt ledger and scorecard by the production handoff and is fixed in production. Security breaches can never be debt. Where `poc-orchestrator` § Security Findings and `poc-security-engineer:23` set a security-MEDIUM fix deadline "no later than the production handoff", that more specific rule governs. | A1, A3–A6, A8, C2 |
| Q3: the omitted/removed/disabled/weakened class on production too? | **"Both tracks (Recommended)"**. It is scoped to the controls `security-guidelines.md` requires for the code under review. Pre-existing gaps outside the change are graded at their own severity and tracked, so older code doesn't deadlock. | A3, A4, A6, B3, B4, C1, C3, C4 |
| Q4: when do Release-gate conditions close? | **"Next release cycle"**. A Release-gate CONDITIONAL_PASS may ship, with its conditions tracked as tasks for the next release cycle. This never applies to security findings. | A5, A6, A8 |

### 1.7 Defined terms (used verbatim in the edits)

- **Security finding.** Any finding in the security category, whichever gate or executor raises it, graded on the
  `security-guidelines.md` § Security Review Workflow scale (SEC-003).
- **The security exclusion.** Four things never qualify for CONDITIONAL_PASS, are never waived and are never recorded as
  debt:
  - a security finding graded `SECURITY:CRITICAL`;
  - a security finding graded `SECURITY:HIGH`;
  - a breach of an Immutable Security Constraint;
  - a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed,
    disabled or weakened, tagged or not.
- **The pre-existing-gap rule (Q3).** A required control missing only from code outside the change under review is
  graded at its own severity and tracked like any other finding of that grade. The omitted-control class does not raise
  its grade.
- **The track rule.** On production, conditions close before the next gate. At the Release gate, conditions are tasks
  for the next release cycle. On PoC, conditions are recorded as debt by the production handoff and fixed in
  production. None of these deferrals applies to a security finding, which follows §2.

## 2. Ruling on the `validation-gates:67` security nuance

**Amend `validation-gates` itself (A5–A8).** It is the mandatory skill at every "Phase or validation transition"
(`AGENTS.md:67`).

- **High findings.** "High findings have documented mitigations" now covers high findings **outside the security
  category only**.
- **The security exclusion.** It yields FAIL until resolved, whatever mitigation is documented, and no waiver applies.
  This holds on both tracks (Q3), with the pre-existing-gap rule.
- **Security findings graded medium.** These yield at best CONDITIONAL_PASS. The remediation plan (owner, fix,
  deadline) is recorded as a condition with the verdict, before the affected work's next merge (`:183`). The condition
  is the fix, and its due point is:
  - **on production**, before the next gate;
  - **at the Release gate**, before the release ships, because the next-release-cycle rule never applies to a security
    finding (Q4);
  - **on PoC**, by its remediation-plan deadline, no later than the production handoff. This is the more specific rule
    in `poc-orchestrator` § Security Findings and `poc-security-engineer:23` (Q2).
- **PASS** requires no security finding graded medium.
- **Observation.** `:74` already classes "security vulnerability" as `critical`. The tier misalignment against
  `security-engineer.md:81–83` is SEC-008, recorded as a follow-up only (§8, FU-6).

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
- **CONDITIONAL_PASS**: Code is acceptable with listed conditions, and merge is permitted with the conditions tracked (`AGENTS.md` § Validation Gates: "`CONDITIONAL_PASS` proceeds with tracked conditions added to the task list"). List each condition with an owner and a due point; the orchestrator adds it to the task list (`AGENTS.md` § Task Protocol). On the production track a condition is resolved before the next gate. On the PoC track it becomes a debt item, recorded in the debt ledger (skill `technical-debt-tracking`) and in `POC-DEBT-SCORECARD.md` (`poc-guidelines.md` § Debt Scorecard) by the production handoff, and fixed in production; where `poc-orchestrator` § Security Findings sets a security finding's fix deadline no later than the production handoff, that more specific rule governs. A security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH` (`security-guidelines.md` § Security Review Workflow), whoever raised it, a breach of an Immutable Security Constraint in `security-guidelines.md`, and a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, tagged or not, never qualify for CONDITIONAL_PASS and are never recorded as debt: the verdict is FAIL until each is resolved, and no waiver applies (§ Merge and Architecture Authority). A required control missing only from code outside the change under review is graded at its own severity and tracked like any other finding of that grade. A security finding listed as a condition carries its remediation plan (owner, fix, deadline) (`security-guidelines.md` § Security Review Workflow).
````

**Authority:** §1.1, §1.2, §1.4; Q2 and Q3; SEC-003, SEC-004 and SEC-007. `:96` and `:98` are unchanged; `:98`
already reads "Merge is denied".

### A4: `commands/code-review.md:51–52`

````
Before:
If CONDITIONAL_PASS, list the conditions that must be met before merge.
If FAIL, include blocker details, owner, and retry attempt guidance.

After:
If CONDITIONAL_PASS, list the conditions, each with an owner and a due point. A security finding listed as a condition carries its remediation plan (owner, fix, deadline) (`security-guidelines.md` § Security Review Workflow). CONDITIONAL_PASS permits the merge, with each condition tracked in the task list (`AGENTS.md` § Validation Gates): on the production track a condition is resolved before the next gate; on the PoC track it becomes a debt item, recorded in the debt ledger and in `POC-DEBT-SCORECARD.md` by the production handoff and fixed in production (`poc-guidelines.md` § Mandatory Debt Tracking, § Debt Scorecard), except where `poc-orchestrator` § Security Findings sets a security finding's fix deadline no later than the production handoff, which governs.
A security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH` (`security-guidelines.md` § Security Review Workflow), whoever raised it, a breach of an Immutable Security Constraint in `security-guidelines.md`, or a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, tagged or not, never yields CONDITIONAL_PASS and is never recorded as debt: the status is FAIL until it is resolved. A required control missing only from code outside the change under review is graded at its own severity and tracked.
If FAIL, the merge is blocked; a Tech Lead waiver may lift a FAIL only when no security finding above is among its causes (skill `code-review` § Review as Validation Gate). Include blocker details, owner, and retry attempt guidance.
````

**Authority:** ADR-007 branch 1, `AGENTS.md` prong; Q1, Q2 and Q3; SEC-003 and SEC-007. A4 names no `**Conditions**:`
field and no list format, so the open golden case's `capability_gap` premise holds (§7).

### A5: `validation-gates/SKILL.md:55`

````
Before:
- [ ] <condition that must be met before proceeding>

After:
- [ ] <condition> — owner: <who>; due: before the next gate (production track; at the Release gate, the next release cycle) | recorded as debt in the debt ledger and scorecard by the production handoff (PoC track); a security finding also carries its remediation plan (owner, fix, deadline)
````

### A6: `validation-gates/SKILL.md:66–68`, Verdict Rules and the security rule

````
Before:
| **PASS** | No critical or high findings. Medium/low findings noted but non-blocking. |
| **CONDITIONAL_PASS** | No critical findings. High findings have documented mitigations. Medium/low with clear remediation plan. All conditions must be resolved before the next gate. |
| **FAIL** | Any critical finding unresolved, OR any high finding without mitigation. Work must return to the implementer. |

After:
| **PASS** | No critical or high findings, and no security finding graded medium. Medium/low findings noted but non-blocking. |
| **CONDITIONAL_PASS** | No critical findings, and none of the security findings excluded below. Other high findings have documented mitigations. Medium/low with clear remediation plan. Each condition is tracked as a task with an owner and a due point, under the track rule: on the production track, all conditions must be resolved before the next gate, except that a Release-gate CONDITIONAL_PASS may ship with its conditions tracked as tasks for the next release cycle; on the PoC track, each condition becomes a debt item, recorded in the debt ledger and the debt scorecard by the production handoff and fixed in production (`poc-guidelines.md` § Mandatory Debt Tracking, § Debt Scorecard). Neither deferral applies to a security finding (below). |
| **FAIL** | Any critical finding unresolved, OR any high finding without mitigation, OR any security finding excluded below. Work must return to the implementer. |

**Security findings never qualify for CONDITIONAL_PASS.** A security finding is any finding in the security category, whichever gate or executor raises it, graded on the `security-guidelines.md` § Security Review Workflow scale (`SECURITY:CRITICAL`/`HIGH`/`MEDIUM`/`LOW`); the Findings table records that grade as its Severity and `security` as its Category. `security-guidelines.md` § Security Review Workflow: "`CRITICAL` and `HIGH` findings block merge until resolved". A security finding graded critical or high, and any breach of an Immutable Security Constraint in `security-guidelines.md` (which "cannot be overridden by any agent, configuration, or runtime decision"), yields FAIL until it is resolved, whatever mitigation is documented, and no waiver applies to it. The "documented mitigations" route above is for high findings outside the security category only. The same holds for any security control `security-guidelines.md` requires for the code under review that is omitted, removed, disabled or weakened, tagged or not (on the PoC track, `poc-orchestrator` § Security Findings). A required control missing only from code outside the change under review is graded at its own severity and tracked like any other finding of that grade. None of these is ever recorded as debt. A security finding graded medium yields at best CONDITIONAL_PASS: its remediation plan (owner, fix, deadline) is recorded as a tracked condition with the verdict, before the affected work's next merge (`security-guidelines.md` § Security Review Workflow: "`MEDIUM` findings must have a remediation plan before merge"); the condition is the fix, due under the track rule above (production: before the next gate; PoC: by the production handoff, as `poc-orchestrator` § Security Findings already requires). The next-release-cycle rule never applies to a security finding: at the Release gate, a security finding graded medium is fixed before the release ships.
````

**Source:** the bold paragraph is SEC-003's text adopted verbatim, with three additions:
- the pre-existing-gap sentence (Q3);
- "None of these is ever recorded as debt." (Q2);
- the closing Release-gate sentence (Q4).

The PASS row uses SEC-003's "no security finding graded medium". The CONDITIONAL_PASS row carries Q2 and Q4. The table
keeps its three rows and two columns.

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
1. Proceed with work, but track all conditions as tasks, each with an owner and a due point. At the Implementation gate, proceeding includes the merge; at the Release gate, it includes shipping the release.
2. On the production track, conditions MUST be resolved before the next gate in the pipeline; at the Release gate, which has no next gate, they are tracked as tasks for the next release cycle. On the PoC track, each condition instead becomes a debt item, recorded in the debt ledger and the debt scorecard by the production handoff and fixed in production (`poc-guidelines.md` § Mandatory Debt Tracking, § Debt Scorecard). Neither deferral applies to a security finding (§ Verdict Rules): one graded medium is fixed before the next gate on the production track (at the Release gate, before the release ships), and on the PoC track by its remediation-plan deadline, no later than the production handoff (`poc-orchestrator` § Security Findings).
````

**Authority:** the user's rule; Q2 and Q4; SEC-006. `:133–135` and `:143` ("The Release Gate verifies that all prior
conditions have been resolved") are unchanged and stay consistent: Q4 concerns the Release gate's *own* conditions.

## 4. Batch B: required (SEC-002, SEC-005)

### B1: `testing-strategy/SKILL.md:240`

````
Before:
| **Security scan** | No critical/high findings | No critical; high findings have mitigations | Any critical finding |

After:
| **Security scan** | No critical, high or medium findings | No critical or high findings; each medium finding has a remediation plan (`security-guidelines.md` § Security Review Workflow) | Any critical or high finding, or any breach of an Immutable Security Constraint (`security-guidelines.md`) |
````

**Source:** SEC-005, verbatim.

### B2: `commands/security-audit.md:44`

````
Before:
   - **HIGH**: Exploitable with moderate effort, fix within current sprint

After:
   - **HIGH**: Exploitable with moderate effort; blocks merge until resolved (`security-guidelines.md` § Security Review Workflow)
````

### B3: `commands/security-audit.md:67`

````
Before:
If any CRITICAL findings exist, the verdict MUST be FAIL.

After:
If any CRITICAL or HIGH finding exists, or any Immutable Security Constraint in `security-guidelines.md` is breached, or any security control that `security-guidelines.md` requires for the code under review is omitted, removed, disabled or weakened, the verdict MUST be FAIL (`security-guidelines.md` § Security Review Workflow: "`CRITICAL` and `HIGH` findings block merge until resolved"). A required control missing only from code outside the change under review is graded at its own severity. If any MEDIUM finding exists, the verdict is at best CONDITIONAL_PASS, with a remediation plan (owner, fix, deadline) listed as a condition for each MEDIUM finding. PASS requires no CRITICAL, HIGH or MEDIUM finding.
````

**Source:** SEC-002's After verbatim, with the Q3 omitted-control clause and the pre-existing-gap sentence added, as
SEC-002 directs ("Because Q3 is adopted, add the omitted/removed/disabled/weakened clause").

### B4: `commands/security-audit.md:73`

````
Before:
**Failure mode**: If any CRITICAL finding exists, the verdict MUST be FAIL — the command cannot return PASS/CONDITIONAL_PASS while a CRITICAL finding is unresolved.

After:
**Failure mode**: If any CRITICAL or HIGH finding exists, an Immutable Security Constraint is breached, or a security control that `security-guidelines.md` requires for the code under review is omitted, removed, disabled or weakened, the verdict MUST be FAIL — the command cannot return PASS/CONDITIONAL_PASS while such a finding is unresolved.
````

**B2–B4 authority:** ADR-007 branch 1, stable-instruction prong; Q3; SEC-002. Every edit tightens the contract.

## 5. Batch C: required, except C2 (SEC-001, Q1)

### C1: `code-review/SKILL.md:150`

````
Before:
1. A `FAIL` verdict blocks the merge request — no override without Tech Lead waiver (documented as a decision artifact).

After:
1. A `FAIL` verdict blocks the merge request — no override without Tech Lead waiver (documented as a decision artifact). No waiver applies to a security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH`, whoever raised it, to a breach of an Immutable Security Constraint, or to a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened: `security-guidelines.md` says "`CRITICAL` and `HIGH` findings block merge until resolved" (§ Security Review Workflow), and that its Immutable Security Constraints "cannot be overridden by any agent, configuration, or runtime decision".
````

**Source:** SEC-001, verbatim.

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
3. Require explicit waiver reference for any approved exception and escalate unresolved conflicts to orchestrator. No waiver applies to a security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH`, whoever raised it, to a breach of an Immutable Security Constraint, or to a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened (`security-guidelines.md` § Security Review Workflow, § Immutable Security Constraints).
````

**C1, C3 and C4 authority:**
- Q1: "Keep it, except for security".
- `security-guidelines` `:153`, `:182` and Rails `:15–20`, by joint satisfiability.
- The precedent is v3 E11 (`rapid-prototyping:74`: "No Tech Lead waiver applies to it").
- C3 and C4 use C1's exclusion list, as SEC-001 directs.

## 6. Optional edits

### C2 (optional): `code-review/SKILL.md:151`

````
Before:
2. A `CONDITIONAL_PASS` verdict allows merge but **requires** that each should-fix item is logged as a task in `docs/tasks/active-tasks.md` with an assigned owner and target sprint.

After:
2. A `CONDITIONAL_PASS` verdict allows merge but **requires** that each should-fix item is logged as a task in `docs/tasks/active-tasks.md` with an assigned owner and target sprint. On the production track the item is resolved before the next gate; on the PoC track it becomes a debt item, recorded in the debt ledger and the debt scorecard by the production handoff and fixed in production (`poc-guidelines.md` § Mandatory Debt Tracking, § Debt Scorecard), unless `poc-orchestrator` § Security Findings sets a security finding's fix deadline no later than the production handoff, which governs.
````

### B2b (optional): `commands/security-audit.md:45`

````
Before:
   - **MEDIUM**: Potential risk, schedule for next sprint

After:
   - **MEDIUM**: Potential risk; requires a remediation plan (owner, fix, deadline) before merge
````

**Source:** SEC-002's optional B2b, verbatim. **Authority:** `security-guidelines:183`.

## 7. Golden coupling and blast radius

**`code-review-conditional-pass-conditions-gap`** (read under grant for v1):
- **Stale quotes.** `brief.md:11–12` and `expect.py:4–5` quote "If CONDITIONAL_PASS, list the conditions that must be
  met before merge." A4 makes both stale.
- **Result unchanged.** `check()` reads only `fixture/review.md`.
- **Premise holds.** The case says the command has "no required field name, no required list format". A4 names neither.

**`security-audit-critical-not-fail`** (the orchestrator's verified finding; I did not read it):
- **Stale quotes.** `brief.md:13`, the `expect.py:5` docstring and the `case.yaml` `known_failing_reason` quote "If any
  CRITICAL findings exist, the verdict MUST be FAIL". B3 makes all three stale.
- **Result unchanged.** `check()` reads only the fixture (CRITICAL: 1, Status: CONDITIONAL_PASS).
- **Premise holds.** CRITICAL still forces FAIL under B3.
- **No other fixtures affected.** No other visible fixture pairs HIGH with CONDITIONAL_PASS.

**`validate-workflow-gate-verdict-sources`** (unread; from `gate-verdict-consistency-v1.md` §§8, 13.1):
- Its fixture copy of `validation-gates` will no longer be byte-identical to source.
- Its `expect.py` reads the § Gate Types rows, the § Verdict Format sentence and the `**Gate:**` field. A5–A8 touch none
  of these, so the result should be unchanged **(unverified)**.

**Held-out:** not read. Coupling is detected only through `scripts/scorecard.py --check`.

**Other patterns to search**, in `open/` with `held-out` pruned **(unverified)**:
- the v1 §5 list;
- `schedule for next sprint`;
- `Potential risk`.

**Files edited:**

| File | Edits | Maturity |
|---|---|---|
| `implementation/knowledge/agents/tech-lead.md` | A1, A2, A3, C4 | experimental |
| `implementation/knowledge/commands/code-review.md` | A4 | experimental |
| `implementation/knowledge/skills/validation-gates/SKILL.md` | A5–A8 | stable |
| `implementation/knowledge/skills/testing-strategy/SKILL.md` | B1 | stable |
| `implementation/knowledge/commands/security-audit.md` | B2–B4 (+ B2b) | stable |
| `implementation/knowledge/skills/code-review/SKILL.md` | C1, C3 (+ C2) | stable |

**Mechanics:**
- **Regenerate:** `sync.mjs --root implementation` and `generate-registry.py`, each confirmed with `--check`.
- **Root drift:** declare exactly what `--print-drift` reports. That is up to 6 × 7 paths **(count unverified)**.
- **Maturity:** none expected at P2. **Affects:** `—`.

**Unchanged:**
- `AGENTS.md`, `security-guidelines.md`, `poc-guidelines.md`, `orchestrator.md`;
- `poc-orchestrator.md`, `poc-security-engineer.md`, `rapid-prototyping`, `security-engineer.md`;
- `tests/golden/**`.

**Behavioural consequences to expect (Q3):**
- **Production security gate.** A medium-graded omitted control in the code under review now yields FAIL instead of
  CONDITIONAL_PASS.
- **PoC texts.** `poc-security-engineer:22` blocks omitted controls "whatever its severity" and has no
  pre-existing-gap carve-out. The PoC texts are stricter, which is jointly satisfiable, and they are not edited here.

## 8. Follow-ups

| ID | Covers | Files | `tests/golden/**` grant? | Owner (suggested) | Priority | Depends on / verify |
|---|---|---|---|---|---|---|
| **FU-0**: delta security review of v2 | §2; A3, A4, A6, B, C; the additions to SEC texts in A6 and B3 | this artifact | No | Security Engineer | P2 | Before FU-1. A narrow phrase check may suffice if the reviewer accepts the stated additions. |
| **FU-1**: apply P39 per **v2** | A1–A8, B1–B4, C1, C3, C4 (required); C2, B2b (orchestrator's call) | §7 table; mirrors; registry; root drift | **No** | Backend Developer | P2 | FU-0. See the verification list below. |
| **FU-2**: refresh stale golden quotes (**widened**) | `code-review-conditional-pass-conditions-gap` `brief.md:11–12`, `expect.py:4–5`; `security-audit-critical-not-fail` `brief.md:13`, `expect.py:5`, `case.yaml` `known_failing_reason` | those files only | **Yes**, `protected-paths-v1.md` §5, scoped to these two case directories; a baseline authorization if an `expect.py` changes | QA Engineer | P2 | After FU-1. Results unchanged. Not ruled here. |
| **FU-3**: `validate-workflow` fixture copy of `validation-gates` | Provenance | that case's fixture copy and brief | **Yes** | QA Engineer | P2 | Only if byte-identity must hold or is test-enforced |
| **FU-5** *(candidate)*: a structured `**Conditions**:` field in `/code-review` | Closes the capability gap | command; case classification | **Yes** | Solution Architect, then QA | P2 | A separate ADR-007 decision |
| **FU-6** (SEC-008, follow-up only) | `security-engineer.md:81–83` SLA table ("HIGH … Must fix before release"; MEDIUM "Fix within current sprint") against `security-guidelines:182–183` and v2's track rule. Also `validation-gates:74` places "security vulnerability" in `critical`, out of line with the four-grade security scale. Also: `security-engineer.md:152–153` (Security Gate Protocol) does not name the omitted-control class that Q3 now applies on production. | `security-engineer.md`; `validation-gates/SKILL.md:74` | No | Solution Architect (decision), then Backend Developer | P2 | Not a v2 edit |
| **FU-7** *(candidate)* | `receiving-code-review:86`: "`FAIL` findings block merge until resolved or escalated via blocker protocol". After Q1, the non-security waiver survives, but "or escalated" is not limited to non-security FAILs. | `receiving-code-review/SKILL.md` | No | Orchestrator scopes | P2 | Not ruled |
| **D1** (P40) | Criteria ranking at the code-review gate (`code-review:96`, `:128`) | — | — | — | — | **Dependency on ADR-008 (T581).** Not decided. |

**FU-1 verification:**
1. Each applied `Before:` matches **exactly once by text** on `develop` at dispatch.
2. 0 hits under `implementation/knowledge/` for each of these:
   - `Merge is blocked until conditions are resolved`
   - `Yes, after conditions met`
   - `must be resolved before merge`
   - `conditions that must be met before merge`
   - `must be met before proceeding`
   - `High findings have documented mitigations`
   - `high findings have mitigations`
   - `If any CRITICAL findings exist`
   - `Exploitable with moderate effort, fix within current sprint`
   - with B2b: `Potential risk, schedule for next sprint`
3. Exact hit counts:
   - `Security findings never qualify for CONDITIONAL_PASS`: 1 (`validation-gates`).
   - `Yes, with conditions tracked`: 1 (`tech-lead`).
   - `whoever raised it`: 2 in `tech-lead.md` (A3, C4), 1 in `commands/code-review.md` (A4), 2 in
     `skills/code-review/SKILL.md` (C1, C3).
   - `next release cycle`: 3 in `validation-gates` (A5, A6, A8).
   - `A security finding listed as a condition carries its remediation plan`: 1 each in `tech-lead.md` and
     `commands/code-review.md`.
4. `AGENTS.md`, `security-guidelines.md`, `poc-guidelines.md`, the PoC agents, `security-engineer.md` and
   `tests/golden/**` are byte-unchanged.
5. `sync.mjs --check` and `generate-registry.py --check` are clean, and the root parity gate is green.
6. `scripts/scorecard.py --check` shows no change against the current baseline. A regression means held-out coupling:
   stop and report it.
7. `check-maturity.py --root implementation` reports 0 failing.
8. `validate-tasks.py` passes. For `tests/run.py`, check the exit code and redirect the output to a file.
9. Report a `cmp` of the `validate-workflow` fixture copy of `validation-gates`. A difference is expected, and that
   case's result must be unchanged.

## 9. Corrections to the brief (`unclear_requirements`, `minor`; unchanged from v1)

- **C1.** `tech-lead` contradicts the rule at `:82` and `:90` as well as `:97`.
- **C2.** `validation-gates:67`, `:132`, `:55` and `:75` do not fully agree with the user's rule.
- **C3.** Further routes let a security HIGH finding through: `testing-strategy:240`, `/security-audit:44,:67,:73`, and
  the waiver at `code-review:150,:159` and `tech-lead:111`. v2 makes all of them required edits.
- **C4.** "A MEDIUM security finding is a CONDITIONAL_PASS" is in tension with `code-review:96` and `:128` at the
  code-review gate. This is P40 (D1).
- **C5.** The facts were verified on `1682077`; the worktree is at `dd7703b`.

## 10. Open questions and dependencies

**Settled by the user:** Q1, Q2, Q3 and Q4 (§1.6). **Settled by the review:** v1's Q5. SEC-003 adopted the PASS-row and
MEDIUM wording.

**Raised by applying the answers** (for FU-0 or the user; minor; none blocks FU-1):
- **Q6. Is a security finding graded medium at the Release gate fixed before shipping?** Q4 says the
  next-release-cycle rule "never applies to security findings". I applied that literally (A6, A8): such a finding is
  fixed before the release ships. The fail-safe alternative is to let it keep its remediation-plan deadline. That
  alternative needs the user's or the reviewer's say-so.
- **Q7. What is "the change under review" in a full-project `/security-audit`?** The command's scope may be "full
  project". For a full-project audit, the change is undefined, so the pre-existing-gap rule has no edge. B3 and B4 use
  the user's wording unchanged.
- **Q8. Does a pre-existing gap graded HIGH block an unrelated change?** Q3 says such gaps are "graded at their own
  severity and tracked". A gap that grades as `SECURITY:HIGH` is still HIGH, and `security-guidelines:182` blocks the
  merge of "every merge request touching security-sensitive code" until it is resolved. v2 does not decide whether that
  blocks an MR that does not touch the gap.
- **D1 (`dependency`, minor):** P40, as in v1. Not decided, and nothing in v2 depends on it.

**Blockers:** none. No edit needs an ADR-008 ranking.

## 11. Unverified claims (need a shell)

1. **No other contradicting text** under `implementation/knowledge/` (v1 §9 #1, including its list of unread files).
2. **No other golden coupling**, searched with `held-out` pruned (§7 patterns). `security-audit-critical-not-fail` was
   settled by the orchestrator.
3. **No test outside `tests/golden/`** asserts text in the six files.
4. **The `validate-workflow` case is unaffected:** its `expect.py` reads no line in A5–A8, and no test enforces
   byte-identity.
5. **The root-projection count.**
6. **"Debt ledger".** `technical-debt-tracking` defines it as `docs/artifacts/debt-ledger-v<N>.md`. I assume Q2's "debt
   ledger" means that file.

## 12. Summary

| Site | Ruling | Edit | Required? | Authority |
|---|---|---|---|---|
| `tech-lead:82, :90, :97` | Merge with tracked conditions; due points by track; PoC debt recorded by handoff and fixed in production, unless `poc-orchestrator` sets a fix deadline for a security finding; security exclusion on both tracks; plan carried | A1–A3 | Yes | User; Q2, Q3; `AGENTS.md:55`; T542/FU-C; SEC-003, SEC-007 |
| `/code-review:51–52` | Same; non-security waiver only | A4 | Yes | ADR-007 b1; Q1–Q3 |
| `validation-gates:55, 66–68, 75, 131–132` | Track rule including the Release gate's next release cycle; security never conditional; medium at best conditional, fix due by track | A5–A8 | Yes | User; Q2–Q4; SEC-003, SEC-006; `security-guidelines` |
| `testing-strategy:240` | High security never conditional; PASS excludes medium | B1 | Yes | SEC-005 |
| `/security-audit:44, 67, 73` | HIGH, constraint breach and omitted control → FAIL; MEDIUM at best conditional | B2–B4 | Yes | ADR-007 b1; SEC-002; Q3 |
| `code-review:150, 159`; `tech-lead:111` | No waiver for the security exclusion | C1, C3, C4 | Yes | Q1; SEC-001 |
| `code-review:151`; `/security-audit:45` | Due points; MEDIUM plan | C2, B2b | Optional | Q2; SEC-002 |
| Golden | Two open cases' quotes stale, results unchanged; one fixture-copy provenance | FU-2 (widened), FU-3 | — | — |

## 13. Change log v1 → v2

| # | Item | Source | v2 change | Where |
|---|---|---|---|---|
| 1 | **SEC-001** (HIGH) | Review; Q1 | C1, C3 and C4 are now **required**. C1's After is SEC-001's verbatim: "whoever raised it", plus the omitted-control class. C3 and C4 use the same exclusion list. C2 stays optional. | §5, §6 |
| 2 | **SEC-002** (HIGH) | Review | B2–B4 are now **required**. B3's After is SEC-002's, with the Q3 omitted-control clause and the pre-existing-gap sentence added. B4 takes the omitted-control clause. B2b is added as optional, verbatim. | §4, §6 |
| 3 | **SEC-003** (MEDIUM) | Review | A6's security paragraph is replaced with SEC-003's verbatim, plus three stated additions (Q3 pre-existing gap; "None of these is ever recorded as debt"; the Q4 Release-gate sentence). PASS row: "no security finding graded medium". Subject-based wording ("security finding graded …, whoever raised it") is used in A3, A4, C1, C3 and C4. A7 reads "a security finding graded high". | §3 A3, A4, A6, A7; §5 |
| 4 | **SEC-004** (MEDIUM) | Review; Q3 | The omitted-control class now applies on **both tracks**, scoped to "the code under review", with the pre-existing-gap rule. v1 applied it on PoC only, and v1's Q3 is settled. | A3, A4, A6, B3, B4, C1, C3, C4; §1.7 |
| 5 | **SEC-005** (MEDIUM) | Review | B1 is now **required**, with SEC-005's After verbatim (PASS: "No critical, high or medium findings"). | §4 B1 |
| 6 | **SEC-006** (LOW) | Review; Q2 | Fixed by SEC-003's "before the affected work's next merge" and "the condition is the fix, due under the track rule". A8 states the medium security fix due points by track. | A6, A8 |
| 7 | **SEC-007** (LOW) | Review | "A security finding listed as a condition carries its remediation plan (owner, fix, deadline) …" is appended to A3 and placed after A4's first sentence. A1 and A5 placeholders carry the plan. | A1, A3, A4, A5 |
| 8 | **SEC-008** (LOW) | Review | Recorded as a follow-up only (FU-6), extended to note that `security-engineer.md:152–153` does not name the production omitted-control class. | §8 FU-6 |
| 9 | **Q1** (user) | "Keep it, except for security (Recommended)" | Non-security waiver kept. A4's FAIL line now says a waiver may lift a FAIL only when no security finding is among its causes. v1's Q1 is settled. `receiving-code-review:86` is parked as FU-7. | A4; §5; §8 |
| 10 | **Q2** (user) | "Recorded by handoff (Recommended)" | The PoC phrase is now "recorded in the debt ledger and scorecard by the production handoff and fixed in production". "Never recorded as debt" is added for the security exclusion. The `poc-orchestrator` security fix deadline is named as the more specific rule. | A1, A3–A6, A8, C2 |
| 11 | **Q3** (user) | "Both tracks (Recommended)" | See #4. New defined term in §1.7. New open items Q7 and Q8. | — |
| 12 | **Q4** (user) | "Next release cycle" | Release-gate conditions are tracked as tasks for the next release cycle, and the release may ship. This never applies to a security finding: a medium one is fixed before shipping. Expressed in the `validation-gates` track rule. v1's Q4 is settled, and Q6 is new. | A5, A6, A8; §10 |
| 13 | **Batches** | Orchestrator | A, B1–B4, C1, C3 and C4 are required. C2 and B2b are optional. v1 had B and C optional. | §§3–6 |
| 14 | **FU-2 widened** | Orchestrator's golden check | Adds `security-audit-critical-not-fail` (`brief.md:13`, `expect.py:5`, `case.yaml` `known_failing_reason`). Results unchanged. | §7, §8 |
| 15 | **FU-0** | — | Now a delta review of v2. | §8 |
| 16 | **Verification** | — | New 0-hit patterns (`If any CRITICAL findings exist`, `fix within current sprint`, `high findings have mitigations`) and new exact counts (`whoever raised it`, `next release cycle`, SEC-007 sentence). | §8 |
| 17 | **Unchanged** | — | Every v1 `Before:` text; A2's After; the authority legs; C1–C5 of §9; FU-3; FU-5; D1. | — |
