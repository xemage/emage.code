# T531 — Re-derive the `/skillify` checker and close the `## Required Context` defect

**ID:** T531
**Owner:** Backend Developer
**Status:** done
**Priority:** P2
**Tier:** mechanical
**Affects:** —
**Depends on:** T527 (merged 2026-09-25)
**Created:** 2026-09-25
**Completed:** 2026-09-25
**Based on:** `docs/plans/plan-074-skillify-followups.md` §1;
`docs/artifacts/skillify-contract-resolution-v1.md`; `docs/tasks/task-T527.md` §5 (its blocker);
`docs/artifacts/protected-paths-v1.md` §5; `docs/decisions/ADR-007-command-contract-authority.md`.

## 1. PROTECTED-PATH AUTHORIZATION — read first

**Authorized to modify a protected path under `tests/golden/`, citing `protected-paths-v1.md` §5.2.**

| Path | Permitted change |
|---|---|
| `tests/golden/open/skillify-skill-file-template-drift/expect.py` | `REQUIRED_SECTIONS` entries and the docstring's quoted clause — **nothing else** |

**Excluded:** `case.yaml`, `brief.md` and `fixture/` in that case (those belong to `T530`);
`scripts/scorecard.py`; every other case; all of `tests/golden/held-out/`.

§5.1 forbids you extending this grant. If more seems needed, **stop and report a blocker** — do not
edit this table. `T520`, `T523`, `T525` and `T527` all hit this boundary and all four refused;
`T527`'s refusal on *this exact file* is why you exist.

## 2. The change

`T527` amended the `/skillify` command's declared template. `expect.py` still asserts the
pre-amendment strings, so **it now checks a contract no document declares.** It returns `False`
either way, so nothing is mis-reported — but a check nobody can trust is worse than a red case.

`T527` supplied the spec:

```python
REQUIRED_SECTIONS = (
    "## When to Use",      # was "## Trigger"
    "## Inputs",           # unchanged
    "## Procedure",        # was "## Steps"
    "## Success Criteria", # unchanged
    "## Examples",         # unchanged
)
```

**Verify this against `implementation/knowledge/commands/skillify.md` yourself** rather than copying
it — if the command file and this spec disagree, the command file wins and you should report the
discrepancy.

### 2.1 The instruction that matters most

**Keep the `section in text` substring operator exactly as it is.**

It admits `## Procedures` and `## Procedure Summary`, which real corpus files use. Switching to an
exact-heading regex, an anchored match, or a line-wise comparison would **strengthen** the check
beyond what `T527` decided, silently changing a verdict nobody re-opened.

This is `ADR-007` Validation 1 (no loss of strength) applied in the unusual direction: **the risk
here is over-strengthening, not relaxation.** Change the five strings and the docstring. Change
nothing else — not the operator, not `check()`'s shape, not the glob, not `main()`.

## 3. Also close `## Required Context`

`implementation/knowledge/skills/skillify/SKILL.md` Round 2 declares `## Required Context` in its
output block, and the skill's own "SKILL.md Template" omits it — the **identical** self-contradiction
`T527` fixed for `## Success Criteria`, verified independently by the orchestrator.

Add `## Required Context` to that template, in the position Round 2 implies (immediately after
`## Inputs`). One line plus its placeholder. **Do not** add it to the command's template — it is not
one of the command's declared sections and adding it there would be scope creep in the guise of
consistency.

This is **not** a protected path. Re-run `node implementation/scripts/sync.mjs` (note: not
`scripts/sync.mjs`, which fails `MODULE_NOT_FOUND` and silently no-ops if stderr is suppressed) and
`python3 implementation/scripts/generate-registry.py` afterwards — a `knowledge/` edit drifts both
the projections and the registry, and `sync.mjs --check` alone will **not** catch registry drift.

## 4. What success looks like — and what over-reach looks like

**`/skillify` is not expected to become promotable.** On `T527`'s scoring the real fixture satisfies
**1 of 5** sections after re-derivation, so `check()` should still return `False` and the case should
stay `known_failing`.

**If your re-derived checker makes the case pass, you have almost certainly over-reached — say so
loudly rather than reporting a green.** Do not touch `case.yaml`; you are not authorized to, and a
status flip is `T530`'s.

## 5. The evaluator-hash baseline — expected to fail, NOT yours to fix

Touching `expect.py` drifts the `tests_golden` digest and turns these two red:

```
tests/functional/test_golden_harness_evaluator_hash.py::TestBuildKnownGoodPayload::test_matches_the_real_committed_known_good_reference
tests/functional/test_golden_harness_evaluator_hash.py::TestRealRepoNoDrift::test_no_drift_against_real_current_repo_state
```

Expected; stated up front. **Do not fix it.** `docs/artifacts/` is unprotected so you could argue the
refresh is in scope — it is not. Recompute read-only via
`golden_harness.evaluator_hash.compute_current_digests(Path('.'))`, report both digests and how each
differs from `evaluator-hash-known-good-v4.json`, and stop. `scripts_scorecard` must come back
byte-identical to v4. The digest hashes **git-tracked files only**, so compute it post-commit.

## 6. Verification

```
python3 tests/run.py       # BASELINE FIRST: 774 tests, OK, 23 skipped
python3 scripts/scorecard.py
python3 implementation/scripts/check-maturity.py --root implementation
python3 implementation/scripts/check.py --registry --root implementation
node implementation/scripts/sync.mjs --check
python3 docs/tasks/validate-tasks.py
git status --porcelain
```

**Full 774-test `tests/run.py`, not `pytest tests/functional` (734.)** Expected after your change:
exactly the two evaluator-hash failures and nothing else. Also call `check()` directly against the
case's fixture and report the boolean.

## 7. Ledger, git, blockers

Set this brief's `**Status:**` to `in_review`; do not move any ledger row. Branch
`agent/backend-developer/T531`. Commit message ends with exactly
`Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

**No merge request, no merge, no self-merge.**

If `git push` fails with `glab auth git-credential: "erase" is an invalid operation` and/or
`HTTP Basic: Access denied`: known environment transient, not your fault, credentials are not
broken, and you must not touch any `glab` or `git config credential.*` setting. Retry two or three
times, then report that the commit is on the local branch.

Blockers: type and severity, max 2 retries. Never widen §1.
