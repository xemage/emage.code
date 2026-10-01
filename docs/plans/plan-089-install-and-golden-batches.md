# plan-089 — Two parallel batches: the installer (P17, P18, P20, P21) and golden prose (P13–P15, P24)

**Created:** 2026-10-01
**Based on:** `plan-083` decision 2 (batching); `plan-084` §4; `plan-085` §3; `plan-086` §2; `plan-088` §3.
**Scopes:** `T559`, `T560`.

- **`T559`** (DevOps) — four `scripts/install.sh` items parked by T552/T555. Needs nothing from the user.
  P20 is sharper than when parked: `implementation/docs/tasks/__pycache__/` exists in the source tree today,
  so every fresh install currently ships it.
- **`T560`** (QA) — four golden-case corrections parked so that **one** evaluator-hash authorization (v12)
  covers all of them, under one protected-path grant table.

The two touch disjoint files (`scripts/install.sh` + `tests/functional/` vs `tests/golden/**`), so they run in
parallel. T560 ends with one v12 request to the user.
