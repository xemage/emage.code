---
description: "Use when selecting which model class to dispatch a task to, once the task's tier (mechanical, standard, judgment) has been assigned. States the static tier-to-model-class mapping and its explicit scope boundary."
applyTo: "docs/tasks/task-*.md"
---

# Model Routing Policy

## Rails

**Inputs**: A task brief that already carries a `tier` value (`mechanical` | `standard` |
`judgment`) assigned per `docs/artifacts/task-tier-schema-v1.md`. This policy consumes that tier
value; it does not assign it.

**Out of scope**: Assigning a `tier` to a task brief (that is `task-tier-schema-v1.md`'s job, not
this file's). Historical-success-rate learning, adaptive routing, bandit algorithms, confidence
scoring, or any feedback loop that adjusts the mapping below based on past outcomes. Escalation
mechanics on `mechanical`-tier failure (a separately scoped, separately authorized task). Actually
wiring any agent, orchestrator, or CI job to read and enforce this policy at dispatch time — this
document states the policy; it does not implement dispatch-time enforcement.

**Failure mode**: If a task brief's tier value does not map cleanly to one of the three rows below
(for example, an unrecognized tier string), the dispatching agent or orchestrator must treat this
as a task-brief defect and escalate rather than guessing a model class.

## The policy

This is a **static** mapping. It does not learn from past outcomes and it is not adjusted
automatically based on success or failure rates. Quoted, near-verbatim, from the roadmap line this
policy implements: **"Static mapping only. No historical-success-rate learning in this version —
that requires volume this project does not yet have."**

| Tier | Model class |
|---|---|
| `mechanical` | economy |
| `standard` | mid-tier |
| `judgment` | frontier |

## Why model classes, not model identifiers

Each row above names a general model **class** (`economy`, `mid-tier`, `frontier`) rather than a
specific vendor or model identifier (a particular model name or version string). This is a
deliberate decision, not an oversight: a specific model identifier goes stale the moment a vendor
renames, retires, or replaces that model, which would silently break this policy or require a
routine maintenance edit that adds no real information. A model **class** describes the intended
capability/cost tradeoff and stays valid across vendor-side model churn. Whoever operationalizes
this policy (a future, separately scoped task — see "Out of scope" above) is responsible for
mapping each class to a concrete, current model identifier at dispatch time, not this document.

- **economy** — the lowest-cost model class capable of reliably completing fully-specified,
  mechanically-checkable work. Intended for `mechanical`-tier tasks: proven components, declared
  rails, binary pass/fail acceptance criteria, no open judgment call left for the assignee.
- **mid-tier** — a balanced capability/cost model class. Intended for `standard`-tier tasks: clear
  acceptance criteria, but real non-mechanical decision-making within the brief's boundaries
  (choosing between reasonable approaches, synthesizing multiple sources).
- **frontier** — the highest-capability model class available. Intended for `judgment`-tier tasks:
  architecture decisions, product-priority tradeoffs, security risk acceptance, and any work
  requiring escalation or interpretation of ambiguous or conflicting requirements.

## Explicit scope boundary

This policy is deliberately narrow. It does **not**:

- Track historical success or failure rates per tier, per component, or per model.
- Adjust the mapping above based on past outcomes (no adaptive routing, no bandit algorithms, no
  confidence scores, no feedback loops).
- Wire any agent, orchestrator, or CI job to read and enforce this mapping at dispatch time. That
  is left to future, separately scoped and separately authorized work.
- Define escalation behavior when a `mechanical`-tier task fails at the economy model class. That
  is a separate, explicitly out-of-scope concern for this document, tracked as its own follow-on
  task in the same roadmap phase.

If a future need arises to add any of the above, it requires a new, separately-scoped task — not a
silent edit to this file's static mapping.

## Relationship to the tier schema

This document is a pure consumer of the tier vocabulary defined in
`docs/artifacts/task-tier-schema-v1.md`. It does not redefine, narrow, or extend the tier
definitions, the mechanical-tier gating rule, or the eligible-component pool described there — see
that artifact as the sole source of truth for what each tier means and which components currently
qualify for `mechanical`.
