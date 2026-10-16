# Artifact: poc-security-shortcut-examples-v1.md

> Filename: `poc-security-shortcut-examples-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T576
- **Created**: 2026-10-02
- **Based on**: `docs/tasks/task-T576.md`; `docs/plans/plan-098-poc-security-shortcut-examples.md`;
  `docs/artifacts/poc-skill-command-overlaps-v1.md` §13 (O1) and §16.3 (P42);
  `implementation/knowledge/instructions/poc-guidelines.md` (`maturity: stable`);
  `implementation/knowledge/instructions/security-guidelines.md` (`maturity: stable`);
  `implementation/knowledge/skills/rapid-prototyping/SKILL.md` (`maturity: experimental`); all read on branch
  `agent/solution-architect/T576` at `develop` `bce238a`.
- **Supersedes**: none (first version)
- **Decision references**: P42 (this task). **No new ADR is minted.** Every ruling applies text that both stable
  instructions already state. ADR-007 is **not applied**, because no command clause is amended. No P34b ranking is
  used (§1.3).

## 0. What this document is, and what it did not do

This document rules on every site in brief §2 and specifies one implementation follow-up. **It changed no
instruction, skill, command, agent or golden case.**

**Method and limits.** This session had **no shell**: no `grep`, git, directory listing or test run. Every claim
comes from reading named files directly in the worktree. Anything that would need a search or a run is marked
**(unverified)** and collected in §8.

**Files read:**
- `poc-guidelines.md` and `security-guidelines.md` (source), in full;
- `rapid-prototyping/SKILL.md` and `technical-debt-tracking/SKILL.md` (source), in full;
- agents `poc-orchestrator.md` and `poc-security-engineer.md`, and command `new-poc.md`, in full. These were spot
  checks for other copies of the pattern (§9);
- one projection, `implementation/.github/instructions/poc-guidelines.instructions.md:75–124`;
- the planning inputs above, plus `poc-contract-resolution-v1.md` §7.4 and §9.3, for P33's scope.

Under the brief's read-only grant I read
`tests/golden/open/evaluate-poc-verdict-debt-reconciliation/{brief.md,fixture/poc-evaluation.md}` and nothing else
under `tests/golden/`. I did not open `tests/golden/held-out/`.

## 1. Authority basis

### 1.1 The quoted texts

Both instructions declare `applyTo: "**"` and `maturity: stable` (`poc-guidelines.md:3–4`,
`security-guidelines.md:3–4`). Both are therefore in force together on every PoC file.

**`security-guidelines.md`, the constraint text:**
- `:153`: "The following constraints are absolute and cannot be overridden by any agent, configuration, or runtime
  decision:"
- `:155`, Constraint 1: "**No secrets in source control** — No API keys, passwords, tokens, certificates, or private
  keys may ever be committed. This is not negotiable regardless of PoC status, urgency, or convenience."
- `:157`, Constraint 3: "**No disabled security checks** — Security middleware, input validation, and authentication
  checks must never be bypassed, even in development or PoC mode."
- `:158`, Constraint 4: "**No unvalidated external input** — Every input from outside the system boundary (user
  input, API calls, file uploads, environment variables) must be validated before use."

**`security-guidelines.md`, its own precedence claim.** Rails, `:17–20`: "Does not grant any agent authority to
disable a security control 'temporarily,' even in PoC or development mode — the Immutable Security Constraints
section forbids that outright, superseding any speed-over-completeness pressure from `poc-guidelines.md`."

**`security-guidelines.md`, the rules reached by the CORS and connection-string questions:**
- `:66`, API Security: "Use CORS allowlist (never `Access-Control-Allow-Origin: *` with credentials)"
- `:29–32`, Input Validation: "Validate ALL user input on the server side … Use allowlists over denylists … Validate
  type, length, format, and range … Reject and log invalid input — don't silently fix it"
- `:69–70`, Secrets Management: "NEVER commit secrets to source control … Use environment variables or secret vaults"
- `:79`, Database: "Use TLS for database connections"
- `:83`, Logging: "DO NOT log: passwords, tokens, session IDs, PII, credit card numbers"

**`poc-guidelines.md`, its own subordination.** Rails, `:17–19`: "Does not waive the Immutable Security Constraints in
`security-guidelines.md` (no exposed secrets, no real PII in demos) merely because a workstream is time-boxed."

### 1.2 Verification of the brief's reading

**The reading holds.** `security-guidelines` claims precedence over `poc-guidelines` on exactly this point, and names
it. `poc-guidelines` disclaims any waiver in its own Rails. One document asserts precedence and the other concedes
it, so no third text is needed to rank them. Constraint 3 also names the PoC context itself ("even in development or
PoC mode"). That leaves no reading on which a PoC is exempt.

Two refinements:
1. **The parenthetical does not narrow the concession.** `poc-guidelines:18` lists "(no exposed secrets, no real PII
   in demos)", which are Constraints 1 and 2 only. But the sentence's object is "the Immutable Security Constraints",
   the whole section, and the parenthetical reads as illustrative. Constraint 3's own words ("even in … PoC mode")
   would decide the point even on a narrow reading. Nothing needs ranking here. §9 O3 records the parenthetical as a
   wording risk, not a blocker.
2. **CORS is reached through the Rails, not a numbered constraint.** None of Constraints 1–6 names CORS. The
   `security-guidelines` Rails sentence, however, covers "a security control" generally ("Does not grant any agent
   authority to disable a security control 'temporarily,' even in PoC or development mode"). `poc-guidelines` claims
   no exemption for CORS or any other API Security rule. Its Allowed Shortcuts (`:63–66`) name none. Again one side
   asserts and the other does not contest, so no ranking is needed (§4.3).

### 1.3 The skill

`rapid-prototyping` is `experimental` and claims no exemption from either instruction. It does not *require* a
forbidden shortcut. It only *exemplifies* one. Replacing the examples makes the skill and both instructions jointly
satisfiable. That is the joint-satisfiability method of `gate-verdict-consistency-v1.md` §1.2(i), accepted in its
§13.2 and applied to skills by `poc-skill-command-overlaps-v1.md`. No skill is ranked against an instruction.

**No P34b blocker.** Every ruling below rests on §1.1's quoted text plus same-file coherence: `poc-guidelines`'
examples contradict its own Rails.

## 2. `poc-guidelines.md` (stable)

### 2.1 Site A1: `:81–82`, "Hardcoded connection string". **Acceptable, with a condition (amend: R1)**

**Constraint 1 is not broken.** `postgresql://localhost:5432/poc_db` carries no user, password, token or key, so
nothing in Constraint 1's list ("API keys, passwords, tokens, certificates, or private keys") is committed. A
hardcoded non-secret configuration value is a legitimate PoC shortcut ("Minimal infrastructure setup", `:65`).

