# Security Review T847: live `opencode debug agent` evidence v2 (T846, SEC-T837-01)

## Metadata

- **Date:** 2026-11-19
- **Task:** T847 (plan-170). The user's decision: "SEC-T837-01 go". LOW policy, the user's words: "Track LOW items as debt, stop chasing (Recommended)".
- **Reviewer:** security-engineer (read-only; no shell; no file edited)
- **Based on:** worktree `/home/emage/Code/emage/worktrees/agent-devops-engineer-T846`, branch `agent/devops-engineer/T846`, commit `eb77fa28` (on `f32100bc` = develop `c764005a` + the plan-170 commit); `docs/artifacts/mcp-agent-denials-evidence-v2.md` (T846); `docs/artifacts/mcp-agent-denials-evidence-v1.md` (T663; in particular § "SEC-T663-03" and the last-match paragraphs at lines 94, 188 and 255); `security-review-t837-opencode-permission-v1.md` (SEC-T837-01..03); the findings tables of `security-review-t840-opencode-read-v1.md`, `security-review-t842-opencode-deny-v1.md` and `security-review-t844-opencode-task-v1.md`; `docs/wiki/mcp-servers.md` line 128 at `eb77fa28`; `tracked-debt-register-v20.md` (id listing only); the orchestrator's independent parse of the raw files (brief of T847).
- **Method limits:**
  - I read evidence v2 in full, including the five indexed rule lists, and checked each list by hand against the stated segment layout (built-in 0-11, global 12-22, agent 23..n-2, final `external_directory`).
  - I did **not** open the raw `raw-*.json` files or re-run T846's `compare.py`. That each indexed list in evidence v2 equals the raw file, and that each agent segment equals its generated `permission:` map, rests on T846's script plus the orchestrator's own independent script **(not re-checked by me; unverified by me)**.
  - I did not read the 28 generated `implementation/.opencode/agents/*.md` files. Agents outside the five observed ones rest on the generator and its tests (T836, T841, T843).
  - No Opencode was run and no tool call was made. A refused tool call stays **not observed (K-20)**.

## Scope

1. Does evidence v2 meet SEC-T837-01's remediation? That remediation is: re-run `opencode debug agent` on opencode-ai 1.19.2 for Tech Lead, QA Engineer, Demo Agent and Orchestrator against the `permission:` form, diff against v1, store the result as evidence v2, and keep the refused-call check under K-20.
2. For SEC-T663-02, SEC-T837-03, SEC-T840-01 and SEC-T842-01: can "not verified in a live run" be lifted?
3. Rulings on the two observations: SEC-T663-03, and rule 0 being `*: allow`.

Out of scope: a refused tool call (K-20); Opencode 2.x (SEC-T837-02); the SEC-T663-03 runs with an `agent.<name>.permission` block or `OPENCODE_CONFIG_CONTENT`, which were not repeated.

## Assessment of the evidence

- **Method.** The method is sound and at least as strict as v1:
  - pinned `opencode-ai@1.19.2`, with the binary hash recorded and the `postinstall` script not run;
  - `env -i` with empty `HOME` and `XDG_*`, so no user configuration leaks in;
  - no MCP server and no `instructions`, so nothing is started or fetched;
  - the same hostile global block as v1, written first;
  - raw stdout stored verbatim, with hashes.
