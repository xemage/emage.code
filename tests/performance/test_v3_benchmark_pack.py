"""v3 benchmark pack for planning, safety, routing, and tool efficiency."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root


FIXTURE_PATH = Path("tests/fixtures/benchmarks/v3_benchmark_pack_cases.json")
THRESHOLD_PATH = Path("tests/_baselines/benchmark-thresholds-v1.json")
REPORT_PATH = Path("tests/_reports/v3-benchmark-report-v1.json")


def _load_json(path: Path) -> dict:
    return json.loads((repo_root() / path).read_text(encoding="utf-8"))


def _planning_quality(required_items: list[str], candidate_items: list[str]) -> float:
    required = set(required_items)
    if not required:
        return 1.0
    candidate = set(candidate_items)
    return len(required & candidate) / len(required)


def _safety_compliance(events: list[dict]) -> float:
    if not events:
        return 1.0
    matched = sum(1 for item in events if item.get("expected") == item.get("actual"))
    return matched / len(events)


def _routing_quality(events: list[dict]) -> float:
    if not events:
        return 1.0
    matched = sum(1 for item in events if item.get("expected") == item.get("actual"))
    return matched / len(events)


def _tool_efficiency(optimal_steps: int, actual_steps: int, tool_errors: int, max_tool_errors: int) -> float:
    if actual_steps <= 0:
        return 0.0
    step_eff = min(1.0, optimal_steps / actual_steps) if optimal_steps > 0 else 1.0
    budget = max(1, max_tool_errors)
    error_penalty = min(1.0, tool_errors / budget)
    error_score = 1.0 - error_penalty
    return max(0.0, (step_eff * 0.7) + (error_score * 0.3))


class TestV3BenchmarkPack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = _load_json(FIXTURE_PATH)
        cls.thresholds = _load_json(THRESHOLD_PATH)["v3_benchmark_pack"]

    def test_v3_benchmark_pack_thresholds(self):
        weights = self.dataset["weights"]
        cases = self.dataset["cases"]
        self.assertGreater(len(cases), 0, "benchmark pack must contain cases")

        per_case: list[dict[str, float | str]] = []
        for case in cases:
            planning = _planning_quality(case["required_plan_items"], case["candidate_plan_items"])
            safety = _safety_compliance(case["safety_events"])
            routing = _routing_quality(case["routing_events"])
            efficiency = _tool_efficiency(
                int(case["optimal_steps"]),
                int(case["actual_steps"]),
                int(case["tool_error_count"]),
                int(case["max_tool_errors"]),
            )
            aggregate = (
                planning * float(weights["planning_quality"])
                + safety * float(weights["safety_compliance"])
                + routing * float(weights["orchestration_routing"])
                + efficiency * float(weights["tool_efficiency"])
            )
            per_case.append(
                {
                    "id": case["id"],
                    "planning_quality": planning,
                    "safety_compliance": safety,
                    "orchestration_routing": routing,
                    "tool_efficiency": efficiency,
                    "aggregate_weighted_score": aggregate,
                }
            )

        count = len(per_case)
        summary = {
            metric: sum(float(item[metric]) for item in per_case) / count
            for metric in (
                "planning_quality",
                "safety_compliance",
                "orchestration_routing",
                "tool_efficiency",
                "aggregate_weighted_score",
            )
        }

        report = {
            "schemaVersion": "1.0.0",
            "benchmark": "v3-benchmark-pack",
            "caseCount": count,
            "summary": summary,
            "thresholds": self.thresholds,
            "cases": per_case,
        }
        report_path = repo_root() / REPORT_PATH
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

        print("\n[v3-benchmark-pack]")
        print(f"  cases={count}")
        print(f"  planning_quality={summary['planning_quality']:.3f}")
        print(f"  safety_compliance={summary['safety_compliance']:.3f}")
        print(f"  orchestration_routing={summary['orchestration_routing']:.3f}")
        print(f"  tool_efficiency={summary['tool_efficiency']:.3f}")
        print(f"  aggregate_weighted_score={summary['aggregate_weighted_score']:.3f}")
        print(f"  report={REPORT_PATH}")

        self.assertGreaterEqual(summary["planning_quality"], self.thresholds["min_planning_quality"])
        self.assertGreaterEqual(summary["safety_compliance"], self.thresholds["min_safety_compliance"])
        self.assertGreaterEqual(
            summary["orchestration_routing"], self.thresholds["min_orchestration_routing"]
        )
        self.assertGreaterEqual(summary["tool_efficiency"], self.thresholds["min_tool_efficiency"])
        self.assertGreaterEqual(
            summary["aggregate_weighted_score"], self.thresholds["min_aggregate_weighted_score"]
        )


if __name__ == "__main__":
    unittest.main()
