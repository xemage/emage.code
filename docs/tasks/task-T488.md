# Task T488 — T458 scaling, Tier 1: 5-case breadth expansion at k=1 (10 live trials)

**ID:** T488
**Owner (this slice, executed directly):** orchestrator — same reasoning as T484/T487: the outer
dispatch mechanism is the in-process `Agent` tool, `devops-engineer`'s registered tool grant has
no `agent` tool, so the orchestrating role executes this bounded slice directly rather than
reassigning it.
**Status:** done
**Priority:** P1
**Depends on:** T486 (done — the populated vault), T487 (done — the mechanism this brief repeats
across more cases)
**Blocks:** Nothing structurally. **Does not close, advance, or scale T458 or T456.** Does not
touch T457 or T483.
**Created:** 2026-09-13
**Completed:** 2026-09-13
**Based on:** `docs/plans/plan-045-t458-scaling.md` (the technical specification this brief
executes — Finding 1's case selection, Finding 2's two-tier design restricted here to Tier 1 only,
Finding 3's non-regression-floor process, Finding 4's agent-formulated-query design, Finding 5's
no-vault-growth constraint, Finding 6's cost/scope estimate); `docs/tasks/task-T484.md` and
`docs/tasks/task-T487.md` (the exact live-dispatch / scratch-directory / `expect.py`-reuse
mechanism this brief repeats, unchanged, across 5 cases instead of 1).

## Authorization — stated plainly, not inferred from a checked box

`plan-045-t458-scaling.md` itself is on record as "proposed — presented for review in this
session's report, **NOT approved**," with every item in its own "Approval" checklist left
unchecked in the version merged to `origin/develop`. **This task was not authorized by any of
those checkboxes being ticked.** It was authorized by the orchestrating session's own direct,
explicit, this-turn instruction: run Tier 1 only (the 5-case, k=1, 10-trial breadth expansion),
explicitly excluding Tier 2 (the separate 4-trial noise probe) as out of scope for this dispatch.
`plan-045` is used here purely as the technical specification for *what* Tier 1 concretely means
(case list, query-design rule, non-regression-floor definition) — not as its own authorization
mechanism.

## Objective

Execute Finding 1's 5-case breadth expansion at Finding 2's Tier 1 scope (`k=1`, one trial per
arm per case): for each of `plan-required-sections-compliant`,
`prepare-release-changelog-grouping-compliant`, `code-review-fail-blocker-details`,
`security-audit-coverage-consistency`, and `security-audit-verdict-fields-compliant`, run one live
control-arm trial and one live treatment-arm trial of the case's own command template
(`{{input}}` = the case's real, quoted `brief.md` request sentence only — see "Input substitution
rule" below), each in its own fresh, isolated, plain scratch directory, dispatched via the
in-process `Agent` tool as the role each command's own frontmatter declares. Score every arm
against its case's real, unmodified `expect.py`. Report the non-regression floor (treatment vs.
control pass rate) and a qualitative, per-case, evidence-based influence assessment — descriptively,
not against any invented numeric threshold.

## Input substitution rule (a genuine design decision, disclosed)

Each case's `brief.md` "Brief (illustrative — not executed live)" section contains a quoted
request sentence, and in three of the five cases, an additional unquoted continuation sentence
describing the case's own expected finding/outcome (e.g. "Review finds a missing
signature-verification check — a real blocker"; "Full-project audit, no findings"). Handing the
continuation sentence to the live session would hand it the answer the golden check is testing
for, corrupting the trial. **This brief uses only the quoted request sentence as `{{input}}` for
every case, uniformly**, letting each live session reach its own conclusion using its own
judgment and (for the treatment arm) whatever it retrieves — exactly the discipline Finding 4
itself argues for (agent-formulated reasoning, not human-curated setup).

## Pre-dispatch verification performed (before any trial ran)

1. Independently re-fetched `origin/develop` and confirmed `HEAD` = `7b99fb4f8ce23f2248120048376eea7a0047aa2b`, matching the orchestrating session's stated expectation.
2. Re-read `docs/tasks/active-tasks.md` fresh: unchanged since T487 closed (`T456` blocked, `T457`
   pending, `T458` pending, `T483` pending); confirmed the real max existing task ID is `T487`
   (a naive `grep -oE 'T[0-9]+'` sweep of both ledger files surfaces several much larger numbers —
   `T1112`, `T1529`, `T1610`, `T1626`, `T1903`, `T1938`, `T2034` — all independently confirmed to be
   false positives, substrings of RUN_ID timestamps like `T190348Z`/`T193832Z` in T407's own
   closure text, not real task IDs), so **T488 is the correct next sequential ID**, not assumed.
3. Read all 5 real `case.yaml`/`brief.md`/`expect.py` files fresh, in full, from this task's own
   worktree — all five confirmed to match `plan-045` Finding 1's characterization exactly: `open`,
   `expected_pass`, hand-authored, each requiring exactly one fresh Phase-1-shaped artifact. No
   discrepancy found; none needed to be reported per the orchestrating session's own stop-condition.
4. Read all 4 real command templates (`plan.md`, `prepare-release.md`, case 3's review-command
   template file, `security-audit.md`) in full, including frontmatter, confirming each `agent:`
   role: `/plan` and `/prepare-release` → `orchestrator`; case 3's own review command →
   `tech-lead`; `/security-audit` → `security-engineer`.
5. Rebuilt the knowledge-vault index myself, from scratch, in a fresh throwaway venv outside the
   repo (`fastembed==0.8.0`, the exact T485-T487 precedent; no repo dependency manifest touched).
   Result independently reproduced T486/T487's own manifest byte-for-byte: `chunk_count: 25`,
   `entry_count: 11`, `rejection_count: 0`, `embedding_model: nomic-ai/nomic-embed-text-v1.5`. The
   vault itself was independently confirmed unchanged at 11 files (5 general + 6 project) before
   and after this task — **no vault growth performed**, per Finding 5's explicit constraint.
6. Confirmed the worktree (`/home/emage/Code/emage/worktrees/agent-orchestrator-T488`, branch
   `agent/orchestrator/T488`, from `origin/develop` @ `7b99fb4`) stayed clean (`git status --short`
   empty) after the index build — the build step touches no repo file, confirmed directly rather
   than assumed.

## New empirical finding beyond T484/T487: `--platform-root` must resolve to a real generated-manifest location

T484/T487 documented the corrected CLI shape (`query_text` positional; `--index-dir`/
`--workspace-root`/`--platform-root` named flags) but neither slice's own record specifies what a
valid `--platform-root` value actually has to contain. This task's own pre-dispatch sanity check
found that pointing `--platform-root` at a plain worktree root fails with
`PlatformResolutionError: could not read platform build manifest at
<root>/.generated-manifest.json`. The real, working value is a **platform-specific generated
folder** (e.g. `<worktree>/.claude`, which contains a real, gitignored `.generated-manifest.json`
produced by this repo's own sync tooling) — not the worktree root itself. This is a genuine new
detail this task surfaces, not a regression: `.generated-manifest.json` is `.gitignore`d and
per-platform-folder, and every treatment-arm dispatch in this task was given the corrected
`--platform-root .../.claude` value, verified working by the orchestrator's own sanity query before
any dispatch.

## Mechanism, exactly as it ran (all 10 trials genuinely live, dispatched in this session)

Ten nested `Agent`-tool sessions were dispatched (5 cases × 2 arms), each given: (a) the case's
own real command template text verbatim, with `{{input}}` substituted per the rule above; (b) a
sandbox instruction confining it to its own absolute, plain scratch directory (never a git
worktree, never under the repo, never permitted to run `git`); (c) for treatment arms only, the
real, corrected `@context-retriever` CLI invocation shape (venv path, index-dir, workspace-root,
the corrected `.claude` platform-root, `--top-k 5`), an explicit instruction that it must formulate
its own query and decide for itself whether to run it at all, and an explicit instruction to report
verbatim whether it queried, its exact query text, and what it did with the results. No treatment
arm was given a pre-vetted query string or any hint about vault contents. Each arm's role matched
its command's own frontmatter (`Orchestrator` for `/plan` and `/prepare-release`, `Tech Lead` for
case 3's own review command, `Security Engineer` for `/security-audit`).

Each arm's real output file was copied, unmodified, into its own case-shaped fixture directory at
the exact relative path its case's real `expect.py` expects (`fixture/docs/plans/*-plan.md`,
`fixture/changelog.md`, `fixture/review.md`, `fixture/audit.md` ×2). The real, unmodified
`expect.py` for each case was loaded via `importlib.util.spec_from_file_location` (verbatim reuse
of `scripts/scorecard.py`'s own `load_expect_module()` pattern) and `check(case_dir)` called once
per arm.

## Real results

| # | Case ID | Control | Treatment | Retrieval used | Retrieval non-empty/relevant | Observable influence |
|---|---------|---------|-----------|-----------------|-------------------------------|------------------------|
| 1 | `plan-required-sections-compliant` | **True** | **True** | Yes | Yes | **Yes, clear and traceable.** Treatment added a "Process Notes (from repository conventions)" section entirely absent from control, containing three claims each independently traceable to a distinct retrieved chunk: branch/MR-flow policy, "reviewers do not modify what they review," and the two-retry-then-escalate rule. |
| 2 | `prepare-release-changelog-grouping-compliant` | **True** | **True** | Yes | Yes (topically) | **No clear distinctive influence.** Treatment's checkpoint explicitly credits retrieval with confirming the three-verdict/`CONDITIONAL_PASS`-tracks-conditions convention, but control independently produced an equivalent `CONDITIONAL_PASS` verdict with tracked conditions with no retrieval at all — this behavior is already mandated by the command template's own Rails, not distinctively attributable to the retrieved content. |
| 3 | `code-review-fail-blocker-details` | **True** | **False** | Yes | Yes | **Minimal/ambiguous.** Treatment added an explicit disclosed "Retrieval consultation" section citing the two-retry rule and "reviewers don't fix what they review" — but control independently stated the identical "max-2 allowed before user escalation" convention with no retrieval. The `expect.py` **False** is unrelated to retrieval content: treatment presented its per-blocker Owner in a markdown table column header ("`| ... | Owner | Retry Guidance |`") rather than the literal bolded inline field `**Owner**:` the check's regex requires; control happened to use the literal bolded form. |
| 4 | `security-audit-coverage-consistency` | **True** | **False** | Yes | Yes (topically) | **No clear distinctive influence found.** The `expect.py` **False** is a literal-format mismatch, not a content/retrieval issue: treatment's matrix and declared count were internally consistent (9 rows, "9/10" declared) but written as `"## VERDICT: FAIL"` plus `"**Declared OWASP coverage: 9/10 categories assessed**"` (one bolded sentence) instead of the template's own literal `"## VERDICT"` + `"**OWASP coverage**: 9/10"` field-label pattern; the check's regex requires the latter exact adjacency. |
| 5 | `security-audit-verdict-fields-compliant` | **True** | **True** | Yes | Yes (topically) | **No clear distinctive influence found.** Treatment's self-report credits retrieval with shaping its structured per-blocker field format (`severity=`/`owner=`/`escalation=`/`retry_attempt=`) "rather than inventing that structure independently," but control produced a materially equivalent structured field format with no retrieval at all — undercutting that specific attribution claim on direct comparison. |

**Retrieval query texts used (verbatim, agent-formulated, not hinted):**
1. "conventions for planning and reviewing a background sync/reconciliation job between local state and a remote service"
2. "release checklist and changelog format conventions for emage.code minor version release, including changelog grouping (Features/Fixes/Breaking Changes/Internal), release checkpoint document structure, and release gate verdict format"
3. "tech lead code review verdict format and gate handling conventions for payment webhook security review"
4. "security audit conventions for admin CLI authentication and authorization review, verdict format, access control policy"
5. "payments gateway service security audit conventions: OWASP verdict format, secrets management, crypto policy, and severity gate rules for CRITICAL findings"

All five queries were independently re-run by the orchestrator against its own separately-built
index and confirmed non-empty and substantively matching each treatment arm's own self-reported
results (not accepted on self-report alone). Every one of the 5 queries' top hit was the vault's
`validation-gate-verdict-protocol.md` entry — a genuinely disclosable finding that runs counter to
Finding 5's own pre-registered prediction of "likely low/no-relevant-hit trials": because every one
of these 5 cases' own command templates centers on a structured VERDICT block, a vault entry about
verdict *semantics* scored as topically relevant across all five, even though the vault still has
no entry about any command's specific field-formatting or heading conventions — exactly the gap
that the two `expect.py` **False** results above turned on.

## Non-regression floor — reported exactly as measured, per Finding 3

**Control pass rate: 5/5. Treatment pass rate: 3/5.** The floor stated in `plan-045` Finding 3
("treatment pass rate must not be lower than control pass rate") **was not met** in this literal
Tier 1 batch. This is reported as the real, measured result, not explained away: at `k=1`, a single
trial's stylistic choice (a table-header field vs. a bolded-inline field; a `"## VERDICT: FAIL"`
heading vs. a `"## VERDICT"` heading with a separate `**Status**:` field) fully determines a binary
pass/fail outcome, and neither of the two treatment shortfalls traces to the substantive content
the retrieval call contributed — both trace to formatting choices any live session, retrieval or
not, could independently make. This is precisely the statistical-resolution fragility Finding 3
itself warned `k=1` would have, now empirically observed rather than merely predicted. It does not,
on its own, support a claim that retrieval degrades quality; it also does not support a claim that
the floor was met. Both must be held simultaneously and honestly.

## What this does and does not mean

This is 5 cases, one trial per arm each — still a small-sample, `k=1` measurement, now spanning
all five of the suite's distinct commands for the first time (T484/T487 only ever exercised
`/new-feature`). It demonstrates the live-dispatch/scratch-isolation/`expect.py`-reuse mechanism
generalizes across all four other command roles (`orchestrator`, `tech-lead`, `security-engineer`)
without modification. It surfaces one clear, traceable instance of retrieval genuinely and
distinctively shaping treatment output (case 1) and three cases where retrieval was consulted,
returned real and topically-relevant results, but produced no content distinguishable from what an
un-retrieved control session already independently produced. It does **not** close T458 (the full
20-case harness with a pre-registered "measurably improve" threshold) or T456 (the ship-gate
measurement) — both remain exactly as they were before this task, `pending`/`blocked`. It does not
touch T457 or T483. **Tier 2 (the 4-trial noise probe) is explicitly out of scope for this task**,
per the orchestrating session's own direct instruction this turn, and remains fully undispatched.

