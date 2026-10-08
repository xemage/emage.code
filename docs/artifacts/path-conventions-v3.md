# Artifact: path-conventions-v3.md

> Filename: `path-conventions-v3.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T595 (P2, judgment tier, decision only), second follow-up
- **Created**: 2026-10-08
- **Based on:**
  - `docs/artifacts/path-conventions-v2.md`: the decided edits P-1 to P-9 and R-1 to R-3, FU-P32-G, and observations
    O1–O6;
  - `docs/artifacts/path-conventions-v1.md`: the D5 records A-1, A-2, A-2′ and B-1, and the analysis;
  - the orchestrator's verification of v2, relayed on 2026-10-08:
    - all 11 fences apply exactly once to 9 files;
    - all 108 real plans match `^plan-[0-9]{3}-[a-z0-9.-]+\.md$`;
    - held-out isolation passes;
  - the orchestrator's finding of a missed site: `implementation/knowledge/skills/validation-gates/SKILL.md:92`;
  - the user's decisions of 2026-10-08, with the option labels verbatim:
    - **Q-P32a: "plan-<NNN>-<slug>.md (Recommended)"**, which is option 1 including the PoC track, with dots allowed in
      the slug;
    - **Q-P32b: "One, at docs/releases/ (Recommended)"**, which is option 1.
- **Supersedes**: `path-conventions-v2.md`. v1 and v2 are unchanged.
- **This document alone is the implementation input.** It carries every decided edit: P-1 to P-10 and R-1 to R-3.
  P-1 to P-9 and R-1 to R-3 are byte-identical to v2. P-10 is new.
- **Decision references**:
  - ADR-008 § Scope: "A question already settled by … a recorded user decision. That decision governs, and documents
    are amended to it."
  - ADR-007: P-4 and P-5 are command edits made on the user's decision.
  - ADR-007 §5: never relax a check.

## 0. Method and limits

- **Commit.** The orchestrator states the worktree is on `develop` `c152eb7` **(unverified: no shell)**. P-10's Before
  text comes from reading `validation-gates/SKILL.md` in full at that commit.
- **No shell.** Nothing was committed. Anchor uniqueness and counts come from reading and are **(unverified by grep)**.
  The orchestrator verified v2's eleven fences.
- **Golden.** I opened no golden file for this version. P-10's golden statement relies on
  `validate-workflow-gate-verdict-sources/brief.md`, which I read for v1 (lines 42–43, 59–63 and 184–186), and on the
  orchestrator's statement. **I never opened `tests/golden/held-out/`.**
- **Encoding.**
  - Characters: `§` is U+00A7, `—` is U+2014, `→` is U+2192, `›` is U+203A, `…` is U+2026.
  - Each four-backtick fence holds exactly one Before/After pair.
  - Apply each edit by its Before text, never by its line number.

## 1. Decisions (unchanged from v2)

| Question | Decision (verbatim label) | Meaning | Edits |
|---|---|---|---|
| Q-P32a | "plan-<NNN>-<slug>.md (Recommended)" | Every plan on either track is written to `docs/plans/plan-<ID>.md`. `<ID>` is a three-digit number, a hyphen, and a slug of lowercase letters, digits, hyphens and dots. It is defined once, in `plan-approve-execute` § File Location | P-1 to P-10 |
| Q-P32b | "One, at docs/releases/ (Recommended)" | A release has one release-notes document, `docs/releases/v<VERSION>.md` | R-1 to R-3 |

- **A-1:** no edit is needed. After P-4, `/new-feature` uses the orchestrator's path.
- **A-2:** settled by the user's decision.
- **A-2′:** parked as O1.
- **B-1:** settled by the user's decision.
- **Withdrawn, as in v2:** E-C1, E-C2, R-4, R-5, C-B2a, C-B2b, and the texts of the options not taken.
- **Covered by "one name everywhere":** P-10 follows from the same Q-P32a decision. `validation-gates:92` names the
  plan an input to the Architecture gate. Under option 1 it is the same plan document, so it takes the same name.

## 2. Edits for Q-P32a (apply verbatim)

**P-1 — `implementation/knowledge/skills/plan-approve-execute/SKILL.md:20–24`.** Anchor: the heading `## File Location`,
which occurs once in the file.

````
Before:
## File Location

