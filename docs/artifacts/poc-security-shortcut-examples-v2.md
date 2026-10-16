# Artifact: poc-security-shortcut-examples-v2.md

> Filename: `poc-security-shortcut-examples-v2.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T576 (revision after Security review)
- **Created**: 2026-10-02
- **Based on**:
  - `docs/artifacts/poc-security-shortcut-examples-v1.md`;
  - the read-only Security Engineer review of v1, **VERDICT: CONDITIONAL_PASS**, findings F1–F8. I received these as
    relayed by the orchestrator and did not read a review file myself;
  - `docs/tasks/task-T576.md`; `docs/plans/plan-098-poc-security-shortcut-examples.md`;
  - `docs/artifacts/poc-skill-command-overlaps-v1.md` §13 (O1) and §16.3 (P42);
  - `implementation/knowledge/instructions/poc-guidelines.md` (`stable`) and `security-guidelines.md` (`stable`);
  - `implementation/knowledge/skills/rapid-prototyping/SKILL.md` (`experimental`).

  All were read on branch `agent/solution-architect/T576` at `develop` `bce238a`.
- **Supersedes**: `poc-security-shortcut-examples-v1.md`. v1 stays unchanged as the historical record. **Where v1 and
  v2 differ, v2 governs.** FU-1 applies v2 only.
- **Decision references**: P42. No new ADR is minted. ADR-007 is not applied, and no P34b ranking is used (§1).

## 0. What this document is, and what it did not do

This document is the full, self-contained ruling on every brief §2 site. It incorporates the Security review's
conditions. §12 lists every v1→v2 change by finding. **It changed no instruction, skill, command, agent or golden
case.**

**Method and limits.**
- **No shell**, the same as for v1. Claims that would need a search or a run are marked **(unverified)** (§8).
- **Files read for v1 apply unchanged** (v1 §0). For v2 I re-read nothing new: the review's citations
  (`security-guidelines:35`, `:56–63`, `:76`, `:79`) match the file as read for v1.
- **Golden files:** none opened for v2.

**Line numbers.**
- Line numbers below are at `bce238a`.
- `develop` now includes T575, which inserts a `## Rails` block into `rapid-prototyping`, so that file's line numbers
  are shifted on `develop`.
- **FU-1 applies every edit by matching its Before text exactly, never by line number.** Every Before text below is
  unique in its file at `bce238a`. None lies in a region T575 edits (T575's E8–E11 touch `rapid-prototyping:7–9`,
  `:54`, `:99`, `:102–105`). That the Before texts are byte-identical on post-T575 `develop` is **(unverified)**
  (§8 #4).

## 1. Authority basis

### 1.1 The quoted texts

Both instructions declare `applyTo: "**"` and `maturity: stable` (`poc-guidelines.md:3–4`,
`security-guidelines.md:3–4`).

**`security-guidelines.md`, its own precedence claim.** Rails, `:17–20`: "Does not grant any agent authority to
disable a security control 'temporarily,' even in PoC or development mode — the Immutable Security Constraints
section forbids that outright, superseding any speed-over-completeness pressure from `poc-guidelines.md`."

**`security-guidelines.md`, the Immutable Security Constraints:**
- `:153`: "The following constraints are absolute and cannot be overridden by any agent, configuration, or runtime
  decision:"
- `:155`, Constraint 1: "No API keys, passwords, tokens, **certificates**, or private keys may ever be committed. This
  is not negotiable regardless of PoC status, urgency, or convenience."
- `:157`, Constraint 3: "Security middleware, input validation, and authentication checks must never be bypassed,
  even in development or PoC mode."
- `:158`, Constraint 4: "Every input from outside the system boundary (user input, API calls, file uploads,
  environment variables) must be validated before use."

**`security-guidelines.md`, the security controls that are not Immutable Constraints:**
- `:29–32`: "Validate ALL user input on the server side … Use allowlists over denylists … Validate type, length,
  format, and range … Reject and log invalid input — don't silently fix it"
- `:35`: "Hash passwords with bcrypt (cost >= 10) or argon2id"
- `:55–66`: "Use HTTPS everywhere … Implement rate limiting on all endpoints … Set security headers … Use CORS
  allowlist (never `Access-Control-Allow-Origin: *` with credentials)"
