#!/usr/bin/env python3
"""Trajectory telemetry replay comparator for v3 runtime."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _event_counts(events: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in events:
        event_type = str(event.get("eventType", "unknown"))
        counts[event_type] = counts.get(event_type, 0) + 1
    return counts


def _verdict_summary(events: list[dict[str, Any]]) -> dict[str, int]:
    out = {"PASS": 0, "CONDITIONAL_PASS": 0, "FAIL": 0}
    for event in events:
        if event.get("eventType") != "verdict":
            continue
        verdict = str(event.get("payload", {}).get("verdict", ""))
        if verdict in out:
            out[verdict] += 1
    return out


def _tool_error_count(events: list[dict[str, Any]]) -> int:
    count = 0
    for event in events:
        if event.get("eventType") != "tool":
            continue
        payload = event.get("payload", {})
        if payload.get("action") == "error" or payload.get("success") is False:
            count += 1
    return count


def _denied_handoff_count(events: list[dict[str, Any]]) -> int:
    count = 0
    for event in events:
        if event.get("eventType") != "handoff":
            continue
        payload = event.get("payload", {})
        if payload.get("routeAllowed") is False:
            count += 1
    return count


def compare_runs(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    base_events = baseline.get("events", [])
    cand_events = candidate.get("events", [])

    base_counts = _event_counts(base_events)
    cand_counts = _event_counts(cand_events)

    structural_deltas: list[str] = []
    for event_type in sorted(set(base_counts) | set(cand_counts)):
        b = base_counts.get(event_type, 0)
        c = cand_counts.get(event_type, 0)
        if b != c:
            structural_deltas.append(f"event count differs for {event_type}: baseline={b}, candidate={c}")

    base_verdicts = _verdict_summary(base_events)
    cand_verdicts = _verdict_summary(cand_events)
    base_tool_errors = _tool_error_count(base_events)
    cand_tool_errors = _tool_error_count(cand_events)
    base_denied_handoffs = _denied_handoff_count(base_events)
    cand_denied_handoffs = _denied_handoff_count(cand_events)

    quality_deltas: list[str] = []
    if cand_verdicts["FAIL"] > base_verdicts["FAIL"]:
        quality_deltas.append("verdict regression: FAIL count increased")
    if cand_verdicts["CONDITIONAL_PASS"] > base_verdicts["CONDITIONAL_PASS"]:
        quality_deltas.append("verdict regression: CONDITIONAL_PASS count increased")
    if cand_tool_errors > base_tool_errors:
        quality_deltas.append("quality regression: tool error count increased")
    if cand_denied_handoffs > base_denied_handoffs:
        quality_deltas.append("quality regression: denied handoff count increased")

    has_regression = bool(quality_deltas)
    return {
        "summary": {
            "baselineEvents": len(base_events),
            "candidateEvents": len(cand_events),
            "hasRegression": has_regression,
        },
        "structuralDeltas": structural_deltas,
        "qualityDeltas": quality_deltas,
        "baseline": {
            "eventCounts": base_counts,
            "verdicts": base_verdicts,
            "toolErrors": base_tool_errors,
            "deniedHandoffs": base_denied_handoffs,
        },
        "candidate": {
            "eventCounts": cand_counts,
            "verdicts": cand_verdicts,
            "toolErrors": cand_tool_errors,
            "deniedHandoffs": cand_denied_handoffs,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--out", default="telemetry-replay-report.json")
    args = parser.parse_args()

    baseline = _load(Path(args.baseline))
    candidate = _load(Path(args.candidate))
    report = compare_runs(baseline, candidate)

    out_path = Path(args.out)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"wrote replay report: {out_path}")
    if report["summary"]["hasRegression"]:
        print("regression detected")
        return 1

    print("no regression detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
