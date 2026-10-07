# T583 — Refresh stale golden quotes and fixture provenance (FU-2 + new-poc docstring)

**ID:** T583
**Owner:** qa-engineer
**Status:** pending
**Priority:** P2
**Tier:** standard
**Affects:** —
**Depends on:** T582
**Created:** 2026-10-07
**Based on:**
- `docs/plans/plan-101-golden-quote-refresh.md`
- `docs/artifacts/conditional-pass-semantics-v4.md` §8 (golden coupling) and §16
- `docs/plans/plan-100-conditional-pass-and-authority-adr.md` §5
- `docs/artifacts/protected-paths-v1.md` §5
- The user's approval of 2026-10-07: "FU-2: approval for v16 baseline"

## 1. What and why

T582 (MR !483) amended several knowledge files that open golden cases quote. Each case's `check()` reads only its own
fixture, so **no case result changes**. But some quotes and one provenance note now describe text that no longer
exists. This task refreshes them so each case quotes the merged source verbatim.

It also fixes the parked `new-poc` docstring, which still calls P11 "parked". P11 was resolved in T563–T565.

**No `check()` logic changes.** Every case's result and status must stay exactly as it is today. If one would change,
stop and report it.

## 2. PROTECTED-PATH AUTHORIZATION — `protected-paths-v1.md` §5

**This task, T583, is the authorizing task** for edits to exactly these files, and only to the text named in §3:

| Case (`tests/golden/open/…`) | Files |
|---|---|
| `code-review-conditional-pass-conditions-gap` | `case.yaml` (`known_failing_reason`), `brief.md`, `expect.py` (docstring only) |
| `security-audit-critical-not-fail` | `case.yaml` (`known_failing_reason`), `brief.md`, `expect.py` (docstring only) |
| `prepare-release-conditional-pass-conditions-gap` | `case.yaml` (`known_failing_reason`), `brief.md`, `expect.py` (docstring only) |
| `validate-workflow-gate-verdict-sources` | `fixture/implementation/knowledge/skills/validation-gates/SKILL.md` (re-copy, byte-identical to the merged source); `brief.md` (provenance only) |
| `new-poc-plan-hypothesis-format` | `expect.py` (docstring only) |

**Not authorized:**
- any `check()` body or constant;
- any `status`, `known_failing_category` or `tags` field;
- any other file or case;
- `tests/golden/held-out/` (do not open it);
- `scripts/scorecard.py`;
- `evaluator_hash.py` and the `evaluator-hash-known-good-v*.json` files.

You may not extend this grant. If more is needed, report it and stop.

## 3. The refreshes (orchestrator-verified sites on `develop` `300a6eb`)

| Case | Stale text | Source to quote now |
|---|---|---|
| `code-review-…-gap` | "list the conditions that must be met before merge" (`case.yaml:6`, `brief.md:12`, `expect.py:5`) | `implementation/knowledge/commands/code-review.md:51`: "If CONDITIONAL_PASS, list the conditions, each with an owner and a due point." The case's premise still holds: the command defines no structured `**Conditions**:` field. Say so. |
| `security-audit-critical-not-fail` | "If any CRITICAL findings exist, the verdict MUST be FAIL." (`case.yaml:6`, `brief.md:13`, `expect.py:4–5`) | `implementation/knowledge/commands/security-audit.md`, as amended by B3: "If any CRITICAL or HIGH finding exists, … the verdict MUST be FAIL". The fixture (CRITICAL: 1, Status: CONDITIONAL_PASS) violates the amended rule just as it violated the old one, so the `capability_gap` premise holds. |
| `prepare-release-…-gap` | "list conditions that must be met before deployment" (`case.yaml:6–7`, `brief.md:12`, `expect.py:6`) | `implementation/knowledge/commands/prepare-release.md` step 9, as amended by R5: "If CONDITIONAL_PASS, list the conditions." The premise (no structured conditions field in the `## RELEASE VERDICT` template) holds. |
| `validate-workflow-gate-verdict-sources` | Fixture copy of `validation-gates/SKILL.md` and provenance "copies of its source at `develop` `a6be6b0`" (`brief.md:167`) | Re-copy the merged source byte-for-byte and confirm with `cmp`. Update the provenance to name the new `develop` SHA. Its `check()` reads only Gate Types and the Verdict Format (`**Gate:**` field and "Every gate MUST produce a verdict"), which T582 did not change. Confirm the case still returns **True**. |
| `new-poc-plan-hypothesis-format` | `expect.py` docstring: "The plan's *path* is deliberately not asserted (parked item P11)" | P11 was **resolved** (T563 ruled; T564 amended the command to `docs/plans/plan-<ID>.md`; T565 realigned this case). State that the path is still not asserted, because the glob is path-agnostic by design, and that P11 is resolved. |

Every quote must be **verbatim** from the merged source. Diff each one against its source line. You may quote a
leading substring of a long sentence; mark any omission with "…".

## 4. Controls

- **No result changes.** Before and after your edits, run each of the five cases' `expect.py` (`check()`) and
  `scripts/scorecard.py --check`. Results must be identical: three `known_failing` cases stay `False`, and
  `validate-workflow` and `new-poc` stay `True`. `scorecard --check` must report 34 cases / 26 pass / 0 regressions.
- **Run `scorecard.py` in write mode only if `--check` reports a content difference.** It should not; results are
  unchanged. If it does, report the diff before committing.
- **Exactly two evaluator-hash tests will go red. Do NOT refresh the baseline.** Report both digests **post-commit**
  against **v15** (`tests_golden 7408bc70…`). `scripts_scorecard` must stay byte-identical (`45346c17…`). The
  orchestrator writes v16. The user has pre-approved v16; the orchestrator verifies your work first.
- Run `test_golden_held_out_isolation`, `test_golden_suite_format`, `validate-tasks.py`, and
  `python3 tests/run.py`. Redirect output to a file, never pipe it to `tail`. Expect 904 tests with **exactly** the
  2 hash failures. Name every failing test.

## 5. Constraints

- Write scope: §2, plus this brief's `**Status:**` line.
- Do not read `.env`, credential or key files. Any search that reaches `tests/` must prune `tests/golden/held-out`
  before traversal.
- Commit locally as one commit. **Do not push. Never run `glab mr merge` or any merge/approve API, with no
  exception.** Hand back.

## 6. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). If a case result would change, or a quote can't be made verbatim, stop and report.
