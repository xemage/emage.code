# Case: evaluate-poc-verdict-debt-reconciliation

## Command under test
`/evaluate-poc`

## Brief (illustrative — not executed live)
"The note-search PoC has finished its three measurement runs. Evaluate it: did it validate the
hypothesis, and should v1 adopt FTS5?"

## What this checks
`implementation/knowledge/commands/evaluate-poc.md`, verbatim. Step 9:

> 9. **Produce a structured VERDICT** at the end of the evaluation:
>
> ```
> ## POC VERDICT
>
> - **Hypothesis**: <restated hypothesis>
> - **Status**: VALIDATED | INVALIDATED | INCONCLUSIVE
> - **Production recommendation**: proceed | proceed_with_constraints | do_not_proceed
> - **Evidence strength**: strong | moderate | weak
> - **Debt items**: <count> (CRITICAL: <n>, HIGH: <n>, MEDIUM: <n>, LOW: <n>)
> - **Residual risks**: <count>
> - **Evaluator**: poc-orchestrator
> - **Timestamp**: <ISO-8601>
> ```

step 11:

> 11. **Produce a debt summary table**:
>
> | # | Debt Item | Severity | Effort | Risk | Owner | Production Impact |
> |---|-----------|----------|--------|------|-------|-------------------|
> | 1 | ... | CRITICAL/HIGH/MEDIUM/LOW | S/M/L/XL | ... | ... | blocks/degrades/cosmetic |

step 10 — "**If recommending `proceed` or `proceed_with_constraints`**, produce a handoff checklist" —
with its eight declared items; step 6 — "Prioritized production refactoring backlog (top 5 minimum)";
and the `## Rails` Failure mode:

> **Failure mode**: If evidence strength is weak or the hypothesis wasn't actually tested, returns `INCONCLUSIVE` rather than forcing a Validated/Invalidated call.

**The load-bearing assertion is reconciliation: the VERDICT's `Debt items` line must agree with the
Debt Summary table, in total and severity by severity.** Step 9 declares a count *with a breakdown*,
and step 11 declares the table it summarises; a VERDICT reading `5 (CRITICAL: 0, …)` above a table
holding a `CRITICAL` row is internally contradicting itself in exactly the number a production
decision-maker reads first. So: the total equals the breakdown's sum, equals the number of table rows,
and each of the four severity counts equals the number of rows carrying that severity. This is
deterministic, it needs no external debt record, and it cannot be satisfied by a VERDICT written
without looking at the table.

Around that: the VERDICT's eight fields once each, in declared order, with the three enums, a numeric
`Residual risks`, `Evaluator: poc-orchestrator` and an ISO-8601 date-time `Timestamp`; the table's
declared header, sequential `#`, and the declared `Severity`, `Effort` and `Production Impact`
vocabularies with non-empty item, risk and owner; the eight checklist items present (checked or not)
**when and only when** the recommendation is `proceed`/`proceed_with_constraints`; and at least five
numbered items under the one backlog heading.

### One clause asserted only in its uncontested part — a new finding, reported not resolved
The Failure mode says weak evidence "returns `INCONCLUSIVE`". `implementation/knowledge/instructions/
poc-guidelines.md` (`maturity: stable`) § Hypothesis-First Validation › Rules says otherwise:

> 3. **Time-box strictly** — Every PoC has a hard deadline. If the hypothesis isn't validated by the deadline, it fails
> 4. **Binary outcome** — A PoC either validates or invalidates the hypothesis. "Partially validated" requires a follow-up PoC with refined criteria

and its scorecard's `## Result` admits only `[VALIDATED / INVALIDATED]`. Under the instruction a weak
PoC at its deadline has *failed*; under the command it is `INCONCLUSIVE`. That is `ADR-007` branch 1
territory (a command clause against a stable instruction), and this case does not adjudicate it. Both
readings agree on one thing — **weak evidence is never `VALIDATED`** — and that is all the check asserts
(demonstrated: weak + `VALIDATED` fails; weak + `INCONCLUSIVE` and weak + `INVALIDATED` both pass). The
status enum is asserted as declared, since it is the command's own value space.

### P12 and the scorecard summary — not asserted
Step 7, "Technical Debt Scorecard summary (severity, effort, risk, owner)", and the Rails input "the
PoC's debt/shortcut record" refer to a scorecard whose location is parked item **P12**
(`docs/decisions/poc-debt-<slug>.md` per `/new-poc` step 11, `POC-DEBT-SCORECARD.md` in the PoC root per
`poc-guidelines.md`, and `TECHNICAL-DEBT.md` per `poc-orchestrator`). Reconciling the table against that
record would mean choosing one, so the reconciliation here is internal to the evaluation. Note also that
the scorecard formats disagree on vocabulary, not only on location: `poc-guidelines.md`'s Production
Effort is `S`/`M`/`L` and its summary has three tiers (Critical / Medium / Low), where this command's table
uses `S/M/L/XL` and four severities. Reported with P12.

### Readings deliberately not asserted
- **`Residual risks: <count>` against the "Residual risks and assumptions" section** — that section
  mixes risks and assumptions, so no count of it is the declared count.
- **Step 3's prose verdict against the VERDICT's `Status`**, and the eight Evaluation Framework items
  as headings — the structured block is the declared contract for both.
- **Whether the evidence actually supports the verdict, or the recommendation follows from it** —
  judgement, which the suite does not grade.

## Pass condition
`fixture/poc-evaluation.md` has exactly one `## POC VERDICT` block with the eight declared fields in
order and in their declared value spaces; weak evidence is not `VALIDATED`; exactly one `## Debt
Summary` table with the declared header and valid rows; `Debt items` total = breakdown sum = row count,
with each severity count matching the table; all eight handoff-checklist items present if the
recommendation is `proceed`/`proceed_with_constraints`; and ≥ 5 numbered backlog items.

## Discrimination (demonstrated at authoring, on temp copies)
`check()` is `True` on the fixture and `False` on each of: `Debt items` total 6 over 5 rows; a breakdown
summing to 5 but wrong per severity; a table row's severity changed with the VERDICT unchanged; weak
evidence with `VALIDATED`; one checklist item dropped; the checklist removed under
`proceed_with_constraints`; the backlog trimmed to 4; `Evaluator: tech-lead`; a date-only timestamp;
effort `XXL`; impact `minor`; status `PARTIALLY_VALIDATED`; `Residual risks` removed. It stays `True` for
weak + `INCONCLUSIVE`, weak + `INVALIDATED`, and `do_not_proceed` with no checklist.

## Provenance
**Hand-authored; no real corpus exists.** No `/evaluate-poc` output has ever been committed here:

```
grep -rlE '^## (POC VERDICT|Hypothesis Status)' --include=*.md . | grep -vE '/commands/|/prompts/|/skills/|/agents/|/workflows/'  ->  0 matches
```

and the history survey in `new-poc-plan-hypothesis-format/brief.md` finds no PoC artifact of any kind
in any revision. `ADR-007` branch 4 territory. The evaluation concludes the same illustrative
note-search PoC the `/new-poc` and `/poc-demo` cases plan and demo; its figures are invented and
ungraded.
