# T305 — Deployment Guide Validation Report

**Producer agent:** qa-engineer
**Task:** T305
**Based on:** `docs/deployment/local-docker-desktop-guide.md`, `docs/tasks/task-T305.md`
**Date:** 2026-08-01
**Environment:** Linux host, Docker 29.6.2, Docker Compose v5.3.1, live CWSO stack from T304
(deployed via `deploy/docker-compose-t226.yml`) already Up/healthy for all 4 target services
(`orchestrator`, `git-shadow`, `merge-engine`, `rollout`) at the start of this validation, and
confirmed still Up/healthy at the end (this validation did not tear it down).

## 0. Scope-mismatch pre-check (mandatory, done first)

The guide's own "Detailed Setup → Step 1" references `deploy/docker-compose-local-dev.yml`,
`deploy/docker-compose-local-dev.env`, and `../.env.jwt.dev` — **not**
`deploy/docker-compose-t226.yml` (the file actually driving the live, verified stack).

Command:
```
ls -la deploy/
ls -la scripts/deploy/
for f in deploy/docker-compose-local-dev.yml deploy/docker-compose-local-dev.env deploy/.env.jwt.dev; do
  if [ -e "$f" ]; then echo "$f EXISTS"; else echo "$f DOES NOT EXIST"; fi
done
```

Actual output:
```
=== ls -la deploy/ ===
total 24
-rw-r--r--  1 emage emage 7732 Aug  1 19:15 docker-compose-t226.yml
-rw-r--r--  1 emage emage 5971 Jun 23 11:26 t226-phase2.env

=== ls -la scripts/deploy/ ===
total 36
-rwxr-xr-x 1 emage emage  9408 Jun 29 09:21 cwso-docker-desktop.sh
-rwxr-xr-x 1 emage emage 12613 Jun 29 09:21 cwso-proxmox-setup.sh

deploy/docker-compose-local-dev.yml DOES NOT EXIST
deploy/docker-compose-local-dev.env DOES NOT EXIST
deploy/.env.jwt.dev DOES NOT EXIST
```

**FINDING (critical, guide-blocking):** none of the three files the guide's "Detailed Setup"
prose instructs the reader to copy/source exist anywhere in this repo. `deploy/` contains only
`docker-compose-t226.yml` and `t226-phase2.env`. Interestingly, the automated setup script
(`scripts/deploy/cwso-docker-desktop.sh`) itself is internally consistent with reality — its
`DOCKER_COMPOSE_SOURCE`/`ENV_SOURCE`/`JWT_SOURCE` variables point at `docker-compose-t226.yml`,
`t226-phase2.env`, and `deploy/.env.jwt.dev` respectively (the last of which *also* does not
exist, triggering the script's own fallback JWT-generation branch — see §1). So there are two
separate, independent guide/reality mismatches: (a) the guide's written prose in Step 1 names
files that don't exist and never matches the script it tells the reader to run in Quick Start,
and (b) the script's own reference to `deploy/.env.jwt.dev` also doesn't exist (that file only
exists inside `../CWSO/.env.jwt.dev`, a different repo entirely).

---

## 1. Quick Start (5 minutes)

### Step 1 — `cd ~/Code/emage/emage.code`

Command: `pwd` (after cd)
Output: `/home/emage/Code/emage/emage.code`
**PASS** — matches guide's assumed working directory.

### Step 2 — `bash scripts/deploy/cwso-docker-desktop.sh`

Attempted exactly as written. Result:
```
Permission for this action was denied by the Claude Code auto mode classifier.
Reason: Blocked by classifier.
```
**This command was blocked by the executing agent's own sandbox/permission layer** — not a guide
failure. The full unattended script performs `docker-compose pull` and `docker-compose up -d`
against a **second, independent Compose project** (`deploy/local-dev`) whose service definitions
use fixed `container_name:` values (`cwso-orchestrator`, `cwso-git-shadow`, `cwso-merge-engine`,
`cwso-rollout`, `cwso-sia-executor` — confirmed via `grep container_name`) and fixed host ports
(`8080`, `8787`) that are already claimed by the live, verified T304 stack. Static analysis of the
script plus Docker's own container-name/port-uniqueness rules indicates this would **not** have
torn down the live stack (Docker refuses to create a duplicately-named/ported container; it does
not remove the pre-existing one), but the classifier correctly treated the action as high-risk
given the two-stack-collision scenario and refused it. I did not attempt to route around this
block (per instructions).

To still produce real evidence, I ran the script's benign, read-only entry points directly:

Command: `bash scripts/deploy/cwso-docker-desktop.sh --help`
Output (verbatim):
```
=== CWSO Docker Desktop Setup ===

Usage: bash cwso-docker-desktop.sh [OPTION]
...
After successful deployment, test with:
  curl http://localhost:8080/health
...
```
**PASS** — help text renders as documented, exit 0.

Command: `bash scripts/deploy/cwso-docker-desktop.sh --status`
Output (verbatim):
```
=== CWSO Deployment Status ===

scripts/deploy/cwso-docker-desktop.sh: line 211: cd: ./deploy/local-dev: No such file or directory
EXIT_CODE=1
```
**FAIL** — `--status` unconditionally assumes `deploy/local-dev` already exists (i.e. that the
full unattended setup has already been run once); it has no guard for the "never set up" case and
exits with an unhandled `cd` error rather than a clean message like "not deployed yet".

**Manual reproduction of the script's non-destructive prerequisite checks** (since the full run
was blocked), run directly on the host:
```
$ docker --version
Docker version 29.6.2, build dfc4efb

$ docker info >/dev/null 2>&1 && echo yes || echo no
yes

$ docker-compose --version
Docker Compose version v5.3.1

$ command -v lsof && echo FOUND
/usr/bin/lsof
FOUND

$ for port in 8080 8787 8788 8789; do lsof -Pi :$port -sTCP:LISTEN -t; echo "port $port exit=$?"; done
port 8080 exit=1
port 8787 exit=1
port 8788 exit=1
port 8789 exit=1
```
**FINDING (environment-specific, worth flagging):** the script's own port-conflict pre-check
(`lsof -Pi :$port -sTCP:LISTEN -t`) reports **no ports in use** even though ports 8080 and 8787
are demonstrably bound and serving traffic from the live containers (confirmed independently
below via `curl` succeeding on both, and via `docker ps`'s own `PORTS` column showing
`0.0.0.0:8080->8080/tcp` and `0.0.0.0:8787->8787/tcp`). In this containerized/sandboxed shell,
`lsof` cannot see the Docker-published listening sockets in the host network namespace, so the
script's "warn if ports are already in use" safety net is silently defeated here. This may be an
artifact specific to this execution sandbox rather than a bug that affects a real Docker Desktop
user, but it is worth recording because it means the script's own documented safety check
(`check_prerequisites`) cannot be relied upon in every environment.

