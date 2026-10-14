# Artifact: poc-security-engineer-tool-scoping-v6.md

> Immutable once produced; revisions bump `<N>`. **Amends `poc-security-engineer-tool-scoping-v5.md`** (which amends v4, v3 and v2),
> all of which stay unchanged as the historical record. Where they differ, v6 governs; everything v5, v4, v3 and v2 say and v6 does
> not mention is unchanged (server, two tools, argv, environment, root check, caps, redaction, `path_altered`, the regex self-test,
> the label conditions of v3 section 4, the SEV-1..SEV-6 bounds, `ref_containment`).
> F-8, E1-b, E1-c and both tool lists are byte-identical. No rule pattern changes, so `RULES_VERSION` stays `2026-10-09.5`. No agent
> text, tool description or projected file changes.

## Metadata

- **Producer agent**: backend-developer
- **Task**: T620 (plan-120): bound the aperiodic-input cost of the JWT rule (residual R-1)
- **Created**: 2026-10-09
- **Based on**:
  - `docs/artifacts/poc-security-engineer-tool-scoping-v5.md` (the contract this amends; section 6 keeps R-1 "documented only") and
    `poc-security-engineer-tool-scoping-v4.md` section 12 (R-1 as first recorded);
  - `docs/artifacts/security-review-t611-scanner-residuals-v1.md` (R-1: "up to about 170 starts share one payload ... a multiplier on
    line length, not quadratic; fails closed at the deadline");
  - `implementation/runtime/security/poc_scan.py`, `tests/functional/test_poc_audit_server.py`.
- **Decision references**: ADR-008 P4 and D5 (via v2). No new ADR. No rule is weakened, no label condition changes, no fail-closed
  path changes and no hit is hidden.

## 1. Outcome

R-1 was measured first. Every plausible case completes within a fixed bound, so **the rule is not changed**: the measurements are
recorded here, a regression timing test is added, and the residual is restated as a linear cost with a documented fail-closed blind
spot (section 4). A bound that would reduce the work (for example a limit on starts per payload) would hide a real token that follows
a dense prefix, i.e. add a false negative, to save time on inputs that already finish in seconds; the task forbids that trade.

## 2. Measurements

Method: a scratch git repository per case, one file added to the index, `poc_scan.scan_secrets(root, "index", None, cfg)` with
`deadline_seconds=120` (the production deadline is 60 s), wall clock for the whole call (git start-up, the regex self-test and all
rules, about 0.55 s fixed). Host: the development host, git 2.43.0, glibc. "Before" is the unchanged tree at `5e07a6b`; "after" is
this change, which touches no scanner code, so the second run is a repeat check of the same scanner.

The shapes (`k` = number of consecutive `eyJ`, all inside the 512-character header window, followed by `.eyJ` and a payload that
holds no dot, so each start runs the payload to its end and fails):

| Id | Shape |
|----|-------|
| A | `eyJ` x170, `.eyJ`, then L `a` characters (one group, 170 starts share one long payload) |
| B | repeated groups: `eyJ` x170, `.eyJ`, 1000 `a`, space |
| C | `eyJ` repeated, no dot (the periodic shape of T611, one start every 3 characters) |
| D | random mix of `eyJ`, base64url runs, `.` and `.eyJ` (aperiodic, with dots; real matches occur) |
| E | random, `eyJ`-heavy, few `.eyJ` |
| F | random, `eyJ`-heavy, with 1 to 20 character base64url runs, no dots |
| G | groups with random k (100 to 170) and random payload length (0 to 5000) |
| H | many lines, each `eyJ` x170, `.eyJ`, `a` padding (about 1 KB per line) |
| J | `eyJ` x170, `.eyJ`, then `eyJ` repeated to length L (the worst found: 170 failing starts run the whole payload, and the payload holds L/3 starts of its own) |

Timings in seconds (index scope, `complete: true` in every row; D and E report a few hits, as they contain real matches; I, the many-line
random file, hit the 500-hit cap at 0.4 to 0.5 s and is a hit-cap case, not a timing case):

| Id | 100 KB | 800 KB | 2 MB |
|----|-------:|-------:|-----:|
| A | 0.65 | 1.03 | 1.78 |
| B | 0.73 | 1.09 | 1.90 |
| C | 0.74 | 1.73 | 3.56 (repeat: 3.53) |
| D | 0.59 | 0.76 | 1.08 |
| E | 0.60 | 0.85 | 1.14 |
| F | 0.71 | 1.76 | 3.41 (repeat: 3.32) |
| G | 0.63 | 1.00 | 1.56 |
| H (many lines) | - | 1.10 | 2.05 (repeat: 2.03) |
| J | 0.78 | 2.13 | 4.47 (repeat: 4.44; worktree scope 4.44) |

Scaling of the worst shape J: 5 MB 10.0 s, 10 MB 19.4 s, so the cost is **linear, about 2 microseconds per byte**, with a fixed cost
of about 0.55 s. It is not quadratic in the line length, but the multiplier is real. Step model: the matcher works from every start
until the automaton dies. A start costs up to 512 steps in the header window (`eyJ` cannot overlap itself, so there is at most one
start every 3 characters: L/3 starts, about 171 x L steps), and each of the at most 170 starts that reach one `.eyJ` then runs the
whole dot-free payload (about 170 x L steps), so about 341 steps per byte; at 2 MB that is about 680 million steps in the 3.7 s above
the fixed cost, or about 6 ns per step. The 170 x payload term needs one more argument to be bounded by 170 x L overall: a payload run
that fails must end in a character that is neither a dot nor in the class (a dot would let the rule match and consume the run), so the
failing payload runs of different dots are disjoint and their total length is at most L. Hence the worst case is about 341 x L steps,
and J is the shape that reaches it (A, with one long payload and no dense payload, reaches only the 170 x L term: 1.8 s at 2 MB).

Result: the worst plausible case (a 2 MB line) takes 4.5 s, below the 10 s the task named; 10 s is reached at about 5 MB on one line.

## 3. Regression tests (`tests/functional/test_poc_audit_server.py`, class `T620Tests`)

About 1 MB per case (about 1 to 2.5 s each on the host), bound 20 s (the scan deadline in the tests stays 40 s) (a margin of about 8 over the slowest case, J at about 2.3 s), `complete: true`, no error, no hit: J in
the index and the worktree scope; a random `eyJ`-dense line with gaps and no dot (seeded); repeated 170-start groups with random
payload lengths (seeded); many lines of 170 starts with a long payload; the `history` scope with three tips of 200 KB of shape J (about 3 s). Also: a real token after a 170-start dense prefix is still
reported (exactly one `jwt` hit; neither the token nor three fragments of it, assembled at run time, appear in the result: no new false negative); the `jwt` pattern string and `RULES_VERSION` are
pinned unchanged; this artifact and the module note exist.

## 4. Fail-closed blind spot (restated R-1)

- The cost of the `jwt` rule is linear in line length at about 2 microseconds per byte on git 2.43.0 (worst shape J).
- A single line (a minified bundle, a data URL) of roughly 30 MB or more of that shape would exceed the 60 s deadline (extrapolated
  from the 10 MB measurement, not measured). The scan then ends `timeout` / `complete: false`, `truncated: true`, never a clean result
  (v2 deadline behaviour, unchanged), and the agent reports it as an incomplete scan. This figure is for ONE file in the index or
  worktree scope. The `history` scope multiplies the cost by the number of tips (up to `max_refs`, 200) and by the changed commits
  `git log -G` examines (it has no commit cap); `stashes` multiplies it by up to 50.
- On a timeout `grep()` returns early: the rules after `jwt` in `RULES` (`sk-api-key`, `url-embedded-credentials`,
  `credential-assignment`, `unquoted-credential-assignment`) do not run, while the hits already found by earlier rules are kept. The
  result is `complete: false`, so nothing is claimed clean.
- The linear measurements were taken under `LC_ALL=C` (which `git_env()` forces), on git 2.43.0 with glibc; another locale or regex
  library was not measured.
- The deadline is aggregate: several such files in one scan add up, so a few multi-megabyte adversarial files can also exhaust it. The
  consequence is again an incomplete scan, not a miss.
- The other rules were measured in v4 section 2 (`password` x100000: 0.6 s; `eyJ` x266000: 1.6 s) and, for the provider-token and URL
  rules, at 0.3 s or less in v4 section 12; this change does not touch them.

## 5. Open residuals and unverified

- R-1 is restated as an accepted fail-closed residual (measured, linear, fail-closed beyond a stated size), not closed. It is not eliminated: a restructured pattern (for example a
  possessive or anchored form) is not available in POSIX ERE, which the rules must stay compatible with.
- The other residuals of v4 section 12 are unchanged.

Unverified:

1. Timings are for git 2.43.0 with glibc on the development host; another git, regex library or a loaded host differs. The test margin
   (about 1 MB cases against a 10 s bound) is meant to absorb a 4x slowdown.
2. The 30 MB figure is an extrapolation.
3. The 30 MB figure applies to ONE file in the index or worktree scope. For `history` only one case was timed (3 tips x 200 KB of shape J,
   about 3 s); `stashes` and a history with many tips or many changed commits were not timed, and their cost is a multiple of the
   single-file cost (section 4).
