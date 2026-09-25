"""Drift gate for the committed golden scorecard artifact (T533).

`docs/benchmarks/scorecard-v6.12.0.{json,md}` are **generated** by
`scripts/scorecard.py` from the golden suite tree. Until this module existed,
**nothing in the repository validated them** -- no test under `tests/functional/` or
`tests/performance/`, no `.gitlab-ci.yml` job -- and they rotted accordingly: landed
once at `T410`-`T415` reporting `20` cases / `11` pass / `tracked_defect: 6`, while the
real tree had moved to `24` / `16` / `tracked_defect: 4`. Three separate implementers
(`T521`, `T525`, `T531`) each hit the resulting dirty `git status`, reverted
`docs/benchmarks/` by hand, and moved on; one of them reasonably mis-read the stale file
as a deliberately frozen baseline, because *one commit in history plus several tasks
declining to touch it* is indistinguishable from a freeze policy when the question "who
validates this?" has an empty answer.

**This module is that answer.** Full reasoning:
`docs/plans/plan-075-scorecard-artifact-staleness.md`.

## Why a test rather than a standalone CI job

This is the same class of control this repo already applies to its other generated
artifacts -- `implementation/registry/` via `check.py --registry`, the platform
projections via the `sync-no-diff` pipeline job -- both of which exist precisely because
a generated file nothing checks drifts. Putting it here rather than in a new
`.gitlab-ci.yml` job is deliberate and strictly wider in coverage: `python3 tests/run.py`
is both the local verification command every task brief in this repo already mandates
*and* the `.gitlab-ci.yml` `unit-tests` job's script, so this gate fires in CI **and**
on the implementer's machine before they ever commit -- which is exactly where the three
prior implementers would have caught it. A CI-only job would have added pipeline surface
while still only reporting after a push.

## What is compared, and what deliberately is not

Only the JSON artifact's **`content`** key. `run_metadata.generated_at` is a wall-clock
stamp that differs on every run *by design* (see `scripts/scorecard.py`'s own
determinism section), so comparing whole files would make this gate red on every single
pipeline -- and a permanently-red gate gets disabled, which is strictly worse than no
gate at all. `content` is exactly the boundary the script's own docstring already draws:
"a pure function of the golden suite tree's on-disk bytes".

The Markdown artifact is compared by re-rendering it from the committed JSON's own
`content` *and* `run_metadata`, which holds the timestamp fixed and therefore isolates
real drift -- and additionally catches a `.md` hand-edited away from its own JSON.

## Held-out redaction

Every dict this module reads has already passed through
`scorecard.redact_held_out_identities()`, so no assertion, failure message, or
`diff_content()` line here can carry a real held-out case identity.
`test_committed_artifact_carries_no_unredacted_held_out_identity` asserts that property
of the committed artifact directly rather than trusting it. This module deliberately
contains no path literal naming the protected subdirectory, so
`test_golden_held_out_isolation.py`'s Check A applies to it unmodified and passes -- this
file is **not** on that guard's allowlist and does not need to be.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root

SCORECARD_SCRIPT = repo_root() / "scripts" / "scorecard.py"
REDACTED_ID_PATTERN = re.compile(r"^held-out-case-\d+$")


def _load_scorecard_module():
    """Load `scripts/scorecard.py` by path -- mirrors
    `test_check_version_consistency.py::_load_module()`, the established pattern for
    exercising a `scripts/` entry point that is not an importable package."""
    spec = importlib.util.spec_from_file_location("scorecard_under_test", SCORECARD_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {SCORECARD_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCORECARD_SCRIPT), *args],
        cwd=repo_root(),
        capture_output=True,
        text=True,
        check=False,
    )


class TestCommittedArtifactIsCurrent(unittest.TestCase):
    """The gate itself: the committed artifacts must match a fresh run."""

    @classmethod
    def setUpClass(cls):
        cls.scorecard = _load_scorecard_module()
        cls.json_path, cls.md_path = cls.scorecard.output_paths(repo_root())
        cls.committed = json.loads(cls.json_path.read_text(encoding="utf-8"))
        cls.fresh_content = cls.scorecard.build_content(cls.scorecard.golden_root())

    def test_committed_json_has_the_two_top_level_keys(self):
        self.assertIn("content", self.committed)
        self.assertIn("run_metadata", self.committed)

    def test_committed_content_matches_a_fresh_computation(self):
        differences = self.scorecard.diff_content(self.committed["content"], self.fresh_content)
        self.assertEqual(
            differences,
            [],
            "docs/benchmarks/ is stale relative to the golden suite tree. "
            "Run `python3 scripts/scorecard.py` and commit both artifacts.\n"
            + "\n".join(differences),
        )

    def test_committed_markdown_matches_a_render_of_the_current_content(self):
        """Delegates to the shipped `diff_markdown()` rather than re-implementing the
        comparison, so the test and the `--check` gate can never disagree.

        Note the subtlety `diff_markdown()` encodes and this test must not undo: the
        `.md` is **not** byte-reproducible from a round-trip through the committed
        `.json`. `summarize()` inserts `by_location` keys in `open`, `held-out` order
        and `render_markdown()` emits that table in dict order, but `main()` serializes
        the JSON with `sort_keys=True`, so parsing the committed JSON back yields
        `held-out` before `open`. The render must therefore be driven by a freshly built
        `content` dict (live insertion order, exactly what produced the committed `.md`)
        with only `run_metadata` taken from the committed file to hold `generated_at`
        fixed. This is a pre-existing asymmetry in the script's two output formats, not
        something this gate introduced; correcting it would change the artifact's
        rendering order, which is out of scope here."""
        self.assertEqual(
            self.scorecard.diff_markdown(self.committed, self.fresh_content, self.md_path),
            [],
            "the committed .md is not a faithful render of the current content. "
            "Run `python3 scripts/scorecard.py` and commit both artifacts.",
        )

    def test_committed_artifact_carries_no_unredacted_held_out_identity(self):
        """Held-out redaction must not regress: every held-out-located case in the
        committed artifact carries an anonymized label, never a real case ID or a real
        `case_dir`. See this module's docstring."""
        held_out = [c for c in self.committed["content"]["cases"] if c["location"] == "held-out"]
        self.assertTrue(held_out, "expected the committed artifact to report held-out cases")
        for case in held_out:
            self.assertRegex(case["id"], REDACTED_ID_PATTERN)
            self.assertTrue(
                case["case_dir"].endswith("<redacted>"),
                f"unredacted case_dir in committed artifact: {case['case_dir']!r}",
            )


