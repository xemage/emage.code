# Checkpoint 018 — Phase 1 Layer 1 (golden suite, T410-T415) complete

> Written by the orchestrator on resuming after two account-wide Claude usage-limit interruptions
> mid-T415. Covers T410-T415 in full (only T414/T415 postdate `checkpoint-017`) and the cross-task
> held-out-isolation audit performed ahead of T416. This is the canonical Layer 1 handoff —
> combined with `checkpoint-016-phase0-ground-truth-complete.md` and `checkpoint-017`, future
> agents need only these three checkpoints, not the full T410-T415 execution history.

## Summary

Phase 1 Layer 1 (the golden-suite evaluator, plan-035 §2.4) is fully delivered, closed, **and now
actually merged to `develop`**: `tests/golden/` (20 cases, 14 `open`/6 `held-out`),
`scripts/scorecard.py` + `docs/benchmarks/scorecard-v6.12.0.{json,md}`,
`docs/benchmarks/baseline-v6.12.0.md`, and `docs/artifacts/failure-taxonomy-v1.md` +
`docs/benchmarks/failures/*.md` all landed via MR !201 (`feature/T410-phase1-golden-suite-v6.12.0`
at commit `3fef6ee`, squash-merged to `develop`).

**A significant sequencing gap was found and closed in this session, not merely noted.** Until
this checkpoint, only the ledger/task-brief bookkeeping for T410-T415 had ever been merged to
`develop` (via the short-lived `docs/phase1-t41X-*` branches) — the actual implementation
(`tests/golden/`, `scripts/scorecard.py`, `docs/benchmarks/`) had accumulated on the feature branch
for the entire phase and had **never been merged**, nor had an MR for it ever been opened. This
was only discovered while investigating T416 (which cannot freeze paths that don't exist on
`develop`). Resolved: dry-run merge against `origin/develop` in a disposable clone (clean, 0
conflicts, purely additive — 106 files, 5717 insertions, 0 modifications to existing files),
verified full `python3 tests/run.py` + the isolation guard pass on the merged result, then opened
and merged MR !201 for real (CI green). Re-verified directly on `develop` post-merge: `python3
tests/run.py` — 367 tests, OK; `test_golden_held_out_isolation.py` — 8/8.

T415 (failure taxonomy) required a second fix pass across two separate interruptions:

1. **Narrative content leak (found and fixed, commit `3fef6ee`).** `held-out-case-1/3/4.md`'s
   "Why" sections described their real held-out fixtures' actual content (quoted command-file
   requirements, described real document structure) well beyond the categorical `cause`/
   `behavior`/`mechanism` axis-value labels the redaction scheme permits. This is distinct from
   case-*identity* leakage (already caught by T412's guard): an improvement-task agent reading
   these files could infer real fixture content without ever seeing a real case ID. Fixed by
   replacing each "Why" with a redaction notice pointing to the general axis definitions in
   `failure-taxonomy-v1.md` §3.
2. **Latent case-ID leak outside T415's own files (found and fixed, MR !199, already merged to
   `develop`).** A broader audit — requested explicitly ahead of T416's freeze, checking every
   T410-T415 file that touches held-out content, not just T415's three — found `task-T411.md` and
   `task-T412.md` (both already on `develop`) each contain bare real held-out case-ID mentions.
   Latent, not yet live (neither the isolation guard nor `tests/golden/` has merged to `develop`
   yet), but confirmed concretely to become real `test_golden_held_out_isolation.py` Check B
   failures the moment the feature branch merges — reproduced by copying each file's pre-fix
   content into the feature-branch worktree and re-running the guard. Fixed by replacing both real
   IDs with their `held-out-case-<n>` redacted labels.

Everything else checked in the same audit was clean (see "Audit detail" below).

## Completed tasks (this checkpoint)

