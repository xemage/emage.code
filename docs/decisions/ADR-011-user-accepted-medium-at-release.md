# ADR-011 — user-accepted-medium-at-release

> Filename: `ADR-011-user-accepted-medium-at-release.md` (zero-padded sequential, kebab-case slug).

- **Status**: Accepted. The user decided on 2026-11-01 (AskUserQuestion, option labels verbatim): TD-T713-01, "(a) Time-bound acceptance (Recommended)"; the end date ("what is the longest an acceptance of a MEDIUM may run before it must be renewed?"), "Until the next release"; SEC-T693-04 command part, "O1: both fields (Recommended)". Accepted ADRs are immutable; a change needs a superseding ADR.
  - The user chose option (a) with the end date "Until the next release", not the 90-day limit of the draft. The text below is revised to that choice: an acceptance covers only the release it was given for, it is renewed by the user at the next release that ships the finding, and there is no time-based maximum.
  - Drafted as Proposed in T718. Until it was accepted, no ruling could cite it as authority. Only the user accepts it (ADR-008 P5; plan-127 § User decisions 1). The acceptance is recorded in this header through a normal merge request (`git-workflow.md`).
  - The answer on the command part (O1) was given in the same decision. It is ruled in `docs/artifacts/rulings-batch-d-v1.md` § 1.5 under ADR-007; it is not part of this ADR's rule.
- **Date**: 2026-11-01
- **Decider(s)**: the user (2026-11-01). solution-architect drafted it.
- **Tasks**: T718 (draft and revision); T720 (applies it); T721 (text pins).
- **Requirements**:
  - `docs/tasks/task-T718.md` § 1; `docs/plans/plan-127-batch-d-knowledge-and-rulings.md` (Goal 3, User decisions 1).
  - `docs/artifacts/tracked-debt-register-v4.md` § 3.10, TD-T713-01.
  - `docs/checkpoints/checkpoint-040-release-v9.0.0.md` § 3 (last row) and § 5.
  - ADR-007 and ADR-008 (Accepted); `AGENTS.md`.
- **Extends**: nothing. **Supersedes**: nothing.

## Context

### The rule

`implementation/knowledge/agents/release-manager.md:43` (Release Gate Policy item 2) says:

> "Risk acceptance never covers a security finding (skill `validation-gates` § Verdict Rules): a `SECURITY:CRITICAL` or `SECURITY:HIGH` finding, a breach of an Immutable Security Constraint, or a required security control omitted, removed, disabled or weakened blocks the release (item 1), and a `SECURITY:MEDIUM` finding is fixed before the release ships."

`implementation/knowledge/skills/validation-gates/SKILL.md:70` says the same: "at the Release gate, a security finding graded medium is fixed before the release ships". `implementation/knowledge/commands/prepare-release.md:62` (step 9) repeats it.

The stable instruction asks for less. `implementation/knowledge/instructions/security-guidelines.md:183`: "`MEDIUM` findings must have a remediation plan before merge" (also its Rails, `:23-24`). It says nothing about a release. The skill's stricter release rule is allowed: "No set of criteria, the rules above included, makes another less strict" (`validation-gates/SKILL.md:72`).

### The practice

Two releases shipped a `SECURITY:MEDIUM` finding that was accepted, not fixed. Both times the user decided it, and the release manager recorded the decision as the user's.

| Release | Finding | The user's words (verbatim as recorded) | Where |
|---|---|---|---|
| v8.0.0 | SEC-T660-01 (GitLab tool list is not a credential boundary) | "Accept the risk, plan after the release (Recommended)" (2026-10-15) | `docs/releases/v8.0.0.md:261`, `:275`, `:297` |
| v8.0.0 | SEC-T658-01 (unfixable remainder) | "Accept the unfixable remainder; fix the rest after v8.0.0 (Recommended)" | `docs/releases/v8.0.0.md:262` |
| v9.0.0 | SEC-T702-09 (Brave 2.1.4, seven advisories) | "Ship with it accepted (Recommended)" (2026-11-01), after "Renew + force stdio (Recommended)" (acceptance v3) | `docs/releases/v9.0.0.md:283`, `:287`; `docs/artifacts/brave-audit-acceptance-v3.md` |

