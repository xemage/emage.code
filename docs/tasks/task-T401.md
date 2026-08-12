# Task T401 — Fix confirmed version drift

**ID:** T401
**Owner:** technical-writer
**Status:** pending
**Priority:** P0
**Depends on:** —
**Created:** 2026-08-12
**Completed:** —
**Based on:** docs/plans/plan-035-roadmap-v7-ground-up.md (Phase 0, §2.4)

This brief is self-contained.

## Objective
Fix the confirmed, currently-live version drift so published docs state the true current release
(v6.10.0 at the time this brief was written — **re-confirm the actual current value of `README.md`'s
`Latest release:` line at execution time**, since a release may have shipped between brief-authoring
and execution). Specifically:
- `implementation/README.md:4` states `(**v6.0.1**).` — ten releases stale.
- `implementation/README.md:31` states `Latest release: v6.0.5` — also stale, and internally
  inconsistent with line 4's `v6.0.1` (the file contradicts itself).
- `implementation/README.md:31` links `docs/releases/v6.0.1.md`.
- `README.md:131` links `docs/releases/v6.0.1.md`.

(Line numbers above are as read at brief-authoring time — re-verify against the current file
before editing; if they've shifted, that's not a blocker, just re-locate the same text.)

## Addendum (orchestrator decision, 2026-08-12, scope expanded by one file)
Running T400's script against the full tree surfaced a **fourth genuine drift point** not in the
original brief, structurally identical to the three above (a "current release" claim plus a
`docs/releases/` link, both stale): `docs/wiki/implementation-guide.md:5` states "current release:
v6.0.2" and `:33` links `docs/releases/v6.0.2.md`. Fix this file too, using the same approach as
the three originally-named locations — correct the version to match `README.md`'s canonical
`Latest release:` marker and correct the release-doc link to point at the file that actually
exists for that version. See `task-T400.md`'s addendum for the full context on how this was found
(a version-consistency script run, not manual re-audit) and why the script's exclusion list was
widened rather than expecting T401 to fix the ~700+ historical-record false positives that same
run also produced (those are legitimate past-tense statements in `docs/tasks/`/`docs/plans/`/
`docs/artifacts/`, out of scope for this task and now excluded at the script level instead).

## Inputs
- `implementation/README.md` (lines 1-35 approx — read the whole file's header/intro section, not
  just the flagged lines, since the surrounding prose may reference the same stale version in
  other phrasing not caught by the line-number grep above)
- `README.md` (root, around line 131 and its surrounding "Documentation release contract" /
  install section)
- `docs/wiki/implementation-guide.md` (lines ~1-35 — see Addendum below: line 5's "current
  release: v6.0.2" and line 33's link to `docs/releases/v6.0.2.md`, a fourth drift point found
  after this brief was originally written)
- `README.md`'s own `Latest release: vX.Y.Z` line — this is the canonical value to propagate; do
  not invent a version number, read it from the file.
- `docs/releases/` directory listing — confirms which release doc actually exists for the current
  version (link targets must point at a file that exists).

## Expected outputs
- `implementation/README.md` — line 4 and line 31 (and any other stale reference found by a full
  read of the file's intro) corrected to the true current version; the `docs/releases/v6.0.1.md`
  link corrected to point at the release doc matching the current version.
- `README.md` (root) — line 131's link corrected the same way.
- `docs/wiki/implementation-guide.md` — line 5 and line 33 corrected the same way (see Addendum).
- A grep sweep: after your edits, `grep -rn "v6\.0\.[125]" README.md implementation/README.md
  docs/wiki/implementation-guide.md` (adjust the pattern to whatever stale versions you actually
  found) should return zero hits.

## Acceptance criteria
1. `implementation/README.md` no longer contains any reference to a version older than the current
   `README.md` "Latest release" marker.
2. `README.md` (root) no longer links to a release doc for a version older than current.
3. `docs/wiki/implementation-guide.md` no longer contains any reference to a version older than
   current, and its `docs/releases/` link is corrected the same way.
4. All three files' version references are mutually consistent with each other and with
   `README.md`'s own marker line (no internal self-contradiction like the current
   v6.0.1-vs-v6.0.5 mismatch).
5. Every link you touch or introduce resolves to a file that actually exists (`docs/releases/
   <version>.md`) — verify with a direct file existence check, not by assumption.
6. No other content in any of the three files changes — this is a targeted drift fix, not a
   rewrite.
7. Once `scripts/check-version-consistency.py` (T400, including its addendum's widened exclusion
   list and context-gate refinement) exists on the shared branch, running it against the tree
   after your fix should no longer flag any of these three files (coordinate order of operations
   with the orchestrator — T400 and T401 may land in either order on the shared branch, but the
   final state after both must satisfy this).

## Note on tooling access
Per this repo's agent permission classification (`.claude/rules/security-guidelines.md` —
Technical Writer is documentation-files-only and does not carry Bash/git access), you make the
file edits directly (you have Write/Edit tools) but the orchestrator performs the actual git
commit on your behalf after reviewing your diff — this mirrors the established precedent from
plan-033/T370 ("Technical Writer had no Bash/git access this session... orchestrator reviewed and
committed on its behalf"). Report your edits as complete and let the orchestrator handle git.

## Blocker protocol
- If you find additional stale-version references beyond the four locations named above (e.g. in
  a section of `implementation/README.md` not covered by the flagged line numbers) — this is
  expected and in-scope; fix them too, and note what you found in your completion report. This is
  not a blocker, just note it.
- If the current `README.md` "Latest release" marker itself looks wrong/inconsistent with the
  newest file in `docs/releases/` — `type: unclear_requirements`, `severity: minor` — report
  rather than guessing which is authoritative.

## Git workflow
Same shared branch as T400: `feature/T400-phase0-ground-truth-v6.11.0` (created by T400 or, if
T401 executes first, create it from `develop`'s current tip). Make your edits; the orchestrator
commits on your behalf with a Conventional Commit message, e.g.:
```
fix(docs): correct stale version references in README files

implementation/README.md stated v6.0.1 (line 4) and v6.0.5 (line 31)
against each other and against the actual current release; both
files linked docs/releases/v6.0.1.md. Ten releases of drift with
nothing to catch it — see T400's new consistency checker.

Refs T401
```
Do not push or open an MR — that's handled by the orchestrator per the T400 brief's shared-branch
note; T406 performs the final validation gate and merge.

## Constraints
- Token budget: ≤12k tokens (raised slightly from the original 10k to account for the addendum's
  third file).
- File ownership: `implementation/README.md`, `README.md` (root), `docs/wiki/
  implementation-guide.md` — version-reference lines only. Do not touch any other file.
