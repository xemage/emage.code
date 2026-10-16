# T575 — Apply the PoC skill/command overlap edits (T574 FU-1)

**ID:** T575
**Owner:** Backend Developer
**Status:** done
**Priority:** P2
**Tier:** mechanical
**Affects:** skill/poc-evaluation, skill/rapid-prototyping, skill/technical-debt-tracking
**Depends on:** T574
**Created:** 2026-10-02
**Based on:** `docs/artifacts/poc-skill-command-overlaps-v1.md` §9 (edits E1–E12), §12 and §16 (orchestrator rulings);
`docs/plans/plan-097-poc-skill-command-overlaps.md`.

## 1. What and why

T574 ruled on all seven P38 overlaps without ranking any document over another. Every amendment falls on an
experimental skill, and `/evaluate-poc` is untouched. The orchestrator accepted E1–E12 in §16.2. Apply them
**exactly as specified**.

## 2. The edits

For each edit in artifact §9, find its exact **before** text and replace it with its exact **after** text.
- Copy both from the artifact's four-backtick fences programmatically. Do not retype them.
- Before applying, assert that each before-block occurs exactly once. If one does not, stop and report it.
- E7 carries fallback wording in case E5 is not applied. **E5 is applied**, so use E7's primary wording.
- Check the result by content, not by hunk count. For each file, applying every before→after pair to develop's
  version must reproduce your file exactly.

Files:
- `implementation/knowledge/skills/poc-evaluation/SKILL.md` (E1–E7)
- `implementation/knowledge/skills/rapid-prototyping/SKILL.md` (E8–E11)
- `implementation/knowledge/skills/technical-debt-tracking/SKILL.md` (E12)

**Do not touch `rapid-prototyping:30–49`** (the POC-DEBT tag examples). They are P42, a separate security ruling.

## 3. Regenerate and declare

1. Run `node implementation/scripts/sync.mjs --root implementation` **and**
   `python3 implementation/scripts/generate-registry.py`.
2. Run `python3 -m tests.functional.test_root_install_parity --print-drift`. Add **exactly** the new paths to the
   `drift` list in `tests/_baselines/root-install-drift.json`, and keep the 33 already declared. Expect 21 new paths.
   Never hand-edit the top-level platform folders.

## 4. Verify, don't assume

- The checks listed in artifact §12.
- `sync.mjs --check` and `generate-registry.py --check` are clean, and the parity gate is green.
- The audience lint passes.
- `commands/evaluate-poc.md` is **byte-unchanged**.
- `check-maturity.py --root implementation` reports 79 components, 0 failing, and the distribution is unchanged
  (skills 7/19).
- `scorecard.py --check` is OK (34/26/0), and the digests match **v15**.
- `validate-tasks.py` passes.
- `python3 tests/run.py` exits 0. Redirect its output to a file and read it there; never pipe it to `tail`.
  Expect **904 OK**.

## 5. Constraints

- **Write scope:**
  - the three source skills, at the artifact's sites only;
  - the regenerated mirrors and `implementation/registry/`;
  - the `drift` list in `tests/_baselines/root-install-drift.json`;
  - this brief's `**Status:**` line.
- **Do not touch `tests/golden/**`, and do not open it.** Any search that reaches `tests/` must prune
  `tests/golden/held-out` before traversal (plan-093 §5).
- Do not touch `scripts/scorecard.py`, the evaluator-hash files, any command, agent or instruction.
- Commit locally as one commit. **Do not push. Never run `glab mr merge` or any merge or approve API, with no
  exceptions.** Hand everything back.

## 6. Blocker protocol

Types: `technical` | `dependency` | `unclear_requirements` | `external`. Severities: `critical` | `major` | `minor`.
If a before-text no longer matches, report it rather than working around it.
