# Task T418 — Freeze the Terminal-Bench stratified iteration subset

**ID:** T418
**Owner:** devops-engineer (reassigned 2026-08-13 — see addendum below; `plan-035`'s table names
`evaluation-agent`)
**Status:** done
**Priority:** P0
**Depends on:** — (T417 done; uses Harbor's already-installed local task cache, not a fresh
Docker/network fetch)
**Created:** 2026-08-13
**Completed:** 2026-08-13
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` (Phase 1, §2.4, Layer 2 table, row
T418)

This brief is self-contained. Read `docs/checkpoints/checkpoint-017-t417-harbor-oracle-smoke-complete.md`
first — it documents the exact Harbor/Docker environment already verified working in this repo's
context, including the venv install path and the two prior oracle runs (5/5 and 17/25).

## Scope boundary — read this first
This task **defines and freezes a task-name subset**. It does not run any agent-under-test, and it
does not need to invoke Docker at all — the full `terminal-bench` task package list is already
cached locally on this host from T417's prior run at
`~/.cache/harbor/tasks/packages/terminal-bench/` (confirmed present, one directory per task, at
brief-authoring time). Read task metadata from that cache (or via whatever `harbor` CLI listing
command exists, if you reinstall/reuse a venv per T417's brief) rather than re-running containers.
If you find the cache stale or insufficient, that is a `type: technical`, `severity: minor` note,
not a reason to run a full Docker oracle pass again.

## Objective
Choose and freeze ~25 of the (per plan-035 §2.2.1) 89 Terminal-Bench 2 tasks, stratified to span
task families/categories, pinned by exact task name in `docs/benchmarks/tb-subset.json`. **This
subset is frozen once committed** — changing it later invalidates every delta measurement that
follows (T41A and all future releases' comparisons). Get the stratification right the first time;
do not treat this as provisional.

## What "stratified" means here
Terminal-Bench task names in the cache span visibly different families (systems/build tasks like
`compile-compcert`, `build-pov-ray`; crypto/security tasks like `feal-linear-cryptanalysis`,
`crack-7z-hash`, `vulnerable-secret`, `git-leak-recovery`, `openssl-selfsigned-cert`; ML/data tasks
like `caffe-cifar-10`, `torch-tensor-parallelism`, `dna-assembly`, `dna-insert`,
`protein-assembly`; infra/networking like `kv-store-grpc`, `pypi-server`, `db-wal-recovery`;
language/interpreter tasks like `make-mips-interpreter`, `schemelike-metacircular-eval`,
`circuit-fibsqrt`; and more). Enumerate the actual full set from the cache (or Harbor's dataset
listing) rather than relying on this brief's partial illustrative list, group by a reasonable
category scheme of your own design, and sample ~25 across groups so no single family dominates the
subset. Document your category scheme and the sampling rationale in the output file's own
preamble/comments, not just in your completion report — future readers of `tb-subset.json` need to
understand *why* a task is or isn't in it without re-deriving your reasoning.

## Predicted-effect tagging (required by the registered interpretation block)
`docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 1's registered interpretation block
(frozen, read it in full before starting) requires: "The tasks in `tb-subset.json` predicted to
move are tagged `predicted_effect: positive` in that file at T418 time." For each task in your
subset, add a `predicted_effect` field: `positive` if you judge the task requires multi-step
planning before execution (the projection's predicted strength, per the registered prediction), or
`neutral` if it is closer to a single-command/lookup task. This is a real judgment call you must
make now, before T41A runs — do not defer it, and do not consult T41A's actual results when making
it (they don't exist yet, but this note exists so a future re-reader knows the tagging is
pre-registered, not fitted after the fact).

## Inputs
- `~/.cache/harbor/tasks/packages/terminal-bench/` — local cache of Terminal-Bench 2 task packages
  (confirmed present; each subdirectory name is a task name)
- `docs/benchmarks/environment.md` — T417's environment record, including the two prior oracle
  runs' task-level results (useful context: `caffe-cifar-10`, `crack-7z-hash`,
  `install-windows-3-11`, `rstan-to-pystan` had non-pass or timeout outcomes in the 25-task
  extended run — you are not required to exclude or include these based on that alone, but note
  if you do either)
- `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.2.1 and §2.4 Phase 1 (registered interpretation
  block) in full

## Expected outputs
- `docs/benchmarks/tb-subset.json` — machine-readable, one entry per task:
  `{"name": "...", "category": "...", "predicted_effect": "positive"|"neutral"}` (add a top-level
  `frozen_at` date and a `rationale` field or sibling doc — your call on exact shape, but keep it
  simple enough for T419's runner to consume with `jq`/`json.load` directly, no custom parser).
- A short prose rationale either as a header comment block in the JSON (if you keep it to a `#`-less
  JSON file, put rationale in a sibling `docs/benchmarks/tb-subset.md` instead, since JSON has no
  comments) covering: category scheme used, how many tasks per category, why ~25 (not more/fewer),
  and the `predicted_effect` tagging rationale.

## Acceptance criteria
1. `docs/benchmarks/tb-subset.json` exists, contains ~25 (23-27 acceptable) task names verified to
   actually exist in the Terminal-Bench 2 dataset (not typos/guesses).
2. Every entry has `predicted_effect` set to either `positive` or `neutral`.
3. The subset spans at least 4 distinct task-family categories (not e.g. all crypto tasks).
4. Rationale document explains the category scheme and sampling logic well enough that a future
   reader can audit whether the stratification was reasonable.
5. `python3 -c "import json; json.load(open('docs/benchmarks/tb-subset.json'))"` parses cleanly.
6. No Docker container was run to produce this file (verify in your completion report — this task
   should be cheap and fast).

