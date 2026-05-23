"""Tool-use complexity benchmark inspired by function-calling evaluations."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root


FIXTURE_PATH = Path("tests/fixtures/benchmarks/tool_use_cases.json")
THRESHOLD_PATH = Path("tests/_baselines/benchmark-thresholds-v1.json")


def _load_json(path: Path) -> dict:
    return json.loads((repo_root() / path).read_text(encoding="utf-8"))


def _flatten_tool_calls(candidate_steps: list[dict]) -> list[dict]:
    calls: list[dict] = []
    for step in candidate_steps:
        calls.extend(step.get("tool_calls", []))
    return calls


def _tool_selection_accuracy(expected_tools: list[str], calls: list[dict]) -> float:
    expected = set(expected_tools)
    used = {call.get("tool") for call in calls if call.get("tool")}
    union = expected | used
    if not union:
        return 1.0
    return len(expected & used) / len(union)


def _argument_key_accuracy(expected_argument_keys: dict[str, list[str]], calls: list[dict]) -> float:
    if not expected_argument_keys:
        return 1.0

    by_tool: dict[str, set[str]] = {}
    for call in calls:
        tool = call.get("tool")
        if not tool:
            continue
        args = call.get("arguments", {})
        if not isinstance(args, dict):
            continue
        by_tool.setdefault(tool, set()).update(args.keys())

    tool_scores: list[float] = []
    for tool, expected_keys in expected_argument_keys.items():
        expected = set(expected_keys)
        if not expected:
            tool_scores.append(1.0)
            continue
        provided = by_tool.get(tool, set())
        tool_scores.append(len(expected & provided) / len(expected))

    return sum(tool_scores) / len(tool_scores)


def _step_efficiency(optimal_steps: int, actual_steps: int) -> float:
    if actual_steps <= 0:
        return 0.0
    if optimal_steps <= 0:
        return 1.0
    return min(1.0, optimal_steps / actual_steps)


class TestToolUseComplexity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = _load_json(FIXTURE_PATH)
        cls.thresholds = _load_json(THRESHOLD_PATH)["tool_use_complexity"]

    def test_tool_use_complexity_scores(self):
        weights = self.dataset["weights"]
        cases = self.dataset["cases"]

        per_case_scores: list[dict[str, float]] = []
        for case in cases:
            candidate_steps = case.get("candidate_steps", [])
            calls = _flatten_tool_calls(candidate_steps)

            selection = _tool_selection_accuracy(case.get("expected_tools", []), calls)
            key_accuracy = _argument_key_accuracy(case.get("expected_argument_keys", {}), calls)
            efficiency = _step_efficiency(case.get("optimal_steps", 0), len(candidate_steps))
            aggregate = (
                selection * weights["tool_selection_accuracy"]
                + key_accuracy * weights["argument_key_accuracy"]
                + efficiency * weights["step_efficiency"]
            )

            per_case_scores.append(
                {
                    "tool_selection_accuracy": selection,
                    "argument_key_accuracy": key_accuracy,
                    "step_efficiency": efficiency,
                    "aggregate_weighted_score": aggregate,
                }
            )

        count = len(per_case_scores)
        self.assertGreater(count, 0, "tool-use dataset has no cases")

        summary = {
            metric: sum(item[metric] for item in per_case_scores) / count
            for metric in (
                "tool_selection_accuracy",
                "argument_key_accuracy",
                "step_efficiency",
                "aggregate_weighted_score",
            )
        }

        print("\n[tool-use-complexity]")
        print(f"  cases={count}")
        print(f"  tool_selection_accuracy={summary['tool_selection_accuracy']:.3f}")
        print(f"  argument_key_accuracy={summary['argument_key_accuracy']:.3f}")
        print(f"  step_efficiency={summary['step_efficiency']:.3f}")
        print(f"  aggregate_weighted_score={summary['aggregate_weighted_score']:.3f}")

        self.assertGreaterEqual(
            summary["tool_selection_accuracy"],
            self.thresholds["min_tool_selection_accuracy"],
            msg="tool_selection_accuracy below threshold",
        )
        self.assertGreaterEqual(
            summary["argument_key_accuracy"],
            self.thresholds["min_argument_key_accuracy"],
            msg="argument_key_accuracy below threshold",
        )
        self.assertGreaterEqual(
            summary["step_efficiency"],
            self.thresholds["min_step_efficiency"],
            msg="step_efficiency below threshold",
        )
        self.assertGreaterEqual(
            summary["aggregate_weighted_score"],
            self.thresholds["min_aggregate_weighted_score"],
            msg="aggregate_weighted_score below threshold",
        )


if __name__ == "__main__":
    unittest.main()
