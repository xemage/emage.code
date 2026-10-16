# Artifact: security-review-t612-altered-paths-selftest-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; static review, no execute tool). Recorded by the orchestrator from the reviewer's report.
- **Task**: T612 (plan-116). Reviewed commit `7dddc44`; the developer fixed every finding in one round (`40daf58`), which the orchestrator verified but the reviewer did not re-read.
- **Based on**: `security-review-t611-scanner-residuals-v1.md` (T611-2, T611-3), `poc-security-engineer-tool-scoping-v4.md` §12, `poc-security-engineer-tool-scoping-v5.md`.
- **Date**: 2026-10-09.
- **Orchestrator checks on `40daf58`** (scratch repos, git 2.43.0): files `cfg\xff.yaml` and `cfg\xfe.yaml` (invalid UTF-8) both show `cfg�.yaml` and are both marked `path_altered: true` in the `worktree` and `index` scopes; a valid file literally named `cfg�.yaml` and `plain.yaml` are not marked; scans complete with no errors. On `7dddc44` the two invalid-UTF-8 files were unmarked and collided (finding SEC-1 reproduced).

## Verdict: CONDITIONAL_PASS (condition met by the fix round)

0 critical, 0 high, 1 medium, 4 low. The self-test is fail-closed and adds no subprocess surface; the marker is derived only from the raw name; no Immutable Security Constraint is breached.

| ID | Grade | Concern | Disposition |
|---|---|---|---|
| SEC-1 | MEDIUM | The marker did not cover names that decode lossily (`errors="replace"`): two files with different invalid bytes showed the same text, both unmarked and flaggable; the agent text and contract falsely said an unmarked hit shows its real path. | Fixed in `40daf58`: `_decode_name` reports whether strict UTF-8 decoding failed, derived from the raw bytes; `add_hit` marks lossy names; a valid name with a literal U+FFFD is unmarked and shares the `hit_count` with a lossy name of the same text; contract v5 §2 and the agent sentence updated; tests for file collisions and ref/tag names. |
| SEC-2 | LOW | An altered hit with a `template-ref` label: the two agent files disagreed on whether it is unresolved. | Fixed: both files say it stays `template-ref` (the label is not a flag) but cannot be flagged; the orchestrator "every other hit" sentence excepts altered hits; pinned. |
| SEC-3 | LOW | The progression task for an altered-path hit was titled "awaiting user: placeholder flag". | Fixed: it awaits the rename or removal, owner = remediating agent; pinned. |
| SEC-4 | LOW | Test quality: the aggregate-deadline test was vacuous for the self-test; no ref/tag no-marker test; `via:log` assertion could pass vacuously. | Fixed: the spy asserts one `Deadline` object across all calls incl. the self-test; `_regex_selftest(..., Deadline(0))` with Popen forbidden; ref/tag test; non-empty assertion. |
| SEC-5 | LOW | `regex_unsupported` is a diagnosis, not proof. | Fixed: worded as "the compile call failed while a trivial pattern compiled (usually a low RE_DUP_MAX)"; a remedy line added to the blocker note. |

Verified without findings: marker never set on redacted names, `via:log` hits, `ref` fields or caller-supplied values; the self-test
(`git grep -q -E -e <largest pattern> <empty tree> --`) goes through `git_executor.run_git` with the scan's `Deadline`; a first-call
`git_failed` with a passing control call gives `regex_unsupported`, a failing control gives `git_failed`, `timeout`/`git_missing`
are unchanged, and every failure is `complete: false`, `hits: []`, `counts: {}`; `tracked_names` correctly skips it;
`RULES_VERSION` unchanged (`2026-10-09.5`); F-8, E1-b, E1-c and both tool lists unchanged; no matched text in results or logs.
Not independently verified by the reviewer: the tests, the gates, the 7560-character pattern length and the 0.25 s self-test cost.
Residuals that remain documented: R-1 (aperiodic-input cost, fails closed); the self-test compiles only the largest-repeat rule;
the `RE_DUP_MAX` values for musl and BSD were not exercised on such a host.
