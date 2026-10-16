# Task <ID> — <Title>

**ID:** T<NNN>
**Owner:** <agent-slug>
**Status:** pending
**Priority:** P0 | P1 | P2
**Tier:** mechanical | standard | judgment | — (optional)
**Depends on:** <IDs or —>
**Affects:** <category>/<id>, … | —
**Created:** YYYY-MM-DD
**Completed:** —
**Based on:** docs/plans/plan-<NNN>-<slug>.md

> **Tier field (optional, additive):** one of `mechanical`, `standard`, or `judgment`, defined in
> `docs/artifacts/task-tier-schema-v1.md`. Leave as `—` for any brief not yet classified — existing
> briefs authored before this field existed remain valid without it; adding this field is not a
> breaking change to the brief schema. Assigning a tier to any specific existing task is out of
> scope for the task that introduced this field (T440); see that artifact's "Not decided here"
> section.

> **Affects field (mandatory for `P0`/`P1`):** the components this task declares **defective** —
> zero or more `<category>/<id>` entries (`agent`, `command`, `instruction`, `skill`), comma
> separated, or `—` for "this task indicts no component". This is an accusation, not a reading
> list: cite whatever files, branch names and component docs the brief needs in its body, and name
> here only what the task says is broken. `docs/artifacts/maturity-promotion-criteria-v2.md` §3.5
> reads this field and nothing else, so an open `P0`/`P1` task blocks a component's promotion if
> and only if it declares it here. **A `P0`/`P1` brief without this field is a hard error** in both
> `validate-tasks.py` (C11) and `check-maturity.py` — an absent field is never read as `—`, because
> a gate that fails open still prints a reassuring PASS. `P2` briefs need not declare it; if they
> do, the value is still validated. Entries naming a component that does not exist are rejected
> (a typo would otherwise silently protect the component it was meant to indict). Introduced by
> T516; unlike the additive `Tier` field, this one is required at `P0`/`P1`.

## Objective
<one paragraph>

## Inputs
- <artifact-vN.md paths>

## Expected outputs
- <artifact paths this task must produce>

## Acceptance criteria
1. <specific, testable>

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
