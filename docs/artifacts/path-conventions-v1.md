# Artifact: path-conventions-v1.md

> Filename: `path-conventions-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T595 (P2, judgment tier, decision only)
- **Created**: 2026-10-08
- **Based on:**
  - `docs/tasks/task-T595.md` (the brief, authoritative);
  - `docs/plans/plan-108-path-conventions.md`;
  - `docs/plans/plan-092-poc-contract-amendments.md` §4 (P32);
  - `docs/artifacts/poc-contract-resolution-v1.md` §2 (P11) and §7.2 (origin of P32), both **inputs, not reopened**;
  - `docs/artifacts/command-contract-resolution-v1.md` §3 row A (T515 verdict A, `/plan` path), an **input, not reopened**;
  - `docs/artifacts/remaining-verdict-renderings-v1.md` §5 (G5 → P32) and §6.3 (G7 plan path → P32);
  - `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted) and
    `docs/decisions/ADR-007-command-contract-authority.md` (Accepted);
  - the user's decision of 2026-10-08, "Next item: continue as recommended" (the recommended item was P32), and the
    user's standing ADR-008 review decision Q1, **"Self-placement only"**.
- **Supersedes**: none (first version).
- **Decision references**: ADR-008 Step A (P3a), Step B (P1), Step C (P2), Step D (P3b), Step E (P5); ADR-008 D2–D5,
  P4, § Risks; ADR-007 § Decision (a command clause changes only on branch 1 or by user decision), §5 (never relax a
  check), § Risks. No new ADR is minted.

## 0. Method and limits

- **Commit.** Every cited line was re-read in the worktree `agent-solution-architect-T595`, which the orchestrator
  states is on `develop` `c152eb7` **(commit unverified: no shell)**. Line numbers are at that commit. Several differ
  from those in T563 and T593 (for example `/prepare-release` step 7 is now `:38–43`, after C-G4 was applied).
- **No shell.** No `grep`, `git`, directory listing or test run. Anchor uniqueness and every hit count come from reading
  whole files and are **(unverified by grep)**. §9 collects every unverified claim.
- **Files read in full (source):** `implementation/AGENTS.md`; instructions `coding-standards`; commands `new-feature`,
  `plan`, `batch`, `new-project`, `new-poc`, `prepare-release`; agents `orchestrator`, `poc-orchestrator`,
  `release-manager`, `scrum-master`, `technical-writer`; skills `plan-approve-execute`, `project-planning`,
  `release-workflow`, `task-management`; `implementation/registry/summary.md`; `implementation/knowledge/README.md`;
  `implementation/knowledge/schemas/{command,skill}.schema.json`. Not knowledge: `implementation/docs/plans/_template.md`,
  `docs/plans/_template.md`, `docs/releases/_template.md`, `tests/performance/test_team_health.py`,
  `implementation/docs/tasks/validate-tasks.py`, `scripts/verify-release-docs.py`, `scripts/publish-release.py:1–279`,
  `.gitlab-ci.yml`. Real artifacts opened: `docs/plans/plan-108-path-conventions.md`, `plan-107-…`, `plan-092-…`,
  `docs/releases/v6.4.1.md:1–12`. `docs/artifacts/release-notes-v6.4.1.md` and `docs/plans/plan-001.md` do not exist.
- **Golden.** Under `tests/golden/open/` only, I read `brief.md`, `expect.py` and `case.yaml` (where present) of
  `new-feature-plan-doc-compliant`, `plan-required-sections-compliant`, `plan-real-doc-header-drift`,
  `plan-task-creation-precondition-real`, `new-poc-plan-hypothesis-format`, `new-feature-checkpoint-line-compliant`,
  `new-feature-real-checkpoint-format-drift`, `prepare-release-real-verdict-missing`,
  `prepare-release-changelog-grouping-compliant`, `prepare-release-conditional-pass-conditions-gap` and
  `validate-workflow-gate-verdict-sources`, and the first lines of three fixtures (named in §6). **I never opened
  `tests/golden/held-out/`.** Some open briefs name sibling cases; I do not repeat any name that lacks a
  `tests/golden/open/` directory.
- **Secrets.** I read no `.env*`, credential or key file.
- **Encoding.** `§` is U+00A7, `—` is U+2014, `→` is U+2192, `›` is U+203A, `…` is U+2026. No emoji is introduced.
  Each four-backtick fence holds one Before/After pair; inner three-backtick fences are literal. Apply each edit by
  its Before text, never by line number.
- **Scope-gaming guard (ADR-008 § Risks).** Declared scope is read as of the commit where the conflict was first
  recorded: for (a), T563 at `8535dca` (`poc-contract-resolution-v1.md` §7.2, §9.1); for (b), T572 at `24518f6` (G5).
  The only scope text a ruling below *relies on* is A-1's: `/new-feature:14` and `orchestrator.md:23, :55–59`, which
  T563 itself quoted (§2 and §7.2). `project-planning:208` was added by T594, after P32 was recorded; it is not relied
  on.

## 1. Authority basis and constraints

ADR-008 § Order of application: A (joint satisfiability, every pair) → B (tier 1: `AGENTS.md` and the stable
instructions) → C (a command's declared output, for a skill or agent applied under it) → D (peers: self-placement only,
per Q1) → E (escalate). Maturity never ranks (P4). A command clause changes only on ADR-007 branch 1 or by a user
decision. Below:

- no edit is upward: none touches `AGENTS.md` or a stable instruction;
- no edit relaxes a check: no test, glob or `check()` is loosened, and no contract admits a second form;
- no command is changed except under an option the user chooses;
- P11 (`plan-<ID>.md` on the PoC track) and T515 verdict A (`plan-<ID>.md` for `/plan`) are inputs. Neither is
  reopened. P11 §7.2 left one question open, "Whether `<ID>` admits a slug suffix belongs to whoever adjudicates the
  production-track plan path", and this artifact puts that question to the user.

## 2. (a) The production-track plan path

### 2.1 Clauses (verbatim, `file:line` at `c152eb7`)

**Commands** (all executed by `agent: "orchestrator"`, `:3` in each file):

- `/new-feature:13–14` "1. **Create a lightweight plan document** for this feature" / "- Write to
  `docs/plans/feature-<slug>.md`"; `:16` "- Reference protocol: `plan-approve-execute` skill § The Three Phases ›
  Phase 1: Plan (Plan Document Format)"; `:25` "5. Have the Scrum Master create tasks and estimate effort"; `:36` "9.
  Update `docs/tasks/active-tasks.md` with new tasks and state transitions".
- `/plan:17` "5. **Write the plan document** — save to `docs/plans/plan-<ID>.md` using this structure:"; `:34–37` "The
  plan document produced by this command is a **precondition**, not a formality: no task row may be added to
  `docs/tasks/active-tasks.md` until (a) the plan document it derives from exists under `docs/plans/plan-<ID>.md` and
  (b) that plan has been presented for review per step 6 above."
- `/batch:19` "Write the decomposition to a plan document at `docs/plans/plan-<ID>.md`, following the structure
  `/plan` step 5 declares (…)".
- `/new-project:13–14` "1. **Create a plan document** with task decomposition and dependency graph" / "- Write the
  plan to `docs/plans/plan-<project-slug>.md`"; `:16` (the same reference protocol line as `/new-feature:16`); `:57`
  "- Write active tasks to `docs/tasks/active-tasks.md`". **Not in the brief's list; found by reading.**

