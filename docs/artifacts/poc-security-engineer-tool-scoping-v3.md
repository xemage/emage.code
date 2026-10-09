# Artifact: poc-security-engineer-tool-scoping-v3.md

> Immutable once produced; revisions bump `<N>`. **Amends `poc-security-engineer-tool-scoping-v2.md`**, which stays unchanged
> as the historical record. Where they differ, v3 governs; everything v2 says and v3 does not mention is unchanged (server,
> two tools, argv, environment, root check, caps, redaction, `ref_containment`).

## Metadata

- **Producer agent**: backend-developer
- **Task**: T609 (plan-114), implementing Question 2 Option A
- **Created**: 2026-10-09
- **Based on**:
  - `docs/artifacts/poc-security-engineer-tool-scoping-v2.md` (the contract this amends);
  - `docs/artifacts/placeholder-flag-ruling-v3.md` §5 Question 2 Option A, §6 E-S2, §7, §9 RA-7, RA-11, RA-12;
  - `docs/artifacts/security-review-placeholder-flag-ruling-v3.md` (V3-2, V3-6, V3-7, V3-8 binding);
  - `docs/artifacts/security-review-t608-placeholder-flag-text-v1.md` (SEC-6, SEC-7, SEC-8 carried);
  - `implementation/runtime/security/poc_scan.py` and `poc_audit_server.py`, `RULES_VERSION` `2026-10-09.4`.
- **Decision references**: ADR-008 P4 and D5 (via v2). No new ADR. Immutable Security Constraint 1 governs.

## 1. Standing decision recorded (V3-7)

The user's decisions of 2026-10-09 (AskUserQuestion, option labels verbatim, relayed in `docs/tasks/task-T609.md`):

| Question | Answer (verbatim label) | Effect |
|---|---|---|
| T606 Question 1 | "You confirm each flag (Recommended)" | Option 1: flags are created only by the user's confirmation (agent text, T608) |
| T606 Question 2 | "Remove skip, label 3 shapes (Recommended)" | Option A: the `$ < { space` skips are removed and three exact template shapes carry a label; this contract and the scanner implement it |

By the second answer the user decided, as a standing decision and for those three exact shapes only, that a hit carrying
`value_shape: "template-ref"` is listed and counted separately and is not an unresolved hit (the one named exception in
ruling-v3 constraint 13). A hit the scanner does not label is never treated this way. The agent text records the quoted
label and grades such hits `SECURITY:LOW` for debt handoff.

## 2. Change log against v2

| # | v2 | v3 | Source |
|---|---|---|---|
| 1 | §3.2 Parsing: everything after the line number "is dropped unread into the result" | The matched-text field is **read in memory** only for the two credential-assignment rules in `worktree` and `index` scope (`_parse_records(..., keep_text=True)`), reduced to a shape name and discarded. It is never returned, logged, stored, or put in an error. Every other rule and scope, and the anchored check of section 4, still drop it unread (`keep_text=False` returns an empty text field; `parse_grep_z` never copies it) | E-S2 cond. 5, V3-6, T609-2 |
| 2 | §3.2 Output hit: `{rule_id, scope, path_or_redacted, path_index?, line, commit?, ref?}` | Adds `via?` (already emitted for `git log -G` hits) and the optional `value_shape` and `template_shape` (section 4). The allow-list is `poc_scan.HIT_KEYS`; `add_hit` drops any key outside it at run time and a test pins the set for every scope | V3-6, T609-3 |
| 3 | Rule table skips values starting `$`, `<`, `{` or a space | Skips removed exactly as E-S2 lists (section 3). `RULES_VERSION` is `2026-10-09.4` | E-S2 |
| 4 | Per-rule `(path, line)` de-duplication keeps the first `-o` record | The records of one `(path, line)` are grouped first; the label is decided over **all** of them, so a second match is never discarded before the check | E-S2 cond. 4, L-3 |
| 5 | Module docstring L-3: the quoted placeholder heuristic skips `$ < { space` | L-3 is superseded by the user decision above; the docstring lists what is still not reported | E-S2 |

## 3. Rule table changes (E-S2, common part)

- `credential-assignment`: the value class `[\"'][^\"'$<{ ]` becomes `[\"'][^\"']`.
- `unquoted-credential-assignment` (`_UNQUOTED_VALUE`): the leading class `[^ \t\r\"'$<{(=]` becomes `[^ \t\r\"'(=]`.
- `url-embedded-credentials`: `:[^/@ $<{]` becomes `:[^/@ ]`.
- **Still excluded, and why:** in the unquoted rule a leading space, tab or carriage return (they separate name from value, so an
  empty value would match), a quote (a quoted value belongs to the quoted rule), `(` (a call such as `get_password(...)`) and `=`
  (a comparison); in the URL rule `/`, `@` and a space (delimiters). Values shorter than eight characters (three for a URL
  password), values holding a quote (or `(` unquoted), names ending in a configuration word, and unlisted formats remain unseen
  (RA-11). A quoted `${ABC}` is six characters and is therefore not reported.

## 4. The label (Option A, V3-2)

A hit gets `value_shape` only when **all** hold:

1. the rule is `credential-assignment` or `unquoted-credential-assignment` (`poc_scan.LABEL_RULES`); URL hits and every other rule
   never carry a label (V3-2);
2. the scope is `worktree` or `index` (`LABEL_SCOPES`) and the hit has no `commit`; `via: "log"` hits, stash and history tree
   hits, name hits and hits whose path is redacted never carry a label;
