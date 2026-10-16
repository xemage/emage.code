# T562 — Promote `/team-status`, `/new-poc`, `/poc-demo`, `/evaluate-poc` to `stable`

**ID:** T562
**Owner:** Backend Developer
**Status:** done
**Priority:** P2
**Tier:** mechanical
**Affects:** —
**Depends on:** T561
**Created:** 2026-10-01
**Based on:** `docs/plans/plan-091-wave-3-promotion-and-poc-conflicts.md` §1; `docs/plans/plan-090-golden-wave-3.md` §2;
`implementation/scripts/check-maturity.py`.

## 1. What and why

Golden wave 3 (T561, MR !443) gave these four `experimental` commands green golden cases. A dry run by the
orchestrator on `develop` (flip the four `maturity:` lines, regenerate the registry, run `check-maturity.py`)
reported **all four PASS every `stable` criterion**, with `command/stable: 13 pass`. `/validate-workflow`, flipped
in the same dry run as a control, **FAILS** criteria 3 and 7 on its own `known_failing` / `tracked_defect` case —
exactly as intended. **It is not promoted here.**

## 2. The change — a promotion is three linked edits

1. `maturity: experimental` → `maturity: stable` in `implementation/knowledge/commands/{team-status,new-poc,poc-demo,evaluate-poc}.md`. Nothing else in those files.
2. Regenerate: `node implementation/scripts/sync.mjs --root implementation` **and**
   `python3 implementation/scripts/generate-registry.py`. `maturity` is source-only (dropped from every projection
   by `keepKeys`), so **no projection should change** — confirm it. The registry's four checksums change.
3. Update the snapshot assertions in `tests/functional/test_check_maturity.py` (around line 531 asserts
   `"command/stable: 9 pass, 0 fail"`) to the new distribution: **13 stable / 6 experimental**. Find every
   assertion that hardcodes the command distribution, not just that one.

## 3. A caveat that must be on the record

**The three PoC greens certify the content of their quoted clauses only — not output paths.** Every output path
`/new-poc` declares is contradicted by another document (P11, P29, P30 in `plan-090` §2), and the T563
adjudication is deciding them. Say this in the commit message. `stable` here means what it has always meant in
this repository: *passes the golden cases that exist*.

## 4. Verify, don't assume

- `check-maturity.py --root implementation`: 79 components, 0 failing, **command 13 stable / 6 experimental**.
- `--print-drift` unchanged (6 `/batch` paths); the audience lint passes; `sync.mjs --check` no drift;
  `generate-registry.py --check` up to date.
- **Mutation:** temporarily flip `/validate-workflow` to `stable` and show `check-maturity` fails it on criteria 3
  and 7; restore and confirm `git diff` is clean of it.
- `python3 tests/run.py` — exit code, redirected to a file, never piped to `tail`. Baseline 904 OK.

## 5. Constraints

- **Write scope:** the four command files (maturity line only), regenerated `implementation/registry/index.json`
  (and `summary.md` if it changes), `tests/functional/test_check_maturity.py` (distribution assertions only), and
  this brief's `**Status:**` line.
- **No `tests/golden/**`, no `scripts/scorecard.py`.** No golden change ⇒ no evaluator-hash change; confirm v13 still
  matches.
- Commit locally, one commit; **do not push; never merge or approve anything.** A Solution Architect works in
  parallel on `docs/artifacts/` only.

## 6. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`. If anything in this
brief is wrong, report it rather than working around it.
