# Artifact: security-review-t734-t736-batch-h-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer, read-only, with no shell. The orchestrator recorded this artifact from the reviewer's two reports.
- **Gate**: security. **Date**: 2026-11-04.
- **Target**: T734, T735 and T736 (LOW batch H, plan-133) on `agent/devops-engineer/T736`. First review at `b48edc23`; re-check at `e95f8932`, from exported diffs.
- **Based on**:
  - `docs/plans/plan-133-batch-h-release-gate-text.md`
  - `docs/decisions/ADR-011-user-accepted-medium-at-release.md`, `docs/decisions/ADR-012-medium-acceptance-record.md`
  - `docs/artifacts/security-review-t718-t720-batch-d-v1.md` § 3
  - `tests/functional/test_release_self_review_text.py`
- **Search tool**: `grep_content` failed on worktree paths, as it did in batch G's review, so the reviewer's greps reflect `develop` and were combined with the diffs. The orchestrator recorded this as a limit of the tool, not a refusal.
- **Orchestrator's checks**: the two handoff schema files are byte-identical (`cmp`), which settles the reviewer's open point on P13. The suite and gates are recorded in plan-133 § Outcome.

## Verdict: PASS (the first review was CONDITIONAL_PASS)

- 0 CRITICAL, 0 HIGH, 0 MEDIUM remaining.
- No breach of an Immutable Security Constraint.
- No required control removed or weakened.
- The reviewer's PASS covers the text and its reading of the pins. It ran no test.

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 1 | 1 | 0 |
| LOW | 10 | 5 | 5 (tracked, section 4) |

## 1. Rulings on the changes

- **ADR-012 against what the user approved.** The first draft stated two rules as the user's that the question had not put to the user: moving a deadline earlier needs no new acceptance, and a change of owner needs none. The first was a fair reading. The second was not: treating silence as "needs none" is an agent inferring how far an acceptance reaches. Resolved by the user's own answers (SEC-T735-01).
- **B1 to B3.** They close SEC-T720-02 and -03. Nothing enforces them: this stays a recorded duty (SEC-T693-07).
- **Changelog Preview in the closed list.** Safe. The agent's verdict block requires that section, and the list stays closed.
- **Hotfix eligibility (SEC-T720-06).** No gate that should run is skipped for the new class. A fix with design impact fails closed into the regular path.
- **SEC-T720-05, -07 and -08.** Closed. `tech-lead.md:100` does not contradict -07. After SEC-T735-03, the orchestrator or top-level session will often be ineligible as checker, because any edit to the release files for this release disqualifies it. `@tech-lead` is read-only during review, so it stays eligible, and the set of checkers is not empty.
- **P10.** Consistent, and it fails closed. Someone reading only `/new-project` could read `APPROVED_WITH_CHANGES` as approval.
- **TD-T725-01.** Closed. Two remaining uses are conditional and assume nothing. Whether targets receive `scripts/verify-release-docs.py` and `_template.md` is **(unverified)**.
- **Pins.** The mutations should fail when a clause is removed (read, not run by the reviewer). `RULED_R1` and `RULED_R3` can hide a change only inside the fragments they reverse, and those are now anchored in plan-133. The plan is not immutable, so this anchors provenance, not immutability.
- **The golden claims.** P14, P15 and T565 are confirmed. P13 is confirmed by the orchestrator's `cmp`. Separately, `consolidate-memory-recommendation-table-grounded/brief.md:70-72` discloses that its fixture does not meet the T549 clause; that is not the parked remark.

## 2. Resolved findings

| Id | Grade | Finding | Fix |
|---|---|---|---|
| SEC-T735-01 | MEDIUM | ADR-012 recorded agent-drafted sentences as the user's decision | The user: "Record it, no new question (Recommended)". ADR-012 records the answer and how it arose; B1 and B3 carry the owner rule |
| SEC-T735-02 | LOW | A deadline that passes without moving was not covered | The user: "Add the sentence (Recommended)". Residual: SEC-T735-08 |
| SEC-T735-03 | LOW | The independence clause had no effect, an ambiguous scope, and no route when the checker edits | The row counts as missing; scope "for this release"; another eligible checker |
| SEC-T735-04 | LOW | Hotfix eligibility: no check that the issue is in the released version, no one to confirm it, "no design impact" stated as fact | Named in `release-workflow/SKILL.md:171, 202, 205` |
| SEC-T736-02 | LOW | The Changelog Preview wording had no recorded source | Recorded in plan-133 § Changes after the first security review, and anchored there |

SEC-T735-05 (the Conditions slots were missing from the published template) is also resolved: `docs/releases/_template.md` points to the format. Residual: SEC-T735-09. The Resolved count of LOW findings is SEC-T735-02, -03, -04, -05 and SEC-T736-02.

## 3. OWASP coverage

| Category | Findings (open) |
|---|---|
| A01 Broken Access Control | SEC-T735-06, -07 |
| A04 Insecure Design | SEC-T735-08 |
| A08 Data Integrity | SEC-T736-01, SEC-T735-09 |
| A02, A03, A05, A06, A07, A09, A10 | 0 (no code or dependency change) |

## 4. Findings tracked as LOW debt (owner: orchestrator, who routes each)

| Id | Location | Finding | Fix (reviewer) |
|---|---|---|---|
| SEC-T735-06 | `validation-gates/SKILL.md:70`; `release-manager.md:46, 183` | "As shown to the user" has no source. An agent writes the plan into Conditions, and nothing requires comparing it with what was shown. | `mitigation` cites where the plan was shown, and the top-level session's verification compares the two. |
| SEC-T735-07 | `validation-gates/SKILL.md:70` | B1 puts the owner sentence before "It covers only the release it was given for", so "It" no longer points clearly to the acceptance. "Given for" keeps the meaning. | "An acceptance covers". This changes ADR-011's A1 text, so confirm the route first. |
| SEC-T735-08 | `validation-gates/SKILL.md:70`; `tracked-debt-register-v6.md:203` | If a carried plan's deadline has already passed when the user is asked, the text does not say whether the new acceptance cures it. The register's checklist omits the release version and "as shown to the user". | **Before the next release:** the next register's checklist says to name the release, record the plan as shown, and show a deadline still ahead when asking. |
| SEC-T735-09 | `docs/releases/_template.md:90`; `release-manager.md:46` | Deleting the pointer sentence after the check is a change that makes the check stale. It fails closed. | **Before the next release:** remove the sentence before the check, or leave it. Say so in the checklist. |
| SEC-T736-01 (rest) | `tests/functional/test_release_self_review_text.py` | Still no pin for B2 (`security-engineer.md:86`), SEC-T720-05 (`orchestrator.md:262`), `release-workflow:233`, or TD-T725-01. | Add pins and mutations. |

## 5. Not verified by the reviewer

- The test suite, the mutation proof, `scorecard.py --check`, the mirrors, the registry and the root drift baseline. The orchestrator ran them before the merge.
- The question shown to the user, beyond the orchestrator's message and ADR-012.
- Whether `verify-release-docs.py` tolerates the leftover pointer sentence (T736 reports that it does).
- Each carried finding's actual plan deadline.
