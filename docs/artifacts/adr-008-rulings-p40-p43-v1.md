# Artifact: adr-008-rulings-p40-p43-v1.md

> Filename: `adr-008-rulings-p40-p43-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T584 (P2, judgment tier, decision only)
- **Created**: 2026-10-07
- **Based on**:
  - `docs/tasks/task-T584.md` (the brief; authoritative);
  - `docs/plans/plan-102-adr-008-rulings-p40-p43.md`;
  - `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted 2026-10-02): § Definitions D1–D5, P1–P5,
    § Order of application, § Worked examples, § Consequences (Risks) and § Validation;
  - the user's review decision on ADR-008 Q1, **"Self-placement only"**, as recorded in ADR-008 § User decisions at
    review and relayed by the orchestrator;
  - `docs/decisions/ADR-007-command-contract-authority.md` (Accepted), especially §5 "Never resolve by relaxing a check";
  - `docs/artifacts/gate-verdict-consistency-v1.md` §7 G1 and §13.3 (the origin of P40), and its §10 E1, E2, E6
    Before texts;
  - `docs/artifacts/poc-skill-command-overlaps-v1.md` §13 O2 and §16.3 (the origin of P43), and its §9 E1, E2, E8, E11
    Before texts;
  - `docs/artifacts/conditional-pass-semantics-v4.md` (P39, applied by T582; an input, not reopened), especially §1.5,
    §10, §11 C4, §12 and §16;
  - the user's instruction of 2026-10-07, "Continue with the Recommended next step";
  - source files under `implementation/knowledge/` and `implementation/AGENTS.md`, as listed in §0.
- **Supersedes**: none (first version).
- **Decision references**: ADR-008 Step A (P3a) for P40 S2, S3 and S4; ADR-008 P5 for P43; ADR-007 §5. No new ADR.

## 0. What this document is, and what it did not do

This is the ruling for P40 slices S2, S3 and S4 and for P43 under ADR-008, with one D5 record per slice (§§3–6), one
user question for the one P5 escalation (§7), a pre-drafted contingent question (§8), and the amendment list (§9).
**It changed no knowledge file, test, ledger or other document.** The only other edit is the brief's `**Status:**`
line, as the brief permits.

**Method and limits.**
- **No shell.** No `grep`, `cmp`, `git` or test run. Every claim comes from reading named files directly. Anything not
  re-read is marked **(unverified)** and collected in §13.
- **Commit.** I read every source file in the worktree at `develop` `c0138a7`. The orchestrator states that `c0138a7`
  differs from `a54bbba` only under `docs/tasks/` and `docs/plans/`, so every line number below is the `a54bbba` line
  number. I could not check that identity myself **(unverified)**.
- **Quotes.** Every quote is verbatim. "…" marks an omission. Where a source line carries an emoji label, the emoji is
  replaced by "…" as an omission.
- **Golden.** I opened only `tests/golden/open/validate-workflow-gate-verdict-sources/{brief.md,expect.py}`,
  `tests/golden/open/code-review-conditional-pass-conditions-gap/{brief.md,expect.py}`,
  `tests/golden/open/code-review-fail-blocker-details/{brief.md,expect.py}` and
  `tests/golden/open/evaluate-poc-verdict-debt-reconciliation/{brief.md,expect.py}`. **I did not open
  `tests/golden/held-out/`**, and I read no `.env*`, credential or key file.

**Files read (source).**
- skills `validation-gates`, `code-review`, `testing-strategy`, `rapid-prototyping`, `poc-evaluation`, in full;
- agents `tech-lead`, `qa-engineer`, `security-engineer`, `evaluation-agent`, `poc-orchestrator`, in full;
  `orchestrator` lines 150–269;
- commands `code-review`, `evaluate-poc`, `security-audit`, in full;
- instructions `security-guidelines` lines 1–30 and 150–185, `poc-guidelines` lines 1–159, `coding-standards` in full;
- `implementation/AGENTS.md` lines 1–75; `implementation/registry/summary.md`.

## 1. Reading rules applied

### 1.1 Step A: what a verdict table requires, and what it only permits

ADR-008 P3a says two clauses conflict "only if no single output or action can satisfy both", and its mandatory
one-value test says "If the two clauses can compute different values for the same input, they contradict". I apply
the test as follows, and every Step A result below depends on it.

1. **A verdict row requires a value, or permits one.** A row that names when a verdict *must* be given (a FAIL
   trigger such as "One or more must-fix findings. Code must not merge.") *requires* that value. A row that states
   what a less strict verdict needs (a PASS or CONDITIONAL_PASS row) *permits* that verdict only when its conditions
   hold. It does not forbid a stricter verdict unless its words do so (P3a step 2: "only", "instead of", "no other",
   "replaces", or a rival closed value set).
2. **"Compute" means "require".** Two clauses compute different values for one input when each *requires* a value and
   the values differ, or when one requires a value the other forbids. A permission that another clause withholds is
   not a contradiction.
3. **Who emits the value matters.** Where one actor is bound by both clauses and emits one verdict, Step A holds if
   some value meets every clause binding that actor. Where each clause binds a *different* emitter, and each emitter
   obeying only its own clause can record a different value for the one decision, the one decision carries two values
   and Step A fails.

**Grounds.**
- **P3a step 2.** None of the verdict rows in S2–S4 uses an exclusive word against a *stricter* verdict (§§3–5 list
  each one). All the documents fix the same closed value set (`PASS` | `CONDITIONAL_PASS` | `FAIL`,
  `implementation/AGENTS.md:52`), so no value set is a rival.
- **The accepted Step A practice since ADR-008.** `conditional-pass-semantics-v4.md` §1.5 (Accepted; applied by T582)
  reads `validation-gates`' "documented mitigations" route as a permission: "The security permission ("documented
  mitigations") and `security-guidelines` `:153`/`:182` are jointly satisfiable by withholding the permission." Its
  §10 D5 row for C1, C3, C4 records "Holds (a permission against a prohibition)".
- **ADR-008's own worked example names this reading.** For S2 it asks: "Are the verdict tables exclusive definitions,
  so that one finding gets two values? Or are they necessary conditions, so that the most restrictive verdict any
  applicable table requires satisfies them all?"
- **The one-value test still bites where it should.** It fails P43 (§6), where two documents bind two different
  emitters of one outcome.

**The strongest counter-reading, and why I do not adopt it.** `code-review`'s table heads its middle column "Meaning"
(`code-review/SKILL.md:124`). Read as definitions, its FAIL row ("One or more must-fix findings") would forbid a FAIL
with no must-fix finding, and S2 would fail Step A. I do not adopt that reading:
- "Meaning" is not an exclusive word under P3a step 2;
- the same reading would also make `validation-gates`' FAIL row exhaustive, which `conditional-pass-semantics-v4.md`
  §1.5 declined to do;
- `validation-gates`' own rows do not partition findings by grade. After T582, a security finding graded medium is
  never PASS (`:66`), and an omitted required security control is FAIL whatever its grade (`:70`).

**If the orchestrator rejects this reading,** S2 and S3 fail Step A, Step D decides neither of them (§8), and both
escalate. §8 pre-drafts that question so no further round is needed.

### 1.2 The scope-gaming mitigation (ADR-008 § Consequences, Risks)

ADR-008 says: "declared scope is read as of the commit on which the conflict was first recorded. A scope edit made in
the same change as the ruling it would decide cannot be relied on."

**When each conflict was first recorded:**
- **P40 (G1).** Recorded in `gate-verdict-consistency-v1.md` §7, read at `24518f6`, and parked in its §13.3 on
  `develop` `24518f6`.
