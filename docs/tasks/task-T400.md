# Task T400 — Add `scripts/check-version-consistency.py`

**ID:** T400
**Owner:** devops-engineer
**Status:** pending
**Priority:** P0
**Depends on:** —
**Created:** 2026-08-12
**Completed:** —
**Based on:** docs/plans/plan-035-roadmap-v7-ground-up.md (Phase 0, §2.4)

This brief is self-contained. You do not need to read the full plan to execute this task.

## Objective
Add a script, `scripts/check-version-consistency.py`, that fails (non-zero exit) if any
non-archived `.md` file in the repo references a release older than the repo's canonical current
release. This is Gate G0's enforcement mechanism: agents read the docs, and stale version claims
in docs make every downstream inference the harness makes unreliable. Today `implementation/
README.md:4`/`:31` claims v6.0.1 and `README.md:131` links `docs/releases/v6.0.1.md`, while the
actual latest release is v6.10.0 — ten releases of drift with nothing that would catch it.

## Important correction vs. the source roadmap draft
The original roadmap draft said this script should compare against
`implementation/knowledge/VERSION`. **That file does not exist in this repo** (verified by direct
search before this brief was written — no file matching `*VERSION*` exists anywhere under
`implementation/` or the repo root, excluding `.git/`). Do not create it as a side effect of this
task; that would be silently expanding scope beyond what T400 asks for.

The repo's actual canonical "current release" signal, confirmed by direct inspection:
- `README.md` contains the line `Latest release: v6.10.0` (line 14 at time of writing) — this
  exact string pattern (`Latest release: vX.Y.Z`) is also the marker `scripts/
  verify-release-docs.py` asserts against (`MARKER_FILES` list, `marker = f"Latest release:
  {args.tag}"`), so it is already established as this repo's canonical version marker, not
  something you'd be inventing.
- Cross-check candidates you should consider and pick the most robust: the newest-dated file
  under `docs/releases/*.md` (excluding `_template.md`), and/or the newest annotated git tag
  matching `vX.Y.Z` (`git tag --list 'v*' --sort=-v:refname | head -1`).

Your script's job: parse `README.md`'s `Latest release: vX.Y.Z` line to get the canonical current
version, then scan the rest of the repo's non-archived `.md` files for any version string
(`vX.Y.Z` pattern) that is numerically older, and fail if found.

## Inputs
- `README.md` — canonical version marker (`Latest release: vX.Y.Z`)
- `docs/releases/` — per-release docs, for cross-checking the marker is itself sane (newest file
  here should match the README marker)
- `scripts/verify-release-docs.py` — existing precedent for how this repo already treats
  `README.md`'s marker line as canonical; read for consistency, do not modify it (T404 extends it,
  not this task)
- Confirmed current drift to validate your script against (do not fix these — that's T401's job,
  not yours; use them only as a positive test case that your script correctly flags them):
  - `implementation/README.md:4` and `:31` (currently state v6.0.1)
  - `README.md:131` (currently links `docs/releases/v6.0.1.md`)

## Expected outputs
- `scripts/check-version-consistency.py` — new script, executable via `python3 scripts/
  check-version-consistency.py` from repo root, exit 0 on a clean tree / exit non-zero with a
  clear per-file report when drift is found.
- The script must exclude, by path prefix, exactly: `docs/releases/`, `docs/checkpoints/`,
  `docs/archiv/`, `CHANGELOG.md`. These are historical-record directories/files that legitimately
  reference old version numbers by design (a release note for v6.0.1 is supposed to say v6.0.1) —
  do not widen or narrow this exclusion list without reporting why as part of your completion
  report.
- A short usage note (docstring/`--help`) is sufficient; no separate doc page needed for this
  task (README/CONTRIBUTING wiring, if any is warranted, is out of scope here — flag it as a
  finding for T404/T401 if you think it's needed, don't add it yourself).

## Acceptance criteria
1. `python3 scripts/check-version-consistency.py` exits 0 when run against the current tree
   **after** T401 has landed its fix (i.e., your script may legitimately report non-zero before
   T401 lands, since the known drift is real and still present when you write this — confirm your
   script correctly *detects* that drift as its own passing test, then note in your completion
   report that a clean exit-0 run requires T401).
2. A test fixture proves detection: temporarily reverting `implementation/README.md:4` to `v6.0.1`
   (in a scratch copy or via a unit test, not a committed change) makes the script exit non-zero
   with a message identifying the offending file and the stale version string found.
3. Running the script against `docs/releases/v6.0.1.md` itself (or any other historical release
   doc) produces no complaint — the exclusion list works.
4. The script has no side effects — it only reads files and reports; it never edits anything.
5. `bash -n` is not applicable (Python) — instead: `python3 -c "import ast; ast.parse(open('scripts/check-version-consistency.py').read())"` parses without error, and running the script with `--help` (if you add argparse) or with no arguments exits cleanly with a usable message.
6. Add a small automated test (e.g. `tests/functional/test_check_version_consistency.py`) that
   exercises both the pass and fail paths using temp-directory fixtures — do not rely only on
   manual verification, since T404/CI will depend on this script's exit code being trustworthy
   going forward.
7. `python3 tests/run.py` still exits 0 (no regression in the existing suite) after your addition.

## Blocker protocol
Report a blocker (type + severity, per `AGENTS.md`'s Blocker Protocol; max 2 retries before
escalating) if:
- You find a *different* file that already serves as a stronger canonical-version source than
  `README.md`'s marker line (e.g. a machine-readable manifest) — `type: unclear_requirements`,
  `severity: minor`. Do not silently pick a different source without flagging it.
- `scripts/verify-release-docs.py`'s marker-parsing logic doesn't match what's described above
  (i.e. the repo has changed since this brief was written) — `type: dependency`, `severity: major`.

## Git workflow
1. Create branch `feature/T400-phase0-ground-truth-v6.11.0` from the current tip of `develop`.
   This branch will accumulate T400–T405's commits (mirrors the `plan-033`/T377-T380 stacking
   pattern) — do not open an MR yet; T406 handles validation + merge after all of T400–T405 land.
2. Make your change; run all acceptance-criteria checks; confirm all pass.
3. Commit with a Conventional Commit message, e.g.:
   ```
   feat(scripts): add check-version-consistency.py for Gate G0

   Fail CI if any non-archived doc references a release older than
   README.md's canonical "Latest release:" marker. Enforces Gate G0
   (Truth) from plan-035 Phase 0 — agents read the docs, and stale
   version claims make every downstream inference unreliable.

   Refs T400
   ```
4. Do NOT push yet if T401 is expected to stack on the same branch shortly after — coordinate with
   the orchestrator, who owns the branch's push/MR lifecycle per `git-workflow.md`. If instructed
   to push, push only this branch, never `develop`/`main` directly, and do not open the MR
   yourself — report the branch name and commit SHA back to the orchestrator.

## Constraints
- Token budget: ≤20k tokens.
- File ownership: `scripts/check-version-consistency.py` (new) and its test file only. Do not
  touch `README.md`, `implementation/README.md`, or `scripts/verify-release-docs.py` — those are
  T401's and T404's scope respectively.
- No unrelated refactor of any existing script.
