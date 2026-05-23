# v3 Hook and Policy Taxonomy Spec v1

Status: Draft for implementation (Execution Wave 1, P1)
Based on: [docs/artifacts/v3-handoff-security-model-v1.md](v3-handoff-security-model-v1.md)

## 1) Purpose

Define a deterministic runtime hook taxonomy and policy precedence model for v3 that is portable across adapters and fail-closed by default.

## 2) Hook Categories

### 2.1 Inspect hooks

Inspect hooks are read-only and cannot mutate payloads.

Supported inspect hooks:
- inspect.session.start: evaluate run context and policy set at session bootstrap.
- inspect.handoff.preflight: evaluate source agent, target agent, task id, and handoff metadata before routing.
- inspect.tool.preflight: validate intended tool call against path, command, and capability policies.
- inspect.response.preflight: check outbound response metadata for policy violations before delivery.

### 2.2 Decide hooks

Decide hooks produce an explicit verdict and rationale.

Supported decide hooks:
- decide.handoff.route: allow or deny route from source to target agent.
- decide.tool.call: allow, deny, or request-review for tool invocations.
- decide.escalation: permit or deny privilege escalation and context expansion.

Verdict domain:
- allow
- deny
- request-review

### 2.3 Transform hooks

Transform hooks can mutate sanitized payload fields only and must produce deterministic output.

Supported transform hooks:
- transform.handoff.payload: redact or normalize handoff payload fields.
- transform.tool.args: normalize tool arguments without changing declared intent.
- transform.response.body: redact sensitive output fields before returning content.

## 3) Lifecycle Timing

Hook execution order is strict:
1. inspect.session.start
2. inspect.handoff.preflight
3. decide.handoff.route
4. transform.handoff.payload
5. inspect.tool.preflight
6. decide.tool.call
7. transform.tool.args
8. inspect.response.preflight
9. transform.response.body

Rules:
- A deny from any decide hook terminates evaluation immediately.
- A failed inspect check terminates evaluation immediately.
- Transform hooks run only after corresponding inspect and decide hooks succeed.

## 4) Context Scopes

Each hook runs with an explicit scope contract:
- session scope: model id, adapter id, run id, checkpoint ref, token budget.
- handoff scope: from agent, to agent, task id, intent, trace identifiers.
- tool scope: tool name, arguments, writable paths, forbidden operations.
- response scope: response metadata, payload size, redactable fields.

Scope constraints:
- Hooks must never receive secrets directly; only redaction-safe metadata.
- Scopes are immutable in inspect and decide phases.
- Transform phase can emit only declared transform outputs.

## 5) Policy Precedence and Resolution

Precedence order (highest to lowest):
1. Immutable security constraints
2. Runtime emergency blocklist
3. Task-level explicit constraints
4. Cookbook handoff policy
5. Agent role permissions
6. Platform adapter defaults

Conflict rules:
- Deny beats allow at every layer.
- If multiple policies of equal level conflict, choose deny and record conflict detail.
- Unknown policy keys are ignored only in compatibility mode; strict mode rejects them.

## 6) Fail-Closed Semantics

Fail-closed behavior is mandatory:
- Missing hook configuration: deny.
- Unknown hook name: deny.
- Hook execution exception: deny.
- Missing policy data for requested action: deny.
- Unsupported adapter capability for required hook: deny.

Audit requirements:
- Emit structured event with correlation id, hook id, and denial reason.
- Do not include secrets, tokens, or raw sensitive payloads in logs.

## 7) Adapter Compatibility Notes

### 7.1 GitHub Copilot adapter
- Maps inspect/decide/transform phases to Copilot tool-invocation mediation boundaries.
- Must preserve orchestrator-only user invocation rules from projected agent metadata.

### 7.2 Gemini adapter
- Runs hook policy checks before stripped tool metadata reaches execution path.
- Requires strict schema validation because projected Gemini agents omit tools frontmatter.

### 7.3 Opencode adapter
- Uses tools object-map projection and evaluates route/tool decisions against true-valued tool capabilities.
- Must enforce deny on unresolved route or capability lookups.

## 8) Minimum Validation Checklist

A compliant implementation must prove:
- hook category registry includes inspect/decide/transform entries.
- precedence model lists all six policy layers in order.
- deny-over-allow and fail-closed rules are explicit.
- compatibility section mentions Copilot, Gemini, and Opencode.
