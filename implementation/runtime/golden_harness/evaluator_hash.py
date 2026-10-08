"""Evaluator-hash tamper-evidence check (T504, `plan-035` nominal `T463`).

`docs/artifacts/protected-paths-v1.md` SS2 item 2, quoted verbatim (the
control this module implements exactly): *"T463's evaluator-hash check (not
yet built, a later task, out of scope here) -- will detect if the
evaluator's on-disk content silently drifts from a known-good hash, a
tamper-evidence control independent of whether the drift was intentional or
accidental."*

This module computes **two separate** SHA-256 digests -- one over
`tests/golden/**`, one over `scripts/scorecard.py` -- and compares each
against a stored known-good reference
(`docs/artifacts/evaluator-hash-known-good-v17.json`). See
`docs/artifacts/evaluator-hash-check-v1.md` for the full design write-up,
including the known-good storage/update policy; this docstring states the
load-bearing properties only.

**This module never writes.** There is no function anywhere in this module
that creates, modifies, or deletes the known-good reference file, or any
other file. Producing/updating the known-good reference is a separate,
explicit, human-invoked action outside this module entirely (see the design
doc's "known-good storage and update policy" section) -- a check function
that could silently accept its own drift by rewriting its own reference
would defeat the entire purpose of a tamper-evidence control.

**A drift finding is a real, valid, reportable result, never an exception.**
`check_evaluator_hash` only raises when the known-good reference file itself
is structurally invalid (missing, unreadable, malformed JSON, or missing a
required key) -- never merely because the computed digests disagree with the
stored ones.

Hashing pattern mirrors `tests/functional/test_meta_improver.py`'s
`test_full_pipeline_leaves_repo_byte_identical`'s own `snapshot()` helper
exactly: SHA-256, sorted `rglob`, each file's repo-relative POSIX path bytes
fed into the hasher before its content bytes, deterministic order.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

# implementation/runtime/golden_harness/evaluator_hash.py -> golden_harness ->
# runtime -> implementation -> repo root. Mirrors kill_switch.py's/
# meta_improver.py's own REPO_ROOT derivation, adjusted for this module's one
# extra package level.
REPO_ROOT = Path(__file__).resolve().parents[3]

# The two protected paths declared by `docs/artifacts/protected-paths-v1.md`
# SS1, reproduced here exactly (not reinvented) -- repo-root-relative POSIX
# strings, matching how `meta_improver.py`'s own target-path handling
# represents repo-relative paths.
PROTECTED_PATH_TESTS_GOLDEN = "tests/golden"
PROTECTED_PATH_SCRIPTS_SCORECARD = "scripts/scorecard.py"

# Digest dict/known-good JSON key names for the two protected paths.
DIGEST_KEY_TESTS_GOLDEN = "tests_golden"
DIGEST_KEY_SCRIPTS_SCORECARD = "scripts_scorecard"

ALGORITHM = "sha256"

DEFAULT_KNOWN_GOOD_PATH = REPO_ROOT / "docs" / "artifacts" / "evaluator-hash-known-good-v17.json"

# Required top-level keys a known-good reference file must declare. Missing
# any of these makes the file structurally invalid (raises), per this
# module's "only a structurally invalid known-good reference should raise"
# contract.
REQUIRED_KNOWN_GOOD_KEYS = frozenset({"algorithm", "digests", "computed_from_commit", "computed_at"})
REQUIRED_DIGEST_KEYS = frozenset({DIGEST_KEY_TESTS_GOLDEN, DIGEST_KEY_SCRIPTS_SCORECARD})


def _iter_tracked_files(repo_root: Path, target: Path) -> list[Path]:
    """Every **git-tracked** file under `target` (or `target` itself if it
    is a single tracked file), sorted, deterministic.

    Uses `git ls-files` rather than a naive filesystem walk (`rglob`) --
    this is a load-bearing correctness fix, not a style choice. A plain
    filesystem walk picks up untracked, gitignored artifacts under
    `tests/golden/**` (concretely: Python's own `__pycache__`/`.pyc`
    bytecode cache, created as an ordinary side effect of dynamically
    importing `expect.py` files -- which every test in this repo that
    scores a golden case, including this module's own real-data tests,
    does). Those files are real, on-disk, and would change the digest
    every time the test suite happens to run before a check, even though
    nothing tracked has changed -- silently defeating the entire point of
    a stable, reproducible known-good baseline. A tamper-evidence check
    must only ever be sensitive to drift in version-controlled content.

    Raises `FileNotFoundError` if `target` has zero git-tracked files
    (covers both "path does not exist" and "path exists on disk but
    nothing under it is tracked" -- either way, not a valid protected-path
    target for this check)."""
    relative = target.relative_to(repo_root).as_posix()
    result = subprocess.run(
        ["git", "ls-files", "--", relative],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    files = sorted(repo_root / line for line in result.stdout.splitlines() if line)
    if not files:
        raise FileNotFoundError(f"no git-tracked files found under protected path: {target}")
    return files


def compute_path_digest(repo_root: Path, relative_path: str) -> str:
    """Compute one SHA-256 digest over `repo_root / relative_path`'s real,
    current on-disk content, restricted to git-tracked files only (see
    `_iter_tracked_files`). For every tracked file under the target
    (sorted, deterministic order), feed the file's repo-relative POSIX
    path bytes into the hasher, then its real, current content bytes read
    fresh from disk -- so an uncommitted local edit to an already-tracked
    file still counts as drift (only the file *set* is git-restricted, the
    content read is always the real working-tree bytes, not `git show`'s
    committed blob)."""
    target = repo_root / relative_path
    hasher = hashlib.sha256()
    for path in _iter_tracked_files(repo_root, target):
        hasher.update(path.relative_to(repo_root).as_posix().encode("utf-8"))
        hasher.update(path.read_bytes())
    return hasher.hexdigest()


def compute_current_digests(repo_root: Path | None = None) -> dict[str, str]:
    """Compute both protected paths' current digests, keyed by
    `DIGEST_KEY_TESTS_GOLDEN` / `DIGEST_KEY_SCRIPTS_SCORECARD`. Two separate
    digests, not one combined digest -- per Piece 1's own requirement, this
    gives a caller a precise answer to *which* protected path drifted, not
    just "something drifted somewhere"."""
    root = repo_root if repo_root is not None else REPO_ROOT
    return {
        DIGEST_KEY_TESTS_GOLDEN: compute_path_digest(root, PROTECTED_PATH_TESTS_GOLDEN),
        DIGEST_KEY_SCRIPTS_SCORECARD: compute_path_digest(root, PROTECTED_PATH_SCRIPTS_SCORECARD),
    }


def compute_git_commit_sha(repo_root: Path | None = None) -> str:
    """Read-only convenience helper: the current `HEAD` commit SHA, via
    `git rev-parse HEAD`. Used only when producing/updating a known-good
    reference (an explicit, human-invoked, out-of-band action -- see module
    docstring); `check_evaluator_hash` itself never calls this, since the
    check compares content digests only and does not care what commit the
    stored known-good value was computed from."""
    root = repo_root if repo_root is not None else REPO_ROOT
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_known_good_payload(repo_root: Path | None = None) -> dict:
    """Build (but never write) the known-good reference payload dict for the
    real, current repo state: both current digests, the algorithm name, the
    current git commit SHA, and a UTC timestamp. This is the one, single,
    disclosed exception to "never automatic" described in the module
    docstring and in `docs/artifacts/evaluator-hash-check-v1.md` --
    establishing the *first* known-good baseline is inherently a one-time
    bootstrap computation, not an ongoing automatic recomputation the check
    performs on its own. This function returns a plain dict; it is the
    caller's job (a human, running this once, out of band) to serialize and
    commit it -- this function itself performs no I/O beyond the read-only
    hashing and the read-only `git rev-parse` call."""
    root = repo_root if repo_root is not None else REPO_ROOT
    return {
        "schema_version": 1,
        "algorithm": ALGORITHM,
        "digests": compute_current_digests(root),
        "computed_from_commit": compute_git_commit_sha(root),
        "computed_at": _utc_now_iso(),
        "protected_paths": {
            DIGEST_KEY_TESTS_GOLDEN: PROTECTED_PATH_TESTS_GOLDEN,
            DIGEST_KEY_SCRIPTS_SCORECARD: PROTECTED_PATH_SCRIPTS_SCORECARD,
        },
    }


def load_known_good(path: Path) -> dict:
    """Read and validate a known-good reference file. Raises `ValueError`
    -- never silently accepts -- for any structurally invalid reference:
    missing/unreadable file, malformed JSON, missing required top-level
    keys, a `digests` value that is not a dict or is missing either
    per-path digest key, or an unsupported `algorithm` value. Never raises
    merely because of what the digests *say* -- only because the file
    itself is not a well-formed known-good reference."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"known-good reference file not found or unreadable: {path}") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"known-good reference file is not valid JSON: {path}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"known-good reference file must contain a JSON object, got {type(data).__name__}: {path}")

    missing = REQUIRED_KNOWN_GOOD_KEYS - data.keys()
    if missing:
        raise ValueError(f"known-good reference file missing required key(s) {sorted(missing)}: {path}")

    digests = data.get("digests")
    if not isinstance(digests, dict) or (REQUIRED_DIGEST_KEYS - digests.keys()):
        raise ValueError(
            f"known-good reference file's 'digests' must be a dict containing keys "
            f"{sorted(REQUIRED_DIGEST_KEYS)}: {path}"
        )

    if data.get("algorithm") != ALGORITHM:
        raise ValueError(
            f"known-good reference file declares unsupported algorithm {data.get('algorithm')!r} "
            f"(only {ALGORITHM!r} is supported): {path}"
        )

    return data


