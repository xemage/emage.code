# Contributing to emage.code

Thanks for your interest! This document describes how to propose changes to the
project. **Please read it before opening a merge request.**

## Code of conduct

By participating you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Where to make changes

| If you want to … | Edit … | Then … |
|------------------|--------|--------|
| Update an agent, skill, command, instruction, or MCP server (current stream) | `v3/implementation/knowledge/**` | re-run v3 sync (see "Working with v3") |
| Update an agent/skill/command for the previous stable stream | `v2/implementation/knowledge/**` | re-run sync (see below) |
| Update workspace conventions | `AGENTS.md` (root) and `v3/implementation/AGENTS.md` | — |
| Update the v2 plan / architecture docs | `v2/plan/**` | — |
| Touch v1 | **don't** — v1 is frozen | open an issue first |
| **Never** edit by hand | `.github/`, `.gemini/`, `.opencode/`, `.cursor/` (generated under each implementation stream) | these are generated |

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

## Working with v3

v3 is the schema-first implementation stream. Use it when you need the
managed cookbook, trigger, packaging, and adapter workflows.

Validate v3 from the repository root:

```bash
python3 v3/implementation/scripts/check-v3.py --root v3/implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers --adapters
node v3/implementation/scripts/verify-v3.mjs --root v3/implementation
```

If you change v3 docs, update the wiki sources in `docs/wiki/` as well and
ensure the release docs gate still passes.

## Merge request checklist

- [ ] Branch is up to date with `develop`
- [ ] Commits follow Conventional Commits
- [ ] `node scripts/sync.mjs` was run and generated changes are committed
- [ ] `node v3/implementation/scripts/sync-v3.mjs --root v3/implementation` was run when v3 canonical/projection files changed
- [ ] CI is green
- [ ] At least one approval
- [ ] No secrets / tokens / PII anywhere in the diff
- [ ] If you added or changed an agent / skill / instruction, the change is
      reflected in `v2/implementation/knowledge/` (the canonical source)
- [ ] If you added or changed v3 agent / skill / instruction content, the change is
   reflected in `v3/implementation/knowledge/` and v3 projections are regenerated

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

## Releasing

The project uses **Semantic Versioning** (`vMAJOR.MINOR.PATCH`) and
**Conventional Commits** to drive automated changelog generation.

### Cutting a release

1. Branch from `develop`: `release/vX.Y.Z`
2. Bump versions / finalise documentation as needed
3. Create the per-release brief `docs/releases/vX.Y.Z.md` (copy
   `docs/releases/_template.md`) with **Install** and **Highlights** sections.
4. Run the local docs verification gate for the target tag:
   ```bash
   python3 scripts/verify-release-docs.py --tag vX.Y.Z
   ```
   This must pass before opening the release MR.
5. Open MR `release/vX.Y.Z → main` using the **Release** MR template
6. After merge to `main`:
   ```bash
   git checkout main && git pull
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   git checkout develop && git merge --no-ff main && git push   # back-merge
   ```
7. The tag push triggers the `release` CI job which:
   - Runs `release-docs-gate` and `scripts/verify-release-docs.py` to verify required docs, marker alignment (`Latest release: vX.Y.Z`), per-release brief (`docs/releases/vX.Y.Z.md`), required content sections, and local/internal links
   - Verifies the v3 documentation surface (`docs/wiki/v3-implementation.md` and `v3/implementation/README.md`) alongside the root and wiki release docs
   - Embeds **Install + Highlights** from `docs/releases/vX.Y.Z.md` in GitLab Release notes
   - Appends a **Changelog** section from Conventional Commits since the previous tag (full git history; `GIT_DEPTH: 0` on release job)
   - Regenerates [`CHANGELOG.md`](CHANGELOG.md) and creates a [GitLab Release](https://gitlab.com/em-age/emage.code/-/releases)

### Hotfixes

1. Branch from `main`: `hotfix/vX.Y.Z+1`
2. Fix, test, MR to `main`
3. After merge: tag `vX.Y.Z+1`, then back-merge `main → develop`

### What goes in the changelog

Determined by your commit type (see Commit messages above):

| Commit type | Changelog group |
|---|---|
| `feat` | Features |
| `fix` | Bug Fixes |
| `perf` | Performance |
| `refactor` | Refactor |
| `docs` | Documentation |
| `test` | Tests |
| `ci` | CI |
| `chore(deps)` | Dependencies |
| `chore` (other) | Chores |
| `revert` | Reverts |
| Any commit body containing `BREAKING CHANGE:` | Breaking Changes |

Configure groups in [`cliff.toml`](cliff.toml).

## Questions?

Open a discussion issue or check the [project Wiki](https://gitlab.com/em-age/emage.code/-/wikis/home).
