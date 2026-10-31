# T696 — CWSO dependency and toolchain security update

**ID:** T696
**Owner:** devops-engineer
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-10-31
**Completed:** —
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-31: T696)
- The user's decision of 2026-10-31: "T696 go"
- Immutable Security Constraint 1 (no secrets in source control); `implementation/SECURITY.md`

## 1. What and why

The repository is CWSO (`https://gitlab.com/em-age/emage.code.cwso`, local clone `/home/emage/Code/emage/CWSO`, target branch `develop`). Work in a separate worktree based on `origin/develop`; the primary clone has unrelated uncommitted files.

1. **Rust (`services/Cargo.lock`).** `cargo audit` reports 16 advisories: wasmtime 36.0.14 (to >= 36.0.20), rustls 0.23.40 (to >= 0.23.46), rustls-webpki 0.103.13 (to >= 0.103.16), webpki-roots 1.0.7 (to >= 1.0.10), libz-sys 1.1.28 (to >= 1.1.31), zstd 0.13.3 / zstd-safe 7.2.4 / zstd-sys 2.0.16 (to zstd >= 0.14.3, zstd-safe >= 8.2.0, zstd-sys >= 2.1.2), fxhash and paste unmaintained. Apply the compatible updates with `cargo update -p <crate> --precise <ver>` first, then the zstd major update (a `Cargo.toml` change plus any code changes it needs). Replace fxhash and paste, or record each in the audit configuration with a reason and a review date. Keep `rust:1.87-slim` unless a crate needs a newer compiler; if so, raise the image in every Dockerfile, in CI and in `scripts/release-assets.sh` together.
2. **Go.** `govulncheck` reports 10 standard library vulnerabilities (net/http, crypto/tls, net/textproto, crypto/x509) fixed in Go 1.26.9/1.26.10. Move the CI golang images (`golang:1.25.13`), `deploy/Dockerfile.orchestrator` (`golang:1.25-alpine`), `scripts/release-assets.sh` and the `go`/`toolchain` lines of `orchestrator/go.mod` to Go 1.26.10 or later, and govulncheck to v1.9.0. Run `go build ./...`, `go vet ./...` and the Go tests.
3. **Evidence.** `cargo audit` and `govulncheck` clean, or each remaining advisory recorded with a reason. The Rust tests (`cargo test --locked`), the Go tests, and a local `docker build` of the four images.

## 2. Output

One or more commits on a branch `agent/devops-engineer/T696` in the CWSO repository; no push.

## 3. Constraints

- Work only in your own worktree of the CWSO repository, based on `origin/develop`. Conventional Commits ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push or merge; never create a tag or release.
- Never print, log or commit a secret value. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/` or any `.env*` file.
- Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

- `cargo audit` and `govulncheck` clean (or every remaining advisory recorded with a reason).
- The Rust and Go tests pass, and the four images build locally.
- The CWSO pipeline is green after the push by the orchestrator.
- A Security Engineer review follows; the user rebuilds the images on the CWSO server after the merge.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
