# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T609 | Remove the $ < { space skips and add the template-ref label to the scanner (E-S2) | backend-developer | pending | P2 | T608 | 2026-10-09 |

> **1 active row (`plan-114`).** T610 (naming edits plus the indentation cosmetic, MR !541) is done. T609 (scanner skip removal and `template-ref`, also carries the T608 review debt SEC-6..SEC-8) implements the user's decision of 2026-10-09 and needs a Security Engineer code review before merge, then one root refresh. Baseline v20; root drift 31 (declared by T608 and T610). T605 stays unscheduled.
> record.** `plan-064` Phase 10 is done, and it is the first task executed from the v8 roadmap.
> **5 agents promoted** (`backend-developer`, `context-retriever`, `devops-engineer`,
> `evaluation-agent`, `solution-architect`) — the agent category moves from 20/8 to **25 `stable` /
> 3 `experimental`**. The 3 that did not promote (`orchestrator`, `security-engineer`, `tech-lead`)
> each fail criteria **3 and 7** on a `known_failing`/`tracked_defect` golden case belonging to a
> command they own; each is a concrete, independently-actionable command-surface defect, and
> together they are the entire remaining distance to 28/28. **`plan-064` §1.3's hypothesis was
> confirmed but its count corrected upward, 4 → 5** — `backend-developer` was also available, missed
> because §1.3 drew on the Wave 2 artifact while that agent was a Wave 1 candidate blocked by the
> same already-resolved `T457` match. The implementer's own conflict of interest (`tech-lead` was
> one of the eight it evaluated) was actively controlled, not assumed away: the top-level session
> independently flipped `tech-lead` itself and confirmed the predicted `FAIL`; the implementer had
> reported its own failure honestly.

> **`T520` and `T521` scoped 2026-09-25** — executing `ADR-007`, `plan-064` Phase 9's critical path.
> Six verdicts split on **whether protected paths are involved**: `T520` (`P1`) takes A, B, D and H-1
> under a **file-scoped `protected-paths-v1.md` §5 authorization**; `T521` (`P2`) takes C, which
> touches none and therefore needs no authorization — keeping it separate keeps `T520`'s grant as
> narrow as §5.1 intends. H-2 needs no action now. **Neither task promotes anything**, though verdict
> D is expected to clear `security-engineer`'s last blocker: `T520` is `P1` and declares
> `command/security-audit`, so that component stays ledger-blocked until this row archives — the same
> sequencing `T515`/`T516` used. **Three of six cases are meant to stay red** (A, C, H-2); an
> implementer optimising for a green board would reclassify them, which `ADR-007` §5 names as evading
> branch 3b. Owner of `T520` is **Backend Developer** because it owns zero commands and one held-out
> case belongs to a `tech-lead`-owned command. See `docs/tasks/task-T520.md`,
> `docs/tasks/task-T521.md` and `docs/plans/plan-070-t520-t521-adr-007-execution.md`.

> **`T518` and `T520` closed 2026-09-25 — see `completed-tasks.md`.** **`T518`** fixed the recurring
> `install.sh --update` destruction, and the reported defect turned out to be the smaller half: the
> sweep was also deleting a target project's **entire `.github/workflows/` CI**, plus `CODEOWNERS`,
> `ISSUE_TEMPLATE/` and `dependabot.yml`. This repo uses GitLab CI so it never noticed; every
> downstream project on GitHub Actions would have. **`T520`** executed `ADR-007` verdicts A, B and D.
> Verdict B's replacement check was mutation-verified to pass the real pre-`T437` fixture while
> rejecting the old filename form, a missing heading and wrong ordering — the `_template.md`-derived
> trap was avoided. **H-1 was deliberately left incomplete**: its `expect.py` hardcodes the
> pre-amendment `v\d+\.\d+` regex, so the case cannot flip whatever the command says — the
> resolution artifact's claim that it "flips with no fixture change" is factually wrong. That file was
> not in the §1 authorization table and the implementer correctly refused to extend its own grant.
> **`security-engineer` is now measurably promotable to `stable`** — measured, not predicted — and
> `/security-audit`'s criterion 6 is confirmed cleared.

> **`T518` and `T519` scoped 2026-09-25** — the two carried defects `checkpoint-036` recorded
> without tasks. **`T518` (`P1`)**: `install.sh --update` deletes `.claude/settings.json` (`rsync
> -a --delete` with no exclude, while `.gemini` already has one at `install.sh:393`) and strips all
> prose from `active-tasks.md`, substituting the template's — which asserts the ledger starts empty
> and the first task is `T001`, **actively false** here with 316 completed. Reproduced: 65 lines → 11,
> false text 0 → 1, while `completed-tasks.md`'s 316 rows survive. Row preservation works; prose
> preservation does not exist. It is worst precisely when the ledger is *healthy* — with zero active
> rows there is nothing to preserve and the template wins. **`T512` hit both, hand-fixed them, and
> opened no task; `T517` hit both again verbatim.** A hand-fix plus a ledger note is not a fix.
> **`T519` (`P2`)**: `SECURITY.md:25` and `mcp-platform-contract-v1.md:87` still enumerate
> `${env:VAR}` for `claude-code`. The security *guarantee* still holds; only the enumeration is
> stale. The substantive part is that `-v1` is immutable, so it needs a `-v2`. See
> `docs/tasks/task-T518.md`, `docs/tasks/task-T519.md` and
> `docs/plans/plan-069-t518-t519-carried-defects.md`.

