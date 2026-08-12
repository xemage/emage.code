# Task T417 — Install Harbor; verify with the oracle smoke run

**ID:** T417
**Owner:** devops-engineer
**Status:** pending
**Priority:** P1
**Depends on:** — (only Docker; independent of Phase 0's T400–T406 batch)
**Created:** 2026-08-12
**Completed:** —
**Based on:** docs/plans/plan-035-roadmap-v7-ground-up.md (Phase 1, §2.4, "Layer 2 — Terminal-Bench
delta harness" table; pulled forward into Phase 0 execution per §2.9's Week 1 guidance, since it
depends only on Docker and de-risks the measurement layer early)

This brief is self-contained.

## Scope boundary — read this first
This task installs Harbor and proves the environment works via the built-in **oracle** solver —
it does **not** invoke any agent-under-test (no `claude-code`, `codex`, or `gemini-cli` run). It is
therefore explicitly **not** blocked by the two open questions in `plan-035`'s Approval section
(which agent is Arm A; what a null delta means) — those only gate T418–T41C (the actual two-arm
delta measurement), which remain out of scope for this run. **Do not proceed to T418 or beyond.**
If at any point completing this task would require picking an agent-under-test or interpreting a
delta score, stop — that's out of scope, not part of T417.

## Objective
Install Harbor (the official Terminal-Bench harness), confirm Docker is available and running, and
run the oracle smoke test to prove the local environment is correctly configured before anything
in Phase 1 depends on it. Record Harbor version, Docker version, and host resources in
`docs/benchmarks/environment.md`.

## Confirmed current mechanics (verified via live doc lookup at brief-authoring time — re-confirm
at execution time in case the tooling has changed)
- Install: `pip install harbor` (PyPI package `harbor`, published by the `harbor-framework`
  project — <https://pypi.org/project/harbor/>). Docker must be installed and the daemon running
  before invoking `harbor run`.
- Oracle smoke run, small/cheap form (recommended first pass, per Harbor's own docs):
  `harbor run -d terminal-bench/terminal-bench-2-1 -a oracle -l 5` — runs the oracle solutions on
  the first 5 tasks only (fast, cheap, low disk/network footprint; good first signal).
- Full oracle run (what the plan literally specifies): `harbor run -d terminal-bench/
  terminal-bench-2 -a oracle` — runs the oracle solutions across the entire dataset (89 tasks per
  `plan-035` §2.2.1's cited count). This is the acceptance bar the plan sets ("Harbor oracle run
  passes 100% on the pinned subset" — though note the *subset* itself isn't pinned until T418,
  which is out of scope here; for T417 "100%" means 100% of whatever you actually ran).
- Sources consulted: <https://pypi.org/project/harbor/>, <https://www.harborframework.com/docs/
  tutorials/running-terminal-bench>, <https://www.tbench.ai/docs/run-terminal-bench-2-1>. If any
  of these has materially changed by execution time (command syntax, package name), that's not a
  blocker — just follow the current docs and note the discrepancy in your completion report.

## Recommended execution order (resource-aware — do not skip straight to the full run)
1. `pip install harbor` (or `pip install --user harbor` / a virtualenv, your call — note which in
   your report). Confirm with `harbor --version` or equivalent.
2. Confirm Docker: `docker --version`, `docker ps` (daemon reachable).
3. Run the **5-task** oracle smoke (`-l 5`) first. This is cheap and fast — if it doesn't pass
   100%, the environment is wrong and there is no point proceeding to the full run (per the plan's
   own instruction: "a non-100% oracle pass means the environment is wrong — stop and fix before
   any measurement"). Debug and fix here before scaling up.
4. Once the 5-task smoke is 100% green, run the **full** `terminal-bench-2` oracle set as the
   plan's literal acceptance bar requires. **Budget-conscious note:** this will build/pull
   multiple task-specific Docker images and can be slow and consume significant disk (each task is
   an isolated container environment). If the full run appears likely to exceed a reasonable time
   or disk budget (use your judgment; there's no hard number given in the plan for this
   non-measurement smoke run, unlike T41B's later hard cap for the two-arm delta runner), it is
   acceptable to stop after a documented larger-but-partial run (e.g. `-l 25`, roughly the T418
   subset size mentioned elsewhere in the plan) and report the full-set run as a follow-up
   recommendation rather than force it to completion — this is a `type: technical`,
   `severity: minor` note to include in your completion report, not a silent scope-down.

## Inputs
- Docker (confirmed available in this environment: `docker --version` → 29.6.2 at
  brief-authoring time, daemon reachable)
- No repo inputs beyond `docs/benchmarks/` (directory likely doesn't exist yet — create it)

## Expected outputs
- `docs/benchmarks/environment.md` — new file recording:
  - Harbor version (`harbor --version` output or equivalent)
  - Docker version (`docker --version`)
  - Host resources: CPU core count, total RAM, available disk space at time of run (e.g. `nproc`,
    `free -h`, `df -h` output relevant to the Docker storage path)
  - The exact command(s) run (5-task smoke, and full run if completed)
  - Full pass/fail result: how many tasks passed oracle, how many failed (should be 100% pass; if
    not, document exactly which task(s) failed and why, and treat that as a blocker per below —
    do not report success if the oracle didn't pass 100%)
  - Date of the run
- No other repo files should need to change for this task — it's a pure environment-verification
  exercise plus a new doc recording the result.

## Acceptance criteria
1. Harbor installed and its version recorded.
2. Docker version and reachability recorded.
3. Host resources recorded.
4. Oracle smoke run(s) actually executed (not simulated/assumed) — real command output captured.
5. 100% oracle pass on whatever scope was actually run (5-task minimum; full-set preferred per the
   plan's literal bar, with the resource-aware fallback above if the full set proves impractical
   in this session).
6. `docs/benchmarks/environment.md` created with all of the above.
7. If the oracle does NOT pass 100% on any scope attempted, this is a blocker — do not report
   completion; report the specific failure per the Blocker Protocol below instead.

## Blocker protocol
- Docker unavailable or daemon unreachable → `type: external`, `severity: critical` — this
  environment was confirmed to have Docker at brief-authoring time; if that's no longer true,
  escalate immediately rather than attempting a workaround.
- `pip install harbor` fails (package not found, dependency conflict, network blocked) →
  `type: technical`, `severity: major` — include exact error output; try once more with a
  clean virtualenv before escalating (max 2 retries per `AGENTS.md`'s Blocker Protocol).
- Oracle smoke run doesn't pass 100% on the 5-task set → `type: technical`, `severity: major` —
  per the plan's own instruction, this means "the environment is wrong," not a task-content
  problem; do not proceed to the full run, and do not report partial success. Include the exact
  failing task name(s) and error output.
- Full run appears likely to exceed a reasonable time/disk budget → not a blocker per se (see
  "Recommended execution order" step 4 above) — document the fallback taken and report as a note,
  not an escalation, unless even the fallback size proves infeasible, in which case escalate as
  `type: technical`, `severity: minor`.

## Git workflow
This task has no dependency on the T400–T406 Phase 0 batch and should NOT share its branch — it's
an independent, unrelated concern (benchmarking infra vs. doc-truth/release-gate work), matching
`git-workflow.md`'s guidance to only group work that's part of the same logical unit.
1. Create branch `feature/T417-harbor-install-oracle-smoke` from the current tip of `develop`.
2. Do the install/run/record work described above.
3. Commit with a Conventional Commit message, e.g.:
   ```
   feat(benchmarks): install Harbor, record oracle smoke-run environment

   Installs Harbor (pip install harbor), confirms Docker availability,
   and runs the terminal-bench-2 oracle solutions as a smoke test
   before any Terminal-Bench delta measurement depends on this
   environment. Records Harbor/Docker versions and host resources in
   docs/benchmarks/environment.md, per plan-035 Phase 1 (pulled
   forward per Sec 2.9 Week 1 guidance).

   Refs T417
   ```
4. Do NOT push, do NOT open a merge request, do NOT merge — report the branch name, commit SHA,
   and full oracle-run output back to the orchestrator, who will independently review before any
   push/MR (same pattern as the T400 brief's instruction, applied to this independent branch).

## Constraints
- Token budget: ≤20k tokens (this task budget draws from Phase 1's 200k budget, pulled forward per
  §2.9 — track separately from Phase 0's 100k budget in the checkpoint).
- File ownership: `docs/benchmarks/environment.md` (new) only. Do not create or touch any other
  file under `docs/benchmarks/` (that's T413/T418/T419's later scope, out of bounds here) — do not
  create `docs/benchmarks/tb-subset.json` or any scorecard file, even if it would be convenient;
  those belong to explicitly out-of-scope later tasks.
- Do not invoke any agent-under-test (`claude-code`/`codex`/`gemini-cli`) via Harbor — oracle only.
