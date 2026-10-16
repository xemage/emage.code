# Case: team-status-dag-colour-code

## Command under test
`/team-status`

## Brief (illustrative — not executed live)
"Where is the team?" — an unscoped (team-wide) status report, including the task dependency graph,
against the active and completed ledgers as they stood on 2026-06-24.

## What this checks
`implementation/knowledge/commands/team-status.md` `## Task DAG Visualization` step 7's four
sub-bullets, verbatim:

> - Read `docs/tasks/active-tasks.md` for pending/in_progress/blocked/in_review nodes
> - Read `docs/tasks/completed-tasks.md` for `done` nodes — `active-tasks.md` NEVER contains `done`
> - Reconstruct dependency edges for done nodes from the `Depends on` cells of active rows
> - Color code: done=green, in_progress=yellow, blocked=red, pending=gray, in_review=blue

and the command's declared `Output format` headings (`## Team Status`, then `### Active Streams`,
`### Blockers`, `### Role Workload`, `### Recommended Next Actions`, `### Checkpoint Delta`,
`### Task DAG`, `### Velocity`, `### Portfolio Dependencies`, in that order), with the graph required
to sit under `### Task DAG`, where the template places `[Mermaid diagram]`.

**The load-bearing assertion is the colour code itself, and it is what distinguishes this case from
`sprint-status-dag-ledger-grounded`.** That sibling checks node classes by *name*, deliberately not by
colour. The fourth bullet here declares five *colours*, so this case resolves each node's class through
its `classDef … fill:` to a colour family and requires it to equal the family the node's **real ledger
status** maps to. A graph that classes an `in_review` node with a yellow, orange or grey fill fails; a
graph that paints `blocked` green fails; a graph that uses a different shade of the declared colour
passes. `in_review=blue` is the clause's newest term (added when `T538` aligned this command with
`/sprint-status`), and the fixture deliberately uses a real ledger snapshot in which an `in_review`
row exists, so the term is exercised rather than vacuously satisfied. That snapshot was chosen because
it is the one real ledger state that exercises **all five** colours at once — not to obtain a result:
the colour mapping it exercises is declared, so there is no gap here to manufacture a red from (unlike
the `in_review` gap `sprint-status-dag-ledger-grounded` recorded and declined to exploit).

Grounding, as in the sibling: a `done`-coloured node must be in `completed-tasks.md` and **not** in
`active-tasks.md`; every other node must be an active row whose real `Status` maps to its colour; every
edge must be backed by its source row's real `Depends on` cell (an unbacked edge is an invented
dependency); and every `pending`/`in_progress`/`blocked`/`in_review` row of the active ledger must be
drawn — the first bullet says those rows *are* the graph's non-done nodes, and the brief is unscoped.

### Colour families — the reading, stated so it can be overruled
A fill is classified by HSV: saturation < 0.15 → **gray**; otherwise hue 0–20° or 340–360° → **red**,
40–70° → **yellow**, 75–165° → **green**, 180–260° → **blue**; anything else (orange, purple, cyan-teal
gaps) → unclassified, which fails. The bands are this case's reading of five plain colour words; they
are wide enough that every conventional rendering of each word passes (the template's own `#90EE90`,
`#FFD700`, `#FF6347`, `#D3D3D3`, `#87CEFA` classify correctly) and narrow enough that adjacent colours
do not collide. Hex literals are **not** asserted — that would promote the template's example to a
contract.

### Readings deliberately not asserted
- **Class names.** `done`/`inProgress`/`blocked`/`pending`/`inReview` appear only in the template.
- **Contents of the other eight sections** — workload saturation, next-action ordering "by impact",
  velocity figures and checkpoint deltas are judgements or recomputations; only the headings are
  checked. The prose in them is illustrative and ungraded.
- **The feature-flag rule** (`TEAM_STATUS_V1_ENABLED`). The report under test is the enabled form;
  the flag's state is environment, which `check()` may not read (`golden-suite-format-v1.md` §4.2).