class DriftCheckResult(NamedTuple):
    """Result of one evaluator-hash check. Never a bare boolean -- reports
    per-path drift so a caller/reviewer knows precisely which protected path
    (if any) drifted, plus the digests compared and a human-readable
    summary."""

    tests_golden_drift: bool
    scripts_scorecard_drift: bool
    any_drift: bool
    current_digests: dict[str, str]
    known_good_digests: dict[str, str]
    known_good_commit: str
    known_good_path: Path
    reason: str


def _build_drift_reason(tests_golden_drift: bool, scripts_scorecard_drift: bool) -> str:
    if not tests_golden_drift and not scripts_scorecard_drift:
        return "NO DRIFT: both protected paths match the known-good reference."
    drifted = []
    if tests_golden_drift:
        drifted.append(PROTECTED_PATH_TESTS_GOLDEN)
    if scripts_scorecard_drift:
        drifted.append(PROTECTED_PATH_SCRIPTS_SCORECARD)
    return "DRIFT DETECTED on: " + ", ".join(drifted)


def check_evaluator_hash(
    repo_root: Path | None = None,
    known_good_path: Path | None = None,
) -> DriftCheckResult:
    """The check itself: read the known-good reference (raises `ValueError`
    only if it is structurally invalid -- see `load_known_good`), compute
    the real current digests of both protected paths, and report per-path
    drift plus an aggregate boolean. Read-only end to end: this function
    never writes the known-good reference, and never writes anything else."""
    root = repo_root if repo_root is not None else REPO_ROOT
    kg_path = known_good_path if known_good_path is not None else DEFAULT_KNOWN_GOOD_PATH

    known_good = load_known_good(kg_path)
    known_good_digests = known_good["digests"]
    current_digests = compute_current_digests(root)

    tests_golden_drift = current_digests[DIGEST_KEY_TESTS_GOLDEN] != known_good_digests[DIGEST_KEY_TESTS_GOLDEN]
    scripts_scorecard_drift = (
        current_digests[DIGEST_KEY_SCRIPTS_SCORECARD] != known_good_digests[DIGEST_KEY_SCRIPTS_SCORECARD]
    )
    any_drift = tests_golden_drift or scripts_scorecard_drift

    return DriftCheckResult(
        tests_golden_drift=tests_golden_drift,
        scripts_scorecard_drift=scripts_scorecard_drift,
        any_drift=any_drift,
        current_digests=current_digests,
        known_good_digests=dict(known_good_digests),
        known_good_commit=known_good.get("computed_from_commit", ""),
        known_good_path=kg_path,
        reason=_build_drift_reason(tests_golden_drift, scripts_scorecard_drift),
    )
