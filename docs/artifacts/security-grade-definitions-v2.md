# Artifact: security-grade-definitions-v2.md

> Filename: `security-grade-definitions-v2.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T590 (P2, judgment tier, decision only), second version
- **Created**: 2026-10-08
- **Based on:**
  - `docs/artifacts/security-grade-definitions-v1.md`, as redacted by the orchestrator. Its analysis stands and is
    referenced here, not repeated:
    - §2, the D5 record (Step A fails; B does not fire; C's test is met but its remedy is barred; D does not apply; E
      (P5) fired);
    - §3, the interaction with E-A1;
    - §4, escalation Q-O1;
    - §6, golden coupling;
    - §8, observations C1 and O2–O4.
  - The orchestrator's verification of v1:
    - 46 of 46 quotes are verbatim;
    - both anchors are unique. `grep -cxF` returns 1 for `security-audit.md:46` (with its three-space indent) and for
      `security-engineer.md:88`.
  - **The user's decision of 2026-10-08**, verbatim option label: Q-O1, **"Higher of the two (Recommended)"**. That is
    option A, edits E-O1a and E-O1b.
  - **The Security Engineer's review** of E-O1a and E-O1b: **CONDITIONAL_PASS**, with conditions SEC-T590-01 (MEDIUM),
    SEC-T590-02 (LOW) and SEC-T590-03 (LOW).
    - The orchestrator commits the record as `docs/artifacts/security-review-security-grade-definitions-v1.md`.
    - The orchestrator relayed the three conditions' text and adopted each one verbatim. I apply them verbatim.
    - I did not read the review record itself.
  - **The sequencing guard**, as the orchestrator verified it:
    - T589 merged as MR !500, giving `develop` at `fad9580`;
    - at that `develop`, `grep -cF 'No grade so given is lower than a minimum grade set elsewhere'` on
      `implementation/knowledge/skills/validation-gates/SKILL.md` returns 1.

    The implementing task re-checks it.
  - Unchanged inputs:
    - `docs/tasks/task-T590.md`;
    - `docs/plans/plan-105-security-grade-definitions-o1.md`;
    - `docs/decisions/ADR-008-knowledge-document-authority.md` and `docs/decisions/ADR-007-command-contract-authority.md`;
    - `docs/artifacts/security-finding-grading-and-owasp-run-v2.md` (E-A1).
- **Supersedes**: `security-grade-definitions-v1.md`. v1 stays as redacted. **v2 alone is the implementation input.**
- **Decision references**:
  - ADR-008 P5, decided by the user (§1). The decision governs under ADR-008 § Scope: "A question already settled by …
    a recorded user decision. That decision governs, and documents are amended to it."
  - ADR-008 P2 Remedy, the shape of E-O1b.
  - ADR-007 §5 (never relax a check).
  - SEC-T590-01 to SEC-T590-03.

## 0. Method and limits

- **No shell.**
  - Line numbers are at `40dc780`, this worktree's commit.
  - Plan-105 §2 says T589 edits `validation-gates`, `code-review` and `tech-lead`, not the two files edited here. So
    both anchors should be unchanged at `fad9580`. I did not read `fad9580` **(unverified)**.
  - Apply each edit by its Before text, not by its line number.
- **Golden.**
  - I opened no file under `tests/golden/` beyond those v1 §0 lists.
  - I never opened `tests/golden/held-out/`.
  - v1 mentioned a sibling case named in two open briefs. Here it is referred to only as "a sibling case named in two
    open briefs (name redacted)".
- **Secrets.** I read no `.env*`, credential or key file.
- **Encoding.**
  - `§` is U+00A7 and `—` is U+2014.
  - Each four-backtick fence holds exactly one Before/After pair.
  - E-O1a's paragraph starts with exactly three spaces.
  - No emoji is introduced.

## 1. Decisions recorded

| Item | Raised in | Decision (verbatim label) | Effect |
|---|---|---|---|
| **Q-O1**: which definitions decide a finding's grade when the Security Engineer runs `/security-audit` | v1 §4 (P5) | **"Higher of the two (Recommended)"** | Option A is chosen. E-O1a and E-O1b are applied, as amended by SEC-T590-01 to SEC-T590-03 (§3). Options B and C are not chosen. Under ADR-008 § Scope, the user's decision lifts v1's hold (P5 § Form 3) for these two edits |
| **O2**: the command's own definitions overlap ("Potential risk" against "Hardening recommendation") | v1 §8 | Not a separate decision. It is **resolved for grading purposes by SEC-T590-01** | E-O1a now compares `se`'s grade with "the highest grade the definitions above give it". Where a finding fits both of the command's MEDIUM and LOW, the command-side grade is therefore MEDIUM. The four command definition lines (`/security-audit:43–46`) are **unchanged**, byte for byte. The ambiguity in their wording stays as text, but it can no longer produce the lower grade |

**Authority for the command change.** E-O1a rests only on the user's decision. No ADR-007 branch licenses it (v1 §2.5),
and it is not made on the strength of the agent (ADR-008 Validation 4). E-O1b has P2's remedy shape: the agent defers to
the command and is scoped to it. It is lawful because E-O1a removes the lowering that barred P2's remedy in v1 §2.5.
**Apply both or neither.**

## 2. Change log against v1

| # | Source | Edit | Change |
|---|---|---|---|
| 1 | User, Q-O1 | E-O1a, E-O1b | Option A is chosen. Both edits move from "held" to final |
| 2 | **SEC-T590-01** (`SECURITY:MEDIUM`) | E-O1a | "Where that grade differs from the one the definitions above give, the higher of the two applies." becomes "Where that grade differs from the highest grade the definitions above give it, the higher of the two applies." This gives option A what it promised the user, "at least what either set gives", and resolves O2 for grading |
| 3 | **SEC-T590-02** (`SECURITY:LOW`) | E-O1a | "(skill `validation-gates` § Severity Definitions)" becomes "(for example those that skill `validation-gates` § Severity Definitions names)". The citation now introduces examples of floors, so it is not a closed list |
| 4 | **SEC-T590-03** (`SECURITY:LOW`) | E-O1b | "…so the grade is never lower than this section gives." becomes "…so the grade is never lower than this section gives, and the SLA paragraph above still applies to it." This keeps `se:86` in force under the command |
| 5 | Orchestrator | §0 | The held-out sibling case name is redacted, and is not repeated here |
| 6 | Orchestrator | Metadata | The sequencing guard is recorded as satisfied (T589 merged, `fad9580`) |
| 7 | — | §5 | The hit counts are corrected. Rows are added for the three new phrases, for `highest grade` (two occurrences on one line), for `SLA` in `se`, and for a must-be-0 guard against v1's superseded wording |

v1's D5 record stands. Its steps and outcome are unchanged. The review conditions only tighten the wording of the chosen
edits.

## 3. Final edits (complete; v2 alone is the implementation input)

| # | Edit | File | Unique anchor (full line, at `40dc780`) | Placement |
|---|---|---|---|---|
| 1 | E-O1a | `implementation/knowledge/commands/security-audit.md` | `:46`, `   - **LOW**: Hardening recommendation, add to backlog` (three leading spaces) | A blank line and a new paragraph after it, inside list item 9 |
| 2 | E-O1b | `implementation/knowledge/agents/security-engineer.md` | `:88`, `## Security Review Report Format` | A new paragraph and a blank line before it, so the paragraph ends § Findings Classification |