| ID | Title | Owner | Outcome |
|----|-------|-------|---------|
| T410 | Golden suite format spec | solution-architect, orchestrator | `docs/artifacts/golden-suite-format-v1.md` |
| T411 | 20 golden cases | qa-engineer, orchestrator | `tests/golden/**` (pre-split) |
| T412 | `open`/`held-out` split + isolation guard | qa-engineer, orchestrator | `tests/golden/open/**`, `tests/golden/held-out/**`, `tests/functional/test_golden_held_out_isolation.py` |
| T413 | `scripts/scorecard.py` | devops-engineer, orchestrator | `scripts/scorecard.py`, `docs/benchmarks/scorecard-v6.12.0.{json,md}` |
| T414 | Baseline publication | release-manager, orchestrator | `docs/benchmarks/baseline-v6.12.0.md` |
| T415 | Failure taxonomy + narrative-leak fix + isolation-fix | qa-engineer, orchestrator | `docs/artifacts/failure-taxonomy-v1.md`, `docs/benchmarks/failures/*.md`; `task-T411.md`/`task-T412.md` isolation fix (MR !199) |

All six rows are `done` in `docs/tasks/completed-tasks.md`. `docs/tasks/active-tasks.md` is empty
(0 active rows) as of this checkpoint.

## Audit detail (pre-T416 cross-task narrative-leak review)

Every file identified as touching held-out content across T410-T415 was read directly (not
sampled or trusted by association):

- `docs/artifacts/failure-taxonomy-v1.md` — clean. Only categorical axis-value tables reference
  held-out cases (by redacted label); §5 documents the redaction scheme itself.
- `docs/benchmarks/scorecard-v6.12.0.json`/`.md` — clean. Held-out rows carry `command`/`status`/
  `known_failing_category`/`bucket`/`actual_result` (categorical/structural) with `id`/`case_dir`
  redacted to `held-out-case-<n>`/`<redacted>`.
- `docs/benchmarks/baseline-v6.12.0.md` — clean. Aggregate counts only; the document
  self-documents its own grep verification against all six real IDs.
- `docs/artifacts/golden-suite-format-v1.md`, `tests/golden/README.md` — clean. General format
  specs, no case-specific content.
- `tests/golden/_manifest-t411.md`, `tests/functional/test_golden_held_out_isolation.py` — clean
  by design (both are the guard's own documented, deliberate exemptions — golden suite's own
  internal bookkeeping, not improvement-task-reachable material).
- The 6 `open`-bucket failure files (`docs/benchmarks/failures/*.md`, excluding the 3 held-out
  ones) — clean; no held-out mentions, and their own narrative detail is fine since `open` cases
  are not secret.
- `docs/benchmarks/failures/held-out-case-{1,3,4}.md` — **fixed** (narrative leak, see above).
- `docs/tasks/task-T411.md`, `task-T412.md` — **fixed** (latent case-ID leak, see above; MR !199).
- `docs/tasks/task-T410.md`, `task-T413.md`, `task-T414.md`, `task-T415.md` — checked, clean (no
  held-out-ID or narrative-fixture-content mentions).

Verification method for both fixes: `tests/functional/test_golden_held_out_isolation.py` re-run
at 8/8 in the feature-branch worktree with each fix's pre-fix content simulated in (reproduced
both failures) and again post-fix (clean, 8/8); `python3 tests/run.py` fresh, exit 0; direct grep
of every touched file against all six real held-out case IDs, zero matches in every case; `git
status` clean under `tests/golden/`, `scripts/`, `docs/benchmarks/scorecard-v6.12.0.*`.

## Key decisions

- **Narrative content leakage is treated as a distinct risk from case-identity leakage**, not
  subsumed by T412's existing guard (which only pattern-matches bare case-ID tokens). No new
  automated guard was built for this in T415's closeout — the fix was manual, reviewed redaction
  of the three affected files. Whether a future automated narrative-leak check is warranted is an
  open question, not decided here (see "Open questions" below).
