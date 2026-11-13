# T810 — Dedicated runner tag on the tag-pipeline jobs

**ID:** T810
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-13
**Completed:** 2026-11-13
**Based on:**
- `docs/plans/plan-159-release-gate-runner-tag.md` (task T810; § Runner facts)
- The user's answer of 2026-11-13, verbatim: "start plan-159"
- `docs/artifacts/security-review-t741-gate-pin-v1.md` § 4 (SEC-T741-17); `.gitlab-ci.yml`; `tests/functional/test_ci_hash_pins.py`; `docs/wiki/mcp-pin-bump-checklist.md`

## 1. What and why

Move `release-docs-gate`, `main-develop-drift-gate` and `release` onto the user's dedicated runner (tag `release-gate`) and pin it, closing the remaining part of SEC-T741-17.

## 2. Output

Commits on `agent/devops-engineer/T810` in `/home/emage/Code/emage/worktrees/agent-devops-engineer-T810`: `.gitlab-ci.yml`, `tests/functional/test_ci_hash_pins.py`, `docs/wiki/mcp-pin-bump-checklist.md`, and any test that pins those files' text.

## 3. Constraints

- Conventional Commits, each ending with `Co-Authored-By: Claude <noreply@anthropic.com>`. Do not push or merge. Never create, push or delete a tag or release.
- Do not edit the ledger or any brief's Status line. No `docker` command. Do not touch any runner, host or project setting.
- Never open `tests/golden/held-out/`; recursive searches over `tests/` need `--exclude-dir=held-out`.
- Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, `.env*`, credential files, or the user's `.claude/settings*.json` and `.vscode/*.json`.
- Nothing under `implementation/knowledge/` changes unless needed; say so if it does.
- No full suite, no mutation tool; `timeout` on every test run. Token budget 60k.

## 4. Acceptance criteria

- The three jobs carry exactly `tags: ["release-gate"]`; no other job and not `default` names `release-gate`; `default.tags` stays `["docker"]`.
- The pins fail on: a tag job without the tag, with an extra tag, or a branch job with `release-gate`.
- GitLab CI lint of the changed file passes (`glab ci lint` or the project lint API, if reachable; otherwise say so).
- These pass: `tests.functional.test_ci_hash_pins`, any test pinning the checklist, `python3 docs/tasks/validate-tasks.py`, `timeout 300 python3 -m unittest tests.functional.test_link_integrity`.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