**Agent:** `orchestrator.md:17` "For every non-trivial request, follow the Plan-Approve-Execute cycle:"; `:23` "4. Write
a plan document to `docs/plans/plan-<ID>.md` with:"; `:55–59` "- **Precondition:** a task row may not be added to
`docs/tasks/active-tasks.md` until the plan document it derives from exists under `docs/plans/plan-<ID>.md` and has
been presented for review (see `commands/plan.md` §"Task Creation Precondition"). Task creation without a backing plan
is not permitted — write and present the plan first."; `:64–65` "- Ensure every created task's ID appears somewhere in
the source plan document's text so automated plan-coverage checks can trace it back."; the same token in the same
file for a task ID: `:34` "2. Create detailed task briefs in `docs/tasks/task-<ID>.md`".

**Skills:**
- `plan-approve-execute:3` (description) "The Plan-Approve-Execute protocol for project work. Use when starting a
  project, planning a feature, or managing the approval workflow before execution begins."; `:20–24` "## File Location
  … docs/plans/plan-<feature-or-phase>.md"; `:97` "Please review the full plan at `docs/plans/plan-<name>.md`."; `:120`
  "2. Create all tasks from the plan's Task Breakdown in `docs/tasks/active-tasks.md` (use `task-management` skill).";
  `:182` "- If a plan is superseded by a new plan, update its status to `superseded` and link to the replacement."
- `project-planning:153` "All plans produced by this skill feed into the **plan-approve-execute** protocol. The workflow
  is:"; `:155` "1. **Plan** — This skill produces the plan document (WBS, milestones, sprint backlogs)."; `:163–168`
  "Plan documents are versioned artifacts stored under `docs/plans/`: … docs/plans/project-plan-v1.md
  docs/plans/project-plan-v2.md"; `:204` "When a plan is approved, the sprint backlog tasks MUST be decomposed into
  entries in `docs/tasks/active-tasks.md`."

**PoC track (P11, input):** `new-poc:17` "- Write to `docs/plans/plan-<ID>.md`"; `poc-orchestrator:25` "3. Write a
lightweight plan in `docs/plans/plan-<ID>.md`:". `/new-poc:18` imports that PLAN PHASE by reference.

**Tier 1:**
- `AGENTS.md` names no plan path anywhere. `:22` "- Immutable artifacts: `<type>-v<N>.md` (e.g. `requirements-v1.md`,
  `architecture-v1.md`)"; `:24` "- Revisions create new versions, never overwrite." It does not say a plan is an
  immutable artifact.
- `coding-standards` (stable instruction, D1): `:2` description "Use when writing code in any language. Covers naming
  conventions, function design, error handling, general clean code principles, and artifact versioning."; `:3`
  `applyTo: "**/*.{ts,js,py,java,cs,go,rs,rb,php,swift,kt}"`; `:10–13` (Rails Inputs) "Triggers on any code file
  matching this instruction's `applyTo` glob (…); also invoked explicitly by `tech-lead.md`'s Code Standards
  responsibilities and by `AGENTS.md`'s "Code Standards" routing table when establishing or reviewing project
  conventions."; `:18–20` (Out of scope) "Does not cover language-specific idioms beyond the naming, function-design,
  error-handling, security, organization, and artifact-versioning rules stated below."; `:66–67` "All plan, decision,
  and documentation artifacts follow the `<type>-vN.md` naming convention: - `plan-v1.md`, `plan-v2.md`,
  `plan-v3.md`"; `:73` "- Version numbers are sequential integers starting at 1 (`v1`, `v2`, `v3`, ...)."; `:74` "- The
  latest version is the active/current version. Prior versions are historical record."; `:80` "| `plan-vN.md` |
  `docs/plans/` | Implementation plans |". **Not in the brief's list; found by reading.**

**Not knowledge (corroboration and consequence only):**
- `implementation/docs/plans/_template.md:3`, identical in `docs/plans/_template.md:3`: "> Filename convention:
  `plan-<slug>.md` (e.g. `plan-payment-feature.md`)."; `:61` "- [ ] Plan locked; revisions create `plan-<slug>-v2.md`".
- `tests/performance/test_team_health.py:83` `return sorted(p for p in plans_dir.glob("plan-*.md"))`; `:188`
  `referenced = set(re.findall(r"\bT\d{3,}\b", plan_text))`; `:168–197` make an unreferenced active task a hard failure.
- Real plans: `plan-108-path-conventions.md`, `plan-107-remaining-verdict-renderings.md`,
  `plan-092-poc-contract-amendments.md`, `plan-030-mcp-remote-transport-alignment.md` (each opened). That *every* real
  plan has this form is **(unverified)**; T563 §9.1 confirmed only that every file but `_template.md` starts `plan-`.

### 2.2 D5 record A-1: the plan path under `/new-feature` — **Step C fires; edit held for sequencing**