> **`T517` closed 2026-09-25 — see `completed-tasks.md`.** Fixed a defect in *shipped* output: the
> `claude-code` MCP emitter used VS Code's `${env:VAR}` placeholder, which Claude Code does not
> expand, so every generated `.mcp.json` carried literal placeholder text. `hindsight` and `cwso`
> failed visibly on an invalid URL; `gitlab`, `brave` and `toolradar` failed **silently**, receiving
> the literal string as a credential. **Proven by live MCP handshake**, not inference: the same
> variable connects under `${VAR}` and reproduces the exact reported error under `${env:VAR}`, and an
> unset-variable control shows the `env:` form is never parsed as a reference at all. Independently
> reproduced by the top-level session in its own isolated config dir before merge. `-v2` of the design
> artifact records the origin of the defect: v1 cited a hand-added `.mcp.json` as "empirically
> verified" when no running client had ever read it, so it attested to field *shape* only.

> **`T515` and `T516` both closed 2026-09-25 — see `completed-tasks.md` for the full closure
> records.** `T515` produced `ADR-007`: *a command's declared contract is authoritative over the
> corpus unless it contradicts a higher-authority document, or the dispute is only a label for
> content the corpus already carries — popularity is not authority.* Its verdicts are **not a clean
> sweep, deliberately**: 2 of 6 cases end green, 1 stops blocking, 3 stay red, so of the three
> `experimental` agents **only `security-engineer` promotes**. `T516` fixed the §3.5 matcher that
> made a brief's own mandated branch name indict its owner — defects are now declared in an
> `**Affects:**` field, mandatory at `P0`/`P1` and **fail-closed** (a missing field is exit 2 with no
> component report, never a quiet `PASS`). Every new `P0`/`P1` brief must now carry that field.
> **Neither task promoted anything**; acting on `ADR-007`'s verdicts is follow-up work that still
> needs a file-scoped `protected-paths-v1.md` §5 authorization, which `T515` itself did not require.

> **T514 dispatched 2026-09-24** — `plan-064` Phase 10, approved by the user for task-brief
> authoring. Re-runs promotion readiness for all 8 agents at `maturity: experimental`; `plan-064`
> §1.3's hypothesis is that four of them (`context-retriever`, `devops-engineer`,
> `evaluation-agent`, `solution-architect`) were blocked *solely* by `T456`/`T457`, both closed
> 2026-09-17. The brief treats that as a hypothesis to test, not a target to hit. **P2 is
> deliberate and disclosed**: the work genuinely is nice-to-have (it collects already-earned value
> and blocks nothing), and P2 also keeps this row out of criterion 7's open-defect scan — which at
> P0/P1 would block the very promotions the task exists to perform, the self-referential trap this
> repo has hit repeatedly. `check-maturity.py`'s own P2 filter was verified against the
> implementation before dispatch, not taken from the criteria document. See `docs/tasks/task-T514.md`
> and `docs/plans/plan-065-t514-dispatch-plan-coverage.md`.

> **`T522` opened and closed 2026-09-25 — see `completed-tasks.md`. `command/security-audit` is the
> repository's first `stable` command.** `plan-064` Phase 9's baseline was **0 of 19**; it is now
> **1 of 19**, and the agent category closes at **26 `stable` / 2 `experimental`**. This collects
> value already earned by `T516`, `T518` and `T520` — no new capability, no criteria weakened.
> **`T520` could not have done this itself**: it was `P1` and declared
> `**Affects:** command/security-audit`, so that component stayed blocked by criterion 3 until the
> row archived. Promotion inside `T520` was not merely undesirable, it was arithmetically
> impossible. `P2` here for the same reason `T514` was `P2` — a `P0`/`P1` row naming these
> components would re-enter criteria 3/7's open-defect scan and block itself. **Measured on two
> different `develop` HEADs, never predicted.** Two steps the "two one-line flips" framing missed,
> both caught by running the suite: `implementation/registry/` is generated and *does* carry
> `maturity:` (needs `generate-registry.py`; `sync.mjs --check` gives **no** signal, as the platform
> projections carry no `maturity:` field at all), and `test_check_maturity.py` hardcodes the tier
> distribution. **Conflict of interest disclosed**: the same actor measured and executed this, so
> `T514`'s second-party control was unavailable — replaced by a one-command reproducible gate
> stated in the brief. The **2 that remain `experimental`** (`orchestrator`, `tech-lead`) still fail
> criteria 3+7 on `ADR-007` verdicts **A** and **H-1**, which `T520` deliberately left red. H-1 is
> the nearer of the two and is blocked on a named authorization for one regex token in an
> `expect.py` under `tests/golden/**`. See `docs/tasks/task-T522.md`.

