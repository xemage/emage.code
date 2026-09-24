# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T515 | Decide contract authority for the six tracked-defect golden cases | solution-architect | pending | P1 | — | 2026-09-24 |
| T516 | Narrow the §3.5 defect-check from free-text scan to a declared field | backend-developer | pending | P2 | — | 2026-09-24 |
| T517 | Emit Claude Code's own env-placeholder syntax in the generated MCP config | devops-engineer | pending | P1 | — | 2026-09-24 |

> **3 active rows (`T515`, `T516`, `T517`). `T514` closed 2026-09-24 — see `completed-tasks.md` for the full closure
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

> **T516 scoped 2026-09-24** — fixes a defect in the promotion gate itself, found while drafting
> `T515`'s brief. `_ledger_defect()` regex-scans the whole body of every active `P0`/`P1` brief for
> component ids, so a brief that spells out its mandated branch name (`agent/<slug>/<id>`) or cites
> an instruction by filename (`.claude/rules/*.md`) **indicts the component it merely mentions**.
> Both failures were hit on `T515`'s first draft and confirmed by running the script, not by reading
> the regex. Latent until `T514` took the `stable` population to 25 agents + 4 instructions +
> 7 skills — false matches only bite components that have a claim to fail. Fix is a declared
> `Affects:` field, **mandatory on `P0`/`P1` briefs with a missing field failing loudly**: the
> tempting "absent field means affects nothing" fallback would turn a loud false positive into a
> silent false negative, which is worse than the bug. `P2` is honest — the defect makes the gate
> over-strict, never under-strict, so nothing is mis-promoted. Migration surface is **one brief**
> today and grows with every future `P0`/`P1` row. See `docs/tasks/task-T516.md` and
> `docs/plans/plan-067-t516-defect-check-declared-field.md`.

> **T515 dispatched 2026-09-24** — `plan-064` Phase 9, first task. Decides which side of six
> command-contract-vs-corpus conflicts is authoritative; these six `tracked_defect` golden cases are
> the entire remaining distance from 25/3 to **28/0** in the agent category, and they also block
> their own commands. **Deliberately read-only and deliberately not an implementation task**:
> scoping found each defect case is one half of a *zero-sum pair* — every affected command also has
> a sibling `expected_pass` case whose `expect.py` encodes the same contract against an opposite
> fixture, so amending a contract to match the real corpus relocates the failure instead of removing
> it. That is judgment, not code, so it is settled first, on its own, without touching the protected
> `tests/golden/**` tree. Owner is **Solution Architect** because it owns zero commands, while three
> of the four agents owning the affected commands are the same agents a favourable resolution would
> promote. `P1` is honest (this blocks Phase 9); the §3.5 self-reference trap is handled by
> display-name phrasing verified against `check-maturity.py`, not by priority-gaming. See
> `docs/tasks/task-T515.md` and `docs/plans/plan-066-t515-command-contract-authority.md`.

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