| Field | Content |
|---|---|
| **Subject (D3)** | A path: where the plan document that `/new-feature` step 1 writes, and from which that run's tasks are created, lives. |
| **Clauses** | `/new-feature:3, :13–14, :25, :36` against `orchestrator.md:23, :55–59, :64–65` and `plan-approve-execute:20–24` (all quoted in §2.1). |
| **Step A** | **Fails.** MUSTs: `/new-feature:14` writes the plan to `feature-<slug>.md`; `orchestrator.md:55–59` forbids adding a task row "until the plan document it derives from exists under `docs/plans/plan-<ID>.md`"; `/new-feature:36` makes the executing orchestrator add those rows. Exclusivity: neither says "only". **One-value test:** both clauses name the *same* document, the plan the run's tasks derive from (`:55–59` "the plan document it derives from"; `:64–65` "the source plan document"), and that document has one path. `feature-<slug>.md` cannot match `docs/plans/plan-<ID>.md` under any reading of `<ID>`, because the fixed prefix differs. `plan-approve-execute:23` fails the same way (`plan-<feature-or-phase>.md`). **Rejected counter-reading: write a second copy at `plan-<ID>.md`.** This differs from G5 (§3), where nothing identifies the two release-notes files as one document. Here both clauses identify one plan, and a copy is a second document that can drift (its `**Status:**` and task list are edited on approval, `plan-approve-execute:109`), the very risk ADR-008 P3b's remedy names: "a copy can drift". |
| **Step B** | **Does not fire.** `AGENTS.md` names no plan path. `coding-standards`: P1(b) is not shown (A-2, Step B). |
| **Step C** | **Fires.** (a) Applied under: `/new-feature:3` `agent: "orchestrator"`; `/new-feature:16` names `plan-approve-execute`. (b) Output contract: the plan path is declared output, "Write to `docs/plans/feature-<slug>.md`". (c) Step A fails. **Not imported text:** `/new-feature:16` imports "§ The Three Phases › Phase 1: Plan (Plan Document Format)" (`plan-approve-execute:28–77`), which names no path. § File Location (`:20–24`) and the Phase 2 prompt (`:97`) are outside the import, so ADR-007's same-file prong does not apply. |
| **Step fired** | **C (P2).** Under `/new-feature`, the command's path governs. Per P2's remedy, the agent and the skill are amended, scoped to "when run through `/new-feature`", and the command is not amended. |
| **Declared scope relied on** | `/new-feature:3` and `:14` (both T563-quoted as the command's executor and its path, §7.2); `orchestrator.md:23, :55–59` (T563-quoted, §2). |
| **Amendment** | **E-C1** (`orchestrator.md`) and **E-C2** (`plan-approve-execute` § File Location), §5.1. **Held for sequencing only**, as T593 held E-R1: options 1 and 2 of Q-P32a change `/new-feature:14` by user decision, after which no conflict remains and neither edit is needed. Under option 3, E-C1 and E-C2 apply as written. Under option 4, E-C1 applies and E-C2's content is folded into P-1/P-2. |
| **Maturity** | Not relied on (`/new-feature` is `stable`; `orchestrator` and `plan-approve-execute` are `experimental`; irrelevant). |

### 2.3 D5 record A-2: `<ID>`, the other plan paths and the track convention — **Step E (P5)**

| Field | Content |
|---|---|
| **Subject (D3)** | A path: the file name of a production-track plan document under `docs/plans/`, including what the `<ID>` slot admits. The version suffix is a separate subject (A-2′, below). |
| **Clauses** | `/plan:17, :34–37`; `/batch:19`; `/new-project:14`; `orchestrator.md:23, :55–59`; `plan-approve-execute:20–24, :97`; `project-planning:163–168, :204`; tier 1 as quoted in §2.1. |
| **Step A** | **(i) The `plan-` family cannot be completed.** `plan-<ID>.md` (`/plan`, `/batch`, `orchestrator`), `plan-<feature-or-phase>.md` (skill) and `plan-<project-slug>.md` (`/new-project`) share `docs/plans/plan-…​.md` and differ only in the slot. None says "only". Whether one name satisfies all of them turns on what `<ID>` denotes, and **no document defines a plan's `<ID>`**. Read as any identifier, the slots nest (D4, "fills a slot the other leaves open"), and Step A holds. Read as a sequence number, as the same token means for tasks in the same file (`orchestrator.md:34`; `AGENTS.md:19` "Sequential IDs: `T001`, `T002`, …"), `plan-<project-slug>.md` and `plan-<feature-or-phase>.md` cannot satisfy it, and Step A fails (one plan, one name). **(ii) `project-planning` fails outright** against the orchestrator's precondition whenever its plan's tasks are created (`:204`). `project-plan-v1.md` does not begin `plan-`, under any reading of `<ID>`. **(iii) Commands among themselves: holds.** Each command declares the path of its own plan only. `/plan:34`'s precondition is scoped to "The plan document produced by this command". The test's glob is not a knowledge clause. |
| **Step B** | **Not shown.** `AGENTS.md` names no plan path and does not say a plan is an "immutable artifact" (`:22`). `coding-standards` meets P1(a): `:66–67` and `:80` quotably give implementation plans in `docs/plans/` the form `plan-vN.md`. **P1(b) is not shown.** The body (`:66`), description (`:2`) and Out-of-scope sentence (`:18–20`) name artifact versioning, plans included. But `applyTo` (`:3`) excludes `docs/plans/*.md`, D2 says "`applyTo` filters paths", and the Rails Inputs (`:10–13`) bring the instruction into play only for code files or on explicit invocation "when establishing or reviewing project conventions". D2's reading rules do not say whether a path filter that excludes the files narrows a subject the body names. Its worked example is the converse case, where an Out-of-scope exclusion narrows `applyTo: "**"`. P1 must be shown on all four parts, and ADR-007 § Risks and ADR-008 § Risks ("The tier-1 loophole") both warn against firing it on contested reach. So I do not fire it. Two facts show this cannot be settled inside this task. (1) On the reaching reading the remedy's target is indeterminate: `:67, :74` model one evolving plan (`plan-v1.md`, "The latest version is the active/current version"), while every party writes one plan per request. (2) Firing it would also amend P11's `plan-<ID>.md` and T515 verdict A's, both inputs. **Consequence:** the version-suffix subject is split off as A-2′ (observation O1, §8), and nothing is amended on it. |
| **Step C** | **Does not decide.** `/new-project` against the orchestrator: P2(a) and (b) hold, but (c) cannot be evaluated until `<ID>` is defined (Step A (i)). `/plan` and `/batch` agree with the orchestrator. No command among those read names `project-planning` **(unverified beyond the six commands read)**, so it is not applied under a command. |
| **Step D** | **Does not decide.** The peers are `orchestrator`, `plan-approve-execute` and `project-planning`. On the path, none places the subject with another. `orchestrator.md:57–58` points to a command (`commands/plan.md`), not a peer, and that command agrees with it. `plan-approve-execute` names no other document for the path. `project-planning:153` ("feed into the **plan-approve-execute** protocol") places its plans in that protocol's *workflow* (`:155–157`: Plan, Approve, Execute), but the same section keeps the file location for itself (`:163`), so it is not self-placement on the path. **Counter-reading recorded:** if `:153` is read as placing the plan document itself with `plan-approve-execute`, P3b makes § File Location govern `project-planning`'s path. That leaves `orchestrator` against `plan-approve-execute` undecided under Step A (i), so the result is still an escalation. Scope breadth or nesting decides nothing (Q1). |
| **Step fired** | **E (P5).** Escalated as **Q-P32a** (§4.1), with the blocker content of P5 § Form 1: type `unclear_requirements`, the subject, the quotes, and Step A (i)/(ii) as the steps that failed to decide. **Hold:** no document is amended on the plan path until the user decides (P5 § Form 3). |
| **Declared scope relied on** | None decides. Read and recorded: `coding-standards:2, :3, :10–13, :18–20`; `plan-approve-execute:3`; `project-planning:153`. |
| **Amendment** | None now. Candidate edits for every option are held verbatim in §5.1. |
| **Maturity** | Not relied on. `coding-standards`' `maturity: stable` is used only for D1 tier-1 membership, the one use P4(c) permits. |

**A-2′ (split off, not ruled): versioning of plan file names.** `coding-standards:66–83` requires `-vN` on "All plan,
decision, and documentation artifacts". Against it: every plan clause except `project-planning`, P11's PoC form, the
templates' first version (`plan-<slug>.md`), and every real plan opened. The same table also gives `checkpoint-vN.md`
against `AGENTS.md:27` `checkpoint-<SEQ>-<phase>.md`, and `decision-vN.md` against `AGENTS.md:33`
`ADR-<NNN>-<slug>.md`, a within-tier-1 tension that ADR-008 P1 § Within tier 1 sends to P5 unless one side declares
precedence (neither does in its Rails). This is outside brief §1. It is reported as **O1** with a parking
recommendation. No option in §4.1 adds or removes a version suffix, so none moves the question.

### 2.4 Answers to brief §1(a)

1. **Do these clauses contradict?**
   - `/new-feature` against the orchestrator and the skill, under `/new-feature`: **yes** (A-1, decided at Step C).
   - `project-planning` against the orchestrator: **yes** (A-2 Step A (ii); not decided, escalated).
   - The `plan-` family (`/plan`, `/batch`, `/new-project`, `orchestrator`, `plan-approve-execute`): **undetermined**,
     because the answer turns on the undefined `<ID>`.
   - The commands among themselves: **no**.
2. **Does `<ID>` admit a `-<slug>` suffix?** **No text decides it.** On the literal reading the pattern has one variable
   part, so a slug is admissible only if a plan's ID is defined to include it, and nothing defines a plan's ID. The
   precedents are inputs, not authority. T515 verdict A described `plan-NNN-<slug>.md` files as following the
   `plan-<ID>.md` form, but only in passing (`command-contract-resolution-v1.md` §3 A, "8 of 8 sampled real plan
   documents follow the second form"); P11 §7.2 left the question open; and T565 renamed the PoC fixture `plan-001.md`.
   Defining `<ID>` fills an open slot in four commands, so it is a convention choice for the user (Q-P32a).
3. **Which convention governs the production track?** **None, by ADR-008.** That is the user's decision (Q-P32a).

## 3. (b) Release notes — D5 record B-1: **Step A holds; the convention is escalated**

| Field | Content |
|---|---|
| **Subject (D3)** | A path, and with it the number of release-notes documents a release has. |
| **Clauses** | `release-workflow:56` "5. **Create the release artifact** at `docs/artifacts/release-notes-v<VERSION>.md`."; `:129` "### 4. Create Release Artifact"; `:132` "# Release Notes — v<VERSION>"; `:154` "- Release: <PASS/CONDITIONAL_PASS> on YYYY-MM-DD"; `:160` "File location: `docs/artifacts/release-notes-v<VERSION>.md`"; `:233` "- Keep release notes user-facing. Internal changes go in the "Internal" changelog section." Against: `/prepare-release:22` "5. Prepare release notes"; `:38–43` "7. **Produce a structured release gate VERDICT** in the release notes document from step 5 (`docs/releases/v<version>.md`) as a top-level `## RELEASE VERDICT` section. That document is the block's home — not the release checkpoint from step 6. `docs/releases/_template.md` carries the slot, and `scripts/verify-release-docs.py --tag v<version>` checks the section is present when the tag is cut. …"; `orchestrator.md:132–134` "- Before calling `glab release create`, verify that `docs/releases/vX.Y.Z.md` exists and is committed / - Publish/update release notes from that file only: … -F docs/releases/vX.Y.Z.md` / - Do not pass ad-hoc inline `--notes`; it can drift from `docs/releases/vX.Y.Z.md`". Related: `release-manager:47` "4. Track blocker metadata in release notes: blocker ID, owner, ETA, mitigation."; `:161` "… that command's `## RELEASE VERDICT` section in the release notes document (its step 7) …". **Not knowledge:** `docs/releases/_template.md:3` "Copy this file to `docs/releases/vX.Y.Z.md` before cutting a release tag."; `:4–6` "The release CI job embeds this document in GitLab Release notes (highlights + install). Commit messages since the previous tag are appended as a changelog section."; `scripts/verify-release-docs.py:24–25` (`Path("docs/releases") / f"{tag}.md"`); `scripts/publish-release.py:99–106` (reads `docs/releases/{tag}.md`, fails closed); `.gitlab-ci.yml:175, :202`. Real releases: `docs/releases/v6.4.1.md` exists; `docs/artifacts/release-notes-v6.4.1.md` does not. |
| **Step A** | **Holds**, re-derived at this commit. (1) No clause says a release has exactly one release-notes document. `orchestrator.md:133`'s "only" governs the source of the *published* notes, which `release-workflow` does not address. (2) The two templates require different sections (`release-workflow:131–158` against `docs/releases/_template.md` and `orchestrator.md:135`), and both files can be written. (3) **One-value test:** the release verdict appears in both (`release-workflow:154` and `/prepare-release`'s `**Status**`). It is one gate's one value, which `:154` copies (T593 G3.6, "Holds by construction"). The changelog groupings differ (`release-workflow:62–87` against `/prepare-release:18`), but in two documents they are two renderings, not two values of one field. |
| **Step B** | **Not engaged on the path.** `AGENTS.md` names no release-notes path. § Artifact Versioning (`:22`) does not say a release-notes document is an "immutable artifact", nor what `<N>` admits, so no contradiction is visible in its own text (P1(a)); see O3. `coding-standards` has the same contested reach as A-2. Even on the reaching reading it would not choose between the paths, because both carry a release version, not "sequential integers starting at 1" (`:73`). |
| **Step C** | **Not applicable.** `/prepare-release` does not name `release-workflow`, and its executor (`orchestrator.md`) and the verdict's issuer (`release-manager.md`) do not name it either (whole files read). |
| **Step D** | Not reached (Step A holds). |
| **Step fired** | **A.** ADR-008 decides one part: the two clauses do not contradict, so keeping two documents is *permitted*. It does not decide whether a release should have one document or two, or which path. That is a convention choice. It binds a command if the command's path changes (a user decision under ADR-007), the orchestrator's preflight, two CI scripts and a template. No ADR-008 step supplies it. Per brief §1(b), it is **escalated as Q-P32b** (§4.2). |
| **Declared scope relied on** | None. |
| **Amendment** | None by ADR-008. Candidate edits per option are held in §5.2. |
| **Maturity** | Not relied on (`release-workflow` and `/prepare-release` are `experimental`, `orchestrator` is `experimental`, `release-manager` is `stable`; irrelevant). |

## 4. User questions (one round)

### 4.1 Q-P32a — the production-track plan file name

**Subject.** What file name does a production-track plan have, and what is `<ID>` in `docs/plans/plan-<ID>.md`?

**Quotes.**
- `/new-feature:14` "Write to `docs/plans/feature-<slug>.md`".
- `/new-project:14` "Write the plan to `docs/plans/plan-<project-slug>.md`".
- `/plan:17` "save to `docs/plans/plan-<ID>.md`". `/batch:19` and `orchestrator.md:23` say the same, and
  `orchestrator.md:55–59` makes it a precondition for every task row.
- `plan-approve-execute:23` `docs/plans/plan-<feature-or-phase>.md`; `:97` `docs/plans/plan-<name>.md`.
- `project-planning:166–167` `docs/plans/project-plan-v1.md`, `docs/plans/project-plan-v2.md`.
- Real plans: `plan-108-path-conventions.md`. The PoC track (P11) uses `plan-<ID>.md`, with `<ID>` left open.

**Why the steps did not decide it.**
- Under `/new-feature`, ADR-008 does decide (Step C): the command's own path governs, and the orchestrator and the skill
  must defer when run through it.
- Everywhere else, whether the clauses even conflict depends on what `<ID>` means, and no document defines it (Step A).
- No tier-1 text can be applied: `AGENTS.md` is silent, and `coding-standards`' reach to plan files is contested (B).
- Self-placement exists on no peer's side (D).
- The commands do not conflict with each other. Choosing one convention for all of them is a convention choice that
  changes commands, which ADR-007 reserves to you.

**Options.** Golden case names below all have `tests/golden/open/` directories. Under every option, `AGENTS.md`, every
instruction, `/plan`, `/batch` and the `/new-poc` text are byte-unchanged.

| Option | Files that change | Test and tooling impact | Golden impact | Renaming |
|---|---|---|---|---|
| **1. One name for every plan: `plan-<NNN>-<slug>.md` (Recommended)** | Commands, by your decision: `/new-feature:14` (P-4) and `/new-project:14` (P-5). Skill `plan-approve-execute:20–24` (P-1, which holds the one definition of `<ID>`) and `:97` (P-2). Agent `orchestrator.md:23` (P-3). Skill `project-planning:163–168` (P-6). PoC: `poc-orchestrator.md:25` (P-7). It fills P11's open slot without changing P11's form, and `/new-poc` imports it. Answer "**1, production only**" to omit P-7. Not knowledge: both `_template.md:3` (P-8, P-9) | `test_team_health.py:83`'s `plan-*.md` glob already matches every new plan, and no test changes. `validate-tasks.py` is unaffected (it checks no plan names). `/plan` and `/batch` get `<ID>` defined through their executor, `orchestrator.md` (a D4 specialisation, no command edit) | **`new-feature-plan-doc-compliant`:** its quote changes (`brief.md:11–13`). Its `check()` (`expect.py:25`, glob `feature-*.md`) stays green on the old fixture `feature-audit-log-export.md`, which is a stale green. Realigning it needs a protected-path grant and a user-authorized **v18**: glob → `plan-*.md` (same strength, exactly one match), fixture renamed to e.g. `plan-001-audit-log-export.md`, brief text updated. **`new-poc-plan-hypothesis-format`** (with P-7): the quote at `brief.md:58` survives (P-7 keeps its words). The fixture `plan-001.md` becomes an example without a slug, but `check()` does not read the path, so the result is unchanged. `brief.md:59–61`'s "amended form" wording goes partly stale; refreshing it is optional (grant + v18). **`/new-project`:** coupling not pre-computed (§6.2). Others: none | None. Real plans already use this form (sampled). `project-planning`'s version moves from the file name to its own `## Version:` field, and each version becomes a new plan with its own number |
| **2. One name, number only: `plan-<NNN>.md`** | Same files as option 1; only the definition text differs (§5.1) | As option 1 | `new-feature-plan-doc-compliant`: as option 1 (fixture renamed to e.g. `plan-001.md`). `new-poc-plan-hypothesis-format`: its fixture `plan-001.md` conforms, and the brief stays accurate | **Every real plan becomes non-conforming.** They cannot safely be renamed: they are historical records (`AGENTS.md:24`), and task briefs cite them by full name in `**Based on:**`. New plans lose a descriptive name |
| **3. No convention change now; apply only what ADR-008 decided** | `orchestrator.md` (E-C1) and `plan-approve-execute` § File Location (E-C2), both scoped to `/new-feature`. No command changes | `<ID>` stays undefined. `/new-project` and `project-planning` against the orchestrator stay escalated, parked with trigger "next task touching `/new-feature`, `/new-project`, `/plan` or `project-planning`". `test_team_health.py:83` does not see `feature-*.md` or `project-plan-v*.md`, so in this repository a task created from such a plan fails `TestPlanCoverage` unless a `plan-*.md` also names it. The test is not changed (never relax) | None | None |
| **4. Feature plans stay `feature-<slug>.md`; every other plan is `plan-<NNN>-<slug>.md`** | `/new-project:14` (P-5, command). `plan-approve-execute` (P-1 and P-2, option-4 texts with the `/new-feature` exception). `orchestrator.md` (P-3 and E-C1). `project-planning` (P-6). PoC P-7 (optional). Templates (P-8, P-9). `/new-feature` unchanged | Feature plans: as option 3 (`TestPlanCoverage`). Other plans: as option 1 | `new-feature-plan-doc-compliant`: none. `new-poc-plan-hypothesis-format`: as option 1. `/new-project`: not pre-computed | None |

**Recommendation: option 1, including the PoC track.**
1. It removes the one contradiction ADR-008 found (A-1) instead of scoping around it, and it gives one artifact class
   one name.
2. The name is self-describing, and no file needs renaming.
3. The plan-coverage test sees every plan.
4. It matches the `plan-` prefix of `coding-standards:80` and leaves the version-suffix question (O1) exactly where it
   is.
5. It fills P11's open slot without changing P11's form.

Its cost: two `stable` command edits, and one golden realignment needing a grant and v18. That real plans already use
this form is a consideration for your choice, not authority for a ruling ("Popularity is not authority", ADR-007).

### 4.2 Q-P32b — the release notes

**Subject.** Does a release have one release-notes document or two, and at which path?

**Quotes.**
- `release-workflow:56` "**Create the release artifact** at `docs/artifacts/release-notes-v<VERSION>.md`" and `:160`.
- `/prepare-release:38–39` "in the release notes document from step 5 (`docs/releases/v<version>.md`)".
- `orchestrator.md:133` "Publish/update release notes from that file only", meaning `docs/releases/vX.Y.Z.md`.

**Why the steps did not decide it.**
- Both documents can be written, and the verdict they share carries one value, so there is no conflict (Step A).
- With no conflict, ADR-008 has nothing to rank. Whether to merge them, and where, is a convention choice.
- Changing the command's path is a command change, which ADR-007 reserves to you.

| Option | Files that change | Test and tooling impact | Golden impact | Renaming |
|---|---|---|---|---|
| **1. One document, `docs/releases/v<VERSION>.md` (Recommended)** | Skill `release-workflow:56` (R-1), `:129–132` (R-2) and `:160` (R-3). No command, agent, instruction, template or script changes | None. `verify-release-docs.py`, `publish-release.py` and CI already use this path | None. No open case cites `release-workflow`, and nothing quoted changes | None. No `docs/artifacts/release-notes-v*.md` exists (only `v6.4.1` checked) |
| **2. One document, `docs/artifacts/release-notes-v<VERSION>.md`** | Command `/prepare-release:38–39` (C-B2a). Agent `orchestrator.md:132–134` (C-B2b). Skill `release-workflow:160` (R-5). Not knowledge, as specified in §5.2: `docs/releases/_template.md:3`; `scripts/verify-release-docs.py:25`, plus the `"docs/releases/"` README snippet it requires (`:49`); `scripts/publish-release.py:100, :103–104` | The CI release-docs gate and release job read the new path; both stay fail-closed. README and CONTRIBUTING text **(unread)** | None. No open `/prepare-release` case quotes step 7's path, and every fixture is path-agnostic | Historical `docs/releases/v*.md` can stay, because the gate reads only the tag being cut. A document keyed by release version and edited until the tag is cut would sit in `docs/artifacts/`, where `AGENTS.md:22` governs immutable artifacts (O3) |
| **3. Two documents, relationship stated** | Skill `release-workflow:160` (R-4) | None | None | None. Two documents carry the changelog and the verdict, and can drift |
| **4. Defer** | Nothing | None | None | None. The duplication stays unstated |

**Recommendation: option 1.**
1. The published notes, the orchestrator's mandatory tag preflight (which ships to target projects), the release
   template, both CI scripts and every existing release already use `docs/releases/`.
2. Option 1 makes the one remaining document agree with them by editing only the skill. It needs no command decision
   and changes nothing that checks a release.

## 5. Held candidate edits (apply verbatim, only after the user decides)

Each Before is unique in its file (by reading whole files; **unverified by grep**).

### 5.1 Q-P32a

**P-1 — `implementation/knowledge/skills/plan-approve-execute/SKILL.md:20–24`** (options 1, 2, 4). Anchor: `## File
Location` (once).

Option 1:

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

`<ID>` is the plan's three-digit number, a hyphen, and a short kebab-case slug naming the feature or phase, for example `docs/plans/plan-042-rate-limiting.md`. A new plan takes the next number not yet used in `docs/plans/`. Every plan document a command or agent writes under this protocol uses this path.
````

Option 2: the same Before; the After's last paragraph reads instead:

````
`<ID>` is the plan's three-digit number, for example `docs/plans/plan-042.md`. A new plan takes the next number not yet used in `docs/plans/`. Every plan document a command or agent writes under this protocol uses this path.
````

Option 4: the same Before; the After's last paragraph reads instead:

````
`<ID>` is the plan's three-digit number, a hyphen, and a short kebab-case slug naming the feature or phase, for example `docs/plans/plan-042-rate-limiting.md`. A new plan takes the next number not yet used in `docs/plans/`. Every plan document a command or agent writes under this protocol uses this path, except the feature plan `/new-feature` step 1 writes, which uses the path declared there.
````

**P-2 — `plan-approve-execute/SKILL.md:97`** (options 1, 2, 4). Anchor: the full line (once).

````
Before:
Please review the full plan at `docs/plans/plan-<name>.md`.

After (options 1, 2):
Please review the full plan at `docs/plans/plan-<ID>.md`.

After (option 4):
Please review the full plan at `docs/plans/plan-<ID>.md` (for `/new-feature`, the path its step 1 declares).
````

**P-3 — `implementation/knowledge/agents/orchestrator.md:23`** (options 1, 2, 4). Anchor: the full line (once).

````
Before:
4. Write a plan document to `docs/plans/plan-<ID>.md` with:

After:
4. Write a plan document to `docs/plans/plan-<ID>.md` (`<ID>`: skill `plan-approve-execute` § File Location) with:
````

`:56`'s `plan-<ID>.md` takes the same meaning by same-file coherence. It is unchanged.

**P-4 — `implementation/knowledge/commands/new-feature.md:14`** (options 1, 2; **command change, by user decision
only**). Anchor: the full line, three leading spaces (once).

````
Before:
   - Write to `docs/plans/feature-<slug>.md`

After:
   - Write to `docs/plans/plan-<ID>.md`, with `<ID>` as the `plan-approve-execute` skill § File Location defines it
````

**P-5 — `implementation/knowledge/commands/new-project.md:14`** (options 1, 2, 4; **command change, by user decision
only**). Anchor: the full line, three leading spaces (once).

````
Before:
   - Write the plan to `docs/plans/plan-<project-slug>.md`

After:
   - Write the plan to `docs/plans/plan-<ID>.md`, with `<ID>` as the `plan-approve-execute` skill § File Location defines it
````

**P-6 — `implementation/knowledge/skills/project-planning/SKILL.md:163–168`** (options 1, 2, 4). Anchor: begins with
`Plan documents are versioned artifacts stored under` (once).

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

**P-7 — `implementation/knowledge/agents/poc-orchestrator.md:25`** (options 1, 2, 4 unless "production only"; it
reaches `/new-poc`'s imported clause, so it rests on the user's decision). Anchor: the full line (once).

````
Before:
3. Write a lightweight plan in `docs/plans/plan-<ID>.md`:

After:
3. Write a lightweight plan in `docs/plans/plan-<ID>.md` (`<ID>`: skill `plan-approve-execute` § File Location):
````

The golden-quoted words "Write a lightweight plan in `docs/plans/plan-<ID>.md`" survive unchanged.

**P-8, P-9 — `implementation/docs/plans/_template.md:3` and `docs/plans/_template.md:3`** (not knowledge; options 1,
2, 4). Anchor: the full line (once in each).

````
Before:
> Filename convention: `plan-<slug>.md` (e.g. `plan-payment-feature.md`).

After (options 1, 4):
> Filename convention: `plan-<ID>.md`, with `<ID>` as the `plan-approve-execute` skill § File Location defines it (e.g. `plan-042-payment-feature.md`).

After (option 2):
> Filename convention: `plan-<ID>.md`, with `<ID>` as the `plan-approve-execute` skill § File Location defines it (e.g. `plan-042.md`).
````

`:61` ("revisions create `plan-<slug>-v2.md`") is left as it is. It belongs to O1.

**E-C1 — `orchestrator.md:30`** (A-1, Step C; options 3, 4). Anchor: the full line (once).

````
Before:
5. Present a summary to the user and ask: **"Shall I proceed with this plan? You can approve, modify, or reject."**

After:
5. Present a summary to the user and ask: **"Shall I proceed with this plan? You can approve, modify, or reject."**

When this agent runs `/new-feature`, the plan document is the one that command's step 1 writes, at the path declared there: step 4's path does not apply, and the precondition in § Task Management › Creating Tasks refers to that document.
````

**E-C2 — `plan-approve-execute/SKILL.md:20–24`** (A-1, Step C; option 3 only). Anchor: `## File Location` (once).

````
Before:
## File Location

```
docs/plans/plan-<feature-or-phase>.md
```

After:
## File Location

```
docs/plans/plan-<feature-or-phase>.md
```

When the plan is written through `/new-feature`, that command's step 1 path governs.
````

| Option | Edits to apply |
|---|---|
| 1 | P-1 (opt 1), P-2, P-3, P-4, P-5, P-6, P-7, P-8, P-9 ("1, production only": omit P-7) |
| 2 | P-1 (opt 2), P-2, P-3, P-4, P-5, P-6, P-7, P-8 and P-9 (opt 2) |
| 3 | E-C1, E-C2 |
| 4 | P-1 (opt 4), P-2 (opt 4), P-3, P-5, P-6, P-7 (optional), P-8, P-9, E-C1 |

### 5.2 Q-P32b

**R-1 — `implementation/knowledge/skills/release-workflow/SKILL.md:56`** (option 1). Anchor: the full line (once).

````
Before:
5. **Create the release artifact** at `docs/artifacts/release-notes-v<VERSION>.md`.

After:
5. **Write the release notes** to `docs/releases/v<VERSION>.md` (§ 4).
````

**R-2 — `release-workflow/SKILL.md:129–132`** (option 1). Anchor: begins with `### 4. Create Release Artifact`
(once).

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

**R-3 — `release-workflow/SKILL.md:160`** (option 1). Anchor: the full line (once).

````
Before:
File location: `docs/artifacts/release-notes-v<VERSION>.md`

After:
File location: `docs/releases/v<VERSION>.md`, one document per release (above).
````

**R-4 — `release-workflow/SKILL.md:160`** (option 3). Anchor: the full line (once).

````
Before:
File location: `docs/artifacts/release-notes-v<VERSION>.md`

After:
File location: `docs/artifacts/release-notes-v<VERSION>.md`

This artifact is the release's record in `docs/artifacts/`. It is a separate document from the published release notes, `docs/releases/v<VERSION>.md` (the `orchestrator` agent § Release Workflow Preflights), into which `/prepare-release` step 7 writes the `## RELEASE VERDICT` section. Both record the release gate's one verdict, so the `Release` line under `## Gate Verdicts` carries the same value as that section's `**Status**`.
````

**R-5 — `release-workflow/SKILL.md:160`** (option 2). Anchor: the full line (once).

````
Before:
File location: `docs/artifacts/release-notes-v<VERSION>.md`

After:
File location: `docs/artifacts/release-notes-v<VERSION>.md`, one document per release. It is also the release notes document into which `/prepare-release` step 7 writes the `## RELEASE VERDICT` section, and the file the `orchestrator` agent § Release Workflow Preflights publishes. Start it from `docs/releases/_template.md` and add the sections above. When the release is prepared with `/prepare-release`, that command's steps govern the document, and these sections accompany them.
````

**C-B2a — `implementation/knowledge/commands/prepare-release.md:38–39`** (option 2; **command change, by user
decision only**). Anchor: begins with `7. **Produce a structured release gate VERDICT**` (once).

````
Before:
7. **Produce a structured release gate VERDICT** in the release notes document from step 5
   (`docs/releases/v<version>.md`) as a top-level `## RELEASE VERDICT` section. That document is

After:
7. **Produce a structured release gate VERDICT** in the release notes document from step 5
   (`docs/artifacts/release-notes-v<version>.md`) as a top-level `## RELEASE VERDICT` section. That document is
````

**C-B2b — `implementation/knowledge/agents/orchestrator.md:132–134`** (option 2). Anchor: begins with `   - Before
calling `glab release create`` (once).

````
Before:
   - Before calling `glab release create`, verify that `docs/releases/vX.Y.Z.md` exists and is committed
   - Publish/update release notes from that file only: `glab release create vX.Y.Z --ref vX.Y.Z --name vX.Y.Z -F docs/releases/vX.Y.Z.md`
   - Do not pass ad-hoc inline `--notes`; it can drift from `docs/releases/vX.Y.Z.md`

After:
   - Before calling `glab release create`, verify that `docs/artifacts/release-notes-vX.Y.Z.md` exists and is committed
   - Publish/update release notes from that file only: `glab release create vX.Y.Z --ref vX.Y.Z --name vX.Y.Z -F docs/artifacts/release-notes-vX.Y.Z.md`
   - Do not pass ad-hoc inline `--notes`; it can drift from `docs/artifacts/release-notes-vX.Y.Z.md`
````

**Option 2, not knowledge (a specification for the implementing task; not code written here):**
1. `docs/releases/_template.md:3`: the copy target becomes `docs/artifacts/release-notes-vX.Y.Z.md`. The template
   stays where it is, and `verify-release-docs.py:38` still requires it.
2. `scripts/verify-release-docs.py:25`: `release_brief_path` returns `docs/artifacts/release-notes-<tag>.md`. Check
   whether README still needs `"docs/releases/"` (`:49`).
3. `scripts/publish-release.py:100`: the same path. `:103–104`: the error message names the new path.

| Option | Edits to apply |
|---|---|
| 1 | R-1, R-2, R-3 |
| 2 | C-B2a, C-B2b, R-5, and the three non-knowledge items |
| 3 | R-4 |
| 4 | none |

## 6. Constraints check and golden coupling

### 6.1 Per-edit statements

| Edit | Upward? | Relaxes a check? | Reopens an input? | Golden: quote / fixture / result |
|---|---|---|---|---|
| P-1, P-2 | No (a skill) | No | No | None / none / none. `validate-workflow-gate-verdict-sources` cites `plan-approve-execute` § The Three Phases › Phase 2: Approve by name only, and holds no copy of the skill (removed by T568). P-2 edits text inside Phase 2 but changes no heading |
| P-3, E-C1, C-B2b | No (an agent) | No | No | None / none / none. The same case cites `orchestrator` § Core Workflow and § Validation Gates by name only |
| P-4 | **Command change by user decision**, not on the strength of a skill or agent | No: the clause still names exactly one path | No | `new-feature-plan-doc-compliant`: **quote changes** (`brief.md:11–13`); fixture and `check()` untouched, so the result stays green but stale. Realignment (glob `feature-*.md` → `plan-*.md`, fixture rename, brief text) needs a grant and v18. `new-feature-checkpoint-line-compliant` and `new-feature-real-checkpoint-format-drift` quote step 7 only: none / none / none |
| P-5 | **Command change by user decision** | No | No | **Not pre-computed** (§6.2) |
| P-6 | No (a skill) | No | No | None (no open case cites it) |
| P-7 | No (an agent); reaches `/new-poc`'s imported clause, so it rests on the user's decision | No | **No**: P11's form `plan-<ID>.md` stays, and only the slot P11 left open is filled | `new-poc-plan-hypothesis-format`: quote unchanged (`brief.md:58`'s words survive), fixture unchanged, result unchanged. Under option 1, the fixture name `plan-001.md` and `brief.md:59–61` become a non-conforming example and stale description; refreshing them is optional (grant + v18) |
| P-8, P-9 | Not knowledge | No | No | None |
| E-C2 | No (a skill) | No | No | None |
| R-1 to R-5 | No (a skill) | No | No | None |
| C-B2a | **Command change by user decision** | No: the section stays required at one path | No | `prepare-release-real-verdict-missing`, `prepare-release-conditional-pass-conditions-gap` and `prepare-release-changelog-grouping-compliant` quote step 7's fields, step 9 and step 2, not step 7's path, and their fixtures are path-agnostic: none / none / none |

