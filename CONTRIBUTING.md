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
| **Never** edit by hand | `.github/`, `.gemini/`, `.opencode/`, `.pi/`, `.claude/`, `.cline/`, `.clinerules/` (generated under `implementation/`) | these are generated |

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

The platform folders (`.github/`, `.gemini/`, `.opencode/`, `.pi/`,
`.claude/`, `.cline/`, `.clinerules/`) are **generated**. CI fails if they drift from `knowledge/`.

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

1. Create `implementation/platforms/<name>.json` (use an existing manifest such as `claude-code.json` as a template)
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
shape by copying a sibling platform's `format` branch verbatim (a `format`
value that is named after one platform but silently reused by another is
exactly that mistake, which is why each `format` value now names its own
platform, as `pi.json` does with `"pi"`) without checking that platform's *own* current
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
3. Create the per-release document `docs/releases/vX.Y.Z.md` (copy
   `docs/releases/_template.md`). It is the release's one document: it carries the **Install**,
   **Highlights** and **RELEASE VERDICT** sections that step 4's gate checks, and the sections
   skill `release-workflow` § 4 prescribes (Summary, Migration Guide, Changelog, Known Issues,
   Gate Verdicts, Rollback Plan). The `## RELEASE VERDICT` block is the release gate outcome
   required by step 7 of `/prepare-release`; the release notes document is its declared home.
4. Run the local docs verification gate for the target tag:
   ```bash
   python3 scripts/verify-release-docs.py --tag vX.Y.Z
   ```
   This must pass before opening the release MR.
5. Open two MRs from `release/vX.Y.Z`: first `release/vX.Y.Z → develop`, then
   `release/vX.Y.Z → main` using the **Release** MR template. Both are merged (step 6) before
   the tag is created, `develop` first, because the `main-develop-drift-gate` fails a tag push
   while `main` is ahead of `develop`.
6. Merge the `develop` MR first, then the `main` MR. Neither is squashed: use the PUT-first
   sequence below for both, with `should_remove_source_branch=false` on the `develop` MR (the
   `main` MR still needs the branch) and `true` on the `main` MR. For `release/*→main` merges
   specifically (not the generic squash-and-merge convention used for `feature/*`/`bugfix/* →
   develop` MRs elsewhere in this doc), use this PUT-first sequence as the standard merge step:
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
7. After both merges, tag the release branch's tip. It is an ancestor of `origin/develop` and
   of `origin/main` and has the same tree as `origin/main`; check that, then push the tag.
   There is no separate back-merge: `main` and `develop` are protected (`git-workflow.md`),
   and the release content reached `develop` in step 6.
   ```bash
   git fetch origin
   sha=$(git rev-parse origin/main^2)   # the release branch tip, when step 6 did not squash
   git merge-base --is-ancestor "$sha" origin/develop && git merge-base --is-ancestor "$sha" origin/main
   git diff --exit-code "$sha" origin/main
   git tag -a vX.Y.Z -m "Release vX.Y.Z" "$sha"
   git push origin vX.Y.Z
   ```
