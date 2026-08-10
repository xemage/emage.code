# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T382 | Execute repo-root update install (prove merge-safety + removal live) | devops-engineer | pending | P0 | T381, T388, T393 | 2026-08-10 |

> Status values: `pending` · `in_progress` · `blocked` · `in_review` · `done` · `cancelled`
> Priority values: `P0` (critical path) · `P1` (important) · `P2` (nice-to-have)
> Owners are agent names from `knowledge/agents/`.
>
> `T377`-`T388` (plan-033, MCP settings hardening): `T377`-`T381` (core merge-safety fix + validation
> gate) merged to `develop` via MR !164 (squash `02b42f0`, merge `453ffb2`); `T386`-`T388` (server
> registry removal + validation gate) merged via MR !166 (squash `0d5f9bc`, merge `f1ebfbf`);
> `T383`-`T385` (secret guard, runtime verification checklist, Pi format decision) merged via MR !168,
> !169, !170 respectively — see `completed-tasks.md` for all of these.
>
> **`docs/plans/plan-034-mcp-provenance-tracking.md`** (approved) designed and implemented a
> provenance-tracking mechanism for `scripts/install.sh --update`'s MCP/settings merge, closing the
> structural gap found during an earlier, reverted `T382` execution attempt on 2026-08-10 (the merge
> could preserve hand-added keys like this repo's own `.vscode/mcp.json` `cwso` block but had no way to
> ever prune a key the generator had since retired, e.g. `e2b`/`redis`/`figma`/`notion` removed by
> `T386`). `T389`-`T393` (ADR-002 design → implementation → tests → docs → validation gate) are all
> `done` — see `completed-tasks.md` for full detail, including a real pre-merge correction to ADR-002's
> pruning algorithm (nesting-level fix, commit `7de1a81`) found and fixed during `T390`'s first
> implementation attempt. `T393` merged plan-034 to `develop` via MR !172 (squash `94a19ed`, merge
> `8343aea`); verification bar re-confirmed green on the fresh `develop` tip.
>
> `T382` is now `pending` (no longer `blocked` — its `T393` dependency is satisfied). Its brief
> (`task-T382.md`) already carries the `Depends on: T381, T388, T393` update and a Step 2b bootstrap-
> bridge invocation (`--force-prune-keys e2b,redis,figma,notion`, or whatever flag name the actually-
> merged `scripts/merge-mcp-json.py --help` exposes) needed to finally prune those four already-retired
> servers from this repo's own root self-install mirror.

Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
