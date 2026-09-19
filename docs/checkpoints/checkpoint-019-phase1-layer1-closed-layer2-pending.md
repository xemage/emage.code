# Checkpoint 019 — Phase 1 Layer 1 closed (T416); Layer 2 (T407/T409) pending launch

> Written by the orchestrator immediately after T416's merge. Covers T416's dispatch/verification/
> close, and a second sequencing gap found and fixed independently this session (T418/T419/T408's
> real implementation had never been merged to `develop`, mirroring the golden-suite gap
> `checkpoint-018` already found once for T410-T415). Combined with `checkpoint-016`,
> `checkpoint-017`, and `checkpoint-018`, this is the canonical Layer 1 → Layer 2 handoff — future
> agents need only these four checkpoints, not the full T410-T419 execution history.

## Summary

**Phase 1 Layer 1 (plan-035 §2.4, T410-T416) is fully done and genuinely merged to `develop`.**
`tests/golden/**` (20 cases, 14 open / 6 held-out), `scripts/scorecard.py`,
`docs/benchmarks/baseline-v6.12.0.md`, `docs/artifacts/failure-taxonomy-v1.md` +
`docs/benchmarks/failures/*.md`, and now `docs/artifacts/protected-paths-v1.md` +
`tests/functional/test_protected_paths_declared.py` (T416's freeze, the third of three
independent controls protecting held-out-set integrity) are all on `develop`. `docs/tasks/active-
tasks.md` is empty (0 active rows).

**A second sequencing gap, same pattern as `checkpoint-018`'s golden-suite finding, found and
fixed independently this session (not reported by any dispatched agent).** T418/T419/T408 were
marked `done` in `completed-tasks.md`, but their actual implementation
(`scripts/tb-delta.sh`, `scripts/tb_delta_agent.py`, `docs/benchmarks/tb-subset.json`/`.md`,
`docs/benchmarks/tb-delta-runner.md`) had never been merged — only ledger bookkeeping had, on
short-lived `docs/phase1-t419-t408-*` branches. The real implementation sat on
`feature/T418-phase1-tb-delta-harness-v6.12.0` (commits `fb136c2`/`3ba46ca`), with no MR ever
opened. Found by checking the artifact column of T418/T419/T408's own `completed-tasks.md` rows
before assuming "done" implied "reachable from `develop`" — those rows say "not yet merged"
plainly. Fixed: dry-run merge in a disposable clone (0 conflicts, purely additive, 5 files/1239
insertions), `python3 tests/run.py` on the merged result (367 tests, OK), then MR !203 (CI green,
squash-merged, `98c8d7d`). A follow-up ledger note (MR !204, `040badb`) documents the merge without
rewriting the historical "not yet merged" narrative in the existing T418/T419/T408 rows — same
preservation-over-rewrite precedent `checkpoint-018` established for the T410 gap.

T416 itself (dispatched to `tech-lead`, confirmed full Bash access, no tool-grant mismatch) closed
cleanly with unusually thorough independent re-verification — see "T416 verification detail"
below. MR !205 (`dcad363`/`c9a9b5b`), ledger closeout MR !206 (`c63c64c`/`2845038`).

## Completed tasks (this checkpoint)

| ID | Title | Owner | Outcome |
|----|-------|-------|---------|
| T416 | Freeze golden-suite evaluator paths (protected paths, 3rd of 3 held-out controls) | tech-lead, orchestrator | `docs/artifacts/protected-paths-v1.md`; pointer in all 27 `implementation/knowledge/agents/*.md`; regenerated projections + registry; `tests/functional/test_protected_paths_declared.py` |

T418/T419/T408 were already `done` as of `checkpoint-018`'s successor state — this checkpoint's
contribution to them is exclusively the merge-gap fix (MR !203/!204), not new task work.

`docs/tasks/active-tasks.md`: 0 active rows. `docs/tasks/completed-tasks.md`: 254 rows, ledger
validator `PASS`.

## T416 verification detail (independent, not the dispatched agent's self-report)

