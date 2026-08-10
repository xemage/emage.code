# Task T391 — Test coverage for provenance-tracking mechanism (both directions + bootstrap + bridge)

**ID:** T391
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T390
**Created:** 2026-08-10
**Based on:** docs/plans/plan-034-mcp-provenance-tracking.md (P034-03)

This brief is self-contained. You do not need to read plan-034 or ADR-002 to execute this task, though
you do need T390's implementation already committed on the branch you check out (see Git workflow
below) — read T390's actual committed diff (not this brief's description of it) for the exact,
final CLI flag names and file-naming convention it landed, since T390's brief explicitly allowed it to
deviate from its own reference sketch if ADR-002's committed text required it.

## Objective
Prove T390's provenance-tracking implementation automatically, covering the four proof classes this
whole plan exists to establish: (a) a cwso-style hand-added key survives `--update` when a sidecar is
present; (b) a retired-but-previously-generator-owned key is correctly pruned once real sidecar
history exists across two `--update` runs; (c) a still-currently-generator-owned key is refreshed, not
pruned, even if a stale sidecar claims it; (d) the bootstrap case (no prior sidecar at all) preserves
every dest-only key exactly as before this mechanism existed; plus (e) the one-time
`--force-prune-keys`-style bridge prunes only its exact named keys.

## Inputs (exact paths, verified against the current file just now — re-verify yourself before
editing; the file has almost certainly changed further once T390's commit lands, since T390 touches
`scripts/install.sh` and `scripts/merge-mcp-json.py`, not this test file, so its own 630-line/16-method
shape should be unchanged by T390 — but confirm this assumption, don't trust it blindly)

The file you will edit: `/home/emage/Code/emage/emage.code/tests/functional/test_install_script.py`
(630 lines, 16 existing test methods, as of this brief's authoring, pre-T390).

Existing pattern to extend (read-only reference — do not modify any of these 16 methods):
- `test_fresh_install_plain_copies_mcp_json` (line 169) — fresh install byte-identical to source.
- `test_update_preserves_unknown_mcp_server_key_github` (line 202) / `..._claude_code` (line 274) —
  unknown server key survives `--update` (plan-031/T369 precedent, no sidecar involved at all — these
  predate this plan's mechanism and must keep passing unmodified, proving your new provenance code is
  purely additive and doesn't regress the pre-existing no-sidecar-flags call path... except T390's own
  wiring now always passes sidecar paths for every platform per ADR-002, so if these two pre-existing
  tests still pass after T390's change, that itself is a useful regression signal — do not weaken
  either test to make it pass; if either fails after T390's change, that's a T390 regression, escalate
  per Blocker protocol, do not paper over it here).
- `test_update_refreshes_generator_known_mcp_keys_github` (line 246) / `..._claude_code` (line 318) —
  a generator-known key (`context7`) is refreshed to match generated source.
- `test_cursor_mcp_json_merge_on_update` (line 349), and its four siblings for `gemini` (line 402),
  `opencode` (line 466), `pi` (line 522), `cline` (line 575) — the T377/T378 precedent covering fresh
  copy / unknown-key survival / `context7` refresh / stale-file cleanup for the five tree-based
  platforms. Each already asserts survival of an unknown hand-added key and refresh of `context7` —
  your new tests are ADDITIONAL methods proving the specifically provenance-related behaviors (retired
  key pruning, bootstrap default, force-prune scoping) these five do not yet cover.

The `_run_install` helper (near the top of the file, read-only reference, do not modify) already
supports `platform` and `update` parameters for any of the seven platform names; you do not need a new
helper for that. If T390's sidecar file needs to be read/written directly by your tests (e.g. to seed
a synthetic "old sidecar" state, or to corrupt one for the refresh-not-prune test), read T390's actual
committed sidecar path/schema from its diff and write small local helper code inline in your new test
methods — do not assume this brief's example paths below are exactly right if T390's ADR-002-governed
implementation named things differently; adapt to what was actually committed.

This repo's own `.vscode/mcp.json` real hand-added precedent (`cwso` key under `servers`, plus a
top-level `inputs` array) is the real-world analog for proof class (a) — you do not need to touch that
actual file; use the existing `_run_install`-into-tempdir pattern with a synthetic key, exactly as the
16 existing tests already do.

## Allow-list (files you may touch)
- `tests/functional/test_install_script.py` only. Add new test methods; do not modify any of the 16
  existing test methods already in the file.

