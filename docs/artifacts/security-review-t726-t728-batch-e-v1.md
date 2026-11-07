# Artifact: security-review-t726-t728-batch-e-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer, read-only. The reviewer had no shell and read the diffs from files the orchestrator exported. The orchestrator recorded this artifact from the reviewer's report.
- **Gate**: security. **Date**: 2026-11-02.
- **Target**:
  - T726 on the emage.code branch `docs/plan-129-batch-e`, at `7e799c12`.
  - T727 and T728 on the CWSO integration branch `chore/plan-129-batch-e`, at `5deb358a` (CWSO MR !218).
- **Based on**:
  - `docs/plans/plan-129-batch-e-cwso-hardening.md`
  - `docs/tasks/task-T726.md` to `task-T728.md`
  - `security-review-t694*`, `-t695*`, `-t696*`
  - the emage.code CWSO helper scripts
  - the CWSO orchestrator config and transport, compose files, `.gitlab-ci.yml`, Dockerfiles, Rust manifests and `services/.cargo/audit.toml`

## Verdict: PASS

- No CRITICAL, HIGH or MEDIUM finding.
- No breach of an Immutable Security Constraint.
- No required control is removed or weakened.
- Every brief item is fixed or reported with a reason: T726 covers SEC-T694-04 to -09 and -11; T727 covers SEC-T695-03, -07 and -10; T728 covers SEC-T695-05, -09 and SEC-T696-01 to -07(a).
- The PASS holds because the eleven LOW findings below are tracked as debt. This artifact is the record of that tracking.

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 11 | 0 | 11 (tracked, section 3) |

## 1. Rulings on the changes

### T726

- **`sia-executor.py`.**
  - The secret never travels on argv. `--jwt-secret` is removed; the secret comes from `--jwt-secret-file` or `CWSO_JWT_SECRET`.
  - `allow_abbrev=False` is set.
  - Unknown arguments are counted, never echoed.
  - No caller breaks: `docker-compose-t226.yml` passes the secret through the environment.
- **Error messages** in all three scripts name the option or the variable, never a value or a path.
- **`export --secret-file`** needs `--print-secret` and refuses to print to a terminal.
- **Secret files.** All four readers apply one rule: the first line that is not empty and does not start with `#`, trimmed.
- **The compose `.env` line** is single-quoted, with `\'` escaped. A value containing a backslash is refused before anything is written. The file is mode 600 and is never world-readable at any point.
- **Downloads** are pinned and sha256-checked inside `mktemp -d`, and fail closed:
  - docker-install at a fixed commit;
  - Docker Engine 29.9.2;
  - compose v5.6.1, with a separate checksum for each architecture.
- **Tests** compare sha256 digests, so no value is ever printed.

### T727

- **Origins.** Origin entries are validated and normalized when the configuration loads.
  - Rejected: `*`, `null`, an entry without a scheme or host, userinfo, a path or trailing `/`, a query or fragment, and a bad port.
  - Entries are lower-cased and de-duplicated.
  - Every bypass tried fails closed: case, a trailing dot, IDN, a port, a duplicate, a wildcard host. The incoming `Origin` header is lower-cased and must match exactly.
- **JWT secret.** The minimum length is 32 bytes. The error message gives neither the value nor its length. The `-transport http` flag path is checked too.
- **Listening address.** The default is loopback: the binary listens on `127.0.0.1:8080`, and compose publishes on `${CWSO_HTTP_PUBLISH_ADDR:-127.0.0.1}`. Opting in needs an explicitly named variable. The CI override is used only through `-f` and through `phase2-integration.py` (SEC-T727-03).

### T728

- **e2e isolation.**
  - Each e2e job runs as its own compose project, `cwso-ci-$CI_JOB_ID`.
  - Fixed container names are reset.
  - The cleanup is anchored to `^cwso-ci-[0-9]+$`.
- **Image pinning.**
  - All 33 references are pinned by digest. A wrong digest fails the pull, so the pinning fails closed.
  - `check-image-pins.sh` fails closed on odd forms (SEC-T728-02).
- **Trivy.**
  - Trivy 0.76.0 runs as a blocking job.
  - That version is outside the compromised range of GHSA-69fq-xp46-6x23 / CVE-2026-33634 (binary v0.69.4; Docker Hub tags 0.69.5 and 0.69.6).
  - The job does not gate publication (SEC-T728-01).
- **Go modules.** `go.sum` is required, followed by `go mod download && go mod verify`.
- **Rust.**
  - One toolchain, 1.99.1, is used everywhere, with `--locked`.
  - arrow and parquet are at 60.0.0. `paste` is gone from the lockfile, and the audit ignore list is empty. The SEC-T696-06 review date is retired.
- **wasmtime.** A new test pins the wasmtime version and the declared feature list (SEC-T728-03).
- **Base images.** The images move to Debian trixie and Alpine 3.24, keeping uid 100 / gid 101. The orchestrator's ids are guarded by `security:ipc-gid-drift`.
- **Release binaries** now need glibc 2.41. This is a compatibility point, not a security one: state it in the release notes or build with musl.

