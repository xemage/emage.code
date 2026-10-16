# Artifact: security-gate-alignment-v2.md

> Filename: `security-gate-alignment-v2.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T586 (P2, judgment tier, decision only), second version
- **Created**: 2026-10-08
- **Based on:**
  - `docs/artifacts/security-gate-alignment-v1.md`. Its analysis stands and is referenced, not repeated: §1 (reading
    rules), §§3–6 (the D5 records for FU-6(a), FU-6(b), FU-6(c) and FU-7), §9 (no P5 escalation) and §10 (parked
    observations O1–O4).
  - `docs/artifacts/security-review-security-gate-alignment-v1.md`, the Security Engineer's review of v1:
    **CONDITIONAL_PASS**. The orchestrator relayed the conditions and adopted every one of them (C1, C2) and every LOW
    recommendation (SEC-T586-03 to SEC-T586-06), plus the three formerly optional items. I apply the relayed wording
    verbatim. I did not read the review record itself, because the orchestrator is committing it under that name.
  - The orchestrator's verification of v1:
    - all 45 cited quotes are verbatim;
    - each of the five v1 Before anchors occurs exactly once (`grep -cxF` = 1);
    - `implementation/` at `cf36a17` is identical to `a9c4f04`;
    - no other file under `implementation/knowledge/` restates the SLA rows or the `:86` sentence;
    - no non-golden test asserts the amended text.

    This closes v1 §11 items 1, 2, 4 and 5.
  - `docs/tasks/task-T586.md`, `docs/plans/plan-103-security-gate-alignment.md`,
    `docs/decisions/ADR-008-knowledge-document-authority.md` and `docs/artifacts/conditional-pass-semantics-v4.md`, as in
    v1.
- **Supersedes**: `security-gate-alignment-v1.md`. v1 stays unchanged. **v2 alone is the implementation input.**
- **Decision references**: as v1 (ADR-008 Step A for every subject; ADR-008 § Scope, P39 Q3/Q7, for FC1's wording;
  ADR-007 §5), plus the Security Engineer review (SEC-T586-01 to SEC-T586-07).

## 0. Method and limits

- **No shell.** Line numbers are at `a9c4f04`, which equals `cf36a17` under `implementation/` (orchestrator-verified).
- **New anchors.** v2 adds two anchors, FC3 at `security-engineer.md:153` and FD1 at `validation-gates/SKILL.md:129`.
  I read both files in full, and each anchor line occurs once. A `grep -cxF` is still owed for those two (§7, item 1).
- **Golden.** I opened nothing new under `tests/golden/`. I never opened `tests/golden/held-out/`. I read no `.env*`,
  credential or key file.
- **Encoding.** `§` is U+00A7 and `—` is U+2014. No emoji is introduced. Each four-backtick fence holds one
  Before/After pair. Apply each edit by its Before text, not by line number.

## 1. Change log against v1

These are exactly the changes the orchestrator listed. Everything else in v1's edits is unchanged.

| # | Source | Edit | Change |
|---|---|---|---|
| 1 | **C1**, SEC-T586-01 (`SECURITY:MEDIUM`) | FA1 | "Each SLA is the latest point by which the fix is due." is kept. Everything after it is replaced by the reviewer's text, verbatim. The constraint-breach and omitted-control classes now block merge whatever the SLA. The earliest-deadline rule is limited to "every other finding" |
| 2 | **C2**, SEC-T586-02 (`SECURITY:MEDIUM`) | FB1 | Its second sentence is replaced by the reviewer's text, verbatim: "its tier never lowers that", and the two classes yield FAIL whatever their tier. This closes the relaxation concern raised in v1 §4.3 |
| 3 | SEC-T586-03 (LOW) | F7 | "Escalation never lifts a `FAIL` caused by a security finding that" becomes "Escalation never lifts a `FAIL` with a security finding among its causes that" |
| 4 | SEC-T586-04 (LOW) | **FC3, new** | `security-engineer.md:153`: `conditional_pass` and `pass` both require that item 2 does not apply. `pass` also requires that no medium finding remains and that each low finding is tracked as technical debt. D5 record in §2.1 |
| 5 | SEC-T586-05 (LOW) | FC1 | (a) "severity vulnerability" becomes "severity finding". (b) "is graded at its own severity." becomes "is graded at its own severity and tracked like any other finding of that grade." |
| 6 | SEC-T586-06 (LOW) | **FD1, new** | `validation-gates/SKILL.md:129`: the FAIL-handling step also addresses every security finding that § Verdict Rules excludes from CONDITIONAL_PASS. D5 record in §2.2 |
| 7 | Reviewer recommendation | FC1, FC2, F7 | FC1's constraint-breach clause, FC2 and F7's second sentence are **no longer optional**. Their text is unchanged from v1 |
| 8 | SEC-T586-07 (a), (b) | §5 | Recorded as parked observations only. No edit |

## 2. D5 records for the new edits

v1's four D5 records stand unchanged in their steps and outcomes. C1, C2, SEC-T586-03 and SEC-T586-05 only tighten the
wording of their amendments, and none of them changes a Step A result. The two new edits follow.

### 2.1 FC3: `security-engineer.md:153` (SEC-T586-04)

| Field | Content |
|---|---|
| **Subject (D3)** | A criterion: what the Security-gate audit needs before it may return `conditional_pass` or `pass`. |
| **Clauses** | `security-engineer:153` "3. `conditional_pass` only when medium/low findings have owners and remediation windows." `:151` "1. Every audit must end with a gate verdict: `pass`, `conditional_pass`, or `fail`." The file states no `pass` criterion. Tier 1 `security-guidelines:183` "4. `MEDIUM` findings must have a remediation plan before merge" and `:184` "5. `LOW` findings are tracked as technical debt". `validation-gates:66` "\| **PASS** \| No critical or high findings, no security finding graded medium, and none of the security findings excluded below. …" |
| **Step A** | Holds. `:153` is a necessary condition for `conditional_pass` and bars nothing stricter (v1 §5.2). The file's silence on `pass` permits what `vg:66` forbids, but forbids nothing that `vg:66` requires. One emitter, the Security Engineer, can meet both: no PASS while a security medium remains. |
| **Step that fired** | **A (P3a): jointly satisfiable.** FC3 is a note that makes the existing requirements explicit where the executor reads them (`sg:183`, `vg:66`). |
| **Declared scope relied on** | None. |
| **Amendment** | FC3 (§3). It adds necessary conditions only: "item 2 does not apply" to `conditional_pass`, and a `pass` criterion. It removes no condition. |
| **Maturity** | Not relied on. |

### 2.2 FD1: `validation-gates/SKILL.md:129` (SEC-T586-06)

| Field | Content |
|---|---|
| **Subject (D3)** | A step: which findings the assignee must address after a `FAIL`, before re-evaluation. |
| **Clauses** | `validation-gates:129` "2. The assignee addresses all critical and high findings." Same file, `:68` "\| **FAIL** \| Any critical finding unresolved, OR any high finding without mitigation, OR any security finding excluded below. …" and `:70` "… The same FAIL rule, with no waiver, holds for any security control `security-guidelines.md` requires for the code under review that is omitted, removed, disabled or weakened, tagged or not …". Tier 1 `security-guidelines:153` "… cannot be overridden by any agent, configuration, or runtime decision:". |
| **Step A** | Holds. `:129` does not forbid addressing more. A gate re-run (`:131`) on an unaddressed excluded finding returns FAIL again under `:68`/`:70`, so no input carries two values. The gap is again silence: an excluded finding graded medium is not "critical and high". |
| **Step that fired** | **A (P3a).** The tension between `:129` and `:68`/`:70` lies within one file. That is the same-file coherence practice ADR-008 § Scope leaves outside the ADR. FD1 is the note that states the relationship either way. |
| **Declared scope relied on** | None. |
| **Amendment** | FD1 (§3). It only adds to what must be addressed. |
| **Maturity** | Not relied on. |

## 3. Final edits (complete; v2 alone is the implementation input)

| # | Edit | File | Anchor (full line, at `a9c4f04`) |
|---|---|---|---|
| 1 | FA1 | `implementation/knowledge/agents/security-engineer.md` | `:84`, the `LOW` SLA row |
| 2 | FC1 | same | `:152`, Security Gate Protocol item 2 |
| 3 | FC3 | same | `:153`, Security Gate Protocol item 3 |
| 4 | FC2 | same | `:222`, Rails Failure mode |
| 5 | FB1 | `implementation/knowledge/skills/validation-gates/SKILL.md` | `:81`, the `low` severity row |
| 6 | FD1 | same | `:129`, Handle a FAIL Verdict step 2 |
| 7 | F7 | `implementation/knowledge/skills/receiving-code-review/SKILL.md` | `:86`, the file's last line |

All anchors are distinct full lines, so applying one edit cannot disturb another's anchor. FC1 and FC3 sit on adjacent
lines and are separate edits.

### FA1: `security-engineer.md`, after `:84`

````
Before:
| **LOW** | Minor issue, best-practice deviation | Fix within next sprint |

After:
| **LOW** | Minor issue, best-practice deviation | Fix within next sprint |

Each SLA is the latest point by which the fix is due. It applies together with `security-guidelines.md` § Security Review Workflow and skill `validation-gates` § Verdict Rules, and never permits a merge or a release that they block. A CRITICAL or HIGH finding blocks merge until it is resolved, whatever its SLA; so does any breach of an Immutable Security Constraint in `security-guidelines.md`, and any security control that `security-guidelines.md` requires for the code under review that is omitted, removed, disabled or weakened, whatever its grade. For every other finding, where they set an earlier point, the earlier point is the deadline: a MEDIUM finding has its remediation plan (owner, fix, deadline) before merge, and its fix is due by its SLA or under that skill's track rule, whichever is earlier; a LOW finding is also tracked as technical debt.
````

### FC1: `security-engineer.md:152`

````
Before:
2. `fail` when any unresolved critical or high severity vulnerability remains.

After:
2. `fail` when any unresolved critical or high severity finding remains, when any Immutable Security Constraint in `security-guidelines.md` is breached, or when any security control that `security-guidelines.md` requires for the code under review is omitted, removed, disabled or weakened, tagged or not, whatever its grade (skill `validation-gates` § Verdict Rules). A required control missing only from code outside the change under review is graded at its own severity and tracked like any other finding of that grade. A change that adds or alters code which the missing control should protect is code under review for that control. With no change under review (for example a full-project `/security-audit`), the whole project is the code under review.
````

### FC3: `security-engineer.md:153`

````
Before:
3. `conditional_pass` only when medium/low findings have owners and remediation windows.

After:
3. `conditional_pass` only when item 2 does not apply and medium/low findings have owners and remediation windows; `pass` only when item 2 does not apply, no medium finding remains, and each low finding is tracked as technical debt (skill `validation-gates` § Verdict Rules).
````

### FC2: `security-engineer.md:222`

````
Before:
**Failure mode**: Any unresolved CRITICAL or HIGH finding forces a `fail` gate verdict; after two failed remediation cycles on the same high-risk finding, the audit escalates to the orchestrator and release manager rather than re-auditing indefinitely.

After:
**Failure mode**: Any unresolved CRITICAL or HIGH finding, any Immutable Security Constraint breach, or any required security control omitted, removed, disabled or weakened in the code under review forces a `fail` gate verdict (§ Security Gate Protocol); after two failed remediation cycles on the same high-risk finding, the audit escalates to the orchestrator and release manager rather than re-auditing indefinitely.
````

### FB1: `validation-gates/SKILL.md`, after `:81`

````
Before:
| `low` | Minor style issue, optimization opportunity, or suggestion. |

After:
| `low` | Minor style issue, optimization opportunity, or suggestion. |

A security finding (§ Verdict Rules) takes the tier its grade names on the `security-guidelines.md` § Security Review Workflow scale: `SECURITY:CRITICAL` is `critical`, `SECURITY:HIGH` is `high`, `SECURITY:MEDIUM` is `medium` and `SECURITY:LOW` is `low`. What a security finding of each grade requires is stated in § Verdict Rules, and its tier never lowers that: a breach of an Immutable Security Constraint, or a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, yields FAIL whatever its tier; any other security finding graded medium needs its remediation plan before merge, and any other graded low is tracked as technical debt.
````

### FD1: `validation-gates/SKILL.md:129`

````
Before:
2. The assignee addresses all critical and high findings.

After:
2. The assignee addresses all critical and high findings and every security finding that § Verdict Rules excludes from CONDITIONAL_PASS.
````

### F7: `receiving-code-review/SKILL.md:86`

````
Before:
`FAIL` findings block merge until resolved or escalated via blocker protocol.

After:
`FAIL` findings block merge until resolved or escalated via blocker protocol. Escalation never lifts a `FAIL` with a security finding among its causes that skill `validation-gates` § Verdict Rules and skill `code-review` § Review as Validation Gate exclude from waiver (a security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH`, a breach of an Immutable Security Constraint, or a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened): such a `FAIL` blocks merge until the finding is resolved (`security-guidelines.md` § Security Review Workflow: "`CRITICAL` and `HIGH` findings block merge until resolved"). Nor does escalation lift a `SECURITY:MEDIUM` finding's remediation plan (owner, fix, deadline), which is recorded as a tracked condition before merge (`security-guidelines.md` § Security Review Workflow).
````