1. **Pointer presence** — `grep -L "protected-paths-v1.md" implementation/knowledge/agents/*.md`
   returned nothing (zero missing); `git diff develop --name-only -- implementation/knowledge/agents/`
   confirmed exactly 27 files touched.
2. **Frontmatter untouched** — looped all 27 files' diffs, grepped for `^[+-](tools:|name:|description:)`
   lines; zero matches across all 27, confirming only body Constraints sections changed.
3. **`sync.mjs` clean re-run** — re-ran `node implementation/scripts/sync.mjs`; zero further diff
   (platform projections already matched source).
4. **Registry regeneration is real, not stale** — re-ran `implementation/scripts/generate-
   registry.py`; the only diff was the non-deterministic `generatedAt` timestamp (restored as
   noise, matching the established content/`run_metadata` split pattern already used by
   `scripts/scorecard.py` and `scripts/tb-delta.sh`'s own scorecards). Spot-checked
   `backend-developer`'s registry `checksum` field against an independently computed
   `sha256sum` of the live post-edit file — exact match, proving the regeneration genuinely
   reflects the new content rather than being a stale re-emit.
5. **Live-removal probe independently reproduced on a *different* file than the dispatched agent
   tested** — the agent's own report removed the pointer from `tech-lead.md`; the orchestrator
   instead removed it from `qa-engineer.md`, confirmed the guard failed and named exactly
   `qa-engineer.md`, restored the file, confirmed `sha256sum` byte-identical to the pre-probe
   original, and confirmed the guard's full 10-test suite passed again. Choosing a different file
   than the agent's own probe is the point — it rules out the failure/pass pair being an artifact
   of that one specific file rather than the guard's general logic.
6. **`tests/golden/**`/`scripts/scorecard.py` untouched** — `git diff develop --stat -- tests/golden
   scripts/scorecard.py` was empty.
7. **Full suite** — `python3 tests/run.py`: 377 tests (up from 367 pre-T416 — the new guard file's
   10 tests), `OK`, exit 0. `git status` clean throughout.

All 6 of `task-T416.md`'s acceptance criteria confirmed met on this independent evidence, not the
agent's characterization of its own work.

## Key decisions

- **T418/T419/T408's merge-gap fix is documented as a new ledger note, not a rewrite of the
  existing "not yet merged" historical entries** — same precedent `checkpoint-018` set for the
  T410-T415 golden-suite gap. Historical narrative entries describe what was true when written;
  merge-status corrections get their own dated note rather than retroactively edited prose.
- **Registry regeneration (`generate-registry.py`) was accepted as in-scope derived-state
  maintenance for T416**, not a deviation requiring a separate task, because it operates on a file
  T416's own edits already indirectly affect (per-agent content checksums) and the brief's
  acceptance criterion 3 (no further `sync.mjs`/projection diff) implicitly required all derived
  state to be current, not just the platform projections.

## Artifacts produced

- `docs/artifacts/protected-paths-v1.md`
- `implementation/knowledge/agents/*.md` (27, body-only additions)
- Regenerated platform projections (`.claude/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`,
  `.github/`, `.cline/` agent dirs) + `implementation/registry/index.json`, `summary.md`
- `tests/functional/test_protected_paths_declared.py`
- `docs/tasks/task-T416.md` (with Completion addendum)
- MR !203 (`feature/T418-phase1-tb-delta-harness-v6.12.0` → `develop`, squash commit `f549401`,
  merge commit `98c8d7d`) — lands T418/T419/T408's actual implementation
- MR !204 (`docs/phase1-t418-merge-note`, squash commit `e4ee9f4`, merge commit `040badb`) —
  ledger note documenting the above
- MR !205 (`feature/T416-protected-paths-v6.12.0`, squash commit `dcad363`, merge commit `c9a9b5b`)
  — T416 implementation
- MR !206 (`docs/phase1-t416-closeout`, squash commit `c63c64c`, merge commit `2845038`) — ledger
  closeout

`develop` HEAD is now `2845038`.

## Blockers (active)

None for Layer 1 (fully closed). Layer 2 (T407) has a **pending user decision, now resolved**: the
user explicitly authorized launching T407 now at conservative concurrency (`-n 2`) given current
host memory pressure, with the budget guard's cap raised to a realistic value (not its 1800s
default) and the full plan-035 §2.4 decision-rule text handed to the executing agent verbatim. This
checkpoint hands off to that launch, not to a further pause.

