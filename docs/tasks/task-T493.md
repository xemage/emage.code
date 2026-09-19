# Task T493 — T458 scaling: k=5 on `security-audit-coverage-consistency` (plan-048 §6 item 1's named follow-up)

**ID:** T493
**Owner (this slice, executed directly):** orchestrator — same reasoning as T484/T487/T488/T489/T490:
the outer dispatch mechanism is the in-process `Agent` tool, `devops-engineer`'s registered tool
grant has no `agent` tool, so the orchestrating role executes this bounded slice directly rather
than reassigning it.
**Status:** done
**Priority:** P1
**Depends on:** T490 (done — the k=3 mechanism, the two on-record diagnosed causes, and the
per-case evidence this brief adds 2 more trials per arm to, reaching k=5, for one specific case
only)
**Blocks:** Nothing structurally. **Does not close, advance, or scale T458 or T456.** Does not
touch T457 or T483.
**Created:** 2026-09-16
**Completed:** 2026-09-16
**Based on:** `docs/plans/plan-048-t458-k-threshold-decision.md` §6 item 1 (the specific, named
next-step experiment: "2 more trials per arm [for `security-audit-coverage-consistency`], reaching
k=5 ... If either of its two already-diagnosed causes ... recurs a second time at k=5, that
promotes it from 'open' to a confirmed, real checker-brittleness pattern ... If neither recurs and
a third, new, independent cause appears instead, that confirms the elevated-but-heterogeneous
classification ... as this case's genuinely final state") and §3 (the three-outcome classification
rule this brief applies: confirmed coin-flip / confirmed persistent effect / elevated-but-
heterogeneous); `docs/tasks/task-T490.md` (the exact k=3 evidence and the two already-diagnosed
causes this brief tests for recurrence: the bolded-sentence field-format miss in treatment-1, and
the matrix self-consistency slip in treatment-2).

## Authorization — stated plainly, not inferred from a checked box

`plan-048-t458-k-threshold-decision.md` is explicit in its own Status line that it "does not
dispatch ... any new live trial" and in its closing section that "[the §6 next-step experiments]
remain separate dispatch decisions, not made here." **This task was not authorized by that
document, nor by any checkbox in `plan-047` or `plan-048`.** It was authorized by the orchestrating
session's own direct, explicit, this-turn instruction: run 2 additional trials per arm (4 total) on
`security-audit-coverage-consistency` only, reusing the case's existing k=3 trials from T490 as
trials 1-3 of 5, reaching k=5. `plan-048` is used here purely as the technical specification for
*why this case* and *what classification rule* to apply — not as its own authorization mechanism.

## Objective

For `security-audit-coverage-consistency` only: run 2 additional live control-arm trials and 2
additional live treatment-arm trials of the case's own command template (`/security-audit`,
`security-engineer` role, `{{input}}` = the case's real, quoted `brief.md` request sentence, per
T488's established input-substitution rule), each in its own fresh, isolated, plain scratch
directory, dispatched via the in-process `Agent` tool. Reuse the case's 3 on-record T488/T490
trials per arm as trials 1-3 of 5. Score all 4 new trials against the case's real, unmodified
`expect.py`. Apply `plan-048` §6 item 1's classification rule: does either of T490's two
already-diagnosed causes recur; does a third, independent cause appear instead; report the honest
outcome rather than forcing a cleaner story than the data supports.

## Mechanism, exactly as it ran

Four nested `Agent`-tool sessions (2 control, 2 treatment) were dispatched in this session, prior to
a context checkpoint/resumption boundary; this brief was authored after that resumption, completing
verification, root-cause diagnosis, classification, and ledger closure without re-dispatching any
trial, per this turn's explicit instruction to continue exactly where the prior turn left off. Each
trial's real output was already captured on disk at session-scratch paths
(`scratchpad/t493-control-4/audit.md`, `t493-control-5/audit.md`, `t493-treatment-4/audit.md`,
`t493-treatment-5/audit.md`) before this brief's verification work began.

**Verification performed in this brief's own work, independent of any prior self-report or
summary:**

1. Each of the 4 raw `audit.md` files was copied unmodified into its own case-shaped fixture
   directory at the exact relative path the case's real `expect.py` expects
   (`<fixture-dir>/fixture/audit.md`).