- `:69–70`: "NEVER commit secrets to source control … Use environment variables or secret vaults"
- `:76`: "ALWAYS use parameterized queries / prepared statements"
- `:79`: "Use TLS for database connections"
- `:83`: "DO NOT log: passwords, tokens, session IDs, PII, credit card numbers"
- `:177`, OWASP A10: "Validate/sanitize URLs, use allowlists, block internal network access"

**`poc-guidelines.md`, its own subordination.** Rails, `:17–19`: "Does not waive the Immutable Security Constraints in
`security-guidelines.md` (no exposed secrets, no real PII in demos) merely because a workstream is time-boxed."

### 1.2 Reading

**The brief's reading holds, so no P34b ranking is needed.**
- `security-guidelines` asserts precedence over `poc-guidelines` by name.
- `poc-guidelines` concedes it in its own Rails.
- Constraint 3 names the PoC context itself.

**The scope of the authority is "a security control", not only the six Constraints.** v1 identified this for CORS,
but then wrote R4–R6 against the Immutable Constraints only, which re-created the gap. The Security review raised this
as F1.
- The Rails sentence (`:17–18`) withholds authority to disable "a security control … even in PoC or development
  mode". That reaches every control in §1.1's second list.
- `poc-guidelines` claims no exemption for any of them. Its Allowed Shortcuts (`:63–66`) name none.
- One side asserts and the other does not contest, so again no ranking is needed.

**The skill.** `rapid-prototyping` is `experimental`, claims no exemption, and only *exemplifies* shortcuts.
Replacing the examples makes the skill and both instructions jointly satisfiable. That is the method of
`gate-verdict-consistency-v1.md` §1.2(i), accepted in its §13.2. No skill is ranked against an instruction.

## 2. `poc-guidelines.md` (stable)

### 2.1 Site A1: `:81–82`, connection string. **Acceptable with conditions (amend: R1)** *(revised, F2)*

**Constraint 1 is not broken.** The URL carries no credential. A hardcoded non-secret value is "Minimal
infrastructure setup" (`:65`).

**Conditions:**
1. **The tag must draw the Constraint 1 line.** "No credentials in it", and the credentials come from the vault.
2. **The URL must meet `:79` with real server authentication.**
   - v1's `sslmode=require` encrypts but does not verify the server, so it gives no MITM protection. It would
     *weaken* authentication silently, which contradicts R4.
   - `verify-full` verifies both the chain and the hostname.
3. **The CA certificate is never committed.** Constraint 1 names "certificates". It is loaded from libpq's default
   location or `PGSSLROOTCERT`.

This is the reviewer's preferred wording, verbatim.

````
Before:
# <!-- POC-DEBT: Hardcoded connection string; production must use secret vault -->
db_url = "postgresql://localhost:5432/poc_db"

After:
# <!-- POC-DEBT: Hardcoded local database URL (no credentials in it); production must read the URL from configuration and the credentials from the secret vault. The local Postgres must run with TLS enabled; the CA certificate is loaded from libpq's default location or PGSSLROOTCERT, never committed -->
db_url = "postgresql://localhost:5432/poc_db?sslmode=verify-full"
````

**Consequence:** the local PoC database needs a TLS certificate whose name matches `localhost`. That is the cost of
`:79` under §1.2, not a new requirement.

**Authority:** `:155`, `:69–70`, `:79`.

### 2.2 Site A2: `:84–86`, "No input validation". **Forbidden (replace: R2)** *(revised, F3, F4, F6)*

It breaks Constraints 3 and 4 and `:29–32`, and it contradicts this file's own Rails. The replacement keeps the
function and makes validation present but simplified:
- hand-written inline checks instead of the shared schema layer;
- type, length and format checks, with an allowlist pattern for email (`:30–31`);
- names that are only whitespace are rejected, not trimmed (`:32`, "don't silently fix it");
- rejections are logged with the field name only, so no PII is logged (`:83`);
- only the two allowlisted fields are inserted.

````
Before:
# <!-- POC-DEBT: No input validation; production must validate all user input -->
def create_user(name, email):
    return db.insert({"name": name, "email": email})

After:
import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,63}")

