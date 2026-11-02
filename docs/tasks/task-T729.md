# T729 — Tracked-debt register v5

**ID:** T729
**Owner:** tech-lead
**Status:** done
**Priority:** P1
**Tier:** standard
**Depends on:** —
**Affects:** —
**Created:** 2026-11-02
**Completed:** 2026-11-02
**Based on:**
- `docs/plans/plan-130-tracked-debt-register-v5.md` (task T729)
- The user's answer of 2026-11-02, verbatim: "v5 go"
- `docs/artifacts/tracked-debt-register-v4.md`; plans 126 to 129 (outcome sections); the four batch security reviews

## 1. What and why

(tech-lead): write `docs/artifacts/tracked-debt-register-v5.md`, a delta on v4, in v4's structure.
   - **Every v4 id that is `open`, `tracked-LOW` or `accepted`:** give its status now. Cite the plan outcome, the completed-task row or the review that closed it, or write "Unchanged".
     - The plan outcome sections list the batch closures:
       - plan-126 (batch B: 17 closed; SEC-T677-01 partly closed; TL-T708-07 unchanged; SEC-T676-14 and SEC-T702-08 still tracked);
       - plan-127 (batch D, including the TD-T671-legacy re-read: P4 and P7 obsolete, P9, P11 and P12 fixed, P10 still open, P14, P15, T539 and T565 parked);
       - plan-128 (batch A: 14 closed, SEC-T663-02 not done);
       - plan-129 (batch E).
     - TD-T713-01 is decided by ADR-011 (Accepted).
     - SEC-T699-04 is decided ("Tie to the bearer (Recommended)").
   - **One row for every new id:**
     - from the four reviews: SEC-T715-01 to -04; SEC-T716-01 to -05; SEC-T720-01 (fixed) to -08; SEC-T722-01 to -05; SEC-T724-01; SEC-T725-01 to -03; SEC-T726-01 to -03; SEC-T727-01 to -05; SEC-T728-01 to -03;
     - from the plan outcomes: TD-T720-01; TD-T723-01; TD-T724-01; TD-T725-01; TD-T726-01 and -02; TD-T728-01 to -03;
     - any other id a plan-126 to plan-129 artifact mints.
   - **The user's decisions since v4, quoted verbatim:**
     - the four batch approvals: "B go", "D go", "A go", "E go";
     - ADR-011 with its end date;
     - O1;
     - root refreshes 23 and 24;
     - SEC-T699-04.
   - **Accepted risks:** apply ADR-011. Each accepted MEDIUM that a release ships needs the user's new acceptance at that release. TD-T697-07 is now tied to the bearer token: it ends 2027-01-29 and is renewed with each token.
   - **A "Next release" checklist:**
     - the T725 migration item (`/prepare-release` no longer installed into targets);
     - the ADR-011 re-acceptances of SEC-T660-01, SEC-T665-01, the SEC-T658-01 remainder and SEC-T702-09;
     - the new verdict fields "Issued at commit" and "Independent check".
   - **The open items as new LOW batches** (letters starting at G), each with a scope, owner and trigger. Name the ones a reviewer flagged as "do first": SEC-T716-01, SEC-T722-03, SEC-T725-02, SEC-T728-01, SEC-T727-01/-02. Keep SEC-T663-02 as its own item, and F (PoC scanner, 2 ids) as it is.
   - **Dates:**
     - GitLab token renewal 2027-01-28;
     - CWSO bearer renewal and the end of TD-T697-07 2027-01-29;
     - end of Brave acceptance v3 2027-01-30;
     - the `paste` review is closed;
     - Trivy 0.76.1 can be adopted from 2026-11-04.
   - **User actions:** A-2, A-7, A-10 to A-15, plus the new CWSO redeploy action (`CWSO_HTTP_PUBLISH_ADDR`, secret length, origins).
   - *Acceptance:*
     - every v4 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
     - each status claim can be traced, or is marked **(unverified)**;
     - the counts add up;
     - `validate-tasks.py`, `test_link_integrity` and the team-health tests pass.

## 2. Output

As stated in section 1.

## 3. Constraints

- Work in your own worktree on branch `agent/<your-role>/<ID>`; Conventional Commits ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates for any change under `implementation/`, `scripts/` or `tests/`: `node implementation/scripts/sync.mjs --root implementation --check`, `python3 implementation/scripts/generate-registry.py --check`, `python3 implementation/scripts/check-maturity.py --root implementation`, `python3 scripts/scorecard.py --check`, `python3 docs/tasks/validate-tasks.py`, the evaluator hash (no drift), `python3 -m unittest tests.functional.test_golden_held_out_isolation`, and the full suite `python3 tests/run.py > file` (summary lines). Declare root drift in `tests/_baselines/root-install-drift.json`; do NOT refresh the root install.
- Never open `tests/golden/held-out/`; never write a held-out case id. Never read `/dev/shm/emage-secrets/`, `~/.config/secrets/`, any `.env*` or credential file, or the user's local `.claude/settings*.json` and `.vscode/mcp.json`; never print a secret value. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

- every v4 id that was open, tracked-LOW or accepted is accounted for, and every new id has a row;
     - each status claim can be traced, or is marked **(unverified)**;
     - the counts add up;
     - `validate-tasks.py`, `test_link_integrity` and the team-health tests pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
