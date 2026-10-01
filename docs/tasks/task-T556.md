# T556 — Declare every command's `audience:` (schema + 19 frontmatter lines, one atomic commit)

**ID:** T556
**Owner:** Backend Developer
**Status:** pending
**Priority:** P2
**Tier:** mechanical
**Affects:** —
**Depends on:** —
**Created:** 2026-10-01
**Based on:** `docs/artifacts/command-audience-resolution-v1.md` §1.5, §2.2, §3, §5; `docs/plans/plan-087-audience-key.md`;
`docs/plans/plan-083-four-decisions-and-batching.md` §4 (P5, P6); `docs/checkpoints/checkpoint-037-phase9-queue-empty-root-refreshed.md` §8.

## 1. What and why

T546 decided that every command declares which audience it serves: the emage.code **authoring** repository,
an installed **target** project, or **both**. Until now no command says so, and the audience has had to be
inferred from whichever paths each command mentions — which is how four `stable` commands came to name paths
that do not exist in installed projects. This task implements T546's decision. Its trigger (`plan-083` P5,
"a round with no open `implementation/knowledge/` task") has fired.

## 2. The change — exactly T546's design

1. **`implementation/knowledge/schemas/command.schema.json`**: add `"audience"` to `properties` as
   `{ "type": "string", "enum": ["authoring", "target", "both"] }`, and add `"audience"` to `required`.
2. **All 19 files in `implementation/knowledge/commands/`**: add one frontmatter line, using T546 §2.2's
   values verbatim:
   - `prepare-release` → `audience: authoring` (this is `plan-083` P6, folded in)
   - the other 18 → `audience: both`
   - none → `target`
3. **One atomic commit for 1 and 2.** The schema sets `"additionalProperties": false` and
   `tests/functional/test_schemas.py` validates all 19 commands unconditionally, so a key without the schema
   change — or a required key missing from any command — turns the suite red. Do not split it.

**Placement in frontmatter:** put `audience:` immediately after `maturity:` in every file, so the 19 diffs are
uniform and reviewable at a glance.

## 3. What should NOT change — verify each, don't assume

- **No projection under `implementation/.<platform>/`.** `audience` is source-only: no manifest's
  `frontmatter.commands.keepKeys` lists it, so `sync.mjs` drops it (exactly as it drops `maturity`). Run
  `node implementation/scripts/sync.mjs --root implementation` and confirm `git status` shows **no** projection
  changes. If any projection changes, stop and report — it would mean the key leaked into a projection.
- **No manifest** in `implementation/platforms/` — do not add `audience` to any `keepKeys`.
- **The repo-root drift list stays empty.** `python3 -m tests.functional.test_root_install_parity --print-drift`
  must still print `[]`. If it does not, stop and report.
- **No golden case and no evaluator-hash change.** Golden checkers read their own fixtures, not live command
  files — confirm by checking that `tests_golden` is unchanged from v11 (`a6326b97…`) and that the two
  evaluator-hash tests still pass. **Do not edit `tests/golden/**` or `scripts/scorecard.py`.**
- **No maturity change.** `check-maturity.py` must stay 79/0 with the same distribution; criterion 1
  (`_check_schema`) now enforces the enum for every non-`experimental` command — confirm all 9 `stable` commands
  still pass it.

## 4. What WILL change

- `implementation/registry/index.json`: **all 19** command checksums (the checksum hashes the whole file
  including frontmatter). Run `python3 implementation/scripts/generate-registry.py` and confirm
  `--check` is clean. **Do not add `audience` to the registry** (T546 §5.2 decided against it).

## 5. Constraints

- **Write scope:** the schema file, the 19 command source files, `implementation/registry/index.json`
  (regenerated), and the `**Status:**` line (to `in_review`) of this brief. Nothing else. In particular **not**
  `implementation/AGENTS.md` — documenting `audience` there would re-render the root `AGENTS.md` and is a
  separate decision.
- **Commit locally**, one commit, Conventional Commits, ending
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. **Do not push. Never merge or approve anything.**

## 6. Verification — real output

- **Mutation, to prove the schema enforces it:** temporarily set one command to `audience: everyone` and
  confirm `tests/functional/test_schemas.py` fails; temporarily delete the line from one command and confirm it
  fails again. Restore both and confirm with `git diff` that nothing stray remains.
- `python3 tests/run.py` — a `unittest` wrapper; the signal is the **exit code** plus `Ran N` / `OK` on stderr;
  **redirect to a file, never pipe to `tail` and read `$?`**. Baseline: 871, OK, skipped=24.
- `validate-tasks.py`, `check-maturity.py --root implementation`,
  `check.py --root implementation --maturity --schemas --registry`, `sync.mjs --root implementation --check`,
  `generate-registry.py --check`, `scorecard.py --check`, and `--print-drift`.

## 7. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`. **If anything
in this brief is wrong — including T546's §2.2 values, which were decided on 2026-09-26 and the commands have
changed since — report it rather than working around it.** Nearly every task this phase has found a defect in
its brief.
