# Contributing Workflow

Full contributor guide: [`CONTRIBUTING.md`](https://gitlab.com/em-age/emage.code/-/blob/main/CONTRIBUTING.md)

## TL;DR

1. Open or pick an issue
2. Branch from `develop`: `feature/<issue-id>-<slug>`
3. Edit **only** under [`v2/implementation/knowledge/`](https://gitlab.com/em-age/emage.code/-/tree/main/v2/implementation/knowledge)
4. Run the sync engine — `cd v2/implementation && node scripts/sync.mjs`
5. Commit using [Conventional Commits](https://www.conventionalcommits.org/)
6. Push, open MR → `develop`, wait for CI green, request review

## Branching (GitFlow)

```
main         ← production releases (protected, no direct push)
develop      ← integration branch (default branch)
feature/*    ← from develop, MR back to develop
bugfix/*     ← from develop, MR back to develop
release/*    ← from develop, MR to main + back-merge to develop
hotfix/*     ← from main, MR to main + back-merge to develop
```

## Commit messages

```
type(scope): description

[optional body]

Refs #<issue>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `ci`, `chore`, `perf`, `revert`.

## CI gates

The pipeline (`.gitlab-ci.yml`) runs three stages:

1. **lint** — markdown link check (informational, non-blocking)
2. **verify** — `scripts/verify.mjs` confirms no drift between `knowledge/` and generated platform folders (BLOCKING)
3. **sync** — re-runs `scripts/sync.mjs` and asserts no diff (BLOCKING)

If you see a sync failure, you forgot step 4 above:
```bash
cd v2/implementation && node scripts/sync.mjs
git add . && git commit --amend --no-edit
git push --force-with-lease
```

## MR rules

- Squash-and-merge to `develop`
- Source branch deleted on merge
- All discussions resolved
- Pipeline must be green
- At least one approval

## Adding a new platform

1. Drop a manifest file at `v2/implementation/platforms/<name>.json`
2. Use [`cursor.json`](https://gitlab.com/em-age/emage.code/-/blob/main/v2/implementation/platforms/cursor.json) as a template
3. Run sync; the new `<name>/` folder appears
4. Update README "Supported platforms" table
5. Document quirks in `v2/plan/`

No script changes needed.