# <!-- POC-DEBT: Hand-written inline validation instead of the shared request-schema layer; production must move these checks into the schema layer and return the project's standard validation error response; keep inserting only allowlisted fields (never pass the request object through), via parameterized queries -->
def create_user(name, email):
    if not (isinstance(name, str) and 1 <= len(name) <= 100 and name.isprintable() and name.strip()):
        log.warning("input_rejected", extra={"field": "name"})
        raise ValueError("invalid name")
    if not (isinstance(email, str) and len(email) <= 254 and EMAIL_RE.fullmatch(email)):
        log.warning("input_rejected", extra={"field": "email"})
        raise ValueError("invalid email")
    return db.insert({"name": name, "email": email})
````

**Notes:**
- **Length before regex.** `len(email) <= 254` runs before `EMAIL_RE.fullmatch`, because `and` short-circuits, so the
  regex only ever sees bounded input.
- **The narrow ASCII-only pattern is part of the simplification.** It is an allowlist and errs toward rejection.
- **Undefined names.** `log` and `db` are left undefined, in the same style as the other examples.
- **F6 wording deviation.** The reviewer proposed "…; insert only allowlisted fields (never pass the request object
  through), via parameterized queries." I wrote "**keep** inserting only allowlisted fields …". Placed after "production
  must …", the reviewer's wording would read as a *deferred* production item. But `:76` ("ALWAYS use parameterized
  queries") applies to the PoC now (§1.2), and the code already inserts only the two fields. "Keep" states the same
  requirement without teaching that it can wait. The substance is unchanged.

### 2.3 Site A3: `:88–89`, synchronous call. **Acceptable with conditions (replace: R10)** *(revised, F8; v1 said "unchanged")*

**v1 was wrong to leave this unchanged.**
- A model call with no timeout can hang the PoC.
- The remedy said nothing about the response, which Constraint 4 requires to be "validated before use".
- The URL's provenance was unstated. Under OWASP A10 (`:177`) a user-influenced URL is an SSRF path.

R10 adds `timeout=10`, a provenance comment on the URL, and the response-validation duty.

````
Before:
# <!-- POC-DEBT: Synchronous call; production should use async with retry -->
response = requests.post(external_api_url, json=payload)

After:
# external_api_url is fixed HTTPS configuration, never user input (OWASP A10, SSRF)
# <!-- POC-DEBT: Synchronous call with no retry; production should use async with retry. The response is validated before use, in the PoC as in production -->
response = requests.post(external_api_url, json=payload, timeout=10)
````

**F8 wording deviation.** The reviewer proposed "…; production should use async with retry and validate the response
before use". That places response validation under "production should", which would model deferring Constraint 4
("validated before use", with no PoC exception). R10 keeps async-with-retry as the deferred shortcut and states
response validation as a standing duty. The substance is the reviewer's.

The provenance comment sits *above* the tag, so the tag stays directly adjacent to the shortcut line (Debt Tag Rule
2, `:94`).

### 2.4 Site B: `:118–120`, scorecard template rows

**Row 2 (`:119`): forbidden (replace: R3).** It mirrors R2.

````
Before:
| 2 | src/api.py | 34 | Validation | No input validation | M — add schema validation |

After:
| 2 | src/api.py | 34 | Validation | Hand-written inline input validation instead of the shared schema layer | M — move checks into the request-schema layer |
````

**Row 1 (`:118`): amend to mirror R1 (R11), keeping the category `Security`.** *(new, F5)*

The reviewer proposed category `Configuration` and asked me to keep `Security` if the change would touch P33.
**I keep `Security`.**
- P33 fires on *any* FU-1 edit to this file anyway (§7.3), so the category is not what triggers it.
- `Configuration` would, however, settle the category-vocabulary question (§9 O2, a P33 candidate) by fiat. It is in
  neither vocabulary: the template has `Security`/`Validation`/`Reliability`, and `technical-debt-tracking:9–14` has
  Security, Architecture, Testing, Data quality and Operations.
- `Security` remains accurate, because the remedy still moves credentials into the vault.

````
Before:
| 1 | src/db.py | 12 | Security | Hardcoded connection string | S — use vault integration |

After:
| 1 | src/db.py | 12 | Security | Hardcoded local database URL (no credentials) | S — read URL from configuration, credentials from vault |
````