- **Coverage.** All four agents named in SEC-T837-01 are covered, plus Context Retriever, which is the only one of the five that exercises all of T841's deny classes (`bash`, `edit`, `webfetch`, `websearch`).
- **Equality.** Check (a), that each agent segment equals its generated map entry for entry and in order, passes for all five agents. Two independent scripts agree on it (T846's and the orchestrator's). Check (c), that rules 0-22 and the final rule are unchanged from v1, also passes.
- **Diff against v1.** SEC-T837-01 expected the lists to be identical. They are not, but every difference is listed and attributed:
  - T839, T841 and T843 account for most of them.
  - Three earlier intended changes account for the rest: T676 (`github_*` removed), T688 (`gitlab_get_pipeline_job_output` removed) and T666 (the Orchestrator's `gitlab_*: deny` followed by 16 named allows).
  - I checked the T666 and T688 attributions against `AGENTS.md`. It names 16 orchestrator GitLab tools, which matches indices 25-40 of the Orchestrator list, and it states that no agent holds a raw job-output tool (T688). Both agree.
  - I did not check the commit hashes `44c15b49`, `d89f75f2` and `58149964` **(unverified)**.
  - No difference is unexplained, and none widens access. Every difference is a removed inert name, a removed allow, or an added deny.
- **Hand check of the indexed lists (mine).**
  - Every agent segment keeps its order: the `<server>_*: deny` wildcard comes before that server's named allows, and the trailing denies come last.
  - No agent segment contains an allow for a tool named in the server-level six-tool Playwright deny that is not followed by that tool's deny. In QA Engineer, `playwright_browser_click` is allowed at #31 and the six denies follow at #63-#68; Demo Agent follows the same pattern.
  - No agent segment contains a `read` rule.
- **Raw files.** The orchestrator reports no credentials (no `glpat`) and only scratch paths and `/tmp/opencode/*` in the `external_directory` patterns, as in v1. I did not re-check this **(unverified by me)**. This is not a finding: the paths are session scratch paths, not secrets.
- **Wiki line 128.** It is accurate:
  - it states that v2 observed the resolved lists of the current `permission:` form for the five agents;
  - it says that this shows only the rule lists;
  - it keeps the refused call marked **unverified, K-20**.

  It overclaims nothing.

## Per-finding statuses

| ID | Prior status | Ruling | Can "not verified in a live run" be lifted? |
|----|--------------|--------|----------------------------------------------|
| SEC-T837-01 | Open, tracked LOW | **Fixed** by T846 (evidence v2). The remediation is met: 1.19.2 was re-run on the `permission:` form, the result was diffed against v1, every difference was attributed, and the result was stored as evidence v2. The refused-call part stays under K-20. | n/a (this is the live check). The refused call stays open under K-20. |
| SEC-T663-02 | Fixed by T836 (live part carried by SEC-T837-01) | Stays **Fixed**. | **Yes, for rule resolution.** It is observed that 1.19.2 resolves the frontmatter `permission:` map into the same ordered rules, for five agents. **No, for a refused call (K-20).** |
| SEC-T837-03 | Open, tracked LOW (`read: allow` re-allowed `.env`) | Fixed by T839 (per evidence v2 § 3, `read` is no longer written). I did not review T839's fix itself here. | **Yes, for the five observed agents.** No agent segment holds a `read` rule, so the last `read` rules from the generated configuration are the built-in `*.env` and `*.env.*` ask rules (#9 and #10), plus `*.env.example` allow (#11). Note: in this test the hostile user rule #12 `*: allow` re-allows `.env` reads. That comes from the user's own configuration, not from the generated files. My reading of how pattern `*` matches a path is **unverified**. For the other 23 agents this rests on the generator **(not observed)**. |
| SEC-T840-01 | MEDIUM → Fixed by T841 + T843 (live unverified) | Stays **Fixed**. | **Yes, for rule resolution of the deny classes observed:** `bash: deny` (Demo Agent #52, Context Retriever #40), and `edit`, `webfetch` and `websearch` deny (Context Retriever #41-#43), each the last match for its name. The holders (Tech Lead, QA Engineer, Orchestrator) correctly fall through to Opencode's default. **Not lifted** for two points: how 1.19.2 maps the permission names `edit`/`bash`/`webfetch`/`websearch` onto its tools at call time (for example whether `edit` also governs write and patch), which evidence v2 § 5 leaves **unverified**; and a refused call (K-20). The read-only roles that motivated the finding (security-engineer, product-owner, scrum-master) were not among the five agents. They rest on the same generator path **(not observed)**. |
| SEC-T842-01 | MEDIUM → Fixed by T843 (live unverified) | Stays **Fixed**. | **Yes, for rule resolution:** `task: deny` is the last match for Tech Lead (#40), QA Engineer (#77), Demo Agent (#53) and Context Retriever (#44). The Orchestrator has no `task` entry, which matches its intended exemption. **Not lifted** for two points: that the `task` permission governs the subagent-launch tool at call time **(unverified)**, and a refused `task` call (K-20). |
| SEC-T663-03 | As its register records it (named in v20 "with no change of status") | **No change of status.** See observation 1. | n/a |

Suggested wording for the records: "resolved rule list observed on opencode-ai 1.19.2 (evidence v2); a refused tool call is not observed (K-20)". This replaces "live unverified" for the four ids above, with the per-row caveats.

## Rulings on the observations

**1. SEC-T663-03.**

- **What v2 shows.** v2 shows the resolved list, not a re-run of the three SEC-T663-03 variants. It shows that the generated agent segment (from #23) still comes **after** the user's global rules (12-22). That is the mechanism SEC-T663-03 recorded, now observed for the `permission:` form for the global configuration.
- **The merge tool.** For `gitlab_merge_merge_request`, the user's `ask` (#16) is now followed by each agent's own `gitlab_*: deny`. By last-match reading (computed, not run) the tool resolves to **deny** for all five agents. The override therefore fails closed: deny is stricter than the user's ask.
- **What SEC-T663-03 is about.** SEC-T663-03 itself is about a **held** tool, and that part is unchanged. Two examples:
  - the Orchestrator's `gitlab_create_merge_request: allow` (#28) still comes after a user's global rule, so a global `ask` on it is overridden;
  - QA Engineer's named allows behave the same way.

  `AGENTS.md` already states exactly this ("a global `ask` on `gitlab_create_merge_request` is overridden for the three agents that hold it"; "a tool that no agent holds, such as `gitlab_merge_merge_request`, stays denied"), so no text is wrong.
- **What is not observed for the `permission:` form.** The project-config `agent.<name>.permission` variant and the `OPENCODE_CONFIG_CONTENT` variant were not run on the `permission:` form **(unverified)**.
- **Ruling.** No status change and no new finding. The register may add one note: "v2 (T846): the global-configuration placement is observed unchanged for the `permission:` form; the v1 merge-tool example now resolves to deny (fails closed, by reading); held named tools are still overridden; the agent-block and `OPENCODE_CONFIG_CONTENT` runs were not repeated."

**2. Rule 0 is `*: allow`.**

- **Why it counts as a finding.** Evidence v1 says, three times (lines 94, 188, 255), that without a user `*` rule an exempt name such as `hindsight_recall` "would match no rule and depend on the default behaviour, ask in the current core". In v1's own lists, rule 0 is the built-in `*: allow`, and check (c) shows that v1 and v2 share rules 0-11. On 1.19.2, therefore, every name matches at least rule 0, and a name with no later rule resolves to **allow**, not ask. The sentence states the default as stricter than it is. That is a documentation error in a security evidence artifact, so it is a finding.
- **Impact.** The impact is low, for three reasons:
  - The affected names are the exempt servers (brave, context7, hindsight, cwso, hf-mcp-server, toolradar). The user chose to leave them allowed (`denyUnlessGranted: false`, 2026-10-16).
  - SEC-T840-01 already relied on rule 0 being `* allow`.
  - No generated control depends on the "ask" claim.
- **Current wording elsewhere.** My search outside `tests/golden/` on the main checkout finds the wrong wording only in evidence v1. Evidence v2 § 4 already states the correct reading. Wiki line 128 does not repeat the error.
- **Fix.** v1 is immutable, so the fix is a pointer, not an edit: SEC-T847-01, LOW.

## Findings

| ID | Severity | Category | Location | Description | Remediation | Owner / status |
|----|----------|----------|----------|-------------|-------------|----------------|
| SEC-T847-01 | SECURITY:LOW | A05 | `docs/artifacts/mcp-agent-denials-evidence-v1.md` lines 94, 188, 255 | v1 says an unmatched name "would match no rule and depend on the default behaviour, ask in the current core". On opencode-ai 1.19.2, built-in rule 0 is `*: allow`, which appears in v1's and v2's resolved lists alike, so such a name resolves to allow. The artifact states the default as stricter than observed. The affected names are the exempt servers, which are allowed by the user's decision; no generated control depends on the claim. | Do not edit v1 (it is immutable). Record in register v21, and next to the wiki's evidence links, that evidence v2 § 4 supersedes v1 on this point: "rule 0 is a built-in `*: allow`; a name with no later rule resolves to allow on 1.19.2". Any future text about Opencode's default must cite rule 0 of the stored lists. | technical-writer or devops-engineer; open, tracked LOW |
| SEC-T837-01 | SECURITY:LOW | A05 | `docs/wiki/mcp-servers.md` Status line; evidence v1 | No observed resolution of the `permission:` form existed. | Evidence v2 (T846) observes it for five agents on 1.19.2. | **Fixed** (refused call: K-20) |
| SEC-T663-02 | SECURITY:LOW | A05 | — | Migrate `tools:` to `permission:`. | Done by T836; resolution now observed. | **Fixed**; "live unverified" lifted for resolution (refused call: K-20) |
| SEC-T837-03 | SECURITY:LOW | A01 / A05 | generated `read: allow` | `read: allow` re-allowed `.env`. | T839 stopped writing `read`; v2 shows no `read` rule in the five agent segments. | **Fixed** (fix not re-reviewed here); resolution observed for five agents |
| SEC-T840-01 | SECURITY:MEDIUM (historical) | A01 / A04 | generated deny-only `bash`/`edit`/`webfetch`/`websearch` | Default shell, edit and web access. | T841 + T843; v2 observes the denies as last match (Demo Agent, Context Retriever). | **Fixed**; "live unverified" lifted for resolution only. Tool mapping at call time and a refused call remain unverified (K-20). |
| SEC-T842-01 | SECURITY:MEDIUM (historical) | A01 / A04 | generated deny-only `task` | Delegation to a shell-holding agent. | T843; v2 observes `task: deny` as last match for four agents and none for the Orchestrator. | **Fixed**; "live unverified" lifted for resolution only. That `task` governs the launch tool at call time, and a refused call, remain unverified (K-20). |
| SEC-T663-03 | as registered | A01 | — | A user prompt on a held tool is overridden. | — | **No change**; the note under observation 1 may be added to the register |

## Compliance Checklist
- [x] OWASP Top 10 reviewed (relevant: A01, A05, A08)
- [x] Authorization enforced: the resolved denials equal the generated maps for the five agents, and no difference from v1 widens access
- [x] Secrets management: no credential read or written; raw files reported clean by the orchestrator (not re-checked by me)
- [x] Dependencies: the pinned opencode-ai 1.19.2 binary is hash-recorded; npm `postinstall` was not run
- [ ] Refused tool call observed (K-20, out of scope)

## VERDICT: PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 new (SEC-T840-01 and SEC-T842-01 were already fixed) | — | 0 |
| LOW | 2 (SEC-T837-01, SEC-T847-01) | 1 (SEC-T837-01) | 1 (SEC-T847-01, tracked as debt) |

### Justification
- Evidence v2 meets SEC-T837-01's remediation. Two independent scripts show that, for all five agents, the resolved agent segment on opencode-ai 1.19.2 equals the generated `permission:` map in names, actions and order.
- The built-in and global segments are unchanged from v1. Every difference from v1 is an attributed, intended change, and none widens access.
- No Immutable Security Constraint is breached, and no required control is weakened. Evidence v2 is documentation and adds no code.
- The one new finding (SEC-T847-01) is a LOW documentation inaccuracy in an immutable older artifact. It is tracked as debt under the user's LOW policy.

### Conditions
None. SEC-T847-01 is tracked LOW debt for register v21.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | Yes (resolved deny/allow per agent; held-tool override) | 0 new (status changes only) |
| A02: Cryptographic Failures | Yes (n/a; no secrets in the evidence, per the orchestrator) | 0 |
| A03: Injection | Yes (n/a; no code change) | 0 |
| A04: Insecure Design | Yes (delegation via `task`) | 0 |
| A05: Security Misconfiguration | Yes | 1 (SEC-T847-01) |
| A06: Vulnerable Components | Yes (pinned 1.19.2; 2.x stays SEC-T837-02) | 0 |
| A07: Auth Failures | Yes (n/a) | 0 |
| A08: Data Integrity Failures | Yes (binary hash recorded, `postinstall` not run, raw file hashes stored) | 0 |
| A09: Logging & Monitoring | Yes (n/a) | 0 |
| A10: SSRF | Yes (n/a; no MCP server or `instructions` fetched) | 0 |
