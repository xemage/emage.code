# Artifact: security-review-t696-cwso-deps-toolchain-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell, so no build, test, `cargo audit`, `govulncheck` or `git diff`; `grep_content` errored on the worktree path; the wasmtime 36.0.20 feature page was fetched from docs.rs on 2026-10-31). Recorded by the orchestrator from the reviewer's report.
- **Gate**: security. **Date**: 2026-10-31.
- **Target**: T696 (CWSO MR !217), branch `agent/devops-engineer/T696`, commits `562e5d6`, `73fb538`, `083c49c` on `05ef236`: wasmtime 36.0.14 -> 36.0.20 without the `cache` and `profiling` features; rustls, rustls-webpki, webpki-roots, libz-sys and tokio bumped; paste ignored in `services/.cargo/audit.toml`; Go 1.26.10 everywhere and govulncheck v1.9.0; the Rust Dockerfiles copy `Cargo.lock` and build with `--locked`.
- **Based on**: the T696 brief and the user's approval of 2026-10-31; the files at `083c49c`; CWSO pipeline 3011518716 at `083c49c` as verified by the orchestrator (`rust:audit`, `go:audit` and all build and test jobs pass; `e2e:phase2` failed on the known container-name race fixed by T695 and passed on retry; `rust:lint` allow_failure).

## Verdict: PASS (0 critical, 0 high, 0 medium, 7 LOW)

No Immutable Security Constraint is breached, and no required control is removed or weakened.

- **wasmtime features**: the explicit list is exactly the 36.0.20 default set minus `cache` and `profiling` (17 of 19 kept, `services/cwso-sparse/Cargo.toml:38-56`); the implicit `once_cell` and `wasmtime-jit-icache-coherence` stay on via `std`. The sandbox controls are unchanged: `Engine::default()` (`agent.rs:155`), `StoreLimitsBuilder` memory cap with `trap_on_grow_failure(true)` and the `ResourceLimiter` (`agent.rs:121-139, 184-194`), the empty `Linker` (`agent.rs:196`), the SHA-256 module pin (`agent.rs:72-76, 298-315`). No `Config::cache*` or `Config::profiler` in `main.rs` or `agent.rs`.
- **Lockfile**: wasmtime 36.0.20, rustls 0.23.46, rustls-webpki 0.103.16, webpki-roots 1.0.11, libz-sys 1.1.31, tokio 1.53.3 present; no `wasmtime-internal-cache`, `fxprof-processed-profile` or `zstd*` package.
- **audit.toml**: one advisory (RUSTSEC-2024-0436, unmaintained, no vulnerability), correct reason (compile-time proc-macro), named acceptance (T696, 2026-10-31) and review date 2027-01-31 (`services/.cargo/audit.toml:10-17`).
- **Go**: 1.26.10 in `.gitlab-ci.yml:61,94,125,164`, `deploy/Dockerfile.orchestrator:4`, `orchestrator/go.mod:3`, `scripts/release-assets.sh:30`; govulncheck pinned (`.gitlab-ci.yml:169`) and checksum-verified by `go install`.
- **Dockerfiles**: all three Rust Dockerfiles copy `Cargo.lock` and build with `--locked` (lines 9 and 15).

| Id | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T696-01 | LOW | `scripts/release-assets.sh:36` builds release binaries with `rust:1.86-bookworm` (out of support, differs from CI's 1.87); `:37` runs `cargo build` without `--locked`. | Same toolchain as CI and `--locked`. |
| SEC-T696-02 | LOW (pre-existing) | Rust pinned at 1.87 (`.gitlab-ci.yml:75,138,179`, Rust Dockerfiles line 3), well behind current stable. | Move to a current stable toolchain in a follow-up. |
| SEC-T696-03 | LOW (pre-existing) | Runtime bases `alpine:3.20` (`Dockerfile.orchestrator:16`) and `debian:bookworm-slim` (Rust Dockerfiles line 17) are old (support dates unverified); no CI job scans OS packages. | Supported bases and an image scan (Trivy or Grype) in the `audit` stage. |
| SEC-T696-04 | LOW (pre-existing) | Base images pinned by mutable tag, not digest (`.gitlab-ci.yml:61,94,125,164,75,138,179,206,224`; Dockerfiles lines 3/4 and 16/17). | Pin by `@sha256:` digest with automated updates. |
| SEC-T696-05 | LOW (pre-existing) | `Dockerfile.orchestrator:9` runs `go mod download || true`; `:8` copies `go.sum*`. The later `go build` (`:12`) still verifies `go.sum`. | Drop `|| true`; copy `go.sum` explicitly. |
| SEC-T696-06 | LOW | The 2027-01-31 review date in `services/.cargo/audit.toml:15-16` is a comment only. | A ledger or register row for the review, or a CI check that fails after the date. |
| SEC-T696-07 | LOW (informational) | (a) With `default-features = false` (`services/cwso-sparse/Cargo.toml:38`), a future wasmtime default is not picked up automatically. (b) Pre-existing: no fuel or epoch interruption (`agent.rs:155`), so a looping start function blocks `instantiate` (`agent.rs:197-199`); mitigated by the operator-chosen, SHA-256-pinned module and the empty `Linker`. | (a) Re-diff the list on every wasmtime bump; (b) enable `epoch_interruption` or `consume_fuel` before untrusted modules are accepted. |

Noted, not a finding: `.gitlab-ci.yml:277,299,319,374` on this branch still carry the committed CWSO_JWT_SECRET value (the rotated, dead value on CWSO develop); T695 removes it, and T695 is rebased onto T696.

## Unverified

- A full search for `Config::cache*`, `Config::profiler` and `fxhash` (only `main.rs` and `agent.rs` read; a removed API would fail compilation, and the build jobs are green).
- The per-commit diffs (final state reviewed).
- That Go 1.26.10 / govulncheck v1.9.0 and wasmtime 36.0.20 fix exactly the reported advisories (evidence: the green `go:audit` and `rust:audit`).
- Whether a std security fix landed between Rust 1.86 and 1.87; the support-end dates of Alpine 3.20 and Debian 12.
- wasmtime internals (`signals-based-traps` as a `Config` setting under `std` in 36.x).
- The developer's local test and audit runs.