- **The `dependency-graphing` skill's palette (parked item P19)** — a different document with a
  different palette; out of scope for a `/team-status` case.
- **Edge labels.** The template shows both `depends on` and `blocked by`; any label is accepted, and
  every edge, whatever its label, must be backed by a `Depends on` cell.

## Pass condition
`fixture/team-status.md` carries the nine declared headings in order and exactly one
```` ```mermaid ```` graph, which sits under `### Task DAG`; every declared node has exactly one class;
every class has a `classDef` whose `fill:` classifies to a colour family; each node's family equals the
family its real status maps to, with `done`-family nodes found only in
`fixture/docs/tasks/completed-tasks.md` and all others only in `fixture/docs/tasks/active-tasks.md`;
every non-terminal active row is drawn; and every edge's target is named in its source row's
`Depends on` cell.

## Discrimination (demonstrated at authoring, on temp copies)
`check()` is `True` on the fixture and `False` on each of: the `in_review` fill turned orange; the
`blocked` fill turned green; `T235` (`in_review`) classed with the yellow class; `T235` classed grey;
an invented edge `T234 → T231`; `T235` omitted with the graph otherwise self-consistent; `T214`
(active) classed `done`; the graph moved out of `### Task DAG`; and the fixture ledger's `T235` status
changed to `in_progress`. It stays `True` when `done` and `in_review` are recoloured to other shades of
green and blue (`#2E8B57`, `#4169E1`).

## Provenance
**Ledgers: real.** Both come from this repository's own ledgers at commit `d3cd183` (2026-06-24).
`fixture/docs/tasks/active-tasks.md` is that revision's file **whole and byte-identical**.
`fixture/docs/tasks/completed-tasks.md` carries that revision's title, preamble, header and separator
lines plus the **real, byte-identical rows** of the five `done` tasks the graph cites (`T212`, `T226`,
`T228`, `T231`, `T232`) in their original order — every line is a line of the original. Reproduce with:

```
git show d3cd183:docs/tasks/active-tasks.md | cmp - fixture/docs/tasks/active-tasks.md
{ git show d3cd183:docs/tasks/completed-tasks.md | head -6
  git show d3cd183:docs/tasks/completed-tasks.md | grep -E '^\|\s*(T212|T226|T228|T231|T232)\s*\|'; } \
  | cmp - fixture/docs/tasks/completed-tasks.md
```

**Why the completed ledger is subset.** The whole 16 KB file was copied first, and it broke a
repository gate rather than this case: its other rows name past releases (`v3.0.0`, `v3.0.1`,
`v4.0.0`), and `scripts/check-version-consistency.py` excludes `docs/tasks/` only at the repository
root, so the nested copy failed `test_check_version_consistency`. The only thing `check()` reads from
that file is the set of `done` IDs, so the subset changes no assertion. Same trade-off as
`sprint-status-dag-ledger-grounded`'s completed ledger.

A historical snapshot was used because the current active ledger holds one `pending` row and cannot
exercise the colour code. A scan of every committed revision of `active-tasks.md` for rows in
`in_review` found 14 revisions with one; two of them (`2439bbc` and `d3cd183`, both 2026-06-24) also
hold `in_progress`, `blocked` and `pending` rows. `d3cd183` is the later of the two (5 active rows, all
four non-terminal states). Every dependency its active rows name (`T212`, `T226`, `T228`, `T231`,
`T232`) is a row of that revision's completed ledger.

**`team-status.md` is hand-authored**, as the agent-side output under test. A corpus survey found
**zero** committed `/team-status` output:

```
grep -rlE '^## Team Status' --include=*.md . | grep -vE '/commands/|/prompts/|/skills/|/agents/|/workflows/'  ->  0 matches
```

Its graph is not invented: its ten nodes, their statuses and its seven edges are read off the two real
ledgers, and `check()` re-derives that resolution from the ledger files rather than trusting the
authoring-time reading.
