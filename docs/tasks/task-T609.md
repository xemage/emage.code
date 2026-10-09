# T609 — Remove the $ < { space skips and add the template-ref label to the scanner (E-S2, Question 2 Option A)

**ID:** T609
**Owner:** backend-developer
**Status:** pending
**Priority:** P2
**Tier:** standard
**Depends on:** T608
**Affects:** —
**Created:** 2026-10-09
**Completed:** —
**Based on:**
- `docs/plans/plan-114-placeholder-flag-and-naming-rulings.md`
- `docs/artifacts/placeholder-flag-ruling-v3.md` §5 Question 2 Option A, §6 E-S2, §7, §9 RA-7, RA-11, RA-12
- `docs/artifacts/security-review-placeholder-flag-ruling-v3.md` (V3-2, V3-6, V3-7, V3-8 are binding)
- `docs/artifacts/poc-security-engineer-tool-scoping-v2.md` (contract) and `security-review-poc-security-audit-code-v1.md` / `-v2.md` (L-3, the dedup at `poc_scan.py:300-304`)
- `implementation/runtime/security/poc_scan.py`, `poc_audit_server.py`, `tests/functional/test_poc_audit_server.py`
- User decisions 2026-10-09 (AskUserQuestion, verbatim option labels): T606 Q1 "You confirm each flag (Recommended)"; T606 Q2 "Remove skip, label 3 shapes (Recommended)"; T607 O1 "Amend coding-standards (Recommended)"; T607 O2+O5 "Apply both (Recommended)".

## 1. What

Implement Question 2 Option A: remove the `$`, `<`, `{` and space leading-character skips named in v3 E-S2, bump `RULES_VERSION`,
and add the `template-ref` label for the three exact shapes (`${NAME}` with NAME all caps, `<word-word>` lowercase with a
separator and no digits, `{{ name }}` with no digits). A bare `$NAME` gets the label `bare-dollar-name` and stays unresolved
(blocking until flagged). Labelled hits are listed, counted separately and graded `SECURITY:LOW` for debt handoff; the user's
standing decision (quoted from the decision line in this brief) is recorded in the agent text.

Binding review conditions, quoted from the v3 security review:

- **V3-2:** restrict `template-ref` and `bare-dollar-name` to `credential-assignment` and `unquoted-credential-assignment`. URL hits become ordinary unlabelled hits (or require the username to be an exact shape too).
- **V3-6:** add a contract v3 (the contract v2 says matched text is dropped unread; E-S2 compares it in memory only), the hit-key pin (`test_poc_audit_server.py:374`) and the server key allow-list for `value_shape` and `template_shape`; pin value extraction and the exact regexes (for example `<[a-z]+([ _-][a-z]+)+>`); add reverse-order and three-match tests.
- **V3-7:** grade labelled hits `SECURITY:LOW` for debt handoff, add a template-ref count to the totals, and record the user's standing decision (quoted) in this brief's report or a decision note.
- **V3-8:** replace E-P2 so it keeps the remaining blind spots (a clean scan excludes ...); state which leaders stay excluded and why; use "unresolved" not "blocks"; drop `dummy-word` for `bearer-token`.
- E-S2 conditions 1-5 of v3 (all matches on the line must be an exact shape; the dedup at `:300-304` must not discard a second match first; only `worktree`/`index` hits without `commit` are labelled; compare in memory, never return matched text), plus the mixed-line and `log`-hit tests.

The tool list stays two tools; the F-8 text and the existing contract tests stay green except where the hit-key pin legitimately changes.

## Constraints

- **Read access:** the whole repo, except `tests/golden/held-out/`, `.env*`, and any credential or key file. Never open `tests/golden/held-out/`; never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on every artifact before committing.
- Work in your own worktree/branch. Commit with a Conventional Commit message. Do not push; do not merge; do not edit `.claude/settings.json` or `.claude/settings.local.json`.
- Apply each edit by exact string replacement and assert each `Before` text occurs exactly once; stop and report if an anchor is missing or not unique.

Gates to report: `node implementation/scripts/sync.mjs --root implementation` then `--check`, `python3 implementation/scripts/generate-registry.py` then `--check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check` (must equal the current baseline 34/26/0), `python3 docs/tasks/validate-tasks.py`, the evaluator hash (`implementation/scripts/evaluator_hash.py`, baseline v20 unchanged), and the full suite `python3 tests/run.py` with output redirected to a file. Report root drift with `--print-drift` and do NOT refresh the root: the orchestrator does that in a separate root-refresh task.

## Outputs

Scanner and server changes, contract v3 (a new artifact), updated and new tests, the agent-text edits for the standing decision, regenerated mirrors and registry, a report with the gate results and the `--print-drift` paths.

## Acceptance criteria

1. All E-S2 conditions and V3-2/V3-6/V3-7/V3-8 are met and tested; no matched text appears in any result or error.
2. A mixed line (placeholder plus real value) gets no label; a `log` hit and stash/history tree hits get none; a URL hit gets none.
3. The full suite and all gates pass; no root refresh.
4. A Security Engineer code-reviews the change before merge (the orchestrator dispatches it).

## Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