**The condition: the model must make the boundary explicit.**
- The current remedy, "production must use secret vault", presents the string as if it were a secret. The obvious
  next copy, `postgresql://user:pass@host/db`, *would* break Constraint 1, and the example gives no sign of where the
  line is.
- The URL is also silent on TLS, against `:79`, "Use TLS for database connections". `sslmode=require` makes the model
  compliant without changing what the shortcut teaches.

R1 states both in the tag and in the URL.

````
Before:
# <!-- POC-DEBT: Hardcoded connection string; production must use secret vault -->
db_url = "postgresql://localhost:5432/poc_db"

After:
# <!-- POC-DEBT: Hardcoded local database URL (no credentials in it); production must read the URL from configuration and the credentials from the secret vault -->
db_url = "postgresql://localhost:5432/poc_db?sslmode=require"
````

**Authority:** Constraint 1 (`:155`); Secrets Management `:69–70`; Database `:79`. **Severable:** R1 is
independent of R2–R9. If the Security review reads the TLS rule as not reaching loopback connections, the
`?sslmode=require` suffix is the only part that changes.

### 2.2 Site A2: `:84–86`, "No input validation". **Forbidden (replace: R2)**

The tag models skipping validation on user-supplied `name` and `email`. That is the exact act Constraint 3 forbids
("input validation … must never be bypassed, even in development or PoC mode"). It also breaks Constraint 4. The
example also contradicts this file's own Rails (`:17–19`).

