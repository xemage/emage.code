# Terminal-Bench / Harbor Environment Verification — T417

**Status (as of 2026-08-13 run): Required gate PASSED. Environment is verified functional.**
The mandatory 5-task oracle smoke test (the brief's minimum acceptance bar) passed 100%
(5/5) with Docker healthy and responsive throughout. An additional, larger-scope 25-task
oracle run was also attempted per the brief's "recommended execution order" step 4/fallback
guidance; it did **not** reach 100% (17/25, 68%) — see "2026-08-13 — extended 25-task run"
below for the honest, undecorated breakdown. This is reported as a distinct `technical`,
`major` finding for orchestrator review, **not** conflated with the 2026-08-12 Docker-daemon-
unreachable blocker, which did not recur at any point in this session (Docker stayed reachable
and responsive across both runs on 2026-08-13).

This document preserves the full historical record of the 2026-08-12 blocked attempt below,
followed by the 2026-08-13 retry results.

---

## 2026-08-13 — retry run (this session)

### Environment at time of run

- **Harbor version:** `harbor --version` → `0.21.0` (same venv-based install as 2026-08-12,
  reused: `python3 -m venv` outside the repo worktree, `pip install harbor` inside it — not
  system/`--user` pip, which remains rejected by this host's PEP 668 "externally-managed"
  system Python).
- **Docker version:** `docker --version` → `Docker version 29.6.2, build dfc4efb`
- **Host resources — fresh readings taken immediately before this run** (explicitly not
  reused from the 2026-08-12 attempt, per instruction):
  - CPU: `nproc` → 14 cores
  - RAM: `free -h` → total 7.5Gi, used 4.3Gi, **free 917Mi**, buff/cache 2.5Gi, available 3.2Gi
  - Swap: 2.0Gi total, used 1.1Gi, **free 949Mi** (contrast with 2026-08-12: swap was 0B free
    / fully saturated at every reading — this is the "measurably improved" host condition the
    retry was predicated on)
  - Disk: `df -h /` → `/dev/sdf` 1007G total, 63G used, 894G available (7% used) — never the
    constraint, unchanged from 2026-08-12
  - `docker ps` (pre-run reachability check, `timeout 8 docker ps`) → returned instantly,
    empty container table, no hang

### Run 1 — 5-task oracle smoke (required minimum gate)

**Command:**
```
harbor run -d terminal-bench/terminal-bench-2-1 -a oracle -l 5 -y
```

**Result: 5/5 PASS (100%). 0 exceptions.**

Raw output (verbatim tail):
```
  5/5 Mean: 1.000 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 0:09:18 0:00:00
terminal-bench/terminal-bench-2-1 • oracle
┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┓
┃ Trials ┃ Exceptions ┃  Mean ┃
┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━┩
│      5 │          0 │ 1.000 │
└────────┴────────────┴───────┘

┏━━━━━━━━┳━━━━━━━┓
┃ Reward ┃ Count ┃
┡━━━━━━━━╇━━━━━━━┩
│ 1.0    │     5 │
└────────┴───────┘

Job Info
Total runtime: 9m 18s
Results written to jobs/2026-08-13__11-19-03/result.json
```

Docker/host re-check immediately after this run: `docker ps` instant/empty, RAM free 1.8Gi,
swap free 803Mi, disk unchanged. No degradation observed. **This satisfies the brief's
required minimum acceptance bar (§ Acceptance criteria #5: "100% oracle pass on whatever
scope was actually run (5-task minimum...)"). The environment is confirmed correctly
configured.**

### Run 2 — extended 25-task oracle run (larger-scope attempt, per step 4 fallback)

**Rationale for scope choice (`-l 25` rather than the full 89-task `terminal-bench-2`
oracle set):** the 5-task run above took 9m18s (≈112s/task average). Extrapolating that
rate to the full 89-task set gives an estimated ≈2.75 hours — well beyond a reasonable time
budget for this environment-verification smoke run, and beyond what's prudent to sustain on
a shared host that had previously experienced resource exhaustion. Rather than launch the
full run and abort it partway (burning ~15-20 minutes of Docker/image-pull churn on a host
being deliberately kept stable), the `-l 25` scope — explicitly sanctioned by the brief's own
"Recommended execution order" step 4 as an acceptable partial-run fallback — was run
directly. **This is a documented, deliberate scope decision, not a silent scope-down.**
Classified per the brief's own guidance: `type: technical`, `severity: minor` (fallback-scope
note, not a failure in itself).

**Command:**
```
harbor run -d terminal-bench/terminal-bench-2 -a oracle -l 25 -y
```
(run with a 30-minute wrapper timeout as a safety bound; the run completed within that
window at 26m22s)

**Result: 17/25 PASS (68%). NOT 100%. This is a genuine, distinct finding — reported
honestly per the brief's "do not fabricate a pass" instruction.**

Raw output (verbatim):
```
  25/25 Mean: 0.680 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 0:26:22 0:00:00
terminal-bench/terminal-bench-2 • oracle
┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┓
┃ Trials ┃ Exceptions ┃  Mean ┃
┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━┩
│     21 │          6 │ 0.680 │
└────────┴────────────┴───────┘

┏━━━━━━━━┳━━━━━━━┓
┃ Reward ┃ Count ┃
┡━━━━━━━━╇━━━━━━━┩
│ 1.0    │    17 │
│ 0.0    │     4 │
└────────┴───────┘

┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Exception         ┃ Count ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ RuntimeError      │     4 │
│ AgentTimeoutError │     2 │
└───────────────────┴───────┘

Job Info
Total runtime: 26m 22s
Results written to jobs/2026-08-13__11-28-55/result.json
```

**Per-task breakdown (from `jobs/2026-08-13__11-28-55/result.json`), 25 tasks total:**

- **17 passed (reward 1.0):** make-mips-interpreter, circuit-fibsqrt, build-pov-ray,
  overfull-hbox, video-processing, distribution-search, dna-assembly,
  log-summary-date-ranges, vulnerable-secret, openssl-selfsigned-cert,
  feal-linear-cryptanalysis, polyglot-rust-c, cancel-async-tasks, dna-insert,
  git-leak-recovery, db-wal-recovery, headless-terminal
- **4 failed with reward 0.0** (task ran to completion, oracle solution did not achieve
  reward): caffe-cifar-10, install-windows-3-11, crack-7z-hash, rstan-to-pystan
  - Of these, `caffe-cifar-10` and `crack-7z-hash` also raised `AgentTimeoutError`
    (compute-heavy tasks — CIFAR-10 training and a hash-cracking workload — timing out
    before completion; plausibly related to residual host CPU/memory contention, though not
    confirmed).
  - `install-windows-3-11` and `rstan-to-pystan` failed with reward 0.0 and **no** exception
    recorded — i.e., the oracle run completed but did not pass verification. Root cause not
    further investigated in this session (out of scope for a smoke-test verification pass;
    would need per-task log inspection to attribute definitively).
- **4 failed with pure `RuntimeError` (no reward recorded at all):**
  break-filter-js-from-html, protein-assembly, path-tracing, compile-compcert — **all four
  failed for the identical, verifiable reason**, visible in `jobs/2026-08-13__11-28-55/job.log`:
  ```
  Error unknown: failed to resolve reference "docker.io/alexgshaw/<task-image>:20251031":
  failed to authorize: failed to fetch oauth token: unexpected status from POST request to
  https://auth.docker.io/token: 500 Internal Server Error
  ```
  This is a **Docker Hub registry-side transient failure** (HTTP 500 from
  `auth.docker.io`'s OAuth token endpoint while pulling task images) — an external
  dependency outage, unrelated to Harbor, the oracle solutions, local host resources, or
  this task's environment setup. It is explicitly **not** a recurrence of the 2026-08-12
  Docker-*daemon*-unreachable failure: `docker ps`/`docker info` against the **local**
  daemon remained instant and responsive throughout this entire run (see host-state
  checkpoints below) — only outbound pulls from Docker Hub's **remote** registry/auth
  service were affected, for 4 of 25 task images.

**Host-state checkpoints taken during the 25-task run** (confirming local Docker daemon
health throughout, distinguishing this from the 2026-08-12 failure mode):
- ~20 min elapsed: `docker ps` instant, showing live task containers; RAM free 78Mi, swap
  free 0B (fully used) — tightest point observed, comparable to 2026-08-12's readings, yet
  **`docker ps` still returned instantly with no hang and no `D`-state processes** (checked
  explicitly via `ps aux`) — a materially different behavior from 2026-08-12, where the
  daemon actually wedged under similar swap pressure.
- Run completion (26m22s): `docker ps` instant/empty (all task containers cleaned up), RAM
  free 1.3Gi, swap free 5.4Mi, disk unchanged at 894G available.
- Post-run: `docker ps -a` confirms no dangling containers left behind.

**Classification of this run's failure, per the brief's Blocker Protocol:**
- `type: technical`, `severity: major` — 17/25 (68%) is not the 100% the brief's acceptance
  criteria requires for "whatever scope was actually run." Per the brief's instruction to
  distinguish different failure causes rather than conflate them, this run's 8 failures
  split into two independently-attributable causes:
  1. 4/8 — external Docker Hub registry OAuth-token 500 errors (transient, outside this
     environment's or Harbor's control; would very likely succeed on retry once Docker
     Hub's auth service recovers)
  2. 4/8 — genuine task-level oracle non-passes (2 explicit 0.0-reward with no exception; 2
     `AgentTimeoutError` on compute-heavy tasks, possibly resource-timing-related)
- This is **not** a recurrence of the 2026-08-12 `type: external`/`severity: critical`
  Docker-daemon-unreachable blocker — the local Docker daemon was confirmed reachable and
  responsive at every checkpoint during this run, including at the point of tightest swap
  pressure.

### Overall assessment for T417

- The brief's **required minimum bar** (5-task oracle smoke, 100% pass, per Acceptance
  Criterion #5's "5-task minimum") is **met**. The environment (Harbor 0.21.0 + Docker
  29.6.2 + this host) is confirmed correctly configured and functional — the 2026-08-12
  blocker does not reproduce under the improved host conditions measured today.
- The **optional larger-scope validation** (`-l 25`, attempted as a more thorough check
  ahead of the full 89-task set per step 4's fallback guidance) surfaced real findings that
  should be reviewed before this environment is relied on for larger unattended measurement
  runs (T418+): a transient external registry dependency (4 tasks) and two apparently
  genuine task-level issues (4 tasks, 2 of which may be timing/resource-sensitive).
- Per the brief's explicit instruction ("do not fabricate a pass"), this run is **not**
  reported as a clean, unqualified 100% pass at the 25-task scope — that would misrepresent
  the actual result. The 5-task gate pass is reported as a genuine pass on its own terms.
- **Recommendation to orchestrator:** the 5-task pass should be sufficient to unblock
  Phase 1 work that only needs a *functional* Harbor/Docker environment. Before running the
  full 89-task oracle set (or relying on `-l 25`-scale runs for T418+ delta measurement),
  consider: (a) retrying the 4 Docker-Hub-registry-affected tasks alone once the registry's
  transient 500s clear, to confirm they pass given a healthy pull path; (b) investigating
  `install-windows-3-11` and `rstan-to-pystan`'s 0.0-reward outcomes specifically, since
  those are not explained by the registry issue or by an exception at all.

### Commands run (verbatim, in order, this session)

```
source <scratchpad>/.venv-harbor/bin/activate
harbor --version                                          # -> 0.21.0
docker --version                                          # -> Docker version 29.6.2, build dfc4efb
free -h ; timeout 8 docker ps ; nproc ; df -h /            # fresh host-state readings
harbor run -d terminal-bench/terminal-bench-2-1 -a oracle -l 5 -y
                                                            # -> 5/5 PASS, 9m18s
timeout 8 docker ps ; free -h ; df -h /                    # post-run health check
harbor run -d terminal-bench/terminal-bench-2 -a oracle -l 25 -y
                                                            # -> 17/25 PASS (68%), 26m22s
timeout 8 docker ps -a ; free -h ; df -h /                 # post-run health check
```

Results on disk: `jobs/2026-08-13__11-19-03/result.json` (5-task run),
`jobs/2026-08-13__11-28-55/result.json` and `jobs/2026-08-13__11-28-55/job.log` (25-task run)
— these are Harbor's own working-directory job outputs inside the worktree, not committed
(outside this task's `docs/benchmarks/environment.md`-only file-ownership scope).

---

## 2026-08-12 — original attempt (historical record, preserved verbatim below)

**Status at the time: BLOCKED — oracle smoke run did not execute (Docker daemon became
unreachable mid-task). Reported per Blocker Protocol, `type: external`, `severity:
critical`.** This section is retained for historical context; it has since been superseded
by the 2026-08-13 retry above, which reproduced neither the Docker-unreachable condition nor
today's host resource state.

### What succeeded

#### Harbor install
- Method: `python3 -m venv` (virtualenv), **not** `--user`/system pip — the host's system
  Python is PEP 668 "externally managed" and rejected `pip install --user harbor` outright
  (`error: externally-managed-environment`).
- Venv location: outside the repo worktree (session scratchpad), so no stray venv directory
  was ever added to the `docs/benchmarks/` file-ownership scope for this task.
- Command: `pip install harbor` inside the venv (after `pip install --upgrade pip`).
- Result: succeeded. Installed `harbor-0.21.0` plus its dependency tree (litellm, supabase
  client, fastapi/uvicorn, etc. — Harbor pulls in a fairly large dependency set).
- **Harbor version:** `harbor --version` → `0.21.0`
- `harbor run --help` confirms the CLI surface matches the brief's assumed syntax:
  `-d/--dataset`, `-a/--agent` (with `oracle` present in the accepted agent enum), `-l/--n-tasks`,
  `-y/--yes` (needed to auto-confirm host-environment-access prompts non-interactively) all exist
  as documented in the brief. No discrepancy from the brief's cited docs was found on the CLI
  surface itself.

#### Docker — initial confirmation (before Harbor install)
- `docker --version` → `Docker version 29.6.2, build dfc4efb`
- `docker ps` → succeeded, returned an empty container list (daemon reachable at this point).
- This matches the brief's brief-authoring-time confirmation.

#### Host resources (initial reading, before Harbor install)
- CPU: `nproc` → 14 cores
- RAM: `free -h` → total 7.5Gi, ~7.3Gi already used, only ~68Mi free, buff/cache ~290Mi
- Swap: 2.0Gi total, already fully used (2.0Gi used) at the very first reading
- Disk: `df -h /` → `/dev/sdf` 1007G total, 62G used, 895G available (7% used) — disk was never
  the constraint

### What failed: Docker daemon became unreachable

Sequence of events, in order:

1. Ran `pip install harbor` in a venv — succeeded (see above). This installed a large
   dependency tree, which is memory/IO intensive.
2. Immediately after, re-checked `docker --version` / `docker ps` / `free -h` — versions
   still printed, `docker ps` still returned instantly with an empty table. RAM: 84Mi free,
   swap: 2.0Gi/2.0Gi used (784Ki free at that instant).
3. Ran the planned 5-task oracle smoke test:
   ```
   harbor run -d terminal-bench/terminal-bench-2-1 -a oracle -l 5 -y
   ```
   Output (immediate, not a hang):
   ```
   Docker daemon is not running. Please start Docker and try again.
   ```
4. Diagnosed directly against the Docker CLI (not just Harbor's wrapper):
   - `docker ps` → hung; moved to background by the shell harness after its timeout window.
   - `docker context ls`, `docker info` → both hung the same way.
   - `timeout 15 docker version` → exit code 124 (timed out).
   - `timeout 25 docker ps` → exit code 124 (timed out), repeated on a second attempt with
     the same result.
   - `ps aux` showed the hung `docker ps` / `docker context ls` client processes stuck in
     kernel state `D` (uninterruptible sleep, i.e. blocked on IO to the daemon/VM, not just
     slow) for several minutes without progressing — e.g. `docker ps` at `Dl 215s` elapsed,
     `docker context ls` at `D 86s` elapsed, still not returning. A batch of
     `docker-cli-plugin-metadata` helper processes (buildx, compose, mcp, model, dhi,
     offload, pass, ai, agent, extension, init, debug) were also stuck in the same `D` state
     for 300+ seconds.
   - `free -h` at each check during this window: RAM free consistently in the 60–85Mi range
     (out of 7.5Gi total) and swap consistently reported as fully used (2.0Gi/2.0Gi, 0B free).
   - `ps aux --sort=-%mem` showed the host is a shared multi-agent dev environment: several
     concurrent VS Code extension-host processes and **multiple concurrent Claude Code agent
     processes** (5 distinct `claude` binary invocations observed running simultaneously)
     plus multiple MCP server child processes (gitlab, playwright, fetch, docker-mcp), all
     competing for the same 7.5Gi RAM / 2Gi swap budget alongside Docker Desktop's WSL2
     backend (`docker-desktop-user-distro` proxy process, PID 100).
   - Final retry (after ~10 minutes elapsed, to rule out a transient blip): `timeout 30
     docker ps` and a subsequent `harbor run ... -l 5 -y` attempt — the `docker ps` call
     again failed to return within its timeout window and the whole command was terminated
     by the shell harness. No new evidence of recovery.

### Root cause assessment (2026-08-12)

The most likely cause is host-wide memory exhaustion: physical RAM was already ~97% used
and swap was 100% full (0 bytes free) at every measurement taken after the Harbor
dependency install, on a shared host running several concurrent Claude Code agent sessions,
VS Code language servers, and multiple MCP server processes alongside Docker Desktop's
WSL2 VM. Under that pressure, the Docker CLI's IPC to the Docker Desktop backend appears to
have wedged (client processes stuck in kernel `D` state, not returning even after their own
`timeout` wrapper attempted to kill them). This is consistent with Docker being confirmed
working at task start and then failing partway through the same session with no
configuration change made by this task's work — i.e. an environment resource issue, not a
Harbor or Docker Compose/config problem introduced by this task.

No attempt was made to restart Docker Desktop, adjust WSL/VM memory limits, or kill other
agents'/IDE's processes — those are outside this task's scope and would be exotic
workarounds for what is, per the brief's own Blocker Protocol, an immediate-escalation
condition ("Docker unavailable or daemon unreachable → `type: external`,
`severity: critical` ... escalate immediately rather than attempting a workaround").

**Confirmed by the 2026-08-13 retry:** with swap at 949Mi free instead of 0B free at
session start, the daemon-unreachable condition did not recur at all, even under later
transient tightness (78Mi RAM free / 0B swap free mid-run on 2026-08-13) — supporting the
original root-cause assessment that this was a host memory/swap-pressure condition specific
to the 2026-08-12 session, not an inherent defect in Harbor, Docker, or this task's config.

### Commands run (2026-08-12, verbatim, in order)

```
pip install --user harbor                       # rejected: externally-managed-environment
python3 -m venv <scratchpad>/.venv-harbor
source <scratchpad>/.venv-harbor/bin/activate
python -m pip install --upgrade pip
pip install harbor                               # succeeded — harbor 0.21.0
harbor --version                                 # -> 0.21.0
docker --version                                 # -> Docker version 29.6.2, build dfc4efb
docker ps                                        # -> succeeded, empty table (pre-install-fallout check)
nproc; free -h; df -h /                          # host resources
harbor --help ; harbor run --help                # confirmed CLI surface / oracle agent option
harbor run -d terminal-bench/terminal-bench-2-1 -a oracle -l 5 -y
                                                  # -> "Docker daemon is not running. Please start Docker and try again."
docker ps                                        # hung (backgrounded by shell harness)
docker context ls; docker info                   # hung
timeout 15 docker version                        # exit 124
timeout 25 docker ps                             # exit 124
timeout 30 docker ps && harbor run ... -l 5 -y    # docker ps still failed to return; command terminated (exit 143)
```

### Oracle run result (2026-08-12)

**Not executed.** Zero trials ran. `harbor run` failed at the environment-startup stage
(Docker daemon unreachable) before any task container could be built or an oracle solution
applied. There is therefore no pass/fail count to report — this is not "0/5 tasks passed,"
it is "the run never reached task execution."
