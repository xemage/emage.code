# Artifact: security-review-t695-cwso-ci-secret-compose-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer. Read-only: no shell and no git, so no diff, test or pipeline run. `grep_content` failed on every call, so files were read directly. Recorded by the orchestrator from the reviewer's reports.
- **Gate**: security. **Date**: 2026-10-31.
- **Target**: T695 in the CWSO repository (`em-age/emage.code.cwso`, MR !216), branch `agent/devops-engineer/T695`. First review at `480e434` (parent `05ef236`); re-check at `72b0d5a` (`480e434` → `ab46f7b` → `72b0d5a`).
  - `480e434`: CI generates a JWT secret per job (`.ci-jwt-secret` via `!reference`); three docs files are redacted to `<redacted 2026-10-31, rotated>`; `restart: unless-stopped` on orchestrator, git-shadow and merge-engine; `CWSO_ALLOWED_ORIGINS` becomes configurable with today's list as the default.
  - `ab46f7b`: the Rust Dockerfiles copy `services/Cargo.lock` and build with `--locked`; `cargo test` in CI and `scripts/release-assets.sh` get `--locked`. This fixes the CI build failure (unlocked builds picked up uuid 1.29.0, which needs rustc 1.89).
  - `72b0d5a`: the README section "Reach CWSO from another host" and the compose comment require an SSH tunnel or a TLS proxy; the CI override isolates the CI stack.
- **Based on**: `docs/tasks/task-T695.md`; in the CWSO worktree: `.gitlab-ci.yml`, `deploy/docker-compose.yml`, `deploy/docker-compose.ci.yml`, the three Rust Dockerfiles, `scripts/release-assets.sh`, `docs/user/README.md`, `orchestrator/internal/config/config.go`, `orchestrator/internal/transport/http.go`, `scripts/cwso-token.sh`, `scripts/cwso-smoke-test.sh` (1-90).
- **Orchestrator checks relied on**: no tracked file at `480e434` or `72b0d5a` holds the dead value (pattern-file procedure, names only); `docker compose config --quiet` passes for base and base plus CI; `glab ci lint` passes.

## First review at 480e434: FAIL (0 critical, 0 high, 1 medium, 7 LOW)

No Immutable Security Constraint is breached and no literal secret is added.

- **CI secret: no finding.** `.gitlab-ci.yml:52` generates 32 bytes from `/dev/urandom` as 64 hex characters, and `:53` checks the length. The key has 256 bits of entropy (RFC 7518 §3.2). GitLab prints command text, not values; there is no `set -x`; the e2e jobs declare no artifacts; `.env.jwt.dev` is written under `umask 077`. Residual exposure for a dead per-job value: `CI_DEBUG_TRACE`, and `docker inspect` on the shared socket while the job runs.
- **Origin list: fails closed for `*` and empty values**; `null` is accepted (SEC-T695-03).
- **DNS rebinding: adding a LAN IP does not weaken it.** A rebinding page sends its own host name in `Origin` and `Host`, never the IP literal.

