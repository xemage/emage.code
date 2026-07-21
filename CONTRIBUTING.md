# Contributing to emage.code

Thanks for your interest! This document describes how to propose changes to the
project. **Please read it before opening a merge request.**

## Code of conduct

By participating you agree to follow the collaboration and review expectations documented in this guide.

## Where to make changes

| If you want to … | Edit … | Then … |
|------------------|--------|--------|
| Update an agent, skill, command, instruction, or MCP server | `implementation/knowledge/**` | re-run sync (see "Working with implementation") |
| Update workspace conventions | `AGENTS.md` (root) and `implementation/AGENTS.md` | — |
| **Never** edit by hand | `.github/`, `.gemini/`, `.opencode/`, `.cursor/`, `.pi/` (generated under `implementation/`) | these are generated |

## Workflow

```
1. Open / pick up a GitLab issue
2. git checkout develop && git pull
3. git checkout -b feature/<issue-id>-<slug>
4. Edit files under implementation/knowledge/
5. make sync && make verify
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

The platform folders (`.github/`, `.gemini/`, `.opencode/`, `.cursor/`, `.pi/`)
are **generated**. CI fails if they drift from `knowledge/`.

From the repository root:

```bash
make sync      # node implementation/scripts/sync.mjs --root implementation
make verify    # node implementation/scripts/verify.mjs --root implementation
```

## Working with implementation

The `implementation/` tree is the schema-first release stream. Use it for
managed cookbooks, triggers, packaging, and adapter workflows.

Validate from the repository root:

```bash
python3 implementation/scripts/check.py --root implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers --adapters
node implementation/scripts/verify.mjs --root implementation
```

If you change docs, update the wiki sources in `docs/wiki/` as well and ensure
the release docs gate still passes.

## Merge request checklist

- [ ] Branch is up to date with `develop`
- [ ] Commits follow Conventional Commits
- [ ] `make sync` was run and generated changes are committed
- [ ] CI is green
- [ ] At least one approval
- [ ] No secrets / tokens / PII anywhere in the diff
- [ ] If you added or changed an agent / skill / instruction, the change is
      reflected in `implementation/knowledge/` and projections are regenerated

We use **squash-and-merge** for feature branches and delete the source branch
on merge.

## Reporting issues

- **Bugs** — open an issue with reproduction steps, expected vs actual, env
- **Security** — see [`implementation/SECURITY.md`](implementation/SECURITY.md);
  do **not** open a public issue for vulnerabilities
- **Ideas / discussion** — start a thread in the wiki or open an issue tagged `discussion`

## Adding a new platform

1. Create `implementation/platforms/<name>.json` (use `cursor.json` as a template)
2. Run `make sync`
3. Verify the generated `<name>/` folder
4. Add a row to the README "Supported platforms" table
5. Document any platform-specific quirks in a new ADR under `docs/decisions/`

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
   - Verifies the implementation documentation surface (`docs/wiki/implementation-guide.md`, `implementation/README.md`, `scripts/install.sh`) alongside the root and wiki release docs
   - Embeds **Install + Highlights** from `docs/releases/vX.Y.Z.md` in GitLab Release notes
   - Appends a **Changelog** section from Conventional Commits since the previous tag (full git history; `GIT_DEPTH: 0` on release job)
   - Regenerates [`CHANGELOG.md`](CHANGELOG.md) and creates a [GitLab Release](https://gitlab.com/em-age/emage.code/-/releases)

If you must manually create or repair a GitLab release entry, always source notes from the release brief file:

```bash
glab release create vX.Y.Z --ref vX.Y.Z --name vX.Y.Z -F docs/releases/vX.Y.Z.md
```

Do not use ad-hoc inline `--notes`, as that can drift from `docs/releases/vX.Y.Z.md`.

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