> **`T523` scoped 2026-09-25, backed by a measured readiness baseline.** Every `command/*` still
> at `experimental` was temporarily set to `stable` in a throwaway detached worktree and
> `check-maturity.py` was run — a probe that touches no protected path, since it edits only
> `implementation/knowledge/commands/*.md`. Result, recorded in
> `docs/artifacts/command-promotion-readiness-v1.md`: the 18 remaining commands split **cleanly into
> two groups with no overlap**. **4** are blocked by an open `tracked_defect` case (criteria 3+7);
> **14** are blocked *solely* by criterion 4 — no golden case exists for them at all, and they fail
> no other criterion, so one case each is sufficient rather than merely necessary.
> **`checkpoint-036`'s estimate of 14 is confirmed exactly**, for the first time by measurement
> rather than carry-forward. **Only 1 of the 4 is actionable**: `ADR-007` verdicts **A** and **H-2**
> are branch-3b outcomes that stay red until the corpus is fixed — making them green would mean
> reclassifying a real defect, which `ADR-007` §5 names as the thing not to do — and **C** belongs to
> `T521`. That leaves **H-1**, which `T523` takes under a **file-scoped
> `protected-paths-v1.md` §5 authorization** covering three files in one held-out case directory.
> `T520` amended the contract half already (branch 1, `AGENTS.md` § Artifact Versioning outranks the
> command); only the checker's pre-amendment regex remains, which `T520` correctly refused to touch
> because §5.1 forbids extending its own grant. **The case is identified mechanically, never by
> name** — `test_golden_held_out_isolation.py` Check B fails the build on any held-out case ID
> appearing outside `tests/golden/`, including in briefs, commit messages and this ledger. **A
> correction is recorded in §5 of the artifact**: an earlier claim in this session that H-1 was the
> nearer of the two remaining *agent* promotions was wrong. H-1 unblocks a **command**, not an agent;
> `orchestrator` and `tech-lead` are blocked by verdicts **A** and **H-2**, both deliberately left
> red, so neither agent promotion is near and neither is blocked on an authorization. **`T523`
> promotes nothing** — it is `P2`, declares `Affects: command/new-feature`, and that component stays
> criterion-3 blocked until the row archives. **`plan-070` assigned H-1 to `T520` on the theory
> that it needed only a `case.yaml` status flip; the resolution artifact's "flips with no fixture
> change" is correct about the fixture and wrong about the checker** — `plan-071` records that
> correction rather than quietly fixing it. See `docs/tasks/task-T523.md`,
> `docs/plans/plan-071-t523-adr-007-h1-completion.md` and
> `docs/artifacts/command-promotion-readiness-v1.md`.

> **`T523` and `T524` closed 2026-09-25 — see `completed-tasks.md`.** `T523` executed `ADR-007`
> verdict **H-1**, and `T524` collected the promotion it made available: **`command/new-feature` is
> `stable`, taking commands from 1 of 19 to 2 of 19.** The implementing agent hit the evaluator-hash
> tamper-evidence drift, **declined to fix it and escalated for human sanction unprompted** — it
> could have argued the fix was in scope, since `docs/artifacts/` is not a protected path. The
> orchestrator did not perform it on the agent's behalf either; the user authorized explicitly and
> `evaluator-hash-known-good-v3.json` followed, with v1 and v2 retained unmodified.
> **A correction, recorded rather than quietly fixed:** `task-T523.md` §6, `plan-071` §5, this
> ledger's own `T523` note and MR !383 all claimed `command/new-feature` stayed "criterion-3 blocked
> until the `T523` row archives" because that row was `P2` and declared
> `Affects: command/new-feature`. **That is backwards** —
> `implementation/scripts/check-maturity.py:504` filters the ledger-defect scan by priority, so a
> **`P2` row never blocks anything**, which is exactly why `T514` and `T522` chose `P2`. Confirmed by
> measurement with the row still `pending`. **No outcome changes**: the real blocker was criterion
> 3's *golden-case* clause, so `T523` was a genuine prerequisite and only the stated mechanism was
> wrong — but the two steps could have been one MR, which is what they are here. **Still open for
> `/new-feature`'s siblings:** `T520` left
> `tests/golden/open/new-feature-real-checkpoint-format-drift/brief.md` reading
> `known_failing / tracked_defect` while its `case.yaml` says `expected_pass` — found by the `T523`
> implementer, independently confirmed, outside its grant, **still needs a row.**

