# Security review T806 — T805 applies ADR-016 (rows D1, D2, W1 to W3) — v1

- **Based on:** `docs/decisions/ADR-016-security-engineer-confirmation-as-validity-condition.md` (Accepted 2026-11-12)
- **Based on:** `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md` (§ Decision lines 64-83 read; the rest taken from ADR-016's quotations)
- **Based on:** `docs/artifacts/security-review-t802-adr-015-apply-v1.md` (SEC-T802-01 to -04)
- **Based on:** `docs/tasks/task-T806.md` (§ 3, the orchestrator's evidence); `docs/tasks/task-T805.md` and `docs/plans/plan-157-confirmation-as-validity-condition.md` cited from the brief, not opened
- **Based on:** commit range `942ca923..946a2a9a` on `agent/solution-architect/T804` (`97e1c0b4` source and pins, `946a2a9a` mirrors, registry, drift declaration), read in the worktree `../worktrees/agent-solution-architect-T804`
- **Date:** 2026-11-12
- **Reviewer:** security-engineer (read-only; no shell, no test run)
- **Gate:** security

## Summary

- **Risk Level**: LOW
- **Findings**: 0 CRITICAL, 0 HIGH, 0 MEDIUM, 3 LOW
- **Status**: PASS

The skill carries ADR-016's rows D1, D2, W1, W2 and W3 word for word, in the places the ADR names. The Security Engineer's confirmation is now inside "only when", with "before the user is asked", and the consequence sentence names "any one of these four". The citing duty stands after the semicolon, outside the condition. Nothing in ADR-011, ADR-012 or the standing part of ADR-015 is weakened. Every clause of the five rows is pinned and has a mutation. The three LOW findings are a timing rule that holds only by inference (in ADR-016's own row text), a record slot that does not carry the review's date, and one sentence still unpinned.

## Answers

### 1. Fourth condition, consequence and O-A to O-C as ruled?

Yes, no more and no less than rows D1 and D2.

| Element | ADR-016 | `SKILL.md:70` |
|---|---|---|
| Condition 4 | row D1 (`ADR-016…md:115`) | "and only when the Security Engineer's review of the finding confirms, before the user is asked, that no harness fix exists" |
| Consequence | "A plan that lacks any one of the four is not a valid plan…, and the acceptance does not hold" (line 67) | "A plan that lacks any one of these four is not a valid plan, and the acceptance does not hold." |
| O-B | review before the question (line 73) | "before the user is asked", inside the condition |
| O-A | citing is a separate duty (line 76) | "; the question to the user cites that review." after the semicolon, outside both "only when" |
| O-C | new review or dated statement (line 74) | "At a later release that ships the finding, an earlier review confirms only with the Security Engineer's dated statement, for that release, that it still holds." |

- **Placement**: D2 stands directly after the consequence sentence and before "The review date is then the plan's deadline", as row D2 requires.
- **Citing (O-A)**: it is still a duty in the rule text and is not one of "these four". Before the consequence sentence there are exactly four items inside "only when" (names, states, sets, confirms); the citing clause follows a semicolon.
- **Valid plan without the review**: I see no such reading. The confirmation is under "only when", and the consequence sentence covers it by count.
- **Review made after the user was asked**: it does not meet "confirms, before the user is asked".
- **Omissions that lose nothing**: the skill leaves out "under ADR-011" and "The finding then blocks the release". The second still follows from "fixed before the release ships, unless the user accepts it" on the same line.

Two points are narrower in wording than § Decision; both come from the ADR's row text, not from T805 (SEC-T806-01):

- **Timing of the dated statement.** § Decision says the new review or the dated statement "comes before the user is asked". D2 does not repeat it. It follows only by combining D2 ("confirms only with") with D1 ("confirms, before the user is asked").
- **"Earlier review" and "later release" have no stated reference point.** I read them as: a review made before the release now asked about, at any release after the first that shipped the finding. At a finding's first release, a review of any age serves; the ADR ruled nothing else.

### 2. W1 to W3 wording only? Do SEC-T802-01 to -04 close?

Yes to both.

- **W1** adds the parenthesis "(whether a harness fix now exists and whether the outside closer is still right; a fix that now exists is a changed fix)". This is ADR-015 O3 in full (`ADR-015…md:79`), and a changed fix already needs a new acceptance on the same line. No new rule. Closes SEC-T802-01.
- **W2** changes "It covers" to "An acceptance covers". The rule is the same; the wrong antecedent is gone. The sentence and the user-only sentence are now pinned. Closes SEC-T802-02.
- **W3** adds "and its plan's deadline" to the Release gate input at `SKILL.md:120`. It is a gate input, not a rule, and gives the date ADR-015 O5 needs. Closes SEC-T802-04.
- **SEC-T802-03** closes by the user's decision (ADR-016) and row D1.

All four close when T805 is merged. The installed root copies keep the old text until the root refresh; that drift is declared.

### 3. Do the pins hold each element?

Yes, by reading the test; that it executes (30 tests OK) is the orchestrator's evidence.

- **Clause pins**: `ADR_016_CLAUSES` (`test_release_self_review_text.py:266-276`) names 18 entries, checked by `_b1_errors` (lines 477-489) in the one § Verdict Rules paragraph, in the source and four mirrors. It includes whole-text pins for D1, D2 and W1, "D2 directly after D1", "W2 sentence directly after C1" and the user-only sentence in its place.
- **Whole-text pins catch any inside change**: `C1_TEXT` (line 250) now spans D1, D2, sentence 2 with W1, and Rule 2, so any single change inside that span fails at least one entry.
- **Old wording kept out**: `ADR_016_OLD` (line 278) fails if ADR-015's confirmation clause, "cites it", "It covers…" or the outcome sentence without the parenthesis returns.
- **W3**: `_w3_errors` (lines 492-501) requires the whole input line verbatim, once, in `### Release Gate`.
- **Mutations**: I count 22 new entries (lines 810-849), which matches "73 to 95". They are 9 for D1, 5 for D2, 2 each for W1, W2, the user-only sentence and W3. Each named clause has one, including the confirmation moved back outside "only when", "before the user is asked" dropped, citing made part of the condition, four changed to three, and D2 moved or undated.
- **Text matches the ADR**: `test_d1_d2_and_w1_to_w3_are_the_text_of_adr_016` (lines 691-698) requires each of the five texts exactly once, in quotes, in ADR-016. By my reading each occurs once (lines 115, 116, 131, 132, 133); the shorter forms in the header at line 14 do not match.
- **The disclosed deviation is sound.** ADR-016 quotes the superseded ADR-015 sentence twice (row S4 at line 98 and row D1's "Live text" at line 115), so a count of one cannot hold. The presence check is an extra. The authority for that sentence is still ADR-015, where `test_c1_and_c2_are_the_text_of_adr_015` (lines 675-680) counts the whole of C1 exactly once.
- **Standing ADR-015 text**: `test_live_c1_is_adr_015_but_for_the_rows_of_adr_016` (lines 682-689) shows the live C1 equals ADR-015's once D1, D2 and W1 are taken out.

Two limits remain:

- The sentence "An acceptance never covers a security finding graded critical or high…" is still not pinned in this file (SEC-T806-03).
- Substring pins do not catch a new contradicting sentence added elsewhere in the paragraph. This limit is general, predates T805, and is not graded.

### 4. Anything weakened in ADR-011, ADR-012 or standing ADR-015?

No. All on `SKILL.md:70`, by reading:

- **ADR-011**: "Only the user can accept it; no agent grants, extends or infers an acceptance." is unchanged and now pinned. "An acceptance covers only the release it was given for…" is clearer, not wider. "An acceptance never covers…" is unchanged.
- **ADR-012**: the record sentence, new-acceptance, lapsed-deadline and owner-change sentences are unchanged and pinned against ADR-012.
- **ADR-015**: O1, O2, O3 and Rule 2 with O5 and O6 are unchanged apart from W1's parenthesis. Row C2 (`release-manager.md:183`) is unchanged; I compared it with `B3_LINE`.
- The fourth condition only narrows when an acceptance holds. The confirmation is not an acceptance, and no text lets an agent grant one.

### 5. Gap between the skill and `release-manager.md:183`?

One, LOW (SEC-T806-02). The validity rule is in the skill only, which is right ("one definition"), and an unfilled slot is an invalid plan. But the slot asks only for "the Security Engineer review that confirms it". It does not ask for the review's date or, at a later release, the dated statement. So whether the review came before the question (O-B) and whether D2 was met (O-C) cannot be read "from the release document alone", which ADR-016 § Validation 1 to 3 expect; the checker must open the artifact. Review artifacts carry a date, so the fact is recoverable. Row D3 ("None") was ruled, so this is not a defect of T805.

### 6. O-D: what the v11.0.0 release plan must carry

See the note below. Not a finding against T805: row D4 rules that no knowledge text carries O-D.

## Findings

| Id | Grade | File:line | Description | Recommendation |
|---|---|---|---|---|
| SEC-T806-01 | SECURITY:LOW | `implementation/knowledge/skills/validation-gates/SKILL.md:70` (from `ADR-016…md:116`, row D2) | (a) D2 does not say that the dated statement must exist before the user is asked; it holds only by combining D2 with D1. A statement written after the question could be argued to serve. (b) "an earlier review" and "a later release" have no stated reference point. | Track. Wording candidate, same rule: "…confirms only with the Security Engineer's dated statement, made for that release before the user is asked, that it still holds." Needs ADR-016's pin and row text to allow it; decide the route at the next edit of § Verdict Rules. Until then the release plan applies § Decision's reading. |
| SEC-T806-02 | SECURITY:LOW | `implementation/knowledge/agents/release-manager.md:183` (unchanged by T805, row D3); also `SKILL.md:120` | The `mitigation` slot names the confirming review but not its date or, at a later release, the dated statement. The Release gate inputs do not list the confirming review. O-B and O-C are therefore not checkable from the release document alone. | Track. Until a text change is decided, the release document names the review artifact with its date, the dated statement if D2 applies, and the date the question was put. A slot change touches ADR-015 row C2 and needs its own decision. |
| SEC-T806-03 | SECURITY:LOW | `tests/functional/test_release_self_review_text.py:266-276` (sentence at `SKILL.md:70`) | "An acceptance never covers a security finding graded critical or high, a breach of an Immutable Security Constraint, or a required security control that is omitted, removed, disabled or weakened." is not pinned in this file. It is the limit of the whole acceptance route. Predates T805 (noted in the T802 review, answer 3). Whether another test file pins it is **(unverified)**. | Track. Add the sentence to the clause pins with one mutation (for example dropping "or high") at the next edit of this test. |

No finding is CRITICAL, HIGH or MEDIUM. No Immutable Security Constraint is touched. No control that `security-guidelines.md` requires is omitted, removed, disabled or weakened; the change adds a condition.

## Status of SEC-T802-01 to -04

- **SEC-T802-01**: fixed by W1 (`SKILL.md:70`), pinned; effective at merge of T805.
- **SEC-T802-02**: fixed by W2 (`SKILL.md:70`); the sentence and the user-only sentence are pinned; effective at merge.
- **SEC-T802-03**: decided by the user (ADR-016) and fixed by D1 and D2; effective at merge. SEC-T806-01 is its residue.
- **SEC-T802-04**: fixed by W3 (`SKILL.md:120`), pinned; effective at merge.

## Note for the v11.0.0 release plan (O-D)

For SEC-T660-01 and SEC-T665-01 the plan must carry these items:

1. **The fact ADR-016 left open.** State whether a Security Engineer review confirming that no harness fix exists was on record before the question of 2026-11-12, naming the artifact and its date for each finding. I know of none and did not search **(unverified)**.
2. **D2 applies.** Both findings shipped in v10.0.0 under the user's acceptance (taken from the session record, **(unverified)** by me), so v11.0.0 is "a later release that ships the finding". A review from before the v11.0.0 question confirms only with the Security Engineer's dated statement, for v11.0.0, that it still holds; otherwise a new review is needed.
3. **Probable consequence.** The question of 2026-11-12 was put before ADR-016, so a new review or dated statement for v11.0.0 is unlikely to have preceded it **(unverified)**. If none did, condition 4 was not met then. The plan must then commission the review first, as its own task, and put the question to the user again afterwards. The new question shows the same plan (owner, fix "none possible in the harness", outside closer, review date 2027-01-28) and cites the review. The verdict records the user's new words verbatim with the date. No agent may treat the earlier answer as carried over.
4. **This review is not that confirmation.** T806 reviewed rule text only and did not assess either finding.
5. **The record.** The Conditions line names the confirming review with its date, the dated statement if one is used, and the date the question was put (SEC-T806-02).
6. **The deadline.** The review date 2027-01-28 must still be ahead when v11.0.0 ships; if not, ADR-015 Rule 2 applies.
7. **Not affected.** SEC-T702-09's plan has a fix (a version bump), so the four conditions do not apply to it.

## What I did not verify

- **Tests and gates**: I ran nothing. The 30 tests, validate-tasks, link integrity, team health, scorecard, sync `--check`, registry `--check` and `--print-drift` results are the orchestrator's evidence (brief § 3). The full suite was not yet run at this range.
- **The diff itself**: I read files at the branch tip. That the word diff shows only the five changes is the orchestrator's evidence. I compared the unchanged sentences of line 70 with the T802 review's quotations and the test's pins, by reading.
- **Mirrors, registry, drift baseline**: not opened (budget). Whether the four mirrors carry the same text rests on the pin test and `sync --check`, both the orchestrator's.
- **ADR-011, ADR-012, plan-157, `task-T805.md`**: not opened. That the user-only and W2 sentences are ADR-011's text rests on `test_w2_and_the_user_only_sentence_are_the_text_of_adr_011` passing in the orchestrator's run. The user's words are taken from ADR-016's header.
- **ADR-015**: only lines 64-83 read; rows C1 and C2 are taken from ADR-016's quotations and the test constants.
- **Counts in ADR-016**: "once, in quotes" for D1, D2 and W1 to W3 is by my reading, in line with the orchestrator's count.
- **Other restatements** of the superseded sentence outside the files read: **(unverified)**; the T802 review found the other places to be pointers.
- **`release-manager.md`**: only lines 181-185 read; line 43 is taken from the T802 review.
- **Token usage**: not measured; estimate about 85k including context, over the 60k budget. The pin file (953 lines) accounts for most of the excess.

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 3 | 0 | 3 |

### Justification
D1, D2 and W1 to W3 are ADR-016's text in the places it names (answers 1 and 2). The confirmation is a validity condition with a stated consequence; the citing stays a duty (O-A); the review must precede the question (O-B); an earlier review needs the dated statement (O-C). Nothing is wider than ruled, and ADR-011, ADR-012 and standing ADR-015 are intact (answer 4). Every clause is pinned and mutated, and the disclosed deviation is sound (answer 3). SEC-T806-01 to -03 are LOW and are tracked as technical debt in the next tracked-debt register; PASS depends on that tracking.

### OWASP Coverage
The change is rule text and text pins, with no executable product code.

| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes (who may accept; no agent path) | 0 |
| A02: Cryptographic Failures | No (not applicable) | 0 |
| A03: Injection | No (not applicable) | 0 |
| A04: Insecure Design | Yes (rule completeness, timing of the confirmation, carried-over reviews) | 2 |
| A05: Security Misconfiguration | No (not applicable) | 0 |
| A06: Vulnerable Components | No (no dependency change) | 0 |
| A07: Auth Failures | No (not applicable) | 0 |
| A08: Data Integrity Failures | Yes (pins, ADR text match) | 1 |
| A09: Logging & Monitoring | Yes (what the verdict records) | 0 (covered by SEC-T806-02 under A04) |
| A10: SSRF | No (not applicable) | 0 |

## Gate Verdict

**Gate:** security
**Verdict:** PASS
**Conditions:** none. LOW findings SEC-T806-01 to SEC-T806-03 go to the next tracked-debt register.

## Task completion

- **Artifact**: this file, `docs/artifacts/security-review-t806-adr-016-apply-v1.md` (the orchestrator commits it).
- **Acceptance criteria**: each finding has a file, line and grade; each claim not verified is marked or listed; the verdict follows the project rule (no CRITICAL, HIGH or MEDIUM; LOW tracked as debt).
- **Follow-ups**: the note for the v11.0.0 release plan, in particular items 1 to 3; SEC-T806-01 and -02 may need the user's word if their fix is judged more than wording.
- **Blockers**: none.
