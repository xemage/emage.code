# T582 — Apply the CONDITIONAL_PASS ruling (T580 FU-1, P39)

**ID:** T582
**Owner:** Backend Developer
**Status:** done
**Priority:** P2
**Tier:** mechanical
**Affects:** agent/tech-lead, agent/release-manager, command/code-review, command/security-audit, command/prepare-release, skill/validation-gates, skill/testing-strategy, skill/code-review
**Depends on:** T580
**Created:** 2026-10-07
**Based on:**
- `docs/artifacts/conditional-pass-semantics-v4.md`: §§3–7 hold the edits, §9 "FU-1 verification" the checks, and
  §16 the orchestrator's rulings.
- `docs/artifacts/security-review-conditional-pass-semantics-v1.md`: three Security Engineer review rounds. v4 meets
  every condition.
- `docs/plans/plan-100-conditional-pass-and-authority-adr.md`
- `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted)

## 1. What and why

The user decided P39 on 2026-10-02:
- CONDITIONAL_PASS allows a merge, with its conditions tracked.
  - On the production track, conditions close before the next gate.
  - At the Release gate, they move to the next release cycle.
  - On the PoC track, they are recorded as debt by the handoff.
- FAIL blocks. A Tech Lead waiver still applies, but never to a security finding.
- A security HIGH or CRITICAL finding, a constraint breach, or an omitted, removed, disabled or weakened required
  control never qualifies for CONDITIONAL_PASS, on either track. A full-project audit treats the whole project as the
  code under review.

T580 v4 rules the exact edits. It went through three Security Engineer reviews, and v4 meets every condition. Apply
**v4's 21 required edits** (A1–A8, B1–B4, B2b, C1, C3, C4, R1–R5) **exactly as written**. Use v4 only, never v1–v3.
Also apply **C2**. It is optional in v4, but the orchestrator includes it: it adds the user's due points to "target
sprint".

## 2. The edits

Each edit is a `### <ID>: \`<file>…\`` heading followed by one four-backtick fence:
`Before:\n<text>\n\nAfter:\n<text>`.
- Copy each before/after pair programmatically from the fences. Do not retype them. Fences can contain nested
  fences, tables and `|` characters.
- Assert that each before-block occurs exactly once. The orchestrator confirmed this on `develop` `5eff98e` (v4
  §16.1). If one does not match, stop and report it.
- Check the result by content, not by hunk count. For each file, applying all of its pairs to develop's version must
  reproduce your file exactly.

| File (under `implementation/knowledge/`) | Edits |
|---|---|
| `agents/tech-lead.md` | A1, A2, A3, C4 |
| `commands/code-review.md` | A4 |
| `skills/validation-gates/SKILL.md` | A5, A6, A7, A8 |
| `skills/testing-strategy/SKILL.md` | B1 |
| `commands/security-audit.md` | B2, B2b, B3, B4 |
| `skills/code-review/SKILL.md` | C1, C2, C3 |
| `agents/release-manager.md` | R1, R2, R3 |
| `commands/prepare-release.md` | R4, R5 |

**Do NOT change any `maturity:` line.** Do not touch `AGENTS.md`, any instruction, or any other file.

## 3. Regenerate and declare

1. Run `node implementation/scripts/sync.mjs --root implementation` **and**
   `python3 implementation/scripts/generate-registry.py`.
2. Run `python3 -m tests.functional.test_root_install_parity --print-drift`. Add **exactly** the reported paths to the
   `drift` list in `tests/_baselines/root-install-drift.json`. The list is empty on develop after the third refresh.
   Never hand-edit the top-level platform folders.

## 4. Verify, don't assume

- Every check in v4 §9 "FU-1 verification", including its 0-hit patterns and exact counts. For C2, §9 only checks
  that its Before text matches exactly once.
- `sync.mjs --check` and `generate-registry.py --check` are clean. The parity gate is green. The audience lint
  passes.
- `test_code_review_skill_contract`, `test_validation_gates_skill_contract` and `test_wave3_skill_contracts` pass.
- `check-maturity.py --root implementation` reports 79 components, 0 failing, and the distribution is unchanged.
- **`scorecard.py --check` is OK (34/26/0).** This is how held-out golden coupling is detected. If it reports any
  regression, **stop and report it. Do not change any golden file.**
- The digests match **v15**, and `validate-tasks.py` passes.
- `python3 tests/run.py`: report the exit code, with output redirected to a file, never piped to `tail`. Expect 904 OK.

## 5. Constraints

- **Write scope:**
  - the eight source files above;
  - the regenerated mirrors and `implementation/registry/`;
  - the `drift` list in the parity baseline;
  - this brief's `**Status:**` line.
- **Do not touch `tests/golden/**`, and do not open it.** If a search reaches `tests/`, prune `tests/golden/held-out`
  before traversal.
- Do not touch `scripts/scorecard.py` or the evaluator-hash files.
- Do not read `.env`, credential or key files.
- Commit locally as one commit. **Do not push. Never run `glab mr merge` or any merge or approve API**, with no
  exceptions. Hand everything back.

## 6. Blocker protocol

Report blockers with a type (`technical` | `dependency` | `unclear_requirements` | `external`) and a severity
(`critical` | `major` | `minor`). If a before-text no longer matches, or the scorecard shows a regression, report it
rather than working around it.
