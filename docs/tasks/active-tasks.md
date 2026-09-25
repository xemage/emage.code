# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T517 | Emit Claude Code's own env-placeholder syntax in the generated MCP config | devops-engineer | pending | P1 | — | 2026-09-24 |

> **1 active row (`T517`). `T514` closed 2026-09-24 — see `completed-tasks.md` for the full closure
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

> **T517 scoped 2026-09-24** — a defect in shipped output, found from a user report that the
> `hindsight` MCP server would not start. Not a user misconfiguration: the env var is set and the
> generated config is wrong. `sync.mjs`'s `claude-code` emitter renders env references with VS Code's
> `${env:VAR}` placeholder, which Claude Code does not expand, so `.mcp.json` ships literal
> placeholder text. **The visible half is the smaller half**: `hindsight` and `cwso` fail loudly
> (invalid URL), but `gitlab`, `brave` and `toolradar` take `fromEnv` in `env` and fail *silently* —
> the process starts, the client reports healthy, and a literal `${env:...}` string is handed over as
> a credential. Three of the five are `core`, so this reaches **every** downstream install of this
> platform. The suite did not catch it because the suite encodes it (two tests + the design artifact
> all specify the wrong template), which is why the brief makes a **live reconnect**, not a green
> suite, the decisive acceptance criterion. Only `claude-code` is proven wrong; the brief explicitly
> forbids "fixing" the other five emitters. See `docs/tasks/task-T517.md` and
> `docs/plans/plan-068-t517-claude-code-mcp-placeholder-syntax.md`.

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
