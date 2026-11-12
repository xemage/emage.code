# T797 — Fix SEC-T796-01: redact credentials in `RemoteResolutionError` messages

**ID:** T797
**Owner:** backend-developer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** T795
**Affects:** —
**Created:** 2026-11-12
**Completed:** 2026-11-12
**Based on:**
- `docs/plans/plan-153-context-retriever-low-residue.md` (fix task after the T796 FAIL)
- The user's instruction of 2026-11-12, verbatim: "O go"
- `docs/artifacts/security-review-t796-context-retriever-v1.md` (SEC-T796-01, blocking)

## 1. What and why

T796 failed T795 on SEC-T796-01: the `RemoteResolutionError` messages of `normalize_remote_to_project_id` (`implementation/runtime/memory/context_retriever.py:102`, `:106`, `:109` at `15e427ba`) repeat the git remote URL with any `user:token@` part (`security-guidelines.md` § Logging). The orchestrator routes it to a fix rather than a ruling. Redact the userinfo (or leave the URL out) in every message that carries a remote URL, and test that a secret in the userinfo appears in no message.

## 2. Output

Commits on `agent/backend-developer/T795` (the same worktree), and a report: changes with file:line, tests, every message site found, gate and suite results.

## 3. Constraints

As plan-153 § Constraints. `scope_filter.py` does not change.

## 4. Acceptance criteria

- No `RemoteResolutionError` message carries the userinfo of the remote URL; tests with a negative case (normal remotes normalise as before).
- `sync.mjs --check`, `generate-registry.py --check` and the full suite pass.
- T796's re-review of the fix passes.

## Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
