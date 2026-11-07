# T765 — Python image bump, the CA check and the installer note

**ID:** T765
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Tier:** standard
**Depends on:** T753, T756
**Affects:** —
**Created:** 2026-11-06
**Completed:** 2026-11-07
**Based on:**
- `docs/plans/plan-145-release-v10.md` (task T765)
- The user's answers of 2026-11-06, verbatim: "release go"; "Approve (Recommended)"

## 1. What and why

SEC-T756-01, SEC-T756-02's check and TL-T753-04, as `docs/plans/plan-145-release-v10.md` § Task Decomposition specifies.

## 2. Output

`.gitlab-ci.yml`, `scripts/install.sh`, any test constant the bump needs, and `docs/artifacts/ca-check-t765-v1.md`, committed on `agent/devops-engineer/T765`.

## 3. Constraints

- As in the plan, § Constraints. Do not push, merge, tag or release unless this task's owner is the orchestrator. Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id; a recursive search over `tests/` needs `--exclude-dir=held-out`. Read no `.env*` or credential file, and not the user's local `.claude/settings*.json` or `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.
- No `docker` command.
- Token budget: 110k, counting context.

## 4. Acceptance criteria

As in the plan, § Task Decomposition, T765, and `docs/artifacts/security-review-t756-accepted-mediums-v1.md`.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
