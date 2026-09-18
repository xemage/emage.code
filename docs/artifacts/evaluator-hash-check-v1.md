# Evaluator-Hash Tamper-Evidence Check — v1

**Based on:** `docs/tasks/task-T504.md` (`plan-035-roadmap-v7-ground-up.md`'s nominal `T463`,
`docs/plans/plan-055-phase6-closed-loop-rescoped-detailed-planning.md` §4's `T463-equiv` row),
`docs/artifacts/protected-paths-v1.md` §1/§2 item 2/§5 (the authoritative source for the two
protected paths and the exception-path process this task's update policy reuses),
`tests/functional/test_meta_improver.py`'s `test_full_pipeline_leaves_repo_byte_identical` (the
hashing pattern this check mirrors exactly), `docs/artifacts/phase6-kill-switch-v1.md` (T502) and
`docs/artifacts/meta-improver-v1.md` (T503, style precedent for this document).

**Refs:** T504. Builds Piece 1 of Phase 6's validation/promotion-rule task.

## 1. What this document declares

This repository now has a real, tested evaluator-hash tamper-evidence check:

- `implementation/runtime/golden_harness/evaluator_hash.py` — the importable library:
  `compute_path_digest`, `compute_current_digests`, `compute_git_commit_sha`,
  `build_known_good_payload`, `load_known_good`, `check_evaluator_hash`, and the `DriftCheckResult`
  result type.
- `docs/artifacts/evaluator-hash-known-good-v1.json` — the bootstrapped known-good reference,
  computed from the real, current repo state at commit `49415a3ac19e93ffb78595d6d515e6a96e93f60b`.
- `tests/functional/test_golden_harness_evaluator_hash.py` — the committed test suite proving
  every property documented below.

Per `docs/artifacts/protected-paths-v1.md` §2 item 2, quoted verbatim: this check will *"detect if
the evaluator's on-disk content silently drifts from a known-good hash, a tamper-evidence control
independent of whether the drift was intentional or accidental."* This document implements exactly
that control, not a reinvented variant.

## 2. What it declares (the two protected paths, hashed separately)

Two SHA-256 digests are computed, one per protected path declared by `protected-paths-v1.md` §1:

- `tests_golden` — over `tests/golden/**`.
- `scripts_scorecard` — over `scripts/scorecard.py`.

**Two separate digests, not one combined digest.** A future caller (a human reviewer, or
T464-equiv's eventual MR gate) needs a precise answer to "*which* of the two protected paths
drifted," not just "something drifted somewhere" — a single combined digest would collapse that
distinction and make triage strictly harder. `DriftCheckResult` reports `tests_golden_drift` and
`scripts_scorecard_drift` independently, plus an aggregate `any_drift` boolean for callers that
only need the combined answer (e.g. `promotion.py`'s conjunct 3).

## 3. Hashing pattern, and a load-bearing correctness fix found during independent verification

`compute_path_digest(repo_root, relative_path)` hashes every **git-tracked** file under the
target path, sorted, deterministic order: for each file (`git ls-files` restricted to the target
path, or a single-element list when the target is itself a tracked file — generalizing the
pattern to `scripts/scorecard.py`, which is a file, not a directory), feed the file's
repo-relative POSIX path bytes into a SHA-256 hasher, then its real, current content bytes read
fresh from disk.

**This originally mirrored `tests/functional/test_meta_improver.py`'s `snapshot()` helper
exactly — a plain, sorted `rglob("*")` filesystem walk, not a git-tracked-only walk — and that
was a real bug, not a style choice, caught during the top-level session's independent
verification of this task before merge.** `tests/golden/**` accumulates Python's own
`__pycache__`/`.pyc` bytecode cache as an ordinary side effect of dynamically importing
`expect.py` files (which every golden-suite-scoring code path in this repo does, including this
module's own real-data tests). Those files are real, on-disk, gitignored, and were being picked
up by the naive walk — meaning the digest changed depending on whether and how recently the test
suite had run in a given environment, even though nothing tracked had changed. This silently
defeated the entire point of a stable, reproducible known-good baseline: the originally-bootstrapped
`v1` hash for `tests_golden` failed to reproduce in the top-level session's own fresh verification
worktree, which is exactly how the bug was caught rather than shipped. Fixed by hashing only
`git ls-files`-enumerated paths; re-bootstrapped and independently confirmed stable across a
`__pycache__`-present/absent A/B comparison after the fix (identical digest both ways).
`tests/functional/test_golden_harness_evaluator_hash.py`'s
`test_an_untracked_new_file_under_tests_golden_is_not_reported_as_drift` is the direct,
non-tautological proof the fix achieves its stated purpose, not merely that old behavior changed.

**Path additions and deletions are detected, not just content edits — but only once tracked.**
Because every file's repo-relative path is fed into the hasher before its content, adding a new
*tracked* file (or removing an existing one) under a protected path changes the digest, even if
every pre-existing file's own content is untouched.
`test_adding_and_committing_a_new_file_under_tests_golden_is_detected_as_drift` proves this
directly; an *untracked* addition (the `__pycache__` case above) correctly does not count.

## 4. Storage: `docs/artifacts/evaluator-hash-known-good-v1.json`

A new, small, versioned artifact, mirroring how `phase6-kill-switch-v1.md` (a sentinel file under
`tmp/`) and `meta-improver-v1.md` (a plain Python module, no persisted state) each picked and
justified their own storage location. Structure (all keys present in the real committed file):

```json
{
  "schema_version": 1,
  "algorithm": "sha256",
  "digests": { "tests_golden": "<64-hex-char digest>", "scripts_scorecard": "<64-hex-char digest>" },
  "computed_from_commit": "<git commit SHA the digests were computed from>",
  "computed_at": "<UTC ISO-8601 timestamp>",
  "protected_paths": { "tests_golden": "tests/golden", "scripts_scorecard": "scripts/scorecard.py" },
  "update_policy": "<pointer to this document's §5, restated inline for a reader who only has the JSON open>"
}
```

`load_known_good` requires at minimum `algorithm`, `digests` (containing both per-path keys),
`computed_from_commit`, and `computed_at` — a file missing any of these, or declaring an
unsupported `algorithm`, is structurally invalid and `load_known_good` raises `ValueError`. This
is a machine-readable sidecar to this prose design doc, not the design doc itself — the JSON file
carries no narrative, only the values a check needs to compare against.

## 5. Known-good storage and update policy — decided here, not left ambiguous

**Update policy: manual only, never automatic, via `protected-paths-v1.md` §5's existing exception
path — no new mechanism was invented.** That section already defines the process a future,
legitimate change to `tests/golden/**` or `scripts/scorecard.py` must go through: *"Never a silent
edit... Always a named, authorized task... Ordinary review still applies."* Updating the known-good
hash after such a change is part of that same exception-path task, not a separate automatic
recomputation this module performs on its own.

**Per this repo's Artifact Versioning convention** (`AGENTS.md`: "Revisions create new versions,
never overwrite"), a future legitimate update produces `evaluator-hash-known-good-v2.json` — it
does not edit `v1` in place. `v1` remains the historical record of what the protected paths' content
was at the time this check was first built; a future reader diffing `v1` against `v2` can see
exactly what changed and when, the same auditability benefit every other artifact version in this
repo already provides.

**`evaluator_hash.py` itself never writes the known-good reference.** There is no function in this
module that creates, modifies, or deletes `evaluator-hash-known-good-v1.json` (or any known-good
file) as a side effect of checking. `check_evaluator_hash` and `load_known_good` are read-only
end to end; `build_known_good_payload` *constructs* a payload dict in memory (used only when
producing/updating a known-good reference — an explicit, out-of-band, human-invoked action) but
performs no I/O to write it anywhere. A check function that could silently accept its own drift by
rewriting its own reference would defeat the entire purpose of a tamper-evidence control — this
module structurally cannot do that.

**Bootstrapping this task's own known-good value — the one, single, disclosed exception to "never
automatic."** `docs/artifacts/evaluator-hash-known-good-v1.json` was produced by calling
`build_known_good_payload()` once, directly, against the real, current, on-disk content of
`tests/golden/**` and `scripts/scorecard.py` at commit `49415a3ac19e93ffb78595d6d515e6a96e93f60b`,
and committing the resulting values as `v1`. This is inherently a one-time bootstrap action —
establishing the *first* known-good baseline has no prior baseline to compare against — not an
ongoing automatic recomputation the check performs going forward. Stated explicitly here so a
future reader does not mistake this task's own bootstrap step for the check silently trusting its
own current state on every run: every subsequent invocation of `check_evaluator_hash` compares the
*current* on-disk digests against the *frozen* `v1` values, and reports drift honestly if they ever
disagree — it never re-bootstraps itself.

## 6. Never raises on drift — only a structurally invalid reference raises

`check_evaluator_hash` never raises merely because the computed digests disagree with the stored
ones — a drift finding is a real, valid, reportable result (`DriftCheckResult` with
`any_drift=True`), not an error condition. The only case that raises `ValueError` is a structurally
invalid known-good reference file: missing/unreadable file, malformed JSON, a value that is not a
JSON object, a missing required top-level key, a `digests` value missing either per-path key, or an
unsupported `algorithm`. `tests/functional/test_golden_harness_evaluator_hash.py`'s
`TestMalformedKnownGood` proves both halves of this distinction: five distinct malformation shapes
each raise, while a well-formed reference whose digests simply disagree with the current repo state
does not raise (`test_well_formed_reference_with_a_digest_mismatch_does_not_raise`).

## 7. What this does *not* do (scope boundary)

- **No automatic recomputation or self-healing.** There is no code path anywhere in this module
  that updates the known-good reference in response to a detected drift, intentional or otherwise.
  A drift finding is purely informational to whatever caller invoked the check (today: nothing —
  see below; going forward: `promotion.py`'s conjunct 3, and eventually T464-equiv's MR gate).
- **No caller wired in yet beyond this task's own `promotion.py`.** `promotion.py`'s
  `evaluate_promotion` consumes a caller-supplied `DriftCheckResult` (typically produced by calling
  `check_evaluator_hash()` once per validation cycle) as its third conjunct — that is the one real
  consumer this task builds. T464-equiv (the human MR gate) does not exist yet and is not part of
  this task.
- **No enforcement of the known-good file's own write-permissions or a commit-time hook.** Like
  `protected-paths-v1.md` §4's own declared scope boundary, this is a declarative-plus-review
  control: nothing here prevents a determined or malfunctioning process from editing
  `evaluator-hash-known-good-v1.json` directly outside the documented exception path. Enforcement is
  (a) this document's own stated policy, (b) ordinary code review catching any violation, and (c)
  the fact that `evaluator_hash.py` itself has no write path to that file at all, so at minimum the
  *check's own code* cannot be the source of an unauthorized update.
- **No support for any hash algorithm other than SHA-256.** `load_known_good` rejects any
  `algorithm` value other than `"sha256"` — this is a deliberate, narrow scope, not an oversight;
  broadening it is a future, explicitly-scoped decision if ever needed.

## 8. Verification

- `tests/functional/test_golden_harness_evaluator_hash.py` — 17 tests: real-repo no-drift proof
  against the committed `v1` reference (`TestRealRepoNoDrift`), real drift-detection tests against
  scratch copies of the protected paths covering content mutation on each path independently, both
  paths simultaneously, and file addition (`TestDriftDetection`), structural-validity tests proving
  only a malformed known-good reference raises while a well-formed-but-mismatched one does not
  (`TestMalformedKnownGood`), and a consistency check that the committed `v1` JSON's digests match
  what `build_known_good_payload` computes today (`TestBuildKnownGoodPayload`).
- `tests/functional/test_golden_held_out_isolation.py` re-run fresh after adding this task's files:
  8/8 pass — no held-out isolation violation introduced.
- Run directly: `python3 -m unittest tests.functional.test_golden_harness_evaluator_hash -v`.
- Included automatically in `python3 tests/run.py` (discovered under `tests/functional/`).