## 4. Per-edit statements

**None of the seven edits is upward** (ADR-008 Validation 4). Every target is an agent or a skill. No edit touches
`security-guidelines.md`, `AGENTS.md`, any command (including `/security-audit`), `tests/golden/**`, or any file other
than the three named.

| Edit | Relaxes a check? (ADR-007 §5) | Security | Interaction with N1 (`validation-gates:72`) | Interaction with `security-engineer:177` (`owner=…, remediation=…, deadline=…`) |
|---|---|---|---|---|
| **FA1** | No. It removes no SLA. It adds tier 1's merge block and P39's two grade-independent classes, and earlier deadlines for every other finding | It tightens. C1 closes the gap where a breach or omitted control graded MEDIUM fell under the "earliest deadline" branch instead of blocking | None in text. N1 covers verdict criteria at two gates; FA1 covers due points. It does not rely on N1 or extend it | `deadline=` carries one value, the earliest bound. A breach or omitted control is never a Condition; it blocks |
| **FC1** | No. It only adds fail triggers. "severity finding" is broader than "severity vulnerability" (SEC-T586-05a). The scope sentences are P39 Q3's own limit and do not narrow the critical/high trigger (Q8 stands) | It carries P39 §1.7 and Q7 into the Security gate's executor. SEC-T586-05b adds "tracked" | It aligns the Security gate's own criteria with § Verdict Rules by citation. N1's "this note covers two of the gates" stays accurate | The excluded classes go under `### Blockers (if FAIL)` (`:179–180`), never under `### Conditions` |
| **FC3** | No. It adds necessary conditions to `conditional_pass` and introduces a `pass` criterion. It removes none | It makes `sg:183` and `vg:66` explicit at the executor: no PASS while a security medium remains | It matches N1's principle (no criteria set admits a laxer verdict) but does not rely on N1 | `conditional_pass` still needs owners and windows (`owner=`, `deadline=`). A `pass` needs no Conditions entry: lows are tracked as debt, not as conditions |
| **FC2** | No. It mirrors FC1 | Same as FC1 | None | None |
| **FB1** | No. C2's "its tier never lowers that" removes v1 §4.3's counter-reading concern on the text itself. The two grade-independent classes yield FAIL whatever their tier | It tightens, or restates `:70` | It sits below N1 and changes no criteria set. N1's "No set of criteria, the rules above included, makes another less strict" is unaffected and is echoed | Indirect. Security-engineer counts map one-to-one onto the tiers. FAIL classes are Blockers |
| **FD1** | No. It only adds findings the assignee must address | It closes the gap where an omitted control graded medium was outside "critical and high" in the FAIL procedure | Consistent: a FAIL that any applicable criterion requires must be cleared before re-evaluation | None. These findings are Blockers, not Conditions |
| **F7** | No. The first sentence of `:86` is unchanged. F7 only removes escalation as an exit. SEC-T586-03 widens it to any FAIL with an excluded finding *among* its causes | It tightens. The second sentence keeps the MEDIUM plan | None. F7 governs the implementer's response | The MEDIUM plan it protects is the Conditions entry. Escalation leaves it in place |

