#!/usr/bin/env python3
"""Deterministic evaluator for emage-agent-task-v1."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def expected_type_name(expected: str) -> type[Any]:
    mapping = {
        "string": str,
        "list": list,
        "object": dict,
        "number": (int, float),
        "bool": bool,
    }
    if expected not in mapping:
        raise ValueError(f"unsupported expected type: {expected}")
    return mapping[expected]


def score_schema_validity(submission: dict[str, Any], ground_truth: dict[str, Any]) -> tuple[float, list[str]]:
    diagnostics: list[str] = []
    requirements = ground_truth["required_top_level_fields"]
    checks = 0
    passed = 0
    for field_name, expected in requirements.items():
        checks += 1
        value = submission.get(field_name)
        if value is None:
            diagnostics.append(f"missing top-level field: {field_name}")
            continue
        if not isinstance(value, expected_type_name(expected)):
            diagnostics.append(f"invalid type for {field_name}: expected {expected}")
            continue
        passed += 1
    return (passed / checks if checks else 0.0), diagnostics


def score_task_quality(submission: dict[str, Any], ground_truth: dict[str, Any]) -> tuple[float, list[str]]:
    diagnostics: list[str] = []
    tasks = submission.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return 0.0, ["tasks must be a non-empty list"]

    allowed_statuses = set(ground_truth["allowed_statuses"])
    allowed_priorities = set(ground_truth["allowed_priorities"])
    required = ground_truth["task_required_fields"]

    checks = 0
    passed = 0
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            diagnostics.append(f"task[{index}] is not an object")
            continue
        for field_name, expected in required.items():
            checks += 1
            value = task.get(field_name)
            if value is None:
                diagnostics.append(f"task[{index}] missing field: {field_name}")
                continue
            if not isinstance(value, expected_type_name(expected)):
                diagnostics.append(
                    f"task[{index}] invalid type for {field_name}: expected {expected}"
                )
                continue
            if field_name == "status" and value not in allowed_statuses:
                diagnostics.append(f"task[{index}] invalid status: {value}")
                continue
            if field_name == "priority" and value not in allowed_priorities:
                diagnostics.append(f"task[{index}] invalid priority: {value}")
                continue
            if field_name == "acceptance_criteria" and len(value) == 0:
                diagnostics.append(f"task[{index}] acceptance_criteria must not be empty")
                continue
            passed += 1
    return (passed / checks if checks else 0.0), diagnostics


def score_dependency_integrity(submission: dict[str, Any]) -> tuple[float, list[str]]:
    diagnostics: list[str] = []
    tasks = submission.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return 0.0, ["dependency checks require a valid tasks list"]

    task_ids = {
        task.get("id")
        for task in tasks
        if isinstance(task, dict) and isinstance(task.get("id"), str)
    }
    checks = 0
    passed = 0
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            continue
        task_id = task.get("id")
        dependencies = task.get("dependencies", [])
        if not isinstance(dependencies, list):
            diagnostics.append(f"task[{index}] dependencies must be a list")
            continue
        for dependency in dependencies:
            checks += 1
            if not isinstance(dependency, str):
                diagnostics.append(f"task[{index}] dependency id must be a string")
                continue
            if dependency == task_id:
                diagnostics.append(f"task[{index}] dependency cannot reference itself")
                continue
            if dependency not in task_ids:
                diagnostics.append(
                    f"task[{index}] dependency not found in task list: {dependency}"
                )
                continue
            passed += 1
    if checks == 0:
        return 1.0, diagnostics
    return passed / checks, diagnostics


def score_content_completeness(submission: dict[str, Any], ground_truth: dict[str, Any]) -> tuple[float, list[str]]:
    diagnostics: list[str] = []
    checks = 3
    passed = 0

    tasks = submission.get("tasks")
    minimum_tasks = int(ground_truth["minimum_tasks"])
    if isinstance(tasks, list) and len(tasks) >= minimum_tasks:
        passed += 1
    else:
        diagnostics.append(f"requires at least {minimum_tasks} tasks")

    risks = submission.get("risks")
    minimum_risks = int(ground_truth["minimum_risks"])
    if isinstance(risks, list) and len(risks) >= minimum_risks:
        passed += 1
    else:
        diagnostics.append(f"requires at least {minimum_risks} risk entries")

    summary = submission.get("summary")
    if isinstance(summary, str) and len(summary.strip()) >= 30:
        passed += 1
    else:
        diagnostics.append("summary must be a string with at least 30 characters")

    return passed / checks, diagnostics


def evaluate_submission(submission: dict[str, Any], ground_truth: dict[str, Any]) -> dict[str, Any]:
    schema_validity, schema_diags = score_schema_validity(submission, ground_truth)
    task_quality, task_diags = score_task_quality(submission, ground_truth)
    dependency_integrity, dependency_diags = score_dependency_integrity(submission)
    content_completeness, completeness_diags = score_content_completeness(
        submission, ground_truth
    )

    metrics = {
        "schema_validity": round(schema_validity, 6),
        "task_quality": round(task_quality, 6),
        "dependency_integrity": round(dependency_integrity, 6),
        "content_completeness": round(content_completeness, 6),
    }
    weights = ground_truth["weights"]
    overall_score = 0.0
    for metric_name, metric_value in metrics.items():
        overall_score += metric_value * float(weights.get(metric_name, 0.0))

    diagnostics = schema_diags + task_diags + dependency_diags + completeness_diags
    pass_threshold = float(ground_truth["pass_threshold"])
    primary_metric = ground_truth["primary_metric"]
    passed = (
        overall_score >= pass_threshold
        and metrics.get(primary_metric, 0.0) >= 1.0
        and metrics["task_quality"] >= 0.9
    )

    return {
        "overall_score": round(overall_score, 6),
        "primary_metric": primary_metric,
        "metrics": metrics,
        "passed": bool(passed),
        "diagnostics": diagnostics,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gen-dir", required=True, help="Directory containing solution.json")
    parser.add_argument("--out", help="Output results.json path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    evaluator_dir = Path(__file__).resolve().parent
    ground_truth_path = evaluator_dir.parent / "private" / "ground_truth.json"

    try:
        ground_truth = load_json(ground_truth_path)
    except Exception as exc:
        print(f"internal evaluator error loading ground truth: {exc}", file=sys.stderr)
        return 2

    gen_dir = Path(args.gen_dir)
    solution_path = gen_dir / "solution.json"
    output_path = Path(args.out) if args.out else gen_dir / "results.json"

    try:
        if not solution_path.exists():
            result = {
                "overall_score": 0.0,
                "primary_metric": ground_truth["primary_metric"],
                "metrics": {
                    "schema_validity": 0.0,
                    "task_quality": 0.0,
                    "dependency_integrity": 0.0,
                    "content_completeness": 0.0,
                },
                "passed": False,
                "diagnostics": [f"missing submission file: {solution_path}"],
            }
        else:
            submission = load_json(solution_path)
            if not isinstance(submission, dict):
                result = {
                    "overall_score": 0.0,
                    "primary_metric": ground_truth["primary_metric"],
                    "metrics": {
                        "schema_validity": 0.0,
                        "task_quality": 0.0,
                        "dependency_integrity": 0.0,
                        "content_completeness": 0.0,
                    },
                    "passed": False,
                    "diagnostics": ["solution.json must be a JSON object"],
                }
            else:
                result = evaluate_submission(submission, ground_truth)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except Exception as exc:
        print(f"internal evaluator error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
