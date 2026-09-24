# Artifact: agent-promotion-rerun-v1.md

> Filename: `agent-promotion-rerun-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata
- **Producer agent**: tech-lead
- **Task**: T514
- **Created**: 2026-09-24
- **Based on**: `docs/tasks/task-T514.md`; `docs/plans/plan-064-roadmap-v8-breadth-and-utility.md`
  §1.3 and Phase 10 (the hypothesis this artifact tests); `docs/artifacts/
  maturity-promotion-criteria-v1.md` (T431 — §3.1's agent criteria 1–7 and §3.5's shared
  defect-check definition, cited not re-derived); `docs/artifacts/maturity-levels-v1.md` (T430);
  `docs/artifacts/phase3-wave1-promotion-v1.md` (T433) and `docs/artifacts/
  phase3-wave2-promotion-v1.md` (T434 — the prior evaluations whose recorded blockers this run
  re-tests); `implementation/scripts/check-maturity.py` (T432 — the mechanical arbiter every
  result below was produced by, not estimated).
- **Supersedes**: none (first version)

## Body

### 0. Outcome summary — read this first

All 8 agents at `maturity: experimental` were re-evaluated mechanically. **5 promoted to
`stable`; 3 did not and remain `experimental`.**

- **Promoted (5):** `backend-developer`, `context-retriever`, `devops-engineer`,
  `evaluation-agent`, `solution-architect`.
- **Not promoted (3):** `orchestrator`, `security-engineer`, `tech-lead` — each blocked by a
  real, pre-existing, independently-tracked golden-suite defect against the command it owns.
  None of the three is blocked by anything this task could or should have fixed.

**`plan-064` §1.3's hypothesis is CONFIRMED, and its count is CORRECTED UPWARD.** The four
agents it named (`context-retriever`, `devops-engineer`, `evaluation-agent`,
`solution-architect`) were indeed blocked solely by the `T456`/`T457` ledger-defect rule, and all
four now pass. A fifth — `backend-developer` — also passes, which §1.3 did not anticipate. See §3.

Post-run state: `check-maturity.py --verbose` reports **79 components checked, 0 failing their
claimed level**; the agent category is now **25 `stable` / 3 `experimental`** (was 20 / 8).

### 1. Method

Exactly the mechanical procedure `task-T514.md` specifies, run once per agent in isolation so
each result is independently attributable and independently re-runnable by a reviewer:

1. Set `maturity: stable` in `implementation/knowledge/agents/<id>.md` (that agent only).
2. Run `python3 implementation/scripts/check-maturity.py --verbose`.
3. Record `PASS`, or `FAIL` plus the numbered criterion the checker itself named.
4. Revert, and move to the next agent.

Then apply the 5 passing flips together and re-run to confirm they hold jointly (they do — the
criteria are per-component and the joint result matches the eight isolated results exactly), and
regenerate `implementation/registry/{index.json,summary.md}`.

No criterion, checker, schema, or test was modified. No new documentation, ledger row,
cross-reference, or golden case was authored to convert a `FAIL` into a `PASS` — see §4.

**Reproduce any single row below:**

```
sed -i 's/^maturity: experimental$/maturity: stable/' implementation/knowledge/agents/<id>.md
python3 implementation/scripts/check-maturity.py --verbose | grep -A3 "agent/<id> "
```

### 2. Per-agent results — all 8

Criterion numbering is `maturity-promotion-criteria-v1.md` §3.1: 1–3 are the
`experimental → beta` bar (schema-valid, `## Rails`, no open P0 defect), 4–7 add the
`beta → stable` bar (evidence, cross-reference, wiki documentation, no open P0 **or P1** defect).

