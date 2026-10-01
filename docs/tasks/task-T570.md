# T570 — Adjudicate the PoC skills' vocabulary and debt-scorecard rivalry (P35)

**ID:** T570
**Owner:** Solution Architect
**Status:** pending
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-01
**Based on:** `docs/plans/plan-094-poc-skills-alignment.md`; `docs/plans/plan-092-poc-contract-amendments.md` §4 (P35);
`docs/artifacts/poc-contract-resolution-v1.md` (rulings P29 and P31, the §1.4 authority gap, and the §9.2 FU-C approval);
`docs/decisions/ADR-007-command-contract-authority.md`.

## 1. What and why

T563 decided, and T564 implemented, that the PoC track has:
- a **binary outcome** (no `INCONCLUSIVE`);
- **one debt scorecard**, `POC-DEBT-SCORECARD.md` in the PoC root, in `poc-guidelines.md`'s structure;
- **S/M/L effort** with **CRITICAL/MEDIUM/LOW** severity.

Those rulings were applied to three commands and two agents. Three **`experimental` skills** still carry the old
contracts. T564's sweep found them, and they were parked as P35.

Decide how each skill aligns, and write the decision down. **Decision only.** Do not edit any skill, command, agent
or instruction. Implementation follows in a separate task sized by your artifact.

## 2. Facts verified by the orchestrator on `develop` `2d7d005`

| Skill (all `maturity: experimental`) | Self-description | Sites |
|---|---|---|
| `poc-evaluation` | "Assess proof-of-concept outcomes against explicit hypotheses and success criteria." | `INCONCLUSIVE` at `:21` (list item "Inconclusive"), `:37` (`[VERDICT] … result=VALIDATED\|INVALIDATED\|INCONCLUSIVE`), `:64` (`**{VALIDATED \| INVALIDATED \| INCONCLUSIVE}**`), `:103` ("A PoC with >50% untested criteria should receive an `INCONCLUSIVE` verdict, not `VALIDATED`.") |
| `rapid-prototyping` | "Create pragmatic scaffolding and integration patterns for fast proof-of-concept delivery." | `:102`, a checkpoint marker with `verdict=validated\|invalidated\|inconclusive` |
| `technical-debt-tracking` | "Document **PoC shortcuts** and production remediation plans using a consistent debt ledger." | see below |

**`technical-debt-tracking`: wider than vocabulary.**
- It scans the same `POC-DEBT` tags that `poc-guidelines.md` § Debt Scorecard says the scorecard "must account
  for" (`:36`).
- It produces its **own** "Technical Debt Scorecard v{N}" (`:136–171`) and a versioned debt ledger at
  `docs/artifacts/debt-ledger-v{N}.md` (`:128–131`). That is a candidate rival to `POC-DEBT-SCORECARD.md`, the same
  shape as P29a.
- Severity has four tiers: `critical | high | medium | low` (`:76`, `:91–96`, `:150–153`, and "Critical/High" at
  `:157`). Effort is `XS | S | M | L | XL` (`:78`), with a story-point mapping `XS=1 … XL=13` (`:119`). That is the
  P29b shape.
- Its promotion procedure (`:100–124`) creates rows in `docs/tasks/active-tasks.md`:
  - with priority **`should`** (`:107`, `:118`), but `AGENTS.md` § Task Protocol allows only `P0`, `P1`, `P2`;
  - in a `### T{ID}` block format with **Assignee** and **Points** fields. `AGENTS.md` instead has a ledger row
    with columns `ID | Title | Owner | Status | Priority | Depends on | Last update`, plus a brief at
    `docs/tasks/task-<ID>.md`.
  - `AGENTS.md` also says "Only orchestrators create/transition tasks".

**Consumers.** No agent or command names any of the three skills. They reference only each other: `rapid-prototyping:53`
and `poc-evaluation:93` point at `technical-debt-tracking`. No golden case quotes them; the only `tests/golden` hit is a
frozen registry copy in a `/discover-skills` fixture, which is not compared to the live registry. **No protected path is
involved.**

## 3. What to decide

- **Authority basis.** ADR-007 does not rank skills against stable instructions (`poc-contract-resolution-v1.md`
  §1.4). Establish, by quoting, why `poc-guidelines.md` and `AGENTS.md` govern these skills. Consider:
  - each skill's own PoC self-description;
  - `poc-guidelines.md`'s Rails jurisdiction;
  - the T542 / FU-C precedents for agent files.

  If the basis does not hold for some item, say so; do not force it.
- **`poc-evaluation` and `rapid-prototyping`:** apply P31. Specify the before/after wording for each site.
  - `:103`'s ">50% untested" rule needs a binary replacement consistent with the amended `/evaluate-poc` Failure mode:
    weak or untested evidence gives `INVALIDATED`, with `Evidence strength: weak` and a follow-up PoC.
  - `rapid-prototyping`'s checkpoint marker uses lowercase values. Decide whether case matters.
- **`technical-debt-tracking`:**
  - **(a) Scorecard identity.** Is its "Technical Debt Scorecard" the same artifact as `POC-DEBT-SCORECARD.md`, or a
    distinct one, the way T563 §3c ruled `TECHNICAL-DEBT.md` distinct? Decide, and say what changes.
  - **(b) Scales:** the four severity tiers, `XS…XL`, and the points mapping.
  - **(c) The debt ledger at `docs/artifacts/debt-ledger-v{N}.md`.**
  - **(d) The promotion procedure** against `AGENTS.md` § Task Protocol: the priorities, the row and brief format,
    and who may create tasks.
- **Blast radius:** confirm that nothing outside these three skills needs to change. If it does, list it.

For each item, give exact before/after wording, specific enough that a Backend Developer can apply it without
re-deciding anything, then a follow-up task table.

## 4. Output

`docs/artifacts/poc-skills-alignment-v1.md`.

## 5. Constraints

- **You have no Bash.** Mark unverified claims as such.
- **Write exactly one file:** the artifact. Hand it back uncommitted. Do not edit this brief.
- **Read-only** on everything. You do not need `tests/golden/`, so do not open it at all.
- **Do NOT run `glab mr merge` or any merge or approve API, and do not commit or push.**

## 6. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`. If a fact in §2 is
wrong, report it.
