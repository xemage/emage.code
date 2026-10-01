# T564 — Amend the PoC command contracts and the two PoC agents' outcome vocabulary (T563 FU-A + FU-C)

**ID:** T564
**Owner:** Backend Developer
**Status:** pending
**Priority:** P2
**Tier:** standard
**Affects:** command/new-poc, command/poc-demo, command/evaluate-poc, agent/poc-orchestrator, agent/evaluation-agent
**Depends on:** T562, T563
**Created:** 2026-10-01
**Based on:** `docs/artifacts/poc-contract-resolution-v1.md` §§2–6 and §9; `docs/plans/plan-092-poc-contract-amendments.md`.

## 1. What and why

T563 decided four PoC-track conflicts under ADR-007. Each PoC command is amended toward a higher-authority text
it contradicts: `poc-guidelines.md` (`maturity: stable`), `AGENTS.md`, or its own imported protocol. The
artifact is the specification. Read §§2–5 for the reasoning and §9 for the orchestrator's rulings. **This task
edits wording only.** It changes no golden case; T565 does that afterwards.

## 2. The edits (source files under `implementation/knowledge/` only)

| File:line | Now | Becomes | Ruling |
|---|---|---|---|
| `commands/new-poc.md:17` | Write to `docs/plans/poc-<slug>.md` | Write to `docs/plans/plan-<ID>.md` | P11 |
| `commands/new-poc.md:37` | Write to `docs/decisions/poc-debt-<slug>.md` | Write to `POC-DEBT-SCORECARD.md` in the PoC root, per `poc-guidelines.md` § Debt Scorecard | P29a |
| `commands/new-poc.md:46` | `checkpoint-poc-<gate>.md` | mirror `new-feature.md:30–31`: "per `AGENTS.md` § Checkpoint Protocol", stored at `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`, with `<phase>` naming the PoC gate. **Keep step 14's marker line.** | P30 |
| `commands/poc-demo.md:25,26,27` | the three `poc-…` links | the same three amended targets | P11, P30, P29a |
| `commands/poc-demo.md:37` | `VALIDATED \| INVALIDATED \| INCONCLUSIVE \| IN_PROGRESS` | `VALIDATED \| INVALIDATED \| IN_PROGRESS` | P31 |
| `commands/evaluate-poc.md:16` | Verdict (Validated, Invalidated, Inconclusive) | Verdict (Validated, Invalidated) | P31 |
| `commands/evaluate-poc.md:31` | `VALIDATED \| INVALIDATED \| INCONCLUSIVE` | `VALIDATED \| INVALIDATED` | P31 |
| `commands/evaluate-poc.md:34` | `(CRITICAL: <n>, HIGH: <n>, MEDIUM: <n>, LOW: <n>)` | `(CRITICAL: <n>, MEDIUM: <n>, LOW: <n>)` | P29b |
| `commands/evaluate-poc.md:59` | `CRITICAL/HIGH/MEDIUM/LOW` and `S/M/L/XL` | `CRITICAL/MEDIUM/LOW` and `S/M/L`. **Keep** the Risk, Owner and Production Impact columns. | P29b |
| `commands/evaluate-poc.md:65` | Failure mode returns `INCONCLUSIVE` | Weak evidence, or a hypothesis not actually tested by its deadline, returns `INVALIDATED` with `Evidence strength: weak`, and names a follow-up PoC with refined criteria as the recommended next step, rather than forcing a `VALIDATED` call. Cite `poc-guidelines.md` Rules 3–4. | P31 |
| `agents/poc-orchestrator.md:83` | (Validated / Invalidated / Inconclusive) | (Validated / Invalidated) | P31, FU-C |
| `agents/evaluation-agent.md:16` | Validated \| Invalidated \| Inconclusive | Validated \| Invalidated | P31, FU-C |
| `agents/evaluation-agent.md:49` | Failure mode returns `Inconclusive` | Same substance as the new `evaluate-poc.md:65`: `Invalidated` with the specific missing evidence named, plus a recommended follow-up PoC | P31, FU-C |

**Do not:**
- Define "PoC root". Quote the instruction's phrase (P33 is parked).
- Change `new-poc.md:36`'s attribute list or `evaluate-poc.md:19`. The scorecard's columns are P33's question.
- Touch `TECHNICAL-DEBT.md` references (§3c: no change).
- Touch `new-feature.md` (P32 is parked).
- Change any `maturity:` line.

**Sweep for missed sites.** Before committing, search all of `implementation/knowledge/` (source, every file
type) for each of the following:
- `INCONCLUSIVE` and `Inconclusive`
- `poc-<slug>`
- `poc-debt-`
- `checkpoint-poc-`
- `S/M/L/XL`
- `HIGH` in a severity context

Report every remaining hit, and explain why each one stays. Search for the concept, not only the literal string.

## 3. Regenerate and declare

1. Run `node implementation/scripts/sync.mjs --root implementation` **and**
   `python3 implementation/scripts/generate-registry.py`.
2. These are body changes, so the repo-root projections now lag. Run
   `python3 -m tests.functional.test_root_install_parity --print-drift`, then add **exactly** the new paths to
   `tests/_baselines/root-install-drift.json` `drift`, keeping the 6 `/batch` paths. **Never hand-edit the
   top-level platform folders.**

## 4. Verify, don't assume

- `sync.mjs --check`: no drift. `generate-registry.py --check`: up to date. The audience lint passes; if a new
  violation appears, report it and do not baseline it.
- `check-maturity.py --root implementation`: 79 components, 0 failing, command 13/6. Because this row is P2, it
  must not hold anything back. Confirm.
- `python3 scripts/scorecard.py --check` passes. The three PoC cases stay green, because their checks accept a
  superset of the amended values. Report each case's result.
- No `tests/golden/**` or `scripts/scorecard.py` change, so the hash still matches **v13**. Confirm.
- `python3 docs/tasks/validate-tasks.py`: PASS.
- `python3 tests/run.py`, exit code with output redirected to a file, never piped to `tail`. Baseline **904 OK**.
  Explain any change in the count.

## 5. Constraints

- **Write scope:**
  - the 5 source files above, at the listed lines only;
  - the regenerated `implementation/.<platform>/` mirrors and `implementation/registry/`;
  - `tests/_baselines/root-install-drift.json` (`drift` list only);
  - this brief's `**Status:**` line.
- **No `tests/golden/**`** (do not even read `held-out/`), no `scripts/scorecard.py`, no evaluator-hash files.
- Commit locally as one commit. **Do not push. Never run `glab mr merge` or any merge or approve API.** This
  applies with no exception for docs-only or wording-only changes. Hand everything back.

## 6. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`. If the artifact
or this brief is wrong, for example a line number has moved or a ruling cannot be applied as written, report it.
Do not work around it.