### 4.1 Golden coupling (each edit: quote / fixture / result)

| Edit | Open case | Quote | Fixture | Result |
|---|---|---|---|---|
| FA1, FC1, FC2, FC3 | `discover-skills-registry-grounded-recommendation` | No change | No change. Frozen registry snapshot plus frontmatter-only skill copies | No change. The check reads only `id` and `category` |
| F7 | same | No change | No change. The frozen copy holds lines 1–4 only | No change |
| FB1 | `validate-workflow-gate-verdict-sources` | No change. Its `brief.md` quotes only "Every gate MUST produce a verdict in this format" and the `**Gate:**` line | No change. Frozen at `7be9926`; it already lags the source since N1 | No change. `check()` reads only the fixture, and within `## Verdict Format` only "every gate must produce a verdict" and the first `**Gate:**` line. FB1 adds neither |
| FD1 | same | No change | No change (frozen) | No change. FD1 is under `## Procedures`, a different level-2 section that `_section(…, ("## Verdict Format",))` never reaches. `## Gate Types` is not touched. The case's Provenance mentions § Procedures › 3 only as history; FD1 edits › 2 |
| — | the three `security-audit-*` cases | Not applicable: `commands/security-audit.md` is not amended | — | — |

Golden coupling was not a reason for any ruling.

