# Failure classification: `new-feature-real-checkpoint-format-drift`

**Scheme:** `docs/artifacts/failure-taxonomy-v1.md`
**Source case:** `tests/golden/open/new-feature-real-checkpoint-format-drift/`
**Command:** `/new-feature`
**`known_failing_category` (T410 axis):** `tracked_defect`

## Axis classification

| Axis | Value |
|---|---|
| `cause` | `established-practice-drift` |
| `behavior` | `required-marker-line-absent` |
| `mechanism` | `whole-block-absence` |

## Why

`implementation/knowledge/commands/new-feature.md` Phase 3 step 7 declares a
`[CHECKPOINT] id=feature-<slug> | done=[...] | in_flight=[...] | blocked=[...] |
artifact_refs=[...] | next=[...]` single-line marker. The fixture — a real repo checkpoint
(`docs/checkpoints/checkpoint-017-t417-harbor-oracle-smoke-complete.md`) — instead uses the
richer, established `AGENTS.md` Checkpoint Protocol convention (`## Summary`, `## Completed
tasks`, `## Token usage`, etc.), with no single-line marker anywhere. The case's own corpus
survey (`grep -rn "^\[CHECKPOINT\] id=" docs/checkpoints/*.md`) returns zero matches across every
real checkpoint in the repo, not just this one fixture.

- **`cause`**: `established-practice-drift` — the declared marker format is unambiguous; a
  corpus-wide survey (not a single hand-picked example) shows real practice has consistently used
  a different, incompatible convention instead.
- **`behavior`**: `required-marker-line-absent` — the specific declared single line never
  appears, distinct from a whole missing section because the contract's unit here is one line,
  not a multi-line block.
- **`mechanism`**: `whole-block-absence` — no partial trace of the declared marker convention
  exists in the document at all (the document uses an entirely different, unrelated structure).
