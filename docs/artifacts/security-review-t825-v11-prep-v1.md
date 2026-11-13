# Artifact: security-review-t825-v11-prep-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Author**: security-engineer (T825), read-only. **Date**: 2026-11-13.
- **Task**: T825 (`docs/tasks/task-T825.md`), plan `docs/plans/plan-161-release-v11.md` § Addendum 1 (wave 1 of v11.0.0).
- **User's words** (2026-11-13, option labels verbatim, as the orchestrator relayed them): plan-161 "Approve (Recommended)"; version "v11.0.0, MAJOR (Recommended)".
- **Based on** (worktree `agent-orchestrator-T813`, branch `agent/orchestrator/T813`, commit `827ba20f`):
  - the orchestrator's diff of T823 and T824 (`t825-diff.patch`: `implementation/PREREQUISITES.md`, both `implementation/runtime/{security,memory}/requirements-mcp-server.lock.txt`, `docs/wiki/mcp-pin-bump-checklist.md` line 24);
  - `docs/artifacts/mcp-pin-audit-v11-v1.md` (T814) § 5.1;
  - `docs/artifacts/security-review-t784-node-advisory-v1.md` § 6 (SEC-T784-01 remediation, lines 123 to 128 and 156);
  - `docs/artifacts/security-review-t786-node-bump-v1.md` (line 52; Conditions, line 121);
  - `docs/plans/plan-161-release-v11.md` § Addendum 1;
  - `implementation/runtime/security/requirements-mcp-server.txt` (the `httpx2` floor precedent, T676 / SEC-T646-04);
  - the server entrypoints (`implementation/runtime/security/audit_server.py:196`, `poc_audit_server.py:94`, `implementation/runtime/memory/context_retriever_mcp_server/server.py:135`).
- **External reads (2026-11-13)**:
  - GitHub advisory `GHSA-mf5v-w3w3-f6cg`;
  - PyPI JSON for `opentelemetry-api` 1.45.2.
