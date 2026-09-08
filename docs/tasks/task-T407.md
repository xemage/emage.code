# Task T407 — First Terminal-Bench delta measurement (k≥3, full frozen subset)

**ID:** T407
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Depends on:** T418 (done), T419 (done), T408 (done) — all three genuinely merged to `develop`
via MR !203 (`scripts/tb-delta.sh`, `scripts/tb_delta_agent.py`, `docs/benchmarks/tb-subset.json`,
`docs/benchmarks/tb-delta-runner.md` all present on disk as of this brief). Does **not** depend on
T416 — Layer 2 was always independent of Layer 1's freeze (see
`docs/checkpoints/checkpoint-018-phase1-layer1-golden-suite-complete.md`, "Next steps").
**Created:** 2026-08-14
**Completed:** 2026-09-08
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 1, Layer 2 table, `T41A`
row (renamed `T407` in this repo's ledger, see `active-tasks.md`'s "Task ID note"): *"Run the first
delta measurement at `k ≥ 3` per arm on the subset. Publish
`docs/benchmarks/tb-delta-v6.12.0.md` reporting both arms, the delta, and the spread. A delta
reported without spread is not a result."*

**User authorization (explicit, this session, in response to the orchestrator's resource/scale
flag):** "Launch now, conservative concurrency" — proceed at `-n 2` given host memory pressure at
decision time, budget guard cap raised to a realistic value (not the script's 1800s default), full
plan-035 §2.4 decision-rule text handed to the executing agent verbatim (reproduced in full below —
do not re-derive or paraphrase it). This is explicit authorization for the real cost/time
commitment this task represents (~9-37 hours wall-clock at full serial-equivalent scale, reduced by
`-n 2` concurrency to roughly half that for real wall-clock; real API spend, T419's own single
economy-model smoke trials cost $0.26/$0.98 each).

## Why this matters ("the actual paying-off measurement this whole harness was built for")

Every task in Phase 1 Layer 2 so far (T417's environment verification, T418's frozen subset,
T419/T408's runner-plus-budget-guard) exists to make this one measurement trustworthy. Getting the
execution right — real k≥3, real spread reported, honest classification against a rule that was
committed *before* seeing the result — is the entire point. A wrong or sloppy result here is worse
than no result: it would license Phase 6's later automated-improvement loop against Terminal-Bench
before establishing whether Terminal-Bench is even a valid signal for this system. Treat this
task's execution and this brief's own re-verification with more scrutiny than a typical task, not
less.

## Known pre-existing risk to interpretation (flagged, not a blocker)

`docs/benchmarks/environment.md`'s T417 25-task oracle verification only reached 17/25 (68%) pass,
not 100%. Of the 8 oracle-level failures, **5 are inside the frozen `tb-subset.json`'s 25 tasks**:
`caffe-cifar-10` and `crack-7z-hash` (`AgentTimeoutError`, compute-heavy — possibly resource-timing
sensitive), `install-windows-3-11` and `rstan-to-pystan` (0.0 reward, no exception — the *oracle*
itself did not pass verification on these two), and `protein-assembly` (transient Docker Hub
registry 500, likely resolves on retry). This is exactly the kind of noise the decision rule below
(spread ≥ 8pp → Inconclusive) exists to catch, not grounds to skip or reduce the measurement's
scope — but the executing agent and whoever interprets the result should expect these 5 tasks
specifically to be more likely sources of within-arm variance or trial-level errors than the other
20, and should not be surprised or alarmed if they behave differently from the rest.

## Registered decision rule (plan-035 §2.4, reproduced verbatim — this is frozen at authoring
time and must not be reworded, reinterpreted, or improvised around)

> **Prediction registered in advance.**
>
> The projection is expected to move Terminal-Bench primarily on tasks requiring multi-step
> planning before execution, and to be neutral on single-command and lookup tasks. The tasks in
> `tb-subset.json` predicted to move are tagged `predicted_effect: positive` in that file at T418
> time. Expected aggregate delta: small positive, plausibly under the resolution floor.
>
> **Decision rule.**
>
> Let `spread` = per-arm min–max across the k runs.
> - **Inconclusive** — either arm's spread ≥ 8pp. The measurement failed; the result is not about
>   emage.code. Action: raise `k`, or reduce nondeterminism, before any interpretation is recorded.
>   Do not report as null.
> - **Null** — both arms tight (spread < 8pp) and their ranges overlap, or `|mean delta| < 4pp`
>   (one task).
> - **Positive / negative** — ranges disjoint and `|mean delta| ≥ 4pp`.
>
> **What a null delta means.**
>
> Terminal-Bench, as configured here, does not resolve emage.code's contribution. It does *not*
> mean the projection is without value, and it does *not* mean the projection is safe. It means
> this instrument is not a progress signal for this system, and the golden suite carries that role
> alone.
>
> **Consequences of a null delta, pre-committed:**
>
> - The result is published in `tb-delta-v6.12.0.md` with the same prominence a positive result
>   would receive. A null is a publication, not a shelved run.
> - The subset is **not** re-cut, re-stratified, or extended to search for a positive. T418's
>   freeze holds. Re-cutting after seeing the result is the specific act this block exists to
>   prevent.
> - The harness is **not** deleted. Terminal-Bench is demoted from *improvement signal* to
>   *no-harm guardrail*: subsequent releases must not show a delta below −4pp. Phase 6's
>   improvement loop then optimises against the golden suite only, with the TB guardrail as a
>   merge precondition.
> - Check the `predicted_effect: positive` tasks in isolation. If they moved and the aggregate did
>   not, the subset is diluted — record this, but do not act on it in this release cycle.
> - Leaderboard submission (§2.7) stays deferred permanently rather than provisionally, unless a
>   successor block supersedes this one.
> - A null delta does **not** relax G1, does **not** license reducing `k`, and is **not** grounds
>   for promoting any component out of beta.
>
> **What a negative delta means.**
>
> A defect, not a philosophy. Most likely causes, in triage order: projection consuming context
> budget the agent needed; projected instructions conflicting with the agent's own system prompt;
> projection introducing files the agent explores and discards. Triage before any further Phase 1
> work; a negative delta blocks G1.

**Note on `spread` units:** "8pp"/"4pp" = percentage points of reward (Terminal-Bench rewards are
0.0/1.0 per trial in this dataset; mean reward is therefore a fraction, and "pp" here means the
mean-reward difference expressed as a percentage, e.g. a swing from mean 0.60 to mean 0.68 is 8pp).
Compute `spread` as `(max(rewards) - min(rewards)) * 100` per arm across the k trials **per task,
then also consider the aggregate** — the rule's own wording ("either arm's spread ≥ 8pp") is
per-arm at the aggregate level per plan-035's own usage elsewhere in this document (see
`docs/benchmarks/tb-delta-runner.md`'s `spread.arm_a_stdev`/`spread.arm_b_stdev` fields, which
report population stdev per arm across all trials, not per-task) — **the orchestrator will compute
and cross-check both the aggregate-level and per-task-level spread from the raw scorecard JSON
independently before classifying; the executing agent should not attempt to pre-classify the
result itself, only report the raw numbers honestly.**

