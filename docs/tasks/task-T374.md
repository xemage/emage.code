# Task T374 — Add Cline-specific test coverage for `--platform all` render output

**ID:** T374
**Owner:** qa-engineer
**Status:** pending
**Priority:** P0
**Depends on:** T373
**Created:** 2026-08-09
**Based on:** docs/plans/plan-032-render-agents-cline-platform-map-fix.md (P032-02)

This brief is self-contained. You do not need to read plan-032 or T373's brief to execute this
task, though you do need T373's fix already committed on the branch you check out (see Git
workflow below).

## Objective
T373 fixed `scripts/render_installed_agents.py`'s `platform == "all"` branch so it derives its
five platform-reference strings from `PLATFORM_MAP` instead of hardcoded literals, which now
includes `cline`. Before T373's fix, there was no automated test that would have caught `cline`
being omitted — the existing `test_all_platform_install_includes_projection_map` test asserts the
original six platforms but never asserts anything Cline-specific, which is exactly why the bug
shipped undetected in v6.8.0. Close this test-coverage gap so the regression class cannot recur
silently.

## Inputs (exact paths, verified against the current file)
The ONLY file you will edit:
`/home/emage/Code/emage/emage.code/tests/functional/test_install_agents_mapping.py`

Current relevant content (quoted verbatim, lines 50-62 — the method you will extend):
```python
    def test_all_platform_install_includes_projection_map(self) -> None:
        with tempfile.TemporaryDirectory(prefix="emage-install-all-") as tmp:
            content = self._run_install(Path(tmp), "all")

        self.assertIn("`.github/skills/`", content)
        self.assertIn("`.cursor/skills/`", content)
        self.assertIn("`.gemini/skills/`", content)
        self.assertIn("`.opencode/skills/`", content)
        self.assertIn("`.pi/skills/`", content)
        self.assertIn("`.claude/skills/`", content)
        self.assertIn("`.vscode/mcp.json`", content)
        self.assertIn("`.gemini/settings.json`", content)
        self.assertIn("`.opencode/opencode.json`", content)
```
This method installs the `all` platform into a temp directory via the real `scripts/install.sh`
(through the `_run_install` helper at lines 14-21, which you must not modify), reads the resulting
`AGENTS.md`, and asserts specific substrings are present. `PLATFORM_MAP["cline"]`'s paths
(`.cline/skills/`, `.clinerules/coding-standards.md`, `.clinerules/security-guidelines.md`,
`.cline/mcp.json`) are never asserted anywhere in this file today — confirm this yourself with
`grep -n cline tests/functional/test_install_agents_mapping.py` (expect zero matches before your
change).

## Allow-list (files you may touch)
- `tests/functional/test_install_agents_mapping.py` only, and within it, ONLY the body of
  `test_all_platform_install_includes_projection_map` (lines 50-62 as quoted above). Add new
  assertion lines; do not remove or modify any of the 9 existing `assertIn` lines.

## Deny-list (do not touch — no exceptions)
- Do NOT edit `scripts/render_installed_agents.py` — T373 already fixed it; this task only adds
  test coverage proving the fix.
- Do NOT edit `scripts/install.sh` or the `_run_install` helper (lines 14-21 of the test file).
- Do NOT edit any other test file in `tests/`.
- Do NOT add a new test file — extend the existing method in the existing file (do not add a
  sibling `test_cline_...` method either; that is out of scope for this task — keep the change
  minimal and inside the one method named above).
- Do NOT add a new test method that re-runs `_run_install` a second time for `all` or for `cline`
  specifically — that would duplicate the slow subprocess install already performed once in this
  method; extend the existing assertions in-place instead.
- Do NOT create any new branch — use the branch T373 already created (see Git workflow below).

## Exact change to make
Add these 6 lines immediately after the existing line
`self.assertIn("`.opencode/opencode.json`", content)` (the last line of the method body), inside
the same method, at the same indentation:
```python
        self.assertIn("`.cline/skills/`", content)
        self.assertIn("`.clinerules/coding-standards.md`", content)
        self.assertIn("`.clinerules/security-guidelines.md`", content)
        self.assertIn("`.cline/mcp.json`", content)
        self.assertIn("`.cline/`", content)
        self.assertIn("`.clinerules/`", content)
```
The resulting method must have exactly 9 pre-existing `assertIn` lines (unchanged) followed by
these 6 new ones (15 total), with no other changes to the method or the file.