**Row 3 (`:120`): acceptable, unchanged.**

## 3. `rapid-prototyping/SKILL.md` (experimental)

Apply by text (§0). No site below overlaps T575.

### 3.1 Site C: `:33`, "disabled security". **Forbidden (amend: R7)** *(unchanged from v1)*

````
Before:
- For configuration shortcuts (e.g., hardcoded values, disabled security), place the tag in the config file.

After:
- For configuration shortcuts (e.g., hardcoded non-secret values, a single replica with no autoscaling), place the tag in the config file.
````

**Authority:** Constraint 3; Rails `:17–20`.

### 3.2 Site D1: `:37–39`, "No input validation". **Forbidden (replace: R8)** *(revised, F3, F4, F6)*

It breaks the same rules as A2. It is worse in one respect: the original inserted the caller's whole dict (mass
assignment). The replacement is R2's code in the skill's tag style, with the skill's `db.users.insert`. The F6
wording deviation is the same as in §2.2, for the same reason.

````
Before:
# <!-- POC-DEBT: No input validation — add comprehensive validation before production -->
def create_user(data):
    return db.users.insert(data)

After:
import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,63}")

# <!-- POC-DEBT: Hand-written inline validation instead of the shared request-schema layer — move these checks into the schema layer before production; keep inserting only allowlisted fields (never pass the request object through), via parameterized queries -->
def create_user(name, email):
    if not (isinstance(name, str) and 1 <= len(name) <= 100 and name.isprintable() and name.strip()):
        log.warning("input_rejected", extra={"field": "name"})
        raise ValueError("invalid name")
    if not (isinstance(email, str) and len(email) <= 254 and EMAIL_RE.fullmatch(email)):
        log.warning("input_rejected", extra={"field": "email"})
        raise ValueError("invalid email")
    return db.users.insert({"name": name, "email": email})
````

### 3.3 Site D2: `:41–42`, in-memory store. **Acceptable, unchanged**

### 3.4 Site D3: `:45–49`, "CORS allow-all". **Forbidden (replace: R9)** *(revised, optional item: "exact-match")*

**It breaks a stated rule, and is not merely a weaker default.**
- `:66`'s primary instruction is "Use CORS allowlist". `origin: "*"` is not an allowlist, whether or not credentials
  are enabled.
- With credentials, it also breaks the absolute "never".
- Disabling the allowlist disables "a security control", which the Rails (`:17–20`) forbid in PoC mode.
- It is not a numbered Immutable Constraint.

The replacement keeps CORS on purpose, to show a control *simplified* rather than removed.

````
Before:
# <!-- POC-DEBT: CORS allow-all — restrict origins before production -->
cors:
  origin: "*"

After:
# <!-- POC-DEBT: CORS exact-match allowlist hardcoded to the single PoC demo origin — load the per-environment exact-match allowlist from configuration before production -->
cors:
  origin:
    - "https://poc-demo.example.com"
````

### 3.5 Pointer to the positive rule (insert: R6) *(revised, F1)*

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

A tag records a shortcut; it does not make a forbidden shortcut permissible. Security work may be simplified but never removed or weakened: the rules in `security-guidelines.md`, including its Immutable Security Constraints, apply to PoC code in full (`poc-guidelines.md` § Allowed Shortcuts).

**Placement rules:**
````

## 4. The positive rule: **add it to `poc-guidelines.md` (R4, R5)** *(revised, F1)*

**Decision: yes.** The instruction body gives an agent no way to tell a permitted shortcut from a forbidden one:
- **Allowed Shortcuts (`:63–66`) is silent on security.**
- **Not Allowed (`:143–148`) names only Constraints 1–2.**

v1's rule bound only the Immutable Constraints, which left CORS, parameterized queries, DB TLS, password hashing,
rate limiting and security headers outside it (F1). v2 binds every security control, matching the scope of
`security-guidelines`' Rails (`:17–18`, "a security control").

**Why it remains conservative.**
- **It restates existing authority** (§1.1–1.2) and creates no new obligation.
- **It makes no exception.** It permits only what neither instruction forbids: simplifying *how* a control is built.
- **It does not change the Rails** (`:9–25`).

