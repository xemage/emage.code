# Checkpoint 014: Plan 015 (Claude Code Platform) — Full Gate Passed

**Phase:** QA → Release transition (Plan 015)
**Status:** T285–T299 all done; T295 GATE green; only release-cut tasks remain
**Date:** 2026-07-30
**Branch:** `feature/t285-add-claude-code-platform` (off `develop`, not pushed)

## Completed since checkpoint-013

| Task | Owner | Commit(s) | Artifact |
|------|-------|-----------|----------|
| T292 | technical-writer | `cd3bfd4` | README.md, docs/wiki/quick-start.md |
| T293 | technical-writer | `d485749` (+ brief fix `e7580d5`) | CONTRIBUTING.md, AGENTS.md |
| T294 | qa-engineer | `44d4d27` | 4 test files extended |
| T298 | backend-developer | `0a70bae` | implementation/registry/index.json (follow-up) |
| T299 | qa-engineer | `66f3d1f` | 12 task-brief Status headers (follow-up) |
| T295 | qa-engineer | `6f527d0` (record only) | GATE — 6/6 steps pass, no code changes |

Plus 2 small orchestrator fixes: `.gitignore` entry for root-level `.claude/`
harness settings (`99e67d7`), and T293's `grep -F` acceptance-criteria bug
(`e7580d5`).

## Defects found and fixed during this segment (3 more, on top of the 2 in checkpoint-013)

3. **T293 AC1-3 used `grep -Fc`** with patterns relying on BRE alternation
   (`\|`) and escaped-dot (`\.`) — `-F` treats those as literal backslash
   characters, so the checks could never pass regardless of edit
   correctness. Fixed: dropped `-F`. Verified against the real (correct)
   edits: counts were 4/5/1, matching the documented thresholds.
4. **Registry never regenerated** — neither T287 (new manifest) nor T288
   (`make sync`) in the original plan included regenerating
   `implementation/registry/{index.json,summary.md}`, so T295's Step 3
   (`check.py --registry`) failed with drift. Fixed by inserting **T298** as
   a new task (not in the original 13-task graph) and wiring it as a T295
   dependency.
5. **No task brief ever updated its own `**Status:**` header** — every
   T285-T294/T298 brief only instructed moving the *row* between
   `active-tasks.md`/`completed-tasks.md`, never the brief file's own status
   line. The shipped ledger validator's `C8` check caught this at T295 Step
   4. Fixed by inserting **T299** as a new task, which (correctly, per its
   own executing subagent's judgment) also flipped its own header to stay
   self-consistent.

Total this plan: **5 real defects found in Orchestrator-authored task briefs**,
each caught by an executing subagent following the Blocker Protocol (revert +
report) rather than silently working around it, each fixed by the
Orchestrator before re-delegating. No test, check, or acceptance criterion
was weakened to force a pass.

## T295 GATE result (third attempt, final)

All 6 steps passed: `sync.mjs` (zero drift, 505 files), `verify.mjs` (OK),
`check.py` full super-gate (247 checks, 0 errors), `tests/run.py` (264 tests,
0 failures), `bash -n scripts/install.sh`, markdown link check. Working tree
clean.

## Key decisions

- Inserted T298/T299 as new tasks rather than reopening/rewriting the
  already-committed T287/T288/T285-T294 briefs — preserves the audit trail of
  what each original task actually did versus what was fixed afterward.
- Root-level `.claude/` (Claude Code CLI's own session settings, distinct
  from the tracked `implementation/.claude/` platform projection) was
  gitignored with an anchored `/.claude/` pattern so it can never affect the
  tracked directory.

## Next steps

1. Batch F: delegate T296 (release docs `v6.4.0.md` + marker bump) to
   release-manager.
2. Delegate T297 (release branch prep only — stop before tag/MR/push).
3. Report final status to user; do not push, open an MR, or tag without
   explicit user confirmation (T297 is designed to stop exactly there).
</content>