> **`T525` scoped 2026-09-25 — Phase 9's largest remaining piece, backed by
> `plan-072`.** The 14 commands blocked by criterion 4 alone are blocked by an *absence*, not a
> defect, and fail no other criterion, so one golden case each is **sufficient**, not merely
> necessary. **The hazard is the point:** an agent asked to author 14 cases that unblock 14
> promotions has every incentive to author 14 trivially-passing ones — the unearned promotion the
> ladder exists to prevent, and nearly undetectable afterwards, since a green board with 14 new
> cases looks like progress. Three controls: every case must **quote the specific contract clause**
> it tests, a **`known_failing` case is a correct outcome** (`ADR-007` §5 binds authoring exactly as
> it binds fixing), and **a wave where everything passes is a suspicious result, not a target** —
> `T515` used that framing and its honest answer was 2 green of 6. **Split into 3 waves by grounding
> strength; only wave 1 is scoped.** Waves 2 and 3 are deliberately left unscoped because wave 1
> tests the approach as much as it delivers: if its four cases come back thin or all green, the
> controls need revising before 10 more are authored against them. **A corpus probe run before the
> split changed it:** `/handoff` has 2 real artifact pairs plus a schema and validator, while the
> PoC three (`/new-poc`, `/poc-demo`, `/evaluate-poc`) have **zero** `POC-DEBT-SCORECARD.md` files
> anywhere in this repo — no corpus at all, which makes them hand-authored counter-examples
> (`ADR-007` branch 4) and puts them last. **The brief pre-schedules the evaluator-hash sanction**
> rather than letting the agent discover it: any authorized `tests/golden/**` change drifts the
> digest and turns 2 tests red, which `T523`'s brief failed to account for, making its acceptance
> criteria unsatisfiable as written. The refresh is explicitly **out of the agent's scope** — it
> reports the digests and stops. See `docs/tasks/task-T525.md` and
> `docs/plans/plan-072-phase9-golden-case-coverage.md`.

> **`T525` and `T526` closed 2026-09-25 — see `completed-tasks.md`.** Wave 1 delivered **3 green,
> 1 red**, and `T526` promoted exactly the three: **commands go from 2 of 19 to 5 of 19 `stable`**.
> **`/skillify` is deliberately not promoted.** All four were flipped to `stable` together to
> measure it, and its `known_failing` case blocked that one component on criteria 3 and 7 while the
> other three passed clean — **the ladder working as designed**, and the strongest available evidence
> wave 1's greens were earned rather than manufactured: the same authoring pass that produced them
> also produced a case that costs a promotion. **Three follow-ups now need rows.** (1) **`/skillify`
> contract conflict** — the command declares a five-section `SKILL.md` template that **0 of 26** real
> skill files satisfy, in both trees including the exact path it names, while the `skillify` *skill*
> declares a different template that 26 of 26 follow; two declared contracts disagree, which is
> precisely an `ADR-007` adjudication. (2) **`implementation/runtime/handoff/schema-v1.json` sets no
> `minItems` on `constraints.writablePaths`**, so a handoff declaring zero writable paths is
> schema-conformant — found by an orchestrator mutation attempt that was itself mis-designed, and a
> gap in the schema rather than in the golden case. (3) The still-stale
> `new-feature-real-checkpoint-format-drift` brief from `T520`, excluded from `T525`'s grant.
> **Waves 2 and 3 remain unscoped by design** — `plan-072` §3 held them back until wave 1 tested the
> approach, and it did: the control that did the work was requiring a **verbatim contract-clause
> quote before writing any `expect.py`**, which is what surfaced the `/skillify` conflict. The
> **mutation harness** the implementer built unprompted should become an explicit wave-2 deliverable.

> **`T527`–`T530` scoped 2026-09-25, backed by `plan-073`.** **A correction first, because it
> was found while scoping and it is in merged documents:** `T525`'s closure record says the real
> skill corpus **"uniformly follows"** the `skillify` skill's template and this ledger said **"26 of
> 26 follow"** it. **Overstated — the corpus follows neither template.** Measured across all 26 real
> `SKILL.md` files: **0 of 26** satisfy the *command*'s template completely, and **1 of 26** satisfy
> the *skill*'s. Per-section against the skill's: `## When to Use` 20/26, `## Purpose` 16/26,
> `## Procedure` 16/26, `## Examples` 9/26, `## Prerequisites` 2/26, `## Edge Cases` 1/26. **The
> `0 of 26` finding stands** — independently verified twice, the golden case's verdict is unaffected
> and `/skillify` correctly does not promote. What changes is the *shape of the adjudication*: not
> "a contract versus a well-formed rival corpus" but **two declared contracts and a corpus following
> neither.** **How it got through:** the orchestrator verified the *falsifying* claim (`0 of 26`)
> and not the *supporting* one (`26 of 26`) — a claim arguing against the proposal gets scrutiny, a
> claim merely colouring it slides past. Worth naming as a general way to be wrong.
> **`T527`** adjudicates under `ADR-007` and is the only one of the four that unblocks a promotion.
> Checked before scoping so it starts from evidence: **branch 1 does not fire** — `AGENTS.md` is
> silent on `SKILL.md` structure and no skills-format contract artifact exists. The live question is
> the *"only a label for content the corpus already carries"* clause, and it looks **only partly**
> satisfied: `## Trigger`≈`## When to Use`, `## Inputs`≈`## Prerequisites`, `## Steps`≈`## Procedure`
> read as branch **3a** (relabel), but `## Success Criteria` appears in 3/26 with no counterpart and
> reads as **3b** (omission). **So the honest verdict may be per-section, and a single tidy verdict
> is the suspicious outcome, not the target** — scoped as a hypothesis to test, never a conclusion
> to implement. Its protected-path grant is **conditional**: the `case.yaml` flip only if the verdict
> genuinely makes `check()` pass, and **`expect.py` is excluded** — changing it needs a wider grant
> and is a blocker, not a table edit. **`T528`** is wave 2, and carries forward the two controls wave
> 1 validated: **quote the verbatim clause before designing the check** (the ordering that surfaced
> the `/skillify` conflict), and a **mutation harness as a mandatory deliverable** — a check that
> cannot be made to fail is vacuous, and wave 1 showed it cuts both ways, catching a *mis-designed
> mutation* twice. **`T529`** and **`T530`** are the two carried defects from `T525`; they get rows
> rather than prose because `T518` established that **a hand-fix plus a ledger note is not a fix**.
> `T530`'s owner has **no `Bash`**, so its brief instructs an uncommitted hand-back rather than
> claimed verification. Wave 3 stays unscoped until wave 2 reports. See `docs/plans/plan-073-...md`.

