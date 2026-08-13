# Task T402 — Split docs into end-user vs. contributor entry points

**ID:** T402
**Owner:** technical-writer
**Status:** done
**Priority:** P1
**Depends on:** —
**Created:** 2026-08-12
**Completed:** —
**Based on:** docs/plans/plan-035-roadmap-v7-ground-up.md (Phase 0, §2.4)

This brief is self-contained.

## Objective
Ensure `docs/wiki/quick-start.md` is the single end-user entry point (install, use, upgrade) and
`CONTRIBUTING.md` is the single contributor entry point (build, test, release), with neither
linking into the other's tree except via exactly one explicit cross-link each way.

## Important correction vs. the source roadmap draft
The original roadmap draft phrased this as if these two files need to be created from scratch.
**Both already exist** (`docs/wiki/quick-start.md`, 88 lines; `CONTRIBUTING.md`, 312 lines,
verified at brief-authoring time). Your job is an **audit and correction** task, not a greenfield
build:
1. Confirm `docs/wiki/quick-start.md` contains only end-user content (install, use, upgrade) and
   does not leak contributor-only material (build-from-source internals, release process,
   `implementation/scripts/` internals, testing harness details).
2. Confirm `CONTRIBUTING.md` contains only contributor content (build, test, release process) and
   does not duplicate/leak end-user quick-start instructions that belong in the wiki page instead.
3. Confirm there is **exactly one** explicit cross-link from each file to the other (e.g.
   `quick-start.md` linking to `CONTRIBUTING.md` for "want to build from source?", and
   `CONTRIBUTING.md` linking to `quick-start.md` for "just want to use it? see the quick start").
   At brief-authoring time, a grep for cross-references between these two files returned **zero
   hits** — confirm this is still true, and if so, add exactly one link each direction at an
   appropriate point in each file (do not add more than one each way).
4. If you find contributor content in `quick-start.md` or end-user content in `CONTRIBUTING.md`,
   move it to the correct file rather than deleting it, preserving the information.

## Inputs
- `docs/wiki/quick-start.md` (full file, 88 lines)
- `CONTRIBUTING.md` (full file, 312 lines)
- `docs/wiki/README.md`, `docs/wiki/home.md` — check these don't already establish a different
  navigation contract that your changes would conflict with; read before editing.
- `scripts/verify-release-docs.py`'s `SECTION_REQUIREMENTS` dict — `docs/wiki/quick-start.md` and
  `CONTRIBUTING.md` both have CI-enforced required section headers/snippets already (e.g.
  `quick-start.md` must keep `## 1. Install`, `## 4. Invoke the orchestrator`, `/new-project`,
  `scripts/install.sh`; `CONTRIBUTING.md` must keep `## Releasing`, `### Cutting a release`,
  `## Working with implementation`, `release-docs-gate`, `verify-release-docs.py`). **Do not
  remove or rename any of these required headers/snippets** — your edits must stay compatible
  with this existing CI gate, verify by re-reading `SECTION_REQUIREMENTS` before you finish.

## Expected outputs
- `docs/wiki/quick-start.md` — corrected if any contributor-only leakage is found; one new
  cross-link to `CONTRIBUTING.md` added if not already present.
- `CONTRIBUTING.md` — corrected if any end-user-only leakage is found; one new cross-link to
  `docs/wiki/quick-start.md` added if not already present.
- A short note in your completion report listing what you found (clean split already / leakage
  found and moved / cross-links added) — this is read by T406's validation gate.

## Acceptance criteria
1. `docs/wiki/quick-start.md` contains no contributor-only content (build internals, release
   process, test harness internals) — end-user only.
2. `CONTRIBUTING.md` contains no duplicated end-user quick-start instructions that belong solely
   in the wiki page.
3. Exactly one explicit link exists from `quick-start.md` to `CONTRIBUTING.md`, and exactly one
   from `CONTRIBUTING.md` to `quick-start.md` — no more, no fewer.
4. Every `SECTION_REQUIREMENTS` snippet for both files (per `scripts/verify-release-docs.py`) is
   still present after your edit — run `python3 scripts/verify-release-docs.py --tag
   v6.10.0` (or whatever the current `README.md` marker states) locally against your changes and
   confirm no new failure is introduced by your edit (pre-existing failures unrelated to your
   change, if any, are not your responsibility to fix here — note them instead).
5. No broken internal links introduced (re-run the link-check portion of `verify-release-docs.py`
   or equivalent).

## Note on tooling access
Per `.claude/rules/security-guidelines.md`, you (Technical Writer) do not have Bash/git access.
Make your edits directly with Write/Edit; the orchestrator runs the verification commands and
commits on your behalf.

## Blocker protocol
- If `quick-start.md` or `CONTRIBUTING.md` already fully satisfy every acceptance criterion with
  no changes needed, that's a valid outcome — report "audit complete, no changes required," don't
  invent busywork.
- If fixing a leak would require removing a `SECTION_REQUIREMENTS`-protected snippet — `type:
  unclear_requirements`, `severity: minor` — report rather than breaking the existing release gate.

## Git workflow
Same shared branch as T400/T401: `feature/T400-phase0-ground-truth-v6.11.0`. Orchestrator commits
your edits with a Conventional Commit message, e.g.:
```
docs: confirm/tighten end-user vs. contributor doc split

Refs T402
```
(Adjust the message body based on what you actually found/changed — "confirm" if it was already
clean, "tighten" or "fix" if leakage was found and corrected.)

## Constraints
- Token budget: ≤15k tokens.
- File ownership: `docs/wiki/quick-start.md`, `CONTRIBUTING.md` only.
