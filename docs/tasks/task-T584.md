# T584 — Rule P40 slices S2–S4 and P43 under ADR-008

**ID:** T584
**Owner:** solution-architect
**Status:** done
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-07
**Based on:**
- `docs/plans/plan-102-adr-008-rulings-p40-p43.md`
- `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted 2026-10-02), especially § Definitions (D1–D5),
  P1–P5, § Order of application, § Worked examples (P40, P43) and § Validation
- `docs/decisions/ADR-007-command-contract-authority.md` (Accepted)
- `docs/artifacts/gate-verdict-consistency-v1.md` (§13.3, G1: the origin of P40)
- `docs/artifacts/poc-skill-command-overlaps-v1.md` (§16.3, O2: the origin of P43)
- `docs/artifacts/conditional-pass-semantics-v4.md` (the P39 ruling, applied by T582; it settles P40 slice S1)
- The user's instruction of 2026-10-07: "Continue with the Recommended next step", where the recommended step was a
  ruling task for P40 S2–S4 and P43 under ADR-008, with no knowledge-file edits until the user approves.

## 1. What and why

ADR-008 is accepted, so the two items that waited on it are schedulable:

- **P40**: the gate documents use different verdict *criteria*. Slice S1 (security findings at any gate) is settled by
  T580/T582. **Rule S2, S3 and S4.**
- **P43**: two binary PoC verdicts (`rapid-prototyping`'s checkpoint verdict and `poc-evaluation`'s `[VERDICT]`) can
  differ for one PoC. **Rule which one is the PoC's outcome, or escalate.**

ADR-008's worked examples name where each slice enters the procedure and the question its ruling must answer. They
"decide nothing". Your job is to decide them, slice by slice, strictly by ADR-008.

**Decision only.** Write exactly one file: your artifact. Edit no knowledge file, test, ledger or other document. The
orchestrator verifies your ruling. The user sees every escalation before anything is implemented, and any amendment you
propose is implemented in a separate task.

## 2. Output

`docs/artifacts/adr-008-rulings-p40-p43-v1.md`, with:

1. **One D5 ruling record per slice**: P40 S2, P40 S3, P40 S4, and P43. Each record contains:
   - the subject (D3);
   - both clauses, quoted verbatim with file and line **as they stand on `develop` `a54bbba`**. T582 moved lines in
     `validation-gates`, `code-review` and `tech-lead`, so the ADR's `dd7703b` line numbers are stale. Re-read every
     cited line.
   - the Step A analysis: which MUSTs are involved, whether either is exclusive, and the mandatory one-value test
     (P3a step 3);
   - the step that fired;
   - for P1–P3, the declared-scope text relied on, quoted;
   - the amendment (exact before/after text and target file) or "none";
   - an explicit statement that maturity was not relied on.
2. **Step D only by self-placement (ADR-008 Q1, Validation 5).** A Step D ruling must quote the governed document's
   *own* sentence that places the subject with the governing document. Scope breadth, specificity or nesting alone
   never decides. If no such sentence exists, the slice **escalates (P5)**. Escalation is a designed outcome, not a
   failure.
3. **The questions the worked examples pose, each answered explicitly**, for example:
   - S2: Is a verdict-rules table "process" or "review content" under `validation-gates`' Rails?
   - S3: Does `orchestrator.md`'s routing count as self-placement for parties that do not name each other (D2 source
     4)?
   - P43: Does `rapid-prototyping`'s Rails sentence disclaim the *outcome* or only the *activity* of evaluating?
4. **For each P5 escalation, a user question**: the subject, both quotes, why Steps A–D did not decide it, two to four
   concrete options with their consequences, and your recommendation. The orchestrator relays it verbatim.
5. **An amendment list** (if any): exact edits with file, anchor text, before and after. State for each edit that it is
   not an upward amendment (Validation 4) and does not relax a check (ADR-007 §5, "Never resolve by relaxing a check").
6. **Security touchpoint.** S4 concerns the security gate. If any amendment touches security criteria, say so; it then
   gets a Security Engineer review before implementation. Under P39 a security finding never qualifies as a
   CONDITIONAL_PASS condition. No ruling may weaken `security-guidelines.md` or any Immutable Security Constraint.
7. **Golden coupling.** The orchestrator pre-computed which open golden cases cite or hold fixtures of the candidate
   files (held-out pruned). Read the listed cases by path. For each amendment, state whether it would change a quote,
   a fixture or a case result:

   | Candidate file | Open golden cases that cite it or hold a fixture copy |
   |---|---|
   | `skills/validation-gates/SKILL.md` | `validate-workflow-gate-verdict-sources` (fixture copy) |
   | `commands/code-review.md` | `code-review-conditional-pass-conditions-gap`, `code-review-fail-blocker-details` |
   | `agents/orchestrator.md` | `validate-workflow-gate-verdict-sources` (cited) |
   | `skills/poc-evaluation/SKILL.md`, `commands/evaluate-poc.md` | `evaluate-poc-verdict-debt-reconciliation` |
   | `skills/code-review`, `skills/testing-strategy`, `agents/{qa-engineer,security-engineer,tech-lead,evaluation-agent,poc-orchestrator}`, `skills/rapid-prototyping` | none |

   All cases are under `tests/golden/open/<case>/`. Golden-coupling convenience is never a reason for a ruling
   (Validation 3).
8. **A short summary table**: slice, step that fired, outcome (jointly satisfiable / amend / escalate), and files
   touched.

## 3. Constraints

- **Read access:** the whole repo except `tests/golden/held-out/` (never open it), `.env*`, credential and key files.
  Knowledge sources live under `implementation/knowledge/`.
- **Write access:** your artifact only, plus this brief's `**Status:**` line (set it to `in_review` when done).
- You have no shell. Do not commit, push or merge. The orchestrator commits your artifact after verifying it.
- Never re-decide P39 (T580) or the verdict *format* (T572). Take both as inputs.
- Quote verbatim. Mark every omission with "…". Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Exactly one file is written: `docs/artifacts/adr-008-rulings-p40-p43-v1.md`, with `Based on:` naming its inputs.
2. Four D5 records (S2, S3, S4, P43). Each names one step, and each quote matches `a54bbba` verbatim.
3. No ruling relies on maturity, corpus counts, majority practice or golden-coupling convenience.
4. Every Step D outcome quotes a self-placement sentence. Every slice without one escalates, with a user question that
   meets §2.4.
5. Every amendment has exact before/after text and is neither upward nor relaxing.
6. Golden coupling is stated per amendment.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). An ADR-008 P5 escalation is not a blocker of this task; it is a ruling outcome
recorded in the artifact. If ADR-008 itself seems unable to apply as written, stop and report it as
`unclear_requirements`. Do not work around it.