| # | Agent | Outcome | Failing criterion | What the checker actually said | What would close it |
|---|-------|---------|-------------------|--------------------------------|---------------------|
| 1 | `backend-developer` | **PASS → promoted** | — | `PASS agent/backend-developer (stable)` | — |
| 2 | `context-retriever` | **PASS → promoted** | — | `PASS agent/context-retriever (stable)` | — |
| 3 | `devops-engineer` | **PASS → promoted** | — | `PASS agent/devops-engineer (stable)` | — |
| 4 | `evaluation-agent` | **PASS → promoted** | — | `PASS agent/evaluation-agent (stable)` | — |
| 5 | `orchestrator` | **FAIL → stays `experimental`** | **#3** *and* **#7** | golden case `new-feature-real-checkpoint-format-drift` is a `known_failing` `tracked_defect` for `/new-feature` | Resolve the tracked defect itself: `/new-feature` Phase 3 step 7 mandates a single-line `[CHECKPOINT] id=… \| done=… \| …` marker that **zero** real checkpoints in `docs/checkpoints/` emit (the repo uses the full-markdown checkpoint convention). Either align the command's declared contract with the convention the repo actually follows, or change the convention — then re-classify the case out of `known_failing`/`tracked_defect`. The case file lives under the protected path `tests/golden/**` and needs the documented exception process. |
| 6 | `security-engineer` | **FAIL → stays `experimental`** | **#3** *and* **#7** | golden case `security-audit-critical-not-fail` is a `known_failing` `tracked_defect` for `/security-audit` | Resolve the tracked defect itself: `/security-audit` states unconditionally that any `CRITICAL` finding forces verdict `FAIL`, with no compensating-control exception clause, while the fixture records `CRITICAL findings: 1` with `Status: CONDITIONAL_PASS`. Either add an explicit, bounded compensating-control clause to the command contract or hold the unconditional rule and fix the fixture's reasoning — then re-classify the case. Same protected-path constraint as row 5. |
| 7 | `solution-architect` | **PASS → promoted** | — | `PASS agent/solution-architect (stable)` | — |
| 8 | `tech-lead` | **FAIL → stays `experimental`** | **#3** *and* **#7** | a `known_failing` `tracked_defect` golden case for `/code-review` — **case ID deliberately withheld**: it is a held-out case, and `tests/functional/test_golden_held_out_isolation.py` Check B forbids any file outside `tests/golden/` from naming a held-out case ID as a whole token. Same withholding precedent as `T433`'s own ledger row. | Resolve the underlying `/code-review` verdict-format drift the case tracks, then re-classify it out of `known_failing`/`tracked_defect`. Details are intentionally not restated here for the same isolation reason; they are readable in the case's own directory by anyone entitled to it. Same protected-path constraint as row 5. |

**Note on rows 5, 6 and 8:** all three fail criterion **#3** as well as **#7**, i.e. they do not
currently clear the `experimental → beta` bar either, not merely the `beta → stable` one. This is
not a stricter reading applied here — `check-maturity.py`'s `_open_defect()` applies the
golden-suite `tracked_defect` check at both tiers, while the `{P0, P1}` ledger filter is what
differs between them. So the honest statement is that these three are blocked from **any**
promotion, not just from `stable`.

**Note on why exactly these three:** they are 3 of the 4 agents that own a command via a
command's `agent:` frontmatter (`/new-feature` → `orchestrator`, `/security-audit` →
`security-engineer`, `/code-review` → `tech-lead`). Command ownership is what makes criterion
4(i)'s golden evidence available to an agent — and it is also what makes the owned command's
golden defects attributable back to it. The mechanism that most easily earns these agents their
evidence is the same mechanism currently blocking them. That is the criteria working as designed,
not a defect in them.

### 3. `plan-064` §1.3 — confirmed on substance, corrected on count

§1.3 claims: `context-retriever`, `devops-engineer`, `evaluation-agent`, `solution-architect`
"were blocked from `stable` **solely** by `check-maturity.py`'s self-referential ledger-defect
rule firing on open P0/P1 tasks `T456`/`T457` naming them. Both tasks closed on 2026-09-17. That
blocker is structurally gone."

**Confirmed, with evidence:**

- `T456` and `T457` are both present in `docs/tasks/completed-tasks.md` and absent from
  `docs/tasks/active-tasks.md`. `T457`'s closure row records both halves of the underlying
  scoped-execution-primitive gap as independently verified resolved.
- `docs/tasks/active-tasks.md` currently holds exactly **one** row — `T514` itself, at `P2`.
  There is therefore **no open P0 or P1 ledger row at all** for criterion 7's scan to match, for
  any component. The ledger half of criterion 7 is vacuously satisfied repo-wide right now.
- All four named agents return a clean `PASS` at `stable`, with no residual failure on any other
  criterion. Their evidence (criterion 4), cross-references (5) and wiki documentation (6) were
  already in place from the `T433`/`T434` waves; only the ledger blocker was ever outstanding.

