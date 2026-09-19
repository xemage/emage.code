# Case: new-feature-checkpoint-line-compliant

## Command under test
`/new-feature`

## Brief (illustrative — not executed live)
Same feature as `new-feature-plan-doc-compliant` (audit-log-export), now at Phase 3 after
implementation completes.

## What this checks
`implementation/knowledge/commands/new-feature.md` Phase 3 step 7: "Write a checkpoint after
implementation completes: `[CHECKPOINT] id=feature-<slug> | done=[...] | in_flight=[...] |
blocked=[...] | artifact_refs=[...] | next=[...]` — Store at
`docs/checkpoints/checkpoint-feature-<slug>.md`."

## Pass condition
A file at `fixture/docs/checkpoints/checkpoint-feature-<slug>.md` contains a line beginning
`[CHECKPOINT] id=feature-<slug>` with `done=`, `in_flight=`, `blocked=`, `artifact_refs=`, and
`next=` keys all present.

## Provenance
Hand-authored. See `new-feature-real-checkpoint-format-drift` for a real checkpoint from this
repo's history checked against this identical contract — it does not satisfy it, which is why
this compliant case is hand-authored rather than sourced.