## 2. OWASP coverage

| Category | Findings |
|---|---|
| A01 Broken Access Control | SEC-T727-01 |
| A04 Insecure Design | SEC-T727-03 |
| A05 Security Misconfiguration | SEC-T727-04, SEC-T727-05 |
| A06 Vulnerable Components | SEC-T728-02 |
| A07 Auth Failures | SEC-T726-03 |
| A08 Data Integrity | SEC-T728-01, SEC-T728-03 |
| A09 Logging | SEC-T726-01, SEC-T726-02, SEC-T727-02 |
| A02, A03, A10 | 0 |

## 3. Findings (all LOW, tracked as debt; owner devops-engineer)

| Id | Location | Finding | Fix (reviewer) |
|---|---|---|---|
| SEC-T726-01 | `scripts/cwso-deploy-helper.sh:218-222` | `reject_argument` prints any token that starts with `-` and contains no `=` in full. A secret that starts with `-`, passed bare, would be printed. | Print the name only if it matches `^--?[A-Za-z][A-Za-z0-9-]{0,40}$`; otherwise print "(not shown)". Add a test. |
| SEC-T726-02 | `sia-executor.py:835`; `mint-cwso-jwt.py` `_load_secret_from_file` | `Path.is_file()` runs outside the `try`. A `PermissionError` on Python 3.13 and earlier could print the path in a traceback. | Move the check inside the `try`, catch `OSError`, report only the exception type, and add a test for EACCES. |
| SEC-T726-03 | the four readers; `docker-compose-t226.yml:177`; CWSO `config.go:127-128` | The one-rule guarantee holds only for the tested layouts. Unicode whitespace is handled differently. The t226 entrypoint and the CWSO server read the whole file. The effect is an auth failure, not a disclosure. | Allow only printable ASCII in secrets and refuse anything else in every reader. |
| SEC-T727-01 | CWSO `transport/http.go:667, 683-697` | With no `Origin` header, the Host check splits at the first `:`. An IPv6 entry reduces to `[`, so any IPv6 Host passes. The JWT still applies. | Compare `url.Parse(o).Hostname()` with `net.SplitHostPort(r.Host)`, and add a test. |
| SEC-T727-02 | CWSO `config/http_security.go:69` | The rejection message quotes the entry as given, so the password in an entry with userinfo goes to the logs. | Print the index and the reason only, or `u.Redacted()`. |
| SEC-T727-03 | CWSO `scripts/phase2-integration.py:35-39` | The CI override is selected by the generic `CI` variable. A developer machine that exports `CI=true` then publishes 8080 on all interfaces. | Select it on `GITLAB_CI=true` or on a dedicated `CWSO_COMPOSE_CI=1`. |
| SEC-T727-04 | CWSO `deploy/docker-compose.yml:272`; `docs/user/README.md` | Before Docker Engine 28, hosts on the same L2 network could reach loopback-published ports (moby/moby#45610). The user's Engine version is unknown **(unverified)**. | Document Engine 28 or later as required for the loopback guarantee, or check it in `make up`. |
| SEC-T727-05 | CWSO `deploy/docker-compose.yml:472-473` | Pre-existing: the opt-in `rollout` service publishes 8787 on all interfaces. | Publish on `"${CWSO_ROLLOUT_PUBLISH_ADDR:-127.0.0.1}:8787:8787"`. |
| SEC-T728-01 | CWSO `.gitlab-ci.yml:269-296, 504-536` | The image scan does not gate `deploy:registry`. That job rebuilds the images instead of pushing the scanned ones, and tag pipelines are not scanned. | Add the scan and the audits to the `needs` of `deploy:registry`, scan on tags, and push the scanned image. |
| SEC-T728-02 | CWSO `config/config.go:154`; `scripts/check-image-pins.sh:24-39` | The sandbox default `alpine:3.20` is unpinned and end-of-life. The guard also misses the long `image:` form, CI `services:`, `COPY --from=`, and `docker run` in scripts and the Makefile. | Pin the default, and widen the guard to every image-like reference in the repo, with an allow-list. |
| SEC-T728-03 | CWSO `services/cwso-sparse/tests/wasmtime_features.rs:96-120` | The test checks the declared features, not the features Cargo resolves. Feature unification could bring `cache` and `profiling` back. | Also assert that `resolve.nodes[].features` of wasmtime contains none of the excluded features. |

## 4. Not verified by the reviewer

- That each image digest matches its tag.
- The upstream sha256 values.
- The Rust 1.99.1 release date.
- The uid/gid claim.
- Whether the compose round-trip test ran.
- Docker 29.9.2 on the Ubuntu 20.04 template.
- That `cargo audit` and the CWSO pipeline pass. The orchestrator checks the pipeline before the merge.