## Deny-list (do not touch — no exceptions)
- Do NOT edit `scripts/install.sh`, `scripts/merge-mcp-json.py`, or `implementation/scripts/sync.mjs`
  — T390's already-committed scope; this task only adds test coverage.
- Do NOT edit any of the 16 existing test methods in this file.
- Do NOT edit any other test file.
- Do NOT add a new test module — extend the existing file.
- Do NOT edit `docs/decisions/ADR-002-mcp-merge-provenance-tracking.md`.
- Do NOT create any new branch — use the branch T389/T390 already created (see Git workflow below).

## Required test coverage (minimum content — you may split across more methods than the five
sketched below if that's clearer, but every bullet must be covered by at least one assertion
somewhere in your new methods)

1. **Hand-added key survives with a sidecar present** (proof class (a)): using any one tree-based
   platform (e.g. `cursor`) or a standalone platform (e.g. `github`), run a fresh install (which,
   per T390's implementation, now also writes a sidecar), inject a synthetic unknown key (mirrors
   `cwso`), run `--update`, assert the unknown key survived byte-for-byte AND assert it is absent
   from the sidecar's `generatorOwnedKeys` list both before and after (proving the mechanism's
   "positive evidence required" rule, not merely that pruning happened not to fire).

2. **Retired generator-owned key is pruned once real history exists** (proof class (b)): run a fresh
   install, then hand-edit the resulting sidecar to add a synthetic key name (e.g.
   `"synthetic-retiring-server"`) to `generatorOwnedKeys` as if the generator had owned it at some
   prior generation, also hand-add that same key to the dest MCP JSON file's server map (simulating
   "it used to be there, generator no longer emits it"), then run `--update` and assert the key is
   gone from the post-update MCP file. This directly exercises the two-generation diff T390 documented
   as unavailable via a single `_run_install` call — construct it by mutating the sidecar/MCP files
   in between two `_run_install(..., update=True)` calls, or by directly seeding the "old" sidecar
   state before the second `--update`, whichever matches T390's actual committed sidecar path/schema.

