# Artifact: path-conventions-v2.md

> Filename: `path-conventions-v2.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T595 (P2, judgment tier, decision only), follow-up after the user's decisions
- **Created**: 2026-10-08
- **Based on:**
  - `docs/artifacts/path-conventions-v1.md` (the D5 records A-1, A-2, A-2′ and B-1, and the held edits; unchanged by
    this version);
  - the orchestrator's verification of v1 and its two corrections, relayed on 2026-10-08;
  - the user's decisions of 2026-10-08, with the option labels verbatim:
    - **Q-P32a: "plan-<NNN>-<slug>.md (Recommended)"**. This is v1 option 1, including the PoC track (P-7 included),
      with dots allowed in the slug.
    - **Q-P32b: "One, at docs/releases/ (Recommended)"**. This is v1 option 1 (R-1, R-2, R-3).
  - `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted) and
    `docs/decisions/ADR-007-command-contract-authority.md` (Accepted).
- **Supersedes**: `path-conventions-v1.md`. That file is unchanged. Its D5 records, analysis and observations stand,
  except where §4 of this document says otherwise.
- **Decision references**:
  - ADR-008 § Scope: "A question already settled by an accepted ADR or a recorded user decision. That decision governs,
    and documents are amended to it."
  - ADR-007: a command clause changes only on branch 1 or by user decision. P-4, P-5 and P-7's reach into `/new-poc`
    rest on the user's decision.
  - ADR-007 §5: never relax a check.
  - P11 is not reopened: its form `plan-<ID>.md` stays, and only the slot it left open is filled.

## 0. Method and limits

- **Commit.** The orchestrator states the worktree is on `develop` `c152eb7` **(unverified: no shell)**. Every Before
  text below was re-read there, and line numbers are at that commit.
- **No shell.** I ran no `grep`, `git` or test, and committed nothing. Hit counts and anchor uniqueness come from
  reading whole files and are **(unverified by grep)**.
- **Verified by the orchestrator after v1:**
  - held-out isolation;
  - 64 + 4 quotes;
  - that no `docs/artifacts/release-notes-v*.md` exists;
  - the `docs/releases/` paths in `scripts/verify-release-docs.py:25, :38, :49` and `scripts/publish-release.py:103–104`;
  - that no non-golden test asserts any changed string.

  This closes v1 §9 items 4 and 6.
- **Golden.** For this version I read only `tests/golden/open/new-project-plan-doc-and-lifecycle-states/{brief.md,expect.py}`
  and the first lines of its fixture plan, which is `fixture/docs/plans/plan-taskflow.md`. **I never opened
  `tests/golden/held-out/`.** I name no golden case that lacks a `tests/golden/open/` directory.
- **Encoding.**
  - `§` is U+00A7, `—` is U+2014, `→` is U+2192, `›` is U+203A, `…` is U+2026.
  - Each four-backtick fence holds exactly one Before/After pair.
  - Apply each edit by its Before text, never by its line number.

## 1. The user's decisions and what follows from them

| Question | Decision (verbatim label) | Meaning | Edits to apply |
|---|---|---|---|
| Q-P32a | "plan-<NNN>-<slug>.md (Recommended)" | Every production plan, and every PoC plan, is written to `docs/plans/plan-<ID>.md`. `<ID>` is a three-digit number, a hyphen, and a slug of lowercase letters, digits, hyphens and dots. It is defined once, in `plan-approve-execute` § File Location | P-1 to P-9 (§2) |
| Q-P32b | "One, at docs/releases/ (Recommended)" | A release has one release-notes document, `docs/releases/v<VERSION>.md`. `release-workflow` is amended to that path | R-1 to R-3 (§3) |

**Consequences for the v1 records.**

- **A-1 (Step C, `/new-feature`): no edit is needed.**
  - P-4 changes `/new-feature:14` to `docs/plans/plan-<ID>.md` by the user's decision. That is the orchestrator's own
    path (`orchestrator.md:23, :56`) and the skill's (P-1).
  - With that change, Step A holds and the conflict is gone. E-C1 and E-C2 are withdrawn. The Step C ruling stays on
    record in v1 as the analysis of the clauses before the decision.
