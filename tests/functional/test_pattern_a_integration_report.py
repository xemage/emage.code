"""Validate the T214 Pattern A integration report artifact.

This keeps report structure and summary counts stable for CI consumers.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests._helpers.pattern_a_report import build_pattern_a_report
from tests._helpers.repo import repo_root


REPORT_PATH = Path("tests/_reports/pattern-a-integration-report-v1.json")


class TestPatternAIntegrationReport(unittest.TestCase):
    def test_report_file_exists(self) -> None:
        report_path = repo_root() / REPORT_PATH
        self.assertTrue(report_path.exists(), f"missing report artifact: {REPORT_PATH}")

    def test_report_has_expected_schema(self) -> None:
        report_path = repo_root() / REPORT_PATH
        report = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(report.get("version"), "v1")
        self.assertEqual(report.get("taskId"), "T214")
        self.assertIsInstance(report.get("generatedBy"), str)
        self.assertIsInstance(report.get("scenarios"), list)
        self.assertIsInstance(report.get("summary"), dict)

        for scenario in report["scenarios"]:
            self.assertIn("id", scenario)
            self.assertIn("name", scenario)
            self.assertIn("expectedOutcome", scenario)
            self.assertIn("status", scenario)
            self.assertIn(scenario["status"], {"pass", "fail"})

    def test_summary_counts_match_scenarios(self) -> None:
        report_path = repo_root() / REPORT_PATH
        report = json.loads(report_path.read_text(encoding="utf-8"))

        scenarios = report["scenarios"]
        summary = report["summary"]

        passed = sum(1 for item in scenarios if item.get("status") == "pass")
        failed = sum(1 for item in scenarios if item.get("status") == "fail")

        self.assertEqual(summary.get("totalScenarios"), len(scenarios))
        self.assertEqual(summary.get("passed"), passed)
        self.assertEqual(summary.get("failed"), failed)

        expected_overall = "pass" if failed == 0 else "fail"
        self.assertEqual(summary.get("overallStatus"), expected_overall)

    def test_report_matches_regenerated_outcomes(self) -> None:
        report_path = repo_root() / REPORT_PATH
        report = json.loads(report_path.read_text(encoding="utf-8"))

        regenerated = build_pattern_a_report()
        self.assertEqual(
            report,
            regenerated,
            "Report artifact is stale. Run: python3 scripts/update_pattern_a_integration_report.py",
        )


if __name__ == "__main__":
    unittest.main()
