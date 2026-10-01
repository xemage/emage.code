# plan-090 — Golden wave 3

**Created:** 2026-10-01
**Based on:** `docs/plans/plan-072-phase9-golden-case-coverage.md` §3 (wave 3, left unscoped on purpose);
`docs/checkpoints/checkpoint-037-phase9-queue-empty-root-refreshed.md` §8.
**Scopes:** `T561`.

`plan-072` deliberately left wave 3 unscoped until waves 1 and 2 had tested the approach. Both did what the
plan hoped: each produced exactly one honest red case that blocked exactly one promotion while the greens passed
clean. Wave 3 covers the last five commands with no golden case — `/team-status`, `/validate-workflow`,
`/new-poc`, `/poc-demo`, `/evaluate-poc`, all `experimental`.

It is the weakest-grounded wave by design: the PoC three have no corpus at all (ADR-007 branch 4), and two parked
findings bear directly on it — **P9** (`/validate-workflow` likely always FAILs) and **P12** (the PoC debt
scorecard specified in two places). The brief tells the implementer to **report** both, not resolve them, and
says plainly that a red case here is a correct outcome.

After the wave: one baseline authorization from the user (v13), then — separately — a promotion run for whichever
of the five pass. P9 and P12 may become rows depending on what the cases show.
