# Artifact: tracked-debt-register-v4.md

> Immutable once produced; revisions bump `<N>`.

Based on: `docs/artifacts/tracked-debt-register-v3.md` (398 ids; v3 stays the record for every id that was `fixed` or `obsolete` there, and for the text of every carried id); `docs/plans/plan-124-release-v9.md` (with its addenda of 2026-11-01); `docs/plans/plan-125-post-v9-follow-ups.md`; `docs/tasks/task-T713.md`; `docs/tasks/completed-tasks.md` (rows T700 to T712); `docs/checkpoints/checkpoint-040-release-v9.0.0.md` (sections 3 and 4); `docs/releases/v9.0.0.md` (`## RELEASE VERDICT`, Migration Guide M-1); the review and gate artifacts `security-review-t697-t699-debt-checkpoint-refresh-v1.md`, `release-v9-audit-v1.md` (T700), `security-review-t701-t703-wave1-v1.md`, `mcp-pin-audit-v9-v1.md` (T702), `security-review-t702-brave-reachability-v1.md`, `brave-audit-acceptance-v3.md`, `security-review-t712-brave-stdio-v1.md`, `release-rehearsal-t706-v1.md`, `qa-gate-release-v9-v1.md` (T707), `code-review-release-v9-v1.md` (T708), `security-review-release-v9-v1.md` (T709), `release-doc-independent-check-v9-v1.md`. Requirements and architecture artifacts: none apply (a debt register). Decision IDs referenced: ADR-010, ADR-007 (through SEC-T693-04), DEC-T681-1; no ADR is amended.

## Metadata