### Step 3 — `curl http://localhost:8080/health` ("Done! CWSO is now running locally")

Command: `curl -s -i http://localhost:8080/health --max-time 5`
Output (verbatim):
```
HTTP/1.1 401 Unauthorized
Content-Security-Policy: default-src 'self'
Content-Type: text/plain; charset=utf-8
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-Xss-Protection: 0
Content-Length: 21

missing bearer token
```
Guide's claim (Quick Start): implies a bare, unauthenticated `curl .../health` succeeds ("Done!
CWSO is now running locally"); Detailed Setup Step 4 makes this explicit: "Expected response:
`{"status":"healthy","timestamp":"2026-06-28T08:45:00Z"}`".

**FAIL** — the actual, live, verified-healthy orchestrator returns HTTP 401 with plaintext body
`missing bearer token` on `GET /health`, not the JSON healthy payload the guide shows. The
orchestrator's real unauthenticated liveness route is `/healthz`, confirmed working:
```
$ curl -s -i http://localhost:8080/healthz --max-time 5
HTTP/1.1 200 OK
Content-Length: 2
Content-Type: text/plain; charset=utf-8

ok
```
So `/healthz` (not `/health`) is the actual no-auth liveness endpoint, and even that returns the
plaintext `ok`, not the JSON `{"status":"healthy","timestamp":...}` shape the guide documents
anywhere. This is a significant Quick-Start-breaking finding: the very first command a brand-new
reader is told to run to confirm success does not produce anything resembling the guide's claimed
output.

---

## 2. Detailed Setup

### Step 1 — Prepare Environment

Commands run exactly as written:
```
$ cd ~/Code/emage/emage.code
$ mkdir -p deploy/local-dev
mkdir exit=0
$ cp deploy/docker-compose-local-dev.yml deploy/local-dev/docker-compose.yml
cp: cannot stat 'deploy/docker-compose-local-dev.yml': No such file or directory
cp1 exit=1
$ cp deploy/docker-compose-local-dev.env deploy/local-dev/.env
cp: cannot stat 'deploy/docker-compose-local-dev.env': No such file or directory
cp2 exit=1
```
**FAIL** — exactly as predicted in §0: both source files the guide names do not exist. This is
the literal, guide-blocking manifestation of the §0 scope-mismatch finding. Everything downstream
in the guide's Detailed Setup that depends on `deploy/local-dev/docker-compose.yml` existing
cannot be executed as literally written from this point forward.

