# T610 — Apply the AGENTS.md naming rulings (O1, O2, O5) and the poc-orchestrator indentation cosmetic

**ID:** T610
**Owner:** backend-developer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** T608
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-114-placeholder-flag-and-naming-rulings.md`
- `docs/artifacts/naming-conflicts-ruling-v1.md` §3 (held edits C-1..C-3, T-1, N-1..N-3, K-1), §4 hit counts, §5 effects and pre-flight greps, §10 handoff package — the single implementation spec
- `docs/decisions/ADR-008-knowledge-document-authority.md`
- User decisions 2026-10-09 (AskUserQuestion, verbatim option labels): T606 Q1 "You confirm each flag (Recommended)"; T606 Q2 "Remove skip, label 3 shapes (Recommended)"; T607 O1 "Amend coding-standards (Recommended)"; T607 O2+O5 "Apply both (Recommended)".

## 1. What

Apply, verbatim, the fences the user approved: O1-A (C-1, C-2, C-3 amend `coding-standards`; T-1 the templates' `:61` revision rule), O2-A (N-1, N-2: `/new-project:43` and `:51`), O5-A (N-3: `/new-feature:25`), and the cosmetic K-1 (the three-space indentation line in `poc-orchestrator.md`, found by text: it is at `:103` in the ruling's worktree, not `:102`; T608 adds text above it, so re-find it). Run the pre-flight greps of ruling §5.4 first; the ruling could not run them. The `N-1` anchor at `/new-project:43` begins with a TAB, and the fence keeps it. `[CHECKPOINT]` at `:42` is left alone.

Do not edit `AGENTS.md`, any other instruction, `scrum-master.md`, `checkpoint-protocol`, any script, or `tests/golden/**`. The stale quote in one open golden case's brief (ruling §5.2) is reported to the orchestrator, not edited. If a non-golden test asserts a `Before` string, stop and report it as a `dependency` blocker.

## Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file. Never open `tests/golden/held-out/`; never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on every artifact before committing.
- Work in your own worktree/branch. Commit with a Conventional Commit message. Do not push; do not merge; do not edit `.claude/settings.json` or `.claude/settings.local.json`.
- Apply each edit by exact string replacement and assert each `Before` text occurs exactly once; stop and report if an anchor is missing or not unique.

Gates to report: `node implementation/scripts/sync.mjs --root implementation` then `--check`, `python3 implementation/scripts/generate-registry.py` then `--check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check` (must equal the current baseline 34/26/0), `python3 docs/tasks/validate-tasks.py`, the evaluator hash (`implementation/scripts/evaluator_hash.py`, baseline v20 unchanged), and the full suite `python3 tests/run.py` with output redirected to a file. Report root drift with `--print-drift` and do NOT refresh the root: the orchestrator does that in a separate root-refresh task.

## Outputs

The edited files; regenerated mirrors and `implementation/registry/index.json`; a report with every §4 count as lines and occurrences, the pre-flight grep results, the gate results and the `--print-drift` paths (expected about 25).

## Acceptance criteria

1. Every Before replaced exactly once; the unchanged-file list of ruling §10 is byte-unchanged.
2. All gates and the full suite pass; no protected-path grant and no new baseline are needed (report if one is).
3. No root refresh is done.

## Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