> **`T527` closed 2026-09-25 — see `completed-tasks.md`. `T531`/`T532` scoped, `T530` widened, per
> `plan-074`.** The adjudication came back **per-section**, and its biggest finding **contradicts the
> brief**: `## Success Criteria` was never a command-vs-skill conflict — the `skillify` **skill**'s
> own Round 4 declares it verbatim and its final template drops it, so the **skill file contradicts
> itself**. **Three further corrections to this orchestrator's own documents**, all independently
> verified: the skill declares **seven** `##` sections not six (`## Guidelines` omitted); `plan-073`
> §1's "no skills-format artifact exists" is wrong (`maturity-promotion-criteria-v2.md` §2.1 mandates
> `## Rails`); and **every published corpus count was an upper bound** because the survey
> substring-matched whole files including fenced code blocks — fence-aware,
> `## Success Criteria` is **0/26** not 3/26, and **0 of 26** satisfy the skill's template, not 1.
> **The corpus satisfies neither contract — zero, both ways**; the bias ran toward conformance, so
> correcting it makes the case *more* firmly red. **Method rule: strip fenced blocks before
> surveying markdown headings.** `/skillify` correctly does **not** promote. **`T531`** re-derives
> the checker, which after `T527` asserts strings no document declares — a check nobody can trust is
> worse than a red case — and carries `T527`'s instruction that the substring operator be **kept**,
> since the risk there is **over**-strengthening, not relaxation. It also closes
> `## Required Context`, the identical self-contradiction, verified independently. **`T532`** takes
> the output-path defect: `.github/skills/` is a **generated** directory `AGENTS.md` says must not be
> hand-edited, and it hardcodes 1 platform of 7 — correct for an installed target project, wrong for
> this repo, so the real question is whether commands declare which audience they address. **`AGENTS.md`
> outranks a command file, so `ADR-007` branch 1 may genuinely fire there, unlike in `T527`.**
> `T532` depends on `T531` because resolving the path changes the fixture glob. **`T530` widened** to
> cover this case's now-stale `known_failing_reason` and `brief.md` — same defect shape, and `T527`
> could not fix it because its grant was conditional on a pass that did not occur.
> **The queue is 7 deep and that is stated, not hidden** — `plan-074` §3 records it. `T525`'s and
> `T527`'s findings are generating work faster than it is being executed, which is what good findings
> do, but the queue should be worked down before wave 3 is scoped. Recommended order: `T531`,
> `T528`, `T529`/`T530`, `T532` — and `T519`/`T521` must not be forgotten because newer work keeps
> arriving.

> **`T531` closed 2026-09-25 — see `completed-tasks.md`. `T532` is now unblocked.** The checker
> again describes the live contract; `/skillify` correctly still does **not** promote. **`T519` and
> `T521` are now the oldest open rows and have been passed over five times** while newer findings
> kept arriving — exactly the accretion `plan-074` §3 warned about. Both are being dispatched now,
> ahead of `T528`, on that basis. **Unresolved and needing an owner:**
> `docs/benchmarks/scorecard-v6.12.0.*` is committed at `total_cases: 20`, `generated_at:
> 2026-08-13`, while the live suite reports **24 cases / 16 pass** — both verified. Two subagents
> read the same file **oppositely**: `T525`'s as a frozen `T414` baseline publication (restored it;
> the orchestrator agreed at the time), `T531`'s as badly stale (proved its own change had zero
> effect by regenerating at the base commit and diffing). Both took the same action; they disagree on
> what the file *is*. Whichever is right, anyone reading it today gets wrong numbers.

