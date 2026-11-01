# T713 — Tracked-debt register v4

**ID:** T713
**Owner:** tech-lead
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-01
**Completed:** 2026-11-01
**Based on:**
- `docs/plans/plan-125-post-v9-follow-ups.md` (task T713)
- The user's answer of 2026-11-01, verbatim: "v4 + C go"
- `docs/checkpoints/checkpoint-040-release-v9.0.0.md`; `docs/artifacts/tracked-debt-register-v3.md`

## 1. What and why

(tech-lead): `docs/artifacts/tracked-debt-register-v4.md`, a delta on v3 (398 ids): the status now of every v3 id that is `open`, `tracked-LOW` or `accepted`; the closures of plan-124 (SEC-T662-01, SEC-T678-03, SEV-T690-07, SEC-T702-07, SEC-T712-01 to -04 and -06, SEC-T689-01/-03/-06, SEC-T699-01, SEC-T689-02 in part, TD-T697-08 ruled LOW); one row per new id from the plan-124 reviews and gates (T700 audit, T701/T703 review, T702 grading, T712 review, T707 QA gate, T708 Tech Lead review, T709 security re-check, T710 decisions); SEC-T686-03 and SEC-T686-06 from the tag pipeline (checkpoint-040 § 4); the user's decisions since v3; the LOW batches A to F as the open-items structure; T714 is in flight and treated as open. *Acceptance:* every v3 id that was open, tracked-LOW or accepted is accounted for; every new id has a row; status claims traceable or (unverified); the validators and link and team-health tests pass.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree on branch `agent/<your-role>/<ID>`; Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

As stated in section 1.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
