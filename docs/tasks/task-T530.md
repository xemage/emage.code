# T530 — Correct the stale `new-feature-real-checkpoint-format-drift` brief

**ID:** T530
**Owner:** Technical Writer
**Status:** pending
**Priority:** P2
**Tier:** mechanical
**Affects:** —
**Depends on:** —
**Created:** 2026-09-25
**Based on:** `docs/plans/plan-073-skillify-adjudication-and-wave2.md` §2;
`docs/artifacts/protected-paths-v1.md` §5; `docs/tasks/task-T520.md`, `docs/tasks/task-T523.md`.

## Objective

`tests/golden/open/new-feature-real-checkpoint-format-drift/brief.md` still opens
`# Case: … (known_failing / tracked_defect)` and still carries `## Why this is known_failing today`
and `## Category: tracked_defect` sections — while its `case.yaml` has read `status: expected_pass`
since `T520` flipped it. The file contradicts its own case.

Found by `T523`'s implementer, independently confirmed by the orchestrator, and deliberately left
alone twice because it fell outside both tasks' authorizations.

## 1. PROTECTED-PATH AUTHORIZATION — read first

**This task is explicitly authorized to modify a protected path under `tests/golden/`, and cites
`docs/artifacts/protected-paths-v1.md` §5.2 as the reason that authorization is required.**

| Path | Permitted change |
|---|---|
| `tests/golden/open/new-feature-real-checkpoint-format-drift/brief.md` | prose only, to match the case's actual `expected_pass` status |

**Nothing else.** Not `case.yaml`, not `expect.py`, not `fixture/`, not `scripts/scorecard.py`, not
any other case, and nothing under `tests/golden/held-out/`. §5.1 forbids you extending this grant —
if more seems needed, **stop and report a blocker**.

Use `tests/golden/open/new-feature-plan-doc-compliant/brief.md` as the shape reference for an
`expected_pass` brief (`## Pass condition`, `## Provenance`). Keep the substantive historical
content — the corpus survey evidence is a real record of why the case once failed; reframe it
rather than deleting it, as `T523` did for its own case's brief.

## 2. The evaluator-hash baseline — expected to fail, and NOT yours to fix

Your change drifts the `tests_golden` digest and turns these two red:

```
tests/functional/test_golden_harness_evaluator_hash.py::TestBuildKnownGoodPayload::test_matches_the_real_committed_known_good_reference
tests/functional/test_golden_harness_evaluator_hash.py::TestRealRepoNoDrift::test_no_drift_against_real_current_repo_state
```

Expected. **Do not fix it.** `docs/artifacts/` is unprotected so you could argue the refresh is in
scope; it is not. Report the digests (recompute read-only via
`golden_harness.evaluator_hash.compute_current_digests(Path('.'))`), note how each differs from
`evaluator-hash-known-good-v4.json`, and stop. The user authorizes the next version.

**Note on your tools:** you have no `Bash`. If you cannot run the digest computation or the test
suite, **say so plainly and hand back uncommitted** — the orchestrator will run the gates and
commit. Do not claim verification you did not perform.

## 3. Acceptance criteria

1. `brief.md` no longer describes the case as `known_failing` anywhere, and matches `case.yaml`.
2. `case.yaml`, `expect.py` and `fixture/` are byte-unchanged.
3. `check()` still returns `True` — prose-only changes cannot affect it, but confirm the file set.
4. Exactly the 2 evaluator-hash failures and no third.

## 4. Ledger, git, blockers

Set this brief's `**Status:**` to `in_review`; do not move any ledger row. **No merge request, no
merge, no self-merge.** Report blockers with type and severity; max 2 retries; never widen §1.
