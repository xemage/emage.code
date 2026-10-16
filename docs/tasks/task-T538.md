# T538 — `team-status.md` carries the same `in_review` colour gap

**ID:** T538
**Owner:** Tech Lead
**Status:** done
**Priority:** P2
**Tier:** mechanical
**Affects:** —
**Depends on:** T536 (merged 2026-09-26)
**Created:** 2026-09-26
**Based on:** `docs/plans/plan-077-parallel-round-findings.md` §1; `docs/tasks/task-T536.md`.

## 1. The defect

`implementation/knowledge/commands/team-status.md` step 7 carries the **identical** node-source bullet:

> - Read `docs/tasks/active-tasks.md` for pending/in_progress/blocked/in_review nodes

and the **identical** four `classDef` lines with the same hex values as `/sprint-status` had — but
**no `Color code:` bullet at all**. Verified.

So it is `T536`'s defect in a weaker form: nothing contradicts the bullet in prose, yet the template
cannot colour an `in_review` node.

## 2. The fix

Add `classDef inReview fill:#87CEFA` to the template, matching `T536` exactly for palette consistency
across the two commands.

**Decide and state whether to also add a `Color code:` bullet.** `/sprint-status` has one and this
command does not; adding one would make the pair symmetric and the colour mapping explicit, but it is
**new prose in a contract**, not just the missing value. Argue it either way — do not add it silently
and do not omit it silently.

**Do not resolve this by deleting `in_review` from the node-source bullet.** `T536` established why on
the merits, not merely by prohibition: `in_review` is a first-class state in `AGENTS.md`'s own machine,
so a DAG that cannot draw it cannot render a real sprint, and `ADR-007` branch 1 would fire in the
opposite direction and force the clause back.

## 3. The more interesting question — answer it

**The two commands are near-duplicates of that whole Mermaid section, which is *how* this defect
propagated.** Check whether any *other* command duplicates that block, and report what you find. A
copied section carries its gaps; if there is a third copy, this defect is not two instances but a
pattern, and that is worth knowing before someone fixes instance three by hand as well.

## 4. Scope

In scope: `implementation/knowledge/commands/team-status.md`, the generated projections and registry
via the generators below, and this brief's `**Status:**`.

Out of scope: anything under `tests/golden/**`; `scripts/scorecard.py`; any `maturity:` field;
`docs/tasks/active-tasks.md` and `docs/tasks/completed-tasks.md` — **archival is orchestrator-only, so
move no row.** `team-status` is `experimental`; nothing promotes either way.

After editing `implementation/knowledge/`, run **both** generators in this order:

```
node implementation/scripts/sync.mjs
python3 implementation/scripts/generate-registry.py
```

`implementation/scripts/sync.mjs`, **not** `scripts/sync.mjs` — the wrong path fails
`MODULE_NOT_FOUND` and silently no-ops if stderr is suppressed. And `sync.mjs --check` alone does
**not** catch registry drift; forgetting `generate-registry.py` has broken two MRs in this phase.

- **Root-drift gate (added 2026-09-30).** Once T543's parity gate (MR !420) is in `develop`, every
  change under `implementation/knowledge/` that does not refresh the repo root must add the affected
  root paths to `tests/_baselines/root-install-drift.json` **in the same MR**, or the pipeline goes
  red. `python3 -m tests.functional.test_root_install_parity --print-drift` prints the exact list.
  If you cannot run it, say so and the orchestrator will.

## 5. Verification

```
python3 tests/run.py                  # BASELINE FIRST — measure it, do not trust this brief
python3 scripts/scorecard.py --check  # READ-ONLY. Never the write mode as a check.
python3 implementation/scripts/check-maturity.py --root implementation
python3 implementation/scripts/check.py --registry --root implementation
node implementation/scripts/sync.mjs --check
python3 docs/tasks/validate-tasks.py
git status --porcelain
```

**Measure the baseline yourself.** Four different figures have circulated in this phase's briefs and
every one was wrong at some point; it should currently be **806 / OK / 23 skipped**, but verify.
`check-maturity.py` must stay `79 / 0` with an unchanged distribution.

## 6. Ledger, git, blockers

Set this brief's `**Status:**` to `in_review`; move no ledger row. Branch `agent/tech-lead/T538`.
Commit message ends with exactly `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

**No merge request, no merge, no self-merge.**

If `git push` fails with `glab auth git-credential: "erase" is an invalid operation` and/or
`HTTP Basic: Access denied`: known environment transient, not your fault, credentials are not broken,
and you must not touch any `glab` or `git config credential.*` setting. Retry two or three times, then
report that the commit is on the local branch.

Blockers: type and severity; max 2 retries. Report anything the brief got wrong.
