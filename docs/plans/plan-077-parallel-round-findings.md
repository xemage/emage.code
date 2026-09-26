# plan-077 — the three findings from T529/T536/T537

**Status: scoped 2026-09-26, awaiting approval to dispatch.**
Based on: `docs/tasks/task-T529.md`, `docs/tasks/task-T536.md`, `docs/tasks/task-T537.md`;
`docs/plans/plan-076-wave2-findings.md`; `docs/artifacts/protected-paths-v1.md` §5.

## 0. Why a third findings plan

`plan-076` recorded wave 2's four findings; executing three of them produced three more. That is not
drift — it is what happens when tasks are told to report rather than work around, and each of these
was found by an implementer refusing to widen its own grant. They get rows for the same reason as
`plan-076`'s: **a hand-fix plus a ledger note is not a fix.**

| # | Found by | Defect | Task |
|---|---|---|---|
| 1 | `T536` | `team-status.md` has the same `in_review` gap, weaker form | **`T538`** |
| 2 | `T529` | no guard anywhere in `tests/golden/**` detects array cardinality | **`T539`** |
| 3 | `T537` | `validate-tasks.py` detects neither self-dependency nor cycles | **`T540`** |

## 1. `T538` — the same defect, propagated by duplication

`team-status.md` step 7 carries the **identical** node-source bullet naming `in_review` and the
**identical** four `classDef` lines with the same hex values — but **no `Color code:` bullet at all**.
Verified.

So it is `T536`'s defect in a weaker form: nothing contradicts the bullet in prose, yet the template
still cannot colour an `in_review` node. The two commands are near-duplicates of that whole section,
which is *how* the defect propagated and is the more interesting finding: **a copied section carries
its gaps.** Worth a glance at whether any other command duplicates that Mermaid block.

Trivial fix, same colour for palette consistency. `team-status` is `experimental`, so nothing promotes
either way.

## 2. `T539` — the guard that does not exist

`T529` established, and the orchestrator verified, that
`tests/golden/open/handoff-payload-schema-fields-real/expect.py` implements `required`,
`additionalProperties`, `enum`, `pattern` and `properties` — and **zero array keywords**. No `items`,
no `minItems`, no `maxItems`.

**Consequence: no case in `tests/golden/**` can detect an empty or malformed array**, at any schema
version. The orchestrator's own mutation against `writablePaths` could never have flipped, in either
direction, and the conclusion drawn at the time — "my mutation was mis-designed, the check is fine" —
was only half right. Write-scope cardinality is now covered solely by `T529`'s five new
`tests/functional/` tests.

`T529` offered two routes and this task must choose:

- **Extend `_object_matches_schema()` to array keywords.** Strengthens every present and future case
  that embeds a schema. Larger, and it is a protected-path edit to a checker.
- **Add a case whose oracle is `validator.py`**, which now genuinely enforces the constraint.
  Narrower, but introduces a case that depends on runtime code rather than on a fixture alone — which
  `golden-suite-format-v1.md` §2.2 may or may not permit. **Check that before choosing it.**

Either way this **strengthens** a check, so `ADR-007` §5's prohibition on relaxing is not the binding
constraint here — the risk is the mirror image, over-strengthening, exactly as in `T531`. A guard that
starts rejecting fixtures that legitimately conform is worse than the gap.

## 3. `T540` — two cheap additions inside `C12`'s shape

`T537` delivered `C12` and named three things it deliberately did not do. Two are in scope here:

- **Self-dependency passes.** A row declaring `Depends on: <its own ID>` resolves, because its ID is
  in `active_ids`. Cheap to add inside `C12`.
- **Cycles are not detected.** `/sprint-status` builds a DAG from these edges and a cycle breaks it.
  Different failure semantics, so probably a separate code rather than an extension of `C12` — that is
  the task's call.

The third — **a dependency on a `cancelled` task resolves**, since cancelled rows live in
`completed-tasks.md` — is deliberately **excluded**. `T537` was right that it is a policy question
rather than a defect: depending on cancelled work may be legitimate during a transition. Deciding it
needs a rule first, and inventing one inside a validator patch is how contracts get made by accident.

**`T537`'s trap 2 still binds and is restated in the brief: a false positive in `validate-tasks.py`
blocks every ledger edit in the repo and runs in CI.** The real ledger must stay `PASS`, and both new
checks must be proven to fire on synthetic input and not on the live tree.

## 4. What none of these do

All three are `P2`, so per `T524`'s correction they do not enter criteria 3/7's open-defect scan.
**None promotes anything.** `T538` and `T540` touch no protected path; `T539` does, and its
authorization is deliberately left for the brief to scope narrowly once the route is chosen — because
the two routes need different grants, and issuing the union of both would be the widest grant in this
phase for no reason.
