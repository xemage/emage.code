# T697 — Tracked-debt register v3

**ID:** T697
**Owner:** tech-lead
**Status:** in_progress
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-10-31
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-31: T697 to T699)
- The user's approval of 2026-10-31: "1 2 go, refresh yes"
- `docs/artifacts/tracked-debt-register-v2.md` (T687, 323 ids)

## 1. What and why

Tracked-debt register v3, a delta on v2. v2 stays the record for every id that was `fixed` or `obsolete` there; v3 does not repeat them.

1. **v2 ids re-checked.** Every v2 id whose status was `open`, `tracked-LOW` or `accepted` gets its status now, with closing evidence (file and line, completed-task row or review artifact) or **(unverified)**.
2. **New ids**, one row each, from: `security-review-t665-token-handling-v2.md`, `-t677-function-size-refactor-v1.md`, `-t686-release-job-token-v1.md`, `-t688-job-trace-removal-v1.md`, `-t689-token-placement-v1.md`, `-t690-copilot-security-servers-v1.md`, `-t693-release-self-review-v1.md`, `-t694-cwso-secret-source-v1.md`, `-t695-cwso-ci-secret-compose-v1.md` and `-t696-cwso-deps-toolchain-v1.md`; the rulings of T691 and T692; the briefs `task-T689.md` (section 6, the live-check results of 2026-10-24) and `task-T693.md` to `task-T696.md`. The T695 and T696 reviews cover the CWSO repository; record their ids here with the repository named.
3. **The user's decisions since 2026-10-23**, with words and dates as recorded in the plan-123 addenda and the briefs: D-3 (full-disk encryption) rejected on 2026-10-24; decision "C" on 2026-10-31 (CWSO over plain HTTP on the LAN accepted as a risk; SSH tunnel and TLS proxy declined); the others recorded in the addenda of 2026-10-24 and 2026-10-31.
4. **Open items by theme** with the LOW policy of 2026-10-23 applied (MEDIUM and higher closed or accepted by the user; LOW stays as debt with an owner; no new task per round), the v9.0.0 release items (SEC-T662-01 among them), the user actions with no task, and the accepted risks (the user's words and dates).
5. **Summary counts** (ids carried from v2, new ids, status totals) and a method/limits section like v2's section 7.

## 2. Output

`docs/artifacts/tracked-debt-register-v3.md` (immutable artifact header, a `Based on:` line, metadata as in v2).

## 3. Constraints

- Work in your own worktree on branch `agent/tech-lead/T697`, created from `chore/T697-T699-debt-checkpoint-refresh`; one Conventional Commit (`docs(artifacts): ...`) ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Documentation artifact only: no code, test, knowledge or generated file changes.
- Never write a secret value, a token, a JWT or any part of one; refer to secrets by name only. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/` or any `.env*` or credential file; do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`. Never open `tests/golden/held-out/`; never write a held-out case id anywhere. Do not name internal LAN addresses; say "the CWSO server".
- Mark anything you did not verify **(unverified)**.
- Budget: about 100k tokens. Read v2 by section, not whole, and read only the review artifacts listed above.

## 4. Acceptance criteria

- `docs/artifacts/tracked-debt-register-v3.md` exists; every v2 id that was `open`, `tracked-LOW` or `accepted` is accounted for; every new id in the listed reviews has a row.
- Every status claim is traceable to a file and line, a row or an artifact, or marked (unverified); no credential-like value and no LAN address.
- `python3 docs/tasks/validate-tasks.py` and `python3 -m unittest tests.functional.test_link_integrity` pass, and `python3 -m unittest discover -s tests -p 'test_team_health*.py'` passes.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
