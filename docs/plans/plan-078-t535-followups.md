# plan-078 — the two defects T535's adjudication left

**Status: scoped 2026-09-26, awaiting approval to dispatch.**
Based on: `docs/artifacts/batch-manifest-resolution-v1.md`; `docs/tasks/task-T535.md`;
`docs/decisions/ADR-007-command-contract-authority.md`; `docs/artifacts/protected-paths-v1.md` §5.

## 0. Two defects, one of which is not about `/batch` at all

| # | Defect | Task |
|---|---|---|
| 1 | `/batch`'s `expect.py` now asserts forms no document declares | **`T541`** |
| 2 | `agents/orchestrator.md` instructs a protected-branch violation | **`T542`** |

`T535` escalated the first as a blocker with an element-for-element spec, and found the second while
reading — it is unrelated to `/batch` and was correctly reported rather than folded in.

## 1. `T541` — the checker outlived its contract, again

`T535` amended two clauses. Three of `expect.py`'s five elements now assert the **pre-amendment**
forms: `UNIT_ID_RE = ^U\d+$` and `BRANCH_RE = ^batch/…$` match patterns no document declares any
more, and assertion C requires a `branch` in a ledger row the amended contract says has none.

The case is still correctly `known_failing` — `check()` returns `False` today and, verified by the
orchestrator, **would still return `False` against a fully conforming artifact.** So this is the same
shape as `T531`: *a check nobody can trust is worse than a red case.*

**`ADR-007` Validation 1 binds in the unusual direction: two of the re-derived elements are strictly
stronger, so the risk here is over-strengthening.** `T535`'s spec is element-for-element and requires
≥ the current strength on every element; a re-derivation that goes further than the spec changes a
verdict nobody re-opened.

**The unresolved question `T535` deliberately left, which `T541` must answer:** `ADR-007`'s sibling
corollary distinguishes branch-1 amendments that change "only a name or path" — fixture updated, case
survives — from those that change the **artifact class**, which invalidate the case and require it to
be re-purposed. `T535` judged this amendment *arguably between the two* and refused to resolve it,
because resolving it **is** the re-derivation. `T541` holds the authorization, so it decides.

One datum that bears on the answer and was verified: **the fixture's ledger half already conforms**
to the amended step 5 with no edit — 7 cells, `T534`/`T535`/`T536`, Titles prefixed
`BATCH structured-logging …`. Only the `decomposition.md` half needs re-authoring, and its own
`brief.md` § Provenance records it as hand-authored, which `ADR-007` §5 permits re-authoring.

**Fold in the same authorization** — same case, same defect class, the `T530` precedent:

- `brief.md` says *"Five of step 5's fields map onto that schema"* and then lists **four**. Confirmed.
- `case.yaml` and `brief.md` both cite `validate-tasks.py:195`; it is now **288** (`C3` at **307**).
  The quoted code is still accurate; only the line numbers are stale.

## 2. `T542` — a document that tells the orchestrator to break branch protection

`implementation/knowledge/agents/orchestrator.md` § "Git Workflow Enforcement":

> - Docs (docs) → commit directly to develop (docs-only changes exempt)
> - Chore (chore) → commit directly to develop (maintenance-only changes exempt)

`git-workflow.md` — **`maturity: stable`**, `applyTo: "**"`:

> **There is no "it's just a doc update" exception.** A single-file, docs-only, or ledger-only change
> … requires exactly the same branch + MR flow as an application-code change.

**`ADR-007` branch 1 fires: an agent file contradicts a stable instruction.** But this one is not
merely a contradiction on paper — it is **operationally harmful, and it has already caused the failure
it describes.** `git-workflow.md`'s own Recovery Procedure records the precedent verbatim: the
orchestrator committed ledger transitions directly onto `develop` twice, and
`git push origin develop` was rejected both times with *"You are not allowed to push code to
protected branches on this project."*

So `orchestrator.md` instructs an action the remote refuses, and the repo has the scar tissue to prove
it. **Every orchestrator reading its own agent file is being told to do something that cannot work.**

The repair direction looks obvious — delete the two exemptions — but `T542` should confirm rather than
assume that no third document grants them, and check whether the same exemption language has
propagated to any other agent or command file, the way `/sprint-status`'s colour gap propagated to
`team-status.md` by duplication.

## 3. Sequencing and what none of these do

`T541` touches `tests/golden/**`; `T542` touches `implementation/knowledge/agents/`. **They do not
collide and may run in parallel** — but neither may run alongside `T538`, which also touches
`implementation/knowledge/` and would contend for the registry and projections.

Both are `P2`, so per `T524`'s correction they do not enter criteria 3/7's open-defect scan.
**Neither promotes anything.** `T541` may make `/batch`'s case flip; `/batch` still would not promote,
because it is `experimental` and must clear `experimental → beta` first — `T535` §8 established that
and it does not change here.