## Constraints

- Never touch `feature/T475-codex-platform-integration`.
- Never edit anything under `tests/golden/**` — `expect.py` read/imported only, in all 5 cases.
- Never edit `scripts/scorecard.py` or `docs/benchmarks/tb-subset.json`/`.md`.
- No new paid/metered API usage beyond ordinary interactive-session dispatch.
- Did not install new dependencies into this repo's own dependency manifests — throwaway-venv only
  (`fastembed==0.8.0`, outside the repo).
- **No vault growth** — `implementation/knowledge/memory/{project,general}/` unchanged at 11 files
  before and after this task, independently confirmed.
- This task does not touch T456, T457, T458, or T483.
- Tier 2 (the 4-trial noise probe on `new-feature-plan-doc-compliant`) is explicitly out of scope
  for this dispatch and was not attempted.

## Expected Outputs

1. Ten real, on-disk scratch runs (outside the repo, in plain temp directories — not committed).
2. Ten real boolean `check()` results (5 cases × 2 arms), reported in the table above.
3. This brief's own results section, filled in with what actually happened.
4. `docs/tasks/active-tasks.md` updated with this row at status `in_review` (not `done` — see Git
   workflow below; not moved to `completed-tasks.md` until the MR merges).

## Acceptance Criteria

1. All 10 arms' live sessions actually ran via the in-process `Agent` tool (not simulated) — true,
   verifiable via each dispatch's own `agentId`/token-usage metadata returned this session.
