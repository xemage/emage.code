# T558 — `/batch` cites `commands/plan.md`, a path installed targets never have

**ID:** T558
**Owner:** Technical Writer
**Status:** done
**Priority:** P2
**Tier:** mechanical
**Affects:** —
**Depends on:** T557
**Created:** 2026-10-01
**Based on:** `docs/plans/plan-088-audience-lint.md` §2; `tests/_baselines/command-audience-paths.json`;
`docs/artifacts/command-audience-resolution-v1.md` §2.3 and §4.3 (class C / rule B4).

## 1. The defect — found by the T557 lint on its first run

`/batch` is `audience: both`, but it cites `` `commands/plan.md` `` — a knowledge-tree path — at step 2 (line ~19)
and again in its "Important" section (line ~45). An installed project has no `commands/plan.md`; it has the
`/plan` command in its platform folder (`.claude/commands/plan.md`, `.github/prompts/plan.prompt.md`, …). T546
classed this as class C and prescribed rule B4: **cite a component by name, never by authoring-tree path**.

`plan-087` §2 wrongly said all six of T546's body edits had landed; four tasks fixed four commands, and
`/batch`'s never happened. This task is that edit.

## 2. The change

Replace each `` `commands/plan.md` `` reference with a by-name reference to the `/plan` command, keeping the
meaning (e.g. "the structure `/plan` step 5 declares"). Read both sites in full first; keep the step numbering and
all other text unchanged.

**In the same change, the orchestrator removes the `/batch` entry from
`tests/_baselines/command-audience-paths.json`** — the lint fails on a declared entry that is no longer a
violation, so the fix and the baseline edit must land together. You cannot run the lint; the orchestrator will.

## 3. Constraints

- **Write scope:** `implementation/knowledge/commands/batch.md` and this brief's `**Status:**` line (to
  `in_review`). Nothing else.
- **You have no Bash.** Hand back uncommitted. The orchestrator runs both generators, declares any new repo-root
  drift, edits the lint baseline, runs every gate, and commits.
- **`tests/golden/**` is protected and you hold no grant.** `/batch` has a golden case
  (`batch-manifest-ledger-schema-conflict`); the orchestrator will check whether its `brief.md` or `expect.py`
  quotes the changed lines before committing. Do not read or edit `tests/golden/`.

## 4. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`. If anything in
this brief is wrong, report it.
