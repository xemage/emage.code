# T618 — Apply the O-1..O-10 rulings (blocker severity, release checkpoint name, release check and follow-up logging, clean-ups)

**ID:** T618
**Owner:** backend-developer
**Status:** pending
**Priority:** P2
**Tier:** mechanical
**Depends on:** —
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-119-task-protocol-observations-o1-o12.md`
- `docs/artifacts/task-protocol-observations-ruling-v1.md` §3 (held edits 1-A, 2-A, 3-A, 4-A: 17 fences across 11 files), §4 hit counts, §5 effects, §7 handoff package and §7.2 pre-flight greps — the single implementation spec
- `docs/decisions/ADR-008-knowledge-document-authority.md` and `ADR-007-command-contract-authority.md`
- User decisions 2026-10-09 (AskUserQuestion, verbatim option labels): groups 1+2 "Amend both (Recommended)"; group 3 "Apply all (Recommended)"; groups 4+5 "Apply all clean-ups (Recommended)" (O-8 gets no edit); O-11 "Move to an archive file (Recommended)".

## 1. What

Apply, verbatim, the approved fences: 1-A (blocker severity in `blocker-escalation` and `team-status`), 2-A (`prepare-release:29` to
`checkpoint-<SEQ>-release-v<version>.md`), 3-A (O3-a, O3-b, O4-a..O4-d: `release-workflow`, `orchestrator.md`, `code-review`,
`testing-strategy`, `ci-cd-pipeline`) and 4-A (O-7, O-9, O-10 in `task-management`, `plan-approve-execute`, `checkpoint-protocol` and
`docs/checkpoints/_template.md` if that fence names it). O-8 gets no edit; O-5, O-6, O-12 get no edit; O-11 is handled by the orchestrator.
Run the pre-flight greps of ruling §7.2 first (over `tests/` including `tests/golden/open/`, the docs; **exclude `tests/golden/held-out/`,
which you never open**) and report the results. Apply each pair by exact string replacement: single-line Befores as whole lines (O4-b is a
substring match: assert it matches once), the multi-line Befores (O1-b, O9-b, O10-a, O10-b) as whole blocks; assert each occurs exactly
once; stop and report as a `dependency` blocker if an anchor is missing or not unique, or if any non-golden test or open golden case
asserts a Before string. Line numbers may be off by one: anchor by text. Never reword.

Do not edit `AGENTS.md`, `implementation/AGENTS.md`, any instruction, `validate-workflow`, `bug-report`, `verification-before-completion`,
`docs/tasks/validate-tasks.py`, any file under `tests/golden/**`, `scripts/`, `.env*`, or any derived platform folder by hand. Do not edit
`docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.

## 2. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file. Never open `tests/golden/held-out/`; never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` before committing.
- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; do not edit `.claude/` (outside the generated `implementation/.claude` mirror), `.github/` or other derived top-level folders.
- Regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py`. Declare the root drift in `tests/_baselines/root-install-drift.json` (currently empty; expected about 74 sorted paths, plus one comment line "Declared 2026-10-09 by T618 (...)"). Do NOT refresh the root install.
- Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`, `scorecard.py --check` (34/26/0), `validate-tasks.py`, the evaluator hash via `implementation/runtime/golden_harness/evaluator_hash.py` (baseline v20 unchanged), the held-out isolation test, and the full suite `python3 tests/run.py` redirected to a file. Confirm byte-unchanged: the do-not-edit list and `tests/golden/**`.

## 3. Outputs

The edited files; regenerated mirrors and `implementation/registry/index.json`; the drift baseline; a report with the pre-flight grep results, every §4 count as lines and occurrences (after edits), the gate results, the suite summary line, the drift paths and every deviation.

## 4. Acceptance criteria

1. Every Before replaced exactly once with its After; nothing else changed in the source files.
2. All gates and the full suite pass; no protected-path grant and no new baseline are needed (report if one is).
3. No root refresh is done.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
