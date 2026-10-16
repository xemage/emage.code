# plan-064 — Roadmap to v8.0.0: breadth, distribution, and loop utility

**Author:** top-level session (planning only — no task briefs opened, no implementation dispatched)
**Date:** 2026-09-19
**Status:** proposed — not approved for task-brief authoring or execution
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` (the v7 roadmap this succeeds),
`docs/plans/plan-054-codex-platform-integration-post-v7.md` (Codex state capture),
`docs/releases/v7.0.1.md`, `docs/checkpoints/checkpoint-release-v7.0.1.md`,
`docs/artifacts/phase3-wave1-promotion-v1.md` / `phase3-wave2-promotion-v1.md`,
`docs/decisions/ADR-004-tb-inconclusive-guardrail-demotion.md`,
`docs/artifacts/t507-closed-loop-cycle-v1.md`, `docs/tasks/completed-tasks.md` (T512/T513).

Every number in Part 1 was verified directly against the repository at `develop`
(`45eecfd`, 2026-09-19), not recalled or estimated.

> **Amended 2026-09-23 — read the "Decisions (2026-09-23)" section before the phase specs.** Four
> decisions (D1–D4) are now settled and the body has been updated to match rather than left to
> contradict them:
> **D1** Codex (Phase 7) is deferred on its external CLI prerequisite — and, as a direct
> consequence, Gate G5 is removed from the v8.0.0 release condition so the roadmap is not silently
> blocked on a CLI install.
> **D2** Execution order is Phase 10 → 9 → 8 → 11, sequential.
> **D3** Intermediate minors get cut for real this time.
> **D4** The v8.0.0 *number* is not pre-committed — the line is cut when G6+G7+G8 close, and the
> major version is awarded only if the work genuinely earns it. The title of this document is
> therefore aspirational, not a commitment.

---

## Part 1 — Where v7.0.1 actually leaves us

v7.0 set out to take the project from *"an architecturally sophisticated system that describes
itself as beta"* to *"a system whose components carry earned maturity claims, whose documentation
is true, and which remembers what it learned."* It delivered that. But it delivered it **narrowly**,
and the narrowness is now the most interesting thing about the current state.

### 1.1 The claims are checkable. They are not broad.

| Category | Stable | Experimental | Total | Stable % |
|---|---:|---:|---:|---:|
| Agents | 20 | 8 | 28 | 71% |
| **Commands** | **0** | **19** | **19** | **0%** |
| Instructions | 4 | 2 | 6 | 67% |
| Skills | 7 | 19 | 26 | 27% |
| **Total** | **31** | **48** | **79** | **39%** |

**Not one of this project's 19 user-facing commands is `stable`.** Commands are the surface users
actually touch (`/new-project`, `/plan`, `/code-review`, `/prepare-release`…) — and they are the
one category the maturity ladder never reached. This is not an oversight; it is a documented,
tracked blocker (`phase3-wave2-promotion-v1.md` §4, Blocker 1) that Phase 3 correctly declined to
force.

### 1.2 The reason commands are stuck, precisely

`maturity-promotion-criteria-v1.md` §3.2.4 requires ≥1 golden case naming the command. Real state
of `tests/golden/` today — 14 `open` cases + 6 `held-out`, covering **5 of 19 commands**:

- **14 of 19 commands have zero golden coverage of any kind** (`batch`, `bug-report`,
  `consolidate-memory`, `discover-skills`, `evaluate-poc`, `handoff`, `new-poc`, `new-project`,
  `poc-demo`, `skillify`, `sprint-status`, `team-status`, `validate-tasks`, `validate-workflow`).
  Authoring cases for them requires a disclosed `protected-paths-v1.md` §5 exception, since
  `tests/golden/**` is a protected path.
- **The 5 commands that do have coverage each carry a `known_failing` case**, which is what blocks
  them rather than missing evidence:

  | Case | Command | Category |
  |---|---|---|
  | `new-feature-real-checkpoint-format-drift` | `/new-feature` | `tracked_defect` |
  | `plan-real-doc-header-drift` | `/plan` | `tracked_defect` |
  | `prepare-release-real-verdict-missing` | `/prepare-release` | `tracked_defect` |
  | `security-audit-critical-not-fail` | `/security-audit` | `tracked_defect` |
  | `code-review-conditional-pass-conditions-gap` | `/code-review` | `capability_gap` |
  | `prepare-release-conditional-pass-conditions-gap` | `/prepare-release` | `capability_gap` |

  Four are **real product defects** awaiting a fix. Two are **capability gaps** awaiting a decision
  (fix the capability, or re-classify honestly). Notably, those two `capability_gap` cases are
  exactly the cluster `T507`'s closed-loop cycle independently selected as its top improvement
  target — see §1.5.

### 1.3 Four agents are already unblocked and nobody has noticed

`phase3-wave2-promotion-v1.md` records that `context-retriever`, `devops-engineer`,
`evaluation-agent`, and `solution-architect` were blocked from `stable` **solely** by
`check-maturity.py`'s self-referential ledger-defect rule firing on open P0/P1 tasks `T456`/`T457`
naming them. Both tasks closed on 2026-09-17. **That blocker is structurally gone**, and no
promotion-readiness pass has been re-run since. This is very likely four `stable` promotions
available today for the cost of re-running an existing evaluation — no new evidence authoring.

### 1.4 The distribution surface is the weakest part of the system

`T513` (shipped in v7.0.1, this week) found that `scripts/install.sh` had **never** shipped the
Python runtime source that two of this project's own MCP servers (`@context-retriever`,
`security-audit`) import. Both were declared in every target project's generated MCP config and
were structurally incapable of starting anywhere except inside this source repository. A real
downstream project (CWSO) had no `implementation/` directory at all. Three independent gaps
compounded: missing runtime source, an undeclared-at-install-time pip dependency, and an
unbuilt per-project index.

That is not a small bug. Two shipped, documented, maturity-tracked features did not work for any
user, and nothing in the test suite, the sync gate, the maturity checker, or the release gate
caught it — because every one of those checks validates the *source repository*, and none validate
*what a target project actually receives*. v7.0.1 fixed the immediate breakage and surfaced the
prerequisites; it did not close the structural gap that allowed it.

One disclosed, unscoped finding from the same investigation remains open: `servers.yaml` hardcodes
`@context-retriever`'s index directory as `em-age-emage.code` for **every** target project,
including CWSO. It does not break connectivity, but it is semantically wrong for any project other
than this one.

### 1.5 The closed loop works mechanically. It has never produced value.

Phase 6 built the full pipeline and `T507` ran it for real: a genuine failure cluster, a genuine
`@meta-improver` proposal, genuine scores, a genuine `promote=True`, a genuine merge request. The
human gate then correctly **rejected** it — the "improvement" was an artifact of thin evidence and
a provenance-confounded comparison, not the proposal's content. `T509`–`T511` then closed that
failure mode with three independent, tested controls.

So the loop is now demonstrably safe. It is not yet demonstrably *useful*: Phase 6's own acceptance
criteria **AC2** ("improvement is measurable on the held-out suite") and **AC5** ("lineage document
exists for every accepted change") remain genuinely open, because no change has ever been accepted.
`checkpoint-035` states this plainly and declines to round it up.

There is a non-obvious reason to expect this to stay true without further work: **the loop mines
the golden suite for failure clusters, and the golden suite covers 5 of 19 commands.** `T507`'s
only viable multi-member cluster was those two `capability_gap` cases from §1.2. The loop is
starved of material, and the fix for that starvation is exactly the command-coverage work in §1.2.

### 1.6 Terminal-Bench is a guardrail, not a signal

`ADR-004` (accepted) records that `T407`'s two-arm delta came back **Inconclusive** (Arm A spread
8.0pp, landing exactly on the pre-registered threshold; aggregate delta −1.33pp) and was treated as
Null-equivalent: Terminal-Bench demoted from improvement signal to no-harm guardrail, with the
golden suite remaining the sole load-bearing signal. This is honest and was correctly pre-committed
— but it means the *only* real measurement surface this project has is the one covering 5 of 19
commands.

### 1.7 Codex: real work, one external blocker, and growing drift

`feature/T475-codex-platform-integration` is a genuine eighth-platform implementation (228 files,
14,319 insertions), with an approved design (`plan-036`), an accepted ADR (`ADR-003`), six of eight
tasks `done`, and a full passing static/projection/installer/secret-guard bar as of 2026-09-01.

It is blocked on exactly one thing, unchanged since then: **`T481` needs a live trusted-project
smoke test against a real Codex CLI host**, and no `codex` executable has ever been available on
this machine. That is an environmental prerequisite, not a code defect.

Meanwhile the drift compounds, and faster than a calendar would suggest. `plan-054` recorded **227
commits behind `develop`** on 2026-09-18. Verified today, one day later: **301 commits behind** —
74 commits of divergence added in a single active working day. The branch is now safely mirrored on
`origin` (pushed this session as a plain backup, no content change), so it is no longer a
single-disk risk — but deferral is measured in sessions, not weeks, and each one raises the
re-application cost against a projection surface that has itself moved (577 generated files across
7 platforms, 19 registered MCP servers, several of which post-date the fork and which the Codex
TOML branch has never once been exercised against).

> **Correction to `plan-054`, verified today:** that plan states `develop` has "23 registered MCP
> servers" and then enumerates 19 names followed by "plus others." A direct parse of
> `implementation/knowledge/mcp/servers.yaml` returns **19** — exactly the names it listed, with no
> others. The substance of `plan-054`'s argument is unaffected (several of the 19 do post-date the
> Codex fork), but the figure itself was wrong and is corrected here rather than inherited.

### 1.8 Summary of the honest position

v7.0 built the instruments. The next line has to point them at the whole surface, make sure what
ships actually arrives, and find out whether the loop is worth having.

*(Amended 2026-09-23: this originally read "v8.0 has to…". Per D4 the version number is earned at
Phase 8's close rather than assumed, so the sentence no longer asserts one.)*

---

## Part 2 — The roadmap

### 2.0 Goal

**v8.0.0: the maturity claims cover the surface users actually touch, what the installer promises
is what a target project actually receives, and the closed loop has been given a real chance to
prove itself — or has honestly failed to.**

Three pillars, in the order the evidence argues for. **Amended 2026-09-23 per D1** — pillar 1
originally led with Codex as the eighth platform; with Phase 7 deferred, what remains of that
pillar is the distribution surface itself, which turns out to be the part that was load-bearing
anyway:

1. **Trustworthy distribution** — what the installer promises is what a target project actually
   receives, gated by a check that validates the *delivered* artifact rather than the source repo.
   (Codex, the eighth platform, was the original headline here and is deferred per D1 — but it was
   always going to arrive *through* this surface, and `T513` showed the surface was the weaker of
   the two.)
2. **Breadth of evidence** — commands from 0 `stable` to a real, earned number; the four agents
   already unblocked.
3. **Utility of the loop** — Phase 6's unfinished AC2/AC5, attempted against a golden suite that
   Phase 9 will have made materially richer.

### 2.1 Anchoring principle

Same as `plan-035` §2.1: anchored to **releases**, not months.

One correction carried forward from v7's own execution, though. `plan-035` mapped each phase to an
intermediate version (v6.11 … v6.17) and **not one of those intermediate versions was ever
tagged** — everything landed as a single v7.0.0 covering 74 tasks. That bundling worked, but it
meant the first real external validation of ~5 months of work happened all at once.

**Decided (D3): the intermediate minors get cut for real this time** (§2.4's version column), and
the v8.0.0 line is the point where its gates close rather than a container for everything. Per D4,
whether that line actually carries the major number is a semver judgement made at Phase 8's close,
not a commitment made here.

### 2.2 Non-negotiable gates

Each gate is a precondition, not a milestone. Work in a later phase must not begin until the
preceding gate is closed.

| Gate | Statement | Why |
|---|---|---|
| **G5 — Projection integrity** *(no longer a v8.0.0 release condition — see D1)* | No new platform ships until its projection is verified against the *current* knowledge corpus, not the corpus its design was written against. | The Codex branch's generation logic has never been exercised against `develop`'s 19 MCP servers or 79 components. A projection that was correct for a 2026-09-01 corpus is an assumption, not a fact, about today's. **Still fully binding on Phase 7 whenever it runs** — D1 removes it from v8.0.0's own release condition, it does not weaken the gate. |
| **G6 — Command evidence** | No command reaches `stable` without ≥1 golden case that can actually fail it. | This is G1 ("no component promoted out of beta until an *outcome* eval exists that can fail it") applied to the one category that never received it. A command promoted on documentation evidence alone is a rename. |
| **G7 — Distribution correctness** | No feature ships whose runtime prerequisites the installer neither delivers nor discloses, and no release gate passes without validating what a *target project* receives — not only what the source repo contains. | Directly from `T513`: two shipped, maturity-tracked features were non-functional for every user, and every existing gate validated the wrong artifact. |
| **G8 — Loop utility** | The closed loop is not described as working until it has produced at least one accepted change with a real lineage document — **or** a written, evidence-backed statement of why it cannot. | Phase 6's AC2/AC5. The disjunction is load-bearing: without it, G8 becomes pressure to manufacture a passing result, which is precisely the failure `T507`–`T511` spent four tasks preventing. |

### 2.3 Phase graph

**Revised per D1/D2 (2026-09-23).** Phase 7 is deferred out of the v8.0.0 line; execution is
sequential, not parallel, because this is one maintainer's attention (`plan-035`'s own Resolved
Decision 2 applies unchanged).

```
  ①            ②                  ③                    ④
Phase 10  →  Phase 9  ────────→  Phase 8   ────────→  Phase 11
(agents)     (commands)          (distribution)       (loop utility)
  no gate      G6                  G7                   G8
                └──────────── depends on ───────────────┘

                    v8.0.0 cut when G6 + G7 + G8 close

Phase 7 (Codex) ── G5 ── DEFERRED, gated on an external prerequisite
                         (a working Codex CLI host). Not in the v8.0.0
                         line. Re-entry condition and consequences: D1.
```

Dependencies that are real and non-obvious:

- **Phase 11 after Phase 9.** The loop mines the golden suite for failure clusters. Today that is
  20 cases across 5 commands, and `T507` could find exactly one viable multi-member cluster. Phase 9
  roughly doubles the suite and quadruples its command coverage. Running the loop before that is
  running it starved.
- **Phase 8 is no longer downstream of Phase 7.** The original graph sequenced it after Codex,
  because adding an eighth platform changes the installer surface. With Phase 7 deferred that
  dependency dissolves, and the ordering inverts usefully: Phase 8 now lands *before* any future
  platform addition, so Codex arrives into an installer whose delivery correctness is already gated
  rather than one being fixed around it.

### 2.4 Phase specifications

#### Phase 7 — Codex, the eighth platform (DEFERRED — version TBD, after v8.0.0)

**Status: DEFERRED (2026-09-23, per D1) — gated on an external prerequisite, not on this
roadmap's own progress. Not approved for task-brief authoring or execution.**

**Re-entry condition:** a working Codex CLI host is available, *or* the user explicitly accepts the
narrowed-validation fallback described in this phase's third task. Until one of those holds, this
phase does not start — `plan-054` remains its durable home, and the branch stays mirrored on
`origin` where it is safe from disk loss.

**Goal (unchanged):** ship Codex as a fully supported eighth platform, on whatever `develop` looks
like at the time, with its projection verified against the corpus current at that point.

> **What the deferral actually costs — recorded so it is not rediscovered later (D1).** `plan-054`
> §1 offers two integration paths: **(a)** cherry-pick the two Codex commits and resolve conflicts,
> or **(b)** treat `plan-036`/`ADR-003` as authoritative and re-implement fresh. Drift was already
> 301 commits on 2026-09-19, growing ~74 per active working day. Deferring on an open-ended
> external prerequisite means path (a) should be assumed **forfeit** by the time this resumes — the
> literal diff will have decayed past useful conflict resolution. Path (b) is the realistic plan.
>
> That is less alarming than it sounds, and it is the reason this deferral is low-risk rather than
> merely tolerable: **`plan-036` and `ADR-003` do not rot.** The design contract, the safety
> constraints (never write global Codex config, never emit credentials, never set project
> model/approval defaults), and the projection shape are all platform-agnostic and independent of
> how much `develop` moves. The durable asset was always the design, not the patch. Whoever resumes
> this should budget for a re-implementation against a current corpus and treat the stale branch as
> a detailed reference, not a starting point.

| ID | Task | Owner agent | Scope |
|---|---|---|---|
| — | Re-application spike: attempt the cherry-pick of both Codex commits onto current `develop`, measure the real conflict surface, and decide **(a) cherry-pick-and-resolve vs (b) re-implement from `plan-036`/`ADR-003`** on evidence. `plan-054` §1 is explicit that this decision must follow an actual attempt, not precede it. | backend-developer | medium |
| — | Re-validate the Codex projection against the **current** corpus: 19 MCP servers (several post-dating the fork — `hindsight`, `cwso`, `context-retriever`, `security-audit`), 79 registry components, 577→~660 generated files. Confirm `emitMcp()`'s Codex/TOML branch produces correct output for every registered server, not just the set that existed in 2026-09-01. | backend-developer | large |
| — | **Resolve `T481`'s external blocker explicitly, before the phase proceeds past re-validation.** Either acquire a working Codex CLI host (`@openai/codex-linux-x64` or equivalent), or make an explicit, recorded decision to accept a narrowed validation (structural/TOML-parsing only) with the interactive trusted-project smoke test tracked as a disclosed, named follow-up. Not discovered mid-phase — decided at phase start. | tech-lead | medium |
| — | Re-open `T481`/`T482` as fresh, re-scoped tasks. Do **not** mark them `done` on 2026-09-01 evidence; the surface they validate has moved. | orchestrator | small |
| — | Root self-install refresh for the eighth platform + release/checkpoint closeout. | release-manager | medium |

**Acceptance criteria**
- [ ] `sync.mjs --check` reports zero drift across all **8** platforms
- [ ] Every one of the 19 registered MCP servers appears correctly in the generated Codex config
- [ ] No write path to global Codex configuration (`~/.codex`/`$CODEX_HOME`) — `ADR-003`'s constraint, re-verified against current code, not inherited from the 2026-09-01 test run
- [ ] `T481`'s validation scope is a recorded decision with a named owner, not an open question
- [ ] Full bar fresh on current `develop`: `tests/run.py`, `check-maturity.py`, `validate-tasks.py`, `verify-release-docs.py`

> **Gate G5 closes here.**

#### Phase 8 — Distribution correctness (③ in execution order — v7.3.0, or v8.0.0 if breaking; see D4)

**Status: proposed — not approved for task-brief authoring or execution.**

**Goal:** make "what the installer promises" and "what a target project receives" the same thing,
structurally rather than by notice.

| ID | Task | Owner agent | Scope |
|---|---|---|---|
| — | **Target-project validation gate.** A real test that installs into a throwaway target and asserts the declared capabilities actually function there — the check class that would have caught `T513` at authoring time instead of two releases later. This is the phase's centrepiece. | qa-engineer | large |
| — | Decide and implement the runtime-distribution model: does a target project carry `implementation/runtime/` source (today's `T513` fix), or do these servers ship as installable packages? `T513` chose the former as the minimal correct fix under time pressure and explicitly did not settle the design question. | solution-architect | medium |
| — | Fix `servers.yaml`'s hardcoded per-project index directory (`em-age-emage.code` emitted for every target). Requires a templating mechanism for per-target values in generated MCP args — none exists today (`${env:…}` covers env vars only). Disclosed, unscoped finding from `T513`. | backend-developer | medium |
| — | **Containerised installer / package-manager distribution** — `plan-035` §2.7 deferred this behind "after Phase 3"; that condition is now met (see §2.5). Sequenced here because it is the same surface. | devops-engineer | large |

**Acceptance criteria**
- [ ] A fresh install into a throwaway target is validated end-to-end by CI, not by hand
- [ ] Every MCP server declared in a target's generated config either runs there or is explicitly, machine-checkably marked as requiring a disclosed prerequisite
- [ ] No generated config contains a value hardcoded to this repository's own identity
- [ ] `T513`'s exact failure mode has a regression test that fails if the runtime source stops shipping

> **Gate G7 closes here.**

#### Phase 9 — Command maturity (② in execution order — v7.2.0)

**Status: proposed — not approved for task-brief authoring or execution.**

**Goal:** close the 0-of-19 gap honestly — promote what the evidence earns, fix what it exposes,
and demote or re-classify what neither.

| ID | Task | Owner agent | Scope |
|---|---|---|---|
| — | Request and record the `protected-paths-v1.md` §5 exception for `tests/golden/open/**` additions, via a named, authorized task brief that explicitly invokes it. | orchestrator | small |
| — | Author 14 genuinely representative golden cases — one per uncovered command — with the same rigor `tests/golden/README.md` applies to the existing suite. **`plan-035` §2.6's own risk applies directly here** ("golden suite authored too easy, baseline reads 20/20"): `T411`'s ≥5-known-failing discipline and `T414`'s reject-a-perfect-baseline rule must both be applied to this batch. | qa-engineer | large |
| — | Fix the 4 real `tracked_defect`s blocking the covered commands (`/new-feature` checkpoint-format drift, `/plan` doc-header drift, `/prepare-release` verdict-missing, `/security-audit` critical-not-fail). | backend-developer | large |
| — | Decide the 2 `capability_gap` cases (`/code-review` and `/prepare-release` conditional-pass conditions): implement the capability, or re-classify with recorded reasoning. Note these are the same cluster `T507` targeted — coordinate with Phase 11. | tech-lead | medium |
| — | Re-run promotion readiness across all 19 commands; promote what qualifies, and record what still does not and why. | product-owner | medium |

**Acceptance criteria**
- [ ] All 19 commands have ≥1 golden case naming them
- [ ] The new batch contains ≥5 genuinely known-failing cases and the aggregate baseline is not perfect
- [ ] Every command is either `stable` with real evidence, or `experimental` with a named, tracked reason
- [ ] No command promoted while a `tracked_defect` case against it is open

> **Gate G6 closes here.**

#### Phase 10 — Agent promotion re-run (① in execution order — v7.1.0)

**Status: proposed — not approved for task-brief authoring or execution.**
**Sequencing: cheapest item on this roadmap, no dependencies — confirmed first per D2.**

**Goal:** collect the promotions already earned but never claimed.

| ID | Task | Owner agent | Scope |
|---|---|---|---|
| — | Re-run promotion readiness for the 4 agents blocked *solely* by `T456`/`T457` (`context-retriever`, `devops-engineer`, `evaluation-agent`, `solution-architect`), both tasks now closed. Promote what qualifies. | product-owner | small |
| — | Re-assess the remaining 4 experimental agents (`backend-developer`, `orchestrator`, `security-engineer`, `tech-lead`) and record each one's actual blocker. | product-owner | medium |

**Acceptance criteria**
- [ ] Each of the 8 experimental agents is either promoted or has a current, named blocker — none left merely un-re-evaluated
- [ ] No promotion granted on the strength of the stale Phase 3 evidence alone without a fresh `check-maturity.py` confirmation

#### Phase 11 — Loop utility (④ in execution order — closes the v8.0.0 line; see D4 on the number)

**Status: proposed — not approved for task-brief authoring or execution.**
**Depends on: Phase 9 (the loop needs the richer suite to have material to mine).**

**Goal:** answer the question Phase 6 deliberately left open — is the closed loop worth having?

| ID | Task | Owner agent | Scope |
|---|---|---|---|
| — | Re-run the hardened loop end-to-end against the post-Phase-9 golden suite, at the evidence depth `T510`'s gate now requires (k≥3 per arm per case, homogeneous provenance). Repeat across multiple clusters if the first produces nothing. | orchestrator | large |
| — | If a proposal genuinely promotes and survives human review: merge it, and author the first real `docs/harness-lineage/harness-v1.md` — closing AC5 for real. | release-manager | medium |
| — | If nothing promotes after a genuine, documented effort: publish an evidence-backed statement of **why**, with the measured data. This is a passing outcome for G8, not a failure. | evaluation-agent | medium |
| — | Re-measure held-out-suite improvement (AC2) against the published baseline either way. | evaluation-agent | medium |

**Acceptance criteria**
- [ ] The loop has been run against the enlarged suite with real, recorded trial data at the required evidence depth
- [ ] Either a real accepted change with a real lineage document exists, **or** a published, evidence-backed account of why the loop cannot yet produce one
- [ ] AC2 is answered with a measurement, not left open
- [ ] No result manufactured to satisfy this gate — the `T507` disclosure discipline applies unchanged

> **Gate G8 closes here. The v8.0.0 line is cut when G6, G7, and G8 have all closed** — G5 was
> removed from this set by D1 along with Phase 7. Whether the resulting release actually carries the
> major number is decided on semver grounds at Phase 8's close, not assumed here (D4).

### 2.5 Deferred items whose re-entry conditions are now met

`plan-035` §2.7 deferred twelve items behind explicit re-entry conditions. Re-checked today,
**exactly two have earned re-entry**, and both are folded into Phase 8:

| Item | Re-entry condition | Status |
|---|---|---|
| Containerised installer / Homebrew / npm / pip / Go | "After Phase 3" | ✅ **Met** — Phase 3 closed 2026-09-11 (`checkpoint-032`). Folded into Phase 8, where it shares a surface with the `T513` distribution work. |
| Native IDE plugins | "After Phase 3 — plugins are thin clients over a canonical surface, and that surface must be stable first" | ⚠️ **Technically met, deliberately still deferred.** Phase 3 is closed, but the condition's *reason* is not satisfied: the canonical surface users touch is commands, and 0 of 19 are stable. Re-evaluate after Gate G6. |

The other ten remain correctly deferred; §2.7 below records the two whose status changed
meaningfully.

### 2.6 Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Codex drift makes the branch unusable as a patch** | **Certain** (accepted, per D1) | Medium | No longer mitigated — *accepted*. D1 defers Phase 7 on an open-ended external prerequisite, which forfeits `plan-054`'s path (a) cherry-pick by design. Mitigation is that the durable asset is `plan-036`/`ADR-003`, which do not decay; the branch is mirrored on `origin` and becomes a reference, not a starting point. Impact drops from High to Medium precisely *because* the deferral was made explicitly rather than by drift. |
| `T481`'s Codex-host blocker is never resolved | **High** | Low (was Medium) | D1 removed Phase 7 and G5 from the v8.0.0 line, so this can no longer block the roadmap — only the eighth platform itself. If it stays unresolved indefinitely, the decision to make is whether to ship Codex on the narrowed validation, and that decision has no deadline attached to it now. |
| 14 new golden cases authored too easy → baseline reads perfect | **High** | **Critical** | `plan-035` §2.6's own named risk. `T411`'s ≥5-known-failing rule and `T414`'s perfect-baseline rejection are carried into Phase 9's acceptance criteria explicitly, not assumed. |
| The loop still produces nothing after Phase 9 | Medium | Medium | G8 accepts an evidence-backed negative as passing. Without that disjunction the gate becomes pressure to fake a result — the exact failure `T507`–`T511` prevented. |
| Protected-path exception becomes a habit | Medium | High | Phase 9's exception is scoped to `tests/golden/open/**` additions via one named, authorized task. The three-control model (`T412` path guard, `T504` evaluator hash, `T416` write-scope exclusion) is unchanged; held-out remains untouched. |
| Distribution fix breaks existing installs | Medium | High | Phase 8's target-project validation gate lands **before** the runtime-distribution model changes, so the change is validated by the very mechanism that would have caught `T513`. |
| A major version bump with no breaking change | Medium | Low | **Resolved by D4**: the release is cut when G6+G7+G8 close, and the major number is awarded only if Phase 8's distribution-model change is genuinely breaking. If nothing in the set breaks, it ships as v7.x and v8.0.0 waits for something that earns it. |
| **The roadmap's own title pressures the version number** | Medium | Medium | A document called "roadmap to v8.0.0" creates quiet pressure to produce a v8.0.0 regardless of what the work earns. D4 is the explicit counterweight, and this row exists so the pressure is named rather than left to operate unnoticed. |

### 2.7 Still deferred — with unchanged or updated conditions

| Item | Re-entry condition | Change since `plan-035` |
|---|---|---|
| SWE-bench Verified integration | After the Terminal-Bench delta is stable | **Condition moved further away.** `ADR-004` demoted Terminal-Bench to a no-harm guardrail after an Inconclusive result; there is no stable delta to build on. Revisit only if the golden suite's own signal justifies a second benchmark. |
| Terminal-Bench leaderboard submission | After the registry has left beta | Still unmet — 39% stable. Phase 9 moves this materially; re-check after G6. |
| GRPO / LoRA fine-tuning at scale | After Gate G4 and sustained trajectory volume | G4's preconditions hold, but trajectory volume does not, and `T500`'s audit found the RL subsystem this depends on architecturally unrelated to what Phase 6 actually built. Effectively superseded. |
| `emage.dev` registry, Enterprise edition, academic program | External adoption thresholds | Unchanged — no external contributions yet. |
| K8s operator / CRDs, live collaboration, sparse-photonic | After CWSO 1.0 / a second concurrent user | Unchanged. CWSO 1.0 (`plan-035` §2.5 Track C) remains a separate repo on a parallel track, untouched by this roadmap and not a v8.0.0 blocker. |
| SIA/CWSO RL subsystem revival | `plan-035` §2.7 | Still unresolved, carried in every checkpoint since `checkpoint-034`. `T500`'s audit stands: Phase 6 did not need it, and nothing since has changed that. |

### 2.8 Recommended first steps

**Revised 2026-09-23 per D1/D2** — the original Step 2 was Phase 7's re-application spike, which
D1 defers.

**Step 1 — Phase 10 (agent re-run).** Cheapest item on the roadmap, no dependencies, and it
converts already-earned evidence into claimed status. Likely a single task.

**Step 2 — Phase 9's protected-path exception request and the first two or three golden cases.**
Start the longest pole early and at low volume, so the "are these cases genuinely hard enough"
question gets answered on a small batch rather than on all 14 at once. Phase 9 is both the largest
body of work and the one Phase 11 is blocked behind, so it is the critical path — starting it
second is the whole reason Phase 8 sits third rather than second.

**Step 3 — Phase 8's target-project validation gate**, specifically: the test that installs into a
throwaway target and asserts the declared capabilities actually function there. Even taken alone,
ahead of the rest of Phase 8, this is the single highest-value check on the roadmap — it is the
class of test that would have caught `T513` at authoring time instead of two releases later.

Everything else waits on those three.

---

## Approval

**Nothing in this document is approved for task-brief authoring or execution.** It is a planning
and state-capture document, following the same Plan-Approve-Execute discipline every phase boundary
in the v7 roadmap used: the plan is reviewed first, phases are approved individually, and task
briefs are authored only after a phase is explicitly approved.

## Decisions (2026-09-23)

The two decisions this plan put to the user, and the two open questions behind them, are now
settled. **D1 is the user's own decision**; D2–D4 were explicitly delegated ("Regarding the other
points decide on your own") and are recorded here with their reasoning so a later reader can
disagree with the argument rather than guess at it.

### D1 — Codex (Phase 7) is deferred *(user's decision)*

> *"Not sure about Codex CLI availability. Put that task at a later date."*

Phase 7 is deferred, gated on the external prerequisite that has blocked it since 2026-09-01: a
working Codex CLI host, or an explicit acceptance of the narrowed-validation fallback.

**This forced a structural consequence that is worth stating plainly, because it was not obvious
when the roadmap was drafted:** Phase 7 was the only phase behind **Gate G5**, and the original
§2.4 made v8.0.0 conditional on *G5 + G6 + G7 + G8*. Deferring Phase 7 on an open-ended external
prerequisite would therefore have made **v8.0.0 itself unreachable indefinitely** — the roadmap
would have been silently blocked on a CLI install. Rather than leave that landmine, G5 and Phase 7
are removed from the v8.0.0 line entirely: **v8.0.0 is now cut when G6, G7, and G8 close.** G5 is
not weakened — it remains fully binding on Phase 7 whenever that phase runs. It simply no longer
gates a release it has nothing to do with.

The cost of deferral (path (a) cherry-pick forfeit, path (b) re-implementation from the
non-rotting design docs) is recorded in Phase 7's own section.

### D2 — Execution order: Phase 10 → Phase 9 → Phase 8 → Phase 11

**Sequential, not parallel.** `plan-035`'s own Resolved Decision 2 applies unchanged: this is a
single maintainer's attention, and parallel tracks compete rather than compound.

- **Phase 10 first** because it is the only item measured in days rather than weeks, and it
  converts evidence already earned into status already deserved. Starting a roadmap with a genuine
  completed increment is worth more than the increment itself.
- **Phase 9 second** because it is the critical path. Phase 11 is blocked behind it, and Phase
  9 + Phase 11 is the longest chain to the v8.0.0 line — standard practice is to start the longest
  chain earliest. It is also the largest single body of work on the roadmap, so it needs the most
  runway.
- **Phase 8 third.** With Phase 7 deferred it has no upstream dependency left, so its position is
  free. Third is the best of the available slots: it does not delay the critical path, and it lets
  Phase 9's 14 new golden cases settle before Phase 11 mines them — fresh cases are exactly the
  ones most likely to need iteration, and the loop should not be reading a suite that is still
  moving.
- **Phase 11 last**, as the final gate, against the enlarged and settled suite.

### D3 — Cut the intermediate minors for real this time

v7 planned v6.11–v6.17 and tagged **none of them**; 74 tasks shipped as one v7.0.0. Repeating that
is rejected, on evidence gathered this week rather than on principle:

- **The release machinery demonstrably works and is cheap.** v7.0.0 and v7.0.1 were both cut
  cleanly within minutes, including a real drift-gate failure that was caught and resolved both
  times. The overhead argument against intermediate releases does not survive contact with the
  actual measured cost.
- **`T513` is the counter-example for bundling.** Two shipped, maturity-tracked features were
  non-functional for every user, and that rode along undetected inside one very large release.
  Smaller releases would not have prevented the bug, but they would have narrowed the window in
  which it could hide.

Each of Phases 10, 9, and 8 produces genuinely user-visible change and should ship on its own.

### D4 — Do not pre-commit the v8.0.0 number

The roadmap's title says v8.0.0 and its own §2.6 flags the risk of "a major version bump with no
breaking change." That tension is resolved in favour of semver, not in favour of the title:

**The v8.0.0 line is cut when G6, G7, and G8 close. Whether it carries the major number is decided
at Phase 8's close, on whether the distribution-model change is genuinely breaking for existing
installs.** On current analysis Phase 8 is the only plausible source of a real breaking change on
this roadmap — Phase 10 is metadata, Phase 9 is promotions plus defect fixes, and Phase 11 changes
no API at all. Notably this means the phase most likely to *earn* the major number is not the one
the original draft assumed (Phase 11).

If nothing in the set turns out to be breaking, the work ships as v7.x and **v8.0.0 waits for
something that earns it.** Bumping major for the accumulated weight of work would be exactly the
kind of unearned claim this project's entire v7 arc existed to eliminate — and a roadmap titled
"to v8.0.0" is not a good enough reason to make one.

### Still open — genuinely, not by omission

- **Is a real Codex CLI host obtainable?** Unresolved, and now explicitly the *only* thing gating
  Phase 7. This is no longer a question that blocks planning — D1 removed it from the critical path
  — but it is still the question that determines when the eighth platform ships.

---

## Approval

**Nothing in this document is approved for task-brief authoring or execution.** It is a planning
and state-capture document, following the same Plan-Approve-Execute discipline every phase boundary
in the v7 roadmap used: the plan is reviewed first, phases are approved individually, and task
briefs are authored only after a phase is explicitly approved.

With D1–D4 settled, the next decision the user actually needs to make is narrower than the ones
above: **approve Phase 10 for task-brief authoring**, which is a single task and the first step in
§2.8.
