# Case: new-project-plan-doc-and-lifecycle-states

## Command under test
`/new-project`

## Brief (illustrative — not executed live)
"Build TaskFlow: a self-hosted task board a co-located team can keep using offline, with edits
reconciling deterministically on reconnect." Phase 1's plan document and Phase 5's initial task graph
are produced.

## What this checks
`implementation/knowledge/commands/new-project.md` `## Phase 1: Plan-Approve-Execute` step 1 and
`## Phase 5: Validation & Artifacts` step 19, verbatim:

> 1. **Create a plan document** with task decomposition and dependency graph
>    - Write the plan to `docs/plans/plan-<project-slug>.md`
>    - Include: objective, scope, task DAG (Mermaid), risk assessment, estimated phases
>    - Reference protocol: `plan-approve-execute` skill § The Three Phases › Phase 1: Plan (Plan Document Format)

> 19. Build an initial task dependency graph with lifecycle states
>     - Track states: `pending → in_progress → blocked → in_review → done | cancelled`
>     - The state is spelled `in_review`, NOT `review`.
>     - Write active tasks to `docs/tasks/active-tasks.md`

**These two are the checkable pair because they are the two steps that name a file.** This command
is 19 steps across five phases, and almost all of them are orchestration directives — "Have the
Product Owner create requirements", "Run an Architecture Briefing", "Coordinate development" — whose
outputs belong to the commands they delegate to, not to `/new-project`. Step 1 declares a path and
its contents; step 19 declares a path and a value vocabulary. Everything else either produces no
artifact of its own or produces one another case already owns.

The load-bearing assertion is **step 19's spelling rule**, and it is load-bearing precisely because
it is the kind of defect that survives review. `review` and `in_review` are visually
interchangeable in a table cell, both read as English, and a ledger using the wrong one looks
completely normal — but `docs/tasks/validate-tasks.py` fails C4 on it (`STATUS_SET` admits only the
six declared spellings) and `check-maturity.py` reads the same field. The command calls the
misspelling out by name, which is itself evidence it has been made. The check enforces the declared
set, so `review`, `in-review`, `In Review` and `reviewing` all fail.

Step 1's contribution is that the plan's Mermaid DAG must actually be a graph: a ```` ```mermaid ````
fence containing a `graph`/`flowchart` declaration **and at least one edge**. "Task DAG (Mermaid)" is
not satisfied by a fenced block with nodes and no dependencies, which is a list with extra syntax.

### Readings deliberately weakened or not asserted, and why

- **Step 2's approval gate is not checked.** "Present the plan for my approval … Wait for explicit
  approval (`APPROVED`, `APPROVED_WITH_CHANGES`, or `REJECTED`)" is a chat interaction. The command
  declares no file in which an approval is recorded, so checking for one would assert an artifact
  that does not exist in the contract — the same reason `/skillify`'s `### Present for Approval` and
  `/consolidate-memory`'s step 4 go unchecked in their cases.
- **Step 1's five contents are matched by concept, not by literal heading.** The command lists
  content ("objective, scope, task DAG (Mermaid), risk assessment, estimated phases") and never
  declares heading text, so the check matches headings containing those concepts rather than exact
  strings.
- **The status column is located from the table's own header row**, not from a hardcoded index.
  Step 19 declares state *values* and says nothing about column order; hardcoding position would
  import `AGENTS.md`'s 7-column schema into a check whose clause does not mention it. That schema is
  asserted by `bug-report-severity-priority-ledger-row` instead, which quotes a clause that does
  declare it.
- **The declared set is checked, not the presence of any particular state.** An initial task graph
  legitimately might contain no `in_review` row at all, so requiring one would fail a conforming
  artifact. The *fixture* uses all four non-terminal states, including `in_review`, so the spelling
  rule is genuinely exercised rather than nominally present — but that is a property of the fixture,
  not a requirement of the check.
- **Step 18's artifact-versioning format (`<artifact-name>-v<major>.<minor>.md`) is deliberately
  not touched**, and neither is step 14's `[CHECKPOINT]` line. Both are already the subject of
  sibling cases for other commands (`new-feature-checkpoint-line-compliant` covers the checkpoint
  contract), and duplicating an assertion across two cases means a single contract change flips two
  cases for one reason, which makes the board harder to read rather than better covered.

## Pass condition
`fixture/docs/plans/` contains exactly one file named `plan-<slug>.md`; it carries headings for all
five declared contents (objective, scope, task DAG / dependency graph, risk, phases) and at least one
```` ```mermaid ```` fence declaring a `graph`/`flowchart` with at least one edge; and every status
cell in `fixture/docs/tasks/active-tasks.md` — with the status column located from the header row — is
one of the six states step 19 declares.

## Provenance
**Hand-authored, both files.** A corpus survey of `docs/plans/` found **75 of 76** files matching
`plan-<NNN>-<slug>.md` and the 76th being `_template.md`:

```
ls docs/plans | grep -cE '^plan-[0-9]{3}-'      ->  75
ls docs/plans | grep -vE '^plan-[0-9]{3}-'      ->  _template.md
```

Zero files match `/new-project`'s declared `plan-<project-slug>.md` shape without an intervening
sequence number, because every real plan here is produced by `/plan` and follows *its* naming
convention. Nothing in this repository was produced by `/new-project` — this harness's own
development has never been bootstrapped by it — so there was no real plan document or initial task
ledger to source either fixture from. That absence is documented rather than worked around,
following `new-feature-plan-doc-compliant/brief.md`'s precedent, which recorded the same finding for
`/new-feature`'s `feature-<slug>.md`.

Note that the check's `PLAN_NAME_RE` (`plan-<slug>.md`) would also accept a real
`plan-072-phase9-golden-case-coverage.md`, since `072-phase9-golden-case-coverage` is a valid slug.
That is intentional: the declared pattern genuinely admits both, and narrowing it to *exclude* the
convention this repo actually uses would be inventing a contract rather than checking one.

The project described (TaskFlow) is illustrative. Its content is not graded — the check asserts the
plan's structure and the ledger's state vocabulary, never whether the risks are the right risks or
the estimates plausible.