| Id | Grade | Finding | Recommendation |
|---|---|---|---|
| SEC-T695-01 | MEDIUM (forces FAIL under § Security Gate Protocol item 2) | `docs/user/README.md:224-237` and `deploy/docker-compose.yml:272-281` documented cross-host access over plain HTTP (`http://<lan-ip>:8080`). Clients send the bearer JWT in cleartext; the listener is plain HTTP only (`http.go:151-163`); `security-guidelines.md` § API Security requires HTTPS. | Require an SSH tunnel or a TLS-terminating proxy for cross-host access, warn about cleartext tokens, use an `https://` example. |
| SEC-T695-02 | LOW | The README read as if the Origin list limits who can reach CWSO. Non-browser clients send any Origin; the port is published on all interfaces (`docker-compose.yml:264`); `/healthz` is outside the middleware. The JWT is the only real access control. | State that the Origin list protects browsers, not the network; document the bind to `127.0.0.1`. |
| SEC-T695-03 | LOW | `CWSO_ALLOWED_ORIGINS` entries are not validated (`config.go:143`, `http.go:186-189`): `null` admits `Origin: null`; `http://` with an empty host may match an empty Host (unverified); IPv6 literals never match (fails closed). | Reject `*`, `null`, entries without scheme or host, and entries with a path at `Load`; log the effective list; tests. |
| SEC-T695-04 | LOW | `restart: unless-stopped` also applied in CI; an orphaned CI stack would survive restarts and hold port 8080 and the fixed container names. | `restart: "no"` in `docker-compose.ci.yml`; `down -v --remove-orphans` before `up`. |
| SEC-T695-05 | LOW | `config.go:127-132` reads `/run/secrets/jwt_secret` before the environment, and the CI override still mounted `cwso-jwt-secret`; a stale volume on a shared daemon would win over the per-job secret (fail-closed). The fixed project name means CI on a daemon with a real `cwso` stack would recreate its containers and delete its volumes. Stale `docker-compose.ci.yml:3-5,11`. | Drop the mount in CI; never run e2e on a daemon that hosts a real CWSO stack; delete the stale lines. |
| SEC-T695-06 | LOW (process) | The implementing agent printed the committed, now-dead value once in its own tool output; it may persist in local session transcripts. The value was rotated on 2026-10-31. | Agents check for presence only (`git grep -l`, counts) and never print matches; do not move the transcript into any committed artifact. |
| SEC-T695-07 | LOW (pre-existing) | `config.go:242-245` rejects only an empty JWT secret; a short HS256 secret is accepted. | Reject secrets shorter than 32 bytes at `Load`, with a test. |
| SEC-T695-08 | LOW | The public repository named a specific internal LAN address. | Use a placeholder or a documentation name. |

## Re-check 2026-10-31 (commit 72b0d5a)

