# ADR-016 — security-engineer-confirmation-as-validity-condition

> Filename: `ADR-016-security-engineer-confirmation-as-validity-condition.md` (zero-padded sequential, kebab-case slug).

- **Status**: Accepted. The user decided on 2026-11-12 (AskUserQuestion; questions, answers and option descriptions verbatim, as [plan-157](../plans/plan-157-confirmation-as-validity-condition.md) § User decisions on ADR-016 records them).
  - Question 1 as shown:
    > ADR-016 is drafted as Proposed. It records your ruling: a "none possible in the harness" plan is valid only when four conditions hold (names an outside closer, says plainly no harness fix exists, sets a review date, and the Security Engineer's review confirms no harness fix exists); a plan lacking any one is not valid and the acceptance does not hold. Your words left four details open (O-A to O-D); the architect recommends an answer for each. Accept ADR-016?
  - The user's answer:
    > Accept with all recommendations (Recommended)
  - The option's description as shown:
    > O-A: citing the review in the question to you stays a separate duty, not part of the condition. O-B: the review must exist before you are asked. O-C: at a later release an earlier review does not serve unseen; a new review or a dated statement that it still holds. O-D: applies to every verdict issued after acceptance, so SEC-T660-01 and SEC-T665-01 need a confirming review on record before the v11.0.0 gate.
  - The other options were "Accept, but citing is part of the condition", "Accept the fourth condition only" and "I want to read it first".
  - Question 2 as shown:
    > Three wording-only fixes sit in the same paragraph (LOW findings from the T802 review; they keep the rule). W1 (SEC-T802-01): the review-date outcome says what it covers ("whether a harness fix now exists and whether the outside closer is still right; a fix that now exists is a changed fix"). W2 (SEC-T802-02): "It covers only the release" becomes "An acceptance covers only the release". W3 (SEC-T802-04): the gate-input line gains "and its plan's deadline". Which should go into the same change?
  - The user's answer (multiple choice):
    > W1 (SEC-T802-01),W2 (SEC-T802-02),W3 (SEC-T802-04)
  - The other option was "None" ("Leave all three as tracked LOW debt.").
  - Accepted ADRs are immutable; a change needs a superseding ADR.
  - Drafted as Proposed in T804. Until it was accepted, no ruling, verdict or knowledge edit could cite it as authority (ADR-008 P5, as cited in the ADR-015 header; ADR-008 itself not opened, **(unverified)**). Only the user accepts it. The acceptance is recorded in this header through a normal merge request (`git-workflow.md`).
  - The user's words are the quoted questions, answers and option descriptions here, and the quoted answer in § The user's decision. The orchestrator's sentences quoted there are the orchestrator's. All other wording of this record is the drafter's.
- **Date**: 2026-11-12
- **Decider(s)**: the user (2026-11-12), and nobody else. solution-architect drafted it.
- **Tasks**: T804 (draft and revision). T805 (apply) and T806 (security review) follow ([plan-157](../plans/plan-157-confirmation-as-validity-condition.md) § Task Decomposition).
- **Requirements**:
  - [`docs/tasks/task-T804.md`](../tasks/task-T804.md) § 2; [plan-157](../plans/plan-157-confirmation-as-validity-condition.md) § User decision, § User decisions on ADR-016 and § Scope choice.
  - [ADR-015](ADR-015-medium-plan-without-fix-and-passed-deadline.md) § Decision (Rule 1, O4), § Files and lines rows C1 and C2.
  - Finding SEC-T802-03, and for the wording table SEC-T802-01, -02 and -04 ([security review T802](../artifacts/security-review-t802-adr-015-apply-v1.md) § Findings).
- **Supersedes**: ADR-015 in part (§ Sentences of ADR-015 this record supersedes). The rest of ADR-015 stands, and so do [ADR-011](ADR-011-user-accepted-medium-at-release.md) and [ADR-012](ADR-012-medium-acceptance-record.md) as ADR-015 left them (ADR-011 not opened in T804, **(unverified)**; of ADR-012 only the header was read). The header of ADR-015 carries the note "Superseded in part by" this record; nothing else in ADR-015 is edited.

## Context

ADR-015 Rule 1 lets the remediation plan of a user-accepted `SECURITY:MEDIUM` finding say "none possible in the harness" as its fix, "only when" the plan does three things, and it states the consequence for those three: a plan that lacks one is not valid and the acceptance does not hold.

ADR-015 also requires (O4) that the Security Engineer's review of the finding confirms that no harness fix exists. That requirement stands outside the "only when" conditions, in ADR-015 and in the live rule text, and no text says that the acceptance fails without it. The security review of T802 recorded this as SEC-T802-03 (LOW) and said the change "needs the user's word, since it makes O4 a fourth validity condition".

Without the consequence, the claim "no harness fix exists" can rest on the plan's own statement alone: the three conditions are all things the plan says about itself. The confirmation is the only one of the four that a party other than the plan's author supplies.

ADR-015 is accepted and immutable, so the change is this new record.

## The user's decision (2026-11-12)

Quoted from [plan-157](../plans/plan-157-confirmation-as-validity-condition.md) § User decision. The plan is the only source for what was said. The acceptance of this record, with the rulings on O-A to O-D and on W1 to W3, is quoted in the header.

The orchestrator wrote, at the end of plan-156:

> One decision is still open with you: whether the Security Engineer's confirmation should become a fourth validity condition for a "none possible in the harness" plan (SEC-T802-03). It is tracked as LOW debt until you decide.

Earlier in the same session it had described the finding as:

> Today the text requires the Security Engineer's confirmation that no harness fix exists, but does not say an acceptance fails without it. Making it a fourth validity condition changes the rule you accepted, so I have left it as tracked debt until you decide.

The user's answer:

> confirmation should become a fourth validity condition

## Decision

**A remediation plan's fix may be "none possible in the harness" only when all four of these hold:**

| # | Condition | Source |
|---|---|---|
| 1 | The plan names who could close the finding outside the harness | ADR-015 Rule 1, unchanged |
| 2 | The plan states plainly that no harness fix exists | ADR-015 Rule 1, unchanged |
| 3 | The plan sets a review date | ADR-015 Rule 1, unchanged |
| 4 | The Security Engineer's review of the finding confirms that no harness fix exists | **New as a validity condition.** ADR-015 O4 required it without stating a consequence |

**A plan that lacks any one of the four is not a valid plan under ADR-011, and the acceptance does not hold.** The finding then blocks the release as any unaccepted `SECURITY:MEDIUM` does, until it is fixed or the user accepts it on a valid plan.

For condition 4 this means: if there is no Security Engineer review of the finding, or the review does not confirm that no harness fix exists, the plan is not valid, whatever the plan itself states.

Ruled with the acceptance (the user accepted "all recommendations"; the short form the user was shown for each point is quoted in the header, and the fuller text here is the drafter's recommended form from § Points that were open):

- **The review comes before the question (O-B).** Condition 4 is met only if the review confirms before the user is asked. A review written after the user's answer does not make that acceptance hold; it can serve a new question.
- **A later release (O-C).** At a later release that ships the same finding, an earlier review does not serve unseen. Condition 4 is then met by a new review, or by the Security Engineer's dated statement, for that release, that the earlier review still holds. Either comes before the user is asked (O-B).
- **From when it applies (O-D).** The four conditions apply to every release verdict issued after this record was accepted, whenever the user's acceptance was given. The verdict for v11.0.0 is not yet issued, so for SEC-T660-01 and SEC-T665-01, which the user accepted for v11.0.0 on 2026-11-12, a confirming review must be on record before the v11.0.0 Release gate. This is a transition rule; it is recorded here and in the v11.0.0 release plan, not in the knowledge sources (row D4).
- **Citing is a separate duty (O-A).** The question to the user cites the confirming review, as ADR-015 O4 already required. That duty binds whoever puts the question, but it is not part of condition 4: if the review confirmed before the user was asked and the question failed to cite it, the acceptance holds, and the missing citation is a finding against the question.

Whether O-B and O-D together require the user to be asked again for SEC-T660-01 and SEC-T665-01 depends on a fact this record does not have: whether a Security Engineer review confirming that no harness fix exists was on record before the question of 2026-11-12 **(unverified)**. If one was, the acceptance stands. If none was, condition 4 was not met when the user was asked, and the release plan must put the question again after the review. The orchestrator establishes the fact; this record does not decide it.

**What does not change.**

- An acceptance covers one release only. The fourth condition does not stretch an acceptance, and a confirming review does not carry an acceptance to another release.
- Only the user gives an acceptance. No agent grants, extends or infers one, and no agent carries one over to another release. The Security Engineer's confirmation is a condition of the plan, not an acceptance: the user still decides.
- An acceptance never covers a `SECURITY:CRITICAL` or `SECURITY:HIGH` finding, a breach of an Immutable Security Constraint, or a required security control that is omitted, removed, disabled or weakened.
- ADR-015's other rulings stand: O1 (the review date is the plan's deadline), O2 (no time limit beyond being still ahead at shipping), O3 (the owner records the outcome on the review date), O7 (the outside closer may be the user), and all of Rule 2 with O5 and O6.
- The production default stays "fix first".
- The rule stays defined once, in `validation-gates` § Verdict Rules. `security-guidelines.md`, `AGENTS.md` and the PoC track are not touched.

## Sentences of ADR-015 this record supersedes

File `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md`. Line numbers as they stand in the T804 worktree after the header note of this revision, which is one line; each is one higher than in the Proposed draft of this record. Lines 67, 73, 79 and 80 were re-read after the note; lines 97, 121, 125, 177 and 186 are computed from the same shift of one line, not re-read **(unverified)**.

| # | Line | Sentence, quoted | Effect |
|---|---|---|---|
| S1 | 67 | "**Rule 1. A remediation plan's fix may be "none possible in the harness", but only when the plan does all three of these:**" | **Superseded in part.** The three stay; a fourth condition is added, which is not something the plan does but something the Security Engineer's review does. |
| S2 | 73 | "A plan that lacks any one of the three is not a valid plan under ADR-011, and the acceptance does not hold." | **Superseded.** "any one of the three" becomes any one of the four. |
| S3 | 80 | "- **Confirmation (O4).** The Security Engineer's review of the finding confirms that no harness fix exists, and the question to the user cites that review. The user decides." | **Superseded in part.** The first clause becomes condition 4, with the consequence of S2 and with O-B and O-C. "the question to the user cites that review" is kept as a separate duty (O-A). "The user decides." is kept. |
| S4 | 125 (row C1, "Text" column, first sentence) | "The plan's fix may be "none possible in the harness" only when the plan names who could close the finding outside the harness (it may be the user), states plainly that no harness fix exists, and sets a review date; the Security Engineer's review of the finding confirms that no harness fix exists, and the question to the user cites it." | **Superseded** by rows D1 and D2. The second and third sentences of row C1 are not superseded; row W1 extends the second in wording only. |
| S5 | 177 (row O4, "Recommended (ruled)" column) | "The Security Engineer's review of the finding states it, and the question to the user cites that review. The user decides" | **Superseded in part**, as S3. |
| S6 | 97 | "Rule 1 does not let an agent call a finding unfixable to avoid a fix: the plan as shown to the user must carry the three statements, and the user accepts it or not." | **Extended, not withdrawn.** The plan still carries the three statements; the confirming review must exist besides. |
| S7 | 186 (§ Validation 1) | "**Three conditions, visible.** Every release verdict that ships a MEDIUM whose fix is "none possible in the harness" shows, from the release document alone, who could close it outside the harness, the plain statement that no harness fix exists, and the review date." | **Extended** by § Validation 1 of this record: the verdict also names the confirming review. |

**Row C2 is not superseded and needs no change** (row D3 below).

## Files and lines this decision changes

None of these edits is made in T804; T805 makes them. Line numbers as read on 2026-11-12 in the T804 worktree. I have no search tool; other copies of the superseded sentence outside the files I read are **(unverified)**. The security review of T802 (answer 5) found the other places to be pointers.

The texts below are the drafter's wording of the decision and of O-A to O-D as ruled. The user accepted the rule and the recommendations, and was shown rows W1 to W3 in the short form quoted in the header; T805 applies the texts as written here and may adjust wording only where a pin or a mirror forces it, never the rule.

### Decision (the fourth condition)

| # | File:line | Live text, quoted | Change | Text |
|---|---|---|---|---|
| D1 | `implementation/knowledge/skills/validation-gates/SKILL.md:70` (§ Verdict Rules) | "The plan's fix may be "none possible in the harness" only when the plan names who could close the finding outside the harness (it may be the user), states plainly that no harness fix exists, and sets a review date; the Security Engineer's review of the finding confirms that no harness fix exists, and the question to the user cites it." | Replace the sentence with | "The plan's fix may be "none possible in the harness" only when the plan names who could close the finding outside the harness (it may be the user), states plainly that no harness fix exists, and sets a review date, and only when the Security Engineer's review of the finding confirms, before the user is asked, that no harness fix exists; the question to the user cites that review. A plan that lacks any one of these four is not a valid plan, and the acceptance does not hold." |
| D2 | `implementation/knowledge/skills/validation-gates/SKILL.md:70` (§ Verdict Rules) | (no live text; an addition) | Directly after D1's second sentence, and before "The review date is then the plan's deadline", add | "At a later release that ships the finding, an earlier review confirms only with the Security Engineer's dated statement, for that release, that it still holds." |
| D3 | `implementation/knowledge/agents/release-manager.md:183` (Conditions line, `mitigation=[...]` slot) | "the plain statement that no harness fix exists with the Security Engineer review that confirms it" | None | — |
| D4 | No knowledge file (O-D) | — | None | — |

- **D1** makes three changes in the live sentence and adds one sentence: "; the Security Engineer's review" becomes ", and only when the Security Engineer's review"; "confirms that" becomes "confirms, before the user is asked, that" (O-B); ", and the question to the user cites it" becomes "; the question to the user cites that review" (O-A: after the semicolon, outside both "only when"); and the consequence sentence follows. "these four" are the three things the plan does and the confirmation; the citing is not one of them.
- **D2** is needed for O-C to be enforceable. Without it, "the Security Engineer's review of the finding" in D1 is met by any earlier review, which is the alternative the user did not choose. A new review needs no words: it is a review of the finding that confirms before the user is asked. D2 states only the other route. It stands after the consequence sentence, so "these four" keeps its count, and it narrows what counts as meeting condition 4.
- **D3**: the slot records the review; it does not state the validity rule, which is defined once in the skill. With condition 4 an unfilled slot means an invalid plan, and that follows from the skill. Under D2 the slot names the dated statement together with the earlier review; the words "the Security Engineer review that confirms it" cover that. `release-manager.md:43` points to "that section" and copies no plan rule, so it needs no change either (ADR-015 row C4).
- **D4**: O-D is a transition rule for the verdicts issued after this record, in practice v11.0.0. It is recorded in § Decision and belongs in the v11.0.0 release plan (the orchestrator's; not yet written, **(unverified)**). No knowledge text carries it: the skill's text has no date of effect, so it applies to every verdict issued once T805 is merged, and a sentence about v11.0.0 would be stale after that release.

### Wording only, not part of the decision

**Included by the user's answer to question 2** (header): "W1 (SEC-T802-01),W2 (SEC-T802-02),W3 (SEC-T802-04)". ADR-015 allows them without an ADR: "the follow-up task may adjust the wording but not the rule" (`ADR-015…md:121`). The orchestrator proposed including them, so that the same line, the same pins and the same root drift are touched once ([plan-157](../plans/plan-157-confirmation-as-validity-condition.md) § Scope choice). The texts are unchanged from the Proposed draft; D1 and D2 touch none of the three quoted fragments, so no adjustment was needed.

| # | Finding | File:line | Live text, quoted | Replace with |
|---|---|---|---|---|
| W1 | SEC-T802-01 | `implementation/knowledge/skills/validation-gates/SKILL.md:70` | "and on it the plan's owner records the outcome in the tracked-debt register." | "and on it the plan's owner records the outcome in the tracked-debt register (whether a harness fix now exists and whether the outside closer is still right; a fix that now exists is a changed fix)." |
| W2 | SEC-T802-02 | `implementation/knowledge/skills/validation-gates/SKILL.md:70` | "It covers only the release it was given for:" | "An acceptance covers only the release it was given for:" |
| W3 | SEC-T802-04 | `implementation/knowledge/skills/validation-gates/SKILL.md:120` (§ Gate Input Requirements, Release Gate) | "with the release each acceptance was given for (§ Verdict Rules:" | "with the release each acceptance was given for and its plan's deadline (§ Verdict Rules:" |

W1 states ADR-015 O3 in full (`ADR-015…md:79`); a changed fix already needs the user's new acceptance under the same paragraph. W2 changes a pronoun whose antecedent moved when ADR-015 row C1 was inserted. W3 gives the release manager the date that ADR-015 O5 requires in the Conditions line.

### Which record a test compares each text with

For T805's pins in `tests/functional/test_release_self_review_text.py` (file not read, **(unverified)**; the description of its present pins is from the security review of T802, answers 3 and 4).

| Row | Live text after T805 | Compare with |
|---|---|---|
| D1 | The two sentences of D1's "Text" column | This record, row D1. It no longer matches ADR-015 row C1's first sentence, so a test that requires the whole C1 text in ADR-015 must be split |
| D2 | The one sentence of D2's "Text" column, directly after D1 | This record, row D2 |
| D3 | The Conditions line, unchanged | ADR-015 row C2 (and ADR-012 row B3 for the part without the C2 insertions), as today |
| D4 | No text | Nothing to pin |
| C1, second sentence (ADR-015) | "The review date is then the plan's deadline, … in the tracked-debt register" followed by W1's parenthesis and the full stop | ADR-015 row C1 for the sentence up to "tracked-debt register"; this record, row W1, for the "Replace with" text |
| C1, third sentence (ADR-015) | Unchanged | ADR-015 row C1, as today |
| W1 | W1's "Replace with" text | This record, row W1 |
| W2 | W2's "Replace with" text | This record, row W2. Which earlier record holds the "It covers" sentence is **(unverified)** (ADR-011 not opened); a pin on that record's text must allow for this one changed word pair |
| W3 | W3's "Replace with" text, in § Gate Input Requirements | This record, row W3 |

Each "Text" and "Replace with" cell above appears once in this record in that exact form, by my reading; I have no tool to count **(unverified)**. If a test requires "exactly once, in quotes", it should count in this record and report a mismatch as a finding, not edit the record.

## Points that were open (O-A to O-D), now ruled

The user's sentence "confirmation should become a fourth validity condition" left these four points open, and the Proposed draft decided none of them. With the acceptance quoted in the header ("Accept with all recommendations (Recommended)") **each of O-A to O-D is ruled as in the "Recommended (ruled)" column**; § Decision states them. The user was shown the short form of each recommendation that the header quotes. Where this column says more than that short form, the longer text is the drafter's recommended form, which the user accepted as "all recommendations" without being shown it in the question. The "Alternative" column is kept as the record of what was not chosen.

| # | Point | Recommended (ruled) | Alternative (not chosen) |
|---|---|---|---|
| O-A | Is "the question to the user cites it" part of the fourth condition, or a separate duty? | A separate duty. The user's sentence names the "confirmation", not the citing. The duty stays binding on whoever puts the question, and the verdict's `mitigation` slot records the review in any case. If the review confirmed in time but the question failed to cite it, the acceptance still holds, and the missing citation is a finding against the question | Part of the condition (the option "Accept, but citing is part of the condition"): an acceptance given on a question without the citation would not hold |
| O-B | When must the confirming review exist? | Before the user is asked. The user decides on the plan as shown, and the question cites the review, so the review comes first. D1 says it in the words "before the user is asked" | It is enough that the review confirms before the release ships |
| O-C | At a later release that ships the same finding, may an earlier release's review serve as the confirmation? | No, not unseen. The acceptance is new for each release, and a harness fix may exist by then (ADR-015 O3). The Security Engineer confirms for the release asked about, by a new review or by a dated statement that the earlier review still holds (row D2) | Any earlier confirming review of the finding is enough until a review says otherwise |
| O-D | Does the fourth condition apply to acceptances the user gave before this record, in particular those of 2026-11-12 for SEC-T660-01 and SEC-T665-01 for v11.0.0? | Yes, for every release verdict issued after this record was accepted. The verdict for v11.0.0 is not yet issued, so a confirming review must be on record before that gate (row D4; § Decision says what follows if no review preceded the question) | Only acceptances given after this record need the confirmation |

## Alternatives considered

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| **Confirmation as a fourth validity condition** | The one condition that does not come from the plan's author has a stated consequence. "No harness fix exists" cannot rest on the plan's word alone | One more thing that can invalidate an acceptance the user has already given; the Release gate must check it | **Chosen by the user** |
| Keep ADR-015 as it is (confirmation required, no consequence) | No rule change | A missing review shows only as an unfilled slot; no text says what follows (SEC-T802-03) | Not chosen |
| Drop the confirmation; the user's acceptance is the only check | Simplest | ADR-015 already rejected it (row O4, alternative) | Not chosen |

## Consequences

- **Positive**
  - The rule says in so many words what follows when the confirmation is missing.
  - The "none possible" escape named in ADR-015 § Risks has a check that the plan's author cannot supply alone.
- **Negative**
  - The Verdict Rules paragraph grows by two sentences and W1's parenthesis.
  - A release with such a finding depends on a Security Engineer review being on record before the user is asked, at every release that ships it.
- **Risks introduced**
  - *A confirmation given too easily.* The review, or the dated statement of D2, says "no harness fix" without looking. Mitigation: each is a recorded, dated statement under the Security Engineer's own rules, the question cites the review, and the user decides.
  - *An acceptance voided late.* The gap is found at the Release gate after the user accepted. Mitigation: O-B puts the review before the question.
  - *A question without the citation.* Under O-A the acceptance holds. Mitigation: the duty stays in the rule text, and the verdict's `mitigation` slot must name the review.
- **Follow-ups** (none made in T804)
  - **Source edits** (T805): rows D1, D2 and W1 to W3 in `implementation/knowledge/skills/validation-gates/SKILL.md`. No edit to `release-manager.md` (row D3).
  - **Test pins** in `tests/functional/test_release_self_review_text.py`: as § Which record a test compares each text with. New pins and mutations are advisable for "and only when", "before the user is asked", the consequence sentence, D2, each W row, the citing clause standing after the semicolon, and (SEC-T802-02's recommendation) the sentence "Only the user can accept it; no agent grants, extends or infers an acceptance".
  - **Header note on ADR-015**: added in this revision of T804, at the coordinator's instruction, in the form ADR-012 carries for ADR-015. Nothing else in ADR-015 is changed.
  - **Mirrors, registry and root drift**: the edits are source edits, so `sync.mjs` and `generate-registry.py` must run. Root drift is declared for the validation-gates skill under each platform folder until a root refresh, which needs the user's approval at that moment. No release-manager mirror changes.
  - **Golden cases** under `tests/golden/`: not opened. If a fixture quotes the changed text, the change needs a protected-path grant.
  - **Security Engineer review** of the applied change (T806).
  - **Tracked-debt register**: the next version records SEC-T802-03 as decided by this record, and SEC-T802-01, -02 and -04 as fixed once T805 is merged.
  - **v11.0.0 release plan**: carries O-D. Before the Release gate, a Security Engineer review confirming that no harness fix exists is on record for SEC-T660-01 and SEC-T665-01; the plan states whether such a review preceded the question of 2026-11-12, and if not, puts the question again after it (§ Decision).

## Validation

The decision is correct if all of these hold:

1. **Four conditions, visible.** Every release verdict that ships a MEDIUM whose fix is "none possible in the harness" shows, from the release document alone, who could close it outside the harness, the plain statement that no harness fix exists, the review date, and the Security Engineer review that confirms it.
2. **No acceptance on three.** No release verdict relies on such a plan without a confirming review dated before the user's acceptance.
3. **No review carried over unseen.** No release verdict relies on a review made for an earlier release without a new review or the dated statement of row D2.
4. **One definition.** After T805, the four conditions and the consequence appear in full only in `validation-gates` § Verdict Rules.
5. **Pinned.** Removing "and only when", "before the user is asked", the consequence sentence or row D2's sentence from the live text fails a test.
6. **Tier 1 untouched.** No diff under this record edits `security-guidelines.md` or `AGENTS.md`.