## Tests to run (literal commands, run from repo root `/home/emage/Code/emage/emage.code`)

1. Targeted run of just this test file:
   ```
   python3 -m unittest tests.functional.test_install_agents_mapping -v
   ```
   PASS = `Ran 4 tests` and `OK` at the end (all 4 existing test methods in this file still pass,
   including your extended one — this actually runs `scripts/install.sh` end-to-end into a temp
   dir, so it depends on T373's fix already being present).

2. Full functional suite:
   ```
   python3 tests/run.py --suite functional -v
   ```
   PASS = exits 0, no `FAILED`/`ERROR` lines.

3. Full suite (functional + performance), the same gate T375 will run:
   ```
   python3 tests/run.py
   ```
   PASS = exits 0. Current baseline as of this brief (pre-T374): 299 tests, `OK (skipped=18)`. Your
   change adds assertions to an existing test, so the total test count should not change; the
   `all`-platform test must still report `ok`.

## Acceptance criteria (all must be true)
- [ ] `git diff` shows changes in exactly one file:
      `tests/functional/test_install_agents_mapping.py`.
- [ ] The diff adds exactly the 6 lines listed above (or an equivalent set of assertions producing
      the same effective coverage — see note below) to
      `test_all_platform_install_includes_projection_map`, and does not remove, reorder, or alter
      any of the 9 pre-existing `assertIn` lines.
- [ ] `python3 -m unittest tests.functional.test_install_agents_mapping -v` passes (4/4, `OK`).
- [ ] `python3 tests/run.py` exits 0.
- [ ] If T373's fix is NOT actually present when you run these tests (i.e. the `all`-platform
      output still lacks Cline strings), the new assertions correctly FAIL — do not weaken an
      assertion to make it pass; a failing assertion here means T373 is incomplete or absent, which
      is a blocker (see below), not something to work around in the test.

Note on "equivalent set of assertions": the 6 lines specified are the minimum required — 4 for the
per-section Cline paths named in this task's objective (`.cline/skills/`, `.clinerules/coding-
standards.md`, `.clinerules/security-guidelines.md`, `.cline/mcp.json`) plus 2 for the Knowledge
Base runtime-reference bullet's two distinct Cline root folders (`.cline/`, `.clinerules/`). Do not
add additional assertions beyond these 6 — keep the change minimal and exactly scoped to this list.

## Blocker protocol
STOP and report a blocker (do not improvise a workaround) if:
- The branch T373 created (`bugfix/T373-render-agents-cline-platform-map`) does not exist, or does
  not contain T373's fix (e.g. `--platform all` output still lacks `.cline/skills/`) →
  `type: dependency`, `severity: critical` — T374 cannot proceed without T373's completed fix.
- The current test file content doesn't match what's quoted above (method renamed, lines shifted,
  existing assertions differ) → `type: dependency`, `severity: major` — re-verify against the
  actual current file before proceeding.
- Any test in the "Tests to run" section fails for a reason unrelated to your added assertions →
  `type: technical`, `severity: major`, include exact command output.
- Adding the 6 assertions causes the test to fail because T373's fix produces different output
  than documented (e.g. different Cline path strings than listed here) → `type: technical`,
  `severity: major` — report the actual vs. expected strings; do not alter T373's implementation
  yourself (out of your allow-list) and do not water down the assertion to hide the mismatch.

Max 2 retries before escalating to the orchestrator with full context.

## Git workflow
1. Check out the EXISTING branch `bugfix/T373-render-agents-cline-platform-map` (created by T373
   — do NOT create a new branch, do NOT branch from `develop` again).
2. Confirm T373's commit is present (`git log --oneline -3` should show T373's fix commit).
3. Make the change; run all tests above; confirm all pass.
4. Commit with a Conventional Commit message, e.g.:
   ```
   test(install): assert Cline-specific strings in --platform all render output

   Closes the coverage gap that let T373's bug (cline omitted from the `all`
   branch's hardcoded platform-reference literals) ship undetected in v6.8.0.

   Refs T374
   ```
5. Do NOT push. Do NOT open a merge request. Do NOT merge to `develop` or `main`. Stop after the
   local commit (stacked on top of T373's commit, same branch) and report completion (commit SHA,
   full test output) back to the orchestrator. T375 will push this branch and open the MR.

## Constraints
- Token budget: ≤8k tokens.
- File ownership: `tests/functional/test_install_agents_mapping.py` only, scoped to the one method
  named above.
- No unrelated refactor of this file.
