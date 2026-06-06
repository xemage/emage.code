# emage.code Wiki

Welcome to the **emage.code** wiki — the central knowledge hub for the multi-platform AI dev-team orchestration framework.

Latest release: v4.0.0

## What is emage.code?

emage.code projects a single canonical knowledge base into the major AI coding assistants (GitHub Copilot, Gemini CLI, Opencode, Cursor, Pi) so that every assistant runs the *same* dev team with the *same* protocols.

## Wiki contents

| Page | Topic |
|------|-------|
| [Quick Start](quick-start) | Drop emage.code into a new project in 5 minutes |
| [Architecture](architecture) | The 6-layer architecture, knowledge → platform projection |
| [Agents Overview](agents-overview) | The 27 specialist agents and their permissions |
| [MCP Servers](mcp-servers) | Tool integrations: GitLab, Playwright, Memory, Brave, … |
| [Performance Benchmarks](performance-benchmarks) | Benchmark dimensions, thresholds, and runtime diagrams |
| [Contributing Workflow](contributing-workflow) | GitFlow + Conventional Commits + sync engine |
| [Migration v1 → v2](migration-v1-to-v2) | What changed and how to upgrade |
| [v3 Implementation](v3-implementation) | Schema-first workflows, cookbooks, triggers, packaging |

Release note: documentation updates are a required release gate. Before tagging,
update release markers and run `python3 scripts/verify-release-docs.py --tag vX.Y.Z`.
The release gate also checks the v3 documentation surface so the wiki and repo
stay aligned.

## Performance snapshot

```mermaid
flowchart LR
	A[Performance suite] --> B[Tool-use complexity]
	A --> C[Trajectory quality]
	A --> D[Scaling throughput]
```

```mermaid
flowchart TD
	V[verify p95: 0.320s / 5.0s budget]
	S[sync p95: 0.352s / 10.0s budget]
```

## Project links

- **Repository:** [`em-age/emage.code`](https://gitlab.com/em-age/emage.code)
- **Issues:** [GitLab issues](https://gitlab.com/em-age/emage.code/-/issues)
- **Pipelines:** [CI/CD](https://gitlab.com/em-age/emage.code/-/pipelines)
- **License:** [MIT](https://gitlab.com/em-age/emage.code/-/blob/main/LICENSE)

## Status

- **v1** — frozen, kept under [`v1/`](https://gitlab.com/em-age/emage.code/-/tree/main/v1) for reference
- **v2** — maintained as the previous stable stream under [`v2/implementation/`](https://gitlab.com/em-age/emage.code/-/tree/main/v2/implementation)
- **v3** — current release stream; new work goes to [`v3/implementation/`](https://gitlab.com/em-age/emage.code/-/tree/main/v3/implementation), see the [v3 Implementation](v3-implementation) page

> The wiki is **hand-curated** and version-controlled separately from the main repo. To propose changes, open an MR against the main repo's wiki sources at [`docs/wiki/`](https://gitlab.com/em-age/emage.code/-/tree/main/docs/wiki).