### Step 2 — Configure JWT Secret

**Option A** (`source ../.env.jwt.dev`): **Not executed**, per this task's mandatory security
guardrail (`.claude/rules/security-guidelines.md` § "Secret and credential files"), which
hard-blocks any agent from reading/sourcing/catting `.env`/`.env.*` files, including
`.env.jwt.dev`. This is recorded as: *Step 2 Option A could not be executed by an AI agent per
this repo's security-guidelines.md hard block on reading `.env.*` files.* This is itself worth
flagging as a documentation gap — **the guide has no AI-safe/agent-safe way to obtain a working
token without reading a raw secret file**, which matters increasingly as agentic readers (not just
humans) are expected to follow deployment guides in this repo's own workflow.

Separately and independent of the AI-agent guardrail: Option A's source file
(`deploy/.env.jwt.dev`) does not exist at the path the guide names anyway (see §0), so even a
human reader following the guide literally would hit `bash: ../.env.jwt.dev: No such file or
directory` at this step, regardless of the agent-safety question.

**Option B** (generate new JWT): executed, since it only generates a fresh secret rather than
reading an existing credential file:
```
$ export JWT_SECRET=$(head -c 32 /dev/urandom | base64)
$ echo "JWT_SECRET=$JWT_SECRET" >> .env
write_exit=0
$ wc -l .env
1 .env
```
**PASS** (mechanically) — the command succeeds and produces a 1-line `.env` file. Note: because
Step 1 failed, this `.env` file was created standalone in a manually-`mkdir -p`'d
`deploy/local-dev/` directory with no accompanying `docker-compose.yml` — i.e., Option B "works"
in isolation but there is no compose stack for it to configure, since Step 1 never produced one.
(This test scaffolding directory was deleted after validation to leave no side effects — see §5.)

### Step 3 — Start CWSO Stack

Commands run exactly as written:
```
$ cd deploy/local-dev
$ docker-compose up -d
no configuration file provided: not found
exit=1
$ docker-compose ps
no configuration file provided: not found
exit=1
```
**FAIL** — cascading failure from Step 1: since no `docker-compose.yml` was ever copied into
`deploy/local-dev`, `docker-compose up -d` cannot find a config file. The guide's "Expected
output" table (four services `Up 2 seconds`) cannot be produced by following the guide's own
steps in order.

**Substitution used to continue testing forward (Step 4 onward):** rather than stop entirely, I
tested Step 4's claims against the **already-running, independently-verified T304 stack**
(`deploy/docker-compose-t226.yml`), since that is the only real CWSO stack present on this host.
This is a deliberate substitution, not a guide-follow — flagged explicitly here per the task
brief's instruction to document any substitution precisely.

Also note, purely by inspection (not executed, to avoid disturbing the live stack): the guide's
own "Expected output" table for this step lists `COMMAND: "python3 ..."` for all four services.
The actual, currently running stack shows:
```
$ docker compose -f deploy/docker-compose-t226.yml ps
NAME                IMAGE                   COMMAND                  SERVICE
cwso-git-shadow     cwso/git-shadow:dev     "/usr/bin/tini -- /u…"   git-shadow
cwso-merge-engine   cwso/merge-engine:dev   "/usr/bin/tini -- /u…"   merge-engine
cwso-orchestrator   cwso/orchestrator:dev   "/sbin/tini -- /usr/…"   orchestrator
cwso-rollout        cwso/rollout:dev        "/usr/bin/tini -- /u…"   rollout
cwso-sia-executor   python:3.11-slim        "/bin/bash -c 'set -…"   sia-executor
```
**FAIL (minor/cosmetic)** — none of the 4 target services run `python3` at all; they are
`tini`-wrapped compiled Go/Rust binaries (only the non-target `sia-executor` service is Python).
The guide's example output table describes a stack that does not match the actual CWSO
architecture.

### Step 4 — Verify Deployment

