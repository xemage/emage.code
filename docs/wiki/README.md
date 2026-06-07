# Wiki Sources

These are the **canonical sources** for the project Wiki at
<https://gitlab.com/em-age/emage.code/-/wikis/home>.

Latest release: v6.0.0

The wiki is hand-curated and the source of truth lives here, in version
control. To update a wiki page:

1. Edit the corresponding `.md` file in this directory
2. Validate links and content locally if preparing a release
3. Push to `develop` to trigger CI wiki sync

## Sync to live Wiki

The CI job [`wiki-sync`](../../.gitlab-ci.yml) runs on every `develop` push
that touches `docs/wiki/**` and pushes the pages via the GitLab Wiki API.

**Required CI/CD variable:** `WIKI_TOKEN` — Project Access Token with scope
`api`. See [Settings → CI/CD → Variables](https://gitlab.com/em-age/emage.code/-/settings/ci_cd).
Mark the variable as **Masked**.

To sync manually (or to test before pushing):

```bash
CI_PROJECT_ID=82070979 WIKI_TOKEN=glpat-... python3 scripts/sync-wiki.py
```

## Release documentation contract

Before a release tag is published, release documentation must be updated and
verified. Required marker:

```text
Latest release: vX.Y.Z
```

Required release docs:

- `README.md`
- `docs/wiki/README.md`
- `docs/wiki/home.md`
- `docs/releases/vX.Y.Z.md` (Install + Highlights for the tagged version)

Local verification command:

```bash
python3 scripts/verify-release-docs.py --tag vX.Y.Z
```

The release pipeline blocks publication if this verification fails.

## Page conventions

- **Slug** = filename without `.md`. e.g. `quick-start.md` → wiki slug `quick-start`.
- **Title** is derived from the slug (`quick-start` → `Quick Start`) **unless**
  the file has YAML frontmatter with an explicit `title:` field. Use frontmatter
  when the auto-derived title is wrong (acronyms, version numbers, etc.):

  ```markdown
  ---
  title: MCP Servers
  ---
  # MCP Servers
  …
  ```

  The frontmatter is stripped before upload.

## Pages

| File | Wiki slug |
|------|-----------|
| `home.md` | `home` |
| `quick-start.md` | `quick-start` |
| `architecture.md` | `architecture` |
| `agents-overview.md` | `agents-overview` |
| `mcp-servers.md` | `mcp-servers` |
| `performance-benchmarks.md` | `performance-benchmarks` |
| `contributing-workflow.md` | `contributing-workflow` |
| `implementation-guide.md` | `implementation-guide` |

> Wiki pages use the same Markdown flavour as the main repo. Internal wiki
> links use the slug (no `.md` extension), e.g. `[Quick Start](quick-start)`.