- **P43 (O2).** Recorded in `poc-skill-command-overlaps-v1.md` §13, read at `1208790`, and parked in its §16.3 on
  `develop` `1208790`.

**Candidate sentences that postdate the recording.** The Before texts of the recording artifacts' own follow-up edits
show that these sentences did not exist when the conflicts were recorded:

| Sentence | Added by |
|---|---|
| `code-review/SKILL.md:120` | T572 E1 |
| `testing-strategy/SKILL.md:219` | T572 E2 |
| `tech-lead.md:68`, beyond "issue a structured verdict" | T572 E6 |
| `rapid-prototyping` Rails `:10–14` | T574 E8 |
| `rapid-prototyping:125` | T574 E11 |
| `poc-evaluation` Rails `:10–14` | T574 E1 |
| `poc-evaluation:46` | T574 E2 |

**Effect on these rulings: none.** No ruling here rests on a Step D self-placement, so no outcome depends on how
broadly the mitigation's first sentence reaches. Where I examine one of these sentences in a Step D analysis (§6, §8),
I find it is not self-placement on its own text, and I also note its date. The breadth question is flagged in §12 for
future rulings.

### 1.3 What no ruling relies on

- **Maturity (P4).** It is never relied on anywhere. The files involved are `stable` (`validation-gates`,
  `code-review`, `testing-strategy`, `qa-engineer`, `security-engineer`, `evaluation-agent`, `poc-orchestrator`,
  `/evaluate-poc`, `/security-audit`) and `experimental` (`tech-lead`, `orchestrator`, `/code-review`,
  `rapid-prototyping`, `poc-evaluation`).
- **Corpus counts, majority practice and golden-coupling convenience.** None of them is relied on (ADR-008 Validation
  3).

## 2. Summary

| Slice | Step that fired | Outcome | Files touched (if the notes are applied) |
|---|---|---|---|
| **P40 S2**: Implementation gate, non-security findings | **A** (P3a) | **Jointly satisfiable.** The gate's one verdict is the most restrictive that `validation-gates` § Verdict Rules or `code-review` § VERDICT Format for Validation Gates requires. Note recommended | `skills/validation-gates/SKILL.md` (N1, recommended); `skills/code-review/SKILL.md` (N2, optional) |
| **P40 S3**: Integration gate | **A** (P3a) | **Jointly satisfiable.** The same rule, across `validation-gates`, `testing-strategy` and `qa-engineer`. Note recommended | `skills/validation-gates/SKILL.md` (N1, shared with S2); `skills/testing-strategy/SKILL.md` (N3, optional) |
| **P40 S4**: Security gate, medium and low findings | **A** (P3a) | **Jointly satisfiable.** "owners and remediation windows" specialises the remediation plan (D4) | none. Any edit to `security-engineer.md` belongs to FU-6 |
| **P43**: two binary PoC verdicts | **E** (P5): Step A fails, and B, C and D do not decide | **Escalate** to the user (§7) | none (held under P5 Form 3) |

**Escalations:** one (P43). A contingent question for S2 and S3 is in §8.

## 3. D5 record: P40 S2, Implementation gate, non-security findings

| Field | Content |
|---|---|
| **Subject (D3)** | The criterion that turns the non-security findings of an Implementation-gate review into the gate's one verdict value (`PASS` / `CONDITIONAL_PASS` / `FAIL`). |
| **Parties** | `skills/validation-gates/SKILL.md` (skill) and `skills/code-review/SKILL.md` (skill). Also `agents/tech-lead.md` (agent), which summarises `code-review`. |
| **Step that fired** | **A (P3a): jointly satisfiable.** |
| **Declared scope relied on** | None. Step A is rank-free. |
| **Amendment** | N1 (recommended) and N2 (optional), §9. Both are notes stating the relationship. Neither ranks anything. |
| **Maturity** | Not relied on. |

### 3.1 Clauses (verbatim, `a54bbba` line numbers)

**`validation-gates/SKILL.md`:**
- `:33` "Every gate MUST produce a verdict in this format:"
- `:66` "| **PASS** | No critical or high findings, no security finding graded medium, and none of the security findings
  excluded below. Medium/low findings noted but non-blocking. |"
- `:67` "| **CONDITIONAL_PASS** | No critical findings, and none of the security findings excluded below. Other high
  findings have documented mitigations. Medium/low with clear remediation plan. … |"
- `:68` "| **FAIL** | Any critical finding unresolved, OR any high finding without mitigation, OR any security finding
  excluded below. Work must return to the implementer. |"
- Severity tiers:
  - `:76` "| `critical` | Broken functionality, security vulnerability, data loss risk. Blocks all progress. |"
  - `:77` "| `high` | Significant defect or design flaw. Must be addressed before release; …"
  - `:78` "| `medium` | Quality concern or technical debt. Should be addressed, can be tracked. |"
  - `:79` "| `low` | Minor style issue, optimization opportunity, or suggestion. |"

**`code-review/SKILL.md`:**
- `:114` "Every review MUST conclude with a structured verdict that downstream gates (CI/CD, release) can consume:"
- `:120` "… Both record the gate's one verdict, so `result=` carries the same value as the block's `### Verdict:`."
- `:126` "| `PASS` | No must-fix findings. Code is merge-ready. | Pipeline proceeds. |"
- `:127` "| `CONDITIONAL_PASS` | Only should-fix findings. Code may merge with tracked follow-ups. | …"
- `:128` "| `FAIL` | One or more must-fix findings. Code must not merge. | Pipeline halts. Re-review required after
  fixes. |"
- Severity Guide:
  - `:96` "| … Must Fix | Bug, security issue, data loss risk | Block merge |"
  - `:97` "| … Should Fix | Performance, maintainability concern | Request changes |"
  - `:98` "| … Nice to Have | Style, minor improvement | Comment only |"

**`tech-lead.md`:**
- `:29–30` "See skill `code-review` for the full structured checklist, feedback format, and VERDICT conventions this section
  summarizes."
- `:68` "… All three record the same verdict. …"
- `:96` "- **PASS**: Code meets all quality gates, architecture conformance confirmed, merge permitted."

**One executor is bound by both skills:**
- `validation-gates:26` "| **Implementation** | Tech Lead | After code complete, before merge | …"
- `implementation/AGENTS.md:59–60` "agents MUST check applicable skills in `knowledge/skills/` …"
- `implementation/AGENTS.md:67` "| Phase or validation transition | `validation-gates`, `checkpoint-protocol` |"
- `orchestrator.md:206` "- Delegate to `@tech-lead`: "Review implementation against architecture-v1.md. Produce VERDICT.""

### 3.2 Step A analysis

**MUSTs involved:**
- `validation-gates:33`. The Verdict Rules are a subsection of that § Verdict Format.
- `code-review:114`.
- `code-review:120` and `tech-lead:68`, which require one value across all renderings.
- `implementation/AGENTS.md:59–60` with `:67`, which make the Tech Lead apply `validation-gates` at this gate, while
  `tech-lead:29–30` takes the VERDICT conventions from `code-review`.

**Exclusivity (P3a step 2):**