**The replacement keeps the same function and makes validation present but simplified.** The shortcut is the *form*
of the validation (hand-written inline checks instead of the shared schema layer), not its absence. The example:
- validates type, length and format, and uses an allowlist pattern for email (`:30–31`);
- rejects and logs (`:32`);
- logs only the field name, never the value, so no PII is logged (`:83`).

This is the positive rule (§4) in code.

````
Before:
# <!-- POC-DEBT: No input validation; production must validate all user input -->
def create_user(name, email):
    return db.insert({"name": name, "email": email})

After:
# <!-- POC-DEBT: Hand-written inline validation instead of the shared request-schema layer; production must move these checks into the schema layer and return the project's standard validation error response -->
def create_user(name, email):
    if not (isinstance(name, str) and 1 <= len(name) <= 100 and name.isprintable()):
        log.warning("input_rejected", extra={"field": "name"})
        raise ValueError("invalid name")
    if not (isinstance(email, str) and len(email) <= 254 and EMAIL_RE.fullmatch(email)):
        log.warning("input_rejected", extra={"field": "email"})
        raise ValueError("invalid email")
    return db.insert({"name": name, "email": email})
````

`log` and `EMAIL_RE` are left undefined, in the same style as `db`, `requests`, `external_api_url` and `payload` in
the existing examples. Debt Tag Rule 2 (`:94`, "directly adjacent … line above") is met in the same way as before.

### 2.3 Site A3: `:88–89`, "Synchronous call". **Acceptable, unchanged**

A blocking call with no retry is a reliability shortcut, and no security rule forbids it. The response is assigned
but not used, so Constraint 4's "validated before use" is not reached by what the example shows. The remedy is
specific. **No edit.** Its missing timeout is a reliability gap, not a security one, and is noted only (§9 O4).

### 2.4 Site B: `:119`, scorecard template row 2. **Forbidden (replace: R3)**

The model scorecard records "No input validation" as an ordinary `M`-effort row. That is the A2 breach again,
presented as normal debt in the template every PoC copies. R3 mirrors R2. It keeps `File`, `Line`, the `Validation`
category and effort `M`, so no vocabulary or scale question is opened. Per-item severity and the category vocabulary
belong to P33 (§9 O2).

````
Before:
| 2 | src/api.py | 34 | Validation | No input validation | M — add schema validation |

After:
| 2 | src/api.py | 34 | Validation | Hand-written inline input validation instead of the shared schema layer | M — move checks into the request-schema layer |
````

**Companion row 1 (`:118`, "Hardcoded connection string | S — use vault integration"): acceptable, unchanged.** It
describes the A1 shortcut, which is permitted. Its remedy is compatible with R1's tag, which keeps the vault for the
credentials.

### 2.5 Authority sites: the Rails (`:15–19`) and Not Allowed (`:143–148`). **No change to the Rails; Not Allowed amended by R5 (§4)**

## 3. `rapid-prototyping/SKILL.md` (experimental)

Line numbers are at `bce238a`. **T575's E8 inserts a `## Rails` block at `:7–9`, which shifts every site below by
about +7 lines (unverified until T575 lands).** Every Before text below is unique in the file, so apply by text, not
by line. None of these sites overlaps T575's E8–E11 (`:7–9`, `:54`, `:99`, `:102–105`).

### 3.1 Site C: `:33`, placement rule "disabled security". **Forbidden (amend: R7)**

"Disabled security" is offered as a routine configuration shortcut to tag. Constraint 3 forbids bypassing security
middleware "even in development or PoC mode", and the `security-guidelines` Rails denies any agent "authority to
disable a security control 'temporarily'". R7 substitutes two legitimate configuration shortcuts. "Hardcoded
non-secret values" draws the Constraint 1 line explicitly. "A single replica with no autoscaling" is "Minimal
infrastructure setup" (`poc-guidelines:65`).

