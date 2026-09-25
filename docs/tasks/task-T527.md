# T527 — Adjudicate the `/skillify` contract conflict under ADR-007

**ID:** T527
**Owner:** Solution Architect
**Status:** in_review
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** T525 (merged 2026-09-25)
**Created:** 2026-09-25
**Based on:** `docs/plans/plan-073-skillify-adjudication-and-wave2.md` §0–§1;
`docs/decisions/ADR-007-command-contract-authority.md`;
`docs/artifacts/protected-paths-v1.md` §5; `docs/tasks/task-T525.md`.

## 1. The conflict

`implementation/knowledge/commands/skillify.md` ("Generate the Skill File") declares a five-section
`SKILL.md` template: `## Trigger`, `## Inputs`, `## Steps`, `## Success Criteria`, `## Examples`.

`implementation/knowledge/skills/skillify/SKILL.md` ("SKILL.md Template") declares a **different**
six-section template: `## Purpose`, `## When to Use`, `## Prerequisites`, `## Procedure`,
`## Examples`, `## Edge Cases`.

Two declared contracts, same artifact. `tests/golden/open/skillify-skill-file-template-drift` is
`known_failing` / `tracked_defect` on this, and it is the only thing keeping `command/skillify` off
`stable`.

## 2. Measured corpus state — start from this, do not re-derive it casually

All 26 real `implementation/knowledge/skills/*/SKILL.md`:

| Template | Satisfied **completely** by |
|---|---|
| the **command**'s | **0 of 26** |
| the **skill**'s | **1 of 26** |

Per-section against the skill's template: `## When to Use` 20/26, `## Purpose` 16/26,
`## Procedure` 16/26, `## Examples` 9/26, `## Prerequisites` 2/26, `## Edge Cases` 1/26.

**`T525`'s closure record overstates this** — it says the corpus "uniformly follows" the skill's
template and `active-tasks.md` says "26 of 26 follow". `plan-073` §0 records the correction. **The
corpus follows neither template.** Re-verify the numbers yourself before relying on them; if they
have moved, say so.

## 3. Your task

Produce an adjudication under `ADR-007`, then execute it.

**Do not assume the answer is one verdict for the whole file.** `plan-073` §1 sets out the leading
hypothesis and its counter-evidence:

- **Branch 1 does not fire.** `AGENTS.md` is silent on `SKILL.md` structure and no skills-format
  contract artifact exists. Verify this rather than taking it from this brief.
- **The "only a label for content the corpus already carries" clause is the live question, and it
  looks only partly satisfied.** `## Trigger` ≈ `## When to Use`, `## Inputs` ≈ `## Prerequisites`,
  `## Steps` ≈ `## Procedure` would be **branch 3a** (relabel). But `## Success Criteria` appears in
  3 of 26 with no clear counterpart, which looks like **branch 3b** (omission — fix the corpus, case
  stays failing).

So the honest verdict may well be **per-section**, with some sections relabelled and others left as
real corpus debt. A single tidy verdict is the suspicious outcome here, not the target — `T515`
faced the same shape and its honest answer was 2 green of 6.

**`ADR-007` §5 binds: never resolve by relaxing a check.** Deleting `## Success Criteria` from the
command's template because the corpus lacks it is relaxation unless you can argue on the merits that
the section should never have been declared. If you make that argument, make it explicitly.

## 4. Deliverables

1. `docs/artifacts/skillify-contract-resolution-v1.md` — the adjudication: which branch fires per
   section, why, and what each implies. Follow `docs/artifacts/command-contract-resolution-v1.md`'s
   shape.
2. The execution of whatever the adjudication concludes — which may amend
   `implementation/knowledge/commands/skillify.md`, or `implementation/knowledge/skills/skillify/SKILL.md`,
   or state that the corpus is at fault and nothing is amended.
3. If and only if the verdict makes the golden case pass, the `case.yaml` status flip — see §5.

**State plainly whether `/skillify` ends promotable.** If it does not, that is an acceptable and
possibly correct outcome; say so rather than engineering around it.

## 5. PROTECTED-PATH AUTHORIZATION — conditional and narrow

**This task is authorized to modify protected paths under `tests/golden/**`, citing
`docs/artifacts/protected-paths-v1.md` §5.2, and the authorization is limited to exactly:**

| Path | Permitted change |
|---|---|
| `tests/golden/open/skillify-skill-file-template-drift/case.yaml` | `status` flip and removal of the `known_failing_*` keys — **only if** your verdict genuinely makes `check()` return `True` |
| `tests/golden/open/skillify-skill-file-template-drift/brief.md` | restate the expected outcome to match |

**`expect.py` is NOT authorized** and must not change. The case checks the command's declared
template; if your verdict changes that template, the checker must be re-derived — and that is a
different, wider grant than this one. If you conclude `expect.py` must change, **stop and report a
blocker**; do not widen this table. `protected-paths-v1.md` §5.1 forbids you extending your own
grant, and `T520` and `T523` both correctly refused in this exact situation.

`scripts/scorecard.py`, every other case, and all of `tests/golden/held-out/` are excluded.

## 6. The evaluator-hash baseline — expected to fail, and NOT yours to fix

If you touch `tests/golden/**` at all, these two tests will go red:

```
tests/functional/test_golden_harness_evaluator_hash.py::TestBuildKnownGoodPayload::test_matches_the_real_committed_known_good_reference
tests/functional/test_golden_harness_evaluator_hash.py::TestRealRepoNoDrift::test_no_drift_against_real_current_repo_state
```

This is expected and is stated up front so you need not discover it. **Do not fix it.**
`docs/artifacts/` is not a protected path, so you could argue the refresh is in scope — it is not.
Refreshing a tamper-evidence baseline is the one action that control exists to stop an actor doing
to itself. Recompute read-only with
`golden_harness.evaluator_hash.compute_current_digests(Path('.'))`, report both digests and how each
differs from `evaluator-hash-known-good-v4.json`, and stop. The user authorizes the next version.

`scripts_scorecard` must come back byte-identical to v4.

## 7. Verification

```
python3 tests/run.py                 # BASELINE FIRST; 774 tests, OK, 23 skipped on develop
python3 scripts/scorecard.py         # read it; do not modify it
python3 implementation/scripts/check-maturity.py --root implementation
node implementation/scripts/sync.mjs --check
python3 docs/tasks/validate-tasks.py
git status --porcelain
```

**`python3 tests/run.py` — the full 774-test suite, not `pytest tests/functional` (734).** The
40-test difference has already broken one MR in this phase. If you amend any
`implementation/knowledge/` file, `sync.mjs --check` will report drift until you re-run
`node implementation/scripts/sync.mjs` — note the path is `implementation/scripts/`, not
`scripts/`; the wrong path fails `MODULE_NOT_FOUND` and silently no-ops if stderr is suppressed.

## 8. Ledger, git, blockers

Set this brief's `**Status:**` to `in_review`; do not move any ledger row — archival is
orchestrator-only. Branch `agent/solution-architect/T527`, Conventional Commits, message ending
with exactly `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

**Do not open a merge request and do not merge anything.** No self-merge, no exceptions.

If `git push` fails with `glab auth git-credential: "erase" is an invalid operation` and/or
`HTTP Basic: Access denied`, that is a known environment transient affecting only the
git-over-HTTPS credential path. It is not your fault, credentials are not broken, and you must not
touch any `glab` or `git config credential.*` setting. Retry two or three times, then report.

Blockers: type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). Max 2 retries, then escalate. Never widen §5 — report instead.
