# ADR-015 — medium-plan-without-fix-and-passed-deadline

> Filename: `ADR-015-medium-plan-without-fix-and-passed-deadline.md` (zero-padded sequential, kebab-case slug).

- **Status**: Accepted. The user decided on 2026-11-12 (AskUserQuestion; question, answer and option description verbatim, as the orchestrator relayed them to the drafter in T800).
  - The question as shown:
    > ADR-015 is drafted as Proposed. It records your two rulings: (1) a MEDIUM's plan may say "fix: none possible in the harness" if it names who could close it outside the harness, says so plainly, and sets a review date; (2) a new acceptance with a new plan and a deadline still ahead cures a passed deadline, and the release document says the old deadline passed. Your words left seven details open (O1 to O7); the architect recommends an answer for each. Accept ADR-015?
  - The user's answer:
    > Accept with all recommendations
  - The option's description as shown:
    > O1: the review date is the plan's deadline. O2: no time limit beyond being still ahead at shipping. O3: on the review date the owner records the outcome in the register. O4: the Security Engineer's review confirms no harness fix exists. O5: the verdict's Conditions line names the old deadline and its release. O6: applies to any passed deadline. O7: the outside closer may be you.
  - The other options were "Accept the two rules only" and "I want to read it first".
  - Accepted ADRs are immutable; a change needs a superseding ADR.
  - **Superseded in part by `docs/decisions/ADR-016-security-engineer-confirmation-as-validity-condition.md`** (Rule 1's opening sentence and its consequence sentence, O4 in § Decision and in § Points that were open, and the first sentence of row C1, as far as ADR-016 says). The rest stands.
  - Drafted as Proposed in T800. Until it was accepted, no ruling, verdict or knowledge edit could cite it as authority (ADR-008 P5). Only the user accepts it. The acceptance is recorded in this header through a normal merge request (`git-workflow.md`).
  - The user's words are the quoted questions, answers and option descriptions, here and in § The user's answers. All other wording of this record is the drafter's.
- **Date**: 2026-11-12
- **Decider(s)**: the user (2026-11-12), and nobody else. solution-architect drafted it.
- **Tasks**: T800 (draft and revision). Follow-up tasks to apply it are not yet created (§ Consequences, Follow-ups).
- **Requirements**:
  - `docs/tasks/task-T800.md` § 2; [plan-155](../plans/plan-155-v11-release-decisions.md) § User decisions 3 and 4, and "The orchestrator's reading".
  - [ADR-011](ADR-011-user-accepted-medium-at-release.md) and [ADR-012](ADR-012-medium-acceptance-record.md).
  - Findings SEC-T762-04 and TL-T761-10 (`docs/artifacts/tracked-debt-register-v12.md`; `docs/artifacts/security-review-t756-accepted-mediums-v1.md`). **(unverified)**: I did not read either artifact (no search tool, token budget); what this record says about how the questions arose comes from the plan and the task brief only.
- **Extends**: ADR-011 and ADR-012. **Supersedes**: ADR-012 in part (rows B1 and B3 of its § Files and lines, as far as § Sentences this record supersedes or extends says). The rest of ADR-011 and ADR-012 stands. Neither file is edited in T800; the header note on ADR-012 is a follow-up (§ Consequences).

## Context

ADR-011 lets a release ship a `SECURITY:MEDIUM` finding only if the user accepts it for that one release, and the verdict records its remediation plan (owner, fix, deadline). ADR-012 added that the plan is recorded as shown to the user, and that a deadline which moves later or passes before the release ships needs the user's new acceptance.

Two points were not ruled (SEC-T762-04, with TL-T761-10):

1. **A plan with no fix.** Both ADRs name "fix" as a part of the plan. Neither says whether the fix may be "none possible in the harness". The case is real: for SEC-T660-01 and SEC-T665-01 the question put to the user on 2026-11-12 said "No harness fix exists; closure needs an isolated user, container or VM" and showed the plan "fix: none possible in the harness" (plan-155 § User decisions 1).
2. **A deadline that has already passed.** ADR-012 says such a deadline "counts as moved later", and that moving a deadline later "needs the user's new acceptance". It does not say in so many words that the new acceptance is enough, or what the release document must then show. The question put to the user names the case: "as SEC-T660-01's did before v10.0.0".

Both option descriptions name "An ADR-011 amendment". Accepted ADRs are immutable (ADR-011 header, ADR-012 header), so the amendment is this new record. That step is the orchestrator's reading, not the user's words (plan-155, "The orchestrator's reading").

## The user's answers (2026-11-12, AskUserQuestion)

Quoted from plan-155 § User decisions 3 and 4. These quotes, and the acceptance quoted in the header, are the only source for what the user said.

**Question 1 (SEC-T762-04, question 1; also TL-T761-10).** The question as shown:

> ADR-011 requires every accepted MEDIUM to have a plan with owner, fix and deadline. May a plan's fix be "none possible in the harness", as for the GitLab token ids?

The user's answer:

> Yes, with conditions (Recommended)

The option's description:

> Allowed only when the plan names who could close it outside the harness, states plainly that no harness fix exists, and sets a review date. An ADR-011 amendment records this.

**Question 2 (SEC-T762-04, question 2).** The question as shown:

> when an accepted MEDIUM's plan deadline has already passed (as SEC-T660-01's did before v10.0.0), does a new acceptance by you, with a new plan and a deadline still ahead, cure the passed deadline?

