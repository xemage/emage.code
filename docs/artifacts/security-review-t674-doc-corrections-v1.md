# Artifact: security-review-t674-doc-corrections-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no shell, so no gate or test run; the `grep_content` tool failed, files read directly; vendor pages fetched on 2026-10-22). Recorded by the orchestrator from the reviewer's two reports (first read, delta re-read).
- **Gate**: security. **Date**: 2026-10-22.
- **Target**: T674 (documentation corrections, tracked debt), branch `agent/technical-writer/T674` (from develop `84312bb0`): live docs and one knowledge source (`release-workflow` skill template title), the new `docs/wiki/severity-and-grade-scales.md`, the operator-controls table, the Developer-level exposure statement and the Reporter profile (T681 option A).
- **Based on**: `docs/tasks/task-T674.md`, `docs/artifacts/tracked-debt-register-v1.md` (rows with disposition T674), `docs/artifacts/gitlab-per-role-token-design-v1.md`, `security-review-t665-token-handling-v1.md`, `security-review-t672-installer-robustness-v1.md`.
- **Orchestrator checks**: regenerated mirrors and registry; the root drift stays at 88 declared paths (the release-workflow skill projections were already declared by T667); all gates and the full suite on the final tree are recorded in the task outcome.

## Verdict: CONDITIONAL_PASS (first read), CONDITIONAL_PASS (delta): 0 critical, 0 high, 0 medium, 9 LOW (8 resolved, 1 handled by merge order)

The changed security statements are accurate against code and vendor sources and label unverified items honestly (operator controls, Pi/Opencode/Gemini, Supabase, submodules, Developer-token reach); the three artifact corrections state true things and leave the immutable artifacts untouched; the severity page does not lower any SECURITY:HIGH or SECURITY:CRITICAL finding; no secret or real PII. No Immutable Security Constraint is breached.

| Id | Grade | Finding | Disposition |
|---|---|---|---|
| SEC-T674-01 | LOW | severity page rows S7/S4 and S6/S7 could be read without the security carve-out | fixed (both parentheticals); resolved |
| SEC-T674-02 | LOW | the GitLab README version basis not fully pinned to 2.2.5 | fixed (only the five points confirmed at 2.2.5 are stated as such; the rest "README on main; not matched to 2.2.5, unverified"); resolved |
| SEC-T674-03 | LOW | "a plugin" named as an Opencode override source without a source | fixed (removed or marked unverified); resolved |
| SEC-T674-04 | LOW | dangling references and an awkward branch-protection pairing | fixed; resolved |
| SEC-T674-05 | LOW | "all six do today" for the Playwright notice | fixed ("names the `playwright` server (the installer tests that per platform)"); resolved |
| SEC-T674-06 | LOW | a repo-local git config could change the submodule statement | fixed ("with default git configuration"); resolved |
| SEC-T674-07 | LOW | the wiki stated the Reporter-profile failure as fact without the label | fixed by the orchestrator ("is expected to fail ... unverified, not run, and the agent files are unchanged for this profile"); resolved |
| SEC-T674-08 | LOW | two minor inconsistencies in the role statements (CI lint tools not in the table; branch creation) | fixed by the orchestrator; resolved |
| SEC-T674-09 | LOW | merge-order dependency on the T681 artifact and the decision record | handled: MR !605 (the artifact, the decision record in the plan addendum and the completed row, T683) merges before T674 |

Condition C-1 (the Reporter profile accuracy criteria a to f) was met in the delta read.

## Open and unverified

- Vendor claims (operator controls, Gemini precedence, Supabase, Pi) rest on fetch summaries, not runs; the permission rows of the GitLab permissions page were flattened by a fetch tool and two rows are inferred.
- The reviewer did not re-read the wiki's own long GitLab-grants paragraph after the edits, and the user's quoted decisions are traced to the plan addendum, not re-verified by the reviewer.
- Register rows not closed by T674: SEC-014 (`git tag -v` documentation: the contribution guide uses `git tag -a`, so documenting `git tag -v` needs a decision to sign tags; `--require-hashes` stays with T676), SEC-T674-06's optional code hardening (`-c submodule.recurse=false` in `git_executor.HARDENING`) is a separate code task.
