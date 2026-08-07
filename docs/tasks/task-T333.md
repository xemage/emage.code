# Task T333 — Regression tests for `check-main-develop-drift.py`

**ID:** T333
**Owner:** qa-engineer
**Status:** pending
**Priority:** P0
**Depends on:** T332
**Created:** 2026-08-07
**Completed:** —
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
<not yet picked up>
