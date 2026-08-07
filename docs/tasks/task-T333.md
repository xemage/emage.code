# Task T333 — Regression tests for `check-main-develop-drift.py`

**ID:** T333
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T332
**Created:** 2026-08-07
**Completed:** 2026-08-07
**Based on:** `docs/plans/plan-019-main-develop-drift-detection.md` §5, `scripts/check-main-develop-drift.py` (T332)

## Objective

Add regression tests for the pure functions in `scripts/check-main-develop-drift.py`
(`parse_marker`, `semver_key`, `sorted_valid_tags`, `releases_behind`, `evaluate`), covering the
exact scenarios described in `docs/plans/plan-019-main-develop-drift-detection.md` §3 (grace
window, real incident shape, invalid tags, missing markers, main-ahead-of-develop invariant). No
real git repository or subprocess calls are needed — every function under test is pure.

## Inputs

- `scripts/check-main-develop-drift.py` (T332's output — do not modify it in this task; if a bug
  is found, report it as a blocker per the Blocker protocol below rather than silently patching it)
- `tests/functional/test_publish_release.py` (precedent for loading a hyphenated `scripts/*.py`
  file via `importlib.util.spec_from_file_location`)
- `tests/_helpers/repo.py` (`repo_root()` helper)

## Expected outputs

- `tests/functional/test_check_main_develop_drift.py` (new file)

## Exact file content

Create `tests/functional/test_check_main_develop_drift.py` with **exactly** this content (adjust
only if a genuine import/syntax issue is found — note any such fix in Execution notes):

```python
"""Regression tests for scripts/check-main-develop-drift.py drift-detection logic."""
from __future__ import annotations

import importlib.util
import unittest

from tests._helpers.repo import repo_root


def _load_module():
    module_path = repo_root() / "scripts" / "check-main-develop-drift.py"
    spec = importlib.util.spec_from_file_location("check_main_develop_drift", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load check-main-develop-drift module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TAGS = ["v6.3.0", "v6.4.0", "v6.4.1", "v6.4.2", "v6.4.3", "v6.5.0"]


class TestParseMarker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_parses_standard_marker(self):
        text = "Some text\nLatest release: v6.5.0\nMore text\n"
        self.assertEqual(self.mod.parse_marker(text), "v6.5.0")

    def test_returns_none_when_marker_absent(self):
        self.assertIsNone(self.mod.parse_marker("no marker here"))


class TestSemverKeyAndSort(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_rejects_non_semver_tags(self):
        self.assertIsNone(self.mod.semver_key("not-a-tag"))
        self.assertIsNone(
            self.mod.semver_key("backup/release-v6.0.3-pre-rewrite-20260617-065656")
        )

    def test_sorts_ascending_numerically_not_lexically(self):
        shuffled = ["v6.5.0", "v6.4.0", "v6.4.10", "v6.4.2"]
        self.assertEqual(
            self.mod.sorted_valid_tags(shuffled),
            ["v6.4.0", "v6.4.2", "v6.4.10", "v6.5.0"],
        )

    def test_drops_invalid_tags_from_sort(self):
        mixed = ["v1.0.0", "not-a-release", "v1.0.1"]
        self.assertEqual(self.mod.sorted_valid_tags(mixed), ["v1.0.0", "v1.0.1"])


class TestReleasesBehind(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_zero_when_versions_match(self):
        self.assertEqual(self.mod.releases_behind("v6.5.0", "v6.5.0", TAGS), 0)

    def test_counts_gap_correctly_matching_real_incident_shape(self):
        # main=v6.4.2, develop=v6.5.0 -> v6.4.3 and v6.5.0 both missing from main -> 2
        self.assertEqual(self.mod.releases_behind("v6.4.2", "v6.5.0", TAGS), 2)

    def test_raises_on_unknown_main_version(self):
        with self.assertRaises(ValueError):
            self.mod.releases_behind("v9.9.9", "v6.5.0", TAGS)

    def test_raises_on_unknown_develop_version(self):
        with self.assertRaises(ValueError):
            self.mod.releases_behind("v6.4.2", "v9.9.9", TAGS)

    def test_raises_when_main_ahead_of_develop(self):
        with self.assertRaises(ValueError):
            self.mod.releases_behind("v6.5.0", "v6.4.2", TAGS)


class TestEvaluate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_pass_when_in_sync(self):
        code, lines = self.mod.evaluate("v6.5.0", "v6.5.0", TAGS)
        self.assertEqual(code, 0)
        self.assertTrue(any("PASS" in line for line in lines))

    def test_pass_within_one_release_grace(self):
        code, _lines = self.mod.evaluate("v6.4.3", "v6.5.0", TAGS)
        self.assertEqual(code, 0)

    def test_fail_when_more_than_one_release_behind(self):
        code, lines = self.mod.evaluate("v6.4.2", "v6.5.0", TAGS)
        self.assertEqual(code, 1)
        self.assertTrue(any("FAIL" in line for line in lines))
        self.assertTrue(any("v6.4.3" in line and "v6.5.0" in line for line in lines))

    def test_fail_when_main_marker_missing(self):
        code, _lines = self.mod.evaluate(None, "v6.5.0", TAGS)
        self.assertEqual(code, 1)

    def test_fail_when_develop_marker_missing(self):
        code, _lines = self.mod.evaluate("v6.5.0", None, TAGS)
        self.assertEqual(code, 1)

    def test_fail_when_main_ahead_of_develop(self):
        code, _lines = self.mod.evaluate("v6.5.0", "v6.4.2", TAGS)
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
```

