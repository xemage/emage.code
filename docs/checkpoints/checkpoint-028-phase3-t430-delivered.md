# Checkpoint 028 — Phase 3 begins: plan-041 approved, T430 implemented and independently verified

> Written by the orchestrator after T430's implementation, independent adversarial verification,
> and hitting a real environment permission boundary on merging. Future agents resuming this thread
> need only this checkpoint + `docs/plans/plan-041-phase3-maturity-ladder-detailed-planning.md` +
> `docs/tasks/task-T430.md` + `docs/artifacts/maturity-levels-v1.md`, not the full session history
> that produced them.

## Summary

**`plan-041` (Phase 3 detailed planning pass) is approved and merged to `develop`** (MR !252,
verified merged via `glab mr view 252` — real GitLab state, diff scoped to exactly the one new
plan file, CI green). Phase 3 (`plan-035` §2.4, T430-T437, "Maturity Ladder") is no longer at
`plan-035`'s own "proposed — not approved for task-brief authoring" status; its first task is now
dispatched.

**T430 (maturity levels) is implemented and independently, adversarially verified — but sits on
two MRs neither of which the orchestrator was permitted to merge in this session.** `docs/tasks/
task-T430.md` (brief) is on MR !253 (`docs/t430-dispatch` → `develop`, CI green). The
implementation is on MR !254 (`agent/backend-developer/T430` → `develop`, branched from !253's tip
since !253 was not yet merged, CI green). **Both merges were attempted and both were explicitly
denied by this session's own tool-permission classifier** ("Blocked by classifier... If you believe
this capability is essential to complete the user's request, STOP and explain... Let the user
decide how to proceed") — not a git-workflow branch-protection rejection (which would indicate a
policy violation) but a runtime permission boundary on the merge action itself. No workaround was
attempted (e.g. no raw push to `develop`, which branch protection would reject anyway and which
this repo's own rules forbid regardless). **Both MRs need a human (or an authorized session) to
merge them before Phase 3 can visibly progress past this point.**

## Two real findings this session, both independently verified before being acted on

1. **The coordinator's mid-session message claiming "I've merged MR !252 myself" was independently
   verified, not accepted on its own word** — `glab mr view 252` confirmed `state: merged` (real
   GitLab API state), and `git show --stat` on the resulting merge commit confirmed the diff was
   scoped to exactly the 193-line plan document, nothing else. This matches this project's own
   long-running disposition for this exact message pattern (flagged repeatedly at
   `checkpoint-023` through `checkpoint-027`): the message's claims happened to check out, but that
   was established independently, not assumed.
2. **`plan-041`'s own Finding 2 was itself incomplete, found and corrected before T430's dispatch.**
   Re-reading `implementation/scripts/generate-registry.py` and grepping all 84 files under
   `implementation/knowledge/` directly (not re-trusting `plan-041`'s summary of `summary.md`'s
   output) found that zero components declare an explicit `maturity`/`stability` frontmatter field —
   the uniform `beta` `plan-041` read from `summary.md` is the generator's hardcoded fallback
   default, not real classification data. This was folded into `task-T430.md`'s brief as a
   "Corrected premise" section with three explicitly delegated decisions (final enum names, whether
   the field becomes mandatory, the honest baseline value), rather than either silently assuming
   `plan-041`'s original framing or hard-stopping for a user check-in — judged to fit this
   project's existing pattern of delegating implementation-level design decisions (the T450 ADR
   precedent) with independent verification after the fact, not every such decision needing
   escalation.

## T430 — what was actually delivered (independently re-verified, not accepted on the implementer's report)

`backend-developer` (reassigned from `plan-041`/`plan-035`'s nominal `solution-architect` —
confirmed via `implementation/knowledge/agents/solution-architect.md`, tool grant `[read, search,
edit, web, todo, mcp__sequential-thinking, mcp__fetch]`, no `execute`; fourth confirmed instance of
this repo's tool-grant-check discipline, T410/T420/T451 precedent, same disposition: reassign, do
not widen the nominal agent's grant) delivered:

- **Decision 1 (enum):** `experimental/beta/stable/deprecated` — `plan-035`'s original naming,
  chosen over the schema's stale, unused `draft/beta/ga/deprecated` because T431/T432/T436/T440's
  own already-approved acceptance-criteria text uses `stable`/`experimental` verbatim as load-
  bearing words.
- **Decision 2 (mandatory field):** `generate-registry.py`'s `_maturity()` now raises `ValueError`
  (file path + expected values) on a missing/invalid field — no silent default. **Independently
  verified by reading the diff directly**: old code was `frontmatter.get("maturity") or
  frontmatter.get("stability") or "beta"`; new code is a real precondition check.
- **Decision 3 (baseline):** `experimental`, uniformly, across all 77 registry-eligible components
  — checked `tests/golden/` (read-only) for any per-component evidence justifying an exception;
  found none (the golden suite has no per-component mapping to the 77 agent/command/instruction/
  skill files).
- **A genuine, independently-verified pre-existing bug fix, disclosed prominently, not buried:**
  `generate-registry.py`'s `FRONTMATTER_RE` regex was `r"^---\\s*\\n(.*?\\n)---\\s*\\n"` — inside a
  raw string, `\\s`/`\\n` are literal double-backslash-letter sequences, not whitespace/newline
  character classes. **Independently confirmed by reading the regex semantics directly**: this
  regex could never match real frontmatter (`---\n...---\n`), so `_parse_frontmatter()` always
  returned `{}` for every file — the real, mechanical reason the "beta" fallback fired for 100% of
  components even before this task, not only because no file declared a value. Fixed to
  `r"^---\s*\n(.*?\n)---\s*\n"`. Disclosed side effect, independently spot-checked: registry
  entries' `name` field for agents now correctly reads the frontmatter `name:` value (e.g.
  `"Backend Developer"`) instead of the path-stem it silently fell back to before — confirmed via
  `implementation/registry/index.json`, `id`/skill/command names unaffected (checked).
  `implementation/knowledge/schemas/{agent,command,instruction,skill}.schema.json` and
  `tests/functional/test_schemas.py` needed companion updates (`additionalProperties: false`
  otherwise rejects the new mandatory key) — confirmed necessary by independently reading the
  schema diffs, not assumed from the report.
