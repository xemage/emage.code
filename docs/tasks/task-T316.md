# Task T316 — Tracked follow-up: ConcurrentMergeOrchestrator role-split + minor Pattern A gaps (non-blocking)

**ID:** T316
**Owner:** backend-developer
**Status:** in_progress
**Priority:** P2
**Depends on:** — (does NOT block T214 or T306; tracked debt only)
**Created:** 2026-08-02
**Completed:** —
**Based on:** `docs/tasks/task-T214.md` Execution notes (qa-engineer's first real, live run of
T214's 4 scenarios, 2026-08-02), findings BUG-A, BUG-E, BUG-F, BUG-G, BUG-H.

## Objective

qa-engineer's real, live run of T214 found several additional real defects/gaps in the Pattern A
runtime modules beyond the critical-path BUG-B/BUG-C/BUG-D fixed in T315. None of these block
T214's stated acceptance criteria (T214's addendum requires only the underlying primitive tool
calls — `create_shadow_workspace`/`write_shadow_file`/`commit_shadow`/AST precheck/
`merge_concurrent_results`/`drop_shadow_workspace` — to work, which they do; it does not require
`ConcurrentMergeOrchestrator.run()` specifically to work end-to-end). This task exists purely to
track them as real, known debt so they are not silently forgotten — per this repo's own
anti-fabrication and debt-tracking norms — not to gate any other task's completion.

**BUG-A (CRITICAL for future real use, not blocking T214)** — `ConcurrentMergeOrchestrator.run()`
cannot execute end-to-end against the live server with a single-role `CwsoClient`. Confirmed live
permission matrix: role `worker` can do everything except `merge_concurrent_results` (denied,
JSON-RPC -32002); role `orchestrator` can do `merge_concurrent_results` but not
`write_shadow_file`/`commit_shadow` (denied, same error class). `ConcurrentMergeOrchestrator.
__init__(self, client)` accepts exactly one client and uses it for the whole flow, so no single
role can complete `.run()` against the real server today. Also reproduced independently via
`tests/functional/test_cwso_client_live.py` (5 of 11 tests fail live, for this exact reason).
Proposed direction (not yet implemented): accept two role-scoped clients (or one client per role,
resolved internally), or split `.run()` into phase methods that accept different clients per
phase. Needs a design decision, not just a one-line fix — that's why this is tracked separately
rather than folded into T315's narrower live-response-shape fix.

**BUG-E (LOW/cosmetic)** — `write_shadow_file`'s real response is non-JSON prose (e.g. `"wrote 32
bytes (blob 77a8c908...)"`), so `CwsoMcpClient._unwrap_tool_result()` (T314) correctly leaves it
enveloped (its defensive fallback fires, since the text isn't valid JSON) — meaning
`CwsoClient.write_shadow_file()`'s documented `blob_oid` key is never actually present in the
returned dict, despite the docstring. Fix would require either (a) the client regex-parsing the
blob OID out of the prose text as a best-effort convenience, or (b) reporting this response-shape
inconsistency upstream if it's judged a genuine CWSO-server inconsistency (JSON for
`create_shadow_workspace`/`commit_shadow`, prose for `write_shadow_file`) — needs a decision on
which.

**BUG-F (MEDIUM)** — `ConcurrentMergeOrchestrator._build_merge_inputs()` silently drops the middle
worker's edits when 3+ workers edit the same path (keeps first worker as `ours`, overwrites
`theirs` with each subsequent worker in turn, so worker 2's content is computed then discarded
when worker 3's overwrites it). The real `merge_concurrent_results`/`MergeInput` schema is
strictly 2-way; there is no native N-way merge primitive server-side. T214's Scenario 1 (3 agents)
was validated via two separate, real, sequential 2-way `merge_concurrent_results` calls instead of
going through this method — proven to work, but not through the convenience class. Needs a design
decision: either document N=2 as the supported width for `ConcurrentMergeOrchestrator` and make
`run()` raise clearly for N>2, or implement genuine sequential-pairwise composition internally
(mirroring what T214's test file did manually).

**BUG-G (LOW, informational, not a code defect)** — real `merge_concurrent_results` conflict
`message` text is the generic `"AST semantic overlap conflict"` in every conflict case observed so
far (both a simultaneous-add case and a diverging-signature case produced byte-identical
messages), not the symbol-specific wording T214's original acceptance criteria anticipated (e.g.
`"Simultaneous add of symbol 'helper'"`). This is CWSO server behavior, not this-repo client code
— if more specific messages are wanted, that's a CWSO-core feature request (T310-style hand-off to
`../CWSO`, not a fix in this repo), not a bug in `implementation/runtime/cwso/*`.

**BUG-H (LOW, packaging hygiene)** — `implementation/runtime/cwso/ast_conflict_check.py` imports
via an absolute `from implementation.runtime.cwso.client import ...` (assumes repo root on
`sys.path`), while `concurrent_merge.py` and friends use relative imports (`from .client import
...`, assumes `implementation/` on `sys.path`). Running both in the same process creates two
distinct `CwsoClient`/`MergeHeuristic`/`QueryType` classes (confirmed via `id()`/`is`). Because
`MergeHeuristic(str, Enum)` mixes in `str`, `==` still works, but `isinstance()` checks across the
two identities return `False` — a latent hazard for any future code doing
`isinstance(x, CwsoClient)` or catching `CwsoToolError` from the "other" import path. Fix: change
`ast_conflict_check.py`'s import to the same relative style as the rest of the package.

## Inputs

- `docs/tasks/task-T214.md` Execution notes (full findings and live evidence)
- `implementation/runtime/cwso/concurrent_merge.py`, `implementation/runtime/cwso/client.py`,
  `implementation/runtime/cwso/ast_conflict_check.py`

## Expected outputs

A future task brief (or this task's own Execution notes, if tackled directly) resolving each of
BUG-A/E/F/G/H — or, for BUG-G, a routed CWSO-core feature-request write-up in `../CWSO` following
the T310 convention, since it is not this-repo-owned behavior.

## Acceptance criteria

This task does not gate any other task. It is considered "addressed" (not necessarily "done") once
each of BUG-A/E/F/G/H has an explicit disposition recorded (fixed, deferred with reason, or routed
to CWSO). It may be picked up in a future wave/plan; no urgency requirement is attached beyond
"do not lose track of it."

## Blocker protocol

Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`) +
severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<not yet picked up — filed for tracking per this repo's anti-fabrication/debt-tracking norms,
consequent to T214's real live run finding these gaps. Does not block T214/T306.>
