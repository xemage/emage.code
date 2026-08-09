# emage.code

> **Multi-platform AI dev-team orchestration** — disciplined software-engineering
> practice for AI-assisted coding, projected from a single canonical knowledge
> base into every major AI coding assistant.

[![pipeline status](https://gitlab.com/em-age/emage.code/badges/main/pipeline.svg)](https://gitlab.com/em-age/emage.code/-/commits/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://www.conventionalcommits.org)

emage.code brings a **structured multi-agent development team** to your
favourite AI assistant. Every project follows the same protocol:

Latest release: v6.9.0

- **Plan → Approve → Execute** lifecycle, never silent execution
- **DAG-based task management** with explicit dependencies
- **Validation gates** with `PASS` / `CONDITIONAL_PASS` / `FAIL` verdicts
- **Checkpoint compression** for long-running multi-agent workflows
- **GitFlow** branching with conventional commits
- **OWASP Top-10** security baseline enforced via the security-engineer agent

---

## Repository layout

```
emage.code/
├── AGENTS.md                  ← workspace-level conventions (loaded by every agent)
├── implementation/            ← canonical knowledge + platform projections
│   ├── knowledge/             ← edit here; platform folders are generated
│   ├── scripts/               ← sync, verify, check, packaging, registry
│   ├── cookbooks/             ← managed-agent definitions
│   ├── triggers/              ← trigger specs and examples
│   └── .cursor/ … .pi/        ← generated platform outputs (do not edit by hand)
├── scripts/
│   └── install.sh             ← one-command install into your project
├── docs/                      ← runtime workspace state + wiki sources
│   ├── wiki/                  ← hand-curated wiki (synced to GitLab Wiki)
│   ├── releases/              ← per-release install + highlights
│   ├── plans/                 ← Plan-Approve-Execute plans
│   ├── tasks/                 ← active + completed task ledgers
│   ├── checkpoints/           ← phase-boundary snapshots
│   ├── decisions/             ← ADRs (Architecture Decision Records)
│   └── artifacts/             ← versioned design artifacts
└── .gitlab-ci.yml             ← drift verification + sync sanity pipeline
```

Use [`implementation/`](implementation/README.md) for all development work.

---

## Supported platforms

| Platform | Output folder | Format |
|----------|---------------|--------|
| GitHub Copilot (VS Code) | `.github/` + `.vscode/mcp.json` | `.agent.md`, `.prompt.md`, `.instructions.md` |
| Gemini CLI | `.gemini/` | `.md` (no `tools` field), `settings.json` with hooks |
| Opencode | `.opencode/` | `.md` (object `tools`), `opencode.json` |
| Cursor | `.cursor/` | `.mdc`, `applyTo` → `globs`, `mcp.json` |
| Pi | `.pi/` | agents, prompts, instructions, skills (`.md`) |
| Claude Code | `.claude/` + `.mcp.json` | `.md` (string `tools`), subagents + skills + rules |
| Cline | `.clinerules/` (root) + `.cline/skills/` + `.cline/mcp.json` | `.md` rules (`paths` frontmatter) + skills; MCP config is a staging file, not auto-applied |

Adding a new platform = adding a `platforms/<name>.json` manifest under
`implementation/`. Usually no script changes are required; add a new
`tools`/MCP format branch to `sync.mjs` only if the platform's frontmatter or
MCP shape doesn't match an existing mode (see `implementation/scripts/sync.mjs`).

---

## Install

Install the current release with the installer script:

```bash
git clone https://gitlab.com/em-age/emage.code.git
cd emage.code
scripts/install.sh --target /path/to/your-project --platform cursor
```

| Platform | `--platform` value |
|----------|-------------------|
| Cursor | `cursor` |
| GitHub Copilot (VS Code) | `github` |
| Gemini CLI | `gemini` |
| Opencode | `opencode` |
| Pi | `pi` |
| Claude Code | `claude-code` |
| Cline | `cline` |
| All platforms | `all` |

Makefile shortcut: `make install TARGET=/path/to/your-project PLATFORM=cursor`

**Update an existing install:**

```bash
scripts/install.sh --target /path/to/your-project --platform cursor --update
```

On `--update`, the single-file MCP/settings configs for every platform —
`.vscode/mcp.json` (`github`), `.mcp.json` (`claude-code`), `.cursor/mcp.json`
(`cursor`), `.gemini/settings.json` (`gemini`), `.opencode/opencode.json`
(`opencode`), `.pi/mcp.json` (`pi`), and `.cline/mcp.json` (`cline`) — are
merged, not overwritten: any existing top-level key the generator doesn't
know about (e.g. a hand-added MCP server entry, or a top-level `inputs`
prompt block) is preserved, while every generator-known key is refreshed to
the current generated content, recursing into nested objects (so hand-added
fields inside a known server's config are preserved too). See
`scripts/merge-mcp-json.py` for the exact algorithm. The rest of each
platform's directory tree (`.github/`, `.cursor/`, `.claude/`, etc.) is still
replaced wholesale on `--update` — only each platform's one MCP/settings file
gets this merge treatment.

Per-release install steps live in [`docs/releases/v6.0.1.md`](docs/releases/v6.0.1.md)
and are embedded in [GitLab Releases](https://gitlab.com/em-age/emage.code/-/releases).

## Quick start

After install, set MCP env vars (`GITLAB_PERSONAL_ACCESS_TOKEN`, `BRAVE_API_KEY`, …)
from the generated `mcp.json`, then in your AI assistant:

```
/discover-skills "start new project"
/new-project "My SaaS application"
```

Detailed guides:

- [`implementation/README.md`](implementation/README.md)
- [`docs/wiki/quick-start.md`](docs/wiki/quick-start.md)
- [project Wiki](https://gitlab.com/em-age/emage.code/-/wikis/home)

### Implementation

The `implementation/` tree provides schema-first knowledge, cookbooks, triggers,
packaging, adapters, and a validation super-gate.

Start here:

- [`implementation/README.md`](implementation/README.md)
- [`docs/wiki/implementation-guide.md`](docs/wiki/implementation-guide.md)

Validate from the repository root:

```bash
python3 implementation/scripts/check.py --root implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers --adapters
node implementation/scripts/verify.mjs --root implementation
```

---

## Use emage.code in practice

Use this sequence in a real project:

1. Bootstrap: copy one platform folder plus `AGENTS.md` and `docs/`.
2. Start with intent: run `/new-project "<your project>"`.
3. Work through task ledger: review `docs/tasks/active-tasks.md` and approve
   plans before implementation.
4. Validate quality gates: ensure CI checks pass (`verify-knowledge-drift`,
   `sync-no-diff`, tests).
5. Release safely: update documentation and pass the release docs gate before
   tag publication.

For contributor detail, see [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Documentation release contract

Release publication is blocked unless documentation is updated for the tag.

- Required marker in release docs: `Latest release: vX.Y.Z`
- Required per-release brief: `docs/releases/vX.Y.Z.md` (Install + Highlights)
- GitLab release notes source of truth: publish from `docs/releases/vX.Y.Z.md` using `glab release create vX.Y.Z --ref vX.Y.Z --name vX.Y.Z -F docs/releases/vX.Y.Z.md`
- Required files:
  - `README.md`
  - `docs/wiki/README.md`
  - `docs/wiki/home.md`
  - `docs/wiki/implementation-guide.md`
  - `implementation/README.md`
  - `scripts/install.sh`
  - `docs/releases/vX.Y.Z.md`
- Content verification script:
  ```bash
  python3 scripts/verify-release-docs.py --tag vX.Y.Z
  ```

This script checks required files, marker alignment, required usage sections,
and local/internal markdown link validity for core release docs.

---

## Architecture (6 layers)

1. **Commands** — 18 slash commands, the user entry point
2. **Orchestration** — Plan-Approve-Execute engine (`@orchestrator`, `@poc-orchestrator`)
3. **Agents** — 27 specialists (backend, frontend, qa, security, devops, …)
4. **Skills** — 22 reusable capabilities (code-review, validation-gates, …)
5. **Memory** — `docs/` artifacts + MCP `memory` server
6. **MCP servers** — declared once in [`implementation/knowledge/mcp/servers.yaml`](implementation/knowledge/mcp/servers.yaml)

Deep dive: [`docs/wiki/architecture.md`](docs/wiki/architecture.md)

---

## Benchmark and performance

The repository includes a deterministic benchmark suite for agent-team quality
and runtime health under `tests/performance/`.

### Benchmark coverage map

```mermaid
flowchart LR
   A[Benchmark suite] --> B[Tool-use complexity]
   A --> C[Orchestration trajectory quality]
   A --> D[Scaling and throughput]
   B --> B1[test_tool_use_complexity.py]
   C --> C1[test_orchestration_trajectory_quality.py]
   D --> D1[test_scaling_and_throughput.py]
   B1 --> E[Thresholds: benchmark-thresholds-v1.json]
   C1 --> E
   D1 --> E
```

### Runtime envelope (latest local baseline run)

```mermaid
flowchart TD
   V[verify.mjs p95: 0.320s] --> VB[budget: 5.0s]
   S[sync.mjs p95: 0.352s] --> SB[budget: 10.0s]
   V --> C1[coefficient of variation: 0.041]
   S --> C2[coefficient of variation: 0.006]
```

Key files:
- `tests/_baselines/benchmark-thresholds-v1.json`
- `tests/fixtures/benchmarks/tool_use_cases.json`
- `tests/fixtures/benchmarks/trajectory_cases.json`
- `tests/fixtures/benchmarks/scaling_cases.json`

Run locally:

```bash
python3 tests/run.py --suite performance -v
BENCH_STRESS=1 python3 tests/run.py --suite performance -v
```

---

## Contributing

1. Edit canonical knowledge under [`implementation/knowledge/`](implementation/knowledge/) — **never** the generated `.github/`, `.gemini/`, `.opencode/`, `.cursor/`, `.pi/` folders.
2. Run the sync engine from the repo root:
   ```bash
   make sync
   make verify
   ```
3. Commit both the knowledge change **and** the regenerated platform folders.
4. CI runs drift gates for `implementation/`.

Full contributor guide: [`CONTRIBUTING.md`](CONTRIBUTING.md)
Authoring rules: [`implementation/knowledge/README.md`](implementation/knowledge/README.md)

### Branching (GitFlow)
```
main         ← production-ready releases
develop      ← integration branch for new work
feature/*    ← branch from develop, MR back to develop
bugfix/*     ← bug fixes, MR back to develop
release/*    ← stabilize a release, MR to main + back-merge to develop
hotfix/*     ← emergency fix from main
```

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):
`feat(scope): …`, `fix(scope): …`, `docs: …`, `refactor: …`, `test: …`, `chore: …`

---

## Security

This project enforces:

- No secrets in source control (use environment variables / vault)
- Parameterized queries only — no string-concat SQL
- Input validation at every system boundary
- OWASP Top-10 audit before every release
- Permission boundaries per agent role

Report vulnerabilities privately — see [`implementation/SECURITY.md`](implementation/SECURITY.md).

---

## License

[MIT](LICENSE) © em-age
