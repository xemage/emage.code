# T600 — Fix the evaluate-poc golden case's backlog check and checklist wording (P44) under a user-approved v19

**ID:** T600
**Owner:** qa-engineer
**Status:** in_review
**Priority:** P2
**Tier:** standard
**Affects:** —
**Depends on:** —
**Created:** 2026-10-08
**Based on:**
- `docs/plans/plan-111-evaluate-poc-backlog-check.md`
- `docs/artifacts/poc-skill-command-overlaps-v1.md` (P44, O3)
- `docs/decisions/ADR-007-command-contract-authority.md` (Accepted): the command's declared output contract governs
  what a golden case may require
- `docs/artifacts/protected-paths-v1.md` §5
- The user's decision of 2026-10-08: "Approving v19 basline"

## 1. What and why

The open case `evaluate-poc-verdict-debt-reconciliation` has two defects. Both were verified by the orchestrator on
`develop` `edd426e`.

1. **The backlog check is narrower than the contract.**
   - `/evaluate-poc` step 6 requires "Prioritized production refactoring backlog (top 5 minimum)" and declares no
     format.
   - The `poc-evaluation` skill's § 6 Refactoring Backlog template renders the backlog as a **table** (`| Priority |
     Item | Rationale | Suggested Owner | Effort |`).
   - `expect.py` `_backlog_size` (`:98–103`) counts only `^\d+\.\s+\S` numbered lines. A conforming report that
     follows the skill's table template therefore fails the check.

   The fix lets the check count table rows as well. Strength stays the same: one backlog heading, at least 5
   prioritized items. The fixture's numbered backlog must still pass.
2. **The brief overstates the checklist rule.**
   - `brief.md:54–55` says the eight checklist items are present "**when and only when**" the recommendation is
     `proceed` or `proceed_with_constraints`.
   - The contract, `/evaluate-poc` step 10, says "**If** recommending `proceed` or `proceed_with_constraints`,
     produce a handoff checklist". That is "if", not "only if".
   - `check()` already enforces exactly "if". The **brief text** is wrong, not the check, so correct the wording.

**Results must not change:** the case stays `expected_pass` and `check()` stays True.

## 2. PROTECTED-PATH AUTHORIZATION — `protected-paths-v1.md` §5

**This task, T600, is the authorizing task** for edits to exactly these files, and only to what §3 names:

| Case (`tests/golden/open/…`) | Files |
|---|---|
| `evaluate-poc-verdict-debt-reconciliation` | `expect.py`: the `_backlog_size` function and the module docstring only. `brief.md`: the checklist "when and only when" wording (`:54–55`) and every "numbered" backlog description (`:56`, `:106`, plus any other sentence that describes the backlog check). |

**Not authorized:**
- any other part of `check()` or any other constant;
- any `case.yaml` field;
- the fixture;
- any other case;
- `tests/golden/held-out/` (never open it; prune it from every traversal);
- `scripts/scorecard.py`, `evaluator_hash.py` and `evaluator-hash-known-good-v*.json`.

No non-golden test loads this case's `expect.py`. The orchestrator checked.

## 3. The changes

1. **`_backlog_size`.**
   - Keep the rule that there is exactly one `## …backlog…` heading. If there is not, return 0.
   - Within that section, count the numbered items as today (`^\d+\.\s+\S`).
   - If there are no numbered items, count the **data rows of the first Markdown table** in the section instead:
     - skip the header row and the `|---|` separator row;
     - count each later `|`-delimited row whose first cell is non-empty;
     - stop at the first non-table line.
   - Return that count.
   - Keep the function small and readable, and add a one-line comment citing `/evaluate-poc` step 6 and the skill's
     § 6 template.
2. **Module docstring.** Describe the backlog rule as "at least five prioritized items under the one backlog heading,
   numbered or as table rows (`/evaluate-poc` step 6 declares no format; the `poc-evaluation` skill's § 6 template is
   a table)".
3. **`brief.md`.**
   - Change "**when and only when**" to "**when**". Add a short clause citing step 10's "If recommending …", and note
     that the check enforces exactly that.
   - Update every description of the backlog check to "numbered items or table rows". Quote the command and the
     skill verbatim wherever they are quoted.

## 4. Controls

- **No result changes.** Record `check()` before and after: it must be True both times. Run
  `python3 scripts/scorecard.py --check` before and after: it must report 34 / 26 / 0.
- **Discrimination run.** Run the probes on scratch copies outside the repo, confirm that each mutation applied, and
  report every result:

  | # | Probe | Expected |
  |---|---|---|
  | 1 | Unmodified fixture (6 numbered items) | True |
  | 2 | Numbered list trimmed to 4 | False |
  | 3 | Backlog replaced by the skill's table with 5 data rows | True |
  | 4 | Table with 4 data rows | False |
  | 5 | Table with header and separator only | False |
  | 6 | A second `## …Backlog…` heading added | False |
  | 7 | Old `_backlog_size` on probe 3 (the table) | False, which proves the defect |

  For every probe, keep all other fields of the fixture valid, so that only the backlog decides the result.
- **Evaluator-hash tests.** Exactly two will go red. **Do NOT refresh the baseline.** After committing, report both
  digests against **v18**: `tests_golden` must differ from `2f0a786b…`, and `scripts_scorecard` must stay
  `45346c17…`. The orchestrator writes v19, which the user has pre-approved, after verifying your work.
- **Gates and suite.**
  - Run `test_golden_held_out_isolation`, `test_golden_suite_format` and `validate-tasks.py`.
  - Run `python3 tests/run.py`, redirecting output to a file (never `| tail`).
  - Expect 904 tests with **exactly** the 2 hash failures. Name every failing test.

## 5. Constraints

- **Write scope:** §2, plus this brief's `**Status:**` line (set it to `in_review`).
- **Forbidden reads and names:** never read `.env*`, credential or key files. Any search that reaches `tests/` must
  prune `tests/golden/held-out` first. **Never write a golden case name unless that case has a `tests/golden/open/`
  directory.**
- **Commit:** one local Conventional Commit, ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Do not push. Never run `glab mr merge` or any merge or approve API, with no exception.**

## 6. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). If the case result would change, stop and report it.
