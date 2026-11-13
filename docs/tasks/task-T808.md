# T808 — Brave acceptance record v4 (SEC-T702-09, for v11.0.0)

**ID:** T808
**Owner:** devops-engineer
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-13
**Completed:** 2026-11-13
**Based on:**
- `docs/plans/plan-158-brave-acceptance-v4-and-register-v16.md` (task T808, § User decision)
- `docs/plans/plan-155-v11-release-decisions.md` (§ User decisions item 2; § Addendum item 5: the question, the answer "Keep the acceptance (Recommended)", the option's description and the other options)
- `docs/artifacts/brave-audit-acceptance-v3.md`; `docs/artifacts/brave-replacement-scouting-v1.md`
- `docs/decisions/ADR-011-user-accepted-medium-at-release.md`, `docs/decisions/ADR-012-medium-acceptance-record.md`, `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md` (what the record of an accepted MEDIUM must carry)

## 1. What and why

v3 records the user's decision of 2026-11-01, given for v9.0.0. Under ADR-011 an acceptance covers only the release it was given for. On 2026-11-12 the user accepted SEC-T702-09 for v11.0.0 only ("Keep the acceptance (Recommended)"; plan shown: owner devops-engineer; fix: bump to the first Brave release above 2.1.4; deadline 2027-01-30 or that release, whichever comes first) and on 2026-11-13 confirmed that the record be written ("1. Keep the acceptance"). Write that record.

## 2. Output

Commits on `agent/devops-engineer/T808`, in the worktree `/home/emage/Code/emage/worktrees/agent-devops-engineer-T808`:

1. `docs/artifacts/brave-audit-acceptance-v4.md`, in v3's structure. v3 stays unchanged (immutable).
   - **Decision:** the user's words quoted verbatim from plan-155 and plan-158, with dates, the question as shown, the option's description and the other options. Say which release the acceptance covers (v11.0.0 only) and that v10.0.0 was covered by its own acceptance (name the record that holds it, from the sources; if you cannot find it, say so, marked **(unverified)**).
   - **Plan (ADR-011/ADR-012 fields):** owner, fix, deadline, exactly as shown to the user. The fix is a version bump, so ADR-015 Rule 1 and ADR-016 do not apply; say so in one line.
   - **Expires:** do not move the date. The user was shown 2027-01-30; a later date needs the user. Check how `scripts/audit-mcp-pins.py` reads the expiry and whether a v4 dated 2026-11-13 is consistent with its 90-day rule; report what you find.
   - **Facts re-checked today,** each with the command and its output: the newest published `@brave/brave-search-mcp-server` version (`npm view … version time.modified`); `python3 scripts/audit-mcp-pins.py audit --audit-level high` without `--accept` and with the documented `--accept` form (does the set of advisories on the pin still equal v3's seven? if npm now reports more or fewer, STOP after recording it: a changed set is a changed acceptance and goes to the user, not into v4 as accepted). The network calls go to the npm registry only.
   - **Unchanged from v3:** the shipped launch (`--transport stdio`), the per-advisory grading; point to v3 and the reviews, do not re-grade.
   - **Scouting result** (T799): one paragraph, pointing to the record.
2. **References to the current record.** Find every place that names `brave-audit-acceptance-v3.md` as the *current* record (`scripts/audit-mcp-pins.py`, `tests/functional/test_pin_bump_checklist.py`, `docs/wiki/mcp-pin-bump-checklist.md`, and any other; search `docs/wiki`, `scripts`, `implementation`, `tests` with `--exclude-dir=held-out`). Move those to v4 and adjust the tests that pin them, keeping every existing check (v1, v2 and v3 stay checked as immutable records where they are today). Leave historical references (a comment that says what T712 did, a drift-baseline note, older artifacts, plans, registers) as they are. Report each hit as moved or left, with the reason. If a moved reference sits in `implementation/knowledge/`, regenerate (`node implementation/scripts/sync.mjs --root implementation`, `python3 implementation/scripts/generate-registry.py`) in a separate commit and declare root drift in `tests/_baselines/root-install-drift.json`; prefer not to touch `implementation/knowledge/` if the reference there is historical.

## 3. Constraints

- Conventional Commits, each ending with `Co-Authored-By: Claude <noreply@anthropic.com>`. Do not push, do not merge, never create a tag or release.
- Do not change the pin, `servers.yaml` behaviour, the gate's logic or the expiry. This task records a decision.
- Do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md`, any brief's Status line, any plan, any ADR, or v1 to v3 of the record.
- `tests/golden/` is protected: change nothing under it. Never open `tests/golden/held-out/` and never write a held-out case id.
- No `docker` command. Do not run `scripts/install.sh`; do not touch the top-level platform folders. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/*.json`. Never print a secret value. Do not read the CWSO repository.
- Run the tests you touch and the gates below with a `timeout`. No full suite, no mutation tool.
- Do not delete anything under `/tmp` that you did not create.
- Token budget: 60k, counting context. Report your usage honestly.

## 4. Acceptance criteria

- v4 quotes the user's words character for character from the plans, and claims nothing the sources do not record.
- These pass: `timeout 300 python3 -m unittest tests.functional.test_pin_bump_checklist tests.functional.test_mcp_package_pins`; `python3 docs/tasks/validate-tasks.py`; `timeout 300 python3 -m unittest tests.functional.test_link_integrity`; `python3 -m unittest discover -s tests -p 'test_team_health*.py'`; `python3 scripts/scorecard.py --check`; `node implementation/scripts/sync.mjs --root implementation --check`; `python3 implementation/scripts/generate-registry.py --check`; `python3 -m unittest tests.functional.test_root_install_parity`.
- `git status` is clean. The report lists each commit, each reference hit (moved or left), the command outputs of § 2, anything **(unverified)**, any new id you think the register needs, and token usage.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`). After two failed attempts at the same step, stop and report.
