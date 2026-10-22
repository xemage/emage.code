# Artifact: security-review-t665-token-handling-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell, so no test, generator or live run; files read at the worktree tip, vendor documentation fetched on 2026-10-22). Recorded by the orchestrator from the reviewer's two reports (first review, delta re-review).
- **Gate**: security. **Date**: 2026-10-22.
- **Target**: T665, branch `agent/devops-engineer/T665` (from develop `5dfd12fa`): the T664 token-scope decision (design option D, `docs/artifacts/gitlab-token-handling-design-v1.md`): token-file mode (`GITLAB_PERSONAL_ACCESS_TOKEN_FILE`), `GITLAB_PERMISSION_MODE=modify`, corrected scope/role documentation, the read-only `scripts/check-gitlab-token.py`, templated-value validation in `sync.mjs`. Reviewed tips: `a45d4215` + merge `492fa2d8` (first review), fix commit `717d8bf8` (delta), fix commit `8fcfb72c` (the four new LOW items, tests and mutation proofs by the developer; not re-read by the reviewer).
- **Based on**: `docs/tasks/task-T665.md`, `docs/artifacts/gitlab-token-handling-design-v1.md` (DEC-T664-1..6), `security-review-t660-*`.
- **Orchestrator checks**: the developer reports the full suite 1617 tests OK (skipped 23) and all gates at the final tip; no token was used and nothing was run against GitLab.

## First review: CONDITIONAL_PASS (0 critical, 0 high, 3 medium, 7 low)

The generator side is sound (validation before write, injection-safe replacers, no token value in any projection), the checker's token-leak, redirect, host-pin and https controls are real and mutation-proofed, the Gemini placeholder fix is justified by the vendor documentation. No Immutable Security Constraint is breached.

| Id | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T665-01 | MEDIUM | Residual of SEC-T660-01 after option D: an agent with a shell (six of seven GitLab roles hold `execute`) runs as the user and can read the token file or call the API directly; `modify` mode does not stop that; the tool lists are not enforced on Opencode and Gemini CLI | the residual the user re-accepted on 2026-10-16 ("Adopt D and re-accept the residual (Recommended)"); stays open and tracked; the three live checks are the user's; closure only by an isolated user, container or VM |
| SEC-T665-02 | MEDIUM | the checker printed `result: ok` although the role (the primary control) is not verified (the two endpoints report none) | fixed: `role: NOT checked ...` line and `result: ok (scope, expiry and owner only; the role was not verified)`, exit 0; a seen role above Developer warns; tests and mutation proofs; closed by the delta review |
| SEC-T665-03 | MEDIUM | plaintext token file at rest: no at-rest guidance (Immutable Constraint 6 judgement call) | fixed: the docs state that full-disk encryption is assumed, offer `$XDG_RUNTIME_DIR` (tmpfs) and keyring-fed placements with the same-user caveat, and that the harness stores nothing; closed. Position on Constraint 6 (orchestrator, for the user to confirm): not breached, because the harness stores nothing, the file is the user's own credential outside the repository, and the previous state (an `export` in a profile file) was strictly worse; it holds only through the stated full-disk-encryption assumption |
| SEC-T665-04 | LOW | token-file read: symlink, TOCTOU, owner | fixed: one `open` with `O_NOFOLLOW|O_NONBLOCK|O_CLOEXEC`, `fstat` regular file owned by euid, size cap; closed |
| SEC-T665-05 | LOW | uncaught exceptions: exit-code collision, one-character leak, argument echo | fixed: printable-ASCII token, BOM strip, catch-all exit 2, no echo; closed |
| SEC-T665-06 | LOW | file-creation snippet leaves `umask` set, keeps an old file's mode | fixed (subshell umask, `: > f; chmod 600`); closed |
| SEC-T665-07 | LOW | one shared token needs Developer for three roles; the scope table may understate Developer's reach | not fixed here: follow-up task T681 |
| SEC-T665-08 | LOW | `secret` advisory, `wrap` unrestricted in `validateSpec` | fixed (`secret` boolean, `wrap` one `{VAR}` and a charset); closed |
| SEC-T665-09 | LOW | Pi: documented diagnosis unverified | wording fixed (what is source-read on Pi main, commit 698a2d2, vs unverified); the Pi optional-variable gap itself is the follow-up task T680 |
| SEC-T665-10 | LOW | test weaknesses and gaps | fixed; closed |

## Delta re-review: CONDITIONAL_PASS

Findings -02..-06, -08..-10 closed; -01 and -07 open as intended and not overstated in the docs. Four new LOW items, all fixed in `8fcfb72c`:

| Id | Grade | Finding | Disposition |
|---|---|---|---|
| T665-LOW-1 | LOW | `Reporter.clean` strips only C0 controls (C1, bidi overrides, U+2028/2029 reach the terminal) | fixed: every non-printable character becomes `?` after redaction |
| T665-LOW-2 | LOW | the output section sits outside the `try`: an uncaught exception there exits 1 (the "warnings" code) | fixed: all of `_run` is guarded, exit 2 |
| T665-LOW-3 | LOW | "nothing is written to disk" overstated for tmpfs | fixed (swap and lingering stated) |
| T665-LOW-4 | LOW | scope guidance contradicted the checker (`read_user`) | fixed: `ACCEPTED_SCOPES` is `{api, read_api}`; a test ties the docs to the constant |

Not graded (INFO): `O_NOFOLLOW` covers only the last path component and is a no-op where the platform lacks it; Python `strip()` differs from the server's `trim()` at a few edge characters (fails closed at GitLab); no `O_NOCTTY`.

## Open and unverified

- Live behaviour: nothing was run against a client or GitLab. The three live checks (fine-grained token against the 20 + 24 qa-engineer and scrum-master tools; Claude Code posture with `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`; the `${VAR:-}` empty default) need a throwaway token and a scratch project from the user; the docs label the claims "unverified until run".
- The Gemini, Pi and Cline findings come from the vendors' main branches, not from installed releases.
- Whether `/personal_access_tokens/self` or `/user` ever reports a role is unverified; the checker handles both outcomes.
- The reviewer's supplied diff did not isolate the fix commit; the delta was assessed from the final files, and other files changed in `717d8bf8` (for example wiki sections) were not all read. The orchestrator's gates cover the generated files.