## Blocker protocol
- If the local Harbor task cache is missing or incomplete and you cannot enumerate the real 89-task
  list without running Docker -> `type: technical`, `severity: minor` — report before falling back
  to a Docker-based listing command, since that changes this task's resource profile.
- If you cannot form a defensible stratification (e.g. task names give no reliable signal about
  family) -> `type: unclear_requirements`, `severity: minor`.

## Git workflow
1. Create worktree + branch: `git worktree add ../worktrees/phase1-tb-delta -b
   feature/T418-phase1-tb-delta-harness-v6.12.0 develop`. This branch will accumulate T418, T419,
   T41B, T41A, and T41C's commits (mirrors the Phase 0 stacking pattern) — do not open an MR yet.
2. Commit with a Conventional Commit message (`feat(benchmarks): freeze Terminal-Bench iteration
   subset... Refs T418`).
3. Do not push. Report the worktree path, branch name, and commit SHA back to the orchestrator.

## Constraints
- Token budget: ~15k tokens.
- File ownership: `docs/benchmarks/tb-subset.json`, `docs/benchmarks/tb-subset.md`. Do not modify
  `docs/benchmarks/environment.md` (T417's, already merged) or run any Docker command.

## Addendum (orchestrator, 2026-08-13, reassignment)
First dispatch (to `evaluation-agent`, per `plan-035`'s literal task table) failed cleanly with a
`type: technical`, `severity: critical` blocker: this repo's actual registered `evaluation-agent`
(`.claude/agents/evaluation-agent.md`, and the source `implementation/knowledge/agents/
evaluation-agent.md`) grants only `Read, WebFetch, WebSearch` — no Bash, no Write/Edit, no git. It
is scoped for PoC hypothesis validation, not general benchmark-execution work requiring a worktree,
file writes, and commits. No worktree, branch, or commit was created by that attempt; the agent
stopped rather than working around the gap or fabricating output, correctly. Reassigned to
`devops-engineer` rather than widening `evaluation-agent`'s tool grant (that would be a
registry-wide change affecting every future task assigned that role, out of proportion to fixing
one task's ownership mismatch). This matches T417's precedent (Layer 2/Harbor work executed by
`devops-engineer` despite similar nominal plan framing) and keeps this task on the same
branch/worktree as T419/T41B, which were already assigned to `devops-engineer`. See
`docs/tasks/active-tasks.md`'s "Owner correction" note for the full record, which also reassigns
T415 (→ `qa-engineer`) and T41A/T41C (→ `devops-engineer`) preemptively to avoid hitting the same
blocker three more times. Everything else in this brief (objective, scope boundary, inputs,
expected outputs, acceptance criteria, git workflow, token budget) is unchanged and still applies
to the new owner.

## Completion (orchestrator, 2026-08-13)
**ID-rename note:** this brief's text above (Objective, Git workflow, Addendum) still says
`T41A`/`T41B`/`T41C`, as originally written. Those are invalid per this repo's enforced task ID
format and have been renamed in the actual ledger to `T407`/`T408`/`T409` respectively — see
`docs/tasks/active-tasks.md`'s "Task ID note" for the full explanation. Not rewritten above,
consistent with this brief being a record of what was asked/done at the time.

`devops-engineer`'s re-dispatch completed cleanly, no blocker. Worktree
`/home/emage/Code/emage/worktrees/phase1-tb-delta`, branch
`feature/T418-phase1-tb-delta-harness-v6.12.0`, commit `fb136c2`. Delivered
`docs/benchmarks/tb-subset.json` (25 tasks, `{name, category, predicted_effect}`, freeze metadata)
and `docs/benchmarks/tb-subset.md` (rationale). Category scheme uses Terminal-Bench's own
`task.toml` `[metadata].category` field, not an invented taxonomy; 16 tasks tagged
`predicted_effect: positive`, 9 `neutral`, pre-registered per plan-035's registered interpretation
block before any T41A measurement exists.

**Self-resolved finding, not escalated:** the local Harbor cache from T417 only held 30/89 task
directories (union of T417's two oracle runs), not the full dataset the brief anticipated. Resolved
via the brief's own pre-sanctioned fallback: `harbor dataset download terminal-bench/
terminal-bench-2 --export` (git sparse-checkout of task-definition files only — `task.toml`,
`README.md`, `instruction.md`, `environment/`, `tests/`, `solution/` — no Docker image pull, no
container run) to get an authoritative 89-name list with real `category` values. Correctly
classified `type: technical`, `severity: minor` and resolved without escalation, per the brief's
own Blocker Protocol.

**Orchestrator independent verification (not merely trusting the self-report):** cross-checked 6 of
the 25 subset tasks' `category` values directly against the real local `task.toml` files still
cached from T417 (`crack-7z-hash`, `dna-assembly`, `db-wal-recovery`, `caffe-cifar-10`,
`make-mips-interpreter`, `kv-store-grpc`) — all 6 matched exactly. Confirmed
`docs/benchmarks/tb-subset.json` parses cleanly via `python3 -c "import json; json.load(...)"`
(25 unique names, 16 categories, 16 positive / 9 neutral). Ran `git status` (clean) and
`python3 tests/run.py` (355/355, exit 0, no regressions) in the worktree. Confirmed `docker ps -a`
empty and no docker images dated to this task's execution window. All 6 of T418's acceptance
criteria independently verified met.

Not pushed, no MR — left for the orchestrator's Layer 2 gate/merge, alongside T419/T41B/T41A/T41C
on the same stacked branch.
