# T529 — `handoff` schema permits a handoff with zero writable paths

**ID:** T529
**Owner:** Backend Developer
**Status:** pending
**Priority:** P2
**Tier:** mechanical
**Affects:** —
**Depends on:** —
**Created:** 2026-09-25
**Based on:** `docs/plans/plan-073-skillify-adjudication-and-wave2.md` §2;
`docs/tasks/task-T525.md`; `implementation/runtime/handoff/schema-v1.json`.

## Objective

`implementation/runtime/handoff/schema-v1.json` declares:

```json
"writablePaths": {"type": "array", "items": {"type": "string", "minLength": 1}, "maxItems": 128}
```

There is **no `minItems`**, so `"writablePaths": []` is schema-conformant. A handoff that grants the
receiving agent no writable paths at all passes validation, which is very likely not the intent —
`constraints.writablePaths` exists to bound what the receiver may touch, and an empty bound reads as
"nothing", not as "unconstrained".

## How it was found, and why that matters

Found by an orchestrator **mutation attempt** against `T525`'s new
`handoff-payload-schema-fields-real` golden case: emptying `writablePaths` did **not** flip
`check()` to `False`. The initial read was "weak check". It was not — the check faithfully encodes
the contract, and **the mutation was mis-designed**. The permissiveness is in the schema.

So: **the golden case is correct and must not be changed to compensate.** Fixing a schema gap by
tightening a test that correctly mirrors the schema would put the two out of step in the opposite
direction.

## Scope

Decide and implement whether `minItems: 1` belongs on `constraints.writablePaths`, and apply the
same question to the sibling `forbiddenActions` array, which may have the identical gap — check it
rather than assuming.

**The artifact is versioned.** `schema-v1.json` is a `-v1` artifact and `AGENTS.md` § Artifact
Versioning says revisions create new versions, never overwrite. Determine whether this repo treats
`implementation/runtime/handoff/schema-v1.json` as immutable in that sense — the naming suggests
yes, and three tasks in this phase have already been caught by in-place edits of `-v1` documents. If
it is immutable, produce `schema-v2.json` and repoint its consumers, including
`implementation/runtime/handoff/validator.py` and any test fixtures. **Report which you concluded
and why.**

## Constraints

- **Do not modify `tests/golden/**`.** No protected-path authorization is granted or needed. If you
  believe the golden case must change, that is a blocker to report, not a file to edit.
- The two real handoff artifacts under `docs/checkpoints/` must still validate after your change.
  Check them; if a real artifact would become invalid, that is a finding worth reporting before
  proceeding.

## Verification

```
python3 tests/run.py       # baseline first: 774 tests, OK, 23 skipped
node implementation/scripts/sync.mjs --check
python3 docs/tasks/validate-tasks.py
git status --porcelain
```

Also validate both real `docs/checkpoints/handoff-*.json` artifacts against the schema before and
after, and report both results.

## Ledger, git, blockers

Set this brief's `**Status:**` to `in_review`; do not move any ledger row. Branch
`agent/backend-developer/T529`. Commit message ends with exactly
`Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`. **No merge request, no merge, no
self-merge.** Report blockers with type and severity; max 2 retries.
