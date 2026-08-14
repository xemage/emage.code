# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|

> No active rows: T415 closed 2026-08-14 (see "Owner corrections and closure history" below and
> `completed-tasks.md`). T416 is next — brief not yet authored, per `C7` (see "Backlog" below).

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done` · `cancelled`
> Priority values: `P0` (critical path) · `P1` (important) · `P2` (nice-to-have)
> Owners are agent names from `knowledge/agents/`.
>
> Based on: `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 1. Phase 0 (T400-T406) and
> T417 are `done` — see `docs/checkpoints/checkpoint-016-phase0-ground-truth-complete.md` and
> `checkpoint-017-t417-harbor-oracle-smoke-complete.md`. Both of Phase 1's gating open questions
> (Arm A agent = `claude-code`; null-delta interpretation) are resolved in `plan-035` §2.4 Phase 1
> and "Open questions." Dispatch of Phase 1 in full was explicitly authorized by the user on
> 2026-08-13.

## Task ID note

`plan-035`'s Layer 2 table names three tasks `T41A`/`T41B`/`T41C`. These do not match this repo's
enforced `^T\d{3,}$` task ID format (`tests/performance/test_team_health.py` /
`docs/tasks/validate-tasks.py`'s `C3` check) — caught by CI when this ledger branch was first
pushed. **Renamed for all ledger/task-brief purposes: `T41A` → `T407`, `T41B` → `T408`,
`T41C` → `T409`** (the free numeric gap in this plan's reserved `T400`-`T474` range). See
`plan-035`'s top-of-document correction note for the full explanation; `plan-035`'s own prose is
left unchanged (still says `T41A`/`T41B`/`T41C`) — this repo's task ledger is the canonical source
for the real IDs from here on.

## Backlog (not yet added as rows — no brief exists yet)

Per `docs/tasks/validate-tasks.py`'s `C7` check, a row may not be added to the table above until
its `task-<ID>.md` brief already exists (confirmed the hard way — CI correctly rejected an earlier
version of this file that added rows for briefs not yet written). Rows are added to the table
above, and briefs authored, together, just-in-time as each task unblocks — matching the real
established Phase 0 pattern, not a deviation from it. This list is for dependency-graph visibility
only; it is not machine-parsed (bullets, not `|`-table rows).

**Layer 1** (all owned by the agents named in plan-035 §2.4 Phase 1, T410 owner unchanged, T415
reassigned to `qa-engineer` — see below):
- T416 — Freeze evaluator interface (protected paths, all agent defs) — `tech-lead` — depends on T410 (done), T411 (done), T412 (done), T413 (done), T414 (done), T415 (done)

**Layer 2** (T407/T409 renamed from plan-035's `T41A`/`T41C` per the note above; T418, T419, T408
all done):
- T407 (plan-035: `T41A`) — First Terminal-Bench delta measurement (`k>=3`), publish `tb-delta-v6.12.0.md` — `devops-engineer` — depends on T418 (done), T419 (done), T408 (done)
- T409 (plan-035: `T41C`) — Extend T415 taxonomy to ingest Harbor trajectories — `devops-engineer` — depends on T415, T407

## Task-brief authoring note

Briefs for T410, T411, and T418 (tasks with no unresolved upstream design dependency, or already
unblocked) are written in full. Remaining Layer 1/2 briefs are authored just-in-time as each task
actually unblocks, because T412 onward depends on design decisions T410/T411 finalize, and T419
onward depends on T418's actual frozen subset content. Writing detailed briefs against a
not-yet-decided design would risk contradicting it — and, as of this note, is also a hard CI
requirement (`C7`), not just a style preference: a row cannot exist in the table above without its
brief already on disk.

Per-task briefs live alongside this file as `task-T410.md`, `task-T411.md`, `task-T418.md`, …

## Owner corrections and closure history

**Owner correction (2026-08-13, after T418's first dispatch attempt):** `plan-035`'s task table
lists `evaluation-agent` as owner for T415, T418, and plan-035's `T41A`/`T41C` (this ledger's
T407/T409). The dispatched T418 attempt reported a `type: technical`, `severity: critical` blocker:
this repo's actual registered `evaluation-agent` (`.claude/agents/evaluation-agent.md` and the
source `implementation/knowledge/agents/evaluation-agent.md`) grants only
`Read, WebFetch, WebSearch` — it is scoped for PoC hypothesis validation (read/research only), not
general write-capable benchmark execution. No worktree, branch, or commit existed from that
attempt; the agent correctly stopped rather than working around the gap. Reassigned rather than
widening the tool grant (a registry-wide change with a much larger blast radius than this one
task): T415 → `qa-engineer` (continuity with T411/T412, which it already owns, and full write/Bash
access); T418, T407, T409 → `devops-engineer` (matches the T417 precedent — Layer 2/Harbor work was
already executed by `devops-engineer` despite similar nominal framing — and matches T419/T408,
already on the same branch/worktree). `evaluation-agent`'s tool grant is unchanged. This
reassignment is recorded here, not in `plan-035` itself, per this repo's established convention of
recording such execution-time corrections in the task ledger/briefs (see `task-T400.md`'s addendum
for precedent) rather than editing the plan document.

**Tool-grant gap #2 (2026-08-13, T410, distinct pattern):** T410's dispatched `solution-architect`
completed all real design work but reported a `type: technical`, `severity: major` blocker at the
apply step — `solution-architect`'s registered tool grant has no Bash, so it could not create a
worktree, run `tests/run.py`, or commit. Unlike T418 this was not a missing-output blocker: the
agent staged every output file plus an apply runbook to the orchestrator's scratchpad. Per this
repo's established fallback precedent (T379/T380/T387/T392 — Bash-less delegate produces content,
Bash-capable orchestrator independently reviews then applies it), the orchestrator read and
verified every staged file, then executed the worktree/test-run/commit steps itself. T410 is now
`done` (see `completed-tasks.md`). `solution-architect`'s tool grant is unchanged. **Pattern check
for remaining Layer 1 owners** (`qa-engineer`: T411/T412/T415; `devops-engineer`:
T413/T418/T419/T407/T408/T409; `release-manager`: T414; `tech-lead`: T416) — all six confirmed to
have Bash per their `.claude/agents/*.md` definitions at the time of this note, so this specific
"no Bash" pattern is not expected to recur, but each dispatch should still independently
re-confirm rather than assume this holds if the registry changes mid-phase.

