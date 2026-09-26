# Case: new-feature-real-checkpoint-format-drift

## Command under test
`/new-feature`

## Brief (illustrative — not executed live)
Same underlying contract as `new-feature-checkpoint-line-compliant`, applied to a real
checkpoint already in this repo's history instead of a hand-authored one:
`docs/checkpoints/checkpoint-017-t417-harbor-oracle-smoke-complete.md` (T417, completed
2026-08-13).

## What this checks
The identical contract as `new-feature-checkpoint-line-compliant`:
`implementation/knowledge/commands/new-feature.md` Phase 3 step 7 — "Write a checkpoint after
implementation completes, per `AGENTS.md` § Checkpoint Protocol: Store at
`docs/checkpoints/checkpoint-<SEQ>-<phase>.md` — Include, in this order: completed tasks, key
decisions, blockers, token metrics, next steps."

The five required elements come from `AGENTS.md` § Checkpoint Protocol's own list, **not** from
`docs/checkpoints/_template.md`'s heading set. The template carries sections `AGENTS.md` does not
mandate (`## Phase summary`, and `## Maturity distribution`, added later by T437), and a check
derived from the template would fail conforming checkpoints that predate those sections.

## Pass condition
Exactly one file exists under `fixture/docs/checkpoints/`; its filename matches
`checkpoint-<SEQ>-<phase>.md` with a numeric `<SEQ>`; and it carries headings for all five
`AGENTS.md`-mandated elements — completed tasks, key decisions, blockers, token metrics, next
steps — each with a non-empty body, appearing in that order. Heading qualifiers are tolerated
(`## Blockers (active)`, `## Completed tasks (this checkpoint)`); a missing, empty or
out-of-order element fails.

The real fixture satisfies all five in the declared order: `## Completed tasks (this checkpoint)`,
`## Key decisions`, `## Blockers (active)`, `## Token usage`, `## Next steps`. Its unmandated extra
sections (`## Summary`, `## Open / carried over`, `## Artifacts produced`, `## Compression note`)
are not penalised — the contract names a required set, not an exhaustive one.

## Provenance
**Fully real.** The fixture is a copy of
`docs/checkpoints/checkpoint-017-t417-harbor-oracle-smoke-complete.md` from this repository's own
history, placed at the repo-relative path the contract declares as the checkpoint's storage
location. It has never been edited to reach a pass.

**Re-purposed at T520**, per `ADR-007` verdict B (branch 1 — the command clause contradicted
`AGENTS.md`, so the clause was amended rather than the corpus). Its hand-authored sibling
`new-feature-checkpoint-line-compliant` was re-purposed in the same change and runs the identical
check; see `docs/artifacts/command-contract-resolution-v1.md` §3 row B.

### History — why this case was `known_failing` before T520
Retained as the record of the drift this case was authored to track, not as a live claim about the
current contract.

Before `ADR-007`, step 7 declared a single-line marker,
`[CHECKPOINT] id=feature-<slug> | done=[...] | in_flight=[...] | blocked=[...] |
artifact_refs=[...] | next=[...]`, stored at `docs/checkpoints/checkpoint-feature-<slug>.md`. This
case was `known_failing / tracked_defect` against that clause, on two grounds recorded when it was
authored:

- The fixture carries **no** `[CHECKPOINT] id=...` marker line anywhere, and is not feature-scoped
  at all — it is task-scoped, following `AGENTS.md`'s `checkpoint-<SEQ>-<phase>.md` convention
  rather than `checkpoint-feature-<slug>.md`.
- A corpus survey (`grep -rn "^\[CHECKPOINT\] id=" docs/checkpoints/*.md`) returned **zero**
  matches across every real checkpoint file in the repository. The declared single-line marker
  format had no precedent in actual practice, which instead followed the richer `AGENTS.md`
  Checkpoint Protocol convention uniformly.

That absence of precedent is what `ADR-007` adjudicated: the contract was amended toward
established practice, and the same untouched real fixture now passes. Contract and corpus agree,
which is the point of keeping this case green against a real artifact.