The orchestrator verified each anchor (`grep -cxF` = 1). After the edits, both anchors survive in their After texts and
still return 1.

### E-O1a: `security-audit.md`, new paragraph after `:46`

````
Before:
   - **LOW**: Hardening recommendation, add to backlog

After:
   - **LOW**: Hardening recommendation, add to backlog

   Grade each finding also with the definitions in agent `security-engineer` § Findings Classification, taking the highest grade it fits there. Where that grade differs from the highest grade the definitions above give it, the higher of the two applies. No grade so given is lower than a minimum grade set elsewhere for that kind of finding (for example those that skill `validation-gates` § Severity Definitions names).
````

- **Indent.** The new paragraph is indented by exactly three spaces and follows a blank line. It therefore continues
  list item 9, and does not read as a fifth grade.
- **What follows it.** The existing blank line `:47` and the `## Verdict Output` heading (`:48`) follow it unchanged.

### E-O1b: `security-engineer.md`, new paragraph before `:88`

````
Before:
## Security Review Report Format

After:
When this agent runs `/security-audit`, that command's § Severity Classification decides each finding's grade: it grades with these definitions as well as its own, and the higher grade applies, so the grade is never lower than this section gives, and the SLA paragraph above still applies to it.

## Security Review Report Format
````

- **Placement.** The paragraph follows `se:86` (the SLA paragraph) and the blank line `:87`. It stays inside § Findings
  Classification, which is where E-A1's pointer (`validation-gates` § Severity Definitions) leads.
