# T626 — Independent check of the T625 /code-review artifact against the command text

**ID:** T626
**Owner:** qa-engineer
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** T625
**Affects:** —
**Created:** 2026-10-14
**Completed:** —
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Task Decomposition item for T626)
- `docs/artifacts/code-review-t619-v1.md` (the artifact under check), `implementation/knowledge/commands/code-review.md`, skill `code-review`
- The user's approval of plan-121 on 2026-10-14 (AskUserQuestion, verbatim option label): "Approve as written (Recommended)", together with the decisions quoted in `docs/plans/plan-121-release-v8-wave-2.md` (header).

## 1. What and why

Check, independently of its author, that `docs/artifacts/code-review-t619-v1.md` conforms to `/code-review`: build a per-field table (field, required by the command at which line, present yes/no, value valid yes/no) covering the checklist coverage, the artifact-versions listing, severity levels, remediation suggestions, the conditions with owner and due point if `CONDITIONAL_PASS`, blocker details if `FAIL`, and every field of the `## VERDICT` block. Also confirm each cited file:line exists in the T619 diff (`git diff 5e07a6b..3771781`) and that the review is about that diff. A failed field returns the artifact to T625 (report it; do not edit the artifact). Do not look for any golden or held-out check of `/code-review`.

## 2. Output

`docs/artifacts/code-review-check-t625-v1.md`: the per-field table, the citation check, and a pass/fail conclusion.

## 3. Constraints

- **Write access:** your artifact and this brief's `**Status:**` line (set it to `in_review`). Read-only shell commands only. Do not commit, push or merge.
- Never open `tests/golden/held-out/` unless this brief explicitly authorizes it; never write a held-out case id anywhere (brief, report, commit message, branch name, ledger row, artifact); never write a golden case name unless that case has a `tests/golden/open/` directory. Run `python3 -m unittest tests.functional.test_golden_held_out_isolation` on every artifact before it is committed.
- No `.env*` or credential files; do not read the user's local `.claude/settings.json` or `.vscode/mcp.json`.
- Mark anything you did not re-read **(unverified)**.

## 4. Acceptance criteria

1. One artifact; every field row is evidenced.
2. The conclusion is explicit (PASS: the artifact may be used as the exit artifact; FAIL: the list of fields to repair).
3. The artifact under check is not modified.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
