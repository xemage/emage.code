# T794 — Tracked-debt register v14

**ID:** T794
**Owner:** tech-lead
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-12
**Completed:** 2026-11-12
**Based on:**
- `docs/plans/plan-152-tracked-debt-register-v14.md` (task T794)
- The user's answer of 2026-11-12, verbatim: "v14 go"
- `docs/artifacts/tracked-debt-register-v13.md`; `docs/plans/plan-150-pin-checklist-no-docker.md`; `docs/artifacts/security-review-t789-pin-checklist-v1.md`; `docs/plans/plan-151-context-retriever-code-residue.md`; `docs/artifacts/security-review-t791-context-retriever-v1.md`; `docs/artifacts/qa-recheck-t792-context-retriever-v1.md`

## 1. What and why

Write `docs/artifacts/tracked-debt-register-v14.md`, as specified in `docs/plans/plan-152-tracked-debt-register-v14.md` § Task Decomposition. That plan's § Facts since v13 is the source for the merges, the user's words since v13 and the ledger count.

## 2. Output

`docs/artifacts/tracked-debt-register-v14.md`, committed on `agent/tech-lead/T794`. No other file changes.

## 3. Constraints

- Work in your own worktree on branch `agent/tech-lead/T794`. Use Conventional Commits, each ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Do not push and do not merge. Never create, push or delete a tag or release.
- Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line. No `docker` command.
- Never open `tests/golden/held-out/`, and never write a held-out case id. A recursive search over `tests/` needs `--exclude-dir=held-out`.
- Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/*.json`. Never print a secret value.
- Do not read the CWSO repository. Mark anything you did not verify **(unverified)**.
- Run no mutation and no full suite. Put a `timeout` on any test run.
- Do not modify or delete files in the shared scratchpad that you did not create.
- Token budget: 80k, counting context. Read v13 and the sources above. Do not re-read v1 to v12.

## 4. Acceptance criteria

As in the plan:
- every v13 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
- each status claim can be traced, or is marked **(unverified)**;
- the counts add up, and the register states whether any open item is above LOW;
- these pass: `python3 docs/tasks/validate-tasks.py`, `python3 -m unittest tests.functional.test_link_integrity` and `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
