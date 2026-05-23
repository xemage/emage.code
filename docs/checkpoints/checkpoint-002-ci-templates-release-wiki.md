# Checkpoint 002 — CI Templates, Release Workflow & Wiki Sync

**Phase:** setup → developer-experience hardening
**Date:** 2026-05-10
**Branch:** `develop`
**Pipeline:** [#2514104901](https://gitlab.com/em-age/emage.code/-/pipelines/2514104901) — all 4 jobs green
**Merge request:** [!1](https://gitlab.com/em-age/emage.code/-/merge_requests/1) — squash-merged

## Completed

| Task | Outcome |
|------|---------|
| Issue templates | `.gitlab/issue_templates/{Default,Bug,Feature}.md` |
| MR templates | `.gitlab/merge_request_templates/{Default,Release}.md` |
| Release workflow | `release` CI stage triggered by `vX.Y.Z` tag pushes; uses [git-cliff](https://git-cliff.org) (`cliff.toml`) to generate `CHANGELOG.md` from Conventional Commits, then creates a GitLab Release via the API. `CHANGELOG.md` seeded in Keep-a-Changelog format. `CONTRIBUTING.md` "Releasing" section added. |
| Wiki auto-sync | `wiki-sync` CI stage runs on `develop` when `docs/wiki/**` changes. `scripts/sync-wiki.py` upserts each `.md` via the Wiki API; supports YAML-frontmatter `title:` overrides for acronyms (`MCP Servers`) and version numbers (`Migration v1 to v2`). |
| Link checker hardening | Now strips fenced and inline code spans before scanning, so `` `[Quick Start](quick-start)` `` example in docs/checkpoints/ no longer trips the gate. |
| CI variable `WIKI_TOKEN` | Created (masked, unprotected) using the current PAT. **Action item:** rotate to a Project Access Token before adding more contributors. |

## Pipeline shape (post-merge)

```
lint        → markdown-links     (informational, allow_failure: true)
verify      → verify-knowledge-drift   (BLOCKING)
sync        → sync-no-diff             (BLOCKING)
wiki-sync   → wiki-sync                (develop only, on docs/wiki/** changes; allow_failure: true)
release     → release                  (on vX.Y.Z tags only)
```

## Decisions

- **`git-cliff` over `semantic-release`** — repo has no `package.json` at root and no npm publish step; `git-cliff` is a single static binary with zero JS dependencies.
- **Wiki sync via Python urllib (no deps)** — alpine-based job needs only `apk add curl python3 jq`. Avoids pulling in a full SDK.
- **Both new jobs are `allow_failure: true` for the wiki-sync** — wiki API hiccups must not block develop merges. The release job is **not** allow_failure (a failed release is real failure).
- **Tag-pattern filter** — `^v[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$` accepts `v1.2.3`, `v1.2.3-rc.1`, `v1.2.3-alpha`, etc.
- **Single `WIKI_TOKEN` reused by `release` job** — releases also need `api` scope; one variable is simpler than two with overlapping permissions.

## Action items

| # | Item | Priority |
|---|------|----------|
| 1 | Rotate `WIKI_TOKEN` from user PAT to a Project Access Token (Settings → Access Tokens) | medium |
| 2 | Cut `v0.1.0` to validate the release pipeline end-to-end | low |
| 3 | Add issue/MR template for `Security` (private vulnerability disclosure) — needs a Service Desk or `confidential` issue workflow | low |
| 4 | Consider adding a `dependabot`-equivalent (Renovate Bot) for the few JS deps (`git-cliff`, future tooling) | low |

## Token usage

Mechanical work; no specialist agent delegation. Well under phase budget.

## Next steps

- Cut `v0.1.0` whenever the team is ready (will exercise the release pipeline)
- First feature work goes through the new MR template