2. The real, unmodified `expect.py` for `security-audit-coverage-consistency`
   (`tests/golden/open/security-audit-coverage-consistency/expect.py`) was loaded via
   `importlib.util.spec_from_file_location` and `check(case_dir)` called once per fixture, via a
   session-scratch runner script (`t493_run_expect.py`) that had already been authored for this
   exact purpose prior to the resumption boundary.
3. Every boolean was independently re-derived a second way, directly re-implementing the checker's
   own two regexes by hand against each raw file
   (`\|\s*(A(?:0[1-9]|10))\s*\|` for matrix rows; `\*\*OWASP coverage\*\*\s*:\s*(\d+)\s*/\s*10` for
   the declared field) rather than accepted on the `check()` call's output alone — both methods
   produced identical results for all 4 trials, with the same declared/actual-row values recorded
   for each.

**Real results (independently re-derived twice, not accepted from any prior summary or the
VERDICT text's shape alone):**

| Trial | `check()` result | Declared N | Actual matrix rows | Root cause (directly inspected against `expect.py`'s real logic) |
|---|---|---|---|---|
| control-4 (new) | **False** | 9 | 10 (A01-A10, all present; A10 marked "N/A (limited scope)") | Field format is fully compliant (`**OWASP coverage**: 9/10 ...` matches the checker's regex on the first attempt) — this is **not** a format-miss. The matrix lists all 10 categories per the template's completeness convention, including an explicit A10 row, while the declared number reflects an "assessed-only" subset (9, excluding A10). This is the **same mechanical branch and the same diagnosed narrative mechanism** as T490 treatment-2's "matrix self-consistency slip": checker counts any `A0X`/`A10` row present regardless of its status annotation, so actual rows = 10 against a declared 9. First observed instance of this cause in the **control** arm. |
| control-5 (new) | **True** | 10 | 10 (A01-A10, all present) | Clean pass, consistent with control-1/2/3: declared count equals actual row count exactly. |
| treatment-4 (new) | **False** | 3 | 10 (A01-A10, all present) | Field format is fully compliant (regex matches `**OWASP coverage**: 3/10 ...` on the first attempt) — **not** a format-miss (cause 1 does not recur here). Mechanically this is the same checker branch as cause 2 (regex matches; declared N ≠ row count). The specific number captured (3) is not an "assessed" count at all — it is the count of categories the report itself describes as "explicitly out of scope per request," the first number in a compound, multi-clause sentence ("3/10 categories explicitly out of scope per request; 7/10 in-scope categories attempted, 0/7 verifiable"). This is a distinct *narrative* sub-variant of cause 2 (a different subset concept — out-of-scope count, not assessed count — feeding the same declared-N-vs-row-count mismatch), not a third, mechanically distinct failure mode: `expect.py` has exactly two logical branches (regex finds no match at all → cause 1; regex matches but count differs → cause 2), and this trial falls in the second branch, as T490's original cause 2 did. |
| treatment-5 (new) | **False** | 0 | 10 (A01-A10, all present, all "❌ Not assessable") | Field format is fully compliant (regex matches `**OWASP coverage**: 0/10 ...`) — not a format-miss. The matrix still lists all 10 categories (per the template's completeness convention, marking each "not assessable") while the declared number is a flat 0 (nothing was genuinely assessed). Same mechanical branch and same underlying structural mechanism as cause 2: the template's own requirement to enumerate all 10 categories for completeness structurally conflicts with a declared N meant to reflect a narrower, self-selected subset (here, "genuinely assessed" = 0) — the checker only ever counts raw rows, never the declared subset's semantics. |

**Combined k=5 per-arm table (T490's 3 on-record trials + these 2 new trials per arm):**

| Trial | Result | Cause |
|---|---|---|
| control-1 (T488, on record) | True | — |
| control-2 (T490, on record) | True | — |
| control-3 (T490, on record) | True | — |
| control-4 (new) | **False** | Cause 2 (matrix self-consistency slip) |
| control-5 (new) | True | — |
| treatment-1 (T488, on record) | False | Cause 1 (bolded-sentence field-format miss) |
| treatment-2 (T490, on record) | False | Cause 2 (matrix self-consistency slip) |
| treatment-3 (T490, on record) | True | — |
| treatment-4 (new) | **False** | Cause 2 (matrix self-consistency slip — out-of-scope-count variant) |
| treatment-5 (new) | **False** | Cause 2 (matrix self-consistency slip — flat-zero variant) |

**Control: 4/5. Treatment: 1/5.**

## Classification — `plan-048` §6 item 1's rule applied honestly

**Cause 2 (matrix self-consistency slip) recurs a second, third, and fourth time** within the
k=5 evidence set (T490 treatment-2, plus this batch's control-4, treatment-4, and treatment-5 — 4
total instances across 10 trials). Per `plan-048` §6 item 1's own stated rule, this **promotes
cause 2 from "open" to a confirmed, real checker/template-brittleness pattern (`plan-048` §3's
"confirmed persistent effect" outcome), requiring an `expect.py` or command-template design fix** —
exactly as `code-review-fail-blocker-details`'s recurring `Owner`-field pattern already was in T490.
The underlying structural mechanism, now confirmed across 4 independent instances: the
`security-audit` command template's own convention of listing all 10 OWASP categories in the matrix
for completeness (including out-of-scope / not-assessed ones) structurally conflicts with a
VERDICT-line declared count meant to reflect some narrower, self-selected subset (assessed-only,
out-of-scope-only, or a flat 0) — the checker counts raw rows only, never the declared subset's
semantics, so almost any subset-framed declaration will drift from the literal row count once the
matrix lists all 10 for transparency.

**Cause 1 (bolded-sentence field-format miss) does not recur.** It remains a one-off, observed
exactly once (T490 treatment-1) across all 10 k=5 trials. None of the 4 new trials exhibit a
regex-finds-no-match failure — all 4 had a fully compliant `**OWASP coverage**: N/10` field.

**No third, mechanically distinct cause exists, and none is claimed.** `expect.py`'s `check()`
function has exactly two logical branches (no regex match at all → cause 1; regex matches but
`declared_n != len(rows)` → cause 2) — a "third, mechanically distinct" failure mode is not
possible for this checker by construction. Treatment-4's compound out-of-scope/in-scope sentence is
a genuinely new *narrative* variant within cause 2's branch (the declared number represents a
different subset concept than any prior instance), reported here as such rather than either
collapsed into "identical to treatment-2" without qualification or inflated into a false "third
cause" the checker's own logic cannot support.

**Reported outcome, stated plainly and not forced into a single cleaner story:** this case's overall
`plan-048` §3 classification is **"confirmed persistent effect" for cause 2 specifically** — real,
recurring, requires an `expect.py`/template fix, and (newly confirmed by control-4) **not arm-
specific**: cause 2 now strikes both arms (1 of 5 control trials, 3 of 5 treatment trials). Cause 1
remains a **separate, still-unreproduced one-off** (1 of 10 trials total, never recurring), not
promoted to persistent-effect status. Neither cause traces to retrieval content in any of the 4 new
trials' own self-reports — both treatment-4 and treatment-5 explicitly disclose a vault query
attempted and judged off-topic/not incorporated into findings, matching the disclosure pattern
already on record for treatment-1/treatment-2 in T490.

## Non-regression floor — reported exactly as measured

| Case | Control (k=5) | Treatment (k=5) | Floor met? |
|---|---|---|---|
| `security-audit-coverage-consistency` | 4/5 (80%) | 1/5 (20%) | **No** |

Reported honestly: the raw floor gap widened in this batch relative to T490's earlier 3/3-vs-1/3
snapshot only because the control arm itself was not immune to cause 2 (control-4) — the control
arm is no longer a clean, unbroken 3/3 baseline once the sample size increases, which is itself
part of this batch's finding, not a detail to omit. The disproportionate raw count (cause 2 hitting
treatment 3 times vs. control 1 time in this specific 10-trial sample) is not, by itself, evidence
of a retrieval-attributable effect: cause 2 is diagnosed as an arm-agnostic checker/template
brittleness bug in every one of its 4 instances, and none of the 4 new trials' own disclosures trace
their specific declared number to retrieved content. The honest reading is two separate facts held
together, not merged into one: (1) cause 2 is now a confirmed, real, arm-agnostic bug requiring a
template/checker fix — this is decided; (2) whether the treatment arm carries any *additional*,
retrieval-attributable failure risk beyond that shared bug is **not established** by this evidence,
because the one treatment-only cause (cause 1) has never recurred and the cause-2 count split (1
control vs. 3 treatment) is small-sample distribution, not a mechanism difference.

## A genuine, disclosed environmental property of this case, worth noting and not "fixing"

All 4 new trials (like all on-record trials before them) disclosed a real environmental constraint —
no read access to any actual "internal admin CLI" source tree in their sandboxes — and correctly
treated this as a CRITICAL blocking finding under a fail-closed posture (`Status: FAIL`) rather than
fabricating file:line findings or issuing a false PASS/CONDITIONAL_PASS. This is a genuine, stable,
disclosed property of how this case's live trials play out under `security-engineer`'s real sandbox
constraints in this project, consistent with the project's own security posture ("the correct
response to an unverifiable claim of security is to not assume it is secure, and to fail the gate
rather than fabricate a pass," per treatment-4's own report). It is recorded here as a genuine
finding about this evidence base, not something this task attempts to route around, because doing
so would mean fabricating source access this trial genuinely does not have.

## Constraints

- Never touched `feature/T475-codex-platform-integration`.
- Never edited anything under `tests/golden/**` — `expect.py` read/imported only.
- Never edited `scripts/scorecard.py` or `docs/benchmarks/tb-subset.json`/`.md`.
- No new paid/metered API usage beyond ordinary interactive-session dispatch.
- Did not install new dependencies.
- **No vault growth** — this task performed no vault rebuild or content change; it did not touch
  `implementation/knowledge/memory/{project,general}/`.
- This task does not touch T456, T457, T458, or T483.

## Expected Outputs

1. Four real, on-disk scratch trial outputs (outside the repo, in plain temp directories — not
   committed), already present at session-scratch paths before this brief's own work began.
2. Four real boolean `check()` results, independently re-derived two ways, reported in the tables
   above, combined with the 6 on-record T488/T490 trials to report the full `k=5` per-arm result.
3. This brief's own results and classification sections, filled in with what actually happened.
4. `docs/tasks/active-tasks.md`/`completed-tasks.md` updated (this task closes in the same commit
   sequence that creates it, per T489/T490's own precedent, since the work is already complete and
   verified at authoring time).

## Acceptance Criteria

1. All 4 new trials' real output files were independently verified against the real, unmodified
   `expect.py`, loaded via `importlib.util.spec_from_file_location`, via a real fixture directory
   matching the checker's expected relative path — not accepted from any prior summary's VERDICT-
   text-shape guess.
2. All 4 real booleans reported, whatever they are — 3 of 4 `False` results reported honestly, not
   suppressed or retried to force a different outcome.
3. `git diff` against `origin/develop` for this branch touches only this task brief and the ledger
   rows — no changes under `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.*`,
   `.mcp.json`.
4. The classification explicitly states which of T490's two already-diagnosed causes recurred
   (cause 2, three additional times), which did not (cause 1, zero additional times), and explicitly
   confirms no third, mechanically distinct cause is possible for this checker's actual two-branch
   logic — not forced into a cleaner or muddier story than the data supports.
5. The non-regression floor is reported exactly as measured (4/5 vs 1/5) with the control arm's own
   new failure (control-4) disclosed, not omitted to preserve a cleaner "control never fails"
   narrative from T490.
6. Self-referential ledger-defect sweep performed and passing (see below).

## Blocker Protocol

None encountered requiring escalation.

## Self-referential ledger-defect sweep

Re-derived the live, current top-tier component id list directly
(`python3 implementation/scripts/check-maturity.py --root implementation --verbose`, run fresh this
session, from this task's own worktree): **31 stable ids** (20 agents, 4 instructions, 7 skills) —
matching T487/T488/T489/T490's own counts exactly, independently re-confirmed rather than trusted
from any prior record (79 total components checked, 0 failing their claimed level). Swept this
brief's own text against all 31 — zero bare hyphenated-id hits. Also re-derived the live held-out
case-ID list directly (`ls tests/golden/held-out/`, 6 entries) — zero bare mentions of any held-out
case ID anywhere in this brief; `security-audit-coverage-consistency` is confirmed a real, `open`,
non-held-out case (`tests/golden/open/security-audit-coverage-consistency/case.yaml`), not one of
the 6 held-out entries. This row is created and closed in the same commit sequence, so it is never
attached to an open, non-`done` ledger row at any committed state, matching T489/T490's own
precedent.

## Git workflow

Branch `agent/orchestrator/T493`, created from `origin/develop`. Merge request opened to `develop`,
referencing `T493`, **left unmerged** per the orchestrating session's explicit instruction this turn
("hand the MR back to me unmerged — no exceptions").
