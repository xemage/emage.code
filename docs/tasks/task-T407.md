# Task T407 — First Terminal-Bench delta measurement (k≥3, full frozen subset)

**ID:** T407
**Owner:** devops-engineer
**Status:** in_progress
**Priority:** P0
**Depends on:** T418 (done), T419 (done), T408 (done) — all three genuinely merged to `develop`
via MR !203 (`scripts/tb-delta.sh`, `scripts/tb_delta_agent.py`, `docs/benchmarks/tb-subset.json`,
`docs/benchmarks/tb-delta-runner.md` all present on disk as of this brief). Does **not** depend on
T416 — Layer 2 was always independent of Layer 1's freeze (see
`docs/checkpoints/checkpoint-018-phase1-layer1-golden-suite-complete.md`, "Next steps").
**Created:** 2026-08-14
**Completed:** —
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
