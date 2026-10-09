# T608 — Apply the placeholder-flag agent text (E-P1, E-O1, E-P2) with the V3 conditions

**ID:** T608
**Owner:** backend-developer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-114-placeholder-flag-and-naming-rulings.md`
- `docs/artifacts/placeholder-flag-ruling-v3.md` §2, §4, §6 (E-P1, E-O1, E-P2), §7, §9 — the single implementation spec
- `docs/artifacts/security-review-placeholder-flag-ruling-v3.md` (conditions V3-1, V3-3, V3-4, V3-5, V3-7, V3-8 are binding)
- `docs/artifacts/security-review-placeholder-flag-ruling-v2.md` and `-v1.md` (history)
- User decisions 2026-10-09 (AskUserQuestion, verbatim option labels): T606 Q1 "You confirm each flag (Recommended)"; T606 Q2 "Remove skip, label 3 shapes (Recommended)"; T607 O1 "Amend coding-standards (Recommended)"; T607 O2+O5 "Apply both (Recommended)".

## 1. What

Apply Question 1 Option 1 (you confirm each flag, no code) and the interim blind-spot note: edit
`implementation/knowledge/agents/poc-security-engineer.md` (E-P1, E-P2) and `implementation/knowledge/agents/poc-orchestrator.md`
(E-O1) exactly as held in v3 §6, **plus** the drafting conditions the Security Engineer attached in the v3 review. Quote and
satisfy each of these verbatim:

- **V3-1** (E-P1 and E-O1): for progression control an unresolved hit is treated as an open blocking finding (task `blocked`, no continue/demo/evaluate/close, a task "awaiting user: placeholder flag" before archival); the exposed-secret steps start only when the hit is classified real or the user declines; an unresolved hit left at timebox, escalation or close becomes an open blocking finding.
- **V3-3** (E-O1, E-P1): the modified-paths list is the paths that differ from `flag_commit` in committed, staged and working-tree state plus untracked files, with deletions and renames; an unavailable or unstated list voids the flags (fail closed).
- **V3-4**: list every register field in E-O1 (or point to one schema) and add a text test that E-O1 names `hit_count` and `class`.
- **V3-5**: state the criteria for "looks like a placeholder": a hit is real at once only for key material, a redacted path, a provider-token format without a user-stated example source, or a user decline; otherwise it is unresolved with a `user-attested` proposal.
- **V3-7**: record the standing decision text only where Question 2 Option A is applied (T609); here, grade covered hits `SECURITY:LOW` for debt handoff as v3 says.
- **V3-8**: add the URL-scheme clause (32 or more characters, or upper case) to E-P2; use "unresolved" where "blocks" is ambiguous.
- Split the very long E-P1 bullet into sub-bullets, keeping each pinned phrase inside one bullet.

If a condition cannot be met without changing a held edit's meaning, stop and report; do not reword on your own.

Do not touch the scanner, the server, the tool lists or `servers.yaml`. The F-8, E1-b and E1-c After texts stay byte-identical.

## Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file. Never open `tests/golden/held-out/`; never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on every artifact before committing.
- Work in your own worktree/branch. Commit with a Conventional Commit message. Do not push; do not merge; do not edit `.claude/settings.json` or `.claude/settings.local.json`.
- Apply each edit by exact string replacement and assert each `Before` text occurs exactly once; stop and report if an anchor is missing or not unique.

Gates to report: `node implementation/scripts/sync.mjs --root implementation` then `--check`, `python3 implementation/scripts/generate-registry.py` then `--check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check` (must equal the current baseline 34/26/0), `python3 docs/tasks/validate-tasks.py`, the evaluator hash (`implementation/scripts/evaluator_hash.py`, baseline v20 unchanged), and the full suite `python3 tests/run.py` with output redirected to a file. Report root drift with `--print-drift` and do NOT refresh the root: the orchestrator does that in a separate root-refresh task.

## Outputs

Edited agent files; regenerated mirrors and `implementation/registry/index.json`; the text-pin tests of v3 §7 (E-P1/E-O1 contain the listed phrases exactly once, the F-8/E1-b/E1-c texts, tools lists and `servers.yaml` unchanged, E-P1 negative pin on "ephemeral local instance"); a report with the gate results and the `--print-drift` paths.

## Acceptance criteria

1. Both agents' text matches v3 §6 plus the quoted conditions, each Before replaced exactly once.
2. All text pins pass; the existing `test_poc_audit_server.py` tests stay green.
3. All gates pass or are reported; no root refresh is done.
4. A Security Engineer reviews the applied diff of E-P1, E-O1 and E-P2 before merge (the orchestrator dispatches it; it is the gate).

## Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