````
Before:
- For configuration shortcuts (e.g., hardcoded values, disabled security), place the tag in the config file.

After:
- For configuration shortcuts (e.g., hardcoded non-secret values, a single replica with no autoscaling), place the tag in the config file.
````

### 3.2 Site D1: `:37–39`, "No input validation". **Forbidden (replace: R8)**

This is the same breach as A2. It is worse in one respect: `create_user(data)` inserts a caller-supplied dict whole,
so nothing is validated, not even which fields exist (mass assignment). R8 uses R2's code in the skill's own tag style
("— … before production") and keeps the skill's `db.users.insert`.

````
Before:
# <!-- POC-DEBT: No input validation — add comprehensive validation before production -->
def create_user(data):
    return db.users.insert(data)

After:
# <!-- POC-DEBT: Hand-written inline validation instead of the shared request-schema layer — move these checks into the schema layer before production -->
def create_user(name, email):
    if not (isinstance(name, str) and 1 <= len(name) <= 100 and name.isprintable()):
        log.warning("input_rejected", extra={"field": "name"})
        raise ValueError("invalid name")
    if not (isinstance(email, str) and len(email) <= 254 and EMAIL_RE.fullmatch(email)):
        log.warning("input_rejected", extra={"field": "email"})
        raise ValueError("invalid email")
    return db.users.insert({"name": name, "email": email})
````

### 3.3 Site D2: `:41–42`, "in-memory store". **Acceptable, unchanged**

A volatile store is a persistence shortcut. It holds nothing at rest, so Constraint 6 is not reached, and the remedy
is specific. **No edit.**

### 3.4 Site D3: `:45–49`, "CORS allow-all". **Forbidden (replace: R9)**

**Is it a breach or only a weaker default? It is a breach of a stated rule, and not merely a weaker default.**
- `security-guidelines:66` gives the rule in two parts. The primary instruction is "Use CORS allowlist". The
  parenthetical, "never `Access-Control-Allow-Origin: *` with credentials", is an absolute floor inside it.
- `origin: "*"` is not an allowlist, so it breaks the primary instruction whether or not credentials are enabled. If
  credentials are enabled (the example does not say), it also breaks the absolute floor.
- The rule has no production-only qualifier, and the instruction applies to `**`.
- Replacing the allowlist with `*` disables a security control. The `security-guidelines` Rails (`:17–20`) withholds
  that authority "even in PoC or development mode".

**Not a numbered Immutable Constraint.** None of Constraints 1–6 names CORS. It is reached through the Rails sentence
and the API Security rule (§1.2 item 2).

R9 keeps CORS as the example on purpose. It shows a security control *simplified* (an allowlist hardcoded to one
origin) rather than *removed*. That keeps the placement rule it illustrates ("place the tag in the config file").
The origin uses `https` (`:55`, "Use HTTPS everywhere") and a reserved `example.com` name.

````
Before:
# <!-- POC-DEBT: CORS allow-all — restrict origins before production -->
cors:
  origin: "*"

After:
# <!-- POC-DEBT: CORS allowlist hardcoded to the single PoC demo origin — load the per-environment allowlist from configuration before production -->
cors:
  origin:
    - "https://poc-demo.example.com"
````

### 3.5 Pointer to the positive rule (insert: R6)

The skill is where prototyping agents read the tagging convention. One sentence points them to the rule and adds no
new obligation (§4).

````
Before:
```html
<!-- POC-DEBT: description of the shortcut or deferred concern -->
```

**Placement rules:**

After:
```html
<!-- POC-DEBT: description of the shortcut or deferred concern -->
```

A tag records a shortcut; it does not permit one. Security work may be simplified but never removed: the Immutable Security Constraints in `security-guidelines.md` apply to PoC code in full (`poc-guidelines.md` § Allowed Shortcuts).

**Placement rules:**
````

## 4. The positive rule: **add it to `poc-guidelines.md` (R4 and R5)**

