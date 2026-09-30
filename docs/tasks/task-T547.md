# T547 — Four commands cite `04-protocols.md`, which exists nowhere in the repository

**ID:** T547
**Owner:** Technical Writer
**Status:** done
**Priority:** P2
**Tier:** mechanical
**Affects:** command/new-project, command/new-feature, command/new-poc, command/validate-workflow
**Depends on:** —
**Created:** 2026-09-26
**Based on:** `docs/artifacts/skillify-output-path-resolution-v1.md` §5.3;
`docs/tasks/task-T532.md`.

## 1. The finding, and its provenance

T532's architect flagged that `/new-project` step 1, `/new-feature` step 1 and `/validate-workflow`
step 5 all cite **`04-protocols.md`**, a file it found no trace of — and correctly marked the claim
**unproven**, because with no shell it could not prove absence.

The orchestrator proved it:

```
$ find . -name "04-protocols*" -not -path "./.git/*"     # no output
$ grep -rln "04-protocols" --include=*.md implementation/knowledge/
implementation/knowledge/commands/validate-workflow.md
implementation/knowledge/commands/new-feature.md
implementation/knowledge/commands/new-project.md
implementation/knowledge/commands/new-poc.md
```

The file does not exist. **And there are four citers, not three** — `new-poc.md` is a fourth the
architect did not name, which is exactly the kind of thing a directory listing finds and careful
reading misses.

Two of the four (`/new-project`, `/new-feature`) are **`stable`**.

## 2. What this task must establish first

**Do not delete the references until you know what they were for.** Three possibilities, and the
repair differs for each:

1. **Renamed.** A numbered-prefix document that was reorganised. Look for
   `implementation/knowledge/**/0*-*.md` and any surviving numbered series — if the series exists and
   `04` is the gap, the successor is probably identifiable by content. Check git history
   (`git log --all --diff-filter=D --name-only -- '*04-protocols*'`) — the orchestrator has **not**
   run this, so run it yourself and report the result either way.
2. **Never existed.** A plausible-looking citation that was written and never backed. Then the
   question is what the citing step actually needs, and whether the content lives elsewhere
   (`AGENTS.md` § Task Protocol and § Checkpoint Protocol are the obvious candidates, but **verify**
   rather than assuming — pointing four commands at the wrong replacement is worse than the dangling
   reference, which at least fails loudly).
3. **Real but uninstalled.** The T546 class: a file that exists in some other context and is simply
   not in this tree. §1's `find` covers the whole repository, so this is unlikely — but confirm.

## 3. Constraints

- **Write scope: `implementation/knowledge/commands/{new-project,new-feature,new-poc,validate-workflow}.md`
  only.** Nothing else.
- **You have no Bash.** ← **This is wrong for your role and you should read it carefully:** the
  Technical Writer has `Read`, `Edit`, `Write` and no shell. §2 asks you to run `git log`. **You
  cannot.** Report that as a `dependency` blocker and state precisely which command you need run and
  what you would conclude from each possible output; the orchestrator will run it and hand back the
  result. **Do not silently skip step 1 and default to possibility 2** — that is the failure mode this
  paragraph exists to prevent.
- **Both generators must run** after any change to `implementation/knowledge/`:
  `node implementation/scripts/sync.mjs` **and**
  `python3 implementation/scripts/generate-registry.py`. You cannot run them. Hand back uncommitted
  and say so; the orchestrator runs them and commits.
- **`tests/golden/**` and `scripts/scorecard.py` are protected paths.** No authorization here. Four
  of these commands have golden cases; if you conclude one must change, **report and stop.**
- Do not touch `AGENTS.md` (**T545** owns it) and do not introduce an `audience:` key (**T546** owns
  that question).

- **Root-drift gate (added 2026-09-30).** Once T543's parity gate (MR !420) is in `develop`, every
  change under `implementation/knowledge/` that does not refresh the repo root must add the affected
  root paths to `tests/_baselines/root-install-drift.json` **in the same MR**, or the pipeline goes
  red. `python3 -m tests.functional.test_root_install_parity --print-drift` prints the exact list.
  If you cannot run it, say so and the orchestrator will.

## 4. Acceptance criteria

1. Which of §2's three possibilities holds, with the evidence — including the `git log` result,
   obtained via the blocker route if necessary.
2. All four citations either repointed at a document that **exists** (quote the target's real path and
   the section that carries the needed content) or removed with the citing step rewritten so it still
   makes sense without the reference.
3. `new-poc.md` is included. It is the one the source finding missed.
4. No new dangling reference introduced — every path you write is one you opened and read.

## 5. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external` with severity
`critical` | `major` | `minor`. **If anything in this brief is wrong, report it rather than working
around it.** Note that §3 deliberately contains a tension (a step you are asked to perform and cannot);
surfacing it is the expected behaviour, not a failure.
