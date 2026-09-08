# Terminal-Bench Two-Arm Delta — v6.12.0 (T407)

**Status: FINAL.** T407 is closed. §§1-5 below (the original k=3 single-pass measurement,
2026-08-14) are preserved verbatim as historical evidence and remain an explicit
non-classification, for the reasons given in §3 — that finding is not superseded, only extended.
§6 reports "Design A" (3 independent full-subset passes, dispatched specifically to produce a
measurement the frozen decision rule can actually classify) and applies plan-035's rule to it for
real. §7 states the artifact-reconciliation decision and the real total cost across the whole
T407 effort. Written per `docs/tasks/task-T407.md` Objective 6; §6/§7 numbers were independently
re-verified against the raw scorecard JSONs a second time by the closing session (see
`task-T407.md`'s final addendum for the verification method) — nothing below is taken on trust
from either the runner's own labels or a prior session's self-report.

**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.2.1, §2.4 Phase 1's registered
decision-rule block; `docs/tasks/task-T407.md`; `docs/benchmarks/tb-delta-runner.md`;
`docs/benchmarks/tb-subset.json`/`.md`.

**Raw scorecards (source of truth for every number below):**
- §§1-5 (original k=3 run): `docs/benchmarks/scorecards/tb-delta-scorecard-20260814T111217Z.json`
- §6 (Design A, 3 independent passes):
  `docs/benchmarks/scorecards/tb-delta-scorecard-20260907T162617Z.json` (pass 1),
  `...-20260907T203448Z.json` (pass 2), `...-20260908T001726Z.json` (pass 3) — all now present in
  this worktree at `docs/benchmarks/scorecards/` (copied from the host they actually ran on; see
  §7.1 for provenance and the reconciliation decision).

---

## 1. Run history (preserved from the scorecard's own `schema_note`)

The scorecard was **not** emitted by a single continuous `scripts/tb-delta.sh` invocation. Its
own `schema_note` field records:

> T407's original run was interrupted at 25/75 Arm-A trials (deliberate kill per explicit user
> instruction, not a crash); Arm A was completed via `harbor job resume -p <job_dir> -f
> NetworkConnectionError -f RuntimeError` (real Harbor 0.21.0 resume capability, reconciles by
> `TrialConfig` equality excluding `trial_name`/`job_id`) and Arm B was run fresh with the exact
> resolved config Harbor had already dumped for it at original config-diff time
> (`config-arm-b.json`). A reconciliation pass against T413's shape is still expected once
> `scripts/scorecard.py` lands (flagged as `type: dependency`, `severity: minor`).

Because `scripts/tb-delta.sh` mints a fresh `RUN_ID`/job name per invocation and has no
resume/merge path of its own, this scorecard JSON was emitted by a **standalone re-invocation of
the script's own Step 5 aggregation logic**, copied verbatim (`emit_scorecard.py`), reading the
resumed Arm A job dir and the freshly-run Arm B job dir. This does not affect trial-level data
integrity (verified below, §3) — it affects only how the final JSON was assembled, which is
disclosed here rather than presented as a normal single-shot run.

## 2. Raw numbers (both arms, independently re-verified)

| | Arm A (control) | Arm B (treatment) |
|---|---|---|
| Agent | `claude-code` (Harbor built-in) | `scripts.tb_delta_agent:EmageCodeClaudeCode` (emage.code projection) |
| Model | `claude-haiku-4-5-20251001` (economy) | same |
| `n_trials` (25 tasks × k=3 attempts) | 75 | 75 |
| Trials with a parseable reward | 61 | 69 |
| Trials with a logged exception | 21 | 17 |
| Trials with **both** a reward *and* an exception (e.g. timeout but still graded 0.0) | 7 | 11 |
| Mean reward (over the 61 / 69 rewarded trials) | 0.327869 (32.79%) | 0.304348 (30.43%) |
| Population stdev of per-trial reward (within this one run) | 0.469437 | 0.460131 |
| Cost | $15.20 | $18.94 |

**Delta (B − A):** −0.023521 (**−2.35 percentage points**). Total cost both arms: **$34.13**.

Config-diff proof (`.runs/20260814T111217Z/config-diff.json`): `"clean": true`, the only
difference between the two arms' resolved Harbor run configs is `agents[0].name` — confirming
T419's non-negotiable "the two arms differ only in projection" acceptance criterion held for
this run.

Budget guard (`.runs/20260814T111217Z/budget-guard.json`): probe ran for real (1027s on
`make-mips-interpreter`), projected serial-equivalent total 154,050s against a 259,200s cap —
`"aborted": false`. The guard did not interfere with this run.

### 2.1 Independent re-verification of the scorecard's own arithmetic

Per the brief ("the scorecard emitter was a standalone re-implementation... worth spot-checking
it's correct"), I recomputed every number above directly from the scorecard's raw
`reward_stats.reward` per-trial buckets (61 named A-trials, 69 named B-trials), not from the
scorecard's already-aggregated fields:

- Recomputed mean reward: A = 20/61 = 0.327869, B = 21/69 = 0.304348 — **exact match** to the
  scorecard's `delta.mean_reward_b_minus_a` field (−0.023521026372059828, reproduced to full
  float precision).
- Recomputed population stdev (Bernoulli, `sqrt(p(1-p))` over the rewarded-trial set): A =
  0.469437, B = 0.460131 — **exact match** to `spread.arm_a_stdev` / `spread.arm_b_stdev`.
