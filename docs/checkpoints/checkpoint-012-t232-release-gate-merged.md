# Checkpoint 012 — T232 Release Gate + Witness Signing Merged

- **Phase:** Phase 2 (CWSO × emage.code × SIA integration) — critical path
- **Date:** 2026-06-23
- **Author:** orchestrator
- **Plan:** [plan-009-cwso-emagecode-sia-integration.md](../plans/plan-009-cwso-emagecode-sia-integration.md)
- **Develop pipeline:** #2622164572 — GREEN (verified via `scripts/check-ci-green.py --ref develop`)

## Completed since checkpoint-011

| Task | Outcome |
|------|---------|
| CI green-keeping | develop pipeline restored to GREEN; markdown-link, plan-coverage, pyarrow, and task-tracking failures resolved. |
| CI-green gate rule | `scripts/check-ci-green.py` + `make ci-gate` / `make ci-status` — mandatory pre-merge gate enforcing latest CI is green. Exit 0=green, 1=red(+failed jobs), 2=pending, 3=tooling. |
| T230 | Trainer bridge (Parquet → GRPO/SFT) merged earlier; 34 tests. |
| **T232** | sia-harness release gate + Ed25519 witness signing. Merged via [MR !47](https://gitlab.com/em-age/emage.code/-/merge_requests/47). 38 tests. |

## T232 detail

- **Artifacts:** `implementation/adapters/sia-target/release_gate.py`, `keys/witness-dev.pub` (DEV public key only), `tests/functional/test_t232_release_gate.py`, `docs/artifacts/release-gate-witness-v1.md`.
- **Functions:** `evaluate_release_candidate`, `sign_witness`, `verify_witness`, `promote` (fail-closed gate; no witness emitted on gate failure).
- **Security review:** CONDITIONAL_PASS → all blocking conditions resolved before merge:
  - SEC-001 (HIGH) — embedded-key authenticity forgery → fixed: `verify_witness` is fail-closed, authenticity requires a pinned trusted public key; embedded-key path is opt-in integrity-only; `promote()` self-verifies emitted witness against a trusted anchor.
  - SEC-002 (MEDIUM) — model bytes unbound → fixed: signed payload binds `model.artifact_sha256` (computed from artifact bytes; declared-vs-computed mismatch blocks promotion).
  - SEC-003 (MEDIUM) — outdated `cryptography` pin → fixed: `cryptography>=43.0.1`; CI `before_script` now installs it.
  - SEC-004/005/006 (LOW) — tracked as POC-DEBT in the artifact.
- **Key safety:** no private key committed; `.gitignore` excludes `*.ed25519.key`, `deploy/keys/`, `**/keys/*.key`.

## Decisions

- HIGH security findings block merge: remediated rather than accepted as tracked risk (validation-gate rule + immutable security constraints).
- CI-green gate is now mandatory before any merge/continuation (`make ci-gate`).

## Task graph state

- **Done:** T220–T226, T230, **T232**.
- **In review:** T228 (CONDITIONAL_PASS) — blocked on a live CWSO dispatch with a valid JWT.
- **Pending:** T214 (in_progress), T231, T233 (now only blocked by T231), T234.

## Blockers (escalated to user)

| Blocker | Type | Detail |
|---------|------|--------|
| T228 full close | external/dependency | Needs a live CWSO dispatch with `CWSO_JWT_SECRET`. Security rules forbid the agent auto-reading `/home/emage/Code/emage/CWSO/.env.jwt.dev`; the user must export it and run the dispatch. |
| T231 fine-tune | dependency | Soft-blocked: needs real trajectory data from the T228 live capture (Parquet store currently empty). |

## Next steps

1. **User action:** export `CWSO_JWT_SECRET` and run the live SIA dispatch (without `--dry-run`) to populate the trajectory store and close T228.
2. T231 fine-tune once trajectories exist (T230 bridge ready, T232 gate ready).
3. T233 closed-loop eval (depends on T231 + T232 ✅).
4. T234 cost/latency telemetry (depends on T233).
