# Artifact: security-review-t611-scanner-residuals-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Reviewer**: security-engineer (read-only; no execute tool; static review). Recorded by the orchestrator from the reviewer's report.
- **Task**: T611 (plan-115). Reviewed commit `ebf0ab6`; the developer then fixed the cheap items in one round (`c2ff9e7`), which the orchestrator verified but the reviewer did not re-read.
- **Based on**: `security-review-poc-security-audit-code-v2.md`, `security-review-t609-template-label-v1.md`, `poc-security-engineer-tool-scoping-v4.md`.
- **Date**: 2026-10-09.
- **Orchestrator checks on `c2ff9e7`** (scratch repos, git 2.43.0): `"password"*100000` completes in 0.7 s and `"eyJ"*266000` in 1.5 s (both previously ran to the 60 s deadline); label behaviour unchanged (template-ref, `<hunter2>`, bare `$NAME`, mixed line, trailing text); `SECRET_PROFILE=abcdefgh1234` reported, `SECRET_FILE=abcdefgh1234` not; a 70-character name before the keyword is still reported. The developer's split-token file-name test was not re-created by the orchestrator (the tracked-names scope reports only sensitive file names).

## Verdict: PASS

0 critical, 0 high, 0 medium, 5 low. SEV-1..SEV-6 and T609-10..T609-13 are implemented as the brief describes. No rule or label
condition is weakened; the new bounds only add documented blind spots (a name run over about 64 characters after the keyword,
a JWT header over 512 characters after `eyJ`); the unquoted-value change is a strict superset of v3 matches; the SEV-4
exclusion set shrinks, so it creates no false negative; every failure path ends in `complete: false` or no label.

| ID | Grade | Concern | Disposition |
|---|---|---|---|
| T611-1 | LOW | Redaction ran on the raw name, then `safe_name` stripped invisible characters, so `AKIA<ZWSP>XXXXXXXXXXXXXXXX` could be shown clean and rule-matching. | Fixed in `c2ff9e7`: every rule is tested on both the raw and the cleaned name before the cap; tests for file, tag and history ref names. |
| T611-2 | LOW | `safe_name` changes `path_or_redacted`, which flags are keyed on; an altered path never equals the real path, so a later change to that file does not void a flag; colliding names merge their `hit_count`. | Tracked (contract v4 §12): needs a v5 delta and agent text so an altered path cannot be flagged. |
| T611-3 | LOW | The new `{7,1024}`, `{1024}` and `{10,512}` repeats exceed `RE_DUP_MAX` 255 on musl and some BSD regex libraries; `git grep -E` would fail to compile. Fails closed (`git_failed`), an availability problem. | Tracked: add a startup self-test and state the regex-library requirement. |
| T611-4 | LOW | Test quality: literal invisible characters in the source, no ref/tag test, regex-size test measured Python `re`, name bound pinned loosely. | Fixed: escapes, tag test, docstring says proxy and limit tightened to 7600, bound pinned at 64/65 (quoted) and 65/66 (unquoted). |
| T611-5 | LOW | Documentation: 1025 not 1024; JWT limit is 512 characters after `eyJ`; a long-named real credential followed by a template-shaped assignment that ends the line yields only the template match, labelled non-blocking (a new, contrived downgrade path). | Fixed: numbers corrected; the contract, docstring and agent text state the label is for the visible match only and that text beyond the bounds is unjudged. |

Residual R-1 (reviewer, aperiodic input): with `eyJ` repeated inside the 512-character header window up to about 170 starts share
one payload, a multiplier on line length, not quadratic; fails closed at the deadline. Tracked in contract v4 §12.

Informational: `git_executor.py` keeps one `assert` that only narrows a type (the AST test covers `poc_scan.py` and
`poc_audit_server.py` only).