- **`task-T411.md`/`task-T412.md` fixed on `develop` directly (via their own branch+MR), not on
  the feature branch.** These files already live on `develop`; the feature branch does not own
  them. This is a deliberate scope split, not an oversight — confirmed the fix independently
  before merging (MR !199, CI green, re-verified post-merge).

## Artifacts produced

- `docs/artifacts/failure-taxonomy-v1.md`, `docs/benchmarks/failures/*.md` (9 files)
- `docs/tasks/task-T410.md` … `task-T415.md` (all `done`, with Completion addenda on T411/T412/T415)
- MR !199 (`docs/phase1-t411-t412-isolation-fix`, squash commit `b6f3008`, merge commit `707cb58`)
- MR !200 (`docs/phase1-t415-closeout`, squash commit `fdf7989`, merge commit `b415b3e`)
- MR !201 (`feature/T410-phase1-golden-suite-v6.12.0` → `develop`, squash commit, merge commit
  `8746eb9`) — lands the full T410-T415 implementation for real; `develop` HEAD is now `8746eb9`

## Blockers (active)

None. Both usage-limit interruptions this session recovered cleanly with no data loss (all
in-flight work was verified complete and uncommitted-but-intact on each resumption).

## Open questions (not blocking, flagged for whoever picks this up next)

1. **Is a narrative-content-leak guard (beyond T412's identity-only Check B) worth building?** Not
   decided in this checkpoint. The two fixes above were manual/reviewed, not automated. If T416's
   freeze makes `tests/golden/` read-only, a future narrative-leak check would need to live outside
   `tests/golden/` (e.g. in `tests/functional/`), same as the existing guard.
2. **How does T416 declare "protected paths" mechanically?** No existing repo mechanism enforces
   file-level write-scope per agent (checked: `implementation/scripts/sync.mjs` has no such
   concept; agent source files at `implementation/knowledge/agents/*.md` are 27 independently
   authored bodies with no shared-include mechanism). T416's brief must resolve whether this means
   (a) a documented declaration added to all 27 agent source files + a new static guard proving the
   declaration's presence/consistency (mirroring the `test_link_integrity.py`-style pattern used 3
   times already this phase), or something else. Not yet decided — first thing T416's own brief
   must scope concretely, not left to the dispatched agent to invent unguided.

## Token usage

| Phase | Budget | Spent (this session) | % |
|-------|--------|----------------------|---|
| Layer 1 closeout (T415 fix + audit + T411/T412 fix + T415 closeout) | ~35k (T415 task-level) + audit overhead | Not separately metered this session; qualitative note: audit + two fix/verify/MR cycles are the dominant cost, consistent with "held-out isolation work costs more than its nominal task-level estimate," a pattern already flagged at T412/T413/T414/T417 | — |

## Next steps

1. **T416** — freeze `tests/golden/**`/`scripts/scorecard.py` as protected/read-only for every
   agent definition. Brief not yet authored (`C7`); this is the very next task, with explicit
   extra scrutiny requested (see "Open questions" #1 above for the first design question it must
   resolve).
2. **Layer 2** — T407 (first Terminal-Bench delta measurement, `k>=3`, depends on T418/T419/T408,
   all `done`) and T409 (taxonomy extension to ingest Harbor trajectories, depends on T415 `done`
   + T407) become available once T416 closes (T409 depends on T415 directly, T407 does not depend
   on Layer 1 at all and could in principle run in parallel — not yet dispatched either way).

## Compression note

This checkpoint plus `checkpoint-016-phase0-ground-truth-complete.md` and
`checkpoint-017-t417-harbor-oracle-smoke-complete.md` together are the canonical handoff for T416
and Layer 2 planning. Subsequent agents receive **only**: these three checkpoints + their own task
brief + `plan-035-roadmap-v7-ground-up.md` — not the full T410-T415 execution history or this
session's interruption/recovery narrative.
