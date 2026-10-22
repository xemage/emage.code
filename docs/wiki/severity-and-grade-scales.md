---
title: Severity and Grade Scales
---
# Severity and Grade Scales

Last updated: 2026-10-22 (T674, SC634-1 to SC634-5 of `docs/artifacts/tracked-debt-register-v1.md`).
Based on: the draft tables of `docs/artifacts/adr-008-status-and-severity-scales-v1.md` §2, re-checked on 2026-10-22 against the defining documents named in the tables (read in the working tree; no line numbers are cited because lines move, sections are).

emage.code uses several scales that share words. `critical`, `high`, `medium` and `low` name five different scales below, and `P0` is a priority, not a severity. **Always name the scale.** This page is a reference, not a rule.

- **Descriptive, never ranking.** Each row points to the document that defines the scale, and that document governs (principle P4 of ADR-008: nothing here orders documents; cited from the draft, ADR-008 itself was not re-read for this page **(unverified)**). If a row differs from its source, the source wins and this page is the defect: report it.
- **Values are written as the source writes them.** Casing differs between documents for the same value (see [Known gaps](#known-gaps)).
- The Migration section M-6 of the v8.0.0 release document (`docs/releases/v8.0.0.md`) compares the old and the new vocabulary of the v8 release. It is a dated record and stays unchanged; this page is the standing reference.

## Table 1: the scales

| ID | Scale | Values | What it grades | Used by | Defined in |
|----|-------|--------|----------------|---------|------------|
| S1 | Blocker severity | `critical`, `major`, `minor` | Impact of a **blocker** on tasks and the timeline | Every agent that reports a blocker; the orchestrator when it triages; `/team-status` (writes `CRITICAL/MAJOR/MINOR` in its blocker table) | `AGENTS.md` § Blocker Protocol (the set); skill `blocker-escalation` § Severity Definitions (the criteria) |
| S2 | Bug severity | `Critical`, `High`, `Medium`, `Low` | Impact of a **reported bug** | `/bug-report` (orchestrator); `qa-engineer` bug reports | `/bug-report` § Severity; `qa-engineer` § Bug Report Format. No per-level definitions beyond "with justification" |
| S3 | Task priority | `P0`, `P1`, `P2` | **Scheduling** priority of a task (not a severity) | The orchestrator (the ledger's Priority column) | `AGENTS.md` § Task Protocol (`P0` is the critical path) |
| S4 | PoC debt severity | `Critical`, `Medium`, `Low` in the scorecard; `critical`, `medium`, `low` in the debt ledger | Impact of one `POC-DEBT` item | `poc-orchestrator`, `technical-debt-narrator`, the Tech Lead's scorecard review | `poc-guidelines.md` § Debt Scorecard (inventory column, Scorecard Rule 5); skill `technical-debt-tracking` § Debt Item Format and its severity assignment guide |
| S5 | Security grade | `SECURITY:CRITICAL`, `SECURITY:HIGH`, `SECURITY:MEDIUM`, `SECURITY:LOW` | Severity of a **security finding** | `security-engineer`, `poc-security-engineer`, any gate that raises a security finding | `security-guidelines.md` § Security Review Workflow (the grades and what they require); agent `security-engineer` § Findings Classification (the definitions, with a time SLA); `/security-audit` § Severity Classification (its own definitions; the higher grade of the two applies) |
| S6 | Code-review level | `Must Fix`, `Should Fix`, `Nice to Have` | The **action** a review finding requires (block merge, request changes, comment only) | `tech-lead`, `/code-review` | Skill `code-review` § Feedback Format and § Severity Guide; `/code-review` (the counts in its VERDICT) |
| S7 | Gate finding severity | `critical`, `high`, `medium`, `low` | Severity of a **finding in a gate verdict**, any gate | Every gate executor (Tech Lead, QA, Security, Release Manager) | Skill `validation-gates` § Verdict Format (Findings table) and § Severity Definitions |
| S8 | GitLab priority label | `priority::critical`, `priority::high`, `priority::medium`, `priority::low` | Priority of a **GitLab issue** | `scrum-master`, `orchestrator` (issues mirror the ledger) | Skill `gitlab-management` § Label Setup and § Priority Labels and the Ledger Priority |
| V1 | Gate verdict (an outcome, not a severity) | `PASS`, `CONDITIONAL_PASS`, `FAIL` | The **result of one gate**; also the Status of the `RELEASE VERDICT` | Every gate executor; `/code-review`, `/security-audit`, `/prepare-release` | `AGENTS.md` § Validation Gates; skill `validation-gates` § Verdict Rules |

Notes on single rows:

- **S1.** A blocker's severity is about delay, not defect. A `critical` blocker also shortens the retry rule (skill `blocker-escalation` § The 2-Retry Rule).
- **S2.** The flags `[RELEASE_BLOCKER]` and `[TEAM_BLOCKER]` of `/bug-report` are not severities. A bug that blocks work is also reported as a blocker on S1.
- **S4.** `Critical` means "must fix before production" and always carries the disposition `must_fix_pre_prod`. Since v8 there is no `high` tier. `INCONCLUSIVE` and the sizes `XS` to `XL` are gone (release document M-6).
- **S5.** Reports sometimes write the grade without the prefix (`CRITICAL`, `HIGH`, ...). The definitions carry a time SLA (due-date overlay, not a scale); the SLA never permits what the workflow blocks. `SECURITY:CRITICAL` and `SECURITY:HIGH` block merge; `SECURITY:MEDIUM` needs a remediation plan (owner, fix, deadline) before merge; `SECURITY:LOW` is tracked as technical debt.
- **S6.** Defined by action, not by impact. `Well Done` is praise, not a level.
- **V1.** The lower-case forms (`pass`, `conditional_pass`, `fail`) in `security-engineer`, `qa-engineer` and `/code-review` step 7 carry the same values. Each gate records one verdict.

## Table 2: how the scales relate

"Maps" means a defining document says that a value of one scale is a value of another. Everything marked "does not map" is explicitly not a mapping: do not infer one.

| Pair | Relation | Source |
|------|----------|--------|
| S5 and S7 | **Maps 1:1.** `SECURITY:CRITICAL` is `critical`, `SECURITY:HIGH` is `high`, `SECURITY:MEDIUM` is `medium`, `SECURITY:LOW` is `low`. What each grade requires comes from the verdict rules and the security guidelines; the tier never lowers it | `validation-gates` § Severity Definitions |
| S5 and S4 | **One-way handling rules, not a value map.** A `SECURITY:CRITICAL` or `SECURITY:HIGH` finding, an Immutable Security Constraint breach and an omitted or weakened required control are never debt. A `SECURITY:MEDIUM` finding is `Critical` debt. A `SECURITY:LOW` finding is tracked as debt and its tier comes from the S4 guide. S4 `Critical` is not a `SECURITY:CRITICAL` grade | `poc-guidelines.md` Scorecard Rule 5; `technical-debt-tracking` (merge step); `security-guidelines.md` § Security Review Workflow |
| S6 and S7 | **Does not map; both apply to the same verdict.** Grade each finding on both and give the most restrictive verdict either requires. A Must Fix finding is `FAIL`; only Should Fix findings give `CONDITIONAL_PASS`; a `high` finding without a documented mitigation is `FAIL` even when graded Should Fix (a security finding graded high or critical is `FAIL` even with a documented mitigation, `validation-gates` § Verdict Rules) | `code-review` § Protocol-Aware Enhancements; `validation-gates` § Verdict Rules |
| S6 and S5 | **Does not map.** A security finding is graded on S5 and, as a review finding, on S6. Must Fix lists "security issue" without a grade; no document makes every `SECURITY:MEDIUM` finding a Must Fix | `code-review` § Severity Guide |
| S7 and S4 | **Does not map.** S4 has no `high`. On the PoC track a `CONDITIONAL_PASS` condition becomes a debt item whose S4 tier comes from the S4 guide, not from the finding's S7 value (a security finding is excepted: see rows S5 and S4; a `SECURITY:MEDIUM` finding is `Critical` debt and is not deferred past the handoff) | `validation-gates` § Handle a CONDITIONAL_PASS Verdict; `technical-debt-tracking` |
| S6 and S4 | **Does not map.** Must Fix and Should Fix findings are merged into the debt ledger, and each item is then given an S4 tier by the guide | `technical-debt-tracking` § POC-DEBT Tag Scanning Procedure |
| S2 and S3 | **Maps, many to one.** `critical` and `high` become `P0`, `medium` becomes `P1`, `low` becomes `P2`. This is the only severity-to-priority rule for bugs | `/bug-report` § Task Creation |
| S8 and S3 | **Maps the same way, and does not reverse.** `priority::critical` and `priority::high` agree with `P0`, `priority::medium` with `P1`, `priority::low` with `P2`. `P0` therefore agrees with two labels | `gitlab-management` § Priority Labels and the Ledger Priority |
| S4 and S3 | **Maps through the disposition, not directly.** `must_fix_pre_prod` is proposed at `P0`, `can_defer_post_ga` at `P1`, `monitor_only` gets no task. A `Critical` item is always `must_fix_pre_prod` | `technical-debt-tracking` § Promotion Procedure |
| S1 and every other scale | **Does not map.** Blocker severity is about delay. A defect that blocks work is reported on its own scale and, separately, as a blocker on S1 | `AGENTS.md` § Blocker Protocol; `/bug-report` § Blocker Classification |
| S2 and S4, S5, S7 | **Does not map.** The words overlap (`High`, `Critical`) but no document equates them. A bug that is a security finding is graded on S5 as well | (absence: no document states a mapping) |
| V1 and the severity scales | The verdict is derived from the findings by each gate's rules (S7 in `validation-gates` § Verdict Rules, S6 in `code-review`, S5 in `security-guidelines.md`); the most restrictive verdict wins | `validation-gates` § Verdict Rules |

## Adjacent vocabularies (outside the table's reach)

These are not severity scales, but they use similar words or sit beside the scales above. Each is named so that it is not mistaken for one of them.

| Vocabulary | Values | Defined in |
|------------|--------|------------|
| Task lifecycle state | `pending`, `in_progress`, `blocked`, `in_review`, `done`, `cancelled` | `AGENTS.md` § Lifecycle States |
| PoC outcome | `VALIDATED` or `INVALIDATED` in the scorecard `## Result`; `Validated` or `Invalidated` as the evaluation agent's Verdict (weak or untested evidence is `Invalidated`); production recommendation `proceed`, `proceed_with_constraints`, `do_not_proceed` | `poc-guidelines.md` § Debt Scorecard; agent `evaluation-agent` |
| Debt disposition and effort | `must_fix_pre_prod`, `can_defer_post_ga`, `monitor_only`; effort `S`, `M`, `L` | Skill `technical-debt-tracking` § Debt Item Format |
| Feasibility rating | Red, Yellow, Green with a Go or No-Go recommendation | Agent `feasibility-agent` (as described in [Agents Overview](agents-overview); the agent source was not re-read for this page **(unverified)**) |
| Component maturity | `experimental`, `beta`, `stable` | `docs/artifacts/maturity-promotion-criteria-v1.md` (as cited in [Commands and Skills Overview](commands-and-skills-overview)); not re-read for this page **(unverified)** |
| Golden-case status and category (test suite) | for example `expected_pass`, `known_failing` with a reason such as `tracked_defect` or `capability_gap` | The golden suite's own documentation; not re-read for this page **(unverified)** |
| QA test-case priority | `High`, `Medium`, `Low` | Agent `qa-engineer` § Test Case Template |
| Security SLA | "Must fix before release", "Fix within current sprint", "Fix within next sprint" | Agent `security-engineer` § Findings Classification (an overlay on S5, see Table 1) |

## Known gaps

These are open points found while writing the page. They are recorded, not decided: a ruling belongs to the owner of the defining document.

1. **An unnamed scale in blocker lines (SC634-2).** The blocker lines of agent `security-engineer` (§ VERDICT Format, "Blockers (if FAIL)") and of agent `qa-engineer` (§ Structured Test Report, "Blockers (if FAIL)") write `severity=[sev]` without naming a scale. `AGENTS.md` § Blocker Protocol defines blocker severity as `critical`, `major`, `minor`, so reading `[sev]` as S1 is consistent; for a blocking security finding the S5 grade also fits. The register records the S1 reading as consistent with ruling T617 O-1 **(unverified here: that ruling was not re-read)**.
2. **The S4 tier for a `SECURITY:LOW` finding (SC634-3).** It is left to the S4 assignment guide; no document fixes it. Only `SECURITY:MEDIUM` has a fixed S4 tier (`Critical`).
3. **Casing (SC634-4).** The same values appear in different casing: S4 (`Critical` in the scorecard, `critical` in the ledger), S5 (`SECURITY:HIGH`, `HIGH`, `High` in a report's Risk Level), V1 (`PASS`, `pass`, `Pass`). No document read says that values are compared case-insensitively.
4. **Scales out of the table's reach (SC634-5).** Those listed under "Adjacent vocabularies". The `priority::` labels, which an earlier draft left out, are now S8 (ruled and applied in T621 and T624, release document M-6).
5. **Also found while writing this page.**
   - Agent `qa-engineer` § Bug Report Format lists the priorities `P0`, `P1`, `P2`, `P3`, while `AGENTS.md` § Task Protocol defines `P0`, `P1`, `P2`. A QA bug report may therefore carry a priority that the ledger does not have.
   - Skill `release-workflow` § Hotfix Workflow says to "assign a severity (must be critical or high)" without naming the scale (S2 writes `Critical`, `High`; S7 writes `critical`, `high`).
   - Agent `security-engineer` § Security Review Report Format has a "Risk Level" of `Critical`, `High`, `Medium`, `Low` and a "Status" of `Pass`, `Fail`, `Conditional Pass`; both repeat S5 and V1 in a third casing.
