# checkpoint-037 — Phase 9: queue empty, repo root refreshed to zero drift

**Phase:** `plan-064` Phase 9 (command maturity) — execution round closed; no open rows
**Written:** 2026-10-01
**Author:** orchestrator
**Based on:** `checkpoint-036`; `plan-065` through `plan-086`; MRs !375–!432
**Ledger at this checkpoint:** **0 active, 354 completed** (checkpoint-036: 0 active, 316 completed)

## 1. Progress summary

Thirty-eight tasks closed since `checkpoint-036`. Command maturity moved from **0 `stable` / 19
`experimental` to 9 / 10**, and agents from 25 / 3 to 26 / 2. Both counts were measured at checkpoint-036's
own commit (`1114ada`) and at `develop`, not recalled. The installer gained a safe repo-root refresh mode,
then used it once, with user approval: the root harness matches a fresh install for the first time since
`fee245a`. Two data-loss defects and one confidentiality leak in shipped behaviour were found and fixed.
The queue is empty.

## 2. Completed tasks

Generated from `docs/tasks/completed-tasks.md` — the ledger is the source of truth; this is a summary.

| Done on | Count | Tasks |
|---|---|---|
| 2026-09-25 | 9 | T518, T520, T522, T523, T524, T525, T526, T527, T531 |
| 2026-09-26 | 16 | T519, T521, T533, T528, T534, T529, T536, T537, T540, T535, T541, T542, T530, T532, T546, T545 |
| 2026-09-30 | 10 | T549, T543, T539, T544, T548, T547, T551, T550, T552, T553 |
| 2026-10-01 | 3 | T538, T555, T554 |

Highlights, by theme:

- **Command maturity and golden coverage.** T518–T527, T531, T533–T537, T540, T541 (golden waves 1–2;
  ADR-007 branches applied to `/skillify` and `/batch`; scorecard staleness gate; validate-tasks C12–C14).
- **Audience and authority.** T532 (`/skillify` output path), T545 (`AGENTS.md` bullet 2 — the root file is
  a render of `implementation/AGENTS.md`), T546 (the `audience:` decision), T547 (dead
  `04-protocols.md` citations), T549 + T551 (`/consolidate-memory` and `memory-management` stopped instructing
  data loss), T553 + T554 (`/handoff` and `/discover-skills` repaired so their `stable` claims hold in installed
  projects).
- **Installer and root harness.** T543 (root-parity gate), T550 (`--projections-only`), T552 (`--update`
  refused at the root; self-copies are no-ops), T555 (**security**: the `cp` fallback leaked this repository's
  memory index into client projects), plus the plan-082 §2 root refresh (MR !432).
- **Golden batch.** T539, T544, T548 under one baseline authorization.
- **Tidying.** T528–T530, T538, T542.

## 3. Active tasks and blockers

| | |
|---|---|
| Active tasks | **none** |
| Active blockers | **none** |

## 4. Key decisions

- **Decision:** a P0/P1 ledger row whose `**Affects:**` names a `stable` component is not a usable way to
  track a defect (`plan-081` §1). **Rationale:** measured — `check.py --maturity` exits 1, CI's
  `validation-super-gate` fails, and every merge is blocked, including the fix's own.
  **Alternatives rejected:** "P1 makes the gate honestly red" — it makes the repository unmergeable.
- **Decision:** the four questions the user delegated on 2026-09-30, settled in `plan-083`, each with a
  revisit condition:
  1. **No demotion** of `/discover-skills` or `/handoff`. Its condition — both repairs land — has now been met.
  2. **Batched dispatch** per contention group and owner.
  3. **Parked items live in plans with triggers**, rather than in a separate register.
  4. **`protected-paths-v1.md` stays edited in place.**
- **Decision:** the **top-level orchestrator session merges**, after its own independent verification, a
  green pipeline, a `mergeable` status and a SHA pin; **subagents never merge** (user instruction,
  2026-09-30). **Rationale:** keeps verification independent of authorship. **Alternatives rejected:** giving
  merge rights to the Orchestrator *subagent*, which invented a "docs-only" exception on 2026-09-16.
- **Decision:** repo-root drift is a **defect**, not a convention (T543). **Rationale:** those trees are the
  live runtime. The T382/T403/T406 precedent held as to mechanism but not intent.
- **Decision:** a golden checker must not be stricter than its contract. Applied to T548's skillify uniqueness
  (scoped per directory) and to T554's stale-registry case. **Alternatives rejected:** whole-set uniqueness,
  which rejected correct multi-platform output.
- **Decision:** evaluator-hash baselines **v8 → v11**, each explicitly authorized by the user — eleven
  escalations in this phase, none self-granted. Current: `tests_golden` `a6326b97…`; `scripts_scorecard`
  `45346c17…`, unchanged since v5.

## 5. Structural findings worth carrying forward

