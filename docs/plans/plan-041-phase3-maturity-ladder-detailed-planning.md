# Plan 041 — Phase 3 (Maturity Ladder) detailed planning pass

> Filename: `plan-041-phase3-maturity-ladder-detailed-planning.md`

**Status:** proposed — presented for review in this session's report, **not approved for
task-brief authoring or execution**. Mirrors the precedent set by `plan-037-phase2-phase5-
sequencing.md` (Phase 2) and `plan-038-phase5-detailed-planning.md` (Phase 5): both phases sat at
`plan-035`'s own `"Status: proposed — not approved for task-brief authoring or execution"` until a
dedicated planning pass was written and approved, *before* any individual task brief (`task-T4xx.md`)
was authored. This document is that pass for Phase 3.

**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.3 (phase graph), §2.4 Phase 3
(task table, T430-T437, unchanged here); `docs/checkpoints/checkpoint-021-phase1-complete-gate-g1-
closed.md` (Gate G1 closure); `docs/checkpoints/checkpoint-022-phase2-complete.md` (Phase 2
closure and its own "G1/G2 determination" section — the most direct existing analysis of Phase 3's
start condition); `docs/plans/plan-037-phase2-phase5-sequencing.md` (established the Phase-2-
before-Phase-5 sequencing this plan does not revisit); `docs/plans/plan-038-phase5-detailed-
planning.md`'s "Open planning questions carried forward" (first recorded the Gate G2 circularity
addressed below); `docs/checkpoints/checkpoint-027-phase5-6of7-done-t456-blocked.md` (latest
checkpoint on `develop`, confirms Phase 5/T456/T458 state, unrelated to Phase 3 but establishes
there is no newer roadmap state this plan needs to account for); `implementation/registry/
schema.json` and `implementation/registry/summary.md` (read directly this session — see Finding 2
below).

## Goal

Produce the same kind of dispatch-ready decomposition for Phase 3 (T430-T437, "Maturity Ladder")
that `plan-037`/`plan-038` produced for Phase 2 and Phase 5: a re-confirmed start-condition check,
a concrete per-task sequencing/agent-assignment table, an artifact flow, risks, and — specific to
Phase 3 — an explicit resolution of what the already-documented Gate G2 circularity means in
practice, since it was deliberately left open by `plan-038` "for whoever next plans Phase 3." This
plan does not itself author any `task-T43x.md` brief and does not dispatch any agent — per this
project's own Plan-Approve-Execute protocol, that is the next, separate step after user approval.

## Re-confirmed state (2026-09-09, this session)

- `origin/develop` HEAD is `bbe0c52` (fetched fresh this session). `docs/checkpoints/checkpoint-
  027-...md` is the latest checkpoint on `develop`; `git log` from its merge commit to
  `origin/develop` is empty — no newer roadmap-relevant state exists that this plan is missing.
- Grepped `active-tasks.md` and `completed-tasks.md` for `T43[0-9]`: **zero matches for
  T430-T432 and T434-T437; one match for T433**, but that single hit is a narrative cross-
  reference inside `completed-tasks.md`'s T455 entry text, not a T433 row — **no Phase 3 task has
  been dispatched, is in progress, or is done.** Phase 3 has not been silently started.
