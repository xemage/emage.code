# Security review T802 — T801 applies ADR-015 (rows C1 and C2) — v1

- **Based on:** `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md` (Accepted 2026-11-12)
- **Based on:** `docs/plans/plan-156-apply-adr-015.md` (task T802; cited from the brief, not opened)
- **Based on:** `docs/tasks/task-T802.md` (§ 6, the orchestrator's evidence)
- **Based on:** commit range `218f86b2..9b9ab6d1` on `agent/backend-developer/T801` (`23de85b9` sources and pins, `9b9ab6d1` mirrors, registry, drift baseline), read in the worktree `../worktrees/agent-backend-developer-T801`
- **Date:** 2026-11-12
- **Reviewer:** security-engineer (read-only; no shell, no test run)
- **Gate:** security

## Summary

- **Risk Level**: LOW
- **Findings**: 0 CRITICAL, 0 HIGH, 0 MEDIUM, 4 LOW
- **Status**: PASS

The two edited sources carry ADR-015's rows C1 and C2 word for word. Both rules and O1 to O7 are present. Nothing in ADR-011 or ADR-012 is weakened: only the user accepts, one release only, no agent grants, extends or infers an acceptance, and critical, high, constraint breaches and weakened controls are never covered. The pins hold every element of C1 and C2. The four LOW findings are wording gaps; three of them are in ADR-015's own row text, which T801 applied faithfully.

## Answers

### 1. Is C1 and are the two C2 insertions the text of ADR-015, with every condition?

Yes.

- **C1**: `implementation/knowledge/skills/validation-gates/SKILL.md:70` holds the three sentences of ADR-015 row C1 (`ADR-015…md:124`), directly after "…records both the owner shown to the user and the current owner." I compared them by reading; the orchestrator's word diff says verbatim (brief § 6).
- **C2**: `implementation/knowledge/agents/release-manager.md:183` holds both insertions of row C2 (`ADR-015…md:125`): in `mitigation=[…]` after "and the current owner if it has changed", and in `deadline=[…]` after "or the fix changes".
- The rest of line 70 is unchanged. I compared it with the main checkout's copy, which lacks the change: the sentences before and after the insertion are the same, by reading, not by a tool diff.

| Element | C1 (`SKILL.md:70`) | C2 (`release-manager.md:183`) |
|---|---|---|
| Rule 1, three conditions | "only when the plan names who could close the finding outside the harness…, states plainly that no harness fix exists, and sets a review date" | "who could close it outside the harness, the plain statement that no harness fix exists…, and the review date" |
| O1 review date is the deadline | "The review date is then the plan's deadline" | "the review date, which is the plan's deadline" |
| O2 no other limit | "with no limit other than being still ahead when the release ships" | not needed in a record slot |
| O3 owner records the outcome | "on it the plan's owner records the outcome in the tracked-debt register" | not a release-time record |
| O4 Security Engineer confirms, question cites it | "the Security Engineer's review of the finding confirms that no harness fix exists, and the question to the user cites it" | "with the Security Engineer review that confirms it" |
| O7 closer may be the user | "(it may be the user)" | not needed |
| Rule 2 cure | "the user's new, dated acceptance with a new plan and a deadline still ahead replaces the old one" | the existing `risk_accepted_by` and `deadline` slots |
| O5 statement, date, release | "the verdict's Conditions line says that the old deadline passed and names its date and the release the old acceptance was given for" | "the statement that it passed, its date, and the release the old acceptance was given for" |
| O6 any passed deadline | "after an earlier release or before this one ships" | "if an earlier plan's deadline for this finding has passed" (covers both cases) |

Nothing is wider than the ADR. Two things are narrower than ADR-015 § Decision, and both come from the ADR's own row text, not from T801:

- **O3**: the skill does not say what the outcome covers, or that a fix which now exists is a changed fix that needs a new acceptance (`ADR-015…md:78`). The second part still follows from "changing the fix needs the user's new acceptance" on the same line. See SEC-T802-01.
- **Rule 1's consequence**: "A plan that lacks any one of the three is not a valid plan under ADR-011, and the acceptance does not hold" (`ADR-015…md:72`) is carried only by the words "only when". That is enough for the three conditions; for O4 see SEC-T802-03.

### 2. Does the new text open a path for an agent, or beyond MEDIUM?

No.

- **Who accepts**: Rule 2 names "the user's new, dated acceptance". "Only the user can accept it; no agent grants, extends or infers an acceptance" is still on `SKILL.md:70`, and `release-manager.md:43` still says "you never grant, extend or infer one, and an acceptance given for an earlier release does not cover this one".
- **One release only**: "It covers only the release it was given for…" still follows, now directly after the Rule 2 sentence. The pronoun's antecedent moved (SEC-T802-02); the rule is not weakened, because `release-manager.md:43` states it independently.
- **"None possible" without review and date**: the review date is one of the three "only when" conditions. The confirming review is stated as a requirement in C1, and C2 makes it a slot of the record. `docs/releases/_template.md:88` says an accepted MEDIUM "fills every slot of that format", so a missing review shows as an unfilled slot at the Release gate. The consequence of a missing confirmation is not stated in so many words (SEC-T802-03).
- **Scope**: C1 sits inside the accepted-MEDIUM passage, and the sentence "An acceptance never covers a security finding graded critical or high, a breach of an Immutable Security Constraint, or a required security control that is omitted, removed, disabled or weakened" still closes it. The Conditions line still opens "never a security finding, except a `SECURITY:MEDIUM` the user accepted for this release".
- **Lapsed deadline without acceptance**: "a deadline that passes before the release ships counts as moved later" and "fixed before the release ships, unless the user accepts it" are unchanged, so the finding still blocks.

### 3. Do the pins fail if any single element is removed or altered?

Yes, by reading the test; the orchestrator's run (26 OK) is the evidence that they execute.

- **C1**: `C1_CLAUSES` (`test_release_self_review_text.py:218-226`) names 14 elements, plus "whole text" and "directly after the owner sentence". Because the whole text is a substring pin, any single change inside C1 fails at least that entry. `_b1_errors` (lines 416-424) checks them in the one § Verdict Rules paragraph, in the source and in four mirrors.
- **C2**: `B3_LINE` (lines 248-253) pins the whole Conditions line, once, directly under its heading (`_b3_errors`, lines 427-432). `C2_CLAUSES` (lines 260-266) names nine elements and the two slot positions.
- **Mutations**: 19 for C1 (lines 690-722) and 10 for C2 (lines 723-738). They cover each named element, the loosened "only when", an added limit, an undated acceptance, a cure without a new plan, a narrowed O6, a moved C1 and swapped insertions.
- **Text matches the ADR**: `test_c1_and_c2_are_the_text_of_adr_015` (lines 595-600) requires each of the three texts exactly once, in quotes, in ADR-015.

No element of C1 or C2 is unpinned. Outside C1 and C2, this file does not pin three sentences of `SKILL.md:70` that the rule depends on: "Only the user can accept it; no agent grants, extends or infers an acceptance", "It covers only the release it was given for…" and "An acceptance never covers…". Whether another test file pins them is **(unverified)**. That gap predates T801.

### 4. T801's question: comparing `B3_LINE_ADR_012` with ADR-012

The reading is right, and row B3 stays pinned.

- ADR-012 is immutable. Its row B3 (`ADR-012…md:51`) is the line without the C2 insertions, and its header (line 8) names ADR-015 as superseding B1 and B3 in part. ADR-015 row S6 says the slots "gain" items; nothing is withdrawn.
- `B3_LINE_ADR_012` (line 254) is `B3_LINE` with both insertions removed. I compared the result with `ADR-012…md:51` by reading: identical.
- `test_b1_and_b3_are_the_text_of_adr_012` (lines 589-593) requires it in ADR-012, so any change to the ADR-012 part of the live line fails there. The live line also fails `_hunk_errors` and `B3_CLAUSES`.
- The `assertNotEqual` at line 597 stops the two `replace` calls from silently doing nothing.
- A consistent change to a C2 constant and to the live line fails the ADR-015 count test.

### 5. C3, C4 and the other restatements

- **C3** `security-engineer.md:86`: unchanged and consistent. "is due by its remediation plan's deadline" reads as the review date under O1.
- **C4** `release-manager.md:43`: unchanged; it points to § Verdict Rules and copies no plan rule.

T801's pointer list, each read in the worktree:

| File:line | What it says | Consistent |
|---|---|---|
| `agents/tech-lead.md:85`, `:100`, `:114` | merge-gate conditions: "remediation plan (owner, fix, deadline)" | Yes; not the release acceptance |
| `commands/code-review.md:51`, `:53` | same, merge gate and waiver | Yes |
| `commands/security-audit.md:45`, `:69` | MEDIUM needs a plan before merge | Yes |
| `skills/receiving-code-review/SKILL.md:86` | escalation does not lift a MEDIUM's plan | Yes |
| `skills/code-review/SKILL.md:155` | waiver does not lift a MEDIUM's plan | Yes |
| `skills/validation-gates/SKILL.md:55` | template line pointing to § Verdict Rules | Yes |
| `docs/wiki/severity-and-grade-scales.md:34` | pointer to § Verdict Rules, cites ADR-011 only | Yes; the ADR citation was already incomplete after ADR-012 |

None of these copies the acceptance rule, so none needed an edit. Rule 1 applies only to the user's acceptance at the Release gate; the merge-gate texts still require a fix, which is correct.

My own search of `implementation/knowledge/{agents,commands,skills,instructions}` found four more places not in T801's list. The search ran in the main checkout, whose unedited files are the same.

- `skills/validation-gates/SKILL.md:120` and `:142`, `commands/prepare-release.md:64`, `agents/release-manager.md:43`: all are pointers to § Verdict Rules and are consistent.
- `SKILL.md:120` lists, as a gate input, each accepted and unfixed MEDIUM "with the release each acceptance was given for", but not the old plan's deadline, which O5 now needs (SEC-T802-04).
- `docs/releases/_template.md:88` is a pointer to the Conditions format and copies no line, so it needs no C2 text. This closes that open item of ADR-015 (`ADR-015…md:133`).

### 6. The 7 declared root-drift paths

Yes. `tests/_baselines/root-install-drift.json:85-93` lists the validation-gates skill under `.claude`, `.cline`, `.github` and `.opencode` (4) and the release-manager agent under `.claude`, `.github` and `.opencode` (3). They are the root counterparts of `VG_MIRRORS` and `RM_MIRRORS` (test lines 61-75). That Cline has no agent projection is the test's statement (lines 59-60), backed by `ProjectionList` passing in the orchestrator's run; I did not open `cline.json`. That `--print-drift` prints exactly these 7 is the orchestrator's evidence (brief § 6).

## Findings

| Id | Grade | File:line | Description | Recommendation |
|---|---|---|---|---|
| SEC-T802-01 | SECURITY:LOW | `implementation/knowledge/skills/validation-gates/SKILL.md:70` (from `ADR-015…md:124`) | O3 is carried in its short form. The skill does not say what the outcome covers (whether a harness fix now exists, whether the outside closer is still right), or that a fix which now exists is a changed fix needing a new acceptance (`ADR-015…md:78`). An owner could record "reviewed" and nothing else. | Track. At the next edit of § Verdict Rules add "(whether a harness fix now exists and whether the outside closer is still right; a fix that now exists is a changed fix)". ADR-015 allows a wording change that keeps the rule. |
| SEC-T802-02 | SECURITY:LOW | `implementation/knowledge/skills/validation-gates/SKILL.md:70` | "It covers only the release it was given for" now follows the Rule 2 sentence, so "It" can be read as only the new acceptance after a passed deadline. The rule holds through `release-manager.md:43`, but the skill is the one definition. This file does not pin the sentence. | Track. Change "It covers" to "An acceptance covers", and pin that sentence and "Only the user can accept it; no agent grants, extends or infers an acceptance". |
| SEC-T802-03 | SECURITY:LOW | `implementation/knowledge/skills/validation-gates/SKILL.md:70` (from `ADR-015…md:124`; § Decision lines 72 and 79) | The Security Engineer's confirmation (O4) stands after the semicolon, outside "only when". Neither the skill nor ADR-015 says that an acceptance does not hold when the review is missing or does not confirm. The control today is the C2 slot and the Release gate's check of the record. | Track. Wording candidate: "…and sets a review date, and only when the Security Engineer's review of the finding confirms…". This needs the user's word, since it makes O4 a fourth validity condition. |
| SEC-T802-04 | SECURITY:LOW | `implementation/knowledge/skills/validation-gates/SKILL.md:120` (line number from the main checkout; surrounding section not read) | The gate-input line names "the release each acceptance was given for" but not the old plan's deadline. O5 needs that date in the Conditions line, so the release manager has to find it elsewhere. | Track. Add "and its plan's deadline" to that input line at the next edit. |

No finding is CRITICAL, HIGH or MEDIUM. No Immutable Security Constraint is touched. No control that `security-guidelines.md` requires is omitted, removed, disabled or weakened.

## What I did not verify

- **Tests and gates**: I ran nothing. "26 OK", all gates exit 0 and the `--print-drift` output are the orchestrator's evidence (brief § 6).
- **The diff itself**: I read the files at the branch tip, not the diff. That no path under `tests/golden/` and no top-level platform folder changed is the orchestrator's evidence.
- **Mirrors and registry**: I did not open the four skill mirrors or three agent mirrors under `implementation/.<platform>/`, or `registry/index.json`. `sync.mjs --check` and `generate-registry.py --check` exit 0 per the orchestrator.
- **ADR-011**: not opened (budget). Its sentences are taken from ADR-015 rows S1 to S3.
- **plan-155, plan-156, `task-T801.md`**: not opened. The user's words are taken from ADR-015's header and § The user's answers.
- **ADR-012's header note** (`ADR-012…md:8`): present. Which commit added it is **(unverified)**; ADR-015 § Follow-ups prescribes it.
- **`docs/wiki/`**: my search reported no file searched, so only `severity-and-grade-scales.md:34` was read. Other wiki restatements are **(unverified)**.
- **`skills/release-workflow/SKILL.md:113`** (ADR-015's list): not read. My search found no hit in that file for the lapse or no-fix wording, so it does not copy those sentences.
- **Other test files** pinning the unpinned sentences of `SKILL.md:70`: **(unverified)**.
- **The brief's "`MUTATIONS` 44 to 73"**: by my count the T801 entries are entries 26 to 54 of 73 (lines 690-738). A note for the orchestrator, not a finding.

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 4 | 0 | 4 |

### Justification
C1 and C2 are ADR-015's text, in the places the ADR names. Both rules and O1 to O7 are present; nothing is wider than ruled. ADR-011 and ADR-012 are not weakened (answer 2). Every element of C1 and C2 is pinned and has a mutation (answer 3). ADR-012's row B3 stays pinned (answer 4). The pointers are consistent (answer 5). The drift declaration is exact (answer 6). SEC-T802-01 to -04 are LOW and are tracked as technical debt in the next tracked-debt register; PASS depends on that tracking.

### OWASP Coverage
The change is rule text and text pins, with no executable product code.

| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes (who may accept; no agent path) | 0 |
| A02: Cryptographic Failures | No (not applicable) | 0 |
| A03: Injection | No (not applicable) | 0 |
| A04: Insecure Design | Yes (rule completeness, abuse of "none possible", serial lapse) | 4 |
| A05: Security Misconfiguration | No (not applicable) | 0 |
| A06: Vulnerable Components | No (no dependency change) | 0 |
| A07: Auth Failures | No (not applicable) | 0 |
| A08: Data Integrity Failures | Yes (pins, ADR text match, drift declaration) | 0 |
| A09: Logging & Monitoring | Yes (record in the verdict and the register) | 0 |
| A10: SSRF | No (not applicable) | 0 |

## Gate Verdict

**Gate:** security
**Verdict:** PASS
**Conditions:** none. LOW findings SEC-T802-01 to SEC-T802-04 go to the next tracked-debt register.

## Task completion

- **Artifact**: this file, `docs/artifacts/security-review-t802-adr-015-apply-v1.md` (the orchestrator commits it).
- **Acceptance criteria**: each finding has a file and line; each claim not verified is marked or listed above.
- **Follow-ups**: SEC-T802-03's wording change needs the user's word. SEC-T802-01, -02 and -04 are wording edits within ADR-015's "may adjust the wording but not the rule".
- **Blockers**: none.
