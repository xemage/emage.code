# T614 — Apply the Scrum Master and checkpoint-name rulings (S1, S2, K)

**ID:** T614
**Owner:** backend-developer
**Status:** done
**Priority:** P2
**Tier:** mechanical
**Depends on:** —
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-117-scrum-master-and-checkpoint-name-rulings.md`
- `docs/artifacts/task-protocol-and-checkpoint-name-ruling-v1.md` §3 (held edits S-1..S-4 for `scrum-master.md`, C-1..C-5 for `checkpoint-protocol/SKILL.md`), §4 hit counts, §5 effects and §5.4 pre-flight greps, §8 handoff package — the single implementation spec
- `docs/decisions/ADR-008-knowledge-document-authority.md`
- User decisions 2026-10-09 (AskUserQuestion, verbatim option labels): T613 S1 "Amend the agent (Recommended)"; S2 "Amend the agent (Recommended)"; K "Amend the skill (Recommended)".

## 1. What

Apply, verbatim, the approved fences: S1-A (S-1, S-2, S-4) and S2-A (S-3) in `implementation/knowledge/agents/scrum-master.md`, and K-A
(C-1..C-5) in `implementation/knowledge/skills/checkpoint-protocol/SKILL.md`. Run the pre-flight greps of ruling §5.4 first
(excluding `tests/golden/held-out/`, which you never open) and report the results. Apply each pair by exact string replacement,
matching each Before as a whole line, and assert it occurs exactly once; stop and report as a `dependency` blocker if an anchor is
missing or not unique, or if any non-golden test asserts a Before string. Line numbers in the ruling may be off by one or have moved:
anchor by text. Never reword.

Do not edit `AGENTS.md`, `implementation/AGENTS.md`, any instruction, any command, `orchestrator.md`, `blocker-escalation`,
`task-management`, `gitlab-management`, `dependency-graphing`, any file under `tests/golden/**`, `scripts/`, `.env*`, or any derived
platform folder by hand. The other-sites observations of ruling §4.3/§7 are not ruled and stay untouched.

## 2. Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file. Never open `tests/golden/held-out/`; never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` before committing.
- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; do not edit `.claude/` (outside the generated `implementation/.claude` mirror), `.github/` or other derived top-level folders, `docs/tasks/active-tasks.md`, `completed-tasks.md`, or any brief's Status line.
- Regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py`. Declare the root drift in `tests/_baselines/root-install-drift.json` (currently empty; expected 13 sorted paths = `scrum-master` on 6 platforms and `checkpoint-protocol` on 7, plus one comment line "Declared 2026-10-09 by T614 (...)"). Do NOT refresh the root install.
- Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`, `scorecard.py --check` (34/26/0), `validate-tasks.py`, the evaluator hash via `implementation/runtime/golden_harness/evaluator_hash.py` (baseline v20 unchanged), the held-out isolation test, and the full suite `python3 tests/run.py` redirected to a file. Confirm byte-unchanged: the files in the do-not-edit list and `tests/golden/**`.

## 3. Outputs

The edited files; regenerated mirrors and `implementation/registry/index.json`; the drift baseline; a report with the pre-flight grep results, every §4 count as lines and occurrences, the gate results, the suite summary line, the drift paths and every deviation.

## 4. Acceptance criteria

1. Every Before replaced exactly once with its After; nothing else changed in the two source files.
2. All gates and the full suite pass; no protected-path grant and no new baseline are needed (report if one is).
3. No root refresh is done.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
