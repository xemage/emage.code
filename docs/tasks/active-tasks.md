# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T519 | Correct the two documents still stating the pre-T517 placeholder syntax | technical-writer | pending | P2 | — | 2026-09-25 |
| T521 | Execute ADR-007 verdict C: give RELEASE VERDICT a declared home | release-manager | pending | P2 | — | 2026-09-25 |
| T523 | Execute ADR-007 verdict H-1: align the held-out checker with the amended contract | backend-developer | pending | P2 | T520 | 2026-09-25 |

> **3 active rows (`T519`, `T521`, `T523`). `T514` closed 2026-09-24 — see `completed-tasks.md` for the full closure
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

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done` · `cancelled`
> Priority values: `P0` (critical path) · `P1` (important) · `P2` (nice-to-have)
> Owners are agent names from `knowledge/agents/`.

> This is not a fresh project — **319 real tasks (`T001`-`T522`)** have already run to completion;
> see `docs/tasks/completed-tasks.md` for the full archive and `docs/checkpoints/` for phase-boundary
> summaries, most recently `checkpoint-036-phase9-partial-and-mcp-syntax-fix.md`. Do not treat a
> short table as "no history exists" — it means little is currently in flight.

Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
