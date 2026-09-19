# Checkpoint 031 — Phase 3: T436 done, T437 is the last remaining task

> Written by the orchestrator after T436's closure. Future agents resuming this thread need only
> this checkpoint + `docs/artifacts/phase3-maturity-demotion-decision-v1.md`, not the full T436
> dispatch history.

## Summary

**T436 (honest demotion pass) is done, merged to `develop`, and independently verified.** The
Product Owner's real, evidence-grounded conclusion: **nothing among the 46 non-`stable` components
currently warrants `deprecated`** — every category's gap (14 commands blocked on a golden-case
coverage gap, 3 commands blocked on tracked defects, 4 agents blocked on open `T456`/`T457`, 4
skills with real content defects, 14 genuinely unsurveyed skills) is a live, trackable, fixable
item, not a genuine dead end. No file changes resulted; no follow-up technical dispatch was
required.

**A real dispatch-mechanics finding**, distinct from every prior Phase 3 tool-grant issue: Product
Owner has neither `edit` nor `execute` at all — the only Phase 3 agent so far with neither,
confirmed as a deliberate security boundary, not an oversight. Its first dispatch attempt correctly
refused to fabricate a decision when the standard "go fetch `origin/develop` yourself" pattern
failed (no git/Bash capability, and its `Read` tool only sees the stale main checkout). Redispatched
with the real evidence embedded directly in the prompt, which worked cleanly. Disposition differed
from every prior tool-grant gap: not a full reassignment (would lose the real product-judgment
intent), but a two-phase split — Product Owner decides, the orchestrator transcribes the decision
into a committed artifact.

**A third variant of the self-referential ledger-defect regression was found and fixed before
dispatch**: T436's own required Owner field necessarily named its owner, itself one of Wave 2's
now-`stable` components — a real, disruptive case (unlike T434/T435's "incidental mention" variant,
this component was already shipped) — fixed by using the agent's display name instead of its
registry id.

## Real, independently-verified current state (not assumed)

- `python3 docs/tasks/validate-tasks.py`: PASS (3 active, 273 completed)
- `python3 tests/run.py`: 514 tests, OK, skipped=24 (unchanged, as expected for a decision-only
  closure)
- `python3 implementation/scripts/check-maturity.py --root implementation`: 77 components, 0
  failing — unchanged from `checkpoint-030` (20 agents, 4 instructions, 7 skills `stable`; 19
  commands remain `experimental`, blocked on the disclosed golden-case coverage gap)

## Phase 3's remaining task list — confirmed directly against `plan-041`'s own table

`plan-041`'s Phase 3 task table (T430-T437) is now **7 of 8 done**. **T437 is the only remaining
task**: "Regenerate `summary.md` + add maturity-distribution table to the release-checkpoint
template. `release-manager`, last in sequence since it reports on the finished state of T430-T436."
T437's only dependency is T436, now done. Not recorded or dispatched this session.

## Process notes worth carrying forward

- **The "avoid naming a real registry component id in an open task's own prose" discipline has now
  hit three distinct variants across T433-T436**: (1) a task naming its own promotion subjects
  (T433, expected/benign since those subjects weren't yet `stable`); (2) a task naming an
  unrelated already-`stable` component as incidental context (T434/T435, caught pre-dispatch); (3)
  a task's own *required* Owner field naming an already-`stable` agent (T436, caught pre-dispatch).
  As more components become `stable`, this collision surface grows — any future Phase 3/4+ task
  brief should be checked against the full current stable-id list before dispatch, not just
  the specific ids a prior incident happened to involve.
- **Not every read-only agent's tool gap looks the same.** `solution-architect` (T430/T451
  precedent) has `edit` but not `execute` — can write docs, can't run scripts/tests. `product-owner`
  has neither — can't write anything at all. The correct disposition depends on which: a
  write-capable-but-Bash-less agent can often still do the real work with the orchestrator handling
  only the mechanical git steps; a fully read-only agent by design (per this repo's own security
  classification) needs the two-phase decision/implementation split T436 used, not a workaround.

## Token metrics

Not separately tracked against a phase budget this session.

## Next steps

- **T437** (`release-manager`, small scope: regenerate `summary.md` + add a maturity-distribution
  table to the release-checkpoint template) is Phase 3's last task — not dispatched this session.
  Once done, Phase 3 (T430-T437) closes in full.
- **Phase 4 (Task-Tier Routing)** remains unblocked at the gate level (Gate G2 closed per `ADR-006`)
  but still needs its own dedicated planning pass (mirroring `plan-037`/`plan-038`/`plan-041`)
  before any `T44x` brief is authored — not started this session.
- Three real, disclosed follow-up gaps remain from T434-T436, none dispatched: (1) 14 commands need
  golden-case coverage under a disclosed protected-path exception; (2) 3 commands need a
  verdict/header-format-drift fix; (3) 4 skills need a content-correction pass (one,
  `dependency-graphing`, needs an explicit schema-vs-skill scoping decision first).
- **T456/T457/T458** (Phase 5 follow-ups) and **`feature/T475-codex-platform-integration`** remain
  exactly as prior checkpoints left them — untouched this session.