The user's answer:

> Yes, a new acceptance cures it (Recommended)

The option's description:

> Your new, dated acceptance with a new plan replaces the old one; the release document must say that the old deadline passed. An ADR-011 amendment records this.

## Decision

**Rule 1. A remediation plan's fix may be "none possible in the harness", but only when the plan does all three of these:**

1. it names who could close the finding outside the harness;
2. it states plainly that no harness fix exists;
3. it sets a review date.

A plan that lacks any one of the three is not a valid plan under ADR-011, and the acceptance does not hold.

Ruled with the acceptance (the user accepted "all recommendations"; the short form the user was shown for each point is quoted in the header, and the fuller text here is the drafter's recommended form from § Points that were open):

- **The review date is the plan's `deadline` (O1).** It takes the `deadline` slot, as in the plan shown for SEC-T660-01 and SEC-T665-01 ("deadline: review at token renewal on 2027-01-28, and a new acceptance at the release after v11.0.0", plan-155 § User decisions 1). ADR-012 therefore applies to it unchanged: moving it later, or letting it pass before the release ships, needs the user's new acceptance.
- **No time limit (O2).** The review date need only be still ahead when the release ships. ADR-011's "There is no time-based maximum" holds, and the acceptance ends at the next release in any case.
- **On the review date (O3)** the plan's owner records the outcome in the tracked-debt register: whether a harness fix now exists, and whether the named outside closer is still right. If a fix now exists, the fix has changed, and ADR-012 requires the user's new acceptance.
- **Confirmation (O4).** The Security Engineer's review of the finding confirms that no harness fix exists, and the question to the user cites that review. The user decides.
- **The outside closer may be the user (O7)**, as in the plan shown for SEC-T660-01 and SEC-T665-01 ("owner you (isolation)").

**Rule 2. When an accepted MEDIUM's plan deadline has already passed, the user's new, dated acceptance, with a new plan and a deadline still ahead, cures the passed deadline: it replaces the old acceptance and plan. The release document must say that the old deadline passed.**

Ruled with the acceptance, as above:

- **Where and what (O5).** The statement stands in the verdict's Conditions line for that finding, and names the old deadline's date and the release the old acceptance was given for.
- **Any passed deadline (O6).** Rule 2 applies wherever the deadline passed: after an earlier release (the case in the question) or between the acceptance and the shipping of the same release (ADR-012's case). Each needs the new acceptance, the new plan and the statement.

Without that new acceptance the finding blocks, as before (ADR-011 § Decision, ADR-012 § Decision).

**What does not change.**

- An acceptance covers one release only. Rule 2's new acceptance is given for one release, like any other, and Rule 1's review date does not stretch an acceptance past the release it was given for.
- Only the user gives an acceptance. No agent grants, extends or infers one, and no agent carries one over to another release; the release manager records it.
- A `SECURITY:CRITICAL` or `SECURITY:HIGH` finding, a breach of an Immutable Security Constraint, and a required security control that is omitted, removed, disabled or weakened are never covered.
- The production default stays "fix first". Rule 1 does not let an agent call a finding unfixable to avoid a fix: the plan as shown to the user must carry the three statements, and the user accepts it or not.
- ADR-012's record rules stay: the verdict records the release version the user was asked about and the plan as shown to the user; a later deadline or a changed fix needs a new acceptance; an owner change is recorded without a new question.
- The rule stays defined once, in `validation-gates` § Verdict Rules. `security-guidelines.md`, `AGENTS.md` and the PoC track are not touched.

## Sentences this record supersedes or extends

Line numbers as read on 2026-11-12 in the T800 worktree.

| # | File:line | Sentence or row, quoted | Effect |
|---|---|---|---|
| S1 | `docs/decisions/ADR-011-user-accepted-medium-at-release.md:60` | "- **The verdict records** all of these: the user's words verbatim with the date; the finding's id and grade; and its remediation plan (owner, fix, deadline)." | **Extended** (already superseded in part by ADR-012). "fix" may be "none possible in the harness" under Rule 1's three conditions. |
| S2 | `docs/decisions/ADR-011-user-accepted-medium-at-release.md:85` (row A1, "With" column) | "The acceptance holds only if the release verdict records the user's words verbatim with the date, the finding's id and grade, and its remediation plan (owner, fix, deadline)." | **Extended**, same as S1. Row A1 was already replaced in part by ADR-012 row B1; see S5. |
| S3 | `docs/decisions/ADR-011-user-accepted-medium-at-release.md:61` | "- **One release only.** An acceptance covers only the release it was given for (the user's end date: "Until the next release"). There is no time-based maximum. At the next release that ships the finding, the finding blocks again until it is fixed or the user accepts it again for that release." | **Not changed.** Quoted because Rule 2 depends on it: the "new acceptance" of Rule 2 is the acceptance "again for that release" of this sentence. |
| S4 | `docs/decisions/ADR-012-medium-acceptance-record.md:28` | "**The verdict also records the release version the user was asked about and the remediation plan as shown to the user. Moving the deadline later or changing the fix needs the user's new acceptance. A deadline that passes before the release ships counts as moved later.**" | **Extended** by Rule 2: the new acceptance, with a new plan and a deadline still ahead, is sufficient, and the release document must say that the old deadline passed. Nothing in it is withdrawn. |
| S5 | `docs/decisions/ADR-012-medium-acceptance-record.md:48` (row B1, "With" column) | "The acceptance holds only if the release verdict records the user's words verbatim with the date, the finding's id and grade, the release version the user was asked about, and its remediation plan (owner, fix, deadline) as shown to the user. Moving the deadline later or changing the fix needs the user's new acceptance, and a deadline that passes before the release ships counts as moved later. A change of the plan's owner needs no new acceptance, but the verdict records both the owner shown to the user and the current owner." | **Superseded in part**: the text stays and two sentences are added after it (row C1). |
| S6 | `docs/decisions/ADR-012-medium-acceptance-record.md:50` (row B3, "With" column) | "- [Gate/Finding — never a security finding, except a `SECURITY:MEDIUM` the user accepted for this release (item 2)]: risk_accepted_by=@[who; for a security finding, the user, with the words verbatim and the date], grade=[for a security finding, its grade], release=[for a security finding, the release version the user was asked about], mitigation=[what; for a security finding, the remediation plan as shown to the user, with its owner and fix, and the current owner if it has changed], deadline=[next release cycle or earlier; for a security finding, the remediation plan's deadline, and a new acceptance by the user at the next release that ships it, or sooner if the deadline moves later or passes before the release ships, or the fix changes]" | **Superseded in part**: the `mitigation` and `deadline` slots gain the Rule 1 and Rule 2 items (row C2). |
| S7 | `docs/decisions/ADR-012-medium-acceptance-record.md:49` (row B2, "With" column) | "is due by its remediation plan's deadline and needs a new acceptance at the next release that ships it, or sooner if the deadline moves later or passes before the release ships, or the fix changes;" | **Extended, wording not changed.** For a plan whose fix is "none possible in the harness", "its remediation plan's deadline" is the review date (O1, ruled). The sentence needs no edit (row C3). |

Not superseded: ADR-011 rows A2 to A7, A9 to A11 and A13, and ADR-012's rules on an earlier deadline and on an owner change (`ADR-012-medium-acceptance-record.md:30-31`).

## Files and lines this decision would change

None of these edits is made in T800; a follow-up task makes them. Line numbers as read on 2026-11-12 in the T800 worktree. I have no search tool, so the list covers only the files I read; before the follow-up task, the orchestrator should search `implementation/knowledge/`, `docs/wiki/` and `tests/functional/` for "remediation plan (owner, fix, deadline)", "passes before the release ships" and "counts as moved later", and report any hit outside this table as a new finding.

The texts below are the drafter's wording of the two rules and of O1 to O7 as ruled. The user accepted the rules and the recommendations, not these sentences word for word; the follow-up task may adjust the wording but not the rule.

| # | File:line | Change | Text |
|---|---|---|---|
| C1 | `implementation/knowledge/skills/validation-gates/SKILL.md:70` (§ Verdict Rules) | After the sentence "A change of the plan's owner needs no new acceptance, but the verdict records both the owner shown to the user and the current owner." add | "The plan's fix may be "none possible in the harness" only when the plan names who could close the finding outside the harness (it may be the user), states plainly that no harness fix exists, and sets a review date; the Security Engineer's review of the finding confirms that no harness fix exists, and the question to the user cites it. The review date is then the plan's deadline, with no limit other than being still ahead when the release ships, and on it the plan's owner records the outcome in the tracked-debt register. When the deadline of an accepted finding's plan has passed, after an earlier release or before this one ships, the user's new, dated acceptance with a new plan and a deadline still ahead replaces the old one, and the verdict's Conditions line says that the old deadline passed and names its date and the release the old acceptance was given for." |
| C2 | `implementation/knowledge/agents/release-manager.md:183` (verdict block, Conditions) | In the `mitigation=[...]` slot, after "and the current owner if it has changed" add; in the `deadline=[...]` slot, after "or the fix changes" add | mitigation: "; if the fix is "none possible in the harness", who could close it outside the harness, the plain statement that no harness fix exists with the Security Engineer review that confirms it, and the review date, which is the plan's deadline". deadline: "; if an earlier plan's deadline for this finding has passed, the statement that it passed, its date, and the release the old acceptance was given for" |
| C3 | `implementation/knowledge/agents/security-engineer.md:86` (SLA paragraph) | None. With O1 ruled, the review date is the plan's deadline: the sentence points to the skill's § Verdict Rules, and "its remediation plan's deadline" reads as the review date | — |
| C4 | `implementation/knowledge/agents/release-manager.md:43` (Release Gate Policy item 2) | None proposed. The item points to "that section" (the skill's § Verdict Rules) and does not copy the plan rule | — |

Also to check in the follow-up, none of them read by me **(unverified)**:

- `tests/functional/test_release_self_review_text.py`: ADR-012 § Validation 2 says it pins B1 and B3. C1 adds text after B1's sentences and C2 inserts text inside B3's line, so the B3 pin is likely to need an update, and new pins for C1 and C2 are advisable.
- `implementation/knowledge/commands/prepare-release.md:62` and `:70`, `implementation/knowledge/skills/release-workflow/SKILL.md:113`, `docs/wiki/severity-and-grade-scales.md:34`: ADR-011 lists them as pointers to § Verdict Rules (rows A10, A11, A13 and the wiki line). If they are still pointers, they need no edit.
- `docs/releases/_template.md`: whether its verdict block copies the Conditions line of `release-manager.md:183`; if it does, it needs the C2 additions (O5).
- Golden cases of `/prepare-release` under `tests/golden/`: not opened. If a fixture quotes the changed text, the change needs a protected-path grant.
- The generated mirrors and the registry: C1 and C2 are source edits, so `sync.mjs` and `generate-registry.py` must run, and root drift is declared until a root refresh that the user approves.

## Alternatives considered

The options the user was not shown in plan-155 are the drafter's reconstruction; plan-155 quotes only the chosen options.

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| **Rule 1: allow "none possible in the harness" under three conditions** | Matches the real case (SEC-T660-01, SEC-T665-01). The plan says truthfully that no fix exists rather than naming a fix nobody will make. The review date keeps the finding visible | An unfixed MEDIUM can recur at every release. "No harness fix exists" is a claim somebody must check (the Security Engineer's review, O4) | **Chosen by the user** |
| Rule 1: every plan must name a fix | Simplest reading of ADR-011 | A finding that only the user's environment can close would block every release, or get a made-up fix, or be regraded down | Not chosen |
| **Rule 2: a new acceptance with a new plan cures a passed deadline** | Consistent with ADR-011 ("accepts it again for that release") and ADR-012 ("counts as moved later"). The release document shows the lapse | A deadline can lapse and be renewed again and again; only the user's attention stops that | **Chosen by the user** |
| Rule 2: a passed deadline cannot be cured; the finding must be fixed | Deadlines bind | Combined with Rule 1 it would block every release for a finding that has no harness fix | Not chosen |

## Consequences

- **Positive**
  - The two v11.0.0 acceptances for SEC-T660-01 and SEC-T665-01 rest on a rule and not on a reading.
  - A plan no longer has to pretend that a fix exists. It names who could close the finding and when it is looked at again.
  - A lapsed deadline is visible in the release document, not silently replaced.
- **Negative**
  - A MEDIUM with no harness fix can ship release after release, each time with one more question for the user.
  - The Verdict Rules paragraph and the Conditions line both get longer.
- **Risks introduced**
  - *"None possible" as an escape*: an agent proposes "none possible in the harness" for a finding that has a fix. Mitigation: the three conditions, the user's own acceptance of the plan as shown, and the Security Engineer's review that the question cites (O4).
  - *Serial lapse*: a deadline passes, is renewed, and passes again. Mitigation: each renewal is the user's dated decision and the verdict's Conditions line names the passed deadline each time (O5).
  - *Review date without a review*: the date passes and nobody looks. Mitigation: the review date is the plan's deadline, so a release after it needs a new acceptance (O1), and the owner's outcome belongs in the register (O3). No text can force the owner to record it; the next Release gate's check of the record is the control.
- **Follow-ups**
  - The orchestrator's merge request adds a "Superseded in part by `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md`" note to the header of ADR-012 (rows B1 and B3), in the way ADR-011's header names ADR-012. T800 does not edit ADR-012.
  - A task that applies C1 and C2 (C3 and C4 need no edit), regenerates the mirrors and the registry, and updates the text pins; then a Security Engineer review, as for T720 and T735.
  - The next tracked-debt register records SEC-T762-04 and TL-T761-10 as decided by this record.
  - The v11.0.0 release document: for SEC-T660-01, whose deadline passed before v10.0.0 according to the question shown to the user, the verdict states that the old deadline passed (Rule 2), and for SEC-T660-01 and SEC-T665-01 it records the three Rule 1 items.

## Points that were open (O1 to O7), now ruled

The user's answers of plan-155 left these seven points open, and the Proposed draft decided none of them. With the acceptance quoted in the header ("Accept with all recommendations") **each of O1 to O7 is ruled as in the "Recommended" column**; § Decision states them. The user was shown the short form of each recommendation that the header quotes. Where this column says more than that short form (O1: ADR-012 applies unchanged; O3: what the outcome covers, and that a fix which now exists needs a new acceptance; O4: the question cites the review; O6: what each case needs), the longer text is the drafter's recommended form, which the user accepted as "all recommendations" without being shown it in the question. The "Alternative" column is kept as the record of what was not chosen.

| # | Point | Recommended (ruled) | Alternative (not chosen) |
|---|---|---|---|
| O1 | When the fix is "none possible in the harness", is the review date the plan's `deadline`? | Yes. The review date takes the `deadline` slot, as in the plan shown for SEC-T660-01 ("deadline: review at token renewal on 2027-01-28, ..."), so ADR-012 applies to it unchanged: moving it later, or letting it pass before the release ships, needs a new acceptance | The plan has no deadline; the review date is a separate field, and ADR-012's deadline rules do not apply to it |
| O2 | Must the review date lie before some limit, for example before the next release or within a number of days? | No limit, beyond being still ahead when the release ships. ADR-011 says "There is no time-based maximum", and the acceptance ends at the next release anyway | The review date must be no later than a fixed period after the acceptance, or no later than the next planned release |
| O3 | What must happen on the review date? | The plan's owner records the outcome in the tracked-debt register: whether a harness fix now exists and whether the named outside closer is still right. If a fix now exists, the fix has changed, and ADR-012 requires a new acceptance | Nothing is recorded; the next release's question to the user is the review |
| O4 | Who confirms that "no harness fix exists"? | The Security Engineer's review of the finding states it, and the question to the user cites that review. The user decides | The plan's own statement is enough; the user's acceptance is the only check |
| O5 | Where must the release document say that the old deadline passed, and what must it name? | In the verdict's Conditions line for that finding (row C2): the old deadline's date, and the release the old acceptance was given for | Anywhere in the release document, in free wording |
| O6 | Does Rule 2 also apply when the deadline passes between the acceptance and the shipping of the same release (ADR-012's case), or only to a deadline that passed after an earlier release (the case in the question)? | Both. A passed deadline is treated the same way wherever it passed: new acceptance, new plan, and the statement in the release document | Only the cross-release case; the same-release case stays under ADR-012 with no statement required |
| O7 | May "who could close it outside the harness" be the user? | Yes. The plan shown for SEC-T660-01 and SEC-T665-01 named "owner you (isolation)" | It must be someone other than the person who accepts |

## Validation

The decision is correct if all of these hold:

1. **Three conditions, visible.** Every release verdict that ships a MEDIUM whose fix is "none possible in the harness" shows, from the release document alone, who could close it outside the harness, the plain statement that no harness fix exists, and the review date.
2. **A lapse is never silent.** Every release verdict that relies on a new acceptance after a passed deadline names the passed deadline.
3. **No carry-over.** No release verdict relies on an acceptance given for an earlier release (ADR-011 § Validation 3 still holds).
4. **One definition.** After the follow-up task, both rules appear in full only in `validation-gates` § Verdict Rules.
5. **Tier 1 untouched.** No diff under this record edits `security-guidelines.md` or `AGENTS.md`.
