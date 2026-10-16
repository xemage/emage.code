# Artifact: poc-security-engineer-tool-scoping-v4.md

> Immutable once produced; revisions bump `<N>`. **Amends `poc-security-engineer-tool-scoping-v3.md`** (which amends v2), both of
> which stay unchanged as the historical record. Where they differ, v4 governs; everything v3 and v2 say and v4 does not mention
> is unchanged (server, two tools, argv, environment, root check, caps, redaction, the label conditions of v3 section 4,
> `ref_containment`). F-8, E1-b, E1-c and both tool lists are byte-identical.

## Metadata

- **Producer agent**: backend-developer
- **Task**: T611 (plan-115): scanner residual cleanup
- **Created**: 2026-10-09
- **Based on**:
  - `docs/artifacts/poc-security-engineer-tool-scoping-v3.md` (the contract this amends);
  - `docs/artifacts/security-review-poc-security-audit-code-v2.md` (SEV-1..SEV-6) and `-v1.md`;
  - `docs/artifacts/security-review-t609-template-label-v1.md` (T609-10..T609-13);
  - `implementation/runtime/security/poc_scan.py` and `poc_audit_server.py`, `RULES_VERSION` `2026-10-09.5`.
- **Decision references**: ADR-008 P4 and D5 (via v2). No new ADR. Immutable Security Constraint 1 governs. No rule is weakened,
  no label condition changes, every failure path still ends in `complete: false` or no label.

## 1. Change log against v3

| # | Finding | v3 | v4 |
|---|---|---|---|
| 1 | SEV-1 | Name run `[A-Za-z0-9_-]*` after a credential keyword and the first JWT segment `[A-Za-z0-9_-]{10,}` are unbounded; one line that repeats `password` or `eyJ` took the full 60 s deadline (`timeout`, `complete: false`) | Name run bounded (section 2), JWT header bounded, unquoted value bounded with a longer-run branch. `RULES_VERSION` is `2026-10-09.5` |
| 2 | SEV-2 | The Python loop over file names ignores the deadline | Checked once per 4096 names (section 3) |
| 3 | SEV-3 | Returned names are verbatim | Control and format characters removed, 200-character cap (section 4) |
| 4 | SEV-4 | A configuration-word ending excludes a name wherever the letters occur | The ending must follow `_` or `-` (section 5) |
| 5 | SEV-5, SEV-6 | Undocumented | Known false positives recorded and pinned (section 6) |
| 6 | T609-10 | Residual in v3 section 4 for several matches only | Limits added (section 7) |
| 7 | T609-11 | Tool description names one rule; `assert` in `_anchored`; label values unchecked | Aligned; explicit `ValueError`; label values checked in `add_hit` (section 8) |
| 8 | T609-12 | Not stated | Section 9 |
| 9 | T609-13 | "A URL whose scheme is 32 or more characters long" listed as a blind spot | Corrected (section 10) |

## 2. SEV-1: bounded work per line

**Measurement (git 2.43.0, a repository holding one file with the line, `scan_secrets(scope="index")`, 60 s deadline):**

| Line | Before (`2026-10-09.4`) | After (`2026-10-09.5`) |
|---|---|---|
| `"password" * 100000` (800 KB, one line) | no result at the deadline (60 s as measured by the orchestrator, 70 s in the T611 re-run): `timeout`, `complete: false` | 0.6 s, `complete: true`, no hit |
| `"eyJ" * 266000` (798 KB, one line) | no result at the deadline (60 s, 70 s in the re-run): `timeout`, `complete: false` | 1.6 s, `complete: true`, no hit |
| `"password=" * 88000 + "("` (found while measuring; same cost shape in the unquoted value) | 20 s per rule without finishing (`timeout`) | 0.6 s |

Cause: for every start (each `password`, each `eyJ`) the engine scans the whole rest of the line before the required next
character fails, so the cost is starts times line length. The fix bounds the scanned run. Regex size and compile time were
checked first, because a bounded repeat is duplicated by the engine: the unquoted rule grows from 5580 to 7560 characters
(0.13 s to compile per `git grep`), and `{10,4096}` on the JWT segments was rejected (1.4 s to compile, 32 s on the line).

