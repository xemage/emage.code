# Artifact: brave-audit-acceptance-v4.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Author**: devops-engineer (T676 for v1; T685 for v2; T712 for v3; T808 for v4). **Date**: 2026-11-13. **Owner**: devops-engineer.
- **Revision**: v4 records the user's acceptance of SEC-T702-09 for release **v11.0.0 only**. It changes no pin, no launch argument, no gate logic, no advisory in the accepted set and no expiry date. v3 stays as the record of the decision of 2026-11-01, given for v9.0.0 (`brave-audit-acceptance-v3.md`: "Renew + force stdio (Recommended)"); its gate command and its expiry are the ones below, unchanged. v2 (`brave-audit-acceptance-v2.md`) and v1 stay as the records of 2026-10-22.
- **Decision**: the user, in three answers. Every quotation below is copied from the plan named with it.
  1. 2026-11-12, AskUserQuestion (`docs/plans/plan-155-v11-release-decisions.md`, § User decisions item 2). The question as shown:
     > For release v11.0.0, SEC-T702-09 (SECURITY:MEDIUM): the pinned Brave search server 2.1.4 ships seven known advisories, and 2.1.4 is still the newest published release (checked on npm today, 2026-11-12). Plan shown: owner devops-engineer; fix: bump to the first Brave release above 2.1.4; deadline 2027-01-30 or that release, whichever comes first. Accept for v11.0.0 only?

     The answer, typed by the user:
     > If there is an easy and good replacement for it, replace it, otherwise Accept for v11.0.0
  2. 2026-11-12, AskUserQuestion, after the scouting of T799 (`docs/plans/plan-155-v11-release-decisions.md`, § Addendum item 5). The question as shown:
     > Brave (SEC-T702-09): the scout found no easy and good replacement. Tavily's official server pins the same vulnerable SDK (1.26.0, I confirmed on npm); Exa and Perplexity stay on zod 3.x and add new unknowns; Kagi, SearXNG and DuckDuckGo servers are unaudited and add page-fetching tools. Brave's own main branch already has the fixed dependencies but is unpublished. By your answer ("If there is an easy and good replacement for it, replace it, otherwise Accept for v11.0.0") the acceptance for v11.0.0 would stand. Confirm?

     The answer:
     > Keep the acceptance (Recommended)

     The option's description read:
     > SEC-T702-09 is accepted for v11.0.0 only: owner devops-engineer; fix: bump to the first Brave release above 2.1.4; deadline 2027-01-30 or that release, whichever comes first.

     The other options were "Remove Brave entirely" and "Audit Tavily and Exa first".
  3. 2026-11-13 (`docs/plans/plan-158-brave-acceptance-v4-and-register-v16.md`, § User decision). The orchestrator listed as the first next step: "1. **Brave acceptance record:** a new version carrying your "Keep the acceptance" decision for v11.0.0." The user's answer to that step, verbatim:
     > 1. Keep the acceptance

     plan-158 reads this as the word for writing this record. It is the orchestrator's reading, recorded there.
