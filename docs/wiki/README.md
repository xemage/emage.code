# Wiki Sources

These are the **canonical sources** for the project Wiki at
<https://gitlab.com/em-age/emage.code/-/wikis/home>.

The wiki is hand-curated and the source of truth lives here, in version
control. To update a wiki page:

1. Edit the corresponding `.md` file in this directory
2. Sync to GitLab Wiki (one of):
   - **Manual** — copy the rendered content into the wiki UI
   - **CLI** — push via the wiki git remote, e.g.
     ```bash
     # one-time setup
     git clone https://gitlab.com/em-age/emage.code.wiki.git ../emage.code.wiki
     # update
     cp docs/wiki/*.md ../emage.code.wiki/
     cd ../emage.code.wiki && git add . && git commit -m "docs(wiki): sync from main repo" && git push
     ```
   - **API** — `glab api -X PUT projects/82070979/wikis/<slug> -f content="..."`

## Pages

| File | Wiki slug |
|------|-----------|
| `home.md` | `home` |
| `quick-start.md` | `quick-start` |
| `architecture.md` | `architecture` |
| `agents-overview.md` | `agents-overview` |
| `mcp-servers.md` | `mcp-servers` |
| `contributing-workflow.md` | `contributing-workflow` |
| `migration-v1-to-v2.md` | `migration-v1-to-v2` |

> Wiki pages use the same Markdown flavour as the main repo. Internal wiki
> links use the slug (no `.md` extension), e.g. `[Quick Start](quick-start)`.
