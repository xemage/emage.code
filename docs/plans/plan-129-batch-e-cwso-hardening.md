# plan-129 — LOW batch E: CWSO hardening

**Created:** 2026-11-02
**Based on:**
- `docs/artifacts/tracked-debt-register-v4.md` § 5 (batch E, 23 ids)
- `docs/artifacts/tracked-debt-register-v3.md` and the reviews `security-review-t694*`, `security-review-t695*`, `security-review-t696*` and `security-review-t697-t699*`
- the user's answers of 2026-11-02, verbatim: "E go"; and, for SEC-T699-04, "Tie to the bearer (Recommended)"

**Scopes:** `T726`, `T727`, `T728`.
**Repositories:** emage.code (T726, this plan, the ledger) and CWSO, `em-age/emage.code.cwso` (T727, T728). The CWSO work follows the T695/T696 pattern: an agent branch from CWSO `origin/develop`, then an MR into CWSO `develop`. The orchestrator merges it with a green pipeline and a pinned sha. The emage.code ledger tracks it.

## Goal

Close the CWSO LOW items before the `paste` acceptance review, which is due **2027-01-31** (SEC-T696-06), and record the user's conditions for the plain-HTTP acceptance (SEC-T699-04).

## Task Decomposition

1. **T726** (devops-engineer, emage.code): the CWSO helper scripts.
   - SEC-T694-04: `implementation/scripts/sia-executor.py` takes `--jwt-secret` on argv, and argparse's `allow_abbrev` echoes values. Read the secret from a file or the environment, remove the argv form or warn on it, and set `allow_abbrev=False`.
   - SEC-T694-05: error messages in `scripts/cwso-deploy-helper.sh` and `scripts/mint-cwso-jwt.py` can echo values or paths. Name variables only.
   - SEC-T694-06: `cwso-deploy-helper.sh export --secret-file` prints the secret to stdout by design. Require an explicit flag or a non-tty check, and document it.
   - SEC-T694-07: the helper and the minter parse the secret file differently. Use one rule.
   - SEC-T694-08: `scripts/deploy/cwso-proxmox-setup.sh` writes the raw value into the `.env` line that compose reads. Fix the quoting, and keep the value at rest with mode 600; document it.
   - SEC-T694-09: in `tests/functional/test_cwso_jwt_secret_source.py`, add the missing cases: `--secret=VALUE`, an unknown argument that echoes, and checks on literal text.
   - SEC-T694-11: `cwso-proxmox-setup.sh` and `cwso-deploy-helper.sh` download `get.docker.com` and `releases/latest` unpinned and without checksum, and use fixed `/tmp` paths. Pin a version, verify a checksum, and use `mktemp`. Any download that cannot be pinned is reported with a reason.
   - *Acceptance:* each item is fixed with a test or reported with a reason. No secret value appears in any test output. All gates and the suite pass.
2. **T727** (devops-engineer, CWSO): the server configuration.
   - SEC-T695-03: `CWSO_ALLOWED_ORIGINS` entries are not validated (`config.go:143`, `http.go:186-189`). Reject `*`, `null`, entries without a scheme or host, and entries with a path at `Load`. Log the effective list. Add tests.
   - SEC-T695-07: short HS256 secrets are accepted (`config.go:242-245`). Enforce a minimum length of 32 bytes and fail at startup, with a test.
   - SEC-T695-10: the plain HTTP listener is published on all interfaces by default (`transport/http.go`, `docker-compose.yml`). Bind to `127.0.0.1` by default, with an explicit opt-in for other interfaces.
   - **The user's own deployment** (the CWSO server, reached over the LAN under TD-T697-07) must keep working. Document the opt-in in the CWSO deployment docs, state what an operator must set, and do not change any server or host.
   - *Acceptance:* each item is fixed with tests. The CWSO CI passes. The opt-in is documented.
3. **T728** (devops-engineer, CWSO): CI, build and supply chain.
   - SEC-T695-05: the e2e jobs use fixed project and container names, and `down -v` on project `cwso` could remove a non-CI stack on the shared `dind` daemon. Use per-job names.
   - SEC-T695-09 and SEC-T696-01: `scripts/release-assets.sh` builds Rust with 1.86, while CI uses 1.87, and calls `cargo build` without `--locked`. Use one toolchain and `--locked`.
   - SEC-T696-02: Rust is pinned at 1.87, behind current stable. Bump it to a current stable that has been out for at least two weeks.
   - SEC-T696-03: the runtime base images `alpine:3.20` and `debian:bookworm-slim` are old, and there is no OS-package scan. Move to current bases, and add a scan job or report why not.
   - SEC-T696-04: base images are pinned by tag. Pin them by digest.
   - SEC-T696-05: `deploy/Dockerfile.orchestrator:8-9` has `go mod download || true` and a `go.sum*` glob. Fail on error and require `go.sum`.
   - **SEC-T696-06, the review due 2027-01-31: do it now.** Check RUSTSEC-2024-0436 (`paste`, unmaintained): is a maintained replacement available, and which crate pulls `paste` in? Either replace it, or record the review result and a new review date in `services/.cargo/audit.toml`. Also report the new date so the register can track it.
   - SEC-T696-07: (a) the explicit wasmtime feature list must be re-diffed on every bump; add a CI check or a test that pins the list. (b) There is no fuel or epoch interruption; this stays tracked until untrusted modules are accepted.
   - *Acceptance:* each item is fixed or reported with a reason, and `cargo audit` and the CWSO CI pass.

