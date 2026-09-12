# Plan 044 — T458 first slice: a walking-skeleton live-execution trial for ONE golden case

> Filename: `plan-044-t458-first-slice.md`

**Status:** proposed — presented for review in this session's report, **NOT approved**. This
document does not author `docs/tasks/task-T458.md`'s actual dispatch brief and does not touch any
code. It is an investigative/scoping pass only, exactly mirroring how `plan-043-phase4-task-tier-
routing-detailed-planning.md` was treated: written, committed via its own docs-only MR, and left
sitting at `proposed` until the top-level session/user explicitly approves a specific next step.
**No task brief may be authored and no code may be written on the strength of this document alone.**

**Based on:** `docs/tasks/task-T458.md` (re-read in full, fresh, from `origin/develop` this
session — the live-execution-harness brief this plan investigates a first slice of);
`docs/plans/plan-040-t458-golden-live-harness-followup.md` (re-read in full, fresh — the prior,
still-`proposed`, not-approved planning pass this document follows on from, re-verified rather
than trusted from any earlier summary); `docs/artifacts/golden-suite-format-v1.md` §2.2/§4
(the `expect.py`/`case.yaml`/`brief.md` contract this slice reuses unmodified); `scripts/
scorecard.py` (the exact `importlib.util.spec_from_file_location` / `check(case_dir)` invocation
pattern this slice re-uses verbatim); `docs/artifacts/protected-paths-v1.md` §5 (the exception
process this document finds is **not** needed — see Finding 1); `docs/artifacts/task-tier-schema-
v1.md`, `implementation/knowledge/instructions/model-routing-policy.md`, `implementation/
knowledge/instructions/mechanical-tier-escalation-policy.md` (T440–T442, all landed after
`plan-040` was written — re-read fresh this session to check whether they change T458's scope; see
Finding 2); `docs/artifacts/context-retriever-v1.md` §2/§2.1 (the real, current invocation
mechanism for `@context-retriever` — a direct in-process Python/CLI call, not nested agent
dispatch — this document's design leans on that fact directly); `implementation/knowledge/
commands/new-feature.md` (read in full — the literal `/new-feature` template, including its
`agent: "orchestrator"` frontmatter field, which is load-bearing for this document's proposed
design); `implementation/knowledge/agents/devops-engineer.md` (T458's assigned owner's real tool
grant, re-checked fresh — see Finding 3); `docs/tasks/active-tasks.md` (re-read fresh from
`origin/develop`, confirming current ledger state).

## 0. Re-verified start conditions (fresh this session, not trusted from any prior summary)

- `origin/develop` HEAD is `2ef0c1c` (`Merge branch 'agent/devops-engineer/T443' into 'develop'`),
  confirmed via `git fetch origin` + `git rev-parse origin/develop` this session. Matches the
  session's stated expectation exactly.
- `docs/tasks/active-tasks.md` on `origin/develop`, re-read fresh: `T458` — **pending**, owner
  `devops-engineer`, priority `P1`, depends on `None`, last update `2026-09-09`. `T456` —
  **blocked**, depends on `T454 (done)`, `T455 (done)`, `T458 (pending)`. `T457` — `pending`. `T483`
  — `pending`. The ledger's own `T443` closure note (already present on `origin/develop`) states
  plainly that Phase 4's four scaffolding tasks (T440–T443) are `done` but Phase 4's *substantive*
  gates remain open, "blocked on the same live-execution-harness gap already tracked at `T458`
  (pending) / `T456` (blocked)" — i.e. the ledger itself, independent of this session's framing,
  already identifies T458 as the real next blocker.
- `docs/plans/plan-040-t458-golden-live-harness-followup.md`, re-read in full fresh: its own header
  states `**Status:** proposed — presented for review in this session's report. T458 is recorded
  and scoped, **not dispatched this session**.` Its Approval section has zero checked boxes. This
  confirms plan-040 is **still not approved for dispatch** — the prior session finding was correct
  and remains true; nothing on `origin/develop` has changed that status.
- `docs/tasks/task-T458.md`, re-read in full fresh: its own header states `**Status:** pending —
  recorded and scoped this session, **not dispatched this session**`. Confirmed not dispatched.

## Finding 1 — the `expect.py`/`check(case_dir)` bridge needs NO protected-path exception

Investigated directly, not assumed either way, per this session's explicit instruction. Read
`docs/artifacts/golden-suite-format-v1.md` §4.1's canonical interface:

```python
def check(case_dir: Path) -> bool: ...
```

`case_dir` is a **parameter**, not a hardcoded path — `scripts/scorecard.py` already calls it as
`module.check(case_dir)` for whatever `case_dir` its own discovery loop found. Read the real,
current `expect.py` body of **all 20 real golden cases** on `origin/develop` (`git ls-tree` +
per-file read; grepped every file for `__file__`, `os.getcwd`, hardcoded `tests/golden` path
components, or any other anchor outside the `case_dir` argument): **zero** cases anchor to
anything other than the `case_dir` argument passed in. Every case's `check()` body does
`case_dir / "fixture" / <relative-path>` (e.g. `case_dir / "fixture" / "docs" / "plans"`,
`case_dir / "fixture" / "review.md"`) and every case's CLI wrapper (`main()`) does
`check(Path(sys.argv[1]).resolve())` — a directory supplied at call time, not compiled in.

**Consequence:** the harness can call a real case's real, unmodified, on-disk `expect.py`'s
`check()` function against a **scratch directory that is not `tests/golden/<case-id>/`at all** —
by loading the module via `importlib.util.spec_from_file_location` (the exact, already-used
`scripts/scorecard.py` pattern — literally re-run its `load_expect_module()`-equivalent logic
unmodified) and calling `module.check(scratch_case_dir)`, where `scratch_case_dir` is a live-run
workspace laid out so that `scratch_case_dir / "fixture" / <the same relative path the real case
expects>` exists. **No edit to `expect.py`. No edit to anything under `tests/golden/**`. No copy of
`expect.py` into a scratch location either** — the real, checked-in file is read-only-imported in
place, exactly as `scripts/scorecard.py` already does today. This resolves T458's own anticipated
blocker ("if `expect.py`'s existing contract genuinely cannot be pointed at a live-run's candidate
output without a protected-path edit... report a blocker") in the negative: **no exception request
is needed for this mechanism**, for any of the 20 cases that exist today. If a future case's
`expect.py` is authored differently (anchoring to `__file__`, say), that would need re-checking at
that time — this finding is scoped to the 20 real cases that exist on `origin/develop` today, not a
guarantee about hypothetical future cases.

## Finding 2 — T440–T443 change what a live run's results *could* eventually feed, not what this slice must do

`plan-040` predates T440–T443 by two days and could not have anticipated them. Re-reading
`task-tier-schema-v1.md`, `model-routing-policy.md`, and `mechanical-tier-escalation-policy.md`
fresh: none of them require anything of T458 directly (none reference `T458` or the golden suite's
live-execution path). The connection is one-directional and forward-looking: `scripts/
scorecard.py`'s `model_tier`/`model_outcome` fields (added by T443, both hardcoded `None` today,
`scripts/scorecard.py`'s own docstring: *"a future, separately scoped task... is expected to be the
actual producer that writes non-null values into these two fields"*) describe **exactly** the kind
of result a live-execution harness could eventually produce (which tier a case's command was
routed at, and whether that live run passed/failed/escalated). **This first slice does not touch
`scripts/scorecard.py` and does not attempt to populate those fields** — doing so would require
its own fresh protected-path exception decision (T443 already used the one pre-approved exception;
`task-T458.md`'s own constraints explicitly say a second edit is not pre-approved and needs a fresh
decision, which this document does not request). Recorded here only so a future dispatch does not
have to re-derive the connection: **a live-run's per-case pass/fail *is* plausible future input to
`model_tier`/`model_outcome`, but wiring that up is out of scope for T458's first slice and remains
a separately-scoped, separately-authorized future step.**

## Finding 3 — a real, previously-unflagged tool-grant gap in the assigned owner

`task-T458.md`'s own Constraints section requires confirming the assigned agent's tool grant
*before* starting, citing this repo's repeated history of exactly this gap (T418/T410/T420/T451/
T415/T455). Checked `implementation/knowledge/agents/devops-engineer.md` fresh this session:
`tools: [read, search, edit, execute, web, mcp__gitlab, mcp__fetch]`. **No `agent` tool.** Cross-
referencing the live Agent-tool roster available in this very session: only orchestrator-shaped
roles (`Orchestrator`, `PoC Orchestrator`) carry the `Agent` tool that lets one dispatched session
launch another. `devops-engineer` cannot.

This matters concretely because T458's Objective literally requires "running two arms per case"
as live agent sessions — and "the existing Claude Code agent-dispatch mechanism" is ambiguous
between two real, different things:

1. **The in-process `Agent` tool** (what this orchestrator session uses for every delegation in
   this project, e.g. every `T440`–`T458` dispatch) — requires the `agent` tool grant, which
   `devops-engineer` does not have and, per this repo's own precedent, should not be unilaterally
   widened (T415/T418/T455 all reassigned the task rather than widening a tool grant).
2. **The standalone `claude` CLI binary, invoked as a subprocess via Bash** — genuinely present in
   this environment (`which claude` → `/home/emage/.local/bin/claude`, version `2.1.220`,
   confirmed live this session) and invocable by any role with the `execute` tool, including
   `devops-engineer`. This is a real, different mechanism: a fresh, separate Claude Code process
   with its own context window, its own cwd, and (per `context-retriever-v1.md` §2.1's own
   documented real invocation shape — "a direct in-process Python call from an agent's Bash-backed
   `execute` tool grant," not nested agent dispatch) is arguably the more literal, more faithfully
   "reused" mechanism, since it does not require anything beyond a tool grant `devops-engineer`
   already has.

**This is now the single most important open decision for T458**, more fundamental than Finding 1:
whichever design is chosen determines whether T458 can be dispatched to `devops-engineer` as
currently assigned, or whether the first live-trial step must be performed by (or delegated
through) an orchestrator-tier role, or whether `devops-engineer`'s tool grant needs a scoped
addition (a decision this document does not make — it only surfaces the gap, per this repo's
own "never silently widen a tool grant" discipline).

## Recommended walking-skeleton scope (not yet authorized — proposed for approval)

### Which single case

**`tests/golden/open/new-feature-plan-doc-compliant`** (`command: /new-feature`, `status:
expected_pass`). Chosen over alternatives for concrete, disclosed reasons:

- Its `expect.py` requires exactly one artifact (`fixture/docs/plans/feature-<slug>.md` containing
  four required headers) — the cheapest, lowest-ambiguity bar of any `/new-feature` case (compare
  `new-feature-checkpoint-line-compliant`, which requires the agent to additionally reach Phase 3
  of the command template and write a checkpoint — a materially larger live session for a first
  proof of mechanism).
- It is in `open/`, not `held-out/` — no isolation-guard interaction to reason about for a first
  slice.
- It is `expected_pass`, not `known_failing` — a clean binary signal (either the mechanism proves
  the case can pass live, or it doesn't) rather than a case where "pass" would be a surprise
  requiring its own investigation.
- Its own `brief.md` "Provenance" section already flags itself as hand-authored/illustrative
  ("Brief (illustrative — not executed live)") — this is itself an open risk, not a reason to
  avoid the case (see Risks below): a walking skeleton is exactly the right, cheap place to
  discover whether that illustrative brief, fed to a real live session, actually produces
  structurally-compliant output, before spending any effort finding out on a harder case.

### What the two arms concretely are (informed by Finding 3, both options kept open)

For **this specific case**, `implementation/knowledge/commands/new-feature.md`'s own frontmatter
declares `agent: "orchestrator"` — i.e., invoking `/new-feature <brief>` for real *is* running the
orchestrator role against that command's literal template with `{{input}}` substituted by the
case's `brief.md` body. This is a load-bearing, case-specific fact (re-confirmed by reading the
command file directly this session), not an assumption:

- **Control arm:** dispatch a live session using `new-feature.md`'s template (with `{{input}}` =
  this case's `brief.md` text) as the task, working directory set to a fresh, isolated scratch
  directory (never the main checkout — a plain temp directory, not a new git worktree, is
  sufficient for a Phase-1-shaped plan doc and avoids any interaction with this repo's worktree
  discipline for a throwaway trial). No mention of, or access to, `@context-retriever` or the
  retrieval CLI.
- **Treatment arm:** the identical dispatch, in its own separate fresh scratch directory, with one
  added instruction: the session may consult prior context via
  `python3 -m implementation.runtime.memory.context_retriever <query> <workspace_root>
  <platform_root> <top_k>` (the real, documented CLI invocation shape from `context-retriever-
  v1.md` §2/"What you do" step 2) before producing its plan doc. This sidesteps Finding 3's
  Agent-tool-roster ambiguity entirely for the *inner* retrieval call — it is a Bash/`execute`
  CLI invocation, not a nested Agent-tool dispatch, and is available regardless of which of
  Finding 3's two dispatch mechanisms is chosen for the *outer* live session.
- Both arms use the *same* outer dispatch mechanism (whichever Finding 3 resolves to) — the only
  difference between arms is the retrieval instruction/capability, per T458's own Objective #2.

### What "pass/fail" means for this slice (deliberately narrow — not T456's ship-gate claim)

1. Run each arm exactly once (a single trial per arm — no `k`-run design, no statistical claim;
   T458's own Blocker Protocol explicitly treats live-session non-determinism as a *separate*,
   disclosable design question for the full harness, not something this slice needs to solve).
2. After each arm's session completes, its scratch directory's actual on-disk output is inspected;
   whatever file the live session wrote is placed at `<scratch_case_dir>/fixture/<the exact
   relative path this case's real expect.py expects>` — for this case, that means the live
   session's produced plan doc ends up reachable at `<scratch_case_dir>/fixture/docs/plans/
   feature-<slug>.md` (a copy or a directory layout construction, not a modification of anything
   under `tests/golden/**`).
3. The real, unmodified, checked-in `tests/golden/open/new-feature-plan-doc-compliant/expect.py`
   is loaded via `importlib.util.spec_from_file_location` (verbatim reuse of `scripts/
   scorecard.py`'s own pattern) and `check(scratch_case_dir)` is called once per arm.
4. **Pass condition for this slice**: the mechanism runs end-to-end for both arms without a
   `type: technical` blocker, and each arm's `check()` call returns a real `True`/`False` — a
   genuine boolean grounded in a real on-disk file the live session actually wrote, not a stub, not
   a hand-constructed fixture. **The slice succeeds if the mechanism works and produces two real,
   honestly-reported booleans — regardless of what those booleans are.** A `False` result for
   either or both arms is a valid, useful outcome (it would mean the live session didn't produce a
   structurally-compliant plan doc) and must be reported as such, not treated as a mechanism
   failure. This is explicitly **not** T458's full Objective #5 ("measurably improve" threshold,
   pre-registered before any comparison run) — one case, one trial per arm, cannot support a
   suite-wide improvement claim, and this document does not claim otherwise.
5. What this slice explicitly does **not** attempt: the other 19 cases; a `k`-run design for
   noise; a pre-registered "measurably improve" threshold (that's meaningful only across a real
   multi-case comparison); populating `scripts/scorecard.py`'s `model_tier`/`model_outcome` fields
   (Finding 2); resolving T456's ship-gate question.

## Open questions / risks requiring a decision before any real dispatch

| # | Question / risk | Why it matters | Status |
|---|---|---|---|
| 1 | Which outer dispatch mechanism — in-process `Agent` tool (orchestrator-tier only) or a `claude` CLI subprocess (available to any `execute`-granted role)? | Determines whether `devops-engineer` can execute T458 as currently owned, or whether ownership/tooling needs to change (Finding 3) | **Unresolved — needs an explicit decision before dispatch, not a silent implementer choice** |
| 2 | Is `devops-engineer` still the right owner given Finding 3, or should this slice be executed by/through an orchestrator-tier role, or should `devops-engineer`'s grant gain a scoped addition? | This repo's own precedent (T415/T418/T455) is "reassign, don't widen a grant" — but none of those precedents involved needing the `Agent` tool specifically; this may be a genuinely new category of gap | **Unresolved — flagged for user/orchestrator decision, not resolved here** |
| 3 | Does feeding `new-feature-plan-doc-compliant`'s `brief.md` to a real live session actually produce output at the expected relative path, given the brief's own "(illustrative — not executed live)" self-description? | The case was authored assuming it would never be executed; a live run might reveal the brief is underspecified for a real session (e.g. no explicit target filename), which would be a real, useful finding, not a mechanism failure | **Open — this is precisely what the walking skeleton is for; expected to be answered empirically, not predicted here** |
| 4 | Does the chosen outer dispatch mechanism constitute a "paid/recurring-cost API call" requiring authorization under `task-T458.md`'s own Constraints, or is it covered by ordinary interactive-session usage (as every other dispatch this session already is)? | T458's Constraints treat a metered API call as a `type: external`, `severity: critical` blocker needing explicit prior cost authorization; a `claude` CLI subprocess launched from within an already-running interactive session may or may not fall under the same usage/billing envelope as this session itself | **Open — needs confirmation before any live dispatch, not assumed** |
| 5 | Scratch-directory isolation: plain temp directory vs. a new git worktree? | A plan-doc-only case does not need git history, but if a later case in the eventual full suite needs to validate against a realistic repo tree (e.g. a case whose `expect.py` checks cross-file consistency), a plain temp dir may not be representative | **Open but low-stakes for this specific case — a plain temp directory is proposed as sufficient for this slice only, not a general answer for the full harness** |

## What this document is not

- It is not `docs/tasks/task-T458.md`'s dispatch (that brief already exists, unchanged, from
  2026-09-09, and is not modified here).
- It is not a new task brief for "T458 first slice" — no `docs/tasks/task-T4xx.md` is authored by
  this document.
- It does not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/
  `.md`, `.mcp.json`, or `feature/T475-codex-platform-integration`.
- It does not authorize any paid/metered API usage.
- It is not an approval of plan-040 — plan-040 remains `proposed`, unapproved, exactly as found.

## Approval

- [ ] User reviews Findings 1–3 and the five open questions above
- [ ] User decides Question 1/2 (dispatch mechanism + real T458 owner) before any task brief is
      authored
- [ ] User approves (or modifies) the recommended walking-skeleton scope as the next authorized
      step, distinct from approving the full `task-T458.md` brief
- [ ] Plan locked; revisions create `plan-044-t458-first-slice-v2.md`
