# Artifact: security-finding-grading-and-owasp-run-v2.md

> Filename: `security-finding-grading-and-owasp-run-v2.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T588 (P2, judgment tier, decision only), second version
- **Created**: 2026-10-08
- **Based on:**
  - `docs/artifacts/security-finding-grading-and-owasp-run-v1.md`. Its analysis stands and is referenced, not repeated:
    - §2, the D5 record for (a);
    - §3, the D5 record for (b);
    - §4, escalations Q-a and Q-b;
    - §6, observations O1–O3 and brief corrections C1–C2.
  - The orchestrator's verification of v1:
    - all 40 cited quotes are verbatim (corpus check);
    - each of the six anchors is unique (`grep -cxF` = 1);
    - O1 is confirmed at `/security-audit:42–46`.

    This closes v1's unverified items for the anchors and their uniqueness.
  - **The user's decisions of 2026-10-08**, relayed by the orchestrator. The option labels are verbatim:
    - Q-a: **"Pointer (Recommended)"**, that is, option A1 and edit E-A1;
    - Q-b: **"Tech Lead per MR (Recommended)"**, that is, option B1 and edits E-B1a and E-B1b;
    - O1: **"Rule it next (Recommended)"**. O1 is a separate task and is only recorded here.
  - **The Security Engineer's review** of E-A1, E-B1a and E-B1b: **CONDITIONAL_PASS**, findings SEC-T588-01 to
    SEC-T588-05. The record is `docs/artifacts/security-review-security-finding-grading-v1.md`; the orchestrator commits
    it under that name. The orchestrator relayed the reviewer's text and adopted every item, and I apply it verbatim. I
    did not read the review record itself.
  - The floor clauses, which the orchestrator confirmed and I re-read at `7ec903a` (worktree `51a4efb`, whose
    `implementation/` tree is identical):
    - `poc-security-engineer.md:21` (§ Behavior): "**Severity floor:** never grade any of these below `SECURITY:HIGH`:
      …";
    - `poc-orchestrator.md:76` (§ Security Findings): "**A secret not yet committed** is still blocking
      (`SECURITY:HIGH` at least). …"
  - `docs/tasks/task-T588.md`; `docs/plans/plan-104-security-finding-grading-and-owasp-run.md`;
    `docs/decisions/ADR-008-knowledge-document-authority.md`; `docs/artifacts/security-gate-alignment-v2.md` and
    `docs/artifacts/conditional-pass-semantics-v4.md`. These are inputs, as in v1, and none of them is reopened.
- **Supersedes**: `security-finding-grading-and-owasp-run-v1.md`. v1 stays unchanged. **v2 alone is the implementation
  input.**
- **Decision references**: ADR-008 Step A (P3a) for both subjects (v1 §§2.5, 3.5); ADR-008 P5, decided by the user
  (§1); ADR-007 §5 (never relax a check); SEC-T588-01 to SEC-T588-05.

## 0. Method and limits

- **No shell.** Line numbers are at `7ec903a`. Apply each edit by its Before text, not by its line number.
- **Golden.** No file under `tests/golden/` was opened beyond those v1 lists. I never opened `tests/golden/held-out/`.
  I read no `.env*`, credential or key file.
- **Encoding.** `§` is U+00A7 and `—` is U+2014. No emoji is introduced. Each four-backtick fence holds exactly one
  Before/After pair.

## 1. Decisions recorded

| Item | Escalated in | Decision (verbatim label) | Effect |
|---|---|---|---|
| **Q-a**: grading a security finding raised by an executor other than the Security Engineer | v1 §4.1 (P5) | **"Pointer (Recommended)"** | A1 is chosen. E-A1 is applied, as amended by SEC-T588-01 and SEC-T588-02 (§3). A2 and A3 are not chosen, so E-A2a and E-A2b are dropped |
| **Q-b**: who runs the per-MR OWASP checklist (`sg:180`) | v1 §4.2 (P5) | **"Tech Lead per MR (Recommended)"** | B1 is chosen. E-B1a is applied, as amended by SEC-T588-03 to SEC-T588-05, and E-B1b is applied unchanged (§3). B2 and B3 are not chosen, so E-B2a and E-B2b are dropped |
| **O1**: two Security Engineer grade-definition sets | v1 §6 | **"Rule it next (Recommended)"** | Scheduled as a separate ruling and only recorded here (§6). No edit in this change |

Both P5 escalations are now decided. Under ADR-008 § Scope ("A question already settled by … a recorded user decision.
That decision governs, and documents are amended to it."), the hold of v1 (P5 § Form 3) is lifted for the chosen edits.

## 2. Change log against v1

| # | Source | Edit | Change |
|---|---|---|---|
| 1 | User, Q-a | E-A1 | Chosen. E-A2a and E-A2b are dropped |
| 2 | **SEC-T588-01** (`SECURITY:MEDIUM`, condition C1) | E-A1 | A sentence is appended verbatim: "No grade so given is lower than a minimum grade set elsewhere for that kind of finding (…)". The highest-fit rule can no longer be read as overriding a severity floor |
| 3 | **SEC-T588-02** (LOW) | E-A1 | A sentence is appended verbatim: "Nor does this paragraph lift an earlier deadline that the executor's own documents set (…)" |
| 4 | User, Q-b | E-B1a, E-B1b | Chosen. E-B2a and E-B2b are dropped |
| 5 | **SEC-T588-03, -04, -05** (LOW) | E-B1a | v1's After item is replaced, verbatim. The review must state whether the MR touches security-sensitive code. Each OWASP category's result is noted. § Severity Definitions is cited. The run does not replace the Security gate |
| 6 | — | E-B1b | Unchanged from v1 |
| 7 | — | Hit counts (§5.3) | The A2 and B2 rows are removed. `Severity floor` in `vg` (0 → 1) is added, along with rows for the new sentences. Every row states whether it counts lines or occurrences |
| 8 | User, O1 | §6 | O1 is recorded with its exact quotes for the next ruling |

v1's D5 records (§§2–3) stand in their steps and outcomes. The reviewer's items only tighten the wording of the chosen
amendments. None of them changes a Step A result.

## 3. Final edits (complete; v2 alone is the implementation input)

| # | Edit | File | Anchor (full line, at `7ec903a`) | Placement |
|---|---|---|---|---|
| 1 | E-A1 | `implementation/knowledge/skills/validation-gates/SKILL.md` | `:83`, the FB1 paragraph in § Severity Definitions | A new paragraph after it |
| 2 | E-B1a | `implementation/knowledge/skills/code-review/SKILL.md` | `:39`, `- [ ] No hardcoded secrets or credentials`, in § Security (OWASP) | A new checklist item after it |
| 3 | E-B1b | `implementation/knowledge/agents/tech-lead.md` | `:38`, § Code Review item 4 | The line is replaced |

The orchestrator verified that each anchor is unique (`grep -cxF` = 1). The three anchors are in three different
files.

### E-A1: `validation-gates/SKILL.md`, new paragraph after `:83`

````
Before:
A security finding (§ Verdict Rules) takes the tier its grade names on the `security-guidelines.md` § Security Review Workflow scale: `SECURITY:CRITICAL` is `critical`, `SECURITY:HIGH` is `high`, `SECURITY:MEDIUM` is `medium` and `SECURITY:LOW` is `low`. What a security finding of each grade requires is stated in § Verdict Rules, and its tier never lowers that: a breach of an Immutable Security Constraint, or a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, yields FAIL whatever its tier; any other security finding graded medium needs its remediation plan before merge, and any other graded low is tracked as technical debt.

After:
A security finding (§ Verdict Rules) takes the tier its grade names on the `security-guidelines.md` § Security Review Workflow scale: `SECURITY:CRITICAL` is `critical`, `SECURITY:HIGH` is `high`, `SECURITY:MEDIUM` is `medium` and `SECURITY:LOW` is `low`. What a security finding of each grade requires is stated in § Verdict Rules, and its tier never lowers that: a breach of an Immutable Security Constraint, or a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened, yields FAIL whatever its tier; any other security finding graded medium needs its remediation plan before merge, and any other graded low is tracked as technical debt.

Whichever gate or executor raises a security finding, it is graded with the definitions in agent `security-engineer` § Findings Classification, whose CRITICAL, HIGH, MEDIUM and LOW are `SECURITY:CRITICAL`, `SECURITY:HIGH`, `SECURITY:MEDIUM` and `SECURITY:LOW`. A finding that fits more than one definition takes the highest grade it fits. Those definitions decide the grade only; what each grade requires is stated in § Verdict Rules and in the paragraph above. No grade so given is lower than a minimum grade set elsewhere for that kind of finding (for example `poc-security-engineer` § Behavior, "Severity floor", or `poc-orchestrator` § Security Findings for a secret not yet committed). Nor does this paragraph lift an earlier deadline that the executor's own documents set (for the Security Engineer, the SLA paragraph of that section).
````

### E-B1a: `code-review/SKILL.md`, new checklist item after `:39`

````
Before:
- [ ] No hardcoded secrets or credentials

After:
- [ ] No hardcoded secrets or credentials
- [ ] The review states whether the merge request touches security-sensitive code. For one that does: the `security-guidelines.md` § OWASP Top 10 Checklist Reference run against the change, all ten categories (A01 to A10), as that instruction's § Security Review Workflow step 1 requires, with each category's result (findings, none, or not applicable) noted in the review; each security finding recorded with its grade (skill `validation-gates` § Verdict Rules, § Severity Definitions). This run does not replace the Security gate before release (skill `validation-gates` § Gate Types).
````

### E-B1b: `tech-lead.md:38` (unchanged from v1)

````
Before:
4. **Security**: Input validation, SQL injection, XSS, auth checks

After:
4. **Security**: Input validation, SQL injection, XSS, auth checks; for a merge request touching security-sensitive code, the full OWASP Top 10 checklist (skill `code-review` § Security (OWASP); `security-guidelines.md` § Security Review Workflow, step 1)
````

## 4. Per-edit statements

**None of the three edits is upward** (ADR-008 Validation 4). E-A1 and E-B1a target skills and E-B1b targets an agent.
No edit touches any of the following: `security-guidelines.md`, `AGENTS.md`, any command (including `/code-review` and
`/security-audit`), `tests/golden/**`, `validation-gates` § Gate Types, or any file other than the three named.

| Edit | Authority | Relaxes a check? (ADR-007 §5) | Security |
|---|---|---|---|
| **E-A1** | The user's Q-a decision (ADR-008 § Scope), filling the gap v1 §2 found with Step A | No. It adds a definition source and a highest-fit rule. It changes no requirement per grade (§ Verdict Rules and FB1 govern). SEC-T588-01 forbids a grade below any existing floor. SEC-T588-02 keeps every earlier deadline | It removes the undefined-grade gap at every gate. Without SEC-T588-01, "takes the highest grade it fits" could, read alone, lead a PoC executor to grade a reachable injection or a credential in code below the `poc-security-engineer:21` floor. The appended sentence closes that reading. FB1's grade-independent FAIL classes stay untouched |
| **E-B1a** | The user's Q-b decision (ADR-008 § Scope), assigning `sg:180` step 1, which v1 §3 found had no owner | No. It adds a checklist item, a statement whether the MR is security-sensitive, a result for each category, and the grade. It removes none of the five existing items | The full Top 10 is now run on each MR touching security-sensitive code, where five items ran before. SEC-T588-03 makes "not security-sensitive" an explicit, reviewable statement instead of a silent skip. SEC-T588-04 makes the coverage auditable for each category. SEC-T588-05 keeps the Security Engineer's audit before release. The grade comes from E-A1 through § Severity Definitions |
| **E-B1b** | Same as E-B1a. `tl:29–30` says this section "summarizes" `code-review` | No. It adds a pointer | It keeps the Tech Lead's summary in line with `cr`. It names no criterion of its own, so it cannot drift from E-B1a |

**Interactions:**
- **E-A1 against `se:86`**, the SLA paragraph, which FA1 set and which is an input. E-A1 names that paragraph as an
  earlier deadline it does not lift, and leaves it unchanged.
- **E-B1a against `/code-review:17`**, "2. Security (OWASP Top 10)". E-B1a brings the skill in line with the command's
  existing item. The command is not changed.
- **E-B1a against `cr:96`/`cr:130`**, the Must Fix scale and grading on both scales. These are unchanged; their
  interplay with a security grade is still P40 S2, parked.

### 4.1 Golden coupling (each edit: quote / fixture / result)

| Edit | Open case | Quote | Fixture | Result |
|---|---|---|---|---|
| E-A1 | `validate-workflow-gate-verdict-sources` | No change. From `vg`, its `brief.md` quotes only "Every gate MUST produce a verdict in this format" and the `**Gate:**` line | No change. The copy is frozen at `7be9926`. It may already lag the source **(unverified; no `cmp` run)** | No change. `check()` reads only the fixture. The new paragraph sits in § Severity Definitions, which is inside `## Verdict Format`, but it contains neither "every gate must produce a verdict" nor a line starting `**Gate:**`. **§ Gate Types is not touched**; E-B1a only *mentions* "§ Gate Types", in another file |
| E-B1a | `code-review-conditional-pass-conditions-gap`, `code-review-fail-blocker-details` | No change. Both `brief.md` files quote only `commands/code-review.md` | No change. Each fixture is `fixture/review.md` only | No change. Each `check()` reads only `fixture/review.md` |
| E-B1b | none | — | — | — |
| — | `security-audit-*` (three cases) | Not applicable: the command is not amended | — | — |

Golden coupling was not a reason for any ruling.

## 5. Implementation checks

### 5.1 Anchors

- `grep -cxF` on each of the three Before lines returns **1** before editing (orchestrator-verified).
- After editing:
  - E-A1's and E-B1a's anchor lines survive in their After texts and still match **1**.
  - E-B1b's anchor is replaced: `grep -cxF '4. **Security**: Input validation, SQL injection, XSS, auth checks'
    implementation/knowledge/agents/tech-lead.md` returns **0**.

### 5.2 Regenerate, golden, maturity

- Run `node implementation/scripts/sync.mjs --root implementation` and
  `python3 implementation/scripts/generate-registry.py`, each followed by `--check`.
- Declare the root drift exactly as `--print-drift` reports it: up to 3 files × 7 platforms = 21 paths
  **(unverified)**.
- `scripts/scorecard.py --check` must match the current baseline.
- `check-maturity.py --root implementation` must report 0 failing.
- No protected-path grant is needed.

### 5.3 Hit counts

All counts are case-sensitive, fixed-string, per file, in the file named, after all three edits.
- **Lines** = `grep -cF` (lines that contain the phrase).
- **Occurrences** = `grep -oF … | wc -l`.
- **Before** is the count at `7ec903a`, established by reading each whole file **(unverified by grep)**.

No phrase below is a substring that an After text splits or negates. No edit removes text, so the only "must be 0"
check is E-B1b's whole-line check in §5.1.

| # | Phrase | File | Before | After: lines | After: occurrences | Edit |
|---|---|---|---|---|---|---|
| 1 | `it is graded with the definitions in agent` | `validation-gates/SKILL.md` | 0 | 1 | 1 | E-A1 |
| 2 | `§ Findings Classification` | `validation-gates/SKILL.md` | 0 | 1 | 1 | E-A1 |
| 3 | `takes the highest grade it fits` | `validation-gates/SKILL.md` | 0 | 1 | 1 | E-A1 |
| 4 | `Those definitions decide the grade only` | `validation-gates/SKILL.md` | 0 | 1 | 1 | E-A1 |
| 5 | `Severity floor` | `validation-gates/SKILL.md` | 0 | 1 | 1 | E-A1 (SEC-T588-01) |
| 6 | `No grade so given is lower than a minimum grade set elsewhere` | `validation-gates/SKILL.md` | 0 | 1 | 1 | E-A1 (SEC-T588-01) |
| 7 | `for a secret not yet committed` | `validation-gates/SKILL.md` | 0 | 1 | 1 | E-A1 (SEC-T588-01) |
| 8 | `Nor does this paragraph lift an earlier deadline` | `validation-gates/SKILL.md` | 0 | 1 | 1 | E-A1 (SEC-T588-02) |
| 9 | `The review states whether the merge request touches security-sensitive code` | `code-review/SKILL.md` | 0 | 1 | 1 | E-B1a (SEC-T588-03) |
| 10 | `OWASP Top 10 Checklist Reference` | `code-review/SKILL.md` | 0 | 1 | 1 | E-B1a |
| 11 | `all ten categories (A01 to A10)` | `code-review/SKILL.md` | 0 | 1 | 1 | E-B1a |
| 12 | `(findings, none, or not applicable)` | `code-review/SKILL.md` | 0 | 1 | 1 | E-B1a (SEC-T588-04) |
| 13 | `§ Verdict Rules, § Severity Definitions` | `code-review/SKILL.md` | 0 | 1 | 1 | E-B1a |
| 14 | `This run does not replace the Security gate before release` | `code-review/SKILL.md` | 0 | 1 | 1 | E-B1a (SEC-T588-05) |
| 15 | `security-sensitive code` | `code-review/SKILL.md` | 0 | 1 | 1 | E-B1a |
| 16 | `§ Gate Types` | `code-review/SKILL.md` | 1 (`:120`) | 2 | 2 | `:120` plus E-B1a (different lines) |
| 17 | `the full OWASP Top 10 checklist` | `tech-lead.md` | 0 | 1 | 1 | E-B1b |
| 18 | `security-sensitive code` | `tech-lead.md` | 0 | 1 | 1 | E-B1b |

**Notes on the counts:**
- **Rows 2 and 16 contain `§`** (U+00A7). Use a UTF-8 locale.
- **Row 15 counts one occurrence, not two.** E-B1a's second sentence reads "For one that does", not "security-sensitive
  code".
- **Row 5 in other files.** `Severity floor` already occurs once in `poc-security-engineer.md` (`:21`). That file is not
  edited, and the row counts `validation-gates/SKILL.md` only.

## 6. O1, recorded for the next ruling (user: "Rule it next (Recommended)")

**Subject (D3).** A criterion: which definitions decide a finding's grade when the Security Engineer runs
`/security-audit`. The two sets below can give one finding two grades.

**Clauses, verbatim at `7ec903a` (the orchestrator confirmed `/security-audit:42–46`):**

- `implementation/knowledge/agents/security-engineer.md` § Findings Classification:
  - `:77` "All findings MUST be classified using these severity levels:"
  - `:81` "\| **CRITICAL** \| Actively exploitable, data breach risk, authentication bypass \| Must fix before release \|"
  - `:82` "\| **HIGH** \| Significant vulnerability, requires specific conditions to exploit \| Must fix before release \|"
  - `:83` "\| **MEDIUM** \| Moderate risk, defense-in-depth gap \| Fix within current sprint \|"
  - `:84` "\| **LOW** \| Minor issue, best-practice deviation \| Fix within next sprint \|"
- `implementation/knowledge/commands/security-audit.md` (`:3` `agent: "security-engineer"`), § Severity Classification:
  - `:42` "9. Classify each finding with severity:"
  - `:43` "- **CRITICAL**: Actively exploitable, immediate remediation required"
  - `:44` "- **HIGH**: Exploitable with moderate effort; blocks merge until resolved (`security-guidelines.md` § Security
    Review Workflow)"
  - `:45` "- **MEDIUM**: Potential risk; requires a remediation plan (owner, fix, deadline) before merge"
  - `:46` "- **LOW**: Hardening recommendation, add to backlog"

**Why it bites (the one-value test, for the next ruling to confirm).** A missing hardening header is a
"defense-in-depth gap", which `se:83` grades MEDIUM. It is also a "Hardening recommendation", which `/security-audit:46`
grades LOW. One input, two values. That changes the verdict: CONDITIONAL_PASS with a plan (`vg:67`) or PASS
(`vg:66`).

**Bearing on this change.**
- E-A1 points every executor to `se` § Findings Classification, and its highest-fit rule applies to a finding that
  fits more than one definition *within* that set.
- Whether the set the Security Engineer uses under `/security-audit` is `se`'s or the command's is O1's question, and
  E-A1 does not answer it.

**Where the next ruling would start** (indicative only; nothing is decided here):
- **Step A first.**
- Then **Step C (P2).** The classification is part of the command's declared output (`:42`, and the VERDICT counts at
  `:56–59`).
- **Constraints:**
  - "The command is never amended on the strength of a skill or agent" (ADR-008 P2 Remedy).
  - Any alignment must not lower a grade (ADR-007 §5).
  - Plan-104 §3: "No command is amended". A command change would need its own basis, for example ADR-007 branch 1.

## 7. Summary

| Subject | Step (v1) | User decision | Outcome | Edits | Files |
|---|---|---|---|---|---|
| (a) Grading by an executor other than the Security Engineer | A; P5 | "Pointer (Recommended)" | Every executor grades with `se` § Findings Classification. The highest grade fits. Never below an existing floor (SEC-T588-01). No earlier deadline lifted (SEC-T588-02) | E-A1 | `skills/validation-gates/SKILL.md` |
| (b) Per-MR OWASP run (`sg:180`) | A; P5 | "Tech Lead per MR (Recommended)" | The Tech Lead runs all ten categories on each MR touching security-sensitive code. It states whether the MR is security-sensitive and notes a result for each category. The Security gate stays (SEC-T588-03 to -05) | E-B1a, E-B1b | `skills/code-review/SKILL.md`, `agents/tech-lead.md` |
| O1: two Security Engineer definition sets | — | "Rule it next (Recommended)" | Recorded with its quotes (§6). A separate ruling | none | — |

- **Totals:** three edits in three files.
  - No command and no tier-1 file is touched, and neither is § Gate Types.
  - No golden quote, fixture or result changes.
  - No open P5 escalation. No blockers.
- **Maturity** is not relied on anywhere. Neither are corpus counts, majority practice or golden-coupling convenience.
- **Still unverified:**
  - the Before counts in §5.3, which come from reading, not `grep`;
  - the root-drift count;
  - whether the `validate-workflow` fixture copy already lags its source.