- **Not run by me**:
  - `pip-audit` (the `run_pip_audit` tool returned an error on the worktree path), the test suites, sync and registry checks;
  - `mcp` 2.2.0 source (T824's reading is taken as reported).
  - All of the above are the orchestrator's or T824's checks, stated as theirs.

## 1. Summary

- **Risk level**: LOW.
- **Findings**: 0 CRITICAL, 0 HIGH, 0 MEDIUM, 3 LOW in scope.
  - SEC-T814-01 is graded and fixed.
  - SEC-T825-01 and SEC-T825-02 are new.
  - SEC-T784-01 stays open only for its release-document part (T816).
- **Status**: CONDITIONAL_PASS.

## 2. SEC-T814-01: grade

**Grade: `SECURITY:LOW` (A06, vulnerable component).** This confirms T814's proposal, with reachability now taken as plausible.

**What is reachable.**
- The advisory (read 2026-11-13) says `TraceContextTextMapPropagator.extract()` backtracks quadratically on a `traceparent` value that has a valid prefix, a long run of whitespace and an embedded newline.
- It says outright that "carriers that keep newlines, such as JSON strings" are in scope, and that on an async event-loop thread one message can delay unrelated requests.
- T824 reports that mcp 2.2.0's default `OpenTelemetryMiddleware` passes each inbound message's `_meta` to `opentelemetry.propagate.extract`. That is exactly such a JSON carrier.
- I therefore do not treat it as unreachable. These are not verified:
  - that the global propagator is the W3C one by default (`OTEL_PROPAGATORS` defaults to `tracecontext,baggage`; from knowledge) **(unverified)**;
  - that the ReDoS triggers through this path **(unverified, not reproduced)**.

**Who the attacker is.**
- All three affected servers (security-audit, poc-security-audit, context-retriever) run only over `stdio` (`.run("stdio")` at the three entrypoints above).
- The only party that can write a JSON-RPC message to their stdin is the MCP client process that the user started and that spawned the server.
- That client is already inside the trust boundary: it holds the user's privileges and can kill or starve the server anyway.
- The model controls tool `arguments`, not the envelope's `params._meta`, which the client builds itself (for example a progress token).
- For model-influenced or prompt-injected content to reach `_meta.traceparent`, the client would have to copy untrusted text into `_meta`. No client is known to do so **(unverified for every client)**.

**Impact.** Availability only:
- the server's event loop spins and its tools hang until the client restarts it;
- no data is disclosed or changed, and no privilege boundary is crossed;
- the base vector `AV:N/PR:N` (5.3) assumes an unauthenticated network attacker, which these servers do not have.

**Why not MEDIUM.** Exploiting it needs a malicious or faulty trusted client, and the worst outcome is that the user's own local tool hangs. There is no gap in another control that this one backs up.

**Does the bump fix it? Yes, for the finding as defined (the two lock files).**
- Both locks now pin `opentelemetry-api==1.45.2`, the advisory's patched version. Per the advisory, 1.45.2 rejects `traceparent` values longer than 512 characters before the regex runs and removes the overlapping expressions.
- I checked both hashes in the diff against PyPI:
  - wheel `2cbd7373…a34`, uploaded 2026-10-29T17:29:06Z;
  - sdist `d7b0008e…6b4`, uploaded 2026-10-29T17:29:37Z.
- `requires_python >=3.10` matches the lock target. `requires_dist` is only `typing-extensions>=4.5.0`.
- The diff changes only the header's `--exclude-newer` and that one entry, identically in both files.
- Orchestrator's checks, not mine: the two locks are byte-identical; pip-audit is clean on both with `--require-hashes`; `test_ci_hash_pins` and the related modules pass.
- The documented default install path is not covered by this fix; see SEC-T825-01.

## 3. T823 and SEC-T784-01

- **What T784 § 6 and T786 Conditions asked for**:
  - name the fixed Node versions (≥ 22.23.5, ≥ 24.22.3, ≥ 26.13.1) as the minimum in `PREREQUISITES.md` and in the v11.0.0 release document;
  - replace the end-of-life "Node.js 18+" floor at `:4` and `≥ 18` at `:227`.
- **What T823 did**:
  - `:4` now reads "Node.js 22.23.5+, 24.22.3+ or 26.13.1+ (the November 2026 Node security releases) … Node 18 and 20 are past end of life";
  - `:227` now reads `# ≥ 22.23.5, ≥ 24.22.3 or ≥ 26.13.1`.
  - Both old floors are gone.
  - My grep over all `*.md` files on `develop` finds no other user-facing Node 18/20 floor outside historical artifacts and plans. `ci/js/package.json` `engines` is `>=24`, which is CI only.
- **Verdict on SEC-T784-01**:
  - The `PREREQUISITES.md` part is done as T784 and T786 worded it.
  - SEC-T784-01 stays **open** until T816's `docs/releases/v11.0.0.md` names the fixed versions; its deadline is that document.
  - The wording T784 itself suggested allows a wrong reading: read literally, the list is satisfied by any version ≥ 22.23.5 (SEC-T825-02). T816 should use the per-line form, and `:4` and `:227` should be tightened in the same wave.
  - Not verified: Node 20's end-of-life date (2026-04-30, from knowledge), and whether a Node major above 26 exists and contains the fixes **(unverified)**.

## 4. Checklist line 24 (`docs/wiki/mcp-pin-bump-checklist.md`)

- The new text matches the diff and PyPI:
  - "current locks use 2026-10-30T00:00:00Z" equals both lock headers;
  - "1.45.2 was uploaded on 2026-10-29" matches PyPI;
  - "from the previous lock so that no other package changed" matches the diff, which shows only the one entry changing;
  - "uv 0.11.9" is T824's report **(unverified)**.
- **Cooldown (SEC-T676-14)**:
  - `--exclude-newer` is 14 days before the 2026-11-13 run, and 1.45.2 was 15 days old at the run.
  - This meets the seven-day rule for these locks, and also the 14-day package-age rule that the checklist sets for the CI locks.
- **Observation O-1 (no grade)**: the next sentence still says "At the next regeneration (SEC-T676-14) set…". This regeneration already applied that rule, so the sentence could say so. This is a text nit.
- **Observation O-2 (no grade)**:
  - The lock header records only `uv pip compile … --exclude-newer 2026-10-30T00:00:00Z`, without `--upgrade-package` or the previous lock.
  - A from-scratch run of that header command could resolve other packages published between 2026-10-22 and 2026-10-30 to newer versions than the committed lock has **(unverified whether any exist)**.
  - The hashes pin exactly what was audited, so this creates no risk. The checklist line records the real method, which is enough. At the next input change, do a full resolve.

## 5. Findings

| ID | Severity | OWASP | Location | Description | Remediation | Status |
|----|----------|-------|----------|-------------|-------------|--------|
| SEC-T814-01 | SECURITY:LOW | A06 | `implementation/runtime/{security,memory}/requirements-mcp-server.lock.txt` (`opentelemetry-api`, line 244) | CVE-2026-126360 / GHSA-mf5v-w3w3-f6cg, a ReDoS in W3C `traceparent` parsing. The input can reach it through `_meta` of stdio messages from the user's own MCP client. Availability only (§ 2) | Bump to 1.45.2 (T824) | **Fixed** by T824 (lock pins 1.45.2, hashes match PyPI). Minted and fixed in this release; the next register should record that |
| SEC-T825-01 | SECURITY:LOW | A06 | `implementation/runtime/security/requirements-mcp-server.txt:23-30`, `implementation/runtime/memory/requirements-mcp-server.txt` (same block); install path at `README.md:185`, `implementation/PREREQUISITES.md:50`, `scripts/install.sh` notice | The documented default install is the unhashed `pip install -r requirements-mcp-server.txt`, which carries no `opentelemetry-api` floor. A fresh install today resolves to the newest version, 1.45.2 (T814 § 5.1; **unverified** for pip specifically). An existing virtual environment built from the `.txt` keeps 1.45.1, because `pip install -r` does not upgrade a dependency that is already satisfied. The repository already uses a floor for exactly this case (`httpx2>=2.12.0`, T676 / SEC-T646-04, whose comment says "keeps a plain `pip install -r` off the vulnerable range"). T824 did not add the equivalent | (a) Add the floor to both `.txt` inputs and regenerate both locks from the previous lock. They stay byte-identical, the entry stays 1.45.2, and the `# via` annotation will change. (b) In `docs/releases/v11.0.0.md` (T816), tell users with an existing server virtual environment to run `pip install --require-hashes -r implementation/runtime/<dir>/requirements-mcp-server.lock.txt` or `pip install -U 'opentelemetry-api>=1.45.2'`. Code example below | Open, new |
| SEC-T825-02 | SECURITY:LOW | A06 | `implementation/PREREQUISITES.md:4`, `:227` (T823) | "22.23.5+, 24.22.3+ or 26.13.1+" and "≥ 22.23.5, ≥ 24.22.3 or ≥ 26.13.1" are, read literally, a single floor of ≥ 22.23.5. They accept unpatched 24.x below 24.22.3, 26.x below 26.13.1, and the end-of-life odd lines 23 and 25. The parenthesis "(the November 2026 Node security releases)" helps, but `:227` has no such context. T823 followed T784's own wording, so T823 is not at fault | State the floor per release line, in PREREQUISITES and in the release document. Code example below | Open, new |
| SEC-T784-01 | SECURITY:LOW | A06 | `implementation/PREREQUISITES.md:4`, `:227`; `docs/releases/v11.0.0.md` | The user-side Node behind the `npx` entries (T784 § 6) | The PREREQUISITES part is done by T823. The release document must name the fixed versions (T816), ideally in the SEC-T825-02 form | **Open, PREREQUISITES part done**; closes when T816's document names the versions |

**Code example, SEC-T825-01** (both `requirements-mcp-server.txt`):
```
# Before
mcp==2.2.0
httpx2>=2.12.0
# After
mcp==2.2.0
httpx2>=2.12.0
# SEC-T814-01: mcp 2.2.0 accepts opentelemetry-api <= 1.45.1, affected by GHSA-mf5v-w3w3-f6cg
# (ReDoS in traceparent parsing via _meta); this floor keeps a plain `pip install -r` off it.
opentelemetry-api>=1.45.2
```

**Code example, SEC-T825-02** (`PREREQUISITES.md`):
```
# Before (:4)   Node.js 22.23.5+, 24.22.3+ or 26.13.1+ (the November 2026 Node security releases)
# After  (:4)   Node.js 22 (22.23.5 or later), 24 (24.22.3 or later) or 26 (26.13.1 or later), the
#               November 2026 security releases; odd-numbered and end-of-life lines (18, 20, 23, 25) are not supported.
# Before (:227) node --version           # ≥ 22.23.5, ≥ 24.22.3 or ≥ 26.13.1
# After  (:227) node --version           # v22 ≥ 22.23.5, v24 ≥ 24.22.3, or v26 ≥ 26.13.1
```

## 6. Recommendations (priority order)

1. **T816**: in `docs/releases/v11.0.0.md`, name the Node minimums in the per-line form (SEC-T784-01, SEC-T825-02), and add the upgrade line for existing MCP server virtual environments (SEC-T825-01 b). Record that SEC-T814-01 was fixed in this release (1.45.2).
2. **Before T815, on `develop`, small** (or track as LOW):
   - add the `opentelemetry-api>=1.45.2` floor to both `.txt` inputs and regenerate the locks (SEC-T825-01 a);
   - tighten `PREREQUISITES.md:4` and `:227` (SEC-T825-02).
   - Re-run the 10 PREREQUISITES-reading test modules, `test_ci_hash_pins`, the lock byte-identity test and pip-audit on both locks.
3. **Next register**: add SEC-T814-01 (minted and fixed), SEC-T825-01 and SEC-T825-02 as tracked-LOW if they are not fixed before the tag, and SEC-T784-01's status. O-1 and O-2 are text nits for the next checklist edit.
4. **Optional defence in depth**: an operator can set `OTEL_PROPAGATORS=none` in the server entries' environment. This is not needed after the bump and is not recommended as a generated change.

## 7. Compliance checklist

- [x] OWASP Top 10 reviewed (for the scope of this delta)
- [x] Authentication secure (not touched)
- [x] Authorization enforced (not touched)
- [x] Input validation complete (the inbound `_meta` path is bounded by 1.45.2's 512-character limit, per the advisory)
- [x] Secrets management verified (no secret in the diff)
- [x] Dependencies audited (lock and hashes against PyPI; pip-audit is the orchestrator's and T824's)
- [ ] Security headers configured (not applicable: stdio)
- [x] Logging appropriate (not touched)

## VERDICT: CONDITIONAL_PASS

### Findings Summary
| Severity | Count | Resolved | Remaining |
|----------|-------|----------|-----------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 4 | 1 | 3 |

(LOW counts SEC-T814-01 as resolved, and SEC-T825-01, SEC-T825-02 and SEC-T784-01 as remaining.)

### Justification
- Nothing blocks:
  - SEC-T814-01 is LOW (§ 2) and fixed by T824's lock bump, with hashes checked against PyPI;
  - there is no CRITICAL, HIGH or MEDIUM;
  - no Immutable Security Constraint is breached;
  - no required control is omitted or weakened. The diff tightens the Node floor and moves a dependency to its patched version.
- It is not a PASS, because three LOW findings are not yet fixed or tracked as debt:
  - SEC-T825-01 (no floor, so existing environments are not upgraded);
  - SEC-T825-02 (the Node floor wording is ambiguous);
  - SEC-T784-01 (still due in the release document).

### Conditions
- SEC-T784-01: owner=@release-manager (T816), remediation=name the fixed Node versions in `docs/releases/v11.0.0.md` in the per-line form, deadline=the v11.0.0 release document.
- SEC-T825-01: owner=@devops-engineer (floor in both `.txt` files and lock regeneration) and @release-manager (T816 upgrade line), remediation=§ 5, deadline=the v11.0.0 release document for (b); (a) before T815 or tracked-LOW in the next register.
- SEC-T825-02: owner=@technical-writer (`PREREQUISITES.md:4`, `:227`) and @release-manager (T816 wording), remediation=§ 5, deadline=the v11.0.0 release document.

### Blockers
None.

### OWASP Coverage
| Category | Reviewed | Findings |
|----------|----------|----------|
| A01: Broken Access Control | No (not in delta) | 0 |
| A02: Cryptographic Failures | Yes (lock hashes) | 0 |
| A03: Injection | No (not in delta) | 0 |
| A04: Insecure Design | Yes (trust boundary of stdio `_meta`) | 0 |
| A05: Security Misconfiguration | Yes (OTel propagator default, **unverified**) | 0 |
| A06: Vulnerable Components | Yes | 4 (SEC-T814-01 fixed; SEC-T825-01, SEC-T825-02, SEC-T784-01) |
| A07: Auth Failures | No (not in delta) | 0 |
| A08: Data Integrity Failures | Yes (hash lock, cooldown, reproducibility O-2) | 0 |
| A09: Logging & Monitoring | No (not in delta) | 0 |
| A10: SSRF | No (not in delta) | 0 |
