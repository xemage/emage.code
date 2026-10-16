# T577 — Replace the PoC examples that model forbidden security shortcuts (T576 FU-1, P42)

**ID:** T577
**Owner:** Backend Developer
**Status:** done
**Priority:** P2
**Tier:** mechanical
**Affects:** instruction/poc-guidelines, skill/rapid-prototyping
**Depends on:** T576
**Created:** 2026-10-02
**Based on:**
- `docs/artifacts/poc-security-shortcut-examples-v2.md`: edits R1–R11 in §§2–4, verification in §7, orchestrator
  rulings in §13.
- `docs/artifacts/security-review-poc-security-shortcuts-v1.md`: Security Engineer CONDITIONAL_PASS; its conditions
  are met in v2.
- `docs/plans/plan-098-poc-security-shortcut-examples.md`.

**Priority note:** P2, dispatched immediately. The user decided this on 2026-10-02.

## 1. What and why

The PoC track's model `POC-DEBT` examples teach shortcuts that `security-guidelines.md` forbids even in a PoC:
"No input validation", "disabled security" and "CORS allow-all". T576 (v2) ruled every site. A Security Engineer
review returned CONDITIONAL_PASS, and v2 meets its conditions. Apply **v2's R1–R11 exactly as written. Use v2 only;
do not use v1.**

## 2. The edits

For each four-backtick fence in v2 §§2–4 that starts with `Before:`, replace its exact before-text with its exact
after-text. Copy both from the fence programmatically; do not retype them. Assert that every before-block occurs
exactly once. The orchestrator has already confirmed each one is unique on `develop` `7da064a` (v2 §13.1). If one
does not match, stop and report.

- `implementation/knowledge/instructions/poc-guidelines.md`: 7 edits (v2 §2 and §4: R1, R2, R10, R3, R11, R4, R5).
- `implementation/knowledge/skills/rapid-prototyping/SKILL.md`: 4 edits (v2 §3: R7, R8, R9, R6).

Check by content, not hunk count: applying all pairs to `develop`'s version of each file must reproduce your file
exactly.

## 3. Regenerate and declare

1. `node implementation/scripts/sync.mjs --root implementation` **and** `python3 implementation/scripts/generate-registry.py`.
2. Run `python3 -m tests.functional.test_root_install_parity --print-drift`. Add **exactly** the new paths to the
   `drift` list in `tests/_baselines/root-install-drift.json`, and keep the existing ones. **Never hand-edit the
   top-level platform folders.** These two files ship to every installed project, so the repo-root copies stay stale
   until the next user-approved refresh.

## 4. Verify, don't assume

- Run every check in v2 §7.1, including:
  - zero hits for `sslmode=require`;
  - zero hits for "No input validation", "disabled security" and "CORS allow-all" in the two source files;
  - each new phrase present exactly once.
- `sync.mjs --check` and `generate-registry.py --check` are clean, the parity gate is green, and the audience lint
  passes.
- `implementation/knowledge/instructions/security-guidelines.md` is **byte-unchanged**.
- `check-maturity.py --root implementation`: 79 components, 0 failing, and the distribution is unchanged apart from
  whatever the O1 task (T578) does to agents.
- `scorecard.py --check` OK (34/26/0), the digests match **v15**, and `validate-tasks.py` passes.
- `python3 tests/run.py`: check the exit code, with output redirected to a file, never piped to `tail`. Expect 904 OK.

## 5. Constraints

- **Write scope:**
  - the two source files, at v2's sites only;
  - the regenerated mirrors and `implementation/registry/`;
  - the `drift` list in `tests/_baselines/root-install-drift.json`;
  - this brief's `**Status:**` line.
- **Do not touch `tests/golden/**`, and do not open it.** If a search reaches `tests/`, prune `tests/golden/held-out`
  before traversal. Do not touch `scripts/scorecard.py`, the evaluator-hash files, `security-guidelines.md`, any
  command or any agent.
- Commit locally as one commit. **Do not push. Never run `glab mr merge` or any merge or approve API, with no
  exception.** Hand everything back.

## 6. Blocker protocol

Types: `technical` | `dependency` | `unclear_requirements` | `external`. Severities: `critical` | `major` | `minor`.
If a before-text no longer matches, report it. Do not work around it.