**T418 closed (2026-08-13).** `devops-engineer`'s re-dispatch completed cleanly. Independently
verified by the orchestrator (not just the agent's self-report): 6/25 subset tasks' `category`
values cross-checked against real local `task.toml` files, all matched; JSON parse + uniqueness/
category/effect-split checks; `git status` clean; `python3 tests/run.py` 355/355 in the worktree;
`docker ps -a`/`docker images` inspected, no evidence of a container run for this task. See
`completed-tasks.md` and `task-T418.md`'s Completion addendum. T419/T408 are now unblocked.

**Ledger branch reconciliation note (2026-08-13):** this file and the task briefs it references
have lived on `docs/phase1-t410-t418-dispatch`, a branch separate from the two feature branches
(`feature/T410-phase1-golden-suite-v6.12.0`, `feature/T418-phase1-tb-delta-harness-v6.12.0`) —
necessary because both feature branches would otherwise independently edit this single shared file
and diverge. This branch is being pushed and merged to `develop` now (ahead of either feature
branch's own merge) specifically so `docs/tasks/task-T418.md` and this file are readable directly
from `develop` rather than requiring `git show <branch>:<path>` from an unmerged branch, as the
dispatched T418 agent had to do to read its own brief. Future ledger updates in this phase continue
to accumulate on new short-lived docs branches merged at each natural boundary, same pattern.

**T411 closed (2026-08-13).** First dispatch was interrupted mid-task by an account-wide Claude
usage-limit stop (not a code error, not a blocker report). On resumption: 11/20 cases plus one
half-authored stub existed, uncommitted, with zero coverage for `/new-feature`/`/prepare-release`.
A second `qa-engineer` dispatch finished the stub and authored the remaining 9 cases. Independently
verified by the orchestrator (not just the agent's self-report): 20/20 case dirs with all four
required members; every `expect.py` re-run twice against its own fixture with identical, correctly-
matching-declared-status results both times and clean `git status` after each; fresh
`python3 tests/run.py` (359 tests, exit 0); and — because this is the one place a shortcut could
quietly invalidate a case — the three real-artifact-grounded fixtures' documented cosmetic
redactions were diffed against their live originals and cross-checked line-by-line against each
affected case's actual `expect.py` logic to confirm the redacted content is genuinely outside what
each check inspects. See `completed-tasks.md` and `task-T411.md`'s Completion addendum. T412
(open/held-out split), T414 (baseline publish), and T415 (taxonomy) are now unblockable — briefs to
be authored just-in-time per this file's own `C7` discipline before their rows are added.

**T419/T408 closed (2026-08-13).** First dispatch was interrupted mid-task by an account-wide
Claude usage-limit stop (not a code error, not a blocker report), leaving real but unverified
uncommitted work: a config-diff mechanism that was genuinely correct, but a smoke test that had
actually failed silently — both arms' single trial errored (`NonZeroAgentExitCodeError`, API
404) because `ECONOMY_MODEL`'s hardcoded default, `claude-3-5-haiku-20241022`, was absent from the
live Anthropic model catalog. The orchestrator found this by reading the raw pre-interruption
scorecard JSON directly rather than trusting that a "smoke test ran" meant it passed, and
independently confirmed the catalog gap via a direct `GET /v1/models` call with the host's own
key. A separate concern was also flagged: the interrupted session's doc claimed a budget-guard
abort had already been demonstrated, but no on-disk artifacts for that claimed run survived —
re-verification was required, not just trust in the transcript.

A `devops-engineer` re-dispatch fixed the model default (`claude-haiku-4-5-20251001`, the cheapest
model actually present in the catalog) and re-ran both pieces of evidence from scratch with real
Docker runs: a fresh smoke test (RUN_ID `20260813T190348Z`, both arms completed real trials, no
infra error) and a fresh budget-guard abort (RUN_ID `20260813T193832Z`, real 747s probe, real
abort at exit 2, real `budget-guard.json` on disk). The re-dispatch's own report included a
harness-level auto-neutralization flag on instruction-shaped text ("bypass-permissions",
"permissions.allow/deny") in its output; the orchestrator independently read the raw underlying
job logs directly (not just the agent's characterization) and confirmed this is Harbor/Claude
Code's own logged CLI invocation and workspace-trust-dialog text — descriptive data about the
sandboxed system under test, not directives aimed at the orchestrator — before accepting the
"benign" read.

Orchestrator independently verified (not just the agent's self-report): re-queried the live model
catalog directly, confirming the new default is present and the old one is not; decoded the raw
`tb-delta-scorecard-20260813T190348Z.json` and the Arm B trial's raw `result.json` directly,
confirming `exception_info: null` (a genuine task-level 0.0 reward, not an infra failure); decoded
the raw `config-diff.json` from both the pre-fix and a fresh post-fix `--config-only` dry run,
confirming `"clean": true` in both; decoded `budget-guard.json` for the abort run directly,
confirming `aborted: true`, no scorecard written, exactly one trial directory on disk; grepped the
raw agent transcript directly for the flagged permission strings and confirmed
`"permission_denials":[]` throughout, matching the "benign" claim; ran `python3 tests/run.py`
fresh in the worktree (355 tests, exit 0). Also removed stale on-disk debris from the pre-fix
broken run (`jobs/tb-delta-20260813T152937Z-*`, its `.runs/` dir, its scorecard JSON) via targeted
`rm` on specifically-identified paths after confirming none of it was git-tracked — the agent's
own cleanup attempt had been correctly blocked by the sandbox's destructive-operation classifier.
See `completed-tasks.md` and `task-T419.md`/`task-T408.md`'s Completion addenda.

**T412 closed (2026-08-13).** This is plan-035's single highest-severity risk item (risk table:
"Held-out set leaks into improvement work | Medium | Critical"), so it received the closest review
pass of any task closed in this phase so far. Delivered: 14/6 `open`/`held-out` split (30% held
out) spanning all 5 command surfaces, balanced 3 `expected_pass`/3 `known_failing` covering both
`known_failing_category` values; a new repo-wide static guard
(`tests/functional/test_golden_held_out_isolation.py`) mirroring the established
`test_link_integrity.py`/`test_check_version_consistency.py` pattern.

One genuine judgment call surfaced, not resolved by silent deference: the brief's literal text
("never referenced from any file outside `tests/golden/held-out/`") would, applied strictly, have
flagged pre-existing T411 sibling cross-references inside `open/*/brief.md` that criterion 1's
byte-identical requirement forbade editing. The agent narrowed the case-ID-mention check to
"outside `tests/golden/` entirely" while leaving the stronger functional-access check (Python
imports/`open()`/`Path()`) unscoped and repo-wide. The orchestrator did not accept this as
pre-settled by the brief's own ambiguity-handling default — independently reasoned through the
actual threat model (files that matter for "leaks into improvement work" live outside
`tests/golden/` entirely and are untouched by the narrowing; the manifest's own mandated
disclosure already makes case-ID tokens non-secret; the alternative would violate criterion 1) and
then proved it rather than just asserting it: planted live adversarial probe files in `scripts/`
and `docs/` in the real repo tree, confirmed the guard's `find_violations()` caught both, removed
the probes, confirmed `git status` clean. Independently verified byte-identity via raw
`git diff --raw -M100%` blob-hash comparison (stronger than trusting the agent's own SHA claim) —
all 82 case-content files identical. Re-ran all 20 cases from their new nested paths (zero status
mismatches), ran the guard's own 8-test suite directly (8/8 OK), ran `python3 tests/run.py` fresh
(367 tests, exit 0). See `completed-tasks.md` and `task-T412.md`'s Completion addendum for the
full reasoning. T413 is now unblockable.

**T413 closed (2026-08-13).** `scripts/scorecard.py` + `docs/benchmarks/scorecard-v6.12.0.{json,md}`
delivered: 20 cases, 11 pass, 0 regressions, `open`/`held-out` breakdown matching T412's split
exactly. A real design interaction with T412 surfaced during implementation, not pre-anticipated in
either brief: the output artifacts live outside `tests/golden/`, so unlike `scripts/scorecard.py`'s
own allowlisted source, they aren't exempt from the isolation guard's Check B — emitting real
held-out case IDs into them would have been exactly the leak that guard exists to prevent. Resolved
within this task's own file ownership (the guard's allowlist was correctly treated as out of
scope): `held-out/` cases report every real field except identity, replaced with a deterministic
anonymized label. This is a second, independent enforcement of held-out isolation on top of T412's
own guard.

Given this is a direct extension of Phase 1's single highest-severity risk item, the orchestrator
applied the same review rigor as T412's own closure rather than treating it as a routine follow-on:
grepped both output files directly for all six real held-out case IDs (zero matches), re-ran the
isolation guard's own 8-test suite against the real tree with the new files present (still 8/8,
including the real-tree-clean test), decoded the redacted JSON entries directly and cross-checked
each anonymized label's fields against the real `case.yaml` ground truth established during T412's
own review (all six correct, correct sorted order), independently re-ran the determinism proof
(two more fresh runs, diffed both JSON and MD myself, confirmed only `generated_at` differs,
restored the worktree afterward), and spot-checked the T419 schema-reconciliation claim against
`tb-delta.sh`'s actual shipped schema. One transient, non-reproducing test-count anomaly (355/17
vs. the expected/stable 367/18) was investigated and resolved as environmental flakiness (T413's
commit touches nothing under `tests/`; two immediate re-runs were stable). See `completed-tasks.md`
and `task-T413.md`'s Completion addendum. T414, T415 are now unblockable (T414 was the last item
waiting on T413 — all of T410-T413 are now done).

