# T809 — Tracked-debt register v16

**ID:** T809
**Owner:** tech-lead
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-13
**Completed:** 2026-11-13
**Based on:**
- `docs/plans/plan-158-brave-acceptance-v4-and-register-v16.md` (task T809; § Facts since v15; § T808 result)
- The user's answer of 2026-11-13, verbatim: "2. v16 go"
- `docs/artifacts/tracked-debt-register-v15.md`; `docs/plans/plan-155-v11-release-decisions.md`; `docs/plans/plan-156-apply-adr-015.md`; `docs/plans/plan-157-confirmation-as-validity-condition.md`; `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md`; `docs/decisions/ADR-016-security-engineer-confirmation-as-validity-condition.md`; `docs/artifacts/security-review-t802-adr-015-apply-v1.md`; `docs/artifacts/security-review-t806-adr-016-apply-v1.md`; `docs/artifacts/brave-replacement-scouting-v1.md`; `docs/artifacts/brave-audit-acceptance-v4.md` (T808)

## 1. What and why

Write `docs/artifacts/tracked-debt-register-v16.md`, as specified in `docs/plans/plan-158-brave-acceptance-v4-and-register-v16.md` § Task Decomposition item 2. That plan's § Facts since v15 is the source for the merges, the user's words since v15 and the ledger count.

## 2. Output

`docs/artifacts/tracked-debt-register-v16.md`, committed on `agent/devops-engineer/T808` (the plan's one branch) in the worktree `/home/emage/Code/emage/worktrees/agent-devops-engineer-T808`. No other file changes.

## 3. Constraints

- Conventional Commits, each ending with `Co-Authored-By: Claude <noreply@anthropic.com>`.
- Do not push and do not merge. Never create, push or delete a tag or release.
- Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line. No `docker` command.
- Never open `tests/golden/held-out/`, and never write a held-out case id. A recursive search over `tests/` needs `--exclude-dir=held-out`.
- Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/*.json`. Never print a secret value.
- Do not read the CWSO repository. Mark anything you did not verify **(unverified)**.
- Run no mutation and no full suite. Put a `timeout` on any test run.
- Do not modify or delete files in the shared scratchpad that you did not create.
- Token budget: 80k, counting context. Read v15 and the sources above. Do not re-read v1 to v14 except where v15 points to one for a carried row.

## 4. Acceptance criteria

As in the plan:
- every v15 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
- each status claim can be traced, or is marked **(unverified)**;
- the counts add up, and the register states whether any open item is above LOW;
- these pass: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity` and `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