- **"the SLA paragraph above".** It names `se:86`, which is the only SLA paragraph in the section.

## 4. Per-edit statements

### 4.1 Upward?

- **E-O1a is a command change.** It is the only edit that is upward in form, and its basis is the user's decision (§1),
  not the agent. ADR-008 Validation 4 forbids changing "a command on the strength of a skill or agent". This edit is not
  made on that strength.
- **E-O1b is not upward.** It amends an agent, scoped to "When this agent runs `/security-audit`" (ADR-008 P2 Remedy).
- **Untouched.** Neither edit touches `security-guidelines.md`, `AGENTS.md`, any other command, `tests/golden/**`,
  `validation-gates`, or any file other than the two named.

### 4.2 Relaxation (ADR-007 §5)

| Edit | Relaxes a check? | Why not |
|---|---|---|
| E-O1a | No | The four definitions `:43–46` and the verdict rule `:67` are unchanged. The edit only adds a maximum, taken over the highest grade under each set, and a floor. For any finding, the grade after the edit is at least every grade either set could give before it. No required field, value or condition is removed, and no second, weaker form is admitted |
| E-O1b | No | It states that the grade under the command "is never lower than this section gives", and it keeps the SLA paragraph in force (SEC-T590-03) |

### 4.3 Security

- **SEC-T590-01 makes the result monotone on both sides.**
  - On the command side, the grade is the highest the command's definitions give.
  - On the agent side, it is the highest `se` gives.
  - The higher of those two is taken.
  - Results:
    - v1's hardening example (`Referrer-Policy`) is MEDIUM, so the verdict is at best CONDITIONAL_PASS with a
      remediation plan (`/security-audit:67`);
    - an authentication bypass that needs a specific configuration is CRITICAL, so the verdict is FAIL;
    - account enumeration that is "Exploitable with moderate effort" stays HIGH, so the verdict is FAIL.
- **SEC-T590-02.** The floor sentence cites `validation-gates` § Severity Definitions, but only as an example of where
  floors are named. A floor stated anywhere else still holds.
  - The guard is satisfied: E-A1's floor sentence is present at `develop` `fad9580` (orchestrator-verified).
  - Through it, the PoC floors in `poc-security-engineer` § Behavior and `poc-orchestrator` § Security Findings are
    reached.
- **SEC-T590-03.** Under the command, `se:86` still applies: an SLA never permits a blocked merge, and an earlier
  deadline wins.
- **Grade-independent FAIL classes are unchanged.** These are an Immutable Security Constraint breach, and a required
  control that is omitted, removed, disabled or weakened (`/security-audit:67`, `se:154`, `vg:70`).
- **Cost, disclosed in v1 §4 and accepted with option A.** There will be more MEDIUM grades, and so more CONDITIONAL_PASS
  verdicts, than the command alone gave. Under SEC-T590-01 this is stronger than v1 projected. "Potential risk" (`:45`)
  is broad, so LOW under the command now needs a finding that fits none of the command's higher definitions and none of
  `se`'s higher ones.

### 4.4 Interaction with E-A1 (now merged)

- **E-A1's pointer.** It sends every executor to `se` § Findings Classification, and E-O1b is the last paragraph of that
  section. Under the command, the chain is therefore E-A1, then `se`, then E-O1b, then `/security-audit` step 9.
- **Floors.** E-A1's floor sentence ("No grade so given is lower than a minimum grade set elsewhere …") admits the higher
  grade that the command side may give.
