# Case: batch-manifest-ledger-schema-conflict (expected_pass)

## Command under test
`/batch`

## Brief (illustrative — not executed live)
"Replace the ad-hoc `print()` diagnostics across the runtime and scripts trees with the shared
structured logger." The change is decomposed into independent units, each with its own worktree
branch, and the batch is tracked.

## History — this case was `known_failing` / `tracked_defect` until `T541`
It recorded a real contract conflict: `batch.md` step 5 declared a five-field manifest row
(`Unit ID, description, assigned agent, branch, status`) to be written into
`docs/tasks/active-tasks.md`, whose schema `AGENTS.md` § Task Protocol pins to exactly seven columns
with no `branch` among them. `T535` adjudicated that conflict under
`docs/decisions/ADR-007-command-contract-authority.md` and recorded the verdict in
`docs/artifacts/batch-manifest-resolution-v1.md`: **branch 1 fires twice**, on step 5 against
`AGENTS.md` and independently on step 3 against `git-workflow.md`, and **nothing is deleted** —
every one of step 5's five declared fields keeps exactly one home (§4.4). `T541` then re-derived
this checker element-for-element against `batch-manifest-resolution-v1.md` §7 and the amended
command file, and the case now passes. The full "why it failed" account, with both directions
demonstrated, is preserved in `batch-manifest-resolution-v1.md` §§1–3, and `T541`'s re-derivation
is recorded in `evaluator-hash-known-good-v8.json`'s `reason` field. (Until `T544` this line cited
`v7`'s `reason` field, which does not mention this case; `v8` is the baseline `T541` refreshed.)

`T544` then closed the one qualification `T541` left open: the fixture's ledger Titles carried a
`U<n>` marker from the abolished unit-ID scheme, which was stripped, and the Title check was
tightened to a kebab-case slug (§ "What is deliberately not asserted", item 2).

## What this checks
`implementation/knowledge/commands/batch.md` `## Instructions` steps 2, 3 and 5, **as amended**:

> 2. **Decompose into independent units** — each unit must be:
>    - Self-contained (no cross-unit dependencies within a batch)
>    …
>    Write the decomposition to a plan document at `docs/plans/plan-<ID>.md`, following the
>    structure `/plan` step 5 declares … plus one additional required section:
>    - **Batch Manifest** — one row per unit: `| Task ID | Description | Assigned agent | Branch |`.
>      This is where the branch is written down; `docs/tasks/active-tasks.md` is not (step 5). Each
>      `Branch` cell must equal `agent/<Assigned agent>/<Task ID>`, so the manifest cannot drift
>      from the ledger row it describes.
> 3. **Create worktree isolation** — for each unit:
>    - Allocate the unit's task ID, ledger row and task brief first (step 5) — the branch name
>      contains the task ID
>    - Create a dedicated worktree and branch using the worktree-isolation skill
>    - Branch naming: `agent/<agent-name>/<task-id>`, per `git-workflow.md` § "Agent Worktree Branch
>      Naming" and the worktree-isolation skill's own convention
> 5. **Track progress** — record each unit as a task in `docs/tasks/active-tasks.md`, using that
>    file's own 7-column schema (`AGENTS.md` § Task Protocol) and never a five-field manifest row,
>    which its validator rejects:
>    - Format (7 columns, exact order):
>      `| T<NNN> | BATCH <slug>: <description> | <agent-slug> | pending | P0\|P1\|P2 | <dep-ids or —> | YYYY-MM-DD |`
>    - Use the NEXT sequential `T<NNN>` ID for every unit. NEVER a `U<n>` …
>    …
>    - `Depends on` must not name another unit of the same batch … A dependency on a task *outside*
>      the batch is permitted.
>    - The branch is **not** a ledger column. …
>    - … The ledger is authoritative for status; the manifest is not a second status record.

These remain the command's only structurally checkable steps. Steps 1, 4, 6 and 7 are analysis,
delegation, verification and human PR guidance, and `## Important`'s "Present the decomposition plan
for user approval" is a human interaction with no declared artifact.

Three independent assertions, the same three as before the amendment — relocated, not dropped:

- **A (step 2) — independence.** No unit's declared dependencies may name another unit in the same
  batch. Read from the unit's `Depends on` cell in `active-tasks.md`, tokenised exactly the way
  `validate-tasks.py:61`'s `DEPENDS_ID_RE` tokenises it for checks `C12`/`C13`/`C14` — which step 5
  itself names as the enforcement home for this constraint. A dependency on a task outside the batch
  is explicitly permitted and is not a violation.
