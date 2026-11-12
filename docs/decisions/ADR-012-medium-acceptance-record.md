# ADR-012 — medium-acceptance-record

> Filename: `ADR-012-medium-acceptance-record.md` (zero-padded sequential, kebab-case slug).

- **Status**: Accepted. The user decided on 2026-11-04 (AskUserQuestion, option label verbatim): "Add it as ADR-012 (Recommended)". The question put this wording to the user: "The verdict also records the release version the user was asked about and the remediation plan as shown to the user. Moving the deadline later or changing the fix needs the user's new acceptance." It also said that the verdict's Conditions template gets slots for date, grade, release, plan owner and fix.
  - The first review found that the first draft stated two more rules as the user's without having asked (SEC-T735-01), and that a deadline which simply passes was not covered (SEC-T735-02). The user then decided, the same day and before this ADR merged (AskUserQuestion, option labels verbatim): on a change of the plan's owner, "Record it, no new question (Recommended)", whose description also said that moving a deadline earlier or finishing sooner needs no new acceptance; on the sentence "A deadline that passes before the release ships counts as moved later", "Add the sentence (Recommended)".
  - Accepted ADRs are immutable; a change needs a superseding ADR.
  - **Superseded in part by `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md`** (rows B1 and B3, as far as ADR-015 says). The rest stands.
- **Date**: 2026-11-04
- **Decider(s)**: the user (2026-11-04). The orchestrator drafted it.
- **Tasks**: T734 (this record); T735 (applies it); T736 (text pins).
- **Requirements**:
  - `docs/artifacts/security-review-t718-t720-batch-d-v1.md` § 3, SEC-T720-02 and SEC-T720-03.
  - `docs/artifacts/tracked-debt-register-v6.md` § 5, batch H.
  - `docs/plans/plan-133-batch-h-release-gate-text.md`.
- **Extends**: ADR-011. **Supersedes**: ADR-011 in part: rows A1, A8 and A12 of § Files and lines, and the words "**The verdict records** all of these" of § Decision. The rest of ADR-011 stands.

## Context

ADR-011 lets a `SECURITY:MEDIUM` ship only under the user's acceptance for that one release, and the verdict records the user's words with the date, the finding's id and grade, and its remediation plan. The batch D review found two gaps:

- **SEC-T720-02.** The record does not name the release the user was asked about, and it does not tie the remediation plan to the plan the user saw. Under row A12, an agent could move the plan's deadline after the acceptance.
- **SEC-T720-03.** The verdict's Conditions template has no slot for the date, the grade, the release, or the plan's owner and fix. A verdict that leaves them out fails closed, because the rule still requires them, but the template invites the omission.

The next release has to re-accept four carried findings (SEC-T660-01, SEC-T665-01, the SEC-T658-01 remainder, SEC-T702-09), so these records will be written soon.

## Decision

**The verdict also records the release version the user was asked about and the remediation plan as shown to the user. Moving the deadline later or changing the fix needs the user's new acceptance. A deadline that passes before the release ships counts as moved later.**

- Moving the deadline earlier or finishing the fix sooner needs no new acceptance.
- A change of the plan's owner needs no new acceptance, but the verdict records both the owner shown to the user and the current owner, so the release document alone shows it.
- Everything else in ADR-011 is unchanged: only the user accepts, one release only, and critical or high findings, constraint breaches and weakened controls are never covered.
- The rule stays defined once, in `validation-gates` § Verdict Rules. The other places point to it.

## Alternatives considered

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| **Add the record as a new ADR** | Closes both gaps before four acceptances are written | One more field in each record, and one more question if a plan changes | **Chosen by the user** |
| **Keep both tracked** | No change | The next release's acceptances use a record that does not bind the plan the user saw | Not chosen |

## Files and lines this decision changes

Line numbers as read on 2026-11-04.

| # | File:line | Replace | With |
|---|---|---|---|
| B1 | `implementation/knowledge/skills/validation-gates/SKILL.md:70` (replaces A1 in part) | "The acceptance holds only if the release verdict records the user's words verbatim with the date, the finding's id and grade, and its remediation plan (owner, fix, deadline)." | "The acceptance holds only if the release verdict records the user's words verbatim with the date, the finding's id and grade, the release version the user was asked about, and its remediation plan (owner, fix, deadline) as shown to the user. Moving the deadline later or changing the fix needs the user's new acceptance, and a deadline that passes before the release ships counts as moved later. A change of the plan's owner needs no new acceptance, but the verdict records both the owner shown to the user and the current owner." |
| B2 | `implementation/knowledge/agents/security-engineer.md:86` (replaces A12 in part) | "is due by its remediation plan's deadline and needs a new acceptance at the next release that ships it;" | "is due by its remediation plan's deadline and needs a new acceptance at the next release that ships it, or sooner if the deadline moves later or passes before the release ships, or the fix changes;" |
| B3 | `implementation/knowledge/agents/release-manager.md:183` (replaces A8) | the whole Conditions line | "- [Gate/Finding — never a security finding, except a `SECURITY:MEDIUM` the user accepted for this release (item 2)]: risk_accepted_by=@[who; for a security finding, the user, with the words verbatim and the date], grade=[for a security finding, its grade], release=[for a security finding, the release version the user was asked about], mitigation=[what; for a security finding, the remediation plan as shown to the user, with its owner and fix, and the current owner if it has changed], deadline=[next release cycle or earlier; for a security finding, the remediation plan's deadline, and a new acceptance by the user at the next release that ships it, or sooner if the deadline moves later or passes before the release ships, or the fix changes]" |

## Consequences

- **Positive**: an acceptance now shows from the release document alone what the user was asked and which plan they saw. An agent can no longer move a deadline later, or let it lapse, under an old acceptance.
- **Negative**: one more question for the user if a plan's fix changes or its deadline slips or lapses between acceptance and release.
- **Risk**: the text still cannot stop an agent from editing a plan without asking. The Release Gate's check of the record, and the top-level session's verification, remain the controls.

## Validation

1. Every release verdict that ships an unfixed `SECURITY:MEDIUM` names the release version and the plan as shown to the user.
2. `test_release_self_review_text.py` pins B1 and B3, and each pin fails if its clause is removed.
3. No diff under this ADR edits `security-guidelines.md` or `AGENTS.md`.