| Rule | Bound | Blind spot (new, documented, otherwise fail closed) |
|---|---|---|
| `credential-assignment` | name run `{0,64}` (`poc_scan.NAME_RUN_MAX`) | a credential keyword followed by more than 64 name characters before the `:` or `=` (pinned: 64 matches, 65 does not) |
| `unquoted-credential-assignment` | name run `{0,64}` before the last character of the excluded-ending check (pinned: 65 name characters match and 66 do not for an ordinary name; 65 to 67 depending on a partial excluded ending); value `{7,1024}` | the same name-run blind spot, one to three characters wider; the exclusion of a configuration-word ending is judged only inside that run |
| `jwt` | first segment `{10,512}` | a JWT whose first segment (before the first `.`) has more than 512 characters after its leading `eyJ` (pinned: 512 matches, 513 does not); the payload segment stays unbounded because a match consumes it |

**Unquoted value (new branch, over-reports only).** The value is now `A{7,1024}([ \t\r]|$)` (a value judged to its end up to 1025 characters, first character included) OR a run of 1025 characters without
space, tab, CR, quote or `(`, where `A` is the v3 character class. A secret longer than the bound stays visible. A token longer
than 1024 characters whose `(` or quote lies beyond the bound is reported (pinned: 1024 characters followed by `(` is not reported, 1025 followed by `(` is) (v3 would have excluded it): over-reporting, the safe
direction. The anchored pattern of v3 section 4 keeps only the bounded branch, so a long run never carries a label.

All timeouts remain fail closed (`timeout`, `truncated: true`, `complete: false`).

## 3. SEV-2: the name loop honours the deadline

`_Scan._name_scan` (tracked and untracked file names) checks `Deadline.remaining()` once per 4096 names (`_NAME_CHECK_EVERY`). On
expiry it records `timeout` with `truncated: true` and stops, so `complete` is `false` and the hits already found stay in the result.

## 4. SEV-3: returned names

`poc_scan.safe_name` removes characters of Unicode category `Cc` (control), `Cf` (format: bidi overrides, zero width),
`Zl` and `Zp` from every returned file, ref and tag name and cuts the name at 200 characters (197 characters plus `...`).
The redaction rules are tested on the raw name **and** on the cleaned name (T611-1), each before the cut, so a token split by
a zero-width or control character (`AKIA<ZWSP>XXXXXXXXXXXXXXXX`) is still redacted and a name that was redacted before this
change still is; the `<redacted-by-rule:ID>` text is untouched. Two names that differ only in removed characters show the same text.

## 5. SEV-4: separator before an excluded ending

The unquoted rule excludes a name only when it ends in `_` or `-` followed by one of `ttl timeout url uri endpoint path file dir
name expiry expires expiration length size type header env var` (`poc_scan.NON_SECRET_NAME_SUFFIXES`).
`SECRET_FILE=...` is excluded; `SECRET_PROFILE=...` is reported. **Consequence:** a run-together or camel-case name
(`secretfile`, `tokenUrl`, `passwordFile`) is no longer excluded and is reported (a false positive; the safe direction).

## 6. SEV-5 and SEV-6: known false positives (pinned, not fixed)

- A type annotation such as `password: Optional[str] = None`, an all-digit value under a name that contains "token"
  (`MAX_TOKENS=100000000`) and a code identifier (`password = args.password`) are reported by the unquoted rule.
- There is deliberately **no** "not all digits" rule (it would miss `DB_PASSWORD=12345678`) and **no** `tokens` exclusion
  (`API_TOKENS=<a>,<b>` is a plausible real secret list).
- A JWT test fixture (the jwt.io sample, or an unsigned token whose signature segment is empty) is reported by the `jwt` rule
  like any token.

## 7. T609-10: limits of the label (adds to v3 section 4 and section 5)

- With several matches of the rule on one line only the last is anchored to the end of the line. Text **between** two shape
  matches that no rule matches is not judged.
- A line continuation is not judged: a YAML plain scalar that continues on the next line, or a trailing backslash.
- A label therefore means "every matched value on this line has the same exact shape and the last ends the line", not "the whole
  logical value is a template". Optional single-match-only labelling was **not** adopted, because v3's multi-match behaviour is
  pinned by tests and the reviewed design.
- **Text beyond the bounds of section 2 is unjudged too (T611-5).** The label is judged on what the rules match. Text that a
  bound hides is not read: a name run over about 64 characters after the keyword (65 to 67 in the unquoted rule) and a JWT first
  segment over 512 characters after `eyJ`. A line with a long-named real credential followed by a template-shaped assignment
  that ends the line is therefore labelled `template-ref`, which is non-blocking, **for the visible match only**. The agent text
  tells the reviewer to re-read a labelled line before relying on the label.

## 8. T609-11: consistency

- The `scan_secrets` tool description now names both label rules, the end-of-line condition, the same-shape requirement, the
  scopes that can carry a label, that other rules and URL hits never do, and the name cleaning of section 4 (control, format and line/paragraph separator characters removed, 200-character cap).
