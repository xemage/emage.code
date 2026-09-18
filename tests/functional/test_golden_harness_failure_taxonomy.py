"""Tests for `implementation/runtime/golden_harness/failure_taxonomy.py` (T501).

Exercises `FailureTaxonomy` against the real, on-disk
`docs/benchmarks/failures/**` data -- not mocked/fixture data -- and asserts
specific, known-correct values reproduced from that directory's own
`README.md` index tables (both the golden-suite table and the Terminal-Bench
table), so a regression that silently changes a parsed axis value or drops a
record would be caught here, not just "returns something non-empty".

A small number of edge-case tests (duplicate `case_id` across sources,
missing axis rows) use synthetic temp-directory fixtures, mirroring
`test_golden_held_out_isolation.py`'s own split between real-tree proof tests
and synthetic-fixture edge-case tests.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from implementation.runtime.golden_harness.failure_taxonomy import (
    SOURCE_GOLDEN_SUITE,
    SOURCE_TERMINAL_BENCH,
    FailureTaxonomy,
)
from tests._helpers.repo import repo_root


def _real_failures_dir() -> Path:
    return repo_root() / "docs" / "benchmarks" / "failures"


class TestLoadRealData(unittest.TestCase):
    """The real proof: parses the real 15 committed failure records."""

    @classmethod
    def setUpClass(cls):
        cls.taxonomy = FailureTaxonomy.load(_real_failures_dir())

    def test_loads_exactly_fifteen_records(self):
        # 9 golden-suite known_failing cases (T415) + 6 Terminal-Bench failure
        # patterns (T409) -- docs/benchmarks/failures/README.md's own two
        # index tables ("9 files, 9 cases" / "6 files, 6 distinct failure
        # patterns").
        self.assertEqual(len(self.taxonomy.all_records()), 15)
        self.assertEqual(len(self.taxonomy), 15)

    def test_golden_suite_and_terminal_bench_counts(self):
        golden = self.taxonomy.filter_by(source=SOURCE_GOLDEN_SUITE)
        terminal_bench = self.taxonomy.filter_by(source=SOURCE_TERMINAL_BENCH)
        self.assertEqual(len(golden), 9)
        self.assertEqual(len(terminal_bench), 6)

    def test_all_expected_case_ids_present(self):
        expected_golden = {
            "code-review-conditional-pass-conditions-gap",
            "new-feature-real-checkpoint-format-drift",
            "plan-real-doc-header-drift",
            "prepare-release-conditional-pass-conditions-gap",
            "prepare-release-real-verdict-missing",
            "security-audit-critical-not-fail",
            "held-out-case-1",
            "held-out-case-3",
            "held-out-case-4",
        }
        expected_terminal_bench = {
            "incorrect-computed-output-value",
            "invariant-violation-in-generated-artifact",
            "required-output-artifact-absent",
            "runtime-service-not-functional",
            "produced-code-fails-to-build",
            "verifier-crashes-on-missing-dependency",
        }
        actual_ids = {r.case_id for r in self.taxonomy.all_records()}
        self.assertEqual(actual_ids, expected_golden | expected_terminal_bench)

    def test_get_known_golden_case_exact_axis_values(self):
        # docs/benchmarks/failures/README.md golden-suite index, row 1.
        record = self.taxonomy.get("code-review-conditional-pass-conditions-gap")
        self.assertEqual(record.source, SOURCE_GOLDEN_SUITE)
        self.assertEqual(record.known_failing_category, "capability_gap")
        self.assertEqual(record.cause, "undefined-structured-convention")
        self.assertEqual(record.behavior, "required-section-absent")
        self.assertEqual(record.mechanism, "field-level-absence-within-declared-block")
        self.assertEqual(
            record.axes(),
            (
                "undefined-structured-convention",
                "required-section-absent",
                "field-level-absence-within-declared-block",
            ),
        )
        self.assertFalse(record.is_held_out)
        self.assertEqual(
            record.relative_path, "code-review-conditional-pass-conditions-gap.md"
        )

    def test_get_known_held_out_golden_case_is_flagged_and_never_leaks_real_identity(self):
        record = self.taxonomy.get("held-out-case-3")
        self.assertTrue(record.is_held_out)
        self.assertEqual(record.known_failing_category, "tracked_defect")
        self.assertEqual(record.cause, "established-practice-drift")
        self.assertEqual(record.behavior, "naming-or-format-drift")
        self.assertEqual(record.mechanism, "naming-convention-drift")
        # The case_id itself is the redacted label, not a real held-out identity.
        self.assertEqual(record.case_id, "held-out-case-3")

    def test_get_known_terminal_bench_case_exact_axis_values_and_no_kfc(self):
        # docs/benchmarks/failures/README.md Terminal-Bench index, row 1.
        record = self.taxonomy.get("incorrect-computed-output-value")
        self.assertEqual(record.source, SOURCE_TERMINAL_BENCH)
        self.assertEqual(record.cause, "agent-incorrect-domain-computation")
        self.assertEqual(record.behavior, "incorrect-computed-output-value")
        self.assertEqual(record.mechanism, "wrong-value-vs-ground-truth")
        # known_failing_category (T410 axis) is a golden-suite-only concept.
        self.assertIsNone(record.known_failing_category)
        self.assertFalse(record.is_held_out)
        self.assertEqual(
            record.relative_path, "terminal-bench/incorrect-computed-output-value.md"
        )

    def test_get_raises_lookup_error_for_unknown_case_id(self):
        with self.assertRaises(LookupError):
            self.taxonomy.get("does-not-exist-anywhere")

    def test_filter_by_cause_established_practice_drift_spans_five_golden_cases(self):
        # README golden-suite index: exactly 5 rows carry this cause.
        records = self.taxonomy.filter_by(cause="established-practice-drift")
        self.assertEqual(
            {r.case_id for r in records},
            {
                "new-feature-real-checkpoint-format-drift",
                "plan-real-doc-header-drift",
                "prepare-release-real-verdict-missing",
                "held-out-case-1",
                "held-out-case-3",
            },
        )
        self.assertTrue(all(r.source == SOURCE_GOLDEN_SUITE for r in records))

    def test_filter_by_behavior_required_section_absent_spans_both_sources(self):
        # `required-section-absent` is reused unmodified by one Terminal-Bench
        # pattern (README.md "Combined proof" section) -- this is the concrete
        # "one taxonomy, two sources" query this task's brief cites as the
        # module's whole point.
        records = self.taxonomy.filter_by(behavior="required-section-absent")
        self.assertEqual(
            {r.case_id for r in records},
            {
                "code-review-conditional-pass-conditions-gap",
                "prepare-release-conditional-pass-conditions-gap",
                "prepare-release-real-verdict-missing",
                "held-out-case-4",
                "required-output-artifact-absent",
            },
        )
        sources = {r.source for r in records}
        self.assertEqual(sources, {SOURCE_GOLDEN_SUITE, SOURCE_TERMINAL_BENCH})

    def test_filter_by_mechanism_cross_field_invariant_violation_spans_both_sources(self):
        records = self.taxonomy.filter_by(mechanism="cross-field-invariant-violation")
        self.assertEqual(
            {r.case_id for r in records},
            {"security-audit-critical-not-fail", "invariant-violation-in-generated-artifact"},
        )

    def test_filter_by_combined_axes_narrows_correctly(self):
        # capability_gap golden cases all share cause=undefined-structured-
        # convention (failure-taxonomy-v1.md SS2) but split behavior/mechanism
        # between "field-level-absence" (2 cases) and "whole-block-absence"
        # (1 case, held-out-case-4).
        records = self.taxonomy.filter_by(
            cause="undefined-structured-convention",
            mechanism="whole-block-absence",
        )
        self.assertEqual({r.case_id for r in records}, {"held-out-case-4"})

    def test_filter_by_no_filters_returns_everything(self):
        self.assertEqual(len(self.taxonomy.filter_by()), 15)

    def test_filter_by_source_terminal_bench_exact_set(self):
        records = self.taxonomy.filter_by(source=SOURCE_TERMINAL_BENCH)
        self.assertEqual(
            {r.case_id for r in records},
            {
                "incorrect-computed-output-value",
                "invariant-violation-in-generated-artifact",
                "required-output-artifact-absent",
                "runtime-service-not-functional",
                "produced-code-fails-to-build",
                "verifier-crashes-on-missing-dependency",
            },
        )


class TestLoadSyntheticFixtures(unittest.TestCase):
    """Edge cases not exercised by the real (currently well-formed) data."""

    def test_duplicate_case_id_across_sources_raises_value_error(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            tb_dir = tmp / "terminal-bench"
            tb_dir.mkdir()
            body = (
                "# Failure classification: `dup-case`\n\n"
                "| Axis | Value |\n|---|---|\n"
                "| `cause` | `x` |\n| `behavior` | `y` |\n| `mechanism` | `z` |\n"
            )
            (tmp / "dup-case.md").write_text(body)
            (tb_dir / "dup-case.md").write_text(body)
            with self.assertRaises(ValueError):
                FailureTaxonomy.load(tmp)

    def test_file_missing_an_axis_row_raises_value_error(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            (tmp / "incomplete-case.md").write_text(
                "# Failure classification: `incomplete-case`\n\n"
                "| Axis | Value |\n|---|---|\n"
                "| `cause` | `x` |\n| `behavior` | `y` |\n"
                # `mechanism` row deliberately omitted.
            )
            with self.assertRaises(ValueError):
                FailureTaxonomy.load(tmp)

    def test_missing_terminal_bench_subdirectory_is_tolerated(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            (tmp / "solo-case.md").write_text(
                "# Failure classification: `solo-case`\n\n"
                "| Axis | Value |\n|---|---|\n"
                "| `cause` | `x` |\n| `behavior` | `y` |\n| `mechanism` | `z` |\n"
            )
            taxonomy = FailureTaxonomy.load(tmp)
            self.assertEqual(len(taxonomy), 1)
            self.assertEqual(taxonomy.get("solo-case").source, SOURCE_GOLDEN_SUITE)

    def test_readme_md_is_never_parsed_as_a_case_file(self):
        with tempfile.TemporaryDirectory() as tmp_s:
            tmp = Path(tmp_s)
            (tmp / "README.md").write_text("# Index\n\nNo axis rows here.\n")
            (tmp / "real-case.md").write_text(
                "# Failure classification: `real-case`\n\n"
                "| Axis | Value |\n|---|---|\n"
                "| `cause` | `x` |\n| `behavior` | `y` |\n| `mechanism` | `z` |\n"
            )
            taxonomy = FailureTaxonomy.load(tmp)
            self.assertEqual(len(taxonomy), 1)
            self.assertEqual(taxonomy.get("real-case").case_id, "real-case")


if __name__ == "__main__":
    unittest.main()
