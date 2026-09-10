# Task T435 — Wave 3 promotion (skills/instructions) to `stable`

**ID:** T435
**Owner:** tech-lead (matches `plan-035`/`plan-041`'s own assignment; tool grant checked before
dispatch — `implementation/knowledge/agents/tech-lead.md`'s registered grant is `[read, search,
edit, execute, web, mcp__fetch]`, has `execute`)
**Status:** pending
**Priority:** P1
**Depends on:** T433 (done — Wave 1; re-confirmed from `plan-041`'s own task graph that T435's only
dependency is T433, no other precondition — and, per `plan-041`'s own explicit note, T435 does
**not** depend on T434 either, despite both being "Wave 2/3" — they target disjoint categories and
are dispatched in parallel, not serialized)
**Blocks:** T436 (needs both T434 and T435's actual outcomes)
**Created:** 2026-09-10
**Completed:** —
**Based on:** `docs/plans/plan-041-phase3-maturity-ladder-detailed-planning.md` (approved, merged
MR !252) — specifically its T435 row; `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 3;
`docs/artifacts/maturity-promotion-criteria-v1.md` (T431 — real per-category `beta→stable`
criteria, §3.3 `instruction`, §3.4 `skill`); `docs/artifacts/phase3-wave1-promotion-v1.md` (T433 —
read this first, it documents the real mechanics you will hit and how they were resolved; do not
rediscover them from scratch); `docs/tasks/task-T433.md`'s completion addendum.

## Real scope — computed fresh this session

`plan-041` named this wave's scope as "26 skills + 4 instructions per `summary.md`'s current
counts" at planning time. Two of those 26 skills are now already `stable`, promoted by T433 — see
`docs/artifacts/phase3-wave1-promotion-v1.md` for exactly which — **confirmed directly against
`implementation/registry/index.json` this session, not assumed from the plan's original count.**
Your real remaining scope is **24 skills + 4 instructions = 28 components.** **Deliberately not
naming the 2 already-`stable` skills again here by id, and do not re-derive and repeat their names
literally in your own new prose either** — see the next section for why (an unrelated
self-referential ledger-defect false trip this exact phrasing already caused once, caught and
fixed before this brief was dispatched).

**This is ~3x T433's own scope** (28 vs. 9). **Do not attempt to force full completion of all 28
components in one dispatch.** Produce real, genuine evidence for as many as you can within a
reasonably bounded effort — instructions are likely the cheaper win (only 4 of them, and
`maturity-promotion-criteria-v1.md` §3.3.4 already found all 4 have real, if incidental, existing
test-code references to build the formal evidence tag from) — then report an honest, itemized
breakdown of what's genuinely evidence-complete vs. what remains, with a recommended split/
continuation plan for the rest. **A partial, honestly-reported result is the expected, successful
outcome for a task this size — not a shortfall.** Mirrors `task-T433.md`'s own successful
resolution and `task-T458.md`'s explicit precedent for large, uncertain-scope tasks.

## The self-referential ledger-defect mechanism — read this before starting, do not rediscover it

**You will not be able to flip any component to `stable` while this task's own row remains open in
`active-tasks.md`.** `maturity-promotion-criteria-v1.md` §3.5's shared defect-check flags any open
P0/P1 ledger row that mentions a component's id anywhere in its brief — and this brief necessarily
names components in its own scope. T433 discovered this the hard way, independently reproduced by
the orchestrator, and resolved it procedurally: author real evidence, report it, let the
orchestrator close this task's ledger row (archival is orchestrator-only), then a fast follow-up
flips whatever is genuinely evidence-complete. **Expect the same here — do not treat a `FAIL ...
open P0/P1 task T435 names it in its brief` result as a defect in your own work.** A clear, itemized
claim of "these N are evidence-complete" is sufficient for your own report; the orchestrator will
independently verify it the same way it verified T433's.

**A second, distinct variant of this same mechanism was found and fixed while drafting this very
brief, before dispatch — not merely theorized:** the defect-check's whole-word text match doesn't
care whether an open task is *promoting* a component or merely *mentioning* it in passing — so an
earlier draft of this brief's own "Real scope" section, which named the 2 already-`stable` skills
from T433 as context, caused both to spuriously start failing `check-maturity.py` the moment this
brief existed as an open row, even though this task doesn't touch either of them. Caught by the
orchestrator running the full test suite before dispatch (`python3 tests/run.py` genuinely went
red), fixed by removing the literal names and pointing to `phase3-wave1-promotion-v1.md` instead.
**Apply the same discipline in anything you write in your own evidence/closure artifact while this
task is open:** do not name any already-`stable` component by id in prose, even in passing/as an
example — reference it by description or point to the artifact that lists it, or you risk
regressing it the same way.