- `_anchored` raises `ValueError` when a rule no longer has the expected tail (it used `assert`, which `python -O` removes). The
  module fails to import in that case, so a drifted rule cannot silently build a wrong anchored pattern.
- `add_hit` checks the label values against the fixed sets: `value_shape` is `template-ref` (with a `template_shape` in
  `braced`, `angle`, `jinja`) or `bare-dollar-name` (without a `template_shape`). Any other combination drops both label
  keys and keeps the hit.

## 9. T609-12: degraded check, quiescent tree

- When the anchored check degrades (error, timeout, truncation, unparseable output) the hits stay and `complete` stays `true`,
  but no hit is labelled. **A missing label therefore may mean the check degraded**, not only that the value is not a template.
  This is the safe direction and is not signalled.
- The scan assumes a **quiescent tree**: the content `git grep` and the anchored `git grep` are two reads, and an edit between
  them could in theory move a line, which at worst gives a missing or wrong label. Run the scan with no concurrent writer.

## 10. T609-13: the URL scheme

v3 and the agent text listed "a URL whose scheme is 32 or more characters long" as a blind spot. It is not: the pattern
`[a-z][a-z0-9+.-]{0,31}://...` is not anchored on the left, so a longer scheme still matches its last 32 characters. Only an
**upper-case scheme** is missed (`HTTP://user:pw@host`). The module docstring and the agent blind-spot bullet
(`implementation/knowledge/agents/poc-security-engineer.md`) are corrected, and the bullet adds the new SEV-1 blind spots and the
SEV-4 separator wording.

## 11. Tests (`tests/functional/test_poc_audit_server.py`, class `T611Tests`; `test_placeholder_flag_text.py` pin)

SEV-1 timing for both lines (under 10 s, `complete: true`) and for the `password=` line; the pinned name-run bounds (64 quoted, 65 unquoted), the JWT 512 edge and the value 1024/1025 edge; regex size and Python compile time (a proxy, not git's regcomp); SEV-2 with an expiring deadline and with a live one; SEV-3 with newline, ESC, a bidi
override, zero width and line-separator characters (written as escapes) and a 240-character name; T611-1 split-token file
names, tag names and history `ref` values (redacted, stripped, capped); SEV-4 pair plus the camel-case consequence; SEV-5
pins; SEV-6 pins; the documented limits; the long and upper-case URL scheme; label-value validation; no `assert` in the scanner and
`_anchored` raising under `python -O`; the tool description; this artifact. Updated pins: `RULES_VERSION`, the
`_not_ending` builder test (separator forms), the hit-key test (valid label values), and the blind-spot sentence in
`test_placeholder_flag_text.py`.

## 12. Open residuals (tracked, not fixed in T611) and unverified

Open residuals from the Security Engineer review of T611 (all `SECURITY:LOW`):

- **T611-2:** `safe_name` changes `path_or_redacted`, the key that placeholder flags match on. A path whose shown text was altered
  (a removed character, a cut) must not be flaggable, because the flag's `path` is "exactly as the scan shows it" and the shown text
  no longer identifies one file. Needs a v5 delta (an explicit marker or a separate field) and agent text; until then the agent
  text does not cover it, and the orchestrator should treat a flag on a cleaned or cut path as unsafe.
- **T611-3:** portability of the bounded repeats `{7,1024}`, `{1024}` and `{10,512}`. They were measured on git 2.43.0 with glibc;
  musl and BSD regex libraries cap a repeat count (`RE_DUP_MAX`, 255 on some) and would reject the pattern. The scan then fails
  closed as `git_failed` (`complete: false`), never a silent pass. Needs a startup self-test that compiles each rule once.
- **R-1 (aperiodic input):** the bounds make the cost per start at most the bound, so a line that starts a match at very many
  positions costs about starts times bound (about 1 s on the measured 800 KB lines). The measured repeated-keyword shapes are
  covered; a crafted aperiodic line that defeats the bound's assumption is not excluded. It fails closed on the deadline.

Unverified:

1. Timings are for the installed git (2.43.0) on the development host; another git or regex library may differ.
2. The JWT header bound (512) and the name bound (64) are judgement values; a real credential name or header above them is a miss.
3. A quadratic shape in a rule not exercised here (`url-embedded-credentials` and the provider-token rules measured at 0.3 s or
   less on 800 KB lines of repeated `a://b:`, `Bearer `, `SG.`, `sk-`, `AKIA`, `password'`, `pwd: `) cannot be ruled out in general.