**Corrected: the count is five, not four.** `backend-developer` also passes and was also
promoted. §1.3 undercounted because it drew on `phase3-wave2-promotion-v1.md`, which covers Wave
2's 23 agents — and `backend-developer` was not among them. It was a **Wave 1** candidate,
recorded in `phase3-wave1-promotion-v1.md` §3.2, which documents it as blocked by
`open P1 task T457 names it in its brief` and correctly characterises that hit as a **false
positive**: `task-T457.md`'s only mention of `backend-developer` was a forward-looking
possible-assignee note ("`and/or backend-developer` for the scoped-tool mechanism itself — to be
assigned once the design [is made]"), not a defect report against the agent. Wave 1 noted the
match "does **not** resolve when `T433` archives" — and it did not; it resolved when `T457` itself
closed. The blocker was mechanically identical to the other four's, so the fifth promotion was
available on exactly the same date, just recorded in a different artifact.

**Net correction:** §1.3's causal claim is right and its list is right as far as it goes; its
implied completeness ("four `stable` promotions available today") is one short. Five were
available. All five were taken.

### 4. What was deliberately *not* done

Per `task-T514.md`'s constraints, and consistent with `phase3-wave2-promotion-v1.md` §4's
treatment of the command golden-case gap:

- **No criterion, checker or test weakened.** `check-maturity.py`,
  `maturity-promotion-criteria-v1.md` and `maturity-levels-v1.md` are untouched by this task.
  Verifiable directly: they do not appear in this branch's diff.
- **No evidence authored to force a pass.** The three failures are real tracked defects in the
  golden suite. Fixing them is genuine, differently-scoped work on three command surfaces — it is
  not a documentation gap that could be papered over, and it would have required writing to
  `tests/golden/**`, a protected path this task may not touch.
- **No golden case re-classified.** Flipping a `known_failing`/`tracked_defect` case to
  `expected_pass` would have converted all three failures into passes with a one-line edit. That
  is precisely the unearned promotion this ladder exists to prevent, and it is out of scope
  twice over (protected path, and "do not weaken the bar").
- **Root self-install mirrors** (`.claude/`, `.cursor/`, … at the repo root) not refreshed — a
  separate, known drift axis owned by `T512`, explicitly out of scope here.

#### 4.1 One test *was* edited — disclosed in full, because the constraint says not to

`tests/functional/test_check_maturity.py`'s
`TestCheckMaturityRealRepo.test_real_registry_runs_clean_at_experimental_baseline` hardcodes the
real repo's current maturity **distribution** as a snapshot:

```
self.assertIn("agent/experimental: 8 pass, 0 fail", proc.stdout)   ->  3 pass
self.assertIn("agent/stable: 20 pass, 0 fail", proc.stdout)        -> 25 pass
```

It failed after the promotions and was updated to the new counts. Stating plainly why this is
**not** the prohibited kind of test edit:

1. **It does not convert any maturity `FAIL` into a `PASS`.** The three failing agents still fail
   and are still `experimental`. No component's outcome changed because of this edit.
2. **It asserts a snapshot, not a criterion.** The load-bearing assertions in the same test —
   `returncode == 0` and `"79 components checked, 0 failing their claimed level"` — are
   **unchanged**. Those are the real gate, and they still hold. The two edited lines only record
   how the 79 are distributed across tiers, which changes by design on every legitimate
   promotion.
3. **Direct precedent, same file, same two lines.** Both prior promotion waves updated exactly
   these assertions in the same commit as the promotion itself: `2f5928f`
   (28→27 experimental / +1 stable) and `e28f168` (27→8 experimental / 1→20 stable). This run
   follows that established pattern rather than inventing a disposition.
4. **Not updating it was not an option that preserves the bar** — it would leave `tests/run.py`
   red and CI failing, with the test asserting a distribution the repo deliberately no longer has.

If a reviewer disagrees with this reading, the correct remedy is to revert the two assertion
lines *and* the five promotions together, not to keep the promotions with a stale snapshot.

### 5. Disclosed conflict of interest, and how it resolved

`tech-lead` owns this task and is itself one of the eight agents evaluated. The arrangement is
sound as structured — the decider is `check-maturity.py`, not the owner's judgement — and the
result is the strongest available evidence that it held: **`tech-lead` failed and was not
promoted.** The owner's own entry is one of the three `experimental` rows it is reporting.

The top-level session's independent re-run of `check-maturity.py` against `tech-lead`'s result
specifically remains warranted and is not made redundant by this outcome; it is cheap and it is
the control that would have caught the opposite result. Reproduce with the §1 snippet using
`<id>` = `tech-lead`; the expected output is a `FAIL` naming criteria #3 and #7.

No objection is raised to the arrangement.

### 6. Verification performed

| Check | Result |
|-------|--------|
| `python3 implementation/scripts/check-maturity.py --verbose` | 79 components checked, **0 failing their claimed level**; agent: 25 `stable` / 3 `experimental` |
| `python3 tests/run.py` | see §7 |
| `python3 docs/tasks/validate-tasks.py` | see §7 |
| `node implementation/scripts/sync.mjs --root implementation --check` | **no drift across 577 files** — confirming, not assuming, `task-T514.md`'s pre-dispatch finding that `maturity` is not projected into the per-platform agent files |
| `python3 implementation/scripts/generate-registry.py --root implementation` | regenerated; diff confined to the 5 promoted ids' `maturity` + `checksum` values and `generatedAt` |
| Protected paths | `tests/golden/**` and `scripts/scorecard.py` absent from this branch's diff |
| Held-out isolation | the held-out case ID blocking `tech-lead` is **not** named in this artifact or in any other file this task touches |

### 7. Consumed by

- `docs/tasks/task-T514.md` — this task's acceptance criteria.
- Any future promotion re-run: the three rows in §2 marked `FAIL` are the complete, current list
  of what stands between the agent category and 28/28 `stable`, and each names a concrete,
  independently-actionable defect rather than a subjective gap.