```
docs/plans/plan-<feature-or-phase>.md
```

After:
## File Location

```
docs/plans/plan-<ID>.md
```

`<ID>` is the plan's three-digit number, a hyphen, and a short slug naming the feature or phase, written in lowercase letters, digits, hyphens and dots, for example `docs/plans/plan-042-rate-limiting.md`. A new plan takes the next number not yet used in `docs/plans/`. Every plan document a command or agent writes under this protocol uses this path.
````

**P-2 — `implementation/knowledge/skills/plan-approve-execute/SKILL.md:97`.** Anchor: the full line, which occurs once.

````
Before:
Please review the full plan at `docs/plans/plan-<name>.md`.

After:
Please review the full plan at `docs/plans/plan-<ID>.md`.
````

**P-3 — `implementation/knowledge/agents/orchestrator.md:23`.** Anchor: the full line, which occurs once. Line `:56` is
unchanged; it takes the same meaning by same-file coherence.

````
Before:
4. Write a plan document to `docs/plans/plan-<ID>.md` with:

After:
4. Write a plan document to `docs/plans/plan-<ID>.md` (`<ID>`: skill `plan-approve-execute` § File Location) with:
````

**P-4 — `implementation/knowledge/commands/new-feature.md:14`.** A command change, made on the user's decision. Anchor:
the full line, with three leading spaces, which occurs once.

````
Before:
   - Write to `docs/plans/feature-<slug>.md`

After:
   - Write to `docs/plans/plan-<ID>.md`, with `<ID>` as the `plan-approve-execute` skill § File Location defines it
````

**P-5 — `implementation/knowledge/commands/new-project.md:14`.** A command change, made on the user's decision. Anchor:
the full line, with three leading spaces, which occurs once.

````
Before:
   - Write the plan to `docs/plans/plan-<project-slug>.md`

After:
   - Write the plan to `docs/plans/plan-<ID>.md`, with `<ID>` as the `plan-approve-execute` skill § File Location defines it
````

**P-6 — `implementation/knowledge/skills/project-planning/SKILL.md:163–168`.** Anchor: the paragraph beginning `Plan
documents are versioned artifacts stored under`, which occurs once.

````
Before:
Plan documents are versioned artifacts stored under `docs/plans/`:

```
docs/plans/project-plan-v1.md
docs/plans/project-plan-v2.md
```

After:
Plan documents are versioned artifacts stored under `docs/plans/`, at the path skill `plan-approve-execute` § File Location defines:

```
docs/plans/plan-<ID>.md
```

Each version is its own plan document at that path, with its own `<ID>`; the `## Version` and `## Changes from v{N-1}` fields below record which version it is. A superseded version is marked as `plan-approve-execute` § Guidelines describes.
````

**P-7 — `implementation/knowledge/agents/poc-orchestrator.md:25`.**
- This edit fills the slot P11 left open.
- `/new-poc` imports this line, so the edit reaches a command clause. It rests on the user's decision.
- Anchor: the full line, which occurs once.
- The golden-quoted words "Write a lightweight plan in `docs/plans/plan-<ID>.md`" survive unchanged.

````
Before:
3. Write a lightweight plan in `docs/plans/plan-<ID>.md`:

After:
3. Write a lightweight plan in `docs/plans/plan-<ID>.md` (`<ID>`: skill `plan-approve-execute` § File Location):
````

**P-8 and P-9 apply the same Before/After pair to two files:**
- P-8: `implementation/docs/plans/_template.md:3`, the shipped template;
- P-9: `docs/plans/_template.md:3`, this repository's copy.

Neither file is a knowledge document. The anchor is the full line, which occurs once in each file. Line `:61`
("revisions create `plan-<slug>-v2.md`") is not touched; it belongs to O1.

````
Before:
> Filename convention: `plan-<slug>.md` (e.g. `plan-payment-feature.md`).

After:
> Filename convention: `plan-<ID>.md`, with `<ID>` as the `plan-approve-execute` skill § File Location defines it (e.g. `plan-042-payment-feature.md`).
````

**P-10 (new in v3) — `implementation/knowledge/skills/validation-gates/SKILL.md:92`, in § Gate Input Requirements ›
Architecture Gate.**
- Anchor: the full line `- Plan document (`docs/plans/plan-<feature>.md`)`.
- It occurs once, by reading the whole file. `plan-<feature>` occurs nowhere else in the file.
- It is the orchestrator's sixth path variant.

