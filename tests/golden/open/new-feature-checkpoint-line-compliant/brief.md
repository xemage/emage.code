# Case: new-feature-checkpoint-line-compliant

## Command under test
`/new-feature`

## Brief (illustrative — not executed live)
Same feature as `new-feature-plan-doc-compliant` (audit-log-export), now at Phase 3 after
implementation completes.

## What this checks
`implementation/knowledge/commands/new-feature.md` Phase 3 step 7: "Write a checkpoint after
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

## Provenance
Hand-authored. **Re-purposed at T520** per `ADR-007` verdict B (branch 1 — the clause
contradicted `AGENTS.md`). This case previously encoded step 7's pre-amendment single-line
`[CHECKPOINT] id=feature-<slug> | done=[...] | ...` marker stored at
`docs/checkpoints/checkpoint-feature-<slug>.md`. When that clause was amended, the old fixture
became non-conforming in its own right, so this case needed a new fixture *and* a new `check()`
rather than a re-fixture — see `docs/artifacts/command-contract-resolution-v1.md` §3 row B.

See `new-feature-real-checkpoint-format-drift` for the identical check applied to a real
checkpoint from this repo's history; under the amended contract that case passes too, which is
the point: the contract and the corpus now agree.