**Decision: yes.** The repair needs more than new examples. Today the instruction's body gives an agent no way to
tell a permitted shortcut from a forbidden one:
- **Allowed Shortcuts (`:63–66`) is silent on security.**
- **Not Allowed (`:143–148`) names only Constraints 1–2**: "Exposing secrets in code", "Using real PII in demos". An
  agent reading the list could conclude that Constraints 3–6 may be traded for a tag.

**Why this is conservative.**
- **It restates existing authority.** It creates no new obligation. Every clause traces to `security-guidelines`
  Constraint 3 (`:157`) and the Rails (`:17–20`), or to this file's own Rails (`:17–19`).
- **It makes no exception.** It permits only what neither instruction forbids: simplifying *how* a control is built.
- **It does not change the Rails** (`:9–25`).

### R4: `:63–68`, after Allowed Shortcuts (insert a paragraph)

````
Before:
## Allowed Shortcuts
- Narrow test coverage to happy path
- Minimal infrastructure setup
- Temporary integration adapters

## Mandatory Debt Tracking

After:
## Allowed Shortcuts
- Narrow test coverage to happy path
- Minimal infrastructure setup
- Temporary integration adapters

Shortcuts may simplify security work but never remove it. The Immutable Security Constraints in `security-guidelines.md` apply to PoC code in full, and Constraint 3 holds "even in development or PoC mode": input validation, authentication checks and security middleware stay in place and stay enforced. What may be simplified is how a control is built, not what it enforces: for example, hand-written validation checks instead of a schema library, or a CORS allowlist hardcoded to the one demo origin. Tag the simplification like any other shortcut. A `POC-DEBT` tag records a shortcut; it does not permit one.

## Mandatory Debt Tracking
````

### R5: `:144–145`, Not Allowed (append a bullet)

This puts the rule on the list that the file's own Rails Failure mode treats as binding (`:21–23`, "violates this
instruction's own 'Not Allowed' list").

````
Before:
- Exposing secrets in code
- Using real PII in demos

After:
- Exposing secrets in code
- Using real PII in demos
- Relaxing any Immutable Security Constraint in `security-guidelines.md`, with or without a `POC-DEBT` tag
````

**Authority for R4–R5:** `security-guidelines:153`, `:157`, `:17–20`; `poc-guidelines:17–19`. The two examples R4
names are the replacements R2 and R9, and both satisfy `security-guidelines:30–32` and `:66`.

## 5. `security-guidelines.md`: **no change**

It already states the constraints and its own precedence (§1.1). Nothing in this ruling edits it, so its `stable`
status is unaffected by any priority choice.

## 6. Golden coupling

**No edit reaches a golden case.**
- `evaluate-poc-verdict-debt-reconciliation/brief.md` quotes `poc-guidelines` only at § Hypothesis-First Validation
  Rules 3–4 (`brief.md:63–64`, i.e. `poc-guidelines:55–56`) and refers to its "S/M/L effort and three-tier summary"
  (`brief.md:76–77`). R1–R5 touch neither the Rules, nor the Summary, nor the effort scale; R3 keeps effort `M`.
- Its `brief.md` cites no `poc-guidelines` line numbers, so R2's and R4's line shifts do not stale it.
- No `tests/golden/**` grant, no re-fixturing and no evaluator-hash baseline are needed.

**Is the fixture misleading under this ruling? No, not for what the case tests. No change is recommended.**
- The fixture's row 1 (`poc-evaluation.md:64`), "No input validation or length limit on search queries | CRITICAL |
  S | Query-based denial of service | backend-developer | blocks", is an evaluation *recording a defect found* in an
  illustrative PoC. It does not quote the guideline as a model.
- It grades the defect at the top tier with impact `blocks`. Its summary (`:31`) and backlog item 4 (`:26`) agree.
  That is the treatment `technical-debt-tracking:93` (security vulnerability → `critical`) and `:97` (`critical` →
  `must_fix_pre_prod`) prescribe.
- After R4, the correct response to a PoC that skipped validation is still to record it as a blocking finding, which
  is what the fixture shows.
- **One narrow residual.** The illustrative PoC *did* break Constraints 3–4, and the fixture's `proceed_with_constraints`
  does not say so. But whether "the evidence actually supports the verdict, or the recommendation follows from it" is
  judgement, which the suite expressly does not grade (`brief.md:98–99`).