**Verdict: CONDITIONAL_PASS** (0 critical, 0 high, 0 medium; 4 closed, 6 LOW open). The only condition is that the open LOW findings are tracked as debt with an owner and a deadline (this artifact is that record, per the user's LOW policy of 2026-10-23); the verdict is then PASS.

**Closed**
- **SEC-T695-01**: `README.md:226-251` forbids plain-HTTP cross-host access, warns that the token travels in cleartext, offers an SSH tunnel (preferred) or a TLS proxy, example `https://cwso.example.com`; the compose comment matches (`docker-compose.yml:272-286`).
- **SEC-T695-02**: `README.md:258-281` says the Origin list protects browsers, the JWT is the access control, `"8080:8080"` listens on all interfaces, and shows the `127.0.0.1` bind via a second `-f` file.
- **SEC-T695-04**: `docker-compose.ci.yml:19,27,30` set `restart: "no"` in CI; the README states the auto-restart on dev hosts (`README.md:283-285`).
- **SEC-T695-08**: reserved example name `cwso.example.com`; no LAN address remains (orchestrator check: no match for the address in either file).

**Partly closed**
- **SEC-T695-05**: in CI the orchestrator no longer mounts `cwso-jwt-secret` (`docker-compose.ci.yml:22-24`, `volumes: !override`), so the per-job secret is its only source. Still open (LOW, pre-existing): `jwt-secret-fix` still writes the volume in CI (harmless now), and the fixed project and container names keep the shared-daemon risk.

**New**

| Id | Grade | Finding | Recommendation |
|---|---|---|---|
| SEC-T695-09 | LOW | `--locked` makes the shipped builds match the audited `services/Cargo.lock`. Gap: `scripts/release-assets.sh:36` builds release binaries with `rust:1.86-bookworm` while CI uses 1.87, and `:30` uses `golang:1.23-bookworm` against `go.mod` `go 1.25.12` and CI's `golang:1.25.13` (pre-existing). | Pin `release-assets.sh` to the CI toolchains, or pin both through `rust-toolchain.toml` and `go.mod`. |
| SEC-T695-10 | LOW (pre-existing) | The listener is plain HTTP (`http.go:151-163`) and published on all interfaces by default (`docker-compose.yml:263-264`); since `72b0d5a` documented, cross-host requires a tunnel or TLS. | Default bind `127.0.0.1:8080:8080`, or native TLS. |

**Open LOW findings (tracked debt; owner: orchestrator, deadline: the next CWSO hardening batch)**: SEC-T695-03, -05 (residual), -06, -07, -09, -10.

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 1 | 1 (SEC-T695-01) | 0 |
| LOW | 9 | 3 (-02, -04, -08) | 6 (-03, -05, -06, -07, -09, -10) |

## Unverified

- The reviewer ran no diff, grep, build or pipeline; the orchestrator's checks and the CWSO pipeline result are recorded in `docs/tasks/task-T695.md`.
- Whether `services/Cargo.lock` is excluded by a `.dockerignore` (the implementing agent built all three images locally with `--locked`, exit 0).
- Whether a `rust-toolchain.toml` exists; which Go toolchain `release-assets.sh` actually uses.
- The Compose version on the CI image (`!override` needs Compose 2.24.4 or later).
- Runner details (`after_script` on cancel, job concurrency on the shared daemon, stale volumes).
- Go `net/http` behaviour for an empty Host on HTTP/1.0.
- Whether `/dashboard` and the rollout routes sit behind the Origin middleware and the JWT.

## Re-check 2026-10-31 (commit 519d2a2)

**Based on**: `72b0d5a` -> `6dc114b` -> `519d2a2` (the merge of CWSO develop, which contains T696), files read at HEAD. CWSO pipeline 3011684701 at `519d2a2` green, all e2e jobs included (orchestrator); merged as CWSO develop `5869cc5`; the orchestrator confirmed that no tracked file on CWSO develop holds the dead value.

**Verdict: CONDITIONAL_PASS -> PASS** (0 critical, 0 high, 0 medium, 6 LOW open; closed: 01, 02, 04, 08). No new finding. The condition (the open LOW findings tracked as debt) is met by this artifact.

- `6dc114b`: `resource_group: cwso-e2e-docker` (`.gitlab-ci.yml:300, 342, 398`) serializes the stack jobs; `down -v --remove-orphans` before `up` (`:309, 348, 404`) removes stacks left by killed jobs (completes the CI part of SEC-T695-04); govulncheck pinned (`:184-186`, v1.9.0 after the merge), checksum-verified by `go install`.
- The secret handling is unchanged by the merge (generator `:50-53`; `.env.jwt.dev` under `umask 077` `:363, 409`; the CI override without `cwso-jwt-secret` and with `restart: "no"`, `deploy/docker-compose.ci.yml:17-30`).
- **SEC-T695-05 (LOW, residual): wider, grade unchanged.** Each e2e job now runs `down -v` on project `cwso` on the shared runner daemon before its own `up`, so a non-CI `cwso` stack on that daemon would lose its containers and volumes at the start of every e2e job. Needs a misconfiguration (a real stack on the CI `dind` daemon). Recommendation: say in the `.e2e-base` comment (`:289-295`) and the runner docs that the `dind` daemon must never host a non-CI `cwso` stack; longer term a per-job project name without `container_name` in CI.
- **SEC-T695-09 (LOW): narrower.** The Go part is resolved (`scripts/release-assets.sh:30` uses `golang:1.26.10-bookworm`). Still open: `release-assets.sh:36` builds with `rust:1.86-bookworm` while CI and the images use 1.87; CI does not run the script.
- Unchanged LOW: SEC-T695-03, -06, -07, -10.
- Not a security finding (reliability): the `down` in `e2e:smoke` and `e2e:projection` runs without `COMPOSE_PROFILES`, so containers of a killed `phase4` job might survive it (unverified); the resource group and the `.e2e-base` cleanup mostly cover this.