## Objective

For as many of the 28 in-scope components as you can genuinely complete: produce real evidence
(a `# maturity-evidence:` tag in a real functional test or golden `expect.py`, `## Rails` sections
with real, category-appropriate content — see §3.3.2/§3.4.2 for what "inputs/out of scope/failure
mode" mean for a passive instruction vs. a procedural skill — `docs/wiki/**` documentation,
cross-references) satisfying the real `beta→stable` criteria.

## Known shared-file collision risk — T434 is dispatched in parallel

T434 (Wave 2, remaining agents/commands) is dispatched at the same time as this task, from the same
`develop` tip, working on genuinely disjoint component categories. Two files may still collide:
`implementation/registry/{index.json,summary.md}` (both waves regenerate the full registry —
deterministic/mechanical, not a real content conflict: rebase and re-run `generate-registry.py`
before your final commit if `develop` has moved) and `docs/wiki/commands-and-skills-overview.md`
(T433 created this page; consider whether skill/instruction documentation belongs there or in a
new, separate page — your call, state it — and if T434's work has already landed with its own
additions to the same file by the time you push, rebase and merge alongside theirs, don't silently
overwrite).

## Inputs

- `docs/artifacts/maturity-promotion-criteria-v1.md` §3.3 (`instruction`), §3.4 (`skill`), §3.5
- `implementation/scripts/check-maturity.py` (T432 — the real verifier)
- `tests/functional/**`, `tests/unit/**`, `tests/performance/**`, `tests/eval/**`,
  `tests/_helpers/**` (real test code — check existing incidental references before assuming a
  skill/instruction has zero coverage to build from; §3.3.4/§3.4.4 already surveyed this once,
  re-verify it's still accurate before relying on it)
- `docs/artifacts/phase3-wave1-promotion-v1.md` (T433 — precedent for evidence shape and the
  self-referential mechanism)

## Expected outputs

1. Real evidence artifacts for each component you complete.
2. A design/closure artifact (e.g. `docs/artifacts/phase3-wave3-promotion-v1.md`) itemizing, per
   attempted component: what evidence existed vs. was newly authored, and your own assessment of
   evidence-completeness.
3. `maturity: stable` is **not** expected to be set in this MR for the reasons above.

## Acceptance criteria

1. Genuine, substantive evidence (not placeholder/padding — expect the same adversarial review that
   found T432's docs-padding gap) produced for a real, honestly-reported subset of the 28 in-scope
   components.
2. The closure artifact itemizes exactly what's complete, what's partial, and what's entirely
   untouched — no silent scope narrowing.
3. If the true remaining scope clearly needs further waves/tasks, report that explicitly as a
   `type: technical`, `severity: major` finding with a proposed split — expected, not a failure.
4. `python3 tests/run.py` passes with no regressions.
5. `node implementation/scripts/sync.mjs --root implementation --check` reports no drift.
6. Coding standards and Conventional Commits followed; branch pushed, MR opened against `develop`,
   not self-merged.

## Constraints

- **No paid or recurring-cost API calls.**
- **Do not touch `.mcp.json`, anywhere. Do not touch the main checkout
  (`/home/emage/Code/emage/emage.code`).**
- **`tests/golden/**` and `scripts/scorecard.py` are protected paths** — new golden `expect.py`
  evidence-tag additions require an explicit, disclosed exception request first, per
  `protected-paths-v1.md`. Do not touch `docs/benchmarks/tb-subset.json`/`.md`.
- **Do not touch `feature/T475-codex-platform-integration`. Do not start T434, T436, or Phase 4
  work.**
- **Confirm your own tool grant before starting** — re-check `implementation/knowledge/agents/
  tech-lead.md` directly.
- **Work in your own worktree/branch** (`agent/tech-lead/T435`), created from `develop`. Commit as
  you go; run the full test suite before reporting completion. **Do not self-merge.**

## Blocker protocol

Report blockers as: type/severity/mitigation. Max 2 retries before escalating. Specifically
anticipated: scope exceeding a reasonable single dispatch (expected, report your real subset and a
proposed continuation plan); the self-referential ledger-defect result on any flip attempt
(expected, not a defect); any criterion genuinely not satisfiable as worded for a given
skill/instruction (report, don't force).

## Execution notes

(To be filled in by the implementing agent during work, if useful — not required.)