### R4: `:63–68` (insert a paragraph)

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

Shortcuts may simplify how security controls are built but never remove or weaken them. Every rule in `security-guidelines.md` applies to PoC code, and its Immutable Security Constraints apply in full; Constraint 3 holds "even in development or PoC mode": input validation, authentication checks and security middleware stay in place and stay enforced. What may be simplified is how a control is built, not what it enforces: for example, hand-written validation checks instead of a schema library, or a CORS allowlist hardcoded to the one demo origin. Tag the simplification like any other shortcut. A `POC-DEBT` tag records a shortcut; it does not make a forbidden shortcut permissible.

## Mandatory Debt Tracking
````

### R5: `:144–145` (append a bullet; reviewer's wording, verbatim)

````
Before:
- Exposing secrets in code
- Using real PII in demos

After:
- Exposing secrets in code
- Using real PII in demos
- Removing or weakening any security control in `security-guidelines.md` — including every Immutable Security Constraint — with or without a `POC-DEBT` tag
````

**Authority for R4–R6:** `security-guidelines:17–20`, `:153`, `:157`; `poc-guidelines:17–19`. The two examples that
R4 names are R2 and R9. Both satisfy `:30–32` and `:66`.

**Consequence for the user to see.** "Every rule … applies to PoC code" means a PoC also gets HTTPS, rate limiting
and the security headers (`:55–64`) on its endpoints, and hashed passwords if it stores any. This is what
`security-guidelines` already requires (§1.2). R4 makes it visible; it does not add it. It may still change how
expensive users find a PoC, so the decision record should say so plainly.

## 5. `security-guidelines.md`: **no change**

## 6. Golden coupling *(unchanged from v1)*

**No edit reaches a golden case.**
- The `evaluate-poc-verdict-debt-reconciliation` brief quotes only `poc-guidelines` Rules 3–4 and the S/M/L effort
  and three-tier summary. No edit touches either. R3 keeps effort `M`, and R11 keeps `S`.
- The brief cites no `poc-guidelines` line numbers.

**The fixture is not misleading for what the case tests.**
- Its row "No input validation or length limit on search queries | CRITICAL | … | blocks" records a defect that was
  found, at the tier `technical-debt-tracking:93,97` prescribes.
- Whether the verdict follows from the evidence is judgement, which the case expressly does not grade
  (`brief.md:98–99`).

**Needed:** no grant, no fixture change, no baseline.

## 7. Follow-ups and priority

### 7.1 Follow-up table

| Task | Covers | Files | `tests/golden/**` grant? | Owner (suggested) | Depends on / verify |
|---|---|---|---|---|---|
| **FU-1**: apply P42 per **v2** | R1–R11 | `implementation/knowledge/instructions/poc-guidelines.md`; `implementation/knowledge/skills/rapid-prototyping/SKILL.md`; regenerated `implementation/.<platform>/` mirrors (`make sync`); `implementation/registry/index.json` (generator); root-drift declarations in `tests/_baselines/root-install-drift.json` | **No** | Backend Developer (needs a shell) | **Before dispatch:** this v2 is the applied version; the orchestrator records P33 as fired (§7.3). **Verify:** (1) each Before matched exactly once **by text** on current `develop` (post-T575); (2) `sync.mjs --check` and `generate-registry.py --check` clean; (3) root parity gate green, declaring exactly what `--print-drift` reports and not double-counting T575's `rapid-prototyping` paths; (4) 0 hits under `implementation/knowledge/` for `No input validation`, `disabled security`, `CORS allow-all`, `origin: "*"` and `sslmode=require`; (5) `Removing or weakening any security control` occurs once in `poc-guidelines.md`, and `does not make a forbidden shortcut permissible` occurs once in each of the two files; (6) `security-guidelines.md`, `commands/` and `tests/golden/**` byte-unchanged; (7) `check-maturity` matches the chosen priority; (8) golden scorecard unchanged. |
| **FU-2**: O1 as its own task *(revised: was "park")* | `poc-security-engineer.md` and `poc-orchestrator.md` routing critical findings to debt; `rapid-prototyping:54` (pre-T575 numbering) | per that task's brief | No | Orchestrator scopes it; a ruling with Security Engineer input | Re-rated **SECURITY:HIGH** by the reviewer (§9). Not ruled here. |

