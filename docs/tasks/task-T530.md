# T530 — Correct the stale `new-feature-real-checkpoint-format-drift` brief

**ID:** T530
**Owner:** Technical Writer
**Status:** in_review
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
| `tests/golden/open/skillify-skill-file-template-drift/brief.md` | prose only |
| `tests/golden/open/skillify-skill-file-template-drift/case.yaml` | the `known_failing_reason` **text** only |

### 1.2 Third defect in the same case, added 2026-09-26 after T528

Wave 2's implementer found a **second** staleness in that same `brief.md`, distinct from §1.1's: its
`## What this checks` presents a *verbatim* quote listing `## Trigger` and `## Steps` — sections
`skillify.md` **no longer declares** after `T527` renamed them to `## When to Use` and `## Procedure`.
`T531` correctly re-derived `expect.py` to check the amended five but was not authorized to touch
`brief.md`, so **the case's stated contract and its actual check now disagree**, and the brief's own
survey table measures two rows corresponding to no declared section.

The verdict is unaffected (still `known_failing`). Correct the quote to the five sections
`skillify.md` declares today, and drop or re-label the two survey rows that no longer correspond to
anything. **Verify the amended quote against `implementation/knowledge/commands/skillify.md` itself,
not against this brief.**

**Nothing else.** Not `case.yaml`, not `expect.py`, not `fixture/`, not `scripts/scorecard.py`, not
any other case, and nothing under `tests/golden/held-out/`. §5.1 forbids you extending this grant —
if more seems needed, **stop and report a blocker**.

Use `tests/golden/open/new-feature-plan-doc-compliant/brief.md` as the shape reference for an
`expected_pass` brief (`## Pass condition`, `## Provenance`). Keep the substantive historical
content — the corpus survey evidence is a real record of why the case once failed; reframe it
rather than deleting it, as `T523` did for its own case's brief.

## 1.1 Second case added 2026-09-25, after T527

`T527` found this case's prose stale for a **different** reason and could not fix it: its own grant
was conditional on a genuine pass, which did not occur. Two statements are now false:

- `known_failing_reason` asserts the corpus "uniformly follows a different template". **It does
  not** — fence-aware measurement shows **0 of 26** files satisfy the command's template and
  **0 of 26** satisfy the skill's. The corpus follows neither.
- It frames the defect as two disagreeing contracts. **After `T527` that is no longer true**: the
  skill's template is now a strict superset of the command's, in the same relative order.

The case is still correctly `known_failing` — the real fixture satisfies 1 of 5 sections — so
`status`, `known_failing_category`, `expect.py` and `fixture/` must **not** change. Only the *reason*
text and the brief's prose. If you believe the status should change, that is a blocker, not an edit.

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
2. `expect.py` and `fixture/` are byte-unchanged in both cases; `case.yaml`'s `status` and `known_failing_category` are unchanged.
3. `check()` still returns `True` — prose-only changes cannot affect it, but confirm the file set.
4. Exactly the 2 evaluator-hash failures and no third.

## 4. Ledger, git, blockers

Set this brief's `**Status:**` to `in_review`; do not move any ledger row. **No merge request, no
merge, no self-merge.** Report blockers with type and severity; max 2 retries; never widen §1.