- Cross-checked the apparent `61 + 21 ≠ 75` / `69 + 17 ≠ 75` arithmetic that looks inconsistent at
  first glance: the 7 (A) / 11 (B) trials that appear in **both** the reward bucket and the
  errored-trials list are trials that timed out or errored but were still graded (typically
  reward 0.0, e.g. `caffe-cifar-10__ykkQPTp`, `caffe-cifar-10__kK8BfkR` — both logged
  `AgentTimeoutError` *and* carry a recorded 0.0 reward). `61 + 21 − 7 = 75` and `69 + 17 − 11 =
  75` — the union of "rewarded" and "errored" trials is exactly 75 for both arms, with no
  double-counted or missing trials. This is expected behavior (a timeout can still leave a
  gradable, failed final state), not a data-integrity defect.

**Conclusion of the re-verification:** the scorecard emitter's Step 5 re-implementation is
arithmetically correct. No numbers in this document are taken on trust from the JSON's own
labels — all were reproduced independently from the underlying per-trial lists.

## 3. The k / spread question — worked reasoning, not an assertion

This is the substantive part of this document. Plan-035 §2.4 Phase 1's frozen decision rule
says, verbatim:

> Let `spread` = per-arm min–max across the k runs.
> - **Inconclusive** — either arm's spread ≥ 8pp... Do not report as null.
> - **Null** — both arms tight (spread < 8pp) and their ranges overlap, or `|mean delta| < 4pp`
>   (one task).
> - **Positive / negative** — ranges disjoint and `|mean delta| ≥ 4pp`.

### 3.1 What was actually measured

`scripts/tb-delta.sh --help` defines its own `-k` flag explicitly: `-k, --n-attempts N
Attempts per task per arm (Harbor's -k)`. This is Harbor 0.21.0's native, standard `-k`
mechanism — the same repeated-sampling convention used for `pass@k`-style metrics across the
Terminal-Bench/SWE-bench family. T407 was invoked with `-k 3 -l 25` (per `task-T407.md`'s
mandated invocation): **one** Harbor job per arm, sweeping the full 25-task frozen subset, with
each of the 25 tasks attempted 3 times inside that single job (25 × 3 = 75 trials per arm,
confirmed directly: the reward-bucket trial names reduce to exactly 25 distinct task base names
per arm, each appearing 3 times).

