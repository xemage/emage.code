# T828 — Installer equal-size skip (TD-T774-01) and build project-id check (QA-T818-03)

**ID:** T828
**Owner:** backend-developer
**Status:** done
**Priority:** P2
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-14
**Completed:** 2026-11-14
**Based on:**
- `docs/plans/plan-163-batch-i-rsync-and-project-id.md` (§ Goal)
- The user's answer of 2026-11-14, verbatim: "I go" (after the orchestrator recommended batch I's installer fix for TD-T774-01, with QA-T818-03 alongside)

## 1. What and why

As in plan-163 § Goal.

## 2. Output

Commits on `agent/backend-developer/T828`: `scripts/install.sh`, `implementation/runtime/memory/build.py`, their tests, and the M-5/M-6 or README text that describes the old behaviour, if any.

## 3. Constraints

- Do not push, merge, tag or release. Do not edit the ledger, any brief's Status line or the plan. No `docker`.
- Never open `tests/golden/held-out/`. Never read secrets or the user's settings files. Mark anything not verified **(unverified)**.

## 4. Acceptance criteria

As in plan-163 § Goal: a changed same-size file is always copied (tested); a mismatched `--project-id` is refused (tested); the installer note is true.

## 5. Blocker protocol

Report each blocker with its type and severity.
