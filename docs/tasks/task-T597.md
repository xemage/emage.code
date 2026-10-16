# T597 — Golden realignment after P32 (FU-P32-G) under a user-approved v18

**ID:** T597
**Owner:** qa-engineer
**Status:** done
**Priority:** P2
**Tier:** standard
**Affects:** —
**Depends on:** T596
**Created:** 2026-10-08
**Based on:**
- `docs/plans/plan-109-golden-realignment-p32.md`
- `docs/artifacts/path-conventions-v3.md` §6 (FU-P32-G: the exact sites) and §2 P-1 (the decided form:
  `docs/plans/plan-<ID>.md`, where `<ID>` is a three-digit number, a hyphen, and a slug of lowercase letters, digits,
  hyphens and dots)
- `docs/artifacts/protected-paths-v1.md` §5
- The user's decision of 2026-10-08: "Approving v18 baseline"

## 1. What and why

T596 (MR !515) applied the user's P32 decision. Every plan is now `docs/plans/plan-<ID>.md`, and `/new-feature` and
`/new-project` now write that path. Several open golden cases still quote, check or name the old paths.

This task realigns them so that:
- each case quotes the merged source verbatim;
- the `new-feature` case checks the decided contract;
- the fixture names follow it.

**No case's status or result may change.**

## 2. PROTECTED-PATH AUTHORIZATION — `protected-paths-v1.md` §5

**This task, T597, is the authorizing task** for edits to exactly these files, and only to the text named in §3:

| Case (`tests/golden/open/…`) | Files |
|---|---|
| `new-feature-plan-doc-compliant` | `expect.py` (the glob constant at `:25` and the docstring `:4–6` only); the fixture plan file (rename only, content byte-identical); `brief.md` (`:11–13` quote, `:16–17` pass condition, `:20–26` provenance) |
| `new-project-plan-doc-and-lifecycle-states` | `brief.md` (`:16` quote; descriptive text at `:72`, `:87`, `:95–98`); `expect.py` (docstring `:6` and comment `:25` only; **`PLAN_NAME_RE` at `:26` unchanged**); the fixture plan file (rename to `plan-001-taskflow.md`, content byte-identical) |
| `new-poc-plan-hypothesis-format` | the fixture plan file (rename to `plan-001-local-note-search.md`, content byte-identical); `brief.md` (`:59–63`, `:96–98` only) |
| `plan-required-sections-compliant` | `brief.md` (`:12`, `:17` only: the stale `*-plan.md` path description, O4) |
| `validate-workflow-gate-verdict-sources` | `fixture/implementation/knowledge/skills/validation-gates/SKILL.md` (re-copy byte-identical from source, `cmp`); `brief.md` § Provenance (one bullet for the P-10 change, `T596`) |

**Not authorized:**
- any other `check()` body or constant;
- any `status`, `known_failing_category` or `tags`;
- any other file or case;
- `tests/golden/held-out/` (never open it; prune it from every traversal);
- `scripts/scorecard.py`;
- `evaluator_hash.py`;
- `evaluator-hash-known-good-v*.json`.

Line numbers come from `path-conventions-v3.md` §6 at `c152eb7`. Re-read each file before editing, and match by text,
not by line number.

**Scope extension (orchestrator, 2026-10-08):** because of BLK-T597-1, edits to
`tests/functional/test_golden_harness_scoring.py` are authorized, limited to the string literals at `:77` and `:83`
only (`"docs/plans/feature-audit-log.md"` → `"docs/plans/plan-001-audit-log.md"`).
That file loads the real `new-feature-plan-doc-compliant/expect.py`, so the glob change above made `:77` fail and `:83`
pass vacuously. It is not a protected path. Nothing else in that file is in scope.

## 3. The changes

