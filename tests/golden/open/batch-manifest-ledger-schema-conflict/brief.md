# Case: batch-manifest-ledger-schema-conflict (known_failing / tracked_defect)

## Command under test
`/batch`

## Brief (illustrative — not executed live)
"Replace the ad-hoc `print()` diagnostics across the runtime and scripts trees with the shared
structured logger." The change is decomposed into independent units, each with its own worktree
branch, and the batch is tracked.

## What this checks
`implementation/knowledge/commands/batch.md` `## Instructions` steps 2, 3 and 5, verbatim:

> 2. **Decompose into independent units** — each unit must be:
>    - Self-contained (no cross-unit dependencies within a batch)
>    - Independently testable
>    - Small enough for a single agent session
> 3. **Create worktree isolation** — for each unit:
>    - Create a dedicated worktree and branch using the worktree-isolation skill
>    - Branch naming: `batch/<slug>/<unit-number>-<short-description>`
> 5. **Track progress** — update `docs/tasks/active-tasks.md` with the full batch manifest:
>    - Unit ID, description, assigned agent, branch, status

These are the command's only structurally checkable steps. Steps 1, 4, 6 and 7 are analysis,
delegation, verification and human PR guidance, and `## Important`'s third bullet ("Present the
decomposition plan for user approval") is a human interaction with no declared artifact.

Three independent assertions:

- **A (step 2) — independence.** No unit's declared dependencies may name another unit in the same
  batch. This is the one step 2 constraint that is mechanically decidable: "independently testable"
  and "small enough for a single agent session" are judgements. It is also the failure the command
  itself singles out — `## Important` says "If a unit turns out to have a dependency on another
  unit, flag it immediately and re-plan", and `## Rails` repeats it as the declared failure mode.
- **B (step 3) — branch naming.** Every unit's branch matches `batch/<slug>/<unit-number>-<short-description>`
  exactly as declared.
- **C (step 5) — the manifest.** `docs/tasks/active-tasks.md` carries, per unit, all five declared
  fields: Unit ID, description, assigned agent, **branch**, status.

## Pass condition
`fixture/decomposition.md` declares at least two units in a five-column table (unit / description /
agent / branch / status), each with a well-formed unit ID, non-empty description, agent and status,
and a branch matching the declared pattern; a per-unit dependency table covers every unit and no
unit depends on another in the batch; and for every unit, some row of `fixture/docs/tasks/active-tasks.md`
carries that unit's ID, agent, status **and branch** together.

## Why this is known_failing today

**Assertions A and B pass. Assertion C cannot be satisfied.** Verified by instrumenting the checker
against its own fixture: three units parse, all three branches match the declared pattern, the
dependency table declares `—` for all three, and the check then fails at C because no ledger row
carries any unit's branch.

It cannot be satisfied because `docs/tasks/active-tasks.md` already has an owner and a schema, and
that schema has no room for a branch. `AGENTS.md` § Task Protocol pins it:

> Task list: `docs/tasks/active-tasks.md` — columns: `ID | Title | Owner | Status | Priority | Depends on | Last update`

and `docs/tasks/validate-tasks.py:195` enforces the count:

```python
if len(row.cells) != 7:
    add_fail(fails, "C2", f"active-tasks.md:{row.line_no} has {len(row.cells)} cells (expected 7)")
```

Five of step 5's fields map onto that schema (`Unit ID`→`ID`, `description`→`Title`,
`assigned agent`→`Owner`, `status`→`Status`), but `branch` maps onto nothing, and the two remaining
columns (`Priority`, `Last update`) are already spoken for. So the manifest step 5 declares is not
writable into the file step 5 names.

**Demonstrated in both directions rather than argued.** The fixture's ledger is schema-conforming
(real header, one 7-column row per unit) and the real validator reports **no** C2 or C3 failure
against it — so the fixture is not a broken ledger, it is a correct one that simply cannot carry a
branch. Appending the declared five-field manifest to the same file makes this check return `True`
and makes the validator fail:

```
FAIL C2: active-tasks.md:11 has 5 cells (expected 7)
FAIL C2: active-tasks.md:13 has 5 cells (expected 7)
```

Line 13 is the manifest's data row; **line 11 is its header row**, which also fails, because
`parse_table_rows` skips a header only when its first cell is the literal string `ID` and `Unit ID`
is not that. A second, independent collision sits behind the first: unit IDs of the declared
`U<n>` shape fail `ID_RE = ^T\d{3,}$` (C3), and `bug-report.md` records the consequence of non-`T`
rows in this file — "non-`T` rows are silently deleted by `install.sh --update`".

**No fixture was selected to manufacture this result.** A survey found nothing to arbitrate between
the two contracts: `git branch -a --list 'batch/*'` returns zero branches and `grep -c 'batch/'`
returns 0 for both ledgers, so `/batch` has never been run to completion in this repository and
practice has not settled the disagreement either way. There is therefore no real artifact that could
have made this case green, and no choice of real fixture that would have changed the outcome. Making
it green would have required either asserting a manifest shape the ledger's own validator rejects,
or quietly dropping `branch` from the five fields step 5 declares — which is exactly the
check-relaxation `ADR-007` §5 forbids.

## Category
`tracked_defect`, not `capability_gap`. Nothing prevents a conforming manifest from being written;
two declared contracts simply disagree about one file, and the disagreement is mechanically
resolvable in either direction — amend `batch.md` step 5 to name a manifest location that is not the
7-column ledger (the batch's own `docs/tasks/task-<ID>.md` briefs, or a dedicated manifest file), or
extend the ledger schema and its validator to carry a branch. Choosing between those needs an
`ADR-007` adjudication of which document holds authority, which is what a tracked defect is for.
Resolving it by editing `implementation/knowledge/commands/batch.md`, `AGENTS.md`,
`docs/tasks/validate-tasks.py` or this fixture is explicitly **out of scope** for the task that
authored this case (`T528` §1).

## Provenance
**Ledger: real schema, real header.** `fixture/docs/tasks/active-tasks.md` carries this repository's
own real title, header and separator lines copied byte-identically, with three added 7-column unit
rows using the next free IDs at authoring time (`T534`–`T536`; the highest real ID in either ledger
is `T533`). The schema the case collides with is therefore the real one, not a restatement.

**`decomposition.md` is hand-authored.** Surveys:

```
git branch -a --list 'batch/*'                                   ->  0 branches
grep -c 'batch/' docs/tasks/active-tasks.md docs/tasks/completed-tasks.md  ->  0, 0
```

No `/batch` run has ever produced a committed artifact here, so there was nothing real to source it
from; that absence is documented rather than worked around, following
`new-feature-plan-doc-compliant/brief.md`'s precedent. The change it decomposes (migrating ad-hoc
`print()` diagnostics to a shared structured logger) is illustrative and the units' contents are not
graded by the check — only their structure, branch naming and mutual independence.