2. All 10 `check()` calls used the real, unmodified `expect.py` for each of the 5 cases, loaded via
   `importlib.util.spec_from_file_location`.
3. All 10 real booleans reported, whatever they are — 2 `False` results reported honestly, not
   suppressed or retried to force a different outcome.
4. `git diff` against `origin/develop` for this branch touches only this task brief and the ledger
   row — no changes under `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.*`,
   `.mcp.json`.
5. This brief's closure explicitly states it does not close T458 or T456, does not attempt Tier 2,
   and reports the non-regression floor exactly as measured (not met), per Finding 3's own
   discipline against inventing a threshold that flatters the result.
6. Self-referential ledger-defect sweep performed and passing (see below).

## Blocker Protocol

None encountered requiring escalation. One real, disclosed empirical finding (the
`--platform-root` / `.generated-manifest.json` requirement) is recorded above as a finding, not a
blocker — it was resolved directly, before any dispatch, by the orchestrator's own pre-dispatch
sanity check.

## Self-referential ledger-defect sweep

Re-derived the live, current top-tier component id list directly
(`python3 implementation/scripts/check-maturity.py --root implementation --verbose`, run fresh this
session): **31 stable ids** (20 agents, 4 instructions, 7 skills) — matching T487's own count,
independently re-confirmed rather than trusted from that prior record. Swept this brief's own text
against all 31 — zero bare hyphenated-id hits (this brief refers to agent roles in plain prose,
e.g. "the tech-lead role" rather than any stable skill/instruction id). Also swept against the live
held-out case-ID list (`ls tests/golden/held-out/`, 6 entries) — zero bare mentions of any
held-out case ID anywhere in this brief (deliberately not listed by name here, per this project's
own guard against bare mentions of held-out case IDs anywhere outside `tests/golden/`); every case
ID named in this brief is one of the 5 real, `open`, non-held-out cases this task actually
dispatched.

## Git workflow

Branch `agent/orchestrator/T488`, created from `origin/develop` @ `7b99fb4`. Merge request opened
to `develop`, referencing `T488`, **left unmerged** per the orchestrating session's explicit
instruction this turn ("do NOT run `glab mr merge` — hand it back to me").