I confirmed this structurally, not just from the `--help` text: cross-referencing `started_at`
timestamps recorded in individual trial `result.json` files (e.g. three `caffe-cifar-10` trials
in Arm A start at `11:53:40`, `11:53:43`, `11:56:46` UTC on 2026-08-14, interleaved with other
tasks' first attempts starting around the same window) shows Harbor dispatched all 75 trials
into **one shared concurrent execution pool**, not as three sequential, complete passes through
the 25-task subset. There is no "run 1 finishes all 25 tasks, then run 2 starts" structure to
recover from this job's data, even retroactively.

### 3.2 Why this does not satisfy the rule's literal wording

The rule's phrase "per-arm min–max **across the k runs**" describes a design where each of the
`k` "runs" is a **complete, independent pass over the whole subset**, producing **one aggregate
arm-level score per run**, and `spread` is the range across those `k` aggregate numbers (e.g.
three numbers like `0.31, 0.34, 0.29` → spread = 0.05). That design directly answers the
question the rule cares about: *if we remeasured this arm's aggregate score from scratch, how
much would it move?* — i.e., run-to-run reproducibility of the reported statistic.

What was executed instead is a **single** full pass per arm, inside which each task was sampled
3 times (Harbor's own `-k`, a legitimate and standard technique for estimating **per-task**
outcome variance — how consistent is *this task's* result across repeated attempts). That is a
different question and a different granularity: it says nothing directly about whether
re-running the *entire measurement* would reproduce the same 0.328 / 0.304 aggregate means.

At the granularity the rule's own sentence assumes — "the k runs" as complete subset passes —
this measurement is **k = 1 per arm**, not k = 3. The 3× replication that did happen (attempts
per task) is real and useful, but it is not the replication the decision rule specifies.

### 3.3 Is the scorecard's own `spread` field a valid stand-in? No — and here's why

The scorecard's `spread.arm_a_stdev` / `spread.arm_b_stdev` fields (0.469 / 0.460) are the
**population standard deviation of individual 0/1 trial outcomes within the one run that did
happen**. I verified this is exactly what they are (§2.1: `sqrt(p(1-p))` over the rewarded-trial
set reproduces them to full precision).

This statistic is not a usable substitute for the rule's "min–max across k runs" concept, for a
structural reason, not just a labeling one: for **any** binary (0/1) reward with a success rate
`p` roughly between 0.07 and 0.93, `sqrt(p(1-p))` is **always** somewhere around 0.25–0.50 —
mechanically, almost by construction, regardless of whether the underlying measurement process
is highly reproducible or wildly noisy. A perfectly deterministic, zero-noise remeasurement of
the same 61/69 binary outcomes would report the *same* ~0.46 "spread" as this run did — because
the statistic measures **how much individual trials differ from each other** (which is inherent
to a binary benchmark and says nothing about measurement noise), not **how much the aggregate
score would differ across repeated full measurements** (which is what "noise" means in this
context).

Applying the rule's literal `≥ 8pp` (0.08) threshold to this field is therefore a category
error: it would classify essentially *any* binary-reward Terminal-Bench delta measurement as
"Inconclusive," including a hypothetical noise-free one, because per-trial Bernoulli stdev
almost never drops below 0.08 for a subset with a moderate pass rate. The field is an honestly
computed, correctly labeled statistic — it is just not the one the decision rule's classification
logic needs.

**Is there a way to compute the rule's actual intended statistic from the data that exists?** I
checked whether the existing 75 trials per arm could be retroactively partitioned into 3
pseudo-independent "runs" (e.g., first attempt at each task = pseudo-run 1, etc.) to recover a
usable approximation. Per §3.1, trial `started_at` timestamps show attempts were dispatched into
one shared concurrency pool, not three temporally-separated complete sweeps — there is no
principled way to assign a given trial to "run 1" vs. "run 2" vs. "run 3" that would correspond
to what three genuinely independent invocations of `scripts/tb-delta.sh -l 25` would have
produced (different container builds, different registry-pull timing, different scheduling
order, etc. all plausibly contribute to real run-to-run variance that this single job's internal
structure cannot separate out). **The statistic the rule requires does not exist in recoverable
form in this artifact.**

As a **supplementary, non-rule** sanity check (explicitly not a substitute for "spread" as
defined), I computed the standard error of each arm's mean under a simple i.i.d.-Bernoulli
approximation: `SE = stdev / sqrt(n)`. `SE_A = 0.469437 / sqrt(61) = 0.0601` (6.0pp), `SE_B =
0.460131 / sqrt(69) = 0.0554` (5.5pp), combined `SE_delta = sqrt(SE_A² + SE_B²) = 0.0817`
(8.2pp). The observed delta magnitude (2.35pp) is well under one combined standard error —
directionally consistent with "this delta is not distinguishable from zero," but this is my own
supplementary calculation, computed on a different statistical basis (independence-of-trials
approximation, not the rule's own run-level min–max), and I am not using it to assign the formal
classification below. It also likely *understates* true variance, since the three attempts per
task are not fully independent of each other (same container image, same task definition, same
model) the way three separate `scripts/tb-delta.sh` invocations would be.

### 3.4 What the frozen rule can still tell us, independent of the spread question

One part of the classification does not depend on resolving the spread ambiguity at all: the
**Positive/Negative** branch requires *both* "ranges disjoint" *and* `|mean delta| ≥ 4pp`. The
observed `|mean delta|` is 2.35pp — below the 4pp bar on its own, regardless of how "ranges
disjoint" is ultimately defined or computed. **This measurement cannot be classified Positive or
Negative under the rule as written, independent of the spread question.** The only live
question is whether the correct label is Inconclusive or Null — and that distinction is exactly
what hinges on the "spread" statistic that, per §3.3, was not validly produced by this run.

### 3.5 Conclusion: explicit non-classification

**This measurement cannot be classified as Inconclusive, Null, Positive, or Negative under
plan-035's frozen decision rule as literally written**, because the rule's classification
machinery requires a `spread` value computed as per-arm min–max across `k ≥ 3` independent
full-subset measurement runs, and only one such run was performed per arm — despite each of the
25 tasks within that one run being sampled 3 times (Harbor's own `-k`, a real but different
replication axis). At the granularity the rule's own text assumes, this is k = 1 per arm, and
"spread" (min − max of one number) is either undefined or trivially zero — which would
misleadingly read as "tight" and risk licensing a false-confident Null (or worse, would combine
with §3.4's `|mean delta| < 4pp` finding to look like a clean, low-variance Null result when no
run-to-run variance was actually measured at all).

This is precisely the scenario plan-035 §2.2.1 itself names, in its own words, as the failure
mode the whole `k ≥ 3` / spread discipline exists to prevent: *"A 3-point 'improvement' from a
single run of each arm is indistinguishable from noise."* Here the direction is negative rather
than positive, and the magnitude is 2.35pp rather than 3pp, but the structural situation is the
same: one full-subset run per arm, with a small aggregate difference between arms that this
particular measurement design cannot distinguish from noise.

I am declining to force a label. Per `docs/tasks/task-T407.md`'s own "Note on `spread` units,"
the task brief that dispatched this run already flagged this exact tension (it proposed treating
the runner's `spread.arm_a_stdev`/`arm_b_stdev` fields as the operative "spread," while
explicitly deferring final classification to "the orchestrator... before classifying"). That
proposed reinterpretation is a plausible operational reading, but it was never registered as a
dated successor block to the frozen decision rule (the rule's own text states it "may not be
edited after the first T41A run — only superseded by a dated successor block that states what
changed and why"; no such block exists in `plan-035-roadmap-v7-ground-up.md` as of this writing).
Absent that supersession, I am treating the rule's original, literal wording as authoritative,
and reporting that this run does not satisfy it, rather than quietly adopting the task brief's
gloss as if it had already been ratified.

## 4. Supplementary context (not part of the formal classification)

### 4.1 `predicted_effect` breakdown

The registered prediction (frozen at T418 time, before any measurement) was: projection expected
to move tasks tagged `predicted_effect: positive` (16 of 25 — multi-step planning tasks), and to
be neutral on the other 9. Computed from the same per-trial reward data:

| Group | n tasks | Arm A mean | Arm B mean | Delta (B−A) |
|---|---|---|---|---|
| `predicted_effect: positive` | 16 | 0.4000 (n=40 rewarded trials) | 0.3556 (n=45) | **−4.44pp** |
| `predicted_effect: neutral` | 9 | 0.1905 (n=21) | 0.2083 (n=24) | **+1.79pp** |

This is the **opposite** of the registered prediction — the tasks predicted to move positive
moved negative, and the tasks predicted to be neutral moved slightly positive. Recorded here per
the rule's own "check the `predicted_effect: positive` tasks in isolation" instruction, but I am
explicitly **not** treating this as a finding in its own right: n=40/45 and n=21/24 are small,
no significance test was applied, and this pre-committed check was written for the "Null" branch
specifically — which this report does not reach. It is disclosed as context, not interpreted
further, and — per the decision rule's own "do not act on it in this release cycle" instruction
for this exact check — no action follows from it here.

### 4.2 Host state (re-verified independently, 2026-08-15)

- `free -h`: 5.8Gi total, 4.3Gi used, 668Mi free, 998Mi buff/cache, 1.5Gi available, 1.7Gi swap
  in use of 8.0Gi. No indication this reflects a T407 leak specifically — no Harbor/Docker
  processes are attributable (see below).
- `docker ps -a`: **empty** — zero containers, running or stopped.
- `ps aux | grep -iE "harbor|tb-delta|tb_delta"`: **no matches** — no leftover driver or resume
  process.
- `jobs/` directory on disk: 150M of raw per-trial artifacts (transcripts, logs) under
  `/home/emage/Code/emage/worktrees/t407-tb-delta/jobs/`; not itself a running-resource concern,
  but flagged here since it is untracked and not part of this task's declared output set
  (`docs/tasks/task-T407.md`'s "Expected outputs" lists only the scorecard JSON, `.runs/*`
  config artifacts, and this document — not the full `jobs/` tree).

Confirms the coordinating session's report: nothing from T407's run is still occupying host
resources.

## 5. Does T407 need to be re-run at a different granularity?

**To produce a result classifiable under plan-035's decision rule as literally written: yes.**
What's needed is `k ≥ 3` **independent full-subset passes** per arm — i.e., invoke the two-arm
comparison against the full frozen 25-task subset three (or more) separate times, each producing
one aggregate mean-reward number per arm, then compute `spread = max − min` across those
per-arm numbers. The cheapest literal-compliant design would be 3 passes at 1 attempt per task
per pass (`-k 1 -l 25`, run 3 times) — 25 × 1 × 2 arms × 3 passes = 150 total trials, the same
total trial count T407 already spent, just restructured into three separable measurements
instead of one. A stronger design (keeping 3 attempts per task *and* 3 independent passes) would
be roughly 3× today's cost and wall-clock (~$100+, multiple days at the authorized `-n 2`
concurrency — T407's single pass alone took from 2026-08-14T11:12Z to roughly
2026-08-15T14:56Z, including one deliberate interruption-and-resume).

This is a materially larger undertaking than T407 as executed and requires the same kind of
explicit, scale/cost-aware authorization T407 itself received before dispatch — I am not
starting it. T418's subset freeze is not violated by this option (same 25 tasks, just measured
more than once), so it would not conflict with the "the subset is not re-cut" consequence in the
decision rule's null-branch text.

**Given the current single-run data alone:** the delta (−2.35pp) is small relative to every
noise indicator available (per-trial Bernoulli stdev ~46–47%, supplementary SE-of-mean ~5.5–6.0pp
per arm), and is below the rule's own 4pp bar for a Positive/Negative call regardless of the
spread question. If a decision is needed *now*, without further measurement, the most honest
statement is: **there is no evidence of a reliable effect in either direction at this scale**,
but this is not the same as a rule-conformant "Null" — that label specifically requires the
spread evidence this run did not produce.

---

## 6. Design A — 3 independent full-subset passes (2026-09-07/08), raw results and classification

### 6.0 Execution summary

Two prior Design A launch attempts (2026-09-05 and 2026-09-06, both dispatched from
`10.10.160.12` against a remote Docker daemon at `10.10.160.11` via
`DOCKER_HOST=ssh://root@10.10.160.11`) produced **no usable data** — every trial across both
attempts failed with `RewardFileNotFoundError` and/or `AgentTimeoutError`. Root cause,
confirmed by direct inspection of both hosts' filesystems for the same bind-mount path: Docker
Compose bind mounts resolve against the **daemon's** filesystem (`.11`), not the client's
(`.12`), so every agent/verifier output was silently stranded on `.11`, unreachable by the
Harbor process running on `.12` that was waiting to read it back.

**Correction to `task-T407.md`'s own prior (uncommitted) "host-exhaustion blocker and restart"
section:** that section characterizes the 2026-09-05 attempt's Pass 1 Arm A data as "25/25 real
trials, valid `result.json`." Independently re-checking that job's actual `result.json`
(`jobs/tb-delta-20260905T224623Z-arm-A/result.json`) during this closeout: `n_completed_trials:
25`, `n_errored_trials: 25` — **all 25 trials errored** (`RewardFileNotFoundError` /
`AgentTimeoutError`), `reward_stats: {}` (zero real rewards recorded). Arm B's 6 completed
trials before the host-exhaustion kill were errored too (4 `RewardFileNotFoundError`, 2
`CancelledError` from the kill itself). So the 2026-09-05 attempt was **already** hitting the
same bind-mount failure mode that the 2026-09-06 attempt (3 full passes, all 100% failed —
`docs/benchmarks/scorecards/tb-delta-scorecard-2026090[6]T0[6-9]*.json` /
`...T142221Z.json`, all showing `n_errored_trials` = `n_completed_trials` for both arms) later
confirmed structurally — the host-exhaustion event that halted the 2026-09-05 attempt was a
second, independent problem layered on top of an already-invalid run, not the sole cause of that
attempt's invalidity. This correction does not change T407's outcome (neither attempt produced
data that was ever going to be used), but it is recorded here because the original text
overstated what that attempt actually produced, and this task's own history is explicit that
self-reported claims get independently checked, not assumed.

Fix: run the Harbor CLI **co-located with the Docker daemon**, i.e. on `10.10.160.11` itself
(fresh `harbor` 0.21.0 install via a `uv`-managed Python 3.12 venv at
`/root/.venvs/harbor-t407` — the host's stock Ubuntu 22.04 Python does not support 3.12). A
4-trial smoke test there (`tb-delta-scorecard-20260907T161020Z.json`, $0.32 total) came back
clean — real rewards, zero infrastructure errors — before the full Design A run was
redispatched from `.11` and completed successfully across all 3 passes.

### 6.1 What was run

Per `task-T407.md`'s Design A addendum: 3 **independent** invocations of
`scripts/tb-delta.sh -k 1 -l 25 --n-concurrent 2 --max-budget-seconds 129600`, run sequentially
(never concurrently), each a separate process with its own config-diff proof and budget-guard
probe. Both arms, full frozen 25-task subset, `k=1` per pass — so the rule's "k independent
runs" is satisfied by 3 passes of k=1, not 1 run of k=3 (the granularity mismatch §3 identified
in the original run). 25 tasks × 2 arms × k=1 = 50 trials/pass, 150 trials total — the same
total trial count as the original k=3 run, restructured across 3 independent measurements
instead of one.

### 6.2 Raw per-pass numbers (independently re-verified from the raw scorecard JSONs)

| Pass | Scorecard | Arm A mean | Arm B mean | Delta (B−A) | Cost | Notable errors |
|---|---|---|---|---|---|---|
| 1 | `tb-delta-scorecard-20260907T162617Z.json` | 0.36 (9/25) | 0.32 (8/25) | −4.00pp | $13.9952 | A: 1 `AgentTimeoutError`; B: 2 `AgentTimeoutError` |
| 2 | `tb-delta-scorecard-20260907T203448Z.json` | 0.28 (7/25) | 0.28 (7/25) | 0.00pp | $13.1988 | A: 3 `AgentTimeoutError`; B: 2 `AgentTimeoutError` |
| 3 | `tb-delta-scorecard-20260908T001726Z.json` | 0.28 (7/25) | 0.28 (7/25) | 0.00pp | $16.7683 | A: 3 `AgentTimeoutError`; B: 2 `AgentTimeoutError` + 6 `ApiUsageLimitError` (rate-limit artifact of sustained real usage, not a harness defect — confirmed by checking the exception text, which names a provider-side usage cap, not a harness/config error) |

Every pass: `n_completed_trials = 25`, `n_rewarded_trials = 25` for both arms (zero trials with
no reward recorded — a real improvement over the original run's 61/69-of-75), config-diff
`"clean": true` with only `agents[0].name` differing, budget-guard `"aborted": false` (worst-case
serial projections 39150-44550s against the 129600s cap — comfortable margin, no guard
interference).

**Re-derivation method:** for each pass, I read the raw `job_summary_stats.evals.*.reward_stats
.reward` per-trial buckets directly (not the scorecard's own pre-aggregated `delta`/`spread`
fields) and recomputed each arm's mean as `(count of reward=1.0 trials) / 25`. All three passes'
recomputed means match the values above exactly (Pass 1: 9/25=0.36, 8/25=0.32; Pass 2: 7/25=0.28
both arms; Pass 3: 7/25=0.28 both arms). Per-pass costs were recomputed by summing each arm's raw
`cost_usd` field; both arms' sums match the table above to the cent.

### 6.3 Cross-pass spread and aggregate delta

- **Arm A** pass means: `[0.36, 0.28, 0.28]` → **spread (max − min) = 8.0pp** (exactly).
- **Arm B** pass means: `[0.32, 0.28, 0.28]` → **spread (max − min) = 4.0pp**.
- **Aggregate mean:** A = (0.36+0.28+0.28)/3 = **0.30667** (30.67%), B =
  (0.32+0.28+0.28)/3 = **0.29333** (29.33%).
- **Aggregate delta (B−A):** **−1.33pp**.

These are the "k independent runs" numbers the original rule's text describes — 3 separate
full-subset passes, one aggregate arm-level score per pass, spread = the range across those 3
numbers. This is the measurement design §3.2/§3.5 of this document identified as missing from
the original run.

### 6.4 Classification, applying plan-035's frozen rule verbatim

> Let `spread` = per-arm min–max across the k runs.
> - **Inconclusive** — either arm's spread ≥ 8pp. The measurement failed; the result is not
>   about emage.code. Action: raise `k`, or reduce nondeterminism, before any interpretation is
>   recorded. Do not report as null.
> - **Null** — both arms tight (spread < 8pp) and their ranges overlap, or `|mean delta| < 4pp`.
> - **Positive / negative** — ranges disjoint and `|mean delta| ≥ 4pp`.

Arm A's spread is 8.0pp. The rule's Inconclusive branch triggers on "either arm's spread **≥**
8pp" — the operator is inclusive of equality, and Arm A's spread lands exactly on that boundary,
not merely near it. Because the Inconclusive branch is evaluated first in the rule's own
if/elif structure (checked before the Null branch's "both arms tight" precondition can even be
evaluated) and Arm A alone is sufficient to trigger it, Arm B's spread (4.0pp, which would
individually read as tight) and the aggregate delta (−1.33pp, which would individually read as
within the Null band) do not change the outcome. Both are recorded above for completeness, but
neither is load-bearing for the classification.

### **CLASSIFICATION: INCONCLUSIVE.**

Per the rule's own text: **"The measurement failed; the result is not about emage.code."** This
is not a Null result, and this document does **not** report it as one — the rule is explicit
that Inconclusive must not be reported as Null, and doing so would misleadingly suggest evidence
of "no effect" when what actually happened is that Arm A's own aggregate score moved 8pp
between passes 1 and 2/3 (0.36 → 0.28), which is measurement noise large enough to make the
−1.33pp aggregate delta and the 4.0pp Arm B spread uninterpretable — a swing that size could
fully explain an observed delta several times larger than the one actually measured.

**What Inconclusive means here, per the rule's own words:** this specific instrumentation
(economy-tier model, `k=1`-per-pass / 3-pass design, this subset, this host configuration) did
not produce a result stable enough to classify. It says nothing about whether the emage.code
projection helps, hurts, or is neutral for Terminal-Bench — the measurement itself did not reach
the precision needed to say. The rule's own **Action**, verbatim: "raise `k`, or reduce
nondeterminism, before any interpretation is recorded." No Positive/Negative/Null interpretation
is recorded in this document, per that instruction.

**Note on what does *not* apply:** plan-035's "Consequences of a null delta, pre-committed"
block (publication-with-prominence, no re-cutting the subset, harness demoted to
no-harm-guardrail with a −4pp guardrail floor, etc.) is written for a **Null** classification
specifically. This result is Inconclusive, not Null — that block is not invoked here. The one
piece of that surrounding text that *is* generically applicable regardless of branch is the
rule's own opening framing that a delta is not reportable without its spread; §6.3 supplies that
spread, and it is what makes this Inconclusive rather than an unreported number.

**Recommended next step (per the rule's own Action text, not executed here):** raising `k` (more
independent passes, so a single 8pp swing has less leverage over the reported spread) or
reducing nondeterminism (e.g. investigating why Arm A's own score moved from 0.36 to 0.28 pass
1→2, since that specific swing is the entire reason this result is Inconclusive) would be the
literal next move the rule prescribes. This is a real-cost, real-wall-clock decision on the same
order as Design A itself and is explicitly **not** authorized or dispatched by this document —
see `task-T407.md`'s closing addendum and the orchestrator's final report for how this is being
surfaced to the user.

### 6.5 What Arm A's 0.36 → 0.28 → 0.28 swing plausibly reflects

Not part of the formal classification (the rule does not ask for a root-cause theory before
reporting Inconclusive), but worth recording as context: Pass 1 logged the fewest
`AgentTimeoutError`s of the three passes for Arm A (1, vs. 3 and 3), and Pass 3 additionally saw
6 `ApiUsageLimitError`s on Arm B specifically (a provider-side rate-limit artifact of sustained
real usage across this task's cumulative spend, not a harness or config defect — see §6.2).
Timeout-sensitive tasks inside the frozen subset were already flagged as a known risk at T407's
original dispatch (`task-T407.md`'s "Known pre-existing risk to interpretation" section, citing
T417's 17/25 oracle pass rate and specifically calling out `caffe-cifar-10` and `crack-7z-hash`
as compute-heavy/timing-sensitive). `caffe-cifar-10` and `feal-linear-cryptanalysis` recur across
multiple passes' `AgentTimeoutError` lists here, consistent with that pre-registered concern. No
further action is taken on this observation in this document.

## 7. Artifact reconciliation and total real cost

### 7.1 Where the Design A artifacts live, and why

The 3 real Design A passes ran with the Harbor CLI on `10.10.160.11` (per §6.0's fix), so their
raw outputs were produced there, at `/root/emage-code-t407/`. Reconciliation decision for this
closeout:

- **Copied into this worktree** (small, and every prior T407 artifact has been referenced by
  in-repo path — keeping that consistent): the 3 pass scorecard JSONs, the smoke-test scorecard,
  and their `.runs/<run-id>/` proof directories (config-diff.json, budget-guard.json,
  stdout logs) — 4 run directories, 40KB each, ~292KB total for the scorecards directory as a
  whole. Copied via `scp` directly from `10.10.160.11`; byte sizes verified identical
  post-copy (209578/22380/31504/60950 bytes for the four scorecard JSONs — matches the source
  listing exactly). All now live under `docs/benchmarks/scorecards/` and
  `docs/benchmarks/scorecards/.runs/` in this worktree, alongside the original run's artifacts.
- **Left on `10.10.160.11`, location documented here, not copied:** the full `jobs/` trial
  directories (raw per-trial transcripts, logs, container artifacts) — 161MB on `.11` at
  `/root/emage-code-t407/jobs/`. This mirrors the existing, already-established handling of this
  worktree's own `jobs/` tree (161MB locally, from the original run plus both failed Design A
  attempts): untracked, not committed, and explicitly outside T407's declared output set per the
  original brief's "Expected outputs" (scorecard JSON + `.runs/` artifacts + this document —
  never the full `jobs/` tree). Applying the same standard to the `.11`-resident `jobs/` tree
  rather than a different one for consistency's sake would be the inconsistent choice; leaving
  large raw trial data off git (on either host) while promoting the small, structured proof
  artifacts (scorecards + `.runs/`) into the repo is the pattern this task has followed
  throughout.

### 7.2 Total real cost, T407 in full

**Correction (2026-09-08, post-merge):** the table and total originally published in this section
misread `cost_usd: null` on the two failed Design A attempts as "$0 spent" and reported a grand
total of "≈$78.41". That reading was wrong — see below for the corrected accounting.

| Component | Cost | Status |
|---|---|---|
| Original k=3 single-pass run (2026-08-14, §2) | $34.13 | Recorded (sum of `agent_result.cost_usd` across 130/150 trial `result.json` files; the other 20 trials errored before an agent session ran and have no cost either way) |
| Design A smoke test on `.11` (2026-09-07, 4 trials) | $0.32 | Recorded |
| Design A, 3 successful independent passes (2026-09-07/08, §6.2) | $43.96 | Recorded |
| **Subtotal — Harbor-recorded cost** | **$78.41** | Exact, not an estimate |
| Design A, 2 failed bind-mount attempts (2026-09-05/06, 181 real trial-attempts across arms A/B) | not recorded by Harbor | `agent_result.cost_usd` is `null` in all 181 of these trials' `result.json` files (independently confirmed by direct inspection of every file); see "Why no cost data" below |
| Rate-based estimate of the unrecorded portion | ≈$22 | Not a measurement — see methodology below |
| **Honest total estimate, entire T407 effort** | **≈$100** | $78.41 recorded + ≈$22 estimated, rounded because the unrecorded portion is an approximation |

**Why the two failed attempts show no cost data — this is not "$0 spent," it is "$0 recorded":**
both failed attempts hit the same Docker-bind-mount misconfiguration identified as the root cause
of their trial failures (§6.0) — bind mounts resolved against the daemon's filesystem
(`10.10.160.11`) rather than the client's (`10.10.160.12`). The same per-trial result-writing path
that this bug broke for reward files also carries Harbor's cost bookkeeping; when that path fails,
`agent_result.cost_usd` is left `null` rather than backfilled with `0`. Real Claude Code agent
sessions ran against real tasks in all 181 of these trial-attempts before the trials failed, and
real tokens were consumed in the process — the absence of a recorded cost reflects a recording
gap, not zero billing.

**Rate-based estimate, methodology:** Harbor recorded both cost and precise per-trial
`started_at`/`finished_at` timestamps for the one dataset with fully reliable cost data — the
original k=3 run (150 trials, $34.13 recorded, 163,516s of summed real per-trial elapsed time) —
giving a rate of **$34.13 / 163,516s ≈ $0.000209/s**. Applying that rate to the failed attempts'
own real elapsed time (181 trials, 104,254s of summed elapsed time, computed the same way from
each trial's own `started_at`/`finished_at`) gives **104,254s × $0.000209/s ≈ $21.76**, rounded to
**≈$22** above.

**Caveat on precision — do not over-read this estimate:** this is a rate extrapolation from one
dataset onto another, not a measurement, and the result is sensitive to a real methodological
choice: which per-trial time window is used as the cost-driving basis. The figure above uses each
trial's full wall-clock span (`started_at`/`finished_at` at the trial level — container setup
through verification). Using instead the narrower `agent_execution.started_at`/`finished_at`
window (agent activity alone, excluding setup/verification overhead — arguably a better
mechanistic proxy for token-driven cost, since setup and verification consume no LLM tokens) gives
a meaningfully different figure: $34.13 / 59,706s ≈ $0.000572/s applied to the failed attempts'
77,412s of agent-execution-only time ≈ **$44**, which would put the honest total nearer **≈$123**
instead of ≈$100. Both bases are defensible; neither is exact. This roughly 2x spread between two
reasonable methodologies is itself evidence that the unrecorded portion cannot be pinned down from
Harbor's artifacts alone.

**Recommendation:** treat **≈$100** (with a plausible range extending toward ≈$120+ depending on
methodology) as a rough planning figure only, not a final number. For the authoritative
ground-truth figure, check the Anthropic Console / usage dashboard directly for the account and
date range covering T407's Design A work (2026-09-05 through 2026-09-08) — neither Harbor's
scorecards nor this repository's artifacts can produce an exact number for the unrecorded portion;
only the billing system that actually metered the API calls can.

---

*Finalized by the closing orchestrator session for T407. §§1-5 unchanged from the prior draft.
§§6-7 added after independently re-verifying the Design A raw scorecard JSONs on
`10.10.160.11` directly (not trusting the dispatching brief's own table, though it was found to
match on every figure checked). Committed to `feature/T407-tb-delta-v6.12.0`; see
`docs/tasks/task-T407.md`'s closing addendum and `docs/tasks/completed-tasks.md` for T407's full
closeout record. T409's unblock status is assessed separately in the orchestrator's final report
— not dispatched by this document.*

*§7.2 corrected 2026-09-08 (docs/t407-cost-correction branch): the merged version of this
document understated total real cost by reading `cost_usd: null` on 181 failed-attempt trials as
"$0 spent" instead of "$0 recorded." Corrected independently by re-deriving cost, `cost_usd`
nullness, and per-trial elapsed time directly from every `result.json` under
`jobs/tb-delta-20260905T224623Z-arm-{A,B}/` and `jobs/tb-delta-20260906T{061146,095951,142221}Z-
arm-{A,B}/` (181 trials, confirmed 181/181 `cost_usd: null`) and the original k=3 run's own
`result.json` files (confirmed $34.1334 recorded across 130/150 trials). See the corrected §7.2
table and its methodology/caveat notes for the honest ≈$100 total estimate and the recommendation
to check the Anthropic Console for ground truth.*

---

## 8. Follow-up: `predicted_effect` split on Design A's raw data (observational, not acted on)

**Status of this section: observational follow-up only.** Per plan-035's Null-branch
consequences ("Check the `predicted_effect: positive` tasks in isolation. If they moved and the
aggregate did not, the subset is diluted — record this, but do not act on it in this release
cycle"), now extended to the Inconclusive result by the 2026-09-08 successor block in
`docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 (see also ADR-004). This section records the
check. It is **not** used to reopen T407's Inconclusive classification, re-cut `tb-subset.json`,
or authorize further trials — that would be exactly the outcome the frozen decision-rule block
was written to prevent. Zero new API spend: this is computed entirely from Design A's existing
raw per-trial `result.json` files, already paid for as part of T407.

**Data source.** For each of the 3 Design A passes
(`20260907T162617Z`/`20260907T203448Z`/`20260908T001726Z`), both arms, read every trial's
`result.json` directly from the raw job directories on `10.10.160.11`
(`/root/emage-code-t407/jobs/tb-delta-<pass>-arm-{A,B}/*/result.json` — not the scorecards, which
only carry arm-level aggregates). Each of the 25 tasks appears exactly once per arm per pass
(`k=1` design), so per-task reward is a single 0.0/1.0 value; no aggregation across attempts
within a pass was needed. All 25 tasks × 3 passes × 2 arms = 150 trials were read and every one
had a real recorded reward (no missing or duplicate task/pass/arm combinations) — full agreement
with §6.2's `n_rewarded_trials = 25` for both arms in every pass. `tb-subset.json`'s own
`predicted_effect` tags (16 `positive`, 9 `neutral`) were used as-is, read-only, per this file's
freeze policy.

### 8.1 Group means and delta, by pass

| Pass | Group | n | Arm A mean | Arm B mean | Delta (B−A) |
|---|---|---|---|---|---|
| 1 (`162617Z`) | positive | 16 | 31.25% (5/16) | 37.50% (6/16) | **+6.25pp** |
| 1 (`162617Z`) | neutral | 9 | 44.44% (4/9) | 22.22% (2/9) | **−22.22pp** |
| 2 (`203448Z`) | positive | 16 | 37.50% (6/16) | 37.50% (6/16) | 0.00pp |
| 2 (`203448Z`) | neutral | 9 | 11.11% (1/9) | 11.11% (1/9) | 0.00pp |
| 3 (`001726Z`) | positive | 16 | 37.50% (6/16) | 37.50% (6/16) | 0.00pp |
| 3 (`001726Z`) | neutral | 9 | 11.11% (1/9) | 11.11% (1/9) | 0.00pp |

### 8.2 Aggregate across all 3 passes, by group

| Group | n (task-attempts) | Arm A mean | Arm B mean | Delta (B−A) |
|---|---|---|---|---|
| `predicted_effect: positive` | 48 (16 tasks × 3 passes) | 35.42% (17/48) | 37.50% (18/48) | **+2.08pp** |
| `predicted_effect: neutral` | 27 (9 tasks × 3 passes) | 22.22% (6/27) | 14.81% (4/27) | **−7.41pp** |

Sanity check against §6.3's published aggregate: weighting these two group deltas by their trial
counts reproduces the document's own aggregate delta exactly — `(48 × +2.08pp + 27 ×
−7.41pp) / 75 = −1.33pp`, matching §6.3's reported aggregate to the same precision.

### 8.3 What drives the split, and why it should not be read as a pattern

Passes 2 and 3 show **zero** within-group delta for both groups — Arm A and Arm B produced
identical per-task outcomes for every one of the 25 tasks in both of those passes. The entire
group-level split in §8.2 is attributable to Pass 1 alone, and within Pass 1, to a small number
of individual task-level flips:

- Positive group's entire pass-1 delta (+6.25pp) is one task: `custom-memory-heap-crash` (Arm A
  0.0, Arm B 1.0) — the only positive-tagged task where the two arms differed in that pass.
- Neutral group's entire pass-1 delta (−22.22pp) is two tasks: `crack-7z-hash` and
  `sparql-university` (both Arm A 1.0, Arm B 0.0) — the only neutral-tagged tasks where the two
  arms differed in that pass.

This is the same Pass 1 already identified in §6.4/§6.5 as the source of Arm A's 8.0pp cross-pass
spread (0.36 → 0.28 pass 1→2) that made the overall measurement Inconclusive. A group of 9
`neutral` tasks has enough leverage that two single-trial (`k=1`) flips move its mean by 22
percentage points; a group of 16 `positive` tasks needs only one flip to move 6 points. Neither
figure reflects a stable, repeated group-level effect — both groups are flat (0.00pp) in the two
passes that were not affected by whatever produced Pass 1's anomalous Arm A behavior.

**Direction, stated plainly and with the caveats it needs:** in this dataset, the tasks tagged
`predicted_effect: positive` show a small positive aggregate delta (+2.08pp) and the tasks tagged
`neutral` show a larger negative aggregate delta (−7.41pp) — the *opposite* pairing from what the
registered prediction anticipated (positive tasks were expected to move, neutral tasks were
expected to stay flat), and also the opposite pairing from the number already published in §4.1
for the original k=3 single-pass run (positive −4.44pp, neutral +1.79pp, computed on a
structurally different single-run dataset). Two independent measurements on this same
subset have now produced opposite-signed group splits. Combined with §8.1's evidence that the
whole split in this dataset reduces to 3 individual task-level flips inside 1 of 3 passes, on
groups of only 16 and 9 tasks, this is not read as evidence of a real `predicted_effect`-linked
effect in either direction — the sample is too small and too dominated by single-trial variance
to distinguish a group-level pattern from noise. No action is taken on this observation, per the
instruction this section exists to satisfy.

---

**Closing note (2026-09-08).** T407's Design A result classifies as Inconclusive, not Null (§6.4).
The decision for what follows an Inconclusive classification — and the guardrail it puts in place
for future releases — is recorded as a dated successor block in
`docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 (immediately after the frozen decision-rule
block) and in `docs/decisions/ADR-004-tb-inconclusive-guardrail-demotion.md`. This document is not
re-opened or re-classified by that decision; see those two artifacts for the reasoning, not
restated here.
