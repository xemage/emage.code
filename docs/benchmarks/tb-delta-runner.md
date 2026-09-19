# `scripts/tb-delta.sh` — two-arm Terminal-Bench delta runner + budget guard

**Refs:** T419 (primary), T408 (budget guard, implemented alongside per plan-035's own
sequencing note). Based on `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.2.1, `docs/benchmarks/tb-subset.json`
(T418, frozen), `docs/checkpoints/checkpoint-017-t417-harbor-oracle-smoke-complete.md`.

This document is the load-bearing audit trail for T419's non-negotiable acceptance criterion:
*"the two arms must differ ONLY in whether the emage.code projection is applied — nothing
else."* A future reader who wants to verify that claim without re-deriving the research should
be able to do so from this file alone, plus `scripts/tb-delta.sh` and `scripts/tb_delta_agent.py`.

## What the two arms are

| | Arm A (control) | Arm B (treatment) |
|---|---|---|
| Harbor `--agent` value | `claude-code` (Harbor built-in, unmodified) | `scripts.tb_delta_agent:EmageCodeClaudeCode` (custom import path) |
| Model | same (`-m`, shared flag array) | same |
| Dataset / task selection / timeouts / resources / `-k` | same (shared flag array) | same |
| Workspace | bare task container | emage.code projection (`.claude/`, `.mcp.json`) copied into `/app` before the agent runs |

`score(B) − score(A)` is intended to isolate emage.code's contribution, per plan-035 §2.2.1.

## The mechanism: why a custom agent subclass, not Harbor's `--skill`/`--mcp-config` flags

Harbor 0.21.0 (the version installed and verified working in this repo per T417/T418) does
expose two supported, CLI-level mechanisms for injecting external content into the stock
`claude-code` agent without subclassing anything:

- `--skill`/`--skills <path>` — resolves local directories (or git sources) containing
  `SKILL.md` files, uploads them via `BaseEnvironment.upload_dir` to `/harbor/skills` inside the
  container, and the built-in `ClaudeCode` agent's own `setup()` copies them into
  `$CLAUDE_CONFIG_DIR/skills/` (`harbor/agents/installed/claude_code.py`,
  `_build_register_skills_command`).
- `--mcp-config <path>` — accepts a Claude-style `.mcp.json` and writes it to
  `$CLAUDE_CONFIG_DIR/.claude.json` as user-scoped MCP servers (same file,
  `_build_register_mcp_servers_command`).

Both were considered and would have worked for exactly two of the projection's five parts
(Claude Code Skills, MCP servers). Neither, nor anything else in Harbor's CLI surface
(confirmed by reading the full `harbor run --help` option tree and the installed
`harbor.cli.jobs` module), has a mechanism for injecting **project-scoped** Claude Code
features: subagents (`.claude/agents/*.md`), slash commands (`.claude/commands/*.md`), or
path-scoped rules (`.claude/rules/*.md`). Those are discovered by the `claude` CLI itself from
the task workspace directory (Terminal-Bench's `WORKDIR /app`, confirmed for every task
Dockerfile in the local cache, e.g.
`~/.cache/harbor/tasks/packages/terminal-bench/*/environment/Dockerfile`), not from
`$CLAUDE_CONFIG_DIR` (which Harbor's `ClaudeCode.run()` redirects to a logs-capturing path
anyway, unrelated to project-scoped discovery).

Harbor's own documented mechanism for this case — cited by plan-035 §2.2.1 itself — is agent
subclassing: *"Custom agents subclass `BaseInstalledAgent` or `BaseAgent`, or are passed via
`--agent-import-path` / `--agent module.path:ClassName`."* This was verified directly against
the installed Harbor 0.21.0 source (not assumed from training data, mirroring T417's own
research practice), specifically:

- `harbor/agents/base.py::BaseAgent` — the abstract base every agent (built-in or custom)
  implements (`setup()`, `run()`).
- `harbor/agents/installed/base.py::BaseInstalledAgent` — the base `ClaudeCode` itself extends;
  its `setup()` runs `install()` then returns, and is a normal Python method any subclass can
  extend with `super().setup(environment)` plus its own logic.
- `harbor/agents/installed/claude_code.py::ClaudeCode` — the actual stock `claude-code` agent;
  its `run()` (the real `claude --print --output-format=stream-json ...` invocation, CLI flags,
  model resolution, env-var handling) is untouched by our subclass.
- `harbor/environments/base.py::BaseEnvironment.upload_dir` / `upload_file` — the primitive
  Harbor's own skill-injection path uses internally
  (`harbor/trial/trial.py::_upload_injected_skills`); available to any agent's `setup()`, not
  gated behind the skill-injection CLI flow.

`scripts/tb_delta_agent.py::EmageCodeClaudeCode` is a **~15-line, single-method override**:
`setup()` calls `super().setup(environment)` (unchanged install/version-detection behavior),
then `environment.upload_dir(<repo>/.claude, "/app/.claude")` and
`environment.upload_file(<repo>/.mcp.json, "/app/.mcp.json")`. `run()` is not overridden at all
— it is inherited byte-for-byte from `ClaudeCode`. The task's own `environment/Dockerfile` is
never read or modified by this module; only files are added to the workspace *after* the
container is already built from the task's own unmodified image.

This design has a useful property for the config-diff proof (below): the *only* CLI-visible
difference between the two arms' `harbor run` invocations is the `--agent` value itself.

## The config-diff proof (criterion 2)

`scripts/tb-delta.sh` runs `harbor run ... --print-config` for both arms with **the same shared
flag array** (`COMMON_FLAGS`, built once, used verbatim for both arms except `-a`), then
flattens both resulting JSON documents and diffs every field. The only field allowed to differ
is `agents[0].name` (`claude-code` vs. the custom import path) — anything else is treated as a
runner defect and the script aborts loudly (exit 1) before touching Docker.

This runs on **every invocation**, including a `--config-only` mode that performs step 2 and
exits without running Docker at all (no cost, useful for CI/dry-run verification):

```
$ scripts/tb-delta.sh --config-only -l 1
...
{
  "clean": true,
  "all_diffs": [
    {
      "field": "agents[0].name",
      "arm_a": "claude-code",
      "arm_b": "scripts.tb_delta_agent:EmageCodeClaudeCode"
    }
  ],
  "unexpected_diffs": [],
  ...
}
```

The diff artifact is also written to `docs/benchmarks/scorecards/.runs/<run-id>/config-diff.json`
on every real run, alongside the raw `--print-config` dumps for both arms
(`config-arm-a.json`, `config-arm-b.json`) — an independent reviewer can re-run
`--config-only` at any time and get the identical result without needing to trust this
document's prose claim.

**Open finding, noted rather than hidden:** `harbor run --print-config` only prints
explicitly-set, non-default fields (confirmed empirically — a minimal invocation prints only
`agents` and `datasets`, not the full resolved `JobConfig` including every timeout/resource
default). Because `scripts/tb-delta.sh` builds `COMMON_FLAGS` once and passes it verbatim to
both arms, every field either arm sets explicitly is guaranteed identical by construction, not
merely by the diff catching a mismatch after the fact — the diff is a second, independent check
on top of that construction, not the sole guarantee.

## Open finding: no `--seed` flag

Harbor 0.21.0's `harbor run` CLI has no `--seed`/`-s` option — confirmed by reading the full
`harbor run --help` option tree (all six panels: Config, Job Settings, Agent, Environment,
Verifier, Dataset/Integrations/Harbor Hub). Plan-035 §2.2.1's arm table lists "Seed, `-k`,
concurrency" as a same-across-arms dimension; `-k` and concurrency (`-n`) are real, controllable
flags and are set identically for both arms via `COMMON_FLAGS`. Seed is not independently
controllable in this Harbor version, so it cannot differ *or* be forced identical by this
script's design — it is whatever Harbor/the underlying model API do by default, applied equally
to both arms since neither arm's invocation sets one. Classified `type: unclear_requirements`,
`severity: minor` per task-T419.md's Blocker Protocol — reported here, not treated as a runner
defect, since there is no flag to omit or misuse.

## Model selection (T408)

`claude-code`'s model is set via `-m <name>`, which `ClaudeCode.run()` resolves into
`ANTHROPIC_MODEL` (confirmed in `harbor/agents/installed/claude_code.py::run()` — the agent
strips a `provider/` prefix if present and passes the bare model id to the `claude` CLI's
environment). `scripts/tb-delta.sh` defaults to an **economy** model for iteration and requires
an explicit `--model-tier frontier` (or `--model <name>`) to opt into a frontier model, per
T408's acceptance criteria:

| Tier | Default model | Override |
|---|---|---|
| `economy` (default) | `claude-haiku-4-5-20251001` (env override: `TB_DELTA_ECONOMY_MODEL`) | `--model <name>` |
| `frontier` (explicit opt-in via `--model-tier frontier`) | `claude-sonnet-4-5-20250929` (env override: `TB_DELTA_FRONTIER_MODEL`) | `--model <name>` |

**Correction (2026-08-13, re-verification pass):** the economy default originally shipped in this
task as `claude-3-5-haiku-20241022`. A real end-to-end smoke test against that default failed
*both* arms' single trial with `NonZeroAgentExitCodeError` (`api_error_status: 404`, *"There's an
issue with the selected model (claude-3-5-haiku-20241022). It may not exist or you may not have
access to it."*) — an infrastructure defect, not a task-level failure. Independently confirmed via
`GET https://api.anthropic.com/v1/models` (`anthropic-version: 2023-06-01`, the host's own working
`ANTHROPIC_API_KEY` — ruling out a key problem) that `claude-3-5-haiku-20241022` is absent from
the live model catalog entirely; no `claude-3-5-haiku-*` id is listed at all. The catalog at
re-verification time was: `claude-opus-5`, `claude-sonnet-5`, `claude-fable-5`, `claude-opus-4-8`,
`claude-opus-4-7`, `claude-sonnet-4-6`, `claude-opus-4-6`, `claude-opus-4-5-20251101`,
`claude-haiku-4-5-20251001`, `claude-sonnet-4-5-20250929`. `claude-haiku-4-5-20251001` ("Claude
Haiku 4.5") is the cheapest/economy-tier model actually present and is now the default.
`claude-sonnet-4-5-20250929` (the frontier default) was already present in the catalog and
required no change. Re-check `GET /v1/models` before assuming this stays correct indefinitely —
model catalogs change over time.

Frontier-tier, full-subset (`k>=3`, all 25 tasks) release-baseline runs are **T407's job, not
this script's** — see task-T419.md's scope boundary. `tb-delta.sh` can be pointed at the
frontier tier for a small run, but nothing about this script schedules or authorizes a T407-scale
measurement.

## Budget guard (T408)

`scripts/tb-delta.sh` runs a **real** pre-flight probe before committing to the full plan:

1. Arm A's first task, `-k 1`, `-n 1` (i.e. exactly one real trial) — this is "a small number of
   completed task-runs" per task-T408.md, not a simulation.
2. Measures its actual wall-clock elapsed time.
3. Extrapolates: `projected_total = probe_elapsed + probe_elapsed * (total_trials_planned - 1)`,
   where `total_trials_planned = 2 (arms) * k * n_tasks`.
4. If `projected_total > --max-budget-seconds` (default 1800s / 30 min, env override
   `TB_DELTA_MAX_BUDGET_SECONDS`), the script **aborts immediately** (exit code 2) — Arm A's
   remaining trials and all of Arm B never run. If not, the script proceeds to run Arm A and Arm
   B to completion.

The extrapolation is intentionally crude (linear scaling from a single real data point) — this
is a hard safety cap for a shared host, not a statistical estimator. The full projection
(probe task, elapsed seconds, trials planned/remaining, cap, and the abort decision) is written
to `docs/benchmarks/scorecards/.runs/<run-id>/budget-guard.json` on every invocation, whether or
not it aborts.

### Demonstrated abort (criterion 3)

Run with an artificially low cap (fresh reproduction, 2026-08-13, RUN_ID `20260813T193832Z`, using
the corrected economy model above):

```
$ scripts/tb-delta.sh -k 1 -t overfull-hbox --max-budget-seconds 5
...
[tb-delta 19:38:33] Budget guard: running Arm A's first task as a real probe (1 task, k=1)...
[tb-delta 19:51:00] Probe elapsed: 747s. Projected total (extrapolated): 1494s. Cap: 5s.

BUDGET GUARD ABORT (T408): projected total 1494s exceeds
the 5s cap after extrapolating from a real
747s probe run. Aborting before running the rest of the
plan (Arm A's remaining trials and all of Arm B never ran). See
.../docs/benchmarks/scorecards/.runs/20260813T193832Z/budget-guard.json for the full projection.
$ echo $?
2
```

`docs/benchmarks/scorecards/.runs/20260813T193832Z/budget-guard.json` (written by this
invocation) confirms the same numbers on disk:

```json
{
  "probe_elapsed_seconds": 747,
  "probe_task": "overfull-hbox",
  "total_trials_planned": 2,
  "remaining_trials_after_probe": 1,
  "projected_total_seconds": 1494,
  "max_budget_seconds": 5,
  "aborted": true
}
```

The probe executed for real — a genuine `overfull-hbox` trial that ran the agent to completion
(747s wall-clock, `verifier_result.rewards.reward: 0.0`, `exception_info: null` — the task simply
didn't pass on its own merits, not an infra error); the guard then correctly computed a 1494s
projection against the artificial 5s cap and aborted (exit code 2) — Arm A's "full" run and all of
Arm B's run never started. This is real, not simulated: no `result.json` / scorecard was produced
for this RUN_ID (only `docs/benchmarks/scorecards/tb-delta-scorecard-20260813T190348Z.json`
exists, from the separate successful smoke-test run below — none for `20260813T193832Z`), and
`jobs/tb-delta-20260813T193832Z-probe/` on disk contains exactly one trial directory
(`overfull-hbox__KdSYvxJ`), not the full two-trial plan.

(An earlier, no-longer-current version of this section described a prior abort attempt at
`15:20–15:26 UTC` with a 385s probe. That run predated the economy-model fix above and its
on-disk artifacts did not survive an interrupted session — it is not used as evidence here. The
transcript above is a fresh, independently-verified reproduction against the corrected default.)

## Real smoke test (criterion 5)

A cheap, real, non-simulated smoke test (`-k 1 -t overfull-hbox`, default `--max-budget-seconds
1800`, `--skip-guard` to avoid a redundant third probe trial of the same task — the guard itself
is demonstrated separately above) completed successfully end-to-end on 2026-08-13, RUN_ID
`20260813T190348Z`:

| Arm | Agent | Trial | Reward | Elapsed | Cost (USD) | Infra error? |
|---|---|---|---|---|---|---|
| A (control) | `claude-code` | `overfull-hbox__SkpSnkR` | 1.0 | 753.6s | 0.257 | none |
| B (treatment) | `scripts.tb_delta_agent:EmageCodeClaudeCode` | `overfull-hbox__4e84c4R` | 0.0 | 1181.9s | 0.981 | none |

Both trials' `result.json` show `exception_info: null`; both agent transcripts end with a
`"subtype":"success"` system event and `"permission_denials":[]`. Arm B's reward of 0.0 is a
legitimate Terminal-Bench task-level outcome (the agent did not solve `overfull-hbox`
correctly under the emage.code projection on this single k=1 trial) — not an infrastructure
failure, and not itself evidence of anything at k=1 (see the scorecard's own `delta.note` and
`spread.note` on why a single-trial delta/spread is not a result to interpret; that is T407's
job at k>=3). The full scorecard is at
`docs/benchmarks/scorecards/tb-delta-scorecard-20260813T190348Z.json`.

**Arm B's `.claude/settings.json` trust warning, checked directly:** Arm B's agent transcript
(`jobs/tb-delta-20260813T190348Z-arm-B/overfull-hbox__4e84c4R/agent/claude-code.txt`) does emit
*"Ignoring 36 permissions.allow entries from .claude/settings.json: this workspace has not been
trusted..."* once, at session init. Checked whether this actually blocked anything: the same
transcript's terminal event is `"subtype":"success"` and `"permission_denials":[]` throughout —
`--permission-mode=bypassPermissions` (set on every `harbor run` invocation via `COMMON_FLAGS`,
confirmed in the exception traceback's own command line) grants tool use unconditionally at the
CLI level regardless of the untrusted-workspace state, so the ignored allow-list entries are
redundant with, not blocking relative to, the bypass flag. This warning is confirmed **benign**:
informational only, does not block Arm B's agent from doing real work (1181.9s of real tool use
producing a real, non-zero-cost trial).

## Operational finding: agent-setup timeouts under host contention (historical)

An earlier, interrupted validation session recorded an `AgentSetupTimeoutError` on this host —
Harbor's default 360s agent-setup timeout was reportedly insufficient for the `claude` CLI's
fresh `npm`/`curl` install (`ClaudeCode.install()`) to complete inside the container under host
contention (see `docs/benchmarks/environment.md` for this host's documented resource-contention
history — the same host T417 hit a Docker-daemon-unreachable blocker on). This did **not**
reproduce during the fresh re-verification runs above: all three real trials (the smoke test's
two arms and the abort demo's probe) completed their agent setup and ran to real completion
without hitting this timeout. This is **unrelated to the projection or to which arm is running**
either way — both arms install the `claude` CLI identically (Arm B's `install()` is inherited,
untouched) — so it remains a host/timeout tuning finding, not a threat to the config-diff proof.

`scripts/tb-delta.sh` still sets `--agent-setup-timeout-multiplier 3.0` by default (env override:
`TB_DELTA_AGENT_SETUP_TIMEOUT_MULTIPLIER`), applied identically to both arms via
`COMMON_FLAGS`/`PROBE_COMMON_FLAGS`, as a conservative safety margin for a shared/contended host —
kept even though it was not strictly needed to pass the fresh re-verification runs above.

## Invocation

Preconditions:
- A Harbor 0.21.0+ install on `PATH` (see `docs/benchmarks/environment.md` for the venv-based
  install method verified working in this repo; the system Python on this host rejects
  `pip install`, PEP 668).
- `ANTHROPIC_API_KEY` (or `CLAUDE_CODE_OAUTH_TOKEN`) set in the environment `harbor run` is
  invoked from — `ClaudeCode` reads it from the host process's environment and passes it into
  the container (`harbor/agents/installed/claude_code.py::run()`).
- Run from the repo root (or anywhere; the script resolves paths relative to its own location)
  with `docs/benchmarks/tb-subset.json` present (T418, frozen).

```
# Cheapest possible smoke test (this task's own validation used
# -t overfull-hbox --skip-guard to avoid a redundant third probe trial of the
# same task; the guard is validated separately, see above):
scripts/tb-delta.sh -k 1 -l 1 --max-budget-seconds 1800

# Prove the budget guard aborts (artificially low cap, no scorecard produced):
scripts/tb-delta.sh -k 1 -l 1 --max-budget-seconds 5

# Config-diff proof only, no Docker, no cost:
scripts/tb-delta.sh --config-only -l 2

# A named task instead of the subset's first N:
scripts/tb-delta.sh -k 1 -t overfull-hbox --max-budget-seconds 1800

# Frontier-tier override (NOT authorized at scale by this task — see scope boundary):
scripts/tb-delta.sh --model-tier frontier -k 1 -l 1 --max-budget-seconds 1800
```

Full flag reference: `scripts/tb-delta.sh --help`.

## Scorecard JSON schema

`scripts/tb-delta.sh` writes `docs/benchmarks/scorecards/tb-delta-scorecard-<run-id>.json` on
every successfully-completed run (not on a budget-guard abort or a config-diff failure). This
is a **self-documented interim schema**, defined ahead of `scripts/scorecard.py` (T413, Layer 1,
not yet built at authoring time), which is meant to share a common scorecard format per
plan-035. **A reconciliation pass against T413's actual shape is expected once it lands** — see
this file's "Follow-up" section below; this is tracked, not silently absorbed.

Top-level fields:

| Field | Meaning |
|---|---|
| `schema_version` | `"tb-delta-scorecard-v1"` |
| `schema_note` | Self-documentation string, repeats this reconciliation note inline |
| `generated_at` | ISO-8601 UTC timestamp |
| `runner` | `"scripts/tb-delta.sh"` |
| `dataset` | `"terminal-bench/terminal-bench-2"` |
| `subset_ref` | `"docs/benchmarks/tb-subset.json"` |
| `subset_frozen_at` | The subset's own `frozen_at` date (T418) |
| `k` | Attempts per task per arm (Harbor's `-k`) |
| `model` | `{name, tier}` |
| `arms.A` / `arms.B` | Per-arm result block (see below) |
| `delta.mean_reward_b_minus_a` | `score(B) - score(A)`, or `null` if either arm has no rewards |
| `delta.note` | Interpretation pointer (plan-035 §2.2.1 / §2.4 null-delta block) |
| `spread.arm_a_stdev` / `spread.arm_b_stdev` | Population stdev of per-trial rewards within each arm; **0.0 at k=1 by definition, not a meaningful variance measurement** — the field exists per criterion 1 even when not yet meaningful |
| `max_budget_seconds` | The cap this run was executed under |
| `run_artifacts_dir` | Path to this run's `config-diff.json`, `budget-guard.json`, and raw `--print-config`/`harbor run` logs |

Per-arm block (`arms.A` / `arms.B`):

| Field | Meaning |
|---|---|
| `agent` | The `--agent` value used |
| `job_dir` | Harbor's own job output directory |
| `job_summary_stats` | Harbor's own job-level `stats` block (n_completed/errored trials, etc.) verbatim |
| `n_trials` | Trial-level `result.json` files found under `job_dir` |
| `n_trials_with_reward` | Of those, how many had a parseable reward |
| `errored_trials` | `[{trial_name, exception}]` for any trial with `exception_info` set |
| `rewards` | Raw per-trial reward list |
| `mean_reward` | `null` if no trial produced a reward |
| `stdev_reward` | Population stdev; `0.0` at `n<=1` |
| `elapsed_seconds_per_trial` | Per-trial wall-clock durations |
| `cost_usd_total` | Summed `agent_result.cost_usd` across trials, `null` if never reported |

## Follow-up (tracked, not blocking)

- **T413 reconciliation** (`type: dependency`, `severity: minor`): once `scripts/scorecard.py`
  (Layer 1) lands with its own scorecard shape, reconcile this schema against it. Expected to be
  a field-renaming/wrapping pass, not a redesign, per this task's brief.
- **Seed control**: if a future Harbor version adds a `--seed` flag, `scripts/tb-delta.sh` should
  set it identically for both arms via `COMMON_FLAGS` (trivial addition to the existing
  mechanism) and this doc's "Open finding: no `--seed` flag" section should be updated or
  removed.
