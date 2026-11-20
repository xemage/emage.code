# T827 — Tracked-debt register v17

**ID:** T827
**Owner:** tech-lead
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-14
**Completed:** 2026-11-14
**Based on:**
- `docs/plans/plan-162-tracked-debt-register-v17.md` (task T827; § Facts since v16)
- The user's answer of 2026-11-14, verbatim: "v17 go"
- `docs/artifacts/tracked-debt-register-v16.md`; plans 159 to 161; `docs/checkpoints/checkpoint-043-release-v11.0.0.md`; `docs/releases/v11.0.0.md`; the artifacts of T811, T812, T813, T814, T818, T819, T820 (and addendum), T821, T825

## 1. What and why

Write `docs/artifacts/tracked-debt-register-v17.md` as specified in plan-162 § Task Decomposition item 1.

## 2. Output

`docs/artifacts/tracked-debt-register-v17.md`, committed on `agent/tech-lead/T827` in `/home/emage/Code/emage/worktrees/agent-tech-lead-T827`. No other file changes.

## 3. Constraints

- Conventional Commits, each ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push, merge, tag or release.
- Do not edit the ledger, any brief's Status line or any plan. No `docker` command.
- Never open `tests/golden/held-out/`; recursive searches over `tests/` need `--exclude-dir=held-out`.
- Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, `.env*`, credential files, or the user's `.claude/settings*.json` and `.vscode/*.json`. Do not read the CWSO repository.
- No mutation and no full suite. `timeout` on any test run.
- Token budget: 80k, counting context. Read v16 and the sources above; do not re-read older registers except where v16 points to one.

## 4. Acceptance criteria

- Every v16 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row.
- Each status claim can be traced to a source, or is marked **(unverified)**.
- The counts add up, and the register states whether any open item is above LOW.
- These pass: `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
