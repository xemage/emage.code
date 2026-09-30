# plan-084 — Round close: six tasks archived, three triggers fired, the parked set refreshed

**Created:** 2026-09-30
**Based on:** `docs/plans/plan-082-root-refresh-and-followups.md`; `docs/plans/plan-083-four-decisions-and-batching.md`;
MRs !422–!425.
**Scopes:** `T552`, `T553`, `T554`.

## 1. What this round delivered

The first round run under `plan-083`'s batched dispatch, and the first in which the orchestrator merged
its own verified MRs (user instruction, 2026-09-30). Four MRs merged; `develop` was green after each.

| MR | Tasks | Outcome |
|---|---|---|
| !422 | T543 archival | ledger |
| !423 | T547 + T551 (knowledge batch) | five dead `04-protocols.md` citations repointed; `memory-management` aligned with `/consolidate-memory` |
| !424 | T550 | `install.sh --projections-only`: the safe root refresh now exists |
| !425 | T539 + T544 + T548 (golden batch) | three golden fixes under **one** baseline authorization (v10) instead of three |

Batching paid off exactly as `plan-083` §2 predicted: T539 and T544 both regenerate `docs/benchmarks/`
and would have conflicted in parallel; the user authorized one baseline, not three.

## 2. `T552` (P1) — a data-loss defect found by T550

`--update` at the repository root on a host without `rsync` **deletes source code**:
`install_mcp_server_runtime` passes the same path as source and destination at the root, and
`sync_tree_into`'s `cp` fallback runs `rm -rf "$dest"` before copying from `$src`. Measured on a
synthetic copy: `implementation/runtime/memory/` 22 files → 0. Confirmed by the orchestrator by
reading the code. P1 with `**Affects:** —`, which cannot block merges.

## 3. Fired triggers from `plan-083` §4

| Parked | Trigger | Fired by | Now |
|---|---|---|---|
| P1 — install `runtime/handoff/` for `/handoff` | T550 merged | !424 | **`T553`**, batched with T552 (same function — T552's fix must land first or with it, or the new directory joins the data-loss path) |
| P2 — repair `/discover-skills` + re-derive its checker | golden batch merged, baseline authorized | !425 | **`T554`** |
| P3 — `new-project` golden brief quotes the dead citation | T547 merged | !423 | folded into **`T554`**'s grant — one baseline, not two |

`plan-083` §1's revisit condition now runs: `/discover-skills` and `/handoff` stay `stable` only if
T553 and T554 are dispatched within two rounds.

## 4. The parked set, refreshed

Still parked from `plan-083` §4, triggers unchanged: **P4** (`skills/local/` carve-out — needs vendor
recursion confirmed; T550 half of its trigger has fired), **P5** (implement `audience:`), **P6**
(`/prepare-release` → `authoring`, after P5), **P7** (seventh `_replace_one`), **P8** (dangling
`_manifest.schema.json` ×7).

New, from this round's hand-backs:

| # | Item | Found by | Trigger |
|---|---|---|---|
| P9 | `/validate-workflow` likely always FAILs: step 6 needs every gate to emit a VERDICT; plan approval emits Approve/Revise/Reject and the architecture briefing is no verdict gate | T547 | golden wave 3 for `/validate-workflow` — it needs a case anyway |
| P10 | Approval vocabulary: `new-project` APPROVED / APPROVED_WITH_CHANGES / REJECTED vs `plan-approve-execute` Approve / Revise / Reject | T547 | any edit to either |
| P11 | Plan filenames: `new-feature` `feature-<slug>`, `new-poc` `poc-<slug>` vs `orchestrator.md`'s required `plan-<ID>` | T547 | any edit to those commands or `orchestrator.md` |
| P12 | PoC debt scorecard in two locations (`docs/decisions/poc-debt-<slug>.md` vs `POC-DEBT-SCORECARD.md`) | T547 | golden wave 3 for the PoC commands |
| P13 | Handoff golden fixture embeds the **pre-T529** schema, so an empty `writablePaths` still passes for that fixture | T539 | next golden batch |
| P14 | Consolidate-memory fixture's Promote rows name "Never use" targets; its `expect.py` docstring says step 4 has no declared artifact | T548 | next golden batch |
| P15 | Skillify `case.yaml` `known_failing_reason` carries a stale path | T548 | next golden batch |
| P16 | `batch.md` declares no character set for `<slug>` | T544 | next knowledge batch |

**Decided, not parked:** the skillify checker accepts two *differently named* conforming skills in
different directories. The path template's single `<name>` arguably implies a shared name, but
requiring it would strengthen the checker beyond what the contract states; the case fails on its
sections regardless.

## 5. Still pending on the user

**`plan-082` §2 — the one real repo-root refresh**, now possible because T550 merged:
`bash scripts/install.sh --target . --platform all --projections-only`. Its pass condition: the changed
set equals the declared drift list exactly, and `docs/tasks/` is byte-identical before and after, or the
MR is abandoned. **Sequencing:** run it when no open task edits `implementation/knowledge/` — every
such task adds root paths to the list the refresh empties. T538 is open now; T554 will be.

## 6. Next dispatch

- **install batch:** T552 + T553 (DevOps Engineer) — `scripts/install.sh`, no contention.
- **T554** (QA Engineer) — knowledge + golden; waits for T538 to leave the knowledge group.