If the P44 protected-path batch is ever opened, the row could optionally be reworded to a simplification gap. I do
**not** recommend spending a grant or a baseline on it.

## 7. Follow-ups and priority

### 7.1 Follow-up table

| Task | Covers | Files | `tests/golden/**` grant? | Owner (suggested) | Depends on / verify |
|---|---|---|---|---|---|
| **FU-1**: apply P42 | R1–R9 | `implementation/knowledge/instructions/poc-guidelines.md`; `implementation/knowledge/skills/rapid-prototyping/SKILL.md`; the regenerated `implementation/.<platform>/` mirrors (`make sync`); `implementation/registry/index.json` (generator); root-drift declarations in `tests/_baselines/root-install-drift.json` | **No** | Backend Developer: needs a shell for sync, registry and drift (T575's owner class). Not the Technical Writer, who has no Bash. | **Before dispatch:** a Security Engineer PASS on this artifact (plan-098 §2 step 2); T575 merged, or FU-1 based on it (both edit `rapid-prototyping`); the orchestrator runs the §8 #1 sweep and records P33 as fired (§7.3). **Verify:** (1) each Before matched exactly once, by text; (2) `sync.mjs --check` and `generate-registry.py --check` clean; (3) root parity gate green, declaring exactly what `--print-drift` reports, without double-counting `rapid-prototyping` paths T575 already declared; (4) 0 hits under `implementation/knowledge/` for `No input validation`, `disabled security`, `CORS allow-all` and `origin: "*"`; (5) `Relaxing any Immutable Security Constraint` occurs once in `poc-guidelines.md`; (6) `security-guidelines.md`, `commands/` and `tests/golden/**` byte-unchanged; (7) the `check-maturity` result matches the chosen priority (P2: baseline unchanged; P1: only the expected `poc-guidelines` hold); (8) golden scorecard unchanged. |
| **FU-2**: park O1 (§9) as a new item | `poc-security-engineer.md` treating Constraint 1 breaches as debt | none now | No | Orchestrator parks it. A later ruling by the Solution Architect with Security Engineer input. | Separate from FU-1: it touches a stable agent file, and the authority route (T542 precedent vs P34b) needs its own check. |

**No golden follow-up and no command follow-up.**

### 7.2 Priority: **P2, dispatched immediately after the Security review**

**Reasons:**
1. **A P1 label protects no one.** The `maturity:` key is source-only and is dropped from projections **(unverified;
   recorded for T556 in session memory)**. Demoting `poc-guidelines` would change nothing that installed client
   projects or this repo's root `.claude/rules/` copy actually load. Only landing FU-1 (plus a root refresh or
   drift declaration, and client `--update`) removes the examples.
2. **The corrective text is already in context.** `security-guidelines` is also `applyTo: "**"`, so every session
   that loads the bad example also loads Constraint 3 and the Rails sentence that overrides it. The risk is an agent
   copying the example despite that, which is real but not unmitigated.
3. **A demotion has real costs.**
   - While FU-1 is open, `poc-guidelines` could not serve as the "stable instruction" prong for ADR-007 branch 1. P29
     and P31 rested on that prong (`poc-contract-resolution-v1.md` §8), and a ruling taken up in the meantime, such
     as P33, would lose it.
   - It would also churn the `check-maturity` baseline **(unverified)**.
4. **The fix is small and fully specified.** Nine text edits on two files, with no golden coupling. It can land
   quickly at P2.

**When P1 is the better choice:** if FU-1 cannot be dispatched promptly. For example, if T575 or the Security review
stalls, or the user wants the label to reflect that a `stable` file currently contradicts its own Rails. That is a
legitimate honesty argument, and the decision is the user's.

### 7.3 Parked triggers

