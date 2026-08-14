# Case: new-feature-real-checkpoint-format-drift (known_failing / tracked_defect)

## Command under test
`/new-feature`

## Brief (illustrative — not executed live)
Same underlying contract as `new-feature-checkpoint-line-compliant`, applied to a real
checkpoint already in this repo's history instead of a hand-authored one:
`docs/checkpoints/checkpoint-017-t417-harbor-oracle-smoke-complete.md` (T417, completed
2026-08-13).

## What this checks
The identical contract as `new-feature-checkpoint-line-compliant`:
`implementation/knowledge/commands/new-feature.md` Phase 3 step 7's declared
`[CHECKPOINT] id=feature-<slug> | done=[...] | in_flight=[...] | blocked=[...] |
artifact_refs=[...] | next=[...]` line.

## Why this is known_failing today
`checkpoint-017-t417-harbor-oracle-smoke-complete.md` is a real, representative checkpoint —
full markdown sections (`## Summary`, `## Completed tasks (this checkpoint)`, `## Open /
carried over`, `## Key decisions`, `## Artifacts produced`, `## Blockers (active)`, `## Token
usage`, `## Next steps`, `## Compression note`), no `id=feature-...` naming (this checkpoint
isn't feature-scoped at all — it's task-scoped, per this repo's actual `AGENTS.md` Checkpoint
Protocol, which defines `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`, not
`checkpoint-feature-<slug>.md`), and critically **no single-line `[CHECKPOINT] id=...` marker
anywhere**. A corpus survey (`grep -rn "^\[CHECKPOINT\] id=" docs/checkpoints/*.md`) confirms
zero matches across every real checkpoint file in this repo — the `/new-feature` command's
declared single-line marker format has no precedent in actual practice, which instead follows
the richer `AGENTS.md` Checkpoint Protocol convention uniformly.

## Category
`tracked_defect` — the command's declared marker format is unambiguous; real practice has
consistently used a different, incompatible convention (`AGENTS.md`'s Checkpoint Protocol)
instead. Either `new-feature.md` should be updated to match established practice, or real
checkpoints need to start emitting the declared marker line — either way this is a concrete,
trackable contract violation, not a permanent limitation.
