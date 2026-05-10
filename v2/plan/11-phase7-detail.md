# 11 — Phase 7 detail: Cross-platform parity & CI

> Backfill of the v1 Phase-7 placeholder. v2 reframes "platform parity" as a build-system concern, not a content concern.

## Goal
The four supported platforms — GitHub Copilot, Gemini CLI, Opencode, Cursor — receive functionally equivalent emage.code installations. Drift between `knowledge/` and the generated platform folders is detected automatically.

## Mechanism

| Capability | Implementation |
|-----------|----------------|
| One source of truth | `knowledge/` |
| Per-platform projection | `platforms/<name>.json` + `scripts/sync.mjs` |
| Drift detection | `scripts/verify.mjs` (CI) |
| Reviewer visibility | `.generated-manifest.json` per platform folder |
| Determinism | placeholder `generatedAt`, sorted file lists, byte-stable JSON serialization |

## Parity matrix

| Feature | GitHub | Gemini | Opencode | Cursor |
|---------|--------|--------|----------|--------|
| 27 agents | ✓ | ✓ | ✓ | ✓ |
| 16 commands | ✓ | ✓ | ✓ | ✓ |
| 22 skills | ✓ | ✓ | ✓ | ✓ |
| 4 instructions | ✓ | ✓ | ✓ | ✓ |
| Core MCP servers (7) | ✓ | ✓ | ✓ | ✓ |
| Extended MCP servers (12) | — | ✓ | ✓ | ✓ |
| Hooks (post-edit reminder) | ✓ (file) | ✓ (settings.json) | — | — |
| Auto-approve terminal | ✓ (`.vscode/settings.json`) | — | — | — |

## CI

`.github/workflows/verify-knowledge.yml` runs `node scripts/verify.mjs` on every PR. Non-zero exit fails the check. Authors must run `node scripts/sync.mjs` and commit the regenerated platform folders before merge.

## Smoke tests (manual)

For each platform the maintainer runs in a throwaway scratch project:

```
/new-feature "add a /health endpoint"
```

Expected: orchestrator drafts a plan referencing `docs/plans/plan-…md` and waits for approval. Failure indicates platform-specific projection is broken — inspect the corresponding `platforms/<name>.json`.

## Acceptance criteria
- [ ] `verify.mjs` exits 0 immediately after `sync.mjs`.
- [ ] CI workflow committed and green on the v2 introduction PR.
- [ ] Smoke test passes on all four platforms.
- [ ] `.generated-manifest.json` lists exactly the expected file count per platform (cursor 70, gemini 70, github 71, opencode 70 at v2.0).
