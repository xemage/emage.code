# T616 — Apply the task-protocol skill rulings (items 1 to 6)

**ID:** T616
**Owner:** backend-developer
**Status:** pending
**Priority:** P2
**Tier:** mechanical
**Depends on:** —
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-118-task-protocol-skill-conflicts.md`
- `docs/artifacts/task-protocol-skill-conflicts-ruling-v1.md` §3 (held edits BE-1, BE-2; TM-1..TM-4; GL-1..GL-3; DG-0..DG-3; CP-1, CP-2: 20 fences), §4 hit counts, §5 effects and §5.4 pre-flight greps, §8 handoff package — the single implementation spec
- `docs/decisions/ADR-008-knowledge-document-authority.md`
- User decisions 2026-10-09 (AskUserQuestion, verbatim option labels): items 1, 5, 6 "Apply all three (Recommended)"; item 2 "Apply all (Recommended)"; item 3 "Apply (Recommended)"; item 4 "Apply (Recommended)".

## 1. What

Apply, verbatim, the approved fences in `implementation/knowledge/skills/blocker-escalation/SKILL.md` (BE-1, BE-2),
`task-management/SKILL.md` (TM-1..TM-4), `gitlab-management/SKILL.md` (GL-1..GL-3), `dependency-graphing/SKILL.md` (DG-0..DG-3) and
`checkpoint-protocol/SKILL.md` (CP-1, CP-2). Run the pre-flight greps of ruling §5.4 first (over `tests/` including `tests/golden/open/`,
`docs/wiki`, `docs/guides`, `README.md`; **exclude `tests/golden/held-out/`, which you never open**) and report the results. Apply each pair
by exact string replacement, matching each Before as a whole line or block, and assert it occurs exactly once; stop and report as a
`dependency` blocker if an anchor is missing or not unique, or if any non-golden test or any open golden case asserts a Before string.
Line numbers in the ruling may be off by one: anchor by text. Never reword. The artifact's §3.2 fence for `task-management` contains headings
inside its fences: take the Before/After text exactly as written between the fence markers.

Do not edit `AGENTS.md`, `implementation/AGENTS.md`, any instruction, any command (including `prepare-release.md`), any agent, `release-workflow`,
`plan-approve-execute`, `code-review`, `testing-strategy`, `ci-cd-pipeline`, any file under `tests/golden/**`, `scripts/`, `.env*`, or any
derived platform folder by hand. The further observations O-1..O-12 of the ruling are not ruled and stay untouched. Do not edit the historical
notes under the table in `docs/tasks/active-tasks.md` (this file belongs to the orchestrator).

## 2. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file. Never open `tests/golden/held-out/`; never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` before committing.
- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; do not edit `.claude/` (outside the generated `implementation/.claude` mirror), `.github/` or other derived top-level folders, `docs/tasks/active-tasks.md`, `completed-tasks.md`, or any brief's Status line.
- Regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py`. Declare the root drift in `tests/_baselines/root-install-drift.json` (currently empty; expected 35 sorted paths = the five skills on 7 platforms each, plus one comment line "Declared 2026-10-09 by T616 (...)"). Do NOT refresh the root install.
- Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`, `scorecard.py --check` (34/26/0), `validate-tasks.py`, the evaluator hash via `implementation/runtime/golden_harness/evaluator_hash.py` (baseline v20 unchanged), the held-out isolation test, and the full suite `python3 tests/run.py` redirected to a file. Confirm byte-unchanged: the do-not-edit list and `tests/golden/**`.

## 3. Outputs

The edited files; regenerated mirrors and `implementation/registry/index.json`; the drift baseline; a report with the pre-flight grep results, every §4 count as lines and occurrences (after edits), the gate results, the suite summary line, the drift paths and every deviation.

## 4. Acceptance criteria

1. Every Before replaced exactly once with its After; nothing else changed in the five source files.
2. All gates and the full suite pass; no protected-path grant and no new baseline are needed (report if one is).
3. No root refresh is done.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
