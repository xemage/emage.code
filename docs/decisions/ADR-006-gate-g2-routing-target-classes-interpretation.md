# ADR-006 — Gate G2 closes on the infrastructure-precondition reading, not a named routing-target-class list

> Filename: `ADR-006-gate-g2-routing-target-classes-interpretation.md`

- **Status**: Accepted
- **Date**: 2026-09-10
- **Decider(s)**: user, orchestrator
- **Tasks**: T433 (this decision's trigger and first consumer), T430, T431, T432 (this decision's
  evidentiary basis), T440-T442 (Phase 4, downstream consumer, not yet planned)
- **Evidence**: `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.2 (Gate table, G2 row), §2.3
  (phase graph, `P3 --> G2 --> P4`), §2.4 (G2 closure sentence, Phase 3/Phase 4 task tables);
  `docs/plans/plan-038-phase5-detailed-planning.md` "Open planning questions" (first recorded the
  underlying circularity, deferred resolution to "whoever next plans Phase 3");
  `docs/plans/plan-041-phase3-maturity-ladder-detailed-planning.md` Finding 1 (re-confirmed the
  circularity does not block Phase 3's start, narrowed the open question to two readings, deferred
  final resolution to T433's own dispatch); `docs/tasks/task-T430.md`, `task-T431.md`,
  `task-T432.md` and their `completed-tasks.md` closure rows (the real infrastructure this decision
  treats as satisfying G2's precondition)

## Context

`plan-035` §2.2's Gate table defines G2 as: "No cheap-model routing until the target task class
has a stable brief with rails and tests." §2.4 states, immediately after Phase 3's own acceptance
criteria: "Gate G2 closes when Wave 1 (T433) is complete for the routing target classes." T433 is
itself one of Phase 3's eight tasks (T430-T432 precede it in the same phase G2 nominally gates).

`plan-038` first named this as circular — G2 is closed *by* completing part of the phase it
nominally gates, unlike G0/G1/G3/G4, which each gate something outside their own phase — and
explicitly deferred resolving it. `plan-041` (approved, MR !252) re-confirmed the circularity does
not block Phase 3 from *starting* (Phase 3's own entry condition, G1 + Phase 2, references neither
G2 nor T433), but found the closure sentence's "for the routing target classes" clause genuinely
ambiguous: `plan-035`'s Phase 4 (§2.4, T440) is where task tiers (`mechanical`/`standard`/
`judgment`) actually get defined, and T440 is itself gated behind G2 — so no operational definition
of "routing target class" exists anywhere in `plan-035` at the point G2 is supposed to close.

Re-reading the source text one further pass before T433's dispatch (this session, 2026-09-10)
surfaced three textually-defensible readings, not two:

- **(a) Automatic/inclusive** — "the routing target classes" informally *means* T433's own named
  Wave 1 set (the 8 highest-traffic components); G2 closes automatically the moment Wave 1
  finishes, no further identification work required.
- **(b) Selective/forward-looking** — T433 must explicitly judge which (if any) of the 8 Wave-1
  components are plausible future routing candidates, as a strict subset decided ahead of Phase
  4's own tier schema (T440) existing.
- **(c) Precondition-only** — the Gate table's G2 row is a general *principle* ("no routing until a
  target class has stable+rails+tests"), not an instruction to enumerate named classes inside
  Phase 3. G2 closes because the *infrastructure* to satisfy that principle now demonstrably
  exists — T430 (mandatory, reconciled maturity levels), T431 (concrete, mechanically-checkable
  promotion criteria), T432 (CI-enforced verification that a claimed level is genuinely satisfied,
  not just declared), and T433 (real components that actually reach `stable` under that
  enforcement) — collectively proving "stable brief with rails and tests" is now a real, checkable,
  non-vacuous state for at least some components. Which specific task classes get routed, and
  under what tier, remains entirely Phase 4's own job (T440-T442), decided against a real schema
  that doesn't exist yet, not guessed at by Phase 3.

None of the three has a textual tiebreaker within `plan-035` itself — this was presented to the
user as a genuine decision point rather than picked unilaterally, per this project's standing
practice for decisions of comparable weight (mirrors `ADR-004`'s own Inconclusive-classification
decision, `ADR-005`'s embeddings-provider/cost-gate decision, and T456's four-option blocker
presentation).

## Decision

**Reading (c) is adopted.** Gate G2 closes when T433 (Wave 1) is complete and the 8 named
components have genuinely, mechanically-verifiably reached `stable` under T432's real enforcement
(not merely had their `maturity` field flipped) — this is treated as satisfying G2's stated
precondition ("target task class has a stable brief with rails and tests") in the general,
infrastructure sense, not as requiring T433 to name, rank, or select any subset of its 8
components as specific future routing candidates.

Concretely:
1. **T433's acceptance criteria are about genuine, verified `stable` promotion** — each of the 8
   named components must actually satisfy T431's `beta→stable` criteria for its category, checked
   for real via T432's `check-maturity.py` (not a status-field flip that happens to pass a
   maturity-declaration schema check alone).
2. **T433 does not identify, rank, or reserve any subset of its 8 components as "routing target
   classes."** That identification is explicitly deferred to Phase 4's own planning pass, once
   T440 defines the `mechanical`/`standard`/`judgment` tier schema those classes need to be judged
   against. Phase 3 does not pre-guess Phase 4's own not-yet-designed criteria.
3. **Gate G2 closes on T433's completion**, recorded as satisfied under this reading — not left
   open pending a separate identification task, and not silently left ambiguous for a future
   session to rediscover.
4. **Phase 4 (T440-T442) is not thereby pre-authorized or scoped by this decision.** This ADR
   resolves G2's closure condition only; it does not approve Phase 4's own task-brief authoring,
   which remains subject to this project's own Plan-Approve-Execute protocol (a dedicated Phase 4
   planning pass, mirroring `plan-037`/`plan-038`/`plan-041`'s own precedent, is still required
   before any `T44x` brief is authored).

## Alternatives considered

| Option | Pros | Cons | Why not chosen |
|--------|------|------|----------------|
| (a) Automatic/inclusive — G2 closes on Wave 1 completion alone, no distinction from (c) in outcome for T433's own dispatch | Simplest; matches the phase graph's literal single `T433 → G2` edge | Textually conflates "component reached `stable`" with "component's *task class* is a routing candidate" — plan-035 nowhere states these are the same thing; risks G2 becoming a rename of "Wave 1 happened" regardless of whether any of the 8 components are sensible cost-routing candidates at all (e.g. `orchestrator`, `security-engineer` are judgment-heavy by nature and arguably should never be `mechanical`-tier regardless of stability) | Rejected — under-specifies the safety principle G2's own rationale states ("routing a cheap model at an under-specified brief is how you convert a cost saving into a correctness incident"); (c) reaches the same practical closure outcome for T433 without this category error |
| (b) Selective/forward-looking — T433 explicitly names a routing-candidate subset of its 8 components | More faithful to the gate's literal "for the routing target classes" wording; produces a concrete artifact Phase 4 could start from | Asks Phase 3 to judge against Phase 4's own tier schema (`mechanical`/`standard`/`judgment`, T440) before that schema is defined — any identification made now is provisional at best and likely needs redoing once T440's real criteria exist; risks Phase 3 scope-creeping into Phase 4's design work | Rejected — produces speculative, likely-to-be-redone work under a real risk of anchoring Phase 4's later design on premature guesses; (c) leaves this judgment to the planning pass equipped to actually make it |
| Leave the ambiguity unresolved, dispatch T433 anyway with the acceptance criterion phrased vaguely ("consider routing-target implications") | No decision-making overhead now | Directly contradicts `plan-041`'s own explicit instruction that T433's acceptance criteria must state this "not left implicit"; risks a future session declaring G2 closed on an unstated, undocumented basis, repeating the exact ambiguity `plan-038` already flagged once | Rejected — this project's own standing practice is to resolve or explicitly escalate ambiguities before dispatch, not silently carry them forward a second time |

## Consequences

- **Positive**: G2 closes on a real, defensible basis once T433 delivers genuine `stable`
  promotions — not a status-flip, and not a speculative routing-candidate list built against an
  undefined schema. Phase 4's eventual planning pass starts with a clean slate for its own
  tier-identification work, using real T440 criteria rather than inheriting a possibly-stale Phase
  3 guess. T433's own scope stays bounded to what Phase 3 can actually determine (component
  maturity), matching this project's existing "no code/decision before the design exists" norm
  (`plan-038`'s closing section, PoC Guidelines' "no code before hypothesis").
- **Negative**: Phase 4's planning pass, whenever it happens, must do the routing-candidate
  identification work from scratch rather than inheriting a head start from Phase 3. This is a
  deferred cost, not an eliminated one.
- **Risks introduced**: none beyond what `plan-035`'s own G2 rationale already accepts — this
  decision does not relax G2's substantive bar (genuine `stable` status, mechanically verified),
  only clarifies what "for the routing target classes" requires Phase 3 to additionally produce
  (nothing, beyond genuine promotions).
- **Follow-ups**: Phase 4's own dedicated planning pass (mirroring `plan-037`/`plan-038`/`plan-041`)
  must explicitly perform the routing-candidate identification this ADR defers, using T440's real
  tier schema once it exists — not silently skip it on the assumption G2's closure already did
  this work. No new task is created by this ADR; this is flagged as a required first step of
  Phase 4's future planning pass, not a task in its own right.

## Validation

Confirmed correct if: (1) `check-maturity.py` (T432) independently, mechanically verifies each of
T433's 8 claimed `stable` promotions against T431's real criteria — not accepted on a self-reported
status change; (2) Phase 4's eventual planning pass, when it happens, is not found to have silently
assumed a routing-candidate list this ADR explicitly did not produce (a documentation/process
check, not a metric); (3) no future session declares G2 "already closed with routing targets
already identified" — this ADR's own text is the authoritative record that no such identification
was made.
