# Task T298 — Regenerate `implementation/registry` after claude-code manifest addition

**ID:** T298
**Owner:** backend-developer
**Status:** done
**Priority:** P0
**Depends on:** T294
**Created:** 2026-07-30
**Completed:** 2026-07-30
**Based on:** docs/plans/plan-015-add-claude-code-platform.md (follow-up fix,
discovered during T295 execution — not in the original task graph); prior
precedent: `docs/releases/v6.3.0.md` § Internal ("Registry regenerated twice
during this cycle... each committed separately as `chore(registry):
regenerate <reason>`").

## Why this task exists
Running T295 (the full validation gate) surfaced a real gap in Plan 015: none
of T287 (create the `claude-code.json` manifest) or T288 (run `make sync`)
included regenerating `implementation/registry/{index.json,summary.md}`.
`implementation/scripts/generate-registry.py` scans `implementation/platforms/*.json`
to build `compatibility.supportedPlatforms`/`projectionStatus` per knowledge
entry — since T287 added a 6th manifest, the committed registry snapshot (still
listing only 5 platforms) now diverges from what the generator produces live.
`implementation/scripts/check.py --registry` correctly fails with `registry:
generation drift detected`. This is exactly the same class of drift this
repo has hit before (see the v6.3.0 release notes) and has an established
fix pattern: regenerate and commit as its own `chore(registry)` commit.

## STOP-RULES (read before touching anything)
- Confirm T294 is `done`. If `pending`, STOP and report
  `PRECONDITION FAILED: T298 (missing dependency)`.
- **R2** This task only regenerates `implementation/registry/index.json` and
  `implementation/registry/summary.md` by running the existing generator
  script. Do NOT hand-edit either file. Do NOT edit
  `implementation/platforms/claude-code.json` or any knowledge file to make
  the registry "look right" — the generator is the single source of truth
  for these two files.
- **R6** Do NOT run `git push`.
- **R7** Commit message, exactly: `chore(registry): regenerate for claude-code platform addition`

## Steps

1. Regenerate:
   ```bash
   python3 implementation/scripts/generate-registry.py --root implementation
   ```
   Expected: exits `0`, rewrites `implementation/registry/index.json` and
   `implementation/registry/summary.md`.

2. Confirm `claude-code` now appears in the registry:
   ```bash
   python3 -c "
   import json
   d = json.load(open('implementation/registry/index.json'))
   assert 'claude-code' in d.get('platforms', []), d.get('platforms')
   print('REGISTRY_LISTS_CLAUDE_CODE')
   "
   ```
   Expected output: `REGISTRY_LISTS_CLAUDE_CODE`

3. Confirm the registry check now passes:
   ```bash
   python3 implementation/scripts/check.py --root implementation --registry
   ```
   Expected: exit `0`, no `registry: generation drift detected` error.

4. Re-run the full validation super-gate (the same command T295 runs) to
   confirm this was the only drift source:
   ```bash
   python3 implementation/scripts/check.py --root implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers --adapters
   ```
   Expected: exit `0`. If it still fails on a DIFFERENT check than `registry`,
   STOP — that is a new, separate blocker, not something this task should fix.

5. Confirm `make sync`/`verify.mjs` are still clean (registry regeneration
   must not have touched any platform projection):
   ```bash
   node implementation/scripts/sync.mjs --root implementation
   git status --porcelain implementation/.cursor implementation/.github implementation/.gemini implementation/.opencode implementation/.pi implementation/.claude
   node implementation/scripts/verify.mjs --root implementation
   ```
   Expected: `git status --porcelain` on those 6 dirs prints nothing;
   `verify.mjs` exits `0`.

## Expected outputs
- `implementation/registry/index.json` modified (now lists `claude-code`).
- `implementation/registry/summary.md` modified.
- No other files changed.

## Acceptance criteria
1. Steps 1-5 above all pass exactly as described.
2. `git status --porcelain` lists exactly two modified files:
   `implementation/registry/index.json`, `implementation/registry/summary.md`.

## Revert rule
If any step fails unexpectedly:
```bash
git checkout -- implementation/registry/index.json implementation/registry/summary.md
```
then STOP and report exactly which step failed and its output.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.

## Execution notes
<filled during execution>
</content>
