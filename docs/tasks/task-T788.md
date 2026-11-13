# T788 — Take `docker` out of the image-bump checklist

**ID:** T788
**Owner:** technical-writer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-12
**Completed:** 2026-11-12
**Based on:**
- `docs/plans/plan-150-pin-checklist-no-docker.md` (task T788)
- The user's instruction of 2026-11-12, verbatim: "Fix SEC-T786-02"
- `docs/artifacts/security-review-t786-node-bump-v1.md` § 3 (SEC-T786-02); `docs/artifacts/ca-check-t765-v1.md`

## 1. What and why

Edit `docs/wiki/mcp-pin-bump-checklist.md` § 2 and § 3, as specified in plan-150 § Task Decomposition item 1. The goal is that the image-bump procedure reads versions from the registry, with no Docker, and that the musl install check is a step for the maintainer only.

## 2. Output

The edited `docs/wiki/mcp-pin-bump-checklist.md`. No other file changes. The orchestrator commits it.

## 3. Constraints

- Docs only. Never open `tests/golden/held-out/`. Read no `.env*` or credential file.
- Keep every phrase and id that `tests/functional/test_pin_bump_checklist.py` requires.

## 4. Acceptance criteria

- No agent instruction to run `docker`, and no "run the image".
- The registry method is complete enough to repeat.
- `python3 -m unittest tests.functional.test_pin_bump_checklist` passes (the orchestrator runs it).

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