3. the git output for that rule was not truncated;
4. **every match of the rule on the line**, not only the first, has a value that is, as a whole (`fullmatch`, no prefix or
   substring match), one of the shapes below, and all matches on the line have the **same** shape;
5. the line ends with the value (T609-1): see the anchored check below;
6. the value is extracted from the matched text in memory and the text is discarded.

**Anchored check (T609-1).** The `-o` text ends at the closing quote or the first whitespace, so it cannot show what follows the
value. For each label rule, when at least one line is a label candidate, `_Scan._value_ends_line` runs **one extra `git grep`**
through the same `run_git` choke point, argv prefix, flags (`--cached` or `--untracked --no-exclude-standard`), `-a -o -n -z -E`
and aggregate deadline, with the rule pattern whose tail is replaced by `[ \t\r]*$` (`poc_scan.ANCHORED_RULES`). A hit is
labelled only if its `(path, line)` is in that result and conditions 1-4 hold. Only spaces, tabs and a carriage return may
follow the value, so a trailing `,` or `;` or any other text leaves the hit unlabelled (the safe direction). The check fails
closed and quietly: an error, timeout, truncation or unparseable output gives no label, adds no scan error, and never removes a
hit, so a complete scan stays complete. The text field of the anchored output is dropped unread. Residual: with several matches on
one line, only the last is anchored; text between two shape matches that no rule matches is not judged.

| `value_shape` | `template_shape` | Value (exact pattern) |
|---|---|---|
| `template-ref` | `braced` | `\$\{[A-Z][A-Z0-9_]{2,}\}` |
| `template-ref` | `angle` | `<[a-z]+([ _-][a-z]+)+>` |
| `template-ref` | `jinja` | `\{\{ [a-z][a-z_.]{1,30} \}\}` (one space each side) |
| `bare-dollar-name` | (none) | `\$[A-Za-z_][A-Za-z0-9_]{2,}`; stays unresolved, never `template-ref` |

Value extraction (pinned by a test, `poc_scan._QUOTED_MATCH_RE` and `_UNQUOTED_MATCH_RE`): quoted rule `[^:=]*[:=][ \t]*[\"']([^\"']*)[\"']`; unquoted rule `[^:=]*[:=][ \t]*([^ \t\r]+)[ \t\r]*`,
each applied with `fullmatch` to the text git returned for one match. A match that does not fit is not a shape, so the line is not
labelled. **Deviation from E-S2 wording (safer direction):** E-S2 allows each match to be "one of the shapes"; v3 additionally
requires the same shape for all matches on a line, because `template_shape` is a single value. Two different shapes on one line
give no label.

The label never changes `hits`, `counts`, `complete` or `truncated`; a hit is never removed because it is labelled.

## 5. Residuals

- **RA-7** (ruling-v3): a real value written exactly in one of the three shapes (a multi-word lowercase passphrase in angle
  brackets, a `${ABCDEFGH}` password, a `{{ name }}` secret) is listed as `template-ref` and does not block. Accepted by the user's
  standing decision; never silent.
- **RA-11:** no option removes the whole blind spot (section 3).
- **RA-12:** shapes in stashes, history and `git log` hits are never labelled and need a `user-attested` flag each.
- **R-1 of v2 (`grep_content` unredacted)** is unchanged. The in-memory read of matched text in `scan_secrets` is a new, narrow
  exception to "dropped unread"; the output side (no matched text, no stderr, no argv) is unchanged.
- **Cap (T609-5, cap unchanged):** `template-ref` and `bare-dollar-name` hits count toward `max_hits` (500) like any hit. A
  repository with more than 500 such lines is always `truncated`, so the verdict is `FAIL`; a label never lowers the count.
- **URL passwords** such as `postgres://u:${PASS}@h` are never labelled (V3-2). They are ordinary hits and need a
  `user-attested` flag each.
- **`hit_count` (T609-6):** a flag's `hit_count` counts every hit the scan reports for its rule, path, scope and commit, labelled
  hits included.
- **`{{ name }}` (T609-9):** the pattern accepts a single lower-case word, so `{{ password }}` is labelled `jinja`. The label
  also tells a reader that the value has a template shape, which is a few bits of information derived from the value (not the
  value itself) and is in the result by design.
- The label is judged on the regular expression match git returns, not on a second read of the file; a text whose shape differs
  between git's POSIX ERE and the Python extraction patterns gets no label.

## 6. Tests (all in `tests/functional/test_poc_audit_server.py`, class `TemplateLabelTests`, and `test_placeholder_flag_text.py`)

Mixed line (both orders, quoted and unquoted) gets no label; three matches in every position, three equal shapes and three
different shapes; second match not discarded by the de-duplication; `index` and `worktree` labelled; `log`, stash and history
tree hits unlabelled; URL hits, other rules and redacted paths unlabelled; truncated output unlabelled; each shape; near-misses
(`<hunter2>`, `<password>`, `${abcdefgh}`, `{{ hunter2 }}`, `{{key}}`); the exact regexes pinned; the hit-key allow-list pinned;
no matched text or error text in any result; the changed skips and the ones that stay.

## 7. Unverified

1. Behaviour on a git whose `-o` output differs from the installed one (the T603 layout test pins the installed git only).
2. That Python `fullmatch` and git's POSIX ERE agree on every byte of a non-UTF-8 value; undecodable bytes become U+FFFD and
   cannot match a shape, so such a line is not labelled.