> **`T519` and `T521` closed 2026-09-26 — see `completed-tasks.md`. `T533` scoped, per `plan-075`.**
> The two oldest rows are finally clear. **`T521` added a real operational gate, surfaced and
> explicitly authorized:** `verify-release-docs.py --tag v7.0.1` goes from **exit 0 to exit 1**, and
> **0 of 31** shipped release documents carry `## RELEASE VERDICT`, so the next tag cut fails until an
> author writes it. Tag pipelines only; ordinary CI untouched. **`T533` settles a disagreement this
> orchestrator got wrong.** `docs/benchmarks/scorecard-v6.12.0.*` is committed at `total_cases: 20 /
> total_pass: 11` while the live tree yields **24 / 16**. `T525`'s implementer read it as a frozen
> `T414` baseline and restored it — **the orchestrator agreed** — while `T531`'s and `T521`'s
> implementers independently called it stale. **`T531`/`T521` are right.** Three checked facts settle
> it: `scorecard.py`'s own docstring says `content` "is a pure function of the golden suite tree's
> on-disk bytes", so it is designed to **track**; **nothing validates the committed copy** — no test,
> no CI job; and it has **exactly one commit**, the original `T410`–`T415` landing, never updated
> while the suite grew 20 → 24. **Why the wrong reading was plausible, because the mistake is
> instructive:** one commit plus three tasks declining to touch it *looks* like a freeze policy, but
> those three declined because it was **outside their scope**, not because a policy existed — absence
> of updates was mistaken for a decision. *"Who validates this?"* is the question that distinguishes a
> frozen artifact from an unowned one. The concrete cost: every `scorecard.py` run rewrites the files,
> so **"expect a clean `git status`" is unreachable in any brief until this is fixed** — it has
> misfired three times, and three implementers each reverted `docs/benchmarks/` by hand.
> `T533` recommends **tracking it under a drift gate**, matching how this repo already gates
> `implementation/registry/` and the platform projections, with a narrow §5 grant for an **additive
> check mode only** in the protected `scripts/scorecard.py`.

> **`T533` closed 2026-09-26 — see `completed-tasks.md`. `T528`'s brief amended as a direct
> consequence.** The scorecard artifact is now **regenerated and gated**: it was a stale build
> output, and the clinching evidence was one `plan-075` missed — the committed file was **missing
> `model_tier`/`model_outcome` on all 20 rows**, schema fields added at `T443`. A frozen baseline is
> frozen at *some valid* schema; that one was frozen at a schema the script no longer emits.
> **`plan-075` §0's causal claim was wrong and is corrected on the record:** the recurring dirty
> `git status` was never caused by staleness but by `run_metadata.generated_at`, which differs every
> run by design — a run on the freshly-regenerated artifact still dirties both files. The fix was a
> **brief-authoring** change, and it has now been applied: verification blocks use the new read-only
> `scripts/scorecard.py --check`. **`T528`'s brief has been amended before dispatch**, because
> `T533`'s gate changes what that task must do: adding five golden cases now *fails* the drift gate
> until `docs/benchmarks/` is regenerated, so **regenerating and committing it is a required step of
> every future golden-suite task**, not a forbidden one — the opposite of the instruction three
> earlier tasks worked around. `T528`'s baseline is also updated to **792** tests, with an explicit
> note to measure it rather than trust the number, since three circulating baselines in this phase
> were all wrong at some point. **`scripts_scorecard` moved for the first time since v1** — its
> constancy across v1–v5 had been cited in five closure records as proof the script was untouched, and
> `-v6`'s `reason` field records that the chain ends there deliberately and under authorization so it
> is not misread as tampering.

> **`T528` and `T534` closed 2026-09-26 — see `completed-tasks.md`. Commands go from 5 of 19 to
> 9 of 19 `stable`.** Wave 2 delivered **4 green, 1 red**, and `T534` promoted exactly the four.
> **`/batch` is deliberately not promoted**: all five were flipped to `stable` together to measure,
> and its `known_failing` case blocked exactly that one component while the other four passed clean
> — **the second consecutive wave where that held**, after `T526`'s `/skillify`. *The same authoring
> pass that earned four promotions also cost one, twice running.* **`/batch`'s red is a real contract
> conflict**: `batch.md` step 5 declares a five-field manifest including `branch` to be written into
> `active-tasks.md`, which `AGENTS.md` pins to seven columns with no `branch` and whose validator
> hard-fails any other cell count — needs an `ADR-007` adjudication. **Four defects now need rows,
> queued for the next step and listed here so they are not lost:** (1) `/batch`'s schema conflict;
> (2) `/sprint-status` declares no colour for `in_review` though step 8 requires four node sources;
> (3) **`validate-tasks.py:203` discards the `Depends on` cell**, so a dangling dependency passes
> `PASS` silently; (4) the `skillify` case's `brief.md` now contradicts its own `expect.py` after
> `T527`/`T531` — same defect class `T530` already tracks, and the natural home for it.
> **Three corrections to this orchestrator's own brief are recorded in `T528`'s row**, the sharpest
> being that brief §5 cited evaluator-hash `-v4` when `-v6` was current: because `T533` deliberately
> moved `scripts_scorecard`, a literal reader of that instruction would have **misdiagnosed a clean
> repo as tampered**.