3. **Currently-active generator-owned key is refreshed, not pruned, even if a stale sidecar claims
   otherwise** (proof class (c) — this is the critical over-pruning guard): seed a scenario where a
   REAL generator-owned key (e.g. `context7`, present in every platform's current source) is also
   listed as "retired" by manipulating only the sidecar's `generatorOwnedKeys` list in a way that
   creates an inconsistency — e.g. construct an old-sidecar state and a source such that the diff
   mechanism's "retired" set naively includes `context7`, but `context7` is still genuinely present in
   the freshly generated source. Assert `context7` survives (refreshed to current content, not
   deleted) after `--update`. This proves non-negotiable property #4 from ADR-002/T389's brief: "a key
   `source` still emits is never pruned, regardless of what any sidecar says."

4. **Bootstrap default — no prior sidecar at all preserves every dest-only key** (proof class (d)):
   run a fresh install, then DELETE the sidecar file entirely (simulating an already-installed project
   from before this mechanism existed — the real scenario this repo's own root was in per
   `docs/tasks/active-tasks.md`'s T382 blocker note), inject a synthetic unknown key, run `--update`,
   assert the unknown key survives (identical assertion shape to test 1, but explicitly with the
   sidecar file physically absent beforehand — this is what distinguishes this test from test 1;
   do not skip it as "redundant with test 1").

5. **The one-time force-prune bridge prunes only its exact named keys** (proof class (e)): using
   T390's actual committed flag (`--force-prune-keys` per this plan's naming, or whatever ADR-002
   specified if it differs), invoke `scripts/merge-mcp-json.py` directly (not through
   `install.sh --update`, since this flag is a one-time bridge invoked explicitly, not part of the
   installer's normal per-platform call chain — confirm this against T390's actual wiring; if T390
   wired it into `install.sh` itself behind a new installer flag instead, invoke it that way and note
   the adaptation) against a dest file containing both a synthetic dest-only key you name in the flag
   and a `cwso`-style dest-only key you do NOT name; assert the named key is gone, the unnamed
   `cwso`-style key survives untouched. Additionally assert that naming a key which is NOT actually
   dest-only (e.g. `context7`) causes a non-zero exit and no write to `--dest` (read the dest file
   before and after, assert byte-identical).

## Tests to run (literal commands, run from repo root `/home/emage/Code/emage/emage.code`)

1. Targeted run of just this file:
   ```
   python3 -m unittest tests.functional.test_install_script -v
   ```
   PASS = all methods report `ok` (16 pre-existing + your new ones), `OK` at the end, exit 0.

2. Full functional suite:
   ```
   python3 tests/run.py --suite functional -v
   ```
   PASS = exits 0, no `FAILED`/`ERROR` lines.

3. Full suite (same gate T393 will run):
   ```
   python3 tests/run.py
   ```
   PASS = exits 0. Capture your own before/after counts — your new tests must increase the total count
   and must not reduce it.

## Acceptance criteria (all must be true)
- [ ] `git diff` shows changes in exactly one file: `tests/functional/test_install_script.py`.
- [ ] Test proves: a synthetic hand-added key with no sidecar entry survives `--update` when a sidecar
      is present (proof class (a) / requirement 1).
- [ ] Test proves: a synthetic key present in an old sidecar's generator-owned set, and absent from
      the new source, is pruned on `--update`, using a real two-generation sequence (not a single-shot
      assertion) (proof class (b) / requirement 2).
- [ ] Test proves: a synthetic/real key present in an (inconsistent/stale) old sidecar's
      generator-owned set, but still present in the new source, is refreshed — NOT pruned — proving
      the mechanism never over-prunes an actively-current server regardless of sidecar content (proof
      class (c) / requirement 3).
- [ ] Test proves: `--update` with no old sidecar file at all preserves every dest-only key (proof
      class (d) / requirement 4), with the sidecar file's absence constructed explicitly, not
      incidentally.
- [ ] Test proves: the force-prune bridge prunes only the named key(s); an unnamed hand-added key
      survives even when the flag is used; naming a key that is not actually dest-only causes a
      non-zero exit and no partial write (proof class (e) / requirement 5).
- [ ] `python3 -m unittest tests.functional.test_install_script -v` passes.
- [ ] `python3 tests/run.py` exits 0, total test count increased from your own recorded baseline.
- [ ] None of the 16 pre-existing test methods in this file were modified.

## Blocker protocol
STOP and report a blocker (do not improvise a workaround) if:
- The branch T389/T390 created does not exist, or does not contain T390's commit → `type:
  dependency`, `severity: critical` — T391 cannot proceed without T390's completed implementation.
- T390's actual committed sidecar naming/schema, or `merge-mcp-json.py`'s actual committed CLI flag
  names, differ from what this brief assumes — adapt your tests to what was actually committed (read
  T390's diff directly); this is expected, not itself a blocker, UNLESS the actual implementation is
  ambiguous or undocumented enough that you cannot determine the right test shape, in which case →
  `type: dependency`, `severity: major`, report exactly what's unclear.
- Any test you write for requirement 1, 2, 3, 4, or 5 genuinely fails against T390's real committed
  code (not a test-authoring mistake on your part) → `type: technical`, `severity: major` — report
  the actual observed behavior; do not weaken your assertion to hide a real regression or design gap
  in T390's implementation. This is exactly the scenario T391 exists to catch, especially requirement
  3 (over-pruning guard), which is the single most safety-critical proof point in this whole plan.
- Any test fails for a reason unrelated to your added tests (a pre-existing test regresses) → `type:
  technical`, `severity: major`, include exact command output; do not modify the pre-existing test to
  make it pass.

Max 2 retries before escalating to the orchestrator with full context.

## Git workflow
1. Check out the EXISTING branch `feature/T389-mcp-merge-provenance-tracking` (created by T389,
   extended by T390 — do NOT create a new branch, do NOT branch from `develop`).
2. Confirm T389's and T390's commits are both present (`git log --oneline -5`).
3. Make the change; run all tests above; confirm all pass.
4. Commit with a Conventional Commit message, e.g.:
   ```
   test(mcp): cover provenance sidecar pruning, bootstrap default, and force-prune bridge

   Proves T390's ADR-002 implementation in both required directions: a
   hand-added key survives --update with a sidecar present or absent
   (bootstrap default), a retired generator-owned key is pruned once real
   two-generation sidecar history exists, a still-current generator-owned
   key is refreshed rather than pruned even under a stale/inconsistent
   sidecar (the critical over-pruning guard), and the one-time
   force-prune-keys bridge prunes only its named keys while erroring on a
   key that isn't actually dest-only.

   Refs T391
   ```
5. Do NOT push. Do NOT open a merge request. Do NOT merge to `develop` or `main`. Stop after the
   local commit (stacked on top of T389's/T390's commits, same branch) and report completion (commit
   SHA, full test output) back to the orchestrator. T392 will stack a further commit on this same
   branch; T393 will push it and open the MR.

## Constraints
- Token budget: ≤25k tokens.
- File ownership: `tests/functional/test_install_script.py` only.
- No unrelated refactor of this file.