- **The root `AGENTS.md` is generated** (`render(implementation/AGENTS.md, --platform all)`); edit the source.
- **Every `implementation/knowledge/` change must declare its repo-root paths** in
  `tests/_baselines/root-install-drift.json` in the same MR, until the root is refreshed again. The list is
  **empty** now, so drift starts from zero.
- **`install.sh --projections-only`** is the only mode permitted at the repo root; `--update` is refused there.
- **No golden case runs against an installed target** except where a fixture adds one (T554 did). Audience
  defects are invisible to the maturity ladder by construction.
- **Brief defects:** nearly every task this phase found at least one defect in its brief or in the documents
  it cited — including several in briefs the orchestrator wrote. Implementers reported them rather than
  working around them; keep telling them to.

## 6. Parked items — all of them (`plan-083` decision 3 requires the full list)

P1–P3 were promoted to T553/T554 and are closed.

| # | Item | Trigger |
|---|---|---|
| P4 | `.<platform>/skills/local/` durable skill home in targets | vendor clients confirmed to walk `skills/local/*/SKILL.md` (T550 half fired) |
| P5 | Implement the `audience:` key (schema + 19 frontmatter lines, one commit) | a round with no open `implementation/knowledge/` task — **fired now** |
| P6 | `/prepare-release` → `audience: authoring` | P5 merged |
| P7 | Seventh `_replace_one` for `AGENTS.md` bullet 2 paths | any `render_installed_agents.py` task |
| P8 | Seven manifests reference a missing `_manifest.schema.json` | any `implementation/platforms/` task |
| P9 | `/validate-workflow` likely always FAILs (not every gate emits a VERDICT) | golden wave 3 for `/validate-workflow` |
| P10 | Approval vocabulary differs (`new-project` vs `plan-approve-execute`) | any edit to either |
| P11 | Plan filenames differ (`feature-<slug>`, `poc-<slug>` vs `plan-<ID>`) | any edit to those commands or `orchestrator.md` |
| P12 | PoC debt scorecard specified in two locations | golden wave 3 for the PoC commands |
| P13 | Handoff golden fixture embeds the pre-T529 schema | next golden batch |
| P14 | Consolidate-memory fixture's Promote rows name never-use targets; docstring stale | next golden batch |
| P15 | Skillify `case.yaml` reason carries a stale path | next golden batch |
| P16 | `batch.md` declares no character set for `<slug>` | next knowledge batch |
| P17 | `--target <repo>/implementation --update` still writes the source | next `install.sh` task |
| P18 | `--update` help line understates that the ledger file is rewritten | next `install.sh` task |
| P19 | `dependency-graphing` palette swaps `in_progress`/`in_review` vs the status commands | next knowledge batch |
| P20 | `docs/tasks/__pycache__/` ships on every fresh install | next `install.sh` task |
| P21 | `cp`-fallback file/directory type conflicts fail loudly where `rsync` replaces | next `install.sh` task |

One more item surfaced after `plan-086` and is **not yet in any plan**: `/discover-skills` step 6 merges
"pack registry entries" from `packs/installed/`, but no pack format contains such entries, so the step does
nothing in either audience (T554 hand-back). It is listed here so it is not lost, and **must be carried into
the next plan that scopes `/discover-skills` or packaging work as P22** — `plan-083` decision 3 keeps parked
items in plans, not checkpoints.

## 7. Suite health and verification at this checkpoint

| Check | Result |
|---|---|
| `tests/run.py` | **Ran 871, OK (skipped=24)** — the 24th skip is the plan-coverage test, which has no rows to verify |
| `validate-tasks.py` | PASS — 0 active, 354 completed |
| `check-maturity.py` | 79 components, 0 failing; agent 26/2, command 9/10, instruction 4/2, skill 7/19 (stable/experimental) |
| `check.py --maturity --schemas --registry` | exit 0 |
| `sync.mjs --check` / `generate-registry.py --check` | no drift / up to date |
| `scorecard.py --check` | clean — 29 cases, 21 pass, 0 regressions |
| root parity (`--print-drift`) | `[]` — declared list empty |
| evaluator hash | matches v11 |

## 8. Next steps

1. **P5 — implement `audience:`**: its trigger has fired. It touches all 19 commands, so it runs alone in the
   knowledge group, with root paths declared in the same MR.
2. **An `install.sh` batch for P17, P18, P20, P21**: four small items in one file.
3. **Golden wave 3** (`/team-status`, `/validate-workflow`, the three PoC commands), folding in P9, P12–P15.

## 9. Not done at this checkpoint

**Older checkpoints are not compressed.** The `checkpoint-protocol` skill says to compress all but the latest
two, but this repository has never compressed one (no file carries the "Compressed" marker), and the skill
calls compression irreversible. Compressing checkpoint-035 and earlier would be a one-way rewrite of
historical records that nobody asked for. Raise it as a decision if wanted.

## 10. Token spend

This phase ran across several sessions and two context compactions. A precise figure is not recoverable; the
orchestrator session's budget was large and was not a constraint. Delegated agents ran between roughly 80k
and 260k tokens each, the largest being batch and install tasks.
