# plan-178 — Batch AB: Opencode permission, third round

**Created:** 2026-11-19
**Based on:**
- `docs/artifacts/tracked-debt-register-v23.md` (§ 5 batch AB; § 6.2 item 49);
- `docs/artifacts/security-review-t856-batch-aa-v1.md` (SEC-T856-01 to -03, § 2.3);
- `docs/artifacts/mcp-agent-denials-evidence-v3.md`.

**Scopes:** `T861`, `T862`, `T863`. Batch X runs in parallel as plan-177.

## User decision (2026-11-19, verbatim)

> X + AB go

## Task Decomposition

1. **T861** (devops-engineer):
   - **(a) SEC-T856-03.** In PREREQUISITES and the wiki, state two things: only the default token directory name (`gitlab-mcp`) is covered, and the token must not be linked into a project.
   - **(b) SEC-T856-01.** Write a redaction rule for future evidence runs:
     - Use a neutral scratch root, or replace the scratch paths in stored raw output with `<path>`, before hashing and storing.
     - Record the redaction in the evidence's Metadata.
     - Put the rule where the evidence method is described (the wiki, or a short method note) and enforce it with a test on new evidence directories. Evidence v2 and v3 stay unchanged.
   - **(c) SEC-T856-02, the optional part.** Test whether a deny-only `external_directory` map for the token directory can be generated without changing Opencode's built-in tool-output allow. Read the 1.19.2 `agent.ts` and `external-directory.ts` logic.
     - **If it can,** emit it for the agents without `execute`, observe it live with the evidence method (redacted per (b)) as `docs/artifacts/mcp-agent-denials-evidence-v4.md`, add tests and mutations, and declare the root drift.
     - **If it cannot,** record why, and keep the wiki's defense-in-depth note.
2. **T862** (security-engineer, read-only): review T861, with a status per id. Restate item 49 only if it changes.
3. **T863** (orchestrator): the root refresh, if (c) ships. It **needs the user's approval at that moment.**

## Constraints

- No `docker`.
- No model or API key in the live run; `opencode debug agent` only.
- Never read secrets, any token file or directory, the user's settings files or the user's real Opencode configuration.
- Never open `tests/golden/held-out/`.
- No change to any other platform's output.

## Outcome

**Done on 2026-11-19.**

**T861** (devops-engineer):
- **(a) SEC-T856-03, `ed214742`.** PREREQUISITES and the wiki state that only the default `gitlab-mcp` directory name is covered, and that the token must never be placed under a project or linked into one.
- **(c) SEC-T856-02, `2603bb57`.** A deny-only `external_directory: {"*/gitlab-mcp/*": deny}` is emitted for the 13 agents without `execute`, through the new manifest key `permissionExternalDirectoryDenyUnlessGranted`.
  - It is validated like the `read` map. `external_directory` is refused in `permissionKeys`.
  - Opencode 1.19.2's `agent.ts` drops its built-in tool-output allow only for a deny whose pattern is exactly that glob. A test pins the generated pattern so it can never be that glob. The allow stays the last rule.
  - **Evidence:** `docs/artifacts/mcp-agent-denials-evidence-v4.md`, observed live on 1.19.2.
  - The Claude Code, Cline and GitHub outputs are byte-identical.
- **(b) SEC-T856-01, `d550037c`.**
  - A wiki rule: use a neutral scratch root or replace paths with `<path>`, and record a `**Redaction**` Metadata line.
  - `T861EvidenceRedactionTests` enforces it for every evidence directory after v3. v4 was taken from `/tmp/evidence-run`.
- **`779010f4`:** the projection-test follow-up.

**T862** (security-engineer): `docs/artifacts/security-review-t862-batch-ab-v1.md`, **PASS**. Nothing is widened.
- **SEC-T856-01: fixed.**
- **SEC-T856-03: fixed.**
- **SEC-T856-02: stays tracked LOW, narrowed.** The token directory itself is now denied for `read`, `grep` and `glob`. What remains is a `grep` on a parent directory such as `/dev/shm`, which by default resolves to `ask`.
- **New, LOW:**
  - **SEC-T862-01,** a stale wiki sentence. The orchestrator corrected it in `f9f3a86b`.
  - **SEC-T862-02,** gaps in the redaction test (tracked):
    - its user-name check uses whoever runs the test;
    - it does not scan the evidence `.md`;
    - it has no macOS or Windows prefixes.
- **Item 49 (d)** is restated in § 4. The SEC-T660-01 scope is narrower, not closed.

**T863** (orchestrator): the root refresh, with the user's approval at that moment (question dialog, option label verbatim: "Refresh now (Recommended)").
- `install.sh --projections-only` changed exactly the 13 declared `.opencode/agents/*.md` files.
- The drift baseline is emptied, and drift is `[]`.

**The orchestrator's own verification:**
- **My own parser** compared the v4 raw lists of context-retriever, demo-agent, orchestrator and tech-lead with the generated maps: all match, and only the built-in tool-output allow follows.
- **Placement:** exactly the 13 agents with `bash: deny` carry the map, and no agent has an `external_directory` allow.
- **Redaction:** the v4 raw files are free of `/tmp/claude-`, `/home/`, `/Users/` and `emage-Code`.
- **The main checkout** holds only the user's own edits.
- **The gates, the full suite and the pipeline** are recorded in the merge request.

**Left for the user:** T861 created `/tmp/evidence-run`, a neutral evidence root (allowed by the brief). It holds scratch copies and the Opencode binary. The user may remove it.

**For register v24:**
- SEC-T856-01 and -03 fixed;
- SEC-T856-02 narrowed;
- SEC-T862-01 minted and fixed;
- SEC-T862-02 new, LOW;
- item 49 (d) restated.

**Budgets:**

| Task | Used (about) | Budget |
|---|---|---|
| T861 | 85k | 90k |
| T862 | 35k | 40k |
| T863 | under 10k | 20k |
