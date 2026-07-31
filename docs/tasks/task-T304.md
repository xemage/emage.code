# Task T304 — Real Docker build + healthcheck of the T226 compose stack

**ID:** T304
**Owner:** devops-engineer
**Status:** blocked
**Priority:** P0
**Depends on:** T300
**Created:** 2026-07-31
**Completed:** —
**Based on:** docs/plans/plan-016-pattern-a-hardening-and-phase23-poc-closure.md

## Objective
Prove, for real, that CWSO's documented Docker Compose profile (`deploy/docker-compose-t226.yml`)
actually builds and runs — no mocked substitute, no assumption carried over from the fabricated
Phase 2/3 reports. This is the prerequisite for Wave 4 (deployment guide validation) and Wave 5
(the real T214 Pattern A test).

## Inputs
- `deploy/docker-compose-t226.yml`, `deploy/t226-phase2.env`
- `../CWSO` (orchestrator, git-shadow, merge-engine, rollout services)
- `docs/artifacts/cwso-mcp-contract-v1.md` (expected 11-tool MCP contract)

## Expected outputs
- A running, healthy 4-container CWSO stack (left running for Wave 4/5).
- This file's Execution notes containing all command outputs below.

## Acceptance criteria
1. Host-side pre-flight: `cd ../CWSO/orchestrator && go build ./...` — paste its exit code and
   output regardless of pass/fail (go IS installed on this host: `go1.26.3 linux/amd64`).
2. `docker compose -f deploy/docker-compose-t226.yml build` then `up -d`, then
   `docker compose -f deploy/docker-compose-t226.yml ps` and
   `docker ps --filter "name=cwso-" --format "table {{.Names}}\t{{.Status}}"`.
3. `orchestrator`, `git-shadow`, `merge-engine`, `rollout` all show `Up` / `healthy`. If ANY service
   fails to build or is unhealthy: capture the FULL build/log output
   (`docker compose -f deploy/docker-compose-t226.yml logs <service>`), file a new bug task in this
   repo's ledger, do NOT mark this task done, do NOT substitute a smaller/mocked compose file, and
   hand off to T310.
4. If the stack is healthy, also run the MCP contract sanity check: mint an orchestrator-role JWT
   per plan-009 Appendix A and call `tools/list` against `http://127.0.0.1:8080/mcp` — expect a
   JSON-RPC response listing 11 tools.
5. Per R8, paste every command's literal output into Execution notes. Do NOT run
   `docker compose down` at the end — leave the stack up for T305/T214.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

Executed 2026-07-31 by devops-engineer subagent (delegated by orchestrator), independently
re-verified by orchestrator via direct `docker ps`/`docker compose ps` calls.

### Step 1 — host-side `go build ./...` pre-flight

Command:
```
cd /home/emage/Code/emage/CWSO/orchestrator && /usr/local/go/bin/go build ./... ; echo "go_build_exit=$?"
```
(Note: `go` is installed at `/usr/local/go/bin/go` — not on this tool's default `bash` PATH, which
is a sandboxing artifact per plan-016 §3 Assumptions, not a fact about the host.)

Output:
```
go_build_exit=0
```
No stdout/stderr besides the exit code — a clean `go build` produces no output on success.
**Host-side Go build: PASS.**

### Step 2 — Docker compose build + up

Commands:
```
cd /home/emage/Code/emage/emage.code
source deploy/t226-phase2.env 2>/dev/null || true
docker compose -f deploy/docker-compose-t226.yml build
docker compose -f deploy/docker-compose-t226.yml up -d
sleep 15
docker compose -f deploy/docker-compose-t226.yml ps
docker ps --filter "name=cwso-" --format "table {{.Names}}\t{{.Status}}"
```

