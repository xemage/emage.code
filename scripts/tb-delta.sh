#!/usr/bin/env bash
# scripts/tb-delta.sh -- two-arm Terminal-Bench delta runner + budget guard.
# Refs: T419 (primary), T408 (budget guard). Based on:
#   docs/plans/plan-035-roadmap-v7-ground-up.md §2.2.1
#   docs/benchmarks/tb-subset.json (T418, frozen 25-task subset)
#   docs/checkpoints/checkpoint-017-t417-harbor-oracle-smoke-complete.md
#
# See docs/benchmarks/tb-delta-runner.md for full documentation: invocation,
# budget-guard configuration, and -- load-bearing -- how the "projection
# applied vs. not" mechanism actually works and how to audit it.
#
# Summary of what this script does:
#   1. Resolves a task list from docs/benchmarks/tb-subset.json (frozen, T418).
#   2. Dumps BOTH arms' resolved `harbor run --print-config` JSON and diffs
#      them programmatically. Fails loudly if anything besides the expected
#      `agents[].name` field (Arm A: `claude-code`, Arm B: the custom
#      scripts/tb_delta_agent.py import path) differs. This is the proof for
#      T419 acceptance criterion 2 -- it runs on every invocation, not just
#      once by hand.
#   3. Budget guard (T408): runs Arm A's first task as a real probe, measures
#      wall-clock elapsed time, extrapolates the full remaining plan (Arm A's
#      remaining k*n_tasks-1 trials + all of Arm B's k*n_tasks trials), and
#      aborts BEFORE running anything further if the projection exceeds
#      --max-budget-seconds. Economy model is the default; --model-tier
#      frontier requires an explicit flag (T408 acceptance).
#   4. If the guard passes, completes Arm A, then runs Arm B (same model,
#      dataset slice, timeouts, resources, -k -- only the projection differs).
#   5. Parses both arms' `result.json`, computes delta/spread, and writes a
#      scorecard JSON (schema documented in emit_scorecard() below; a T413
#      reconciliation pass is expected once scripts/scorecard.py lands --
#      see docs/benchmarks/tb-delta-runner.md).
#
# Exit codes: 0 = full run completed, scorecard written.
#             2 = budget guard aborted (by design -- see criterion 3).
#             1 = any other failure (config-diff mismatch, harbor error, etc).

set -euo pipefail

# ---------------------------------------------------------------------------
# Paths and defaults
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SUBSET_JSON="$REPO_ROOT/docs/benchmarks/tb-subset.json"
DATASET="terminal-bench/terminal-bench-2"

ARM_A_AGENT="claude-code"
ARM_B_AGENT="scripts.tb_delta_agent:EmageCodeClaudeCode"

# T408: economy model is the default; frontier requires --model-tier frontier
# (an explicit override), reserved for release-baseline runs (T407, not this
# script's job to run at scale -- see task-T419.md's scope boundary).
# claude-3-5-haiku-20241022 (this default's original value) was found to be
# absent from the live Anthropic model catalog during this task's own
# re-verification (2026-08-13; confirmed via `GET /v1/models` against the
# host's own key) -- it 404s ("model may not exist or you may not have
# access to it") rather than running. claude-haiku-4-5-20251001 ("Claude
# Haiku 4.5") is the cheapest/economy-tier model actually present in the
# current catalog; re-check `GET /v1/models` before assuming this stays
# correct indefinitely (see docs/benchmarks/tb-delta-runner.md's model
# table).
ECONOMY_MODEL="${TB_DELTA_ECONOMY_MODEL:-claude-haiku-4-5-20251001}"
FRONTIER_MODEL="${TB_DELTA_FRONTIER_MODEL:-claude-sonnet-4-5-20250929}"
MODEL_TIER="economy"
MODEL_OVERRIDE=""