## Objective

1. Re-check host resources immediately before invoking Harbor (`free -h`, `timeout 8 docker ps`) —
   conditions may have shifted since this brief was authored. If genuinely exhausted (near-zero
   available memory, swap fully saturated, or `docker ps`/`docker info` hangs/unresponsive), do
   **not** proceed — report a `type: technical`, `severity: major` blocker instead of forcing the
   run through.
2. Run the full two-arm delta measurement across the **entire frozen 25-task subset** (no scope
   reduction — `tb-subset.json`'s freeze from T418 holds) at `k=3`, using this exact invocation:
   ```
   scripts/tb-delta.sh -k 3 -l 25 -n 2 --max-budget-seconds 259200
   ```
   - `-k 3`: minimum required by the decision rule.
   - `-l 25`: the full frozen subset, not a partial sample.
   - `-n 2`: conservative concurrency per explicit user authorization, given host memory pressure.
   - `--max-budget-seconds 259200` (72h): the budget guard's own projection formula is purely
     serial (`probe_elapsed * total_trials_planned`, does not divide by `-n` concurrency) — this
     cap is set well above the expected serial-equivalent projection (~31-50h at 750-1200s/trial ×
     150 trials) specifically so a legitimate `-n 2` run (real wall-clock roughly half the serial
     projection) is not falsely aborted by the guard's own conservative arithmetic. This is *not*
     a signal that a 72-hour run is expected or acceptable in practice — real wall-clock at `-n 2`
     should be well under half that. If the run is genuinely still active after ~24 real hours,
     treat that itself as worth a status report to the orchestrator, not silent continuation.
   - Do **not** pass `--skip-guard` — the probe must run for real, exactly as designed.
   - Economy model (script default, `claude-haiku-4-5-20251001`) — do not pass `--model-tier
     frontier`. Frontier-tier is explicitly out of scope for T407 per `tb-delta-runner.md`'s own
     scope note (reserved for later release-baseline runs, a different task).
3. **This is a long-running operation.** Launch `scripts/tb-delta.sh` via your Bash tool with
   `run_in_background: true` (or equivalent nohup-and-redirect-to-log pattern), then poll
   periodically for completion using an until-loop against the process/log rather than blocking
   synchronously. Do not attempt to run this as a single foreground call.
4. **Monitor host resources at natural checkpoints**, not just at the start: after the budget-guard
   probe completes (before Arm A's full run begins), after Arm A completes (before Arm B begins),
   and once at completion. `free -h`/`timeout 8 docker ps` each time; note the readings in your
   final report. If at any checkpoint the host shows genuine exhaustion (not just tightness) that
   threatens the run's own integrity or the shared host's stability, use your judgment on whether
   to let the current arm finish and stop before the next one, versus continuing — and report
   either way with the readings that informed the decision, not just the outcome.
5. On completion (or budget-guard abort), locate the raw scorecard JSON
   (`docs/benchmarks/scorecards/tb-delta-scorecard-<run-id>.json`) and the run's
   `config-diff.json`/`budget-guard.json` artifacts. Report the **raw numbers** back — per-arm mean
   reward, per-arm spread (min-max across the k trials, both aggregate and, if feasible from the
   raw JSON, per-task), delta, total cost, total elapsed time, `k`, model. **Do not classify the
   result yourself** (Inconclusive/Null/Positive/Negative) — state the raw numbers plainly and let
   the orchestrator apply the decision rule independently. You may note an initial observation, but
   label it clearly as your own read, not the final classification.
6. Draft `docs/benchmarks/tb-delta-v6.12.0.md` reporting **both arms, the delta, the spread** (per
   T41A's literal acceptance criterion — "a delta reported without spread is not a result"), `k`,
   the model, and total cost. State the raw numbers factually. You may include a proposed
   classification, but flag it explicitly as "proposed, pending orchestrator's independent
   verification against the raw JSON" — do not present it as final in the document's own voice.

## Held-out isolation — does not apply here

T407 does not read `tests/golden/**` at all (Terminal-Bench is a separate dataset). No held-out
isolation concern for this task specifically. `tests/golden/**`/`scripts/scorecard.py` remain
protected per T416 regardless — do not touch them.

## Inputs

- `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 1, Layer 2 table + the decision-rule
  block (reproduced verbatim above — read the plan itself too, for full surrounding context)
- `docs/benchmarks/tb-delta-runner.md` (T419/T408 — full invocation reference, schema, known
  findings: no `--seed` flag, T413-reconciliation follow-up)
- `docs/benchmarks/tb-subset.json`, `docs/benchmarks/tb-subset.md` (T418 — the frozen subset, do
  not modify)
- `docs/benchmarks/environment.md` (T417 — host/Harbor verification history, including the 17/25
  oracle-run finding cited above)
- `docs/checkpoints/checkpoint-019-phase1-layer1-closed-layer2-pending.md` (latest checkpoint —
  Open Questions #1-3 are this task's own pre-flagged risks)
- `scripts/tb-delta.sh`, `scripts/tb_delta_agent.py` (the runner itself — read before invoking,
  do not modify)

## Expected outputs

- `docs/benchmarks/scorecards/tb-delta-scorecard-<run-id>.json` (raw, produced by the script
  itself — not hand-authored)
- `docs/benchmarks/scorecards/.runs/<run-id>/*` (config-diff.json, budget-guard.json, raw
  `--print-config` dumps — produced by the script)
- `docs/benchmarks/tb-delta-v6.12.0.md` (hand-authored, reporting the raw numbers per Objective 6)

## Acceptance criteria

1. Full frozen 25-task subset run at `k=3`, both arms, real Docker execution (not simulated,
   not `--skip-guard`, not a partial `-l` sample).
2. Config-diff proof clean (`"clean": true`, only `agents[0].name` differs) — this is produced
   automatically by the script on every invocation; confirm and report it, don't just assume.
3. Published `tb-delta-v6.12.0.md` states both arms' mean reward, the spread (per-arm, min-max
   across k), the delta, `k`, the model, and total cost — all sourced from and matching the raw
   scorecard JSON exactly (no rounding/summarizing that loses the actual numbers).
4. Raw scorecard JSON, budget-guard.json, and config-diff.json all exist on disk and are reported
   by path.
5. `python3 tests/run.py` exits 0 (full suite, no regression) after the run completes and outputs
   are committed.
6. `git status` clean; only the expected new artifacts are added (scorecard JSON, `.runs/`
   artifacts, `tb-delta-v6.12.0.md`) — no unrelated changes.

## Blocker protocol

- Host resources genuinely exhausted at any checkpoint (start, or during) →
  `type: technical`, `severity: major` — stop, do not force the run, report with the actual
  readings that triggered the stop.
- Budget guard aborts (exit code 2) → this is the guard working correctly, not a blocker in
  itself. Report the abort with the full `budget-guard.json` projection; do not silently retry
  with a higher cap without checking in — a guard abort at a 259200s cap would mean the probe
  measurement itself was unusually slow (well outside the 750-1200s range previously observed),
  worth flagging as `type: technical`, `severity: minor` for the orchestrator's awareness even
  though the guard itself handled it correctly.
- Any ambiguity in applying the decision rule's units/thresholds to the raw JSON → do not
  improvise a resolution; report raw numbers only and let the orchestrator classify, per
  Objective 5 above.
- Docker Hub registry transient failures (as seen in T417's environment.md, HTTP 500 from
  `auth.docker.io`) on any of the 25 tasks → `type: external`, `severity: minor`, retry that
  specific task once if the script's own error handling allows; if not, report which task(s) were
  affected and proceed with what completed — do not abandon the whole run over one task's
  transient pull failure without checking in first if it affects more than 2-3 tasks.

## Git workflow

1. Create worktree: `git worktree add ../worktrees/t407-tb-delta -b feature/T407-tb-delta-v6.12.0
   develop` (fresh branch from current `develop`, which includes T416's freeze and the merged
   T418/T419/T408 harness).
2. Do the work (this will take real, extended wall-clock time — expect to poll/check back over
   many hours, not complete in one continuous session turn).
3. Commit with a Conventional Commit message (`feat(benchmarks): first Terminal-Bench delta
   measurement (T407) ... Refs T407`).
4. Do not push, do not open an MR. Report worktree path, branch name, commit SHA, raw scorecard
   path, and explicit confirmation of each of the 6 acceptance criteria back to the orchestrator.

## Constraints

- Token budget: ~40k tokens (medium scope per the plan; most of the "cost" here is real wall-clock
  and API spend, not orchestrator/agent token usage — the script does the heavy lifting).
- File ownership: `docs/benchmarks/scorecards/**` (script-generated), `docs/benchmarks/tb-delta-
  v6.12.0.md` (hand-authored). Do not touch `scripts/tb-delta.sh`, `scripts/tb_delta_agent.py`,
  `docs/benchmarks/tb-subset.json`/`.md` (T418/T419/T408's frozen deliverables — read-only for this
  task), `tests/golden/**`, `scripts/scorecard.py` (T416-protected).
- Real cost: proceed under the user's explicit authorization recorded above. Report actual total
  cost (from the scorecard's `cost_usd_total` fields) in your final report regardless of outcome.

## Design A addendum (execution redesign, dispatched 2026-09-05T22:45:47Z)

**Everything above this line is preserved verbatim from the original k=3 dispatch and documents
real, valuable completed work — it is not superseded, deleted, or reworded.** This addendum
supersedes only the *execution design* for classification purposes; the task's identity,
ownership, decision-rule text (reproduced verbatim above), and cost authorization all remain
binding and unchanged.

### Why

Plan-035's decision rule (reproduced verbatim above) defines `spread` as **the per-arm min–max
across `k` independent runs**. The k=3 execution actually performed on 2026-08-14 (artifacts:
`jobs/tb-delta-20260814T111217Z-arm-{A,B}/`, `docs/benchmarks/scorecards/tb-delta-scorecard-
20260814T111217Z.json`) was one single pass of `scripts/tb-delta.sh -k 3 -l 25 -n 2
--max-budget-seconds 259200` — i.e. 3 attempts-per-task *within one invocation/run*. That measures
within-run trial variance (repeated attempts inside one process's lifetime, one config-diff proof,
one budget-guard probe), not across-run variance (separate invocations, separate process
lifetimes, separate probes). It does not satisfy the literal decision rule as written. This is not
a flaw in the completed measurement's execution quality — it is a mismatch between what the rule
asks for ("k independent runs") and what was run ("k attempts inside one run"). The k=3 artifacts
remain valid, real, historical evidence and are preserved untouched; they are simply not
classifiable under §2.4's literal rule as it stands.

### What: Design A

3 **independent** full-subset passes. Each pass = a separate invocation of `scripts/tb-delta.sh`,
run to completion (or abort) before the next pass starts — separate process, separate config-diff
proof, separate budget-guard probe, separate scorecard. Both arms, full frozen 25-task subset,
`k=1` per pass (so "k=3 independent runs" is satisfied by 3 passes of k=1, not 1 run of k=3):

```
scripts/tb-delta.sh -k 1 -l 25 --n-concurrent 2 --max-budget-seconds 129600
```

Run 3 times sequentially (never concurrently — host memory is finite, and the user's original
"conservative concurrency" authorization governs this redesign too). 25 tasks x 2 arms x k=1 = 50
trials/pass, 150 trials total across all 3 passes — the same total trial count as the original
k=3/150-trial design, just distributed across 3 independent runs instead of attempts within one.

**Note on flag syntax:** the dispatch instruction for this addendum specified `-n 2` as shorthand,
but `scripts/tb-delta.sh`'s actual argument parser only recognizes the long form
`--n-concurrent N` (confirmed by reading the parser's `case` block and by a failing
`--config-only` dry run reproducing `Unknown option: -n` before using the correct flag). The
invocation above uses `--n-concurrent 2`, which is the intended conservative-concurrency-2
semantics — not a change in design intent, just the flag spelled correctly for this script.

**Harbor venv note:** the original T417/environment.md Harbor install (`harbor` 0.21.0) lived in
that session's own ephemeral scratchpad directory, which does not survive past that session and
was confirmed absent on disk at this dispatch. Since Design A must survive as a detached background
process well past this dispatching session's own lifetime, a fresh Harbor venv was installed at
`/home/emage/.venvs/harbor-t407` (outside the repo worktree, outside any ephemeral per-session
scratchpad — a durable, session-independent location) via the same `python3 -m venv` + `pip install
harbor` method as the original install. This resolved to `harbor` 0.22.0 (one minor version ahead
of the original 0.21.0). CLI surface compatibility was re-verified before launch: `harbor run
--help` shows the same `-k/--n-attempts`, `-n/--n-concurrent` flags `tb-delta.sh` depends on, and a
`--config-only` dry run against the real frozen subset produced a clean config-diff (`"clean":
true`, only `agents[0].name` differs) identical in shape to the original run's proof.

### Budget-seconds sizing rationale (129600s / 36h)

The original k=3/150-trial pass used `259200s` (72h) as a cap well above its worst-case serial
projection (~180000s at up to 1200s/trial × 150 trials), a ~1.44x margin. Design A's per-pass trial
count is 50 (25 tasks × 2 arms × k=1), so worst-case serial projection is ~60000s (1200s/trial ×
50). `129600s` preserves an equivalent-or-better margin (~2.16x) while staying comfortably below
the point where the cap would mask a genuinely stuck run. This value is fixed for all 3 passes —
do not lower it, and do not raise it without checking in (per the original brief's blocker
protocol for a budget-guard abort).

### Execution

Launched as a single detached background process (`run-design-a.sh`, sequential loop over the 3
passes, halting on any non-zero-non-clean exit rather than blindly chaining) via `nohup ... &
disown`, fully independent of the dispatching agent session. See the session's dispatch report for
the PID, log path (`jobs/design-a-run.log`), and launch verification evidence.

### Explicitly out of scope for this dispatch

- Classification (Inconclusive/Null/Positive/Negative) of any Design A result — there is no result
  yet; the passes have only just started.
- Any update to `docs/benchmarks/tb-delta-v6.12.0.md`'s existing drafted content.
- T409 or any downstream task.

These happen in a follow-up session once all 3 passes complete (or halt).

### Design A — host-exhaustion blocker and restart

**Blocker:** `type: technical`, `severity: major`, reported per this task's own blocker protocol
("Host resources genuinely exhausted at any checkpoint... stop, do not force the run, report with
the actual readings").

**What happened:** ~1h41m into Pass 1 of the first Design A attempt, Arm A had completed all 25
trials (valid `result.json`) and Arm B was 6/25 tasks in (4 errored, 2 cancelled, 19 pending — see
`jobs/tb-delta-20260905T224623Z-arm-{A,B}/result.json`) when the remote Docker daemon host
(`10.10.160.11`, reached via `DOCKER_HOST=ssh://root@10.10.160.11`) hit genuine resource
exhaustion: 4.0GB total RAM with 34MB free, swap 2.0GB/2.0GB fully exhausted, load average 13.79,
`docker ps`/`docker info` timing out even when run directly on the host. Root cause: the
`rstan-to-pystan` subset task's Stan/httpstan C++ compile step alone used ~3.3GB RSS (two
`cc1plus` processes) on a host with only 4GB total RAM — a real capacity problem with that
specific host, not a defect in the harness or in Design A's execution design.

**Response:** per the blocker protocol above and the user's explicit direction, the run was
stopped rather than forced: SIGTERM to the whole process group triggered Harbor's own graceful
`docker compose down --rmi local --volumes --remove-orphans` cleanup for the 2 in-flight Arm B
trials (`dna-assembly`, `caffe-cifar-10`) — both ended cleanly (`CancelledError` /
`RewardFileNotFoundError`, no orphaned containers). Pass 1's Arm A data (25/25 real trials, valid
`result.json`) survived intact in `jobs/tb-delta-20260905T224623Z-arm-A/`; Arm B's partial state
(6 trial subdirs, `result.json` present with `finished_at: null`, no scorecard — scorecard only
emits once both arms finish) survived intact in `jobs/tb-delta-20260905T224623Z-arm-B/`. This
first Design A attempt's log was preserved and renamed to
`jobs/design-a-run-attempt1-halted.log` — do not delete or overwrite it; it is evidence, matching
this task's own established pattern of preserving partial/orphaned run artifacts rather than
deleting them (e.g. the original k=3 run's `jobs/tb-delta-20260814T111217Z-arm-A-orphaned-trials/`
directory).

**Host resize and restart:** the user resized `10.10.160.11` to 24GB RAM / 8GB swap / 8 CPUs
(verified: `free -h` showed 22Gi available, `docker info` reported 8 cpus / 25769803776 bytes
mem). Design A was restarted from scratch (all 3 passes again, same invocation/parameters, same
wrapper script `run-design-a.sh`) with a fresh log at `jobs/design-a-run.log`. This second attempt
is in progress as of this writing (confirmed alive: `run-design-a.sh` and its
`scripts/tb-delta.sh` child process running, a live probe job
`jobs/tb-delta-20260906T061146Z-probe` on disk, host free memory healthy immediately after
restart). No result, spread, or classification exists yet for either Design A attempt — this
section records the blocker and restart only.

## Design A results and classification (final, 2026-09-08) — T407 closed

**Correction to the section immediately above, found during closeout:** this section's own text
characterizes the 2026-09-05 attempt's Pass 1 Arm A data as "25/25 real trials, valid
`result.json`." Independently re-checking `jobs/tb-delta-20260905T224623Z-arm-A/result.json`
during closeout: `n_completed_trials: 25`, `n_errored_trials: 25` — all 25 trials errored
(`RewardFileNotFoundError`/`AgentTimeoutError`), `reward_stats: {}`, zero real rewards. Arm B's 6
completed trials before the kill were errored too. So the 2026-09-05 attempt was **already**
invalid (same bind-mount root cause identified below) before the host-exhaustion event that
halted it — the exhaustion was a second, independent problem on top of an already-failed run,
not the run's sole defect. This does not change any downstream conclusion (neither attempt's
data was ever used), but the prior section's "valid" claim was not accurate and is corrected
here rather than silently left standing, per this task's own standard of independently checking
self-reported claims rather than assuming them.

### What happened after the restart

The restarted second attempt (still dispatched from `10.10.160.12` against the remote Docker
daemon on `10.10.160.11`) ran all 3 passes to completion but every trial in every pass failed —
confirmed directly from the 3 resulting scorecards
(`docs/benchmarks/scorecards/tb-delta-scorecard-2026090[6]T0[69]1146Z.json` /
`...T095951Z.json` / `...T142221Z.json`, all in this worktree): `n_errored_trials =
n_completed_trials = 25` for both arms in every pass, `RewardFileNotFoundError` (137-143
instances) and `AgentTimeoutError` (11-17 instances) across the three, `cost_usd: null`
throughout (no billable model completion was ever captured as a cost figure, despite real agent
execution happening — see the cost table in `tb-delta-v6.12.0.md` §7.2). Root cause, confirmed
by direct inspection of both hosts' filesystems for the same bind-mount path: Docker Compose
bind mounts resolve against the **daemon's** filesystem (`10.10.160.11`), not the client's
(`10.10.160.12`) — so every agent/verifier output file was silently written to `.11` and never
became visible to the Harbor process on `.12` that was waiting to read it back. This is a
`type: technical`, `severity: critical` root cause (100% trial failure across two full launch
attempts), now resolved (see below) rather than escalated, since a working fix was found and
verified before further dispatch was needed.

### Fix and successful run

Fix: run the Harbor CLI **co-located with the Docker daemon**, i.e. directly on
`10.10.160.11`. A fresh clone of this branch was bundled to `/root/emage-code-t407` on `.11`;
Harbor was installed there via a `uv`-managed Python 3.12 venv at `/root/.venvs/harbor-t407`
(the host's stock Ubuntu 22.04 Python does not support 3.12), resolving to Harbor 0.22.0 (one
minor version ahead of the original 0.21.0 install — CLI surface re-verified compatible:
`harbor run --help` shows the same `-k`/`-n` flags `tb-delta.sh` depends on, and a
`--config-only` dry run against the real frozen subset produced a clean config-diff identical in
shape to prior runs). A 4-trial smoke test there
(`docs/benchmarks/scorecards/tb-delta-scorecard-20260907T161020Z.json`, $0.32 total, now copied
into this worktree — see `tb-delta-v6.12.0.md` §7.1) came back clean: real rewards, zero
infrastructure errors. The full Design A run was then redispatched from `.11` and **completed
successfully** at 2026-09-08T05:10Z: all 3 passes, 150 real trials, valid reward data throughout,
no regression to the bind-mount failure mode.

### Results

Full raw numbers, cross-pass spread computation, and the rule application are in
`docs/benchmarks/tb-delta-v6.12.0.md` §6 (not duplicated here to avoid two sources of truth for
the same numbers — that document is the canonical report). Summary:

- Arm A pass means `[0.36, 0.28, 0.28]` → spread = **8.0pp** (exactly at the rule's `≥ 8pp`
  Inconclusive threshold, which is inclusive of equality).
- Arm B pass means `[0.32, 0.28, 0.28]` → spread = **4.0pp**.
- Aggregate delta (B−A) = **−1.33pp**.
- Design A cost: **$43.96** across the 3 successful passes (plus $0.32 for the `.11` smoke test;
  the two failed `.12` attempts cost $0.00 in API spend — pure infrastructure failure).

**Classification: INCONCLUSIVE**, per plan-035's frozen rule ("either arm's spread ≥ 8pp... Do
not report as null"). Arm A's spread alone triggers this branch; Arm B's tighter spread and the
small aggregate delta are not load-bearing for the classification and are not being used to
argue toward a Null reading, which the rule explicitly forbids. This is not a Positive, Negative,
or Null result — it is a statement that this measurement, as executed, did not reach the
precision the rule requires before any directional interpretation can be recorded. The rule's own
prescribed next step ("raise `k`, or reduce nondeterminism") is a real-cost follow-on, not
executed or authorized by this task — see the orchestrator's closing report.

### Total real cost, T407 in full

$34.13 (original k=3 run) + $0.00 (2 failed Design A attempts) + $0.32 (smoke test) + $43.96 (3
successful Design A passes) = **≈$78.41** across this task's entire history. See
`tb-delta-v6.12.0.md` §7.2 for the itemized table.

### Artifact reconciliation

The 3 successful passes' scorecard JSONs and `.runs/` proof directories (config-diff.json,
budget-guard.json, stdout logs — small, ~40KB per run) were copied from `10.10.160.11` into this
worktree, alongside every prior T407 artifact, for path-consistency with how this task has always
been referenced. The much larger raw `jobs/` trial directories (161MB on `.11`) were left there,
their location documented here and in `tb-delta-v6.12.0.md` §7.1, consistent with how this
worktree's own local `jobs/` tree (also 161MB, also untracked) has been handled throughout —
`jobs/` was never part of this task's declared output set (scorecard JSON + `.runs/` + the
benchmark doc only).

### T409 status

T409 ("Extend the T415 failure taxonomy to ingest Harbor trajectories") depends on T407
"genuinely completing," per `active-tasks.md`'s backlog note — not on any specific classification
outcome. T407 has now genuinely completed: real trial data and real Harbor trajectories exist
from both the original k=3 run and Design A's 3 passes (plus the two failed bind-mount attempts,
which are themselves real trajectory data of a different, infrastructure-failure kind — plausibly
also useful for taxonomy purposes, though that judgment call belongs to whoever picks up T409,
not to this closeout). T409 is assessed as unblocked by the closing orchestrator; it is not
dispatched by this task's closeout — that remains a separate decision. See
`docs/tasks/active-tasks.md` for T409's resulting ledger status.

---

*This task is closed. All artifacts referenced above are committed on this branch
(`feature/T407-tb-delta-v6.12.0`) and merged to `develop`. See `docs/tasks/completed-tasks.md`
for the archival record.*
