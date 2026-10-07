# Artifact: conditional-pass-semantics-v1.md

> Filename: `conditional-pass-semantics-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T580 (P2, P39)
- **Created**: 2026-10-02
- **Based on**:
  - `docs/tasks/task-T580.md` (the brief; the user's rule quoted verbatim in §1);
  - `docs/plans/plan-100-conditional-pass-and-authority-adr.md` §1;
  - `docs/artifacts/gate-verdict-consistency-v1.md` §6 V6, §7 G1/G2, §13.3 (P39, P40);
  - `docs/decisions/ADR-007-command-contract-authority.md` (Accepted), branch 1;
  - `docs/artifacts/poc-contract-resolution-v1.md` §1.4, §9.2 (the T542/FU-C precedent);
  - `docs/artifacts/poc-security-reviewer-blocking-v3.md` §§1–3, §12 X7, §16.2 (the O1 blocking classes; the parked
    waiver carve-out);
  - source files read in full or in the cited range, at worktree `develop` `dd7703b`: `AGENTS.md`;
    `implementation/knowledge/agents/{tech-lead,orchestrator,poc-orchestrator,poc-security-engineer,security-engineer}.md`,
    `qa-engineer.md:100–179`, `release-manager.md:1–209`;
    `implementation/knowledge/commands/{code-review,security-audit}.md`;
    `implementation/knowledge/skills/{validation-gates,code-review,rapid-prototyping,technical-debt-tracking,release-workflow,receiving-code-review}/SKILL.md`,
    `testing-strategy/SKILL.md:200–254`;
    `implementation/knowledge/instructions/{security-guidelines,poc-guidelines}.md`;
    `implementation/registry/summary.md`.
  - Golden, under the brief's read-only grant only:
    `tests/golden/open/code-review-conditional-pass-conditions-gap/{brief.md,expect.py}`. Nothing else under
    `tests/golden/` was opened. `tests/golden/held-out/` was not opened.
- **Supersedes**: none (first version).
- **Decision references**: P39 (the user's decision, §1). ADR-007 branch 1 (commands). T542/FU-C precedent (agent).
  No new ADR is minted. **No ADR-008 (P34b) ranking is used** (§1.5).

## 0. What this document is, and what it did not do

It turns the user's P39 rule into exact edits, rules on the `validation-gates:67` security nuance, and lists every
other contradicting site I found. **It changed no agent, skill, command, instruction or golden case.**

**Method and limits.**
- **No shell.** Anything that needs a search or a run is marked **(unverified)** and collected in §9.
- **Apply by text, not by line.** Line numbers are at `dd7703b`. Every `Before:` was copied from the file as read, and
  was unique in that file when I read it in full (the two partial reads, `qa-engineer` and `release-manager`, are not
  edited).
- **Characters.** `—` is U+2014 and `§` is U+00A7, as in the source files.
- **Fences.** Each edit is one four-backtick fence beginning `Before:`. Text inside is literal.
- **The brief's facts** were verified on `1682077`; this worktree is at `dd7703b`. Every line the brief cites matches at
  `dd7703b`. T579 (O1) has landed: `poc-orchestrator.md` already carries § Security Findings, and
  `poc-security-engineer.md` its § Behavior blocking classes.

## 1. Authority basis

### 1.1 The user's rule (2026-10-02, relayed verbatim in `task-T580.md` §1)

> "CONDITIONAL_PASS allows merge with conditions tracked (closed before the next gate on production; PoC debt due by
> handoff). FAIL blocks. Security HIGH/CRITICAL and constraint breaches never qualify for CONDITIONAL_PASS. The
> experimental /code-review command and tech-lead agent get amended to match AGENTS.md." The user chose: **"Adopt it
> (Recommended)"**.

This is the primary authority for every edit below. Nothing here re-decides it. Where its words leave a reading open,
§8 reports that instead of deciding it.

### 1.2 `AGENTS.md` § Validation Gates (`:51–55`)

> "`FAIL` blocks progression. Orchestrator creates fix tasks and re-routes."
> "`CONDITIONAL_PASS` proceeds with tracked conditions added to the task list."

And § Task Protocol (`:18`): "Only orchestrators create/transition tasks. Agents report completion and blockers." So a
reviewer *lists* conditions, and the orchestrator *adds* them to the task list. The edits say so.

### 1.3 The command: ADR-007 branch 1, `AGENTS.md` prong

ADR-007 § Decision, branch 1: "Does the clause contradict `AGENTS.md`, a `stable` instruction, or another clause of the
same command file? If yes, the command is wrong regardless of what the corpus does. `AGENTS.md` is this repository's
top-level convention document; a command may specialise it but may not create a rival convention for the same thing."

**The contradiction, quotable from both texts** (ADR-007 § Risks: "the contradiction must be quotable from `AGENTS.md`'s
own text"):
- `AGENTS.md:55`: "`CONDITIONAL_PASS` proceeds with tracked conditions added to the task list."
- `commands/code-review.md:51`: "If CONDITIONAL_PASS, list the conditions that must be met before merge."

The code-review gate sits "after code complete, before merge" (`validation-gates:26`), so "proceeds" there is the merge.
A command that holds the merge until the conditions are met defines a rival meaning for the same verdict. Branch 1
fires, and the command is amended (A4).

**`/security-audit` (B2–B4)** takes branch 1 on the **stable-instruction prong**: `security-guidelines.md`
(`maturity: stable`, `applyTo: "**"`), `:182`, "`CRITICAL` and `HIGH` findings block merge until resolved", against
`security-audit.md:67`, which makes only CRITICAL force FAIL.

**ADR-007 § Decision 5 ("Never resolve by relaxing a check")** is respected. Every command edit tightens or keeps the
contract. B3 keeps "exist" and does not loosen it to "unresolved".

### 1.4 The agent: T542/FU-C precedent

`poc-contract-resolution-v1.md` §9.2: FU-C was "approved … The basis is the T542 precedent, where ADR-007 branch 1 was
applied by analogy to an agent file that contradicted a `stable` instruction. Each agent also subordinates itself in its
own words." `tech-lead` meets both legs:

- **It contradicts `AGENTS.md:55`.** `tech-lead.md:97`: "Merge is blocked until conditions are resolved."
- **It subordinates itself in its own words**, twice:
  - `:29–30`: "See skill `code-review` for the full structured checklist, feedback format, and VERDICT conventions this
    section summarizes." That skill (`stable`), `:151`, says: "A `CONDITIONAL_PASS` verdict allows merge but
    **requires** that each should-fix item is logged as a task".
  - `:68`, added by T573/E6: "A code review is the `validation-gates` skill's **Implementation** gate, so this block
    accompanies, and does not replace, that skill's `## Gate Verdict` block … All three record the same verdict." That
    skill's `:131–132` proceeds with tracked conditions.
