# T545 — AGENTS.md § Knowledge Base bullet 2 is wrong in two independent ways

**ID:** T545
**Owner:** Tech Lead
**Status:** in_review
**Priority:** P1
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-09-26
**Based on:** `docs/artifacts/skillify-output-path-resolution-v1.md` §1.3, §2.2, §5.3;
`docs/tasks/task-T532.md`; `AGENTS.md` lines 88–89; `implementation/scripts/sync.mjs` line 47;
`scripts/install.sh` lines 113–180, 252–262, 324.

## 1. Why this is P1 when the rest of the queue is P2

This clause is the **authority** that T527, T532 and (prospectively) T543 and T546 cite to decide
where knowledge may be authored. An adjudication that rests on a clause which is itself wrong is
load-bearing on sand. T532 worked around it by resting its verdict on bullet 1 instead — a
deliberate choice, documented, but not a repair.

`**Affects:** —` is correct and deliberate: `AGENTS.md` is a convention document, not a registry
component, so this row names no component and **cannot block any promotion**. P1 here buys ordering,
not leverage. (Verified: `—` is in `check-maturity.py`'s `AFFECTS_NONE_TOKENS`, parses to the empty
set, and `_ledger_defect` therefore matches nothing.)

## 2. Defect 1 — the platform list omits `.claude/`

`AGENTS.md:88`:

> - Per-platform folders (`.github/`, `.gemini/`, `.opencode/`, `.cursor/`, `.pi/`, `.clinerules/`,
>   `.cline/`) are **generated** by `scripts/sync.mjs`. **Do not edit them by hand.**

`AGENTS.md:89`:

> - Use the installed platform folders (`.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`,
>   `.claude/`, `.cline/`, `.clinerules/`) as runtime references in this target project.

Bullet 3 lists **eight** folders; bullet 2 lists **seven**. `.claude/` is the one bullet 2 omits. So
by `AGENTS.md`'s own text, the hand-edit prohibition **does not cover `.claude/`** — the platform
this repository is most often driven from.

**This is not a hypothetical.** T532 had to choose its ground around it: had `/skillify` hardcoded
`.claude/skills/` instead of `.github/skills/`, bullet 2 would have been unavailable as authority and
the same defect would have gone unadjudicated. A rule that applies to seven of eight platforms by
accident of drafting is a rule that decides cases by accident.

`.claude/` is not special in the code. `scripts/install.sh:466` installs it through the same
`install_tree_into` as every other platform, and `CLAUDE_LOCAL_PATHS` (line 255) carves out only
`settings.json` and `settings.local.json` — a narrower carve-out than `.github/`'s.

## 3. Defect 2 — the stated mechanism is wrong for the tree it names

Bullet 2 says the folders "are **generated** by `scripts/sync.mjs`". Two problems.

**The path is wrong.** The script is at `implementation/scripts/sync.mjs`, not `scripts/sync.mjs`.
Invoking the stated path fails with `MODULE_NOT_FOUND` — and silently no-ops if stderr is suppressed.

**The tree is wrong.** `implementation/scripts/sync.mjs:47` resolves `ROOT` to
`path.resolve(__dirname, '..')` when `--root` is absent, i.e. `implementation/`. With
`github.json`'s `outputDir: ".github"`, it writes **`implementation/.github/`**. A file at the
**repo-root** `.github/skills/` is untouched by `make sync`. So for the root trees — the ones bullet 3
tells agents to *use* — bullet 2 names a program that does not touch them.

**The imperative is nonetheless true, by a different program.** `install.sh`'s `sync_tree_into`
(line 171) runs `rsync -a --delete`, and `GITHUB_LOCAL_PATHS` (line 262) does **not** list `skills`.
`install.sh:324` prints the consequence itself:

> warning: --update replaces $TARGET/.github entirely (rsync --delete)… Other local edits there
> will be lost.

So a hand-written file in a root platform tree is destroyed by `--update`, just not by `make sync`.
An inaccurate rationale attached to a correct rule does not suspend the rule — but it does mean every
agent reasoning from the stated mechanism reasons wrongly.

## 4. The repair this task should make

Restate the prohibition on **source-versus-derived** grounds rather than **sync-versus-install**
grounds. The durable fact is that these trees are *owned by a generator or an installer and not by
the author*; which program overwrites them, and when, is an implementation detail that has already
drifted once.

Requirements:

1. One platform list, complete, used by both bullets — or one list defined once and referenced.
   `.claude/` must be in the prohibition.
2. The generator's real path (`implementation/scripts/sync.mjs`) and its real output root
   (`implementation/.<platform>/`).
3. The root trees' actual owner named: `scripts/install.sh --update`, with the destructiveness
   stated, since that is the fact an agent needs in order not to lose work.
4. `python3 implementation/scripts/generate-registry.py` named alongside `sync.mjs`. Bullet 2 names
   only one of the two required generators; `index.json` carries a per-entry `checksum`, so any
   source edit invalidates it and `sync.mjs` alone leaves the registry stale.
5. **`docs/artifacts/protected-paths-v1.md` §6 carries the same imprecision** — fix both or state
   why not.

## 5. Two copies

`AGENTS.md` exists at the repo root **and** at `implementation/AGENTS.md`, and `scripts/install.sh:397`
copies the latter into a target. **Establish which is the source before editing, and check whether
anything enforces parity between them.** If nothing does, say so — do not add a gate under this task,
but report it, because a two-copy convention document with no parity check is the same class of defect
as the one T540 found in `validate-tasks.py` (where a green test *does* hold the two copies at parity).

## 6. Constraints

- **Read-only outside `AGENTS.md`, `implementation/AGENTS.md` and `docs/artifacts/protected-paths-v1.md`.**
  Do not touch `implementation/knowledge/`, any platform folder, or any script.
- **`tests/golden/**` and `scripts/scorecard.py` are protected paths.** This task carries **no**
  authorization for either. If you conclude a golden case must change, **report it and stop.**
- Editing `AGENTS.md` may require regenerating nothing at all — **verify** whether it is projected
  before assuming. Report what you find.
- Run `python3 docs/tasks/validate-tasks.py` and `python3 implementation/scripts/check-maturity.py
  --root implementation` before reporting done, and **measure the test count yourself** rather than
  trusting any figure in this brief.

## 7. Acceptance criteria

1. Both defects in §2 and §3 are repaired, or a reasoned refusal is recorded for either.
2. The replacement text is checked against the code it describes — quote line numbers.
3. §5's two-copy question is answered with evidence, either way.
4. `validate-tasks.py` PASS and `check-maturity.py` no new failures.

## 8. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external` with severity
`critical` | `major` | `minor`. **If anything in this brief is wrong, say so rather than working
around it** — implementers have caught a defect in a brief on ten consecutive tasks, and that record
is the reason this instruction is here.