- **Which release this covers**: v11.0.0 only (ADR-011: an acceptance covers only the release it was given for). v9.0.0 was covered by the decision in v3 and in `docs/releases/v9.0.0.md`. v10.0.0 was covered by its own acceptance, which no version of this artifact holds: the record is `docs/releases/v10.0.0.md`, § RELEASE VERDICT, under Conditions ("Accept for v10.0.0 (Recommended)", 2026-11-07, AskUserQuestion), which names v3 for the deadline. The release after v11.0.0 that ships this pin needs the user again.
- **Plan (ADR-011 and ADR-012 fields), exactly as shown to the user**: owner devops-engineer; fix: bump to the first Brave release above 2.1.4; deadline 2027-01-30 or that release, whichever comes first. The fix is a version bump, so ADR-015 Rule 1 (a plan whose fix is "none possible in the harness") and ADR-016 (the Security Engineer's confirmation of such a plan) do not apply.
- **Based on**: `brave-audit-acceptance-v3.md`; `brave-audit-acceptance-v2.md`; `docs/tasks/task-T808.md`; `docs/plans/plan-155-v11-release-decisions.md`; `docs/plans/plan-158-brave-acceptance-v4-and-register-v16.md`; `docs/artifacts/brave-replacement-scouting-v1.md` (T799); `docs/decisions/ADR-011-user-accepted-medium-at-release.md`, `docs/decisions/ADR-012-medium-acceptance-record.md`, `docs/decisions/ADR-015-medium-plan-without-fix-and-passed-deadline.md`, `docs/decisions/ADR-016-security-engineer-confirmation-as-validity-condition.md`; `docs/releases/v10.0.0.md`; `scripts/audit-mcp-pins.py`; `implementation/knowledge/mcp/servers.yaml` (`brave`); the runs of 2026-11-13 below.
- **Expires**: unchanged from v3: the earlier of (a) the first release of `@brave/brave-search-mcp-server` above 2.1.4 and (b) **2027-01-30**. After either, `python3 scripts/audit-mcp-pins.py audit --audit-level high` must pass without `--accept` for these ids, or a new version of this artifact must renew the decision with the user. The user was shown 2027-01-30; a later date needs the user. How the script reads the date is under "The expiry and the 90-day rule" below.

## What is accepted

The same seven advisories as in v3, on the same pin, `@brave/brave-search-mcp-server@2.1.4`, which depends on `@modelcontextprotocol/sdk` at exactly `1.30.0` and on `zod` at exactly `4.3.6`:

| Advisory | Package | npm grade |
|---|---|---|
| GHSA-6qxp-vccf-f47h | `@modelcontextprotocol/sdk` | high |
| GHSA-22jm-h49p-29qw | `@modelcontextprotocol/sdk` | high |
| GHSA-6prh-2h8m-c8cw | `@modelcontextprotocol/sdk` | moderate |
| GHSA-46jr-4wx8-v453 | `@modelcontextprotocol/sdk` | high |
| GHSA-rvq5-wwqv-78pq | `@modelcontextprotocol/sdk` | moderate |
| GHSA-f897-62hf-6gxq | `@modelcontextprotocol/sdk` | high |
| GHSA-mrhx-c7xc-m3w5 | `zod` | high |

Titles, ranges and fixed versions are in v3's table. The per-advisory npm grades in this table are v3's; the run of 2026-11-13 prints one grade per package (`high` for the sdk, `high` for zod), not one per advisory, so they were not re-read today.

## Unchanged from v3

This version does not re-grade anything. For each of these, v3 and the reviews it names are the record:

- **The overall finding and the per-advisory grading**: SEC-T702-09 (MEDIUM), each advisory graded LOW in the shipped stdio mode by the Security Engineer on 2026-11-01 (`docs/artifacts/security-review-t702-brave-reachability-v1.md`; v3, § Reasoning; the review of v3 itself is `docs/artifacts/security-review-t712-brave-stdio-v1.md`). The state before v10.0.0 is in `docs/artifacts/security-review-t756-accepted-mediums-v1.md`.
- **The shipped launch**: `npx -y @brave/brave-search-mcp-server@2.1.4 --transport stdio` (`implementation/knowledge/mcp/servers.yaml`; T808 did not touch that file). `tests/functional/test_mcp_package_pins.py` (`test_brave_entry_is_a_forced_stdio_launch` and its mutation test) still enforces this form.
- **v3's reasoning, items 1 to 5, and v3's limits L-1 to L-6**, including that the override of `BRAVE_MCP_TRANSPORT` by the command-line flag was read, not run (L-3).
- **SEC-T702-08 (LOW)**, the Brave API fetches without timeout or size cap: not accepted here and not changed.

## Scouting result (T799)

The user's first answer made the acceptance conditional on a replacement search. `docs/artifacts/brave-replacement-scouting-v1.md` (T799, 2026-11-12) is the record of that search; its summary reads: "No candidate is both easy and good. Recommendation: **no easy and good replacement; keep the acceptance** (§ 6)." No audit was run on any candidate (plan-155, § Outcome). The user then gave answer 2 above. Nothing in this artifact re-judges the candidates.

## Conditions

Unchanged from v3.

- **Stdio only.** The `brave` entry in `servers.yaml` launches exactly `npx -y @brave/brave-search-mcp-server@2.1.4 --transport stdio`: the one flag is `--transport stdio`; no `--host`, `--port` or other flag and no `BRAVE_MCP_*` variable in `servers.yaml`.
- **Operators must not set `BRAVE_MCP_TRANSPORT` or `BRAVE_MCP_HOST`** in the environment or in a `.env` file of the launch directory. An operator who sets `BRAVE_MCP_TRANSPORT=http` and edits the launch arguments of an installed config reopens GHSA-46jr-4wx8-v453, GHSA-f897-62hf-6gxq and the HTTP path of GHSA-mrhx-c7xc-m3w5 (v3, § Conditions and L-3).
- **The release gate command lists exactly these seven acceptances, and nothing broader**: `python3 scripts/audit-mcp-pins.py audit --audit-level high --accept GHSA-6qxp-vccf-f47h:2027-01-30:@brave/brave-search-mcp-server@2.1.4 --accept GHSA-22jm-h49p-29qw:2027-01-30:@brave/brave-search-mcp-server@2.1.4 --accept GHSA-6prh-2h8m-c8cw:2027-01-30:@brave/brave-search-mcp-server@2.1.4 --accept GHSA-46jr-4wx8-v453:2027-01-30:@brave/brave-search-mcp-server@2.1.4 --accept GHSA-rvq5-wwqv-78pq:2027-01-30:@brave/brave-search-mcp-server@2.1.4 --accept GHSA-f897-62hf-6gxq:2027-01-30:@brave/brave-search-mcp-server@2.1.4 --accept GHSA-mrhx-c7xc-m3w5:2027-01-30:@brave/brave-search-mcp-server@2.1.4`. It is v3's command, character for character. An accepted id is still printed as ACCEPTED; an expired acceptance fails the audit; each acceptance counts only when brave 2.1.4 is the only pinned package the vulnerable entry puts at risk, and a bump of the brave pin voids all seven (SEC-T676-11).
- **Re-audit** at any `@brave/brave-search-mcp-server` release above 2.1.4, at any new advisory on `@modelcontextprotocol/sdk@1.30.0` or `zod@4.3.6` that affects the stdio transport or tool-input validation, at any change to the `brave` entry of `servers.yaml`, and at the expiry.
- **Only the user can renew** this acceptance, in a new version of this artifact. Two mechanisms stay separate (ADR-011, § Consequences): this pin-audit acceptance decides whether `scripts/audit-mcp-pins.py` passes; the user's acceptance for a release decides whether that release may ship the MEDIUM. A release needs both. This artifact carries both for v11.0.0; the release document of v11.0.0 still has to record the acceptance in the form its own rules ask for.

## Facts re-checked on 2026-11-13 (T808)

All in the T808 worktree, npm 11.17.0, public registry only.

1. **Newest Brave release.** `npm view @brave/brave-search-mcp-server version time.modified dist-tags --registry https://registry.npmjs.org/` printed:

   ```
   version = '2.1.4'
   time.modified = '2026-09-17T14:48:16.174Z'
   dist-tags = { latest: '2.1.4' }
   ```

   No release above 2.1.4 exists, so expiry condition (a) has not occurred.
2. **The audit without `--accept`.** `python3 scripts/audit-mcp-pins.py audit --audit-level high`: **exit 1**, `result: FINDINGS`, `npm pins audited: 8`. Printed `high`: `@brave/brave-search-mcp-server` (direct, "via a dependency"), `@modelcontextprotocol/sdk` and `zod`. The advisory ids in the output, each once: the six sdk ids and the one zod id of the table above, and `GHSA-3g3m-2fjr-6pw4` (`glob`) and `GHSA-g3hv-75wg-m249` (`minimatch`), both `moderate` through `@modelcontextprotocol/server-filesystem`. **The set on the Brave pin equals v3's seven: none more, none fewer.** The two moderate ids are the ones v3's run log already names as below the audit level and not part of this decision.
3. **The audit with the gate command above** (the seven `--accept` entries, without `--signatures`): **exit 0**, `result: no finding at or above the audit level`. Printed as `ACCEPTED high`: `@brave/brave-search-mcp-server`, `@modelcontextprotocol/sdk` and `zod`. All seven printed as `accepted ... until 2027-01-30 for @brave/brave-search-mcp-server@2.1.4`. `moderate`, not accepted and below the level: `@modelcontextprotocol/server-filesystem`, `glob`, `minimatch`.

Not run today: the negative control with six entries (v3 ran it), `--signatures`, `provenance`, and the manual advisory read for the three reference servers that the script asks for (SEC-T646-06). They are checklist steps of a bump or a release, not of this record.

## The expiry and the 90-day rule

`scripts/audit-mcp-pins.py` does not read this artifact. It reads each `--accept GHSA:DATE:PACKAGE@VERSION` from the command line and applies two date rules against the day of the run (`check_acceptances` and `acceptance_lines`; `MAX_ACCEPT_DAYS = 90`):

- a date more than 90 days after the day of the run is an error (exit 2);
- a date before the day of the run is an expired acceptance and fails the run.

So the rule bounds how far ahead the date lies on the day the command runs; it does not look at the day of the decision or the date of this artifact. 2027-01-30 is 90 days after 2026-11-01 (the first day the command could run with it), 79 days after the decision of 2026-11-12, and 78 days after 2026-11-13. A v4 dated 2026-11-13 with the unchanged expiry is therefore consistent with the rule, and run 3 above shows the script accepting it today. The command passes on every day up to and including 2027-01-30 as long as the pin and the advisory set stay as they are. `tests/functional/test_pin_bump_checklist.py` additionally requires that the expiry is at most 90 days after this artifact's date and after it; 78 days meets that.

A consequence, stated so that nobody reads more into v4 than it holds: this version does **not** extend the acceptance in time. If v11.0.0 is tagged after 2027-01-30, or after a Brave release above 2.1.4, the gate fails whatever this artifact says, and the user decides again.

## Limits

L-1 The user's words were copied from plan-155 and plan-158, which the orchestrator wrote; the question dialogs themselves were not seen by T808. L-2 The advisory set was compared by id from the script's output; titles, ranges and patches were not re-read, and the reachability grades were not re-derived (v3, L-1 and L-2 stand). L-3 Nothing in the Brave package was run (v3, L-3 stands). L-4 That Brave's upstream default branch carries the fixed dependencies unpublished is the orchestrator's check of 2026-11-12 (plan-155, § Outcome), not re-checked here **(unverified)**. L-5 The runs above are of one day; npm's advisory feed can change before the release gate runs the same command. L-6 No Security Engineer reviewed this version; plan-158 records that as the orchestrator's ruling and names the release security review as the reader.
