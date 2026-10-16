# plan-091 — Promote the four wave-3 greens; adjudicate the PoC-track conflicts

**Created:** 2026-10-01
**Based on:** `docs/plans/plan-090-golden-wave-3.md` §2; MR !443 (T561).
**Scopes:** `T562`, `T563`.

## 1. `T562` — promotion, measured before it was scoped

A dry run on `develop` flipped `/team-status`, `/new-poc`, `/poc-demo`, `/evaluate-poc` to `stable`: **all four pass
every `stable` criterion**. `/validate-workflow`, flipped as a control, **fails criteria 3 and 7 on its own red
case** — the ladder blocking exactly one promotion, as in waves 1 and 2. Commands move **9/10 → 13/6**.

**Caveat on the record:** the three PoC greens certify clause **content**, not output **paths** — the paths are what
`T563` is deciding. `stable` means *passes the golden cases that exist*, as it always has here.

## 2. `T563` — the PoC conflicts (P11, P29, P30, P31), decided before anything is amended

Four disagreements about where the PoC track writes its plan, debt scorecard and checkpoints, and whether
`INCONCLUSIVE` is a legal outcome. `T563` decides each under ADR-007 and costs the follow-up, including golden
coupling. It changes nothing itself. **P28** (`/validate-workflow`'s non-verdict gates) is a separate,
single-command repair and stays parked until after `T563`.

`T562` and `T563` touch disjoint files and run in parallel.
