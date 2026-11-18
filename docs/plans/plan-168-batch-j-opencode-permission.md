# plan-168 — Batch J: Opencode agent `tools:` map to a `permission:` block (SEC-T663-02)

**Created:** 2026-11-14
**Based on:**
- `docs/artifacts/security-review-t663-agent-denials-v1.md` (SEC-T663-02)
- `docs/plans/plan-128-batch-a-installer-generator.md` (§ Outcome: the Opencode docs call the agent `tools` map deprecated and prefer `permission`)
- `docs/artifacts/tracked-debt-register-v19.md` (batch J)
- `docs/artifacts/mcp-agent-denials-v1.md` and `docs/artifacts/mcp-agent-denials-evidence-v1.md`

**Scopes:** `T836`, `T837`, `T838`, `T839`, `T840`, `T841`, `T842`, `T843`, `T844`.

## User decision (2026-11-14, verbatim)

> J go

## Goal

The generator (`implementation/scripts/sync.mjs`) writes every Opencode agent file (`implementation/.opencode/agents/*.md`, 28 files) with a frontmatter `tools:` map. That map holds the agent's own grants and its `false` entries: the per-agent MCP denials (T663) and the six Playwright tools. Opencode's documentation marks this map deprecated and documents `permission:` as the control.

The generator is to emit each agent's controls as a frontmatter `permission:` block in the documented form, with the same effect:
- every tool an agent holds stays allowed;
- every denial stays denied;
- the order that Opencode's "last matching rule wins" needs is preserved: the wildcard first, then named allows.

Tests and documents follow. If the documented `permission` form cannot express the current denials exactly, T836 stops and reports before changing anything.

## Task Decomposition

1. **T836** (devops-engineer): read the current Opencode agent and permission documentation, change the generator, regenerate the mirrors and the registry, and update the tests and documents. Brief: `docs/tasks/task-T836.md`.
2. **T837** (security-engineer, read-only): review T836, above all for a lost, widened or reordered denial.
3. **T838** (orchestrator): the root refresh of `.opencode/`, **only with the user's approval at that moment**.
4. **The orchestrator:** gates, the full suite in a clean worktree, the merge request, and a pinned, squashed merge on a green pipeline.

## Constraints

- No `docker`. No live Opencode run: the live check stays K-20 / A-7.
- Never open `tests/golden/held-out/`. `tests/golden/**` and `scripts/scorecard.py` are protected.
- Never read secrets or the user's settings files.
- Do not hand-edit installed top-level folders. Author in `implementation/` and regenerate.

## Outcome (T836, T837; T838 pending the user's approval)

**Done on 2026-11-14:**
- **T836** (devops-engineer), commits `956c9d1c` and `00538942`.
  - The generator writes each Opencode agent's grants and denials as a frontmatter `permission:` map, with the same names in the same order (`true`→`allow`, `false`→`deny`). It no longer writes `tools:`.
  - All 28 agent files and the registry are regenerated. The tests, the manifest, the schema and the documents are updated.
  - Mutations that lose, widen or reorder a denial each fail the tests.
  - **Sources:** Opencode 1.x documentation (v1.18.35, via ctx7) and the current (2.x) documentation.
  - **The developer kept the V1 `permission:` map, not the 2.x `permissions:` list.** The 1.x documentation does not know the list, so the denials could be lost on the observed 1.19.2. **(unverified)**
- **T837** (security-engineer): `docs/artifacts/security-review-t837-opencode-permission-v1.md`, **PASS**.
  - **SEC-T663-02: fixed.** Its live-check part moves to SEC-T837-01.
  - **New, LOW, tracked:**
    - **SEC-T837-01:** re-run `opencode debug agent` on 1.19.2 against the new form.
    - **SEC-T837-02:** no supported Opencode version range is declared; how 2.x translates the V1 map is undocumented.
    - **SEC-T837-03** (pre-existing, unchanged by T836): `search`, `execute` and `web` are inert names. `read: allow` comes after Opencode's default `read: ask` for `*.env`, so the generated agents can read `.env` without a prompt.

