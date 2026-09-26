# T546 — No command declares its audience, and two stable commands are already broken by it

**ID:** T546
**Owner:** Solution Architect
**Status:** pending
**Priority:** P2
**Tier:** judgment
**Affects:** command/discover-skills, command/handoff, command/prepare-release
**Depends on:** —
**Created:** 2026-09-26
**Based on:** `docs/artifacts/skillify-output-path-resolution-v1.md` §3; `docs/tasks/task-T532.md`;
`scripts/install.sh`; `implementation/registry/index.json`.

## 1. The finding

Every command in `implementation/knowledge/commands/` ships into **two** audiences: the emage.code
authoring repository, and any project that ran `install.sh`. **No command declares which it is for.**
There is no `audience:` frontmatter key, no slot in `command.schema.json`, no `## Rails` clause and no
`AGENTS.md` section naming the distinction. A reader infers each command's audience from whichever
paths it happens to mention.

T532 fixed one instance (`/skillify` aimed a write at a derived tree). This task is the class.

## 2. Two `stable` commands are already unperformable in a target project

Verified directly: **neither `implementation/registry/` nor `implementation/runtime/handoff/` is ever
installed.** Neither string appears anywhere in `scripts/install.sh`. What leaves `implementation/`
is only `docs/`, `runtime/memory/` and `runtime/security/` (lines 382–430).

| Command | Maturity | Path it names | In a target project |
|---|---|---|---|
| `/discover-skills` step 1 | **stable** | "load `implementation/registry/index.json`" | `implementation/registry/` never installed — **step 1 cannot be performed** |
| `/handoff` step 3 | **stable** | `implementation/runtime/handoff/schema-v1.json` | `runtime/handoff/` never installed — only `memory` and `security` are |
| `/prepare-release` steps 6–7 | experimental | `implementation/scripts/generate-registry.py`, `scripts/verify-release-docs.py` | neither script tree installed; wholly about this repo's own release process, and says so nowhere |

`/skillify` was the only command naming a target-project path as a **write** target. The remaining
fifteen are audience-neutral **by accident, not design** — they touch only `docs/**` or project
source, which exist in both. `/validate-tasks` is portable only because `install_docs()` copies
`implementation/docs/` into `$TARGET/docs/`.

## 3. Read this before choosing a priority — the `**Affects:**` field here is deliberate and contestable

This row is **P2** while naming three components in `**Affects:**`. That combination is load-bearing
and you should understand it before changing either half.

`check-maturity.py:_ledger_defect` filters by priority (`DECLARED_PRIORITIES = {"P0","P1"}`) **before**
reading `**Affects:**`. So at P2 the declaration is **recorded but inert**: criterion 3 and criterion 7
do not see it. Promote this row to P1 and the gate goes **red for `/discover-skills` and `/handoff`,
both currently `stable`**, plus their owning agents under criterion 7.

**The orchestrator chose P2 and is flagging the choice rather than burying it.** The reasoning: these
two commands were promoted against criteria that did not include audience-portability, so the `stable`
claim was not fraudulent — a new criterion emerged. Recording the defect at P2 preserves the
information without retroactively demoting two components by a priority keystroke.

**That reasoning is contestable and the decision is the user's, not this task's.** If the user judges
that an unperformable step 1 in a `stable` command should show red, the change is one character in
this row's `Priority` column. **Do not make that change inside this task.** If you believe it should
be P1, say so in your report.

## 4. What to decide

Produce `docs/artifacts/command-audience-resolution-v1.md` answering:

1. **Is a declared `audience:` field the right mechanism?** Candidate values
   `authoring | target | both`. Alternatives to weigh and reject explicitly: a `## Rails` prose
   clause only; per-step annotation; splitting divergent commands into two files; doing nothing and
   fixing paths case by case as T532 did.
2. **What does `both` oblige a command to do?** `/skillify`'s answer was a precondition test on a
   directory's existence. Is that the general pattern, or is it specific to that command?
3. **Blast radius, costed not guessed.** A new frontmatter key touches
   `implementation/knowledge/_schemas/command.schema.json` (confirm the path), the `keepKeys` list in
   **each** of seven platform manifests, `generate-registry.py`, and every projection of all nineteen
   commands. Registry entries carry `id`, `category`, `name`, `path`, `checksum`, `maturity`,
   `compatibility` — **and no `description`** (verified by reading `index.json`), so decide whether
   `audience` belongs in the registry too.
4. **The three commands in §2 — repair, or reclassify?** `/prepare-release` is honestly
   `authoring`-only. `/discover-skills` and `/handoff` are meant to be portable and name paths that
   are not there, so they need either a portable path or an installer change.
5. **The durable-home question T532 deferred.** A target project has **no** durable place for a
   hand-written skill: `install.sh --update` runs `rsync -a --delete` on every platform tree, and
   `skills` is not in any carve-out list. `docs/**` *is* durable (`install_docs` uses
   `rsync -a --ignore-existing`, never overwriting, never deleting — the one installed tree treated
   as the project's own), but **no skill loader reads it.** T532 refused to mint `docs/skills/` on
   `batch-manifest-resolution-v1.md` §3.2's ground (no mandate to mint a namespace inside an
   adjudication). **This task has that mandate if you conclude it is needed** — but a carve-out in
   `install.sh` may be the cheaper answer. Weigh both.

## 5. Constraints

- **Decide, do not implement.** Write the artifact. Do **not** edit `command.schema.json`, any
  manifest, `generate-registry.py`, `install.sh`, or any command file. The implementation is a
  follow-up task sized by your own blast-radius answer.
- **You have no Bash.** Say so where a claim would need one. Do not assert counts, absences or
  "nothing else references X" as verified — the orchestrator will run the checks. State what you
  read by name and mark everything else as unevidenced. **T532's predecessor did exactly this and it
  was the right call.**
- **`tests/golden/**` and `scripts/scorecard.py` are protected paths.** No authorization here, not
  even to read `tests/golden/`.
- Do not touch `AGENTS.md` — **T545 owns it**, and it is authority you may need to cite.

## 6. Acceptance criteria

1. §4's five questions each answered, with rejected alternatives named and the grounds for rejection.
2. A recommendation on §3's P1/P2 question, argued either way.
3. The blast radius costed against files read by name, not estimated.
4. Every unverifiable claim explicitly marked as unevidenced.

## 7. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external` with severity
`critical` | `major` | `minor`. **If anything in this brief is wrong, report it rather than working
around it.** Ten consecutive tasks have found a defect in their brief; §2's table and §3's reading of
`check-maturity.py` are the most likely places for the eleventh.
