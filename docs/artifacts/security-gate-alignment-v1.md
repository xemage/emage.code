# Artifact: security-gate-alignment-v1.md

> Filename: `security-gate-alignment-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T586 (P2, judgment tier, decision only)
- **Created**: 2026-10-07
- **Based on:**
  - `docs/tasks/task-T586.md` (the brief; authoritative);
  - `docs/plans/plan-103-security-gate-alignment.md`;
  - `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted 2026-10-02): D1–D5, P1–P5, § Order of
    application, § Consequences (Risks), § Validation; the user's review decision Q1, **"Self-placement only"**;
  - `docs/artifacts/conditional-pass-semantics-v4.md` (P39, applied by T582; an input, not reopened): §1.6 (Q3, Q7,
    Q8), §1.7, §2 and §9 (the FU-6 and FU-7 rows);
  - `docs/artifacts/security-review-conditional-pass-semantics-v1.md` (SEC-008, the origin of FU-6; FU-7);
  - `docs/artifacts/adr-008-rulings-p40-p43-v1.md` §1.1, §5 and §10, and `adr-008-rulings-p40-p43-v3.md` (S4 is
    jointly satisfiable; FU-6 noted; N1 as applied);
  - `docs/artifacts/security-review-adr-008-rulings-n1-v1.md` (F2: the Security gate's own criteria were left to FU-6);
  - the user's instruction of 2026-10-07, "Continue with the next best step" (the recommended step was FU-6, with FU-7
    as its sibling);
  - source files under `implementation/knowledge/` and `implementation/AGENTS.md`, listed in §0.
- **Supersedes**: none (first version).
- **Decision references**: ADR-008 Step A (P3a) for all four subjects; ADR-008 P1 (Step B) shown as reached but not
  fired; ADR-008 § Scope (P39 Q3, Q7) as the source of FU-6(c)'s wording; ADR-007 §5. No new ADR.

## 0. What this document is, and what it did not do

This is the ruling for FU-6(a), FU-6(b), FU-6(c) and FU-7 under ADR-008, with one D5 record per subject (§§3–6), the
amendment list with exact Before/After text (§7), and the per-amendment statements (§8). **It changed no knowledge
file, test, ledger or other document.** The only other edit is the brief's `**Status:**` line, as the brief permits.

**Method and limits.**
- **No shell.** No `grep`, `cmp`, `git` or test run. Every claim comes from reading named files directly. Anything not
  re-read is marked **(unverified)** and collected in §11.
- **Commit.** I read every source file in the worktree at `develop` `cf36a17`. The orchestrator states that its
  `implementation/` tree is identical to `a9c4f04`, so every line number below is the `a9c4f04` line number. I could not
  check that identity myself **(unverified)**.
- **Quotes.** Every quote is verbatim. "…" marks an omission.
- **Golden.** I opened only `tests/golden/open/validate-workflow-gate-verdict-sources/{brief.md,expect.py}` and
  `tests/golden/open/discover-skills-registry-grounded-recommendation/brief.md`. **I did not open
  `tests/golden/held-out/`**, and I read no `.env*`, credential or key file.

**Files read (source, in full).**
- agents `security-engineer`, `poc-orchestrator`, `poc-security-engineer`;
- skills `validation-gates`, `receiving-code-review`, `code-review`;
- command `security-audit`;
- instruction `security-guidelines`;
- `implementation/AGENTS.md`.

## 1. Reading rules applied

### 1.1 Step A

I apply ADR-008 P3a exactly as `adr-008-rulings-p40-p43-v1.md` §1.1 applied it, a reading the orchestrator accepted
for S2–S4 and the user then adopted for S2/S3 ("Strictest applies (Recommended)"):

1. A clause that names when a value *must* be given **requires** it. A clause that states what a less strict outcome
   needs **permits** that outcome only when its conditions hold. It forbids nothing stricter unless its words do (P3a
   step 2: "only", "instead of", "no other", "replaces", or a rival closed value set).
2. Two clauses "compute different values for the same input" when each requires a value and the values differ, or when
   one requires a value the other forbids. "A permission that another clause withholds is not a contradiction."
3. Where one actor is bound by both clauses and emits one value, Step A holds if some value meets every clause.