- **Lowering.** No grade under the command is lower than E-A1 gives elsewhere.
- **Residual closed.** v1 recorded a residual for Q-a option A1: "under `/security-audit`, `:42–46` may grade the same
  finding differently". That residual is closed.

### 4.5 Golden coupling (each edit: quote / fixture / result)

| Edit | Open case (`tests/golden/open/…`) | Quote | Fixture | Result |
|---|---|---|---|---|
| E-O1a | `security-audit-coverage-consistency` | No change. It quotes § "Verdict Output" (`brief.md:11–12`) and § "Audit Scope" (`brief.md:13`). E-O1a touches neither | No change | No change. `check()` compares only `**OWASP coverage**` with the A01–A10 rows (`expect.py:24–33`) |
| E-O1a | `security-audit-critical-not-fail` | No change. It quotes the `:67` verdict rule (`case.yaml:6–7`, `brief.md:13–14`, `expect.py:4–5`). E-O1a does not touch `:67` | No change | No change. It stays `known_failing` (`check()` returns False; `expect.py:31–41`) |
| E-O1a | `security-audit-verdict-fields-compliant` | No change. It quotes the § "Verdict Output" field formats (`brief.md:10–16`) | No change | No change. `check()` reads matrix rows and field formats only (`expect.py:36–66`) |
| E-O1b | none (no open case cites `se`; brief §2.3) | — | — | — |

- **No protected-path grant and no evaluator-hash baseline is needed.**
- **Fixture observation** (v1 §6; not a reason, P4(e)). `security-audit-coverage-consistency/fixture/audit.md:10`
  grades a LOW finding with `Status: PASS`. Under SEC-T590-01, that finding is more likely to be graded MEDIUM, through
  "Potential risk" or "defense-in-depth gap". No `check()` reads a grade, and the fixture is frozen and hand-authored, so
  no result changes. That grade is a judgment **(unverified)**.

### 4.6 Implementation checks

1. **Sequencing.** Before editing, re-check that `grep -cF 'No grade so given is lower than a minimum grade set
   elsewhere' implementation/knowledge/skills/validation-gates/SKILL.md` returns 1.
2. **Anchors.**
   - Before editing, `grep -cxF` on each Before line returns 1:
     - E-O1a: `'   - **LOW**: Hardening recommendation, add to backlog'`;
     - E-O1b: `'## Security Review Report Format'`.
   - After editing, each still returns 1.
3. **Regenerate.**
   - Run `node implementation/scripts/sync.mjs --root implementation` and
     `python3 implementation/scripts/generate-registry.py`, each followed by `--check`.
   - Declare the root drift as `--print-drift` reports it. Up to 2 files × 7 platforms is expected **(unverified)**.
4. **Golden and maturity.**
   - `scripts/scorecard.py --check` must match the current baseline.
   - `check-maturity.py --root implementation` must report 0 failing.

## 5. Hit counts (corrected)

All counts are case-sensitive, fixed-string and per file, in the file named, after both edits.

- **Lines** means `grep -cF` (the lines that contain the phrase).
- **Occurrences** means `grep -oF … | wc -l`.
- **Before** is the count at `40dc780`, from reading each whole file **(unverified by grep)**.
- No phrase below is split by an After text. Each After phrase is contiguous on one line.
- Neither edit removes text. The only must-be-0 row is row 12, which guards against applying v1's superseded wording.