- **B (step 3) — branch naming.** Every unit's branch matches `agent/<agent-name>/<task-id>`, and —
  per step 2's Batch Manifest clause — *equals* `agent/<Assigned agent>/<Task ID>` rather than
  merely being well-formed. This is checkable against the ledger row, not just against a regex,
  which is why it is a stronger assertion than the `batch/<slug>/<n>-<desc>` one it replaces.
- **C (step 5) — the manifest.** Each unit is a row of `active-tasks.md` in that file's own 7-column
  schema, carrying the unit's ID (matching the `^T\d{3,}$` that `validate-tasks.py:307`'s `C3`
  applies), a `Title` of the form `BATCH <slug>: <description>` with a kebab-case `<slug>`, the
  unit's agent as `Owner`, and a non-empty
  `Status`. The `branch` is **not** there — it is in the plan document's Batch Manifest, which is
  what assertion B reads.

Step 5 declares five manifest fields, and each has exactly one home
(`batch-manifest-resolution-v1.md` §4.4): **four** in the plan document's Batch Manifest
(`Task ID`, `Description`, `Assigned agent`, `Branch`) and `status` in the ledger row's `Status`
column. The ledger's seven columns remain untouched, and the cell count is still hard-failed as `C2`
by `docs/tasks/validate-tasks.py`:

```python
        if len(row.cells) != 7:
            add_fail(
                fails,
                "C2",
                f"active-tasks.md:{row.line_no} has {len(row.cells)} cells (expected 7)",
            )
```

at line 287, with `C3`'s `ID_RE.fullmatch` check at line 307 and `ID_RE = re.compile(r"^T\d{3,}$")`
at line 11. (The pre-`T541` text of this file and of `case.yaml` cited `validate-tasks.py:195` for
the cell-count check; that citation was stale, and the quoted one-line `add_fail` form has since
been wrapped across five lines.)

## Pass condition
`fixture/decomposition.md` declares at least two units in a four-column Batch Manifest
(`Task ID | Description | Assigned agent | Branch`), each with a distinct `^T\d{3,}$` task ID, a
non-empty description and agent, and a branch that both matches
`^agent/[a-z0-9][a-z0-9-]*/T\d{3,}$` and equals `agent/<that row's agent>/<that row's task ID>`; and
for every unit, `fixture/docs/tasks/active-tasks.md` carries a row, in that file's declared 7-column
order, whose `ID` is the unit's ID, whose `Title` matches `^BATCH [a-z0-9][a-z0-9-]*: \S` (the
literal `BATCH `, a kebab-case slug, a colon and space, and a non-empty description), whose `Owner`
is the unit's agent, whose `Status` is non-empty, and whose `Depends on` names no other unit of the
batch.

## What is deliberately not asserted
Recorded here so that it can be overruled rather than discovered. `ADR-007` Validation criterion 1
requires the replacement checker to assert "the same number of structural elements with the same
ordering and value constraints" as the one it replaces — which for a re-derivation whose elements are
already *stronger* (assertions A and B both are) is a ceiling as much as a floor.

1. **Step 2's declared plan-document path and `/plan`'s six section headers.**
   `batch-manifest-resolution-v1.md` §7 offers this as its one net addition and instructs that it be
   omitted, and the omission stated, if §4.1's counter-reading is taken. It is omitted. §4.1 itself
   records that under either reading "no case outcome or promotion outcome moves", and adding a sixth
   element would exceed criterion 1's element count. The fixture keeps the filename
   `decomposition.md` for the same reason: the checker asserts the document's *content*, not its
   path. A future task that wants the path and the six headers asserted should add them together,
   with the fixture moved to `fixture/docs/plans/plan-<ID>.md` — and should expect to inherit
   `/plan`'s own standing red (`command-contract-resolution-v1.md` row A) while doing so.
2. **A *declared* character class for step 5's `<slug>` — there still is none, and since `T544` the
   check asserts one anyway.** This is the one place a reader should be suspicious, so the basis and
   its limit are both stated.
   - **Before `T544`** only what was declared was asserted — the literal `BATCH ` prefix, a
     non-empty colon-terminated slug, a non-empty description (`^BATCH [^:\s][^:]*: \S`) — because
     the fixture's ledger Titles read `BATCH structured-logging U1: …`. The interposed
     `U1`/`U2`/`U3` was a residue of the very `U<n>` unit-ID scheme step 5's amendment abolishes,
     surviving inside the evidence offered for its abolition, and a kebab-case check would have
     rejected it. `T541` held no authorization over the ledger half and left it byte-identical.
   - **`T544` stripped the marker** and tightened the Title check to
     `^BATCH [a-z0-9][a-z0-9-]*: \S`, the form `T541` named as assertable once the marker was gone.
     The tightening is strict: every Title the new regex accepts, the old one accepted.
   - **The basis is convention, not declaration.** Every slug this repository materializes is
     lowercase kebab-case: the `<agent-name>` that `git-workflow.md` declares kebab-case and assertion
     B already checks, the task-management skill's "agent slug, kebab-case", and every
     `docs/decisions/ADR-<NNN>-<slug>.md` filename. The word *slug* itself denotes a single
     whitespace-free token, which is exactly what the `U1` residue violated.
   - **The limit.** `batch.md` does not say `<slug>` is kebab-case, so a Title such as
     `BATCH structured_logging: …` or `BATCH release-v6.13.0: …` satisfies the command's literal text
     and fails this check. The circularity worry — tightening a regex to match a fixture just edited —
     is answered by the order of events (`T541` named `^BATCH [a-z0-9][a-z0-9-]*: ` in this file
     before the fixture changed; `T544` added only the trailing `\S` the old regex already had), not
     by any declaration. Declaring `<slug>`'s character set in `batch.md` step 5 would turn this
     from a convention the check enforces into a contract it measures; that is a knowledge-base
     change outside this case.