- **And the user named it.** "The experimental /code-review command and tech-lead agent get amended to match AGENTS.md."

### 1.5 The skills and the security exclusion: the user's rule, the stable instruction, and joint satisfiability

`validation-gates`, `testing-strategy` and `code-review` (all skills, all `stable`) are not commands, so ADR-007 does not
reach them (`gate-verdict-consistency-v1.md` §1.1). Their edits rest on two things:

1. **The user's rule names the content.** "Security HIGH/CRITICAL and constraint breaches never qualify for
   CONDITIONAL_PASS", and "closed before the next gate on production; PoC debt due by handoff".
2. **`security-guidelines.md` (stable, `applyTo: "**"`) already requires it:**
   - Rails `:22–24`: "`SECURITY:CRITICAL`/`SECURITY:HIGH` findings block merge per the Security Review Workflow until
     resolved; `SECURITY:MEDIUM` findings require a documented remediation plan before merge";
   - `:153`: the Immutable Security Constraints "are absolute and cannot be overridden by any agent, configuration, or
     runtime decision";
   - `:182–183`: "`CRITICAL` and `HIGH` findings block merge until resolved"; "`MEDIUM` findings must have a remediation
     plan before merge".

**No ranking is needed.** Each clause amended here is a *permission* (CONDITIONAL_PASS "with documented mitigations"; a
Tech Lead waiver). The instruction is a *prohibition*. Both are obeyed by not using the permission for a security
HIGH/CRITICAL finding or a constraint breach. That is joint satisfiability (`gate-verdict-consistency-v1.md`
§1.2(i)). The user's rule then makes the carve-out explicit. **ADR-008 is not needed for any edit here.** One residual
question does need it, and it is reported as a dependency rather than decided (§8, D1).

### 1.6 "Constraint breaches"

I read the user's "constraint breaches" as **breaches of the Immutable Security Constraints** in `security-guidelines.md`
§ Immutable Security Constraints. That is the brief's own reading (§3.1: "Immutable Constraint breaches"), and those are
the only constraints the instruction makes non-overridable (`:153`).

**On the PoC track**, the already-accepted O1 rule also blocks "any required security control omitted, removed, disabled
or weakened, tagged or not" (`poc-orchestrator.md:65`, `poc-security-engineer.md:22`, `rapid-prototyping:74`). Leaving
it out of the new CONDITIONAL_PASS texts would contradict live, user-approved PoC text. So the edits carry it **on the
PoC track only**, by reference. Whether it also applies on the production track is **not** decided here (§8, Q3).

## 2. Ruling on the `validation-gates:67` security nuance

**Ruling: amend `validation-gates` itself (A5–A8), not a specialisation note elsewhere.**

- `validation-gates` is the mandatory skill at every "Phase or validation transition" (`AGENTS.md:67`). A carve-out
  anywhere else would not be read where the verdict is computed.
