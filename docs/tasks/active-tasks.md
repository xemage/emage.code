# Active Tasks

| ID | Title | Owner | Status | Priority | Depends on | Last update |
|----|-------|-------|--------|----------|-----------|-------------|
| T393 | Validation gate and merge to develop (plan-034) | tech-lead | pending | P0 | T391, T392 | 2026-08-10 |
| T382 | Execute repo-root update install (prove merge-safety + removal live) | devops-engineer | blocked | P0 | T381, T388, T393 | 2026-08-10 |

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
>
> **`docs/plans/plan-034-mcp-provenance-tracking.md`** (approved) designs and implements that
> provenance-tracking mechanism as `T389`-`T393` (ADR-002 design → implementation → tests → docs →
> validation gate), all currently `pending` above. `T382`'s `Depends on` column now includes `T393`
> (added alongside its already-satisfied `T381`/`T388`), and its brief (`task-T382.md`) gained a new
> Step 2b applying a one-time `--force-prune-keys e2b,redis,figma,notion` bootstrap-bridge invocation
> (per plan-034's Approach step 6) so this specific already-retired set finally prunes from this repo's
> own root once `T393` merges. `T382` remains `blocked` until `T393` merges — do not delegate it before
> then.
>
> `T389` (ADR-002 design) and `T390` (provenance sidecar + recursive pruning + bootstrap bridge
> implementation) are `done` — see `completed-tasks.md`. `T390`'s first implementation attempt
> literally implemented ADR-002 Decision §4 as originally written and found it structurally broken
> (checked key containment at the parsed file's top level, but every platform nests server names one
> level inside a per-format wrapper key — `servers`/`mcpServers`/`mcp` — so no real server key could
> ever be located/pruned); routed back to `solution-architect` as a `technical`/`critical` blocker, who
> corrected ADR-002 in place (commit `7de1a81`, pre-merge correction, not a supersession — ADR-002 had
> not yet reached `develop` or the `T393` gate) to a recursive tree-walk algorithm; `T390` then
> re-implemented against the corrected text and all tests passed.
>
> `T393`'s `Owner` field is `tech-lead` only (not `tech-lead, orchestrator` as its task brief specifies)
> while this row is in the active queue — `tests/performance/test_team_health.py`'s
> `test_task_owners_are_real_agents` only accepts single, known-agent-slug owner values for active-queue
> rows (it does not parse comma-separated multi-owner strings), matching the exact precedent `T375` hit
> and fixed the same way. The combined `tech-lead, orchestrator` attribution is restored once this row
> archives to `completed-tasks.md` (that file's rows are not checked by this test).

Per-task briefs live alongside this file as `task-T001.md`, `task-T002.md`, …
