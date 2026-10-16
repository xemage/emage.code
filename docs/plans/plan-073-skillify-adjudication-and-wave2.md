# plan-073 — `/skillify` adjudication, golden-case wave 2, and two carried defects

**Status: scoped 2026-09-25, awaiting approval to dispatch.**
Based on: `docs/decisions/ADR-007-command-contract-authority.md`;
`docs/plans/plan-072-phase9-golden-case-coverage.md`;
`docs/tasks/task-T525.md`, `docs/tasks/task-T526.md`;
`docs/artifacts/command-promotion-readiness-v1.md`;
`docs/artifacts/protected-paths-v1.md` §5.

## 0. A correction to `T525`'s report, found while scoping this

`T525`'s closure record and MR !386 both state that the real skill corpus **"uniformly follows"**
the template declared by the `skillify` *skill*, and `active-tasks.md` says **"26 of 26 follow"**
it. **That is overstated. The corpus follows neither template.**

Measured against all 26 real `implementation/knowledge/skills/*/SKILL.md`:

| Template | Files satisfying it **completely** |
|---|---|
| the `/skillify` **command**'s (`## Trigger`, `## Inputs`, `## Steps`, `## Success Criteria`, `## Examples`) | **0 of 26** |
| the `skillify` **skill**'s (`## Purpose`, `## When to Use`, `## Prerequisites`, `## Procedure`, `## Examples`, `## Edge Cases`) | **1 of 26** |

Per-section, against the skill's template: `## When to Use` 20/26, `## Purpose` 16/26,
`## Procedure` 16/26, `## Examples` 9/26, `## Prerequisites` **2/26**, `## Edge Cases` **1/26**.

**The `0 of 26` finding stands and was independently verified twice** — the golden case's verdict
is unaffected and `/skillify` correctly does not promote. What changes is the *shape of the
adjudication*: this is not "a command contract versus a well-formed corpus following a rival
contract". It is **two declared contracts and a corpus that follows neither**.

How this got through: the orchestrator verified the **falsifying** claim (`0 of 26`) and did not
verify the **supporting** one (`26 of 26`). A claim that argues against the thing being proposed
gets scrutiny; a claim that merely colours it slides past. Worth naming, because it is a
general-purpose way to be wrong.

## 1. Why the adjudication is genuinely non-obvious

`ADR-007`'s core rule: *a command's declared contract is authoritative over the corpus unless the
contract contradicts a higher-authority document, or unless the only thing in dispute is a label
for content the corpus already carries.*

Checked before scoping, so the task starts from evidence rather than assumption:

- **Branch 1 does not fire.** `AGENTS.md` is silent on `SKILL.md` structure and no
  skills-format artifact exists (`docs/artifacts/` holds only
  `research-agents-skills-ecosystem-v1.md`, which is research, not a contract). There is no
  higher-authority document to contradict.
- **The "only a label" clause is the live question, and it is only partly satisfied.** Several
  sections map plausibly — `## Trigger` ≈ `## When to Use`, `## Inputs` ≈ `## Prerequisites`,
  `## Steps` ≈ `## Procedure` — which would make those **branch 3a** (relabelling: amend the
  labels). But `## Success Criteria` appears in only **3 of 26** and has no clear counterpart,
  which looks like **branch 3b** (omission: fix the corpus, the case stays failing).

**So the answer is probably per-section, not per-template**, and a single verdict for the whole
file may be the wrong shape. That is a hypothesis for `T527` to test, **not a conclusion to
implement**. `T515` was scoped the same way and its honest answer was not the tidy one.

## 2. The four tasks

| Task | Objective | Protected path? |
|---|---|---|
| `T527` | Adjudicate the `/skillify` contract conflict under `ADR-007` and execute the verdict | **yes** if the verdict touches the golden case |
| `T528` | Golden-case coverage wave 2 — 5 commands | **yes** — new case directories |
| `T529` | `handoff` schema permits an empty `writablePaths` | no |
| `T530` | Stale `new-feature-real-checkpoint-format-drift` brief | **yes** |

All four are `P2`. Per `T524`'s correction, `check-maturity.py:504` filters the ledger-defect scan
by priority, so `P2` rows never block criteria 3 or 7 — no task here blocks any other's promotion.

`T527` is the only one that unblocks a promotion (`/skillify`). `T528` is the bulk. `T529` and
`T530` are small carried defects that must not be left as prose: `T518`'s closure established that
**a hand-fix plus a ledger note is not a fix**, and the user has previously had to ask explicitly
for carried defects to be given tasks.

## 3. What wave 2 carries forward from wave 1

Wave 1 validated `plan-072` §1's controls. Two specifics are now mandatory rather than advisory:

1. **Quote the verbatim contract clause before writing any `expect.py`.** This is the control that
   actually did the work — going looking for a checkable clause in `skillify.md` is what surfaced
   the conflict. Keep the ordering.
2. **Ship a mutation harness as an explicit deliverable.** `T525`'s implementer built one
   unprompted: copy the case to a temp dir, damage the fixture, re-run `check()`. A check that
   cannot be made to fail is vacuous, and this is the only cheap way to tell a real green from a
   manufactured one. Wave 1 also showed it works in both directions — the harness caught a
   *mis-designed mutation* twice (once by the implementer, once by the orchestrator), which is
   itself evidence the technique is load-bearing rather than decorative.

And the precedent worth repeating in the brief: wave 1's four cases were **all** flipped to
`stable` together to measure, and the one red case blocked exactly one component while the other
three passed clean. The same authoring pass that earned three promotions also cost one. **An
implementer optimising for a green board would not have produced that distribution.**

## 4. Wave 2 scope

`/consolidate-memory`, `/bug-report`, `/batch`, `/new-project`, `/sprint-status` — five commands
with thin corpus, per `plan-072` §3. Wave 3 (`/team-status`, `/validate-workflow`, and the three
PoC commands, which have **no** corpus at all) stays unscoped until wave 2 reports.

## 5. Evaluator-hash, again

`T527`, `T528` and `T530` will each drift the `tests_golden` digest if they touch
`tests/golden/**`. This is now confirmed four times (`T520`, `T523`, `T525`, and whichever of these
lands first). **Every brief here pre-schedules the human sanction** — names the two tests that will
fail, puts the next `evaluator-hash-known-good-v<N>.json` explicitly out of the agent's scope, and
requires the agent to report the recomputed digests and stop. Agents have respected this boundary
three times running, including once where the agent noted it could have argued the refresh was in
scope and declined anyway. That behaviour is the standard.