In v8.0.0 the release manager first issued FAIL on SEC-T660-01, and the user's decision cleared it (`docs/releases/v8.0.0.md:256`). In v9.0.0 the verdict says: "Release Gate Policy item 2 literally says that a `SECURITY:MEDIUM` finding is fixed before the release ships ... This verdict applies the reading used for v8.0.0" (`docs/releases/v9.0.0.md:283`).

### The problem

The text says "never" and the practice says "when the user decides". Three things follow:

1. Each release re-argues the same exception, and the verdict cites a "reading" rather than a rule.
2. Nothing says what the user's acceptance must record. The two precedents differ: v9.0.0 has an end date (2027-01-30), v8.0.0 has none ("plan after the release"), and SEC-T660-01 is still accepted at v9.0.0 with no end date.
3. Nothing says who may accept. Both verdicts say "the release manager does not grant this acceptance", but no knowledge text says so.

### Why this is the user's decision

No document ranks the user's per-release decision against an agent's policy text. ADR-008 decides conflicts between knowledge documents; this is a conflict between a document and practice, so ADR-008 P5 applies: escalate, do not choose. The change also reaches a command (`prepare-release.md` step 9). Under ADR-007 a command clause is amended only if it contradicts `AGENTS.md`, a stable instruction or itself; none applies, and ADR-008 P2 adds that "the command is never amended on the strength of a skill or agent". An accepted ADR is a recorded decision, and "that decision governs, and documents are amended to it" (ADR-008 § Scope). The user's acceptance of this ADR is therefore what allows the command edit (A10, A11).

## Decision (option (a), with the user's end date)

