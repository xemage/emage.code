# Checkpoint — Release v6.10.0

> Filename: `checkpoint-release-v6.10.0.md`
> Written at the release phase boundary.

## Phase summary
Minor, release-only cycle. No new implementation work performed in this cycle — the tasks this
release packages (T368-T393, T382: plan-031 installer merge-safety pilot, plan-032
`render_installed_agents.py` Cline fix, plan-033 MCP settings hardening, plan-034 merge provenance
tracking + ADR-002) were already fully complete and merged to `develop` prior to this release. This
phase only packages and ships that already-done work: release docs, marker updates, verification,
tag, and publish. Per this session's established pattern (T337/T342/T347/T350/T358/T366), landed
via a branch + MR — no direct commits to `develop`.

## Completed work (this cycle)
| ID / Commit | Type | Summary |
|--------|------|---------|
| T394 | docs | Updated `Latest release: v6.9.0` → `v6.10.0` marker in `README.md`, `docs/wiki/README.md`, `docs/wiki/home.md` |
| T394 | docs | Authored `docs/releases/v6.10.0.md` (Install + Highlights + Breaking changes + Internal) |
| T394 | docs | Authored this checkpoint |
| T394 | docs | Created task briefs `docs/tasks/task-T394.md`, `docs/tasks/task-T395.md`; added both rows to `docs/tasks/active-tasks.md` |

Prior cycle work being shipped in this release (already merged to `develop`, not redone here):
| ID | Type | Summary |
|----|------|---------|
| T368-T372 | feat/test/docs | plan-031: installer MCP JSON merge-safety pilot (`.vscode/mcp.json`/`.mcp.json`); MR !158 |
| T373-T376 | fix/test/docs | plan-032: `render_installed_agents.py` `all`-platform literal-string bug (Cline omitted since v6.8.0); MR !161, !162 |
| T377-T381 | feat/test/docs | plan-033 P033-01/02/03/04/05: merge-safety extended to remaining 5 platforms; MR !164 |
| T383 | test | plan-033 P033-07: literal-secret guard for generated MCP/settings output; MR !168 |
| T384 | test/docs | plan-033 P033-08: schema validation for Gemini/Opencode + manual checklist for the other 5; MR !169 |
| T385 | docs | plan-033 P033-09: Pi MCP-format research closed with an explicit reasoned decision; MR !170 |
| T386-T388 | chore/docs | plan-033 P033-10/11/12: removed `e2b`/`redis`/`figma`/`notion` server entries; MR !166 |
| T389-T393 | docs/feat/test | plan-034: ADR-002 + `<mcpfile>.provenance.json` sidecar mechanism + `--force-prune-keys` bridge; MR !172 |
| T382 | chore | plan-033/034 final proof point: root self-install merge-safety + server removal both confirmed live; MR !174 |

**Excluded from this release's notes (verified, not assumed):** T360-T365 (plan-030, MCP remote
transport alignment) was already shipped as `v6.9.0` — confirmed against `docs/releases/v6.9.0.md`
and the `v6.9.0` tag's own content before writing `v6.10.0.md`, so it is not re-listed as new here.

## Open / carried over
| ID | Title | Owner | Status | Notes |
|----|-------|-------|--------|-------|
| — | — | — | — | none open at time of writing |

## Key decisions
- **Version bump: MINOR (v6.9.0 → v6.10.0).** Per the user's explicit request. Classification:
  Highlights/Fixed + Highlights/Removed + Highlights/Hardened (multiple user-visible items: the
  installer merge-safety protection, the Cline platform-map omission fix, the explicit server
  removal, and the secret-guard/schema-validation hardening), not Internal-only — several of these
  change observable behavior of `--update` for any existing consumer.
- **Breaking changes: None.** Verified: the merge-safety change only replaces destructive overwrite
  with safe merge (strictly additive protection, nothing could have depended on the old
  data-loss-on-update behavior as a feature); the new provenance sidecars are new files alongside
  existing output, not replacements; `--force-prune-keys` is opt-in only and never triggered by a
  plain `--update` (confirmed in `docs/wiki/mcp-servers.md` § "Provenance-aware merge on
  `--update`" — first post-upgrade `--update` prunes nothing). Confirmed via `sync.mjs --check` (0
  drift) and full test suite green.
- **plan-030 (T360-T365) explicitly excluded from v6.10.0's release notes** — already shipped in
  v6.9.0. Re-listing it here would misrepresent the changelog; caught by verifying directly against
  `docs/tasks/completed-tasks.md` and the existing `v6.9.0` tag rather than trusting the release
  task brief's initial framing at face value.
- Tagging on `develop` via a `docs/release-v6.10.0` branch, consistent with the
  T337/T347/T350/T358/T366 precedent. The `release/v6.10.0 → main` sync is a separate follow-up
  task (T395), using the PUT-first merge procedure from `CONTRIBUTING.md` (4/4 successful as of
  T367: MR !126, !134, !151, !156).
- No deprecations.

## Token metrics
- Release phase budget: ≤ 60k tokens (per AGENTS.md Token Governance). This cycle is
  docs/verification-only, well within budget.

## Artifacts produced
- `docs/releases/v6.10.0.md` (Install + Highlights + Breaking changes + Internal)
- `docs/checkpoints/checkpoint-release-v6.10.0.md` (this file)
- Release markers updated: `README.md`, `docs/wiki/README.md`, `docs/wiki/home.md`
- `docs/tasks/task-T394.md`, `docs/tasks/task-T395.md`, `docs/tasks/active-tasks.md` (T394/T395 rows)

## Next steps
1. Run the full local verification bar (`make verify`, `generate-registry.py --check`,
   `validate-tasks.py`, `tests/run.py`, `sync.mjs --check`).
2. Push `docs/release-v6.10.0`, open MR → `develop`, watch CI green, independently re-verify diff,
   merge.
3. Tag `v6.10.0` on `develop`'s new tip, push tag, watch tag pipeline to green.
4. Independently confirm the GitLab Release via API.
5. T395: `release/v6.10.0 → main` sync via the PUT-first sequence; independently re-verify ancestry.
6. Phase 3: sync local `develop`/`main`/tags with origin; clean up merged session branches.