## Acceptance criteria

1. `tests/functional/test_check_main_develop_drift.py` exists with the exact content above (or a
   version fixing only genuine issues, noted in Execution notes).
2. `python3 tests/run.py --suite functional -v 2>&1 | grep -A2 "test_check_main_develop_drift\|Ran"`
   — full functional suite still passes (0 failures) with the new test file included in the count.
3. Direct isolated run:
   ```bash
   python3 -m unittest tests.functional.test_check_main_develop_drift -v
   echo "EXIT_CODE=$?"
   ```
   Expected: all listed test methods (14 total) `ok`, `EXIT_CODE=0`.
4. No modification made to `scripts/check-main-develop-drift.py` in this task — if any test fails
   against T332's actual output, that is a blocker to report, not something to silently patch
   around.

## Blocker protocol

Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes

**Executed by:** qa-engineer, 2026-08-07, worktree `agent-af40748c222647533` (branch
`feature/332-main-develop-drift-detection`).

### AC1 — file exists with exact content

`tests/functional/test_check_main_develop_drift.py` was created with the **exact** content given
in this brief, verbatim. No import/syntax issue was found — the module-loading pattern mirrors
`tests/functional/test_publish_release.py` exactly, and manual trace of every test case against
`scripts/check-main-develop-drift.py`'s actual `parse_marker`/`semver_key`/`sorted_valid_tags`/
`releases_behind`/`evaluate` implementations confirmed the expected values before running (e.g.
`releases_behind("v6.4.2", "v6.5.0", TAGS)` → index 3 to index 5 → `2`, matching the "real
incident shape" assertion). No deviation was made from the brief's file content.

### AC2 — full functional suite

Command: `python3 tests/run.py --suite functional -v 2>&1 | grep -A2
"test_check_main_develop_drift\|Ran"`

```
test_fail_when_develop_marker_missing (tests.functional.test_check_main_develop_drift.TestEvaluate.test_fail_when_develop_marker_missing) ... ok
test_fail_when_main_ahead_of_develop (tests.functional.test_check_main_develop_drift.TestEvaluate.test_fail_when_main_ahead_of_develop) ... ok
test_fail_when_main_marker_missing (tests.functional.test_check_main_develop_drift.TestEvaluate.test_fail_when_main_marker_missing) ... ok
test_fail_when_more_than_one_release_behind (tests.functional.test_check_main_develop_drift.TestEvaluate.test_fail_when_more_than_one_release_behind) ... ok
test_pass_when_in_sync (tests.functional.test_check_main_develop_drift.TestEvaluate.test_pass_when_in_sync) ... ok
test_pass_within_one_release_grace (tests.functional.test_check_main_develop_drift.TestEvaluate.test_pass_within_one_release_grace) ... ok
test_parses_standard_marker (tests.functional.test_check_main_develop_drift.TestParseMarker.test_parses_standard_marker) ... ok
test_returns_none_when_marker_absent (tests.functional.test_check_main_develop_drift.TestParseMarker.test_returns_none_when_marker_absent) ... ok
test_counts_gap_correctly_matching_real_incident_shape (tests.functional.test_check_main_develop_drift.TestReleasesBehind.test_counts_gap_correctly_matching_real_incident_shape) ... ok
test_raises_on_unknown_develop_version (tests.functional.test_check_main_develop_drift.TestReleasesBehind.test_raises_on_unknown_develop_version) ... ok
test_raises_on_unknown_main_version (tests.functional.test_check_main_develop_drift.TestReleasesBehind.test_raises_on_unknown_main_version) ... ok
test_raises_when_main_ahead_of_develop (tests.functional.test_check_main_develop_drift.TestReleasesBehind.test_raises_when_main_ahead_of_develop) ... ok
test_zero_when_versions_match (tests.functional.test_check_main_develop_drift.TestReleasesBehind.test_zero_when_versions_match) ... ok
test_drops_invalid_tags_from_sort (tests.functional.test_check_main_develop_drift.TestSemverKeyAndSort.test_drops_invalid_tags_from_sort) ... ok
test_rejects_non_semver_tags (tests.functional.test_check_main_develop_drift.TestSemverKeyAndSort.test_rejects_non_semver_tags) ... ok
test_sorts_ascending_numerically_not_lexically (tests.functional.test_check_main_develop_drift.TestSemverKeyAndSort.test_sorts_ascending_numerically_not_lexically) ... ok
test_agent_references_resolve (tests.functional.test_cross_references.TestCrossReferences.test_agent_references_resolve) ... ok
test_mcp_tool_references_resolve (tests.functional.test_cross_references.TestCrossReferences.test_mcp_tool_references_resolve) ... ok
--
Ran 268 tests in 17.438s

OK (skipped=17)
```

All 16 new test methods appear as `ok`; full functional suite `OK (skipped=17)`, no failures. PASS.

### AC3 — direct isolated run

Command:
```bash
python3 -m unittest tests.functional.test_check_main_develop_drift -v
echo "EXIT_CODE=$?"
```

```
test_fail_when_develop_marker_missing (tests.functional.test_check_main_develop_drift.TestEvaluate.test_fail_when_develop_marker_missing) ... ok
test_fail_when_main_ahead_of_develop (tests.functional.test_check_main_develop_drift.TestEvaluate.test_fail_when_main_ahead_of_develop) ... ok
test_fail_when_main_marker_missing (tests.functional.test_check_main_develop_drift.TestEvaluate.test_fail_when_main_marker_missing) ... ok
test_fail_when_more_than_one_release_behind (tests.functional.test_check_main_develop_drift.TestEvaluate.test_fail_when_more_than_one_release_behind) ... ok
test_pass_when_in_sync (tests.functional.test_check_main_develop_drift.TestEvaluate.test_pass_when_in_sync) ... ok
test_pass_within_one_release_grace (tests.functional.test_check_main_develop_drift.TestEvaluate.test_pass_within_one_release_grace) ... ok
test_parses_standard_marker (tests.functional.test_check_main_develop_drift.TestParseMarker.test_parses_standard_marker) ... ok
test_returns_none_when_marker_absent (tests.functional.test_check_main_develop_drift.TestParseMarker.test_returns_none_when_marker_absent) ... ok
test_counts_gap_correctly_matching_real_incident_shape (tests.functional.test_check_main_develop_drift.TestReleasesBehind.test_counts_gap_correctly_matching_real_incident_shape) ... ok
test_raises_on_unknown_develop_version (tests.functional.test_check_main_develop_drift.TestReleasesBehind.test_raises_on_unknown_develop_version) ... ok
test_raises_on_unknown_main_version (tests.functional.test_check_main_develop_drift.TestReleasesBehind.test_raises_on_unknown_main_version) ... ok
test_raises_when_main_ahead_of_develop (tests.functional.test_check_main_develop_drift.TestReleasesBehind.test_raises_when_main_ahead_of_develop) ... ok
test_zero_when_versions_match (tests.functional.test_check_main_develop_drift.TestReleasesBehind.test_zero_when_versions_match) ... ok
test_drops_invalid_tags_from_sort (tests.functional.test_check_main_develop_drift.TestSemverKeyAndSort.test_drops_invalid_tags_from_sort) ... ok
test_rejects_non_semver_tags (tests.functional.test_check_main_develop_drift.TestSemverKeyAndSort.test_rejects_non_semver_tags) ... ok
test_sorts_ascending_numerically_not_lexically (tests.functional.test_check_main_develop_drift.TestSemverKeyAndSort.test_sorts_ascending_numerically_not_lexically) ... ok

----------------------------------------------------------------------
Ran 16 tests in 0.003s

OK
EXIT_CODE=0
```

**Discrepancy note (documentation-only, not a code/test fix):** the brief's Acceptance Criteria §3
states "all listed test methods (14 total) `ok`". Counting the methods actually listed in this
brief's "Exact file content" section gives **16**: `TestParseMarker` (2) + `TestSemverKeyAndSort`
(3) + `TestReleasesBehind` (5) + `TestEvaluate` (6) = 16. Both the isolated run and the full-suite
run above independently confirm "Ran 16 tests ... OK". The test file content itself was not
altered — this is purely an inaccurate expected count in the brief's narrative text, not a defect
in the file or in `scripts/check-main-develop-drift.py`. Reporting as informational per the "note
deviations in Execution notes" instruction rather than as a blocker, since all 16 tests pass and
zero failures/errors occurred.

### AC4 — `scripts/check-main-develop-drift.py` untouched

```
$ git diff scripts/check-main-develop-drift.py
(empty output)
```

Confirmed no modification was made to `scripts/check-main-develop-drift.py` in this task.

### Scope note

`git status --porcelain` at the time of this run also showed pre-existing unstaged modifications
to `CONTRIBUTING.md` and `docs/tasks/task-T335.md` in this shared worktree. These are outside this
task's scope (T333 only touches `tests/functional/test_check_main_develop_drift.py` and this task
brief) and were not made by this task execution.

### Verdict

All 4 acceptance criteria PASS. No blockers. `scripts/check-main-develop-drift.py` was not
modified.
