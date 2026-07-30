# Task T295 — GATE: full validation suite green

**ID:** T295
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T294, T298, T299
**Created:** 2026-07-30
**Completed:** 2026-07-30
**Based on:** docs/plans/plan-015-add-claude-code-platform.md § Task graph T295;
`.gitlab-ci.yml` stages `test`, `verify`, `sync` (this task reproduces those
CI gates locally before the release is cut).

> **Note (added after first execution attempt):** T298 (registry
> regeneration) was inserted as a dependency after this gate's first run
> failed Step 3 with `registry: generation drift detected` — neither T287 nor
> T288 regenerated `implementation/registry/` after the new manifest was
> added. T298 fixes that; do not re-diagnose the same failure if it recurs
> here — confirm T298 is `done` first.
>
> **Note (added after second execution attempt):** T299 (fix task-brief
> `**Status:**` headers) was inserted as a dependency after this gate's
> second run failed Step 4 (`tests/run.py`) on the shipped ledger validator's
> `C8` check — every T285-T294/T298 brief still said `**Status:** pending` in
> its own header despite being recorded `done` in `completed-tasks.md`, since
> none of those briefs' instructions included updating their own header.
> T299 fixes that; confirm T299 is `done` before re-running this gate.

## Why this task exists
T285–T294 touched the sync engine, a new manifest, generated output, the
installer, the AGENTS.md renderer, and four doc files. This is the mandatory
convergence gate before release-cut tasks (T296–T297) run: it reproduces every
CI gate locally in one pass so any regression across the whole chain is caught
before it reaches `develop`.

## STOP-RULES (read before touching anything)
- Confirm T294 is `done`. If `pending`, STOP and report
  `PRECONDITION FAILED: T295 (missing dependency)`.
- **This task edits NO files.** It only runs commands. If a command fails,
  identify which upstream task (T285–T294) is at fault and STOP — report the
  task ID to re-open. Do NOT hand-patch generated output, tests, or source to
  force a pass.
- **R6** Do NOT run `git push`.
- No commit is made by this task unless a command surfaces uncommitted
  generated drift (see Step 1) — in that case, commit exactly that drift with
  message `chore(sync): T295 regenerate projections after gate check`.

## Steps (run all, in order, from repository root)

1. Sync engine — must produce zero diff (mirrors CI `sync-no-diff`):
   ```bash
   node implementation/scripts/sync.mjs --root implementation
   git status --porcelain implementation
   ```
   Expected: `git status --porcelain implementation` prints nothing. If it
   prints changes, review them — if legitimate (e.g. missed committing T288's
   output), stage and commit with the message above; if unexpected, STOP and
   report which task ID produced the drift.

2. Drift verification (mirrors CI `verify-knowledge-drift`):
   ```bash
   node implementation/scripts/verify.mjs --root implementation
   ```
   Expected: exit code `0`.

3. Validation super-gate (mirrors CI `validation-super-gate`):
   ```bash
   python3 implementation/scripts/check.py --root implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers --adapters
   ```
   Expected: exit code `0`.

4. Full test suite (mirrors CI `unit-tests`):
   ```bash
   python3 tests/run.py
   ```
   Expected: exit code `0`, all suites (`functional`, `performance`) pass.

5. Installer syntax sanity:
   ```bash
   bash -n scripts/install.sh
   ```
   Expected: no output, exit code `0`.

6. Markdown link check (mirrors CI `markdown-links`, informational in CI but
   run it here as a real gate):
   ```bash
   python3 - <<'PY'
   import os, re, sys
   SKIP = ("/.git", "node_modules", ".vscode-server", "/docs/wiki")
   link_re = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
   fence_re = re.compile(r'```.*?```', re.DOTALL)
   inline_re = re.compile(r'`[^`\n]*`')
   broken = []
   for root, dirs, files in os.walk("."):
       if any(s in root for s in SKIP): continue
       for f in files:
           if not f.endswith(".md"): continue
           p = os.path.join(root, f)
           with open(p, encoding="utf-8", errors="ignore") as fh:
               text = fh.read()
           text = fence_re.sub("", text)
           text = inline_re.sub("", text)
           base = os.path.dirname(p)
           for m in link_re.finditer(text):
               t = m.group(2).strip()
               if t.startswith(("http://","https://","mailto:","#","tel:")): continue
               clean = t.split("#")[0].split("?")[0]
               if not clean: continue
               full = os.path.normpath(os.path.join(base, clean))
               if not os.path.exists(full):
                   broken.append(f"{p}  ->  {t}")
   if broken:
       print("Broken markdown links:")
       for b in broken: print("  ", b)
       sys.exit(1)
   print("All markdown links resolve.")
   PY
   ```
   Expected: `All markdown links resolve.`, exit code `0`.

## Expected outputs
- No file changes, unless Step 1 surfaces uncommitted sync drift (rare — all
  prior tasks were required to commit their own generated output).

## Acceptance criteria
1. All 6 steps above pass exactly as described.
2. `git status --porcelain` is empty (clean tree) after this task completes.

## Revert rule
This task makes no speculative edits, so there is nothing to revert. If a
step fails, STOP immediately and report:
- which step failed
- the exact command output
- which upstream task ID (T285–T294) most plausibly owns the regression

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.
This is the FINAL GATE before release-cut tasks — do not let it pass with any
step failing, and do not weaken a step's command to force a green result.

## Execution notes
<filled during execution>
</content>
