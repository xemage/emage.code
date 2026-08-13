# Task T412 — Split `tests/golden/open/` vs `tests/golden/held-out/` + guard

**ID:** T412
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T410 (done), T411 (done — 20 golden cases, `docs/artifacts/golden-suite-format-v1.md`)
**Created:** 2026-08-13
**Completed:** 2026-08-13
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` (Phase 1, §2.4, Layer 1 table, row T412)
and `docs/artifacts/golden-suite-format-v1.md` §3.1 ("Reservation for T412"), which this brief's
mechanics MUST follow exactly — read that section in full before doing anything, it is the binding
design contract for how this split has to work.

## Why this matters (read plan-035's own risk table first)
`plan-035`'s risk table: *"Held-out set leaks into improvement work | Medium | Critical | T412 path
guard + T463 evaluator-hash check + T416 write-scope exclusion. Three independent controls."*
T412 is the **first** of three independent controls protecting the held-out set's integrity for the
entire rest of this roadmap (T463 and T416 build on what you establish here). Getting the guard
wrong here is a Critical-impact defect that later tasks will inherit silently.

## Objective
1. Move the 20 existing case directories under `tests/golden/` (all currently flat, per T411's
   manifest at `tests/golden/_manifest-t411.md`) into two new sibling directories,
   `tests/golden/open/<case-id>/` and `tests/golden/held-out/<case-id>/`, as a **pure directory
   move** — per the format spec §3.1, this requires zero changes to any case's `brief.md`,
   `case.yaml`, `fixture/`, or `expect.py` content. If you find yourself needing to edit case
   content to make the move work, stop — that means the format spec's "zero change to the
   per-case contract" claim doesn't actually hold, and that's a `type: technical` blocker to
   report, not something to work around silently.
2. Decide the split. Not numerically specified by the plan — use your judgment, but the held-out
   set must be genuinely representative (not just "whatever's left over"): a reasonable starting
   point is roughly 25-30% of the 20 cases (5-6) held out, spanning multiple command surfaces (not
   all from one surface), and including at least one `known_failing` case (a held-out set that's
   100% `expected_pass` can't catch an improvement that games known failures). Document your
   reasoning for which specific cases you chose in a short note (see "Expected outputs" below) —
   this is a real methodological decision future readers will want to audit, not a coin flip.
3. Build the enforcement guard: a test (or tests) that fails if `tests/golden/held-out/` is
   referenced — by path string, file read, import, or any other means — from any file outside
   `tests/golden/held-out/` itself. This repo already has precedent for exactly this kind of
   repo-wide static guard: read `tests/functional/test_link_integrity.py` and
   `tests/functional/test_check_version_consistency.py` for the established pattern (walk the repo,
   flag violations, hard-fail with a clear message listing every violation found) before designing
   yours from scratch.

## What "referenced" means (scope the guard correctly)
The acceptance criterion is "never referenced from any file outside `tests/golden/held-out/`." This
needs to be strict enough to catch a real leak but not so broad it false-triggers on legitimate
things. At minimum, the guard MUST catch:
- Any Python `import`/`open()`/`Path(...)` string literal containing `tests/golden/held-out` (or a
  relative path that resolves into it) in a file outside that directory.
- Any markdown/doc reference to a specific held-out case ID or file path from outside the
  directory (this protects against a human/agent copy-pasting a held-out case's content elsewhere,
  not just code referencing the path).
- `scripts/scorecard.py` (T413, not yet built — coordinate scope, see "Coordination note" below) is
  explicitly **allowed** to reference `tests/golden/held-out/` for discovery/execution purposes —
  that's its whole job (running both suites). Your guard needs a principled way to distinguish
  "the scorecard runner is allowed to execute held-out cases" from "an improvement-task file is
  allowed to read held-out case content for authoring/design purposes" (the latter is exactly what
  the leak risk is about). Document how you drew this line — this is the actual hard part of the
  task, not the directory move.

This directory-only, file-content split does NOT need to implement GitLab-level access control
(that's a separate, heavier lift and not what "CODEOWNERS-style" requires here) — a
`CODEOWNERS`-style *static test guard* enforced in CI is the deliverable, mirroring how
`test_link_integrity.py`/`test_check_version_consistency.py` already enforce repo-wide invariants
in this codebase without any GitLab-side branch protection changes. If you think an actual
`CODEOWNERS` file entry (GitLab's real review-routing feature) would add genuine additional
protection on top of the test guard, you may add one, but the test guard is the acceptance-bearing
deliverable — don't substitute one for the other.

## Coordination note (T413 runs concurrently/after)
T413 (`scripts/scorecard.py`) is not yet built and depends on this task. Do not block on it — build
your guard against the format spec's documented discovery contract (§3.1: recursive glob for
`expect.py` under `tests/golden/`, directory-shape-agnostic, excludes `_`-prefixed paths), not
against T413's actual (not-yet-written) code. If your guard's "who's allowed to reference held-out"
distinction ends up needing an explicit allowlist (e.g. a path/file the guard treats as exempt),
allowlist `scripts/scorecard.py` by name/path now — T413's author will need to build against that
exemption, not invent their own.

## Expected outputs
- `tests/golden/open/<case-id>/` and `tests/golden/held-out/<case-id>/` — all 20 cases moved, none
  left flat under `tests/golden/` directly (except `README.md`, `_example-scaffold/`,
  `_manifest-t411.md`, which stay where they are).
- Update `tests/golden/_manifest-t411.md` (or add a small addendum) to reflect each case's new
  `open`/`held-out` location — the manifest becoming stale the moment you move files would be a
  needless regression for T413/T414/T415's authors who were told to rely on it.
- A new guard test, e.g. `tests/functional/test_golden_held_out_isolation.py` (your call on exact
  name, follow this repo's existing `tests/functional/test_*.py` naming convention) enforcing the
  isolation rule above.
- A short note (in the guard test's own docstring, or a small section in
  `tests/golden/README.md` — your call) explaining: the chosen split (which cases, why), and the
  "who's allowed to reference held-out" line you drew for the guard's allowlist logic.

## Acceptance criteria
1. All 20 cases live under `tests/golden/open/` or `tests/golden/held-out/`, each with all four
   required members, content byte-identical to before the move (prove this — e.g. diff each moved
   case's files against T411's pre-move commit, don't just assert it).
2. Held-out set is genuinely representative: spans multiple command surfaces, includes at least one
   `known_failing` case, documented reasoning for the specific split chosen.
3. The guard test fails (on a scratch/temp fixture, not by actually committing a violation into
   this repo) when something outside `tests/golden/held-out/` references it, and passes on the
   real, clean repo tree as it stands after your move — prove both directions, mirroring how
   `test_check_version_consistency.py`'s own test suite proves both a clean-pass and a
   drift-detected case via temp fixtures, not just asserting the real tree is currently clean.
4. Every case's `expect.py` still runs correctly from its new nested location — re-run all 20
   (`python3 <case>/expect.py <case>`) and confirm each still matches its declared `case.yaml`
   status, exactly as it did before the move.
5. `python3 tests/run.py` still exits 0 (no regression), including the new guard test actually
   executing (not skipped).
6. `git status` clean after the full run bar above (no fixture mutation, consistent with the
   format spec's purity rules).

## Blocker protocol
- If the "pure directory move, zero content change" claim in the format spec turns out not to hold
  for some real reason you discover -> `type: technical`, `severity: major` — report what you
  found rather than quietly patching case content to make the move work.
- If you can't design a guard that's both strict enough to catch a real leak and permissive enough
  not to false-trigger on `scripts/scorecard.py`'s legitimate future access -> `type:
  unclear_requirements`, `severity: minor` — pick your best reading (a scorecard.py allowlist is
  the expected answer), document it, keep moving.

## Git workflow
1. `cd /home/emage/Code/emage/worktrees/phase1-golden-suite` (existing worktree, branch
   `feature/T410-phase1-golden-suite-v6.12.0` — do not create a new one; this branch already has
   T410's `ed8c525` and T411's `90f1f26`).
2. Perform the move, build the guard, verify the full acceptance bar above.
3. Commit with a Conventional Commit message (`feat(golden): split open/held-out + isolation guard
   ... Refs T412`).
4. Do not push, do not open an MR. Report worktree path (unchanged), branch name (unchanged),
   commit SHA(s), the exact held-out case list + reasoning, and confirmation of each numbered
   acceptance criterion back to the orchestrator.

## Constraints
- Token budget: ~35k tokens (medium scope per the plan).
- File ownership: `tests/golden/open/**`, `tests/golden/held-out/**` (via `git mv`, not
  delete+recreate — preserve history), `tests/golden/_manifest-t411.md` (update in place),
  `tests/functional/test_golden_held_out_isolation.py` (or your chosen name). Do not touch
  `tests/golden/README.md`'s core content beyond what's needed to reflect the new layout, do not
  touch `docs/artifacts/golden-suite-format-v1.md` (T410's, immutable), do not touch any existing
  `tests/functional/test_*.py` file other than adding your new one.

## Completion addendum (2026-08-13)

Delivered: 14 cases in `tests/golden/open/`, 6 in `tests/golden/held-out/` (30%), spanning all 5
command surfaces (2 `/code-review`, 1 each of the other 4), balanced 3 `expected_pass`/3
`known_failing` covering both `known_failing_category` values. New
`tests/functional/test_golden_held_out_isolation.py` (8 tests: 6 synthetic-fixture, 2 against the
real tree), mirroring the established `test_link_integrity.py`/`test_check_version_consistency.py`
repo-wide static-guard pattern.

**Design call flagged for explicit sign-off, not treated as pre-settled:** the brief's literal
text ("never referenced from any file outside `tests/golden/held-out/`") would, applied strictly,
flag pre-existing T411 `brief.md` cross-references between sibling cases inside `open/` (two real
examples: `open/security-audit-verdict-fields-compliant/brief.md` naming
`security-audit-owasp-matrix-compliant`, `open/new-feature-plan-doc-compliant/brief.md` naming
`new-feature-real-artifact-versioning-drift`, both pre-existing T411 provenance notes that
acceptance criterion 1's byte-identical requirement forbids editing). The agent scoped the
case-ID-mention check to "outside `tests/golden/` entirely" rather than merely "outside
`held-out/`", leaving the stronger Python-functional-access check (imports/`open()`/`Path()`)
unscoped and repo-wide including inside `open/`.

**Orchestrator independently verified this scoping decision, not merely accepted it as the
brief's documented default for ambiguity.** Reasoning, arrived at independently: (1) the files
that matter for the actual threat (plan-035's risk table: "held-out set leaks into improvement
work") — agent/skill/command definitions, scripts, docs an improvement task would read — have no
legitimate reason to live under `tests/golden/`, so the narrowing doesn't touch them; confirmed by
reading the guard's code directly (Check A's branch runs before the `_is_inside_golden_dir` guard
that only narrows Check B) and then proving it live: planted adversarial probe files in `scripts/`
(a Python path reference) and `docs/` (a bare case-ID mention) in the real repo tree, ran
`find_violations()` directly, confirmed both were caught, then removed the probes and confirmed
`git status` clean; (2) the case-ID token itself isn't secret — `_manifest-t411.md` is required by
this same brief to name all six held-out case IDs plus reasoning, and is correctly exempted, so a
sibling `open/` brief naming a held-out case ID discloses strictly less than the manifest's own
mandated disclosure; (3) the alternative (strict literal scoping) would have required editing
T411's already-authored content, directly violating this brief's own criterion 1. Independently
confirmed the two cited real cross-references exist exactly as described (`brief.md` lines checked
directly). Sign-off: the scoping is correct.

**Full independent verification, artifact-level, not self-report-level:**
1. Split counts confirmed by direct `ls`: 14 `open/`, 6 `held-out/`, nothing left flat.
2. Held-out surface/status distribution confirmed by direct `grep` on every `case.yaml`: all 5
   surfaces represented, 3 `expected_pass`/3 `known_failing` (2 `tracked_defect`, 1
   `capability_gap`), matching the claim exactly.
3. Byte-identity confirmed via `git diff 90f1f26 e3381b8 --raw -M100%` — all 82 case-content files
   show as `R100` renames with **identical blob hashes** before and after (a stronger,
   independently-derived check than trusting the agent's own SHA-comparison claim).
4. All 20 cases re-run from their new nested `open/`/`held-out/` paths — zero status mismatches
   against declared `case.yaml` status.
5. Guard's real-tree detection independently stress-tested with live adversarial probes (see
   above), not just the shipped synthetic-fixture tests (which were also run directly and all
   passed: `python3 -m unittest tests.functional.test_golden_held_out_isolation -v`, 8/8 OK).
6. `python3 tests/run.py` re-run fresh: 367 tests, exit 0, `git status` clean throughout.

All 6 of this brief's acceptance criteria confirmed PASS. Status set to `done`. See
`docs/tasks/completed-tasks.md` and `docs/tasks/active-tasks.md`'s "Owner corrections and closure
history" for the ledger-level closure note.
