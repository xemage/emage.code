# Case: sprint-status-dag-ledger-grounded

## Command under test
`/sprint-status`

## Brief (illustrative — not executed live)
"Where is this sprint?" — a status report for the phase-9 golden-case-coverage sprint, including the
task dependency graph.

## What this checks
`implementation/knowledge/commands/sprint-status.md`'s four declared `##` section headings, and
`## Task DAG Visualization` step 8 with its four sub-bullets, verbatim:

> 8. **Produce a task dependency graph** (Mermaid format):
>
> - Read `docs/tasks/active-tasks.md` for pending/in_progress/blocked/in_review nodes
> - Read `docs/tasks/completed-tasks.md` for `done` nodes — `active-tasks.md` NEVER contains `done`
> - Reconstruct dependency edges for done nodes from the `Depends on` cells of active rows
> - Color code: done=green, in_progress=yellow, blocked=red, pending=gray

**The load-bearing assertion is that the graph is resolved against the two real ledgers rather than
merely well-formed, and that is why this case is worth having.** Step 8 does not ask for a diagram;
it specifies, per node, *which file the node's existence must be read out of*. Three distinct
failures follow from that, and none is visible by looking at the graph:

- **A node that resolves to nothing.** `T531` and `T513` render identically as a box. A Mermaid graph
  citing a task ID that exists in neither ledger is syntactically perfect and completely wrong, and
  the reader of a status report is exactly the person least able to catch it.
- **A node read out of the wrong ledger.** The second bullet states the invariant in capitals —
  `active-tasks.md` NEVER contains `done`. So a node classed `done` must be found in
  `completed-tasks.md` *and must not appear in* `active-tasks.md`; a `done`-coloured node sitting in
  the active ledger means either the graph or the ledger is lying, and the check refuses both.
- **A colour that contradicts the row.** The fourth bullet is a mapping from real status to class, so
  a node classed `pending` whose real row says `blocked` fails. This is the assertion that makes the
  report's colours *mean* something: a burndown reader acts on red and grey.

The third bullet is checked in the direction the command's own `## Rails` states it — "If dependency
edges for `done` nodes can't be reconstructed from the active rows' `Depends on` cells, **omits that
edge rather than inventing an unverified dependency**". So every drawn edge must be backed by the
source row's real `Depends on` cell; an edge that is not is an invented dependency, and a missing but
unreconstructable edge is contract-compliant.

### A real gap in this clause, found while authoring and deliberately not worked around

**Step 8's first bullet declares four node sources — `pending/in_progress/blocked/in_review` — and
its fourth bullet declares only three non-done colours: `done=green, in_progress=yellow, blocked=red,
pending=gray`. There is no declared colour for `in_review`.** The command's own template confirms it:
it emits exactly four `classDef` lines. So a sprint containing a task in `in_review` — a state
`AGENTS.md` § Lifecycle States declares and `validate-tasks.py`'s `STATUS_SET` admits — has a node
the contract requires to be drawn and gives no way to colour.

This case does **not** manufacture a red result out of that gap. The real `active-tasks.md` at
authoring time contains four rows, all `pending`, and no `in_review` row, so a faithful graph of the
real ledger never encounters the gap and this case passes honestly. Constructing a fixture ledger
with an `in_review` row purely to turn the case red would be choosing a fixture to manufacture a
failure — the mirror image of choosing one to manufacture a pass, and no more honest. The checker
reflects the contract exactly as written (`STATUS_TO_CLASS` maps three statuses, so an `in_review`
node fails), the gap is recorded here, and **it is reported to the orchestrator as a candidate
`/sprint-status` defect for its own task rather than resolved inside this one** — amending
`sprint-status.md` is out of scope for `T528` §1.

### Readings deliberately weakened or not asserted, and why

- **`classDef` fill colours are checked by class *name*, not by hex value.** The fourth bullet
  declares colours in words ("done=green"); the specific `#90EE90`/`#FFD700`/`#FF6347`/`#D3D3D3`
  values appear only in the template's illustrative code block. Asserting those literals would
  promote an example to a contract and fail a report that used a different green.
- **Metrics 1–7, 9 and 10 are not checked beyond their section headings existing.** Velocity,
  burndown trajectory, token spend and checkpoint counts are values a deterministic checker cannot
  verify without recomputing the sprint, and grading their plausibility is exactly the LLM-judged
  scoring the suite forbids. The four declared `##` headings are checked; their contents are not.

## Pass condition
`fixture/sprint-status.md` contains all four declared `##` headings and exactly one ```` ```mermaid ````
fence declaring a graph; that fence declares all four `classDef` names (`done`, `inProgress`,
`blocked`, `pending`); every node declared in it has exactly one `class` assignment and every
assignment names a declared node; every node classed `done` appears in `fixture/docs/tasks/completed-tasks.md`
and **not** in `fixture/docs/tasks/active-tasks.md`; every other node appears in `active-tasks.md`,
not in `completed-tasks.md`, and carries the class its real status maps to; and every edge's source is
an active row whose real `Depends on` cell names the edge's target.

## Provenance
**Ledgers: real.** `fixture/docs/tasks/active-tasks.md` is a byte-identical copy of this repository's
own `docs/tasks/active-tasks.md`, the exact file step 8's first bullet names —
`cmp` it against the original to confirm. `fixture/docs/tasks/completed-tasks.md` carries the real
title, preamble, header and separator lines byte-identically plus the **real, byte-identical rows**
for the three `done` tasks the report cites (`T527`, `T531`, `T533`).

**The completed ledger is subset, and that is a deliberate size trade-off rather than a shortcut.**
The real `completed-tasks.md` is 440K across 328 rows; copying it whole would have grown the entire
golden suite by roughly 50% (`tests/golden/open/` is 900K, and the largest existing fixture is 76K)
for no additional assertion, because the only thing the check reads from that file is the set of
`done` IDs. Every byte the checker reads is real; only rows no node cites are omitted. Reproducible
with:

```
head -6 docs/tasks/completed-tasks.md
grep -E '^\|\s*(T527|T531|T533)\s*\|' docs/tasks/completed-tasks.md
```

**`sprint-status.md` is hand-authored**, as the agent-side output under test. A corpus survey found
**zero** committed `/sprint-status` output:

```
grep -rl 'classDef done' --include=*.md . | grep -vE 'commands/|prompts/|skills/'   ->  0 matches
```

Every file in this repo containing a `classDef done` line is either `sprint-status.md` itself, its
sibling `team-status.md`, one of their platform projections, or the `dependency-graphing` /
`plan-approve-execute` skill files — i.e. every hit is a declared *template*, and none is produced
output. No real `/sprint-status` report has ever been committed here, so there was nothing real to
source it from. That absence is documented rather than worked around, following
`new-feature-plan-doc-compliant/brief.md`'s precedent.

The graph itself, however, is not invented: its seven nodes, their statuses, and its single edge
(`T532 -->|depends on| T531`, backed by `T532`'s real `Depends on` cell reading `T531`) are all read
off the real ledgers, and the check re-derives that resolution from the ledger files rather than
trusting the authoring-time reading. The prose metrics around it are illustrative and ungraded.
