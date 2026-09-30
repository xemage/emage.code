# T544 — Three loose ends in the `/batch` golden case

**ID:** T544
**Owner:** QA Engineer
**Status:** in_review
**Priority:** P2
**Tier:** mechanical
**Affects:** —
**Depends on:** T541 (merged 2026-09-26)
**Created:** 2026-09-26
**Based on:** `docs/plans/plan-079-install-sync-gap.md` §2; `docs/tasks/task-T541.md`;
`docs/artifacts/protected-paths-v1.md` §5.

## 1. PROTECTED-PATH AUTHORIZATION

**Authorized under `protected-paths-v1.md` §5.2, one case directory:**

| Path | Permitted change |
|---|---|
| `…/fixture/docs/tasks/active-tasks.md` | strip the `U<n>` marker from the three Titles — **nothing else in that file** |
| `…/expect.py` | tighten `LEDGER_TITLE_RE` only, per §2 |
| `…/case.yaml` | remove the stale `contract-drift` tag; the `id` only if §4 concludes it should change |
| `…/brief.md` | restate to match |

All in `tests/golden/open/batch-manifest-ledger-schema-conflict/`. **Excluded:**
`scripts/scorecard.py`; every other case; all of `tests/golden/held-out/`; the rest of that ledger
fixture. §5.1 forbids widening — **report a blocker instead.**

## 2. The `U<n>` Titles — the substantive item

The fixture's ledger rows read:

```
BATCH structured-logging U1: migrate runtime/memory diagnostics
```

Step 5 of `batch.md` declares `BATCH <slug>: <description>`. These are
`BATCH <slug> U<n>: <description>`. **The `U<n>` residue is the abolished unit-ID scheme surviving
inside the evidence offered for its own abolition** — `T535` and the orchestrator both cited these
Titles as proof the ledger half "already conforms". It conforms cell-for-cell and **not** in the
Title form; `T541` caught that.

**Strip the marker**, so the Titles read `BATCH structured-logging: migrate runtime/memory diagnostics`.

**Then tighten `expect.py`'s `LEDGER_TITLE_RE` to `^BATCH [a-z0-9][a-z0-9-]*: \S`** — and this is the
point of the task, not a side effect. `T541` could only assert a non-empty colon-terminated slug,
because no document declares `<slug>`'s character set and asserting one would have been
over-strengthening against an unconforming fixture. **Once the fixture conforms to the kebab form,
the stricter regex asserts what the fixture demonstrates rather than what you wish were declared.**

**Say explicitly whether you think that is legitimate.** The honest worry is that tightening a regex
to match a fixture you just edited is circular. The counter is that kebab-case slugs are the
repository's universal convention and `T541` declined only because the *fixture* contradicted it.
**If you find that unconvincing, leave the regex alone and say why** — stripping the marker is
worthwhile regardless, because it removes a reference to an abolished scheme.

## 3. The stale tag

`case.yaml`'s `tags:` still contains `contract-drift` on a case whose drift `T535` resolved and `T541`
closed. Remove it. Leave the other tags.

## 4. The case id — `T541` recommended AGAINST renaming, and that should be weighed

The id still reads `…-schema-conflict` on a green case. Tidiness says rename it. `T541` said don't,
and gave reasons worth taking seriously: the id is referenced by
`docs/benchmarks/scorecard-v6.12.0.{json,md}`, `evaluator-hash-known-good-v8.json`'s `reason` field,
and `batch-manifest-resolution-v1.md`. **A rename touches a published baseline and two historical
records**, one of which is an immutable tamper-evidence artifact.

**Keeping the id and saying why is a legitimate and probably correct outcome.** Decide, and if you
rename, enumerate every reference you updated and every one you deliberately left as history.

## 5. The scorecard and the hash

1. **Regenerating `docs/benchmarks/` is required.** Run `python3 scripts/scorecard.py` (write mode)
   and **commit both files**. Not protected. Confirm held-out rows stay redacted.
2. **Two evaluator-hash tests will go red.** Expected, **not yours to fix.** Recompute read-only via
   `golden_harness.evaluator_hash.compute_current_digests(Path('.'))`, report both digests against
   `evaluator-hash-known-good-v9.json`, and stop. `scripts_scorecard` must come back byte-identical to
   v9. Compute **post-commit** — the digest walks git-tracked files only.

## 6. Verification

```
python3 tests/run.py                  # BASELINE FIRST — measure it yourself
python3 scripts/scorecard.py          # WRITE mode, required
python3 scripts/scorecard.py --check  # must exit 0 once committed
python3 -m pytest tests/functional/test_golden_held_out_isolation.py tests/functional/test_scorecard_artifact_no_drift.py -q
python3 implementation/scripts/check-maturity.py --root implementation
python3 docs/tasks/validate-tasks.py
git status --porcelain
```

**Measure the baseline yourself** — six figures have circulated in this phase's briefs and all were
wrong at some point. Expected after: exactly the two evaluator-hash failures and nothing else.

**`check()` must still return `True`** — call it directly, before and after. If your regex tightening
makes it `False`, the fixture and the regex disagree and **you have the fixture edit wrong**, not the
regex. `check-maturity.py` must stay `79 / 0`; **`/batch` does not promote** and remains
`experimental`.

## 7. Ledger, git, blockers

Set this brief's `**Status:**` to `in_review`; move no ledger row. Branch `agent/qa-engineer/T544`.
Commit message ends with exactly `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

**No merge request, no merge, no self-merge.** Push transient: known, not your fault, touch no
credential config.

Blockers: type and severity; max 2 retries. Never widen §1.