> **`T535`–`T537` scoped 2026-09-26 per `plan-076`; the fourth wave-2 finding folded into `T530`.**
> All four defects wave 2 surfaced now have owners rather than a ledger note — `T518`'s rule that **a
> hand-fix plus a ledger note is not a fix**. **`T535`** adjudicates `/batch`: `AGENTS.md` outranks a
> command file so `ADR-007` branch 1 may fire, **but branch 1 firing does not say *how* to amend** —
> a batch of parallel units plausibly needs somewhere to record branches, so "delete the requirement"
> may be the wrong repair even if the contract is what must change. The brief deliberately withholds
> a preferred answer and states that reaching "drop `branch`" *on the merits* is a good outcome while
> reaching it *because it was the smallest edit* is not. **`T536`** closes a gap worth recording as a
> limitation of the ladder, not just of the command: **`/sprint-status` was promoted to `stable` by
> `T534` while carrying it.** Step 8 requires four node sources and declares three non-`done`
> colours, so an `in_review` node must be drawn and cannot be coloured — and its only golden case
> **cannot reach the gap**, since that fixture's four rows are all `pending` and its lone `in_review`
> occurrence is the status-legend line, not a data row (verified). The case is honest and the criteria
> were met, so this is **not** grounds to un-promote — but it means **`stable` certifies "passes the
> cases that exist", not "has no known contract gaps"**, and this is the first concrete instance where
> those differ. Whether to extend the case is posed to `T536` as a separate question it must answer
> rather than assume, with no `tests/golden/**` grant. **`T537`** adds the dangling-dependency check
> `validate-tasks.py:203` never had — it destructures `Depends on` into `_`. Two traps written in: a
> satisfied dependency legitimately points into `completed-tasks.md` (`T532` → completed `T531`), so
> resolving only against the active ledger would flag every satisfied edge; and **a false positive
> there blocks all work**, since that validator gates every ledger edit and runs in CI.

> **`T529`, `T536` and `T537` closed 2026-09-26 — see `completed-tasks.md`. `T538`–`T540` scoped per
> `plan-077`.** All three were dispatched in parallel, chosen as the only three of six with **zero file
> overlap**. **A governance precedent was set and user-ratified in `T529`:** `AGENTS.md`'s
> artifact-immutability rule governs **`.md` deliverables under `docs/`**, not runtime JSON contracts
> whose filename is a wire-protocol identifier — so `implementation/runtime/handoff/schema-v1.json`
> was edited **in place**, contradicting this orchestrator's own brief steer and the rule it had
> enforced four times this phase. Five premises verified: the rule text is literally `.md`-scoped; **no
> `-v2` exists anywhere outside `docs/`**; `benchmark-thresholds-v1.json` has three in-place
> revisions; both real payloads name the schema **in-band** so a rename orphans them; and a rename
> would strand `handoff-security-model-v1.md`, a genuine immutable docs artifact hardcoded in
> `check.py`. **Stop steering briefs toward `-v2` for runtime schemas.** **Two further corrections to
> this orchestrator's own work**, both recorded in the closure rows: the brief listed seven emittable
> validator codes when **all of `C1`–`C11`** are emittable, and an earlier diagnosis that a failed
> mutation was merely "mis-designed" was **half wrong** — the golden `expect.py` implements **zero
> array keywords**, so that mutation could never have flipped at any schema version. **Three new
> findings now have rows:** `team-status.md` carries the identical `in_review` gap in a weaker form
> (no `Color code:` bullet at all); **no guard anywhere in `tests/golden/**` detects array
> cardinality**, so write-scope emptiness is covered only by `T529`'s new functional tests; and
> `validate-tasks.py` detects neither self-dependency nor cycles, both cheap additions inside `C12`'s
> shape. Also found: **`validator.py` never loads `schema-v1.json`** — it re-implements the rules, so
> any future handoff-schema change must patch the validator too or have no runtime effect.

> **`T540` closed 2026-09-26 — see `completed-tasks.md`.** The ledger validator now carries `C13`
> (self-dependency) and `C14` (cycles), and the suite is at **824 tests**. **A session rate limit
> (HTTP 429) terminated both dispatched agents mid-task this round** — `T540`'s and `T535`'s. Neither
> reported, but **`T540`'s worktree was not empty**: its last emitted line was "Now the patch" while
> it had already written a complete, uncommitted, entirely unverified patch. The lesson is procedural
> and now recorded: **always check a dead agent's worktree before re-dispatching.** That work was
> reviewed as *unverified partial work rather than a delivered result*, verified across seven graph
> shapes — including the **diamond** case a naive cycle detector fails — and committed with the
> provenance stated in both the commit message and MR !405. **`T535` produced nothing and still needs
> dispatching from scratch**; its worktree is clean and waiting. **`T538` was deliberately held** last
> round because it collided with `T535` on `implementation/knowledge/commands/`, and that collision no
> longer exists while `T535` is not in flight — but the two must still not run concurrently, since
> both regenerate `registry/index.json` and the platform projections. **`T538`'s central question is
> pre-answered:** a grep for the shared Mermaid block finds exactly **two** copies, `sprint-status.md`
> (already fixed by `T536`) and `team-status.md`. **There is no third instance** — so this is two
> instances of a copied section, not an unbounded pattern.

