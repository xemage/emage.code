# Artifact: security-review-t694-cwso-secret-source-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only). No shell, so no test run, no mutation run and no `git diff`; `grep_content` could not reach the worktree, so all findings come from reading files directly. Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-10-31.
- **Target**: T694, worktree `agent-devops-engineer-T694`, commit `5117ee0d` (parent develop `95727e1f`): the CWSO JWT secret comes only from `CWSO_JWT_SECRET` or an explicit `--secret-file`; no default file; the dead committed value is removed.
- **Based on**: `docs/tasks/task-T694.md` (develop `f23f0204`); the changed files (`scripts/mint-cwso-jwt.py`, `scripts/cwso-deploy-helper.sh`, `implementation/scripts/sia-executor.py`, `implementation/scripts/test-phase3.1.py`, `implementation/scripts/test-jwt-registration.py`, `scripts/deploy/cwso-docker-desktop.sh`, `scripts/deploy/cwso-proxmox-setup.sh`, `docs/tasks/task-T344.md`, `tests/functional/test_cwso_jwt_secret_source.py`); `implementation/runtime/cwso/mcp_client.py`; `deploy/docker-compose-t226.yml`; format of `docs/artifacts/security-review-t690-copilot-security-servers-v1.md`.
- **Orchestrator checks relied on**: the dead value occurs in no tracked file at `5117ee0d`; the value printed by the implementing agent was hash-verified as the dead pre-rotation value.

## Verdict at 5117ee0d: CONDITIONAL_PASS (0 critical, 0 high, 2 medium, 9 LOW)

No Immutable Security Constraint is breached by the change, and no required control is removed or weakened in the code under review.

Checked and found correct:
- `mint-cwso-jwt.py`: secret from the explicit `--secret-file` or `CWSO_JWT_SECRET` (`:49-60`); `allow_abbrev=False` with `parse_known_args`, unknown arguments counted but never echoed (`:85-128`); `--secret` cleanly gone.
- `cwso-deploy-helper.sh`: `verify` passes the secret through the environment, not argv (`:131-132`); `export` prints no secret line without `--secret-file` (`:88-97`); `%q` makes the one secret line safe for `eval` (`:92`).
- Proxmox path (`cwso-proxmox-setup.sh:401-402`): built-in `printf` piped to a fixed `pct exec … sh -c 'cat >> …'`; never on an external argv or inside a shell string; CR/LF stripped; container `.env` mode 600 (`:393`).
- Docker Desktop path: `chmod 600` before the append (`cwso-docker-desktop.sh:129-130`).
- No injection route: no `sed` or `eval` touches the value; every expansion is quoted.
- `test-jwt-registration.py`: literal gone; token, signature and bearer header redacted (`:83, :98, :135`).
- The test file uses only made-up values and strips the caller's `CWSO_JWT_SECRET` (`test_cwso_jwt_secret_source.py:43, 57-63`).

