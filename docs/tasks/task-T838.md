# T838 — Root refresh of .opencode after T836 (user approval at that moment)

**ID:** T838
**Owner:** orchestrator
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-14
**Completed:** 2026-11-14
**Based on:**
- `docs/plans/plan-168-batch-j-opencode-permission.md` (§ Goal)
- The user's answer of 2026-11-14, verbatim: "J go"

## 1. What and why

As in plan-168 § Goal and § Task Decomposition.

## 2. Output

The refreshed `.opencode/` in the repository root; `--print-drift` gives `[]`.

## 3. Constraints

- Do not push, merge, tag or release. Do not edit the ledger, any brief's Status line or the plan.
- No `docker`. Never open `tests/golden/held-out/`. Never read secrets or the user's settings files.
- Mark anything not verified **(unverified)**.

## 4. Acceptance criteria

As in plan-168 § Goal: the same effective allows and denials, in the documented `permission:` form, with tests that fail if a denial is lost or reordered.

## 5. Blocker protocol

Report each blocker with its type and severity.