## 5. Parked observations

- **O1–O4**: unchanged from v1 §10. O2 (the `/security-audit` VERDICT block has no Conditions field) stays with FU-5,
  and no command change is proposed.
- **SEC-T586-07 (a) and (b)**: recorded as parked observations only, with no edit, as the orchestrator directed. **The
  text of these two items was not relayed to me.** I do not restate them, so that I do not misquote them. Their wording
  is in `docs/artifacts/security-review-security-gate-alignment-v1.md`.

## 6. Escalations and blockers

- **P5 escalations:** none (v1 §9). Nothing is optional any more, so no choice is left for the user.
- **Blockers:** none.

## 7. Implementation checks

1. **Each Before matches once.** `grep -cxF` on each of the seven Before lines must return **1** in its file before
   editing. The orchestrator verified five; FC3 (`security-engineer.md:153`) and FD1 (`validation-gates/SKILL.md:129`)
   are new. I checked them only by reading **(unverified by grep)**.
2. **Regenerate.** Run `node implementation/scripts/sync.mjs --root implementation` and
   `python3 implementation/scripts/generate-registry.py`, each followed by `--check`. Declare the root drift as
   `--print-drift` reports it: up to 3 files × 7 platforms = 21 paths **(unverified)**.
3. **Golden and maturity.** `scripts/scorecard.py --check` must match the current baseline. `check-maturity.py --root
   implementation` must report 0 failing. No protected-path grant is needed.
