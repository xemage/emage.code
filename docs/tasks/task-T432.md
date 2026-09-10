# Task T432 — scripts/check-maturity.py (CI-enforced)

**ID:** T432
**Owner:** devops-engineer (matches `plan-041`'s own reasoning — this repo's existing precedent of
CI/tooling scripts going to `devops-engineer`, T413/T419/T422; tool grant checked at recording time
— `implementation/knowledge/agents/devops-engineer.md`'s registered grant is `[read, search, edit,
execute, web, mcp__gitlab, mcp__fetch]`, has `execute` — re-confirm this is still accurate at
actual dispatch time, do not assume it stays true indefinitely)
**Status:** pending — recorded and scoped, **not dispatched this session** (T431, its only
dependency, is done; recorded now to satisfy this repo's own "no ledger row without a backing
brief" precondition, mirroring the `T457`/`T458` precedent of a full brief existing before
dispatch)
**Priority:** P1 (blocks T433, which needs a real, working `check-maturity.py` before Wave 1
promotion claims can be mechanically verified — though `T433` also needs its own separate
attention per `plan-041`'s own flag that it is Phase 3's largest single task)
**Depends on:** T431 (done — `docs/artifacts/maturity-promotion-criteria-v1.md`)
**Blocks:** T433
**Created:** 2026-09-10
**Completed:** —
**Based on:** `docs/plans/plan-041-phase3-maturity-ladder-detailed-planning.md` (approved, merged
MR !252) — specifically its T432 row; `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 3
(T432's original nominal scope: "mechanically verify a claimed level; CI-enforced. A component may
not *declare* `stable`; it must *satisfy* it."); `docs/artifacts/maturity-levels-v1.md` (T430 — the
enum and the mandatory-field policy); `docs/artifacts/maturity-promotion-criteria-v1.md` (T431 —
the concrete, per-category/per-transition criteria this script must implement as real checks, not
re-derive or reinterpret).

## Objective

Implement `scripts/check-maturity.py`: given a component's declared `maturity` value (from its
frontmatter, mandatory per T430) and its category (`agent`/`command`/`instruction`/`skill`),
mechanically verify that the component actually satisfies every criterion `docs/artifacts/
maturity-promotion-criteria-v1.md` defines for that level — not merely that the field contains a
valid enum string. A component claiming `stable` with no qualifying evidence must fail the check,
loudly, in CI. Wire this into the same CI gate set `implementation/scripts/check.py` already runs
(`--registry`, or a new flag — your call, document it), so a claimed-but-unearned promotion cannot
merge silently.

## Inputs

- `docs/artifacts/maturity-promotion-criteria-v1.md` (T431 — the concrete criteria per category/
  transition, including the `# maturity-evidence: <category>/<id>` tag convention it defines for
  `agent`/`instruction`/`skill`'s golden-case substitute)
- `docs/artifacts/maturity-levels-v1.md` (T430 — enum, mandatory-field policy)
- `implementation/registry/schema.json`, `implementation/scripts/generate-registry.py` (the
  existing registry pipeline this script's checks should compose with, not duplicate or bypass)
- `implementation/scripts/check.py` (the existing CI gate runner this new check should integrate
  into)

## Expected outputs

- `scripts/check-maturity.py` (or `implementation/scripts/check-maturity.py` — match this repo's
  existing convention for where registry/knowledge-adjacent scripts live; state your actual
  choice), implementing real, per-criterion checks for every category/transition `maturity-
  promotion-criteria-v1.md` defines.
- Wired into `implementation/scripts/check.py`'s gate set (new flag or folded into an existing one
  — your call, document the choice).
- Tests proving the checker itself is correct — both that a component satisfying all criteria for
  its claimed level passes, and that one missing any single required criterion fails with a clear,
  actionable message naming which criterion failed.

## Acceptance criteria

1. A component whose frontmatter claims `stable` but does not satisfy at least one of `docs/
   artifacts/maturity-promotion-criteria-v1.md`'s stated `beta→stable` criteria for its category
   fails the check, with a message naming the specific unmet criterion (not just "invalid").
2. A component satisfying every stated criterion for its claimed level passes.
3. The check runs against the real, current state of all 77 registry-eligible components without
   crashing — report what the real current pass/fail distribution is (expected: most/all still at
   `experimental`, which should trivially pass the `experimental` bar per T431's design — confirm
   this is genuinely true rather than assumed).
4. Wired into CI (`implementation/scripts/check.py` or an equivalent existing gate), not a
   standalone script nobody runs.
5. `python3 tests/run.py` passes with no regressions.
6. Coding standards (max 50-line functions, max 4 parameters, early returns) and Conventional
   Commits followed; branch pushed, MR opened against `develop`, not self-merged.

## Constraints

- **No paid or recurring-cost API calls.**
- **Do not touch `.mcp.json`, anywhere, for any reason. Do not touch the main checkout
  (`/home/emage/Code/emage/emage.code`).**
- **Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/tb-subset.json`/`.md`**
  — if `maturity-promotion-criteria-v1.md`'s `# maturity-evidence:` tag convention genuinely
  requires adding a tag inside a golden case's `expect.py` as one valid evidence location (per its
  own text), treat any such edit as a `type: unclear_requirements` blocker requiring an explicit,
  disclosed exception request before touching that path, per `protected-paths-v1.md`'s documented
  exception process — do not edit unilaterally.