One addition, needed by FU-6(a): **a due point is an upper bound** ("fix no later than X"). Two upper bounds on the same
fix are met together by meeting the earlier one. They contradict only if one clause also sets a lower bound ("not
before") or forbids the earlier fix. No clause read here does either.

### 1.2 Why Step B is reached but does not fire

The brief says: "Expect Step B (P1) wherever `security-guidelines.md`'s declared scope covers the subject, but show it."
I show it in each record. But ADR-008 makes Step A run "before every other step", says "The first step that fires
decides the case", and P1's Test requires "**(c)** Step A fails". So where Step A holds, P1(b) can be met while P1 still
does not fire. Each record therefore names **Step A**, quotes the tier-1 declared-scope text that P1(b) would rely on,
and states the **contingent path** if the orchestrator rejects the Step A reading. On every contingent path the
amendment text is the same, so the choice of step changes no edit.

### 1.3 The scope-gaming mitigation (ADR-008 § Consequences, Risks)

No ruling here rests on declared scope (Step A is rank-free), so none rests on a scope sentence written after FU-6 or
FU-7 was recorded (2026-10-02, the P39 security review). The only declared-scope text quoted is tier 1's
`security-guidelines.md`, whose cited lines match the line numbers P39 used at `dd7703b` (`:153`, `:182–183`, Rails
`:15–24`). I did not compare bytes across commits **(unverified)**.

### 1.4 What no ruling relies on

- **Maturity (P4).** Never relied on. `security-guidelines.md` reads `maturity: stable` (`:4`), which places it in tier 1
  (D1, the one use P4(c) permits). That is used only in the Step B checks, which do not fire.
- **Corpus counts, majority practice and golden-coupling convenience.** None is relied on (ADR-008 Validation 3).

## 2. Summary

| Subject | Step that fired | Outcome | Amendment | Files |
|---|---|---|---|---|
| **FU-6(a)**: `security-engineer` SLA column against tier 1 and `validation-gates` § Verdict Rules | **A** (P3a) | **Jointly satisfiable.** Each SLA is an upper bound; the earliest due point meets every clause. Note recommended | **FA1** (recommended) | `agents/security-engineer.md` |
| **FU-6(b)**: `validation-gates` § Severity Definitions against the `SECURITY:*` grading | **A** (P3a) | **Not misaligned with tier 1.** Tier 1 fixes four grades and who flags them; it defines none. The same file already records a security finding's grade as its Severity (`:70`). Note recommended | **FB1** (recommended) | `skills/validation-gates/SKILL.md` |
| **FU-6(c)**: Security Gate Protocol silent on the omitted-control class, constraint breaches and Q7 scope | **A** (P3a) | **Jointly satisfiable** (as S4 input (d)). `:152` is a non-exclusive trigger; `:153` is a necessary condition. Note recommended; wording from P39 Q3/Q7 (§ Scope) | **FC1** (recommended); **FC2** (optional) | `agents/security-engineer.md` |
| **FU-7**: `receiving-code-review:86` "until resolved or escalated" against "until resolved" and no waiver | **A** (P3a) | **Jointly satisfiable.** The clause ends its own block; it does not permit a merge that tier 1 blocks. Note recommended | **F7** (recommended) | `skills/receiving-code-review/SKILL.md` |

**Escalations under P5:** none (§9). **Command changes:** none needed; one observation parked (§10, O2).
**Blockers:** none (§12).

## 3. D5 record: FU-6(a), the SLA table

| Field | Content |
|---|---|
| **Subject (D3)** | A criterion: the latest point by which a security finding of each grade must be fixed (the `SLA` column of `security-engineer` § Findings Classification), as it sits beside the merge and due-point rules for the same finding. |
| **Parties** | `agents/security-engineer.md` (agent) against tier 1 `instructions/security-guidelines.md`; also `skills/validation-gates/SKILL.md` (skill; a peer of the agent). |
| **Step that fired** | **A (P3a): jointly satisfiable.** |
| **Declared scope relied on** | None (Step A is rank-free). The P1(b) text that Step B would use is quoted in §3.3. |
| **Amendment** | **FA1** (recommended), a note stating the relationship (§7). |
| **Maturity** | Not relied on. |

### 3.1 Clauses (verbatim, `a9c4f04` line numbers)

**`security-engineer.md`:**
- `:77` "All findings MUST be classified using these severity levels:"
- `:79` "| Severity | Definition | SLA |"
- `:81` "| **CRITICAL** | Actively exploitable, data breach risk, authentication bypass | Must fix before release |"
- `:82` "| **HIGH** | Significant vulnerability, requires specific conditions to exploit | Must fix before release |"
- `:83` "| **MEDIUM** | Moderate risk, defense-in-depth gap | Fix within current sprint |"
- `:84` "| **LOW** | Minor issue, best-practice deviation | Fix within next sprint |"
- `:152` "2. `fail` when any unresolved critical or high severity vulnerability remains."
- `:177` "- [Finding ID]: owner=@[who], remediation=[what], deadline=[when]"
- `:222` "**Failure mode**: Any unresolved CRITICAL or HIGH finding forces a `fail` gate verdict; …"

**Tier 1, `security-guidelines.md` § Security Review Workflow:**
- `:181` "2. Security Engineer flags findings as `SECURITY:CRITICAL`, `SECURITY:HIGH`, `SECURITY:MEDIUM`, or
  `SECURITY:LOW`"
- `:182` "3. `CRITICAL` and `HIGH` findings block merge until resolved"
- `:183` "4. `MEDIUM` findings must have a remediation plan before merge"
- `:184` "5. `LOW` findings are tracked as technical debt"

**`validation-gates/SKILL.md` § Verdict Rules, the security paragraph (`:70`):**
- "… A security finding graded critical or high, and any breach of an Immutable Security Constraint in
  `security-guidelines.md` …, yields FAIL until it is resolved, whatever mitigation is documented, and no waiver applies
  to it. …"
- "… A security finding graded medium yields at best CONDITIONAL_PASS: its remediation plan (owner, fix, deadline) is
  recorded as a tracked condition with the verdict, before the affected work's next merge …; the condition is the fix,
  due under the track rule above (production: before the next gate; PoC: by the production handoff, …). The
  next-release-cycle rule never applies to a security finding: at the Release gate, a security finding graded medium is
  fixed before the release ships. A security finding graded low is not a condition: it is tracked as technical debt …"

### 3.2 Step A analysis

**MUSTs involved:** `security-engineer:77` (classify with this table); `security-guidelines:182–184`;
`validation-gates:33` ("Every gate MUST produce a verdict in this format:"), of which § Verdict Rules is a subsection.

**Exclusivity (P3a step 2).** No SLA cell says "only", "instead of", "no other" or "replaces". Each is a deadline, an
upper bound on one fix. None sets a lower bound or forbids an earlier fix. Tier 1's `:182` and `:183` are preconditions
on merge; `:184` requires tracking. `validation-gates:70`'s due points are upper bounds.

**Why the CRITICAL/HIGH rows differ from P39's B2.** P39 amended `/security-audit`'s "HIGH … fix within current sprint"
under ADR-007 branch 1 because, in that command at the time, a HIGH could reach CONDITIONAL_PASS ("If any CRITICAL
findings exist, the verdict MUST be FAIL" was its only FAIL rule), so the sprint deadline operated as a deferral past
merge. Here the same file already requires `fail` for any unresolved critical or high (`:152`, `:222`), so "Must fix
before release" cannot operate as a deferral past merge.

**One-value test (P3a step 3):**

| Input | `security-engineer` | Tier 1 | `validation-gates:70` | One value meeting all |
|---|---|---|---|---|
| (a) An unresolved `SECURITY:HIGH` in the change under review | fix no later than release (`:82`); `fail` (`:152`) | block merge until resolved (`:182`) | FAIL until resolved | **Merge blocked; fixed before merge**, which precedes release |
| (b) A pre-existing `SECURITY:HIGH` in untouched code (P39 Q8) | fix no later than release | blocks every merge until resolved | FAIL until resolved | **Fixed before the next merge** |
| (c) A `SECURITY:MEDIUM` on the production track; the sprint ends after the next gate | fix within the current sprint (`:83`) | plan before merge (`:183`) | plan before the next merge; fix before the next gate | Plan before merge; **`deadline=` the next gate** (the earlier bound) |
| (d) A `SECURITY:MEDIUM` at the Release gate; the release ships before the sprint ends | fix within the current sprint | plan before merge | fixed before the release ships | **`deadline=` before the release ships** |
| (e) A `SECURITY:LOW` | fix within the next sprint (`:84`) | tracked as technical debt (`:184`) | not a condition; tracked as debt | **Tracked as debt, with a due point in the next sprint** |

In every case one action meets every clause: the earliest due point. `:177` carries one `deadline=` per condition, and
that one value is the earliest bound. Step A holds.

**The strongest counter-reading.** "Must fix before release" for CRITICAL/HIGH could be read as *permitting* a merge
before the fix. I do not adopt it: D2 is "Quotable only", the cell names no merge, and `:152`/`:222` in the same file
require `fail`.

### 3.3 Step B check (reached, not fired)

- **P1(a)**: the tier-1 sentences are `:182–184` (quoted above). No contradiction is visible on the texts read together
  (§3.2).
- **P1(b), declared scope** (D2), from the tier-1 side:
  - `:2` (description): "Use when implementing authentication, authorization, input validation, cryptography, session
    management, or any security-sensitive code. …"
  - `:3`: `applyTo: "**"`.
  - `:15–17` (Rails, Out of scope): "Does not replace a dedicated threat model or penetration test — see the Security
    Review Workflow for how OWASP findings feed into merge decisions."
  - `:181`: "Security Engineer flags findings as …", and `:102`: "**Security Engineer** — read-only during audit phase
    (can only flag issues, annotate, and create findings)". Each is a roster entry naming the agent (D2 source 4; the T542
    precedent, "The Rails names "the orchestrator"").
- **P1(c)**: **fails**, because Step A holds. **P1(d)**: met (an agent).
- **Contingent path.** If the orchestrator adopts the counter-reading, Step A fails on input (a) and Step B fires. The
  remedy, "Amend the lower document. Prefer citing the tier-1 text to restating it", is FA1 unchanged: it cites
  § Security Review Workflow and states that no SLA permits a merge tier 1 blocks.

### 3.4 Peer check (`security-engineer` against `validation-gates`)

Agent against skill: peers. Step A holds (inputs (c) to (e)), so Step D is not reached and no self-placement is relied
on.

## 4. D5 record: FU-6(b), the `validation-gates` severity tiers

| Field | Content |
|---|---|
| **Subject (D3)** | A value set: the tier (`critical`/`high`/`medium`/`low`) that a security finding takes in a gate's Findings table, against tier 1's `SECURITY:*` grade for the same finding. |
| **Parties** | `skills/validation-gates/SKILL.md` (skill) against tier 1 `instructions/security-guidelines.md`. `agents/security-engineer.md` (the agent that flags the grade) is read for consistency. |
| **Step that fired** | **A (P3a): jointly satisfiable.** The tiers are not misaligned with tier 1. |
| **Declared scope relied on** | None. The P1(b) text is quoted in §4.3. |
| **Amendment** | **FB1** (recommended), a note at the table stating the mapping that `:70` already fixes (§7). |
| **Maturity** | Not relied on. |

### 4.1 Clauses (verbatim)

**`validation-gates/SKILL.md` § Severity Definitions (`:74–81`):**
- `:78` "| `critical` | Broken functionality, security vulnerability, data loss risk. Blocks all progress. |"
- `:79` "| `high` | Significant defect or design flaw. Must be addressed before release; a security finding graded high
  blocks merge until resolved (§ Verdict Rules). |"
- `:80` "| `medium` | Quality concern or technical debt. Should be addressed, can be tracked. |"
- `:81` "| `low` | Minor style issue, optimization opportunity, or suggestion. |"

**`validation-gates/SKILL.md:70`:** "… A security finding is any finding in the security category, whichever gate or
executor raises it, graded on the `security-guidelines.md` § Security Review Workflow scale
(`SECURITY:CRITICAL`/`HIGH`/`MEDIUM`/`LOW`); the Findings table records that grade as its Severity and `security` as its
Category. …"

**Tier 1:** `security-guidelines:181–184` (quoted in §3.1).

**Read for consistency:** `security-engineer:82` "| **HIGH** | Significant vulnerability, requires specific conditions
to exploit | …"; `:83` "| **MEDIUM** | Moderate risk, defense-in-depth gap | …".

### 4.2 Step A analysis

**What tier 1 fixes.** A closed set of four grades for security findings, and the actor who flags them (`:181`). It
gives **no definition** of any grade. Its consequences (`:182–184`) are a merge block, a precondition on merge, and
tracking.

**What `validation-gates` fixes.** The same four values by name. For a security finding, `:70` fixes the value: "the
Findings table records that grade as its Severity". `:79` provides for "a security finding graded high".

**Exclusivity.** The Definition cells use no exclusive word. `:78` says "security vulnerability", not "every" or "any"
security finding. The two value sets are the same set, so neither is a rival.

**One-value test:**

| Input | Tier 1 | `validation-gates` (`:70`, `:78–81`) | One value |
|---|---|---|---|
| (a) A vulnerability the Security Engineer flags `SECURITY:HIGH` | grade HIGH; blocks merge until resolved | Severity `high` (`:70`); `:79` blocks merge until resolved | **`high`**; FAIL |
| (b) A defense-in-depth gap flagged `SECURITY:MEDIUM` | plan before merge | Severity `medium`; `:80` "can be tracked" permits tracking and forbids no plan; `:70` requires the plan | **`medium`**; plan before merge |
| (c) A best-practice deviation flagged `SECURITY:LOW` | tracked as debt | Severity `low`; `:70` tracked as debt; `:81` describes other kinds and requires nothing | **`low`**; tracked |
| (d) A `SECURITY:CRITICAL` | blocks merge until resolved | `critical`, "Blocks all progress", which is stricter and meets tier 1 a fortiori | **`critical`** |

Step A holds. **Ruling on the brief's question:** the tiers are **not misaligned** with tier 1's grading, read with the
same file's `:70` and `:79`. What is missing is only that the table does not say so where readers grade findings.

**The strongest counter-reading, and why it is not adopted.** Read alone, `:78` could put every "security
vulnerability" in `critical`. Input (a) would then carry two Severity values, `critical` and `high`. That reading is
excluded by the file's own later and specific text (`:70`, which says which value the Findings table records, and
`:79`), and by P39 §1.7, which defines a security finding as "graded on the `security-guidelines.md` § Security Review
Workflow scale". Any residue is a same-file question in `validation-gates`, which ADR-008 § Scope does not cover. Even
under that reading no tier-1 check is relaxed: it only makes verdicts stricter.