- **Fires: P42** (this task).
- **P33 fires when FU-1 edits `poc-guidelines.md`.** P33 is the "`poc-guidelines.md` owner items",
  `poc-contract-resolution-v1.md` §7.4/§9.3, plus O6/O7 of the overlaps artifact. The trigger reading is inferred from
  `poc-skill-command-overlaps-v1.md` §11 **(unverified)**.
  - **Recommendation: do not batch P33 into FU-1.** Keep the security fix small and reviewable by the Security
    Engineer.
  - R3 deliberately leaves P33's severity-column question open.

## 8. Unverified claims (need a shell)

1. **No other live file models the forbidden shortcuts.** I spot-checked only `poc-orchestrator.md`,
   `poc-security-engineer.md`, `new-poc.md` and `technical-debt-tracking/SKILL.md`. A `grep` under
   `implementation/knowledge/` (agents, commands, prompts, workflows, wiki) and `docs/guides/` is needed for:
   `No input validation`, `disabled security`, `allow-all`, `origin: "*"`, `Allow-Origin: *`. Any further hit takes
   the ruling of its matching site here.
2. **No golden case other than the one read quotes `poc-guidelines:79–90`, `:118–119`, `:63–68`, `:143–148`, or
   `rapid-prototyping:26–49`.** I relied on brief §2 and `poc-skill-command-overlaps-v1.md` §16.1 #1.
3. **The projections carry the same text.** Verified only for `implementation/.github/instructions/poc-guidelines.instructions.md`
   (same text, one line earlier), plus the repo-root `.claude/rules/poc-guidelines.md`, whose content this session
   loaded (from the primary checkout). The other platforms and every `rapid-prototyping` projection are unverified.
4. **The T575 interaction.**
   - Its status (merged or open) is unknown.
   - The line shift of about +7 lines is derived from E8's text, not measured.
5. **The `maturity:` key is not projected** (§7.2 reason 1). This comes from session memory, not checked in the
   worktree.
6. **P1 side effects** on the `check-maturity` baseline and on any test that keys on `poc-guidelines` being `stable`.
7. **The root-drift path count** for FU-1: `poc-guidelines` per platform plus `rapid-prototyping` per platform,
   net of T575's declarations.
8. **No live knowledge file cites `poc-guidelines` by line number at or after `:63`.** R2 adds 6 lines and R4 adds 2.
   Citations by section name are unaffected. Historical artifacts that cite lines stay as written.
9. **libpq details.** That libpq accepts `?sslmode=require` in a `postgresql://` URI, and that its default is
   `prefer`. This is from knowledge; I could not fetch docs without a shell.
10. **P33's trigger is "`poc-guidelines.md` edited"** (§7.3).
11. **`bce238a` differs from the brief's `0956b1d` only under `docs/`.** Every line I cite matches at `bce238a`.

## 9. Findings outside scope (not decided; candidates for parking)

- **O1 (major, security; proposed P45): the PoC security agent routes Constraint-1 breaches to debt.**
  - `poc-security-engineer.md` (`maturity: stable`) says at `:19–20`: "Do not block progress by default … Record
    findings for debt handoff". Its Failure mode (`:47`) reads: "If a critical risk (exposed secret, obvious
    injection/auth gap) is found, records it explicitly for debt handoff".
  - **Why it conflicts:**
    - Constraint 1 is "not negotiable regardless of PoC status".
    - `security-guidelines`' own Failure mode (`:22–23`) says `SECURITY:CRITICAL`/`HIGH` findings "block merge".
    - An exposed secret recorded as debt and left in place is the same class of defect as P42, moved from examples
      into an agent's operating rule.
  - `poc-orchestrator.md:114` ("DO NOT block on non-critical security findings") is consistent as written, because
    it says *non-critical*. But `:53` scopes the PoC scan to "critical risks only", and the two agents together leave
    no text saying a critical PoC finding blocks.
  - **Not ruled.** It touches stable agent files, and whether the T542 precedent suffices or P34b is needed must be
    checked separately (FU-2).
- **O2 (minor; P33): two category vocabularies.** The scorecard template uses categories `Validation` and
  `Reliability` (`poc-guidelines:119–120`). `technical-debt-tracking:9–14` lists Security, Architecture, Testing,
  Data quality and Operations. R3 keeps `Validation` so as not to decide this.
