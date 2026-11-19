# plan-172 — Batch P: draft of the upstream report to the Brave project (SEC-T702-08)

**Created:** 2026-11-19
**Based on:**
- `docs/artifacts/tracked-debt-register-v21.md` (§ 5 batch P);
- `docs/artifacts/security-review-t702-brave-reachability-v1.md` (SEC-T702-08);
- `docs/plans/plan-126-batch-b-release-tooling.md` (§ Not in this plan);
- `docs/artifacts/brave-audit-acceptance-v4.md`.

**Scopes:** `T849`, `T850`.

## User decision (2026-11-19, verbatim)

> P go

**The record says** (plan-126): "The orchestrator offers the user a draft of the report; the user files it, or decides not to. It stays tracked until then." The user's earlier answer on this id, of 2026-11-02, was "Keep it tracked". So "P go" asks for the draft.

**Filing is the user's step.** No agent and no orchestrator posts anything to the Brave project.

## Task Decomposition

1. **T849** (devops-engineer): check the finding and write the draft.
   - **Re-read the shipped code.** Read `src/BraveAPI/index.ts` in the shipped `@brave/brave-search-mcp-server@2.1.4`, from the npm tarball, with `npm pack`. Do not install or run it.
   - **Check upstream.** Check the current upstream default branch and the newest npm version for the same lack of a timeout or response size cap. If upstream has fixed it, say so: the draft is then not needed, and the finding can close at the next pin.
   - **Look for an existing report.** Check whether an issue or PR upstream already covers this.
   - **Write `docs/artifacts/brave-upstream-report-draft-v1.md`.** It holds the record of the checks and a ready-to-paste issue text: title, affected version, file and lines, the behaviour, the impact (LOW: a hang or memory growth only if the fixed HTTPS endpoint misbehaves), and a suggested fix (`AbortSignal.timeout`, a response size cap). Also state the channel, an ordinary issue or a security advisory, and justify the choice.
   - **The draft must not name** the user, this project, the repository, any host, path, token or email.
2. **T850** (security-engineer, read-only): review the draft.
   - Is the finding accurate?
   - Is anything about the user or the project disclosed?
   - Is the channel right?
   - Verdict: PASS, CONDITIONAL_PASS or FAIL.

## Constraints

- No `docker`.
- Do not run the Brave package.
- No API key.
- No post, issue, comment or PR to any external service.
- Never read secrets or the user's settings files.
- Never open `tests/golden/held-out/`.
- No source change. The pin is unchanged; SEC-T702-09 keeps its own date.

## Outcome

**Done on 2026-11-19. The draft is offered to the user; filing is the user's step.**

**T849** (devops-engineer, commit `919fad8c`) wrote `docs/artifacts/brave-upstream-report-draft-v1.md`.
- **The finding is confirmed in 2.1.4.** The npm tarball ships `dist/` only. In `dist/BraveAPI/index.js`:
  - line 103: `fetch(urlWithParams, { headers })`, with no signal;
  - lines 108, 112 and 118: whole-body `json()` / `text()`, with no size check.
- **Still present upstream:**
  - in 2.1.5, the newest version on npm, published 2026-11-17, where `dist/BraveAPI/` is byte-identical to 2.1.4;
  - on `main` at `e08f5af0`, which is 2.1.5's `gitHead`: lines 116, 123, 126 and 134 of `src/BraveAPI/index.ts`.
- **No existing upstream issue or PR** covers it. PR #315 shows the `AbortSignal.timeout` pattern for another client.
- **Recommendation:** an ordinary public issue. There is no `SECURITY.md`, and the issue is availability-only and LOW.

**T850** (security-engineer): `docs/artifacts/security-review-t850-brave-report-v1.md`, **CONDITIONAL_PASS**.
- **Confirmed:** the finding is accurate, the paste text discloses nothing, and the channel is right.
- **Two LOW wording findings**, conditions before the draft is offered:
  - SEC-T850-01: undici's `headersTimeout` is a total wait, and only `bodyTimeout` is an inactivity timer.
  - SEC-T850-02: do not quote an unverified error string.

**The condition is met.** The orchestrator wrote `docs/artifacts/brave-upstream-report-draft-v2.md`: v1 with T850's exact replacement text for those two paragraphs. SEC-T850-01 and -02 are minted and fixed.

**SEC-T702-08 stays tracked-LOW (batch P)** until the user answers, as draft v2 § 5 describes:
- "filed: <URL>": recorded as reported upstream; it closes when a release with the fix is pinned;
- "declined": recorded as declined.

**The orchestrator's own verification:**
- `npm view`: 2.1.5 was published 2026-11-17, with `gitHead` `e08f5af0`. It depends on `@modelcontextprotocol/sdk` 1.32.2 and `zod` 4.6.7.
- Line 103 is the same in both extracted tarballs.
- Raw `src/BraveAPI/index.ts` at `e08f5af0` has 141 lines, with the fetch at 116 and the body reads at 123, 126 and 134.
- v1 is unchanged.
- The gates, the full suite and the pipeline are recorded in the merge request.

**Found on the way, for the user:** 2.1.5 is the first Brave release above 2.1.4. SEC-T702-09's acceptance for v11.0.0 runs to 2027-01-30 or to that release. It carries the upstream fixes the acceptance waited for (sdk 1.32.2, zod 4.6.7). Bumping the pin is the agreed fix and needs its own plan and the user's word. This plan does not change the pin.

**Budgets:**

| Task | Used (about) | Budget |
|---|---|---|
| T849 | 40k | 50k |
| T850 | 25k | 30k |
