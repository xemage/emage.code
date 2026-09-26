# T542 — `orchestrator.md` instructs a protected-branch violation

**ID:** T542
**Owner:** Tech Lead
**Status:** done
**Priority:** P2
**Tier:** standard
**Affects:** —
**Depends on:** —
**Created:** 2026-09-26
**Completed:** 2026-09-26
**Based on:** `docs/plans/plan-078-t535-followups.md` §2;
`docs/artifacts/batch-manifest-resolution-v1.md` (where it was found);
`docs/decisions/ADR-007-command-contract-authority.md`.

## 1. The contradiction

`implementation/knowledge/agents/orchestrator.md` § "Git Workflow Enforcement", lines 98–99:

> - Docs (docs) → commit directly to develop (docs-only changes exempt)
> - Chore (chore) → commit directly to develop (maintenance-only changes exempt)

`git-workflow.md` — **`maturity: stable`**, `applyTo: "**"`, line 53:

> **There is no "it's just a doc update" exception.** A single-file, docs-only, or ledger-only change
> … requires exactly the same branch + MR flow as an application-code change.

**`ADR-007` branch 1 fires: an agent file contradicts a stable instruction.** Verify that from the
documents rather than taking it from this brief.

## 2. Why this is not a paper cut

It is **operationally harmful, and it has already caused the failure it describes.**
`git-workflow.md`'s own Recovery Procedure records the precedent verbatim: the orchestrator committed
ledger transitions directly onto `develop` twice, and `git push origin develop` was rejected both
times with *"You are not allowed to push code to protected branches on this project."*

So `orchestrator.md` instructs an action the remote refuses, and the repository has the scar tissue
to prove it. **Every orchestrator reading its own agent file is being told to do something that
cannot work** — and the two exemptions name precisely the change classes an orchestrator handles most
(`docs` for ledger transitions and checkpoints, `chore` for maintenance).

## 3. The fix looks obvious — confirm it rather than assuming

Deleting the two exemptions is the likely repair, and `ADR-007` §5 does not obstruct it: you would be
removing a *permission* that a higher authority already denies, not weakening a check.

**But confirm two things first:**

1. **That no third document grants the exemption.** If some instruction or skill also carves out
   docs-only commits, the defect is wider than one file and the verdict must say so.
2. **Whether the same exemption language has propagated.** `/sprint-status`'s colour gap turned out
   to exist in `team-status.md` too, by duplication — a copied section carries its gaps. Check the
   other agent files and the commands for the same wording, and **report what you find even if it is
   nothing.** "I checked and there is exactly one instance" is a useful result.

Also decide, and state: **should the lines be deleted, or replaced with the correct routing?** A bare
deletion leaves the section silent on `docs`/`chore`, which is arguably how it should have read; an
explicit "→ branch + MR like everything else" is more useful to a reader but is new prose. Argue it.

## 4. Scope

In scope: `implementation/knowledge/agents/orchestrator.md`, the generated projections and registry
via the generators below, and this brief's `**Status:**`.

Out of scope: `git-workflow.md` itself (it is the correct document and needs no change); anything
under `tests/golden/**`; `scripts/scorecard.py`; any `maturity:` field; `docs/tasks/active-tasks.md`
and `docs/tasks/completed-tasks.md` — **archival is orchestrator-only, so move no row.**

**Note `orchestrator` is one of the two remaining `experimental` agents**, blocked on `ADR-007`
verdict A via a `/plan` golden case. This task does not change that and **must not touch its
`maturity:` field.**

After editing `implementation/knowledge/`, run **both** generators in order:

```
node implementation/scripts/sync.mjs
python3 implementation/scripts/generate-registry.py
```

`implementation/scripts/sync.mjs`, **not** `scripts/sync.mjs` — the wrong path fails
`MODULE_NOT_FOUND` and silently no-ops if stderr is suppressed. `sync.mjs --check` alone does **not**
catch registry drift; forgetting the second generator has broken two MRs in this phase.

## 5. Verification

```
python3 tests/run.py                  # BASELINE FIRST — measure it yourself
python3 scripts/scorecard.py --check  # READ-ONLY. Never the write mode as a check.
python3 implementation/scripts/check-maturity.py --root implementation
python3 implementation/scripts/check.py --registry --root implementation
node implementation/scripts/sync.mjs --check
python3 docs/tasks/validate-tasks.py
git status --porcelain
```

**Measure the baseline yourself** — five figures have circulated in this phase's briefs and all were
wrong at some point. It should be **824 / OK / 23 skipped**. `check-maturity.py` must stay `79 / 0`
with an unchanged distribution; evaluator-hash unchanged, since you touch no protected path.

## 6. Ledger, git, blockers

Set this brief's `**Status:**` to `in_review`; move no ledger row. Branch `agent/tech-lead/T542`.
Commit message ends with exactly `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

**No merge request, no merge, no self-merge.** And note the irony available here: this task is itself
a docs-class change to a knowledge file, and it goes through a branch and an MR like everything else.

If `git push` fails with the `glab auth git-credential: "erase" is an invalid operation` /
`HTTP Basic: Access denied` pair: known environment transient, not your fault, credentials are not
broken, and you must not touch any `glab` or `git config credential.*` setting.

Blockers: type and severity; max 2 retries.