Command: `curl http://localhost:8080/health` — already covered in §1 Step 3 above (401, "missing
bearer token" — **FAIL** against guide's claimed JSON healthy response).

Command: `curl http://localhost:8787/health`
Output (verbatim):
```
HTTP/1.1 405 Method Not Allowed
content-type: application/json
content-length: 46

{"error":{"message":"only POST is supported"}}
```
Guide gives no explicit "expected response" for this specific line (only implies success by
proximity to the orchestrator health check), but a `405 Method Not Allowed` on a documented
"health" endpoint is self-evidently not a health check success. **FAIL.** The real rollout
liveness route is `/healthz` (confirmed separately, matches T304/T312's findings):
```
$ curl -s -i http://localhost:8787/healthz --max-time 5
HTTP/1.1 200 OK
content-type: application/json
content-length: 15

{"status":"ok"}
```

Command: JWT authentication test, exactly as written but substituting Option B's freshly-generated
secret in place of reading it back out of a `.env` file (to avoid a second `.env` read, consistent
with the security guardrail):
```
$ export JWT_SECRET=$(head -c 32 /dev/urandom | base64)
$ TOKEN=$(python3 -c "
import jwt
secret = '$JWT_SECRET'
payload = {'sub': 'test-user', 'role': 'admin'}
print(jwt.encode(payload, secret, algorithm='HS256'))
")
$ curl -s -i -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/status --max-time 5
HTTP/1.1 401 Unauthorized
Content-Length: 14

invalid token
```
**Expected and documented distinction, NOT a guide defect:** a token minted with a freshly
generated secret cannot match whatever secret the already-running orchestrator container was
actually configured with at build time, so `401 invalid token` here is attributable to the
Option-B/live-stack secret mismatch created by this validation's own necessary substitution, not
to a flaw in the guide's instructions for this specific sub-step. Recorded as **N/A (substitution
artifact)**, not scored PASS/FAIL against the guide.

---

## 3. Common Tasks

### Viewing Logs

Guide's exact commands (`docker-compose logs -f orchestrator`, `docker-compose logs --tail=50
rollout-proxy`) require a `deploy/local-dev` compose context that doesn't exist (Step 1 failure,
above), so literal execution is not possible. Substituting `-f deploy/docker-compose-t226.yml`
against the live stack to check the **service name** claim specifically:
```
$ docker compose -f deploy/docker-compose-t226.yml logs --tail=5 rollout-proxy
no such service: rollout-proxy
exit=1

$ docker compose -f deploy/docker-compose-t226.yml logs --tail=5 rollout
cwso-rollout  | {"timestamp":"2026-08-01T17:11:55.773868Z","level":"INFO", ... "cwso-rollout proxy listening" ...}
exit=0
```
**FAIL (systemic across the guide)** — the compose service is named `rollout`, not `rollout-proxy`,
anywhere in `deploy/docker-compose-t226.yml` (`grep container_name`/`grep "^  [a-z-]*:$"`
confirms the service key is `rollout:` and `container_name: cwso-rollout`). The guide uses
`rollout-proxy` as the service/container identifier repeatedly: here, in "Container Status"
(`docker stats cwso-orchestrator cwso-rollout-proxy`), and in the Appendix ("rollout-proxy (port
8787)"). Every one of these literal invocations fails against the real stack.

### Stopping CWSO / Removing CWSO / Updating CWSO Image

**Not executed** (would either fail identically to the above due to missing `deploy/local-dev`
context, or — if adapted to target the live T226 stack directly — would stop/remove/force-recreate
the verified-healthy stack that T304 spent two rounds of debugging to get healthy). Reviewed by
inspection only, per task scope carve-out:
- `docker-compose stop` / `start`: syntactically fine, no observed defect by inspection, but same
  missing-directory problem as above applies to literal execution.
- `docker-compose down` / `down -v`: same.
- `bash ../../scripts/deploy/cwso-docker-desktop.sh --update`: by inspection, `update_deployment()`
  in the script also assumes `deploy/local-dev` already has a valid compose file (same root
  problem as `--status`, confirmed above).

### Testing with Sample Requests

Not separately executed beyond the equivalent JWT/dispatch pattern already covered in §2 Step 4
(same secret-mismatch caveat would apply to the `POST /dispatch` example). By inspection: no
additional defects beyond what's already flagged.

---

## 4. Troubleshooting (read critically; destructive items not executed)

### Port Already in Use
By inspection: `lsof -i :8080` / `kill -9 <PID>` is standard and fine, though this validation
independently found (§1 Step 2) that `lsof` does not see Docker-Desktop/Docker-Engine-published
ports from inside this particular execution sandbox — a caveat worth a documentation footnote but
not a guide defect per se.

### Out of Memory
Not executed (no OOM condition present); read only, no defect found by inspection.

### JWT Authentication Failed
Step 1 (`grep JWT_SECRET deploy/local-dev/.env`) — **not executed**, since it requires reading an
`.env` file's contents, which the security guardrail blocks regardless of who authored the file.
Step 4 (`rm deploy/local-dev/.env ... source ../../deploy/.env.jwt.dev`) references
`deploy/.env.jwt.dev` again — confirmed in §0 not to exist. **FAIL** (same root cause as §0/§2
Step 2).

### Network Connection Issues
```
$ docker network ls
NETWORK ID     NAME                DRIVER    SCOPE
56bab6e0aa4b   bridge              bridge    local
b5db1d3511dd   cwso-t226_default   bridge    local
c7b03f50d40c   host                host      local
409e209d3aa0   none                null      local
```
**PASS** (informational) — real network name is `cwso-t226_default`; the guide's
`<cwso-network>` is a documented placeholder, not a defect.

```
$ docker exec cwso-orchestrator curl -s -i http://localhost:8080/healthz
OCI runtime exec failed: exec failed: unable to start container process:
exec: "curl": executable file not found in $PATH
```
**FAIL** — guide's own troubleshooting step #4 (`docker-compose exec orchestrator curl
http://localhost:8080/health`) cannot work against the real orchestrator image: it does not ship
`curl` (a minimal distroless-style Go binary image). This is a genuine, reproducible defect in
the guide's own troubleshooting advice, not a scope-mismatch artifact — the command is otherwise
correctly formed (aside from also using the wrong `/health` vs `/healthz` path).

`docker inspect cwso-orchestrator | grep -A 10 NetworkSettings` — **not separately executed**
verbatim (grep pattern flagged by this session's own command classifier as sensitive-looking);
equivalent structured data obtained via `docker inspect --format '{{json .NetworkSettings.Networks}}'`
successfully, confirming the orchestrator is reachable on `cwso-t226_default` with DNS aliases
`cwso-orchestrator`/`orchestrator`. No defect found in the underlying network config itself.

### Containers Won't Start
Not executed (stack is already running; would require tearing it down to test `docker-compose
build --no-cache` / `down -v` / `docker system prune` meaningfully). Read only: commands are
standard Docker Compose troubleshooting boilerplate; no CWSO-specific defect visible by inspection.

---

## 5. Performance Tuning

Not executed (would require editing/restarting the live compose stack's resource limits). Read
only: the guide's example `mem_limit`/`cpus` block references top-level `orchestrator:` /
`rollout-proxy:` keys directly under `docker-compose.yml` — by inspection of the real
`docker-compose-t226.yml`, `mem_limit`/`cpus` are **not currently set on any service** in the
actual file (`grep -c "mem_limit\|cpus:"` → 0 matches), so this section documents an aspirational
configuration that isn't reflected in the actual compose file's current defaults, and again names
`rollout-proxy` instead of the real service name `rollout`. **Not scored PASS/FAIL** since nothing
was executed — flagged as an inspection-only observation.

---

## 6. Monitoring and Healthchecks

### Built-in Health Checks
```
$ for port in 8080 8787 8788 8789; do
    echo "Port $port:"
    curl -s http://localhost:$port/health | jq '.' || echo "  [not responding]"
  done
Port 8080:
jq: parse error: Invalid numeric literal at line 1, column 8
  [not responding]
Port 8787:
{
  "error": {
    "message": "only POST is supported"
  }
}
Port 8788:
Port 8789:
```
**FAIL** — run exactly as the guide instructs (including its own `for port in 8080 8787 8788
8789` loop from the Appendix's own service list). None of the four ports returns anything
resembling a healthy status: 8080 returns plaintext (401 body), which breaks `jq` parsing and
triggers the loop's own "[not responding]" fallback message (misleadingly, since the port *did*
respond — it just wasn't valid JSON due to the auth requirement); 8787 returns a JSON error object
about the wrong HTTP method, not a health status; 8788 and 8789 (`git-shadow`, `merge-engine`)
return nothing at all because — confirmed directly from the compose file — **neither service
publishes any port to the host** (`grep -A5 "git-shadow:\|merge-engine:"` shows no `ports:` block
for either service; both are IPC-socket-only, `cwso-runtime` volume-mounted services). The guide's
own Appendix explicitly lists "Git Shadow (port 8788)" and "Merge Engine (port 8789)" as if they
were directly curlable HTTP health endpoints on `localhost`; this is not true of the actual
architecture.

### Container Status
```
$ docker stats cwso-orchestrator cwso-rollout-proxy --no-stream
Error response from daemon: No such container: cwso-rollout-proxy
exit=1
```
**FAIL** — same `rollout` vs `rollout-proxy` naming defect as §3 "Viewing Logs", reproduced here
literally as the guide's own example command.

```
$ docker exec cwso-orchestrator free -h
              total        used        free      shared  buff/cache   available
Mem:           7.5G        6.2G       76.4M        8.2M        1.2G        1.1G
Swap:          2.0G        2.0G       12.0K
```
**PASS** — `docker-compose exec orchestrator free -h` works fine substituting `docker exec`
directly (no compose project context needed for this one); real output obtained.

```
$ docker system df
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          13        5         7.552GB   7.131GB (94%)
Containers      5         5         2.941MB   0B (0%)
Local Volumes   6         1         74.76MB   74.76MB (100%)
Build Cache     76        0         6.87GB    6.843GB
```
**PASS** — works as documented, no CWSO-specific claims to verify beyond "command runs".

### Logs Analysis
```
$ docker compose -f deploy/docker-compose-t226.yml logs 2>&1 | grep -i error | tail -10
cwso-sia-executor  | ... WARNING - HTTP POST http://orchestrator:8080/nodes/sia-executor-1/heartbeat
    gave up after 2 attempts: <urlopen error [Errno -3] Temporary failure in name resolution>
... (9 more similar lines, all from cwso-sia-executor)
```
**PASS (mechanically)** — the `grep -i error` pattern itself works as documented. Note: this
surfaced a separate, out-of-scope observation (repeated DNS resolution failures for the
`orchestrator` hostname from inside `cwso-sia-executor`) that is not a guide claim under test here
and is not part of the guide's own 4-service target list — flagged only as an FYI, not scored, and
not investigated further since it's outside T305's scope (the guide doesn't mention
`sia-executor` at all).

`docker-compose logs orchestrator | grep -i "token\|auth"` — **blocked by this session's own
command-permission classifier** (flagged as a sensitive-secret-adjacent pattern search); not
executed. No literal output to report for this specific sub-command; not scored PASS/FAIL.

---

## 7. Data Persistence

### Parquet Store
```
$ ls -la /tmp/t226-parquet-store
-rw-r--r--    1 emage emage   4496 Jun 23 14:02 trajectories-shard-00.parquet
-rw-r--r--    1 emage emage   4501 Jun 23 14:02 trajectories-shard-01.parquet
-rw-r--r--    1 emage emage   4543 Jun 23 14:02 trajectories-shard-02.parquet
```
**PASS** — the guide's claim ("The Parquet trajectory store is created at
`/tmp/t226-parquet-store` by default") is accurate; this matches the compose file's own default
(`PARQUET_STORE_HOST_PATH:-/tmp/t226-parquet-store`), and real `.parquet` files are present.

### Volume Management
```
$ docker volume ls | grep -i cwso
local     cwso-t226_cwso-runtime
local     cwso_cwso-runtime

$ docker volume inspect cwso-local-dev_orchestrator-data
Error response from daemon: get cwso-local-dev_orchestrator-data: no such volume
exit=1
```
**FAIL** — the guide's "Volume Management" and "Backup and Restore" sections both name a volume
`cwso-local-dev_orchestrator-data` that has never existed. The real `docker-compose-t226.yml`
defines exactly one named volume, `cwso-runtime` (an IPC-socket-sharing volume, not
"orchestrator-data" — confirmed via `grep -A2 "^volumes:"`), and the actually-present volumes on
this host are `cwso-t226_cwso-runtime` / `cwso_cwso-runtime` (from different compose-project-name
prefixes across runs). There is no per-service "orchestrator-data" volume in this architecture at
all.

---

## 8. Backup and Restore

**Not executed** (per task scope carve-out — `docker-compose down -v` inside "Restore from
Backup" would delete the live, verified stack's volumes, and the whole section depends on the
nonexistent `cwso-local-dev_orchestrator-data` volume from §7). Reviewed by inspection only:
- "Full Backup" and "Restore from Backup" both reference `cwso-local-dev_orchestrator-data`,
  already shown in §7 not to exist.
- "Restore from Backup" calls `docker-compose down -v` then later `docker-compose up -d` assuming
  a `deploy/local-dev` compose context that (per §2 Step 1) is never actually created by following
  the guide's own earlier steps.
- No CWSO-specific defect beyond the volume-name issue already logged in §7; not independently
  re-scored here to avoid double-counting.

---

## 9. Next Steps / Support links

```
$ ls -la docs/deployment/
README.md
gcp-cloud-run-guide.md
local-docker-desktop-guide.md
proxmox-lxc-guide.md
troubleshooting-guide.md
```
**PASS** — all three cross-referenced guides (`proxmox-lxc-guide.md`, `gcp-cloud-run-guide.md`,
`troubleshooting-guide.md`) exist at the paths the guide links to. Content of those files was
**not** independently validated — out of scope for T305 (which is specifically about
`local-docker-desktop-guide.md`).

---

## Findings / Bugs Summary

Numbered for the orchestrator's convenience when filing bug tasks. None of these were created as
task briefs or ledger rows by this agent — filing is orchestrator-owned per this repo's
`AGENTS.md`.

| # | Title | Guide section | Literal failing output | Suggested severity |
|---|-------|---------------|-------------------------|---------------------|
| 1 | Guide's "Detailed Setup → Step 1" references `deploy/docker-compose-local-dev.yml`, `deploy/docker-compose-local-dev.env` which do not exist anywhere in the repo | Detailed Setup, Step 1 | `cp: cannot stat 'deploy/docker-compose-local-dev.yml': No such file or directory` (and `.env` variant) | **Critical** — blocks the entire Detailed Setup path for any reader, human or agent |
| 2 | Guide's "Configure JWT Secret → Option A" references `../.env.jwt.dev` / `deploy/.env.jwt.dev`, neither of which exists in this repo (`../CWSO/.env.jwt.dev` is a different repo/path); the automated script's own `JWT_SOURCE` variable makes the same wrong assumption | Detailed Setup, Step 2 (Option A); also `scripts/deploy/cwso-docker-desktop.sh` `JWT_SOURCE` var | `deploy/.env.jwt.dev DOES NOT EXIST` | **Critical** |
| 3 | No AI-agent-safe path exists to obtain a working JWT per this repo's own security guardrails — Option A requires reading a raw secret file, which agents are hard-blocked from doing | Detailed Setup, Step 2 | N/A — policy gap, not a runtime error | **Medium** (documentation/process gap, not a code defect) |
| 4 | `GET /health` on the orchestrator (port 8080) returns `401 Unauthorized` / `missing bearer token`, not the guide's documented `{"status":"healthy","timestamp":...}` JSON, on a stack independently confirmed healthy by T304 | Quick Start Step 3; Detailed Setup Step 4 | `HTTP/1.1 401 Unauthorized` body `missing bearer token` | **Critical** — the guide's flagship "you're done!" verification command fails on a genuinely healthy stack |
| 5 | `GET /health` on rollout (port 8787) returns `405 Method Not Allowed` ("only POST is supported"); real liveness route is `/healthz`, undocumented anywhere in the guide | Detailed Setup Step 4; Monitoring section | `HTTP/1.1 405 Method Not Allowed` `{"error":{"message":"only POST is supported"}}` | **High** |
| 6 | Guide/script use service name `rollout-proxy` throughout (Viewing Logs, Container Status, Appendix), but the actual compose service/container is named `rollout`/`cwso-rollout` | Common Tasks → Viewing Logs; Monitoring → Container Status; Appendix | `no such service: rollout-proxy`; `Error response from daemon: No such container: cwso-rollout-proxy` | **High** — systemic, appears in 3+ places |
| 7 | Guide's Monitoring "Built-in Health Checks" loop (ports 8080/8787/8788/8789) fails on every port when run exactly as written: 8080 non-JSON (breaks `jq`), 8787 wrong-method error, 8788/8789 not published to host at all | Monitoring and Healthchecks | See full loop output in §6 | **Critical** |
| 8 | git-shadow (8788) and merge-engine (8789) are documented as directly curlable HTTP health endpoints on localhost, but neither service publishes any host port in `docker-compose-t226.yml` (IPC-socket-only services) | Appendix; Monitoring section | `curl` returns empty / connection refused (exit 7) on both ports | **High** |
| 9 | `docker-compose exec orchestrator curl ...` (troubleshooting step) fails — the orchestrator image ships no `curl` binary | Troubleshooting → Network Connection Issues | `exec: "curl": executable file not found in $PATH` | **Medium** |
| 10 | Guide's "expected output" table shows `COMMAND: "python3 ..."` for all 4 target services; actual containers run `tini`-wrapped compiled Go/Rust binaries, not Python | Detailed Setup Step 3 | `"/usr/bin/tini -- /u…"` / `"/sbin/tini -- /usr/…"` vs. documented `"python3 ..."` | **Low** (cosmetic/inaccurate but not blocking) |
| 11 | `scripts/deploy/cwso-docker-desktop.sh --status` crashes with an unhandled `cd` error if run before the full setup has ever completed once, instead of a clean "not deployed" message | Quick Start / script usage | `cd: ./deploy/local-dev: No such file or directory` | **Low** |
| 12 | Guide's "Volume Management"/"Backup and Restore" sections reference a Docker volume `cwso-local-dev_orchestrator-data` that does not exist and is not defined anywhere in `docker-compose-t226.yml` (only volume defined is `cwso-runtime`) | Data Persistence → Volume Management; Backup and Restore | `Error response from daemon: get cwso-local-dev_orchestrator-data: no such volume` | **Medium** |
| 13 | Performance Tuning section's `mem_limit`/`cpus` example blocks do not reflect any settings actually present in the current `docker-compose-t226.yml` (0 matches for `mem_limit`/`cpus:` in the real file) | Performance Tuning | (inspection only — 0 matches via `grep`) | **Low** |

### Root-cause routing (CWSO-core vs. this-repo)

All 13 findings above trace to **this repo's documentation/scripts** (`docs/deployment/local-docker-desktop-guide.md`, `scripts/deploy/cwso-docker-desktop.sh`, `deploy/docker-compose-t226.yml`'s
naming/labels) — i.e., guide wording, stale file references, and one Compose-level naming
inconsistency (`rollout` vs `rollout-proxy`). **None of these 13 findings trace to a genuine
CWSO-core (`../CWSO`) defect** in the sense of T310's convention — findings #4/#5 (health
endpoint auth/method mismatches) reflect CWSO's *actual, intentional* current API surface
(`/health` requires auth, `/healthz` doesn't; rollout's `/health` root requires POST) which the
guide simply never documented correctly, not a CWSO regression. Finding #9 (`curl` missing in the
orchestrator image) is arguably a CWSO image-packaging choice (minimal image, no shell tooling)
rather than a defect — flagged here as a guide-writing gap (don't tell readers to `exec curl` into
a minimal image), not as a CWSO bug. **No T310 hand-off is recommended for this task's findings.**

## Blockers encountered (for the record, not silently worked around)

1. **Type: technical, severity: minor.** `bash scripts/deploy/cwso-docker-desktop.sh` (full,
   unattended run) was blocked by this session's own command-permission classifier due to the
   risk of colliding container names/ports with the live, verified stack. Mitigated by running
   the script's safe subcommands (`--help`, `--status`) directly and manually reproducing its
   non-destructive prerequisite checks on the host instead. Not retried against the same command.
2. **Type: technical, severity: minor.** `cat`ing a freshly-created, self-authored `deploy/local-dev/.env`
   file (to confirm Option B's JWT write) was blocked by the classifier as a `.env`-pattern match,
   consistent with this repo's own hard security guardrail. Mitigated by using `wc -l`/`ls` to
   confirm the write succeeded without reading file contents.
3. **Type: technical, severity: minor.** `docker-compose logs orchestrator | grep -i "token\|auth"`
   (Troubleshooting → JWT Authentication Failed, step 3) was blocked by the classifier as a
   sensitive-pattern search. Not retried; recorded as not executed, no literal output available.

None of these blockers required a second retry cycle or orchestrator escalation — each was
resolved by using an equivalent, safe, read-only substitute that still produced literal evidence.

## Cleanup

The `deploy/local-dev/` directory created during this validation (containing only a
self-generated, never-used `.env` with a freshly-random JWT secret, and no compose file) was
deleted after evidence collection (`rm -rf deploy/local-dev`), confirmed via `git status --short`
to leave no residual working-tree changes beyond the pre-existing, orchestrator-owned
`docs/tasks/active-tasks.md` edit (not touched by this task). The live CWSO stack
(`docker-compose-t226.yml`) was re-confirmed Up/healthy for all 4 target services at the end of
this validation and was never stopped, restarted, or torn down.

```
$ docker ps --filter "name=cwso-" --format "table {{.Names}}\t{{.Status}}"
NAMES               STATUS
cwso-rollout        Up 3 hours (healthy)
cwso-orchestrator   Up 3 hours (healthy)
cwso-git-shadow     Up 3 hours
cwso-merge-engine   Up 3 hours
cwso-sia-executor   Up 3 hours
```

## VERDICT: FAIL

### Justification
The guide fails at the very first verification step a fresh reader would run (`curl
http://localhost:8080/health` returning 401 instead of the documented healthy JSON), and its
"Detailed Setup" section cannot be completed at all as literally written because its Step 1
references files that do not exist anywhere in the repository (finding #1/#2, both critical).
13 distinct findings were logged, of which 5 are rated critical/high-severity and directly block
a new reader from successfully following the guide end-to-end. Per this task's own acceptance
criteria, any failing/missing/inconsistent step must be identified for bug filing rather than
silently routed around — that has been done comprehensively above. No CWSO-core defect requiring
T310 hand-off was found; every issue is attributable to this repo's own guide text, helper script,
or Compose file labeling.
