# Artifact: security-review-t609-template-label-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no execute tool; read the code, ran nothing). Recorded by the orchestrator from the reviewer's two reports.
- **Task**: T609 (plan-114): scanner skip removal and the `template-ref` label. Round 1 on commit `a4c08b5`, re-check on the amended commit `4689cf4` (later rebased onto develop unchanged in content).
- **Based on**: `placeholder-flag-ruling-v3.md`, `security-review-placeholder-flag-ruling-v3.md`, `security-review-t608-placeholder-flag-text-v1.md`, `poc-security-engineer-tool-scoping-v3.md`.
- **Date**: 2026-10-09.
- **Orchestrator probes** (scratch repos, git 2.43.0): on `a4c08b5`, `password: <set-me> hunter2hunter2xx`, `password = "<set-me>" "realvalue1xyz"`, `PASSWORD="<set-me>"realtail1xyz` and `password = "<set-me>",` were all labelled `template-ref` (finding T609-1 reproduced). On `4689cf4` all four are unlabelled, and trailing whitespace alone still labels. Mixed lines, `<hunter2>`, bare `$NAME` and URL cases behave as designed.

## Round 1 (a4c08b5): CONDITIONAL_PASS

0 critical, 0 high, 1 medium, 8 low. No Immutable Security Constraint breached; the label only lowers a hit that was previously not reported at all.

| ID | Grade | Concern | Outcome |
|---|---|---|---|
| T609-1 | MEDIUM | The label judged only the matched text, not the rest of the value or line. | Fixed in `4689cf4`: a second end-anchored `git grep` per label rule (same executor, same deadline, fail closed); a line is labelled only if it ends after the shape (optional spaces, tabs, CR). |
| T609-2 | LOW | Matched text was copied for every rule and scope. | Fixed: `keep_text` only for label rules in `worktree`/`index` scope; docs corrected. |
| T609-3 | LOW | `HIT_KEYS` enforced only by tests. | Fixed: runtime enforcement in `add_hit`; tests extended. |
| T609-4 | LOW | Test gaps (trailing text, logging, invalid UTF-8, full-width look-alikes, tabs, regex pins). | Fixed. |
| T609-5 | LOW | More than 500 template-ref lines always truncate; URL passwords unlabelled. | Recorded as a residual in contract v3 §5. |
| T609-6 | LOW | `hit_count` ambiguity. | Fixed in agent text; pinned. |
| T609-7 | LOW | Documentation drift in L-3 and E-P2. | Fixed. |
| T609-8 | LOW | Severity floor for a known-real template-ref value. | Fixed in the template-ref bullet. |
| T609-9 | LOW | `{{ password }}` is labelled; shape is derived information. | Recorded in contract v3 §5. |

## Round 2 re-check (4689cf4): PASS

T609-1 closed with a fail-closed design: every error, timeout, truncation and parse failure yields no label; no new subprocess
surface (the call goes through `run_git`/`git_argv`, the AST test still holds); the anchored check only removes labels and
never changes the hit list, `complete` or `truncated`. T609-2..T609-9 applied accurately. F-8, E1-b, E1-c and both tool
lists unchanged. 0 critical, 0 high, 0 medium, 4 low.

| ID | Grade | Concern | Disposition |
|---|---|---|---|
| T609-10 | LOW | With several matches on one line only the last is anchored; text between two shape matches that no rule matches, and line continuation (YAML plain scalar, trailing backslash), are not judged. | Tracked debt; add the limits to contract §5 and the docstring; optionally label only single-match lines. |
| T609-11 | LOW | The tool description names only `credential-assignment`; `_anchored`'s `assert` vanishes under `python -O`; `add_hit` allow-lists keys, not values. | Tracked debt: align the description, replace the assert with an explicit raise, validate `value_shape`/`template_shape` in `add_hit`. |
| T609-12 | LOW | A failed anchored check leaves `complete: true` with fewer labels and no signal (safe direction); concurrent edits between the two greps could in theory shift a line. | Accepted; state in contract §5 that the scan assumes a quiescent tree. |
| T609-13 | LOW | "A URL whose scheme is 32 or more characters long" is not a blind spot (the pattern is unanchored on the left); only an upper-case scheme is. | Tracked debt: correct the wording at the next text revision. |

Owner for T609-10..T609-13: backend-developer, next sprint; not scheduled (T605 is the related unscheduled follow-up, which can absorb them).
