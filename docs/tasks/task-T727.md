# T727 — Batch E: CWSO server configuration

**ID:** T727
**Owner:** devops-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-02
**Completed:** 2026-11-02
**Based on:**
- `docs/plans/plan-129-batch-e-cwso-hardening.md` (task T727)
- The user's answer of 2026-11-02, verbatim: "E go"
- `docs/artifacts/tracked-debt-register-v4.md` (batch E rows) and v3; the T694 to T696 security reviews

## 1. What and why

(devops-engineer, CWSO): the server configuration.
   - SEC-T695-03: `CWSO_ALLOWED_ORIGINS` entries are not validated (`config.go:143`, `http.go:186-189`). Reject `*`, `null`, entries without a scheme or host, and entries with a path at `Load`. Log the effective list. Add tests.
   - SEC-T695-07: short HS256 secrets are accepted (`config.go:242-245`). Enforce a minimum length of 32 bytes and fail at startup, with a test.
   - SEC-T695-10: the plain HTTP listener is published on all interfaces by default (`transport/http.go`, `docker-compose.yml`). Bind to `127.0.0.1` by default, with an explicit opt-in for other interfaces.
   - **The user's own deployment** (the CWSO server, reached over the LAN under TD-T697-07) must keep working. Document the opt-in in the CWSO deployment docs, state what an operator must set, and do not change any server or host.
   - *Acceptance:* each item is fixed with tests. The CWSO CI passes. The opt-in is documented.

## 2. Output

The changes stated in section 1, on your own branch, and a closing report: per id, fixed (with the test or check that shows it) or not fixed (with the reason).

## 3. Constraints

- Work only in your CWSO worktree on branch `agent/devops-engineer/T727` (from CWSO `origin/develop`); Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release. Do not edit the CWSO ledger (`docs/tasks/`) or the emage.code ledger.
- Run the CWSO checks that its CI runs (Go: `go vet`, `go test ./...`; Rust: `cargo fmt --check`, `cargo clippy`, `cargo test`, `cargo audit`; as `.gitlab-ci.yml` defines them) and report the summary lines; mark any check you could not run locally **(unverified)**.
- Never read or print a secret value (no `.env*`, no secret files; presence checks only). Do not change any server, host or running container. Do not touch `/home/emage/Code/emage/CWSO` itself (it holds local modifications). Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

Each item is fixed with tests. The CWSO CI passes. The opt-in is documented.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
