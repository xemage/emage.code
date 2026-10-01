# T567 — Amend `/validate-workflow` step 5's gate list (T566 FU-1)

**ID:** T567
**Owner:** Backend Developer
**Status:** pending
**Priority:** P2
**Tier:** mechanical
**Affects:** command/validate-workflow
**Depends on:** T566
**Created:** 2026-10-01
**Based on:** `docs/artifacts/validate-workflow-gate-resolution-v1.md` §5(a), §5(b) and §9; `docs/plans/plan-093-validate-workflow-repair.md`.

## 1. What and why

T566 ruled under ADR-007 branch 1 that `/validate-workflow` step 5's gate list is the defective clause. The list
becomes the `validation-gates` skill's five gate types in pipeline order. The architecture briefing is replaced by
the Architecture gate, and plan approval leaves the list. **The wording is fully specified, so nothing is left to
choose.**

## 2. The edit

In `implementation/knowledge/commands/validate-workflow.md`, replace **lines 25–32 exactly** with the "After" block
of artifact §5(a), byte for byte. Copy it from the artifact; do not retype it.
- Each bullet's separator is ` — ` (space, U+2014 EM DASH, space).
- The new bullet's name is exactly `Architecture review gate`.
- The order is Architecture → Implementation (Code review) → Integration → Security → Release.
- Line 24 and every other line stay unchanged. The file becomes one line shorter.

Confirm the edit applied: `git diff -U0` must show a single hunk at lines 25–32, and nothing else.

## 3. Regenerate and declare

1. `node implementation/scripts/sync.mjs --root implementation` **and** `python3 implementation/scripts/generate-registry.py`.
2. Run `python3 -m tests.functional.test_root_install_parity --print-drift`. Add **exactly** the new root paths to
   the `drift` list in `tests/_baselines/root-install-drift.json` and keep the existing 36. Artifact §9.1 expects
   six paths, one per platform: `.claude`, `.cursor`, `.gemini`, `.github`, `.opencode` and `.pi`. **Never
   hand-edit the top-level platform folders.**

## 4. Verify, don't assume

- `sync.mjs --check`: no drift. `generate-registry.py --check`: up to date. The audience lint passes; report any new
  violation rather than baselining it.
- `check-maturity.py --root implementation`: 79 components, 0 failing, command 13/6. `/validate-workflow` is still
  `experimental`, and its golden case **stays red** until T568, because the case reads frozen fixture copies.
  Confirm both.
- `python3 scripts/scorecard.py --check`: OK, with no change.
- No `tests/golden/**` or `scripts/scorecard.py` change, so the digests still match **v14**. Confirm.
- `python3 docs/tasks/validate-tasks.py`: PASS.
- `python3 tests/run.py`: report the exit code, with output redirected to a file (never piped to `tail`). Baseline
  is **904 OK**.

## 5. Constraints

- **Write scope:**
  - the one command file, lines 25–32 only;
  - the regenerated `implementation/.<platform>/` mirrors and `implementation/registry/`;
  - the `drift` list in `tests/_baselines/root-install-drift.json`;
  - this brief's `**Status:**` line.
- **No `tests/golden/**`.** Do not open `held-out/`. Do not touch `scripts/scorecard.py`, the evaluator-hash files,
  or any skill or agent.
- Commit locally as one commit. **Do not push. Never run `glab mr merge` or any merge or approve API. There is no
  exception for docs-only changes.** Hand everything back.

## 6. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`. If the artifact's
"Before" block no longer matches lines 25–32, report it rather than working around it.
