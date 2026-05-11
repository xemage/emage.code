"""Orchestration trajectory quality benchmark for multi-turn planning traces."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests._helpers.repo import repo_root


FIXTURE_PATH = Path("tests/fixtures/benchmarks/trajectory_cases.json")
THRESHOLD_PATH = Path("tests/_baselines/benchmark-thresholds-v1.json")


def _load_json(path: Path) -> dict:
    return json.loads((repo_root() / path).read_text(encoding="utf-8"))


def _plan_coverage_score(required_items: list[str], candidate_items: list[str]) -> float:
    required = set(required_items)
    if not required:
        return 1.0
    candidate = set(candidate_items)
    return len(required & candidate) / len(required)


def _dependency_validity_score(allowed: list[list[str]], candidate: list[list[str]]) -> float:
    if not candidate:
        return 1.0
    allowed_set = {tuple(edge) for edge in allowed}
    candidate_set = [tuple(edge) for edge in candidate]
    valid = sum(1 for edge in candidate_set if edge in allowed_set)
    return valid / len(candidate_set)


def _blocker_routing_score(events: list[dict], routing_policy: dict[str, str]) -> float:
    if not events:
        return 1.0
    correct = 0
    for event in events:
        blocker_type = event.get("type")
        expected_owner = routing_policy.get(blocker_type)
        if expected_owner is None:
            continue
        if event.get("routed_to") == expected_owner:
            correct += 1
    return correct / len(events)


def _lifecycle_transition_score(
    transitions: list[list[str]],
    valid_transitions: dict[str, list[str]],
) -> float:
    if not transitions:
        return 1.0
    valid = 0
    for src, dst in transitions:
        allowed = valid_transitions.get(src, [])
        if dst in allowed:
            valid += 1
    return valid / len(transitions)


class TestOrchestrationTrajectoryQuality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = _load_json(FIXTURE_PATH)
        cls.thresholds = _load_json(THRESHOLD_PATH)["orchestration_trajectory_quality"]

    def test_orchestration_quality_scores(self):
        weights = self.dataset["weights"]
        routing_policy = self.dataset["routing_policy"]
        valid_transitions = self.dataset["valid_transitions"]
        cases = self.dataset["cases"]

        per_case_scores: list[dict[str, float]] = []
        for case in cases:
            plan_coverage = _plan_coverage_score(
                case.get("required_plan_items", []), case.get("candidate_plan_items", [])
            )
            dependency_validity = _dependency_validity_score(
                case.get("allowed_dependencies", []), case.get("candidate_dependencies", [])
            )
            blocker_routing = _blocker_routing_score(
                case.get("blocker_events", []), routing_policy
            )
            lifecycle = _lifecycle_transition_score(
                case.get("state_transitions", []), valid_transitions
            )

            aggregate = (
                plan_coverage * weights["plan_coverage_score"]
                + dependency_validity * weights["dependency_validity_score"]
                + blocker_routing * weights["blocker_routing_score"]
                + lifecycle * weights["lifecycle_transition_score"]
            )

            per_case_scores.append(
                {
                    "plan_coverage_score": plan_coverage,
                    "dependency_validity_score": dependency_validity,
                    "blocker_routing_score": blocker_routing,
                    "lifecycle_transition_score": lifecycle,
                    "aggregate_weighted_score": aggregate,
                }
            )

        count = len(per_case_scores)
        self.assertGreater(count, 0, "trajectory dataset has no cases")

        summary = {
            metric: sum(item[metric] for item in per_case_scores) / count
            for metric in (
                "plan_coverage_score",
                "dependency_validity_score",
                "blocker_routing_score",
                "lifecycle_transition_score",
                "aggregate_weighted_score",
            )
        }

        print("\n[orchestration-trajectory-quality]")
        print(f"  cases={count}")
        print(f"  plan_coverage_score={summary['plan_coverage_score']:.3f}")
        print(f"  dependency_validity_score={summary['dependency_validity_score']:.3f}")
        print(f"  blocker_routing_score={summary['blocker_routing_score']:.3f}")
        print(f"  lifecycle_transition_score={summary['lifecycle_transition_score']:.3f}")
        print(f"  aggregate_weighted_score={summary['aggregate_weighted_score']:.3f}")

        self.assertGreaterEqual(
            summary["plan_coverage_score"],
            self.thresholds["min_plan_coverage_score"],
            msg="plan_coverage_score below threshold",
        )
        self.assertGreaterEqual(
            summary["dependency_validity_score"],
            self.thresholds["min_dependency_validity_score"],
            msg="dependency_validity_score below threshold",
        )
        self.assertGreaterEqual(
            summary["blocker_routing_score"],
            self.thresholds["min_blocker_routing_score"],
            msg="blocker_routing_score below threshold",
        )
        self.assertGreaterEqual(
            summary["lifecycle_transition_score"],
            self.thresholds["min_lifecycle_transition_score"],
            msg="lifecycle_transition_score below threshold",
        )
        self.assertGreaterEqual(
            summary["aggregate_weighted_score"],
            self.thresholds["min_aggregate_weighted_score"],
            msg="aggregate_weighted_score below threshold",
        )


if __name__ == "__main__":
    unittest.main()
