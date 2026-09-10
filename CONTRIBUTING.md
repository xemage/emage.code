# Contributing to emage.code

Thanks for your interest! This document describes how to propose changes to the
project. **Please read it before opening a merge request.**

> Just want to **use** emage.code in your own project rather than contribute to
> this repo? See the [Quick Start guide](https://gitlab.com/em-age/emage.code/-/wikis/quick-start)
> instead.

## Code of conduct

By participating you agree to follow the collaboration and review expectations documented in this guide.

## Where to make changes

| If you want to … | Edit … | Then … |
|------------------|--------|--------|
| Update an agent, skill, command, instruction, or MCP server | `implementation/knowledge/**` | re-run sync (see "Working with implementation") |
| Update workspace conventions | `AGENTS.md` (root) and `implementation/AGENTS.md` | — |
| **Never** edit by hand | `.github/`, `.gemini/`, `.opencode/`, `.cursor/`, `.pi/`, `.claude/` (generated under `implementation/`) | these are generated |

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

The platform folders (`.github/`, `.gemini/`, `.opencode/`, `.cursor/`, `.pi/`,
`.claude/`) are **generated**. CI fails if they drift from `knowledge/`.

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
python3 implementation/scripts/check.py --root implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --maturity --packaging --triggers --adapters
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

Most platforms are fully manifest-driven and need no script changes. If the
platform's subagent `tools` frontmatter or MCP config shape doesn't match an
existing mode in `implementation/scripts/sync.mjs` (see the `tools` and MCP
`format` branches — e.g. `claude-code` added a `"string"` tools mode and a
`"claude-code"` MCP format), add a new branch there first, as its own commit,
before writing the manifest.

**Lesson from a real regression (see `docs/tasks/task-T360.md`):** a platform's
remote-server (`transport: remote`) encoding can require its own field name or
discriminator even when nothing else about the platform justifies a new MCP
`format` branch — this is a narrower axis than the `format` value itself. VS
Code required an undocumented-in-this-repo `"type": "http"` field, Gemini CLI
requires `"httpUrl"` instead of `"url"` (it reserves `"url"` for the legacy SSE
transport), and Cline requires `"type": "streamableHttp"`, not `"http"` — three
platforms, three different requirements, none discoverable by analogy to
another platform already wired up. Never assume a new platform's remote-server
shape by copying a sibling platform's `format` branch verbatim (as `pi.json`
currently does with `cursor`'s) without checking that platform's *own* current
official MCP docs for the `context7`/`hf-mcp-server` remote-transport case
specifically — training-data memory and cross-platform analogy are exactly
what caused this drift in the first place. See
[MCP Servers § Remote-server transport encoding differs per platform](https://gitlab.com/em-age/emage.code/-/wikis/mcp-servers)
for the current per-platform reference.

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
6. Merge it. For `release/*→main` merges specifically (not the generic squash-and-merge
   convention used for `feature/*`/`bugfix/* → develop` MRs elsewhere in this doc), use this
   PUT-first sequence as the standard merge step:
   ```bash
   # Update the MR resource's own persisted squash attribute BEFORE merging — confirm the
   # response shows "squash": false.
   glab api -X PUT projects/:id/merge_requests/:iid -f squash=false
   # No squash param needed here — the MR resource itself now already carries the correct value.
   glab api -X PUT projects/:id/merge_requests/:iid/merge -f should_remove_source_branch=true
   # Still required immediately after, as the safety net — a FAIL here means it squashed anyway
   # and the recovery procedure below is needed.
   python3 scripts/verify-main-sync-merge.py <mr_iid>
   ```
   Passing `squash: false` only in the `/merge` call's own body (the previous documented step)
   failed to prevent squashing on all 3 attempts made this session (MR !103, !109, !125). Updating
   the MR resource's `squash` attribute via `PUT` first, then calling `/merge` with no `squash`
   param, held on the one attempt made (MR !126). **Confidence:** 1 confirmed success against 3
   prior failures of the old sequence — adopted as the new standard now anyway because it is a
   strict superset of the old step (adds one call, changes nothing else) with a plausible mechanism
   (the `/merge` endpoint appears to read the MR's persisted `squash` field rather than honoring a
   same-call body override). See `docs/tasks/task-T348.md` § Outcome, Steps 5–7 for the full
   evidence trail.
7. After merge to `main`:
   ```bash
   git checkout main && git pull
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   git checkout develop && git merge --no-ff main && git push   # back-merge
   ```
8. The tag push triggers the `release` CI job which:
   - Runs `release-docs-gate` and `scripts/verify-release-docs.py` to verify required docs, marker alignment (`Latest release: vX.Y.Z`), per-release brief (`docs/releases/vX.Y.Z.md`), required content sections, local/internal links, and repo-wide version consistency (via `scripts/check-version-consistency.py`, Gate G0 — fails the tag if any non-archived doc still references a stale release)
   - Verifies the implementation documentation surface (`docs/wiki/implementation-guide.md`, `implementation/README.md`, `scripts/install.sh`) alongside the root and wiki release docs
   - Embeds **Install + Highlights** from `docs/releases/vX.Y.Z.md` in GitLab Release notes
   - Appends a **Changelog** section from Conventional Commits since the previous tag (full git history; `GIT_DEPTH: 0` on release job)
   - Regenerates [`CHANGELOG.md`](CHANGELOG.md) and creates a [GitLab Release](https://gitlab.com/em-age/emage.code/-/releases)

If you must manually create or repair a GitLab release entry, always source notes from the release brief file:

```bash
glab release create vX.Y.Z --ref vX.Y.Z --name vX.Y.Z -F docs/releases/vX.Y.Z.md
```

Do not use ad-hoc inline `--notes`, as that can drift from `docs/releases/vX.Y.Z.md`.

### Drift detection

`main` and `develop` are checked for content drift on every release and on every push to
`develop`, using `scripts/check-main-develop-drift.py`. The check compares the
`Latest release: vX.Y.Z` marker in `README.md` on each branch and counts how many tagged
releases separate them.

- **Grace window:** `main` may lag `develop` by up to 1 release — the normal transient state
  between a release being tagged and its `release/vX.Y.Z → main` sync MR landing.
- **Blocking gate (`main-develop-drift-gate`, `release` stage):** runs on every tag push. If
  `main` is already more than 1 release behind at the moment a new release is tagged, this job
  fails and blocks the `release` job (CHANGELOG + GitLab Release publish) until the outstanding
  `release/vX.Y.Z → main` MR is merged.
- **Informational check (`main-develop-drift-check`, `verify` stage):** runs on every push to
  `develop`, non-blocking (`allow_failure: true`), for earlier visibility between releases.

**If the gate fails:** the job output lists exactly which release tags are missing from `main`.
Resolve it the normal way — branch `release/vX.Y.Z` from `develop` for the oldest missing
release, open an MR to `main` per the "Cutting a release" steps above, get it merged, then retry
the tag push (or re-run the pipeline once `main` is caught up).

See `docs/tasks/task-T331.md` for the incident this gate was built to prevent, and
`docs/plans/plan-019-main-develop-drift-detection.md` for the full design rationale (why content
comparison instead of `git merge-base --is-ancestor`, why a 1-release grace window, why a
blocking release-time gate instead of a scheduled pipeline).

### Post-merge squash verification

GitLab's `/merge` API has twice (`docs/tasks/task-T331.md`, `docs/tasks/task-T339.md`) squashed a
`release/vX.Y.Z → main` merge despite an explicit `squash: false` override passed in the request
body, on this project's `squash_option: default_on` setting. When that happens, `main`'s new merge
commit gets GitLab's own `squash_commit_sha` as its second parent instead of the release branch's
real tip — content-identical, but not a genuine ancestor of it — which corrupts
`git merge-base(main, develop)` for the *next* sync and can resurface stale conflicts that were
never actually there (exactly what happened in `docs/tasks/task-T339.md`, discovered a full release
cycle later). `docs/tasks/task-T340.md` § Findings independently confirmed the mechanism: this is
GitLab's documented squash-then-merge behavior, not a bug, but the `squash: false` override
demonstrably does not reliably take effect on this project.

**When to run it:** immediately after every `release/vX.Y.Z → main` merge (step 6 above), before
considering the sync complete:

```bash
python3 scripts/verify-main-sync-merge.py <mr_iid>
```

It fetches the just-merged MR's own record (`GET projects/:id/merge_requests/:iid`) and asserts
`squash == false` and `squash_commit_sha == null` — the two fields GitLab itself uses to report
that a squash occurred.

**What a failure means:** GitLab squashed the merge despite the override. The merge has already
happened — this check cannot prevent it, only catch it immediately instead of a release cycle
later. See `docs/tasks/task-T340.md` § Findings §2–3 for why this can happen even with an explicit
`squash: false` in the request.

**Recovery procedure:** `main` is push-protected (`push_access_levels: ['No one']`, identical to
`develop` — confirmed via `glab api projects/:id/protected_branches/main`, see
`docs/tasks/task-T348.md` § Outcome, Step 6), so a direct `git push` to `main` **cannot work**.
Instead, open a small "ancestry restore" follow-up MR so the *next* sync's `merge-base` resolves
correctly — a no-op commit on `main` with the true source-branch tip as an explicit second parent:

```bash
git fetch origin
git checkout -b chore/restore-ancestry-vX.Y.Z origin/main
git merge --no-ff <true-source-branch-tip-sha> -s ours -m "chore(release): restore true ancestry after GitLab squash"
git diff origin/main HEAD                                                    # must be empty
git merge-base --is-ancestor <true-source-branch-tip-sha> HEAD && echo ok    # must exit 0
git push -u origin chore/restore-ancestry-vX.Y.Z
```

Open an MR `chore/restore-ancestry-vX.Y.Z → main` and merge it using the same PUT-first sequence
documented in "Cutting a release" step 6 above, then re-run
`python3 scripts/verify-main-sync-merge.py <mr_iid>` against that MR too.

(`docs/tasks/task-T340.md` § Findings §4, option 1, for the original rationale;
`docs/tasks/task-T348.md` § Outcome, Step 6 for the exact branch+MR sequence that worked in
production, adapted here from that incident's actual commands.) This is deliberately the cheapest
remediation — bypassing the `/merge` API via direct push is not possible on this project's branch
protection, and disabling `squash_option` project-wide is a heavier option deferred until this one
is shown insufficient on a real sync.

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
