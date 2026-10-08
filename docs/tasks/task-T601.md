# T601 — Mechanical cleanup of parked golden and test notes, under a user-approved v20

**ID:** T601
**Owner:** qa-engineer
**Status:** pending
**Priority:** P2
**Tier:** standard
**Affects:** —
**Depends on:** —
**Created:** 2026-10-08
**Based on:**
- `docs/plans/plan-112-parked-note-cleanup.md`
- `docs/plans/plan-106-golden-residual-staleness.md` §3, `docs/plans/plan-109-golden-realignment-p32.md` §3 and
  `docs/plans/plan-111-evaluate-poc-backlog-check.md` §3 (the origin of each note)
- `docs/artifacts/protected-paths-v1.md` §5
- The user's decisions of 2026-10-08: "Approving v20 baseline" and "Batch the small notes into one cleanup task"

## 1. What and why

Five parked notes are purely mechanical: each makes a statement true again and changes no logic. The orchestrator
verified every site on `develop` `0143f86`. **No `check()` and no case result may change.**

## 2. PROTECTED-PATH AUTHORIZATION — `protected-paths-v1.md` §5

**This task, T601, is the authorizing task** for edits to exactly these files, and only to the text named in §3:

| File | Change |
|---|---|
| `tests/golden/open/evaluate-poc-verdict-debt-reconciliation/brief.md` | the "Discrimination (demonstrated at authoring)" section only |
| `tests/golden/open/validate-workflow-gate-verdict-sources/brief.md` | the provenance grep restatement only (near `:193`) |
| `tests/golden/open/prepare-release-conditional-pass-conditions-gap/fixture/release-notes.md` | the one `Release manager` line only (`:14`) |

`tests/functional/test_golden_held_out_isolation.py` (one docstring sentence) and
`tests/functional/test_golden_harness_scratch.py` (one filename literal) are **not protected paths**, and they are
not part of the evaluator-hash digest. They are covered by this task as ordinary edits.

**Not authorized:** any `expect.py` or `case.yaml`, any other fixture or case, `tests/golden/held-out/` (never open it;
prune it from every traversal), `scripts/scorecard.py`, `evaluator_hash.py` and `evaluator-hash-known-good-v*.json`.

## 3. The changes

1. **Isolation-test docstring** (`test_golden_held_out_isolation.py`, around `:39–41`). It says the open
   `new-feature-plan-doc-compliant` brief names a held-out sibling case. T597 removed that reference, so the claim is
   now false. Remove only that example (the `new-feature` clause). Keep the `security-audit-verdict-fields-compliant`
   example and the rest. Do not add or reword any case name.
2. **Scratch test filename** (`test_golden_harness_scratch.py`, `:55–56`). Change the literal `docs/plans/feature-x.md`
   and its two matching `feature-x.md` path parts to `plan-001-x.md`. It tests only the file-writing helper.
3. **`evaluate-poc` case brief.** Add the T600 table probes to the "Discrimination (demonstrated at authoring)"
   section. The seven probes and their expected results are in `docs/tasks/task-T600.md` §4. Re-run them yourself on
   scratch copies outside the repo and record **your** measured results, not copies of the old ones. Keep the
   existing probes.
4. **`validate-workflow` brief, provenance grep.** The statement says the grep returns 0 matches, scoped to an old
   commit. Re-run that grep exactly as written at your commit (with `tests/golden/` and `docs/artifacts/` pruned) and
   restate the true result and commit. Today it returns one match, `docs/tasks/task-T572.md`, which only mentions the
   block. Keep the surrounding explanation true.
5. **Stale fixture field** (`prepare-release-conditional-pass-conditions-gap/fixture/release-notes.md:14`). Change
   `- **Release manager**: orchestrator` to the merged value in `docs/releases/_template.md`
   (`- **Release manager**: release-manager`). No `check()` reads this field. Confirm that.

## 4. Controls

- **No result changes.** Record all affected cases' `check()` results before and after: `evaluate-poc…` True,
  `validate-workflow…` True, `prepare-release-conditional-pass-conditions-gap` False (known_failing). Run
  `python3 scripts/scorecard.py --check` before and after; both must report 34 / 26 / 0.
- **Exactly two evaluator-hash tests will go red. Do NOT refresh the baseline.** After committing, report both
  digests against **v19**: `tests_golden` must differ from `2811d829…`, and `scripts_scorecard` must stay
  `45346c17…`. The orchestrator writes v20, which the user has approved, after verifying your work.
- **Gates and suite.**
  - Run `test_golden_held_out_isolation`, `test_golden_suite_format` and `validate-tasks.py`.
  - Run `python3 tests/run.py`, redirecting output to a file (never `| tail`).
  - Expect 904 tests with **exactly** the 2 hash failures. Name every failing test.

## 5. Constraints

- **Write scope:** §2, plus this brief's `**Status:**` line (set it to `in_review`).
- **Held-out:** never read `.env*`, credential or key files. Prune `tests/golden/held-out` before any search that
  reaches `tests/`. **Never write a golden case name unless that case has a `tests/golden/open/` directory.**
- **Commit:** one local Conventional Commit, ending with
  `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- **Do not push. Never run `glab mr merge` or any merge or approve API, with no exception.**

## 6. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). If any case result would change, stop and report it.
