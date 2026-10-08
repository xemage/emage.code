# Artifact: security-review-poc-security-audit-code-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; read the code, ran nothing). The orchestrator recorded this from the
  reviewer's reports, because the agent has no write tool.
- **Task**: T603 (plan-113). A code review of the `poc-security-audit` server (`git_executor.py`, `poc_scan.py`,
  `poc_audit_server.py`, `tests/functional/test_poc_audit_server.py`) and the grant swap in `poc-security-engineer.md`.
- **Date**: 2026-10-09
- **Based on**: `poc-security-engineer-tool-scoping-v2.md` (the contract) and
  `security-review-poc-security-engineer-tool-scoping-v1.md` (findings F-1..F-12).

## Round 1, commit `19ed598`: FAIL

One HIGH, three MEDIUM and eight LOW findings (P-1..P-13). The orchestrator tested the claims in scratch
repositories on git 2.43.0 before returning the work:

| Finding | Orchestrator's result |
|---|---|
| P-1 (HIGH): `git log` runs a repo-planted `gpg.program` | **Did not reproduce.** The planted program did not run under `log -G … --format=%H`. An explicit `--show-signature` control did. The fix was adopted anyway as defence in depth. |
| P-2 (MEDIUM): `color.ui=always` breaks the parser, giving `complete: true` with zero hits | **Reproduced.** |
| P-3 (MEDIUM): a committed `.gitattributes` with `* -diff` hides secrets from every scan | **Reproduced** for the worktree, tree and history scans. |
| P-4 (MEDIUM): rule-table gaps | Accepted: new rules were added. |

The work went back to the Backend Developer as retry 1 of 2.

## Round 2, commit `82960df`: CONDITIONAL_PASS

0 critical, 0 high, 1 medium (a residual), 8 low.

- **All earlier findings are closed.**
- **P-1 is re-graded from HIGH to LOW.** The reviewer accepted the orchestrator's reproduction over its own reading of
  the config surface. The planted-gpg test is a regression guard, not proof that a fix was needed. **No "fixed a HIGH"
  claim belongs in release notes.**
- **The developer's `-a` / `--text` choice is better than the reviewer's `-I` suggestion.** It also covers
  `.git/info/attributes`, which `--attr-source` does not. The kill logic is sound. The new tests are not vacuous.
- The orchestrator's end-to-end probes agree: a planted fsmonitor, gpg program, forced colour, `* -diff`,
  `* binary` and `.git/info/attributes` neither run a command nor hide a secret. Subdirectory roots are rejected,
  `pushed` is `"unknown"`, and no secret value appears in any output.

### Condition C-1 (SECURITY:MEDIUM, residual R-7): the unquoted `KEY=value` rule

The rule was deliberately left out, because it matches things like `TOKEN_TTL=3600`. The gap is the most common PoC
secret shape (`.env`, docker-compose `password: hunter2`). A clean `worktree` scan therefore says nothing about an
untracked `.env`. The reviewer requires a plan with a concrete owner and deadline before merge.

**Remediation plan (recorded 2026-10-09):**
- **owner:** `@orchestrator`
- **fix:** add an unquoted-assignment rule (`KEY=value`, `key: value`), subject to the user's decision on its
  false-positive trade-off, and add a name-only check of untracked `.env*`-style files in the `worktree` scope. Bump
  `RULES_VERSION`.
- **deadline:** task **T604**, which must be done no later than the production handoff of any PoC that relies on this
  scanner.

`poc-security-engineer-tool-scoping-v2.md` is immutable, so this record and `plan-113` §5 carry the plan instead.

### LOW findings, tracked in T604

| ID | Concerns |
|---|---|
| L-1 | `git grep -a` prints whole lines, so a multi-megabyte single-line file hits the byte cap and fails closed. Fix: `-o`, with a per-rule `(path, line)` dedupe. |
| L-2 | `resolve_root` maps a `git_failed` (an old git, SHA-256 repos) to `not_a_toplevel`, so the reviewer is told the wrong thing. |
| L-3 | The placeholder heuristic skips real secrets starting with `$`, `<`, `{` or a space. A trade-off to decide. |
| L-4 | `git log -G` does not diff merge commits. Document as a limit. |
| L-5 | `rev_range` over 200 commits is flagged `truncated` even though the `log` pass covers it. Over-conservative. |
| L-6 | A `.git` file can point to a gitdir outside `allowed_root`. Document in R-6. |
| L-7 | The process-death test treats a zombie as alive (`os.kill(pid, 0)`), so it can flake in a container whose pid 1 does not reap. Fix: also read `/proc/<pid>/stat` and treat state `Z` as dead. |
| L-8 | `grep_content` stays granted. The "never reproduce the value" duty is prompt-level only. Already an accepted residual. |

Also for the rules revision: npm (`npm_…`), SendGrid (`SG.…`) and JWT (`eyJ…`) formats.
