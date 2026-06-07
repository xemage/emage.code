# v3 Telemetry Schema v1

Status: Draft for implementation (Execution Wave 2, P1)
Based on: [docs/artifacts/hook-policy-spec-v1.md](hook-policy-spec-v1.md)

## 1) Purpose

Define normalized telemetry for runtime trajectory capture and replay across Copilot, Gemini, and Opencode adapters.

## 2) Event model

Each trajectory is an ordered list of events with strict monotonic step numbers.

Common event envelope fields:
- eventId: uuid-like string
- runId: uuid-like string
- step: integer >= 1
- timestamp: RFC3339 UTC string
- agent: kebab-case agent id
- eventType: one of step, tool, handoff, verdict
- payload: object (event-type specific)

## 3) Event types

### 3.1 step event
- lifecycle: start|end
- phase: planning|implementation|qa|release
- objective: non-empty string

### 3.2 tool event
- toolName: string
- action: invoke|result|error
- durationMs: integer >= 0
- success: boolean

### 3.3 handoff event
- fromAgent: string
- toAgent: string
- taskId: pattern TNNN
- routeAllowed: boolean

### 3.4 verdict event
- gate: architecture|implementation|integration|security|release
- verdict: PASS|CONDITIONAL_PASS|FAIL
- notes: string

## 4) Replay comparison contract

Replay compares a baseline run and candidate run and reports:
- structural deltas:
  - missing event types
  - changed event counts by type
  - changed unique tool/handoff sets
- quality deltas:
  - verdict regressions (PASS to FAIL, PASS to CONDITIONAL_PASS)
  - increased tool error count
  - increased denied handoff count

Output format:
- machine-readable JSON report with summary and delta arrays.
- non-zero exit code when regression thresholds are exceeded.

## 5) CI artifact support

Replay output file name convention:
- telemetry-replay-report.json

CI publishing recommendations:
- store baseline and candidate trajectory fixtures as artifacts.
- publish replay report artifact on every validation run.
- treat verdict regressions as blocking.

## 6) Adapter compatibility notes

Copilot:
- map tool events from tool invocation boundaries and result callbacks.

Gemini:
- map event stream from orchestration step boundaries and safety checks.

Opencode:
- map tool and handoff events from object-map capabilities and execution traces.
