# Task T432 — scripts/check-maturity.py (CI-enforced)

**ID:** T432
**Owner:** devops-engineer (matches `plan-041`'s own reasoning — this repo's existing precedent of
CI/tooling scripts going to `devops-engineer`, T413/T419/T422; tool grant checked at recording time
— `implementation/knowledge/agents/devops-engineer.md`'s registered grant is `[read, search, edit,
execute, web, mcp__gitlab, mcp__fetch]`, has `execute` — re-confirm this is still accurate at
actual dispatch time, do not assume it stays true indefinitely)
**Status:** pending — recorded and scoped, **not dispatched this session** (T431, its only
dependency, is done; recorded now to satisfy this repo's own "no ledger row without a backing
brief" precondition, mirroring the `T457`/`T458` precedent of a full brief existing before
dispatch)
**Priority:** P1 (blocks T433, which needs a real, working `check-maturity.py` before Wave 1
promotion claims can be mechanically verified — though `T433` also needs its own separate
attention per `plan-041`'s own flag that it is Phase 3's largest single task)
**Depends on:** T431 (done — `docs/artifacts/maturity-promotion-criteria-v1.md`)
**Blocks:** T433
**Created:** 2026-09-10
**Completed:** —
**Based on:** `docs/plans/plan-041-phase3-maturity-ladder-detailed-planning.md` (approved, merged
MR !252) — specifically its T432 row; `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 3
(T432's original nominal scope: "mechanically verify a claimed level; CI-enforced. A component may
not *declare* `stable`; it must *satisfy* it."); `docs/artifacts/maturity-levels-v1.md` (T430 — the
enum and the mandatory-field policy); `docs/artifacts/maturity-promotion-criteria-v1.md` (T431 —
the concrete, per-category/per-transition criteria this script must implement as real checks, not
re-derive or reinterpret).

## Objective

Implement `scripts/check-maturity.py`: given a component's declared `maturity` value (from its
frontmatter, mandatory per T430) and its category (`agent`/`command`/`instruction`/`skill`),
mechanically verify that the component actually satisfies every criterion `docs/artifacts/
maturity-promotion-criteria-v1.md` defines for that level — not merely that the field contains a
valid enum string. A component claiming `stable` with no qualifying evidence must fail the check,
loudly, in CI. Wire this into the same CI gate set `implementation/scripts/check.py` already runs
(`--registry`, or a new flag — your call, document it), so a claimed-but-unearned promotion cannot
merge silently.

## Inputs

- `docs/artifacts/maturity-promotion-criteria-v1.md` (T431 — the concrete criteria per category/
  transition, including the `# maturity-evidence: <category>/<id>` tag convention it defines for
  `agent`/`instruction`/`skill`'s golden-case substitute)
- `docs/artifacts/maturity-levels-v1.md` (T430 — enum, mandatory-field policy)
- `implementation/registry/schema.json`, `implementation/scripts/generate-registry.py` (the
  existing registry pipeline this script's checks should compose with, not duplicate or bypass)
- `implementation/scripts/check.py` (the existing CI gate runner this new check should integrate
  into)

## Expected outputs

- `scripts/check-maturity.py` (or `implementation/scripts/check-maturity.py` — match this repo's
  existing convention for where registry/knowledge-adjacent scripts live; state your actual
  choice), implementing real, per-criterion checks for every category/transition `maturity-
  promotion-criteria-v1.md` defines.
- Wired into `implementation/scripts/check.py`'s gate set (new flag or folded into an existing one
  — your call, document the choice).
- Tests proving the checker itself is correct — both that a component satisfying all criteria for
  its claimed level passes, and that one missing any single required criterion fails with a clear,
  actionable message naming which criterion failed.

## Acceptance criteria

1. A component whose frontmatter claims `stable` but does not satisfy at least one of `docs/
   artifacts/maturity-promotion-criteria-v1.md`'s stated `beta→stable` criteria for its category
   fails the check, with a message naming the specific unmet criterion (not just "invalid").
2. A component satisfying every stated criterion for its claimed level passes.
3. The check runs against the real, current state of all 77 registry-eligible components without
   crashing — report what the real current pass/fail distribution is (expected: most/all still at
   `experimental`, which should trivially pass the `experimental` bar per T431's design — confirm
   this is genuinely true rather than assumed).
4. Wired into CI (`implementation/scripts/check.py` or an equivalent existing gate), not a
   standalone script nobody runs.
5. `python3 tests/run.py` passes with no regressions.
6. Coding standards (max 50-line functions, max 4 parameters, early returns) and Conventional
   Commits followed; branch pushed, MR opened against `develop`, not self-merged.

## Constraints

- **No paid or recurring-cost API calls.**
- **Do not touch `.mcp.json`, anywhere, for any reason. Do not touch the main checkout
  (`/home/emage/Code/emage/emage.code`).**
- **Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`**
  — if `maturity-promotion-criteria-v1.md`'s `# maturity-evidence:` tag convention genuinely
  requires adding a tag inside a golden case's `expect.py` as one valid evidence location (per its
  own text), treat any such edit as a `type: unclear_requirements` blocker requiring an explicit,
  disclosed exception request before touching that path, per `protected-paths-v1.md`'s documented
  exception process — do not edit unilaterally.
- **Do not touch `feature/T475-codex-platform-integration`. Do not start T433 or any later Phase 3
  task.**
- **Confirm your own tool grant before starting** — re-check `implementation/knowledge/agents/
  devops-engineer.md` directly, do not assume this brief's recorded grant is still accurate.
- **Work in your own worktree/branch** (`agent/devops-engineer/T432`), created from `develop`.
  Commit as you go; run the full test suite before reporting completion. **Do not self-merge** —
  push and open a merge request, then stop.

## Blocker protocol

Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`) +
severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries before
escalating to the orchestrator. If any of `maturity-promotion-criteria-v1.md`'s stated criteria
turns out not to be mechanically checkable as worded despite T431's own acceptance criterion that
it should be, report this as a `type: unclear_requirements` blocker naming the specific criterion,
rather than silently inventing a looser check that doesn't actually verify what was intended.

## Execution notes

(To be filled in by the implementing agent during work, if useful — not required.)