| # | Phrase | File | Before: lines / occ. | After: lines / occ. | Edit |
|---|---|---|---|---|---|
| 1 | `Hardening recommendation` | `security-audit.md` | 1 / 1 (`:46`) | 1 / 1 | anchor, survives |
| 2 | `§ Findings Classification` | `security-audit.md` | 0 / 0 | 1 / 1 | E-O1a |
| 3 | `security-engineer` | `security-audit.md` | 2 / 2 (`:3`, `:62`) | 3 / 3 | E-O1a adds one |
| 4 | `taking the highest grade it fits there` | `security-audit.md` | 0 / 0 | 1 / 1 | E-O1a |
| 5 | `the highest grade the definitions above give it` | `security-audit.md` | 0 / 0 | 1 / 1 | E-O1a (**SEC-T590-01**, new) |
| 6 | `highest grade` | `security-audit.md` | 0 / 0 | **1 / 2** | E-O1a (rows 4 and 5 are on one line) |
| 7 | `the higher of the two applies` | `security-audit.md` | 0 / 0 | 1 / 1 | E-O1a |
| 8 | `minimum grade set elsewhere` | `security-audit.md` | 0 / 0 | 1 / 1 | E-O1a |
| 9 | `for example those that skill` | `security-audit.md` | 0 / 0 | 1 / 1 | E-O1a (**SEC-T590-02**, new) |
| 10 | `validation-gates` | `security-audit.md` | 0 / 0 | 1 / 1 | E-O1a |
| 11 | `§ Severity Definitions` | `security-audit.md` | 0 / 0 | 1 / 1 | E-O1a |
| 12 | `differs from the one the definitions above give` | `security-audit.md` | 0 / 0 | **0 / 0** | must stay 0 (v1's superseded wording) |
| 13 | `## Security Review Report Format` | `security-engineer.md` | 1 / 1 (`:88`) | 1 / 1 | anchor, survives |
| 14 | `/security-audit` | `security-engineer.md` | 1 / 1 (`:154`) | 2 / 2 | E-O1b adds one |
| 15 | `§ Severity Classification` | `security-engineer.md` | 0 / 0 | 1 / 1 | E-O1b |
| 16 | `never lower than this section gives` | `security-engineer.md` | 0 / 0 | 1 / 1 | E-O1b |
| 17 | `the SLA paragraph above still applies to it` | `security-engineer.md` | 0 / 0 | 1 / 1 | E-O1b (**SEC-T590-03**, new) |
| 18 | `SLA` | `security-engineer.md` | **2 / 4** (`:79` once; `:86` three times: "Each SLA", "whatever its SLA", "by its SLA") | **3 / 5** | E-O1b adds one |

**Notes on the counts:**

- **`§`.** Rows 2, 11 and 15 contain `§` (U+00A7). Use a UTF-8 locale.
- **Headings.** `se:75` reads `## Findings Classification` and `/security-audit:40` reads `## Severity Classification`.
  Neither contains `§`, so rows 2 and 15 count 0 before.
- **The three new phrases** from the review are rows 5, 9 and 17.
- **Rows 6 and 18** show line counts that differ from occurrence counts.

## 6. Summary

| Item | Step (v1) | User decision | Outcome | Edits | Files |
|---|---|---|---|---|---|
| O1 / Q-O1: grade definitions under `/security-audit` | A fails; B does not fire; C barred; E (P5) | **"Higher of the two (Recommended)"** | Under the command, each finding takes the higher of: the highest grade the command's definitions give it, and the highest grade `se` § Findings Classification gives it. It is never below a floor set elsewhere. `se:86` still applies. The four command definition lines are unchanged | E-O1a (user-decided command change, with SEC-T590-01 and SEC-T590-02); E-O1b (agent, scoped, with SEC-T590-03) | `implementation/knowledge/commands/security-audit.md`, `implementation/knowledge/agents/security-engineer.md` |
| O2: the command's internal overlap | — | (covered by Q-O1, via SEC-T590-01) | Resolved for grading purposes: the overlap always resolves to the higher grade. The text is unchanged | none beyond E-O1a | — |

- **Totals:** two edits in two files. No tier-1 file, no other command, no skill and no golden file is touched.
- **Golden:** no quote, fixture or result changes. No grant or baseline is needed.
- **No grade is lowered** and no check is relaxed.
- **Maturity** was not relied on. Neither were corpus counts, majority practice or golden-coupling convenience.
- **Open P5 escalations:** none. **Blockers:** none.
- **Still unverified:**
  - the Before counts in §5, which come from reading, not `grep`;
  - that both anchors are unchanged at `fad9580`, which plan-105 §2 implies and the implementing task re-checks;
  - the root-drift count;
  - the grade judgment in the §4.5 fixture observation;
  - the review record itself, which I did not read (its conditions were relayed verbatim).
