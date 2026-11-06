# T741 — Two batch S fixes: the gate job's pin, and strict decoding

**ID:** T741
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-05
**Completed:** 2026-11-06
**Based on:**
- `docs/plans/plan-138-gate-pin-and-strict-read.md` (task T741)
- The user's answer of 2026-11-05, verbatim: "05 01 go"
- `docs/artifacts/security-review-t739-gate-parser-v1.md` § 4; `docs/artifacts/tracked-debt-register-v8.md` § 3

## 1. What and why

Fix SEC-T739-05 and SEC-T739-01, as `docs/plans/plan-138-gate-pin-and-strict-read.md` § Task Decomposition specifies. Then fix SEC-T741-01 to -05, as § Changes after the first security review specifies (the user: "Fix all four first (Recommended)"). Then SEC-T741-09, -10, -13, -14 and -15, as § Changes after the second security review records. The orchestrator finished this task after the implementer stopped (the user: "Finish T741 yourself").

## 2. Output

Changes to `scripts/verify-release-docs.py`, `tests/functional/test_ci_hash_pins.py` and `tests/functional/test_verify_release_docs.py`, committed on `agent/devops-engineer/T741`. After the first security review, also `tests/functional/test_publish_release.py`, and in the event `tests/functional/test_knowledge_template_images.py`. No other file changes; `.gitlab-ci.yml` does not change.

## 3. Constraints

- Work in your own worktree on branch `agent/devops-engineer/T741`. Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Never open `tests/golden/held-out/`; never write a held-out case id; a recursive search over `tests/` needs `--exclude-dir=held-out`. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Do not read the CWSO repository.
- Fix these two ids only. If you find another problem, report it and do not fold it in. Mark anything you did not verify **(unverified)**.
- Do not run the full suite: the orchestrator does. Do not start Docker or change any running container.
- Token budget: 90k.

## 4. Acceptance criteria

As in the plan.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
