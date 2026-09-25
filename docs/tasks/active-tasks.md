# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T518 | Stop `install.sh --update` destroying local settings and ledger prose | devops-engineer | pending | P1 | — | 2026-09-25 |
| T519 | Correct the two documents still stating the pre-T517 placeholder syntax | technical-writer | pending | P2 | — | 2026-09-25 |

> **2 active rows (`T518`, `T519`). `T514` closed 2026-09-24 — see `completed-tasks.md` for the full closure
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

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done` · `cancelled`
> Priority values: `P0` (critical path) · `P1` (important) · `P2` (nice-to-have)
> Owners are agent names from `knowledge/agents/`.

> 0 active rows. This is not a fresh project — 511 real tasks (`T001`-`T511`) have already run to
> completion; see `docs/tasks/completed-tasks.md` for the full archive and `docs/checkpoints/` for
> phase-boundary summaries, most recently `checkpoint-release-v7.0.0.md`. Do not treat an empty
> table as "no history exists" — it means no task is currently in flight.

Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
