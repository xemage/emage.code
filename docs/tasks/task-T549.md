# T549 — `/consolidate-memory` instructs data loss in an installed target project

**ID:** T549
**Owner:** Technical Writer
**Status:** in_review
**Priority:** P2
**Tier:** mechanical
**Affects:** command/consolidate-memory
**Depends on:** —
**Created:** 2026-09-26
**Based on:** `docs/artifacts/command-audience-resolution-v1.md` §6.4;
`docs/plans/plan-081-t546-repair-verdicts.md` §2; `docs/tasks/task-T546.md`;
`scripts/install.sh`; `scripts/render_installed_agents.py`.

## 1. The defect

`/consolidate-memory` is **`maturity: stable`**. Its step 5 says:

> **Promote**: append the content to the appropriate section of `AGENTS.md` or the relevant doc,
> then remove from memory

In an installed target project, `$TARGET/AGENTS.md` is **regenerated unconditionally** on every
install and every `--update`: `scripts/install.sh:434` calls `install_agents_doc`, which runs
`scripts/render_installed_agents.py`, whose only write is an unguarded
`dest.write_text(rendered)` at line 174 (the sole guard is `--dry-run`).

So the promoted content is destroyed by the next `--update`, **and the memory entry it came from has
already been deleted by the same step.** The command instructs an irreversible two-step data loss.

This is the same audience pathology as `/skillify`'s hardcoded path (T532), with two differences that
make it worse: the command is **`stable`**, not experimental, and the outcome is **destructive**
rather than merely futile.

**It also disproves the general pattern T532 established.** `/skillify` resolved its audience problem
with a precondition test on a directory's existence. `AGENTS.md` exists in **both** audiences — what
differs is **authority over the file**, not its presence. No existence test detects this. Do not
reach for T532's shape here.

## 2. Verified before dispatch

The orchestrator ran these; you may rely on them.

- `install.sh:434` calls `install_agents_doc` from inside `install_common`, so it runs on **every**
  install and **every** `--update`.
- `render_installed_agents.py:174` is `dest.write_text(rendered, encoding="utf-8")`, reached
  unconditionally after the `--dry-run` early return.
- `/consolidate-memory` declares `agent: "orchestrator"` and `maturity: stable`.
- `AGENTS.md` references appear at lines 2, 15, 24 and 32 of the command. **Line 24 is the
  destructive one**; the others describe or qualify it and must be reviewed for consistency, not
  blindly rewritten.

## 3. What to decide, and the constraint that shapes it

`render_installed_agents.py` rewrites AGENTS.md from `implementation/AGENTS.md` through a fixed list
of `_replace_one` substitutions. **A hand-appended section survives only if no substitution
overlaps it — and the whole file is rewritten from source, so it does not survive at all.** There is
therefore no "append here instead" answer within `AGENTS.md`.

Candidate directions, in the order the orchestrator judges them promising. **Weigh them; do not
assume the first is right.**

1. **Redirect the promotion target to `docs/**`.** T546 §2.1 established that `docs/` is the one
   installed tree treated as the project's own: fresh install is `rsync -a`, `--update` is
   `rsync -a --ignore-existing`, and **a file with no upstream counterpart is never overwritten and
   never deleted under either mode.** A project-local memory-promotion document under `docs/` is
   durable by construction. The cost: it is not `AGENTS.md`, so it is not automatically in an agent's
   context.
2. **Make the deletion conditional on the write being durable.** Whatever the target, step 5's
   "then remove from memory" is the half that makes this irreversible. Requiring the command to
   verify the write survived — or simply to **not delete** — removes the data loss even if the
   promotion target stays imperfect. This is the smaller, safer change and may be the right one to
   ship first.
3. **Declare the command `audience: authoring`.** Honest only if promoting to `AGENTS.md` is
   genuinely an authoring-repo act. It is not: memory consolidation is exactly what a *target*
   project needs. Recorded so it is rejected on the record rather than by omission.

**Do not** invent a new top-level tree, and do not propose changing `install.sh` or
`render_installed_agents.py` — an installer carve-out is `T546` Q5's territory and is tracked
separately in `plan-081` §3.

## 4. Constraints

- **Write scope: `implementation/knowledge/commands/consolidate-memory.md` only.** If the fix needs a
  companion doc under `docs/`, **report that as a blocker first** and name the path you would create;
  do not create it under this task.
- **You have no Bash.** You cannot run `sync.mjs`, `generate-registry.py`, the validators or the
  tests. **Both generators must run** after any `implementation/knowledge/` change
  (`node implementation/scripts/sync.mjs` **and**
  `python3 implementation/scripts/generate-registry.py`) — hand back **uncommitted**, say you ran
  nothing, and the orchestrator will run them and commit.
- **`tests/golden/**` and `scripts/scorecard.py` are protected paths.** This task carries **no**
  authorization, **not even to read `tests/golden/`.** `/consolidate-memory` is `stable`, so it
  plausibly has a golden case whose `expect.py` may assert strings your fix retires — the same class
  as T527/T531 and T535/T541. **If you conclude a case must change, report it and stop.**
- Do not touch `AGENTS.md` or `implementation/AGENTS.md` — **T545** owns those, and bullet 3 is
  generated, so an edit there would be overwritten.
- Do not introduce the `audience:` frontmatter key. **T546 decided it; no task has implemented it**,
  and the schema sets `additionalProperties: false`, so adding the key without the schema edit turns
  `test_schemas.py` red for all 19 commands.

## 5. Acceptance criteria

1. Step 5 no longer instructs an action whose result is destroyed by `install.sh --update` while
   having already deleted its source.
2. The chosen direction from §3 is argued, with the rejected ones named and why.
3. All four `AGENTS.md` references (lines 2, 15, 24, 32) are consistent with the outcome — no
   surviving text that still tells the reader to append to `AGENTS.md` and delete.
4. No new file is created under this task; a needed companion doc is reported as a blocker instead.
5. Nothing under `tests/golden/` is read or written.

## 6. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external` with severity
`critical` | `major` | `minor`. **If anything in this brief is wrong, report it
rather than working around it.** Eleven consecutive tasks have found a defect in their brief, every
time, and §3's reading of `render_installed_agents.py`'s substitution behaviour is the likeliest
place for the twelfth.