`docker compose build`: succeeded for all 4 defined images (`cwso/orchestrator:dev`,
`cwso/git-shadow:dev`, `cwso/merge-engine:dev`, `cwso/rollout:dev`) plus the compose file's 5th
service (`sia-executor`, using stock `python:3.11-slim`, not part of T304's 4-service target list).
Only "error" hits in the full build log were the Rust type name `SparseTensorError` — not an actual
build failure. Rollout crate finished: `Finished 'release' profile [optimized] target(s) in 3m 14s`.

`docker compose up -d`: all 5 containers created and started; `cwso-orchestrator` reported
`Waiting` → `Healthy` during startup.

`docker compose -f deploy/docker-compose-t226.yml ps` (re-checked at t+15s and again at t+53s to
rule out a transient healthcheck blip — independently re-run by orchestrator at a later time too,
see below):

```
NAME                IMAGE                   COMMAND                  SERVICE        CREATED         STATUS                     PORTS
cwso-git-shadow     cwso/git-shadow:dev     "/usr/bin/tini -- /u…"   git-shadow     2 minutes ago   Up 2 minutes
cwso-merge-engine   cwso/merge-engine:dev   "/usr/bin/tini -- /u…"   merge-engine   2 minutes ago   Up 2 minutes
cwso-orchestrator   cwso/orchestrator:dev   "/sbin/tini -- /usr/…"   orchestrator   2 minutes ago   Up 2 minutes (healthy)     0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp
cwso-rollout        cwso/rollout:dev        "/usr/bin/tini -- /u…"   rollout        2 minutes ago   Up 2 minutes (unhealthy)   0.0.0.0:8787->8787/tcp, [::]:8787->8787/tcp
cwso-sia-executor   python:3.11-slim        "/bin/bash -c 'set -…"   sia-executor   2 minutes ago   Up 2 minutes
```

`docker ps --filter "name=cwso-" --format "table {{.Names}}\t{{.Status}}"` (orchestrator's own
independent re-run, same result):

```
NAMES               STATUS
cwso-sia-executor   Up 2 minutes
cwso-orchestrator   Up 2 minutes (healthy)
cwso-rollout        Up 2 minutes (unhealthy)
cwso-merge-engine   Up 2 minutes
cwso-git-shadow     Up 2 minutes
```

### Step 3 — evaluation: CASE B (failure)

`cwso-orchestrator` is `healthy`. `cwso-git-shadow` and `cwso-merge-engine` have no `HEALTHCHECK`
defined in their images (confirmed via `docker inspect`), so plain `Up` satisfies the acceptance
criteria for those two. `cwso-rollout` DOES have a healthcheck and it is **unhealthy**, with
`FailingStreak: 6` and no recovery — this is a real, persistent failure, not a startup race.

Full `docker compose -f deploy/docker-compose-t226.yml logs rollout`:
```
cwso-rollout  | {"timestamp":"2026-07-31T17:42:36.557575Z","level":"INFO","fields":{"message":"trajectory Parquet store enabled","written":0},"target":"cwso_rollout"}
cwso-rollout  | {"timestamp":"2026-07-31T17:42:36.557687Z","level":"ERROR","fields":{"message":"trajectory store writer exited","error":"create rollout store \"./rollout_store\""},"target":"cwso_rollout::store"}
cwso-rollout  | {"timestamp":"2026-07-31T17:42:36.557917Z","level":"INFO","fields":{"message":"cwso-rollout IPC ready","socket_path":"\"/run/cwso/rollout.sock\""},"target":"cwso_rollout::ipc"}
cwso-rollout  | {"timestamp":"2026-07-31T17:42:36.559679Z","level":"INFO","fields":{"message":"starting rollout proxy","bind":"0.0.0.0:8787","upstream":"http://127.0.0.1:18080"},"target":"cwso_rollout"}
cwso-rollout  | {"timestamp":"2026-07-31T17:42:36.559828Z","level":"INFO","fields":{"message":"cwso-rollout proxy listening","bind":"0.0.0.0:8787"},"target":"cwso_rollout::proxy"}
```

`docker inspect cwso-rollout --format '{{json .Config.Healthcheck}}'` (the healthcheck definition
itself, independently re-run by orchestrator):
```json
{"Test":["CMD","curl","-f","http://127.0.0.1:8787/v1/models"],"Interval":10000000000,"Timeout":3000000000,"Retries":5}
```

`docker inspect cwso-rollout --format '{{json .State.Health}}'` (probe history, first 5 attempts,
all identical):
```json
{
  "Status": "unhealthy",
  "FailingStreak": 6,
  "Log": [
    {"Start":"2026-07-31T17:42:56Z","End":"2026-07-31T17:42:56Z","ExitCode":22,
     "Output":"curl: (22) The requested URL returned error: 405\n"},
    {"Start":"2026-07-31T17:43:06Z","End":"2026-07-31T17:43:06Z","ExitCode":22,
     "Output":"curl: (22) The requested URL returned error: 405\n"},
    {"Start":"2026-07-31T17:43:16Z","End":"2026-07-31T17:43:16Z","ExitCode":22,
     "Output":"curl: (22) The requested URL returned error: 405\n"},
    {"Start":"2026-07-31T17:43:26Z","End":"2026-07-31T17:43:26Z","ExitCode":22,
     "Output":"curl: (22) The requested URL returned error: 405\n"},
    {"Start":"2026-07-31T17:43:36Z","End":"2026-07-31T17:43:36Z","ExitCode":22,
     "Output":"curl: (22) The requested URL returned error: 405\n"}
  ]
}
```

**Two distinct real defects identified in CWSO core, both inside `cwso-rollout`:**
1. Its own healthcheck (`curl -f http://127.0.0.1:8787/v1/models`, a bare GET) receives HTTP 405
   Method Not Allowed from the `/v1/models` endpoint — the healthcheck's HTTP method/path does not
   match what the service actually accepts.
2. Its startup log shows an unrecovered `ERROR`: `"trajectory store writer exited","error":"create
   rollout store \"./rollout_store\""` — the binary appears to write to a hardcoded relative path
   `./rollout_store` rather than the `CWSO_ROLLOUT_TRAJECTORY_STORE_PATH=/data/parquet-store`
   env var the compose file sets, and/or that relative path is not writable/does not exist inside
   the container's working directory.

Per plan-016 §"WAVE 3" Case B instructions: no fix attempted, no code touched in `../CWSO`, no
smaller/mocked compose file substituted. Containers left running as-is (not force-removed).
**Step 4 (MCP contract sanity check) was correctly skipped — it only runs in the healthy case.**

### Disposition

- Docker stack is left running (git-shadow, merge-engine, orchestrator all fine; rollout unhealthy;
  sia-executor running but restart-limited and depends on orchestrator being healthy, which it is).
- **T304 acceptance criterion 3 is NOT met** ("orchestrator, git-shadow, merge-engine, rollout all
  Up/healthy") — `rollout` is unhealthy. This task is NOT marked done.
- Bug filed as **T311** in this repo's ledger (`docs/tasks/task-T311.md`).
- T310 executed for real — see `docs/tasks/task-T310.md` Execution notes and the three files
  written into `../CWSO`.

### Independent orchestrator re-verification (2026-07-31, after subagent report)

```
$ docker compose -f /home/emage/Code/emage/emage.code/deploy/docker-compose-t226.yml ps
NAME                IMAGE                   COMMAND                  SERVICE        CREATED         STATUS                     PORTS
cwso-git-shadow     cwso/git-shadow:dev     "/usr/bin/tini -- /u…"   git-shadow     2 minutes ago   Up 2 minutes
cwso-merge-engine   cwso/merge-engine:dev   "/usr/bin/tini -- /u…"   merge-engine   2 minutes ago   Up 2 minutes
cwso-orchestrator   cwso/orchestrator:dev   "/sbin/tini -- /usr/…"   orchestrator   2 minutes ago   Up 2 minutes (healthy)
cwso-rollout        cwso/rollout:dev        "/usr/bin/tini -- /u…"   rollout        2 minutes ago   Up 2 minutes (unhealthy)
cwso-sia-executor   python:3.11-slim        "/bin/bash -c 'set -…"   sia-executor   2 minutes ago   Up 2 minutes

$ docker ps --filter "name=cwso-" --format "table {{.Names}}\t{{.Status}}"
NAMES               STATUS
cwso-sia-executor   Up 2 minutes
cwso-orchestrator   Up 2 minutes (healthy)
cwso-rollout        Up 2 minutes (unhealthy)
cwso-merge-engine   Up 2 minutes
cwso-git-shadow     Up 2 minutes
```
Confirms the subagent's report is accurate — CASE B stands.
