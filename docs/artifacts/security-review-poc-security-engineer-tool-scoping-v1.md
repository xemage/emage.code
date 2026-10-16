# Artifact: security-review-poc-security-engineer-tool-scoping-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only). The orchestrator recorded this from the reviewer's report, because the
  agent has no write tool.
- **Task**: T602 (plan-113). A security review of `poc-security-engineer-tool-scoping-v1.md`: the options (§6), the
  proposed contract of two new fixed-argv tools (§7) and the held edits (§8).
- **Date**: 2026-10-09
- **Based on**: `poc-security-engineer-tool-scoping-v1.md`, `poc-security-engineer.md`, `poc-orchestrator.md`,
  `security-guidelines.md`, `security-engineer-audit-server-design-v1.md`, and `implementation/runtime/security/`.

## Verdict

**CONDITIONAL_PASS.** 0 critical, 0 high, 8 medium, 4 low. The direction (Option 1) is sound. The eight medium
findings are contract gaps that would have become HIGH if implemented as §7 then read. All were adopted in
`poc-security-engineer-tool-scoping-v2.md`.

## Findings

| ID | Severity | Concerns | Disposition |
|---|---|---|---|
| F-1 | `SECURITY:MEDIUM` (A03/A05) | Git reads the scanned repository's own config, and other agents can write an agent worktree's `.git/config`. A planted `core.fsmonitor` or textconv command would run when the scanner runs, recreating the execution capability Option 1 removes. | Adopted as a contract field: hardened git argv, explicit subprocess env, and a planting test. The orchestrator reproduced the risk (a planted `core.fsmonitor` command runs under a plain `git grep` and not under the hardened one). |
| F-2 | MEDIUM (A04) | A subdirectory of a work tree passes "must be a git work tree" and would scan only that subtree, which is a false clean result. | `root_dir` must equal `git rev-parse --show-toplevel`. |
| F-3 | MEDIUM (A02/A09) | Paths, ref names and tag names can carry the secret, and splitting git output on `:` is unsafe. | `git grep -z`; redact via the rule table; `--format=%H` only; no stderr or argv returned. |
| F-4 | MEDIUM (A04) | A stale "not pushed" is the dangerous direction. | `pushed` is `true` or `"unknown"`, never `false`, plus `last_fetch_time`. |
| F-5 | MEDIUM (A05) | E1-c named an orchestrator confirmation that no document writes. | Resolved by rewording E1-c so it names no actor. |
| F-6 | MEDIUM (A02) | `grep_content` takes a caller pattern and returns matched text, so the "redaction is met by design" claim overclaimed. | The user chose to keep it and record the residual; the claim is narrowed. |
| F-7 | MEDIUM (A04) | Unbounded scans (memory, aggregate time, ref count). | Aggregate deadline, caps, bounded streaming, `truncated` and `complete`. |
| F-8 | MEDIUM (A04) | An incomplete scan must not read as clean. | `poc-security-engineer.md:25` gains the fail-closed sentence. |
| F-9 to F-12 | `SECURITY:LOW` | `allowed_root`; `rev_range` scope; the history scan's limits; the `read` plus `web` exfiltration path. | F-9 to F-11 adopted as contract fields; F-12 recorded as a residual. |

## Rollout requirements (adopted)

- Register the server in every platform's MCP config, with a start-up smoke test.
- The `.claude/settings.json` permission is a **documented manual step**: that file is client-owned and is never
  auto-edited.
- Add a test that `poc-security-engineer` has neither `execute` nor `Bash`.
- The grant swap is the last step, so no merge leaves the agent without a scan capability.

## Orchestrator verification of the reviewer's technical claims

Run in a scratch repository: a planted `core.fsmonitor` command runs under a plain `git grep` and does not under
`git -c core.fsmonitor=false`; with two `-G` options the last one wins; `git rev-parse --show-toplevel` from a
subdirectory returns the repository top; `git for-each-ref --contains` lists the containing refs; and with
`git grep -z -n` the line number is also NUL-terminated (`path NUL line NUL text`). The implementation spec must
use that layout.