**No golden follow-up and no command follow-up.**

### 7.2 Priority: **P2, dispatched immediately**

v1's reasoning stands.
1. A P1 demotion does not change shipped guidance: `maturity:` is source-only **(unverified)**. Only landing FU-1
   does.
2. `security-guidelines` is co-loaded everywhere (`applyTo: "**"`).
3. A demotion would remove `poc-guidelines`' standing as a stable instruction under ADR-007 while FU-1 is open.
4. The fix is small, fully specified, and has no golden coupling.

**P1 is the better choice** if FU-1 cannot be dispatched promptly, or if the user wants the label to show that a
stable file currently contradicts its own Rails. The decision is the user's.

**What v2 changes for the user's decision:**
- R4/R5 now state a wider scope, every security control (§4 Consequence). This is still a restatement of the
  authority, but the user should see it when choosing P1 or P2.
- O1's re-rating to HIGH is a separate task and does not change FU-1's priority.

### 7.3 Parked triggers

- **Fires: P42.**
- **P33 fires on FU-1's edit to `poc-guidelines.md`** **(trigger reading unverified)**. Do not batch P33 into FU-1.
  R3 and R11 deliberately leave its category and severity-column questions open.

## 8. Unverified claims (need a shell)

1. **Settled by the orchestrator: no other live file models the forbidden shortcuts.** The orchestrator's shell sweep
   found the forbidden phrases only at the ruled sites: `rapid-prototyping:33`, `:37`, `:46` and
   `poc-guidelines:84`, `:119`. The one other hit, `security-guidelines:157`, is Constraint 3 itself.
2. No golden case other than the one read for v1 quotes the edited lines. I relied on brief §2 and
   `poc-skill-command-overlaps-v1.md` §16.1 #1.
3. **The projections carry the same text.** Verified for v1 only for
   `implementation/.github/instructions/poc-guidelines.instructions.md` and the repo-root `.claude/rules/poc-guidelines.md`.
4. **Every Before text is byte-identical on post-T575 `develop`.** My worktree is at `bce238a`, before T575. T575's
   specified edits do not touch these sites, but the merged result is unchecked.
5. **`maturity:` is not projected.** This comes from session memory.
6. **P1 side effects** on the `check-maturity` baseline.
7. **The root-drift path count** for FU-1, net of T575's declarations.
8. **No live knowledge file cites `poc-guidelines` line numbers at or after `:63`.**
   - Line growth at `bce238a` in `poc-guidelines`: R2 adds 10, R10 adds 1, R4 adds 2.
   - In `rapid-prototyping`: R6 adds 2, R8 adds 10, R9 adds 1.
9. **libpq behaviour.** That `?sslmode=verify-full` in a `postgresql://` URI makes libpq verify the CA chain and the
   hostname, using `~/.postgresql/root.crt` by default or `PGSSLROOTCERT`. This is from knowledge plus the reviewer's
   text; I could not fetch docs.
10. **P33's trigger** is "`poc-guidelines.md` edited".
11. **`bce238a` differs from the brief's `0956b1d` only under `docs/`.**
12. **I did not read the Security review file.** v2 follows the orchestrator's relay of it.

## 9. Findings outside scope

