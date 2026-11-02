# T728 — Batch E: CWSO CI, build and supply chain

**ID:** T728
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-02
**Completed:** 2026-11-02
**Based on:**
- `docs/plans/plan-129-batch-e-cwso-hardening.md` (task T728)
- The user's answer of 2026-11-02, verbatim: "E go"
- `docs/artifacts/tracked-debt-register-v4.md` (batch E rows) and v3; the T694 to T696 security reviews

## 1. What and why

(devops-engineer, CWSO): CI, build and supply chain.
   - SEC-T695-05: the e2e jobs use fixed project and container names, and `down -v` on project `cwso` could remove a non-CI stack on the shared `dind` daemon. Use per-job names.
   - SEC-T695-09 and SEC-T696-01: `scripts/release-assets.sh` builds Rust with 1.86, while CI uses 1.87, and calls `cargo build` without `--locked`. Use one toolchain and `--locked`.
   - SEC-T696-02: Rust is pinned at 1.87, behind current stable. Bump it to a current stable that has been out for at least two weeks.
   - SEC-T696-03: the runtime base images `alpine:3.20` and `debian:bookworm-slim` are old, and there is no OS-package scan. Move to current bases, and add a scan job or report why not.
   - SEC-T696-04: base images are pinned by tag. Pin them by digest.
   - SEC-T696-05: `deploy/Dockerfile.orchestrator:8-9` has `go mod download || true` and a `go.sum*` glob. Fail on error and require `go.sum`.
   - **SEC-T696-06, the review due 2027-01-31: do it now.** Check RUSTSEC-2024-0436 (`paste`, unmaintained): is a maintained replacement available, and which crate pulls `paste` in? Either replace it, or record the review result and a new review date in `services/.cargo/audit.toml`. Also report the new date so the register can track it.
   - SEC-T696-07: (a) the explicit wasmtime feature list must be re-diffed on every bump; add a CI check or a test that pins the list. (b) There is no fuel or epoch interruption; this stays tracked until untrusted modules are accepted.
   - *Acceptance:* each item is fixed or reported with a reason, and `cargo audit` and the CWSO CI pass.

## 2. Output

The changes stated in section 1, on your own branch, and a closing report: per id, fixed (with the test or check that shows it) or not fixed (with the reason).

## 3. Constraints

- Work only in your CWSO worktree on branch `agent/devops-engineer/T728` (from CWSO `origin/develop`); Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release. Do not edit the CWSO ledger (`docs/tasks/`) or the emage.code ledger.
- Run the CWSO checks that its CI runs (Go: `go vet`, `go test ./...`; Rust: `cargo fmt --check`, `cargo clippy`, `cargo test`, `cargo audit`; as `.gitlab-ci.yml` defines them) and report the summary lines; mark any check you could not run locally **(unverified)**.
- Never read or print a secret value (no `.env*`, no secret files; presence checks only). Do not change any server, host or running container. Do not touch `/home/emage/Code/emage/CWSO` itself (it holds local modifications). Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

Each item is fixed or reported with a reason, and `cargo audit` and the CWSO CI pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
