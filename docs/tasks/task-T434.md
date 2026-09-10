# Task T434 — Wave 2 promotion (remaining core agents/commands) to `stable`

**ID:** T434
**Owner:** tech-lead (matches `plan-035`/`plan-041`'s own assignment; tool grant checked before
dispatch — `implementation/knowledge/agents/tech-lead.md`'s registered grant is `[read, search,
edit, execute, web, mcp__fetch]`, has `execute`)
**Status:** pending
**Priority:** P1
**Depends on:** T433 (done — Wave 1; re-confirmed from `plan-041`'s own task graph that T434's only
dependency is T433, no other precondition)
**Blocks:** T436 (needs both T434 and T435's actual outcomes)
**Created:** 2026-09-10
**Completed:** —
**Based on:** `docs/plans/plan-041-phase3-maturity-ladder-detailed-planning.md` (approved, merged
MR !252) — specifically its T434 row; `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 3;
`docs/artifacts/maturity-promotion-criteria-v1.md` (T431 — real per-category `beta→stable`
criteria); `docs/artifacts/phase3-wave1-promotion-v1.md` (T433 — read this first, it documents the
real mechanics you will hit and how they were resolved; do not rediscover them from scratch);
`docs/tasks/task-T433.md`'s completion addendum.

## Real scope — computed fresh this session, not the "TBD" `plan-041` left it as

`plan-041` explicitly deferred T434's real component count to "whatever remains, TBD at T433's
closeout." That is now known: **23 agents + 17 commands = 40 components**, computed by querying
`implementation/registry/index.json` directly and subtracting the 5 agents and 2 commands T433
already produced real evidence for — see `docs/artifacts/phase3-wave1-promotion-v1.md`'s own
table for the exact list and per-component status; one of those 5 agents is already `stable`
today, the rest remain `experimental`, blocked on real, disclosed, unrelated defects per that same
artifact's §3.2 (**deliberately not naming any of the 7 by id again here, to avoid an unrelated
self-referential ledger-defect false trip on the already-`stable` one — see the next section — do
not re-derive their names by grepping the artifact and repeating them literally in your own new
prose either, for the same reason**). **Do not re-do evidence work for those 7, and do not attempt
to fix their underlying defects — that is separate, already-scoped follow-up work, not this
task's job.**

**This is ~4-5x T433's own scope** (40 vs. 9), and T433 itself needed a two-stage
evidence-then-flip resolution for a much smaller set. **Do not attempt to force full completion of
all 40 components in one dispatch.** Produce real, genuine evidence for as many as you can within a
reasonably bounded effort, prioritizing components with structurally cheaper evidence paths first
(e.g. commands that already have golden-case coverage, agents that already own a documented
command) — then report an honest, itemized breakdown of what's genuinely evidence-complete vs. what
remains, with a recommended split/continuation plan for the remainder. **A partial, honestly-
reported result is the expected, successful outcome for a task this size — not a shortfall.**
Mirrors `task-T433.md`'s own successful resolution (0/9 flipped in that MR, by design, with real
evidence for all 9 and a clean, disclosed structural finding) and `task-T458.md`'s explicit
precedent for large, uncertain-scope tasks.

## The self-referential ledger-defect mechanism — read this before starting, do not rediscover it

**You will not be able to flip any component to `stable` while this task's own row remains open in
`active-tasks.md`.** `maturity-promotion-criteria-v1.md` §3.5's shared defect-check flags any open
P0/P1 ledger row that mentions a component's id anywhere in its brief — and this brief necessarily
names every component in its own scope. T433 discovered this the hard way, independently
reproduced by the orchestrator, and resolved it procedurally: author real evidence, report it, let
the orchestrator close this task's ledger row (archival is orchestrator-only), then a fast
follow-up flips whatever is genuinely evidence-complete. **Expect the same here — do not treat a
`FAIL ... open P0/P1 task T434 names it in its brief` result as a defect in your own work.** Verify
your evidence is genuinely sufficient by temporarily checking what the result *would* be once this
task's row is gone (you can reason about this from `check-maturity.py`'s source directly, or note
which components you believe are evidence-complete for the orchestrator's own post-closure
verification) — do not need to actually simulate archival yourself if that's awkward from within
your own worktree; a clear, itemized claim of "these N are evidence-complete" is sufficient, the
orchestrator will independently verify it the same way it verified T433's.

**A second, distinct variant of this same mechanism was found and fixed while drafting this very
brief, before dispatch — not merely theorized:** the defect-check's whole-word text match doesn't
care whether an open task is *promoting* a component or merely *mentioning* it in passing — so an
earlier draft of this brief's own "Real scope" section, which named the specific already-`stable`
component from T433 as context, caused that component to spuriously start failing
`check-maturity.py` the moment this brief existed as an open row, even though this task doesn't
touch it at all. Caught by the orchestrator running the full test suite before dispatch (`python3
tests/run.py` genuinely went red), fixed by removing the literal name and pointing to
`phase3-wave1-promotion-v1.md` instead. **Apply the same discipline in anything you write in your
own evidence/closure artifact while this task is open:** do not name any already-`stable`
component by id in prose, even in passing/as an example — reference it by description or point to
the artifact that lists it, or you risk regressing it the same way.