### 4.3 Step B check (reached, not fired)

- **P1(a)**: tier 1 `:181`. No contradiction is visible (§4.2).
- **P1(b)**: tier 1's description `:2`, `applyTo: "**"`, and Rails `:15–17` (quoted in §3.3). From the skill's side,
  `:70`'s "graded on the `security-guidelines.md` § Security Review Workflow scale" is an explicit sentence placing the
  grading of security findings with tier 1 (D2 source 4).
- **P1(c)**: fails. **P1(d)**: met (a skill).
- **Contingent path.** Under the counter-reading, Step B fires and the skill is amended toward tier 1's grading. FB1 is
  that amendment, unchanged.

**FB1 and relaxation.** Under the counter-reading only, FB1 would move a vulnerability flagged `SECURITY:MEDIUM` from
`critical` to `medium`. I rule that this relaxes no check, because the documents read together do not impose
`critical` there: `:70` (P39's applied text) already records the tier-1 grade as the Severity and says "A security
finding graded medium yields at best CONDITIONAL_PASS". **This is the one point I ask the Security Engineer to check
specifically** (§8).

## 5. D5 record: FU-6(c), the Security Gate Protocol

| Field | Content |
|---|---|
| **Subject (D3)** | A criterion: when the Security-gate audit verdict must be `fail`. In particular: (i) a required security control that is omitted, removed, disabled or weakened, at any grade; (ii) an Immutable Security Constraint breach, at any grade; (iii) the code under review when there is no change (Q7). |
| **Parties** | `agents/security-engineer.md` (agent) against `skills/validation-gates/SKILL.md` (skill) and tier 1. `/security-audit` (`agent: "security-engineer"`, `:3`) governs that agent's output when it is run through the command (P2), and is read for consistency. The recorded user decisions P39 Q3 and Q7 bear on the subject. |
| **Step that fired** | **A (P3a): jointly satisfiable.** This is the same result as `adr-008-rulings-p40-p43-v1.md` §5.2, input (d). |
| **Declared scope relied on** | None. |
| **Amendment** | **FC1** (recommended): item 2 names the classes and the Q7 scope, citing `validation-gates` § Verdict Rules. **FC2** (optional): the Rails Failure mode follows. Wording source: P39 Q3 and Q7 (ADR-008 § Scope, "That decision governs, and documents are amended to it"), as already worded in `validation-gates:70` and `/security-audit:67, 73`. |
| **Maturity** | Not relied on. |

### 5.1 Clauses (verbatim)

**`security-engineer.md` § Security Gate Protocol:**
- `:151` "1. Every audit must end with a gate verdict: `pass`, `conditional_pass`, or `fail`."
- `:152` "2. `fail` when any unresolved critical or high severity vulnerability remains."
- `:153` "3. `conditional_pass` only when medium/low findings have owners and remediation windows."
- `:220` (Rails, Inputs) "The codebase, configuration, and infrastructure definitions under audit; …"
- `:222` (Rails, Failure mode) "Any unresolved CRITICAL or HIGH finding forces a `fail` gate verdict; …"

**`validation-gates/SKILL.md:70`:**
- "… The same FAIL rule, with no waiver, holds for any security control `security-guidelines.md` requires for the code
  under review that is omitted, removed, disabled or weakened, tagged or not … A required control missing only from code
  outside the change under review is graded at its own severity and tracked like any other finding of that grade. A
  change that adds or alters code which the missing control should protect is code under review for that control. With
  no change under review (for example a full-project `/security-audit`), the whole project is the code under review. …"
- `:28` "| **Security** | Security Agent | Before any release | …"; `:104` "- Full codebase scan results".

**`/security-audit` (`commands/security-audit.md`):** `:67` "If any CRITICAL or HIGH finding exists, or any Immutable
Security Constraint in `security-guidelines.md` is breached, or any security control that `security-guidelines.md`
requires for the code under review is omitted, removed, disabled or weakened, the verdict MUST be FAIL … With no change
under review (for example a full-project `/security-audit`), the whole project is the code under review. …"

**Tier 1:** `security-guidelines:153` "The following constraints are absolute and cannot be overridden by any agent,
configuration, or runtime decision:"; `:157` "3. **No disabled security checks** — Security middleware, input
validation, and authentication checks must never be bypassed, even in development or PoC mode."

**Recorded user decisions (P39 v4 §1.6):** Q3 "**"Both tracks (Recommended)"**. It is scoped to the code under review.
Pre-existing gaps outside the change are graded at their own severity and tracked." Q7 "**"Whole project
(Recommended)"**. With no change under review, the audit's scope is the code under review. A missing required control
anywhere blocks the audit verdict."

### 5.2 Step A analysis

**MUSTs involved:** `security-engineer:151`, `:160` ("Every security audit MUST conclude with a structured verdict");
`validation-gates:33`; `/security-audit:67` when run through it. **One emitter**: the Security Engineer (`validation-gates:28`;
`/security-audit:3`; `implementation/AGENTS.md:67`, "| Phase or validation transition | `validation-gates`,
`checkpoint-protocol` |").

**Exclusivity.** `:152` ("`fail` when …") is a non-exclusive trigger. `:153` ("`conditional_pass` only when …") is a
necessary condition for `conditional_pass`; it bars that verdict when unmet and never bars `fail`. This is the reading
accepted for S4 (`adr-008-rulings-p40-p43-v1.md` §5.2). All three files fix the same value set.

**One-value test:**

| Input | `security-engineer` | `validation-gates:70` (and `/security-audit:67` under the command) | One value |
|---|---|---|---|
| (a) A required control omitted in the change, graded `SECURITY:MEDIUM`, owner and window recorded | permits `conditional_pass`; does not forbid `fail` | requires FAIL | **FAIL** |
| (b) Real PII in test data (Constraint 2), graded `SECURITY:MEDIUM` | permits `conditional_pass`; does not forbid `fail` | requires FAIL | **FAIL** |
| (c) Full-project audit with no diff; a required control missing in old code, graded `SECURITY:MEDIUM` | silent on the scope ("under audit") | the whole project is under review: requires FAIL | **FAIL** |
| (d) MR-scoped audit; a required control missing only outside the change, graded `SECURITY:MEDIUM` | permits `conditional_pass` with owner and window | graded at its own severity; at best CONDITIONAL_PASS with the plan | **CONDITIONAL_PASS** |

Step A holds. The gap is one of **silence**: an executor reading only its own protocol could emit `conditional_pass` on
input (a), (b) or (c) without contradicting any of its own sentences. That is why a note is recommended.

### 5.3 Other steps

- **Step B (reached, not fired).** Tier 1 states no verdict rule for the classes; the FAIL rule for them is P39's (Q3,
  Q7, §1.7). P1(a) needs the contradiction "visible in its own text", and `:153`/`:157` do not speak in verdicts. P1(c)
  fails in any case.
- **Step C (P2).** `/security-audit:67` already carries the classes and Q7. The agent is applied under it (`:3`). P2(c)
  fails because Step A holds. No command change is needed.
- **Contingent path.** If `:153` were read as granting `conditional_pass`, the question is one P39 Q3 and Q7 already
  settle ("A missing required control anywhere blocks the audit verdict"). ADR-008 § Scope then says "That decision
  governs, and documents are amended to it". FC1 is that amendment, unchanged.

## 6. D5 record: FU-7, `receiving-code-review:86`

| Field | Content |
|---|---|
| **Subject (D3)** | A criterion: whether escalation via the blocker protocol ends the merge block of a `FAIL` caused by a security finding excluded from waiver (graded `SECURITY:CRITICAL`/`HIGH`, a constraint breach, or an omitted required control). Second, whether escalation lifts a `SECURITY:MEDIUM` finding's remediation plan. |
| **Parties** | `skills/receiving-code-review/SKILL.md` (skill) against tier 1 `security-guidelines.md`; also `skills/validation-gates/SKILL.md` and `skills/code-review/SKILL.md` (peers). |
| **Step that fired** | **A (P3a): jointly satisfiable.** |
| **Declared scope relied on** | None. The P1(b) text is quoted in §6.3. |
| **Amendment** | **F7** (recommended): two sentences appended to `:86` (§7). The second sentence (the MEDIUM plan) can be dropped without affecting the first. |
| **Maturity** | Not relied on. |

### 6.1 Clauses (verbatim)

**`receiving-code-review/SKILL.md`:**
- `:86` "`FAIL` findings block merge until resolved or escalated via blocker protocol."
- `:80–83` "| Review source | Gate |" … "| Security Engineer | Security gate |"
- `:10–12` (Rails, Inputs) "MR/PR review comments, `tech-lead`/`security-engineer` findings, or an orchestrator
  review-gate condition — any structured feedback an agent must act on before implementing suggested changes."

**Tier 1:** `security-guidelines:182` "3. `CRITICAL` and `HIGH` findings block merge until resolved"; `:183` "4. `MEDIUM`
findings must have a remediation plan before merge"; `:153` "… cannot be overridden by any agent, configuration, or
runtime decision:".

**`validation-gates:70`:** "… yields FAIL until it is resolved, whatever mitigation is documented, and no waiver applies
to it. … The same FAIL rule, with no waiver, holds for any security control … that is omitted, removed, disabled or
weakened, tagged or not …"

**`code-review/SKILL.md:152`:** "… No waiver applies to a security finding graded `SECURITY:CRITICAL` or
`SECURITY:HIGH`, whoever raised it, to a breach of an Immutable Security Constraint, or to a security control that
`security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened: … A
waiver that lifts a `FAIL` with a security finding graded `SECURITY:MEDIUM` among its causes does not lift that
finding's remediation plan (owner, fix, deadline), which is recorded as a tracked condition before merge …"

**Escalation is required in some cases:** `implementation/AGENTS.md:49` "Max 2 retries before user escalation. Agents
MUST NOT silently fail."; `security-engineer:156` "5. After two failed remediation cycles for the same high-risk finding,
escalate to orchestrator and release manager."

### 6.2 Step A analysis

**MUSTs involved:** tier 1 `:182–183`; `validation-gates:70`; `implementation/AGENTS.md:65` ("| Code review feedback to
implement | `receiving-code-review` |"), which binds the implementer to `:86`.

**Exclusivity.** `:86` uses no exclusive word. It states when *its* block ends. It neither requires nor permits a merge.
Under the skill, the implementer responds to review; the skill grants no merge authority (Rails `:16–17`: "this skill
governs the *implementer's* response, not the *reviewer's* output").

**One-value test:**

| Input | `receiving-code-review:86` | Tier 1, `validation-gates:70`, `code-review:152` | One action |
|---|---|---|---|
| (a) An unresolved `SECURITY:HIGH` escalated after two failed cycles (the escalation is required) | block lasts until escalation; after it, this clause requires nothing | block until resolved; no waiver | **Merge stays blocked until resolved** |
| (b) An omitted required control graded `SECURITY:MEDIUM`, escalated | as (a) | FAIL until resolved; no waiver | **Blocked until resolved** |
| (c) A `FAIL` with a `SECURITY:MEDIUM` among its causes, escalated, then lifted by an authorised non-security route | silent on the plan | plan before merge (`:183`); the plan survives a waiver (`code-review:152`) | **Plan recorded as a tracked condition before merge** |

Step A holds: ending one clause's block is not a permission to merge (§1.1, rule 2). This is the same reading P39 gave
the Tech Lead waiver: "The waiver is a permission and the instruction a prohibition, so Step A holds"
(`conditional-pass-semantics-v4.md` §1.5).

**The strongest counter-reading.** Read `:86` as fixing the *duration* of the block that the FAIL findings impose, so
that after escalation they "do not block". Input (a) would then carry two values for one state (blocked and not
blocked), and Step A would fail.

### 6.3 Step B check (reached, not fired)

- **P1(a)**: `:182` "block merge until resolved" against `:86` "until resolved or escalated". The difference is visible
  in the texts.
- **P1(b)**: tier 1's description `:2` ("any security-sensitive code") and Rails `:15–17` ("see the Security Review
  Workflow for how OWASP findings feed into merge decisions"). The subject is the merge effect of security findings,
  which is what that sentence assigns to § Security Review Workflow. From the skill's side, its Rails names
  "`security-engineer` findings" (`:10`) and its table names the Security gate (`:83`).
- **P1(c)**: fails on the adopted reading. **P1(d)**: met (a skill).
- **Contingent path.** Under the counter-reading, Step B fires. The remedy, "Amend the lower document … citing", is F7
  unchanged.

### 6.4 Outside the subject

Whether escalation, as an act, ends the block of a **non-security** `FAIL` (against `implementation/AGENTS.md:54`,
"`FAIL` blocks progression") is a different subject. It is not ruled here, and F7 leaves the first sentence of `:86`
unchanged (§10, O1).

## 7. Amendment list (exact text)

Apply each edit by its Before text, not by line number. Each Before occurs **exactly once** in its file; I checked this by
reading each file in full, and a `grep -c` is still owed (§11). `§` is U+00A7 and `—` is U+2014. No emoji is introduced.
Each four-backtick fence holds one Before/After pair.

### FA1 (recommended): `implementation/knowledge/agents/security-engineer.md`, after `:84`

**Anchor:** the full `:84` line (the `LOW` row of § Findings Classification).

````
Before:
| **LOW** | Minor issue, best-practice deviation | Fix within next sprint |

After:
| **LOW** | Minor issue, best-practice deviation | Fix within next sprint |

Each SLA is the latest point by which the fix is due. It applies together with `security-guidelines.md` § Security Review Workflow and skill `validation-gates` § Verdict Rules, and never permits a merge or a release that they block. Where they set an earlier point, the earlier point is the deadline: a CRITICAL or HIGH finding blocks merge until it is resolved; a MEDIUM finding has its remediation plan (owner, fix, deadline) before merge, and its fix is due by its SLA or under that skill's track rule, whichever is earlier; a LOW finding is also tracked as technical debt.
````

### FB1 (recommended): `implementation/knowledge/skills/validation-gates/SKILL.md`, after `:81`

**Anchor:** the full `:81` line (the `low` row of § Severity Definitions).

````
Before:
| `low` | Minor style issue, optimization opportunity, or suggestion. |

After:
| `low` | Minor style issue, optimization opportunity, or suggestion. |

A security finding (§ Verdict Rules) takes the tier its grade names on the `security-guidelines.md` § Security Review Workflow scale: `SECURITY:CRITICAL` is `critical`, `SECURITY:HIGH` is `high`, `SECURITY:MEDIUM` is `medium` and `SECURITY:LOW` is `low`. What a security finding of each grade requires is stated in § Verdict Rules: for example, one graded medium needs its remediation plan before merge, and one graded low is tracked as technical debt.
````

### FC1 (recommended): `implementation/knowledge/agents/security-engineer.md:152`

**Anchor:** the full `:152` line (item 2 of § Security Gate Protocol).

````
Before:
2. `fail` when any unresolved critical or high severity vulnerability remains.

After:
2. `fail` when any unresolved critical or high severity vulnerability remains, when any Immutable Security Constraint in `security-guidelines.md` is breached, or when any security control that `security-guidelines.md` requires for the code under review is omitted, removed, disabled or weakened, tagged or not, whatever its grade (skill `validation-gates` § Verdict Rules). A required control missing only from code outside the change under review is graded at its own severity. A change that adds or alters code which the missing control should protect is code under review for that control. With no change under review (for example a full-project `/security-audit`), the whole project is the code under review.
````

**Scope note.** The brief names two missing items: the omitted-control class and Q7. FC1 also names the
constraint-breach class, because it is the third member of the same P39 exclusion (§1.7) and `:152` names it nowhere
either. It only adds a FAIL trigger. The orchestrator can drop that clause without affecting anything else.

### FC2 (optional, depends on FC1): `implementation/knowledge/agents/security-engineer.md:222`

**Anchor:** the full `:222` line (Rails, Failure mode).

````
Before:
**Failure mode**: Any unresolved CRITICAL or HIGH finding forces a `fail` gate verdict; after two failed remediation cycles on the same high-risk finding, the audit escalates to the orchestrator and release manager rather than re-auditing indefinitely.

After:
**Failure mode**: Any unresolved CRITICAL or HIGH finding, any Immutable Security Constraint breach, or any required security control omitted, removed, disabled or weakened in the code under review forces a `fail` gate verdict (§ Security Gate Protocol); after two failed remediation cycles on the same high-risk finding, the audit escalates to the orchestrator and release manager rather than re-auditing indefinitely.
````

FC2 keeps the Rails summary in step with FC1, as P39's B4 did for `/security-audit`. A Failure mode is not declared
scope (D2), so FC2 changes no scope.

### F7 (recommended): `implementation/knowledge/skills/receiving-code-review/SKILL.md:86`

**Anchor:** the full `:86` line (the file's last line).

````
Before:
`FAIL` findings block merge until resolved or escalated via blocker protocol.

After:
`FAIL` findings block merge until resolved or escalated via blocker protocol. Escalation never lifts a `FAIL` caused by a security finding that skill `validation-gates` § Verdict Rules and skill `code-review` § Review as Validation Gate exclude from waiver (a security finding graded `SECURITY:CRITICAL` or `SECURITY:HIGH`, a breach of an Immutable Security Constraint, or a security control that `security-guidelines.md` requires for the code under review and that is omitted, removed, disabled or weakened): such a `FAIL` blocks merge until the finding is resolved (`security-guidelines.md` § Security Review Workflow: "`CRITICAL` and `HIGH` findings block merge until resolved"). Nor does escalation lift a `SECURITY:MEDIUM` finding's remediation plan (owner, fix, deadline), which is recorded as a tracked condition before merge (`security-guidelines.md` § Security Review Workflow).
````

The second sentence (from "Nor does escalation") mirrors SEC-011 and SEC-020 for waivers. It can be dropped without
affecting the first.

### 7.1 Expected hit counts after implementation (case-sensitive, under `implementation/knowledge/`)

| Phrase | Expected |
|---|---|
| `Each SLA is the latest point by which the fix is due` | 1 (`security-engineer.md`, FA1) |
| `takes the tier its grade names` | 1 (`validation-gates`, FB1) |
| `Escalation never lifts a` | 1 (`receiving-code-review`, F7) |
| `Nor does escalation lift` | 1 (`receiving-code-review`, F7; 0 if dropped) |
| `the whole project is the code under review` | `security-engineer.md` 1 (FC1), in addition to P39's `security-audit.md` 2 and `validation-gates` 1 |
| `adds or alters code which the missing control should protect` | `security-engineer.md` 1 (FC1), in addition to P39's five files |
| `whatever its grade` | `security-engineer.md` 1 (FC1), in addition to P39's `testing-strategy` 1 and `prepare-release.md` 1 |
| `(§ Security Gate Protocol)` | `security-engineer.md` 1 (FC2; 0 if not applied) |

**Effect on P39's FU-1 verification table** (`conditional-pass-semantics-v4.md` §9): if anyone re-runs it after this
lands, the three P39 rows above gain one hit each in `security-engineer.md`. That is expected and is not a regression.
v4 §9 item 4 lists `security-engineer.md` and `receiving-code-review` as "Byte-unchanged". That check applied to FU-1
only.

## 8. Per-amendment statements

| Edit | Upward? (ADR-008 Validation 4) | Relaxes a check? (ADR-007 §5) | Weakens tier 1, an Immutable Security Constraint or P39? | Interaction with N1 (`validation-gates:72`) | Interaction with `security-engineer:177` (`owner=…, remediation=…, deadline=…`) |
|---|---|---|---|---|---|
| **FA1** | No. An agent | No. It removes no SLA. It adds earlier bounds from tier 1 and `validation-gates`, and says no SLA permits a merge or release they block | No. It cites § Security Review Workflow and only tightens | None in text. N1 covers verdict criteria at two gates and leaves the Security gate out on purpose (F2). FA1 is about due points, not verdict criteria. It follows the same "earliest/strictest bound" logic but does not rely on N1 or extend it | `deadline=` carries one value: the earliest of the SLA and the track-rule due point. FA1 states which, so one condition cannot carry two deadlines |
| **FB1** | No. A skill, amended toward tier 1's grading | No, on the documents read together (§4.3). **Security Engineer: please check the counter-reading in §4.2 specifically** | No. Every rule in `:66–70` is untouched, and a `SECURITY:CRITICAL` keeps `critical`'s "Blocks all progress" | It sits below N1 (end of the § Severity Definitions table) and changes no criteria set, so N1's "No set of criteria, the rules above included, makes another less strict" is unaffected | Indirect. The `CRITICAL`/`HIGH`/`MEDIUM`/`LOW` counts in `security-engineer`'s Findings Summary map one-to-one onto the `validation-gates` tiers, so a Security-gate verdict rendered in both formats carries one Severity per finding |
| **FC1** | No. An agent | No. It only adds FAIL triggers. The scope sentences are P39 Q3's own limit and do not narrow `:152`'s existing critical/high trigger (Q8: a pre-existing HIGH still fails) | No. It carries P39 §1.7 and Q7 into the Security gate's executor | It brings the Security gate's own criteria into line with § Verdict Rules by citing it. N1's "this note covers two of the gates" stays accurate and is not extended. With FC1, the Security gate gets the same verdict whether or not N1's principle is applied to it | The excluded classes yield `fail`, so they go under `### Blockers (if FAIL)` (`:179–180`) and never under `### Conditions`. Input (d) of §5.2 (a gap outside the change, graded medium) remains a Condition with `owner=`, `remediation=` and `deadline=` |
| **FC2** | No | No. It mirrors FC1 | No | None | None |
| **F7** | No. A skill | No. The first sentence of `:86` is unchanged; F7 only removes escalation as an exit for the excluded classes and the MEDIUM plan | No. It cites `:182–183` and adds tier 1's no-override effect where it was missing | None. F7 governs the implementer's response, not verdict criteria | The MEDIUM plan F7 protects is the Conditions entry (`owner=…, remediation=…, deadline=…`). Escalation leaves it in place |

**No edit touches** `security-guidelines.md`, `AGENTS.md`, any command (`/security-audit` included), `tests/golden/**`,
or any file other than the three named.

### 8.1 Golden coupling

Coupling as pre-computed by the orchestrator (held-out pruned), checked against the two case files I opened:

| Edit | File | Open case | Quote changes? | Fixture changes? | Result changes? |
|---|---|---|---|---|---|
| FA1, FC1, FC2 | `agents/security-engineer.md` | `discover-skills-registry-grounded-recommendation` | No | No | No. The fixture is a frozen registry snapshot plus frontmatter-only skill copies, and the check "reads only `id` and `category`" (its `brief.md` Provenance). No id or category changes |
| F7 | `skills/receiving-code-review/SKILL.md` | same | No | No. The frozen copy holds lines 1–4 (frontmatter) only, from `19ab1e7`; F7 edits `:86` | No |
| FB1 | `skills/validation-gates/SKILL.md` | `validate-workflow-gate-verdict-sources` | No. Its `brief.md` quotes "Every gate MUST produce a verdict in this format" and the `**Gate:**` line only | No. The fixture copy is frozen at `7be9926`, already lags the source since N1, and its Provenance pins it to that commit | No. `check()` reads only `case_dir / "fixture"`. Its `_verdict_gate_kinds` takes the whole `## Verdict Format` section (which contains § Severity Definitions), but reads only "every gate must produce a verdict" and the first `**Gate:**` line. FB1 adds neither, so even a refreshed fixture would give the same result |
| — | `commands/security-audit.md` | `security-audit-coverage-consistency`, `security-audit-critical-not-fail`, `security-audit-verdict-fields-compliant` | Not applicable: the command is not amended | — | — |

Golden coupling was not a reason for any ruling.

**Mechanics for the implementing task** (not mine to run):
- regenerate with `node implementation/scripts/sync.mjs --root implementation` and
  `python3 implementation/scripts/generate-registry.py`, each followed by `--check`;
- declare root drift exactly as `--print-drift` reports it: up to 3 files × 7 platforms = 21 paths **(unverified)**;
- `scripts/scorecard.py --check` must match the current baseline (held-out coupling is detected only there);
- `check-maturity.py --root implementation` must report 0 failing;
- no protected-path grant is needed.

## 9. Escalations (P5)

**None.** Step A decided all four subjects. On each contingent path (§3.3, §4.3, §5.3, §6.3) a deciding step exists:
Step B for FU-6(a), FU-6(b) and FU-7, and § Scope (P39 Q3, Q7) for FU-6(c). Each gives the same amendment. So no
subject reaches P5, and no user question is required.

**Choices for the reviewers, not the user.** These choices can only tighten or add explanation. None can relax a check:
- FC1's constraint-breach clause (§7, scope note);
- FC2 (optional);
- F7's second sentence.

## 10. Parked observations (not ruled)

- **O1: non-security escalation (`receiving-code-review:86`).** "until resolved or escalated" against
  `implementation/AGENTS.md:54` ("`FAIL` blocks progression") for a `FAIL` with no excluded security cause. This is a
  different subject from FU-7. On the §1.1 reading, Step A would hold. F7 leaves that sentence unchanged. **Trigger:** a
  ruling on what escalation, as opposed to its outcome (for example a Tech Lead waiver), may lift.
- **O2: `/security-audit` VERDICT block has no Conditions field (command; parked).** `:67` says a MEDIUM's remediation
  plan is "listed as a condition", but the block (`:53–64`) has no Conditions line, while `security-engineer:176–177`
  has one. Under the command, P2 lets the agent's Conditions section accompany the block (specialisation), so nothing in
  FU-6 needs a command change. Making it structural would be a command change. This is the existing **FU-5** candidate
  ("structured `**Conditions**:` field"). **Not proposed here.**
- **O3: `/security-audit:46` "LOW: Hardening recommendation, add to backlog"** beside `security-engineer:84` "Fix within
  next sprint". This is command against agent. A backlog item with a due point meets both, and FA1 adds "also tracked as
  technical debt". No change; a command change would be out of scope in any case.
- **O4: `security-engineer:94` "**Status**: [Pass | Fail | Conditional Pass]".** This is a report-format label beside
  the `VERDICT` tokens (T572 territory). It is not touched.

## 11. Unverified claims (need a shell)

1. `cf36a17` and `a9c4f04` have identical `implementation/` trees (the orchestrator's statement).
2. Each Before text in §7 occurs exactly once in its file. I checked by reading each file in full; a `grep -c` is owed.
3. The tier-1 lines quoted (`security-guidelines:2–3, 15–17, 102, 153, 157, 181–184`) are byte-identical to their text at
   `dd7703b`, when FU-6/FU-7 were recorded. I matched line numbers against P39's citations only (§1.3).
4. No test outside `tests/golden/` asserts text in `security-engineer.md`, `receiving-code-review/SKILL.md` or the
   § Severity Definitions part of `validation-gates/SKILL.md`. P39 recorded that `test_validation_gates_skill_contract`
   asserts only verdict tokens, markers and the Gate Types executor mapping. I did not read it.
5. No other knowledge file restates the `security-engineer` SLA table or the `receiving-code-review:86` sentence. I did
   not read `orchestrator.md`, `release-manager.md`, `tech-lead.md` or `qa-engineer.md` for this task.
6. The root-drift path count (§8.1).
7. The three `security-audit-*` open cases quote only `commands/security-audit.md`. This is the orchestrator's
   pre-computation; I did not open them.

## 12. Corrections to the brief, and blockers

**Corrections** (all `unclear_requirements`, severity `minor`):
1. **`security-guidelines.md` § Security Review Workflow is `:179–184`** (heading `:179`, items `:180–184`). The file
   ends at `:184`, so the brief's "`:182–185`" is `:182–184`.
2. **`validation-gates` § Severity Definitions**: the heading is `:74` and the table `:76–81` (rows `:78–81`), as the
   brief says. P39's `:74` cited the table's old position; N1 (`:72`) moved it.
3. **`security-engineer` SLA rows** are `:81–84` (header `:79`). P39 §9 cited `:81–83` at `dd7703b`. The LOW row is
   `:84`, consistent with `adr-008-rulings-p40-p43-v1.md` §5.1.
4. **"Expect Step B (P1)".** ADR-008 runs Step A first, and P1(c) requires Step A to fail. Step B is reached in each
   record and its declared-scope text is quoted, but Step A decides (§1.2). No outcome depends on this: each contingent
   path gives the same edit.

**Blockers:** none. ADR-008 applied as written to all four subjects.
