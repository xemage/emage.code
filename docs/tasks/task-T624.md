# T624 — Apply the T621 rulings (A1: O4-a, O1-a, O2-a, O6-a; B1: O5-a; C1: O8-a)

**ID:** T624
**Owner:** backend-developer
**Status:** pending
**Priority:** P1
**Tier:** mechanical
**Depends on:** —
**Affects:** —
**Created:** 2026-10-14
**Completed:** —
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Task Decomposition item for T624)
- `docs/artifacts/remaining-observations-ruling-v1.md` §3 (held edits), §4 hit counts, §5 effects, §7 handoff package and §7.2 pre-flight greps — the single implementation spec
- `docs/decisions/ADR-008-knowledge-document-authority.md`
- The user's approval of plan-121 on 2026-10-14 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)", together with the decisions quoted in `docs/plans/plan-121-release-v8-wave-2.md` (header).

## 1. What and why

Apply, verbatim, the fences the user approved: O4-a (`orchestrator.md` Implementation-gate wording), O1-a and O5-a (`technical-debt-tracking` skill: category-set note; scan scope = the PoC root, every text file, registers skipped), O2-a (`technical-debt-narrator.md`: exempt `TECHNICAL-DEBT.md` and `POC-DEBT-SCORECARD.md` from the `<type>-vN.md` rule), O6-a (`poc-evaluation` skill: scope the `/evaluate-poc` Debt Summary severities to the ledger/scorecard values) and O8-a (`gitlab-management` § Label Conventions: document the `priority::*` to ledger-priority mapping from `commands/bug-report.md:54`: critical and high to `P0`, medium to `P1`, low to `P2`, as an agreement rule). Not applied: O1-b (`poc-guidelines.md`), O5-c, option C2-C4. Run the ruling's §7.2 pre-flight greps first (over `tests/` including `tests/golden/open/`, `docs/wiki`, `README.md`; exclude `tests/golden/held-out/`, which you never open); apply each pair by exact string replacement asserting every Before occurs exactly once (anchor by text; line numbers may be off); stop and report as a `dependency` blocker if an anchor is missing/not unique or any non-golden test or open golden case asserts a Before string. Never reword. Expected: 6 fences in 5 files, about 33 root-drift paths (3 skills x 7 + 2 agents x 6).

## 2. Output

The edited files; regenerated mirrors and `implementation/registry/index.json`; the declared drift baseline; a report with the pre-flight greps, every hit count after the edits (lines/occurrences), gate results, the suite summary line and every deviation.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; do not edit `.claude/` (outside the generated `implementation/.claude` mirror), `.github/` or other derived top-level folders, `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py` when a projected file changes; declare the root drift in `tests/_baselines/root-install-drift.json` (sorted `--print-drift` paths plus one comment line starting "Declared <date> by <task> ("); do NOT refresh the root install.
- Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`, `scorecard.py --check` (34/26/0 unless the brief says otherwise), `docs/tasks/validate-tasks.py`, the evaluator hash via `implementation/runtime/golden_harness/evaluator_hash.py` (baseline v20 unchanged unless the brief says otherwise), the held-out isolation test, and the full suite `python3 tests/run.py` redirected to a file.
- Never open `tests/golden/held-out/` unless this brief explicitly authorizes it; never write a held-out case id anywhere (brief, report, commit message, branch name, ledger row, artifact); never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on every artifact before it is committed.
- No `.env*` or credential files; do not read the user's local `.claude/settings.json` or `.vscode/mcp.json`.
- Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. Every Before replaced exactly once with its After; nothing else changed in the source files.
2. All gates and the full suite pass; no grant or new baseline needed (report if one is); no root refresh.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
