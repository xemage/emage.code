# T560 — Golden batch: P13, P14, P15, P24 (prose and fixture corrections)

**ID:** T560
**Owner:** QA Engineer
**Status:** done
**Priority:** P2
**Tier:** mechanical
**Affects:** —
**Depends on:** —
**Created:** 2026-10-01
**Based on:** `docs/plans/plan-089-install-and-golden-batches.md`; `docs/plans/plan-084-round-close-and-fired-triggers.md` §4
(P13–P15); `docs/plans/plan-088-audience-lint.md` §3 (P24).

Four golden-case corrections parked so that **one** evaluator-hash baseline authorization covers all of them
(`plan-083` decision 2). Keep **one commit per item**.

## PROTECTED-PATH AUTHORIZATION — `protected-paths-v1.md` §5

This task, T560, is the authorizing task for **exactly** these paths:

| Item | Case | Authorized paths |
|---|---|---|
| P13 | `handoff-payload-schema-fields-real` | `fixture/implementation/runtime/handoff/schema-v1.json` |
| P14 | `consolidate-memory-recommendation-table-grounded` | `fixture/recommendations.md`; `expect.py` (**module docstring only**) |
| P15 | `skillify-skill-file-template-drift` | `case.yaml` (**`known_failing_reason` text only**) |
| P24 | `batch-manifest-ledger-schema-conflict` | `brief.md` |
| P14b | `consolidate-memory-recommendation-table-grounded` | `brief.md` — **extension, see below** |
| P24b | `batch-manifest-ledger-schema-conflict` | `expect.py` — **module docstring only; extension, see below** |

**Not authorized:** any other file in those cases (in particular any `expect.py` *logic*, any `status` or
`known_failing_category`), any other case, `tests/golden/held-out/` (do not open it), `scripts/scorecard.py`, and
the evaluator-hash baseline. You may not extend this grant; report and stop instead.

### Grant extension — 2026-10-01, by the orchestrator

The implementer's first hand-back found that its own fixes left two neighbouring spots stale: the
consolidate-memory `brief.md` still described the old Promote destinations, and the batch `expect.py` docstring
still cited `commands/plan.md`. It also found three pre-existing deviations in the batch `brief.md` quote block
(already in the original grant). Rather than compute v12 and need a v13 for these, the orchestrator extended the
grant **before** the baseline was computed, with rows **P14b** and **P24b** above. `protected-paths-v1.md` §5.1
forbids a *holding agent* from extending its own grant; it does not forbid the orchestrator from scoping one. The
extension was first given by message; the implementer rightly pointed out that §5.2 wants it in this brief, so it is
recorded here in the same MR as the work.

## The four items

- **P13.** The handoff fixture embeds the **pre-T529** schema (no `minItems`), so an empty `writablePaths` still
  passes *for this fixture*. Replace the fixture's `schema-v1.json` with the live
  `implementation/runtime/handoff/schema-v1.json` (verify byte-identical afterwards). `check()` must still return
  **True** — the fixture payload must satisfy the stricter schema; if it doesn't, **stop and report**, don't edit
  the payload. Then show, in a temp copy, that emptying `writablePaths` now returns **False** — that is the point
  of the item.
- **P14.** The consolidate-memory fixture's Promote rows name targets T549 put on the "Never use" list (root
  `AGENTS.md`) or outside `docs/` (`implementation/knowledge/memory/README.md`). Re-point their Rationale text at
  durable project documents under `docs/`, per the command's `## Promotion Targets`. Keep every key, action, and
  the table's four columns exactly as they are. Update `expect.py`'s **docstring** where it says step 4 has "no
  declared artifact": T549 made step 4 name each Promote's target file and section below the table. State that
  this checker does not assert step 4, and why. **Do not add an assertion.** `check()` must stay **True**.
- **P15.** The skillify `case.yaml` `known_failing_reason` still says the template is "written to
  `.github/skills/<name>/SKILL.md`", but T532 changed the output path to a two-row rule. Correct the reason text
  only; the case stays `known_failing` / `tracked_defect`, and `check()` stays **False**.
- **P24.** `batch-manifest-ledger-schema-conflict/brief.md` line 37 quotes `/batch` step 2 verbatim with the old
  `commands/plan.md`; T558 changed it to `/plan`. Requote it against `implementation/knowledge/commands/batch.md`
  as it is now. `check()` stays **True**.

## Scorecard and hash

- If no case outcome moves, a scorecard regeneration is timestamp-only — **revert it**, don't commit it.
- **Exactly two evaluator-hash tests will go red. Do NOT refresh the baseline** or touch
  `docs/artifacts/evaluator-hash-known-good-v*.json` / `evaluator_hash.py`. Compute both digests **post-commit**
  and report them against **v11**; `scripts_scorecard` must be byte-identical to v11.
- Run `tests/functional/test_golden_held_out_isolation.py`.

## Git and constraints

Commit locally on your branch (the digest hashes git-tracked files); **do not push; never merge or approve
anything.** A DevOps Engineer runs in parallel on `scripts/install.sh` and `tests/functional/` — stay out of
those.

## Verification

`python3 tests/run.py` (exit code; redirect to a file) showing **exactly** the two evaluator-hash failures; every
`check()` you touched, observed; `scorecard.py --check`; `validate-tasks.py`; `check-maturity.py`.

## Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`. If anything in this
brief is wrong, report it.
