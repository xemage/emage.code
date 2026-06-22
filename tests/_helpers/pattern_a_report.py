"""Helpers for generating the Pattern A integration report from test outcomes."""

from __future__ import annotations

import io
import unittest
from typing import Dict, List


SCENARIOS = [
    {
        "id": "S1",
        "name": "Three independent edits merge successfully",
        "expectedOutcome": "merge_success",
        "test_method": "test_three_agent_independent_edits_merge_success",
    },
    {
        "id": "S2",
        "name": "AST pre-check invocation when enabled",
        "expectedOutcome": "precheck_invoked",
        "test_method": "test_precheck_is_invoked_when_enabled",
    },
    {
        "id": "S3",
        "name": "Conflicting edits are reported",
        "expectedOutcome": "merge_conflict_reported",
        "test_method": "test_conflicting_merge_is_reported",
    },
    {
        "id": "S4",
        "name": "Merge input build is deterministic",
        "expectedOutcome": "deterministic_projection",
        "test_method": "test_merge_input_build_is_deterministic",
    },
]


class _CollectingResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity) -> None:
        super().__init__(stream, descriptions, verbosity)
        self.outcomes: Dict[str, str] = {}

    @staticmethod
    def _name(test: unittest.case.TestCase) -> str:
        return getattr(test, "_testMethodName", str(test))

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        super().addSuccess(test)
        self.outcomes[self._name(test)] = "pass"

    def addFailure(self, test: unittest.case.TestCase, err) -> None:  # type: ignore[override]
        super().addFailure(test, err)
        self.outcomes[self._name(test)] = "fail"

    def addError(self, test: unittest.case.TestCase, err) -> None:  # type: ignore[override]
        super().addError(test, err)
        self.outcomes[self._name(test)] = "fail"

    def addSkip(self, test: unittest.case.TestCase, reason: str) -> None:  # type: ignore[override]
        super().addSkip(test, reason)
        self.outcomes[self._name(test)] = "fail"


def collect_pattern_a_outcomes() -> Dict[str, str]:
    """Run Pattern A integration tests and return method -> pass/fail outcomes."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(
        "tests.functional.test_pattern_a_integration.TestPatternAIntegration"
    )
    runner = unittest.TextTestRunner(
        stream=io.StringIO(),
        verbosity=0,
        resultclass=_CollectingResult,
    )
    result = runner.run(suite)
    return result.outcomes


def build_pattern_a_report() -> Dict[str, object]:
    """Build report JSON payload based on live test outcomes."""
    outcomes = collect_pattern_a_outcomes()

    scenarios: List[Dict[str, str]] = []
    for scenario in SCENARIOS:
        status = outcomes.get(scenario["test_method"], "fail")
        scenarios.append(
            {
                "id": scenario["id"],
                "name": scenario["name"],
                "expectedOutcome": scenario["expectedOutcome"],
                "status": status,
            }
        )

    passed = sum(1 for scenario in scenarios if scenario["status"] == "pass")
    failed = len(scenarios) - passed

    return {
        "version": "v1",
        "taskId": "T214",
        "generatedBy": "scripts/update_pattern_a_integration_report.py",
        "scenarios": scenarios,
        "summary": {
            "totalScenarios": len(scenarios),
            "passed": passed,
            "failed": failed,
            "overallStatus": "pass" if failed == 0 else "fail",
        },
    }