4. **Hit counts.** All counts are case-sensitive, fixed-string and per file, in the file named, after all seven edits.
   - **Lines** = `grep -cF` (lines containing the phrase).
   - **Occurrences** = `grep -oF … | wc -l`.
   - "Before" is the count on `a9c4f04`.

   No phrase below is a substring that an After text negates or splits, except the three rows marked **must be 0**,
   which test that old wording is gone.

| # | Phrase | File | Before | After: lines | After: occurrences | Source |
|---|---|---|---|---|---|---|
| 1 | `Each SLA is the latest point by which the fix is due` | `security-engineer.md` | 0 | 1 | 1 | FA1 |
| 2 | `whatever its SLA` | `security-engineer.md` | 0 | 1 | 1 | FA1 |
| 3 | `For every other finding, where they set an earlier point` | `security-engineer.md` | 0 | 1 | 1 | FA1 |
| 4 | `whatever its grade` | `security-engineer.md` | 0 | 2 | 2 | FA1, FC1 (different lines) |
| 5 | `omitted, removed, disabled or weakened` | `security-engineer.md` | 0 | 3 | 3 | FA1, FC1, FC2 |
| 6 | `critical or high severity finding remains` | `security-engineer.md` | 0 | 1 | 1 | FC1 |
| 7 | `severity vulnerability remains` | `security-engineer.md` | 1 | **must be 0** | 0 | old FC1 wording gone |
| 8 | `graded at its own severity and tracked like any other finding of that grade` | `security-engineer.md` | 0 | 1 | 1 | FC1 |
| 9 | `adds or alters code which the missing control should protect` | `security-engineer.md` | 0 | 1 | 1 | FC1 |
| 10 | `the whole project is the code under review` | `security-engineer.md` | 0 | 1 | 1 | FC1 (not in FC2) |
| 11 | `only when item 2 does not apply` | `security-engineer.md` | 0 | **1** | **2** | FC3: once for `conditional_pass` and once for `pass`, **on the same line** |
| 12 | `(skill \`validation-gates\` § Verdict Rules)` | `security-engineer.md` | 0 | 2 | 2 | FC1, FC3. FA1's mention has no parentheses |
| 13 | `(§ Security Gate Protocol)` | `security-engineer.md` | 0 | 1 | 1 | FC2 |
| 14 | `takes the tier its grade names` | `validation-gates/SKILL.md` | 0 | 1 | 1 | FB1 |
| 15 | `and its tier never lowers that` | `validation-gates/SKILL.md` | 0 | 1 | 1 | FB1 |
| 16 | `yields FAIL whatever its tier` | `validation-gates/SKILL.md` | 0 | 1 | 1 | FB1 |
| 17 | `omitted, removed, disabled or weakened` | `validation-gates/SKILL.md` | 1 (`:70`) | 2 | 2 | `:70` plus FB1 |
| 18 | `every security finding that § Verdict Rules excludes from CONDITIONAL_PASS` | `validation-gates/SKILL.md` | 0 | 1 | 1 | FD1 |
| 19 | `Verdict Rules: for example` | `validation-gates/SKILL.md` | 0 | **must be 0** | 0 | v1's FB1 wording must not land |
| 20 | `Escalation never lifts a \`FAIL\` with a security finding among its causes` | `receiving-code-review/SKILL.md` | 0 | 1 | 1 | F7 |
| 21 | `caused by a security finding` | `receiving-code-review/SKILL.md` | 0 | **must be 0** | 0 | v1's F7 wording must not land |
| 22 | `Nor does escalation lift` | `receiving-code-review/SKILL.md` | 0 | 1 | 1 | F7 |

