# T541 — Re-derive `/batch`'s checker and resolve the sibling-corollary question

**ID:** T541
**Owner:** Backend Developer
**Status:** in_review
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** T535 (merged 2026-09-26)
**Created:** 2026-09-26
**Based on:** `docs/plans/plan-078-t535-followups.md` §1;
`docs/artifacts/batch-manifest-resolution-v1.md` §7 (the element-for-element spec);
`docs/decisions/ADR-007-command-contract-authority.md`; `docs/artifacts/protected-paths-v1.md` §5.

## 1. PROTECTED-PATH AUTHORIZATION

**Authorized under `protected-paths-v1.md` §5.2, limited to one case directory:**

| Path | Permitted change |
|---|---|
| `tests/golden/open/batch-manifest-ledger-schema-conflict/expect.py` | re-derive per `batch-manifest-resolution-v1.md` §7 |
| `…/case.yaml` | `status` + `known_failing_*` keys, **only if `check()` genuinely returns `True`**; and the stale line-number citation regardless |
| `…/brief.md` | restate to match, plus the two corrections in §4 |
| `…/fixture/` | the `decomposition.md` half only — see §3 |

**Excluded:** `scripts/scorecard.py`; every other case; all of `tests/golden/held-out/`; the
fixture's ledger half (see §3). §5.1 forbids widening this — **report a blocker instead.** Six tasks
in this phase hit that boundary and all six refused.

## 2. The re-derivation, and the direction the risk runs

Three of `expect.py`'s five elements assert the **pre-amendment** contract: `UNIT_ID_RE = ^U\d+$`
and `BRANCH_RE = ^batch/…$` match forms no document declares any more, and assertion C requires a
`branch` in a ledger row the amended contract says has none.

`check()` returns `False` today and **would still return `False` against a fully conforming
artifact** — verified. Same shape as `T531`: *a check nobody can trust is worse than a red case.*

**`batch-manifest-resolution-v1.md` §7 has the element-for-element spec. Follow it, and do not
exceed it.** Two re-derived elements are strictly *stronger* than what they replace, so **`ADR-007`
Validation 1 binds in the unusual direction here: the risk is over-strengthening.** A re-derivation
that goes further than the spec changes a verdict nobody re-opened. If you believe the spec is wrong
on an element, **say so and argue it** rather than quietly improving on it.

## 3. The question `T535` deliberately left you

`ADR-007`'s sibling corollary distinguishes branch-1 amendments that change **only a name or path**
— fixture updated, case survives — from those that change the **artifact class**, which invalidate
the case and require it to be *re-purposed*. `T535` judged this amendment **arguably between the
two** and refused to resolve it, because resolving it *is* the re-derivation. **You hold the
authorization, so you decide. State which limb you chose and why.**

Two data bearing on it, both verified:

- **The fixture's ledger half already conforms** to the amended step 5 with no edit — 7 cells,
  `T534`/`T535`/`T536`, Titles prefixed `BATCH structured-logging …`. **Do not touch it.** That it
  already conforms is evidence, and editing it would destroy the evidence.
- The `decomposition.md` half does **not** conform and would need re-authoring. Its own `brief.md`
  § Provenance records it as hand-authored, which `ADR-007` §5 permits re-authoring — that is the
  §3b exit, *produce one conforming artifact of that class and re-fixture against it*, not a fixture
  chosen to manufacture an outcome.

**If your honest answer is that the case must be re-purposed rather than re-fixtured, say so** —
that is a legitimate outcome and a blocker-shaped one, since re-purposing is a wider change than
this grant covers.

## 4. Fold in — same case, same defect class

Per the `T530` precedent:

- `brief.md` says *"Five of step 5's fields map onto that schema"* and then lists **four**. Confirmed.
- `case.yaml` and `brief.md` both cite `validate-tasks.py:195`; it is now **288**, with `C3` at
  **307**. The quoted code is still accurate — only the line numbers are stale. **Verify the current
  numbers yourself** rather than copying these; the file has changed three times this phase.

## 5. What this does not do

**`/batch` does not become promotable even if your work makes the case pass.** It is `experimental`
and must clear `experimental → beta` first; `T535` §8 established that and it does not change here.
**If you find yourself reasoning toward a promotion, stop** — that is a component-state change and a
separate task.

## 6. The scorecard and the hash

1. **Regenerating `docs/benchmarks/` is required**, not forbidden — `T533`'s gate asserts the
   committed artifact matches a fresh run, and a status flip changes it. Run
   `python3 scripts/scorecard.py` (write mode) and **commit both files**. `docs/benchmarks/` is not
   protected. Confirm held-out rows stay redacted as `held-out-case-<n>` / `<redacted>`.
2. **Two evaluator-hash tests will go red.** Expected. **Do not fix it.** `docs/artifacts/` is
   unprotected so you could argue the refresh is in scope — it is not. Recompute read-only via
   `golden_harness.evaluator_hash.compute_current_digests(Path('.'))`, report both digests and how
   each differs from `evaluator-hash-known-good-v7.json`, and stop. `scripts_scorecard` must come
   back byte-identical to v7. The digest hashes git-tracked files only, so compute it **post-commit**.

## 7. Verification

```
python3 tests/run.py                  # BASELINE FIRST — measure it yourself
python3 scripts/scorecard.py          # WRITE mode, required by §6
python3 scripts/scorecard.py --check  # must exit 0 once committed
python3 -m pytest tests/functional/test_golden_held_out_isolation.py tests/functional/test_scorecard_artifact_no_drift.py -q
python3 implementation/scripts/check-maturity.py --root implementation
python3 docs/tasks/validate-tasks.py
git status --porcelain
```

**Measure the baseline yourself** — five different figures have circulated in this phase's briefs and
every one was wrong at some point. It should be **824 / OK / 23 skipped**, but verify. Expected after:
exactly the two evaluator-hash failures and nothing else. `check-maturity.py` must stay `79 / 0` with
an **unchanged distribution**.

Also call `check()` directly and report the boolean, before and after.

## 8. Ledger, git, blockers

Set this brief's `**Status:**` to `in_review`; move no ledger row. Branch
`agent/backend-developer/T541`. Commit message ends with exactly
`Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

**No merge request, no merge, no self-merge.**

If `git push` fails with the `glab auth git-credential: "erase" is an invalid operation` /
`HTTP Basic: Access denied` pair: known environment transient, not your fault, credentials are not
broken, and you must not touch any `glab` or `git config credential.*` setting. Retry two or three
times, then report that the commit is on the local branch.

Blockers: type and severity; max 2 retries. Never widen §1.