| Id | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T694-01 | MEDIUM (pre-existing, outside the change) | `deploy/docker-compose-t226.yml:165-177`: the `sia-executor` entrypoint runs `set -x`, so the expanded secret lands in the container log; `--jwt-secret "$$JWT_SECRET"` puts it on argv; a fixed fallback string is used when the secret file is missing. The changed scripts print those logs (`cwso-docker-desktop.sh:165,182,301`, `cwso-proxmox-setup.sh:438`). | Fix before merge: drop `set -x`, export `CWSO_JWT_SECRET` from `/run/secrets/jwt_secret` and fail when missing, exec without `--jwt-secret`, `logs --tail` of named services. |
| SEC-T694-02 | MEDIUM | `deploy/docker-compose-t226.yml:14-16` still takes the `jwt_secret` secret from the absolute default file `/home/emage/Code/emage/CWSO/.env.jwt.dev`; no service reads the `JWT_SECRET=` line the scripts write (`cwso-docker-desktop.sh:130`, `cwso-proxmox-setup.sh:401`). The deploy path does not meet T694's goal and the scripts' messages give false assurance. | Fix before merge: explicit compose secret source (`environment: CWSO_JWT_SECRET`, or `file: ${CWSO_JWT_SECRET_FILE:?…}`), stop writing the unused line, true messages. |
| SEC-T694-03 | LOW (outside the change) | `implementation/runtime/cwso/mcp_client.py:77-86` silently falls back to `../CWSO/.env.jwt.dev` / `./CWSO/.env.jwt.dev`; the functional test scans only `scripts/` and `implementation/scripts/`. | Remove the fallback, fail naming the variable, extend the scan to `implementation/runtime/` and `deploy/`. |
| SEC-T694-04 | LOW | `sia-executor.py:836-843` keeps `--jwt-secret` on argv (help text admits it); `parse_args()` with `allow_abbrev=True` (`:829-860`) can echo a mistyped flag's value. | Remove `--jwt-secret` or add `--jwt-secret-file`; `allow_abbrev=False` with a non-echoing unknown-argument path. |
| SEC-T694-05 | LOW | Error messages can echo values: `cwso-deploy-helper.sh:190` echoes any unknown argument; secret-file errors echo the given path (`cwso-deploy-helper.sh:60,66`; `mint-cwso-jwt.py:36,43`); argparse `--role`/`--ttl` errors echo the bad value (`mint-cwso-jwt.py:91-106`). | Print only the flag name (`${1%%=*}`); print a path only when it is an existing file. |
| SEC-T694-06 | LOW | `export --secret-file` prints the secret to stdout by design (`cwso-deploy-helper.sh:92`, documented `:7-8, :26-27`). | Refuse when stdout is a TTY, or drop secret printing from `export`. |
| SEC-T694-07 | LOW | Inconsistent secret-file parsing: the helper joins all lines (`cwso-deploy-helper.sh:64`), the minter takes the first non-comment line (`mint-cwso-jwt.py:38-41`). Fails closed. | One rule in both. |
| SEC-T694-08 | LOW (informational) | Raw value in `.env` (`printf 'JWT_SECRET=%s\n'`, `cwso-docker-desktop.sh:130`, `cwso-proxmox-setup.sh:401`); Compose `.env` parsing of special characters unverified; unused today (SEC-T694-02). | Fixed together with SEC-T694-02. |
| SEC-T694-09 | LOW | Test gaps: `--secret=VALUE` not tested; helper and `sia-executor.py` unknown-argument echo not tested; the Proxmox stdin and helper argv tests check literal text only (`test_cwso_jwt_secret_source.py:173-175, 216-219`); the `.env.jwt.dev` scan skips `implementation/runtime/` and `deploy/` (`:85-97`). | Tracked debt. |
| SEC-T694-10 | LOW (incident) | The implementing agent printed the dead pre-rotation value once in tool output through a broken heredoc, bypassing the brief's pattern-file procedure (`task-T694.md` §1.2, §3). Rotated (hash-verified) and already public in git history; the local session transcript holds it. Instance of SEC-T695-06. | Tracked under SEC-T695-06. Write pattern files with a non-printing tool, never through a heredoc in a shell call. |
| SEC-T694-11 | LOW (pre-existing) | `cwso-proxmox-setup.sh:342-343` runs `get.docker.com` unpinned; `:362-363` fetch `docker-compose` from `releases/latest` without checksum (A08); `cwso-deploy-helper.sh:15-16,139` use fixed `/tmp` paths. | Pinned versions with checksums; `mktemp -d`. |

## Unverified

