# T568 — Realign `validate-workflow-gate-verdict-sources` to the amended gate list (T566 FU-2)

**ID:** T568
**Owner:** QA Engineer
**Status:** in_review
**Priority:** P2
**Tier:** judgment
**Affects:** command/validate-workflow
**Depends on:** T567
**Created:** 2026-10-01
**Based on:** `docs/artifacts/validate-workflow-gate-resolution-v1.md` §5(c) and §9; `docs/plans/plan-093-validate-workflow-repair.md`;
`docs/decisions/ADR-007-command-contract-authority.md` (§5, Validation 1 and Validation 2); `docs/artifacts/protected-paths-v1.md` §5.

## 1. What and why

T567 amended `/validate-workflow` step 5 to list the `validation-gates` skill's five gate types. This case still
checks the old six-gate list against frozen copies of the old sources, so it stays red. Realign it to the amended
contract as specified in artifact §5(c). If the repair works, the case flips to **`expected_pass`**. The
orchestrator ruled in §9.2 that the 6 → 5 change is **not** a Validation 1 weakening, *provided* the two new
predicates (completeness and ordered list fidelity) are added and demonstrated.

## 2. PROTECTED-PATH AUTHORIZATION — `protected-paths-v1.md` §5

**This task, T568, is the authorizing task** for edits inside exactly one directory,
`tests/golden/open/validate-workflow-gate-verdict-sources/`:
- `expect.py`, `brief.md`, `case.yaml`;
- **add** `fixture/implementation/knowledge/commands/validate-workflow.md`, a byte-identical copy of the merged
  source;
- **delete** `fixture/implementation/knowledge/skills/plan-approve-execute/SKILL.md` and
  `fixture/implementation/knowledge/agents/orchestrator.md`;
- `fixture/implementation/knowledge/skills/validation-gates/SKILL.md`: re-confirm only, with `cmp`. Do not edit it.

You may also run `python3 scripts/scorecard.py` in write mode and commit `docs/benchmarks/scorecard-v6.12.0.{json,md}`.
**This is required here,** because the case's status changes.

**Not authorized:**
- any other case, including reading one;
- `tests/golden/held-out/` (do not open it);
- `scripts/scorecard.py` itself;
- `evaluator_hash.py` and `docs/artifacts/evaluator-hash-known-good-v*.json`.

You may not extend this grant. If more is needed, report it and stop.

## 3. The work (artifact §5(c) is the specification)

- **`expect.py`:**
  - Set `GATES` to exactly the five entries in §5(c)1, in that order.
  - Remove `PAE` and `ORCH`, and add `CMD`.
  - Leave the per-gate predicate **byte-for-byte unchanged**.
  - Add the **completeness** predicate (§5(c)3) and the **ordered list-fidelity** predicate (§5(c)4).
  - `check()` is the AND of all three.
  - Update the docstring and `main()`.
- **Fixture:** add the amended command copy (confirm with `cmp` against the merged source), delete the two unused
  copies, and re-confirm the `validation-gates` copy.
- **`case.yaml`:** the shape of an `expected_pass` case is `id`, `command`, `status: expected_pass`, `tags`, with no
  `known_failing_*` keys. Remove the `contract-self-contradiction` tag and keep the others.
- **`brief.md`:** rewrite it to the corrected contract as §5(c) lists:
  - quote the amended step 5 and the unchanged step 6 and Failure mode verbatim from the merged source;
  - include a five-row Result table plus the two predicates;
  - add a Resolution section;
  - update Provenance with the `develop` SHA the copies came from.
  - **Correct the report grep:** it does not return 0 (§9.1). Restate it honestly, for example by excluding
    `tests/golden/` and `docs/artifacts/`, and say that you did.

## 4. Controls

- **Discrimination:** on temp copies outside `tests/golden/`, show `True` on the fixture and **`False` for each of
  the seven perturbations** in §5(c). Confirm that each mutation actually applied before trusting its result, then
  restore. Also show that the **pre-T568** `check()` returns `False` on the new fixture, which is the contrast run.
- **Verbatim:** diff every quoted line against the merged command source.
- **A red result is legitimate.** If the case cannot honestly go green, leave it red and report it. Never soften a
  predicate.

## 5. Scorecard, maturity and hash

- Regenerate the scorecard once, then confirm that `--check` is OK. **ADR-007 Validation 2:** exactly **one**
  transition, this case moving from `known_failing` to `expected_pass` (expected 34 cases, 26 pass, 0 regressions),
  and nothing else. Held-out rows must stay redacted.
- `check-maturity.py --root implementation`: 79 components, 0 failing, command 13/6. `/validate-workflow` stays
  `experimental` here, because promotion is T569.
- **Exactly two evaluator-hash tests will go red. Do NOT refresh the baseline.** Report both digests
  **post-commit** against **v14** (`tests_golden 58509ae8…`); `scripts_scorecard` must be byte-identical
  (`45346c17…`). The user decides whether to authorize v15.
- Run the held-out isolation test, the audience lint and `validate-tasks.py`.
- `python3 tests/run.py`, with output redirected to a file: 904 tests with exactly the 2 hash failures. Name every
  failing test.

## 6. Constraints

- Write scope is §2 plus this brief's `**Status:**` line.
- Commit locally as one commit. **Do not push. Never run `glab mr merge` or any merge or approve API, with no
  exception.** Hand everything back.

## 7. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`. If the artifact
or T567's merged wording makes an instruction here wrong, report it rather than working around it.