T726 runs in emage.code; T727 and T728 run in CWSO worktrees. T727 and T728 may both touch `docker-compose.yml`: T727 owns its port binding, and T728 owns image references and CI files. A Security Engineer reviews all three.

## Items without code change

- **SEC-T699-04 / TD-T697-07** (user decision, 2026-11-02: "Tie to the bearer (Recommended)"). The acceptance of plain HTTP on the LAN stays MEDIUM. It ends when the current CWSO bearer token expires (**2027-01-29**), and the user must renew it with each new token. It ends at once if CWSO becomes reachable from outside the LAN, if the token's role widens beyond orchestrator, or if a token leak is suspected.
- **SEC-T694-10 and SEC-T695-06** (incidents, process). The process rule is in force: only presence checks such as `git grep -l` and counts are allowed, and secret values are never printed. The local transcripts remain user action A-15. Both stay tracked under A-15, with no code change.
- **SEC-T694-12** (operational, user A-11). No such container exists on the CWSO server; other hosts are **(unverified)**. It stays a user action.

## Constraints

- Subagents never merge, tag or release.
- Never read or print a secret value: no `.env*`, no `/dev/shm/emage-secrets/`, no CWSO secret file. Use presence checks only.
- Do not change any server, host or running container.
- Never open `tests/golden/held-out/`.
- In the CWSO checkout at `/home/emage/Code/emage/CWSO`, do not touch the 411 local modifications. Work only in the worktrees.

## Outcome (2026-11-02)

- **Tasks.** T726 to T728 are done.
  - T726 is merged here.
  - T727 and T728 went into CWSO through MR !218, squash-merged as CWSO develop `6630ecb`. CWSO pipeline 3016294206 passed all 19 jobs: the four e2e jobs, `security:image-scan`, `check:image-pins`, `rust:audit` and `go:audit`.
- **Batch-E ids.**
  - Closed: SEC-T694-04 to -09 and -11; SEC-T695-03, -05, -07, -09 and -10; SEC-T696-01 to -06; SEC-T696-07(a).
  - SEC-T696-06: `paste` is removed, so the review due 2027-01-31 is closed.
  - SEC-T699-04: decided by the user ("Tie to the bearer (Recommended)"). The conditions are in § Items without code change.
  - Still tracked: SEC-T696-07(b), SEC-T694-10, SEC-T694-12 and SEC-T695-06 (process and user actions A-11 and A-15).
- **Security review.** `docs/artifacts/security-review-t726-t728-batch-e-v1.md` gives PASS, with no MEDIUM or higher. 11 LOW findings are tracked: SEC-T726-01 to -03, SEC-T727-01 to -05 and SEC-T728-01 to -03.
- **New tracked LOW items from the task reports.**
  - TD-T726-01: `implementation/scripts/dispatch-test-sia.py` still accepts `--jwt-secret` on argv.
  - TD-T726-02: the default Proxmox template is Ubuntu 20.04. Whether Docker Engine 29.9.2 is packaged for it is **(unverified)**.
  - TD-T728-01: the CWSO Rust release binaries now need glibc 2.41. This belongs in the next CWSO release notes.
  - TD-T728-02: Trivy 0.76.1 (the eMudhra CA mitigation) can be adopted from 2026-11-04. A Go 1.26 backport of the CA fix is **(unverified)**.
  - TD-T728-03: `docker:27.5.1` is out of support. An upgrade needs the runner daemon's version first.
- **User actions.** All three must be in place before the next redeploy of the CWSO server (`git pull` plus `docker compose up -d`), or it loses LAN access:
  - set `CWSO_HTTP_PUBLISH_ADDR=0.0.0.0` in `deploy/.env`, or add `ports: !override ["8080:8080"]` to the local override;
  - make sure the JWT secret is at least 32 bytes;
  - make sure the `CWSO_ALLOWED_ORIGINS` entries pass the new checks.
- **Process deviations.** T728 broke the brief's "do not change any host" constraint. It built images and ran test containers on the remote Docker host this machine's Docker client uses. It removed everything it created except the Docker build cache. `rustup` on this machine updated itself from 1.29.0 to 1.29.2. No server or running deployment was changed.
- **Token use against budget.**

  | Task | Used | Budget |
  |---|---|---|
  | T726 | about 139k | 100k |
  | T727 | about 161k | 100k |
  | T728 | about 218k | 120k |
  | Security review | about 224k | 80k |
