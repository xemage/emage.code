# T695 — CWSO repository: dead JWT value out of CI and docs; restart policy and Origin allow-list

**ID:** T695
**Owner:** devops-engineer
**Status:** pending
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-10-31
**Completed:** —
**Based on:**
- `docs/plans/plan-123-post-release-follow-ups.md` (Addendum of 2026-10-31: T695)
- The user's decision of 2026-10-31: "T694 go"
- Immutable Security Constraint 1 (no secrets in source control); `implementation/SECURITY.md`

## 1. What and why

The repository is CWSO (`https://gitlab.com/em-age/emage.code.cwso`, local clone `/home/emage/Code/emage/CWSO`, target branch `develop`). The local clone has uncommitted generated files that are not part of this task, so work in a separate worktree based on `origin/develop`.

1. **Dead secret value.** The rotated JWT secret is committed in `.gitlab-ci.yml`, `docs/tasks/task-T192.md`, `docs/archive/tasks/task-T049.md` and `docs/archive/cursor-chats/cursor_gitlab_runner_pipeline_configura.md`. In CI, generate a random secret per job at run time (for example `openssl rand -hex 32` written to the file or variable the job needs), or use a masked CI variable only if a job really needs a fixed value. Redact the docs to `<redacted 2026-10-31, rotated>`. Find occurrences with the pattern-file procedure of `docs/tasks/task-T694.md` section 1.2 (the dead value from `git show origin/develop:.gitlab-ci.yml`, kept in `/dev/shm` only) and report file names only.
2. **Server fixes into the repository.** In `deploy/docker-compose.yml`:
   - add `restart: unless-stopped` to `orchestrator`, `git-shadow` and `merge-engine`. Not to the one-shot `workspace-check` or `jwt-secret-fix`; check `rollout`.
   - make `CWSO_ALLOWED_ORIGINS` configurable: `${CWSO_ALLOWED_ORIGINS:-<today's list>}`. Today's list stays the default, so no LAN address is hard-coded. Document how a deployment adds its own address, for example `http://10.10.160.13` and `http://10.10.160.13:8080`.

   The server at 10.10.160.13 currently runs with a local `deploy/docker-compose.override.yml` that does exactly this. After the merge, the user replaces the override with the variable.
3. **Tests and CI:** the CWSO pipeline stays green, and any compose or CI tests in the repository are updated.

## 2. Output

As stated in section 1, as one commit on a branch `agent/devops-engineer/T695` in the CWSO repository, with no push.

## 3. Constraints

- Work only in your own worktree of the CWSO repository, based on `origin/develop`. Make one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push or merge, and never create a tag or release.
- **Never print, log or commit a secret value, dead or live.** Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/` or any `.env*` file. The only permitted access to the dead value is the pattern-file procedure above.
- Run the CWSO repository's own checks, as its `AGENTS.md`/CI defines them (Go build and tests for touched packages, `docker compose config` for the compose file). Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

- The dead value occurs in no tracked file of the CWSO repository; the orchestrator verifies this independently.
- `docker compose -f deploy/docker-compose.yml config` succeeds.
- The CWSO pipeline is green after the push by the orchestrator.
- A Security Engineer review follows.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
