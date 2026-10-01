# T565 — Realign the three PoC golden cases to the amended contracts (T563 FU-B)

**ID:** T565
**Owner:** QA Engineer
**Status:** in_review
**Priority:** P2
**Tier:** judgment
**Affects:** command/new-poc, command/poc-demo, command/evaluate-poc
**Depends on:** T564
**Created:** 2026-10-01
**Based on:** `docs/artifacts/poc-contract-resolution-v1.md` §§2–5 ("Golden coupling") and §9;
`docs/plans/plan-092-poc-contract-amendments.md`; `docs/decisions/ADR-007-command-contract-authority.md`
(Validation 1; corollary row "1, … only a name or path"); `docs/artifacts/protected-paths-v1.md` §5.

## 1. What and why

T564 amended the wording of `/new-poc`, `/poc-demo` and `/evaluate-poc`. Their golden cases still quote the old
wording, and two of them hard-code the old value sets. Those cases are still green, but they check the old
contract. This task realigns each case so it **quotes the merged wording verbatim** and **checks the amended
contract**. T562's three PoC greens must then be **re-earned**, not inherited.

## 2. PROTECTED-PATH AUTHORIZATION — `protected-paths-v1.md` §5

**This task, T565, is the authorizing task** for edits to exactly these files:

- `tests/golden/open/evaluate-poc-verdict-debt-reconciliation/`: `expect.py`, `brief.md`, `fixture/poc-evaluation.md`
- `tests/golden/open/poc-demo-hypothesis-status-evidence-gaps/`: `expect.py`, `brief.md`
- `tests/golden/open/new-poc-plan-hypothesis-format/`: `brief.md`, and renaming the plan file under
  `fixture/docs/plans/` to a `plan-<ID>.md` form (contents unchanged except where the rename requires it)

You may also run `python3 scripts/scorecard.py` in write mode and commit `docs/benchmarks/scorecard-v6.12.0.{json,md}`
**if** `--check` reports a difference.

**Not authorized:**
- any other case, including `team-status-dag-colour-code` (it is not coupled);
- each case's `case.yaml`;
- `tests/golden/held-out/` (do not open it);
- `scripts/scorecard.py` itself;
- the evaluator-hash baseline, `evaluator_hash.py` and `docs/artifacts/evaluator-hash-known-good-v*.json`.

You may not extend this grant. If more is needed, report it and stop.

## 3. Per case

Each case's "Golden coupling" row in the artifact lists exactly which lines go stale. In summary:

- **`evaluate-poc-verdict-debt-reconciliation`:**
  - Requote `brief.md:19,22,34,40` from the merged `evaluate-poc.md`.
  - In `expect.py`: drop `INCONCLUSIVE` from `STATUS`; set `SEVERITIES` to `CRITICAL/MEDIUM/LOW`; set `EFFORT`
    to `S/M/L`; remove the `HIGH:` group from `DEBT_ITEMS_RE`.
  - Re-author the fixture: it uses `HIGH` at lines 31, 44 and 65. Re-tier that item to `CRITICAL` or `MEDIUM`
    using the instruction's meanings ("must fix" or "should fix before production"), and keep the counts
    reconciling.
  - The weak-evidence section is no longer contested. With a binary Status, "weak is never `VALIDATED`" is
    exactly "weak ⇒ `INVALIDATED`". State that it is now asserted in full.
  - Invert the discrimination note (`brief.md:103`): weak + `INCONCLUSIVE` must now return **False**.
- **`poc-demo-hypothesis-status-evidence-gaps`:**
  - Requote `brief.md:20`.
  - Drop `INCONCLUSIVE` from `STATUS_VALUES` and `NO_EVIDENCE_STATUSES`; keep `IN_PROGRESS`.
  - The fixture stays `IN_PROGRESS`. Confirm.
  - Update the descriptive text the artifact lists (Rule 4, step 7). The "`Evidence gaps: n/a` with
    `INCONCLUSIVE`" perturbation now fails on the enum, so the gap rule must stay demonstrated by
    "`Evidence gaps: None` with `IN_PROGRESS`".
- **`new-poc-plan-hypothesis-format`:**
  - Requote `brief.md:18`.
  - Rename the fixture plan file to a `plan-<ID>.md` form.
  - `check()` does not change. Its glob is path-agnostic.
  - Mark the contested-clause text as resolved.

## 4. Controls (plan-072 and ADR-007 Validation 1)

- **No check gets weaker.** The ruling in §9.2 is that dropping a severity sub-count is not a weakening,
  **provided `check()` rejects `HIGH`, `XL` and `INCONCLUSIVE` outright** rather than ignoring them. Demonstrate
  every rejection with a temporary perturbation of a scratch copy of the fixture. Show the input and the
  `False`, confirm that each mutation actually applied before trusting its result, and then restore.
- **Every quote is verbatim** from the merged command files. Diff each quoted string against its source line.
- **A red case is a legitimate outcome.** If a case cannot be made to pass honestly against the amended
  contract, leave it red and report it. Do not soften `check()`.

## 5. Scorecard, maturity and hash

- `python3 scripts/scorecard.py --check`. If it reports a difference, regenerate once and commit the scorecard.
  Held-out rows must stay redacted.
- `python3 implementation/scripts/check-maturity.py --root implementation`: 79 components, 0 failing, command
  **13/6**. These are the re-earned greens. Report each PoC command's line.
- **Exactly two evaluator-hash tests will go red. Do NOT refresh the baseline.** Report both digests
  **post-commit** against **v13** (`tests_golden 481c2d4c…`). `scripts_scorecard` must be byte-identical
  (`45346c17…`). The user decides v14.
- Run `tests/functional/test_golden_held_out_isolation.py`, the audience lint and `validate-tasks.py`.
- Run `python3 tests/run.py`, redirecting output to a file. Expect 904 tests with **exactly** the 2 hash
  failures. Explain any other failure or any change in the count.

## 6. Constraints

- Write scope is §2, plus this brief's `**Status:**` line.
- Commit locally as one commit. **Do not push. Never run `glab mr merge` or any merge or approve API.** This
  applies with no exception. Hand everything back.

## 7. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`. If the artifact,
this brief or T564's merged wording makes an instruction here wrong, report it. Do not work around it.
