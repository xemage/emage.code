# Case: bug-report-severity-priority-ledger-row

## Command under test
`/bug-report`

## Brief (illustrative — not executed live)
"`validate-tasks.py` says PASS on a ledger whose `Depends on` cell names a task that does not
exist." A structured bug report is produced and a tracking task is added to the ledger.

## What this checks
`implementation/knowledge/commands/bug-report.md`'s `Use this format:` block (the nine `###`
sections of `## Bug Report`) and `### Task Creation` step 1, verbatim:

> 1. **Create a TASK entry** for tracking this bug:
>    - Add to `docs/tasks/active-tasks.md` with state `pending`
>    - Assign severity-appropriate priority
>    - Use the NEXT sequential `T<NNN>` ID. NEVER invent a `BUG-` prefix — non-`T` rows are silently deleted by `install.sh --update`.
>    - Format (7 columns, exact order):
>      `| T<NNN> | BUG: <title> | <owner-slug> | pending | P0\|P1\|P2 | <dep-ids or —> | YYYY-MM-DD |`
>    - Map severity → priority: critical→P0, high→P0, medium→P1, low→P2

**The load-bearing assertion is cross-artifact, and that is why this case is worth having.** The
report and the ledger row are two separate artifacts, and the command declares a mapping *between*
them: whatever `### Severity` says must determine the row's priority through the declared table.
Nothing inside either artifact reveals a violation — a report saying `Critical` next to a row saying
`P2` is perfectly well-formed in isolation, and both look right. Only resolving one against the other
catches it. This is the same shape as `handoff-payload-schema-fields-real`'s filename-equals-field
assertion: the failure lives in the relationship, not in either file.

Three further assertions come from the same step, each covering a failure mode the command
explicitly names:

- **The 7-column shape.** The declared row has exactly 7 cells in a fixed order. This is not a
  stylistic preference: `docs/tasks/validate-tasks.py:195` hard-fails C2 on any active row whose cell
  count differs (`has {n} cells (expected 7)`), so a 6- or 8-column bug row breaks the ledger's own
  validator. The check asserts the count the command declares.
- **No `BUG-` prefix.** The command states the consequence itself — "non-`T` rows are silently
  deleted by `install.sh --update`". A `BUG-041` row is the worst kind of defect because it looks
  filed and then vanishes without a message. Checked across every row, not just the new one.
- **`pending` state, `T<NNN>` ID form, `YYYY-MM-DD` date.** All three are literal in the declared
  format string.

### Readings deliberately weakened or not asserted, and why

- **"NEXT sequential" is checked as "greater than every other ID in this ledger", not "max of both
  ledgers + 1".** The strong reading needs `completed-tasks.md` too, and this repo's real one is
  440K — shipping it would roughly halve-again the whole suite's size for a single assertion. The
  weaker reading still fails a re-used or lower ID, which is the collision this rule exists to
  prevent; it would not fail a gap (`T534` where `T533` was next). That limit is stated rather than
  hidden.
- **`### Blocker Classification` is not checked.** Its three flags (`[RELEASE_BLOCKER]`,
  `[TEAM_BLOCKER]`, blocked task IDs) are all declared *conditionally* — "Does this bug block …" —
  so their absence is contract-compliant whenever the answer is no, and requiring them would fail
  conforming reports. The fixture's bug blocks nothing.
- **Prose quality is not graded anywhere.** `### Root Cause Analysis` is required to be non-empty,
  not to be correct — that judgement is outside what a deterministic check can make.

## Pass condition
`fixture/bug-report.md` contains `## Bug Report` and all nine declared `###` sections, in the
declared order, each with a non-empty body, with at least two numbered steps under
`### Steps to Reproduce` and a `### Severity` naming one of `Critical|High|Medium|Low` *plus* a
justification. `fixture/docs/tasks/active-tasks.md` contains exactly one row whose title begins
`BUG: `; that row has exactly 7 cells, a `T<NNN>` ID greater than every other ID in the ledger, a
non-empty owner, status exactly `pending`, a `YYYY-MM-DD` date, and a priority equal to the declared
mapping of the report's severity (`High` → `P0`). No row in the ledger carries a `BUG-` prefixed ID.

## Provenance
**Ledger: real schema and real rows.** `fixture/docs/tasks/active-tasks.md` carries this
repository's own real header, separator and four real active rows (`T528`, `T529`, `T530`, `T532`),
copied byte-identically, with one added `BUG:` row — so the 7-column shape the check asserts is the
real ledger's shape, not a restatement of it. `T534` is genuinely the next free ID at authoring time
(the highest ID in either real ledger is `T533`).

**Report: hand-authored, but its content is factually true of this repository.** A corpus survey
found **zero** real `BUG:` rows in either ledger:

```
grep -cE '^\|\s*T[0-9]+\s*\|\s*BUG:' docs/tasks/active-tasks.md docs/tasks/completed-tasks.md
  docs/tasks/active-tasks.md:0
  docs/tasks/completed-tasks.md:0
```

and every file containing the `## Bug Report` heading is either the command itself, one of its
platform projections, or the `qa-engineer` agent definition that declares a *different* bug-report
template (`## Bug: [Title]` with `### Severity`/`### Priority` lines) — no produced output. So no
real `/bug-report` artifact existed to copy.

Rather than invent a fictional defect, the hand-authored report documents a **real, verified gap** in
this repo: `docs/tasks/validate-tasks.py` destructures the `Depends on` cell into an unused slot at
line 203 (`task_id, _, _, status, priority, _, last_update = row.cells`) and no check in its
inventory (`C2`, `C3`, `C4`, `C5`, `C7`, `C10`, `C11` are the codes it can emit) ever resolves a
dependency reference against the known ID set. Verified by reading the source, not inferred. The
case does not assert this defect — it asserts the report's *shape* — but the fixture describes
something true, so a future reader is not misled by it. **Filing that defect is out of scope for
the task that authored this case (`T528` §1); it is reported to the orchestrator instead.**