**Notes on the counts:**
- **Rows 12 and 20 contain backticks.** The backslashes before them in the table are Markdown escapes, not part of the
  phrase. The literal phrases are (skill `validation-gates` § Verdict Rules) and Escalation never lifts a `FAIL` with a
  security finding among its causes.
- **Row 7** is the only "must be 0" phrase that exists before the edits. It is a full-word tail ("vulnerability
  remains") that FC1's After does not contain.
- **No count for FD1's old line as a substring.** "The assignee addresses all critical and high findings" survives
  inside FD1's After, so a substring count would stay 1 and prove nothing. Check FD1 instead by row 18, and by
  `grep -cxF '2. The assignee addresses all critical and high findings.'` returning **0** after the edit (a whole-line
  match).
- **Rows 4, 5, 9 and 10 against P39.** P39's FU-1 table (`conditional-pass-semantics-v4.md` §9) counted these phrases
  in other files. After v2, each of those phrases also occurs in `security-engineer.md`. That is expected and is not a
  regression.

## 8. Summary

| Subject | Step | Outcome | Edits | Files |
|---|---|---|---|---|
| FU-6(a): SLA table | A | Jointly satisfiable. SLAs are latest deadlines; tier-1 merge blocks and the P39 classes govern regardless (C1) | FA1 | `agents/security-engineer.md` |
| FU-6(b): severity tiers | A | Not misaligned with tier 1. The tier is the `SECURITY:*` grade and never lowers a requirement (C2) | FB1 | `skills/validation-gates/SKILL.md` |
| FU-6(c): Security Gate Protocol | A | Jointly satisfiable. The P39 classes and Q7 are named; `conditional_pass` and `pass` require that item 2 does not apply | FC1, FC2, FC3 | `agents/security-engineer.md` |
| FU-7: escalation | A | Jointly satisfiable. Escalation never lifts a FAIL with an excluded finding among its causes, nor a MEDIUM plan | F7 | `skills/receiving-code-review/SKILL.md` |
| SEC-T586-06: FAIL handling | A (same-file note) | The assignee also addresses the excluded security findings | FD1 | `skills/validation-gates/SKILL.md` |

- **Totals:** seven edits in three files. No command and no tier-1 file is touched. No golden quote, fixture or result
  changes. No P5 escalation. No blockers.
- **Maturity** is not relied on anywhere.
- **Still unverified:**
  - `grep -cxF` for the two new anchors (§7.1);
  - the root-drift count;
  - tier-1 byte identity at `dd7703b` (v1 §11.3);
  - that the three `security-audit-*` cases quote only the command (v1 §11.7; the orchestrator's pre-computation).