- **A-2 (Step E): settled by the user's decision (ADR-008 § Scope).**
  - `<ID>` is defined.
  - `/new-project` (P-5) and `project-planning` (P-6) move to the decided path.
  - `plan-approve-execute` (P-1, P-2) carries the definition, and the orchestrator (P-3) and `poc-orchestrator` (P-7)
    cite it.
  - `/plan`, `/batch` and the text of `/new-poc` are unchanged. Their `plan-<ID>.md` now resolves through their
    executing agents, which is a slot filled (ADR-008 D4), not a command edit. `/new-poc` imports P-7's line.
- **A-2′ (version suffix, against `coding-standards`): unchanged.** It remains parked as O1 (§8). No decided edit adds
  or removes a version suffix.
- **B-1 (Step A): the convention is decided.** One document at `docs/releases/v<VERSION>.md`. Only the skill changes.
  No command, agent, instruction, template or script changes.
- **Not taken:**
  - Q-P32a options 2–4 and Q-P32b options 2–4.
  - Their edits are withdrawn: E-C1, E-C2, the option-2 and option-4 texts of P-1, P-2 and P-8/P-9, R-4, R-5, C-B2a,
    C-B2b and the option-2 script specifications.

## 2. Final edits for Q-P32a (apply verbatim)

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

**P-3 — `implementation/knowledge/agents/orchestrator.md:23`.** Anchor: the full line, which occurs once. `:56` keeps
`plan-<ID>.md` unchanged; it takes the same meaning by same-file coherence.

````
Before:
4. Write a plan document to `docs/plans/plan-<ID>.md` with:

After:
4. Write a plan document to `docs/plans/plan-<ID>.md` (`<ID>`: skill `plan-approve-execute` § File Location) with:
````

**P-4 — `implementation/knowledge/commands/new-feature.md:14`.** This is a command change, made on the user's decision.
Anchor: the full line, with three leading spaces, which occurs once.

````
Before:
   - Write to `docs/plans/feature-<slug>.md`

After:
   - Write to `docs/plans/plan-<ID>.md`, with `<ID>` as the `plan-approve-execute` skill § File Location defines it
````

**P-5 — `implementation/knowledge/commands/new-project.md:14`.** This is a command change, made on the user's decision.
Anchor: the full line, with three leading spaces, which occurs once.

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

**P-7 — `implementation/knowledge/agents/poc-orchestrator.md:25`.** This edit fills the slot P11 left open. `/new-poc`
imports this line, so the edit reaches a command clause; it rests on the user's decision. Anchor: the full line, which
occurs once. The golden-quoted words "Write a lightweight plan in `docs/plans/plan-<ID>.md`" survive unchanged.

````
Before:
3. Write a lightweight plan in `docs/plans/plan-<ID>.md`:

After:
3. Write a lightweight plan in `docs/plans/plan-<ID>.md` (`<ID>`: skill `plan-approve-execute` § File Location):
````

**P-8 and P-9 — the same Before/After pair, applied to two files:**
- P-8: `implementation/docs/plans/_template.md:3`, the shipped template;
- P-9: `docs/plans/_template.md:3`, this repository's copy.

Neither file is a knowledge document. Anchor: the full line, which occurs once in each file. `:61` ("revisions create
`plan-<slug>-v2.md`") is not touched; it belongs to O1.

````
Before:
> Filename convention: `plan-<slug>.md` (e.g. `plan-payment-feature.md`).

After:
> Filename convention: `plan-<ID>.md`, with `<ID>` as the `plan-approve-execute` skill § File Location defines it (e.g. `plan-042-payment-feature.md`).
````

**Real plans.** No real plan is renamed. The orchestrator surveyed the 108 real plans: six have dots in the slug, for
example `plan-024-release-v6.7.0.md` and `plan-010-t235-phase3.3-real-harness-wiring.md`, and P-1's revised wording
admits them. That every real plan conforms to P-1 rests on that survey **(not re-verified by me)**.

## 3. Final edits for Q-P32b (apply verbatim)

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

**Mechanics for the implementing task.**
1. Apply each edit by its Before text. Each Before must match exactly once at dispatch.
2. Run `node implementation/scripts/sync.mjs --root implementation` and
   `python3 implementation/scripts/generate-registry.py`, each followed by `--check`.
3. Declare root drift exactly as `--print-drift` reports it.
4. Confirm all of the following:
   - `scripts/scorecard.py --check` matches the current baseline (FU-P32-G does not land here);
   - `check-maturity.py --root implementation` reports 0 failing;
   - `python3 docs/tasks/validate-tasks.py` passes.
5. Confirm these are byte-unchanged: `AGENTS.md`, every instruction, `/plan`, `/batch`, `/new-poc`, `/prepare-release`,
   every script, `docs/releases/_template.md` and `tests/golden/**`.

## 4. Change log against v1

1. **Decisions recorded (§1).** Q-P32a is option 1 including the PoC track. Q-P32b is option 1. All other options and
   their edits are withdrawn: E-C1, E-C2, R-4, R-5, C-B2a, C-B2b, the option-2 and option-4 texts, and the option-2
   script specifications.
2. **P-1 slug wording.**
   - v1: "a short kebab-case slug naming the feature or phase".
   - v2: "a short slug naming the feature or phase, written in lowercase letters, digits, hyphens and dots".
   - The example `plan-042-rate-limiting.md` is kept.
   - Reason: six real plans have dots in the slug, so v1's wording would have made them non-conforming (orchestrator
     correction 1).