| Row | Requires | Permits only if | Exclusive word against a stricter verdict? |
|---|---|---|---|
| `validation-gates:68` FAIL | FAIL on an unresolved critical, a high without mitigation, or an excluded security finding | — | No |
| `validation-gates:66` PASS | — | its conditions hold | No. "noted but non-blocking" is row-local (see below) |
| `validation-gates:67` CONDITIONAL_PASS | — | its conditions hold | No |
| `code-review:128` FAIL | FAIL on one or more must-fix findings | — | No |
| `code-review:126` PASS | — | no must-fix finding | No |
| `code-review:127` CONDITIONAL_PASS | — | "Only should-fix findings" | "Only" bars CONDITIONAL_PASS when a must-fix exists, which is a *less* strict verdict. It does not bar FAIL |

Both skills fix the same value set, so neither is a rival value set.

**One-value test (P3a step 3), on four inputs:**

| Input | `validation-gates` | `code-review` | One value meeting both |
|---|---|---|---|
| (a) G1's example: a lone maintainability concern (`medium`; Should Fix) | permits PASS or CONDITIONAL_PASS | permits CONDITIONAL_PASS (and, literally, PASS: "No must-fix findings") | **CONDITIONAL_PASS** |
| (b) A significant bug with a documented mitigation (`high`; Must Fix, "Bug") | permits CONDITIONAL_PASS, does not forbid FAIL | requires FAIL | **FAIL** |
| (c) A significant design flaw that is not a bug, with no mitigation (`high`; Should Fix, "maintainability concern") | requires FAIL | permits CONDITIONAL_PASS, does not forbid FAIL | **FAIL** |
| (d) A minor bug (`medium` or `low`; Must Fix, "Bug") | permits PASS or CONDITIONAL_PASS, does not forbid FAIL | requires FAIL | **FAIL** |

In every case one value meets both. That value is the most restrictive one either requires. No clause requires PASS or
CONDITIONAL_PASS, and none forbids FAIL. Step A holds.

### 3.3 The worked example's questions, answered

- **Are the verdict tables exclusive definitions or necessary conditions?** Necessary conditions for PASS and
  CONDITIONAL_PASS, and requirements for FAIL (§1.1). `tech-lead:96` reads the same way: PASS is given when "Code
  meets all quality gates".
- **Does "noted but non-blocking" exclude CONDITIONAL_PASS?** **No.**
  - `validation-gates`' own CONDITIONAL_PASS row admits "Medium/low with clear remediation plan" (`:67`).
  - CONDITIONAL_PASS does not block: it "proceeds with tracked conditions added to the task list"
    (`implementation/AGENTS.md:55`).
  - The phrase does not exclude FAIL either. It describes what a PASS tolerates, and the same file makes some
    medium-graded findings FAIL (`:70`: an omitted required security control, with no grade limit).
- **Is a verdict-rules table "process" or "review content" under `validation-gates`' Rails?** This question is **not
  reached**, because Step A fired. It is answered in §8 for the contingent path. The answer is "process and format",
  so `validation-gates` does not concede the subject.
- **G1's example is not a two-value case.** `gate-verdict-consistency-v1.md` §7 compared `validation-gates`' most
  lenient verdict with `code-review`'s. CONDITIONAL_PASS meets both.

### 3.4 Observation: the security piece that P39 left to P40

`conditional-pass-semantics-v4.md` §11 C4 and §12 left "`code-review:96`/`:128` against a security MEDIUM at the
code-review gate" to P40 (D1). The T584 brief treats S1 as settled. Applying the same Step A analysis:
- `code-review` requires FAIL for any "security issue" (`:96`, `:128`).
- `validation-gates:70` says a security finding graded medium "yields at best CONDITIONAL_PASS". It permits that
  verdict and does not forbid FAIL.
- `security-guidelines.md:183` reads "`MEDIUM` findings must have a remediation plan before merge". That is a
  precondition for merging, and it is met a fortiori when the merge is blocked.

The result is FAIL, which is stricter than tier 1 requires. A Tech Lead waiver may lift a FAIL that no excluded
security finding caused, and the MEDIUM finding's remediation plan survives that waiver (`code-review:150`, P39 Q1).
Nothing relaxes a security check. **No amendment.** This is recorded here as a note, not as a fifth ruling (§12,
correction 2).

## 4. D5 record: P40 S3, Integration gate

| Field | Content |
|---|---|
| **Subject (D3)** | The criterion that turns test results, coverage and non-security defects at the Integration gate into the gate's one verdict value. Security scan rows are S1, which is settled and excluded here. |
| **Parties** | `skills/validation-gates/SKILL.md` (skill), `skills/testing-strategy/SKILL.md` (skill) and `agents/qa-engineer.md` (agent). |
| **Step that fired** | **A (P3a): jointly satisfiable.** |
| **Declared scope relied on** | None. Step A is rank-free. |
| **Amendment** | N1 (recommended, shared with S2) and N3 (optional), §9. |
| **Maturity** | Not relied on. |

### 4.1 Clauses (verbatim)

**`validation-gates/SKILL.md`:** `:66–68`, as quoted in §3.1. `:27` "| **Integration** | QA Agent | After feature
merge, before release | …"

**`testing-strategy/SKILL.md`:**
- `:15–18` (Rails): "Does not execute tests or produce the QA gate verdict itself — the agent executing the QA gate
  runs the strategy this skill defines and emits the actual `PASS`/`CONDITIONAL_PASS`/`FAIL` verdict against it. This
  skill defines the plan and thresholds a gate is judged against, not the judgment."
- `:227` "| `PASS` | All tests pass, coverage thresholds met, no critical defects. | Pipeline proceeds to next stage. |"
- `:228` "| `CONDITIONAL_PASS` | Minor test failures (non-critical paths), coverage within 5% of threshold. | …"
- `:229` "| `FAIL` | Critical test failures, coverage below threshold by >5%, or security test failures. | Pipeline halts.
  Defects must be fixed and tests re-run. |"
- `:233` "The following coverage thresholds directly determine the QA gate verdict:"
- `:237` "| **Unit test coverage** | ≥ 80% | 75–79% | < 75% |"
- `:239` "| **E2E critical path pass rate** | 100% | N/A (critical paths must pass) | < 100% |"

**`qa-engineer.md`:**
- `:107` "- New features: minimum 80% line coverage"
- `:114–120` "1. Every QA run must end with a gate verdict: … 2. `fail` conditions: - Any unresolved critical defect. -
  Missing coverage for critical acceptance criteria. 3. `conditional_pass` conditions: - Only medium/low issues with
  explicit mitigation and owner."

**One executor is bound by all three:**
- `validation-gates:27`;
- `implementation/AGENTS.md:67`;
- `orchestrator.md:209–211` "- Delegate to `@qa-engineer`: … - The coverage thresholds and
  `PASS`/`CONDITIONAL_PASS`/`FAIL` criteria this VERDICT is judged against are defined by skill `testing-strategy`, not
  invented ad hoc per delegation.";
- `testing-strategy:15–18` ("the agent executing the QA gate … emits the actual … verdict against it").

### 4.2 Step A analysis

**MUSTs involved:**
- `validation-gates:33`;
- `testing-strategy:219` ("`result=` carries the same value as the block's `### Verdict:`");
- `qa-engineer:114` ("Every QA run must end with a gate verdict");
- `implementation/AGENTS.md:67`.

**Exclusivity:**
- **FAIL rows are requirements.** These are `validation-gates:68`, `testing-strategy:229` and the `:237`–`:241` FAIL
  column, and `qa-engineer:116–118`.
- **PASS and CONDITIONAL_PASS rows are necessary conditions.** `qa-engineer:120`'s "Only medium/low issues" bars
  CONDITIONAL_PASS when a high issue is open. It does not bar FAIL.
