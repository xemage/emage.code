# T785 — Bump node:24-alpine to Node 24.22.3

**ID:** T785
**Owner:** devops-engineer
**Status:** blocked
**Priority:** P1
**Tier:** standard
**Depends on:** T784
**Affects:** —
**Created:** 2026-11-11
**Based on:**
- `docs/plans/plan-148-node-image-bump.md` (task T785; § Facts)
- The user's answer of 2026-11-11, verbatim: "Re-grade now, bump later (Recommended)"
- T784's review: `docs/artifacts/security-review-t784-node-advisory-v1.md`

## 1. What and why

Bump the `node:24-alpine` pin to an official image that carries Node 24.22.3, as plan-148 § Task Decomposition item 2 specifies.

**Blocked:** external dependency, severity minor. No official image carries 24.22.3 on 2026-11-11. The orchestrator checks Docker Hub and dispatches this task when one does.

## 2. Output

- The change to `.gitlab-ci.yml` (the only file expected to change), and any test it needs, committed on `agent/devops-engineer/T785`.
- A report of the digests, the Alpine version and the package versions read, with the date each was read.

## 3. Constraints

- No `docker` command. Read digests through the registry API.
- Do not change a runner, CI variable or project setting.
- Never open `tests/golden/held-out/`. Read no `.env*` or credential file.
- Do not push, and do not merge.

## 4. Acceptance criteria

- The tests that guard the pins pass.
- `ca-chain-check-python` and `ca-chain-check-node` pass in the MR pipeline on the new digest.
- T784's proof obligations are met.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