````
Before:
- Plan document (`docs/plans/plan-<feature>.md`)

After:
- Plan document (`docs/plans/plan-<ID>.md`; `<ID>`: skill `plan-approve-execute` § File Location)
````

## 3. Edits for Q-P32b (apply verbatim)

**R-1 — `implementation/knowledge/skills/release-workflow/SKILL.md:56`.** Anchor: the full line, which occurs once.

````
Before:
5. **Create the release artifact** at `docs/artifacts/release-notes-v<VERSION>.md`.

After:
5. **Write the release notes** to `docs/releases/v<VERSION>.md` (§ 4).
````

**R-2 — `implementation/knowledge/skills/release-workflow/SKILL.md:129–132`.** Anchor: the block beginning with the
heading `### 4. Create Release Artifact`, which occurs once.

````
Before:
### 4. Create Release Artifact

```markdown
# Release Notes — v<VERSION>

After:
### 4. Create Release Artifact

The release notes are one document per release, `docs/releases/v<VERSION>.md`: the file the `orchestrator` agent § Release Workflow Preflights publishes, and the release notes document into which `/prepare-release` step 7 writes the `## RELEASE VERDICT` section. Add the sections below, from `## Summary` on, to that document. When the release is prepared with `/prepare-release`, that command's steps govern the document, and these sections accompany them. The `Release` line under `## Gate Verdicts` carries the same value as the `**Status**` of the `## RELEASE VERDICT` section.

