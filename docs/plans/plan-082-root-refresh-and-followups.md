# plan-082 — Curing root drift safely, and T549's two follow-ups

**Created:** 2026-09-30
**Based on:** `docs/artifacts/root-projection-resolution-v1.md` (T543, MR !420);
`docs/tasks/task-T549.md` (MR !419); `docs/plans/plan-081-t546-repair-verdicts.md`.
**Scopes:** `T550`, `T551`. **Amends:** `T548` (grant extended), `T538` and `T547` (root-drift rule).

## 1. `T550` — the gate detects root drift; nothing can yet cure it safely

T543 established that repo-root drift is a **defect**, not a convention: those trees are the live
runtime of every agent in this repository. Two consequences are live today, both verified:

- root `.claude/agents/orchestrator.md` lines 96–97 still instruct direct commits to `develop` for
  docs and chore changes — the protected-branch violation T542 removed from source;
- root `/consolidate-memory` projections still carry the data-loss step 5 that T549 removed.

T543's gate makes further drift **visible and declared**. It does not cure the existing 55 paths,
because the only mode `install.sh` permits at the repository root is `--update`, which also runs the
`docs/tasks` ledger merge — and **the last root refresh, `fee245a`, took `active-tasks.md` from 2460
lines to 11.** A plain install at the root is refused, and the refusal points at `make sync`, which
does not write the root at all. **The only sanctioned cure is the one that last destroyed the ledger.**

`T550` adds a projections-only mode that refreshes the derived harness and touches nothing the
project owns, proven against synthetic roots under both `rsync` and the `cp` fallback CI uses.

It is **P1 with `**Affects:** —`**. `install.sh` is not a registry component, so the row blocks no
promotion and cannot turn `check.py --maturity` red — the trap `plan-081` §1 measured for P1 rows that
name `stable` components.

## 2. After `T550` merges — one human-approved refresh, no task row

The real root is refreshed **once**, by the orchestrator, **only with the user's explicit approval**
at the time, using the new mode. In the same MR:

1. the declared list in `tests/_baselines/root-install-drift.json` is emptied, and the gate proves it
   — it fails if a declared path no longer drifts, so an incomplete refresh cannot pass;
2. `docs/tasks/` is diffed byte-for-byte before and after, and the MR is abandoned if it moved;
3. `git status` of the main checkout is recorded before and after.

No ledger row is opened for this step: it is one command plus verification, and it is gated on a human
decision rather than on work. It is recorded here so it is a plan, not an improvisation.

Once the list is empty, making "empty" a release condition becomes possible. That is a later decision
and is not taken here.

## 3. `T551` — the `memory-management` skill contradicts the command T549 just fixed

The skill's line 83 says *"For promotions: Add to `AGENTS.md`, remove from MCP Memory"* — the
identical data-loss instruction. The whole skill models `AGENTS.md` as "Tier 2" of a memory
hierarchy. After T549 the two documents disagree, and an agent that loads the skill is told to do what
the command now forbids.

It is a design question — what Tier 2 means where `AGENTS.md` is generated — not a line fix, so it is
its own task rather than an extension of T549. It is `experimental` with no golden case, so it gates
nothing while it waits; P2.

## 4. `T548` amended — one baseline refresh instead of two

T549 made `consolidate-memory-recommendation-table-grounded/brief.md` line 17 stale: it quotes the old
Promote line naming the destructive targets. Fixing it needs a protected-path grant, and every
authorized `tests/golden/**` change drifts the evaluator-hash digest and needs an explicit human
authorization for a new baseline.

T548 already holds a protected-path grant for a golden `brief.md` prose correction. Extending that
grant **before dispatch**, by the orchestrator, folds both into **one** baseline refresh.
`protected-paths-v1.md` §5.1 forbids a *holding agent* from extending its own grant; it does not
forbid the orchestrator from scoping a grant before any agent holds it. The grant is `brief.md` only —
that case's `expect.py`, `case.yaml` and `fixture/` are excluded, and its `check()` must stay `True`.

## 5. `T538` and `T547` amended — the root-drift rule

Once !420 lands, every `implementation/knowledge/` change that does not refresh the root must declare
its root paths in the same MR, or its pipeline goes red. Both open knowledge tasks now say so. `T551`
was written with it. Every future knowledge-task brief must carry it until §2's refresh empties the
list.

## 6. Queue and contention

With T549 archived here and T543 archived after !420: **7 active** — `T538`, `T539`, `T544`, `T547`,
`T548`, `T550`, `T551`.

- `implementation/knowledge/` group: `T538`, `T547`, `T551` — one at a time.
- `tests/golden/**` group: `T539`, `T544`, `T548` — one at a time.
- `T550`: `scripts/install.sh` and new tests only — **no contention**, and the highest-leverage row.

`T550` runs next. One knowledge task and one golden task can run beside it.

## 7. What this plan does not do

- Does not refresh the repo root. §2 is gated on the user.
- Does not change any priority or `maturity:` field.
- Does not archive T543 — its brief is changed by the still-open !420, and archiving it here would
  conflict. It is archived once !420 merges.
- Does not resolve the five decisions still open from `plan-080` and `plan-081` (demotion, batching,
  a standing-debt register, `protected-paths-v1.md` as `-v2`, and — now superseded by T543's gate —
  the `AGENTS.md` parity test).