**At the Release gate, a `SECURITY:MEDIUM` finding is fixed before the release ships, unless the user accepts it for that release.**
- **Only the user** can accept it. No agent grants, extends or infers an acceptance; the release manager records it.
- **The verdict records** all of these: the user's words verbatim with the date; the finding's id and grade; and its remediation plan (owner, fix, deadline).
- **One release only.** An acceptance covers only the release it was given for (the user's end date: "Until the next release"). There is no time-based maximum. At the next release that ships the finding, the finding blocks again until it is fixed or the user accepts it again for that release.
- **Never covered**: a `SECURITY:CRITICAL` or `SECURITY:HIGH` finding, a breach of an Immutable Security Constraint, or a required security control that is omitted, removed, disabled or weakened. These still block (item 1; `validation-gates` § Verdict Rules).
- **Defined once**: in `validation-gates` § Verdict Rules. The other places point to it and do not copy it (ADR-008 P3b remedy).
- **Unchanged**: the production default (fix first); the merge rule of `security-guidelines.md`; the PoC track (`poc-orchestrator` § Security Findings); `AGENTS.md`.

The draft proposed an end date no later than 90 days after the acceptance. The user chose "Until the next release" instead. Separate time-bound acceptances that other mechanisms keep are not changed by this ADR: the per-advisory acceptances of `scripts/audit-mcp-pins.py` (90 days, `docs/releases/v9.0.0.md:186`, F-05) and the Brave pin-audit acceptance `docs/artifacts/brave-audit-acceptance-v3.md` (until 2027-01-30 or the first Brave release above 2.1.4) stay as they are. They decide whether the pin audit passes; this ADR decides whether a release may ship a `SECURITY:MEDIUM`.

## Alternatives considered

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| **(a) Allow a MEDIUM to ship only under the user's explicit, recorded, time-bound acceptance, with a remediation plan** | Matches both precedents. Keeps "fix first" as the default. Consistent with tier 1, which asks only for "a documented remediation plan before merge" (`security-guidelines.md:183`). Says who may accept and what is recorded. The per-release bound forces review at every release | Changes 13 lines in 5 knowledge files, one of them a command. Every carried MEDIUM acceptance (SEC-T660-01, SEC-T665-01, the SEC-T658-01 remainder, SEC-T702-09) needs a new acceptance at the next release that ships it | **Chosen by the user**, with the end date "Until the next release" |
| **(b) Keep item 2 as written; record v8.0.0 and v9.0.0 as user overrides** | No knowledge edit. Every exception stays a visible, separate user decision | Text and practice keep diverging; each verdict cites a "reading". No rule says what an override must record or that only the user may make one. The release manager must FAIL first and ask each time | Not chosen: it leaves TD-T713-01 open in substance |
| **(c) A separate override clause that names who may override and what must be recorded** | Keeps item 2 strict and puts the exception in one visible place | If general ("the user may override a Release Gate Policy rule"), it is wider than the problem and invites other overrides. If limited to MEDIUM, it is option (a) in another place, plus one more item. A new item 6 changes the item count the pins check (`tests/functional/test_release_self_review_text.py:111-113`), and the other places still need the same pointer edits | Not chosen; (a) gives the same control with less text |
| **(d) Strict: no acceptance; a MEDIUM is always fixed or the release does not ship** | Simplest rule. Matches the current text | Would have blocked v8.0.0 and v9.0.0. A finding with no upstream fix (SEC-T702-09: no Brave release above 2.1.4) blocks every release. Creates pressure on the Security Engineer to regrade findings down to LOW | Rejected on the merits |

## Files and lines this decision changes

Line numbers as read on 2026-11-01 in the T718 worktree (no shell). The list covers the files I read; **a repository-wide search was not possible** (no search tool). Before T720, the orchestrator should grep `implementation/knowledge/` for "fixed before the release ships", "never covers a security finding", "never a security finding", "conditions resolved" and "graded CRITICAL, HIGH or MEDIUM", and report any hit outside this table as a new finding.

Exact text for option (a), as the user decided it:

| # | File:line | Replace | With |
|---|---|---|---|
| A1 | `implementation/knowledge/skills/validation-gates/SKILL.md:70` (§ Verdict Rules) | the sentence "The next-release-cycle rule never applies to a security finding: at the Release gate, a security finding graded medium is fixed before the release ships." | "The next-release-cycle rule never applies to a security finding: at the Release gate, a security finding graded medium is fixed before the release ships, unless the user accepts it for that release. Only the user can accept it; no agent grants, extends or infers an acceptance. The acceptance holds only if the release verdict records the user's words verbatim with the date, the finding's id and grade, and its remediation plan (owner, fix, deadline). It covers only the release it was given for: at the next release that ships the finding, the finding blocks again until it is fixed or the user accepts it again for that release. An acceptance never covers a security finding graded critical or high, a breach of an Immutable Security Constraint, or a required security control that is omitted, removed, disabled or weakened." |
| A2 | `validation-gates/SKILL.md:55` (Conditions line) | "except a security finding, which is fixed before the release ships)" | "except a security finding, which is fixed before the release ships or, if graded medium, accepted by the user for that release under § Verdict Rules)" |
| A3 | `validation-gates/SKILL.md:67` (CONDITIONAL_PASS row) | "Neither deferral applies to a security finding (below)." | "Neither deferral applies to a security finding (below), except the user's acceptance of one graded medium for that release at the Release gate (§ Verdict Rules)." |
| A4 | `validation-gates/SKILL.md:114` (Release Gate inputs) | "- All prior gate verdicts (must be PASS or CONDITIONAL_PASS with conditions resolved)" | "- All prior gate verdicts (must be PASS or CONDITIONAL_PASS with conditions resolved; a security finding graded medium that the user accepted for this release under § Verdict Rules counts as resolved for this release only)" |
| A5 | `validation-gates/SKILL.md:140` (Handle a CONDITIONAL_PASS, step 2) | "(at the Release gate, before the release ships)" | "(at the Release gate, before the release ships, unless the user accepts it for that release under § Verdict Rules)" |
| A6 | `validation-gates/SKILL.md:151` (Gate Pipeline) | "The Release Gate verifies that all prior conditions have been resolved." | "The Release Gate verifies that all prior conditions have been resolved, or, for a security finding graded medium, accepted by the user for this release under § Verdict Rules." |
| A7 | `implementation/knowledge/agents/release-manager.md:43` (Release Gate Policy item 2) | "and a `SECURITY:MEDIUM` finding is fixed before the release ships." | "and a `SECURITY:MEDIUM` finding is fixed before the release ships, unless the user accepts it for this release as that section allows. You record the user's acceptance in the verdict; you never grant, extend or infer one, and an acceptance given for an earlier release does not cover this one." |
| A8 | `release-manager.md:181` (verdict block, Conditions) | "- [Gate/Finding — never a security finding]: risk_accepted_by=@[who], mitigation=[what], deadline=[next release cycle or earlier]" | "- [Gate/Finding — never a security finding, except a `SECURITY:MEDIUM` the user accepted for this release (item 2)]: risk_accepted_by=@[who; for a security finding, the user, with the words verbatim], mitigation=[what], deadline=[next release cycle or earlier; for a security finding, the remediation plan's deadline, and a new acceptance by the user at the next release that ships it]" |
| A9 | `release-manager.md:222` (Constraints) | "- DO NOT release when unresolved critical QA findings, or any unresolved security finding graded CRITICAL, HIGH or MEDIUM, remain" | "- DO NOT release when unresolved critical QA findings, or any unresolved security finding graded CRITICAL or HIGH, or graded MEDIUM and not accepted by the user for this release under item 2, remain" |
| A10 | `implementation/knowledge/commands/prepare-release.md:62` (step 9) | "a `SECURITY:MEDIUM` finding is fixed before the release ships;" | "a `SECURITY:MEDIUM` finding is fixed before the release ships, unless the user accepts it for this release as skill `validation-gates` § Verdict Rules allows, and the verdict records that acceptance;" |
| A11 | `prepare-release.md:70` (Rails, Failure mode) | "`CONDITIONAL_PASS` with listed conditions only when no security finding is among them" | "`CONDITIONAL_PASS` with listed conditions only when no security finding is among them other than a `SECURITY:MEDIUM` finding the user accepted for this release (step 9)" |
| A12 | `implementation/knowledge/agents/security-engineer.md:86` (§ Findings Classification, SLA paragraph) | "and its fix is due by its SLA or under that skill's track rule, whichever is earlier;" | "and its fix is due by its SLA or under that skill's track rule, whichever is earlier, except that a MEDIUM finding the user accepted for a release under that skill's § Verdict Rules is due by its remediation plan's deadline and needs a new acceptance at the next release that ships it;" |
| A13 | `implementation/knowledge/skills/release-workflow/SKILL.md:113` (Release Gate Checklist) | "- [ ] Security gate: PASS or CONDITIONAL_PASS (all conditions resolved)" | "- [ ] Security gate: PASS or CONDITIONAL_PASS (all conditions resolved, or a medium security finding accepted by the user for this release under `validation-gates` § Verdict Rules)" |

Also changed, outside `implementation/knowledge/` (T720):
- `docs/wiki/severity-and-grade-scales.md:34` (note S5): append "At the Release gate a `SECURITY:MEDIUM` finding is fixed before the release ships unless the user accepts it for that release under `validation-gates` § Verdict Rules (ADR-011)."
- `tests/functional/test_release_self_review_text.py`: no edit is needed for option (a).

Read and **not** changed by this decision:
- `security-guidelines.md:23-24`, `:183` (tier 1): (a) is consistent with them. ADR-008 P1 never amends a tier-1 text to match a lower one.
- `AGENTS.md` § Validation Gates: "`CONDITIONAL_PASS` proceeds with tracked conditions added to the task list" holds.
- `orchestrator.md:143-146`, `:220-223`: no MEDIUM rule there.
- `security-engineer.md:157`: `pass` "only when ... no medium finding remains" stays true; an accepted MEDIUM gives at best CONDITIONAL_PASS.
- `docs/releases/_template.md`: holds no MEDIUM rule. (It changes under the separate O1 ruling, not under this ADR.)
- PoC track (`poc-orchestrator` § Security Findings, `poc-guidelines.md` Scorecard Rule 5): out of scope; not changed.

## Consequences

- **Positive**
  - The text matches the two recorded decisions, so verdicts cite a rule, not a "reading".
  - It says who may accept (the user only) and what is recorded. The release manager's role ("records, never grants") becomes text, not only verdict practice.
  - Every accepted MEDIUM comes back to the user at every release that ships it.
- **Negative**
  - The release rule gets longer, in one place (A1); the other twelve edits are pointers.
  - It makes an unfixed MEDIUM at release a normal path. The default stays "fix first", and each case still needs the user's own words.
  - One more question for the user at each release, per carried MEDIUM.
- **Risks introduced**
  - *Routine acceptance*: the user is asked so often that acceptance becomes a habit. Mitigation: each acceptance names the finding and its plan, and the plan's owner and fix are recorded.
  - *Agent-inferred acceptance*: an agent reads an old acceptance as covering a new release. Mitigation: "for that release", "no agent ... infers an acceptance" and "an acceptance given for an earlier release does not cover this one" (A1, A7).
  - *Golden cases* **(unverified)**: golden cases of `/prepare-release` may quote step 9. I did not open `tests/golden/`. If a fixture must change, that needs a protected-path grant.
- **Carried acceptances.** SEC-T660-01, SEC-T665-01, the SEC-T658-01 remainder and SEC-T702-09 (register v4 § 6) were accepted for v8.0.0 or v9.0.0. Under this decision each covers only that release. At the next release that ships any of them, the user must accept it again for that release, or it blocks.
  - SEC-T702-09 needs this too. Its separate Brave pin-audit acceptance (`docs/artifacts/brave-audit-acceptance-v3.md`, until 2027-01-30 or the first Brave release above 2.1.4) is a different mechanism and is not changed: it decides whether `scripts/audit-mcp-pins.py` passes, not whether a release may ship the MEDIUM. A release needs both: an unexpired pin-audit acceptance, and the user's acceptance for that release.
- **Follow-ups**
  - T720 applies A1 to A13 and the wiki line. T721 pins A1, A7 and A10 if the orchestrator wants them pinned.
  - Register v5 records TD-T713-01 as decided by this ADR, and records in § Accepted risks that the four carried MEDIUM acceptances need renewal at the next release.

## Validation

The decision is correct if all of these hold:

1. **No silent acceptance.** Every release verdict that ships an unfixed `SECURITY:MEDIUM` quotes the user's words given for that release, with the date and the plan. A reviewer can check this from the release document alone.
2. **No widening.** No release ships a `SECURITY:CRITICAL` or `SECURITY:HIGH` finding, a constraint breach or a weakened required control under this rule.
3. **No carry-over.** No release verdict relies on an acceptance given for an earlier release. `tracked-debt-register` § Accepted risks shows, per carried MEDIUM, the release each acceptance was given for.
4. **One definition.** After T720, the full rule appears only in `validation-gates` § Verdict Rules; the other places point to it (grep for "accepts it again for that release" finds one knowledge file).
5. **Tier 1 untouched.** No diff under this ADR edits `security-guidelines.md` or `AGENTS.md`.
