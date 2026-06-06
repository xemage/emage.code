# emage.code

> **Multi-platform AI dev-team orchestration** — disciplined software-engineering
> practice for AI-assisted coding, projected from a single canonical knowledge
> base into every major AI coding assistant.

[![pipeline status](https://gitlab.com/em-age/emage.code/badges/main/pipeline.svg)](https://gitlab.com/em-age/emage.code/-/commits/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://www.conventionalcommits.org)

emage.code brings a **structured multi-agent development team** to your
favourite AI assistant. Every project follows the same protocol:

Latest release: v3.0.0

- **Plan → Approve → Execute** lifecycle, never silent execution
- **DAG-based task management** with explicit dependencies
- **Validation gates** with `PASS` / `CONDITIONAL_PASS` / `FAIL` verdicts
- **Checkpoint compression** for long-running multi-agent workflows
- **GitFlow** branching with conventional commits
- **OWASP Top-10** security baseline enforced via the security-engineer agent

**v3 is the current release stream** — schema-first canonical knowledge with
managed cookbooks, trigger workflows, packaging, adapter smoke tests, and a
stricter validation super-gate. v2 remains available as the previous stable
toolchain; v1 is frozen.

---

## Repository layout

```
emage.code/
├── AGENTS.md                  ← workspace-level conventions (loaded by every agent)
├── docs/                      ← runtime workspace state
│   ├── plans/                 ← Plan-Approve-Execute plans
│   ├── tasks/                 ← active + completed task ledgers
│   ├── checkpoints/           ← phase-boundary snapshots
│   ├── decisions/             ← ADRs (Architecture Decision Records)
│   └── artifacts/             ← versioned design artifacts
├── v1/                        ← v1 release — frozen, kept for reference
│   ├── plan/                  ← original architecture & phase plans
│   └── implementation/        ← per-platform agent bundles (triple-duplicated)
├── v2/                        ← previous stable release — single source of truth
│   ├── plan/                  ← v2 architecture, adapter spec, phase backfills
│   └── implementation/        ← canonical knowledge + sync engine + generated mirrors
├── v3/                        ← current release — schema-first knowledge + runtime
│   └── implementation/        ← canonical knowledge, projections, cookbooks, triggers, packaging
└── .gitlab-ci.yml             ← drift verification + sync sanity pipeline
```

Use [`v3/implementation/`](v3/implementation/README.md) for new work — v2 is
preserved as the previous stable stream and v1 is frozen.

---

## Versions at a glance

| | **v1** (legacy) | **v2** (previous) | **v3** (current) |
|---|---|---|---|
| Source of truth | per-platform folders, **triple-duplicated** | single `knowledge/` tree | schema-first `knowledge/` + runtime workflows |
| Supported platforms | GitHub Copilot, Gemini CLI, Opencode | + **Cursor** | + **Pi**, packaging, triggers, adapters |
| MCP config | three divergent JSON files | one `mcp/servers.yaml` registry | same registry model, stricter validation |
| Drift detection | none | `verify.mjs` + CI gate | `check-v3.py` + `verify-v3.mjs` |
| Status | **frozen** — no new development | **maintained** — previous stable stream | **current** — active release stream |

Migration guide: [`v2/plan/05-migration-from-v1.md`](v2/plan/05-migration-from-v1.md)

---

## Supported platforms

| Platform | Output folder | Format |
|----------|---------------|--------|
| GitHub Copilot (VS Code) | `.github/` + `.vscode/mcp.json` | `.agent.md`, `.prompt.md`, `.instructions.md` |
| Gemini CLI | `.gemini/` | `.md` (no `tools` field), `settings.json` with hooks |
| Opencode | `.opencode/` | `.md` (object `tools`), `opencode.json` |
| Cursor | `.cursor/` | `.mdc`, `applyTo` → `globs`, `mcp.json` |
| Pi | `.pi/` | agents, prompts, instructions, skills (`.md`) |

Adding a new platform = adding a `platforms/<name>.json` manifest. No script
changes required. See
[`v2/plan/02-platform-adapter-spec.md`](v2/plan/02-platform-adapter-spec.md).

---

## Install

Install the **current release** (`v3.0.0`) by copying from `v3/implementation/`.
Per-release install steps also live in [`docs/releases/v3.0.0.md`](docs/releases/v3.0.0.md)
and are embedded in [GitLab Releases](https://gitlab.com/em-age/emage.code/-/releases).

## Quick start

Pick the platform you use, copy that folder to your project root, plus
`AGENTS.md` and `docs/`:

```bash
# GitHub Copilot
cp -r v3/implementation/.github         <your-project>/
mkdir -p <your-project>/.vscode
cp    v3/implementation/.vscode/mcp.json <your-project>/.vscode/

# Gemini CLI
cp -r v3/implementation/.gemini         <your-project>/

# Opencode
cp -r v3/implementation/.opencode       <your-project>/

# Cursor
cp -r v3/implementation/.cursor         <your-project>/

# Pi (terminal coding agent — https://pi.dev)
cp -r v3/implementation/.pi             <your-project>/.pi/

# Always include
cp    v3/implementation/AGENTS.md       <your-project>/
cp -r v3/implementation/docs            <your-project>/
```

Set the MCP env vars (`GITLAB_PERSONAL_ACCESS_TOKEN`, `BRAVE_API_KEY`, …) — the
full list lives in the generated `mcp.json`.

Then in your AI assistant:

```
/new-project "My SaaS application"
```

Detailed guide: [`v3/implementation/README.md`](v3/implementation/README.md)
and [project Wiki](https://gitlab.com/em-age/emage.code/-/wikis/home).

### v3 implementation

v3 is the **current release stream** (schema-first knowledge, cookbooks,
triggers, packaging, adapters, validation super-gate).

Start here:

- [`v3/implementation/README.md`](v3/implementation/README.md)
- [`docs/wiki/v3-implementation.md`](docs/wiki/v3-implementation.md)

Validate from the repository root:

```bash
python3 v3/implementation/scripts/check-v3.py --root v3/implementation --required --schemas --cookbooks --handoff-security --hook-policy --telemetry --benchmarks --registry --packaging --triggers --adapters
node v3/implementation/scripts/verify-v3.mjs --root v3/implementation
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
- Required files:
  - `README.md`
  - `docs/wiki/README.md`
  - `docs/wiki/home.md`
  - `docs/wiki/v3-implementation.md`
  - `v3/implementation/README.md`
  - `docs/releases/vX.Y.Z.md`
- Content verification script:
  ```bash
  python3 scripts/verify-release-docs.py --tag vX.Y.Z
  ```

This script checks required files, marker alignment, required usage sections,
and local/internal markdown link validity for core release docs.

---

## Architecture (6 layers)

1. **Commands** — 16 slash commands, the user entry point
2. **Orchestration** — Plan-Approve-Execute engine (`@orchestrator`, `@poc-orchestrator`)
3. **Agents** — 27 specialists (backend, frontend, qa, security, devops, …)
4. **Skills** — 22 reusable capabilities (code-review, validation-gates, …)
5. **Memory** — `docs/` artifacts + MCP `memory` server
6. **MCP servers** — declared once in [`v2/implementation/knowledge/mcp/servers.yaml`](v2/implementation/knowledge/mcp/servers.yaml)

Deep dive:
- [`v2/plan/00-vision-v2.md`](v2/plan/00-vision-v2.md)
- [`v2/plan/01-shared-knowledge-architecture.md`](v2/plan/01-shared-knowledge-architecture.md)
- [`v2/plan/04-sync-script-design.md`](v2/plan/04-sync-script-design.md)

---

## Benchmark and performance

v2 includes a deterministic benchmark suite for agent-team quality and runtime
health under `tests/performance/`.

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

1. Edit canonical knowledge under [`v2/implementation/knowledge/`](v2/implementation/knowledge/) — **never** the generated `.github/`, `.gemini/`, `.opencode/`, `.cursor/` folders.
2. Run the sync engine:
   ```bash
   cd v2/implementation
   node scripts/sync.mjs
   ```
3. Commit both the knowledge change **and** the regenerated platform folders.
4. CI runs [`scripts/verify.mjs`](v2/implementation/scripts/verify.mjs) — it
   fails the pipeline if generated folders drift from `knowledge/`.

Full contributor guide: [`CONTRIBUTING.md`](CONTRIBUTING.md)
Authoring rules: [`v2/implementation/knowledge/README.md`](v2/implementation/knowledge/README.md)

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

Report vulnerabilities privately — see [`v2/implementation/SECURITY.md`](v2/implementation/SECURITY.md).

---

## License

[MIT](LICENSE) © em-age