- **Phase 3's start condition is met.** Per `plan-035` §2.3's own phase graph, Phase 3 requires
  two inbound edges: `G1 --> P3` and `P2 --> P3`. Both are independently confirmed satisfied:
  Gate G1 closed at `checkpoint-021` (2026-08-13); Phase 2 (T420-T423) closed in full at
  `checkpoint-022` (2026-09-08), independently re-verified this session (`completed-tasks.md`'s
  T420-T423 entries, `checkpoint-022`'s own three-bullet acceptance-criteria confirmation). This
  matches `checkpoint-022`'s own contemporaneous conclusion ("it makes Phase 3 *proposable* as a
  next phase... that precondition is now met in full") — re-derived here from primary sources, not
  taken on that checkpoint's word alone.
- **Finding 1 — Gate G2 does not gate Phase 3's start; it gates Phase 3's own exit to Phase 4, and
  the "circularity" `plan-038` flagged is real but does not block this plan.** `plan-035`'s phase
  graph reads `P3 --> G2 --> P4`, and §2.4 states "Gate G2 closes when Wave 1 (T433) is complete
  for the routing target classes" immediately after Phase 3's own acceptance-criteria list — T433
  is one of Phase 3's own eight tasks (T430-T432 precede it). `plan-038`'s "Open planning
  questions" section already named this precisely: G2 is closed *by* completing part of the phase
  it nominally gates, unlike G0/G1/G3/G4, which each gate something outside their own phase — and
  explicitly deferred resolving it to "whoever next plans Phase 3." Resolving it now, with the
  actual text: this circularity affects **only** the definition of Phase 3's own *exit* criterion
  (and therefore Phase 4's entry), not whether Phase 3 can begin — Phase 3's own entry condition
  (G1 + Phase 2) contains no reference to G2 or T433 anywhere in `plan-035`. **Phase 3 can start on
  the evidence above.** What remains genuinely unresolved — and is *not* resolved by this plan,
  consistent with `plan-038`'s own disposition — is what "the routing target classes" means
  operationally: `plan-035`'s Gate table (§2.2) defines G2 in terms of Phase 4's own task tiers
  ("no cheap-model routing until the target task class has a stable brief"), but Phase 4's task
  tiers are not defined until T440, which is gated behind G2 itself. Two readings are consistent
  with the surrounding text and neither is stated explicitly enough to pick without a user
  decision: (a) "the routing target classes" informally *means* T433's own named Wave 1 set (the
  eight highest-traffic components), making G2 close automatically on T433's completion with no
  further definition needed; or (b) G2 requires a lightweight, forward-looking identification of
  which of Wave 1's promoted components are actually routing candidates (a strict subset, decided
  at T433's own closeout, not deferred to T440). This is flagged again here, now scoped
  specifically to **T433's own acceptance criteria**, which is where it must actually be answered —
  not before Phase 3 starts, but before Phase 3's fourth task closes. This plan's task table below
  carries the question forward to T433 explicitly rather than silently picking (a) or (b).
- **Finding 2 — `plan-035`'s premise for T430 ("define maturity levels... `experimental` → `beta`
  → `stable` → `deprecated`") is partially stale.** Read `implementation/registry/schema.json`
  directly (not assumed from `plan-035`'s prose): a `maturity` field **already exists** today, with
  enum `["draft", "beta", "ga", "deprecated"]` — different names than `plan-035`'s proposed four
  levels, most notably `ga` vs. `stable` and `draft` vs. `experimental`. Read `implementation/
  registry/summary.md` directly: all 77 registered components (28 agents + 19 commands + 4
  instructions + 26 skills, minus overlaps per the file's own "Counts" section) carry `maturity:
  beta` uniformly today — confirmed by grep, 77 of 79 table rows read `beta` (2 non-data rows: the
  Markdown header separator and header row itself) — this part of `plan-035`'s framing ("end the
  state where 76 of 76 components are beta") holds and does not need correction; only the *level
  names* do. **T430, as actually dispatched, needs to be scoped as a migration/rename decision
  against an existing enum, not a greenfield schema addition** — this is a real, concrete
  correction analogous to `plan-037`'s own `.vscode/mcp.json` finding and `plan-038`'s SoloMD
  verification, surfaced here so T430's eventual brief does not repeat `plan-035`'s stale premise.
  This does not change T430's owner (`solution-architect`) or its Phase 3 sequencing — only its
  actual scope of work once dispatched.
- No other roadmap item (Phase 4, Phase 6, Track C/CWSO) has any state change relevant to Phase 3
  that was not already captured by `checkpoint-021`/`checkpoint-022`.

## Task breakdown (T430-T437) — sequencing and agent assignment

`plan-035` §2.4's task table (task ID, title, owner, nominal scope) is **unchanged** by this plan —
same eight tasks, same owners. What this plan adds is real sequencing, per-task dependency detail,
and the two findings above folded into the tasks they actually affect.

### Task graph

```mermaid
graph TD
    G1["Gate G1 (closed)"] --> P3start
    P2["Phase 2 (done)"] --> P3start
    P3start(("Phase 3 start")) --> T430["T430 — maturity levels in schema.json<br/>solution-architect · medium<br/>NOW SCOPED AS a rename/migration of the<br/>existing draft/beta/ga/deprecated enum,<br/>not a greenfield addition (Finding 2)"]
    T430 --> T431["T431 — promotion criteria per category<br/>tech-lead · medium"]
    T431 --> T432["T432 — scripts/check-maturity.py<br/>devops-engineer · medium · CI-enforced"]
    T432 --> T433["T433 — Wave 1 promotion (8 components)<br/>tech-lead · large<br/>CARRIES Finding 1's open G2 question —<br/>acceptance criteria must state which<br/>promoted components double as<br/>'routing target classes' before this<br/>task closes"]
    T433 --> G2{{"Gate G2 closes here<br/>(per Finding 1's resolution)"}}
    T433 --> T434["T434 — Wave 2 (remaining core agents/commands)<br/>tech-lead · large"]
    T433 --> T435["T435 — Wave 3 (skills/instructions)<br/>tech-lead · large"]
    T434 --> T436["T436 — honest demotion pass<br/>product-owner · medium"]
    T435 --> T436
    T436 --> T437["T437 — regenerate summary.md +<br/>release-checkpoint template<br/>release-manager · small"]
    G2 --> P4["Phase 4 (Task-Tier Routing)<br/>not proposed by this plan"]
```

### Per-task summary

| Task | Depends on | Scope | Note |
|------|-----------|-------|------|
| T430 | Phase 3 start (G1 + Phase 2) | medium | Rescoped by Finding 2: reconcile/rename the existing `draft/beta/ga/deprecated` enum to `plan-035`'s proposed four levels (or a reconciled set — the exact target names are `solution-architect`'s call at dispatch, not pre-decided here), not a greenfield schema field. Must not silently drop the existing enum's semantics for any of the 77 already-classified components. |
| T431 | T430 | medium | Promotion criteria per `plan-035`'s five proposed bullets (golden-case coverage, declared rails, ≥1 referencing command/agent, end-user docs, no open P0/P1 defect). `tech-lead` owns this — matches this repo's existing pattern of `tech-lead` owning standards/criteria work. |
| T432 | T431 | medium | `scripts/check-maturity.py`, CI-enforced — cannot be written until T431's criteria are concrete and machine-checkable. `devops-engineer`, matching this repo's own precedent of CI/tooling scripts going to `devops-engineer` (T413/T419/T422 precedent). |
| T433 | T432 | large | Wave 1 — the 8 named highest-traffic components. **This is Phase 3's largest single task and the one most likely to need the same kind of mid-task re-scoping T407/T417-T419 needed** (8 components × 5 promotion criteria each is real, non-trivial work — golden-case authorship alone may need per-component sub-tasks). Flag this expectation in T433's own brief at dispatch time, mirroring `task-T458.md`'s explicit "do not treat this as one quick task" framing, rather than discover it mid-work. **Must explicitly resolve Finding 1's open question** (which, if any, of the 8 Wave-1 components are "routing target classes" for G2's purposes) as a stated acceptance criterion, not left implicit. |
| T434 | T433 | large | Wave 2, same promotion mechanics as T433 at whatever component count remains — likely also large, actual count TBD at T433's closeout (depends how many components exist outside the named 8 + skills/instructions, which T435 covers separately). |
| T435 | T433 | large | Wave 3 — skills and instructions specifically (26 skills + 4 instructions per `summary.md`'s current counts) — can run in parallel with T434 since both depend only on T433 (Waves 2 and 3 target disjoint component categories: T434 = "remaining core agents and commands," T435 = "skills and instructions"), not on each other. Flag this parallelization explicitly in each task's brief so it is not accidentally serialized at dispatch. |
| T436 | T434, T435 | medium | Honest demotion pass — needs both waves' actual promotion outcomes first, since "cannot reach `stable` in three waves" is only knowable once T434/T435 both report. `product-owner`, matching `plan-035`'s framing of this as a product-priorities call ("an accurate `experimental` label is worth more than an aspirational `beta` one"), not a technical one. |
| T437 | T436 | small | Regenerate `summary.md` + add maturity-distribution table to the release-checkpoint template. `release-manager`, last in sequence since it reports on the finished state of T430-T436. |

## Artifact flow

`docs/plans/plan-041-...md` (this document, pending approval) → (on approval) → individual
`docs/tasks/task-T430.md` through `task-T437.md` briefs authored in dependency order (mirroring
`plan-037`/`plan-038`'s own precedent — briefs written and dispatched one at a time, not all
upfront) → `implementation/registry/schema.json` (T430, migrated enum) → `docs/artifacts/
maturity-promotion-criteria-v1.md` or equivalent (T431) → `scripts/check-maturity.py` (T432) →
per-component promotion changes across `implementation/knowledge/**` + new/extended golden cases
(T433-T435) → `implementation/registry/summary.md` regenerated with a real distribution (T437) →
consumed by Phase 4's own eventual planning pass (not authored here) once Gate G2 closes.

## Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| T433's true scope (8 components × 5 criteria, including new golden cases) exceeds a single `large` task, mirroring T407/T417-T419's own mid-flight re-scoping | Medium-High | Medium | State the expectation explicitly in T433's own brief at dispatch time (mirrors `task-T458.md`'s disclosed precedent); treat a reported re-scoping as an expected outcome, not a failure, consistent with this project's existing disposition for T407/T458 |
| Finding 1's "routing target classes" question is left ambiguous at T433's dispatch, and G2 is declared closed without a stated basis | Medium | Medium (downstream: Phase 4 planning inherits an undefined routing-candidate set) | T433's brief must carry an explicit acceptance criterion naming which promoted components (if any) are routing-target candidates, per this plan's Task-breakdown row for T433 — not left to a later checkpoint to reconstruct |
| T430's actual dispatch repeats `plan-035`'s stale "greenfield schema" framing instead of the real rename/migration scope (Finding 2) | Low (now documented here) | Low-Medium (wasted work re-deriving what this plan already found) | This plan's Finding 2 and the T430 table row state the corrected scope explicitly; the eventual `task-T430.md` brief should cite this plan, not re-derive from `plan-035` §2.4 alone |
| Existing golden-suite coverage may not map cleanly onto the 8 Wave-1 components, requiring new golden cases as part of T433 rather than reuse of the existing 20 | Medium | Medium | Not resolved here — flagged for T433's own dispatch-time investigation (a `git ls-tree` scan this session found golden case names referencing `code-review`, `plan`, `prepare-release`, `security-audit`, `new-feature` workflows, but not all 8 Wave-1 component names directly — T433's brief should require an explicit coverage check before assuming reuse) |
| Phase 3 runs concurrently with a future Phase 4/6 dispatch and both touch `active-tasks.md` | Low (Phase 4/6 not proposed) | Medium | Same mitigation `plan-037`/`plan-038` already prescribed: separate worktree/branch per concurrent phase, no interleaved single-ledger-edit races |

## Token budget

Not set to a single number here, consistent with `plan-040`'s own disposition for a similarly
uncertain-scope task and `plan-038`'s treatment of its own `large`-scope tasks (T452/T453): T433 in
particular should get a concrete budget only once its implementer has done enough initial
investigation (golden-case coverage check, rails-gap survey across the 8 components) to estimate
honestly. T430-T432 and T436-T437 are closer in shape to this repo's existing `medium`/`small`
task norms and can likely use standard per-scope budgets at dispatch time.

## Open planning questions carried forward (not resolved by this document)

- **Finding 1's "routing target classes" question** — deliberately carried forward to T433's own
  acceptance criteria (see Task-breakdown table), not resolved here, since resolving it in the
  abstract (before Wave 1's actual promotion outcomes are known) risks the same kind of premature
  commitment this project's "no code before the design decision" discipline (`plan-038`'s own
  closing section) already avoids elsewhere.
- **T434's real component count** depends on T433's actual Wave-1 outcome and is not knowable
  precisely until then.
- **`feature/T475-codex-platform-integration`** remains unmerged and unrelated to Phase 3's own
  component set (Codex platform support, not an agent/command/skill maturity question) — noted
  here only because a stale registry snapshot on that branch could, if merged before T430, need a
  fresh `summary.md` regeneration; not a blocker to this plan.

## No prep work performed under this plan

No `task-T43x.md` brief was authored, no `implementation/registry/schema.json` edit was made, and
no agent was dispatched under this plan — consistent with `plan-035`'s own "Status: proposed — not
approved for task-brief authoring or execution" header for Phase 3, and with this project's
Plan-Approve-Execute protocol.

## Approval

- [ ] User approves Phase 3 detailed planning as scoped above (task breakdown, sequencing, agent
      assignments)
- [ ] User acknowledges Finding 1 (Gate G2 circularity resolution: does not block Phase 3's start;
      remains open for T433's own acceptance criteria) and Finding 2 (T430's real scope is a
      rename/migration of the existing `draft/beta/ga/deprecated` enum, not greenfield)
- [ ] User authorizes authoring `task-T430.md` (first task in sequence) once this plan is approved
- [ ] Plan locked; revisions create `plan-041-phase3-maturity-ladder-detailed-planning-v2.md`
