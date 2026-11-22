# Security Review: T911 batch X round 2 (plan-201, SEC-T909-01 and SEC-T909-02 fix)

Based on: docs/plans/plan-201-batch-x-sec-t909.md; docs/artifacts/security-review-t908-batch-x-v1.md (rows SEC-T909-01, SEC-T909-02); diff of commit 6591811d on agent/devops-engineer/T911 (scratchpad t911.diff); the worktree file tests/functional/test_ci_hash_pins.py (`ca_job_pairing_problems` / `apk_adds`, lines 1469-1518, and `unwrapped`); .gitlab-ci.yml (ca-chain-check-python lines 169-187, main-develop-drift-gate lines 308-333).
Reviewer: security-engineer, read-only. Nothing was executed (no shell). Statements marked \"(reasoned, not run)\" are read from the code; the engineer's run results (15 new subtests, 142 tests OK, each new refusal case accepted on the old code) were not re-run by me. The full suite and the pipeline are outside this review.
Scope: tests/functional/test_ci_hash_pins.py only. The diff touches that one file; no job, digest or pin changed (confirmed from the diff).

## Per-id status

| Id | Status | Basis |
|----|--------|-------|
| SEC-T909-01 (quote/escape split, variable program, after_script) | Partly fixed | Closed (reasoned, not run): `ap\"\"k add x` and `a\\pk add x` (the new gate also tests `\"apk\" in bare`, the line with quotes and backslashes removed, and the line then fails the literal `apk\\s+add` match); `$PM add x`, `PM=apk; $PM add x` and `true && ${PM} add x` (`var_cmd` at a command position); `after_script` is scanned in both jobs. Forms that still escape are in SEC-T912-01 and SEC-T912-03. |
| SEC-T909-02 (`'git>=2.54'` refused) | Fixed | `<` and `>` are removed from the per-word set and tested only on `unquoted` (the line with single- then double-quoted regions blanked). `'git>=2.54'` becomes `''` and is accepted; `apk add x > /tmp/y` and `< /tmp/y` keep the operator and are refused. The message and docstring now name the refused characters. One flaw in the quote stripping is SEC-T912-02. |

## Answers to the review points

1. Closure of SEC-T909-01. The three named forms are closed. Real lines pass (reasoned, not run): the standard add line matches `literal`, has no `$` or backtick at a command position, and its words are clean; the wrapper line passes through the optional `run-allowlisted.py ... -- ` prefix; none of the other lines contains `apk`, and no other line has `$` or a backtick at a command position. Forms that still escape:
 - `$PM` not at the start of the line or just after `; & | (`: `env $PM add x`, `X=1 $PM add x`, `then $PM add x`, `eval $X`, `sudo $PM add x`, `xargs $PM`. No `apk` token is in the line and `var_cmd` does not match.
 - A multi-line YAML block item (`|`) whose later line starts with `$PM`: `var_cmd` has no `re.M`, so `^` matches only the start of the whole string and the newline is not a separator. A block that contains `apk` is still refused (the newline in `unquoted`).
 - A command built without the text `apk`: `eval \"$(printf 'a%sk' p) add x\"` and similar. Not enumerable with a denylist.
 - `after_script`, `before_script` or `script` given as a plain string or as a nested list (valid in GitLab): see SEC-T912-01.
 - `extends:`, `default:` or `!reference`: the function reads only the job's own three fields from the loaded YAML. An `after_script` inherited from `default:` or an extended template (a job with no own `after_script` inherits it) is not scanned. A template `before_script` is replaced by the job's own list, so it does not run, which is why that one is not a gap. `!reference` in a list makes `yaml.safe_load` raise on the unknown tag if the loader is stock (reasoned, not run), so that fails loudly, not open.
 - `exec apk add`, `xargs apk add`, `eval 'apk add x'`, here-docs and `sh -c` payloads that contain the text `apk` are refused (stray).
2. `'git>=2.54'` is accepted while an unquoted redirect is refused: confirmed (reasoned, not run). The quote stripping is wrong for mismatched or nested quotes, because single-quoted regions are blanked first: `apk add \"a'b\" > /tmp/y 'c'` has its `> /tmp/y ` hidden inside a fake `'...'` region, and shlex gives `>` as its own word, which the per-word set no longer tests. See SEC-T912-02. The effect is limited to a redirect on an otherwise literal add line; `;`, `&`, `|`, `$`, backtick and parentheses are still tested on shlex words, which parse the quotes correctly.
3. False positives. Present edits pass. Plausible refusals that may annoy a maintainer: any line in the two jobs whose text contains the substring `apk` (a path such as `/tmp/apkcache`, a file `x.apk`), and any unrelated line that begins with a variable or has one right after `;`, `&&`, `||`, `|` or `(` (for example `- $SOME_TOOL --check`). The new message says \"runs a command through a variable\" and lists the refused characters, so the reason is readable. See SEC-T912-04. The ordinary ways to write a package constraint are all accepted: `'git>=2.54'`, `\"git>=2.54\"`, `'git~=2.54'`.
4. No existing assertion weakened or dropped. The diff only adds subtests and one test method. Every old `single` condition is kept; only `<` and `>` moved from the per-word set to the unquoted-text test (deliberate, SEC-T909-02), and a backslash and a newline in the unquoted text are newly refused. The old `not a or a != b` condition is unchanged. The problem-message text changed; the engineer's run shows no test depends on the old wording.
5. Nothing but the one test file changed: confirmed from the diff; no job, digest or pin.