K=1
N_TASKS=1
EXPLICIT_TASKS=()
MAX_BUDGET_SECONDS="${TB_DELTA_MAX_BUDGET_SECONDS:-1800}"
N_CONCURRENT=1
# Empirically needed on this shared host: claude-code's agent-*install* step
# (npm/curl-installing the `claude` CLI fresh inside every container) can
# exceed Harbor's 360s default agent-setup timeout under host contention --
# observed directly during this task's own validation (see
# docs/benchmarks/tb-delta-runner.md's "Operational finding" section). This
# is unrelated to the projection (both arms install the same way) and is
# applied identically to both arms via COMMON_FLAGS below.
AGENT_SETUP_TIMEOUT_MULTIPLIER="${TB_DELTA_AGENT_SETUP_TIMEOUT_MULTIPLIER:-3.0}"
JOBS_DIR="${TB_DELTA_JOBS_DIR:-$REPO_ROOT/jobs}"
SCORECARD_DIR="$REPO_ROOT/docs/benchmarks/scorecards"
SKIP_GUARD=false
CONFIG_ONLY=false

usage() {
  cat <<'EOF'
Usage: scripts/tb-delta.sh [options]

Two-arm Terminal-Bench delta runner (T419) with a built-in budget guard
(T408). Arm A = stock claude-code (Harbor built-in). Arm B = claude-code +
the emage.code .claude/ projection applied to the task workspace. Both arms
run the same model, dataset slice, timeouts, resources, and -k.

Options:
  -k, --n-attempts N        Attempts per task per arm (Harbor's -k). Default: 1.
  -l, --n-tasks N            Number of tasks to sample from the frozen subset
                              (docs/benchmarks/tb-subset.json), in file order.
                              Ignored if --task is given. Default: 1.
  -t, --task NAME             Explicit task name from the subset (repeatable).
                              Overrides --n-tasks task selection.
  --model-tier economy|frontier
                              Model tier (T408). Default: economy. Frontier is
                              an explicit opt-in for release-baseline runs.
  --model NAME                 Override the resolved model name outright
                              (bypasses --model-tier's default lookup).
  --max-budget-seconds N       Hard cap (T408) for total projected wall-clock
                              time across both arms. Default: 1800 (30 min),
                              override via TB_DELTA_MAX_BUDGET_SECONDS.
  --n-concurrent N              Harbor's -n (concurrent trials). Default: 1
                              (deliberately serial on a shared host -- see
                              docs/benchmarks/environment.md's resource
                              history before raising this).
  --jobs-dir PATH               Where Harbor writes its own job directories.
                              Default: <repo-root>/jobs (override via
                              TB_DELTA_JOBS_DIR; not committed).
  --config-only                  Only perform step 2 (config-diff proof); do
                              not run Docker at all. Useful for CI/dry-run
                              verification of the projection-only-difference
                              claim without spending any budget.
  --skip-guard                   Skip the budget-guard pre-flight probe (NOT
                              recommended; documented for the case where the
                              caller has already budgeted externally).
  -h, --help                     Show this help.

Examples:
  # Cheapest possible smoke test (this task's own validation):
  scripts/tb-delta.sh -k 1 -l 1 --max-budget-seconds 1800

  # Prove the budget guard aborts (artificially low cap):
  scripts/tb-delta.sh -k 1 -l 1 --max-budget-seconds 5

  # Config-diff proof only, no Docker, no cost:
  scripts/tb-delta.sh --config-only -l 2

See docs/benchmarks/tb-delta-runner.md for full documentation.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -k|--n-attempts) K="$2"; shift 2 ;;
    -l|--n-tasks) N_TASKS="$2"; shift 2 ;;
    -t|--task) EXPLICIT_TASKS+=("$2"); shift 2 ;;
    --model-tier) MODEL_TIER="$2"; shift 2 ;;
    --model) MODEL_OVERRIDE="$2"; shift 2 ;;
    --max-budget-seconds) MAX_BUDGET_SECONDS="$2"; shift 2 ;;
    --n-concurrent) N_CONCURRENT="$2"; shift 2 ;;
    --jobs-dir) JOBS_DIR="$2"; shift 2 ;;
    --config-only) CONFIG_ONLY=true; shift ;;
    --skip-guard) SKIP_GUARD=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if [[ "$MODEL_TIER" != "economy" && "$MODEL_TIER" != "frontier" ]]; then
  echo "ERROR: --model-tier must be 'economy' or 'frontier', got '$MODEL_TIER'" >&2
  exit 1
