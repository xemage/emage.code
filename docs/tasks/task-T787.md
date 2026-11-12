# T787 — Tracked-debt register v13

**ID:** T787
**Owner:** tech-lead
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-12
**Completed:** 2026-11-12
**Based on:**
- `docs/plans/plan-149-tracked-debt-register-v13.md` (task T787)
- The user's answer of 2026-11-12, verbatim: "v13 go"
- `docs/artifacts/tracked-debt-register-v12.md`; `docs/plans/plan-148-node-image-bump.md`; `docs/artifacts/security-review-t784-node-advisory-v1.md`; `docs/artifacts/security-review-t786-node-bump-v1.md`; `docs/checkpoints/checkpoint-042-plan-146-ca-pi-gemini.md`

## 1. What and why

Write `docs/artifacts/tracked-debt-register-v13.md`, as specified in `docs/plans/plan-149-tracked-debt-register-v13.md` § Task Decomposition. That plan's § Facts since v12 is the source for the new image review date and for plan-148's merges.

## 2. Output

`docs/artifacts/tracked-debt-register-v13.md`, committed on `agent/tech-lead/T787`. No other file changes.

## 3. Constraints

- Work in your own worktree on branch `agent/tech-lead/T787`. Use Conventional Commits, each ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Do not push and do not merge. Never create, push or delete a tag or release.
- Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line. No `docker` command.
- Never open `tests/golden/held-out/`, and never write a held-out case id. A recursive search over `tests/` needs `--exclude-dir=held-out`.
- Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/*.json`. Never print a secret value.
- Do not read the CWSO repository. Mark anything you did not verify **(unverified)**.
- Run no mutation and no full suite. Put a `timeout` on any test run.
- Do not modify or delete files in the shared scratchpad that you did not create.
- Token budget: 80k, counting context. Read v12 and the sources above. Do not re-read v1 to v11.

## 4. Acceptance criteria

As in the plan:
- every v12 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
- each status claim can be traced, or is marked **(unverified)**;
- the counts add up, and the register states whether any open item is above LOW;
- these pass: `python3 docs/tasks/validate-tasks.py`, `python3 -m unittest tests.functional.test_link_integrity` and `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