3. **Golden coupling for `/new-project` computed.** This closes v1 §6.2 item 2. `new-project-plan-doc-and-lifecycle-states`
   quotes `/new-project` step 1. P-5 makes that quote stale and leaves the result unchanged (§5). This was orchestrator
   correction 2.
4. **FU-P32-G defined (§6).** It is the golden realignment, kept separate from the knowledge edits.
5. **A-1:** no edit is needed, because option 1 removes the conflict (§1).
6. **Hit counts (§7):** restated for the decided edits only. They add `§ File Location` per file, `hyphens and dots`, and
   the `Create the release artifact` removal row.
7. **Unverified list shortened (§9).** Items the orchestrator verified are removed.
8. **No other text changes.** P-2 to P-9 and R-1 to R-3 are byte-identical to v1's option-1 texts.

## 5. Per-edit statements

None of these edits touches `AGENTS.md` or a stable instruction.

| Edit | Upward? | Relaxes a check? | Golden: quote / fixture / result | Security |
|---|---|---|---|---|
| P-1, P-2 | No (a skill, amended to the user's decision) | No. The path is still one form; the slug wording describes the decided form and admits no second path | None / none / none. `validate-workflow-gate-verdict-sources` cites `plan-approve-execute` § The Three Phases › Phase 2: Approve by name only, and holds no copy of the skill. P-2 changes no heading | None |
| P-3 | No (an agent) | No | None / none / none. The same case cites `orchestrator` sections by name only | None |
| P-4 | **A command edit made on the user's decision** (ADR-007), not on the strength of a skill or agent | No. The command still names exactly one path | `new-feature-plan-doc-compliant`: **quote stale** (`brief.md:11–13`). Fixture unchanged. **Result unchanged but stale green**: `expect.py:25` still globs `feature-*.md` and still matches `feature-audit-log-export.md`. Realignment is FU-P32-G. `new-feature-checkpoint-line-compliant` and `new-feature-real-checkpoint-format-drift` quote step 7 only: none | None |
| P-5 | **A command edit made on the user's decision** | No | `new-project-plan-doc-and-lifecycle-states`: **quote stale** (`brief.md:16`, and the docstring `expect.py:6`). Fixture `plan-taskflow.md` unchanged; it is now a non-conforming example because it has no number. **Result unchanged**: `PLAN_NAME_RE = re.compile(r"^plan-[a-z0-9][a-z0-9-]*\.md$")` (`expect.py:26`) still matches the fixture, and would also match `plan-042-taskflow.md`. Realignment is FU-P32-G | None |
| P-6 | No (a skill) | No | None (no open case cites it) | None |
| P-7 | No (an agent). It reaches `/new-poc`'s imported clause on the user's decision. P11's form is not reopened | No | `new-poc-plan-hypothesis-format`: **quote unchanged** (`brief.md:58`'s words survive). Fixture `plan-001.md` is unchanged and becomes a non-conforming example because it has no slug; `check()` does not read the path. **Result unchanged.** An optional refresh is part of FU-P32-G | None |
| P-8, P-9 | Not knowledge documents | No | None | None |
| R-1, R-2, R-3 | No (a skill, amended to the user's decision) | No. `verify-release-docs.py` and `publish-release.py` are unchanged and stay fail-closed on `docs/releases/<tag>.md` | None / none / none. No open case cites `release-workflow` | None. R-2 points the skill at the file the orchestrator's mandatory preflight already publishes |

**No edit in §§2–3 changes a golden fixture or result.** Two golden quotes go stale (P-4, P-5). That is FU-P32-G's
scope, not this implementation's.

## 6. FU-P32-G — golden realignment (separate follow-up; **not yet authorized**)

**Prerequisites:**
1. An explicit, file-scoped `docs/artifacts/protected-paths-v1.md` §5 grant covering the case directories below.
2. A **user-authorized v18** evaluator-hash baseline. The user has **not** authorized it yet; the orchestrator will ask.
   Every `expect.py` edit and fixture rename moves the `tests_golden` digest. The orchestrator should confirm whether a
   `brief.md`-only edit does too.

It lands after the knowledge edits, because the briefs must quote the merged wording verbatim. No item requires
access to `tests/golden/held-out/`.

### 6.1 Required

**`tests/golden/open/new-feature-plan-doc-compliant/`** (quote, glob and fixture realigned to P-4):

| File | Change |
|---|---|
| `expect.py:25` | Glob `feature-*.md` becomes `plan-*.md`. Same strength: exactly one match is still required. |
| `expect.py:4–6` (docstring) | `docs/plans/feature-<slug>.md` becomes `docs/plans/plan-<ID>.md`. |
| `fixture/docs/plans/feature-audit-log-export.md` | Renamed to `fixture/docs/plans/plan-001-audit-log-export.md`. Content unchanged. |
| `brief.md:11–13` | The step 1 quote is replaced by P-4's merged text, verbatim. |
| `brief.md:16–17` | The pass condition names `fixture/docs/plans/plan-<ID>.md`. |
| `brief.md:20–26` | The provenance records the P32 realignment: the user's decision of 2026-10-08 and `path-conventions-v2.md`. |
| `case.yaml` | No change; `expected_pass` stays. |

- Expected result: `True` before and after.
- Discrimination to show: `False` with zero `plan-*.md` files, `False` with two, and `False` with the fixture left at
  its old `feature-*.md` name.

**`tests/golden/open/new-project-plan-doc-and-lifecycle-states/`** (quote realigned to P-5):

| File | Change |
|---|---|
| `brief.md:16` | The step 1 quote line becomes `>    - Write the plan to `docs/plans/plan-<ID>.md`, with `<ID>` as the `plan-approve-execute` skill § File Location defines it`, matching the merged text verbatim. |
| `expect.py:6` (docstring) | The same quote updated. |
| `expect.py:25` (comment) | `plan-<project-slug>.md` becomes `plan-<ID>.md`. |
| `brief.md:72, :87, :95–98` | Descriptive text updated: the pass condition's `plan-<slug>.md`, and the provenance notes on `/new-project`'s former shape. |
| `fixture/docs/plans/plan-taskflow.md` | **Optional** rename to `plan-001-taskflow.md`, so the hand-authored example carries the decided form. It still matches `PLAN_NAME_RE`, so the result is unchanged. |
| `expect.py:26` `PLAN_NAME_RE` | **Unchanged by default.** It requires no number, which is looser than P-1, and admits no dots, which is stricter. Bringing it to P-1's form would tighten it on the number and widen it on dots. Any change is a separate check decision for the orchestrator. Under ADR-007 §5, it may not be made for convenience. |

- Expected result: `True` before and after.

### 6.2 Optional

**`tests/golden/open/new-poc-plan-hypothesis-format/`.** The fixture `plan-001.md` lacks the slug P-1 now requires.

| File | Change |
|---|---|
| `fixture/docs/plans/plan-001.md` | Rename to `plan-001-local-note-search.md`. The path is not asserted, so the result is unchanged. |
| `brief.md:59–63, :96–98` | Descriptive text: the fixture name, and "the amended form". |

`brief.md:18–19` and `:58` are unchanged, because `/new-poc`'s text and P-7's quoted words are unchanged.

**`tests/golden/open/plan-required-sections-compliant/` (pre-existing, O4; not caused by P32).**

| File | Change |
|---|---|
| `brief.md:12, :17` | Still say `docs/plans/<slug>-plan.md` and `fixture/docs/plans/*-plan.md`, while `expect.py:33` globs `plan-*.md`. Change the descriptive text to `docs/plans/plan-<ID>.md` and `fixture/docs/plans/plan-*.md`. The result is unchanged. |

Bundling it here would use the same grant.

**Scorecard.** FU-P32-G predicts **no case-status transition**. Every case stays at its current status and result.

## 7. Hit counts (decided edits only)

Counts are case-sensitive and fixed-string, per file, after every decided edit to that file:
- **Lines** = `grep -cF`.
- **Occurrences** = `grep -oF … | wc -l`.
- **Before** counts are at `c152eb7`, taken by reading **(unverified by grep)**.
- **0 / 0** in the After column means the old wording must be gone.

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

## 8. Observations to park (carried from v1 §8; not ruled)

- **O1: version suffixes on plan file names, against `coding-standards`.**
  - `coding-standards:66–83` requires `<type>-vN.md` for "All plan, decision, and documentation artifacts". Its reach to
    plan files is contested (v1 A-2, Step B).
  - The same table also gives `checkpoint-vN.md` against `AGENTS.md:27`, and `decision-vN.md` against `AGENTS.md:33`.
    That is a conflict inside tier 1.
  - The templates' `:61` names revisions `plan-<slug>-v2.md`, while `plan-approve-execute:182` makes a revision a new,
    superseding plan.
  - Suggested trigger: the next task touching `coding-standards.md` § Artifact Versioning & File Naming, or the first
    plan revision. Any fix to `coding-standards` itself is an instruction-change task.
- **O2: `/new-project:43` and `:51` against `AGENTS.md:27` and `:22`.**
  - `:43` writes checkpoints to `docs/checkpoints/checkpoint-<phase>.md`.
  - `:51` uses `<artifact-name>-v<major>.<minor>.md`.
  - These have the shape T515 ruled at ADR-007 branch 1 for `/new-feature`.
- **O3: release-version-keyed files under `docs/artifacts/`, against `AGENTS.md:22`.** This is moot under the decided
  Q-P32b option. It is kept only so it is not re-raised.
- **O4: `plan-required-sections-compliant/brief.md:12, :17` describe a stale path.** It is listed as an optional item in
  FU-P32-G (§6.2).
- **O5: `/new-feature:25` against `AGENTS.md:18`.** `/new-feature:25` says "Have the Scrum Master create tasks", and
  `AGENTS.md:18` says "Only orchestrators create/transition tasks".
- **O6: CI generates a third file, `release-notes.md`, at the repository root.** It comes from
  `publish-release.py:210–211` and `.gitlab-ci.yml:206`, and is the `docs/releases` document plus a commit changelog.
  It is generated, not knowledge.

## 9. Still unverified

1. The worktree commit `c152eb7`.
2. Anchor uniqueness and every count in §7, which come from reading, not `grep`.
3. That all 108 real plans conform to P-1. This rests on the orchestrator's survey.
4. That no command other than the six read in v1 writes a plan path.
5. Whether a `brief.md`-only edit moves the `tests_golden` digest. This matters for FU-P32-G's prerequisites.

## 10. Summary

| Item | Subject | Settled by | Outcome | Edits |
|---|---|---|---|---|
| A-1 | Plan path under `/new-feature` | The user's decision (supersedes the held Step C edit) | No conflict remains after P-4; E-C1 and E-C2 withdrawn | none |
| A-2 | `<ID>`; the plan path on both tracks | The user's decision: "plan-<NNN>-<slug>.md (Recommended)" | `docs/plans/plan-<ID>.md`. `<ID>` = three-digit number, a hyphen, and a slug of lowercase letters, digits, hyphens and dots. Defined once, in `plan-approve-execute` § File Location | P-1 to P-9 |
| A-2′ | Version suffixes on plan file names | — | Parked as O1 | none |
| B-1 | Release-notes path; one document or two | The user's decision: "One, at docs/releases/ (Recommended)" | One document, `docs/releases/v<VERSION>.md` | R-1 to R-3 |
| FU-P32-G | Golden realignment | Needs a grant and a user-authorized v18 (**not yet authorized**) | Two required cases and two optional ones; no status transitions | §6 |

- **No edit is upward and none relaxes a check.**
  - The only command edits are P-4 and P-5, both on the user's decision.
  - P-7 reaches `/new-poc`'s imported clause, also on the user's decision.
- **Security:** none of these edits touches a security control, a secret or a gate check.
- **Golden:** the knowledge edits change no fixture or result. Two quotes go stale (P-4, P-5) until FU-P32-G.
- **Blockers:** none.
