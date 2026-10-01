# T571 — Align the three PoC skills with T563's rulings (T570 FU-1)

**ID:** T571
**Owner:** Backend Developer
**Status:** done
**Priority:** P2
**Tier:** standard
**Affects:** skill/poc-evaluation, skill/rapid-prototyping, skill/technical-debt-tracking
**Depends on:** T570
**Created:** 2026-10-01
**Based on:** `docs/artifacts/poc-skills-alignment-v1.md` §§2–6 (edits E1–E14) and §10 (the orchestrator's approval);
`docs/plans/plan-094-poc-skills-alignment.md`.

## 1. What and why

T570 decided how three `experimental` PoC skills align with T563's rulings and `AGENTS.md` § Task Protocol. The
orchestrator approved the decision in artifact §10.2. This task applies **edits E1–E14 exactly as specified**, with
nothing left to decide:
- `poc-evaluation`: E1–E5
- `rapid-prototyping`: E6–E7
- `technical-debt-tracking`: E8–E14

## 2. The edits

Apply each edit by matching its exact **before** text from the artifact and replacing it with its exact **after**
text. Copy the text programmatically from the artifact's code fences; do not retype it. Before replacing, assert that
each before-block occurs exactly once. If one does not match, stop and report it. **Check the result by content, not by
diff-hunk count:** for each file, applying every before→after pair to `develop`'s version must reproduce your file
exactly, and nothing else may change.

## 3. Regenerate and declare

1. Run `node implementation/scripts/sync.mjs --root implementation` **and**
   `python3 implementation/scripts/generate-registry.py`.
2. Run `python3 -m tests.functional.test_root_install_parity --print-drift`. Add **exactly** the new root paths to
   the `drift` list in `tests/_baselines/root-install-drift.json` and keep the existing 42. Artifact §10.1 #4 expects
   up to 21 new paths: the three skills across seven platforms. **Never hand-edit the top-level platform folders.**

## 4. Verify, don't assume

- `sync.mjs --check` and `generate-registry.py --check` are clean.
- The verification greps in artifact §6:
  - the case-insensitive string `inconclusive` occurs in none of the three source files;
  - `technical-debt-tracking` no longer contains `XS`/`XL` as effort values, `high` as a severity value, or `should`
    or `must` as priorities.

  Report any hit and explain why it stays.
- The audience lint passes.
- `check-maturity.py --root implementation` reports 79 components, 0 failing, and an unchanged distribution
  (commands 14/5, skills 7 stable / 19 experimental).
- `scorecard.py --check` is OK (34/26/0) and the digests still match **v15**. Nothing under `tests/golden/` changes.
- `validate-tasks.py` passes.
- `python3 tests/run.py`: report the exit code, with output redirected to a file, never piped to `tail`. The
  baseline is **904 OK**.

## 5. Constraints

- **Write scope:**
  - the three source `SKILL.md` files, at the artifact's sites only;
  - the regenerated `implementation/.<platform>/` mirrors and `implementation/registry/`;
  - the `drift` list in `tests/_baselines/root-install-drift.json`;
  - this brief's `**Status:**` line.
- **No `tests/golden/**`.** Do not open it. If a search must cover `tests/`, prune `tests/golden/held-out` before
  traversal (plan-093 §5). Do not touch `scripts/scorecard.py`, the evaluator-hash files, or any command, agent or
  instruction.
- Commit locally as one commit. **Do not push. Never run `glab mr merge` or any merge or approve API**, with no
  exception for wording-only changes. Hand everything back.

## 6. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`. If the artifact's
before-text no longer matches, report it. Do not work around it.
