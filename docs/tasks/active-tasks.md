# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T456 | Downstream measurement (ship gate) | evaluation-agent | blocked | P0 | T454 (done), T455 (done), T458 (pending) | 2026-09-09 |
| T457 | Scoped, non-`Bash` execution/read primitive for `@security-engineer` and `@context-retriever` | solution-architect | pending | P1 | None | 2026-09-09 |
| T458 | Live-execution harness for the golden suite (unblocks T456) | devops-engineer | pending | P1 | None | 2026-09-09 |

> **T436 closed 2026-09-10 — real, evidence-grounded decision: nothing currently warrants
> `deprecated`.** `docs/artifacts/phase3-maturity-demotion-decision-v1.md` (this task's real
> deliverable — a decision, not code) records the Product Owner's itemized, per-category judgment
> across all five categories of non-`stable` component (14 commands blocked on a golden-case gap;
> 3 commands blocked on tracked golden-suite defects; 4 agents blocked on `T456`/`T457`; 4 skills
> with real, disclosed content defects; 14 genuinely unsurveyed skills) — every category concluded
> "leave `experimental`, no deprecation," each with specific, cited reasoning, not a blanket
> rubber-stamp. **A real dispatch-mechanics finding, not a content problem:** the first dispatch
> attempt failed cleanly — the Product Owner has no `execute`/`edit` tool at all (confirmed
> deliberate per `security-guidelines.md`'s Agent Permission Classification, not a gap), so it
> could not run the `git show origin/develop:<path>` commands its brief initially assumed it could;
> it correctly refused to fabricate a decision rather than guess at unseen evidence. Redispatched
> with the real, current artifact content embedded directly in the prompt (verified fresh
> beforehand) instead of asking it to fetch anything itself — this worked cleanly. **Orchestrator
> independent verification before committing the decision as an artifact** (not accepted on the
> Product Owner's self-report alone): independently grepped `AGENTS.md` for the decision's two
> specific factual citations (Blocker Protocol severities; the real `active-tasks.md` column
> schema) — both confirmed exact matches; confirmed the decision explicitly named and then rejected
> its own strongest deprecation candidate (`worktree-isolation`) for a specific, evidence-grounded
> reason rather than uniformly waving every component through. **No file changes result from this
> decision — no follow-up technical dispatch is required.** `python3 tests/run.py` fresh (514
> tests, `OK`, `skipped=24`, unchanged, as expected for a decision-only artifact); real GitLab CI
> green (5/5) before merging.

> **T436 dispatched 2026-09-10 — re-confirmed from `plan-041`'s own task graph and both plans'
> literal T436 rows directly, not assumed.** Owner `product-owner`, unchanged from `plan-035`'s
> original assignment (`plan-041` reaffirms it as "a product-priorities call... not a technical
> one"). **Tool grant checked before dispatch and found to be a deliberate, documented security
> boundary, not an oversight** — `product-owner`'s real grant (`[read, search, web, todo]`) has
> neither `edit` nor `execute`, and `implementation/knowledge/instructions/
> security-guidelines.md`'s own Agent Permission Classification explicitly lists it as "read-only at
> all times." **Disposition differs from every prior Phase 3 tool-grant gap**: not a full
> reassignment (which would lose the real product-judgment intent), but a two-phase split —
> `product-owner` performs the actual decision (achievable with read-only tools), the orchestrator
> transcribes its real reasoning into a committed artifact (since it cannot write one itself), and
> any resulting mechanical changes (if the decision calls for `deprecated`) are a small, separate
> follow-up to a write-capable agent executing that decision, not making a new one. **A framing
> correction included in the brief**: `plan-035`'s original T436 description predates T432's
> mechanical enforcement, which already prevents the false-promotion failure mode T436 was
> originally worried about — every component's current label is already accurate; T436's real
> remaining question is narrower, whether anything among the 46 non-`stable` components is a
> genuine dead end (warranting `deprecated`) versus honestly `experimental` with a live path
> forward, and "nothing currently qualifies" is stated explicitly as an acceptable, honest outcome,
> not a failure to find something to demote.

> **T434/T435 closed 2026-09-10 — real evidence-authorship complete and independently verified for
> both; 28 components genuinely evidence-complete and ready for immediate flip, 0 flipped in these
> closures by design.** `docs/artifacts/phase3-wave2-promotion-v1.md` (T434, MR !267, squash-merged
> `develop` `ce616c1`) and `phase3-wave3-promotion-v1.md` (T435, MR !268, squash-merged `develop`
> `4c88cc7`, after a real, anticipated, purely mechanical rebase conflict in `implementation/
> registry/index.json` against T434's own registry regeneration — resolved by regenerating fresh
> post-rebase, not hand-editing JSON, independently confirmed clean before merging). **T434's own
> finding, independently reproduced by the orchestrator, not accepted on self-report: T433's
> self-referential ledger-defect blocker does NOT reproduce for T434/T435**, because both briefs
> were deliberately drafted to never name any in-scope component by id (the lesson from the
> dispatch-time regression recorded in the prior note). Verified directly — grepped `task-T434.md`
> against the real 40 in-scope ids (23 agents + 17 commands, computed fresh against `index.json`,
> not the 5-agent/2-command set T433 already covered): zero hits; same for `task-T435.md` against
> its 28. **Practical effect: 19 of T434's 23 agents and 9 of T435's 10 evidence-complete components
> (all 4 instructions + 5 skills; the 10th, one task-tracking skill, is evidence-complete but
> blocked by real, independent, pre-existing `T456`) already report a clean `PASS` today, with both
> tasks' rows still open — not merely "would pass once archived" the way Wave 1's 3 clean candidates
> were.** Spot-checked 12 of the 28 claimed-clean components directly (not trusted from the
> artifacts' own counts): `data-mockup-agent`, `poc-orchestrator`, `product-owner`, `scrum-master`,
> `technical-writer` (agents), all 4 instructions, `checkpoint-protocol`, `systematic-debugging`,
> `testing-strategy` (skills) — all 12 genuinely pass `stable` when simulated; also spot-checked 2
> claimed-blocked components (`devops-engineer` → real `T457` defect; the blocked skill → real
> `T456` defect) and one claimed-blocked command (`bug-report` → genuinely fails only on the
> golden-case criterion) — all matched their claims exactly. Confirmed `bug-report.md`'s missing
> `agent:` frontmatter fix (`agent: "orchestrator"`) against the real repo convention: 14 of 18
> other commands with an `agent:` field already use `orchestrator` for the same class of generic,
> ledger-writing utility command — correct, in-scope, not scope creep. `git diff --name-only`
> grepped for every protected path on both MRs — zero hits both times; `python3 tests/run.py` fresh
> on both (505, then 514 tests, `OK`, `skipped=24`, no regressions); `generate-registry.py --check`
> and `sync.mjs --check` clean on both; real GitLab CI green (5/5) on all three MRs (!267, !268,
> and the rebase force-push) independently polled before merging. **14 of T434's 17 commands remain
> blocked solely on a real, well-defined golden-case coverage gap** (a protected-path exception not
> requested this round, per the brief's own instruction); **18 of T435's 24 skills remain genuinely
> untouched**, with 4 of those flagged as having real, pre-existing content defects found
> incidentally (not fixed here, out of scope for a promotion task). Neither new-golden-case
> authorship nor the flagged skill-content defects are dispatched this round.

> **T434/T435 dispatched 2026-09-10 — re-confirmed from `plan-041`'s own task graph directly, not
> assumed from last round's claim.** `plan-041`'s per-task table shows both depend only on T433
> (done) and explicitly states they "can run in parallel... target disjoint component categories...
> flag this parallelization explicitly in each task's brief so it is not accidentally serialized at
> dispatch" — text re-read fresh, unchanged since last round, dispatched together accordingly.
> Briefs at `docs/tasks/task-T434.md`/`task-T435.md`. **Owner tool grant re-checked before dispatch**
> — `tech-lead`'s real grant (`[read, search, edit, execute, web, mcp__fetch]`) has `execute`.
> **Real scope computed fresh this session** (`plan-041` had left both as "TBD"/nominal counts):
> T434 = 23 agents + 17 commands = 40 components (excluding the 5 agents + 2 commands T433 already
> produced evidence for, most still blocked on real disclosed defects, not re-done here); T435 = 24
> skills + 4 instructions = 28 components (2 skills already `stable` from T433, confirmed directly
> against `implementation/registry/index.json`, not assumed from `plan-041`'s original 26-skill
> count). Both are 3-5x T433's own scope — both briefs explicitly instruct against forcing full
> completion in one dispatch, mirroring T433's own successful "honest partial delivery, expected
> re-scoping" resolution, and both proactively carry forward T433's self-referential ledger-defect
> finding (a promotion task's own open row blocks its own claimed promotions) rather than requiring
> each implementer to rediscover it. Both briefs flag a known shared-file collision risk
> (`implementation/registry/*`, `docs/wiki/commands-and-skills-overview.md`) from running in
> parallel, with instructions to rebase rather than force a conflict through.
>
> **A second, distinct variant of T433's self-referential ledger-defect mechanism was found and
> fixed before dispatch, not merely theorized.** The first drafts of both briefs' own "Real scope"
> sections named the 3 components T433 already promoted to `stable` (as context — "here's what's
> already done, don't redo it"), which is a different act from *promoting* them, but the shared
> defect-check's whole-word text match doesn't distinguish the two: naming an already-`stable`
> component by id anywhere in any open P0/P1 task's brief regresses that component's own claimed
> `stable` status, independent of what the task actually does. Caught directly, not assumed:
> `python3 tests/run.py` was run before dispatch (a discipline this session applies to every ledger
> edit, not only code changes) and genuinely went red — `test_check_maturity.py`'s and
> `test_validation_gate.py`'s real-repo baseline tests failed, correctly reporting all 3 previously-
> `stable` components as newly `FAIL`ing, each naming the correct culprit task (`T434` or `T435`).
> Fixed by removing the literal identifier mentions from both briefs and pointing to
> `phase3-wave1-promotion-v1.md` instead; both briefs' own text now explicitly warns the
> implementer not to reintroduce the same pattern in their own closure artifacts. Re-ran
> `python3 tests/run.py` clean (499 tests, `OK`, `skipped=24`) before this commit. **Resolved the
> same principled way as T433's own finding — by not naming things unnecessarily in open task
> prose, not by weakening `check-maturity.py`'s check itself**, which remains exactly as strict as
> T431/T432 designed it.

> **T433 closed 2026-09-10 — real evidence-authorship complete and independently verified; 0 of 9
> candidates flipped to `stable` in this closure, by design, for a structural reason explained
> below, not a shortfall.** `docs/artifacts/phase3-wave1-promotion-v1.md` (MR !262, squash-merged
> `develop` `0766c58`) documents, per component, genuine `## Rails` content, real evidence (existing
> golden-case ownership, `completed-tasks.md` MR references, or two newly-authored substantive
> functional tests — `tests/functional/test_validation_gates_skill_contract.py`/
> `test_code_review_skill_contract.py`, real cross-consistency assertions, not placeholders),
> cross-references, and `docs/wiki/commands-and-skills-overview.md` (new) for real documentation.
> **`code-review` identifier ambiguity (flagged in the brief, not previously flagged by `plan-041`)
> resolved and disclosed**: both the `skill` id and the `command` id of that exact name were treated
> as in scope (9 candidates from 8 named components), reasoned as the more conservative reading.
>
> **A genuine structural finding, independently reproduced by the orchestrator, not accepted on the
> implementer's self-report:** `maturity-promotion-criteria-v1.md` §3.5's shared defect-check flags
> any open P0/P1 ledger row that mentions a component's id anywhere in its brief — with no
> distinction between "this task reports a defect in `<id>`" and "this task's own subject is
> `<id>`." `task-T433.md` necessarily names all 9 candidates as its own subject matter, so **no
> commit could make any of the 9 pass `check-maturity.py` while T433's own row remained open** —
> verified directly by the orchestrator (`sed`-flipping `qa-engineer` to `stable` against the real,
> unmodified repo state and re-running `check-maturity.py --verbose`: `FAIL ... open P0 task T433
> names it in its brief`, exactly as claimed, then reverted). **Independently simulated the
> implementer's own claimed resolution** (uncommitted, reverted after each check): with T433's row
> removed from `active-tasks.md` and all 9 flipped to `stable`, exactly 3 (`qa-engineer`,
> `validation-gates` skill, `code-review` skill) pass cleanly; the other 6 fail on **real,
> independent, pre-existing defects** unrelated to T433 — confirmed directly, not estimated: golden
> `known_failing`/`tracked_defect` cases for `/plan`, `/code-review` (held-out, case ID
> deliberately not quoted, per `test_golden_held_out_isolation.py`'s own guard), and
> `/security-audit`; open `T457` (security-engineer tool-scoping gap, a real, already-disclosed
> defect, not a false positive); and one genuine false positive caught by the implementer's own
> review (`backend-developer`'s `T457` mention is a forward-looking possible-assignee note, not a
> defect report — does not resolve on its own). `git diff --name-only` grepped for every protected
> path on the evidence-authorship MR — zero hits; `python3 tests/run.py` fresh (499 tests, `OK`,
> `skipped=24`, matching the implementer's claim); `sync.mjs --check` no drift (563 files); the two
> new test files run standalone (5/5 pass); real GitLab CI green (5/5) before merging.
>
> **This closure breaks the structural cycle deliberately** — `T433` archives now (a necessary,
> orchestrator-only action per this repo's own "Archival is orchestrator-only" invariant) so that
> the 3 genuinely evidence-complete components can actually be verified `PASS` in an immediate
> follow-up, which the implementer's own artifact §4 anticipated and is consumed directly (see next
> note). The other 6 components' real defects are **not** resolved by this closure — recorded as
> follow-up candidates, not opened as new tasks this round: (a) `commands/plan.md` header-format
> drift vs. real historical plan docs (tracked defect `plan-real-doc-header-drift`); (b)
> `commands/code-review.md` verdict-format drift vs. real historical review docs (held-out tracked
> defect, case ID withheld); (c) `T457`'s own resolution (security-engineer tool-scoping,
> already tracked); (d) `security-audit-critical-not-fail`'s OWASP compensating-control handling (a
> fourth real defect, not previously named in any open task, surfaced only once Blocker 1 was
> simulated away). None dispatched this round — flagged for prioritization, not silently dropped.

> **ADR-006 accepted 2026-09-10 — resolves Gate G2's "routing target classes" ambiguity
> (`plan-041` Finding 1) on the infrastructure-precondition reading.** Three textually-defensible
> readings were found on re-analysis (deepened beyond `plan-041`'s original two): (a) automatic/
> inclusive — G2 closes on Wave 1 completion alone; (b) selective/forward-looking — T433 must name
> a routing-candidate subset ahead of Phase 4's own tier schema; (c) precondition-only — G2's
> gate-table text is a general principle, satisfied once real infrastructure (T430-T432 + genuine
> `stable` promotions) demonstrates the "stable brief with rails and tests" precondition is
> achievable, with actual routing-class identification deferred entirely to Phase 4's own planning
> pass once its tier schema (T440) exists. **None had a textual tiebreaker within `plan-035`
> itself — presented to the user as a genuine decision point, not picked unilaterally, matching
> this project's standing practice for decisions of comparable weight** (`ADR-004`'s Inconclusive-
> classification decision, `ADR-005`'s cost-gate decision, T456's four-option blocker
> presentation). **User approved reading (c).** Full record, including the rejected alternatives
> and reasoning, in `docs/decisions/ADR-006-gate-g2-routing-target-classes-interpretation.md`.

> **T433 dispatched 2026-09-10 — re-confirmed from `plan-041`'s own task graph directly, not
> assumed.** T433's only dependency is T432 (done). Brief at `docs/tasks/task-T433.md`, grounded in
> `docs/artifacts/maturity-promotion-criteria-v1.md`'s real per-category `beta→stable` criteria
> (not re-derived) and `ADR-006`'s disposition (no routing-target-class identification required or
> permitted in this task). **Owner tool grant checked before dispatch** (sixth confirmed check this
> phase) — `tech-lead`'s real grant (`[read, search, edit, execute, web, mcp__fetch]`) has
> `execute`; no reassignment needed, second Phase 3 task not to hit the recurring gap. Per
> `plan-041`'s own explicit flag, this is Phase 3's largest single task and the one most likely to
> need T407/T417-T419/T458-style mid-task re-scoping — the brief states this expectation plainly
> rather than assuming a single dispatch suffices. A real identifier ambiguity not previously
> flagged by `plan-041` was found and carried into the brief rather than silently resolved: `code-
> review` exists as both a `skill` id and a `command` id with no textual basis in `plan-035` to
> prefer one — the implementer must resolve and disclose this, not pick silently.

> **T433's previous "not recorded/dispatched" note (below) is superseded by the above — kept for
> the historical record, not because the situation it describes still holds.**

> **T433 — re-confirmed as the next task in `plan-041`'s sequence 2026-09-10, NOT recorded/dispatched
> this round.** `plan-041`'s per-task table shows T433's only dependency is T432 (now done). Unlike
> T430-T432, `plan-041` itself explicitly flags T433 as "Phase 3's largest single task and the one
> most likely to need the same kind of mid-task re-scoping T407/T417-T419 needed" (8 components × 5
> promotion criteria each) and requires it to resolve Finding 1's still-open "routing target
> classes" question as a stated acceptance criterion, not left implicit. Deliberately not recorded
> as a ledger row or dispatched in the same turn as T432's closeout — reported to the user first,
> matching this repo's own precedent of pausing before a task flagged as needing dedicated,
> non-cascading attention (mirrors the T458 disposition after Phase 5's own similarly-flagged
> harness task).

> **T432 closed 2026-09-10** — `implementation/scripts/check-maturity.py` (new, 744+ lines),
> `implementation/scripts/check.py` (`--maturity` CI-gate wiring), `.gitlab-ci.yml`
> (`validation-super-gate` job now runs `--maturity`), `README.md`/`CONTRIBUTING.md`/
> `implementation/README.md`/`docs/wiki/implementation-guide.md` (doc-snippet updates),
> `tests/functional/test_check_maturity.py` (new) + `tests/functional/test_validation_gate.py`
> published (MR !259, squash-merged `develop` `5803890`), moved to `completed-tasks.md`. Mechanically
> verifies a component's declared `maturity` against `docs/artifacts/maturity-promotion-criteria-
> v1.md`'s real per-category/per-transition criteria (not just enum validity) — a claimed `stable`
> with no qualifying evidence fails CI, naming the specific unmet criterion. Real current-state run:
> 77/77 components pass at `experimental` (all still at the floor, as expected — no promotions
> claimed yet). **Two genuine implementation bugs were found and fixed by the implementer while
> writing their own tests** (both regex-greediness issues: an `\s*` crossing newlines let an empty
> label silently borrow the next label's text; a `## Deprecation Notice` heading regex was missing
> its own section-boundary helper's required capture group) — both now covered by regression tests.
> **A real, more serious gaming vulnerability was found during the orchestrator's own independent
> adversarial review — not accepted on the implementer's self-report of "77/77 pass, tried and
> caught a false stable claim":** the orchestrator ran its own from-scratch adversarial probes (not
> the implementer's own example) — three were correctly caught (a bare false `stable` claim; a junk
> `## Rails` heading with no real labels; a `## Rails` section with correct labels but empty
> values) — but a fourth succeeded: `_documented_in_wiki()`'s "≥40 non-whitespace characters on the
> matching line" check accepted a single padded/repeated-character line (`<id>
> xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`) as satisfying the "documented in docs/wiki/**"
> criterion, with zero real content. Sent back to the same implementing agent (continued session,
> same branch) with the exact reproduction; agent added `_looks_like_real_description()` layering a
> minimum-real-word-count and minimum-distinct-word-count gate on top of the original character
> floor, with the residual limitation (a sufficiently deliberate adversary could still hand-craft
> several distinct vowel-bearing pseudo-words) explicitly disclosed in the function's own docstring
> rather than claimed as a complete fix. **Orchestrator independently re-verified the fix itself —
> including one further adversarial variation of its own, not just re-running the implementer's own
> regression test:** first reproduction attempt against the fixed version appeared to still pass,
> traced to the orchestrator's own test-design error (probed at the `beta` claim level, which per
> `maturity-promotion-criteria-v1.md`'s own tiering does not invoke the `documented`-in-wiki
> criterion at all — that criterion only applies at the `beta→stable` transition); re-ran correctly
> isolated at the `stable` level with all other criteria genuinely satisfied and confirmed the
> padding attack now correctly fails, naming criterion #6 specifically. Confirmed a genuinely
> well-formed Rails section with real content is still accepted (not over-tightened into false
> negatives, via the implementer's own added positive-case regression test, independently spot-read).
> `git diff --name-only` grepped for every protected path on both the original and corrected commits
> — zero hits either time; `python3 tests/run.py` run fresh before and after the fix (491, then 494
> tests, `OK`, `skipped=24`, no regressions either time); real GitLab CI green (5/5) independently
> polled on both commits before merging; all adversarial-probe file edits fully reverted
> (`git status --short` clean) before each `python3 implementation/scripts/check-maturity.py`
> re-baseline run. T433 (Wave 1 promotion, 8 named components) is next in `plan-041`'s own task
> graph — see the note above.
> NOT dispatched this round.** `plan-041`'s per-task table shows T432's only dependency is T431
> (now done); `owner` `devops-engineer` has `execute` in its real tool grant (checked), no
> reassignment anticipated. Not dispatched in the same turn as T431's closeout, deliberately — a
> real factual error was found and corrected in T431's own delivered artifact during independent
> review (see the T431 closure note below), which is reported to the user as its own checkpoint-
> worthy event before further cascading dispatch, rather than auto-chaining straight through.

> **T431 closed 2026-09-10** — `docs/artifacts/maturity-promotion-criteria-v1.md` published (MR
> !257, squash-merged `develop` `8cf217c`; brief MR — see `docs/t430-closeout-t431-dispatch`
> closure commit `cc12f54`, merged via MR !256), moved to `completed-tasks.md`. Defines concrete,
> per-category (`agent`/`command`/`instruction`/`skill`), per-transition
> (`experimental→beta`/`beta→stable`/any→`deprecated`) promotion criteria, resolving `plan-035`'s
> five proposed `stable`-tier bullets where they didn't transfer cleanly across categories (per
> `task-T431.md`'s own explicit instruction not to force a uniform rule). **A real factual error
> was found during the orchestrator's independent, adversarial pre-merge review and corrected
> before merging, not glossed over:** the artifact's first delivered version claimed "zero existing
> tests reference any of the 26 skill ids by name," used as load-bearing justification for
> `skill`'s promotion-criteria design — direct evidence check found this false:
> `tests/functional/test_check_version_consistency.py:341` genuinely, deliberately references
> `implementation/knowledge/skills/release-workflow/SKILL.md` by literal path inside a real
> functional test, not a golden-suite fixture. Sent back to the same implementing agent (continued
> session, not a fresh dispatch) with the exact evidence; agent re-verified repo-wide across all
> real test code (`tests/functional/**`, `tests/unit/**`, `tests/performance/**`, `tests/eval/**`,
> `tests/_helpers/**`, excluding `tests/golden/**`/`tests/fixtures/**` as simulated content) and
> corrected the claim to the real count (1/26 `release-workflow`, not 0/26), cross-checking
> `instruction`'s parallel claim for consistency (genuinely 4/4) — the underlying design conclusion
> ("skill promotion needs a harder bootstrap than instruction") held, now correctly grounded rather
> than resting on a false premise. **Orchestrator independently re-verified the correction itself**
> (not accepted on the correction's own self-report either): re-ran the same grep methodology
> myself for both the `release-workflow` hit and the `instruction` 4/4 cross-check, confirmed both
> counts match exactly; confirmed no held-out golden case IDs leaked into the artifact (`grep`ped
> the artifact against all 6 real held-out case IDs from `tests/golden/held-out/`, zero matches);
> re-ran `tests/functional/test_golden_held_out_isolation.py` directly (8/8 pass); `git diff
> --name-only` grepped for every protected path — zero hits; `python3 tests/run.py` fresh (478
> tests, `OK`, `skipped=24`, both before and after the correction, no regressions); real GitLab CI
> green (5/5) on both the original and corrected commits, independently polled, before merging.
> T432 (`scripts/check-maturity.py`) is next in `plan-041`'s own task graph — see the note above.

> **T431 dispatched 2026-09-10 — re-confirmed from `plan-041`'s own task graph/per-task table
> directly, not assumed.** `plan-041`'s per-task summary shows exactly one task depending on T430:
> T431 (`T430 → T431` is T431's only listed dependency; T432 depends on `T431`, not `T430`, so it
> remains blocked and is **not** dispatched alongside T431 despite being an "obvious next pair" at
> a glance). Brief at `docs/tasks/task-T431.md`. **Owner tool grant checked before dispatch**
> (fifth confirmed check this phase, following the T430/T410/T420/T451 pattern) — `tech-lead`'s
> real grant (`implementation/knowledge/agents/tech-lead.md`: `[read, search, edit, execute, web,
> mcp__fetch]`) has `execute`; **no reassignment needed this time**, first Phase 3 task so far that
> doesn't hit the gap. Cites `docs/artifacts/maturity-levels-v1.md` (T430's design artifact) for
> the final enum names (`experimental/beta/stable/deprecated`) and the mandatory-field policy,
> rather than re-deriving them.

> **T430 closed 2026-09-10** — `implementation/registry/schema.json` (enum reconciled),
> `implementation/scripts/generate-registry.py` (mandatory-field enforcement + a genuine
> pre-existing `FRONTMATTER_RE` regex fix), `implementation/knowledge/schemas/{agent,command,
> instruction,skill}.schema.json` + `tests/functional/test_schemas.py` (companion fixes for the
> new mandatory field), 77 `implementation/knowledge/**` component files (`+maturity: experimental`
> baseline), `implementation/registry/{index.json,summary.md}` (regenerated), `docs/artifacts/
> maturity-levels-v1.md` (design artifact) published (MR !254, squash-merged `develop`
> `a765a23`/`e371ec8`; brief MR !253, `4edba90`; checkpoint MR !255, `09cc132`), moved to
> `completed-tasks.md`. Full independent-verification record (diff scope, regex-bug fix read
> directly, fresh `tests/run.py`/`generate-registry.py --check`/`sync.mjs --check`/`check.py`
> gate, CI) in `docs/checkpoints/checkpoint-028-phase3-t430-delivered.md` — re-confirmed again this
> session on fresh `origin/develop` before dispatching T431: `python3 docs/tasks/
> validate-tasks.py` PASS; `python3 tests/run.py` fresh (478 tests, OK, skipped=24, matching both
> the implementer's and the coordinator's claims independently); `implementation/knowledge/agents/
> orchestrator.md` and `implementation/registry/summary.md` spot-checked directly for the real
> `maturity: experimental` value (77/77), not an inflated or defaulted one.

> **T430 dispatched 2026-09-09 — Phase 3 (`plan-041`, approved/merged MR !252) begins.** Brief at
> `docs/tasks/task-T430.md`. **Reassigned from `plan-041`/`plan-035`'s nominal `solution-architect`
> to `backend-developer`** — `solution-architect`'s real tool grant (`[read, search, edit, web,
> todo, mcp__sequential-thinking, mcp__fetch]`) has no `execute`; this task needs to run
> `generate-registry.py` and the test suite. Fourth confirmed instance of this repo's own
> tool-grant-check discipline (T410/T420/T451 precedent), same disposition (reassign, leave the
> nominal agent's grant unchanged). **Pre-dispatch finding corrects `plan-041`'s own Finding 2**:
> grepped all 84 `implementation/knowledge/**/*.md` files for an explicit `maturity:`/`stability:`
> frontmatter field — zero matches anywhere; read `generate-registry.py` directly and confirmed its
> `_maturity()` function returns the hardcoded fallback `"beta"` for every component because the
> field is absent, not because any component was actually classified; `check.py` has zero
> references to `maturity`, so nothing validates it today either. **The uniform "beta" `plan-041`
> read from `summary.md` is a generator default, not real per-component classification data** —
> `task-T430.md`'s own "Corrected premise" section carries this forward in full, with three
> decisions (final enum names, whether the field becomes mandatory, the honest baseline value for
> unpromoted components) explicitly delegated to the dispatched agent per `plan-041`'s own existing
> delegation of the naming question, not silently resolved here. Not treated as needing a fresh
> user check-in — matches this repo's established pattern of delegating implementation-level design
> decisions (T450's ADR precedent) with independent verification after the fact, rather than
> escalating every such decision.

> **T456 BLOCKED 2026-09-09 — genuine infrastructure gap, user-approved disposition, not a
> fabricated pass, not silently dropped.** Full record at `docs/tasks/task-T456.md`. Re-confirming
> T456's actual mechanism (not paraphrase) before dispatch found: the golden suite was deliberately
> designed, as a Phase 1 architectural decision, to never invoke a live agent/model completion in
> its automated run path — `docs/artifacts/golden-suite-format-v1.md` §2.2 ("Each case's `expect.py`
> ... never itself invokes a live, sampling model completion"), §4.2 ("make no network calls and
> invoke no live/sampling model completion"), and `scripts/scorecard.py`'s own docstring ("No
> subprocess, no shelling out") — all read directly, not quoted from memory. **Consequence:** no
> "retrieval enabled/disabled" configuration can change `scripts/scorecard.py`'s output on the
> existing 20 golden cases, because nothing in that pipeline is sensitive to `@context-retriever`'s
> existence at all — running the scorecard tool twice in any two configurations produces
> byte-identical results. No separate live-agent-execution mechanism for golden cases exists
> anywhere else in this repo either (confirmed by search). Presented four options to the user
> (build the harness now under T456's own mismatched scope; a bounded pilot; declare the gate
> honestly unmeasurable and open a properly-scoped follow-up; redefine "improve"); **user approved
> option (C)** — T456 is `blocked`, not `done`/`cancelled`, per this repo's own task-lifecycle
> convention (`blocked` triggered by "dependency or blocker encountered," not terminal, stays in
> this ledger); **T458 opened** (below) as the real follow-up. **`golden-suite-format-v1.md` and
> `scripts/scorecard.py` were read directly to ground this finding — never edited**, per this
> task's own Constraints and `protected-paths-v1.md`.
>
> **What this does and does not mean for Phase 5:** T450-T455 (6 of 7 tasks) are genuinely done and
> independently verified — the memory layer (storage substrate, enforced scopes, indexing pipeline,
> hybrid retrieval, the read-only `@context-retriever` agent, and its own independently-verified
> retrieval-quality eval) exists, works, and is usable by any agent today. **Phase 5's formal ship
> gate has not been cleared** — per `plan-035`'s own literal rule, the RAG feature does not formally
> ship until T456 actually runs (using T458's harness) and passes its pre-registered improvement
> threshold. **Gate G3 remains open** for the same reason — this is the direct, honest consequence
> of T456 being blocked, not a new finding beyond it.

> **T458 recorded 2026-09-09 — scoped, NOT DISPATCHED this session.** Brief at
> `docs/tasks/task-T458.md`, backed by `docs/plans/plan-040-t458-golden-live-harness-followup.md`.
> Builds a real, two-arm (control/treatment) live-execution harness for the golden suite — reusing
> each case's existing `brief.md` as a live-agent prompt and each case's existing, unmodified
> `expect.py` as the pass/fail check — comparable in shape (not mechanics) to what Terminal-Bench's
> own Layer 2 harness (T417-T419) needed, explicitly scoped as real infrastructure, not a quick
> task. Owner `devops-engineer`, matching this repo's own precedent that harness-building work goes
> to `devops-engineer`, not `evaluation-agent` (T417/T418/T419/T407/T408/T409 precedent). Priority
> P1 — blocks Phase 5's formal ship decision and Gate G3's closure, does **not** block the memory
> layer itself, which is already usable. Not dispatched this session because it is real,
> substantial new infrastructure deserving its own dedicated dispatch/planning attention, and
> nothing currently depends on it being resolved immediately.

> **T455 closed 2026-09-09** — `tests/eval/memory_retrieval/{labeled_dataset.py,metrics.py,
> scorecard-v1.json,scorecard-v1.md}`, `tests/functional/test_retrieval_eval_metrics.py`,
> `tests/performance/test_retrieval_eval_scorecard.py`, `docs/artifacts/retrieval-eval-v1.md`
> published (MR !249, squash-merged to `develop`), moved to `completed-tasks.md`. **Owner
> reassigned from `plan-038`'s nominal `evaluation-agent` to `qa-engineer`** —
> `evaluation-agent`'s actual tool grant (`[read, search, web]`, no Bash, no edit) cannot author/run
> a real eval sub-suite; same disposition as the existing T415/T418 precedent. `evaluation-agent`'s
> tool grant left unchanged.
>
> **Real, measured result (k=5, 23 hand-labeled queries, real local `nomic-embed-text-v1.5`
> embeddings, no network egress):** recall@5 = 1.000 across all 23 queries, zero exceptions,
> including against 4 purpose-built confusable decoys; precision@5 mean 0.226 (structurally capped
> by the label design — 20/23 queries have exactly 1 relevant chunk in a 24-chunk corpus, capping
> precision@5 at 1/5=0.2; the 3 multi-relevant queries reach 2/5=0.4 — disclosed explicitly, not a
> retrieval-quality problem); irrelevant-context-rate mean 0.774 (=1−precision by definition);
> latency p50=63.4ms/p95=76.5ms/p99=max=93.5ms, comfortably under the 500ms budget.
> **Recommendation (`docs/artifacts/retrieval-eval-v1.md` §7): proceed to T456**, with the
> corpus-scale caveat (24 chunks vs. T453's ~13,000-chunk benchmark scale) stated plainly, not
> hidden.
>
> **Orchestrator independent, adversarial verification before merging** (not accepted on the
> implementer's self-report, and not accepted on two separate mid-session messages purporting to
> relay it either — third/fourth occurrence of the "coordinator sent a message while you were
> working" pattern this phase already flagged at `checkpoint-025`/`checkpoint-026`; the second
> message additionally fabricated a claim that the orchestrator "hadn't done any actual
> verification work yet" when it demonstrably had, per its own tool-call history — neither
> message's claims were accepted as fact, both were independently re-derived against real state
> first, matching this repo's standing disposition for this pattern). Confirmed the branch/commit
> genuinely exist and the diff is scoped to exactly the 9 files claimed, no protected paths or
> `.mcp.json` touched. Read `labeled_dataset.py` directly: `relevant_ids` are hardcoded Python tuple
> literals defined alongside each query, confirmed non-circular by construction (not computed from
> any retriever call), not merely trusted from the docstring's own claim. **Independently
> re-derived the precision-cap arithmetic** against the real query distribution read from source
> (20 single-relevant + 3 double-relevant queries): `(20×0.2 + 3×0.4)/23 = 0.226086956...`, matching
> the published mean to full float precision, and cross-checked the real scorecard JSON's per-query
> breakdown shows exactly 20 queries at 0.2 and exactly 3 at 0.4 — the disclosed
> capped-by-design explanation is mathematically sound, independently confirmed, not accepted at
> face value. Read `test_retrieval_eval_scorecard.py` directly and confirmed it constructs a real
> `ContextRetriever(index_dir)` and calls `.query()` end-to-end — not a bypass to `Retriever.search()`
> — against a real index built via T452's own `build_index`/`write_index`, with a real temp git
> remote and `.generated-manifest.json` so `RequestingContext` derivation is genuinely exercised.
> Ran `python3 tests/run.py` fresh (478 tests, `OK`, `skipped=24`, up from checkpoint-026's 453/23,
> exactly `+24` new default-tier `+1` new opt-in-skipped, no regressions — matches the implementer's
> claim exactly, independently reproduced). Ran `test_protected_paths_declared.py` +
> `test_golden_held_out_isolation.py` directly (18/18 pass). **Independently reproduced the real
> embedding run in a completely fresh, throwaway venv** (`fastembed==0.8.0` installed fresh, no
> dependency on the implementer's own environment): precision@5/recall@5/irrelevant-rate
> distributions matched the committed scorecard byte-for-byte identical; latency differed (148.8ms
> vs. 76.5ms p95 — expected, load-sensitive/different sandbox, both well under budget); restored the
> original committed scorecard files afterward rather than leaving the reproduction run's own
> output in the tree. `sync.mjs --check` no drift; `docs/tasks/validate-tasks.py` PASS; CI green
> (5/5) before merging. **All 8 acceptance criteria independently confirmed met.** T456 (downstream
> measurement/ship gate) is next in `plan-038`'s dependency graph — its own owner-reassignment
> check (same `evaluation-agent` gap) must be repeated at its own dispatch time, not assumed
> inherited from T455's.

> **T457 recorded 2026-09-09 — NOT DISPATCHED, backlog item only.** Brief at
> `docs/tasks/task-T457.md`. Found during T454's own MR review: both `@security-engineer` and
> `@context-retriever`'s `tools:` grants include `execute`, which the Claude Code platform's own
> `toolMap` (`implementation/platforms/claude-code.json`) maps to unrestricted `Bash` — neither
> agent's "read-only"/"no write path" claim is backed by a technical tool-scoping restriction on
> this platform, only by the agent definition's own prose instruction. User-decided disposition:
> accept prose-only enforcement for now (matching the pre-existing, previously-un-flagged
> `security-engineer.md` precedent), correct the overclaiming documentation this same session
> (`docs/artifacts/context-retriever-v1.md` §2/§2.1, `docs/tasks/task-T454.md`'s completion
> addendum, `ADR-005-memory-layer-design.md`'s Validation addendum — all dated 2026-09-09), and
> open this task to track the real fix properly rather than leave it undocumented. The likely real
> fix (a dedicated MCP server or equivalent scoped-tool mechanism) would need to touch `.mcp.json`
> in some form — out of scope for dispatch under this session's standing constraint on that file.
> **Confirmed not to block T455/T456** — see `task-T457.md`'s own "Does this block T455/T456?"
> section, checked against plan-038's actual acceptance criteria for both, not assumed.

> **T454 closed 2026-09-09** — `implementation/knowledge/agents/context-retriever.md` (28th agent,
> read-only wrapper), `implementation/runtime/memory/context_retriever.py`, `deploy/docker-compose-
> context-retriever.yml`, `tests/functional/test_context_retriever.py`, and `docs/artifacts/
> context-retriever-v1.md` published (MR !246, squash-merged to `develop`), moved to
> `completed-tasks.md`. All 9 acceptance criteria functionally met — see `completed-tasks.md`'s T454
> row for the full closure record, including one genuine, honestly-recorded downgrade.
>
> **Acceptance criterion 1 ("no write path from any agent into the canonical knowledge base") does
> not hold in full, and was corrected rather than silently accepted, before this MR merged.** MR
> review (this session) found the implementation's own design doc originally overclaimed layer 1
> ("agent definition tools grant") as a technical restriction — it is prose-only: the generated
> Claude Code projection grants `tools: Read, Bash` (`execute` → `Bash` via `implementation/
> platforms/claude-code.json`'s `toolMap`), so a `@context-retriever` session genuinely has
> unrestricted shell access, and layer 3 (deployment manifest) does not protect the real,
> non-containerized deployment this component actually runs as. Only layer 2 (the server module's
> absent write API) is a genuine technical control today, and even it only constrains callers going
> through that module. **User-decided disposition:** accept prose-only enforcement for now (matching
> the pre-existing, previously-un-flagged `security-engineer.md` "read-only mode" precedent already
> in this repo — not a new or weaker standard), correct every overclaiming document rather than
> leave the false stronger claim standing, and open T457 (see the note above the table) to track the
> real fix. Corrected: `docs/artifacts/context-retriever-v1.md` §2/§2.1 (new)/§4;
> `context-retriever.md`'s own prose (source + all 7 regenerated platform projections + registry);
> `docs/tasks/task-T454.md`'s completion addendum (acceptance criterion 1's honest downgrade);
> `docs/decisions/ADR-005-memory-layer-design.md`'s Validation-section dated addendum (mirrors
> ADR-004's dated-successor-block pattern for a gap found after acceptance).
>
> **Orchestrator independently re-verified the corrections before merging** (not accepted on
> self-report of its own edits): re-read every corrected section end-to-end after editing and found
> one remaining internal inconsistency the first correction pass missed (agent-definition prose
> still claimed "you have no tool capable of doing it" immediately above the new honest
> §2.1-referencing paragraph) — fixed before pushing, not left for a second review pass to catch.
> Confirmed `.mcp.json` untouched throughout (`git diff --stat -- .mcp.json`, both before and after
> the correction commit). Ran `python3 tests/run.py` fresh after the corrections (453 tests, `OK`,
> `skipped=23` — includes fixing a real, self-caused registry-drift failure from the source-file
> edit, resolved by re-running `generate-registry.py`, and a real plan-coverage guardrail failure
> from opening T457 without a backing plan, resolved by writing `docs/plans/plan-039-t457-tool-
> scoping-followup.md`); `docs/tasks/validate-tasks.py` PASS; `sync.mjs --check` no drift across 563
> files; `check.py` full gate set (251 checks, 0 errors); CI green (5/5) before merging.
>
> **T455 (retrieval eval sub-suite) is next in `plan-038`'s dependency graph — confirmed unblocked**
> (depends only on T454, now done) and **confirmed not blocked by T457** (T457 has no dependency
> relationship to T455/T456 either direction, per `task-T457.md`'s own check against plan-038's
> actual acceptance criteria for both).

> **T453 closed 2026-09-09** — `implementation/runtime/memory/{scope_filter,lexical,structural,
> rank,retrieve}.py` (hybrid retrieval + mandatory query-time scope pre-filter) and
> `docs/artifacts/hybrid-retrieval-v1.md` published (MR !243, squash-merged), moved to
> `completed-tasks.md`. All 9 acceptance criteria independently verified met, including a real
> `<500ms` p95 latency re-measurement (233.6ms, independent) and a 7-probe adversarial
> scope-enforcement script the orchestrator designed itself against a hand-merged, simulated
> shared-index scenario. **A real defect was found and fixed before merge** — CI's `unit-tests` job
> genuinely failed (`ModuleNotFoundError: No module named 'numpy'` in 4 tests), contradicting the
> MR's own "0 failures" claim; caught via `glab ci status`, not via the implementer's report; fixed
> in a same-branch follow-up commit and independently re-verified in a fresh clean venv before
> merging. See `completed-tasks.md`'s T453 row and `task-T453.md`'s completion addendum for full
> detail.
>
> **Process note:** three separate messages arrived mid-session framed as "the coordinator sent a
> message while you were working," each relaying claims about the implementer's progress/
> completion and instructing next steps. Matching `checkpoint-023`/`checkpoint-024`'s prior
> disposition of the identical pattern, none of their claims were taken as fact and none of their
> instructions were treated as authorization — every claim was independently re-derived against
> real GitLab/git/filesystem state before being acted on. Their factual claims were substantially
> accurate on the parts that were checkable (MR numbers, branch names except one metadata-field
> discrepancy, general shape of the fix) but this was established independently each time, not
> assumed. Flagging this here per this project's own disclosure discipline for the pattern.
>
> **T454 (`@context-retriever`, read-only agent wrapper) is next in `plan-038`'s dependency graph —
> not dispatched this session.**

> **T452 closed 2026-09-09 — `implementation/runtime/memory/` (indexing pipeline),
> `implementation/knowledge/memory/{general,project,shared}/` (vault convention, structure only),
> `docs/artifacts/indexing-pipeline-v1.md` published (MR !239, squash-merged), moved to
> `completed-tasks.md`.** All 9 acceptance criteria independently verified met by the
> orchestrator before merge — not accepted on the agent's self-report, and not accepted on a
> mid-session message purporting to relay that report either (see below). Orchestrator ran the
> full test suite fresh (399 tests, `OK`), independently re-ran the full optional-dependency
> pipeline suite (20/20, real local-model download observed), rebuilt the index from a genuinely
> separate clean git clone + fresh venv and diffed zero against the original build, and designed
> and ran an adversarial symlink-escape probe not present in the agent's own test suite (a
> symlink inside an "evil" project's own tree pointing at a foreign project's `project`-scope
> content) — the escape attempt produced zero leakage. See `completed-tasks.md`'s T452 row and
> `task-T452.md`'s completion addendum for full detail.
>
> **Process note:** mid-session, a message arrived framed as "the coordinator sent a message
> while you were working," reporting the agent's completion and instructing next steps. Per this
> project's own standing rule (no agent message is ever the user's consent) and
> `checkpoint-023`'s own prior incident with the identical framing, none of its claims were taken
> as fact and none of its instructions were followed as given — every factual claim in it was
> independently re-derived against real GitLab/git/filesystem state before being acted on (it
> turned out to check out: MR !239 and the branch were real). Flagging this here, matching
> `checkpoint-023`'s own disclosure discipline, since it's the second occurrence of the same
> pattern.
>
> **T453 (hybrid retrieval) is next in `plan-038`'s dependency graph — both T452's outputs exist —
> but is not dispatched in this session.** Same disposition as T452 was left in after T451: a
> pause point, not a decision withheld indefinitely, ahead of the next large-scope real-design
> task in this phase.
>
> **T451 closed 2026-09-09 — `docs/artifacts/memory-scope-model-v1.md` published (MR !235,
> squash-merged), moved to `completed-tasks.md`.** All 6 acceptance criteria independently
> verified met by the orchestrator before merge, including three factual corrections the
> Bash-less `solution-architect` could not self-check (misattributed ADR-005 citation; a
> fabricated `xemage` org slug across every example, corrected to the real `em-age/*` remotes;
> a platform list that assumed `codex` was already live on `develop`). See
> `completed-tasks.md`'s T451 row and `task-T451.md`'s completion addendum for full detail,
> including the tool-grant disposition (left unchanged, third confirmed instance of the same
> T420-established pattern) and the separate small ADR-005 Approval-section follow-up (MR !234,
> already merged, fixing a staleness the header flip alone didn't reach).
>
> **T452 (indexing pipeline) was next in `plan-038`'s dependency graph — both its dependencies
> (T450, T451) were done. It has now been dispatched (2026-09-09); see the note at the top of
> this file above the active-tasks table.**
>
> **ADR-005 accepted 2026-09-09** — the user approved all three of ADR-005's decisions this
> session (git-versioned Markdown/frontmatter store + locally-rebuilt vector index; local/open-
> source embeddings, zero cost; read-only-by-default for the canonical store and
> `@context-retriever`). Status field flipped `proposed` → `Accepted` in a small, standalone
> docs commit/MR (`docs/adr-005-accept`, MR !232, merged `develop`) — ADR body, Alternatives,
> Consequences, and Approval sections left untouched in that MR per the user's explicit
> instruction to change only the Status field, not rewrite the ADR's content. A separate,
> narrow follow-up (MR !234, merged) later fixed the ADR's own `## Approval` section, which
> still read "proposed, not accepted" with unchecked boxes after the header-only flip — same
> standalone-MR discipline, nothing else in the ADR touched.
>
> **T451 dispatched 2026-09-09**, per `plan-038-phase5-detailed-planning.md`'s own sequencing
> (T450 → T451 → T452 → T453 → T454 → {T455, T456}), now that ADR-005's approval gate is
> cleared. T452 remained undispatched pending T451's actual completion — its own gate
> (T451's scope model must land first, per `plan-038`'s explicit dependency reasoning: "a later
> task cannot conform to a contract that does not exist yet") is now satisfied, independent
> of ADR-005's money-gate already resolving negative (local/zero-cost embeddings, no
> cost-authorization step required per ADR-005 Decision 2).

> **T450 closed 2026-09-09 — `docs/decisions/ADR-005-memory-layer-design.md` published (MR !230,
> squash-merged `da865ed`/`cec4735`), status `proposed`.** Resolves all three items T450's brief
> required: (1) storage/format substrate — a git-versioned Markdown/frontmatter knowledge store as
> canonical source of truth (written only via reviewed MRs, never live agent writes) with a
> separately-built, read-only, rebuildable vector index derived from it at T452 index time; SoloMD's
> own single-device substrate (confirmed real and free/MIT at `https://solomd.app/`, fetched
> directly) was explicitly rejected as the primary design — its single point of direct alignment
> (read-only-by-default MCP exposure) was adopted on its own independent merits (this repo's T416
> protected-paths precedent), not by unexamined imitation — and a server-side vector-DB alternative
> (Chroma/Qdrant/pgvector) was named, compared, and deferred as a documented upgrade path, not
> silently dismissed; (2) embeddings provider — **local/open-source, zero cost, not paid**
> (`nomic-embed-text-v1.5` primary, `bge-small-en-v1.5` fallback, final pick deferred to T455's
> empirical eval); (3) read-only-by-default principle for T454's `@context-retriever`
> (three-place `ALLOW_WRITE=false` assertion, mirroring T416).
>
> **Money-gate: NOT triggered.** Per `plan-038-phase5-detailed-planning.md`'s own gate wording
> ("if T450 instead recommends a local/open-source model, no such gate applies and T452 can proceed
> under Phase 5's normal token budget alone"), no user cost-authorization step is required before
> T452/T453 — the ADR's Decision 2 concludes zero cost, one-off or recurring. **This does not by
> itself authorize T452's dispatch in this session** — the user's own explicit instruction dispatching
> T450 separately named T452 as a hard stop pending their return regardless of the ADR's cost
> conclusion; T452 remains undispatched for that reason, not because a cost gate applies to it.
>
> **Independent verification performed by the orchestrator before merging** (not accepted on the
> agent's self-report): fetched `https://solomd.app/` directly and confirmed every specific claim
> the ADR makes about it (MIT license, fully local/on-device embeddings with zero network calls,
> "$0 forever" pricing, 8-tool MCP server read-only by default with an explicit `--allow-write` opt
> in, 14 named BYOK providers, no built-in multi-user sync) — exact match, no discrepancy;
> independently searched and confirmed `nomic-embed-text-v1.5`'s MTEB score (~62.28-62.39, multiple
> independent sources) sits at genuine parity with OpenAI `text-embedding-3-small` (~62.26-62.3),
> supporting the ADR's central "quality gap does not exist" claim; independently confirmed OpenAI
> `text-embedding-3-small` pricing at exactly $0.02/M input tokens as the ADR states; independently
> confirmed `bge-small-en-v1.5`'s 33.4M-parameter figure exactly (retrieval NDCG@10 figure found by
> the orchestrator's own search, 58.9 on a different domain-specific benchmark, is in the same
> ballpark as the ADR's cited 53.9 general-MTEB-retrieval figure — different benchmark subsets, not
> a contradiction). Also independently read the full ADR text end-to-end and confirmed it does the
> required reasoning work rather than a superficial "SoloMD does X so we do X" copy: it names a
> second alternative (server-side vector DB) beyond SoloMD, and its dedicated "why emage.code's
> multi-agent/shared-memory requirements do not favor SoloMD's design" section concretely ties the
> rejection to SoloMD's lack of any scope concept and lack of a multi-consumer/write-back mechanism,
> against `plan-035`'s own Phase 5 acceptance criterion that a `project`-scoped entry be provably
> unreachable from a different project's session while `shared`-scoped entries remain reachable.
> `python3 tests/run.py` run fresh in the agent's own worktree before commit (clean, full pass); CI
> pipelines green on both this task's MRs (`docs/phase5-t450-dispatch` !229,
> `agent/solution-architect/T450` !230) before either was merged.
>
> ADR-005 status is `proposed`, not `accepted` — per the ADR's own explicit "Approval" section and
> `plan-038`'s own instruction, it does not self-authorize dispatch of T451-T454 as final designs.
> **T451 is next in the dependency graph but is not dispatched in this session** — pending the
> user's review/approval of ADR-005's three decisions.
>
> **T422 closed 2026-09-08 — closes Phase 2 (T420-T423, MCP Conformance) in full.**
> `tests/functional/test_mcp_platform_conformance.py` (2 new tests) proves plan-035 §2.4 Phase 2's
> three acceptance criteria live: (1) adding a `core` server to `servers.yaml` and running
> `node scripts/sync.mjs` for real propagates it to all 7 platform outputs — an actual add-and-
> sync-and-assert round trip against a temp copy of `implementation/`, not a static read; (2)
> deleting a server's entry from one platform's generated output makes the shared presence-check
> helper raise, naming the offending platform — an actual delete-and-assert-failure round trip,
> proving the check is load-bearing; (3) `test_mcp_secret_guard.py` still passes (3/3). Reused
> `test_sync_determinism.py`'s established isolation pattern (deep-copy `implementation/` into a
> `tempfile.TemporaryDirectory()`, run `node scripts/sync.mjs` with `cwd` set to the copy, relying
> on `sync.mjs`'s own `ROOT` default) rather than the `--root`/`--knowledge`/`--platforms` flags the
> brief guessed at — confirmed as the actual pre-existing pattern, not assumed. Orchestrator
> independently re-ran everything on this task's own branch before merging, not trusting the
> transcripts in the completion report: read `test_sync_determinism.py` directly and confirmed the
> claimed isolation mechanism is real; ran the two new tests directly (2/2 pass); ran
> `test_mcp_secret_guard.py` directly (3/3 pass); ran the full suite fresh (379 tests, up from 377,
> exactly the +2 new tests, `OK`, `skipped=17`, no regressions); confirmed `git status` clean both
> mid-run and after (no temp-dir leakage into the real tree); confirmed the merged diff is scoped to
> exactly the one new file (`tests/functional/test_mcp_platform_conformance.py`, 255 lines, nothing
> else touched). **Phase 2 (T420-T423) is now fully done, all four tasks independently verified
> before merge, not merely accepted on self-report.** See "Phase 2 / Gate G2 closure status" note
> below for what this does and does not close.
>
> **Phase 2 / Gate G2 closure status (2026-09-08) — read before proposing next steps.** Phase 2
> (T420-T423, MCP Conformance) is complete. **This does NOT close Gate G2.** Per `plan-035` §2.4,
> "Gate G2 closes when Wave 1 (T433) is complete for the routing target classes" — T433 is Phase
> 3's (Maturity Ladder) Wave-1 promotion task, gated on Phase 3's own T430-T432 first, none of
> which exist yet: Phase 3 is still `plan-035`'s own "**Status: proposed — not approved for
> task-brief authoring or execution**," with zero `T43x` rows in either ledger. What Phase 2
> completing actually does, per `plan-037-phase2-phase5-sequencing.md`'s own framing: it makes
> Phase 3 *proposable* as a next phase (Phase 3 needed both G1, closed, and Phase 2 at least
> underway/re-scoped before it could be proposed at all) — it does not itself advance G2 by even
> one task. Phase 5 (Persistent Memory/RAG) is also now unblocked to start per plan-037's own
> sequential recommendation ("Start Phase 5 after Phase 2 closes"), but neither Phase 3 nor Phase 5
> has been planned to execution-ready detail or approved for dispatch — that is next planning work,
> not yet done, and is a decision for the user per Plan-Approve-Execute, not something this
> ledger note pre-authorizes.
>
> **T421 closed 2026-09-08.** Fixed the one real, narrow gap T420 surfaced:
> `.vscode/mcp.json.provenance.json` (the `github` platform's ADR-002 provenance sidecar) was not
> git-tracked — `.gitignore`'s `.vscode/*` rule matched it with no negation entry, unlike the
> tracked sidecar for all 6 other platforms. Fixed with a one-line `.gitignore` negation
> (`!.vscode/mcp.json.provenance.json`) plus force-tracking the file itself (7 core server keys,
> content matches live generator output). Independently re-confirmed, not re-litigated, that the
> plan-037 `brave`/`context7`/`cwso` claim remains false. Both `.claude`/`.mcp.json` and
> `.github`/`.vscode/mcp.json` were explicitly checked (not just one), per the brief's acceptance
> criteria. Orchestrator independently re-ran every verification command on this task's own branch
> before merging, not trusting the self-report: `git check-ignore -v .vscode/mcp.json.provenance.
> json` (exit 1, no longer ignored), `git ls-files | grep provenance` (all 7 platforms now
> symmetric), `node scripts/sync.mjs --check` (zero drift, 557 files), `pytest tests/functional/
> test_mcp_secret_guard.py tests/functional/test_platform_projections.py` (16/16 pass), and a full
> `python3 tests/run.py` (377 tests, OK, skipped=17, no regressions). Diff confirmed scoped to
> exactly the two files claimed (`.gitignore` +1 line, new tracked sidecar +12 lines) — the agent's
> own report disclosed and fully reverted an earlier accidental broad `install.sh --update` side
> effect before committing, and the orchestrator's independent diff check confirms the final commit
> carries none of it. T422 (qa-engineer) now dispatched — both its dependencies (T420, T421) are
> done.
>
> **T423 closed 2026-09-08 — verify-and-close, no file changes.** `technical-writer` checked every
> tag/platform-count/output-path/remote-transport-shape section of `docs/wiki/mcp-servers.md`
> against `docs/artifacts/mcp-platform-contract-v1.md` (T420) and against T384's own
> `completed-tasks.md` entry for the runtime-checklist section specifically, and found zero
> discrepancies. Orchestrator independently re-verified rather than trusting the self-report: read
> both documents directly and line-by-line compared the tag table (7 core / 8 extended, exact name
> match), all 7 per-platform output paths, and all 7 remote-transport-shape encodings — all match
> the contract exactly, no divergence found. The provenance-sidecar gap found during T420 (routed
> to T421) is correctly out of `docs/wiki/mcp-servers.md`'s scope — its "Provenance-aware merge"
> section describes the merge mechanism generically and makes no per-platform completeness claim
> the missing `.vscode` sidecar would falsify, so there is nothing there to correct. As instructed
> by its own brief, zero file changes means no commit and no MR for this task.
>
> **T420 closed 2026-09-08.** `docs/artifacts/mcp-platform-contract-v1.md` published (MR !220,
> squash-merged `89b1ba3`). Confirms, from primary sources (`servers.yaml`, all 7
> `implementation/platforms/*.json`, `sync.mjs`, `merge-mcp-json.py`), the per-platform MCP
> contract, and independently re-adjudicates (a third, independent confirmation, after the
> orchestrator's own pre-dispatch check) that plan-037's `brave`/`context7`/`cwso` kickoff finding
> is false — both are `core`-tagged, `github.json` scopes to `core`-only, live
> `node scripts/sync.mjs --check` reports zero drift across all 7 platforms (557 files), confirmed
> independently by the orchestrator on this document's own branch before merge, not just accepted
> from the agent's report. Surfaced one new, real, narrow, unrelated finding: `.vscode/
> mcp.json.provenance.json` is untracked by git (caught by `.gitignore`'s `.vscode/*` rule, no
> negation entry, unlike its 6 sibling provenance sidecars) — content is correct and matches
> generator output, but the file does not survive a fresh clone/worktree. Root-caused by the
> orchestrator (`git check-ignore -v`, `git ls-files` comparison across all 7 platforms) and handed
> to T421 as its concrete, real fix — see `task-T421.md` §"Context" and the contract doc's own §7.
> **Tool-grant note, not a new finding:** the dispatched `solution-architect` again had no Bash
> grant (same pattern as T410's ledger entry) and could not run the brief's required
> `sync.mjs --check` itself; it disclosed this as a blocker and substituted a disclosed manual
> byte-level trace rather than fabricating a command transcript. Orchestrator ran the real command
> independently, confirmed the agent's manual trace was accurate, root-caused the provenance-sidecar
> finding the agent could not fully resolve without shell access, appended both as a new §7 to the
> document, then committed/pushed/opened the MR on the agent's behalf (mirroring T410's established
> resolution exactly). Per T410's own precedent and `security-guidelines.md`'s "Architect —
> read-only for implementation code" classification, this is by design, not a bug — `solution-
> architect`'s tool grant is intentionally left unchanged again. Task briefs should not instruct
> `solution-architect` to run shell verification commands going forward; route that instruction to
> the orchestrator or to a Bash-capable agent instead. See `docs/tasks/completed-tasks.md` for
> T420's full closure record.
>
> **Phase 2 (MCP Conformance, T420-T423) dispatched 2026-09-08**, per `plan-037-phase2-phase5-
> sequencing.md` (merged to `develop` via MR !218, commit `a710e4a`) — approved by the user as the
> next phase, sequenced before Phase 5. Reuses `plan-035` §2.4 Phase 2's task table verbatim (owners,
> scope) plus plan-037's execution sequencing (T420 first; T421/T423 in parallel off T420; T422 after
> T421). **Orchestrator pre-dispatch correction to plan-037's own kickoff finding:** plan-037 claimed
> `.vscode/mcp.json` over-includes `brave`/`context7` as `extended`-tagged servers leaking into the
> `github` platform. This was independently re-checked directly against the repo before dispatch (not
> trusted as-is) and found to be **incorrect** — `implementation/knowledge/mcp/servers.yaml` tags both
> `brave` and `context7` as `[core]` (matching `AGENTS.md`'s own "Core servers (always available)"
> table, which lists both explicitly), `implementation/platforms/github.json`'s own manifest scopes
> `mcp.tags` to `["core"]` only (correctly excluding `extended`), and a live
> `node scripts/sync.mjs --check` run (both `--platform=github` alone and unscoped, all 7 platforms)
> reports **zero drift across 557 files**, right now, on `develop`. The `cwso` entry present in
> `.vscode/mcp.json` (not in `servers.yaml` at all) is also not a defect — `scripts/merge-mcp-json.py`
> (ADR-002) explicitly documents preserving hand-added, non-generator dest-only keys exactly like
> `cwso` by design, and its docstring cites "a locally-added MCP server entry" as the literal use case.
> Full detail and the corrected scope are in `task-T420.md` and `task-T421.md`. T421 is not cancelled
> — plan-035 already anticipated re-scoping could shrink Phase 2's real scope at kickoff, and T421's
> assignee still owns confirming this finding independently (not just trusting the orchestrator's
> pre-dispatch check either) across all 7 platforms, not only `github`, before formally closing.
>
> **T409 closed, Gate G1 closed, 2026-09-08.** T409 ("Extend the T415 failure taxonomy to ingest
> Harbor trajectories") is the task record of plan-035 §2.4 Phase 1's acceptance-criteria checklist
> (immediately before "Gate G1 closes here") having one bullet unmet — "Terminal-Bench and golden
> failures appear in one taxonomy" — while all nine others were already independently verified met.
> `docs/artifacts/failure-taxonomy-v1.md` §7 ("Reuse notes for T409") explicitly named T409 as the
> task that would extend the scheme to Harbor trajectories; that extension has now happened and was
> independently verified twice (see "Owner corrections and closure history" below for the full
> two-pass narrative, including a real gap the orchestrator caught and sent back before accepting
> the first pass). **All ten of Phase 1's acceptance-criteria bullets are now genuinely met. Gate
> G1 (`plan-035` §2.2, "Signal") is closed** — no component may be promoted out of beta before an
> outcome eval exists that can fail it, and that eval (golden suite + Terminal-Bench guardrail, one
> shared failure taxonomy) now exists in full. Gate G4's evaluator-protection precondition, which
> plan-035 states closes at the same point as G1, is also closed (already satisfied by T416's
> protected-paths freeze, confirmed untouched by T409's own diff). This closes Phase 1 (T410-T409,
> all `done`) in its entirety. See `completed-tasks.md` for T409's full closure record.
>
> T416 closed 2026-08-14 (see "Owner corrections and closure history" below and
> `completed-tasks.md`). **Phase 1 Layer 1 (T410-T416) is now fully done and merged to `develop`.**
> T407 dispatched 2026-08-14 per explicit user authorization ("launch now, conservative
> concurrency") — see `task-T407.md` for the full brief, including the verbatim decision-rule
> reproduction and the pre-flagged host-resource/oracle-overlap risks. T409 remains in the backlog
> below, blocked on T407 actually completing (not merely being dispatched).
>
> **T407 "Design A" re-dispatch, 2026-09-05.** The completed 2026-08-14 k=3 run measured
> within-run trial variance (3 attempts/task inside one pass), not the across-run spread
> plan-035's decision rule actually requires (`spread` = per-arm min-max across *k independent
> runs*), so it cannot be classified under the literal rule. Same task, same owner
> (`devops-engineer`), same worktree/branch (`feature/T407-tb-delta-v6.12.0`) — the 2026-08-14
> artifacts are preserved untouched as historical evidence, not superseded. Re-dispatched as
> "Design A": 3 independent full-subset passes (`-k 1 -l 25 --n-concurrent 2
> --max-budget-seconds 129600` each), both arms, ~150 trials total, run sequentially and launched
> as a detached background process (verified alive, config-diff clean, a real probe trial running
> in Docker, host resources healthy). See `task-T407.md`'s "Design A addendum" section for the
> full rationale, exact invocation, and verification evidence. Expected wall-clock: roughly
> 6-12h if all three passes run smoothly, up to ~a day at the high end. T407 remains
> `in_progress`; classification and `tb-delta-v6.12.0.md`'s conclusions are still pending a
> follow-up check once all 3 passes complete. T409 remains blocked on that.
>
> **T407 Design A — host-exhaustion blocker and restart, 2026-09-06.** The first Design A attempt
> halted ~1h41m into Pass 1 (Arm A complete 25/25, Arm B 6/25) on a `type: technical`,
> `severity: major` blocker: the remote Docker host (`10.10.160.11`) genuinely exhausted resources
> (4.0GB RAM host, RAM+swap fully exhausted, load average 13.79) — root cause was the
> `rstan-to-pystan` subset task's Stan/httpstan C++ compile alone using ~3.3GB RSS on a 4GB host,
> a real host-capacity problem, not a harness or design defect. Per this task's own blocker
> protocol, the run was stopped (not forced): SIGTERM triggered Harbor's own graceful container
> cleanup, both in-flight Arm B trials ended cleanly with no orphaned containers, and Pass 1's
> completed Arm A data plus Arm B's partial state were preserved on disk along with the halted
> attempt's log (`jobs/design-a-run-attempt1-halted.log`). The user then resized the host to 24GB
> RAM / 8GB swap / 8 CPUs (verified healthy post-resize), and Design A was restarted from scratch
> (all 3 passes, same invocation) — a second attempt is in progress as of this note. See
> `task-T407.md`'s "Design A — host-exhaustion blocker and restart" section for full detail. No
> result or classification exists yet; T409 remains blocked.
>
> **T407 closed, 2026-09-08.** The restarted second Design A attempt (above) also hit 100% trial
> failure across all 3 passes — root cause, confirmed by direct filesystem inspection on both
> hosts: Docker Compose bind mounts resolve against the daemon's filesystem (`10.10.160.11`), not
> the client's (`10.10.160.12`), so agent/verifier output was silently stranded on `.11`. Fixed by
> running the Harbor CLI co-located with the daemon, directly on `.11`; a clean 4-trial smoke test
> there was followed by a full, successful Design A re-run: 3 independent passes, 150 real trials,
> valid reward data throughout, completed 2026-09-08T05:10Z. Arm A pass means `[0.36, 0.28, 0.28]`
> (spread = 8.0pp), Arm B `[0.32, 0.28, 0.28]` (spread = 4.0pp), aggregate delta −1.33pp.
> **Classification: INCONCLUSIVE** per plan-035's frozen rule (Arm A's spread sits exactly on the
> rule's own `≥ 8pp` threshold, which is inclusive of equality) — this is not a Null, Positive, or
> Negative result; the rule's own text is explicit that Inconclusive must not be reported as Null.
> Total real cost across T407's entire history (original k=3 run + both failed Design A attempts
> + the `.11` smoke test + the 3 successful passes): **≈$78.41**. Full numbers, spread
> derivation, and rule application: `docs/benchmarks/tb-delta-v6.12.0.md` §6-7. Full narrative,
> including an independent-verification correction to this note's own 2026-09-06 entry (the
> 2026-09-05 attempt's Arm A data was not "valid" as previously stated — re-checked during
> closeout and found to be 100% errored, same root cause, just discovered later):
> `task-T407.md`'s closing addendum. T407 moved to `completed-tasks.md`. T409 is unblocked — see
> the "Backlog" section's T409 entry below for its updated status.

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done` · `cancelled`
> Priority values: `P0` (critical path) · `P1` (important) · `P2` (nice-to-have)
> Owners are agent names from `knowledge/agents/`.
>
> Based on: `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 1. Phase 0 (T400-T406) and
> T417 are `done` — see `docs/checkpoints/checkpoint-016-phase0-ground-truth-complete.md` and
> `checkpoint-017-t417-harbor-oracle-smoke-complete.md`. Both of Phase 1's gating open questions
> (Arm A agent = `claude-code`; null-delta interpretation) are resolved in `plan-035` §2.4 Phase 1
> and "Open questions." Dispatch of Phase 1 in full was explicitly authorized by the user on
> 2026-08-13.

## Task ID note

`plan-035`'s Layer 2 table names three tasks `T41A`/`T41B`/`T41C`. These do not match this repo's
enforced `^T\d{3,}$` task ID format (`tests/performance/test_team_health.py` /
`docs/tasks/validate-tasks.py`'s `C3` check) — caught by CI when this ledger branch was first
pushed. **Renamed for all ledger/task-brief purposes: `T41A` → `T407`, `T41B` → `T408`,
`T41C` → `T409`** (the free numeric gap in this plan's reserved `T400`-`T474` range). See
`plan-035`'s top-of-document correction note for the full explanation; `plan-035`'s own prose is
left unchanged (still says `T41A`/`T41B`/`T41C`) — this repo's task ledger is the canonical source
for the real IDs from here on.

## Backlog (not yet added as rows — no brief exists yet)

Per `docs/tasks/validate-tasks.py`'s `C7` check, a row may not be added to the table above until
its `task-<ID>.md` brief already exists (confirmed the hard way — CI correctly rejected an earlier
version of this file that added rows for briefs not yet written). Rows are added to the table
above, and briefs authored, together, just-in-time as each task unblocks — matching the real
established Phase 0 pattern, not a deviation from it. This list is for dependency-graph visibility
only; it is not machine-parsed (bullets, not `|`-table rows).

**Layer 1** — all done (T410-T416). See "Owner corrections and closure history" below for T416's
closeout detail.

**Layer 2** (T407/T409 renamed from plan-035's `T41A`/`T41C` per the note above; T418, T419, T408
all done and genuinely merged to `develop`, MR !203 — see "Owner corrections and closure history"
below):
- T407 — closed 2026-09-08, see `completed-tasks.md` and `task-T407.md` (Inconclusive
  classification; not a Null/Positive/Negative result — see the closure note above)
- T409 — closed 2026-09-08, see `completed-tasks.md` and `task-T409.md` (one taxonomy, two
  sources; closes Gate G1 — see the note above the table).

## Task-brief authoring note

Briefs for T410, T411, and T418 (tasks with no unresolved upstream design dependency, or already
unblocked) are written in full. Remaining Layer 1/2 briefs are authored just-in-time as each task
actually unblocks, because T412 onward depends on design decisions T410/T411 finalize, and T419
onward depends on T418's actual frozen subset content. Writing detailed briefs against a
not-yet-decided design would risk contradicting it — and, as of this note, is also a hard CI
requirement (`C7`), not just a style preference: a row cannot exist in the table above without its
brief already on disk.

Per-task briefs live alongside this file as `task-T410.md`, `task-T411.md`, `task-T418.md`, …

## Owner corrections and closure history

**Owner correction (2026-08-13, after T418's first dispatch attempt):** `plan-035`'s task table
lists `evaluation-agent` as owner for T415, T418, and plan-035's `T41A`/`T41C` (this ledger's
T407/T409). The dispatched T418 attempt reported a `type: technical`, `severity: critical` blocker:
this repo's actual registered `evaluation-agent` (`.claude/agents/evaluation-agent.md` and the
source `implementation/knowledge/agents/evaluation-agent.md`) grants only
`Read, WebFetch, WebSearch` — it is scoped for PoC hypothesis validation (read/research only), not
general write-capable benchmark execution. No worktree, branch, or commit existed from that
attempt; the agent correctly stopped rather than working around the gap. Reassigned rather than
widening the tool grant (a registry-wide change with a much larger blast radius than this one
task): T415 → `qa-engineer` (continuity with T411/T412, which it already owns, and full write/Bash
access); T418, T407, T409 → `devops-engineer` (matches the T417 precedent — Layer 2/Harbor work was
already executed by `devops-engineer` despite similar nominal framing — and matches T419/T408,
already on the same branch/worktree). `evaluation-agent`'s tool grant is unchanged. This
reassignment is recorded here, not in `plan-035` itself, per this repo's established convention of
recording such execution-time corrections in the task ledger/briefs (see `task-T400.md`'s addendum
for precedent) rather than editing the plan document.

**Tool-grant gap #2 (2026-08-13, T410, distinct pattern):** T410's dispatched `solution-architect`
completed all real design work but reported a `type: technical`, `severity: major` blocker at the
apply step — `solution-architect`'s registered tool grant has no Bash, so it could not create a
worktree, run `tests/run.py`, or commit. Unlike T418 this was not a missing-output blocker: the
agent staged every output file plus an apply runbook to the orchestrator's scratchpad. Per this
repo's established fallback precedent (T379/T380/T387/T392 — Bash-less delegate produces content,
Bash-capable orchestrator independently reviews then applies it), the orchestrator read and
verified every staged file, then executed the worktree/test-run/commit steps itself. T410 is now
`done` (see `completed-tasks.md`). `solution-architect`'s tool grant is unchanged. **Pattern check
for remaining Layer 1 owners** (`qa-engineer`: T411/T412/T415; `devops-engineer`:
T413/T418/T419/T407/T408/T409; `release-manager`: T414; `tech-lead`: T416) — all six confirmed to
have Bash per their `.claude/agents/*.md` definitions at the time of this note, so this specific
"no Bash" pattern is not expected to recur, but each dispatch should still independently
re-confirm rather than assume this holds if the registry changes mid-phase.

**T418 closed (2026-08-13).** `devops-engineer`'s re-dispatch completed cleanly. Independently
verified by the orchestrator (not just the agent's self-report): 6/25 subset tasks' `category`
values cross-checked against real local `task.toml` files, all matched; JSON parse + uniqueness/
category/effect-split checks; `git status` clean; `python3 tests/run.py` 355/355 in the worktree;
`docker ps -a`/`docker images` inspected, no evidence of a container run for this task. See
`completed-tasks.md` and `task-T418.md`'s Completion addendum. T419/T408 are now unblocked.

**Ledger branch reconciliation note (2026-08-13):** this file and the task briefs it references
have lived on `docs/phase1-t410-t418-dispatch`, a branch separate from the two feature branches
(`feature/T410-phase1-golden-suite-v6.12.0`, `feature/T418-phase1-tb-delta-harness-v6.12.0`) —
necessary because both feature branches would otherwise independently edit this single shared file
and diverge. This branch is being pushed and merged to `develop` now (ahead of either feature
branch's own merge) specifically so `docs/tasks/task-T418.md` and this file are readable directly
from `develop` rather than requiring `git show <branch>:<path>` from an unmerged branch, as the
dispatched T418 agent had to do to read its own brief. Future ledger updates in this phase continue
to accumulate on new short-lived docs branches merged at each natural boundary, same pattern.

**T411 closed (2026-08-13).** First dispatch was interrupted mid-task by an account-wide Claude
usage-limit stop (not a code error, not a blocker report). On resumption: 11/20 cases plus one
half-authored stub existed, uncommitted, with zero coverage for `/new-feature`/`/prepare-release`.
A second `qa-engineer` dispatch finished the stub and authored the remaining 9 cases. Independently
verified by the orchestrator (not just the agent's self-report): 20/20 case dirs with all four
required members; every `expect.py` re-run twice against its own fixture with identical, correctly-
matching-declared-status results both times and clean `git status` after each; fresh
`python3 tests/run.py` (359 tests, exit 0); and — because this is the one place a shortcut could
quietly invalidate a case — the three real-artifact-grounded fixtures' documented cosmetic
redactions were diffed against their live originals and cross-checked line-by-line against each
affected case's actual `expect.py` logic to confirm the redacted content is genuinely outside what
each check inspects. See `completed-tasks.md` and `task-T411.md`'s Completion addendum. T412
(open/held-out split), T414 (baseline publish), and T415 (taxonomy) are now unblockable — briefs to
be authored just-in-time per this file's own `C7` discipline before their rows are added.

**T419/T408 closed (2026-08-13).** First dispatch was interrupted mid-task by an account-wide
Claude usage-limit stop (not a code error, not a blocker report), leaving real but unverified
uncommitted work: a config-diff mechanism that was genuinely correct, but a smoke test that had
actually failed silently — both arms' single trial errored (`NonZeroAgentExitCodeError`, API
404) because `ECONOMY_MODEL`'s hardcoded default, `claude-3-5-haiku-20241022`, was absent from the
live Anthropic model catalog. The orchestrator found this by reading the raw pre-interruption
scorecard JSON directly rather than trusting that a "smoke test ran" meant it passed, and
independently confirmed the catalog gap via a direct `GET /v1/models` call with the host's own
key. A separate concern was also flagged: the interrupted session's doc claimed a budget-guard
abort had already been demonstrated, but no on-disk artifacts for that claimed run survived —
re-verification was required, not just trust in the transcript.

A `devops-engineer` re-dispatch fixed the model default (`claude-haiku-4-5-20251001`, the cheapest
model actually present in the catalog) and re-ran both pieces of evidence from scratch with real
Docker runs: a fresh smoke test (RUN_ID `20260813T190348Z`, both arms completed real trials, no
infra error) and a fresh budget-guard abort (RUN_ID `20260813T193832Z`, real 747s probe, real
abort at exit 2, real `budget-guard.json` on disk). The re-dispatch's own report included a
harness-level auto-neutralization flag on instruction-shaped text ("bypass-permissions",
"permissions.allow/deny") in its output; the orchestrator independently read the raw underlying
job logs directly (not just the agent's characterization) and confirmed this is Harbor/Claude
Code's own logged CLI invocation and workspace-trust-dialog text — descriptive data about the
sandboxed system under test, not directives aimed at the orchestrator — before accepting the
"benign" read.

Orchestrator independently verified (not just the agent's self-report): re-queried the live model
catalog directly, confirming the new default is present and the old one is not; decoded the raw
`tb-delta-scorecard-20260813T190348Z.json` and the Arm B trial's raw `result.json` directly,
confirming `exception_info: null` (a genuine task-level 0.0 reward, not an infra failure); decoded
the raw `config-diff.json` from both the pre-fix and a fresh post-fix `--config-only` dry run,
confirming `"clean": true` in both; decoded `budget-guard.json` for the abort run directly,
confirming `aborted: true`, no scorecard written, exactly one trial directory on disk; grepped the
raw agent transcript directly for the flagged permission strings and confirmed
`"permission_denials":[]` throughout, matching the "benign" claim; ran `python3 tests/run.py`
fresh in the worktree (355 tests, exit 0). Also removed stale on-disk debris from the pre-fix
broken run (`jobs/tb-delta-20260813T152937Z-*`, its `.runs/` dir, its scorecard JSON) via targeted
`rm` on specifically-identified paths after confirming none of it was git-tracked — the agent's
own cleanup attempt had been correctly blocked by the sandbox's destructive-operation classifier.
See `completed-tasks.md` and `task-T419.md`/`task-T408.md`'s Completion addenda.

**T412 closed (2026-08-13).** This is plan-035's single highest-severity risk item (risk table:
"Held-out set leaks into improvement work | Medium | Critical"), so it received the closest review
pass of any task closed in this phase so far. Delivered: 14/6 `open`/`held-out` split (30% held
out) spanning all 5 command surfaces, balanced 3 `expected_pass`/3 `known_failing` covering both
`known_failing_category` values; a new repo-wide static guard
(`tests/functional/test_golden_held_out_isolation.py`) mirroring the established
`test_link_integrity.py`/`test_check_version_consistency.py` pattern.

One genuine judgment call surfaced, not resolved by silent deference: the brief's literal text
("never referenced from any file outside `tests/golden/held-out/`") would, applied strictly, have
flagged pre-existing T411 sibling cross-references inside `open/*/brief.md` that criterion 1's
byte-identical requirement forbade editing. The agent narrowed the case-ID-mention check to
"outside `tests/golden/` entirely" while leaving the stronger functional-access check (Python
imports/`open()`/`Path()`) unscoped and repo-wide. The orchestrator did not accept this as
pre-settled by the brief's own ambiguity-handling default — independently reasoned through the
actual threat model (files that matter for "leaks into improvement work" live outside
`tests/golden/` entirely and are untouched by the narrowing; the manifest's own mandated
disclosure already makes case-ID tokens non-secret; the alternative would violate criterion 1) and
then proved it rather than just asserting it: planted live adversarial probe files in `scripts/`
and `docs/` in the real repo tree, confirmed the guard's `find_violations()` caught both, removed
the probes, confirmed `git status` clean. Independently verified byte-identity via raw
`git diff --raw -M100%` blob-hash comparison (stronger than trusting the agent's own SHA claim) —
all 82 case-content files identical. Re-ran all 20 cases from their new nested paths (zero status
mismatches), ran the guard's own 8-test suite directly (8/8 OK), ran `python3 tests/run.py` fresh
(367 tests, exit 0). See `completed-tasks.md` and `task-T412.md`'s Completion addendum for the
full reasoning. T413 is now unblockable.

**T413 closed (2026-08-13).** `scripts/scorecard.py` + `docs/benchmarks/scorecard-v6.12.0.{json,md}`
delivered: 20 cases, 11 pass, 0 regressions, `open`/`held-out` breakdown matching T412's split
exactly. A real design interaction with T412 surfaced during implementation, not pre-anticipated in
either brief: the output artifacts live outside `tests/golden/`, so unlike `scripts/scorecard.py`'s
own allowlisted source, they aren't exempt from the isolation guard's Check B — emitting real
held-out case IDs into them would have been exactly the leak that guard exists to prevent. Resolved
within this task's own file ownership (the guard's allowlist was correctly treated as out of
scope): `held-out/` cases report every real field except identity, replaced with a deterministic
anonymized label. This is a second, independent enforcement of held-out isolation on top of T412's
own guard.

Given this is a direct extension of Phase 1's single highest-severity risk item, the orchestrator
applied the same review rigor as T412's own closure rather than treating it as a routine follow-on:
grepped both output files directly for all six real held-out case IDs (zero matches), re-ran the
isolation guard's own 8-test suite against the real tree with the new files present (still 8/8,
including the real-tree-clean test), decoded the redacted JSON entries directly and cross-checked
each anonymized label's fields against the real `case.yaml` ground truth established during T412's
own review (all six correct, correct sorted order), independently re-ran the determinism proof
(two more fresh runs, diffed both JSON and MD myself, confirmed only `generated_at` differs,
restored the worktree afterward), and spot-checked the T419 schema-reconciliation claim against
`tb-delta.sh`'s actual shipped schema. One transient, non-reproducing test-count anomaly (355/17
vs. the expected/stable 367/18) was investigated and resolved as environmental flakiness (T413's
commit touches nothing under `tests/`; two immediate re-runs were stable). See `completed-tasks.md`
and `task-T413.md`'s Completion addendum. T414, T415 are now unblockable (T414 was the last item
waiting on T413 — all of T410-T413 are now done).

**T414 closed (2026-08-13).** `docs/benchmarks/baseline-v6.12.0.md` published — the last of
T410-T413's dependents, closing plan-035's "do not optimise before this file exists" gate.
Headline numbers (20 cases, 11 pass, 9 known_failing [6 `tracked_defect`, 3 `capability_gap`], 0
regressions) sourced from and matching T413's real scorecard exactly. The "reject a too-easy
baseline" risk-table control was performed and documented in the file itself: known_failing=9
clears T411's ≥5 floor with margin, spread across both categories and both `open`/`held-out`
subsets. This is the third independent held-out-isolation check in the T412→T413→T414 chain (T412's
guard, T413's anonymization, now T414's own document), each verified on its own merits by the
orchestrator rather than assumed correct by association with the prior two: decoded the real
scorecard JSON directly and cross-checked every published number against it, grepped the published
document for all six real held-out case IDs (zero matches), re-ran the isolation guard's own 8-test
suite with the new file present (8/8), ran `python3 tests/run.py` fresh (367 tests, exit 0), `git
status` clean. See `completed-tasks.md` and `task-T414.md`'s Completion addendum. T415 is now
unblockable (T416 remains gated on T415).

**T415 closed (2026-08-14).** Original delivery (`docs/artifacts/failure-taxonomy-v1.md`,
`docs/benchmarks/failures/*.md`) landed cleanly at commit `76ab91c`, meeting all 6 stated
acceptance criteria. The session doing final sign-off was itself interrupted twice by an
account-wide Claude usage-limit stop before closing this task, so a third resumption picked up a
requested pre-T416 cross-task review (T416 makes `tests/golden/**`/`scripts/scorecard.py`
read-only, raising the cost of anything found afterward).

That review found a real issue distinct from case-*identity* leakage (which T412's isolation guard
already catches): `held-out-case-1.md`/`-3.md`/`-4.md`'s "Why" sections narratively described the
real held-out fixtures' actual content (quoted requirements, described real document structure) —
well beyond the categorical axis-value labels the redaction scheme was designed to permit. Fixed
in commit `3fef6ee`: each "Why" replaced with a redaction notice pointing to the general axis-value
definitions in `failure-taxonomy-v1.md` §3; axis-value tables (the only non-redacted content)
unchanged.

The same review's broader mandate — checking every T410-T415 file that touches held-out content,
not just T415's own three — surfaced one further issue outside T415's file set: `task-T411.md` and
`task-T412.md` (already merged to `develop`) each contained bare real held-out case-ID mentions,
latent since neither the isolation guard nor `tests/golden/` itself had merged to `develop` yet,
but confirmed (by copying pre-fix content into the feature-branch worktree and reproducing the
guard failure) to become live violations the moment `feature/T410-phase1-golden-suite-v6.12.0`
merges. Fixed via `docs/phase1-t411-t412-isolation-fix` (MR !199, merged to `develop` ahead of and
independent of this closeout).

Orchestrator independently verified rather than trusting either fix's self-description:
`tests/functional/test_golden_held_out_isolation.py` re-run at 8/8 with both fixes' pre-fix content
simulated into the feature-branch worktree (reproduced the failures) and again post-fix (clean);
`python3 tests/run.py` fresh in the worktree, exit 0; grepped all three redacted files and both
task briefs against all six real held-out case IDs directly, zero matches in every case; `git
status` clean under `tests/golden/`, `scripts/`, `docs/benchmarks/scorecard-v6.12.0.*` (untouched,
as the brief required). See `completed-tasks.md` and `task-T415.md`'s Completion addendum for full
detail. T416 is now unblockable.

**Golden-suite implementation landed to `develop` (2026-08-14, discovered and closed alongside
T416 dispatch).** While investigating T416 (which cannot freeze paths that don't exist on
`develop`), found that `feature/T410-phase1-golden-suite-v6.12.0` — the actual T410-T415
implementation (`tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/**`,
`docs/artifacts/golden-suite-format-v1.md`/`failure-taxonomy-v1.md`) — had never been merged to
`develop`; only each task's ledger bookkeeping had been. No MR for it had ever been opened. Fixed:
dry-run merge verified clean (0 conflicts, purely additive, 106 files/5717 insertions) in a
disposable clone, then MR !201 opened and merged for real (CI green). Re-verified directly on
`develop` post-merge: `python3 tests/run.py` — 367 tests, OK; `test_golden_held_out_isolation.py`
— 8/8. See `docs/checkpoints/checkpoint-018-phase1-layer1-golden-suite-complete.md` for full
detail. `develop` HEAD is now `8746eb9`. T416's brief (`task-T416.md`) reflects this — it targets
paths that now genuinely exist on `develop`, not the stale feature branch.

**TB-delta harness implementation landed to `develop` (2026-08-14, discovered and fixed while
verifying Layer 2 preconditions ahead of dispatching T407/T409).** Same sequencing gap as the
golden-suite one above, found independently this time by checking `completed-tasks.md`'s own T418/
T419/T408 rows before assuming their prerequisite status meant the actual code was reachable from
`develop`: those rows' artifact columns say "not yet merged" plainly, and a direct `ls` on `develop`
confirmed `scripts/tb-delta.sh`, `scripts/tb_delta_agent.py`, `docs/benchmarks/tb-subset.json`,
`docs/benchmarks/tb-subset.md`, and `docs/benchmarks/tb-delta-runner.md` did not exist there — only
each task's ledger bookkeeping had landed, on the short-lived `docs/phase1-t419-t408-*` branches; the
actual implementation sat on `feature/T418-phase1-tb-delta-harness-v6.12.0`
(worktree `../worktrees/phase1-tb-delta`, commits `fb136c2`/`3ba46ca`), with no MR ever opened for it.
Fixed: dry-run merge in a disposable clone against `develop` — automatic merge, 0 conflicts, purely
additive (5 files, 1239 insertions, 0 modifications to existing files; the branch predates the
golden-suite merge, so a raw two-way diff against current `develop` misleadingly shows deletions for
files the branch's older base never had — a real three-way merge was performed, not just a diff
inspection, to confirm this). `python3 tests/run.py` on the dry-run-merged result: 367 tests, OK,
exit 0. The source worktree's untracked job-run debris (`docs/benchmarks/scorecards/`, `jobs/` — real
smoke-test/budget-guard-abort artifacts from T419/T408's own closeout) was confirmed uncommitted and
therefore not part of the branch's actual commits before merging, so it was correctly excluded by
construction, not filtered post hoc. Branch pushed, MR !203 opened, CI green
(`sync-no-diff`/`validation-super-gate`/`verify-knowledge-drift`/`unit-tests`/`markdown-links` all
passed), squash-merged to `develop` (merge commit `98c8d7d`, squash commit `f549401`). Re-verified
directly on `develop` post-merge: all five files present with expected content;
`git log --oneline -3 origin/develop` shows the merge. T407 and T409 are now genuinely unblockable —
not just ledger-unblockable.

**T416 closed (2026-08-14) — Phase 1 Layer 1 (T410-T416) complete.** Dispatched `tech-lead`
delivered `docs/artifacts/protected-paths-v1.md`, a pointer in all 27
`implementation/knowledge/agents/*.md` source files, regenerated platform projections and
`implementation/registry/`, and `tests/functional/test_protected_paths_declared.py` (10 tests).
The dispatched agent itself live-tested its own guard (removed the pointer from `tech-lead.md`,
confirmed the failure, restored, confirmed the pass) before reporting completion — matching this
phase's own "prove it live" standard, not merely asserting it.

Orchestrator independently re-verified rather than trusting the report: `grep -L` across all 27
agent source files confirmed none missing the pointer; every one of the 27 diffs checked directly
to confirm frontmatter (`tools:`/`name:`/`description:`) was never touched, only body Constraints
sections; `sync.mjs` re-run produced zero further diff; `generate-registry.py` re-run and its
`backend-developer.md` checksum entry cross-checked against an independently computed
`sha256sum` of the live file (exact match — the regeneration is real, not stale; only the
non-deterministic `generatedAt` timestamp differed, restored as noise matching this repo's
established content/`run_metadata` split pattern already used by `scripts/scorecard.py` and
`scripts/tb-delta.sh`'s own scorecards); independently reproduced the live-removal probe on a
**different** file (`qa-engineer.md`) than the one the dispatched agent had already tested
(`tech-lead.md`) — removed the pointer, confirmed the guard failed and named exactly
`qa-engineer.md`, restored it, confirmed `sha256sum` byte-identical to the pre-probe original, and
confirmed the guard passed again (10/10); confirmed `tests/golden/**`/`scripts/scorecard.py`
untouched (`git diff` empty, as required — this task declares them protected, it does not modify
them); ran `python3 tests/run.py` fresh (377 tests, up from 367 — the new guard file's own 10 tests
— exit 0); `git status` clean. Branch pushed, MR !205 opened, CI green, squash-merged to `develop`
(squash commit `dcad363`, merge commit `c9a9b5b`). See `completed-tasks.md` and `task-T416.md` for
full detail.

This closes plan-035's Phase 1 Layer 1 in full (T410-T416, all `done`, all genuinely merged to
`develop`). T407 and T409 (Layer 2) were already independently unblocked by the TB-delta harness
merge above and do not depend on T416 — both were eligible for dispatch throughout T416's own
execution and remain the only open work in this phase.

**CI rejection and fix (2026-08-13):** the first push of this branch failed CI (`unit-tests` job,
`tests/performance/test_team_health.py::TestTaskLifecycle` + the shipped `validate-tasks.py`
validator it wraps) on three independent, genuine defects, all fixed in this revision: (1) invalid
task IDs `T41A`/`T41B`/`T41C` (see "Task ID note" above); (2) a malformed `completed-tasks.md` row
— an escaped literal pipe (`` \| ``) in T410's entry text split into an extra table cell, because
the validator's table parser does a naive `split("|")` with no backslash-escape awareness; fixed by
rewording to avoid the literal character; (3) this file had rows for tasks with no corresponding
`task-<ID>.md` brief yet (`C7` — every ledger row must have its brief on disk already, not
JIT-deferred) — fixed by moving those to the non-table backlog list above until each is actually
dispatched with a real brief.

**T409 closed (2026-09-08) — Phase 1 complete, Gate G1 closed.** Dispatched `devops-engineer`
combined T407's two Harbor trajectory sources (local k=3 run, 150 trials; remote Design A's 3
successful passes on `10.10.160.11`, read via read-only SSH, not copied into the repo per T407's
own artifact-reconciliation decision) and extended `docs/artifacts/failure-taxonomy-v1.md` (new
§8) to classify genuine Terminal-Bench task-level failures (`exception_info: null`, `reward: 0.0`)
along the same three axes T415 defined for golden-suite failures, adding new axis values only
where no existing value fit without forcing it (2 of the resulting patterns reused existing
`behavior`/`mechanism` values unmodified). Infrastructure/harness failures (`AgentTimeoutError`,
the two fully-failed Design A attempts) were explicitly excluded and documented, not dropped.

**First pass (MR !215, commit `2535a54`) was not accepted as-is.** The orchestrator's independent
re-verification (re-deriving the same `exception_info`/`reward` extraction directly from raw
`result.json` files on both hosts, not trusting the dispatched agent's own counts) confirmed most
of the self-report exactly — 157 genuine failures (71 local + 86 remote), 57 infra-exclusions (38 +
19), and two spot-checked verbatim evidence quotes (`chess-best-move__76RBoFA` locally,
`custom-memory-heap-crash__kYz3evQ` on the remote host) matched the raw source byte-for-byte — but
also found a real, independently-verified gap the self-report did not disclose: the headline "157
failures across 17 task names" was the **local-source-only** task-name count, not the true union
across both sources (**21**, computed directly from raw data). Three genuine, non-infra failing
task names present only in the remote source — `caffe-cifar-10`, `rstan-to-pystan`,
`train-fasttext` (6 trials) — were absent from every pattern file and every summary count, with no
exclusion note. A smaller arithmetic error was also found (`failure-taxonomy-v1.md` §8.3 stated "45
local passes," the real figure is 41; the aggregate 86 was always correct). Not merged; sent back
to the same agent (continuing on the same branch/MR, not a new one) with the exact 3 trials, the
orchestrator's own independent read of their raw verifier output, and a specific fix scope.

**Second pass (same MR !215, commit `2f7927a`)** independently re-verified each of the 3 flagged
trials via SSH before acting (not taking the fix request's characterization on faith), confirmed
`rstan-to-pystan` and 3-of-4 `train-fasttext` trials fit already-existing patterns
(`incorrect-computed-output-value.md`, `required-output-artifact-absent.md` respectively — the 4th
`train-fasttext` trial has a genuinely different shape, a loadable-but-wrong-value model, and was
correctly split into `incorrect-computed-output-value.md` instead of forced into the same bucket as
its 3 siblings), and created a 6th pattern file
(`docs/benchmarks/failures/terminal-bench/verifier-crashes-on-missing-dependency.md`, new
`behavior`/`mechanism` pair) for `caffe-cifar-10`'s fatal in-process `SIGABRT` crash, which the
agent's own reasoning showed does not fit any of the other 5 patterns. Corrected every "17 task
name" reference to the real union (21, local=17/remote=20) and fixed the §8.3 arithmetic. Added a
new §8.6 documenting the gap and the fix, rather than silently rewriting the original narrative.

Orchestrator independently re-verified the fix pass end-to-end, not trusting the second
self-report either: re-checked the `train-fasttext` split and the new `caffe-cifar-10` pattern
file directly against raw `result.json`/`verifier/test-stdout.txt` on the remote host (exact
match); re-derived the 17/20/21 local/remote/union task-name arithmetic independently from raw
data (exact match); confirmed the 5→6 pattern count and 65→71 cited-trial-hash count arithmetically
(20+14+14+21+1+1 = 71); confirmed `python3 tests/run.py` fresh (377 tests, exit 0),
`tests/functional/test_golden_held_out_isolation.py` (8/8), and `git diff` against `develop` for
`tests/golden/**`/`scripts/scorecard.py` (empty, both passes) directly rather than trusting either
report; checked `docker ps -a`/`docker images` on the remote host directly (nothing dated after
2026-08-25, confirming no new Terminal-Bench trial/Docker/Harbor activity from either pass). CI
green on both pushes; MR !215 squash-merged to `develop` (squash commit `b96d1b9`, merge commit
`24781c1`). See `completed-tasks.md` and `task-T409.md` for full detail.

**This closes Phase 1 in its entirety (T410-T409, plan-035 §2.4) and Gate G1.** All ten of Phase
1's acceptance-criteria bullets are now independently verified met — see the note above the active
tasks table for the full gate-closure statement. `docs/tasks/active-tasks.md`: 0 active rows.