- **O3 (minor): the narrow parenthetical in `poc-guidelines`' Rails.** "(no exposed secrets, no real PII in demos)"
  (`:18`) names only Constraints 1–2. R4 and R5 close the gap in the body. The Rails is left unchanged on purpose, to
  keep the stable file's Rails untouched.
- **O4 (minor, reliability): the A3 example has no timeout.** `requests.post` with no timeout can hang indefinitely,
  and the remedy names "async with retry" but not timeouts. Not a security rule. Noted only.
- **O5 (minor): the skill's tag format omits the remedy half.** `rapid-prototyping:27`,
  `<!-- POC-DEBT: description of the shortcut or deferred concern -->`, lacks the production-remedy half that
  `poc-guidelines` Debt Tag Rule 1 (`:93`) requires. The skill's examples include it, but the format line does not.
  Candidate for a later skill pass.

## 10. Corrections to the brief (all `unclear_requirements`, `minor`)

1. **§2 row 4: the range `:35–47` is too narrow.** The examples block runs `:35–49`. The CORS fence opens at `:45`,
   and `origin: "*"` is at `:48`. The placement rules are `:30–33`.
2. **§2 row 5: `:150–158` is off by one at the start and stops short.** The section heading is `:151` (`:150` is
   blank), the "absolute" preamble is `:153`, and the list runs to `:160` (Constraints 5–6). The quoted Constraints 3
   and 4 are correctly at `:157–158`.
3. **§2 row 6: the Rails "Out of scope" paragraph is `:15–20`.** The quoted sentence is `:17–20`. The bolded
   supersession clause is `:19–20`. This is a refinement, not an error.
4. **§2 omits two `poc-guidelines` sites that the ruling needs:**
   - scorecard row 1 (`:118`), the connection-string example's scorecard twin, which is in scope through §2's
     connection-string question;
   - Not Allowed (`:143–148`), which lists only Constraints 1–2 and is where R5 lands.
5. **The facts were verified on `0956b1d`; this worktree is at `bce238a`.** All cited lines match at `bce238a` (§8
   #11).
6. **§2's "No golden case quotes these example sections" is confirmed for the one case I may read** (§6). It is
   unverified beyond that (§8 #2).

No fact in §2 was found materially wrong. **No blockers.**

## 11. Summary

| Site | Ruling | Edit | Authority |
|---|---|---|---|
| A1 `poc-guidelines:81–82` connection string | Acceptable with condition: state "no credentials", require TLS | R1 | C1 `:155`; `:69–70`; `:79` |
| A2 `poc-guidelines:84–86` no input validation | Forbidden → simplified-not-removed validation | R2 | C3 `:157`; C4 `:158`; `:29–32`; own Rails `:17–19` |
| A3 `poc-guidelines:88–89` synchronous call | Acceptable, unchanged | — | no rule reached |
| B `poc-guidelines:119` scorecard row 2 | Forbidden → mirrors R2 (row 1 `:118` unchanged) | R3 | as A2 |
| C `rapid-prototyping:33` "disabled security" | Forbidden → non-secret values / single replica | R7 | C3; Rails `:17–20` |
| D1 `rapid-prototyping:37–39` no input validation | Forbidden → as R2 | R8 | as A2 |
| D2 `rapid-prototyping:41–42` in-memory store | Acceptable, unchanged | — | no rule reached |
| D3 `rapid-prototyping:45–49` CORS allow-all | Forbidden (breaks "Use CORS allowlist"; not a numbered constraint) → single-origin allowlist | R9 | `:66`; Rails `:17–20` |
| Positive rule | Add to `poc-guidelines` (paragraph + Not Allowed bullet) and point to it from the skill | R4, R5, R6 | C3; Rails of both instructions |
| `security-guidelines` | Unchanged | — | — |
| Golden fixture | Not misleading for what it tests; no change, no grant | — | `brief.md:98–99`; `technical-debt-tracking:93,97` |
| Priority | P2, dispatched next after Security review; P1 if dispatch would stall | — | §7.2 |
| P34b | Not needed | — | §1.2–1.3 |
