# Task T415 — Failure taxonomy (`cause × behavior × mechanism`)

**ID:** T415
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T411 (done — 20 golden cases), T413 (done — `scripts/scorecard.py`,
`docs/benchmarks/scorecard-v6.12.0.json`)
**Created:** 2026-08-13
**Completed:** 2026-08-14
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` (Phase 1, §2.4, Layer 1 table, row T415:
*"Failure taxonomy: classify each golden failure as `cause × behavior × mechanism`, stored in
`docs/benchmarks/failures/`. Adopted from the source roadmaps."*; also §1.1's verdict on this idea,
*"Correct and cheap. Adopted."*). Reassigned from `evaluation-agent` to `qa-engineer` per this
ledger's "Owner correction" note (`evaluation-agent`'s registered tool grant is read/research-only,
scoped for PoC hypothesis validation — this task needs write/Bash access to build real artifacts).

## Why this matters beyond this task
This taxonomy is not a one-off report. Two later items in this plan build directly on it:
`docs/plans/plan-035-roadmap-v7-ground-up.md`'s T409 (`T41C`, already in this ledger's backlog)
extends it to ingest Terminal-Bench/Harbor trajectory failures into the *same* scheme ("one
taxonomy, two sources"), and the plan's own cross-repo coordination table (line ~626) says this
scheme should be **defined once in emage.code and referenced from CWSO** — i.e. this needs to be a
clean, well-specified, reusable classification scheme, not an ad hoc one-off writeup. Design it
with that reuse in mind.

## Objective
1. **Define the taxonomy scheme itself** — plan-035 names the three axes (`cause`, `behavior`,
   `mechanism`) but does not enumerate their values (the source roadmaps this was adopted from are
   not available to you; you are defining the concrete scheme, not looking one up). Derive it
   **bottom-up from the real failures**, not from invented categories: read all 9 currently
   `known_failing` golden cases' `brief.md` files (both `open/` and `held-out/` — see the isolation
   note below for how to handle held-out identities in your output) and their
   `known_failing_reason`/`known_failing_category` fields in `case.yaml`, and derive axis values
   that actually discriminate between the real failures you're classifying. A reasonable starting
   frame (not prescriptive — adjust based on what the real 9 cases actually show):
   - **`cause`**: the root reason the check fails today (e.g. a declared contract with no
     real-world precedent, an established real convention that diverges from the declared
     contract, a genuinely unimplemented capability).
   - **`behavior`**: the observable symptom (e.g. a required field/section is absent, a marker
     line never appears, a format diverges from spec).
   - **`mechanism`**: how/where the gap manifests structurally (e.g. whole-block absence vs.
     field-level mismatch vs. naming-convention drift).
   Document the scheme itself — axis definitions, enumerated values, and why each value is
   distinct enough to be worth its own bucket — in a format spec doc (your call on exact location;
   `docs/artifacts/failure-taxonomy-v1.md` mirrors this repo's existing artifact-versioning
   convention and is a reasonable default, consistent with T410's own
   `golden-suite-format-v1.md` precedent).
2. **Classify each of the 9 currently `known_failing` golden cases** along all three axes, stored
   under `docs/benchmarks/failures/` (the plan's own literal path). One file per case (mirroring
   the golden suite's own per-case-directory convention) or a single index — your call, but make
   the per-case classification auditable (which case, which axis values, why).
3. **Regressions and `unexpected_pass` cases are out of scope for this initial taxonomy** — there
   are currently 0 of each (per T413's scorecard), so this is a non-issue today, but note explicitly
   in your deliverable that the taxonomy currently only covers the `known_failing` bucket, so a
   future regression has nowhere to land in this scheme yet without extension (flag as a natural
   follow-up, not something to solve now).

## Held-out isolation — carried forward from T412/T413/T414, same discipline required
This is the fourth task in a row that touches held-out case content, and the failure classification
data is *exactly* the kind of content that would tempt naming a held-out case's real ID (you need to
discuss *why* each case fails, which is inherently close to revealing what the held-out check
actually validates). Apply the same discipline T413 (`scripts/scorecard.py`) and T414
(`baseline-v6.12.0.md`) already established:
- `docs/benchmarks/failures/` lives outside `tests/golden/`, so it is **not** exempt from
  `tests/functional/test_golden_held_out_isolation.py`'s Check B — real held-out case IDs must not
  appear anywhere in it.
- For the 3 held-out cases among the 9 known_failing (per T412's split), classify them along all
  three taxonomy axes exactly like the open cases — the axis values themselves reveal nothing about
  *which* case it is — but use a redacted identity, exactly mirroring T413's
  `redact_held_out_identities()` pattern (`held-out-case-<n>`, deterministic by sorted real ID, so
  it stays consistent with T413's own labeling if useful, though a fresh consistent scheme within
  this task's own files is also fine — your call, document which you chose).
- Verify this yourself before finishing: `grep` your new files for all six real held-out case IDs
  (zero matches expected), and re-run `tests/functional/test_golden_held_out_isolation.py` after
  writing them to confirm the guard still passes with your new files present.

## Inputs
- `tests/golden/open/*/brief.md`, `tests/golden/held-out/*/brief.md`, `*/case.yaml` — the 9
  `known_failing` cases' actual content (you have full read access to both, unlike future
  improvement-task agents; this task is suite-internal classification work, not improvement work).
- `docs/benchmarks/scorecard-v6.12.0.json`/`.md` (T413) — the current known_failing set and its
  `tracked_defect`/`capability_gap` split, as your starting index of what to classify.
- `docs/artifacts/golden-suite-format-v1.md` (T410) — for the `known_failing_category` distinction
  (`tracked_defect` vs `capability_gap`) your taxonomy's `cause` axis should relate to, not
  duplicate outright (they're not the same axis — a `tracked_defect` and a `capability_gap` case
  could share a `cause` value or differ, depending on what you find in the real 9 cases).

## Expected outputs
- A taxonomy format/scheme document (e.g. `docs/artifacts/failure-taxonomy-v1.md`) defining the
  three axes and their enumerated values, written so T409 (Harbor trajectory extension) and a
  future CWSO reference can build against it without re-deriving your reasoning.
- `docs/benchmarks/failures/` populated with a classification entry for each of the 9 current
  `known_failing` cases (open, real identity; held-out, redacted identity per the isolation note
  above).

## Acceptance criteria
1. All 9 currently `known_failing` cases (per the real, current `docs/benchmarks/scorecard-v6.12.0.json`
   — re-read it yourself, don't trust a stale count) are classified along all three axes.
2. The taxonomy scheme document exists and defines each axis's enumerated values with real-example
   grounding (cite which actual case(s) motivated each value — open cases by real ID, held-out
   cases by redacted label).
3. No real held-out case ID appears anywhere in `docs/benchmarks/failures/` or the taxonomy scheme
   document — verified by `grep` against all six real IDs (zero matches).
4. `tests/functional/test_golden_held_out_isolation.py` still passes (re-run it) with your new
   files present.
5. `python3 tests/run.py` still exits 0 (no regression).
6. `git status` clean under `tests/golden/`, `scripts/`, and `docs/benchmarks/scorecard-v6.12.0.*`
   after your work (you should not have touched any of them — read-only inputs).

## Blocker protocol
- If the real 9 known_failing cases don't cleanly discriminate into 3 meaningfully-distinct axes
  (e.g. `cause` and `mechanism` end up redundant for every real case) -> `type:
  unclear_requirements`, `severity: minor` — use your best judgment on how to keep the axes
  genuinely distinct (even if narrower than a hypothetical general-purpose scheme), document the
  reasoning, keep moving. Do not force three axes to look different if the real data doesn't
  support it — a taxonomy that fakes distinctness is worse than an honest, narrower one.
- If you find the held-out redaction pattern from T413 doesn't cleanly transfer to this task's own
  file shape -> `type: unclear_requirements`, `severity: minor` — adapt it sensibly, document your
  adaptation, keep moving.

## Git workflow
1. `cd /home/emage/Code/emage/worktrees/phase1-golden-suite` (existing worktree, branch
   `feature/T410-phase1-golden-suite-v6.12.0` — do not create a new one; currently at commit
   `1ebc970`, with T410 through T414 all landed).
2. Build the taxonomy scheme and classify the 9 cases, verify the full acceptance bar above.
3. Commit with a Conventional Commit message (`docs(benchmarks): failure taxonomy (cause x
   behavior x mechanism) for golden suite ... Refs T415`).
4. Do not push, do not open an MR. Report worktree path (unchanged), branch name (unchanged),
   commit SHA(s), the taxonomy scheme's axis values with real-case grounding, and explicit
   confirmation of each of the 6 acceptance criteria above back to the orchestrator.

## Constraints
- Token budget: ~35k tokens (medium scope per the plan — real classification work across 9 cases
  plus scheme design).
- File ownership: `docs/artifacts/failure-taxonomy-v1.md` (or your chosen scheme-doc path),
  `docs/benchmarks/failures/**`. Do not touch `tests/golden/**` (read-only), `scripts/`,
  `docs/benchmarks/scorecard-v6.12.0.json`/`.md` (T413's, generated — read only),
  `docs/benchmarks/baseline-v6.12.0.md` (T414's, frozen), or
  `tests/functional/test_golden_held_out_isolation.py` (T412's).

## Completion addendum (2026-08-14)

Original delivery (commit `76ab91c`): `docs/artifacts/failure-taxonomy-v1.md` (the `cause` ×
`behavior` × `mechanism` scheme, three axes each with 3-4 enumerated values, every value grounded
in at least one real case) plus `docs/benchmarks/failures/` (9 files, one per `known_failing`
case — 6 `open` by real ID, 3 `held-out` as `held-out-case-{1,3,4}`). All 6 stated acceptance
criteria were met at that commit.

**Narrative-leak finding and fix (session interrupted twice by an account-wide Claude usage-limit
stop; completed on a third resumption).** A cross-task review requested ahead of T416's freeze
(T416 makes `tests/golden/**`/`scripts/scorecard.py` read-only, so anything wrong here is much
harder to fix afterward) found that `held-out-case-1.md`, `-3.md`, `-4.md`'s "Why" sections went
beyond the categorical axis-value labels the redaction scheme (§5 of the taxonomy doc) was
designed to permit — they narratively described the real held-out fixtures' actual content in
detail (quoted command-file requirements, described real document structure). This is narrative
content leakage: distinct from case-*identity* leakage (which the T412 isolation guard's Check B
already catches), but the same underlying risk the held-out split exists to prevent — an
improvement-task agent reading these files could infer real fixture content without ever seeing a
real case ID. Fixed in commit `3fef6ee`: each "Why" section replaced with a redaction notice
pointing to the general axis-value definitions in `failure-taxonomy-v1.md` §3 (the only
non-redacted content is the axis-value table itself, unchanged); `held-out-case-4.md` also gained
one cross-reference note distinguishing its `mechanism` from two open cases without describing its
own fixture.

**Broader audit performed, not just the one fix.** Per the same review's request, every file
across T410-T415 that's allowed to touch held-out content was re-checked for the same
narrative-leak pattern, not just T415's own three files: `docs/artifacts/failure-taxonomy-v1.md`
(clean — axis tables only), `docs/benchmarks/scorecard-v6.12.0.json`/`.md` (clean — held-out rows
carry only `command`/`status`/`known_failing_category`/`bucket`/`actual_result`, identity fields
redacted), `docs/benchmarks/baseline-v6.12.0.md` (clean — aggregate counts only, self-documents its
own grep verification), `docs/artifacts/golden-suite-format-v1.md` and `tests/golden/README.md`
(clean — general format specs, no case-specific content), the 6 `open` failure files (clean — no
held-out mentions; their narrative detail is fine since `open` cases aren't secret). One additional
issue was found, outside T415's own file set: `docs/tasks/task-T411.md` and `task-T412.md`
(already on `develop`) each contained bare mentions of real held-out case IDs — latent, not yet a
live violation (the isolation guard and `tests/golden/` itself hadn't merged to `develop` yet), but
confirmed to become a real Check B failure the instant this branch merges, by copying each file's
pre-fix content into this worktree and reproducing the guard failure. Fixed separately via
`docs/phase1-t411-t412-isolation-fix` (MR !199, merged to `develop` ahead of this closeout,
independent of this branch since those two files live on `develop` already). Re-verified clean
after that fix using the same worktree-copy method.

Full acceptance-bar re-verification after both fixes: `tests/functional/test_golden_held_out_isolation.py`
8/8 (was 7/8 pre-fix, `test_real_repo_has_no_held_out_violations` was never actually run against
the narrative-leak issue — that check only covers identity mentions, not narrative content, which
is exactly why the manual cross-task review was needed); `python3 tests/run.py` exit 0; `git
status` clean under `tests/golden/`, `scripts/`, `docs/benchmarks/scorecard-v6.12.0.*` (untouched,
as required). Status set to `done`. See `docs/tasks/completed-tasks.md` for the ledger entry.
