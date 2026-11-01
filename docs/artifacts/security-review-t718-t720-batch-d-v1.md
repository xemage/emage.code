# Artifact: security-review-t718-t720-batch-d-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer. Read-only: the reviewer had no shell and read the diffs from files the orchestrator exported. The orchestrator recorded this artifact from the reviewer's two reports.
- **Gate**: security. **Date**: 2026-11-01.
- **Target**: plan-127 (LOW batch D) on `docs/plan-127-batch-d`.
  - First review at `7501f0d5`, covering T718 (rulings and ADR-011), T719 (knowledge edits) and T720 (rulings and ADR-011 applied).
  - Re-check of the SEC-T720-01 fix, commit `06a48087`.
- **Based on**:
  - `docs/decisions/ADR-011-user-accepted-medium-at-release.md` (Accepted 2026-11-01) and `docs/artifacts/rulings-batch-d-v1.md`
  - `docs/plans/plan-127-batch-d-knowledge-and-rulings.md`
  - the changed knowledge files: `release-manager`, `orchestrator`, `security-engineer`, `qa-engineer`, `scrum-master`, `validation-gates`, `release-workflow`, `dependency-graphing`, `/prepare-release`, `/discover-skills`, `/batch`
  - `docs/releases/_template.md`, `docs/wiki/mcp-servers.md`, `docs/wiki/severity-and-grade-scales.md`

## Verdict: PASS (after the re-check)

The first review was CONDITIONAL_PASS, with one MEDIUM (SEC-T720-01). The fix closes it.

- No CRITICAL or HIGH finding.
- No breach of an Immutable Security Constraint.
- No required control weakened. `security-guidelines.md` and `AGENTS.md` are untouched.

The PASS holds with SEC-T720-02 to -08 tracked as LOW debt. This artifact is the record; the next register version takes them over.

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 1 | 1 (SEC-T720-01) | 0 |
| LOW | 7 | 0 | 7 (tracked, section 3) |

## 1. Rulings on the changes

- **ADR-011, the MEDIUM accepted at a release** (`validation-gates/SKILL.md:70`, A1; `release-manager.md:43`, A7). Sound.
  - Only the user can accept. No agent grants, extends or infers an acceptance.
  - An acceptance covers one release only, and is never carried over (A7: "an acceptance given for an earlier release does not cover this one").
  - It never covers CRITICAL or HIGH, a breach of an Immutable Security Constraint, or a weakened required control.
  - Every place in `implementation/knowledge/` that repeats the rule is one of the A1-A13 rows. The reviewer confirmed this with the `security-audit` grep on develop, so coverage is complete.
- **The pointers A2 to A13** point to § Verdict Rules and copy nothing. Sound.
- **The orchestrator's wording in `/prepare-release` step 9** changes "never such a condition" to "never such a next-cycle condition". It weakens nothing: "such" already meant the next-cycle condition, and the list after it still covers every grade. Without it, line 64 would contradict A11 at line 72.
- **Release-gate rulings.**
  - SEC-T693-02 fails closed: a missing, stale or FAIL independent-check row gives FAIL.
  - SEC-T693-03 and -05 are sound. The top-level session's own verification before the merge is kept.
  - SEC-T693-06 now puts the Release Gate before deployment.
  - SEC-T693-09 closes the list of fields that may change after the check (residual: SEC-T720-04).
  - R4 and R10 add `Issued at commit` and `Independent check` (the user: "O1: both fields (Recommended)").
- **T719 edits.**
  - The `/batch` slug character set cannot traverse paths or break a table row.
  - Removing `/discover-skills` step 6 reduces the input surface (ADR-007 branch 1).
  - The VS Code wiki advice (single-folder workspace) protects what `--allowed-root .` points to.
  - The other T719 edits have no security impact.
- **SEC-T720-01 fix** (`06a48087`): the reviewer's four texts, applied word for word.
  - (a) `validation-gates/SKILL.md:120`: a Release Gate input that lists every medium an earlier release shipped under the user's acceptance and that is not yet fixed.
  - (b) `validation-gates/SKILL.md:146`: such a finding is never checked off as resolved.
  - (c) `release-workflow/SKILL.md:114`: the checklist line.
  - (d) `release-workflow/SKILL.md:206`: the abbreviated hotfix Release gate keeps that input.
  - None widens a rule. A wording tension with A4 ("counts as resolved for this release only") remains. It is consistent if A4 is read as limited to the Release Gate input. Rewording A4 needs a superseding ADR or the user; it is not a finding.

## 2. OWASP notes

- **A01:** who may accept, and who may check (SEC-T720-02, -08).
- **A03:** slug character set. No finding.
- **A04:** carry-over (SEC-T720-01, resolved), deployment precondition (SEC-T720-05), hotfix eligibility (SEC-T720-06), heading (SEC-T720-07).
- **A05:** VS Code wiki. No finding.
- **A08:** release-file check integrity (SEC-T720-04).
- **A09:** acceptance records (SEC-T720-03).
- **A02, A06, A07, A10:** not applicable to knowledge text.

## 3. Findings tracked as LOW debt (owner: orchestrator, who routes each)

| Id | Location | Finding | Fix (reviewer) | Route |
|---|---|---|---|---|
| SEC-T720-02 | `validation-gates/SKILL.md:70` (A1); `security-engineer.md:86` (A12) | The acceptance record does not name the release the user was asked about, and does not tie the remediation plan to the plan the user was shown. Under A12 an agent could move the plan's deadline. | Record the release version and the plan put to the user; a later change of the plan's deadline needs a new acceptance. | Changes ADR-011 row text: needs a superseding ADR or the user |
| SEC-T720-03 | `release-manager.md:183` (A8) | The Conditions template has no slot for the date, grade, release, or the plan's owner and fix that A1 requires. It fails closed. | Extend the template line (exact text in the reviewer's report). | Same as -02 |
| SEC-T720-04 | `release-manager.md:46` (R1) | "What you add below the field list" can be read as open-ended. | Name only Gate Inputs, Justification, Conditions, Blockers and the user's decisions, and add "no other text may be added after the check". | Knowledge edit plus a re-pin of `test_release_self_review_text.py` |
| SEC-T720-05 | `orchestrator.md:262` (R6) | Deployment after a CONDITIONAL_PASS does not repeat that the item 2 risk acceptance must be recorded. | Add "with the explicit risk acceptance `release-manager` § Release Gate Policy item 2 requires recorded in the verdict". | Same as -04 |
| SEC-T720-06 | `release-workflow/SKILL.md:171,232` (R8) | Hotfix eligibility names only CRITICAL and HIGH, so a constraint breach or weakened control graded lower waits for a regular release. Pre-existing; R8 made it explicit. | Admit these whatever their grade. | Knowledge edit |
| SEC-T720-07 | `validation-gates/SKILL.md:70` (heading) | "Security findings never qualify for CONDITIONAL_PASS" contradicts the body, which allows it for medium. It fails closed. Pre-existing. | Add "except one graded medium as stated below". | Knowledge edit |
| SEC-T720-08 | `release-manager.md:46` (R1); `orchestrator.md:218` (R3) | The independent checker is not required to be someone other than the author or editor of the release files. | Add "the checker has not authored or edited the release files at the checked commit". | Knowledge edit plus a re-pin |

## 4. Not verified by the reviewer

The reviewer did not verify:
- the commit shas, since it had no shell;
- the user's verbatim decisions of 2026-11-01. They are recorded in the ADR-011 header and in plan-127;
- the wiki's statement about the `type` key;
- golden fixtures. `scripts/scorecard.py --check` passes after T720 (orchestrator).
