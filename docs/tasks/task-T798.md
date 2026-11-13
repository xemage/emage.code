# T798 — Tracked-debt register v15

**ID:** T798
**Owner:** tech-lead
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-12
**Completed:** 2026-11-12
**Based on:**
- `docs/plans/plan-154-tracked-debt-register-v15.md` (task T798)
- The user's answer of 2026-11-12, verbatim: "v15 go"
- `docs/artifacts/tracked-debt-register-v14.md`; `docs/plans/plan-153-context-retriever-low-residue.md`; `docs/artifacts/security-review-t796-context-retriever-v1.md`; `docs/artifacts/security-review-t796-context-retriever-v2.md`

## 1. What and why

Write `docs/artifacts/tracked-debt-register-v15.md`, as specified in `docs/plans/plan-154-tracked-debt-register-v15.md` § Task Decomposition. That plan's § Facts since v14 is the source for the merges, the user's words since v14 and the ledger count.

## 2. Output

`docs/artifacts/tracked-debt-register-v15.md`, committed on `agent/tech-lead/T798`. No other file changes.

## 3. Constraints

- Work in your own worktree on branch `agent/tech-lead/T798`. Use Conventional Commits, each ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Do not push and do not merge. Never create, push or delete a tag or release.
- Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line. No `docker` command.
- Never open `tests/golden/held-out/`, and never write a held-out case id. A recursive search over `tests/` needs `--exclude-dir=held-out`.
- Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/*.json`. Never print a secret value.
- Do not read the CWSO repository. Mark anything you did not verify **(unverified)**.
- Run no mutation and no full suite. Put a `timeout` on any test run.
- Do not modify or delete files in the shared scratchpad that you did not create.
- Token budget: 80k, counting context. Read v14 and the sources above. Do not re-read v1 to v13 except where v14 points to one for a carried row.

## 4. Acceptance criteria

As in the plan:
- every v14 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
- each status claim can be traced, or is marked **(unverified)**;
- the counts add up, and the register states whether any open item is above LOW;
- these pass: `python3 docs/tasks/validate-tasks.py`, `python3 -m unittest tests.functional.test_link_integrity` and `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
