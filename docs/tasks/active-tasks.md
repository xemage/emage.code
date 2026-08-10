# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T382 | Execute repo-root update install (prove merge-safety + removal live) | devops-engineer | blocked | P0 | T381, T388 | 2026-08-10 |

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
> **`T382` is `blocked`, not merely pending — a genuine, independently-verified structural blocker
> was found during a real (uncommitted, reverted) execution attempt on 2026-08-10.**
> `scripts/merge-mcp-json.py`'s merge algorithm treats any key present only in `dest` (the existing
> installed file) as permanently preserved — by design, this is what protects hand-added content like
> this repo's own `.vscode/mcp.json` `cwso` block. But it means the algorithm has no way to distinguish
> "hand-added, keep forever" from "previously generator-owned, now retired by the source template" —
> so it can **never** prune a key the generator has since removed (`e2b`/`redis`/`figma`/`notion`,
> removed from `implementation/knowledge/mcp/servers.yaml` by `T386`) from an **already-installed**
> root. Confirmed live: this repo's own root `.mcp.json` (and the other five `extended`-tagged
> mirror files) still contain all four retired server entries after a real `--update --platform all`
> dry-run-then-real execution against post-`T381`+`T388` `develop`; `.vscode/mcp.json`'s hand-added
> `cwso` block and `inputs` array were confirmed to survive correctly (the merge-safety half of the
> proof succeeds), but the server-removal half cannot succeed via `--update` as currently implemented.
> No file was committed for this attempt — the one incidental side effect (a `docs/` merge-tool note
> replacement) was reverted, leaving the working tree clean. This is an architecture-level gap (fixing
> it needs a key-provenance-tracking mechanism, e.g. a per-install manifest of generator-owned keys,
> to safely distinguish prunable retired keys from permanent hand-added ones) — resolving it is outside
> this task's original brief and requires new design work + a fresh task/plan cycle, not an ad hoc fix.
> See the full write-up in the orchestrator's final report for this execution run.

Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
