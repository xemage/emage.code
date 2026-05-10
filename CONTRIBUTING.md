# Contributing to emage.code

Thanks for your interest! This document describes how to propose changes to the
project. **Please read it before opening a merge request.**

## Code of conduct

By participating you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Where to make changes

| If you want to … | Edit … | Then … |
|------------------|--------|--------|
| Update an agent, skill, command, instruction, or MCP server | `v2/implementation/knowledge/**` | re-run sync (see below) |
| Update workspace conventions | `AGENTS.md` (root) and `v2/implementation/AGENTS.md` | — |
| Update the v2 plan / architecture docs | `v2/plan/**` | — |
| Touch v1 | **don't** — v1 is frozen | open an issue first |
| **Never** edit by hand | `.github/`, `.gemini/`, `.opencode/`, `.cursor/` (under `v2/implementation/`) | these are generated |

## Workflow

```
1. Open / pick up a GitLab issue
2. git checkout develop && git pull
3. git checkout -b feature/<issue-id>-<slug>
4. Edit files under v2/implementation/knowledge/
5. cd v2/implementation && node scripts/sync.mjs
6. git add . && git commit -m "feat(scope): …"
7. git push -u origin HEAD
8. Open MR  →  develop
9. Wait for CI  →  request review  →  squash-merge
```

### Branch naming
```
feature/<issue-id>-short-description    e.g. feature/42-add-rust-platform
bugfix/<issue-id>-short-description
release/v<MAJOR.MINOR.PATCH>
hotfix/v<MAJOR.MINOR.PATCH>
```

### Commit messages — [Conventional Commits](https://www.conventionalcommits.org/)
```
type(scope): short description

[optional body — explain what and why, not how]

[optional footer]
Refs #<issue>
```

| Type | Use for |
|------|---------|
| `feat` | New capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Restructuring without behaviour change |
| `test` | Test additions / fixes |
| `ci` | CI configuration changes |
| `chore` | Tooling, deps, config |
| `perf` | Performance |
| `revert` | Revert previous commit |

## Sync engine — required before every commit

The platform folders (`.github/`, `.gemini/`, `.opencode/`, `.cursor/`) are
**generated**. CI fails if they drift from `knowledge/`.

```bash
cd v2/implementation
node scripts/sync.mjs        # regenerate
node scripts/verify.mjs      # confirm no drift
```

Wrappers: `scripts/sync.sh` (POSIX), `scripts/sync.ps1` (Windows).

## Merge request checklist

- [ ] Branch is up to date with `develop`
- [ ] Commits follow Conventional Commits
- [ ] `node scripts/sync.mjs` was run and generated changes are committed
- [ ] CI is green
- [ ] At least one approval
- [ ] No secrets / tokens / PII anywhere in the diff
- [ ] If you added or changed an agent / skill / instruction, the change is
      reflected in `v2/implementation/knowledge/` (the canonical source)

We use **squash-and-merge** for feature branches and delete the source branch
on merge.

## Reporting issues

- **Bugs** — open an issue with reproduction steps, expected vs actual, env
- **Security** — see [`v2/implementation/SECURITY.md`](v2/implementation/SECURITY.md);
  do **not** open a public issue for vulnerabilities
- **Ideas / discussion** — start a thread in the wiki or open an issue tagged `discussion`

## Adding a new platform

1. Create `v2/implementation/platforms/<name>.json` (use `cursor.json` as a template)
2. Run `node scripts/sync.mjs`
3. Verify the generated `<name>/` folder
4. Add a row to the README "Supported platforms" table
5. Document any platform-specific quirks in `v2/plan/`

No script changes are needed — the sync engine is fully manifest-driven.

## Questions?

Open a discussion issue or check the [project Wiki](https://gitlab.com/em-age/emage.code/-/wikis/home).