## Open questions / risks flagged, not yet resolved (carried into Layer 2)

1. **Host resource state is genuinely tight and must be re-checked immediately before T407's actual
   launch** (`free -h`/`timeout 8 docker ps`), not assumed stable from an earlier reading this
   session — conditions were sub-2Gi-available/multi-Gi-swap-used at last check, and this exact
   host has hit genuine exhaustion multiple times already this phase (T417, T419).
2. **T417's own 25-task oracle verification only reached 17/25 (68%)**, and 5 of those 8
   oracle-level failures/timeouts (`caffe-cifar-10`, `install-windows-3-11`, `crack-7z-hash`,
   `rstan-to-pystan`, `protein-assembly`) are inside the frozen `tb-subset.json`'s 25 tasks. This is
   not a blocker — it is exactly the kind of noise plan-035's decision rule (spread ≥ 8pp →
   Inconclusive, not Null) exists to catch — but it raises the real chance T407's first run returns
   Inconclusive rather than a clean Null/Positive/Negative on first attempt, especially concentrated
   on those 5 tasks. Flagged for whoever interprets T407's raw per-task results.
3. **T407's real scale**: 2 arms × k≥3 × 25 tasks = 150 real Docker trials, roughly 9-37 hours
   wall-clock depending on concurrency (T419's own smoke-test trials ran 750-1200s each), plus real
   API spend (T419's single smoke trials cost $0.26/$0.98 each — extrapolated, plausibly $40-150+
   at k=3 scale even on the economy model). User has explicitly authorized this cost/time
   commitment; the executing agent should still report actual elapsed time and cost once complete
   for the record, not just the pass/fail outcome.

## Token usage

| Phase | Budget | Spent (this session, T416 + merge-gap-fix + checkpoint) | % |
|-------|--------|----------------------|---|
| Layer 1 closeout (T416 dispatch/verify/merge, T418/419/408 merge-gap discovery/fix, checkpoint) | ~30k (T416 task-level) + merge-gap-fix overhead + checkpoint-authoring overhead | Not separately metered this session; qualitative note: the second merge-gap discovery (T418/419/408) was unplanned overhead beyond T416's own ~30k budget, consistent with this phase's recurring finding that "ledger done ≠ merged" checks cost more than their nominal task-level estimate | — |

## Next steps

1. **T407** — re-check host resources immediately before launch (see Open Questions #1); author
   `task-T407.md` (not yet on disk — required before the ledger row per `C7`); dispatch to
   `devops-engineer` at `-n 2` concurrency, budget guard cap raised to a realistic value, plan-035
   §2.4's decision-rule text (lines 424-467) handed verbatim; run in the background given the
   9-37 hour expected scale; classify the result per that exact decision rule once complete
   (orchestrator classifies independently, not the dispatched agent); publish
   `docs/benchmarks/tb-delta-v6.12.0.md`.
2. **T409** — remains correctly blocked on T407 completing (not just T407 being dispatched). Author
   and dispatch only after T407's real measurement lands.

## Compression note

This checkpoint plus `checkpoint-016-phase0-ground-truth-complete.md`,
`checkpoint-017-t417-harbor-oracle-smoke-complete.md`, and
`checkpoint-018-phase1-layer1-golden-suite-complete.md` together are the canonical handoff for
Layer 2 (T407/T409). Subsequent agents receive **only**: these four checkpoints + their own task
brief + `plan-035-roadmap-v7-ground-up.md` §2.4 (especially the decision-rule block, lines
424-467) — not the full T410-T419 execution history.
