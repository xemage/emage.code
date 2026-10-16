# plan-079 — the root-projection sync gap, and a golden-case cleanup

**Status: scoped 2026-09-26, awaiting approval to dispatch.**
Based on: `docs/tasks/task-T542.md` and `docs/tasks/task-T541.md` (where both were found);
`AGENTS.md` § Knowledge Base; `docs/artifacts/protected-paths-v1.md` §5.

## 0. One of these is a systemic gap, the other is tidying

| # | Defect | Task |
|---|---|---|
| 1 | **repo-root projections are refreshed by no generator and checked by no gate** | **`T543`** |
| 2 | the `/batch` case's `U<n>` Titles, stale tag and stale id | **`T544`** |

## 1. `T543` — the gap that silently affects every knowledge fix

`implementation/scripts/sync.mjs` writes **only** under `implementation/.<platform>/`. The repo-root
folders — `.claude/`, `.cursor/`, `.gemini/`, `.github/`, `.opencode/`, `.pi/` — are the *installed*
projection, refreshed only by `scripts/install.sh --update`.

**And `sync.mjs --check` reports "no drift across 577 files" regardless**, because it only inspects
the `implementation/` tree. Both facts verified directly.

**The consequence is live and was demonstrated by `T542`.** That task removed a direct-commit
exemption from `orchestrator.md`, correctly regenerated all six `implementation/` projections, and
passed every gate — yet **`.claude/agents/orchestrator.md`, which is what the orchestrator actually
running in this repo reads, still says "commit directly to develop."** Nothing in CI notices.

This is not one task's oversight. Corroborating evidence gathered independently: **5 of 19 root
command projections already differed from `implementation/` before `T536` touched anything.** So the
root tree has been drifting for some time, and **every knowledge fix in this repo has silently failed
to reach the running agent** unless someone ran `install --update` afterwards.

`T543` decides what to do about it. The obvious candidates, none endorsed:

- **Extend `sync.mjs --check` to the root tree**, so drift is at least *visible*. Cheapest, and it
  makes the next occurrence loud instead of silent. But it would fail immediately and keep failing
  until someone syncs — which is arguably the point, and arguably an unmergeable gate.
- **Have `sync.mjs` write both trees.** Removes the gap entirely, but collapses a distinction
  `AGENTS.md` draws deliberately: the root folders are the *installed* artifact of a target project,
  not a generator output of this one.
- **A CI job or test asserting the two trees agree**, failing loudly on drift.
- **Document the gap and require `install --update` in the checkpoint protocol** — the weakest
  option, and it should be rejected on the record if chosen, because it is what the repo already
  implicitly does and it is how the drift accumulated.

**`T543` must also answer the prior question: is root drift a *defect* at all?** If the root tree is
genuinely a target-project artifact that this repo merely happens to contain, then it is *supposed*
to lag until installed, and the real defect is only that nothing says so. If it is meant to track,
five of nineteen files are wrong right now. **Those are different repairs and the task must pick
one**, not split the difference.

## 2. `T544` — three loose ends in one golden case

All three are in `tests/golden/open/batch-manifest-ledger-schema-conflict/`, all left by `T541`
because its grant excluded them, and all verified:

1. **The `U<n>` Titles.** The fixture's ledger rows read `BATCH structured-logging U1: …` where step 5
   declares `BATCH <slug>: <description>`. **This is the single largest remaining looseness in the
   case:** because of it, `expect.py` can only assert a non-empty colon-terminated slug rather than
   `^BATCH [a-z0-9][a-z0-9-]*: `. Strip the marker and the stricter form becomes assertable — which is
   the point of doing it.

   Note the irony worth preserving in the brief: the `U<n>` residue is *the abolished unit-ID scheme
   surviving inside the evidence offered for its own abolition.* And note that the orchestrator
   claimed twice that these Titles "already conform"; they conform cell-for-cell and not in the Title
   form, which `T541` caught.

2. **`case.yaml`'s `tags:` still contains `contract-drift`** on a case whose drift is resolved.
3. **The case id still reads `…-schema-conflict`** on a green case.

On (3), `T541` recommended *against* renaming, and that recommendation should be weighed rather than
overridden by tidiness: the id is referenced by `docs/benchmarks/scorecard-v6.12.0.{json,md}`,
`evaluator-hash-known-good-v7.json`'s `reason` field, and `batch-manifest-resolution-v1.md`. A rename
touches a published baseline and two historical records. **`T544` may keep the id and say why** — that
is a legitimate outcome.

## 3. The queue is not shrinking, and that is worth naming

After this plan the ledger holds **6 active** rows, the same count as three rounds ago. Each round has
closed two or three tasks and surfaced two or three more, because every task in this phase is
instructed to report rather than work around.

That is the system functioning as designed, not drift — `T518` established that a finding without a
row is a finding that gets lost. But it means **the phase will not converge by executing findings
alone**, and at some point the remaining items should be triaged for whether they are worth doing at
all rather than queued indefinitely. `T544`'s item (3) is the first candidate for "correctly declined".

## 4. Sequencing

`T543` touches `scripts/`, `.gitlab-ci.yml` or `tests/functional/` depending on its verdict; `T544`
touches one golden case directory and `docs/benchmarks/`. **They do not collide and may run in
parallel.** Neither may run alongside a task touching `implementation/knowledge/`.

`T544` will drift `tests_golden` and needs the usual escalation; `T543` will not unless its verdict
reaches a protected path, which it should not.