- **"directly determine" (`testing-strategy:233`) is not exclusive.** It is not a P3a step 2 word. `testing-strategy`'s
  own PASS row already takes a non-threshold input ("no critical defects"), and its own test-plan template requires
  "- [ ] No critical or high bugs open" (`:116`).
- `qa-engineer` defines no PASS row, so it forbids no PASS beyond its fail and conditional_pass conditions.

**One-value test:**

| Input | `validation-gates` | `testing-strategy` | `qa-engineer` | One value meeting all three |
|---|---|---|---|---|
| (a) All tests pass and coverage is met, but a critical acceptance criterion has no test | permits any; the finding is graded by the executor | permits PASS, does not forbid FAIL | requires `fail` (`:118`) | **FAIL** |
| (b) All tests pass and coverage is met; one open high non-security defect, with mitigation and owner | permits CONDITIONAL_PASS; bars PASS | permits PASS | bars `conditional_pass` (`:120`, "Only medium/low") | **FAIL** |
| (c) Unit coverage 77%, no defects | permits CONDITIONAL_PASS with a plan | bars PASS (`:237`), permits CONDITIONAL_PASS | permits `conditional_pass` if the shortfall, which is below its own 80% requirement (`:107`), is recorded with mitigation and owner | **CONDITIONAL_PASS** |
| (d) Unit coverage 70% | does not forbid FAIL | requires FAIL (`:237`) | does not forbid FAIL | **FAIL** |

Step A holds. Input (b) shows the practical effect: at the Integration gate, an open high defect yields FAIL even with
a mitigation, because `qa-engineer` admits a conditional pass only for medium and low issues. That is `qa-engineer`'s
existing rule, not a new one.

### 4.3 The worked example's question, answered

- **Does `orchestrator.md`'s routing count as self-placement for parties that do not name each other (D2 source 4)?**
  This is **not reached**, because Step A fired. The answer, for the contingent path in §8, is **No.**
  - P3b fires only on "one document's own text" placing the subject with "the other document".
  - Q1 and Validation 5 require "the governed document's own sentence".
  - `orchestrator.md:210–211` is a third document's assignment. Neither `qa-engineer` nor `testing-strategy` is the
    author of that sentence.

## 5. D5 record: P40 S4, Security gate, medium and low findings

| Field | Content |
|---|---|
| **Subject (D3)** | What a security finding graded medium or low must carry for the Security-gate verdict to be CONDITIONAL_PASS. |
| **Parties** | `agents/security-engineer.md` (agent) and `skills/validation-gates/SKILL.md` (skill). They are checked against tier 1: `security-guidelines.md`. `/security-audit` (`agent: "security-engineer"`) governs that agent's output when it is run through the command (P2). It is read for consistency, not ranked. |
| **Step that fired** | **A (P3a): jointly satisfiable.** The clauses specialise one another (D4). |
| **Declared scope relied on** | None. |
| **Amendment** | None. Any wording change in `security-engineer.md:152–153` belongs to FU-6 (§10). |
| **Maturity** | Not relied on. |

### 5.1 Clauses (verbatim)

**`security-engineer.md`:**
- `:151` "1. Every audit must end with a gate verdict: `pass`, `conditional_pass`, or `fail`."
- `:152` "2. `fail` when any unresolved critical or high severity vulnerability remains."
- `:153` "3. `conditional_pass` only when medium/low findings have owners and remediation windows."
- `:177` "- [Finding ID]: owner=@[who], remediation=[what], deadline=[when]"
- SLA table (FU-6, noted only):
  - `:83` "| **MEDIUM** | Moderate risk, defense-in-depth gap | Fix within current sprint |"
  - `:84` "| **LOW** | Minor issue, best-practice deviation | Fix within next sprint |"

**`validation-gates/SKILL.md`:**
- `:67` "… Medium/low with clear remediation plan. …"
- `:70` "… A security finding graded medium yields at best CONDITIONAL_PASS: its remediation plan (owner, fix, deadline) is
  recorded as a tracked condition with the verdict, before the affected work's next merge … A security finding graded
  low is not a condition: it is tracked as technical debt (`security-guidelines.md` § Security Review Workflow; …)."
- `:28` "| **Security** | Security Agent | Before any release | …"

**Tier 1, `security-guidelines.md`:**
- `:183` "4. `MEDIUM` findings must have a remediation plan before merge"
- `:184` "5. `LOW` findings are tracked as technical debt"

**`/security-audit` (`commands/security-audit.md`):**
- `:67` "… If any MEDIUM finding exists, the verdict is at best CONDITIONAL_PASS, with a remediation plan (owner, fix,
  deadline) listed as a condition for each MEDIUM finding. PASS requires no CRITICAL, HIGH or MEDIUM finding."
- `:46` "- **LOW**: Hardening recommendation, add to backlog"

### 5.2 Step A analysis

