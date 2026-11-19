# plan-170 — SEC-T837-01: live `opencode debug agent` check of the `permission:` form

**Created:** 2026-11-19
**Based on:**
- `docs/artifacts/tracked-debt-register-v20.md` (batch U, SEC-T837-01; § 6.2 item 49);
- `docs/artifacts/security-review-t837-opencode-permission-v1.md` (SEC-T837-01);
- `docs/artifacts/mcp-agent-denials-evidence-v1.md` (the method and the stored lists);
- `docs/plans/plan-168-batch-j-opencode-permission.md` (§ Outcome).

**Scopes:** `T846`, `T847`.

## User decision (2026-11-19, verbatim)

> SEC-T837-01 go

## Objective

Observe, with the real Opencode binary, how opencode-ai 1.19.2 resolves the generated `permission:` maps. These are the T836 form, as narrowed by T839, T841 and T843. Store the result as `docs/artifacts/mcp-agent-denials-evidence-v2.md` with its raw output.

The v1 lists were taken with the `tools:` form, before T839, T841 and T843. So v2 is **not** expected to be identical to v1. Instead:
1. Each resolved agent segment must equal that agent's generated `permission:` map: the same names, actions and order.
2. Every difference from v1 must be explained by T836, T839, T841 or T843.

## Task Decomposition

1. **T846** (devops-engineer): the live run, `docs/artifacts/mcp-agent-denials-evidence-v2.md`, its raw files, and the wiki Status line.
   - **Method.** Repeat the evidence v1 method:
     - `npm install opencode-ai@1.19.2` into an empty scratch directory.
     - Use empty scratch `HOME` and `XDG_*` directories, and a minimal environment (`env -i` with `PATH` and those variables only).
     - Use a scratch project holding a copy of `implementation/.opencode/agents/` at develop `c764005a`.
     - Use the same scratch `opencode.json`: no `mcp` or `instructions` keys, and v1's hostile global `permission` first.
   - **Agents:** "Tech Lead", "QA Engineer", "Demo Agent" and "Orchestrator".
     - Demo Agent is one of the 13 agents without a shell, so it shows the `bash` and `task` denials.
     - Tech Lead and QA Engineer hold `execute`, so they show `task: deny` only.
     - Orchestrator holds both `execute` and `agent`.
     - Add a fifth agent, "Context Retriever" (`context-retriever.md`). It carries all five denials: `bash`, `edit`, `webfetch`, `websearch` and `task`.
   - **Comparison:** compare by script, not by eye.
2. **T847** (security-engineer, read-only): review T846 against SEC-T837-01. Decide whether SEC-T837-01 is fixed. Decide whether the "unverified" notes about live runs on SEC-T663-02, SEC-T837-03, SEC-T840-01 and SEC-T842-01 can be lifted. A refused tool call stays out of scope (K-20).

## Constraints

- No `docker`.
- No model, no API key, no MCP server started, no credentials in the environment.
- Never read secrets or the user's settings files.
- Never open `tests/golden/held-out/`.
- No source or generator change. If the run shows a defect, stop and report it as a blocker.

## Outcome

**Done on 2026-11-19.**

**T846** (devops-engineer, commit `eb77fa28`) wrote `docs/artifacts/mcp-agent-denials-evidence-v2.md`, with the raw output of `opencode debug agent` on opencode-ai 1.19.2.
- **Run conditions:** `env -i` with empty `HOME` and `XDG_*` directories; no MCP server; v1's hostile global permission first.
- **Agents:** Tech Lead, QA Engineer, Demo Agent, Orchestrator and Context Retriever.
- **Result:** each resolved agent segment equals the generated `permission:` map, in names, actions and order. The built-in rules (0-11), the global rules (12-22) and the final rule are unchanged from v1.
- **Differences from v1:** each is attributed to T836, T839, T841 or T843, or to three earlier intended changes: T676, T688 and T666. None widens access.
- **The wiki Status line** now cites evidence v2.

**T847** (security-engineer): `docs/artifacts/security-review-t847-opencode-live-v1.md`, **PASS**.
- **SEC-T837-01:** fixed.
- **"Not verified in a live run" is lifted for rule resolution only** on SEC-T663-02, SEC-T837-03, SEC-T840-01 and SEC-T842-01. The new wording is "resolved rule list observed on 1.19.2 (evidence v2); a refused tool call is not observed (K-20)".
- **Still unverified:**
  - how 1.19.2 maps `bash`, `edit`, `webfetch`, `websearch` and `task` onto its tools at call time;
  - the 23 agents that were not run, which rest on the generator.
- **SEC-T663-03:** no change of status. The merge tool now resolves to deny for all five agents (fails closed, by reading). Named tools an agent holds are still overridden.
- **New: SEC-T847-01** (LOW, tracked). Evidence v1 says an unmatched name defaults to "ask". On 1.19.2, built-in rule 0 is `*: allow`, so such a name resolves to allow. v1 is immutable; register v21 records that evidence v2 § 4 supersedes it on this point.

**The orchestrator's own verification:**
- **My own script, independent of T846's:**
  - For all five agents, `rules[23:23+n]` equals the generated frontmatter map, and only the built-in `external_directory` rule follows it.
  - Rules 0-22 and the final rule equal v1 for the four v1 agents, with path patterns normalised.
- **Raw files:** the sha256 values match the artifact. They hold no credentials; the keyword hits are agent prompt text only, and there is no `glpat`.
- **Gates, full suite and pipeline:** recorded in the merge request.

**For register v21:**
- SEC-T837-01 is fixed; batch U shrinks by one.
- SEC-T847-01 is new and tracked-LOW.
- The live-run notes on the four ids are narrowed as above.
- The SEC-T663-03 note.

**Budgets:**

| Task | Used (about) | Budget |
|---|---|---|
| T846 | 45k | 60k |
| T847 | 30k | 40k |