**Only the recommended Q-P32a option needs a protected-path grant and a v18 baseline**, and only to realign
`new-feature-plan-doc-compliant`. Q-P32b's recommended option needs neither.

### 6.2 Corrections to the pre-computed coupling table (brief §2.5)

1. `agents/poc-orchestrator.md` is listed with "none". But `new-poc-plan-hypothesis-format/brief.md:58` quotes
   `poc-orchestrator`'s PLAN PHASE line verbatim. P-7 is worded so that the quote survives.
2. `commands/new-project.md` is not in the table. P-5 edits it. Its open-case coupling must be computed before an
   option that includes P-5 is implemented. I did not search for it and name no case.

## 7. Amendment list and hit counts

Case-sensitive, fixed-string, per file, after all of that option's edits in that file. **Lines** = `grep -cF`;
**occurrences** = `grep -oF … | wc -l`. Before counts are at `c152eb7`, by reading **(unverified by grep)**. "→ 0"
rows test that the old wording is gone.

**Q-P32a, option 1 (recommended):**

| # | File | Phrase | Before (lines / occ.) | After | Edit |
|---|---|---|---|---|---|
| 1 | `skills/plan-approve-execute/SKILL.md` | `plan-<feature-or-phase>` | 1 / 1 | **0 / 0** | P-1 |
| 2 | same | `plan-<name>` | 1 / 1 | **0 / 0** | P-2 |
| 3 | same | `docs/plans/plan-<ID>.md` | 0 / 0 | 2 / 2 | P-1, P-2 |
| 4 | same | `plan-042-rate-limiting.md` | 0 / 0 | 1 / 1 | P-1 |
| 5 | same | `## File Location` | 1 / 1 | 1 / 1 | anchor survives |
| 6 | `agents/orchestrator.md` | `docs/plans/plan-<ID>.md` | 2 / 2 (`:23`, `:56`) | 2 / 2 | P-3 |
| 7 | same | `§ File Location` | 0 / 0 | 1 / 1 | P-3 |
| 8 | `commands/new-feature.md` | `feature-<slug>` | 1 / 1 | **0 / 0** | P-4 |
| 9 | same | `docs/plans/plan-<ID>.md` | 0 / 0 | 1 / 1 | P-4 |
| 10 | same | `plan-approve-execute` | 1 / 1 (`:16`) | 2 / 2 | P-4 |
| 11 | `commands/new-project.md` | `plan-<project-slug>` | 1 / 1 | **0 / 0** | P-5 |
| 12 | same | `docs/plans/plan-<ID>.md` | 0 / 0 | 1 / 1 | P-5 |
| 13 | `skills/project-planning/SKILL.md` | `project-plan-v` | 2 / 2 | **0 / 0** | P-6 |
| 14 | same | `docs/plans/plan-<ID>.md` | 0 / 0 | 1 / 1 | P-6 |
| 15 | same | `plan-approve-execute` | 2 / 2 (`:153`, `:156`) | 4 / 4 | P-6 |
| 16 | `agents/poc-orchestrator.md` | `Write a lightweight plan in `docs/plans/plan-<ID>.md`` | 1 / 1 | 1 / 1 | P-7 (golden quote survives) |
| 17 | same | `plan-approve-execute` | 0 / 0 | 1 / 1 | P-7 |
| 18 | each `_template.md` | `plan-<slug>.md` | 1 / 1 | **0 / 0** | P-8 / P-9 |
| 19 | each `_template.md` | `plan-<slug>` | 2 / 2 | 1 / 1 (`:61`) | P-8 / P-9 |