**The orchestrator's ruling on T837's question.** The "Envsitter" rule in `security-guidelines.md` (§ Agent Safety Guards) is a rule on agent behaviour ("Do not read, cat, or copy: `.env`"). It is not a configuration control that the guidelines require the generator to emit. So SEC-T837-03 stays LOW and does not trigger the required-control rule. The orchestrator offers the user a fix in this batch rather than leaving it as debt, because it is a direct path to secret files.

**The orchestrator's own verification:**
- The gates, the full suite in a clean worktree and the pipeline (recorded in the merge request).
- Root drift is exactly 29 paths: the 28 files `.opencode/agents/*.md` and `AGENTS.md`. These are for T838.

**Budgets:**

| Task | Used (about) | Budget |
|---|---|---|
| T836 | 162k | 120k |
| T837 | 70k | 60k |

## Addendum 1 (2026-11-14): SEC-T837-03 fixed before the root refresh

**The user's words, verbatim:**

> SEC-T837-03: fix before root refresh.
> Once done do the root refresh

The second line is the user's approval of T838, the root refresh, once T839 and T840 are done and merged.

**Tasks:**
- **T839** (devops-engineer): stop emitting `read` in the Opencode `permission` map, so Opencode's default `read` rules apply again (allow, with `ask` for `*.env` and `*.env.*`). Drop or map the inert names `search`, `execute` and `web`, and correct any document that says `execute` grants a shell. Same branch.
- **T840** (security-engineer, read-only): review T839.

## Addendum 2 (2026-11-14): SEC-T840-01, a MEDIUM finding, fixed before the root refresh

**T839** (devops-engineer, commits `9d2f3e7d` and `b1072317`) no longer writes `read` or the inert names `search`, `execute`, `web`, `agent` and `todo`. Opencode's default read rules apply again. It keeps every MCP allow and deny, in the same order.

**T840** (security-engineer), `docs/artifacts/security-review-t840-opencode-read-v1.md`: **CONDITIONAL_PASS**.
- **SEC-T837-03:** fixed.
- **New: SEC-T840-01** (`SECURITY:MEDIUM`). It existed before T839, and v11.0.0 shipped with it.
  - On Opencode, the default rule `* allow *` gives every generated agent `bash`, `edit`/`write` and web access, read-only roles included.
  - Through the shell, every agent can also read the `gitlab` token.
- **New: SEC-T840-02** (LOW). The wiki's wording about the default read rules is imprecise.

**The user's decision**, asked in the session (question dialog; option label verbatim):

> Fix now, then refresh (Recommended)

The option described the following: "Same batch, before the root refresh: write deny-only entries (bash/edit/webfetch/websearch: deny) for agents that don't hold that tool, with tests and a security review. Then merge and run the root refresh you approved."

**Tasks:**
- **T841** (devops-engineer):
  - Generate deny-only entries for the agents that do not hold the matching source tool:
    - `bash: deny` where the source line has no `execute`;
    - `edit: deny` where it has no `edit`;
    - `webfetch: deny` and `websearch: deny` where it has no `web`.
  - Holders keep Opencode's default. No new allow is written.
  - Add tests and mutations for each class.
  - Fix SEC-T840-02's wording.
- **T842** (security-engineer, read-only): review T841.

**The SEC-T660-01 scope:** the user's acceptance for v11.0.0 named the GitLab-holding roles with a shell. After T841, the Opencode case narrows back to the agents whose source line holds `execute`. Register v20 must record this, and so must the acceptance question at the next release.

## Addendum 3 (2026-11-14): SEC-T842-01 (MEDIUM), the `task` path, fixed before the root refresh

**T841** (devops-engineer, commits `496ac559` and `a51a14dc`) writes deny-only `bash`, `edit`, `webfetch` and `websearch` entries for agents that do not hold the matching tool. SEC-T840-02's wiki wording is fixed.

**T842** (security-engineer): `docs/artifacts/security-review-t842-opencode-deny-v1.md`, **CONDITIONAL_PASS**.
- SEC-T840-01: reduced. Its direct path is closed.
- SEC-T840-02: fixed.
- **New: SEC-T842-01** (`SECURITY:MEDIUM`). Opencode allows `task` by default, and a subagent uses its own permissions. So an agent without a shell can still reach one by launching another agent.
- **New: SEC-T842-02** (LOW, tracked). For an agent with `bash: deny`, the only guard between the `read` tool and the out-of-project token file is the `external_directory` prompt.

