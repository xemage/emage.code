# T579 — Make the PoC security reviewer block on critical findings (T578 FU-1, O1, SECURITY:HIGH)

**ID:** T579
**Owner:** Backend Developer
**Status:** pending
**Priority:** P1
**Tier:** mechanical
**Affects:** agent/poc-security-engineer
**Depends on:** T578
**Created:** 2026-10-02
**Based on:**
- `docs/artifacts/poc-security-reviewer-blocking-v3.md` (§§2–4: edits E1, E2a, E2–E11; §8: FU-1 verification; §16: orchestrator rulings)
- `docs/artifacts/security-review-poc-security-reviewer-blocking-v1.md` (CONDITIONAL_PASS; v2 meets its conditions)
- `docs/artifacts/security-review-poc-security-reviewer-blocking-v2.md` (delta re-review, CONDITIONAL_PASS; v3 adopts its After texts verbatim)
- `docs/plans/plan-099-poc-security-reviewer-blocking.md`

**Priority note:** P1, by the user's decision of 2026-10-02. This row keeps `poc-security-engineer` at `beta` until
it closes. Re-promotion to `stable` is a separate later task.

## 1. What and why

The `poc-security-engineer` agent, backed by `poc-orchestrator`, currently sends critical PoC findings to debt
handoff instead of blocking. That includes an exposed secret or an obvious injection or authorization gap. This
contradicts `security-guidelines` Immutable Constraint 1 and its rule that "CRITICAL and HIGH findings block
merge".

T578 v3 rules the repair. A Security Engineer reviewed v1 (CONDITIONAL_PASS) and re-reviewed v2 (CONDITIONAL_PASS), and v3
adopts its texts verbatim. The user decided the declined-rewrite path, accepted the presence check, and kept QD strict.
Apply **v3's 12 edits exactly as written**, using v3 only, never v1 or v2.

## 2. The edits

Each edit is a four-backtick fence in v3 §§2–4 that starts with `Before:`. Replace its exact before-text with its
exact after-text.

- Copy both texts from the fence programmatically; do not retype them. Fences can contain nested fences and `##`
  headings.
- Assert that each before-block occurs exactly once. The orchestrator confirmed this on develop `c523415`, which
  includes T577.
- If a before-block does not match exactly once, stop and report.

| File | Edits | v3 section |
|---|---|---|
| `implementation/knowledge/agents/poc-security-engineer.md` | E1, E2a, E2–E5 (6 edits) | §2 |
| `implementation/knowledge/agents/poc-orchestrator.md` | E6–E10 | §3 |
| `implementation/knowledge/skills/rapid-prototyping/SKILL.md` | E11 | §4 |

Check the result by content, not by hunk count: applying all pairs to develop's version of each file must reproduce
your file exactly.

**The literal "The PoC orchestrator will handle escalation" must remain in `poc-security-engineer.md`.**
`test_agent_escalation_consistency` requires it.

**Do NOT change any `maturity:` line.** `poc-security-engineer` stays `beta` while this row is open.

## 3. Regenerate and declare

1. Run `node implementation/scripts/sync.mjs --root implementation` **and**
   `python3 implementation/scripts/generate-registry.py`.
2. Run `python3 -m tests.functional.test_root_install_parity --print-drift`. Add **exactly** the new paths to the
   `drift` list in `tests/_baselines/root-install-drift.json` and keep the existing ones. Never hand-edit the
   top-level platform folders.

## 4. Verify, don't assume

- Every check in v3 §8 FU-1, including:
  - 0 hits for `as open debt` in `rapid-prototyping/SKILL.md`;
  - exactly 1 hit each for `accepted-risk`, `Severity floor`, `This is a presence check` and `awaiting user: step 1` in their target files;
  - 0 hits for the old phrases: "Do not block progress by default", "Record findings for debt handoff", "without
    blocking rapid validation", "critical risks only".
- `sync.mjs --check` and `generate-registry.py --check` are clean. The parity gate is green. The audience lint
  passes.
- `security-guidelines.md`, `poc-guidelines.md`, every command, and every agent other than the two named above are
  **byte-unchanged**.
- `check-maturity.py --root implementation` reports 79 components, 0 failing, agents 25 stable / 1 beta /
  2 experimental. `poc-security-engineer` stays `beta`.
- `scorecard.py --check` is OK (34/26/0). The digests match **v15**. `validate-tasks.py` passes.
- `python3 tests/run.py` exits 0 with 904 OK. Redirect its output to a file and read it there; never pipe it to
  `tail`.

## 5. Constraints

- **Write scope:**
  - the three source files above;
  - regenerated mirrors and `implementation/registry/`;
  - the `drift` list;
  - this brief's `**Status:**` line.
- **Do not touch `tests/golden/**`, and do not open it.** If a search reaches `tests/`, prune
  `tests/golden/held-out` before traversal.
- Do not touch `scripts/scorecard.py` or the evaluator-hash files.
- Do not read `.env` files, credentials or keys.
- Commit locally as one commit. **Do not push. Never run `glab mr merge` or any merge or approve API.** There is no
  exception to this. Hand everything back.

## 6. Blocker protocol

Types: `technical` | `dependency` | `unclear_requirements` | `external`. Severities: `critical` | `major` | `minor`.
If a before-text no longer matches, report it. Do not work around it.