## New findings

| Id | Severity | OWASP | Location | Finding | Remediation |
|----|----------|-------|----------|---------|-------------|
| SEC-T912-01 | SECURITY:LOW | A08 Data Integrity Failures | `apk_adds`, lines 1489-1492 | `for line in job.get(field, [])` with `if not isinstance(line, str): continue`. GitLab accepts `script`, `before_script` and `after_script` as a single string or as nested lists. A string iterates character by character (no character matches); a nested list is skipped. Either way the install is not scanned. This now also covers the newly scanned `after_script`. No current exposure: both jobs use flat lists. | Normalise first: a `str` becomes `[str]`; a list is flattened; any other shape is returned as a stray. `value = job.get(field, []); items = [value] if isinstance(value, str) else value`; then `strays.append(repr(item))` for any non-str item instead of `continue`. Add a case `after_script: \"apk add x\"` and a nested-list case. |
| SEC-T912-02 | SECURITY:LOW | A08 | `unquoted`, line 1502 | Single-quoted regions are blanked before double-quoted ones, so a stray apostrophe inside a double-quoted word pairs with a later one and hides what is between them: `apk add \"a'b\" > /tmp/y 'c'` loses its `>`. Since `<` and `>` are no longer tested per word, the redirect is accepted (reasoned, not run). Effect limited to a redirect or here-string on a literal add line. | Blank quoted regions in one left-to-right pass: `re.sub(r\"'[^']*'\\|\\\"[^\\\"]*\\\"\", \"''\", line)` (alternation, first opener wins), or use `shlex.shlex(line, posix=True, punctuation_chars=True)` and refuse any punctuation token. Add the case above. |
| SEC-T912-03 | SECURITY:LOW | A08 | `var_cmd`, line 1494 | The variable-program test is a denylist for a command position only after `^`, `;`, `&`, `\\|`, `(`. It misses `env $PM add x`, `X=1 $PM add x`, `then $PM add x`, `eval $X`, a later line of a multi-line block (no `re.M`), and any program built without the text `apk`. Scanning also reads only the job's own three fields, not an `after_script` inherited through `default:` or `extends:`. No current exposure. | Prefer a positive rule to a denylist: in these two jobs refuse any `before_script` or `after_script` line that contains `$`, a backtick or `eval` outside the known set of lines (an exact-line allowlist, with the standard add line pinned to its full text). Add `re.M` and `then\\|do\\|else\\|eval\\|exec\\|env\\|sudo\\|xargs` to the command-position test if a denylist is kept. Resolve `extends:` and `default:` for `after_script` or add a case that the jobs inherit none. |
| SEC-T912-04 | SECURITY:LOW | A08 (maintainability) | `apk_adds` line 1495 and `var_cmd` | Over-refusal: any line containing the substring `apk`, or any line that starts with or chains into a variable, is a stray with a message that names the add-line check. Plausible innocent edits can trip it and push a maintainer to loosen the rule. | Keep the new message; add a docstring sentence and a short comment in the checklist naming these two refusals, and a test that documents each (`mkdir /tmp/apkcache` refused, with its reason). Do not loosen the code. |

## Verdict

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 4 new (SEC-T912-01 to -04); SEC-T909-01 partly fixed (residue = SEC-T912-01, -03), SEC-T909-02 fixed | 1 (SEC-T909-02) | 4 new plus the residue of SEC-T909-01 (tracked as technical debt) |

### Justification
Every named form of SEC-T909-01 (quote split, escape split, variable program, after_script) is refused, and `'git>=2.54'` is accepted while an unquoted redirect is refused. The real jobs pass, no assertion is weakened, and only the one test file changed. The remaining findings are LOW, have no current exposure (no job uses these forms and both jobs are equal) and are tracked as technical debt. No Immutable Security Constraint is breached and no required control is weakened.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01-A05, A07, A09, A10 | No (not in scope of this diff) | 0 |
| A06: Vulnerable Components | No | 0 |
| A08: Data Integrity Failures | Yes | 4 (LOW) |

## What stays open
- SEC-T912-01 to -04 (LOW, new); SEC-T909-01 residue as above.
- SEC-T881-02 and SEC-T756-02: out of scope, unchanged.
- Pending outside my review: the full clean-worktree suite, the pipeline and the merge.

## Orchestrator addendum (2026-11-22)

- Verdict stands: PASS. The four new ids are LOW and are tracked as debt under the user's LOW policy; they go to register v35 in batch X (SEC-T912-01 to -04). **SEC-T909-02 is fixed. SEC-T909-01 is partly fixed:** its named forms are closed, and its residue is SEC-T912-01 and SEC-T912-03 (the register counts the residue once, as in the v32 and v33 precedents, so v35 rules whether SEC-T909-01 is fixed with those two as its residue).
- **The engineer's report was wrong on one point:** it said a two-space or tab form `apk  add` is now refused. The reviewer read the code: the `literal` regex uses `apk\s+add`, so those forms are still accepted as a plain add. No behaviour change there.
- **A design note for a later round (not done here):** the check is a denylist, and each round closes the forms the last review named while the reviewer names the next ones. SEC-T912-03 proposes a positive rule instead (an exact-line allowlist, with the standard add line pinned to its full text). That would end the cycle; it is a larger change and is left to the user's word.
- The engineer ran the old-versus-new check on a copy; I read the diff, ran the two test files (142 tests OK) and the ledger and link-integrity gates. The full suite on the pushed head is recorded in the merge request.