class TestCheckFlagCli(unittest.TestCase):
    """`--check` is the invocable form of the gate above, for use outside a test run."""

    def test_check_flag_exits_zero_on_the_real_tree(self):
        proc = _run_cli("--check")
        self.assertEqual(proc.returncode, 0, f"stdout={proc.stdout}\nstderr={proc.stderr}")
        self.assertIn("OK", proc.stdout)

    def test_check_flag_writes_nothing(self):
        scorecard = _load_scorecard_module()
        paths = scorecard.output_paths(repo_root())
        before = [p.read_bytes() for p in paths]
        self.assertEqual(_run_cli("--check").returncode, 0)
        self.assertEqual([p.read_bytes() for p in paths], before)

    def test_unrecognized_argument_is_rejected_rather_than_ignored(self):
        """A gate invoked with a typo'd flag must not silently pass."""
        proc = _run_cli("--chekc")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("unrecognized argument", proc.stderr)


class TestDiffContentFixtures(unittest.TestCase):
    """Proves `diff_content()` reports both directions on synthetic dicts, rather than
    only asserting the real tree currently agrees -- mirrors
    `test_golden_held_out_isolation.py::TestFindViolationsSyntheticFixtures`."""

    @staticmethod
    def _content(total: int = 1, bucket: str = "pass") -> dict:
        return {
            "cases": [{"id": "synthetic-case", "location": "open", "bucket": bucket}],
            "summary": {"total_cases": total, "total_pass": 1, "by_location": {}},
        }

    def setUp(self):
        self.scorecard = _load_scorecard_module()

    def test_identical_content_reports_no_differences(self):
        self.assertEqual(self.scorecard.diff_content(self._content(), self._content()), [])

    def test_changed_summary_count_is_reported(self):
        lines = self.scorecard.diff_content(self._content(total=1), self._content(total=2))
        self.assertTrue(any("summary.total_cases" in line for line in lines), lines)

    def test_changed_case_field_is_reported(self):
        lines = self.scorecard.diff_content(self._content(), self._content(bucket="regression"))
        self.assertTrue(any("synthetic-case.bucket" in line for line in lines), lines)

    def test_added_and_removed_cases_are_reported(self):
        empty = {"cases": [], "summary": {}}
        self.assertTrue(
            any("case added" in line for line in self.scorecard.diff_content(empty, self._content()))
        )
        self.assertTrue(
            any("case removed" in line for line in self.scorecard.diff_content(self._content(), empty))
        )

    def test_drift_in_a_key_outside_summary_and_cases_is_still_reported(self):
        base = self._content()
        extended = dict(base, unexpected_future_key={"a": 1})
        lines = self.scorecard.diff_content(base, extended)
        self.assertTrue(any("unexpected_future_key" in line for line in lines), lines)


