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

## 2. Both batches landed; three installer items parked

T560 merged as !440 (baseline v12). T559 closes P17, P18, P20 and P21, and found that T555 §8.2 was wrong:
`sync_tree_into` had the same type-conflict defect, which T559 fixed too.

| # | Item | Trigger |
|---|---|---|
| P25 | `merge_tree_preserve_existing` symlink cases (`--update`, `docs/` subdirectories other than `tasks/`): 6/300 fuzz mismatches; in one, `rsync` itself writes through a symlink, so parity would copy a hazard — needs a policy decision, not a fix | next `install.sh` task |
| P26 | `sync_tree_into` can still strand backup directories in `/tmp` when it fails for reasons other than a type conflict | next `install.sh` task |
| P27 | `sync_tree_into` is 75 lines, over the 50-line limit in `coding-standards.md` (74 before T559 — pre-existing) | next `install.sh` task |