**MUSTs involved:** `security-engineer:151`; `security-engineer:160` ("Every security audit MUST conclude with a
structured verdict"); `validation-gates:33`; `security-guidelines:183–184`. One executor emits one verdict
(`validation-gates:28`; `orchestrator.md:214`; `/security-audit:3`).

**Exclusivity.** `security-engineer:153`'s "only when" is a necessary condition for `conditional_pass`. It does not bar
FAIL. `security-engineer:152`'s "`fail` when" is a non-exclusive trigger.

**One-value test:**

| Input | `security-engineer` | `validation-gates` and tier 1 | One value |
|---|---|---|---|
| (a) One security MEDIUM, with an owner, a fix and a deadline | permits `conditional_pass` | bars PASS; requires the plan recorded as a condition | **CONDITIONAL_PASS** |
| (b) Security LOWs only, with no owner or window | bars `conditional_pass`; requires no `fail` | permits PASS (a low "is not a condition"; it is tracked as debt) | **PASS** |
| (c) One security MEDIUM, with no plan yet at verdict time | `conditional_pass` needs an owner and a window | requires the plan (owner, fix, deadline) to be recorded with the verdict | **CONDITIONAL_PASS**, once the executor records the plan, which meets both |
| (d) A required security control omitted, graded medium | does not forbid FAIL | requires FAIL (`:70`) | **FAIL** |

Step A holds.

### 5.3 The worked example's question, answered

**Does "owners and remediation windows" specialise "clear remediation plan", or contradict it?** It **specialises**
it (D4: "uses values that nest inside the other's").
- **Medium findings.** Owner is owner, and remediation window is deadline. `security-engineer`'s own Conditions
  template (`:177`) also carries the fix, as "remediation=[what]". The values nest in `validation-gates`' "remediation
  plan (owner, fix, deadline)" and in tier 1's "remediation plan".
- **Low findings.** The clause adds an owner and a window to an item that `validation-gates` and tier 1 track as debt.
  That fills a slot the other text leaves open. Nothing in `security-engineer` makes a low finding a CONDITIONAL_PASS
  *condition*. If its Conditions list were read that way, it would contradict `validation-gates:70` ("A security
  finding graded low is not a condition"), but its text does not require that reading.

## 6. D5 record: P43, two binary PoC verdicts

| Field | Content |
|---|---|
| **Subject (D3)** | Which verdict is the PoC's one hypothesis outcome (an actor): the verdict `rapid-prototyping`'s `[CHECKPOINT]` reports at a trigger, or the one the evaluation returns (`poc-evaluation`'s `[VERDICT]` `result=`, rendered as `/evaluate-poc`'s `Status` and `evaluation-agent`'s Verdict), when the two differ. |
| **Parties** | `skills/rapid-prototyping/SKILL.md` and `skills/poc-evaluation/SKILL.md` (skill against skill). `agents/evaluation-agent.md` and `agents/poc-orchestrator.md` also bear on the subject. |
| **Step that fired** | **E (P5): escalate.** Step A fails. Steps B, C and D do not decide. |
| **Declared scope relied on** | None decides. The texts examined at Step D are quoted in §6.4. |
| **Amendment** | None. Under P5 Form 3, neither document is amended on the subject until the user decides (§7). |
| **Maturity** | Not relied on. |

### 6.1 Clauses (verbatim)

**`rapid-prototyping/SKILL.md`:**
- `:122` "[CHECKPOINT] id=poc-{name}-validation | hypothesis="{hypothesis text}" | evidence=[{evidence items}] |
  debt_tags={count} | verdict=validated|invalidated|in_progress | artifact_refs=[poc-{name}-v{N}] | next=[{next
  steps}]"
- `:127` "**Verdict values:** `in_progress` is allowed only at a milestone checkpoint, before any of the checkpoint
  triggers below has fired. At a trigger, the verdict is binary: `validated` or `invalidated` (`poc-guidelines.md`
  § Hypothesis-First Validation, Rule 4). A hypothesis not validated when the time-box expires is `invalidated` (Rule
  3). A partial result is `invalidated`, and `next=` names a follow-up PoC with refined criteria."
- `:135` "- All success criteria have been tested (regardless of outcome)."
- `:136` "- A showstopper is discovered that invalidates the hypothesis."
- `:137` "- The PoC time-box expires (document whatever evidence exists)."

**`poc-evaluation/SKILL.md`:**
- `:40` "Every PoC evaluation MUST conclude with a structured verdict that integrates with the gate protocol:"
- `:43` "[VERDICT] gate=poc-evaluation | result=VALIDATED|INVALIDATED | evidence_strength=strong|moderate|weak | …"
- `:46` "This line is the one-line rendering of the evaluation's single verdict: a PoC either validates or invalidates its
  hypothesis (`poc-guidelines.md` § Hypothesis-First Validation, Rule 4). …"
- `:115` "- The verdict is `VALIDATED` only if every success criterion defined in the PoC artifact was tested and met by
  the PoC's deadline. Post-hoc criteria cannot stand in for an untested one."
- `:117` "- Otherwise, if any such criterion is "Not Tested" or rests only on weak evidence, the verdict is `INVALIDATED`
  with `Evidence strength: weak`, and the Recommended next step names a follow-up PoC with refined criteria. …"

**Also bearing on the subject:**
- `/evaluate-poc:31` "- **Status**: VALIDATED | INVALIDATED"
- `evaluation-agent:16` "- Verdict: Validated | Invalidated"
- `evaluation-agent:47` "**Inputs**: The PoC's stated hypothesis, success signal, and failure criteria, plus the observed
  evidence …"
- `poc-orchestrator:38` "1. Delegate to `@evaluation-agent` for hypothesis verdict"
- `poc-orchestrator:56` "11. **Evaluation** — `@evaluation-agent`: hypothesis verdict"
- `poc-orchestrator:65` "… If the timebox expires, record the verdict `poc-guidelines.md` Rule 3 requires, but do not close
  the PoC. …"
- `poc-orchestrator:101` "- Hypothesis verdict (Validated / Invalidated)"

**Tier 1, `poc-guidelines.md`:**
- `:55` "3. **Time-box strictly** — Every PoC has a hard deadline. If the hypothesis isn't validated by the deadline, it
  fails"
- `:56` "4. **Binary outcome** — A PoC either validates or invalidates the hypothesis. …"
- `:124–125` "## Result" / "[VALIDATED / INVALIDATED]"

### 6.2 Step A analysis: fails

**MUSTs involved:** `poc-evaluation:40`; `rapid-prototyping:127` ("At a trigger, the verdict is binary"); tier-1 Rule
4, which `rapid-prototyping:127` and `poc-evaluation:46` both invoke for their own verdict.

**Exclusivity.** Both fix the same binary set for the outcome. Case is not normative, per
`gate-verdict-consistency-v1.md` G8. Neither line excludes the other as a format, so both can be emitted.

**One-value test: it bites.** The two clauses bind **different emitters at different times**:
- the prototyping agent reports at a trigger;
- the evaluator decides later.

Each emitter, obeying only its own clause, can record a different value for the one outcome. At the trigger "All
success criteria have been tested", `rapid-prototyping` permits `validated`. Nothing in it applies `poc-evaluation`'s
evidence rules, and its own Rails says it "does not run the PoC evaluation". The evaluation must return `INVALIDATED`
under `:115` or `:117` where a criterion is post-hoc or rests on weak evidence.

**The reverse case.** After a showstopper trigger (`:136`), the checkpoint is `invalidated`. `poc-evaluation` grades
success criteria only. Its `:115` is a necessary condition, so it can still return `INVALIDATED`, but nothing in it
requires that.

**The rescue reading fails on the texts.** Step A would hold only if the checkpoint verdict were a report that the
evaluation supersedes. `:125` ("This line is a status report, not a checkpoint file") contrasts the line with a
*checkpoint file*, which was T574 F6's subject. It says nothing about the verdict being provisional, and it postdates
the recording (§1.2).

### 6.3 Steps B and C: do not fire

- **Step B (P1).** Rules 3–4 and the scorecard's single `## Result` fix the *value* of the outcome: binary, and failed
  at the deadline. No tier-1 sentence names the *issuer*. Neither skill contradicts Rule 3 or Rule 4 on its own; the
  contradiction exists only between the two skills. P1(a), "the contradiction must be quotable" from the tier-1 text,
  is not met. **Confirmed: P1 fixes the constraints, not the issuer.**
- **Step C (P2).** `/evaluate-poc`'s `Status` governs the evaluation's rendering when the evaluation runs through that
  command. But `rapid-prototyping` is not applied under `/evaluate-poc`: the command does not name it, invoke it or
  import it, so P2(a) fails. The checkpoint line is not the command's output, so P2(b) fails as well.

### 6.4 Step D: no self-placement

**`rapid-prototyping:12` (Rails).** "… and does not run the PoC evaluation (the poc-evaluation skill). …"

**Does this Rails sentence disclaim the outcome, or only the activity? The activity only.**
- **Its words.** "run" names an activity. The sentence is built in parallel with "Does not scan … or write the debt
  scorecard (the technical-debt-tracking skill scans for them …)", which is activity plus owner.
- **The same file.** `:127` has the skill issue a Rule-4 binary verdict at every trigger, and no sentence in the file
  makes that verdict provisional or subordinate to the evaluation. Reading the Rails as disclaiming the outcome would
  have to infer that. D2 forbids inference: "Quotable only".
- **Its author.** T574 drafted the sentence (E8) and, in the same artifact, recorded O2 as open: "No text says which
  one is the PoC's outcome, or that the checkpoint's verdict is provisional" (`poc-skill-command-overlaps-v1.md` §13).
- **Its date.** It postdates the recording of O2 (§1.2).

**`rapid-prototyping:12` and `:125`, "reported to the orchestrator".**
- These sentences make the line an input to the orchestrator's *checkpoint* (checkpoint content), which is not the
  PoC outcome.
- "the orchestrator" names a role, not a document.
- A chain through `poc-orchestrator:38` to `evaluation-agent` would be multi-hop. That is not "the governed document's
  own sentence" (Validation 5).
- Both sentences postdate the recording.

**`poc-orchestrator:38`, `:56` and `:101`.**
- **Is `poc-orchestrator` a party? Yes.** By `:65` it records the Rule 3 verdict at timebox expiry.
- Its own text assigns the "hypothesis verdict" to `@evaluation-agent`. That is self-placement of `poc-orchestrator`
  under `evaluation-agent`, and the two do not conflict.
- It names neither `rapid-prototyping` nor `poc-evaluation`, so it does not place the subject between the two
  documents whose clauses conflict. A third document's assignment is not self-placement under Q1 (the same answer as
  §4.3).

**`poc-evaluation`.**
- Its description ("Assess proof-of-concept outcomes …"), `:12` ("The `[VERDICT]` line is the PoC track's hypothesis
  verdict …") and `:46` are claims made *by the governing candidate*. They are not a sentence of the governed document.
- `:12` and `:46` also postdate the recording.
- That "Assess proof-of-concept outcomes" reads as more specific than "scaffolding and integration patterns" is a
  scope comparison, and Q1 excludes it.

**Result.** Neither `rapid-prototyping` nor `poc-evaluation` has a sentence placing the subject with the other.
**P5.**

### 6.5 P5 Form

| Field | Value |
|---|---|
| **Blocker type** | `unclear_requirements` |
| **Severity** | `minor` (no PoC is live; P43 is a parked P2 item) |
| **Content** | The subject, both quotes and the failed steps, as above |
| **Step that failed to decide** | D. No self-placement sentence exists, and A has already failed |
| **Route proposed** | A one-off user decision (P5 Form 2, "as P36 did"). The question is §7 |
| **Hold** | `rapid-prototyping` and `poc-evaluation` are not amended on the subject until the user decides |

This is a ruling outcome, not a blocker of T584 (brief §5).

## 7. Escalation P43: the user question (for verbatim relay)

> **P43: when a PoC's two verdicts disagree, which one is the PoC's outcome?**
>
> **The subject.** A PoC can produce two binary verdicts on its hypothesis:
> - **The prototyping agent's checkpoint line.** `rapid-prototyping` says: "At a trigger, the verdict is binary:
>   `validated` or `invalidated` (`poc-guidelines.md` § Hypothesis-First Validation, Rule 4)." One of its triggers is
>   "All success criteria have been tested (regardless of outcome)."
> - **The evaluation's verdict.** `poc-evaluation` says: "The verdict is `VALIDATED` only if every success criterion
>   defined in the PoC artifact was tested and met by the PoC's deadline. Post-hoc criteria cannot stand in for an
>   untested one." and "if any such criterion is "Not Tested" or rests only on weak evidence, the verdict is
>   `INVALIDATED` …". This verdict is rendered as `/evaluate-poc`'s `Status` and `evaluation-agent`'s Verdict.
>
> `poc-guidelines.md` Rule 4 allows a PoC one outcome. The two can still disagree:
> - a checkpoint can say `validated` where the evaluation must say `INVALIDATED` (for example, on weak evidence);
> - after a showstopper, the checkpoint says `invalidated`, while an evaluation that looks only at success criteria
>   could find them all met.
>
> **Why ADR-008 could not decide it.**
> - The two clauses bind different agents at different times, so they can record two values for one outcome (Step A
>   fails).
> - `poc-guidelines.md` fixes the value (binary; failed at the deadline) but names no issuer (Step B).
> - The prototyping skill is not run under `/evaluate-poc` (Step C).
> - Neither skill has a sentence placing the outcome with the other (Step D). `rapid-prototyping`'s "does not run the
>   PoC evaluation (the poc-evaluation skill)" disclaims the *activity* of evaluating, not the outcome. Its author
>   recorded this question as open in the same document. `poc-orchestrator`'s "Delegate to `@evaluation-agent` for
>   hypothesis verdict" is a third document's routing, which your "Self-placement only" decision does not count.
>
> **Options.**
> 1. **The evaluation decides, and may only confirm or tighten the checkpoint (Recommended).**
>    - **The rule.** The PoC's outcome is the evaluation's verdict. The checkpoint verdict is the prototyping agent's
>      report and an input to the evaluation. The evaluation may turn a checkpoint `validated` into `INVALIDATED`. It
>      may not turn a trigger checkpoint's `invalidated` (showstopper, time-box, partial result) into `VALIDATED`; that
>      case needs a follow-up PoC with refined criteria (Rule 4).
>    - **Checks.** No check is relaxed: every invalidation rule in both skills survives.
>    - **Edits** (exact text drafted after your decision): a note in `rapid-prototyping` and one added rule in
>      `poc-evaluation`, plus the same rule in `evaluation-agent` so that both evaluation paths agree.
>    - **Not touched:** `/evaluate-poc` and every golden case. The `evaluate-poc` case quotes only the command and reads
>      only its own fixture.
>    - **Security:** none.
> 2. **The evaluation decides; the checkpoint is provisional.**
>    - **The rule.** The evaluation's verdict replaces the checkpoint's, whatever the checkpoint said.
>    - **Edits:** `rapid-prototyping` only.
>    - **Checks.** This relaxes a check. A PoC invalidated by a showstopper could be `VALIDATED` by an evaluation that
>      checks only success criteria. ADR-007 §5 ("Never resolve by relaxing a check") bars a ruling from doing this, so
>      it needs your explicit latitude.
> 3. **The checkpoint decides.**
>    - **The rule.** The trigger checkpoint is the outcome. The evaluation carries it forward and adds the production
>      recommendation.
>    - **Checks.** This relaxes `poc-evaluation`'s evidence rules (a `validated` on weak evidence would stand).
>    - **Edits:** it reverses `poc-orchestrator`'s and `evaluation-agent`'s routing of the "hypothesis verdict".
>    - **A gap remains.** `/evaluate-poc`'s `Status` could not be amended on a skill's strength (ADR-008 Validation 4),
>      so the command would still compute its own value. A further decision would be needed.
> 4. **Park it for a general ADR.**
>    - **Edits:** none.
>    - **Effect.** A PoC can keep two different binary outcomes in its records, against Rule 4's single outcome, until
>      the ADR lands.
>
> **Recommendation: option 1.** It is the only option that gives one outcome without relaxing either skill's check, and
> it matches the routing `poc-orchestrator` already uses.

## 8. Contingent question for S2 and S3 (relay only if the orchestrator rejects §1.1)

If the orchestrator rejects the reading in §1.1 and treats each verdict table as an exclusive definition, S2 and S3
fail Step A. For example, input (b) in §3.2 is CONDITIONAL_PASS under `validation-gates` and FAIL under `code-review`.
They then fall through as follows. **Under the reading I adopted, none of this is reached.**

### 8.1 Steps B, C and D on the contingent path

- **Step B.** No tier-1 sentence states the non-security criteria.
  - `implementation/AGENTS.md:52–55` fixes only the vocabulary and the effects.
  - `implementation/AGENTS.md:67` mandates checking `validation-gates` but contradicts no criterion.
  - `coding-standards.md:22–24` ("Violations surface during code review as Must Fix/Should Fix items in the
    `code-review` skill's checklist; they do not automatically block a merge unless the Tech Lead's VERDICT marks them
    Critical") is a Failure mode. D2 says "**Failure mode** is not scope", so P1(b) cannot be met.
- **Step C.** No command declares the criteria. `/code-review` declares `Status` and the Must Fix, Should Fix and Nice
  to Have counts (`commands/code-review.md:41–45`), not the mapping between them, so P2(b) fails. No command produces
  the Integration-gate verdict: `orchestrator.md:209` delegates the gate directly.
- **Step D, S2.**
  - **Is a verdict-rules table "process" or "review content" under `validation-gates`' Rails? "Process and format."**
    - The Rails at `:188` reads: "**Out of scope**: Performing the underlying implementation work being gated, or
      substituting for the gate executor's own domain expertise — this skill defines the verdict process and format,
      not the review content itself."
    - `### Verdict Rules` (`:62`) and `### Severity Definitions` (`:72`) are subsections of `## Verdict Format`
      (`:31`), which is the "format" the Rails says the skill defines.
    - The Rails pairs "review content" with "substituting for the gate executor's own domain expertise", that is,
      with doing the review. It does not pair it with the rule that turns graded findings into a verdict.
    - So `validation-gates` does not concede the subject.
  - **`code-review:120` ("Both record the gate's one verdict …") is about the rendering.** It makes the line carry the
    block's value, and it is silent on whose criteria compute that value. The artifact that ordered it said so
    directly: "They do not say whose criteria compute that value" (`gate-verdict-consistency-v1.md` §7 G1). It also
    postdates the recording (§1.2).
  - **`tech-lead:29–30` places VERDICT conventions with `code-review`.** That is a real self-placement, but between
    `tech-lead` and `code-review`, which do not conflict.
  - **Result: no self-placement between `validation-gates` and `code-review`. P5.**
- **Step D, S3.**
  - `testing-strategy:15–18` keeps "the plan and thresholds a gate is judged against". It gives away only "the
    judgment", to "the agent executing the QA gate", which is a role, not a named document.
  - `testing-strategy:207` ("Test results are a critical input to the **integration validation gate**") makes test
    results an input. It does not concede the thresholds, and `:233` claims them.
  - `qa-engineer` names neither skill.
  - `orchestrator.md:210–211` does not count (§4.3).
  - **Result: P5.**

### 8.2 The contingent user question (CQ-1)

> **CQ-1: when a gate has two sets of verdict rules, which one decides?**
>
> **The subject.** `validation-gates` states verdict rules for every gate, for example "**FAIL** | Any critical finding
> unresolved, OR any high finding without mitigation …". Other documents state their own rules for some gates:
> - `code-review` at the Implementation gate: "**FAIL** | One or more must-fix findings. Code must not merge.";
> - `testing-strategy` at the Integration gate: "**PASS** | All tests pass, coverage thresholds met, no critical
>   defects.";
> - `qa-engineer` at the Integration gate: "`conditional_pass` conditions: Only medium/low issues with explicit
>   mitigation and owner".
>
> Read as exclusive definitions, they can give one review two verdicts. For example, a significant bug with a
> documented mitigation is CONDITIONAL_PASS under `validation-gates` and FAIL under `code-review`.
>
> **Why ADR-008 could not decide it.**
> - No `AGENTS.md` or stable-instruction text sets these criteria.
> - No command declares them.
> - Neither document's own text hands the criteria to the other. `validation-gates`' Rails keeps "the verdict process
>   and format", and its rules sit under its Verdict Format section. `orchestrator.md`'s routing of the integration
>   criteria to `testing-strategy` is a third document's routing, which "Self-placement only" does not count.
>
> **Options.**
> 1. **The strictest applies (Recommended).**
>    - **The rule.** Every applicable rule set applies to the gate's one verdict. PASS needs every set to admit PASS;
>      CONDITIONAL_PASS needs every set to admit at least CONDITIONAL_PASS; otherwise the verdict is FAIL.
>    - **Checks.** No check is relaxed.
>    - **Edits:** the notes N1 to N3 in `adr-008-rulings-p40-p43-v1.md` §9.
>    - **Effect.** Some reviews get stricter. Any must-fix finding is FAIL. An unmitigated high finding is FAIL even if
>      it is graded "should fix". At integration, an open high defect is FAIL even with a mitigation.
> 2. **`validation-gates` decides.**
>    - **Edits:** `code-review`, `testing-strategy` and `qa-engineer` are amended to point to it.
>    - **Checks.** This relaxes checks: a mitigated significant bug becomes CONDITIONAL_PASS, a minor bug can PASS, and
>      a missing test for a critical acceptance criterion no longer forces FAIL. ADR-007 §5 bars a ruling from that, so
>      it needs your explicit latitude.
> 3. **Each gate executor's own documents decide at their gate.**
>    - **Edits:** `validation-gates` is amended to defer at the Implementation and Integration gates. It is a stable
>      skill whose frozen golden fixture copy would then lag the source; the case result does not change.
>    - **Checks.** This relaxes `validation-gates`' "unmitigated high finding is FAIL". The same latitude is needed.
> 4. **Park it for a general ADR.**
>    - **Edits:** none.
>    - **Effect.** Two-value verdicts stay possible until the ADR lands.
>
> **Recommendation: option 1.** It is also what ADR-008 Step A yields on the texts read as permissions and requirements.

## 9. Amendment list

These are notes only, under ADR-008 Step A ("At most a note stating the relationship"). **N1 is recommended. N2 and
N3 are optional and depend on N1.** For each edit, match the Before text by text, not by line number. Each Before text
occurs exactly once in its file, which I checked by reading each file in full (a `grep` count is still owed, §13).
`§` is U+00A7. No other non-ASCII characters are used.

### N1 (recommended): `implementation/knowledge/skills/validation-gates/SKILL.md`, before `### Severity Definitions` (`:72`)

````
Before:
### Severity Definitions

After:
**Criteria from the executor's own documents.** Other documents also state verdict criteria for two of the gates: skill `code-review` § VERDICT Format for Validation Gates (Implementation gate); skill `testing-strategy` § VERDICT Format for QA Gate and § Coverage Thresholds That Determine Gate Outcome, and the `qa-engineer` agent's § Validation Gate Protocol (Integration gate). They apply together with the rules above to the gate's one verdict. A PASS or CONDITIONAL_PASS row states what that verdict requires; it does not grant the verdict when another applicable criterion requires a stricter one. So the verdict is PASS only if every applicable set of criteria admits PASS, CONDITIONAL_PASS only if every one admits at least CONDITIONAL_PASS, and FAIL otherwise. None of them makes another less strict.

### Severity Definitions
````

**Covers:** S2 and S3. The Security gate is left out on purpose: S4 needs no note, and `security-engineer.md` is FU-6's
scope.

### N2 (optional): `implementation/knowledge/skills/code-review/SKILL.md`, before `### Artifact Version Awareness` (`:130`)

````
Before:
### Artifact Version Awareness

After:
These definitions apply together with skill `validation-gates` § Verdict Rules, which applies to the same verdict (§ Criteria from the executor's own documents there). Grade each finding on both scales, this skill's § Severity Guide and that skill's § Severity Definitions, and give the most restrictive verdict either requires. A Must Fix finding is `FAIL` even where that skill would admit `CONDITIONAL_PASS` for a high finding with a documented mitigation, and a high finding without a documented mitigation is `FAIL` even when it is graded Should Fix here.

### Artifact Version Awareness
````

### N3 (optional): `implementation/knowledge/skills/testing-strategy/SKILL.md:233`

````
Before:
The following coverage thresholds directly determine the QA gate verdict:

After:
The following coverage thresholds directly determine the QA gate verdict, together with skill `validation-gates` § Verdict Rules and the executing agent's own gate criteria; the verdict is the most restrictive that any of them requires (`validation-gates` § Verdict Rules, Criteria from the executor's own documents):
````

### Per-edit statements

| Edit | Upward amendment? (Validation 4) | Relaxes a check? (ADR-007 §5) | Touches security criteria? | Golden coupling |
|---|---|---|---|---|
| N1 | No. `validation-gates` is a skill, not tier 1, and no command is changed | No. It adds no permission and states that no set of criteria makes another less strict | It changes none, but it sits in § Verdict Rules beside them and reaches security findings at two gates, always toward the stricter verdict. **For routing, I classify it as touching; Security Engineer phrase check** | `validate-workflow-gate-verdict-sources` holds a fixture copy, frozen at `develop` `7be9926` (its `brief.md` Provenance). `check()` reads only `case_dir / "fixture"`. Within § Verdict Format, `_verdict_gate_kinds` reads only "every gate must produce a verdict" and the first `**Gate:**` line; N1 adds neither. **No quote, fixture or result changes.** The fixture copy lags the source, which its Provenance (pinned to a commit) already allows. Refreshing it would be optional and would need a grant |
| N2 | No | No | No | No open case cites or copies `skills/code-review` (brief §2.7) |
| N3 | No | No | No | No open case cites or copies `skills/testing-strategy` (brief §2.7) |

**No edit touches a command.** `code-review-conditional-pass-conditions-gap` and `code-review-fail-blocker-details`
(`commands/code-review.md`) and `evaluate-poc-verdict-debt-reconciliation` (`commands/evaluate-poc.md`,
`skills/poc-evaluation`) are untouched. Each `check()` I read reads only its own `fixture/` file. `agents/orchestrator.md`
is not edited.

**Mechanics for the implementing task** (not mine to run):
- regenerate with `node implementation/scripts/sync.mjs --root implementation` and
  `python3 implementation/scripts/generate-registry.py`, each followed by `--check`;
- declare the root drift exactly as `--print-drift` reports it: 7 paths for N1 alone, up to 21 with N2 and N3
  **(unverified)**;
- `scripts/scorecard.py --check` must match the current baseline;
- run `check-maturity.py --root implementation`.

## 10. Security touchpoint

- **No ruling weakens `security-guidelines.md`** or any Immutable Security Constraint. No ruling reopens P39. Under P39,
  a security finding never qualifies as a CONDITIONAL_PASS condition when it is graded critical or high, is a
  constraint breach, or is an omitted control. N1 restates that no set of criteria relaxes another, so it cannot be read
  as admitting one.
- **S4 needs no amendment.** `security-engineer:152–153` does not name the omitted-control class or the Q7 scope, and
  its SLA table (`:83–84`) sets sprint-based windows beside `validation-gates`' track rule. Both are **FU-6**. This
  ruling bears on FU-6 only by showing that Step A holds as the texts stand: `:152`'s trigger is non-exclusive, and
  `:153`'s "only when" is a necessary condition. **FU-6 is noted, not decided** (plan-102 §3).
- **N1 gets a Security Engineer phrase check before implementation** (§9).
- **§3.4 records the security piece P39 left to P40.** A security MEDIUM at the code-review gate is FAIL under
  `code-review:96`/`:128`. That is stricter than tier 1, and no amendment is made.

## 11. Golden coupling summary

| Candidate file | Amended here? | Open case | Quote changes? | Fixture changes? | Result changes? |
|---|---|---|---|---|---|
| `skills/validation-gates/SKILL.md` | N1 | `validate-workflow-gate-verdict-sources` (fixture copy) | No | No (frozen copy; it lags the source) | No |
| `commands/code-review.md` | No | `code-review-conditional-pass-conditions-gap`, `code-review-fail-blocker-details` | No | No | No |
| `agents/orchestrator.md` | No | `validate-workflow-gate-verdict-sources` (cited) | No | No | No |
| `skills/poc-evaluation/SKILL.md`, `commands/evaluate-poc.md` | No (P43 held) | `evaluate-poc-verdict-debt-reconciliation` | No | No | No |
| `skills/code-review`, `skills/testing-strategy` | N2, N3 (optional) | none | — | — | — |

Golden coupling was not a reason for any ruling (Validation 3).

## 12. Corrections to the brief and the records; observations

These are all `unclear_requirements`, severity `minor`.

1. **G1's example is not a two-value case** (§3.3). `gate-verdict-consistency-v1.md` §7 G1 and ADR-008's S2 row cite
   it. A lone maintainability concern is CONDITIONAL_PASS under both skills. The two-value cases G1 feared exist only
   under the exclusive-definition reading (§1.1, §8).
2. **The S1/S2 boundary.** The brief says S1 is settled, but `conditional-pass-semantics-v4.md` §12 lists
   "`code-review:96`/`:128` against a security MEDIUM at the code-review gate" under P40 (D1). §3.4 records it as a
   Step A note with no amendment. If the orchestrator wants a separate D5 record for it, §3.4 holds the content.
3. **ADR-008's line numbers at `dd7703b`** are stale in these places:
   - the `validation-gates` Rails is now `:188`, not `:186`;
   - the `testing-strategy` Out-of-scope sentence is `:15–18`, not `:14–18`;
   - `validation-gates:66–67` were rewritten by T582 (P39). The S4 phrase "Medium/low with clear remediation plan"
     survives in `:67`, and the security-specific medium and low rules are now in `:70`.

   Unchanged: `code-review:94–98`, `:120` and `:126–128`; `tech-lead:29–30`; `qa-engineer:116–120`;
   `security-engineer:152–153`; `orchestrator.md:210–211`; and every P43 line cited in the ADR.
4. **The breadth of the scope-gaming mitigation** (§1.2). It is outcome-neutral here. A future Step D ruling that
   relies on a scope sentence added by a follow-up task (for example `code-review:120` or `testing-strategy:219`) will
   need to know whether the mitigation's first sentence ("read as of the commit on which the conflict was first
   recorded") bars it, or only the second ("made in the same change as the ruling"). I recommend the orchestrator
   record a reading.

**Observations (not decided, same-file or out of scope):**
- **`code-review`'s own rows overlap.** For a lone should-fix finding, `:126` ("No must-fix findings") and `:127` both
  hold, and `:97`'s "Request changes" sits beside `:126`'s "merge-ready". This is a same-file question, outside ADR-008.
  Candidate for P41.
- **`coding-standards.md:22–24`'s "marks them Critical".** It is open to two readings: `tech-lead:53`'s "…
  Critical (must fix)", or `validation-gates`' `critical` tier. Under the first, it is jointly satisfiable with N1. It
  is not declared scope (D2), so it decides nothing here. Noted for whoever next edits `coding-standards`.

## 13. Unverified claims (need a shell)

1. `c0138a7` and `a54bbba` have identical `implementation/` trees. This is the orchestrator's statement.
2. Each Before text in §9 occurs exactly once in its file. I checked by reading the full file; a `grep -c` is owed.
3. At `24518f6`, `### Verdict Rules` was already nested under `## Verdict Format`. This is used only on the contingent
   path (§8.1). I inferred it from `gate-verdict-consistency-v1.md`'s citations of `:33`, `:62–68` and `:62–77`, which
   match today's layout.
4. `poc-orchestrator:38` existed at `1208790`, and `:65`'s timebox sentence postdates it. Neither is relied on.
5. No other knowledge file states Implementation, Integration or Security gate verdict criteria. I did not read
   `release-manager`, `receiving-code-review`, `poc-qa-engineer`, `poc-security-engineer`, `scaffolding-agent`,
   `integration-agent`, `release-workflow` or `ci-cd-pipeline`.
6. The root-drift path count for N1 to N3.

## 14. Blockers

**None.** The P43 escalation is a designed ruling outcome under P5, not a blocker of T584. ADR-008 applied as written
to all four slices.