## Objective

For as many of the 40 in-scope components as you can genuinely complete: produce real evidence
(golden cases where structurally missing and tractable, `# maturity-evidence:` tags, `## Rails`
sections with real content, `docs/wiki/**` documentation, cross-references) satisfying
`maturity-promotion-criteria-v1.md`'s real `beta→stable` criteria for each category.

## Known shared-file collision risk — T435 is dispatched in parallel

T435 (Wave 3, skills/instructions) is dispatched at the same time as this task, from the same
`develop` tip, working on genuinely disjoint component categories. Two files may still collide:
`implementation/registry/{index.json,summary.md}` (both waves regenerate the full registry — this
is a deterministic, mechanical conflict, not a real content conflict: if you find `develop` has
moved when you're ready to push, rebase and re-run `generate-registry.py` before your final
commit, don't force a stale registry through) and `docs/wiki/commands-and-skills-overview.md`
(T433 created this page for commands *and* skills — you (Wave 2/commands) may need to add entries
to it; if T435's work has already landed with its own additions by the time you push, rebase and
merge your additions alongside theirs, don't silently overwrite).

## Inputs

- `docs/artifacts/maturity-promotion-criteria-v1.md` §3.1 (`agent`), §3.2 (`command`), §3.5
- `implementation/scripts/check-maturity.py` (T432 — the real verifier)
- `tests/golden/**` (READ-ONLY reference — check existing coverage before assuming new cases needed)
- `docs/artifacts/phase3-wave1-promotion-v1.md` (T433 — precedent for evidence shape and the
  self-referential mechanism)

## Expected outputs

1. Real evidence artifacts for each component you complete (as in T433: new golden cases only via
   the disclosed exception process, `# maturity-evidence:` tags, `## Rails` sections, wiki entries).
2. A design/closure artifact (e.g. `docs/artifacts/phase3-wave2-promotion-v1.md`) itemizing, per
   attempted component: what evidence existed vs. was newly authored, and your own assessment of
   evidence-completeness (the orchestrator verifies this independently before any flip).
3. `maturity: stable` is **not** expected to be set in this MR for reasons explained above — if you
   determine a specific component's evidence is so clearly complete that you want to flip it anyway
   to prove the point, that's fine, but expect it to still show `FAIL` in `check-maturity.py` while
   this task remains open, and don't treat that as your own defect.

## Acceptance criteria

1. Genuine, substantive evidence (not placeholder/padding — expect the same adversarial review that
   found T432's docs-padding gap and reviewed T433's evidence directly) produced for a real,
   honestly-reported subset of the 40 in-scope components.
2. The closure artifact itemizes exactly what's complete, what's partial, and what's entirely
   untouched — no silent scope narrowing.
3. If the true remaining scope (after your own real subset) clearly needs further waves/tasks,
   report that explicitly as a `type: technical`, `severity: major` finding with a proposed split —
   expected, not a failure, per the "Real scope" section above.
4. `python3 tests/run.py` passes with no regressions.
5. `node implementation/scripts/sync.mjs --root implementation --check` reports no drift.
6. Coding standards and Conventional Commits followed; branch pushed, MR opened against `develop`,
   not self-merged.

## Constraints

- **No paid or recurring-cost API calls.**
- **Do not touch `.mcp.json`, anywhere. Do not touch the main checkout
  (`/home/emage/Code/emage/emage.code`).**
- **`tests/golden/**` and `scripts/scorecard.py` are protected paths** — new golden cases require
  an explicit, disclosed exception request first, per `protected-paths-v1.md`. Do not touch
  `docs/benchmarks/tb-subset.json`/`.md`.
- **Do not touch `feature/T475-codex-platform-integration`. Do not start T435, T436, or Phase 4
  work.**
- **Confirm your own tool grant before starting** — re-check `implementation/knowledge/agents/
  tech-lead.md` directly.
- **Work in your own worktree/branch** (`agent/tech-lead/T434`), created from `develop`. Commit as
  you go; run the full test suite before reporting completion. **Do not self-merge.**

## Blocker protocol

Report blockers as: type/severity/mitigation. Max 2 retries before escalating. Specifically
anticipated: scope exceeding a reasonable single dispatch (expected, report your real subset and a
proposed continuation plan, not a failure); the self-referential ledger-defect result on any
flip attempt (expected, not a defect — see above); any component whose criteria genuinely can't be
satisfied as worded (report, don't force).

## Execution notes

(To be filled in by the implementing agent during work, if useful — not required.)
