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
> - **Status**: VALIDATED | INVALIDATED
> - **Production recommendation**: proceed | proceed_with_constraints | do_not_proceed
> - **Evidence strength**: strong | moderate | weak
> - **Debt items**: <count> (CRITICAL: <n>, MEDIUM: <n>, LOW: <n>)
> - **Residual risks**: <count>
> - **Evaluator**: poc-orchestrator
> - **Timestamp**: <ISO-8601>
> ```

step 11:

> 11. **Produce a debt summary table**:
>
> | # | Debt Item | Severity | Effort | Risk | Owner | Production Impact |
> |---|-----------|----------|--------|------|-------|-------------------|
> | 1 | ... | CRITICAL/MEDIUM/LOW | S/M/L | ... | ... | blocks/degrades/cosmetic |

step 10 — "**If recommending `proceed` or `proceed_with_constraints`**, produce a handoff checklist" —
with its eight declared items; step 6 — "Prioritized production refactoring backlog (top 5 minimum)";
and the `## Rails` Failure mode:

> **Failure mode**: If evidence strength is weak, or the hypothesis wasn't actually tested by its deadline, returns `INVALIDATED` with `Evidence strength: weak` and names a follow-up PoC with refined criteria as the recommended next step, rather than forcing a `VALIDATED` call (`poc-guidelines.md` § Hypothesis-First Validation, Rules 3–4).

**The load-bearing assertion is reconciliation: the VERDICT's `Debt items` line must agree with the
Debt Summary table, in total and severity by severity.** Step 9 declares a count *with a breakdown*,
and step 11 declares the table it summarises; a VERDICT reading `5 (CRITICAL: 0, …)` above a table
holding a `CRITICAL` row is internally contradicting itself in exactly the number a production
decision-maker reads first. So: the total equals the breakdown's sum, equals the number of table rows,
and each of the three severity counts equals the number of rows carrying that severity. This is
deterministic, it needs no external debt record, and it cannot be satisfied by a VERDICT written
without looking at the table.

Around that: the VERDICT's eight fields once each, in declared order, with the three enums, a numeric
`Residual risks`, `Evaluator: poc-orchestrator` and an ISO-8601 date-time `Timestamp`; the table's
declared header, sequential `#`, and the declared `Severity`, `Effort` and `Production Impact`
vocabularies with non-empty item, risk and owner; the eight checklist items present (checked or not)
**when** the recommendation is `proceed`/`proceed_with_constraints` — step 10 says
"**If recommending `proceed` or `proceed_with_constraints`**, produce a handoff checklist", an "if", not
an "only if", and the check enforces exactly that (a checklist under `do_not_proceed` is not asserted
either way); and at least five prioritized items under the one backlog heading, as numbered items or
table rows. Step 6, "Prioritized production refactoring backlog (top 5 minimum)", declares no format,
and the `poc-evaluation` skill's § 6 Refactoring Backlog template
(`implementation/knowledge/skills/poc-evaluation/SKILL.md`) renders the backlog as a table:

> [Prioritized list of items from POC-DEBT tags and review findings]
>
> | Priority | Item | Rationale | Suggested Owner | Effort |
> |----------|------|-----------|-----------------|--------|

So the check counts the section's numbered items, or, when it has none, the data rows of its first
table (the header and `|---|` separator skipped, each row with a non-empty first cell, up to the first
non-table line).

### The weak-evidence Failure mode — asserted in full (formerly contested, resolved by T563/T564)
This case was authored (T561) while the Failure mode said weak evidence "returns `INCONCLUSIVE`",
against `implementation/knowledge/instructions/poc-guidelines.md` (`maturity: stable`)
§ Hypothesis-First Validation › Rules:

> 3. **Time-box strictly** — Every PoC has a hard deadline. If the hypothesis isn't validated by the deadline, it fails
> 4. **Binary outcome** — A PoC either validates or invalidates the hypothesis. "Partially validated" requires a follow-up PoC with refined criteria

and the case then asserted only the part both readings shared, "weak evidence is never `VALIDATED`".
`poc-contract-resolution-v1.md` §5 (P31) ruled it `ADR-007` branch 1, stable-instruction prong, and T564
amended the command: `Status` is now binary (quoted above) and the Failure mode returns `INVALIDATED`.
With a binary `Status`, "never `VALIDATED`" and "weak ⇒ `INVALIDATED`" are the same assertion, and the
check now states it directly: weak evidence with any status other than `INVALIDATED` fails, and
`INCONCLUSIVE` is rejected outright as off-enum. The Failure mode's other duty, naming a follow-up PoC
as the next step, is prose with no declared form and is not asserted.