> **`T535` closed 2026-09-26 — see `completed-tasks.md`. `T541`/`T542` scoped per `plan-078`.**
> `ADR-007` branch 1 fired **twice** on `/batch`, against two different higher authorities, and the
> amendment **deleted nothing** — all five of step 5's declared fields survive with exactly one home
> each. **Three of this orchestrator's own claims were wrong** and are corrected in the closure row:
> the conflict was never only step 5 (**step 3 carries an independent branch-1 defect against the
> `stable` `git-workflow.md`**, and the case's `expect.py` actively asserts the wrong form); the
> "branch may be derivable" option was **unsound as stated**, since under the old step 3 the branch
> was a function of nothing on the ledger; and **`Depends on` was backwards** — not dead weight
> crowding out `branch` but the column `/batch` most needs, being the only enforcement home for step
> 2's independence, now validated by `C12`/`C13`/`C14`. **The refusal worth remembering: branch 4
> would have cleared the promotion criterion today with no command edit at all, and was refused on
> branch 4's own stated condition.** `/batch` does **not** promote; the amendment makes its contract
> *harder* to satisfy. **`T542` is the one to read twice**: `orchestrator.md` tells the orchestrator
> to *"commit directly to develop (docs-only changes exempt)"*, which `git-workflow.md` — `stable`,
> `applyTo: "**"` — flatly forbids, **and which the remote has already rejected twice**, a precedent
> `git-workflow.md`'s own Recovery Procedure records verbatim. So an agent file instructs an action
> that cannot work, in exactly the change classes an orchestrator handles most. `T541` and `T542` do
> not collide and may run in parallel, but **neither may run alongside `T538`**, which also contends
> for the registry and projections.

> **`T541` and `T542` closed 2026-09-26 — see `completed-tasks.md`. `T543`/`T544` scoped per
> `plan-079`.** **`T542`'s substantive finding: the defect was three encodings in one section, not the
> two lines that this orchestrator, `plan-078` and `T535` all located.** Beyond the explicit grant,
> line 91's *"MANDATORY before any **code** commit"* excluded docs **by wording**, and lines 102–103's
> *"NEVER commit … **for feat/fix/refactor/test work**"* excluded them **by omission** from an
> enumerated list. **A bare deletion would have left the exemption standing.** Generalisable: when
> removing a permission, check whether the surrounding framing sentence and any enumerated guard
> re-grant it by wording or by omission. **`T541` proved the superseded checker was unfalsifiable
> rather than asserting it** — the old `expect.py` run against the *fully conforming* new fixture also
> returns `False` — and answered the sibling-corollary question `T535` deliberately left, on an
> argument neither brief nor spec contained: **the pre-amendment ledger row for a batch unit was never
> an instantiable artifact, and an amendment cannot change the class of an artifact that had no
> instances.** It also **corrected a claim this orchestrator made twice**: the fixture's ledger Titles
> read `BATCH <slug> U<n>: …`, so **the abolished `U<n>` scheme survived inside the evidence offered
> for its own abolition** — literally "already prefixed", but misleading as evidence of conformance.
> **`T543` is the systemic one.** The repo-root projections are refreshed by **no generator** and
> checked by **no gate**: `sync.mjs` writes only under `implementation/`, and `sync.mjs --check`
> reports "no drift across 577 files" regardless — so **`.claude/agents/orchestrator.md`, which the
> running orchestrator actually reads, still carries the defect `T542` just fixed.** 5 of 19 root
> command projections already differed before `T536`. It is asked the prior question first — **is root
> drift a defect at all**, or is that tree a target-project artifact that is *supposed* to lag? —
> because those are different repairs and it must pick one. **The queue has held at 6 for three rounds**
> and `plan-079` §3 names why: every task is instructed to report rather than work around, so each
> round closes two or three and surfaces two or three. That is the system working, not drift — but the
> phase will not converge by executing findings alone, and the remaining items should eventually be
> triaged for whether they are worth doing at all. `T544`'s case-id rename is the first candidate for
> **correctly declined**, and its brief says so.

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done` · `cancelled`
> Priority values: `P0` (critical path) · `P1` (important) · `P2` (nice-to-have)
> Owners are agent names from `knowledge/agents/`.

> This is not a fresh project — **319 real tasks (`T001`-`T522`)** have already run to completion;
> see `docs/tasks/completed-tasks.md` for the full archive and `docs/checkpoints/` for phase-boundary
> summaries, most recently `checkpoint-036-phase9-partial-and-mcp-syntax-fix.md`. Do not treat a
> short table as "no history exists" — it means little is currently in flight.

Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