- **Do not touch `feature/T475-codex-platform-integration`. Do not start T433 or any later Phase 3
  task.**
- **Confirm your own tool grant before starting** — re-check `implementation/knowledge/agents/
  devops-engineer.md` directly, do not assume this brief's recorded grant is still accurate.
- **Work in your own worktree/branch** (`agent/devops-engineer/T432`), created from `develop`.
  Commit as you go; run the full test suite before reporting completion. **Do not self-merge** —
  push and open a merge request, then stop.

## Blocker protocol

Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`) +
severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries before
escalating to the orchestrator. If any of `maturity-promotion-criteria-v1.md`'s stated criteria
turns out not to be mechanically checkable as worded despite T431's own acceptance criterion that
it should be, report this as a `type: unclear_requirements` blocker naming the specific criterion,
rather than silently inventing a looser check that doesn't actually verify what was intended.

## Execution notes

Implemented by devops-engineer on branch `agent/devops-engineer/T432`, worktree
`/home/emage/Code/emage/worktrees/agent-devops-engineer-T432`.

- **Location:** `implementation/scripts/check-maturity.py`, not top-level `scripts/`. It imports
  `generate-registry.py`'s `_collect_entries`/`_determine_source`/`_detect_platforms` directly
  (via `importlib`, since the filename has a hyphen) rather than re-walking
  `implementation/knowledge/**` a second time, per the Inputs section's "compose with, not
  duplicate or bypass" instruction.
- **CI wiring:** new `--maturity` flag on `implementation/scripts/check.py` (`_check_maturity`),
  following the same subprocess-invocation pattern as `_check_registry`. Added to the explicit gate
  list in `.gitlab-ci.yml`'s `validation-super-gate` job (which enumerates flags rather than relying
  on check.py's no-flags-means-all-gates default) and to the four "Validate from the repository
  root" doc snippets (`README.md`, `CONTRIBUTING.md`, `implementation/README.md`,
  `docs/wiki/implementation-guide.md`) so a human following the docs also runs it.
- **Interpretation calls made (documented in the script's own module docstring too):**
  1. A `stable` claim is checked against the *general form* of the `experimental→beta` bar (schema
     validity of whatever the component currently declares, `## Rails` present, no open P0) rather
     than literally re-requiring the string `maturity: beta` once a component has been promoted past
     it — `maturity-promotion-criteria-v1.md`'s "ALL of the above, still holding" only makes sense
     read this way for an already-`stable` component.
  2. "Documented ... ≥40 non-whitespace chars, not an incidental substring match" (criterion d, all
     four categories) is checked as: a `docs/wiki/**/*.md` line containing the id/name as a whole
     word, with ≥40 non-whitespace chars remaining on that line once the match is stripped.
  3. Agent criterion (a)(iii)'s "resolves to a real, existing file/MR reference" is checked without
     any network call (script must run offline in CI): backtick-quoted paths are verified to exist
     on disk; `!<digits>` MR references are accepted at face value.
  4. `## Deprecation Notice`'s `**Replacement**:` value is resolved against the set of all 77 real
     component ids across all four categories (T431's wording doesn't restrict it to the same
     category).
- **Two real bugs found and fixed while writing the accompanying tests** (both regex greediness
  bugs, not spec-interpretation issues): `\s*` before a captured value crossed newlines, so an empty
  `**Inputs**:` label would silently "borrow" the next label's text as its own content; and the
  `## Deprecation Notice` heading regex lacked the capture group `_find_labeled_section` needs for
  its own heading level, crashing on every deprecation-tier check. Both are covered by regression
  tests in `tests/functional/test_check_maturity.py`.
- Real registry run (`python3 implementation/scripts/check-maturity.py --root implementation`):
  **77/77 components pass at `experimental`** (28 agents, 19 commands, 4 instructions, 26 skills) —
  confirmed genuinely true, not assumed, per Acceptance Criterion 3.
- Adversarial manual check performed and reverted (not committed): temporarily set
  `implementation/knowledge/agents/devops-engineer.md`'s `maturity:` to `stable` with no other
  change — the checker correctly failed with three named unmet criteria (`## Rails` missing,
  not documented in `docs/wiki/**`, and an open P1 ledger defect: T432 itself, since this task's own
  brief names `devops-engineer` as Owner). Adding a well-formed `## Rails` section then reduced the
  failures to exactly the remaining two, as expected. `git status --short` confirmed a clean revert
  before committing real work.