1. **`new-feature-plan-doc-compliant`:**
   - **Glob.** `expect.py:25` `plans_dir.glob("feature-*.md")` becomes `plans_dir.glob("plan-*.md")`. This is the only
     `check()` change in this task, and it has the same strength: still exactly one matching plan, with the same
     required headers.
   - **Fixture.** Rename `fixture/docs/plans/feature-audit-log-export.md` to `plan-001-audit-log-export.md`. The
     content stays byte-identical, which you can show with `git mv` plus `cmp` against the old blob.
   - **Docstring.** Update the docstring to `/new-feature`'s new step 1 text, quoted verbatim from the merged
     `implementation/knowledge/commands/new-feature.md`.
   - **Brief.** Update the brief's quote, pass condition and provenance in the same way.
2. **`new-project-plan-doc-and-lifecycle-states`:**
   - **Quotes.** Make the `brief.md:16` and `expect.py:6` quotes match the merged `/new-project` step 1 verbatim.
   - **Comment.** Update the `:25` comment to describe the decided `plan-<ID>.md` form.
   - **Fixture.** Rename the fixture plan to `plan-001-taskflow.md`. It must still match the unchanged `PLAN_NAME_RE`;
     confirm this.
   - **Descriptive text.** Update `:72`, `:87` and `:95–98` so every claim is true.
3. **`new-poc-plan-hypothesis-format`.** Rename the fixture plan to `plan-001-local-note-search.md`. Update
   `brief.md:59–63` and `:96–98`. `check()` does not read the path; confirm it still returns its current result.
4. **`plan-required-sections-compliant`.** In `brief.md:12` and `:17`, make the plan-path description true. The
   current text describes an old `*-plan.md` form.
5. **`validate-workflow-gate-verdict-sources`.**
   - Re-copy the `validation-gates` fixture from `implementation/knowledge/skills/validation-gates/SKILL.md` at your
     worktree's commit, and confirm with `cmp`.
   - Add one § Provenance bullet: "§ Gate Input Requirements › Architecture Gate: the plan document's path (`T596`,
     P32), not read by `check()`".
   - Also update the bullet's "copied at `develop` …" reference to your commit.

Every quote must be **verbatim** from the merged source. Diff each one against its source line.

## 4. Controls

- **No result changes.** Record each of the five cases' `check()` result before and after your edits. Run
  `python3 scripts/scorecard.py --check` before and after; both runs must report 34 / 26 / 0.
- **Discrimination for the changed glob** (`new-feature-plan-doc-compliant`). Run these on scratch copies outside the
  repo, and report each result:
  1. The renamed fixture returns True.
  2. A fixture that keeps only the old name, `feature-audit-log-export.md`, returns **False** under the new glob.
  3. Two `plan-*.md` files return False.
  4. A `plan-*.md` fixture missing one required header returns False.
  5. The unmodified copy returns True, as a control.

  Confirm that the mutations actually applied, and that the old glob behaved the mirror-image way on the old fixture.
- **Exactly two evaluator-hash tests will go red.** **Do NOT refresh the baseline.** After committing, report both
  digests against **v17**:
  - `tests_golden` must change from `05fb8b07…`;
  - `scripts_scorecard` must stay `45346c17…`.

  The orchestrator writes v18, which the user has pre-approved, after verifying.
- **Gates and suite.**
  - Run `test_golden_held_out_isolation`, `test_golden_suite_format` and `validate-tasks.py`.
  - Run `python3 tests/run.py`, redirecting output to a file (never `| tail`).
  - Expect 904 tests with **exactly** the two hash failures, and name every failing test.

## 5. Constraints

- **Write scope:** §2, plus this brief's `**Status:**` line (set it to `in_review`).
- **Off limits:** never read `.env*`, credential or key files. Any search that reaches `tests/` must prune
  `tests/golden/held-out` first. **Never write a golden case name unless that case has a `tests/golden/open/`
  directory.**
- **Commit:** commit locally as one Conventional Commit, ending with
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Do not push. Never run `glab mr merge` or any merge or approve API, with no exception.**

## 6. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). If any case result or status would change, stop and report it.