### The value scales and the scorecard summary (P12 / P29 — resolved by T563/T564)
When this case was authored, the scorecard's home was parked item **P12**, and this command's table used
`S/M/L/XL` and four severities against `poc-guidelines.md`'s `S`/`M`/`L` effort and three-tier summary
(Critical / Medium / Low). `poc-contract-resolution-v1.md` §3 (P29) ruled both: the scorecard is
`POC-DEBT-SCORECARD.md` in the PoC root (§3a; `TECHNICAL-DEBT.md` is a separate narrative register, §3c),
and the command's scales are `CRITICAL/MEDIUM/LOW` and `S/M/L` (§3b). T564 amended the `Debt items` line
and the table row, both quoted above. The check now uses the amended scales and **rejects** `HIGH` and
`XL` outright (a `HIGH` row or an `XL` effort fails `_rows_valid`; a `HIGH:` group fails the `Debt items`
pattern), as `poc-contract-resolution-v1.md` §9.2 requires for the drop from four sub-counts to three not
to be a weakening. The fixture's one `HIGH` item (no online-write strategy, impact `blocks`, the gap the
`proceed_with_constraints` recommendation is conditional on) was re-tiered to `CRITICAL`, "must fix
before production", and its counts reconciled (`ADR-007` §5: re-authoring a hand-authored fixture to a
corrected contract).

Step 7, "Technical Debt Scorecard summary (severity, effort, risk, owner)", and the Rails input "the
PoC's debt/shortcut record" are still not reconciled against a scorecard file: the case has no
`POC-DEBT-SCORECARD.md` fixture, so the reconciliation stays internal to the evaluation.

### Readings deliberately not asserted
- **`Residual risks: <count>` against the "Residual risks and assumptions" section** — that section
  mixes risks and assumptions, so no count of it is the declared count.
- **Step 3's prose verdict against the VERDICT's `Status`**, and the eight Evaluation Framework items
  as headings — the structured block is the declared contract for both. (Step 3 now reads "3. Verdict
  (Validated, Invalidated)", binary like `Status`.)
- **Whether the evidence actually supports the verdict, or the recommendation follows from it** —
  judgement, which the suite does not grade.

## Pass condition
`fixture/poc-evaluation.md` has exactly one `## POC VERDICT` block with the eight declared fields in
order and in their declared value spaces; weak evidence is `INVALIDATED`; exactly one `## Debt
Summary` table with the declared header and valid rows; `Debt items` total = breakdown sum = row count,
with each severity count matching the table; all eight handoff-checklist items present if the
recommendation is `proceed`/`proceed_with_constraints`; and ≥ 5 backlog items under the one backlog
heading, numbered items or table rows.

## Discrimination (demonstrated at authoring, on temp copies)
`check()` is `True` on the fixture and `False` on each of: `Debt items` total 6 over 5 rows; a breakdown
summing to 5 but wrong per severity; a table row's severity changed with the VERDICT unchanged; weak
evidence with `VALIDATED`; one checklist item dropped; the checklist removed under
`proceed_with_constraints`; the backlog trimmed to 4; `Evaluator: tech-lead`; a date-only timestamp;
effort `XXL`; impact `minor`; status `PARTIALLY_VALIDATED`; `Residual risks` removed. Against the amended
contract (T565), it is also `False` on each of: status `INCONCLUSIVE`; weak + `INCONCLUSIVE` (inverted
from T561, where it stayed `True`); a table row's severity `HIGH` with a reconciling
`(CRITICAL: 1, HIGH: 1, MEDIUM: 2, LOW: 1)` breakdown; the same `HIGH` row under a three-tier breakdown;
effort `XL`. It stays `True` for weak + `INVALIDATED` and `do_not_proceed` with no checklist.

Backlog-format probes (T600, re-run at T601 on scratch copies outside the repo, each mutation confirmed applied,
all other fixture fields kept valid): the unmodified fixture (6 numbered items) is `True`; the numbered list
trimmed to 4 is `False`; the backlog replaced by the skill's table with 5 data rows is `True`; the same table
with 4 data rows is `False`; a table with only the header and separator rows is `False`; a second
`## ...Backlog...` heading added is `False`; and the pre-T600 `_backlog_size` (numbered items only), run on the
5-row table, is `False`, which demonstrates the defect T600 fixed.

## Provenance
**Hand-authored; no real corpus exists.** No `/evaluate-poc` output has ever been committed here:

```
grep -rlE '^## (POC VERDICT|Hypothesis Status)' --include=*.md . | grep -vE '/commands/|/prompts/|/skills/|/agents/|/workflows/'  ->  0 matches
```

and the history survey in `new-poc-plan-hypothesis-format/brief.md` finds no PoC artifact of any kind
in any revision. `ADR-007` branch 4 territory. The evaluation concludes the same illustrative
note-search PoC the `/new-poc` and `/poc-demo` cases plan and demo; its figures are invented and
ungraded.