- No test, gate or suite was run by the reviewer (the orchestrator's runs are recorded in `docs/tasks/task-T694.md`).
- `implementation/scripts/test-phase3.1.py` beyond line 99; the `docs/tasks/task-T344.md` change (the orchestrator's check covers the dead value).
- Whether `deploy/local-dev/.env` is git-ignored; how Compose treats a missing absolute `secrets.file` and special characters in `.env`; whether `secrets.<name>.environment` is supported by the installed Compose version; that `pct exec` forwards stdin.
- Retention of agent transcripts that hold the dead value.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01 | Yes | 0 |
| A02 | Yes | 4 (01, 02, 03, 06) |
| A03 | Yes | 1 (08) |
| A04 | Yes | 1 (07) |
| A05 | Yes | 1 (04) |
| A06 | Yes (no dependency change) | 0 |
| A07 | Yes | 0 |
| A08 | Yes | 1 (11) |
| A09 | Yes | 3 (05, 09, 10) |
| A10 | Yes (fixed URLs only) | 0 |

## Re-check 2026-10-31 (commit dd25a98c)

**Verdict: PASS** (0 critical, 0 high, 0 medium; MEDIUM 2 of 2 resolved; LOW 11 in total over both rounds, 1 resolved, 10 open and tracked as debt under the LOW policy of 2026-10-23). Read-only; nothing was run by the reviewer. The orchestrator's checks: `docker compose -f deploy/docker-compose-t226.yml config --quiet` passes with a made-up value (Compose 5.5.0); no `.env.jwt.dev` default under `scripts/`, `implementation/scripts/`, `implementation/runtime/` or `deploy/`; the gates and the full suite (recorded in `docs/tasks/task-T694.md`).

**Closed**
- **SEC-T694-01**: no `set -x` (`set -eu`, `docker-compose-t226.yml:171`); the secret is read from `/run/secrets/jwt_secret` with CR/LF stripped and never echoed (`:177`); a missing or empty secret exits 1 with a message naming only the variable (`:178-181`), no fallback string; `export CWSO_JWT_SECRET` (`:182`) and no `--jwt-secret` on argv (`:184-188`). The deploy scripts call `logs --tail=50` of named services (`cwso-docker-desktop.sh:24,167,184,304`, `cwso-proxmox-setup.sh:442`), pinned by `test_cwso_jwt_secret_source.py:237-244`.
- **SEC-T694-02**: `secrets: jwt_secret: environment: CWSO_JWT_SECRET` (`docker-compose-t226.yml:20-22`), no file default; Docker Desktop no longer writes the secret to disk (`cwso-docker-desktop.sh:129-133`), `--update` checks the variable first (`:266`); the helper's `up` and `reload` resolve and export the secret through the environment (`cwso-deploy-helper.sh:112-130`); Proxmox writes the key compose reads, `CWSO_JWT_SECRET=`, over stdin with built-in `printf` into a mode-600 `.env` (`cwso-proxmox-setup.sh:395, 401-406`). Tests at `:190-197, 219-235, 260-266`.
- **SEC-T694-03**: `implementation/runtime/cwso/mcp_client.py:77-83` raises a `ValueError` naming the variable, no file fallback; the scan covers `implementation/runtime/` and `deploy/` (`test_cwso_jwt_secret_source.py:58-63, 97-110`).

**Updated**
- **SEC-T694-08 (LOW, reworded)**: `cwso-proxmox-setup.sh:405` writes the raw value into the line compose reads, so quoting matters: compose's `.env` parser may alter a value with `$`, quotes, `#` or spaces (unverified; result is a failed authentication, not a leak). The value stays at rest in `/opt/cwso/repo/.env` (mode 600, root, inside the container; `.gitignore` coverage of that clone unverified), covered by the POC-DEBT note at compose `:23`. Recommendation: validate against a fixed character set (base64url) without echoing, or write it single-quoted with escaping.

**New**
- **SEC-T694-12 (LOW, operational)**: a `cwso-sia-executor` container created from the old compose definition keeps its xtrace output in its Docker log; if started while the default file held the new secret, that log holds the live secret, and `logs --tail=50 … sia-executor` could print it. Recommendation: remove or recreate such containers (`docker compose -f deploy/docker-compose-t226.yml down`, or `docker rm cwso-sia-executor`) before using the new scripts. Whether such a container exists is unverified.

**Still open (LOW, tracked as debt)**: SEC-T694-04, -05, -06, -07, -09 (reduced), -10 (recorded under SEC-T695-06), -11; plus -08 and -12 above.

**Unverified at the re-check**: whether `secrets.<name>.environment` reads a value that comes only from the project `.env` (the Proxmox path) and whether the standalone `docker-compose` from `releases/latest` supports it; whether `ps`, `logs` and `down` fail when the variable is unset; whether the CWSO orchestrator image logs the secret.