**T414 closed (2026-08-13).** `docs/benchmarks/baseline-v6.12.0.md` published — the last of
T410-T413's dependents, closing plan-035's "do not optimise before this file exists" gate.
Headline numbers (20 cases, 11 pass, 9 known_failing [6 `tracked_defect`, 3 `capability_gap`], 0
regressions) sourced from and matching T413's real scorecard exactly. The "reject a too-easy
baseline" risk-table control was performed and documented in the file itself: known_failing=9
clears T411's ≥5 floor with margin, spread across both categories and both `open`/`held-out`
subsets. This is the third independent held-out-isolation check in the T412→T413→T414 chain (T412's
guard, T413's anonymization, now T414's own document), each verified on its own merits by the
orchestrator rather than assumed correct by association with the prior two: decoded the real
scorecard JSON directly and cross-checked every published number against it, grepped the published
document for all six real held-out case IDs (zero matches), re-ran the isolation guard's own 8-test
suite with the new file present (8/8), ran `python3 tests/run.py` fresh (367 tests, exit 0), `git
status` clean. See `completed-tasks.md` and `task-T414.md`'s Completion addendum. T415 is now
unblockable (T416 remains gated on T415).

**T415 closed (2026-08-14).** Original delivery (`docs/artifacts/failure-taxonomy-v1.md`,
`docs/benchmarks/failures/*.md`) landed cleanly at commit `76ab91c`, meeting all 6 stated
acceptance criteria. The session doing final sign-off was itself interrupted twice by an
account-wide Claude usage-limit stop before closing this task, so a third resumption picked up a
requested pre-T416 cross-task review (T416 makes `tests/golden/**`/`scripts/scorecard.py`
read-only, raising the cost of anything found afterward).