fi

if [[ -n "$MODEL_OVERRIDE" ]]; then
  MODEL="$MODEL_OVERRIDE"
elif [[ "$MODEL_TIER" == "frontier" ]]; then
  MODEL="$FRONTIER_MODEL"
else
  MODEL="$ECONOMY_MODEL"
fi

if ! command -v harbor >/dev/null 2>&1; then
  echo "ERROR: 'harbor' not found on PATH. Activate the Harbor venv first" >&2
  echo "       (see docs/benchmarks/environment.md for the install path used" >&2
  echo "       by T417/T418; docs/benchmarks/tb-delta-runner.md for this" >&2
  echo "       script's own preconditions)." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found on PATH (needed for JSON parsing)." >&2
  exit 1
fi

if [[ ! -f "$SUBSET_JSON" ]]; then
  echo "ERROR: frozen subset not found at $SUBSET_JSON (T418 must run first)." >&2
  exit 1
fi

mkdir -p "$JOBS_DIR" "$SCORECARD_DIR"
export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"

RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_OUT_DIR="$SCORECARD_DIR/.runs/$RUN_ID"
mkdir -p "$RUN_OUT_DIR"

log() { echo "[tb-delta $(date -u +%H:%M:%S)] $*"; }

# ---------------------------------------------------------------------------
# Step 1: resolve task list from the frozen subset
# ---------------------------------------------------------------------------
if [[ ${#EXPLICIT_TASKS[@]} -gt 0 ]]; then
  TASKS_JSON="$(printf '%s\n' "${EXPLICIT_TASKS[@]}" | python3 -c '
import json, sys
print(json.dumps([line.strip() for line in sys.stdin if line.strip()]))
')"
else
  TASKS_JSON="$(python3 -c "
import json
with open('$SUBSET_JSON') as f:
    subset = json.load(f)
names = [t['name'] for t in subset['tasks']][:$N_TASKS]
print(json.dumps(names))
")"
fi
mapfile -t TASK_NAMES < <(python3 -c "import json,sys; [print(n) for n in json.loads(sys.argv[1])]" "$TASKS_JSON")
if [[ ${#TASK_NAMES[@]} -eq 0 ]]; then
  echo "ERROR: no tasks resolved (check --n-tasks / --task / $SUBSET_JSON)." >&2
  exit 1
fi
log "Task(s) selected: ${TASK_NAMES[*]}"
log "Model: $MODEL (tier: $MODEL_TIER)  k=$K  n_tasks=${#TASK_NAMES[@]}  max_budget_seconds=$MAX_BUDGET_SECONDS"

INCLUDE_FLAGS=()
for t in "${TASK_NAMES[@]}"; do
  # docs/benchmarks/tb-subset.json (T418) stores bare task names (e.g.
  # "overfull-hbox"); Harbor's dataset registers them dataset-qualified
  # (e.g. "terminal-bench/overfull-hbox") and -i/--include-task-name matches
  # the qualified name exactly unless given a glob -- confirmed against
  # `harbor run --print-config` at authoring time (see
  # docs/benchmarks/tb-delta-runner.md). The "*" prefix bridges the two
  # without needing to touch tb-subset.json's frozen bare-name schema.
  INCLUDE_FLAGS+=(-i "*${t}")
done

# Common flags shared by BOTH arms verbatim -- this is the mechanism that
# guarantees "same model, dataset, timeouts, resources, seed, -k": both arms
# are built from the exact same array plus only the --agent value differs.
# (Harbor 0.21.0 has no --seed flag on `harbor run` -- confirmed against
# `harbor run --help`'s full option surface; see docs/benchmarks/
# tb-delta-runner.md's "Open finding: no --seed flag" section. Neither arm
# sets one, so this axis is trivially identical between arms even though it
# is not independently controllable.)
COMMON_FLAGS=(
  -d "$DATASET"
  "${INCLUDE_FLAGS[@]}"
  -l "${#TASK_NAMES[@]}"
  -k "$K"
  -m "$MODEL"
  -n "$N_CONCURRENT"
  --agent-setup-timeout-multiplier "$AGENT_SETUP_TIMEOUT_MULTIPLIER"
  -y
)

arm_run_config() {
  local agent="$1"
  harbor run -a "$agent" "${COMMON_FLAGS[@]}" --print-config 2>/dev/null
}

# ---------------------------------------------------------------------------
# Step 2: config-diff proof (T419 acceptance criterion 2) -- runs every time.
# ---------------------------------------------------------------------------
log "Dumping resolved Harbor run configs for both arms (--print-config, no Docker)..."
CONFIG_A="$RUN_OUT_DIR/config-arm-a.json"
CONFIG_B="$RUN_OUT_DIR/config-arm-b.json"
arm_run_config "$ARM_A_AGENT" > "$CONFIG_A"
arm_run_config "$ARM_B_AGENT" > "$CONFIG_B"

DIFF_RESULT="$(python3 - "$CONFIG_A" "$CONFIG_B" "$ARM_A_AGENT" "$ARM_B_AGENT" <<'PYEOF'
import json, sys

path_a, path_b, agent_a, agent_b = sys.argv[1:5]
with open(path_a) as f:
    a = json.load(f)
with open(path_b) as f:
    b = json.load(f)

def flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flatten(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out

flat_a = flatten(a)
flat_b = flatten(b)
keys = sorted(set(flat_a) | set(flat_b))

diffs = []
for k in keys:
    va, vb = flat_a.get(k, "<missing>"), flat_b.get(k, "<missing>")
    if va != vb:
        diffs.append((k, va, vb))

# The ONLY field allowed to differ is the agent identity field
# (agents[0].name), which is expected to hold "claude-code" for Arm A and
# the custom import path for Arm B -- that IS the projection difference this
# whole harness exists to isolate. Anything else differing is a runner
# defect per task-T419.md's non-negotiable acceptance criterion 2.
allowed_prefix = "agents[0].name"
unexpected = [d for d in diffs if d[0] != allowed_prefix]

result = {
    "clean": len(unexpected) == 0,
    "all_diffs": [{"field": k, "arm_a": va, "arm_b": vb} for k, va, vb in diffs],
    "unexpected_diffs": [{"field": k, "arm_a": va, "arm_b": vb} for k, va, vb in unexpected],
    "expected_field": allowed_prefix,
    "arm_a_agent": agent_a,
    "arm_b_agent": agent_b,
}
print(json.dumps(result, indent=2))
PYEOF
)"
echo "$DIFF_RESULT" > "$RUN_OUT_DIR/config-diff.json"
echo "$DIFF_RESULT"

CONFIG_DIFF_CLEAN="$(python3 -c "import json,sys; print(json.loads(sys.argv[1])['clean'])" "$DIFF_RESULT")"
if [[ "$CONFIG_DIFF_CLEAN" != "True" ]]; then
  echo "" >&2
  echo "FAIL: the two arms' Harbor run configs differ in more than the" >&2
  echo "projection (see $RUN_OUT_DIR/config-diff.json 'unexpected_diffs')." >&2
  echo "This is a runner defect per task-T419.md's non-negotiable criterion" >&2
  echo "2. Aborting before running anything -- do not proceed on a dirty diff." >&2
  exit 1
fi
log "Config diff clean: only agents[0].name differs between arms (as expected)."

if [[ "$CONFIG_ONLY" == "true" ]]; then
  log "--config-only: stopping here (no Docker run performed)."
  exit 0
fi

# ---------------------------------------------------------------------------
# Step 3: budget guard (T408) -- real probe, then extrapolate, then decide.
# ---------------------------------------------------------------------------
run_arm() {
  # $1 = arm label (A|B), $2 = agent, $3... = extra harbor run flags
  local label="$1" agent="$2"
  shift 2
  local job_name="tb-delta-${RUN_ID}-arm-${label}"
  local before after elapsed
  before="$(date +%s)"
  if ! harbor run -a "$agent" "${COMMON_FLAGS[@]}" \
        --job-name "$job_name" -o "$JOBS_DIR" "$@" \
        > "$RUN_OUT_DIR/arm-${label}.stdout.log" 2>&1; then
    echo "ERROR: harbor run failed for Arm $label (agent=$agent). See:" >&2
    echo "       $RUN_OUT_DIR/arm-${label}.stdout.log" >&2
    return 1
  fi
  after="$(date +%s)"
  elapsed=$((after - before))
  echo "$elapsed" > "$RUN_OUT_DIR/arm-${label}.elapsed_seconds"
  # Job-level result.json (jobs/<job_name>/result.json) only carries summary
  # stats -- trial_results there is always empty. Per-trial detail (rewards,
  # timing, cost) lives one level down at
  # jobs/<job_name>/<task>__<suffix>/result.json (confirmed against a real
  # run's on-disk layout during this task's own validation). Return the JOB
  # DIRECTORY; the scorecard parser globs it for trial-level result.json
  # files itself.
  echo "$JOBS_DIR/$job_name"
}

if [[ "$SKIP_GUARD" == "true" ]]; then
  log "SKIP_GUARD set: skipping the budget-guard probe (not recommended)."
else
  log "Budget guard: running Arm A's first task as a real probe (1 task, k=1)..."
  PROBE_COMMON_FLAGS=("${COMMON_FLAGS[@]}")
  # Probe scope is exactly 1 task, k=1, regardless of the full plan's size --
  # "a small number of completed task-runs" per task-T408.md.
  PROBE_COMMON_FLAGS=(
    -d "$DATASET" -i "*${TASK_NAMES[0]}" -l 1 -k 1 -m "$MODEL" -n 1
    --agent-setup-timeout-multiplier "$AGENT_SETUP_TIMEOUT_MULTIPLIER" -y
  )
  probe_before="$(date +%s)"
  probe_job="tb-delta-${RUN_ID}-probe"
  if ! harbor run -a "$ARM_A_AGENT" "${PROBE_COMMON_FLAGS[@]}" \
        --job-name "$probe_job" -o "$JOBS_DIR" \
        > "$RUN_OUT_DIR/probe.stdout.log" 2>&1; then
    echo "ERROR: budget-guard probe run itself failed. See $RUN_OUT_DIR/probe.stdout.log" >&2
    exit 1
  fi
  probe_after="$(date +%s)"
  probe_elapsed=$((probe_after - probe_before))

  total_trials=$(( 2 * K * ${#TASK_NAMES[@]} ))          # both arms, full plan
  remaining_trials=$(( total_trials - 1 ))                 # probe already ran 1
  projected_remaining=$(( probe_elapsed * remaining_trials ))
  projected_total=$(( probe_elapsed + projected_remaining ))

  cat > "$RUN_OUT_DIR/budget-guard.json" <<EOF
{
  "probe_elapsed_seconds": $probe_elapsed,
  "probe_task": "${TASK_NAMES[0]}",
  "total_trials_planned": $total_trials,
  "remaining_trials_after_probe": $remaining_trials,
  "projected_total_seconds": $projected_total,
  "max_budget_seconds": $MAX_BUDGET_SECONDS,
  "aborted": $([ "$projected_total" -gt "$MAX_BUDGET_SECONDS" ] && echo true || echo false)
}
EOF
  log "Probe elapsed: ${probe_elapsed}s. Projected total (extrapolated): ${projected_total}s. Cap: ${MAX_BUDGET_SECONDS}s."

  if [[ "$projected_total" -gt "$MAX_BUDGET_SECONDS" ]]; then
    echo "" >&2
    echo "BUDGET GUARD ABORT (T408): projected total ${projected_total}s exceeds" >&2
    echo "the ${MAX_BUDGET_SECONDS}s cap after extrapolating from a real" >&2
    echo "${probe_elapsed}s probe run. Aborting before running the rest of the" >&2
    echo "plan (Arm A's remaining trials and all of Arm B never ran). See" >&2
    echo "$RUN_OUT_DIR/budget-guard.json for the full projection." >&2
    exit 2
  fi
  log "Budget guard: projection is within cap. Proceeding."
fi

# ---------------------------------------------------------------------------
# Step 4: run both arms for real (Arm A includes the probe's task; small
# duplication of the probe's single trial is accepted as the cost of a real,
# non-simulated pre-flight measurement -- see docs/benchmarks/
# tb-delta-runner.md's budget-guard section for the tradeoff).
# ---------------------------------------------------------------------------
log "Running Arm A (${ARM_A_AGENT})..."
JOB_DIR_A="$(run_arm A "$ARM_A_AGENT")"
log "Arm A job dir: $JOB_DIR_A"

log "Running Arm B (${ARM_B_AGENT})..."
JOB_DIR_B="$(run_arm B "$ARM_B_AGENT")"
log "Arm B job dir: $JOB_DIR_B"

# ---------------------------------------------------------------------------
# Step 5: parse results, compute delta/spread, emit scorecard.
# ---------------------------------------------------------------------------
SCORECARD_PATH="$SCORECARD_DIR/tb-delta-scorecard-${RUN_ID}.json"
python3 - "$JOB_DIR_A" "$JOB_DIR_B" "$SCORECARD_PATH" "$RUN_OUT_DIR" \
         "$MODEL" "$MODEL_TIER" "$K" "$MAX_BUDGET_SECONDS" "$SUBSET_JSON" \
         "$ARM_A_AGENT" "$ARM_B_AGENT" <<'PYEOF'
import glob, json, os, statistics, sys, datetime

(job_dir_a, job_dir_b, scorecard_path, run_out_dir, model, model_tier,
 k, max_budget_seconds, subset_json_path, agent_a, agent_b) = sys.argv[1:12]


def load_arm(job_dir, agent_name):
    # jobs/<job_name>/result.json is a job-level SUMMARY only -- its
    # `trial_results` is always empty. Per-trial detail (rewards, timing,
    # cost) lives one directory down, at
    # jobs/<job_name>/<task_name>__<suffix>/result.json -- confirmed against
    # a real run's on-disk layout during this task's own validation (see
    # docs/benchmarks/tb-delta-runner.md).
    summary_path = os.path.join(job_dir, "result.json")
    with open(summary_path) as f:
        summary = json.load(f)

    trial_result_paths = sorted(
        glob.glob(os.path.join(job_dir, "*", "result.json"))
    )

    rewards = []
    elapsed_list = []
    cost_total = 0.0
    cost_seen = False
    errored_trials = []
    for trial_path in trial_result_paths:
        with open(trial_path) as f:
            tr = json.load(f)
        vr = tr.get("verifier_result") or {}
        r = vr.get("rewards") or {}
        # Prefer a "reward" key if present; else take the first numeric value.
        if "reward" in r:
            rewards.append(r["reward"])
        elif r:
            rewards.append(next(iter(r.values())))
        if tr.get("exception_info"):
            errored_trials.append(
                {"trial_name": tr.get("trial_name"), "exception": tr["exception_info"]}
            )
        started, finished = tr.get("started_at"), tr.get("finished_at")
        if started and finished:
            try:
                t0 = datetime.datetime.fromisoformat(started.replace("Z", "+00:00"))
                t1 = datetime.datetime.fromisoformat(finished.replace("Z", "+00:00"))
                elapsed_list.append((t1 - t0).total_seconds())
            except ValueError:
                pass
        agent_result = tr.get("agent_result") or {}
        cost = agent_result.get("cost_usd") if agent_result else None
        if cost is not None:
            cost_total += cost
            cost_seen = True

    mean_reward = statistics.fmean(rewards) if rewards else None
    stdev_reward = statistics.pstdev(rewards) if len(rewards) > 1 else 0.0

    return {
        "agent": agent_name,
        "job_dir": job_dir,
        "job_summary_stats": summary.get("stats"),
        "n_trials": len(trial_result_paths),
        "n_trials_with_reward": len(rewards),
        "errored_trials": errored_trials,
        "rewards": rewards,
        "mean_reward": mean_reward,
        "stdev_reward": stdev_reward,
        "elapsed_seconds_per_trial": elapsed_list,
        "cost_usd_total": cost_total if cost_seen else None,
    }


arm_a = load_arm(job_dir_a, agent_a)
arm_b = load_arm(job_dir_b, agent_b)

delta = None
if arm_a["mean_reward"] is not None and arm_b["mean_reward"] is not None:
    delta = arm_b["mean_reward"] - arm_a["mean_reward"]

with open(subset_json_path) as f:
    subset = json.load(f)

scorecard = {
    "schema_version": "tb-delta-scorecard-v1",
    "schema_note": (
        "Self-documented interim schema (T419/T408), defined ahead of "
        "scripts/scorecard.py (T413, Layer 1, not yet built at authoring "
        "time). A reconciliation pass against T413's shape is expected once "
        "it lands -- flagged as type: dependency, severity: minor in "
        "T419's completion report, not silently absorbed. Fields: per-arm "
        "results (arms.A / arms.B), k, model, dataset subset reference "
        "(subset_ref + subset_frozen_at), delta, spread, cost/time "
        "(elapsed_seconds_per_trial / cost_usd_total per arm), timestamp "
        "(generated_at)."
    ),
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "runner": "scripts/tb-delta.sh",
    "dataset": "terminal-bench/terminal-bench-2",
    "subset_ref": "docs/benchmarks/tb-subset.json",
    "subset_frozen_at": subset.get("frozen_at"),
    "k": int(k),
    "model": {"name": model, "tier": model_tier},
    "arms": {"A": arm_a, "B": arm_b},
    "delta": {
        "mean_reward_b_minus_a": delta,
        "note": (
            "score(B) - score(A) per plan-035 §2.2.1. Positive = the "
            "emage.code projection improved outcomes on this run; negative "
            "= regressed; null/near-zero = no measurable effect at this k. "
            "See plan-035 §2.4 Phase 1's registered null-delta "
            "interpretation block for how a null/negative result at full "
            "k>=3 scale (T407, not this task) should be read -- not "
            "applicable at this smoke test's k."
        ),
    },
    "spread": {
        "arm_a_stdev": arm_a["stdev_reward"],
        "arm_b_stdev": arm_b["stdev_reward"],
        "note": (
            "Population stdev of per-trial rewards within each arm. At "
            "k=1 (this smoke test) stdev is trivially 0.0 by definition, "
            "NOT a meaningful measurement of variance -- k>=3 per arm is "
            "required before a spread value should be treated as signal, "
            "per plan-035 §2.2.1 discipline 1 ('Variance')."
        ),
    },
    "max_budget_seconds": int(max_budget_seconds),
    "run_artifacts_dir": run_out_dir,
}

with open(scorecard_path, "w") as f:
    json.dump(scorecard, f, indent=2)

print(json.dumps(scorecard, indent=2))
PYEOF

log "Scorecard written: $SCORECARD_PATH"
log "Done."