**Option 2:** rows as option 1, except row 4 becomes `plan-042.md` (0 / 0 → 1 / 1) in the skill.

**Option 3:** `orchestrator.md`: `/new-feature` 0 / 0 → 1 / 1 (E-C1). `plan-approve-execute`: `/new-feature` 0 / 0 → 1 / 1
(E-C2), and `plan-<feature-or-phase>` stays at 1 / 1.

**Option 4:** as option 1, except: rows 8–10 are unchanged (`feature-<slug>` stays 1 / 1); `plan-approve-execute` gains
`/new-feature` 0 / 0 → 2 / 2 (P-1 and P-2, one line each); `orchestrator.md` gains `/new-feature` 0 / 0 → 1 / 1 (E-C1).

**Q-P32b:**

| # | File | Phrase | Before | After | Option / edit |
|---|---|---|---|---|---|
| 20 | `skills/release-workflow/SKILL.md` | `docs/artifacts/release-notes-v<VERSION>.md` | 2 / 2 | **0 / 0** | 1: R-1, R-3 |
| 21 | same | `docs/releases/v<VERSION>.md` | 0 / 0 | 3 / 3 | 1: R-1, R-2, R-3 |
| 22 | same | `/prepare-release` | 0 / 0 | **1 / 2** (two on R-2's line) | 1: R-2 |
| 23 | same | `### 4. Create Release Artifact` | 1 / 1 | 1 / 1 | anchor survives |
| 24 | same | `docs/releases/v<VERSION>.md` | 0 / 0 | 1 / 1 | 3: R-4 |
| 25 | `commands/prepare-release.md` | `docs/releases/v<version>.md` | 1 / 1 | **0 / 0** | 2: C-B2a |
| 26 | `agents/orchestrator.md` | `docs/releases/vX.Y.Z.md` | 3 / 3 | **0 / 0** | 2: C-B2b |
| 27 | same | `docs/artifacts/release-notes-vX.Y.Z.md` | 0 / 0 | 3 / 3 | 2: C-B2b |

**Mechanics for the implementing task.**
1. Apply each edit by its Before, which must match exactly once at dispatch.
2. Run `node implementation/scripts/sync.mjs --root implementation` and
   `python3 implementation/scripts/generate-registry.py`, each followed by `--check`.
3. Declare root drift as `--print-drift` reports it.
4. Confirm that `scripts/scorecard.py --check` matches the current baseline (unless a granted realignment moves it to
   v18), that `check-maturity.py --root implementation` reports 0 failing, and that
   `python3 docs/tasks/validate-tasks.py` passes.
5. Confirm that `AGENTS.md`, every instruction, `/plan`, `/batch`, `/new-poc` and `tests/golden/**` are byte-unchanged,
   except as a grant permits.

## 8. Observations (not ruled; candidates for parking)

- **O1: plan-file versioning against `coding-standards` (A-2′).**
  - `coding-standards:66–83` requires `<type>-vN.md` for "All plan, decision, and documentation artifacts".
  - Its reach to plan files is contested (A-2, Step B).
  - The same table contradicts `AGENTS.md:27` (`checkpoint-vN.md`) and `AGENTS.md:33` (`decision-vN.md`), within tier
    1.
  - The templates' `:61` `plan-<slug>-v2.md` and `plan-approve-execute:182` (a superseding *new* plan) also describe
    revisions differently.
  - Suggested trigger: the next task touching `coding-standards.md` § Artifact Versioning & File Naming, or the first
    plan revision. Any fix to `coding-standards` itself is an instruction-change task (ADR-008 P1 Remedy).
- **O2: `/new-project` against `AGENTS.md`.** `:43` "Write checkpoint to `docs/checkpoints/checkpoint-<phase>.md`"
  against `AGENTS.md:27`, and `:51` "Format: `<artifact-name>-v<major>.<minor>.md`" against `AGENTS.md:22`. These have
  the shape T515 row B ruled at ADR-007 branch 1 for `/new-feature`. Not in brief §1.
- **O3: release notes under `docs/artifacts/`.** Whether a release-version-keyed document meets `AGENTS.md:22`'s
  `<type>-v<N>.md` is not visible in `AGENTS.md`'s own text. It matters only under Q-P32b option 2.
- **O4: stale golden description.** `plan-required-sections-compliant/brief.md:12, :17` still say
  `docs/plans/<slug>-plan.md` and `fixture/docs/plans/*-plan.md`, while its `expect.py:33` globs `plan-*.md` (realigned
  after T515 verdict A). This is a golden matter, flagged only.
- **O5: `/new-feature:25`** "Have the Scrum Master create tasks" against `AGENTS.md:18` "Only orchestrators
  create/transition tasks". This is G7's shape. Not in scope.
- **O6: a third generated file.** CI writes `release-notes.md` at the repository root (`publish-release.py:210–211`;
  `.gitlab-ci.yml:206`). It is the `docs/releases` document plus a commit changelog. It is generated, not knowledge,
  and is noted because Q-P32b talks about "one document".

## 9. Unverified claims (need a shell)

1. The worktree commit `c152eb7`, as stated by the orchestrator.
2. Every anchor's uniqueness and every count in §7, all by reading, not `grep`.
3. That every real plan in `docs/plans/` has the `plan-<NNN>-<slug>.md` form. Four were opened.
4. That no `docs/artifacts/release-notes-v*.md` exists. Only `v6.4.1` was checked.
5. That no command other than the six read names `project-planning` or `release-workflow`, or writes a plan or
   release-notes path.
6. That no non-golden test asserts any changed string: `feature-<slug>`, `plan-<feature-or-phase>`, `plan-<name>`,
   `plan-<project-slug>`, `project-plan-v`, `docs/artifacts/release-notes-v<VERSION>.md`.
7. The fixture filename in `plan-required-sections-compliant/fixture/docs/plans/`. Its `check()` globs `plan-*.md`, so
   no option changes its result either way.
8. Whether `audience: authoring` (`/prepare-release:6`) keeps the command out of target projects. It affects only the
   context of Q-P32b option 1, not its edits.
9. That `/new-feature:3` and `project-planning:153` read as they do now at `8535dca`, the commit where P32 was first
   recorded. Only A-1 relies on the former, and nothing relies on the latter.
10. The README and CONTRIBUTING text that Q-P32b option 2 would touch.

## 10. Summary

| Item | Subject | Step fired | Outcome | Edits | User decision? |
|---|---|---|---|---|---|
| A-1 | Plan path under `/new-feature` | **C (P2)** | The command's path governs over `orchestrator` and `plan-approve-execute` under `/new-feature`. Edit held for sequencing | E-C1, E-C2 (options 3, 4) | Sequencing only |
| A-2 | `<ID>`; the `plan-` family; `project-planning`; the track convention | **E (P5)** | Escalated: **Q-P32a**; recommended option 1 (`plan-<NNN>-<slug>.md`, both tracks) | P-1 to P-9 per option | **Yes** |
| A-2′ | Plan-file versioning against `coding-standards` | — (split off; Step B not shown) | Observation O1, recommended for parking | none | Park |
| B-1 | Release-notes path; one document or two | **A** | No contradiction; the convention is escalated: **Q-P32b**; recommended option 1 (`docs/releases/v<VERSION>.md`) | R-1 to R-5, C-B2a/b per option | **Yes** |

- **Maturity, corpus counts, majority practice and golden-coupling convenience** were relied on nowhere as authority.
  Practice is offered only as a consideration for the user's choice.
- **No edit is upward or relaxing, and no input is reopened.** A command changes only under an option the user chooses
  (P-4, P-5, C-B2a, and P-7 through `/new-poc`'s import).
- **Golden:** the recommended Q-P32a option changes one quote and leaves one green case stale. Its realignment needs a
  protected-path grant and a user-authorized v18. The recommended Q-P32b option touches nothing golden.
- **Blockers:** none. Q-P32a and Q-P32b are ruling outcomes, not blockers.