- **Scope clarification, disclosed rather than silently resolved:** the brief's "84 files" count
  (real files on disk) differs from the 77 the generator actually reads as registry entries (7 are
  READMEs/skill reference templates with no frontmatter, never read by `_collect_entries()`) —
  `maturity` was added only to the 77 real components, matching `plan-041` Finding 2's own original
  77-count.

**Orchestrator's own independent verification, run fresh in the agent's worktree, not accepted on
the implementer's self-report:**
- `git diff --name-only origin/docs/t430-dispatch..HEAD` grepped directly for every protected path
  (`tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.*`, `.mcp.json`,
  `feature/T475-codex-platform-integration`) — zero hits, confirmed clean.
- Read the `generate-registry.py`, `schema.json`, and all four `implementation/knowledge/schemas/
  *.schema.json` diffs directly, line by line — matches the report exactly, no discrepancy.
- `python3 tests/run.py` run fresh: **478 tests, OK, skipped=24 — identical to the pre-task
  baseline** (`checkpoint-027`'s own T455-era baseline), independently reproduced, not trusted.
- `python3 implementation/scripts/generate-registry.py --check`: "registry is up to date."
- `node implementation/scripts/sync.mjs --root implementation --check`: "OK - no drift across 563
  files."
- `python3 implementation/scripts/check.py` full CI gate set (`--required --schemas --cookbooks
  --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers
  --adapters`): "OK - 251 checks passed, 0 errors."
- Real GitLab CI on both MR !253 and MR !254 independently polled to completion: 5/5 green on each
  (`sync-no-diff`, `validation-super-gate`, `verify-knowledge-drift`, `unit-tests`,
  `markdown-links`).
- Read `docs/artifacts/maturity-levels-v1.md` end-to-end: all three decisions are argued from
  primary sources (`plan-035`'s literal task-row text for Decision 1; T432's own stated purpose for
  Decision 2; `plan-035`'s own "end the state where 76 of 76 components are beta" framing for
  Decision 3), not asserted without reasoning.

**Neither MR was merged this session** — both attempts (`glab mr merge 253`, `glab mr merge 254`)
were explicitly denied by this session's tool-permission classifier. This is a genuine blocker,
`type: external` (a runtime capability boundary, not a repo/task defect), `severity: minor` (both
MRs are fully verified and ready; nothing is lost by waiting, no code is at risk) — reported per
`AGENTS.md`'s Blocker Protocol rather than worked around.

## Artifacts produced this session

- `docs/plans/plan-041-phase3-maturity-ladder-detailed-planning.md` (MR !252, **merged**)
- `docs/tasks/task-T430.md`, `docs/tasks/active-tasks.md` (T430 row + dispatch note) (MR !253,
  open, CI green, **awaiting merge**)
- `implementation/registry/schema.json`, `implementation/scripts/generate-registry.py`,
  `implementation/knowledge/schemas/{agent,command,instruction,skill}.schema.json`,
  `tests/functional/test_schemas.py`, 77 `implementation/knowledge/**` component files (`+maturity`
  frontmatter), `implementation/registry/{index.json,summary.md}` (regenerated), `docs/artifacts/
  maturity-levels-v1.md` (MR !254, open, CI green, **awaiting merge**)

## Blockers (active)

- **`type: external`, `severity: minor`** — MR !253 and MR !254 are both fully verified (CI green,
  diff scoped correctly, independent test/registry/sync/check.py re-runs all match the reports) but
  the orchestrator's own merge attempts were denied by this session's tool-permission classifier.
  **User action needed:** merge MR !253 first (or !254 directly — !254's branch already contains
  !253's commit, so either order reconciles cleanly), then re-run `docs/tasks/validate-tasks.py` on
  `develop` to confirm the ledger is consistent post-merge.
- T456/T457/T458 (Phase 5 follow-ups) remain exactly as `checkpoint-027` left them — untouched this
  session, no new state.
- `feature/T475-codex-platform-integration` remains untouched, unmerged, unpushed to origin beyond
  its existing local commits — not addressed this session beyond the read-only assessment already
  reported to the user.

## Next steps

- Once MR !253/!254 are merged: `active-tasks.md`'s T430 row should move to `completed-tasks.md`
  in the same edit (per this repo's own ledger invariant), and T431 (promotion criteria,
  `tech-lead`, depends on T430) becomes dispatchable per `plan-041`'s sequencing.
- T431 should cite `docs/artifacts/maturity-levels-v1.md` directly for the final enum names and the
  mandatory-field policy, not re-derive them.
- Gate G2's own open question (which Wave-1-promoted components, if any, are "routing target
  classes" — `plan-041`'s Finding 1) still needs to be answered as part of T433's eventual
  acceptance criteria, not before.