class TestDiffMarkdownFixtures(unittest.TestCase):
    """Proves `diff_markdown()` reports both directions, not just that the real tree
    currently agrees."""

    def setUp(self):
        self.scorecard = _load_scorecard_module()
        self.committed = json.loads(
            self.scorecard.output_paths(repo_root())[0].read_text(encoding="utf-8")
        )
        self.content = self.scorecard.build_content(self.scorecard.golden_root())

    def test_missing_markdown_file_is_reported(self):
        lines = self.scorecard.diff_markdown(
            self.committed, self.content, repo_root() / "docs" / "benchmarks" / "no-such.md"
        )
        self.assertTrue(any("does not exist" in line for line in lines), lines)

    def test_markdown_that_does_not_match_the_content_is_reported(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            stale = Path(tmp) / "stale.md"
            stale.write_text("# Not the rendered scorecard\n", encoding="utf-8")
            lines = self.scorecard.diff_markdown(self.committed, self.content, stale)
        self.assertTrue(any("does not match" in line for line in lines), lines)

    def test_unusable_run_metadata_is_reported_rather_than_raising(self):
        lines = self.scorecard.diff_markdown(
            {"run_metadata": {}}, self.content, self.scorecard.output_paths(repo_root())[1]
        )
        self.assertTrue(any("cannot re-render" in line for line in lines), lines)


class TestLoadCommittedScorecardFailureModes(unittest.TestCase):
    """A missing or malformed committed artifact is a reportable check failure, never a
    traceback escaping to the caller."""

    def setUp(self):
        self.scorecard = _load_scorecard_module()

    def test_missing_file_is_reported(self):
        data, reason = self.scorecard.load_committed_scorecard(repo_root() / "docs" / "no-such.json")
        self.assertIsNone(data)
        self.assertIn("does not exist", reason)

    def test_malformed_json_is_reported(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text("{not json", encoding="utf-8")
            data, reason = self.scorecard.load_committed_scorecard(bad)
        self.assertIsNone(data)
        self.assertIn("not valid JSON", reason)

    def test_json_without_a_content_object_is_reported(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            no_content = Path(tmp) / "nc.json"
            no_content.write_text('{"run_metadata": {}}', encoding="utf-8")
            data, reason = self.scorecard.load_committed_scorecard(no_content)
        self.assertIsNone(data)
        self.assertIn("no top-level 'content' object", reason)


if __name__ == "__main__":
    unittest.main()