- **Producer**: tech-lead (read-only on source; the only file written is this artifact). **Task**: T713 (plan-125; the user's approval of 2026-11-01: "v4 + C go"). **Date**: 2026-11-01.
- **Tree read**: branch `docs/plan-125-post-v9` at `ef62fd50`, worktree `agent/tech-lead/T713`. CWSO repository not read: CWSO statuses repeat v3.
- **Review mode**: read-only. Closures cite a file and line read on `ef62fd50`, a completed-task row, a review artifact or the checkpoint. "Unchanged" means no plan-124 task, review or gate names the id and I did not re-check the code; anything not traced is **(unverified)**.
- **T714 (batch C) is in flight** and every item in it is treated as open here (SEC-T701-01 to -03, SEC-T689-04, -05, SEV-T690-02, -04).
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, the user's secret stores, the user's `.claude/settings*.json` and `.vscode/mcp.json`. No credential, token value or network address is written here.
- **Policy** (unchanged, the user 2026-10-23): "Track LOW items as debt, stop chasing (Recommended)". Status vocabulary and id prefixes as in v3. `TD-T713-*` are ids minted by this register. Decision ids (`D-T700-*`, `D-T710-1`) and user-action ids (`UA-*`) are recorded in sections 4 and 6 and are not counted as debt ids, as in v3; `D-T710-2` is debt (CHANGELOG order) and is counted.

## 1. Summary

v4 holds **443 ids**: the 398 of v3 and **45 new**. After v4: **303 fixed**, **45 accepted**, **6 obsolete**, **3 open**, **86 tracked-LOW**.

- **Open above LOW: none.** SEC-T662-01 (MEDIUM) is closed (T705 M-1, T709 hand check). The three open ids are K-20 (live checks), TD-T671-legacy (spot-check) and TD-T713-01 (the Release Gate Policy item 2 ruling).
- **Accepted at MEDIUM by the user**: SEC-T657-01/SEC-T658-01 (remainder), SEC-T660-01, SEC-T665-01, TD-T697-07 (decision "C"; re-decide by 2027-01-29, SEC-T699-04) and **SEC-T702-09** (Brave 2.1.4, acceptance v3, **until 2027-01-30 or the first Brave release above 2.1.4**). SEC-T676-02 is superseded by SEC-T702-09.
- **Nearest dates**: GitLab token renewal 2027-01-28; CWSO bearer renewal and TD-T697-07 re-decision 2027-01-29; Brave acceptance v3 end 2027-01-30; CWSO `paste` review 2027-01-31 (SEC-T696-06).

### 1.1 v3 ids by v3 status and status now

| v3 status | ids | now fixed | now accepted | now obsolete | now open | now tracked-LOW |
|---|---:|---:|---:|---:|---:|---:|
| open | 4 | 2 | 0 | 0 | 2 | 0 |
| tracked-LOW | 77 | 7 | 0 | 0 | 0 | 70 |
| accepted | 39 | 0 | 38 | 1 | 0 | 0 |
| fixed | 273 | 273 | 0 | 0 | 0 | 0 |
| obsolete | 5 | 0 | 0 | 5 | 0 | 0 |
| **all v3 ids** | **398** | **282** | **38** | **6** | **2** | **70** |

The 120 v3 ids that were open, tracked-LOW or accepted are each in section 2. One v3 `fixed` id, SEC-T686-03, is re-recorded in section 2.4 because the tag pipeline now gives the evidence v3 lacked; it stays `fixed`.

### 1.2 New ids by source (status now)

| Source | new | fixed | accepted | open | tracked-LOW |
|---|---:|---:|---:|---:|---:|
| `security-review-t697-t699-debt-checkpoint-refresh-v1.md` | 4 | 3 | 0 | 0 | 1 |
| `release-v9-audit-v1.md` (T700) | 4 | 4 | 0 | 0 | 0 |
| `security-review-t701-t703-wave1-v1.md` (T701, T703) | 6 | 0 | 0 | 0 | 6 |
| `security-review-t702-brave-reachability-v1.md` (T702) | 9 | 1 | 7 | 0 | 1 |
| `security-review-t712-brave-stdio-v1.md` (T712) | 6 | 5 | 0 | 0 | 1 |
| `qa-gate-release-v9-v1.md` (T707) | 3 | 2 | 0 | 0 | 1 |
| `code-review-release-v9-v1.md` (T708) | 7 | 2 | 0 | 0 | 5 |
| `security-review-release-v9-v1.md` (T709) | 4 | 4 | 0 | 0 | 0 |
| `docs/releases/v9.0.0.md` verdict (T710) | 1 | 0 | 0 | 0 | 1 |
| this register | 1 | 0 | 0 | 1 | 0 |
| **All new** | **45** | **21** | **7** | **1** | **16** |

`mcp-pin-audit-v9-v1.md`, `brave-audit-acceptance-v3.md`, `release-rehearsal-t706-v1.md` and `release-doc-independent-check-v9-v1.md` mint no finding id (T706 observation O-1 became D-T710-2).

## 2. v3 ids re-checked

Columns: Id | v3 | now | Batch (section 5) | Evidence or reason. "U" = user action or live check, no batch.

### 2.1 v3 `open` (4)

| Id | v3 | now | Batch | Evidence or reason |
|---|---|---|---|---|
| SEC-T662-01 | open (MEDIUM) | **fixed** | - | Second half by T703 (`verify-release-docs.py` pointer gate); first half by T705: `docs/releases/v9.0.0.md:72` M-1 with every element; content checked by hand in T709 (`security-review-release-v9-v1.md`); verdict justification records it closed. |
| TD-T697-08 | open (decision D-11) | **fixed** | - | Ruled LOW, no user decision needed (`security-review-t697-t699-...` § Grading; D-T700-4); the four doc places fixed by T701 (SEC-T699-01; grep: no "export the token" in `AGENTS.md`, `implementation/AGENTS.md`, `docs/wiki/mcp-servers.md`); release doc M-5/K-24 corrected in T710 (SEC-T709-01). |
| K-20 | open | open | U | Still not observed live (Copilot grants, Gemini denials, Pi lists, Opencode per-agent denies, VS Code behaviour of the two T690 servers); T700 K-20 "Still true; extend". A-7. |
| TD-T671-legacy | open | open | D | T700 K-8: "older parked remarks not re-read (TD-T671-legacy, unverified)". Owner orchestrator. |

### 2.2 v3 `tracked-LOW` (77)

| Id | v3 | now | Batch | Evidence or reason |
|---|---|---|---|---|
| TD-T671-P5 | tracked-LOW | tracked-LOW | A | T700 K-6 "Still true". |
| TD-T671-K5 | tracked-LOW | tracked-LOW | A | T700 K-5 "Still true" (`servers.yaml:198`). |
| SEC-011 | tracked-LOW | tracked-LOW | F | Unchanged. |
| SEC-T658-02 | tracked-LOW | tracked-LOW | U | Live checks not run (A-7). |
| RO621-N-3 | tracked-LOW | tracked-LOW | D | T700 K-8 "N-3 open". |
| TD-T671-P16 | tracked-LOW | tracked-LOW | D | Unchanged. |
| TD-T671-T538 | tracked-LOW | tracked-LOW | D | Unchanged. |
| TD-T671-T554 | tracked-LOW | tracked-LOW | D | Unchanged. |
| SEC-T663-02 | tracked-LOW | tracked-LOW | A | Unchanged. |
| SEC-T665-07 | tracked-LOW | tracked-LOW | C (not in T714) | T700 K-16 restates it (DEC-T681-1); reopening conditions as in v3. |
| SEC-T674-06 | tracked-LOW | tracked-LOW | F | Unchanged. |
| SEC-T675-08 | tracked-LOW | tracked-LOW | B | Unchanged. |
| SEC-T675-10 | tracked-LOW | tracked-LOW | B | Unchanged. |
| SEC-T676-14 | tracked-LOW | tracked-LOW | B | Unchanged. |
| SEC-T678-03 | tracked-LOW | **fixed** | - | `docs/releases/v9.0.0.md:76` (M-1, "A leftover `.cursor/` is frozen (SEC-T678-03)"); completed-task row T705. |
| SEC-T684-01 | tracked-LOW | tracked-LOW | A | Unchanged; T704 touched `install.sh` only in the Cursor notice (`f9739be5`). |
| SEC-T684-02 | tracked-LOW | tracked-LOW | A | Same. |
| SEC-T684-03 | tracked-LOW | tracked-LOW | A | Same. |
| SEC-T684-04 | tracked-LOW | tracked-LOW | A | Same. |
| SEC-T684-05 | tracked-LOW | tracked-LOW | A | Same. |
| SEC-T684-06 | tracked-LOW | tracked-LOW | A | Same. |
| SEC-T685-01 | tracked-LOW | tracked-LOW | B | Unchanged; T703 changed `verify-release-docs.py` but no review names it. |
| SEC-T685-02 | tracked-LOW | tracked-LOW | B | Same. |
| SEC-T685-03 | tracked-LOW | tracked-LOW | B | Same; coverage by CONTRIBUTING still **(unverified)**. |
| TD-T687-02 | tracked-LOW | tracked-LOW | D | Unchanged. |
| TD-T687-03 | tracked-LOW | tracked-LOW | D | Unchanged. |
| TD-T687-04 | tracked-LOW | tracked-LOW | D | Unchanged. |
| SEC-T677-01 | tracked-LOW | tracked-LOW | B | Unchanged. |
| SEC-T677-02 | tracked-LOW | tracked-LOW | B | Unchanged; whether T703's 11 tests pin `check_section_requirements` **(unverified)**. |
| SEC-T677-03 | tracked-LOW | tracked-LOW | A | Unchanged. |
| SEC-T686-06 | tracked-LOW | **fixed** | - | Tag pipeline 3014698085 (checkpoint-040 § 4; row T711): on runner 19.5.2 the two `git fetch` calls ran under the filtered environment and the job created the release. Residual: the clone method stays undetermined and the fail-closed path was not exercised; on another runner it is availability only (fail-closed). |
| SEC-T686-07 | tracked-LOW | tracked-LOW | B | Unchanged. |
| SEC-T686-08 | tracked-LOW | tracked-LOW | B | Unchanged. |
| SEC-T689-01 | tracked-LOW | **fixed** | - | T701; `implementation/PREREQUISITES.md:147` (`rm -f -- "$d/token"` before creation); T701 review "closed (residual SEC-T701-03)". |
| SEC-T689-02 | tracked-LOW | **fixed (in part)** | - | T701 added the lifetime qualifiers; T701 review "partly closed (rest is SEC-T701-01)". The rest is carried only by SEC-T701-01. |
| SEC-T689-03 | tracked-LOW | **fixed** | - | T701; T701 review "closed (residual SEC-T701-02)"; grep as for TD-T697-08. |
| SEC-T689-04 | tracked-LOW | tracked-LOW | C (T714) | In flight. |
| SEC-T689-05 | tracked-LOW | tracked-LOW | C (T714) | In flight. |
| SEC-T689-06 | tracked-LOW | **fixed** | - | T701; T701 review "closed". |
| SEV-T690-01 | tracked-LOW | tracked-LOW | A | Unchanged. |
| SEV-T690-02 | tracked-LOW | tracked-LOW | C (T714) | In flight; disclosed in release doc M-8 and K-25. |
| SEV-T690-03 | tracked-LOW | tracked-LOW | D | Unchanged. |
| SEV-T690-04 | tracked-LOW | tracked-LOW | C (T714) | In flight; disclosed in K-25. |
| SEV-T690-05 | tracked-LOW | tracked-LOW | A | Unchanged. |
| SEV-T690-06 | tracked-LOW | tracked-LOW | A | Disclosed in K-25; code unchanged. |
| SEV-T690-07 | tracked-LOW | **fixed** | - | D-T700-5 (a): release notes only; `docs/releases/v9.0.0.md` M-8 states the silent addition. No stderr note (by that decision). |
| SEC-T693-02 | tracked-LOW | tracked-LOW | D | Unchanged. |
| SEC-T693-03 | tracked-LOW | tracked-LOW | D | Unchanged. |
| SEC-T693-04 | tracked-LOW | tracked-LOW | D | Narrowed in practice: the v9.0.0 verdict carries an independent-check row with a commit (`a47d982d`); the template and command are unchanged **(unverified)**; a command change needs the user (ADR-007). |
| SEC-T693-05 | tracked-LOW | tracked-LOW | D | Unchanged. |
| SEC-T693-06 | tracked-LOW | tracked-LOW | D | Unchanged. |
| SEC-T693-07 | tracked-LOW | tracked-LOW | D | Residual accepted by ruling (v3 § 7.2); unchanged. |
| SEC-T693-08 | tracked-LOW | tracked-LOW | D | Unchanged. |
| SEC-T693-09 | tracked-LOW | tracked-LOW | D | Unchanged. |
| SEC-T694-04 | tracked-LOW | tracked-LOW | E | Unchanged (not re-read). |
| SEC-T694-05 | tracked-LOW | tracked-LOW | E | Same. |
| SEC-T694-06 | tracked-LOW | tracked-LOW | E | Same. |
| SEC-T694-07 | tracked-LOW | tracked-LOW | E | Same. |
| SEC-T694-08 | tracked-LOW | tracked-LOW | E | Same. |
| SEC-T694-09 | tracked-LOW | tracked-LOW | E | Same. |
| SEC-T694-10 | tracked-LOW | tracked-LOW | E | Same (A-15). |
| SEC-T694-11 | tracked-LOW | tracked-LOW | E | Same. |
| SEC-T694-12 | tracked-LOW | tracked-LOW | E | Same (A-11). |
| SEC-T695-03 | tracked-LOW | tracked-LOW | E | CWSO; not read. |
| SEC-T695-05 | tracked-LOW | tracked-LOW | E | Same. |
| SEC-T695-06 | tracked-LOW | tracked-LOW | E | Same (A-15). |
| SEC-T695-07 | tracked-LOW | tracked-LOW | E | Same. |
| SEC-T695-09 | tracked-LOW | tracked-LOW | E | Same. |
| SEC-T695-10 | tracked-LOW | tracked-LOW | E | Same. |
| SEC-T696-01 | tracked-LOW | tracked-LOW | E | Same. |
| SEC-T696-02 | tracked-LOW | tracked-LOW | E | Same. |
| SEC-T696-03 | tracked-LOW | tracked-LOW | E | Same. |
| SEC-T696-04 | tracked-LOW | tracked-LOW | E | Same. |
| SEC-T696-05 | tracked-LOW | tracked-LOW | E | Same. |
| SEC-T696-06 | tracked-LOW | tracked-LOW | E | Same; **review due 2027-01-31**. |
| SEC-T696-07 | tracked-LOW | tracked-LOW | E | Same. |
| TD-T697-03 | tracked-LOW | tracked-LOW | U | Live-check cases still open (A-2). |

### 2.3 v3 `accepted` (39)

All unchanged unless stated; basis as in v3 § 7.

| Id | v3 | now | Evidence or reason |
|---|---|---|---|
| K-2b | accepted | accepted | "D-6 a". |
| TD-T687-01 | accepted | accepted | "D2 b". |
| SEC-014 | accepted | accepted | "D-7 b". |
| RO621-N-1 | accepted | accepted | "D-5: Accept N-1. ..."; T700 K-8. |
| TD-T671-FN2 | accepted | accepted | "D-8 accept". |
| SEC-T657-01 / SEC-T658-01 | accepted (MEDIUM) | accepted | Unchanged (one id in v2 and v3; kept as one). |
| SEC-T660-01 | accepted (MEDIUM) | accepted | T700 K-16 restates "mitigated, not closed"; v9.0.0 shipped with it (v8.0.0 precedent). |
| SEC-T657-04 | accepted | accepted | Unchanged. |
| K-15 | accepted | accepted | Unchanged. |
| SEC-T660-05 | accepted | accepted | Unchanged. |
| SEC-T650-03 | accepted | accepted | Unchanged; the tag pipeline used `JOB-TOKEN`, `WIKI_TOKEN` only as a name in the command text (checkpoint-040 § 4). |
| T636-L6 | accepted | accepted | Unchanged. |
| T636-L7 | accepted | accepted | Unchanged. |
| TD-T671-K7 | accepted | accepted | Unchanged. |
| R-1 | accepted | accepted | Unchanged; who accepted it still **(unverified)**. |
| K-4 limits | accepted | accepted | Unchanged. |
| CR619-N5 | accepted | accepted | Unchanged. |
| K-10 | accepted | accepted | Unchanged; release doc K-10 restates it (with D-T710-2). |
| GOLDEN_VERSION_LABEL | accepted | accepted | Unchanged. |
| T638-L-1 | accepted | accepted | Unchanged. |
| K-13 | accepted | accepted | Unchanged; T700 K-13 "Changed" (the `github` container gone, Brave now SEC-T702-09). |
| K-19 | accepted | accepted | Unchanged. |
| RO621-N-4 | accepted | accepted | Unchanged. |
| RO621-N-5 | accepted | accepted | Unchanged. |
| RO621-O1b | accepted | accepted | Unchanged. |
| RO621-O5c | accepted | accepted | Unchanged. |
| TL-T649-09 | accepted | accepted | Unchanged. |
| SIGNOFF-CR649 | accepted | accepted | Unchanged. |
| K-14 | accepted | accepted | Unchanged. |
| K-21 | accepted | accepted | Unchanged; release doc K-21 and Rollback Plan corrected in T710 (TL-T708-02). |
| SEC-T662-05 | accepted | accepted | Unchanged. |
| SEC-T667-03 | accepted | accepted | Unchanged. |
| SEC-T667-06 | accepted | accepted | Unchanged. |
| SEC-T665-01 | accepted (MEDIUM) | accepted | Unchanged. |
| SEC-T676-02 | accepted (MEDIUM, to 2026-11-21) | **obsolete** | Superseded before expiry by `brave-audit-acceptance-v3.md` (seven advisories, the user's "Renew + force stdio (Recommended)"); carried by SEC-T702-09. |
| SEC-T686-05 | accepted | accepted | Unchanged. |
| TD-T697-01 | accepted | accepted | Unchanged. |
| TD-T697-02 | accepted | accepted | Unchanged. |
| TD-T697-07 | accepted (MEDIUM) | accepted | MEDIUM confirmed with conditions by `security-review-t697-t699-...` § Grading: re-decide by the bearer renewal (2027-01-29) or earlier if the LAN gains untrusted devices or the role widens; regrade to HIGH if the orchestrator role can make the CWSO server run code or read secrets (SEC-T699-04). |

### 2.4 One v3 `fixed` id re-recorded

| Id | v3 | now | Evidence |
|---|---|---|---|
| SEC-T686-03 | fixed (masking unverified) | fixed | Tag pipeline 3014698085 `release` log (95 lines): 0 job-token values, 0 credentialed `gitlab-ci-token:`, 0 `[MASKED]` (masking not exercised; the script never prints the token); checkpoint-040 § 4; T706 rehearsal: no git or apk child received the token. |

## 3. New ids

Columns: Id | Grade | Location | Short description | Status | Owner | Batch.

### 3.1 `security-review-t697-t699-debt-checkpoint-refresh-v1.md`

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| SEC-T699-01 | LOW | register v3; wiki, both `AGENTS.md` | TD-T697-08 shown open though mostly done; four doc places left. | fixed (T701; T701 review "closed") | - | - |
| SEC-T699-02 | LOW (A09) | checkpoint-039 § 9 | User-side plaintext secrets had no id. | fixed (UA-T699-1 to -3 assigned) | - | - |
| SEC-T699-03 | LOW | checkpoint-039 §§ 3, 9 | Token dates and transcript advice disagreed with v3. | fixed (in that branch) | - | - |
| SEC-T699-04 | LOW | register v3 TD-T697-07 | The acceptance had no review date or grade conditions. | tracked-LOW | orchestrator; the user decides | E (by 2027-01-29) |

### 3.2 `release-v9-audit-v1.md` (T700)

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| TL-T700-01 | LOW | `scripts/install.sh:1300` | `--force-prune-keys` said to exist only in the v8.0.0 installer. | fixed (T704 `f9739be5`; "Fix in T704 (Recommended)") | - | - |
| TL-T700-02 | LOW | M-1 | The merge-script recipe with the v8.0.0 Cursor file has side effects. | fixed (D-T700-3: hand editing in M-1) | - | - |
| TL-T700-03 | INFO | `install.sh:1304-1307` | Cursor notice only on `--update`/`--projections-only`. | fixed (`docs/releases/v9.0.0.md:75` states it; ADR-010 text immutable) | - | - |
| TL-T700-04 | INFO | ADR-010 | The version gate would fail on the immutable ADR. | fixed (D-T700-1; `scripts/check-version-consistency.py:22,68`) | - | - |

### 3.3 `security-review-t701-t703-wave1-v1.md` (T701, T703)

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| SEC-T701-01 | LOW | `PREREQUISITES.md:155-156`; T665 v2 record | Hibernation note missing; immutable T665 record not corrected. | tracked-LOW (in flight) | devops-engineer; the T665 v3 record by the orchestrator at closure | C (T714) |
| SEC-T701-02 | LOW | `PREREQUISITES.md:160,213` | Where an environment-mode `.env` may live is unstated. | tracked-LOW (in flight) | devops-engineer | C (T714) |
| SEC-T701-03 | LOW (info) | `PREREQUISITES.md:157` | gpg/keyring variant lacks the `rm -f --` step. | tracked-LOW (in flight) | devops-engineer | C (T714) |
| SEC-T703-01 | LOW | `verify-release-docs.py:129-131,341-347` | Anchor checks presence not content; fences and comments pass. | tracked-LOW (v9.0.0 condition met: hand check in T709) | devops-engineer | B |
| SEC-T703-02 | LOW | `verify-release-docs.py:127,314-321` | Pointers in another form pass vacuously. | tracked-LOW; due before the next release | devops-engineer | B |
| SEC-T703-03 | LOW | `verify-release-docs.py:333-338,357-358` | A pointer to a newer version is skipped silently. | tracked-LOW; same | devops-engineer | B |

### 3.4 `security-review-t702-brave-reachability-v1.md` (T702)

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| SEC-T702-01 | LOW | sdk 1.30.0 | GHSA-f897-62hf-6gxq, HTTP only; not reachable in stdio. | accepted (acceptance v3, to 2027-01-30) | devops-engineer | - |
| SEC-T702-02 | LOW | zod 4.3.6 | GHSA-mrhx-c7xc-m3w5; code path yes, harm at most a local crash. | accepted (same) | devops-engineer | - |
| SEC-T702-03 | LOW | sdk 1.30.0 | GHSA-46jr-4wx8-v453, HTTP only. | accepted (same) | devops-engineer | - |
| SEC-T702-04 | LOW | sdk 1.30.0 | GHSA-6qxp-vccf-f47h, OAuth client unused. | accepted (same) | devops-engineer | - |
| SEC-T702-05 | LOW | sdk 1.30.0 | GHSA-22jm-h49p-29qw, tasks API unused. | accepted (same) | devops-engineer | - |
| SEC-T702-06 | LOW | sdk 1.30.0 | GHSA-6prh-2h8m-c8cw and GHSA-rvq5-wwqv-78pq, SDK HTTP client unused. | accepted (same) | devops-engineer | - |
| SEC-T702-07 | (fix required) | `servers.yaml` `brave` | Env or `.env` could switch Brave to an HTTP listener. | fixed (T712: `servers.yaml:150` `--transport stdio`; pin test; UA-T712-1 observed) | - | - |
| SEC-T702-08 | LOW | upstream `src/BraveAPI/index.ts` | No timeout or size cap on Brave API fetches. | tracked-LOW (report upstream) | devops-engineer | B |
| SEC-T702-09 | MEDIUM | the pin 2.1.4 | Seven known advisories, no newer Brave release. | **accepted** ("Ship with it accepted (Recommended)"; acceptance v3) | devops-engineer; the user renews | - |

### 3.5 `security-review-t712-brave-stdio-v1.md` (T712)

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| SEC-T712-01 | LOW | acceptance v3:10 | Grading artifact not cited. | fixed (that branch) | - | - |
| SEC-T712-02 | LOW | acceptance v3 § Reasoning 1 | stdio override read, not run. | fixed (wording; UA-T712-1 observed, plan-124 addendum) | - | - |
| SEC-T712-03 | LOW | acceptance v3 | Prompt-injection caveat missing. | fixed (that branch) | - | - |
| SEC-T712-04 | LOW | acceptance v3 § Reasoning 4 | "Fixed versions not published" inaccurate. | fixed (that branch) | - | - |
| SEC-T712-05 | LOW | `test_audit_mcp_pins_hardening.py` | No tests for `via` cycles and odd `via` shapes. | tracked-LOW | devops-engineer | B |
| SEC-T712-06 | LOW | root install | Fix reaches installs only after refresh. | fixed (root refresh 22, `21045301`) | - | - |

### 3.6 `qa-gate-release-v9-v1.md` (T707)

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| QA-T707-01 | minor | `merge-mcp-json.py:112-128` | False "differs from the generated entry" note for Opencode `{env:NAME}`. | tracked-LOW (verdict: v9.0.1 or this register) | backend-developer | A |
| QA-T707-02 | minor | release doc M-4 | Placeholder change applies to generated entries only. | fixed (T710) | - | - |
| QA-T707-03 | minor | `check-main-develop-drift.py` | Grace hides a forgotten merge to main. | fixed for v9.0.0 (`releases_behind=0` after the tag, checkpoint-040 § 1); the gate's grace itself unchanged | - | - |

### 3.7 `code-review-release-v9-v1.md` (T708)

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| TL-T708-01 | major (procedural) | T711 brief vs CONTRIBUTING | Publish order conflict. | fixed (T711 brief corrected; B1 used, checkpoint-040 § 1) | - | - |
| TL-T708-02 | major (docs) | release doc Rollback Plan, K-21 | Contradicted by a rollback run. | fixed (T710; independent check PASS) | - | - |
| TL-T708-03 | minor | `install.sh:1300`; test pin | Two cases in one sentence. | tracked-LOW (release doc M-1 fixed in T710; installer text and test unchanged) | devops-engineer | A |
| TL-T708-04 | minor | `test_verify_release_docs.py:194-203` | Weaker test since the bump. | tracked-LOW | devops-engineer | B |
| TL-T708-05 | minor | `test_verify_release_docs.py:256-260` | Dead (always skipped) test. | tracked-LOW | devops-engineer | B |
| TL-T708-06 | minor | `publish-release.py:433-435,463-466` | 5 and 7 parameters (limit 4). | tracked-LOW | devops-engineer | B |
| TL-T708-07 | minor | `check-version-consistency.py:68-82` | Exclusion wider than its rationale (Proposed ADRs). | tracked-LOW (reviewer: acceptable as is) | devops-engineer | B |

### 3.8 `security-review-release-v9-v1.md` (T709)

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| SEC-T709-01 | LOW | release doc M-5, K-24 | D-11 shown open. | fixed (T710; independent check) | - | - |
| SEC-T709-02 | LOW | release doc M-5 | Lifting `modify` lacks the unrestricted-client caveat. | fixed (T710) | - | - |
| SEC-T709-03 | LOW | release doc M-4 | Pi: prefer the file variable. | fixed (T710) | - | - |
| SEC-T709-04 | LOW | release doc M-1 | Replacement `filesystem` launcher has advisories. | fixed (T710; D-T710-1, `docs/releases/v9.0.0.md:82`) | - | - |

### 3.9 `docs/releases/v9.0.0.md` verdict (T710)

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| D-T710-2 | LOW | release job `CHANGELOG.md` artifact | `## [Unreleased]` follows the new entry (T706 O-1; K-10). | tracked-LOW (verdict condition C-3) | devops-engineer | B |

### 3.10 This register

| Id | Grade | Location | Short description | Status | Owner | Batch |
|---|---|---|---|---|---|---|
| TD-T713-01 | process (ruling) | Release Gate Policy item 2 | The text says a MEDIUM is fixed before a release ships; v8.0.0 (SEC-T660-01) and v9.0.0 (SEC-T702-09) shipped one by the user's recorded decision (checkpoint-040 § 3). | open (needs a ruling, then the user) | orchestrator; solution-architect or security-engineer to rule | D |

## 4. Decisions since v3

### 4.1 The user's (words as recorded)

| Date | Words | Effect | Source |
|---|---|---|---|
| 2026-11-01 | plan-124 Q1 "Approve (Recommended)"; Q2 "Yes, in v9.0.0 (Recommended)"; Q3 "Decide after T702 (Recommended)"; Q4 "Yes, rehearse (Recommended)" | plan-124 run; token-docs batch T701 in v9.0.0 (v3 D-12 in part); D-T700-6 deferred; T706 | `plan-124-release-v9.md:5` |
| 2026-11-01 | "Grade, then renew (Recommended)", then "Renew + force stdio (Recommended)" | T702 grading; T712; acceptance v3; SEC-T702-07 fixed; SEC-T676-02 superseded | plan-124 addendum; `brave-audit-acceptance-v3.md` |
| 2026-11-01 | D-T700-1 "Exclude docs/decisions/ (Recommended)" | TL-T700-04 fixed (T704) | plan-124 addendum; row T704 |
| 2026-11-01 | D-T700-2 "Fix in T704 (Recommended)" | TL-T700-01 fixed (T704) | same |
| 2026-11-01 | "Ship with it accepted (Recommended)" | SEC-T702-09 accepted for v9.0.0 under Release Gate Policy item 2 | `docs/releases/v9.0.0.md` `## RELEASE VERDICT` |
| 2026-11-01 | The three publish steps, each approved at its moment (words not recorded in the read sources) | T711 | checkpoint-040 § 5 |
| 2026-11-01 | "v4 + C go" | T713 (this register), T714 | plan-125; `task-T713.md` |

The user's live check UA-T712-1 (2026-11-01) is a report, not a decision: `--transport stdio` overrides `BRAVE_MCP_TRANSPORT` (observed).

### 4.2 Other decisions (not the user's)

| Id | Decision | By | Effect |
|---|---|---|---|
| D-T700-3 | Cursor cleanup in M-1 by hand editing | release-manager (T705) | TL-T700-02 fixed |
| D-T700-4 | = v3 D-11 / TD-T697-08: ruled LOW, no user decision needed | security-engineer (T697-T699 review) | TD-T697-08 fixed; v3 D-11 settled |
| D-T700-5 | (a) release notes only for SEV-T690-07 | release-manager (T705) | SEV-T690-07 fixed |
| D-T700-6 | Brave HIGH findings: decided by the user after T702 (4.1) | user | superseded by 4.1 |
| D-T710-1 | `filesystem` entry: remove, do not replace | release-manager (T710) | SEC-T709-04 fixed |
| v3 D-13 | T688, T689, T690, T693 into the migration list | release-manager (T705) | done (release doc M-5, M-6, M-8, M-9) |

## 5. Open items by LOW batch (T714 = batch C, in flight)

| Batch | Scope | Ids | Size | Owner | Trigger |
|---|---|---|---:|---|---|
| A | Installer and generator | TD-T671-P5, TD-T671-K5, SEC-T663-02, SEC-T684-01 to -06, SEC-T677-03, SEV-T690-01, SEV-T690-05, SEV-T690-06, QA-T707-01, TL-T708-03 | 15 | devops-engineer; backend-developer (QA-T707-01) | next installer/generator task; QA-T707-01 by v9.0.1 |
| B | Release tooling and CI | SEC-T677-01, SEC-T677-02, SEC-T685-01 to -03, SEC-T675-08, SEC-T675-10, SEC-T676-14, SEC-T686-07, SEC-T686-08, SEC-T703-01 to -03, SEC-T712-05, SEC-T702-08, TL-T708-04 to -07, D-T710-2 | 20 | devops-engineer; technical-writer (SEC-T685-03) | before the next release (SEC-T703-02/-03, C-3 items) |
| C | Token docs and security runtime | SEC-T701-01 to -03, SEC-T689-04, SEC-T689-05, SEV-T690-02, SEV-T690-04 (T714); SEC-T665-07 (not in T714) | 8 | devops-engineer | T714 in flight |
| D | Knowledge text and rulings | RO621-N-3, TD-T671-P16, TD-T671-T538, TD-T671-T554, TD-T687-02 to -04, SEC-T693-02 to -09, SEV-T690-03, TD-T671-legacy (open), **TD-T713-01** (open: ruling on user-accepted MEDIUM findings under Release Gate Policy item 2) | 18 | technical-writer; solution-architect (TD-T687-*, TD-T713-01); orchestrator (TD-T671-legacy) | when the user chooses; TD-T713-01 before the next release |
| E | CWSO hardening | SEC-T694-04 to -12, SEC-T695-03, -05, -06, -07, -09, -10, SEC-T696-01 to -07, SEC-T699-04 | 23 | devops-engineer (CWSO); the user (SEC-T699-04) | `paste` review **2027-01-31** (SEC-T696-06); SEC-T699-04 by 2027-01-29 |
| F | PoC scanner | SEC-011, SEC-T674-06 | 2 | backend-developer; devops-engineer | next PoC-scanner change |
| U | Live checks (user) | SEC-T658-02, K-20 (open), TD-T697-03 | 3 | the user or an authorised live session | A-7, A-2 |

Total 89 = 86 tracked-LOW + 3 open. No open item is above LOW.

## 6. Accepted risks

| Item | Grade | Words, date | Until |
|---|---|---|---|
| SEC-T702-09 (with SEC-T702-01 to -06) | MEDIUM | "Renew + force stdio (Recommended)" (acceptance v3); "Ship with it accepted (Recommended)", 2026-11-01 | **2027-01-30 or the first Brave release above 2.1.4**: then `audit-mcp-pins.py audit --audit-level high` passes without these `--accept` entries, or a new acceptance version with the user |
| TD-T697-07 | MEDIUM | "C", 2026-10-31 | re-decide by 2027-01-29 (SEC-T699-04 conditions) |
| SEC-T657-01/SEC-T658-01, SEC-T660-01, SEC-T665-01 | MEDIUM | as in v3 § 7.1 | unchanged |
| Every other accepted id of section 2.3 | LOW/INFO | as in v3 §§ 7.1, 7.2 | unchanged |

## 7. User actions

| # | Action | State now | Due |
|---|---|---|---|
| A-2 | Remaining T665 live checks (TD-T697-03; design checks 4, 5) | open | - |
| A-5 | First real tag pipeline | **done** (3014698085; SEC-T686-03, -06 above) | - |
| A-6 | Brave acceptance expiry | **done** (renewed: acceptance v3) | successor: re-audit by **2027-01-30** or the next Brave release |
| A-7 | Live checks Gemini CLI, Opencode denials, VS Code T690 servers, Pi lists | open | - |
| A-9 | v9.0.0 migration items | **done** (release doc M-1 to M-12) | - |
| A-10, A-11, A-12, A-14, A-15 | As in v3 | unchanged (A-12, A-15 optional; A-14 reference) | - |
| A-13 | Renew the GitLab token and the CWSO bearer token | open; dates as recorded in checkpoint-039/-040 and the T697-T699 review (the user's token check; the 90-day mint of 2026-10-31), not re-read by me | GitLab **2027-01-28**; CWSO bearer **2027-01-29** (with the TD-T697-07 re-decision) |
| UA-T699-1 | Plaintext `.env` files of the user's other projects | open | - |
| UA-T699-2 | Plaintext JWT secret file on the CWSO server | open | - |
| UA-T699-3 | Stored Context7 CLI key (invalid; remove or replace) | open | - |
| UA-T712-1 | Brave `--transport stdio` live check | **done** 2026-11-01 (plan-124 addendum) | - |

UA-T699-1 to -3 fall under Immutable Security Constraint 6: user actions, never accepted risks.

## 8. Method, limits and validation

- Carried statuses: v3 rows plus every plan-124 review, gate row and checkpoint-040; code greps on `ef62fd50` where cited. CWSO not read. Items marked **(unverified)**: SEC-T677-02 (T703 tests), SEC-T685-03 (CONTRIBUTING coverage), SEC-T693-04 (template/command), R-1 (who accepted), A-13 dates (not re-read by me).
- SEC-T686-06 is closed on the observed success of the job; the orchestrator may reopen it if another runner is used.
- Validators run before commit: `python3 docs/tasks/validate-tasks.py`, `python3 -m unittest tests.functional.test_link_integrity`, `python3 -m unittest discover -s tests -p 'test_team_health*.py'`.

## 9. Review mode and references

- Read-only review; no source modified. Reviewed by: Tech Lead.
- Inputs: `tracked-debt-register-v3.md`; `plan-124-release-v9.md`; `plan-125-post-v9-follow-ups.md`; `checkpoint-040-release-v9.0.0.md`; `docs/releases/v9.0.0.md`; the artifacts listed under "Based on". Decision IDs: ADR-010, ADR-007, DEC-T681-1.