3. **Self-dependency, lifecycle-status membership, and slug consistency across a batch's rows.** A
   row naming *itself* in `Depends on` is not treated as a cross-unit dependency (it is not "another
   unit"; `validate-tasks.py`'s `C13` catches it on the real ledger), `Status` is required non-empty
   rather than a member of `AGENTS.md`'s lifecycle set (`C4`'s job), and the batch's rows are not
   required to share one slug. All three are defensible additions; none is declared by §7, and §7's
   spec is the ceiling.

## Category
No longer a defect of any flavour. The conflict this case recorded was real, was adjudicated by
`T535` on `ADR-007` branch 1 against two different higher-authority documents, and was cured by
amending the command rather than by weakening this check: assertions A and B are both **stronger**
than the elements they replace, assertion C gained conjuncts, and no field was deleted, no regex
loosened and no second form admitted (`ADR-007` §5). The case now measures the live contract, which
is the property it lost the moment step 3 and step 5 were amended — under the superseded checker it
returned `False` against this very fixture even after the fixture was made fully conforming
(verified by `T541`, by running the superseded `check()` against the re-authored fixture).

**This does not make `/batch` promotable.** It is `maturity: experimental` and must clear
`experimental → beta` on a separate component-state decision before `beta → stable` is in question
(`batch-manifest-resolution-v1.md` §8).

## Provenance
**Ledger: real schema, real header; not edited by `T541`, and its three Titles edited by `T544`.**
`fixture/docs/tasks/active-tasks.md` carries this repository's own real title, header and separator
lines copied byte-identically, with three 7-column unit rows using the next free IDs at authoring
time (`T534`–`T536`). It conformed to the amended step 5 **cell for cell** with no edit — 7 cells,
`^T\d{3,}$` IDs, real agent-slug `Owner`s, a valid `Status`, `Priority`, `—` in `Depends on`, and a
well-formed date, all confirmed against `validate-tasks.py`'s own `parse_table_rows`, `ID_RE` and
`STATUS_SET` — which is why `T541` deliberately left this half alone. It did **not** conform in the
Title form: each Title read `BATCH structured-logging U<n>: …`, not step 5's
`BATCH <slug>: <description>`, and `T535` and the orchestrator had both cited these rows as evidence
that the ledger half "already conforms". `T544` removed the `U1`/`U2`/`U3` marker from the three
Titles and changed nothing else in the file; see § "What is deliberately not asserted" item 2.

**`decomposition.md` is hand-authored, and was re-authored by `T541`.** `ADR-007` §5 permits exactly
this — "Re-authoring a *hand-authored fixture* to a corrected contract is permitted and is not
relaxation: the check's strength is unchanged and only the example moves" — and `ADR-007`'s
sibling-fate corollary's first row ("branch 1, where the amendment changes only a *name or path*")
is the limb `T541` took: the manifest's unit-ID scheme and branch pattern are **names**, the
branch's move from a ledger column to a named plan-document section is a **path**, the two artifact
classes the case reads are the same two files as before, and the ledger half needed no edit at all.
The change it decomposes (migrating ad-hoc `print()` diagnostics to a shared structured logger) is
illustrative and the units' contents are not graded — only their structure, their branch naming,
their agreement with the ledger, and their mutual independence.

Surveys from the original authoring, unchanged and still true of `batch/*`:

```
git branch -a --list 'batch/*'                                             ->  0 branches
grep -c 'batch/' docs/tasks/active-tasks.md docs/tasks/completed-tasks.md  ->  0, 0
```

No `/batch` run has ever produced a committed artifact here, so there was nothing real to source the
decomposition from; that absence is documented rather than worked around, following
`new-feature-plan-doc-compliant/brief.md`'s precedent.
