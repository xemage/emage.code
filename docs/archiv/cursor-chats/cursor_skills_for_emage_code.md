# Skills for emage.code
_Exported on 6/16/2026 at 14:19:24 GMT+2 from Cursor (3.7.36)_

---

**User**

/agentskill-sh-learn Learn skills helpful für 'emage.code' 

---

**Cursor**

Searching agentskill.sh for skills that fit the emage.code project — I'll analyze the repo stack first, then run targeted searches.


Learn skill is outdated — updating it, then analyzing the project stack for targeted skill searches.


Curating recommendations and prompting which skills to install.


**Install skills for emage.code**

> **Which skill would you like to install? (Top picks for your multi-agent orchestration + GitLab + MCP stack)**
> - multi-agent-task-orchestrator ✔
> - gitlab-ci-patterns-v2
> - mcp-builder-v2
> - Browse more / search again

Installing **multi-agent-task-orchestrator** — fetching preview details, then installing.


## Recommended for emage.code

Based on your **multi-agent orchestration + GitLab + MCP + Python/Node** project on branch `develop`:

### Already covered locally

emage.code ships **25 canonical skills** under `implementation/knowledge/skills/` — including `plan-approve-execute`, `validation-gates`, `checkpoint-protocol`, `task-management`, `gitlab-management`, `systematic-debugging`, and `ci-cd-pipeline`. External skills mainly **complement** these, not replace them.

### Already installed (agentskill.sh)

| Skill | Author | Purpose |
|-------|--------|---------|
| **learn** | @agentskill-sh | Find & install skills |
| **review-skill** | @agentskill-sh | Audit SKILL.md quality |

---

## Skills matching your stack

| # | Skill | Author | Security | Quality | Fit for emage.code |
|---|-------|--------|----------|---------|-------------------|
| 1 | **multi-agent-task-orchestrator** | @diegosouzapw | 100/100 | 75 | Task routing, quality gates, anti-duplication — aligns with your orchestrator model |
| 2 | **gitlab-ci-patterns-v2** | @diegosouzapw | 82/100 | 83 | `.gitlab-ci.yml` patterns for your drift/sync pipeline |
| 3 | **mcp-builder-v2** | @diegosouzapw | 97/100 | 75 | Extend `implementation/knowledge/mcp/servers.yaml` with new MCP servers |
| 4 | **GitLab CI/CD Pipeline Orchestrator** | @agentskillexchange | 99/100 | 50 | DAG pipelines, multi-project CI — mirrors your task DAG concept |
| 5 | **owasp-security-review** | @diegosouzapw | 100/100 | 100 | OWASP Top 10 audits for your security-engineer agent |

**Descriptions:**
1. **multi-agent-task-orchestrator**: Route tasks to specialized agents with anti-duplication, quality gates, and heartbeat monitoring.
2. **gitlab-ci-patterns-v2**: Comprehensive GitLab CI/CD pipeline patterns for automated testing, building, and deployment.
3. **mcp-builder-v2**: Create MCP servers that enable LLMs to interact with external services through well-designed tools.
4. **GitLab CI/CD Pipeline Orchestrator**: Build and manage GitLab CI/CD pipelines with DAG scheduling and Runner fleet management.
5. **owasp-security-review**: Review code against OWASP Top 10:2025 with remediation guidance.

---

## Installed: multi-agent-task-orchestrator

**Author:** @diegosouzapw  
**Security:** 100/100  
**Location:** `.agents/skills/diegosouzapw-multi-agent-task-orchestrator/`  
**Platforms:** Cursor, Gemini CLI, GitHub Copilot, Opencode

---

Want to install more? Reply with a number from the table, or run `/learn gitlab ci`, `/learn mcp builder`, etc.

---

**User**

Question:
'multi-agent-task-orchestrator' was installed at @.agents/ 
Is this the (only) folder Cursor is using?
I'm asking as the implementation of 'emage'code' (@implementation/ ) uses the folder '.cursor' (and subfolder agents, commands, rules, skills in it)

---

**Cursor**

Checking how emage.code projects skills into `.cursor/` and where agentskill.sh installs skills under `.agents/`.


Short answer: **no** — `.agents/` is not the only folder Cursor uses, and it is **not** the folder emage.code owns.

## Two parallel skill systems

| Location | Who owns it | What it contains |
|----------|-------------|------------------|
| **`.cursor/skills/`** | emage.code (via sync) | Canonical skills from `implementation/knowledge/skills/` |
| **`.agents/skills/`** | agentskill.sh CLI | Skills installed via `/learn` (e.g. `multi-agent-task-orchestrator`) |

agentskill.sh deliberately installs into `.agents/skills/`. That path is **not** referenced anywhere in emage.code’s sync pipeline or docs.

## What emage.code uses for Cursor

Per `implementation/platforms/cursor.json`, sync projects into **`.cursor/`**:

```6:10:implementation/platforms/cursor.json
  "fileMap": {
    "agents":       { "dir": "agents",   "ext": ".mdc" },
    "commands":     { "dir": "commands", "ext": ".mdc" },
    "instructions": { "dir": "rules",    "ext": ".mdc" },
    "skills":       { "dir": "skills",   "preserveTree": true }
```

Flow:

```
implementation/knowledge/skills/  →  sync.mjs  →  implementation/.cursor/skills/
                                              →  (install.sh copies to) <project>/.cursor/skills/
```

So emage.code’s **agents, commands, rules, skills, and `mcp.json`** all live under **`.cursor/`**, not `.agents/`.

## What Cursor actually loads

Cursor discovers skills from **multiple** places, not just one:

1. **`<workspace>/.cursor/skills/`** — emage.code projected skills  
2. **`<workspace>/.agents/skills/`** — agentskill.sh installs (your new skill is here only)  
3. **`~/.cursor/skills-cursor/`** — user-global Cursor skills  
4. **Plugin cache paths** — e.g. GitLab/Render plugin skills  

So `multi-agent-task-orchestrator` is available because Cursor also reads `.agents/skills/`. It is **not** in `.cursor/skills/` and is **not** part of emage.code’s canonical registry.

## In this repo specifically

You effectively have **three** skill-related trees:

| Path | Skills count | Role |
|------|--------------|------|
| `implementation/.cursor/skills/` | 25 | Fresh sync output (source of truth for distribution) |
| `.cursor/skills/` (repo root) | 22 | Installed copy — missing `receiving-code-review`, `systematic-debugging`, `verification-before-completion` |
| `.agents/skills/` | 3 | agentskill.sh only (`learn`, `review-skill`, `multi-agent-task-orchestrator`) |

Cursor’s workspace root is the repo root, so it uses **root `.cursor/`**, not `implementation/.cursor/` directly. `implementation/.cursor/` is what gets packaged/copied to consumer projects via `install.sh`.

## Practical implication

- **emage.code orchestration** (`/discover-skills`, mandatory skill workflow in `AGENTS.md`) expects skills under **`knowledge/skills/`** → **`.cursor/skills/`**.
- **agentskill.sh skills** sit outside that pipeline in **`.agents/skills/`**. They work in Cursor, but won’t be synced, versioned, or validated by emage.code CI.

If you want `multi-agent-task-orchestrator` to be a first-class emage.code skill, you’d need to add it to `implementation/knowledge/skills/` and run sync — not leave it only in `.agents/`. I can outline that workflow in Agent mode if you want.

