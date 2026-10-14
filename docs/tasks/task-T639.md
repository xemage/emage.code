# T639 — Apply the approved release-document and release-order amendments (T632 groups A1, B1 and the text part of C3)

**ID:** T639
**Owner:** backend-developer
**Status:** pending
**Priority:** P1
**Tier:** mechanical
**Depends on:** —
**Affects:** —
**Created:** 2026-10-15
**Completed:** —
**Based on:**
- `docs/plans/plan-121-release-v8-wave-2.md` (Addendum 3: T639)
- `docs/artifacts/release-documents-ruling-v1.md` §4 (the contract), §7.1 (H-A1..H-A5), §7.2 (H-B1..H-B6; H-B7 is optional and is NOT applied), §7.3 (H-C1), §8 hit counts, §9 effects, handoff package
- `docs/decisions/ADR-008-knowledge-document-authority.md`, `AGENTS.md`
- The user's answers of 2026-10-15 (AskUserQuestion, verbatim option labels): T632 group A "A1: union contract + fixes (Recommended)", group B "B1: develop, then main, then tag (Recommended)", group C "C3: the document only (Recommended)"; T637: SEC-002 grade "Yes, HIGH for that entry (Recommended)", replacements "Approve all four (Recommended)", pins "Approve the proposed pins (Recommended)", docker and postgresql "Remove both"; ADR-009 "Accept ADR-009 as written (Recommended)".

## 1. What and why

Apply, verbatim, the held fences the user approved: H-A1 (`docs/releases/_template.md`, replace the whole file), H-A2 (`orchestrator.md`), H-A3 (`release-workflow` skill), H-A4 (`CONTRIBUTING.md` step 3), H-A5 (two one-line wording edits); H-B1 (`CONTRIBUTING.md`, five fences), H-B2 (`.gitlab/merge_request_templates/Release.md`, replace the whole file), H-B3 (`orchestrator.md`), H-B4 (`release-manager.md`, two fences), H-B5 (`release-workflow` skill hotfix steps), H-B6 (two wording edits outside the knowledge tree); and H-C1 (`CONTRIBUTING.md` step 8 bullets, for C3). Do NOT change `/prepare-release` (`implementation/knowledge/commands/prepare-release.md`), `verify-release-docs.py`, any CI file or `publish-release.py` (that is T640), and do not apply H-B7. Run the ruling's pre-flight greps first (exclude `tests/golden/held-out/`, which you never open); apply each pair by exact string replacement asserting every Before occurs exactly once (anchor by text; line numbers drift); for the whole-file replacements assert the old file's content equals the ruling's Before (or its recorded hash) before overwriting; stop and report as a `dependency` blocker if an anchor is missing/not unique or any test or open golden case asserts a Before string. Never reword. Note the dependency on T624 and T631: T624 changed `orchestrator.md`; T631 changed README/wiki files (not the ones above). Expected root drift about 19 (orchestrator 6, release-manager 6, release-workflow skill 7); `docs/releases/_template.md`, `CONTRIBUTING.md` and the Release MR template are not projected.

## 2. Output

The edited files, regenerated mirrors and registry, the drift baseline, and a report with the pre-flight greps, every hit count after the edits (lines/occurrences), gate results, the suite summary line and every deviation.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line; do not edit generated platform folders by hand; no root refresh.
- Regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py` when a projected file changes; declare ALL root drift in `tests/_baselines/root-install-drift.json` (it currently lists the 33 paths of T624 and may list more by the time you start: add, never remove; sorted paths plus one comment line starting "Declared 2026-10-15 by <task> (").
- Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`, `scorecard.py --check` (34/26/0), `docs/tasks/validate-tasks.py`, the evaluator hash (baseline v20 unchanged), the held-out isolation test, and the full suite `python3 tests/run.py` redirected to a file.
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere. No `.env*` or credential files; do not read the user's local `.claude/settings.json` or `.vscode/mcp.json`.

## 4. Acceptance criteria

1. Every Before replaced exactly once with its After; nothing else changed in the source files; the byte-unchanged list holds (`/prepare-release`, `verify-release-docs.py`, scripts, CI, `tests/golden/**`).
2. All gates and the full suite pass; no grant or baseline needed (report if one is); no root refresh.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