- **`:67`'s "High findings have documented mitigations" now covers non-security high findings only.** A
  `SECURITY:CRITICAL` or `SECURITY:HIGH` finding, or an Immutable Security Constraint breach, is FAIL until resolved,
  whatever mitigation is documented (A6's note). On the PoC track the omitted-control class is added (§1.6).
- **A `SECURITY:MEDIUM` finding yields at best CONDITIONAL_PASS.** Its remediation plan (owner, fix, deadline) is
  recorded as a tracked condition with the verdict, and in any case before the affected work merges (`:183`). That is
  why A6 also removes PASS for a gate with a `SECURITY:MEDIUM` finding. It mirrors the accepted PoC verdict rule
  (`poc-security-engineer.md:25`: "`CONDITIONAL_PASS` if `SECURITY:MEDIUM` findings remain with their remediation
  plans, otherwise `PASS`").
- **Observation for the Security Engineer.** `validation-gates:74` already defines `critical` as including "security
  vulnerability". So `:67` was mostly ambiguous: how does `SECURITY:HIGH` map onto the gate's own tiers? It was not
  plainly permissive. The amendment removes the ambiguity in either reading.
- **The PoC due point.** `:67` and `:132` say "resolved before the next gate" with no track distinction. On the PoC
  track, that contradicts the user's "PoC debt due by handoff". A6 and A8 split the clause by track. The brief listed
  `:67` as agreeing, but on the PoC track it does not (§7, C2).

## 3. Batch A: required edits (the two named sites plus their same-file and `validation-gates` dependants)

### A1: `tech-lead.md:82`, the Conditions placeholder

````
Before:
- [ ] [Condition 1 — must be resolved before merge]

After:
- [ ] [Condition 1 — owner; due point: before the next gate (production track), or a debt item due by the production handoff (PoC track)]
````

**Why:** same-file coherence with A3. `:82` restates the blocking meaning (`gate-verdict-consistency-v1.md` G2 lists
`:82`, `:90`, `:97`). `:83` `- [ ] [Condition 2]` is unchanged.

### A2: `tech-lead.md:90`, Merge Authorization

````
Before:
- Merge permitted: [Yes | Yes, after conditions met | No]

After:
- Merge permitted: [Yes | Yes, with conditions tracked | No]
````

**Why:** "after conditions met" is the blocking meaning. The value count is unchanged (three).

### A3: `tech-lead.md:97`, the CONDITIONAL_PASS definition

````
Before:
- **CONDITIONAL_PASS**: Code is acceptable with listed conditions that must be addressed before merge. Merge is blocked until conditions are resolved.

After:
- **CONDITIONAL_PASS**: Code is acceptable with listed conditions, and merge is permitted with the conditions tracked (`AGENTS.md` § Validation Gates: "`CONDITIONAL_PASS` proceeds with tracked conditions added to the task list"). List each condition with an owner and a due point; the orchestrator adds it to the task list (`AGENTS.md` § Task Protocol). On the production track a condition is resolved before the next gate; on the PoC track it becomes a debt item (`poc-guidelines.md` § Mandatory Debt Tracking), due by the production handoff. A `SECURITY:CRITICAL` or `SECURITY:HIGH` finding (`security-guidelines.md` § Security Review Workflow), or any breach of an Immutable Security Constraint in `security-guidelines.md`, never qualifies for CONDITIONAL_PASS: the verdict is FAIL until it is resolved. On the PoC track the same applies to any security control `security-guidelines.md` requires that is omitted, removed, disabled or weakened (`poc-orchestrator` § Security Findings).
````

**Authority:** §1.1, §1.2, §1.4. `:96` (PASS) and `:98` (FAIL: "Merge is denied") are unchanged; `:98` already says FAIL
blocks.

### A4: `commands/code-review.md:51–52`

````
Before:
If CONDITIONAL_PASS, list the conditions that must be met before merge.
If FAIL, include blocker details, owner, and retry attempt guidance.

After:
If CONDITIONAL_PASS, list the conditions, each with an owner and a due point. CONDITIONAL_PASS permits the merge, with each condition tracked in the task list (`AGENTS.md` § Validation Gates): on the production track a condition is resolved before the next gate; on the PoC track it becomes a debt item (`poc-guidelines.md` § Mandatory Debt Tracking), due by the production handoff.
A `SECURITY:CRITICAL` or `SECURITY:HIGH` finding (`security-guidelines.md` § Security Review Workflow), or any breach of an Immutable Security Constraint in `security-guidelines.md`, never yields CONDITIONAL_PASS: the status is FAIL until it is resolved. On the PoC track the same applies to any security control `security-guidelines.md` requires that is omitted, removed, disabled or weakened (`poc-orchestrator` § Security Findings).
If FAIL, the merge is blocked; include blocker details, owner, and retry attempt guidance.
````

**Authority:** ADR-007 branch 1, `AGENTS.md` prong (§1.3); the user's rule.

**Deliberately not added: a structured `**Conditions**:` field.** It would close the golden case's capability gap, but
it would also change that case's classification. That is a separate ADR-007 and golden decision (§6, FU-5). A4 names no
field and no list format, so the case's premise stays true (§5).

`:25` ("If status is `fail`, include blocker details …") and the Rails `:56–58` are unchanged.

### A5: `validation-gates/SKILL.md:55`, the template's Conditions line

````
Before:
- [ ] <condition that must be met before proceeding>

After:
- [ ] <condition> — owner: <who>; due: before the next gate (production track) | a debt item due by the production handoff (PoC track)
````

**Why:** "must be met before proceeding" is the blocking meaning, inside the canonical verdict block. `:56`
`- [ ] <condition>` is unchanged.

### A6: `validation-gates/SKILL.md:66–68`, Verdict Rules, plus the security rule

````
Before:
| **PASS** | No critical or high findings. Medium/low findings noted but non-blocking. |
| **CONDITIONAL_PASS** | No critical findings. High findings have documented mitigations. Medium/low with clear remediation plan. All conditions must be resolved before the next gate. |
| **FAIL** | Any critical finding unresolved, OR any high finding without mitigation. Work must return to the implementer. |

After:
| **PASS** | No critical or high findings, and no `SECURITY:MEDIUM` finding. Medium/low findings noted but non-blocking. |
| **CONDITIONAL_PASS** | No critical findings, and none of the security findings excluded below. Other high findings have documented mitigations. Medium/low with clear remediation plan. Each condition is tracked as a task with an owner and a due point: on the production track, all conditions must be resolved before the next gate; on the PoC track, each becomes a debt item (`poc-guidelines.md` § Mandatory Debt Tracking), due by the production handoff. |
| **FAIL** | Any critical finding unresolved, OR any high finding without mitigation, OR any security finding excluded below. Work must return to the implementer. |

**Security findings never qualify for CONDITIONAL_PASS.** `security-guidelines.md` § Security Review Workflow: "`CRITICAL` and `HIGH` findings block merge until resolved". A `SECURITY:CRITICAL` or `SECURITY:HIGH` finding, and any breach of an Immutable Security Constraint in `security-guidelines.md` (which "cannot be overridden by any agent, configuration, or runtime decision"), yields FAIL until it is resolved, whatever mitigation is documented. The "documented mitigations" route above is for non-security high findings only. On the PoC track the same holds for any security control `security-guidelines.md` requires that is omitted, removed, disabled or weakened, tagged or not (`poc-orchestrator` § Security Findings). A `SECURITY:MEDIUM` finding yields at best CONDITIONAL_PASS: its remediation plan (owner, fix, deadline) is recorded as a tracked condition with the verdict, and in any case before the affected work merges (`security-guidelines.md` § Security Review Workflow: "`MEDIUM` findings must have a remediation plan before merge").
````

**Authority:** §1.1, §1.5, §2. The table keeps its three rows and two columns.

**For the Security Engineer:** the PASS-row change (no `SECURITY:MEDIUM`) and the MEDIUM sentence apply `:183` and the
brief's statement. They are not words the user used (§8, Q5).

### A7: `validation-gates/SKILL.md:75`, the `high` severity definition

````
Before:
| `high` | Significant defect or design flaw. Must be addressed before release. |

After:
| `high` | Significant defect or design flaw. Must be addressed before release; a `SECURITY:HIGH` finding blocks merge until resolved (§ Verdict Rules). |
````

**Why:** "before release" is later than `security-guidelines:182`'s "before merge". This makes the security exception
explicit where the tier is defined.

### A8: `validation-gates/SKILL.md:131–132`, Handle a CONDITIONAL_PASS Verdict

````
Before:
1. Proceed with work, but track all conditions as tasks.
2. Conditions MUST be resolved before the next gate in the pipeline.

After:
1. Proceed with work, but track all conditions as tasks, each with an owner and a due point. At the Implementation gate, proceeding includes the merge.
2. On the production track, conditions MUST be resolved before the next gate in the pipeline. On the PoC track, each condition instead becomes a debt item (`poc-guidelines.md` § Mandatory Debt Tracking), due by the production handoff.
````

**Authority:** the user's rule ("allows merge"; the two due points); `code-review:151` ("allows merge").
`:133–135` are unchanged.

## 4. Batches B and C: other sites where the security exception applies (recommended)

These sites let a security HIGH finding through, or let a waiver lift one. The acceptance criterion "the security
exception is explicit everywhere it applies" reaches them. **They are separable from Batch A.** B touches a stable,
possibly golden-covered command (§5), and C was parked by the orchestrator as v3 X7 (`poc-security-reviewer-blocking-v3`
§16.2). Including them is the orchestrator's call. I recommend both.

### B1: `testing-strategy/SKILL.md:240`, the Security scan threshold row

````
Before:
| **Security scan** | No critical/high findings | No critical; high findings have mitigations | Any critical finding |

After:
| **Security scan** | No critical/high findings | No critical or high findings; each medium finding has a remediation plan (`security-guidelines.md` § Security Review Workflow) | Any critical or high finding, or any breach of an Immutable Security Constraint (`security-guidelines.md`) |
````

**Why:** the same defect as `validation-gates:67`, in a second stable skill ("high findings have mitigations" yields
CONDITIONAL_PASS). **Authority:** §1.5. The column count is unchanged.

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
If any CRITICAL or HIGH findings exist, or any Immutable Security Constraint in `security-guidelines.md` is breached, the verdict MUST be FAIL (`security-guidelines.md` § Security Review Workflow: "`CRITICAL` and `HIGH` findings block merge until resolved"). CONDITIONAL_PASS is available only when the remaining findings are MEDIUM or LOW, with a remediation plan for each MEDIUM finding.
````

### B4: `commands/security-audit.md:73`, Rails Failure mode

````
Before:
**Failure mode**: If any CRITICAL finding exists, the verdict MUST be FAIL — the command cannot return PASS/CONDITIONAL_PASS while a CRITICAL finding is unresolved.

After:
**Failure mode**: If any CRITICAL or HIGH finding exists, or an Immutable Security Constraint is breached, the verdict MUST be FAIL — the command cannot return PASS/CONDITIONAL_PASS while such a finding is unresolved.
````

**B2–B4 authority:** ADR-007 branch 1, stable-instruction prong (§1.3); the user's rule. Every edit tightens; none
relaxes (ADR-007 §5). `security-engineer.md:152` ("`fail` when any unresolved critical or high severity vulnerability
remains") already agrees, so the command moves toward the agent it runs.

### C1: `code-review/SKILL.md:150`, the Tech Lead waiver

````
Before:
1. A `FAIL` verdict blocks the merge request — no override without Tech Lead waiver (documented as a decision artifact).

After:
1. A `FAIL` verdict blocks the merge request — no override without Tech Lead waiver (documented as a decision artifact). No waiver applies to a `SECURITY:CRITICAL` or `SECURITY:HIGH` finding or to a breach of an Immutable Security Constraint: `security-guidelines.md` says "`CRITICAL` and `HIGH` findings block merge until resolved" (§ Security Review Workflow), and that its Immutable Security Constraints "cannot be overridden by any agent, configuration, or runtime decision".
````

### C2: `code-review/SKILL.md:151`, the due point

````
Before:
2. A `CONDITIONAL_PASS` verdict allows merge but **requires** that each should-fix item is logged as a task in `docs/tasks/active-tasks.md` with an assigned owner and target sprint.

After:
2. A `CONDITIONAL_PASS` verdict allows merge but **requires** that each should-fix item is logged as a task in `docs/tasks/active-tasks.md` with an assigned owner and target sprint. On the production track the item is resolved before the next gate; on the PoC track it becomes a debt item (`poc-guidelines.md` § Mandatory Debt Tracking), due by the production handoff.
````

**Why:** today it is jointly satisfiable, but a "target sprint" can fall after the next gate. This aligns it with the
user's due points. It is optional, and it sits in C only because it is in the same file as C1 and C3.

### C3: `code-review/SKILL.md:159`, Rails Failure mode

````
Before:
**Failure mode**: A `FAIL` verdict halts the pipeline and requires re-review after fixes; a `FAIL` may not be overridden without a documented Tech Lead waiver decision artifact.

After:
**Failure mode**: A `FAIL` verdict halts the pipeline and requires re-review after fixes; a `FAIL` may not be overridden without a documented Tech Lead waiver decision artifact, and a `FAIL` for a `SECURITY:CRITICAL` or `SECURITY:HIGH` finding or an Immutable Security Constraint breach may not be overridden at all (§ Review as Validation Gate).
````

### C4: `tech-lead.md:111`, Merge and Architecture Authority

````
Before:
3. Require explicit waiver reference for any approved exception and escalate unresolved conflicts to orchestrator.

After:
3. Require explicit waiver reference for any approved exception and escalate unresolved conflicts to orchestrator. No waiver applies to a `SECURITY:CRITICAL` or `SECURITY:HIGH` finding or to a breach of an Immutable Security Constraint (`security-guidelines.md`).
````

**C1, C3 and C4 authority:** §1.5 (joint satisfiability: the waiver is a permission, `:182` and `:153` are
prohibitions). The precedent is v3 E11, which made the same carve-out for the PoC track (`rapid-prototyping:74`: "No
Tech Lead waiver applies to it"). The PoC omitted-control class is not repeated in C1, C3 and C4, because
`rapid-prototyping:74` already covers it. **C carves out security only.** Whether "FAIL blocks" abolishes the waiver for
non-security FAILs is not decided (§8, Q1).

## 5. Golden coupling and blast radius

**The open case `code-review-conditional-pass-conditions-gap`** (read under grant):
- `brief.md:11–12` and `expect.py:4–5` quote "If CONDITIONAL_PASS, list the conditions that must be met before merge."
  After A4 **both quotes are stale**.
- `check()` (`expect.py:15–29`) reads only `fixture/review.md`: `**Status**: CONDITIONAL_PASS` plus a `**Conditions**:`
  field or a `## Conditions` section with a list item. **No command text is read, so the result does not change**
  (known_failing).
- **The category premise stays true.** `brief.md:13–15` says the command specifies "no required field name, no required
  list format". A4 adds per-condition content (owner, due point) but no field name and no list format. So
  `capability_gap` is still accurate. The brief's "Why known_failing" paragraph (`:21–29`) stays accurate.
- Refreshing the quotes is a protected-path edit (grant, and a baseline if `expect.py` changes). **Not ruled** (§6,
  FU-2).

**The open case `validate-workflow-gate-verdict-sources`** (not read; from `gate-verdict-consistency-v1.md` §8 and
§13.1):
- Its `expect.py` reads a **fixture copy** of `validation-gates`: the § Gate Types rows, the § Verdict Format sentence
  and the `**Gate:**` field.
- A5–A8 touch none of those lines, so its **result should not change (unverified)**.
- The fixture copy will **no longer be byte-identical** to source, so the case brief's Provenance statement goes stale.
  Whether a test enforces that identity is **(unverified)**; T568 and §13.1 checked it by hand with `cmp`.

**Other possible golden coupling (unverified; search `tests/golden/` with `held-out` pruned before traversal):**
`Merge is blocked until conditions`, `after conditions met`, `must be resolved before merge`,
`must be met before proceeding`, `High findings have documented mitigations`, `high findings have mitigations`,
`Must be addressed before release`, `Conditions MUST be resolved before the next gate`, `If any CRITICAL findings exist`,
`If any CRITICAL finding exists`, `fix within current sprint`, `no override without Tech Lead waiver`,
`Require explicit waiver reference`, `with an assigned owner and target sprint`, `Merge permitted`.

**Held-out:** not read. The implementing task detects held-out coupling only through `scripts/scorecard.py --check`
regressions against the current baseline.

**Files and mechanics:**

| File | Edits | Maturity | Note |
|---|---|---|---|
| `implementation/knowledge/agents/tech-lead.md` | A1, A2, A3, (C4) | experimental | — |
| `implementation/knowledge/commands/code-review.md` | A4 | experimental | golden quote stale (above) |
| `implementation/knowledge/skills/validation-gates/SKILL.md` | A5–A8 | stable | fixture-copy provenance (above) |
| `implementation/knowledge/skills/testing-strategy/SKILL.md` | (B1) | stable | coupling unverified |
| `implementation/knowledge/commands/security-audit.md` | (B2–B4) | stable | golden-covered command? **(unverified)** |
| `implementation/knowledge/skills/code-review/SKILL.md` | (C1–C3) | stable | coupling unverified |

- **Generated outputs:** `node implementation/scripts/sync.mjs --root implementation` and
  `python3 implementation/scripts/generate-registry.py`, both confirmed with `--check`.
- **Root projections:** declare exactly what `--print-drift` reports in `tests/_baselines/root-install-drift.json`.
  That is up to 3 files × 7 platforms for Batch A, or 6 × 7 for all batches **(count unverified)**.
- **Maturity:** a P2 task editing these files should not affect `check-maturity` (`gate-verdict-consistency-v1.md`
  §13.1 #7: only P0/P1 rows count). **Affects:** `—`.
- **Unchanged:** `AGENTS.md`, `security-guidelines.md`, `poc-guidelines.md`, `orchestrator.md`,
  `poc-orchestrator.md`, `poc-security-engineer.md`, `rapid-prototyping`, and everything under `tests/golden/**`.

## 6. Follow-ups

| ID | Covers | Files | `tests/golden/**` grant? | Owner (suggested) | Priority | Depends on / verify |
|---|---|---|---|---|---|---|
| **FU-0**: security review of this artifact | §2, A3, A4, A6, A7, B, C; Q3, Q5 | this artifact (read-only) | No | Security Engineer | P2 | Before FU-1. The user's rule says the security wording is reviewed first. |
| **FU-1**: apply P39 | Batch A; B and C if the orchestrator includes them | §5 table; mirrors; registry; root-drift declaration | **No** | Backend Developer (needs a shell) | P2 | FU-0. **Verify:** see the list below. |
| **FU-2**: refresh the stale golden quotes | `code-review-conditional-pass-conditions-gap` `brief.md:11–12`, `expect.py:4–5` docstring | those two files only | **Yes** (`protected-paths-v1.md` §5, scoped to this one case directory); a baseline authorization if `expect.py` changes | QA Engineer | P2 | After FU-1. **Not ruled here** (brief §2). The result does not change. |
| **FU-3**: `validate-workflow` fixture copy of `validation-gates` | Provenance (§5) | that case's fixture copy and brief | **Yes** | QA Engineer | P2 | Only if FU-1's checks show the provenance must stay byte-identical, or a test enforces it. **Not ruled.** |
| **FU-4**: user question Q1 (waiver and escalation for non-security FAILs) | `code-review:150,159`; `tech-lead:111`; `receiving-code-review:86` | — | No | Orchestrator → user | P2 | Independent of FU-1 |
| **FU-5** *(candidate)*: a structured `**Conditions**:` field in `/code-review`'s VERDICT | Closes the capability gap | `commands/code-review.md`; the case's classification | **Yes** | Solution Architect, then QA | P2 | A separate ADR-007 decision. It changes the case's category. Not proposed for FU-1. |
| **D1** (P40): criteria ranking | §8 D1 | — | — | — | — | **Dependency on ADR-008 (T581).** Unaffected by FU-1. |

**FU-1 verification:**
1. Each applied `Before:` matches **exactly once by text** on `develop` at dispatch.
2. 0 hits under `implementation/knowledge/` for: `Merge is blocked until conditions are resolved`,
   `Yes, after conditions met`, `must be resolved before merge`, `conditions that must be met before merge`,
   `must be met before proceeding`, `High findings have documented mitigations`. With Batch B, also
   `high findings have mitigations` and `Exploitable with moderate effort, fix within current sprint`.
3. Exactly 1 hit for `Security findings never qualify for CONDITIONAL_PASS` (in `validation-gates`), and 1 for
   `Yes, with conditions tracked` (in `tech-lead`).
4. `AGENTS.md`, `security-guidelines.md`, `poc-guidelines.md` and `tests/golden/**` are byte-unchanged.
5. `sync.mjs --check` and `generate-registry.py --check` are clean. The root parity gate is green.
6. `scripts/scorecard.py --check` is unchanged against the current baseline. A regression is held-out coupling: stop and
   report it.
7. `check-maturity.py --root implementation`: 0 failing.
8. `python3 docs/tasks/validate-tasks.py` passes. Run `python3 tests/run.py`, check its exit code, and redirect its
   output to a file.
9. Report the `cmp` of the `validate-workflow` fixture copy of `validation-gates` against source. A difference is
   expected; the case's result must be unchanged.

## 7. Corrections to the brief (`unclear_requirements`, `minor`)

- **C1: `tech-lead` contradicts the rule at three lines, not one.** `:82` ("must be resolved before merge") and `:90`
  ("Yes, after conditions met") restate `:97`. `gate-verdict-consistency-v1.md` G2 already listed all three.
- **C2: `validation-gates:67` does not fully agree.** Its "All conditions must be resolved before the next gate" (and
  `:132`) has no track split, so on the PoC track it contradicts "PoC debt due by handoff". `:55` ("must be met before
  proceeding") and `:75` (high "before release") also needed edits.
- **C3: more sites let a security HIGH through** than the brief lists: `testing-strategy:240`; `/security-audit:44,
  :67, :73`; and the waiver at `code-review:150, :159` and `tech-lead:111` (§4).
- **C4: "A MEDIUM security finding is a CONDITIONAL_PASS" holds at the gates `validation-gates` governs. At the code-review
  gate it is in tension with `code-review:96`**, which makes any "security issue" a 🔴 Must Fix, and with `:128`, which
  makes any must-fix finding FAIL. That is P40 (D1). Batch A therefore states no MEDIUM rule in `tech-lead` or
  `/code-review`.
- **C5:** the facts were verified on `1682077`; the worktree is at `dd7703b`. Every cited line matches.

## 8. Open questions and dependencies (not decided)

- **Q1 (`unclear_requirements`, minor): does "FAIL blocks" abolish the Tech Lead waiver for non-security FAILs?**
  `code-review:150` and `:159` and `tech-lead:111` allow a documented waiver, and `receiving-code-review:86` says FAIL
  blocks "until resolved or escalated". `AGENTS.md:54` has no waiver. The user's three words do not say. C1, C3 and C4
  carve out security only, which `:182` and `:153` already compel.
- **Q2 (`unclear_requirements`, minor): what is "due" by the production handoff?** It could mean *recorded* in the debt
  handoff (with the fix done in production), or *fixed* by then. The edits use the user's words, so they are correct
  under either reading. The user's own P39 question ("with debts left for production", plan-100 §1) supports
  *recorded*. `poc-orchestrator.md:66` gives a security MEDIUM's fix a "deadline no later than the production handoff",
  and that stays as it is.
- **Q3 (for the Security Engineer, minor): the omitted-control class on the production track.** It is applied on the PoC
  track only (§1.6). `security-guidelines` Rails `:17–18` ("no authority to disable a security control 'temporarily,'
  even in PoC or development mode") arguably reaches production *a fortiori*. At the code-review gate, `code-review:96`
  already makes it FAIL. At the production security gate a MEDIUM omitted control would be CONDITIONAL_PASS under A6.
- **Q4 (minor): conditions on the Release gate have no "next gate".** `release-manager.md:45` requires "explicit risk
  acceptance for any `conditional_pass` prior to production deployment". The rule's production due point does not
  define this case. Not edited.
- **Q5 (for the Security Engineer): A6's PASS-row change and its MEDIUM sentence** apply `:183` and the brief. They go
  beyond the user's words.
- **D1 (`dependency`, minor): P40.** At the implementation gate, `code-review:96` and `:128` make any security issue
  FAIL, while `validation-gates`, `security-guidelines:183` and the PoC rules allow CONDITIONAL_PASS for MEDIUM.
  Deciding whose criteria compute the verdict is a ranking among stable skills, which is ADR-008 (T581). **Not decided.**
  No edit here depends on it.

**Blockers:** none. No edit needs an ADR-008 ranking (§1.5).

## 9. Unverified claims (need a shell)

1. No other text under `implementation/knowledge/` says CONDITIONAL_PASS blocks a merge, or lets a security
   HIGH/CRITICAL finding through. I did **not** read: `ci-cd-pipeline` (it consumes the verdict at the `approve` stage,
   `code-review:148`), `checkpoint-protocol`, `task-management`, `blocker-escalation`, `verification-before-completion`,
   `gitlab-management`, `worktree-isolation`, `poc-evaluation`, `backend-developer`, `frontend-developer`,
   `devops-engineer`, `scrum-master`, `poc-qa-engineer`, `evaluation-agent`, `/validate-workflow`, `/prepare-release`,
   `/new-feature`, `/batch`, or `implementation/SECURITY.md`. Suggested search: the §5 pattern list plus
   `conditional_pass`, `CONDITIONAL_PASS`, `before merge`, `waiver`, `risk accept` and `mitigation`, over
   `implementation/knowledge/`, `implementation/SECURITY.md` and `AGENTS.md`.
2. No golden case outside the granted one asserts any amended text (§5 pattern list; `held-out` pruned).
3. Whether `/security-audit` has golden coverage, and whether any fixture has a HIGH finding with CONDITIONAL_PASS. If
   one does, B3 makes that fixture non-conforming while its `check()` stays unchanged.
4. No test outside `tests/golden/` asserts text in the six files (search `tests/` with `golden` excluded, using the §5
   patterns).
5. The `validate-workflow` case's `expect.py` reads no line A5–A8 touch, and no test enforces byte-identity of its
   fixture copy.
6. The root-projection count.
7. `registry/summary.md` lists `poc-security-engineer` as `stable`, while v3 §2 says it was held at `beta`. I assume it
   was re-promoted after T579 (FU-2 of v3). This is irrelevant to the edits.

## 10. Summary

| Site | Ruling | Edit | Authority |
|---|---|---|---|
| `tech-lead:97` (+ `:82`, `:90`) | Merge permitted with tracked conditions (owner, due point); production: before the next gate; PoC: debt due by handoff; security HIGH/CRITICAL and constraint breaches → FAIL | A1–A3 | User; `AGENTS.md:55`; T542/FU-C (self-description `:29–30`, `:68`) |
| `/code-review:51–52` | Same; FAIL blocks; no Conditions field added | A4 | User; ADR-007 b1 (`AGENTS.md` prong) |
| `validation-gates:55, 66–68, 75, 131–132` | Track-split due points; security never conditional; MEDIUM at best conditional | A5–A8 | User; `security-guidelines:22–24, 153, 182–183`; joint satisfiability |
| `testing-strategy:240` | High security finding no longer conditional | B1 | as A6 |
| `/security-audit:44, 67, 73` | HIGH and constraint breach → FAIL | B2–B4 | ADR-007 b1 (stable-instruction prong) |
| `code-review:150, 151, 159`; `tech-lead:111` | No waiver for security HIGH/CRITICAL or constraint breach; due points | C1–C4 | `:153`, `:182`; v3 E11 precedent |
| Non-security waiver; "due"; production omitted controls; release-gate conditions; PASS-row MEDIUM | Open | — | Q1–Q5 |
| P40 criteria ranking | Dependency on ADR-008 | — | D1 |
| Golden | 1 open case's quotes stale, result unchanged; 1 fixture-copy provenance stale; held-out via `scorecard --check` | FU-2, FU-3 | — |