```markdown
# Release Notes — v<VERSION>
````

**R-3 — `implementation/knowledge/skills/release-workflow/SKILL.md:160`.** Anchor: the full line, which occurs once.

````
Before:
File location: `docs/artifacts/release-notes-v<VERSION>.md`

After:
File location: `docs/releases/v<VERSION>.md`, one document per release (above).
````

**Totals.** There are 12 fences and 10 files:

| Count | Breakdown |
|---|---|
| 12 fences | v2's eleven, plus P-10 |
| 10 files | v2's nine, plus `validation-gates` |
| 13 applications | P-8/P-9's fence is applied twice |

**Mechanics for the implementing task.**
1. Apply each edit by its Before text. Each Before must match exactly once at dispatch.
2. Run `node implementation/scripts/sync.mjs --root implementation`, then the same command with `--check`.
3. Run `python3 implementation/scripts/generate-registry.py`, then the same command with `--check`.
4. Declare root drift exactly as `--print-drift` reports it.
5. Confirm all three of these:
   - `scripts/scorecard.py --check` matches the current baseline;
   - `check-maturity.py --root implementation` reports 0 failing;
   - `python3 docs/tasks/validate-tasks.py` passes.
6. Confirm these are byte-unchanged:
   - `AGENTS.md` and every instruction;
   - the commands `/plan`, `/batch`, `/new-poc` and `/prepare-release`;
   - every script, `docs/releases/_template.md` and `tests/golden/**`.

## 4. Change log against v2

1. **P-10 added** (`validation-gates:92`). The orchestrator found it after v2. The user's Q-P32a decision covers it.
2. **Every v2 edit is carried over byte-identical:** P-1 to P-9 and R-1 to R-3, with the same fences, Before texts and
   After texts. Only the prose around them is restated.
3. **FU-P32-G gains an optional item:** re-copy the frozen `validation-gates` fixture in
   `validate-workflow-gate-verdict-sources` (§6).
4. **Hit counts gain rows 35–39** for `validation-gates` (§7). Rows 1–34 are unchanged from v2.
5. **Totals:** 12 fences and 10 files, up from 11 fences and 9 files.
6. **Real plans:** the orchestrator verified that all 108 real plans match `^plan-[0-9]{3}-[a-z0-9.-]+\.md$`. This
   closes v2 §9 item 3.

## 5. Per-edit statements

**v2's statements carry over unchanged for P-1 to P-9 and R-1 to R-3** (v2 §5). In summary:

- **Upward edits:** none. No edit touches `AGENTS.md` or a stable instruction.
- **Command changes:** P-4 and P-5 are the only command edits, and both are made on the user's decision. P-7 reaches
  `/new-poc`'s imported clause, also on the user's decision.
- **Checks:** no edit relaxes a check.
- **Security:** no edit has a security effect.
- **Golden quotes:** two go stale, under P-4 (`new-feature-plan-doc-compliant/brief.md:11–13`) and P-5
  (`new-project-plan-doc-and-lifecycle-states/brief.md:16`, and its `expect.py:6` docstring).
- **Golden fixtures and results:** no edit changes either.

**P-10:**

| Aspect | Statement |
|---|---|
| **Upward?** | **No.** `validation-gates` is a `stable` *skill*, not a stable instruction, so it is not tier 1 (ADR-008 D1). It is amended to the user's recorded decision (ADR-008 § Scope). Maturity is not relied on. |
| **Relaxes a check?** | **No.** The input stays required at the Architecture gate, and the path keeps one form. The Rails Inputs (`:193`) still require "that gate type's required inputs per the "Gate Input Requirements" table above", and nothing in that table is removed. |
| **Golden** | **Quote: none. Fixture: lags. Result: unchanged.** `validate-workflow-gate-verdict-sources` holds a frozen, byte-identical copy of this skill at `fixture/implementation/knowledge/skills/validation-gates/SKILL.md`. Its `check()` reads only § Gate Types, the Verdict Format's first `**Gate:**` line, and "Every gate MUST produce a verdict" (`brief.md:184–186`). It does not read § Gate Input Requirements. After P-10 the copy is no longer byte-identical to its source, and the brief's Provenance list of later source changes (`brief.md:178–186`) lacks this one. Re-copying is optional (FU-P32-G). The case's `brief.md` quotes `/validate-workflow` step 5, which names `validation-gates` § Gate Types and § Verdict Format, not § Gate Input Requirements. So no quote changes. |
| **Non-golden tests** | The orchestrator's v2 search covered v2's changed strings. **Whether any non-golden test asserts `plan-<feature>` in `validation-gates` is unverified.** `test_validation_gates_skill_contract` is reported to assert tokens, markers and the executor mapping (`conditional-pass-semantics-v4.md` §16.1); none of those is this line. |
| **Security** | **None.** It changes a path in an input list. It changes no verdict rule, security criterion or executor. |

## 6. FU-P32-G — golden realignment (separate follow-up; **not yet authorized**)

**Unchanged from v2 §6**, plus one optional item. The follow-up needs two things the user has **not yet** authorized:
- a file-scoped `protected-paths-v1.md` §5 grant;
- a user-authorized **v18** baseline.

It predicts no change to any case's status.

**Required (as in v2 §6.1):**

| Case | Changes |
|---|---|
| `tests/golden/open/new-feature-plan-doc-compliant/` | `expect.py:25`: glob `feature-*.md` → `plan-*.md`. `expect.py:4–6`: docstring path. Fixture renamed to `plan-001-audit-log-export.md`. `brief.md:11–13`: quote. `brief.md:16–17`: pass condition. `brief.md:20–26`: provenance. `case.yaml`: unchanged. |
| `tests/golden/open/new-project-plan-doc-and-lifecycle-states/` | `brief.md:16`: quote. `expect.py:6`: docstring quote. `expect.py:25`: comment. Descriptive text at `brief.md:72, :87, :95–98`. Optional fixture rename to `plan-001-taskflow.md`. `PLAN_NAME_RE` (`expect.py:26`): unchanged by default; any change is a separate check decision. |

**Optional (as in v2 §6.2):**
- `tests/golden/open/new-poc-plan-hypothesis-format/`: rename the fixture to `plan-001-local-note-search.md`, and update
  `brief.md:59–63, :96–98`.
- `tests/golden/open/plan-required-sections-compliant/brief.md:12, :17`: this is O4.

**Optional (new in v3):**
- `tests/golden/open/validate-workflow-gate-verdict-sources/`:
  - re-copy `fixture/implementation/knowledge/skills/validation-gates/SKILL.md` from source after P-10 merges, and
    confirm with `cmp`;
  - add one Provenance bullet under `brief.md:178–186`, for example "§ Gate Input Requirements › Architecture Gate:
    the plan document's path (`T595`/P32), not read by `check()`".
- If it is not re-copied, the fixture just lags. The result is `True` either way. Earlier re-copies (`T583`, `T592`)
  set the precedent.

## 7. Hit counts (decided edits only)

- **Scope:** case-sensitive, fixed-string, per file, after every decided edit to that file.
- **Lines** = `grep -cF`; **occurrences** = `grep -oF … | wc -l`.
- **Before:** counts are at `c152eb7`, by reading **(unverified by grep)**.
- **0 / 0 in the After column:** the old wording must be gone.
- **Rows 1–34:** unchanged from v2.

| # | File | Phrase | Before (lines / occ.) | After | Edit |
|---|---|---|---|---|---|
| 1 | `skills/plan-approve-execute/SKILL.md` | `plan-<feature-or-phase>` | 1 / 1 | **0 / 0** | P-1 |
| 2 | same | `plan-<name>` | 1 / 1 | **0 / 0** | P-2 |
| 3 | same | `docs/plans/plan-<ID>.md` | 0 / 0 | 2 / 2 | P-1, P-2 |
| 4 | same | `plan-042-rate-limiting.md` | 0 / 0 | 1 / 1 | P-1 |
| 5 | same | `hyphens and dots` | 0 / 0 | 1 / 1 | P-1 |
| 6 | same | `kebab-case` | 0 / 0 | 0 / 0 | P-1 (v1 wording not used) |
| 7 | same | `## File Location` | 1 / 1 | 1 / 1 | anchor survives |
| 8 | `agents/orchestrator.md` | `docs/plans/plan-<ID>.md` | 2 / 2 (`:23`, `:56`) | 2 / 2 | P-3 |
| 9 | same | `§ File Location` | 0 / 0 | 1 / 1 | P-3 |
| 10 | `commands/new-feature.md` | `feature-<slug>` | 1 / 1 | **0 / 0** | P-4 |
| 11 | same | `docs/plans/plan-<ID>.md` | 0 / 0 | 1 / 1 | P-4 |
| 12 | same | `plan-approve-execute` | 1 / 1 (`:16`) | 2 / 2 | P-4 |
| 13 | same | `§ File Location` | 0 / 0 | 1 / 1 | P-4 |
| 14 | `commands/new-project.md` | `plan-<project-slug>` | 1 / 1 | **0 / 0** | P-5 |
| 15 | same | `docs/plans/plan-<ID>.md` | 0 / 0 | 1 / 1 | P-5 |
| 16 | same | `plan-approve-execute` | 1 / 1 (`:16`) | 2 / 2 | P-5 |
| 17 | same | `§ File Location` | 0 / 0 | 1 / 1 | P-5 |
| 18 | `skills/project-planning/SKILL.md` | `project-plan-v` | 2 / 2 | **0 / 0** | P-6 |
| 19 | same | `docs/plans/plan-<ID>.md` | 0 / 0 | 1 / 1 | P-6 |
| 20 | same | `plan-approve-execute` | 2 / 2 (`:153`, `:156`) | 4 / 4 | P-6 |
| 21 | same | `§ File Location` | 0 / 0 | 1 / 1 | P-6 |
| 22 | `agents/poc-orchestrator.md` | `Write a lightweight plan in `docs/plans/plan-<ID>.md`` | 1 / 1 | 1 / 1 | P-7 (golden quote survives) |
| 23 | same | `plan-approve-execute` | 0 / 0 | 1 / 1 | P-7 |
| 24 | same | `§ File Location` | 0 / 0 | 1 / 1 | P-7 |
| 25 | each `_template.md` (P-8, P-9) | `plan-<slug>.md` | 1 / 1 | **0 / 0** | P-8 / P-9 |
| 26 | each `_template.md` | `plan-<slug>` | 2 / 2 | 1 / 1 (`:61`) | P-8 / P-9 |
| 27 | each `_template.md` | `plan-<ID>.md` | 0 / 0 | 1 / 1 | P-8 / P-9 |
| 28 | each `_template.md` | `plan-042-payment-feature.md` | 0 / 0 | 1 / 1 | P-8 / P-9 |
| 29 | `skills/release-workflow/SKILL.md` | `docs/artifacts/release-notes-v<VERSION>.md` | 2 / 2 (`:56`, `:160`) | **0 / 0** | R-1, R-3 |
| 30 | same | `Create the release artifact` | 1 / 1 (`:56`) | **0 / 0** | R-1 (the hotfix line `:188` reads "Create release artifact" and is untouched) |
| 31 | same | `docs/releases/v<VERSION>.md` | 0 / 0 | 3 / 3 | R-1, R-2, R-3 |
| 32 | same | `/prepare-release` | 0 / 0 | **1 / 2** (two on R-2's line) | R-2 |
| 33 | same | `## RELEASE VERDICT` | 0 / 0 | 1 / 1 | R-2 |
| 34 | same | `### 4. Create Release Artifact` | 1 / 1 | 1 / 1 | anchor survives |
| 35 | `skills/validation-gates/SKILL.md` | `plan-<feature>` | 1 / 1 (`:92`) | **0 / 0** | P-10 |
| 36 | same | `docs/plans/plan-<ID>.md` | 0 / 0 | 1 / 1 | P-10 |
| 37 | same | `plan-approve-execute` | 0 / 0 | 1 / 1 | P-10 |
| 38 | same | `§ File Location` | 0 / 0 | 1 / 1 | P-10 |
| 39 | same | `- Plan document (` | 1 / 1 | 1 / 1 | anchor line survives |

Row 35 is a full fixed string and cannot match `plan-<feature-or-phase>`, which does not occur in this file anyway.

## 8. Observations to park (unchanged from v2 §8)

- **O1.** Version suffixes on plan file names, against `coding-standards:66–83`.
  - Within tier 1 the same table conflicts with `AGENTS.md:27` (checkpoint naming) and `AGENTS.md:33` (decision
    naming).
  - The templates' `:61` revision rule conflicts with `plan-approve-execute:182`.
- **O2.** `/new-project:43` and `:51` conflict with `AGENTS.md:27` and `:22`.
- **O3.** Release-version-keyed files under `docs/artifacts/`. Moot under the decided option.
- **O4.** `plan-required-sections-compliant/brief.md:12, :17` describe a stale path. This is optional in FU-P32-G.
- **O5.** `/new-feature:25`, "Have the Scrum Master create tasks", conflicts with `AGENTS.md:18`.
- **O6.** CI generates a third release-notes file, `release-notes.md`, at the root (`publish-release.py:210–211`;
  `.gitlab-ci.yml:206`).

## 9. Still unverified

1. The worktree commit `c152eb7`.
2. P-10's anchor uniqueness and rows 35–39, both established by reading.
3. That no command or other knowledge file carries a further plan-path variant. This rests on the orchestrator's
   search, which found only the sites edited here.
4. That no non-golden test asserts `plan-<feature>` in `validation-gates`.
5. Whether a `brief.md`-only edit moves the `tests_golden` digest. This affects FU-P32-G's prerequisites.

## 10. Summary

| Item | Subject | Settled by | Outcome | Edits |
|---|---|---|---|---|
| A-1 | Plan path under `/new-feature` | The user's decision | No conflict remains after P-4; E-C1 and E-C2 are withdrawn | none |
| A-2 | `<ID>`; plan path on both tracks; every site naming it | The user's decision: "plan-<NNN>-<slug>.md (Recommended)" | `docs/plans/plan-<ID>.md`. `<ID>` = three-digit number, a hyphen, and a slug of lowercase letters, digits, hyphens and dots. Defined once, in `plan-approve-execute` § File Location | P-1 to P-10 (P-10 new) |
| A-2′ | Version suffixes on plan file names | — | Parked as O1 | none |
| B-1 | Release-notes path; one document or two | The user's decision: "One, at docs/releases/ (Recommended)" | One document, `docs/releases/v<VERSION>.md` | R-1 to R-3 |
| FU-P32-G | Golden realignment | Needs a grant and a user-authorized v18 (**not yet authorized**) | Two required cases. Three optional items (v3 adds the `validate-workflow-gate-verdict-sources` re-copy). No status transitions | §6 |

- **Upward:** no edit is upward, and none relaxes a check. P-4 and P-5 are command edits made on the user's decision.
  P-7 reaches `/new-poc`'s import on the same basis. P-10 amends a stable skill, not tier 1.
- **Security:** none.
- **Golden:** no edit changes a fixture or a result. Two quotes go stale (P-4, P-5). One frozen fixture copy lags
  (P-10). FU-P32-G covers all three.
- **Blockers:** none.