- **O1: re-rated SECURITY:HIGH by the Security reviewer; it gets its own task (FU-2) instead of parking.** Recorded
  only; **not ruled here**.
  - **The finding:** `poc-security-engineer.md:19–20`, and its Failure mode at `:47`, route "exposed secret, obvious
    injection/auth gap" to debt handoff instead of blocking. `poc-orchestrator.md:53` scopes the PoC scan to "critical
    risks only".
  - **The reviewer's fix direction:** a blocking carve-out for constraint breaches and for CRITICAL/HIGH findings,
    plus rotation of any exposed secret.
  - **Linked site: `rapid-prototyping:54`** (pre-T575 numbering; T575's E9 rewrites that bullet). Per the reviewer,
    an *untagged security-control removal* should block, not be a 🟡 Should Fix. This goes with the O1 task, not
    FU-1.
- **O2 (minor; P33 candidate): two category vocabularies.** This is why R11 keeps `Security`.
- **O3 (minor): the narrow parenthetical in `poc-guidelines`' Rails** (`:18`). R4 and R5 close the gap in the body.
  The Rails stays unchanged.
- **O4: resolved by R10.** It was "no timeout" in v1.
- **O5 (minor): `rapid-prototyping:27`'s tag format lacks the production-remedy half** that Debt Tag Rule 1 (`:93`)
  requires.

## 10. Corrections to the brief (`unclear_requirements`, all `minor`; unchanged from v1)

1. The `rapid-prototyping` examples run `:35–49`, not `:35–47`. `origin: "*"` is at `:48`, and the placement rules
   are `:30–33`.
2. The Immutable Constraints section is `:151–160`, not `:150–158`.
3. The Rails "Out of scope" paragraph is `:15–20`, and the quoted sentence is `:17–20`.
4. §2 omits scorecard row 1 (`:118`) and Not Allowed (`:143–148`). Both are now edited (R11, R5).
5. The facts were verified on `0956b1d`; this worktree is at `bce238a`.
6. "No golden case quotes these example sections" is confirmed for the one case I may read.

**No blockers.**

## 11. Summary

| Site | Ruling | Edit | Authority |
|---|---|---|---|
| A1 `poc-guidelines:81–82` connection string | Acceptable with conditions: no credentials, `verify-full`, CA never committed | R1 | `:155`, `:69–70`, `:79` |
| A2 `poc-guidelines:84–86` no input validation | Forbidden → simplified validation: defined `EMAIL_RE`, whitespace rejected, allowlisted fields | R2 | `:157`, `:158`, `:29–32`, `:76`, `:83` |
| A3 `poc-guidelines:88–89` synchronous call | Acceptable with conditions: timeout, fixed URL, response validated | R10 | `:158`, `:177` |
| B `poc-guidelines:119` row 2 | Forbidden → mirrors R2 | R3 | as A2 |
| B `poc-guidelines:118` row 1 | Mirror R1; category kept `Security` | R11 | as A1; O2 |
| C `rapid-prototyping:33` "disabled security" | Forbidden | R7 | `:157`; Rails `:17–20` |
| D1 `rapid-prototyping:37–39` no input validation | Forbidden → as R2 | R8 | as A2 |
| D2 `rapid-prototyping:41–42` in-memory store | Acceptable, unchanged | — | — |
| D3 `rapid-prototyping:45–49` CORS allow-all | Forbidden → exact-match single-origin allowlist | R9 | `:66`; Rails `:17–20` |
| Positive rule | Binds every security control, not only the six Constraints | R4, R5, R6 | Rails `:17–20`; `:153`, `:157`; `poc-guidelines:17–19` |
| `security-guidelines` | Unchanged | — | — |
| Golden | No change, no grant | — | §6 |
| Priority | P2, dispatched immediately; P1 if dispatch would stall | — | §7.2 |
| O1 | SECURITY:HIGH, its own task; not ruled | FU-2 | reviewer |

## 12. Change log v1 → v2

| Finding | Severity | v2 change | Where |
|---|---|---|---|
| **F1** scope gap | MEDIUM (mandatory) | R4's first two sentences replaced with the reviewer's wording. R5 replaced with the reviewer's wording, verbatim. R6 widened to "the rules in `security-guidelines.md`, including its Immutable Security Constraints". "it does not permit one" → "it does not make a forbidden shortcut permissible" in R4 and R6. §1.2 now states the authority's scope as "a security control". | §1.2, §3.5, §4 |
| **F2** `sslmode=require` | MEDIUM (mandatory) | R1 replaced with the reviewer's preferred tag and `?sslmode=verify-full`, verbatim. The CA is never committed (Constraint 1 names certificates). v1's "severable TLS suffix" note is withdrawn. | §2.1 |
| **F3** undefined `EMAIL_RE` | LOW | `import re` and the reviewer's `EMAIL_RE` added to R2 and R8. The `len(email) <= 254` check is kept before the regex. | §2.2, §3.2 |
| **F4** whitespace-only names | LOW | `and name.strip()` added to the name condition in R2 and R8, so these names are rejected, not trimmed. | §2.2, §3.2 |
| **F5** scorecard row 1 | LOW | New edit R11 mirrors R1. **Category kept `Security`, not `Configuration`.** P33 fires on any edit, but `Configuration` would decide the O2 vocabulary question by fiat. | §2.4 |
| **F6** allowlisted fields and parameterized queries | LOW | Appended to the R2 and R8 tags. **Wording deviation:** "keep inserting …" instead of "insert …", so that a rule that applies now (`:76`) is not presented as a deferred production item. | §2.2, §3.2 |
| **F8** synchronous call | LOW | A3 is no longer "acceptable unchanged". New edit R10 adds `timeout=10`, a URL-provenance comment (fixed HTTPS configuration, never user input; A10) and the response-validation duty. **Wording deviation:** response validation is stated as a standing duty ("in the PoC as in production"), not under "production should", because Constraint 4 has no PoC exception. | §2.3 |
| Optional | — | "exact-match" added to the R9 tag. | §3.4 |
| §8 #1 | — | Settled by the orchestrator's sweep. | §8 |
| O1 | — | Re-rated SECURITY:HIGH; it becomes its own task (FU-2); the fix direction is recorded; `rapid-prototyping:54` is attached to it. Not ruled. | §7.1, §9 |
| Line numbers | — | Apply-by-text instruction made explicit for post-T575 `develop`. | §0, §7.1 |
| (F7) | — | Not relayed to me, so there is no v2 change for it. | — |

## 13. Orchestrator verification and rulings (added before commit, 2026-10-02)

*The orchestrator added this section, not the producing agent. It applies on `develop` `7da064a`, which includes
T575. §§0–12 are unchanged.*

**13.1 Verified**

- **Every edit applies on current `develop`.** I simulated all 11 Before→After pairs in order against the live files:
  7 in `poc-guidelines.md` (§2, §4) and 4 in `rapid-prototyping/SKILL.md` (§3). Each Before text occurs **exactly
  once**, including after T575's `## Rails` insert. This settles §8 #4.
- **The sweep (§8 #1) finds nothing beyond the ruled sites.** Searching for the forbidden phrases across
  `implementation/knowledge/` hits only the ruled sites, plus the constraint itself at `security-guidelines:157`.
- **No golden case quotes the edited sections (§8 #2).** I searched `tests/golden/` with `held-out` pruned. The only
  hits are a debt row in the `evaluate-poc` fixture, which records a violation and quotes no guideline, and old
  ledger text in the `team-status` fixture. No grant is needed and the baseline does not change.
- **Maturity is not projected (§8 #5).** The `.github` instruction projection and the root `.claude/rules/` copy carry
  no `maturity:` line.
- **No live file cites `poc-guidelines` line numbers (§8 #8).**
- **The projections number 7 (§8 #3, #7).** `poc-guidelines` has one per platform, and `rapid-prototyping` adds 7
  more, so FU-1 declares exactly what `--print-drift` reports.
- **`0956b1d..bce238a` touches only `docs/` (§8 #11).**

**13.2 Rulings**

- **Accepted: v2 R1–R11 as written.** That includes the architect's **stricter** wording for F6 and F8. The reviewer
  phrased those requirements as "production must/should". v2 states them as applying to PoC code now, which is
  consistent with R4 and with `security-guidelines:76`. This tightens the guidance and does not weaken it.
- **The Security Engineer's conditions F1 and F2 (MEDIUM) are met in v2**, and the LOW items F3–F6 and F8 are
  included. Record: `docs/artifacts/security-review-poc-security-shortcuts-v1.md`.
- **Priority: P2, dispatched immediately.** This is the user's decision of 2026-10-02. FU-1 is `T577`.
- **The wider rule is flagged to the user (§4 note).** R4–R6 make visible that a PoC must meet *every*
  `security-guidelines` rule, not only the Immutable Constraints: HTTPS, rate limiting, security headers and password
  hashing included. `security-guidelines` already requires this, so the change adds no new obligation. It does,
  however, make PoCs visibly heavier.
- **O1 is re-rated SECURITY:HIGH and is now its own task. It is no longer parked as P45.** By the user's decision of
  2026-10-02 it is scoped next at **P1**. That task declares `agent/poc-security-engineer`, which comes off `stable`
  (to `beta`) while the task is open. `rapid-prototyping:54` is batched with it.
