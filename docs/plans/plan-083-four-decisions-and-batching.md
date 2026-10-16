# plan-083 — Four open decisions, settled; batched dispatch; parked work with triggers

**Created:** 2026-09-30
**Based on:** `docs/plans/plan-080-audience-and-authority.md` §3–§4;
`docs/plans/plan-081-t546-repair-verdicts.md` §1, §3–§4; `docs/plans/plan-082-root-refresh-and-followups.md`;
`docs/artifacts/command-audience-resolution-v1.md`.
**Scopes:** no new rows. **Corrects:** `T539` §5 (stale baseline), `T544` §4 (off-by-one history).

The user delegated four open decisions to the orchestrator on 2026-09-30 ("decide on your own which is
the best option"). Each is recorded here with its evidence and a condition under which it should be
revisited, so a later reader can overturn it on the record rather than by drift.

## 1. Decision 1 — do NOT demote `/discover-skills` or `/handoff`

**The choice was never P1 vs P2.** `plan-081` §1 measured that a P1 row naming a `stable` component
makes `check.py --maturity` exit 1 and blocks every merge. The real choice was: demote to
`experimental` and track at P1, or keep `stable` and track at P2.

**Decision: keep both `stable`; track at P2; repair on named triggers (§4).** Grounds:

1. **The ladder cannot evaluate the defect.** Both are target-audience defects — a path that exists in
   the authoring repo but is never installed. Every golden case runs against a fixture *inside*
   `tests/golden/`, i.e. inside the authoring repo; there is no installed-target fixture. Demoting
   would act on a criterion the ladder does not define and could not later confirm was cleared.
2. **The destructive member of the class is already fixed.** `/consolidate-memory` (T549, MR !419)
   was the one that lost user data. What remains degrades or misleads; it does not destroy.
3. **A demote-fix-repromote round trip costs more than the fix.** Re-promotion is a full criteria
   pass (T514, T522 showed the cost). Both repairs are decided (T546) and small.
4. **Nothing is hidden.** The defects are recorded in `command-audience-resolution-v1.md` §6,
   `plan-081` §3 and here.

**Revisit — and demote — if** either repair is not dispatched within two rounds of its trigger in §4
firing. A `stable` claim kept on the promise of a fix has to be kept honest by the fix actually coming.

**A fact that shaped the schedule:** the `/discover-skills` golden case's *load-bearing* assertion is
step 1 — every recommended skill must resolve against `fixture/implementation/registry/index.json`.
Repairing step 1 therefore *necessarily* supersedes what its checker asserts. It is a coupled
knowledge-plus-golden change needing a protected-path grant, not a writer's edit. The `/handoff`
repair is an installer change that leaves the command text — and so its case — untouched.

## 2. Decision 2 — batch dispatch, per contention group and owner

**Decision: yes.** One agent per contention group per round, carrying several tasks.

| Batch | Tasks | Owner | Why batching wins |
|---|---|---|---|
| golden | `T539`, `T544`, `T548` | QA Engineer | All three touch `tests/golden/**`. Separately: **three** evaluator-hash authorizations from the user, and three regenerations of `docs/benchmarks/scorecard-v6.12.0.*` — which `T539` and `T544` both require, so run in parallel they would **conflict** on that file. Batched: one of each. |
| knowledge | `T547`, `T551` | Technical Writer | Both touch `implementation/knowledge/`. Batched: one generator run, one registry update, one root-drift declaration. |
| install | `T550` | DevOps Engineer | Alone — it is the only task touching `scripts/install.sh`. |

`T538` (Tech Lead, knowledge) waits for the knowledge batch.

**Mechanics.** Rows stay separate: each task keeps its brief, acceptance criteria and archival. One
branch per batch, `agent/<agent>/<lowest-task-id>`, one MR naming every task. The agent holds the
**union of its tasks' grants and nothing more**, and may not use one task's grant for another task's
path. This is multi-task dispatch, **not** the `/batch` command, which is `experimental`.

**Revisit if** a batch hand-back arrives with one task's findings contaminating another's, or its
review becomes too large to verify thoroughly — the reason tasks are separate in the first place.

## 3. Decision 3 — no standing-debt register; parked work lives in plans, with triggers

**Decision: no new file.** A second place to look is a second place to forget. `plan-081` §3 already
showed the working pattern; this formalises it:

- a finding that is decided but not yet worth a row is **parked** in the plan that decided it;
- every parked item names a **trigger** — the event that makes it dispatchable;
- the orchestrator opens a row **when the trigger fires**, not before;
- **every checkpoint enumerates every parked item**, so none depends on someone choosing to read an
  old plan. That is the failure `plan-081` §4 predicted for an ad-hoc register.

It keeps the queue honest: rows mean *dispatchable now*, and the plan-coverage guard
(`test_every_active_task_has_a_plan`) still ties every row to a plan.

**Revisit if** a checkpoint is written without the parked list, or a trigger fires and nothing is
opened.

## 4. The parked set, with triggers

| # | Item | Decided in | Trigger |
|---|---|---|---|
| P1 | `/handoff`: one `install_tree_into` line so `implementation/runtime/handoff/` is installed | `command-audience-resolution-v1.md` §6 | `T550` merged — same file, `scripts/install.sh` |
| P2 | `/discover-skills`: repath step 1 and `## Rails` Inputs; **re-derive its golden checker** under a protected-path grant | same, §6; §1 above | golden batch merged and its baseline authorized — avoids hash contention |
| P3 | `new-project-plan-doc-and-lifecycle-states/brief.md` quotes `/new-project` step 1 verbatim, including the `04-protocols.md` line `T547` will change | this plan | `T547` merged — fold into P2's grant, one baseline instead of two |
| P4 | `.<platform>/skills/local/` carve-out giving a target a durable skill home (Option C) | same, §7 | `T550` merged, **and** vendor clients confirmed to walk `skills/local/*/SKILL.md` recursively |
| P5 | Implement the `audience:` key: one schema edit plus 19 frontmatter lines, one atomic commit | same, §3–§5 | a round with no open `implementation/knowledge/` task — it touches all 19 commands |
| P6 | `/prepare-release` declared `audience: authoring` | same, §6 | P5 merged |
| P7 | A seventh `_replace_one` rewriting `AGENTS.md` bullet 2's generator paths per target | `T545` hand-back | any `render_installed_agents.py` task |
| P8 | Seven manifests declare `"$schema": "./_manifest.schema.json"`, which does not exist | `T546` hand-back | any `implementation/platforms/` task |

## 5. Decision 4 — `protected-paths-v1.md` stays edited in place; no `-v2`

T545 corrected §6 in place: a stale count (27 → 28 agents), a false claim that `.cline/` carries the
pointer, and a wrong generator. `AGENTS.md` says revisions create new versions.

**Decision: keep it in place.** `coding-standards.md` draws the line itself: "Typo or formatting fixes do
NOT require a new version" and "Adding new sections or modifying conclusions DOES require a new
version." §6 is a descriptive *Verification* section; no conclusion changed and no section was added.

**The same file also says "Any material change to an artifact's content requires a new version", and
that cuts against this decision — it is addressed rather than omitted.** The judgment is that
correcting a false *description of how the policy is verified* is not material to the *policy*: no
grant, rule or permitted action moved. A reader who holds that any factual correction is material has a
fair point, and the revisit condition below is where that disagreement should be settled. The rule exists to stop decision
records being silently rewritten, and nothing was. A `-v2` would orphan the many live citations of
"`protected-paths-v1.md` §5" across task briefs or force a migration — cost with no protective benefit.

**The precedent this sets, stated narrowly:** a factual correction to a descriptive section of a live
policy artifact may be made in place, **disclosed in the commit**. Any change to a rule, a grant, a
conclusion or a section's meaning still requires a new version.

**Revisit if** an in-place edit is ever used to change what a policy *permits*.

## 6. Two brief corrections, made in this MR

- **`T539` §5 compared against `evaluator-hash-known-good-v7.json` — two baselines stale.** It was
  missed during the v9 refresh because the sweep then looked for `v8`. Now `v9`.
- **`T544` §4 said `v7`'s `reason` field names the batch case.** Checked: `v7` has 0 matches, `v8`
  has 1 (T541's refresh). Now `v8`.

## 7. Next round, once !420 and !421 merge

1. Archive `T543`.
2. Dispatch in parallel — file sets verified disjoint: **`T550`** (`scripts/install.sh`, new tests),
   the **golden batch** (`tests/golden/**`, `docs/benchmarks/`), the **knowledge batch**
   (`implementation/knowledge/`, projections, registry, `tests/_baselines/root-install-drift.json`).
3. Golden-batch pre-check already done: `T547`'s edits touch no golden **checker** — only P3's
   `brief.md` quotes the affected line.
4. When the golden batch hands back: **one** v10 baseline authorization request to the user.