That review found a real issue distinct from case-*identity* leakage (which T412's isolation guard
already catches): `held-out-case-1.md`/`-3.md`/`-4.md`'s "Why" sections narratively described the
real held-out fixtures' actual content (quoted requirements, described real document structure) —
well beyond the categorical axis-value labels the redaction scheme was designed to permit. Fixed
in commit `3fef6ee`: each "Why" replaced with a redaction notice pointing to the general axis-value
definitions in `failure-taxonomy-v1.md` §3; axis-value tables (the only non-redacted content)
unchanged.

The same review's broader mandate — checking every T410-T415 file that touches held-out content,
not just T415's own three — surfaced one further issue outside T415's file set: `task-T411.md` and
`task-T412.md` (already merged to `develop`) each contained bare real held-out case-ID mentions,
latent since neither the isolation guard nor `tests/golden/` itself had merged to `develop` yet,
but confirmed (by copying pre-fix content into the feature-branch worktree and reproducing the
guard failure) to become live violations the moment `feature/T410-phase1-golden-suite-v6.12.0`
merges. Fixed via `docs/phase1-t411-t412-isolation-fix` (MR !199, merged to `develop` ahead of and
independent of this closeout).

Orchestrator independently verified rather than trusting either fix's self-description:
`tests/functional/test_golden_held_out_isolation.py` re-run at 8/8 with both fixes' pre-fix content
simulated into the feature-branch worktree (reproduced the failures) and again post-fix (clean);
`python3 tests/run.py` fresh in the worktree, exit 0; grepped all three redacted files and both
task briefs against all six real held-out case IDs directly, zero matches in every case; `git
status` clean under `tests/golden/`, `scripts/`, `docs/benchmarks/scorecard-v6.12.0.*` (untouched,
as the brief required). See `completed-tasks.md` and `task-T415.md`'s Completion addendum for full
detail. T416 is now unblockable — brief not yet authored (`C7`).

**CI rejection and fix (2026-08-13):** the first push of this branch failed CI (`unit-tests` job,
`tests/performance/test_team_health.py::TestTaskLifecycle` + the shipped `validate-tasks.py`
validator it wraps) on three independent, genuine defects, all fixed in this revision: (1) invalid
task IDs `T41A`/`T41B`/`T41C` (see "Task ID note" above); (2) a malformed `completed-tasks.md` row
— an escaped literal pipe (`` \| ``) in T410's entry text split into an extra table cell, because
the validator's table parser does a naive `split("|")` with no backslash-escape awareness; fixed by
rewording to avoid the literal character; (3) this file had rows for tasks with no corresponding
`task-<ID>.md` brief yet (`C7` — every ledger row must have its brief on disk already, not
JIT-deferred) — fixed by moving those to the non-table backlog list above until each is actually
dispatched with a real brief.