8. The tag push triggers the `release` CI job which:
   - Runs `release-docs-gate` and `scripts/verify-release-docs.py` to verify required docs, marker alignment (`Latest release: vX.Y.Z`), per-release brief (`docs/releases/vX.Y.Z.md`), required content sections, local/internal links, and repo-wide version consistency (via `scripts/check-version-consistency.py`, Gate G0 — fails the tag if any non-archived doc still references a stale release)
   - Verifies the implementation documentation surface (`docs/wiki/implementation-guide.md`, `implementation/README.md`, `scripts/install.sh`) alongside the root and wiki release docs
   - Publishes `docs/releases/vX.Y.Z.md`, whole, as the GitLab Release description (the same text the `glab release create ... -F` command below publishes; the body starts with `# Release vX.Y.Z`)
   - Regenerates [`CHANGELOG.md`](CHANGELOG.md) as a job artifact (not committed) from Conventional Commits since the previous tag, merge commits excluded (full git history; `GIT_DEPTH: 0` on release job)
   - Creates the [GitLab Release](https://gitlab.com/em-age/emage.code/-/releases)

   The `release-docs-gate` fails when the release document's Gate Verdicts or RELEASE VERDICT section
   still holds `pending`, `YYYY-MM-DD` or another template placeholder (fill every row and field before
   the tag). Since T686 the `release` job authenticates with the GitLab job token: it reads
   `CI_JOB_TOKEN` through `--token-env CI_JOB_TOKEN --token-header JOB-TOKEN`, so the value is never
   in argv, is sent only in the `JOB-TOKEN` header (the script accepts only `PRIVATE-TOKEN` and
   `JOB-TOKEN` as header names, and never follows a redirect), and the API host is pinned to
   `CI_SERVER_HOST`. The `git` and `apk` child processes get an allowlisted environment, and no
   variable whose value contains the job token is passed to either of them, whatever the variable is
   called (the same token also appears as `CI_REGISTRY_PASSWORD` and inside `CI_REPOSITORY_URL`). The job no longer uses
   `WIKI_TOKEN`; see "Release token and permissions" below.

If you must manually create or repair a GitLab release entry, always source notes from the release brief file:

```bash
glab release create vX.Y.Z --ref vX.Y.Z --name vX.Y.Z -F docs/releases/vX.Y.Z.md
```

Do not use ad-hoc inline `--notes`, as that can drift from `docs/releases/vX.Y.Z.md`.

### Release token and permissions

The tag pipeline creates the GitLab Release with the job token of the user who pushed the tag
(T686; `docs/artifacts/security-review-t685-supply-chain-residuals-v1.md`, the `WIKI_TOKEN` section).
A job token acts with the permissions of that user, so:

- The pushing user needs at least the **Developer role** on the project and the permission to
  create the tag (GitLab's Releases API requires the Developer role to create or update a release).
  That role may be higher than the role the old `WIKI_TOKEN` carried: the release now acts with the
  pusher's role, not with the token's.
- Protected `v*` tags should be **restricted to Maintainers** ("Allowed to create"). Whoever can push
  a release tag runs the tagged commit's scripts in the release job, with the job token of that
  user in its environment. Tag protection limits who runs the release job; it does **not** limit
  who holds a Releases-capable token: every job of every pipeline has a job token, so any Developer
  job holds one. The real controls are the protected `v*` tags (Maintainers) and GitLab's job token
  permission and allowlist settings (on newer GitLab versions, fine-grained job token permissions).
- `WIKI_TOKEN` is used **only by the `wiki-sync` job** (the Wiki API does not accept job tokens). It
  must be a **protected and masked** CI/CD variable holding a token with the minimum role that can
  edit the wiki (typically Developer) and the `api` scope that wiki pages need. The release job does
  not use it; its `git` and `apk` child processes also never see it.
- What the child-process filter does, exactly: `git` and `apk` get only allowlisted variable names
  (`PATH`, `HOME`, locale, temp directory, proxy and CA-bundle variables, and the few `GIT_*` names
  git needs), and no variable whose value contains the job token, `WIKI_TOKEN` or the token that was
  passed is handed to either of them. It does not hide the token from the script itself, from the
  runner's own `.git/config` (which holds the clone credential) or from other jobs.
- Keep the manual fallback above (`glab release create ...`) until a real tag pipeline has confirmed
  the job token. If the `release` job fails with a 401 or 403 from the Releases API (for example
  because a job token permission or allowlist setting denies it), create the release with the
  fallback and report the status code in the release record.
- Not changed by T686 and not checked by any agent: the GitLab settings themselves (tag protection,
  the variable flags, the token's role and scope, the job token permissions) belong to the user.
- **(unverified)** Whether job tokens work in tag pipelines on protected tags in this GitLab
  instance, whether the Releases API accepts the job token here (the GitLab documentation says it
  does, read 2026-10-22), whether protected tags also restrict release create, update and delete,
  and whether `CI_JOB_TOKEN` is masked in job logs.

First-tag rehearsal checklist (the user runs it on the first real tag pipeline):

- [ ] The `release` job succeeded, or failed with a status code you wrote down (then use the fallback).
- [ ] Search the whole job log of the `release` job and of `release-docs-gate` for the job token value
      (it is not printed by the script, and masking of `CI_JOB_TOKEN` in job logs is unverified).
- [ ] The GitLab Release shows the text of `docs/releases/vX.Y.Z.md`.
- [ ] `git fetch` in the `release` job worked with the allowlisted environment (the runner's clone
      credential lives in `.git/config`); if it did not, report the log line, do not widen the allowlist
      to the job token.

### Drift detection

`main` and `develop` are checked for content drift on every release and on every push to
`develop`, using `scripts/check-main-develop-drift.py`. The check compares the
`Latest release: vX.Y.Z` marker in `README.md` on each branch and counts how many tagged
releases separate them.

- **Grace window:** `main` may lag `develop` by up to 1 release. In the order of "Cutting a
  release" both branches carry the release before the tag, so the window is a tolerance, not a
  step. `main` ahead of `develop` is always a failure. **The duty is yours, not the gate's:**
  merge `release/vX.Y.Z` to `develop` and to `main` before you push the tag. A tag pushed while
  `main` is exactly one release behind still passes the gate (the grace window is unchanged);
  the gate prints a `NOTE` line in that case, and you check that line in the tag pipeline.
- **An offline run proves nothing:** the check compares the `Latest release` marker on the two
  refs it is given. Without `git fetch origin main develop` first (or with the same ref twice) it
  reports `releases_behind=0` and passes without having seen the real `main`.
- **Blocking gate (`main-develop-drift-gate`, `release` stage):** runs on every tag push. If
  `main` is already more than 1 release behind at the moment a new release is tagged, this job
  fails and blocks the `release` job (CHANGELOG + GitLab Release publish) until the outstanding
  `release/vX.Y.Z → main` MR is merged.
- **Tag tree check (same job, T685):** after the marker check the job runs
  `python3 scripts/check-release-tag-tree.py --tag vX.Y.Z --main-ref origin/main`. The tag's commit
  must have the same tree (the same files, byte for byte) as `origin/main`; this is the check that
  "the release is on `main` before the tag" actually holds, and it has no grace window. It compares
  tree ids, not commit ancestry, because GitLab's API merge makes a new commit with the same tree,
  so the tag commit is not an ancestor of `main` even for a correct release; it works in the
  depth-1 clone of the tag job. It fails when `main` was not fetched (an offline run proves nothing),
  when the tag was pushed before the `main` merge, and on a re-run of the tag pipeline after `main`
  has moved on (re-tag from the right commit instead). Run it locally the same way after
  `git fetch origin main` and with the tags fetched.
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
2. Fix, test; bump the `Latest release:` marker and write `docs/releases/vX.Y.Z+1.md`
3. MR to `develop` first, then MR to `main`, merged as in "Cutting a release" step 6
4. Tag `vX.Y.Z+1` as in step 7 (the same gates run: `main` must not be ahead of `develop`)

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