**The user's decision** (question dialog, option label verbatim):

> Fix now, then refresh (Recommended)

The option described the change as: "Same batch, before the root refresh: add the deny-only task rule (26 of 28 agents), tests, security review; then merge and run the root refresh."

**Tasks:**
- **T843** (devops-engineer): add `"agent": ["task"]` to `permissionDenyUnlessGranted`. Every agent whose source line has no `agent` then gets `task: deny`. Only `orchestrator` and `poc-orchestrator` hold `agent`. Add tests and mutations.
- **T844** (security-engineer, read-only): review T843. When `task` is closed, SEC-T840-01 closes with SEC-T842-01.

## Outcome (T836 to T844; T838 next, approved by the user)

**Done on 2026-11-14.**

**What changed:**
- **T836:** the `tools:` map becomes a `permission:` map (SEC-T663-02).
- **T839:** `read` and the inert generic names are no longer written (SEC-T837-03).
- **T841:** deny-only `bash`, `edit`, `webfetch` and `websearch` for agents that do not hold them (SEC-T840-01, direct path).
- **T843:** deny-only `task` for every agent except the two orchestrators (SEC-T842-01).

**Reviews:**
- T837: PASS.
- T840: CONDITIONAL_PASS. It raised SEC-T840-01; the user chose "Fix now, then refresh (Recommended)".
- T842: CONDITIONAL_PASS. It raised SEC-T842-01; the user chose "Fix now, then refresh (Recommended)".
- T844: **PASS**.

**Statuses for register v20:**
- **Fixed:** SEC-T663-02, SEC-T837-03, SEC-T840-01, SEC-T840-02 and SEC-T842-01. None of these is verified in a live run; the live check stays under SEC-T837-01.
- **New, LOW, tracked:**
  - SEC-T837-01: live `opencode debug agent` check.
  - SEC-T837-02: no version range is declared for Opencode 2.x.
  - SEC-T842-02: the `external_directory` prompt is the only guard for the token file; documented in PREREQUISITES.
  - SEC-T844-01: the orchestrators can launch the built-in agents.

**SEC-T660-01 on Opencode, as restated by T844:**
- **Direct shell, and with it the token:** the 15 agents that hold `execute`, the built-in agents, and the user's own agents.
- **Delegation:** only the two orchestrators.
- **The other 13 agents:** no shell and no delegation. Their only path to the token is `read`, behind the `external_directory` prompt.

**The orchestrator's own verification:**
- `orchestrator.md` and `poc-orchestrator.md` are the only agents without `task: deny`.
- No agent writes `read`.
- The gates pass.
- The full suite and the pipeline are recorded in the merge request.
- The root drift is exactly 29 paths, which T838 refreshes.

**Budgets:**
- devops-engineer: about 250k tokens across T836, T839, T841 and T843, against 120k + 60k + 70k + 50k.
- security-engineer: about 182k across T837, T840, T842 and T844, against 60k + 40k + 40k + 35k.

## Addendum 4 (2026-11-14): failed suite, test fix, root refresh (T838)

**The failed run.** The full suite at `3a895f61` failed with 57 failures, and both pipelines failed. There were two causes:
- 56 failures were in `tests/functional/test_platform_projections.py`, which still pinned the `tools:` form. The developer's check set had missed that module.
- 1 failure was in `test_root_install_parity`: the 29 paths had changed but were not yet refreshed.

**The test fix.** In `2b1081ba` the developer updated `test_platform_projections.py`. It now pins the `permission:` map and checks the expected allows and denials, derived independently from `servers.yaml` and the manifest. Mutations W1 to W4 fail as they should. A wider set of 43 modules passes, except the drift test and one file that contains no tests.

**T838, the root refresh.** It ran with the user's approval ("Once done do the root refresh"):
- `bash scripts/install.sh --target <worktree> --platform all --projections-only` exited 0.
- It changed exactly the 29 declared paths: the 28 files `.opencode/agents/*.md` and `AGENTS.md`.
- `--print-drift` then gave `[]`.
