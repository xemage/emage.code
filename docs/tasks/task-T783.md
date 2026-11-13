# T783 — Tracked-debt register v12

**ID:** T783
**Owner:** tech-lead
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-11
**Completed:** 2026-11-11
**Based on:**
- `docs/plans/plan-147-tracked-debt-register-v12.md` (task T783)
- The user's answer of 2026-11-11, verbatim: "v12 go"
- `docs/artifacts/tracked-debt-register-v11.md`; `docs/checkpoints/checkpoint-041-release-v10.0.0.md`; `docs/checkpoints/checkpoint-042-plan-146-ca-pi-gemini.md`; `docs/plans/plan-145-release-v10.md`; `docs/plans/plan-146-ca-check-pi-removal-gemini-scoping.md`; ADR-013; ADR-014; the review artifacts named in the plan

## 1. What and why

Write `docs/artifacts/tracked-debt-register-v12.md`, as `docs/plans/plan-147-tracked-debt-register-v12.md` § Task Decomposition specifies. That plan's § Facts since v11 is the source for TD-T774-01, A-19's closure and the Node image bump.

## 2. Output

`docs/artifacts/tracked-debt-register-v12.md`, committed on `agent/tech-lead/T783`. No other file changes.

## 3. Constraints

- Work in your own worktree on branch `agent/tech-lead/T783`. Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Do not push and do not merge. Never create, push or delete a tag or release.
- Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line. No `docker` command.
- Never open `tests/golden/held-out/`, and never write a held-out case id. A recursive search over `tests/` needs `--exclude-dir=held-out`.
- Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/*.json`. Never print a secret value.
- Do not read the CWSO repository. Mark anything you did not verify **(unverified)**.
- Run no mutation and no full suite. Put a `timeout` on any test run.
- Do not modify or delete files in the shared scratchpad that you did not create.
- Token budget: 150k, counting context. Read v11 and the sources above, and do not re-read v1 to v10.

## 4. Acceptance criteria

As in the plan:
- every v11 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
- each status claim can be traced, or is marked **(unverified)**;
- the counts add up, and the register states whether any open item is above LOW;
- these pass: `python3 docs/tasks/validate-tasks.py`, `python3 -m unittest tests.functional.test_link_integrity` and `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
