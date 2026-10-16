# Artifact: task-protocol-observations-ruling-v1.md

> Filename: `task-protocol-observations-ruling-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T617 (P2, judgment tier, decision only)
- **Created**: 2026-10-09
- **Based on:**
  - `docs/tasks/task-T617.md` (the brief, authoritative);
  - `docs/plans/plan-119-task-protocol-observations-o1-o12.md`;
  - `docs/artifacts/task-protocol-skill-conflicts-ruling-v1.md` §7 (the twelve observations O-1..O-12 with quotes and
    readings), §4.6, §5.2, §5.4 (the T615 ruling; its items 1 to 6 were applied by T616);
  - `docs/artifacts/task-protocol-and-checkpoint-name-ruling-v1.md` (the S1/S2/K model) and
    `docs/artifacts/naming-conflicts-ruling-v1.md` (the O1/O2/O5 model; §5.1 gives the projection counts used below);
  - `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted) and
    `docs/decisions/ADR-007-command-contract-authority.md` (Accepted);
  - `AGENTS.md` § Lifecycle States, § Task Protocol, § Checkpoint Protocol, § Blocker Protocol, § Validation Gates (root
    copy `:8–11`, `:13–19`, `:26–30`, `:46–49`, `:51–55`; `implementation/AGENTS.md:1–35` carries the same lines, re-read);
  - the user's instruction of 2026-10-09, "Continue with the twelve observations";
  - the user's decisions of 2026-10-09 on the same class of conflict, as the orchestrator relayed them: the recommended
    amendment toward `AGENTS.md` for T607 O1/O2/O5, T613 S1/S2/K and every item of T615 (the orchestrator writes the ledger;
    the ledger has seven columns; `AGENTS.md` names win over agents, skills and commands). I honor them as precedent and do
    not re-litigate them.
- **Supersedes**: none (first version).
- **Decision references**: ADR-008 Step A (P3a), Step B (P1), D2, D3, D4, D5, P4, P5; ADR-007 branch 1 (including its
  same-file prong and sibling corollary) and §5 (never relax a check). No new ADR is minted.
- **Status of every edit in this document**: **held for the user. Nothing is applied.** The only other file changed by this
  task is the `**Status:**` line of `task-T617.md`.

## 0. Method and limits

- **Commit.** The orchestrator states the worktree is on `develop` `03f9c2b` plus one scoping commit **(unverified: no shell,
  no `git`)**. T616 has already applied the T615 edits, so the live text differs from the T615 artifact. I re-read every
  clause below in the worktree, in the source files under `implementation/knowledge/`. I trusted no earlier line number.
  T615 §7 cites `blocker-escalation:148, :165`; the lines are `:147, :163` live.
- **No shell and no grep tool.** Every count in §4 comes from reading files and is **(unverified by grep)**. §7.2 lists the
  greps the implementing task must run first. §9 collects every unverified claim.
- **Read in full (source files):** `AGENTS.md:1–60`, `implementation/AGENTS.md:1–36`; skills `blocker-escalation`, `task-management`,
  `gitlab-management`, `checkpoint-protocol`, `release-workflow`, `plan-approve-execute`, `validation-gates`;
  agents `orchestrator`, `scrum-master`, `release-manager`; commands `prepare-release`, `team-status`, `validate-workflow`,
  `bug-report`, `handoff`, `sprint-status`, `plan`, `code-review`; instruction `coding-standards`; `docs/checkpoints/_template.md`;
  `implementation/runtime/handoff/schema-v1.json`; `docs/tasks/active-tasks.md`. `docs/tasks/validate-tasks.py` was read at
  `:1–150` only.
- **Read in part (the clause lines and their surroundings):** skills `code-review` (`:110–164`), `testing-strategy`
  (`:205–254`), `ci-cd-pipeline` (`:160–181`), `verification-before-completion` (`:1–93`), `systematic-debugging`
  (`:75–101`), `technical-debt-tracking` (`:80–139`); agents `tech-lead` (`:80–129`), `frontend-developer` (`:80–109`),
  `backend-developer` (`:60–129`), `qa-engineer` (`:90–169`).
- **Also read:** `ADR-008` in full; `ADR-007` (`:1–120`); the T615 artifact in full; the T613 artifact (`:1–320`) and the T607 artifact
  (`:1–80`, `:330–460`). The other agents, skills and commands that T615 §0 lists are not re-read. T615 found them conforming; I
  rely on that only where I say so, and mark it **(unverified)**.
- **Golden.** I opened only `tests/golden/open/` case directories: `brief.md` of `prepare-release-changelog-grouping-compliant`,
  `prepare-release-conditional-pass-conditions-gap`, `prepare-release-real-verdict-missing`, `team-status-dag-colour-code`,
  `bug-report-severity-priority-ledger-row`, `validate-workflow-gate-verdict-sources`, `code-review-conditional-pass-conditions-gap`,
  `code-review-fail-blocker-details` and `skillify-skill-file-template-drift` (`:1–80`), and `expect.py` of the first, second,
  third, fourth and fifth of those. Every golden case name in this document has a `tests/golden/open/` directory.
  **I never opened `tests/golden/held-out/`, so held-out coupling is unknown and was not checked.** To find the open case names
  I read `tests/golden/_manifest-t411.md` and `docs/benchmarks/scorecard-v6.12.0.md`, files outside `held-out/`. I use nothing
  from them about a held-out case, I name none, and I did not design any ruling around the held-out set.
- **Secrets.** I read no `.env*`, credential or key file. I edited nothing under `.claude/`, `.github/` or any other derived
  platform folder, and nothing outside this artifact and the brief's `**Status:**` line. I read `scripts/scorecard.py` (the
  first 140 lines) and `docs/artifacts/evaluator-hash-known-good-v20.json`; I wrote nothing near them.
- **Encoding.** `§` is U+00A7 and `—` is U+2014. Each four-backtick fence holds one Before/After pair; inner single and triple
  backticks are literal. Apply each edit by its Before text, never by line number. Match every single-line Before as a **whole
  line** (`grep -cxF`), including its leading spaces.
- **Scope-gaming guard (ADR-008 § Risks).** O-1 to O-12 were first recorded in T615 §7 on 2026-10-09, before this task. The
  clauses ruled below are where T615 read them (apart from the two shifted line numbers above), and no declared-scope sentence
  relied on below was added in the same change as this ruling **(unverified: I cannot diff history)**.
- **Maturity.** I relied on no `maturity:` value anywhere in this document (P4). `team-status` and `checkpoint-protocol` and
  `release-manager` are `stable`; `blocker-escalation`, `prepare-release`, `release-workflow`, `orchestrator`, `task-management`,
  `plan-approve-execute`, `code-review`, `testing-strategy`, `ci-cd-pipeline` and `/plan` carry the values in their
  frontmatter, and none of that decides any step below. `AGENTS.md` is tier 1 by ADR-008 D1. The agreement of other files with
  `AGENTS.md` (for example three agent files that already use the `AGENTS.md` severity set) appears only as a witness, never as
  authority (P4(e)).

## 1. Disposition of O-1..O-12

| Obs. | Subject (D3) | Disposition | Step that fired | Held edits |
|---|---|---|---|---|
| **O-1** | The value set of a blocker's severity | **Rule** (real conflict) | Skill: **B (P1)**. Command `team-status`: **B (ADR-007 branch 1)**. Not inside tier 1, so no P5 | O1-a to O1-d (`blocker-escalation`), O1-e (`team-status`) |
| **O-2** | The file name of a release checkpoint | **Rule** (real conflict, a command) | **B (ADR-007 branch 1)**, with the same-file prong as a second ground | O2-a (`prepare-release`) |
| **O-3** | Where a completed task is looked for when a release is checked | **Step A holds**; note-level edits held | **A** (T615's "can never be tested" reading rejected, §2.3) | O3-a (`release-workflow`), O3-b (`orchestrator`) |
| **O-4** | (a) the actor that logs a follow-up; (b) the fields a logged follow-up carries | **(a) Step A holds; (b) rule** | (a) **A**; (b) **B (P1)** | O4-a to O4-d (3 skills) |
| **O-5** | The Scrum Master "assigns tasks" | **Step A holds / no edit** | **A** | none |
| **O-6** | `verification-before-completion` "marking a task `done` in `active-tasks.md`" | **Step A holds / no edit** | **A** | none |
| **O-7** | The `NEVER T001` typo in `task-management` | **Typo (same-file defect)** | ADR-008 § Scope (same-file coherence) | O7-a |
| **O-8** | `priority::` labels and "Must Have" against `P0`/`P1`/`P2` | **Step A holds / no edit**; no mapping needed now | **A** | none |
| **O-9** | The plan's Task Breakdown table against the ledger columns | **Step A holds**; a mapping is needed, at `plan-approve-execute:122` | **A**, note-level | O9-a, O9-b |
| **O-10** | `Assignee` against `Owner` in the checkpoint skill and template | **Step A holds**; not a Task Protocol conflict; cosmetic edit held | **A** (the template is outside ADR-008) | O10-a, O10-b |
| **O-11** | `active-tasks.md` leftover blockquote text | **Not a knowledge file: report only** | none | none (orchestrator tidies) |
| **O-12** | `technical-debt-tracking:95` debt `Status` | **Lookalike** (record) | none | none |

Disposition counts (12 observations): 2 rule (O-1, O-2); 1 split (O-4: 4a Step A holds with a held note, 4b rule); 3 Step A
with held note-level edits (O-3, O-9, O-10); 3 Step A with no edit (O-5, O-6, O-8); 1 typo (O-7); 1 lookalike (O-12); 1
report-only (O-11).

**No conflict is inside tier 1.** The only tier-1 text on blocker severity is `AGENTS.md:48`; `security-guidelines`
(`SECURITY:CRITICAL/HIGH/MEDIUM/LOW`) and `poc-guidelines` (debt severity `Critical`/`Medium`/`Low`) grade other objects
(§2.1). The only tier-1 text on the checkpoint name is `AGENTS.md:27`, and `coding-standards:73, :88` already repeat it. So
nothing escalates under P5. Two user options change a tier-1 file instead (1-C, 2-C in §6). ADR-008 P1 never amends tier 1 on
its own, so I draft no edit for them.

## 2. D5 records

### 2.1 O-1: the value set of a blocker's severity

**Verbatim clauses (live, source files).**

Tier 1, `AGENTS.md` (identical in `implementation/AGENTS.md`):
- `:44` "7. **Blocker Protocol** — reminder to report blockers with type and severity"
- `:46–49` "## Blocker Protocol" / "- Types: `technical` | `dependency` | `unclear_requirements` | `external`" / "- Severities: `critical` | `major` | `minor`" / "- Max 2 retries before user escalation. Agents MUST NOT silently fail."

`implementation/knowledge/skills/blocker-escalation/SKILL.md`:
- `:3` (description) "Handle and escalate blockers using the structured escalation protocol. …"
- `:22–27` the Blocker Types table, whose four values are the `AGENTS.md:47` types verbatim
- `:31` "When filing a blocker, create a report with this structure:" and `:38` "- **Severity:** critical | high | medium | low"
- `:50–57` "### Severity Definitions" and the table rows "| `critical` | Blocks the critical path; no workaround; project timeline at risk |", "| `high` | Blocks multiple tasks or a high-priority task; workaround is costly |", "| `medium` | Blocks a single non-critical task; workaround available |", "| `low` | Minor inconvenience; does not block progress |"
- `:147` "- **Severity:** high" (Technical Blocker example) and `:163` "- **Severity:** medium" (Unclear Requirements example)
- `:79` "5. Send the Blocker Report to the orchestrator." (the skill places itself under the orchestrator's triage)

`implementation/knowledge/commands/team-status.md` (a command; `agent: "orchestrator"`):
- `:19` "2. Blockers (severity, owner, age, mitigation, escalation status)"
- `:64–66` "| # | Blocker ID | Severity | Owner | Age (days) | Blocked Tasks | Mitigation | Escalation |" and "| 1 | ... | CRITICAL/HIGH/MEDIUM | ... | ... | [task IDs] | ... | ... |"

Witnesses that already use the tier-1 set (not authority): `frontend-developer:93` and `backend-developer:99` "3. Assign severity: `critical` (work stopped) | `major` (significant impact) | `minor` (workaround exists)"; `systematic-debugging:91` "1. Report blocker type `technical`, severity `major`".

**Subject (D3).** The value set of the severity of a blocker (a blocker report, the blocker table of a status report). One subject.
The same clause is repeated at three sites in one skill (set line, definitions, examples) and in one command (the blocker table).

**Other objects that look alike and are not this subject.** `validation-gates:76–81` (severity of a gate *finding*: `critical`/`high`/`medium`/`low`);
`validate-workflow:66` "Severity (CRITICAL/HIGH/MEDIUM/LOW)" (severity of a *remediation backlog item*);
`bug-report:20` "[Critical | High | Medium | Low]" (severity of a *bug*); `security-guidelines` § Security Review Workflow
(`SECURITY:*` grades of a *finding*); `poc-guidelines` § Debt Scorecard and `technical-debt-tracking:85` (severity of a *debt item*);
`team-status:88` "[low|medium|high] saturation" (a workload level). None of these is a blocker, so each stays as it is (lookalikes).
`validate-workflow:66` is the closest: its backlog items are issues found by a validation run, and Blocker Protocol blockers
are raised by an agent that cannot proceed. T615 grouped it with O-1; I separate it.

| Field | Content |
|---|---|
| **Step A** | **Fails.** MUSTs: `blocker-escalation:31` is an imperative ("create a report with this structure") whose `:38` slot fixes the value set; `AGENTS.md:44` and `:48` fix the set for every blocker report. **Exclusivity:** `AGENTS.md:48` fixes a closed value set for the same field (P3a step 2). **One-value test:** a blocker that blocks several tasks with a costly workaround is `high` by `:55` and `major` by `AGENTS.md:48`; the two texts compute different tokens for one blocker. Only `critical` is shared. **Rescue reading (ii), recorded and rejected:** read `high` as a sub-grade that nests inside `major` (D4, "uses values that nest inside the other's"). The skill carries no sentence that maps its four tokens to the three, so a report written to the skill has a token outside the set, and a reader cannot tell whether `medium` is `major` or `minor`. A nesting needs a stated mapping; there is none. For `team-status:66` the same holds: a `major` blocker has no row value to render as. |
| **Step B (P1; for the command, ADR-007 branch 1)** | **Fires.** (a) *Quotable:* `AGENTS.md:48` and `blocker-escalation:38`, `team-status:66`, above. (b) *Reach, declared-scope text relied on:* `AGENTS.md` declares no scope narrower than the repository (D2), and its § Blocker Protocol is a section about blockers' type and severity. The skill places itself inside it: it adopts the `AGENTS.md:47` type set verbatim (`:22–27`), its description (`:3`) names the blocker protocol, and `:79` and `:81` route the report to the orchestrator. The command places itself inside it by naming "Blockers (severity, …)" (`:19`) and a Blocker Summary table (`:60–66`) for the orchestrator. (c) Step A fails. (d) The other documents are a skill and a command; for the command, P1 *is* ADR-007 branch 1 unchanged. |
| **Step fired** | **B (P1)** for the skill; **B (ADR-007 branch 1)** for `team-status`. |
| **Tier 1 and P5** | Not escalated. No other tier-1 text sets a blocker severity (§1). The user may want the four-level scale instead; that is a change to `AGENTS.md:48`, which ADR-008 P1 never makes on its own ("This ADR never amends a tier-1 document to match a lower one"). It is option 1-C in §6, with its cost, and is not recommended. |
| **Amendment** | **Amend the skill and the command** toward `AGENTS.md:48`. O1-a to O1-d move `blocker-escalation` to `critical | major | minor`. The criteria are kept, regrouped by what each old value already said: `high` becomes `major`; `medium` and `low` (the cases with a workaround or no blocking effect) become `minor`. O1-e changes the one table value in `team-status`. Both cite `AGENTS.md` and do not restate its rules at length. The blocker type set, the 2-retry rule and the escalation path (`severity = critical`) are untouched. **The regrouping coarsens four levels to three, and that is a design choice for the user to see** (1-A). |
| **Not changed** | `validate-workflow:66`, `validation-gates` severities, `bug-report:20`, `team-status:88`, `technical-debt-tracking:85–86`: other objects. |
| **Maturity** | Not relied on. |

### 2.2 O-2: the file name of a release checkpoint

**Verbatim clauses (live).**

Tier 1, `AGENTS.md:27` "- Checkpoints: `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`"; `:28` "- Written at every phase boundary by the orchestrator."
Repeated by `instructions/coding-standards.md:73` "- Checkpoints: `checkpoint-<SEQ>-<phase>.md` (`AGENTS.md` § Checkpoint Protocol)" and `:88`
(a stable instruction, which agrees with `AGENTS.md`); by `skills/checkpoint-protocol/SKILL.md:44` and `:47–51`
(`<SEQ>` "is a sequential integer (zero-padded, e.g. `001`, `029`)", "This matches `AGENTS.md`'s Checkpoint Protocol section verbatim");
and by `docs/checkpoints/_template.md:3` "> Filename: `checkpoint-<SEQ>-<phase>.md` (e.g. `checkpoint-002-architecture.md`)."

`implementation/knowledge/commands/prepare-release.md` (`agent: "orchestrator"`):
- `:29` "   - Create a release checkpoint: `docs/checkpoints/checkpoint-release-v<version>.md`, based on"
- `:30` "     `docs/checkpoints/_template.md` (including its `## Maturity distribution` section — regenerate"

**Subject (D3).** The file name of a checkpoint (here, the one `/prepare-release` writes).

| Field | Content |
|---|---|
| **Step A** | **Fails.** `AGENTS.md:27` fixes the path as `checkpoint-<SEQ>-<phase>.md`. `prepare-release:29` fixes it as `checkpoint-release-v<version>.md`. **One-value test:** if the 37th checkpoint is the release checkpoint of v6.9.0, `AGENTS.md:27` computes `checkpoint-037-<phase>.md` and the command computes `checkpoint-release-v6.9.0.md`; the file names differ. **Rescue reading (ii), recorded and rejected:** read `release` as the `<SEQ>` slot and `v<version>` as `<phase>`. `<SEQ>` is "a sequential integer" (`checkpoint-protocol:47`), and `release` is not one. **Second ground, same-file prong:** the command tells the orchestrator to base the checkpoint "on `docs/checkpoints/_template.md`" (`:29–30`). Text a command imports by reference is a clause of the command (ADR-008 P2 Remedy), and the template's `:3` gives the other name. So the command also contradicts the document it imports. |
| **Step B (ADR-007 branch 1)** | **Fires.** (a) *Quotable:* `AGENTS.md:27` and `prepare-release:29`, above. (b) *Reach:* `AGENTS.md:27–28` name checkpoints and the phase boundary; the orchestrator's own Checkpoint Management lists "release" among the phases (`orchestrator.md:151`, "planning → architecture → implementation → qa → release"). The command places a release checkpoint inside it by taking the template. (c) Step A fails. (d) A command: ADR-007 branch 1 names `AGENTS.md` and "another clause of the same command file". |
| **Step fired** | **B (ADR-007 branch 1).** |
| **What does not decide it** | The real files. At least one real release checkpoint is named `checkpoint-release-v6.4.1.md` (it is the source of the fixture of `prepare-release-real-verdict-missing`), and the brief of `prepare-release-changelog-grouping-compliant` says real release checkpoints use `checkpoint-release-v*.md`. That is practice. "Popularity is not authority" (ADR-007; ADR-008 P4(e)). Frozen historical files are not renamed (ADR-007 branch 3b). The amendment applies to the next release checkpoint onwards. |
| **Amendment** | **Amend the command** toward `AGENTS.md:27`, `release-v<version>` filling `<phase>`: `checkpoint-<SEQ>-release-v<version>.md`. The amendment changes only a name (ADR-007 corollary, branch 1 row 1): the paired cases survive, and the open cases need no fixture or glob update (§5.2). It tightens the contract (adds `<SEQ>`) and relaxes nothing (ADR-007 §5). **Not decided here:** whether `<phase>` may contain dots (`v6.9.0`). `AGENTS.md:27` gives `<phase>` no character set; only `checkpoint-protocol:47` calls it "kebab-case". The command already uses the same `v<version>` token, so I rule that the slot accepts it (D4, "fills a slot the other leaves open"). A dot-free form is a cosmetic choice for the user and does not change the ruling. |
| **Maturity** | Not relied on. |

### 2.3 O-3: completed tasks looked for in the active ledger when a release is checked

**Verbatim clauses (live).**

Tier 1: `AGENTS.md:15` "- **INVARIANT:** `active-tasks.md` MUST NEVER hold a `done` or `cancelled` row. Terminal rows move to `docs/tasks/completed-tasks.md` … in the same edit."

- `skills/release-workflow/SKILL.md:51–53` "2. **Verify all planned tasks are complete:**" / "   - Check `docs/tasks/active-tasks.md` — no tasks for this release should be `in_progress` or `blocked`." / "   - All planned tasks should be `done` or archived."
- `skills/release-workflow/SKILL.md:117` "- [ ] All planned tasks completed and archived" (consistent)
- `agents/orchestrator.md:143–146` "3. **Release Blocking Conditions:**" … "   - All task statuses in `docs/tasks/active-tasks.md` matching the release scope must be `done`"
- Context: `commands/prepare-release.md:17` "Read `docs/tasks/completed-tasks.md` for all tasks completed since last release" (correct) and `:34` (see §8, N-1).

**Subject (D3).** The ledger in which "the release scope is complete" is tested.

| Field | Content |
|---|---|
| **Step A** | **Holds for both.** `release-workflow:53` "`done` or archived" is a disjunction, and "archived" is the only state a `done` task can be in (`AGENTS.md:15`), so the line is obeyed by a ledger with no scoped row left. `orchestrator:146` is a universal statement: every row of `active-tasks.md` that matches the release scope must be `done`. The ledger can never hold a `done` row, so the statement is true exactly when no row matches the release scope. That is testable, and it is the intended gate: a scoped task that is not finished is still a row there (`pending`, `in_progress`, `blocked` or `in_review`), and a finished one is gone. **One-value test:** for one release, "is the scope complete?" computes the same answer under `orchestrator:146` and under `AGENTS.md:15` (yes iff no scoped row remains). **T615's reading is considered and rejected:** it said the condition "can never be tested as written". A universal predicate over an empty set is true, and over a non-empty set it fails, so it can be tested. **The hazard is real:** a reader who takes "must be `done`" as "find `done` rows" finds none and blocks a release that is ready. That is a note-level problem (ADR-008 Step A: "at most a note stating the relationship"). |
| **Step fired** | **A.** No contradiction, so no rank. If the user prefers the T615 reading (Step B), the held edit is the same text, so the conclusion does not depend on it. |
| **Amendment** | Held, note-level: O3-a states where a finished task is (`completed-tasks.md`); O3-b rewrites the condition to the equivalent test "no scoped task remains" and cites `AGENTS.md`. O3-a and O3-b are consistent with each other and with `release-workflow:117`. |
| **Declared-scope text** | Not needed for a Step A ruling. |
| **Maturity** | Not relied on. |

### 2.4 O-4: follow-up items logged to the active ledger (actor, and the fields)

**Verbatim clauses (live).**

Tier 1: `AGENTS.md:55` "- `CONDITIONAL_PASS` proceeds with tracked conditions added to the task list."; `:54` "- `FAIL` blocks progression. Orchestrator creates fix tasks and re-routes."; `:14` (the seven columns); `:18` "- Only orchestrators create/transition tasks. Agents report completion and blockers."

- `skills/code-review/SKILL.md:130` "| `CONDITIONAL_PASS` | Only should-fix findings. Code may merge with tracked follow-ups. | Pipeline proceeds; follow-up items logged to `docs/tasks/active-tasks.md`. |"
- `skills/code-review/SKILL.md:156` "2. A `CONDITIONAL_PASS` verdict allows merge but **requires** that each should-fix item is logged as a task in `docs/tasks/active-tasks.md` with an assigned owner and target sprint. On the production track …"
- `skills/testing-strategy/SKILL.md:228` "| `CONDITIONAL_PASS` | Minor test failures (non-critical paths), coverage within 5% of threshold. | Pipeline proceeds; failures logged as tasks in `docs/tasks/active-tasks.md`. |"
- `skills/ci-cd-pipeline/SKILL.md:180` "- `CONDITIONAL_PASS` verdicts from code review allow progression but require tracked follow-up items in `docs/tasks/active-tasks.md`."
- Compliant neighbours (no edit): `agents/tech-lead.md:100` "the orchestrator adds it to the task list (`AGENTS.md` § Task Protocol)"; `commands/code-review.md:51` "with each condition tracked in the task list (`AGENTS.md` § Validation Gates)"; `skills/validation-gates:67, :139` "track all conditions as tasks, each with an owner and a due point" (no ledger named).

**Subjects (D3). Two, so two rulings.** (a) the actor that writes the follow-up row; (b) the fields the logged follow-up carries.

| Sub-item | Step A | Step B (P1) and step fired | Amendment |
|---|---|---|---|
| **4a. Actor** (`code-review:130, :156`; `testing-strategy:228`; `ci-cd-pipeline:180`) | **Holds.** All four are in the passive voice and name no actor, so the orchestrator can obey them and `AGENTS.md:18` too (same shape as `gitlab-management:137` and `blocker-escalation:122` in T615). The hazard is a reviewer or QA subagent reading "logged to `active-tasks.md`" as a licence to write it. `tech-lead:100` already assigns the write to the orchestrator for the same event. | **A**, note only (ADR-008 P3a). | **O4-a, O4-c, O4-d** and the first half of **O4-b**: name the orchestrator, citing `AGENTS.md` § Task Protocol |
| **4b. Fields** (`code-review:156`) | **Fails on the literal text.** The clause logs a task "in `docs/tasks/active-tasks.md` with an assigned owner and target sprint". `AGENTS.md:14` lists seven columns, a closed set; `Owner` is one, and a sprint is not. One ledger row cannot carry a target sprint. **One-value test:** the fields of a ledger row are the seven, and the clause computes eight. **Rescue reading (ii), recorded:** read "a task" as the row together with its brief and GitLab issue, where the sprint lives. I rule on the literal reading, as T613 S2 did for `scrum-master:27`, because the sentence puts the ledger in the clause and names the file. **The conclusion does not depend on it.** Under (ii) the held edit is the note ADR-008 Step A permits. | **B (P1).** (a) Quotable: `AGENTS.md:14` and `code-review:156`. (b) Reach: `AGENTS.md:14` is the ledger schema; the clause names that ledger. (c) Step A fails on reading (i). (d) A skill. The user's T613 S2 decision (the ledger has seven columns; sprint goes to the brief and the GitLab issue) also governs (ADR-008 § Scope). No P5. | **O4-b:** `owner` stays; the target sprint goes to the task brief or the GitLab issue. The same model as `scrum-master:27` after T616 and `technical-debt-tracking:129` |

**Declared-scope text relied on (4b).** `AGENTS.md:14–19` (reach: each sentence reaches what it names, D2) and the skill's own words naming the ledger file.
**Maturity.** Not relied on.

### 2.5 O-9: the plan's Task Breakdown table against the ledger columns

**Verbatim clauses (live).**

`skills/plan-approve-execute/SKILL.md`:
- `:57–60` "## Task Breakdown" / "| ID | Title | Assignee | Priority | BlockedBy | Estimated Effort |" / "| TNNN | ... | ... | ... | ... | S/M/L |"
- `:122` "2. Create all tasks from the plan's Task Breakdown in `docs/tasks/active-tasks.md` (use `task-management` skill)."
- `:125` "5. Assign tasks to agents per the plan's Assignee column."
- `:166–171` the example table, with the rows "| T020 | Research rate limit strategies | backend-dev | high | — | S |", "| T021 | Implement token bucket | backend-dev | high | T020 | M |", "| T022 | Add rate limit headers | backend-dev | medium | T021 | S |" and "| T023 | Write rate limit tests | qa-agent | high | T021 | M |"

Tier 1 and the ledger skill: `AGENTS.md:14`, `:19` "Priorities: `P0` (critical path), `P1`, `P2`."; `task-management:68` "Exact agent slug, kebab-case, from the installed agents folder."; `task-management:70` "| Priority | `P0` \| `P1` \| `P2`. NEVER `critical`/`high`/`medium`/`low`. |"

**Subject (D3).** The mapping from a plan-table row to a ledger row (a field mapping).

| Field | Content |
|---|---|
| **Step A** | **Holds.** The plan table is a different object from the ledger: it is a section of a plan document, with its own columns (`Assignee`, `BlockedBy`, `Estimated Effort`). `:122` names no actor and no mapping, so the orchestrator can obey it and `AGENTS.md:14` and `:19` too, by translating each row. Nothing forces `high` into a ledger cell. **But the translation is nowhere written down.** The only place it could be is `:122`, the one sentence that turns the plan table into ledger rows, and the example rows carry exactly the values the ledger forbids (`high`, `medium`, `backend-dev`, `qa-agent`). An orchestrator that copies a row fails `validate-tasks.py` `C4` (Priority set) and writes an Owner that is not an agent slug. |
| **Step fired** | **A.** At most a note stating the relationship where readers will see it. |
| **Is a mapping needed, and where?** | **Yes, at `plan-approve-execute:122`**, in one sentence, and the example rows should carry valid values. The mapping is: `Assignee` becomes `Owner` (an agent slug); `Priority` is `P0`, `P1` or `P2`; `BlockedBy` becomes `Depends on`; `Estimated Effort` goes to the task brief, because the ledger has no column for it (the T613 S2 model). It belongs in this skill, not in `task-management`, because this skill owns the plan table. |
| **Amendment** | Held, note-level: O9-a (`:122`) and O9-b (the four example rows, so that an example no longer teaches the forbidden values). The plan table's own header (`BlockedBy`, `Assignee`) is left alone: it names plan-document columns and `O9-a` explains the translation. |
| **Maturity** | Not relied on. |

### 2.6 O-10: `Assignee` against `Owner` in the checkpoint skill and template

**Verbatim clauses (live).** `skills/checkpoint-protocol/SKILL.md:71` and `:153` "| ID | Title | Status | Assignee |" (under "## Active Tasks" and "## Active Work");
`docs/checkpoints/_template.md:10` "| ID | Title | Owner | Outcome |" and `:14` "| ID | Title | Owner | Status | Notes |"; the ledger column is `Owner` (`AGENTS.md:14`).
The skill's Rails (`:15–20`): "a checkpoint's "Completed Tasks"/"Active Tasks" tables are a point-in-time summary derived from that ledger".
`AGENTS.md:29` "- Include: completed tasks, key decisions, blockers, token metrics, next steps."

**Subject (D3).** The name of the owner column in a checkpoint's task tables.

| Field | Content |
|---|---|
| **Step A** | **Holds.** `AGENTS.md:29` lists the elements a checkpoint includes, not their table headings, so no tier-1 clause fixes the heading. The skill and the template are not rivals under ADR-008 either: the template is not a covered document (ADR-008 § Scope names `AGENTS.md` and the files under `implementation/knowledge/`), as T607 O1-d already held. So there is no Task Protocol conflict. |
| **Related finding, not ruled** | The skill's checkpoint format and the template differ in far more than this label (for example "Completed Tasks | ID | Title | Completed" against "Completed tasks (this phase) | ID | Title | Owner | Outcome", and "Active Tasks" against "Open / carried over"). That divergence is a skill-against-template question outside ADR-008. Real checkpoints follow the template. It is recorded in §8 (N-3), not ruled. |
| **Step fired** | **A.** |
| **Amendment** | Held, cosmetic, optional: O10-a and O10-b change the two `Assignee` cells in the skill to `Owner`. The ground is the skill's own sentence that its tables are "derived from that ledger" (the skill places itself as a consumer of the ledger, whose column is `Owner`), not that other files use `Owner`. Either answer is acceptable (option 4-C or 4-D in §6). |
| **Maturity** | Not relied on. |

### 2.7 Items with no D5 record (not "rule")

| Obs. | Record |
|---|---|
| **O-5** | `scrum-master.md:20` "5. Assign tasks to appropriate team roles". Step A holds. `AGENTS.md:18` reserves "create/transition" to orchestrators; naming an owner for a task in a sprint plan is neither a creation nor a transition, and the file's own `:23–27` and `:135` (as amended by T616) have the Scrum Master propose rows that the orchestrator writes. The agent's `tools:` list has no edit tool. Same reading as T613 O-8. No edit. |
| **O-6** | `verification-before-completion:32` "- Before marking a task `done` in `docs/tasks/active-tasks.md`". Step A holds. The line is a trigger ("when to use"), not an instruction to leave a `done` row there. The act it precedes is the orchestrator's atomic completion (`task-management` § Complete a Task), which sets `done` and archives in one edit, and its Orchestrator Enforcement (`:89–92`) already gives the rejection of a `done` transition to the orchestrator. The wording is loose, not wrong: a reader can obey it and `AGENTS.md:15`. The hazard is smaller than O-3, since this line never asks anyone to look for a `done` row. No edit; a note is not worth a stable-skill edit and seven root paths. |
| **O-7** | See §3 (O7-a). `task-management:67` "`T` + 3 or more digits. `T001`, `T042`, `T1001`. NEVER `T001`. NEVER `BUG-7`." allows and forbids `T001` in one sentence. `AGENTS.md:19` ("Sequential IDs: `T001`, `T002`") and the validator's `ID_RE = ^T\d{3,}$` (`validate-tasks.py:11`, a witness only) say the shape is `T` plus three or more digits, so the forbidden shape is a shorter one. A same-file defect, resolved by same-file coherence (ADR-008 § Scope), not by ranking. |
| **O-8** | `gitlab-management:47–50` (`priority::critical/high/medium/low`), `:87` "## Priority: Must Have", `:88`; `scrum-master.md:32` "`priority::high/medium/low`", `:85` "## Priority: [High/Medium/Low]". Step A holds: these are fields of the GitLab issue, and no text computes a GitLab priority from the ledger or the reverse. `gitlab-management:134–137` syncs the Status labels only. The one mapping that exists, `bug-report.md:54` "Map severity → priority: critical→P0, high→P0, medium→P1, low→P2", maps a *bug's severity* to a ledger priority; the open case `bug-report-severity-priority-ledger-row` quotes it in its brief and hardcodes it in `expect.py` (`SEVERITY_TO_PRIORITY`). **A mapping for the issue labels is not needed now:** no step turns a label into a ledger value. If the user later wants issue priority synced, the home is `gitlab-management` § Label Conventions, and the values are a product choice. I draft none, and it must not contradict `bug-report:54`. Also recorded: there is no `status::cancelled` label for the lifecycle's `cancelled` state (an omission, not a conflict; §8 N-2). No edit. |
| **O-11** | Not a knowledge file. Live facts for the orchestrator (no edit by me): `docs/tasks/active-tasks.md:7` is the current note; `:8` begins "> record.** `plan-064` Phase 10 is done, …", the tail of a sentence whose start is gone; `:8–457` are historical Phase-9 blockquote paragraphs (about 450 lines, none starting with `|`, so `validate-tasks.py` ignores them); `:459–461` is a status/priority legend; `:463` says "**319 real tasks (`T001`-`T522`)** have already run to completion … most recently `checkpoint-036-…`", which is stale; `:468` is the briefs line. The issue is larger than T615's "blockquote fragment". The orchestrator tidies it in a ledger MR. |
| **O-12** | `technical-debt-tracking:95` "- **Status:** open \| in-progress \| resolved \| accepted-risk". Lookalike, not a hit: this is a debt-ledger item's status (`:82` "### DEBT-{ID}"), a different object from the task ledger's Status (`AGENTS.md:10`). Recorded so the next scan does not flag it. The skill's `:92` "Target sprint" and `:129` are likewise debt-item fields, consistent with the S2 model. No edit. |

## 3. Held edits (apply verbatim, only after the user decides)

Each Before is unique in its file by reading the whole file or the range read **(unverified by grep)**. No edit relaxes a check
(ADR-007 §5). None is upward: each moves an agent, a skill or a command toward `AGENTS.md`. None touches a tier-1 file, the
validator, `tests/golden/**` or `scripts/scorecard.py`. Edits are listed by source file; the platform projections are
regenerated, never edited by hand.

### 3.1 Option 1-A (O-1): blocker severity

`implementation/knowledge/skills/blocker-escalation/SKILL.md`

**O1-a: `:38`.** Anchor: the full line, which occurs once.

````
Before:
- **Severity:** critical | high | medium | low

After:
- **Severity:** critical | major | minor
````

**O1-b: `:50–57`** (the heading, a blank line, and the table). Anchor: the heading line `### Severity Definitions`, which occurs once, with the six lines after it.

````
Before:
### Severity Definitions

| Severity | Criteria |
|----------|----------|
| `critical` | Blocks the critical path; no workaround; project timeline at risk |
| `high` | Blocks multiple tasks or a high-priority task; workaround is costly |
| `medium` | Blocks a single non-critical task; workaround available |
| `low` | Minor inconvenience; does not block progress |

After:
### Severity Definitions

The severity set is the one in `AGENTS.md` § Blocker Protocol: `critical`, `major`, `minor`.

| Severity | Criteria |
|----------|----------|
| `critical` | Blocks the critical path; no workaround; project timeline at risk |
| `major` | Blocks multiple tasks or a high-priority task; workaround is costly |
| `minor` | Blocks a single non-critical task and a workaround is available, or is a minor inconvenience that does not block progress |
````

**O1-c: `:147`.** Anchor: the full line, which occurs once.

````
Before:
- **Severity:** high

After:
- **Severity:** major
````

**O1-d: `:163`.** Anchor: the full line, which occurs once.

````
Before:
- **Severity:** medium

After:
- **Severity:** minor
````

`implementation/knowledge/commands/team-status.md`

**O1-e: `:66`.** Anchor: the full line, which occurs once.

````
Before:
| 1 | ... | CRITICAL/HIGH/MEDIUM | ... | ... | [task IDs] | ... | ... |

After:
| 1 | ... | CRITICAL/MAJOR/MINOR | ... | ... | [task IDs] | ... | ... |
````

### 3.2 Option 2-A (O-2): the release checkpoint name

`implementation/knowledge/commands/prepare-release.md`

**O2-a: `:29`.** Anchor: the full line, with its three leading spaces, which occurs once.

````
Before:
   - Create a release checkpoint: `docs/checkpoints/checkpoint-release-v<version>.md`, based on

After:
   - Create a release checkpoint: `docs/checkpoints/checkpoint-<SEQ>-release-v<version>.md` (`AGENTS.md` § Checkpoint Protocol, with `release-v<version>` as the `<phase>`), based on
````

### 3.3 Option 3-A (O-3, O-4): completed tasks and follow-up logging

`implementation/knowledge/skills/release-workflow/SKILL.md`

**O3-a: `:53`** (note-level; Step A holds). Anchor: the full line, with its three leading spaces, which occurs once.

````
Before:
   - All planned tasks should be `done` or archived.

After:
   - All planned tasks should be `done` and archived in `docs/tasks/completed-tasks.md`: `active-tasks.md` never holds a `done` row (`AGENTS.md` § Task Protocol), so none should be left there.
````

`implementation/knowledge/agents/orchestrator.md`

**O3-b: `:146`** (note-level; Step A holds). Anchor: the full line, with its three leading spaces, which occurs once.

````
Before:
   - All task statuses in `docs/tasks/active-tasks.md` matching the release scope must be `done`

After:
   - No task matching the release scope remains in `docs/tasks/active-tasks.md`: each is `done` and archived in `docs/tasks/completed-tasks.md` (`AGENTS.md` § Task Protocol: `active-tasks.md` never holds a `done` row)
````

`implementation/knowledge/skills/code-review/SKILL.md`

**O4-a: `:130`** (note-level; 4a). Anchor: the full line, which occurs once.

````
Before:
| `CONDITIONAL_PASS` | Only should-fix findings. Code may merge with tracked follow-ups. | Pipeline proceeds; follow-up items logged to `docs/tasks/active-tasks.md`. |

After:
| `CONDITIONAL_PASS` | Only should-fix findings. Code may merge with tracked follow-ups. | Pipeline proceeds; follow-up items are proposed to the orchestrator, who logs them in `docs/tasks/active-tasks.md` (`AGENTS.md` § Task Protocol). |
````

**O4-b: `:156`** (4a note and 4b amendment; replace only this substring of the line). Anchor: the substring, which occurs once in the file.

````
Before:
requires** that each should-fix item is logged as a task in `docs/tasks/active-tasks.md` with an assigned owner and target sprint. On the production track

After:
requires** that each should-fix item is logged by the orchestrator as a task in `docs/tasks/active-tasks.md` with an assigned owner (`AGENTS.md` § Task Protocol); the ledger has no sprint column, so any target sprint is recorded in the task brief or the GitLab issue. On the production track
````

`implementation/knowledge/skills/testing-strategy/SKILL.md`

**O4-c: `:228`** (note-level; 4a). Anchor: the full line, which occurs once.

````
Before:
| `CONDITIONAL_PASS` | Minor test failures (non-critical paths), coverage within 5% of threshold. | Pipeline proceeds; failures logged as tasks in `docs/tasks/active-tasks.md`. |

After:
| `CONDITIONAL_PASS` | Minor test failures (non-critical paths), coverage within 5% of threshold. | Pipeline proceeds; failures are proposed to the orchestrator, who logs them as tasks in `docs/tasks/active-tasks.md` (`AGENTS.md` § Task Protocol). |
````

`implementation/knowledge/skills/ci-cd-pipeline/SKILL.md`

**O4-d: `:180`** (note-level; 4a). Anchor: the full line, which occurs once.

````
Before:
- `CONDITIONAL_PASS` verdicts from code review allow progression but require tracked follow-up items in `docs/tasks/active-tasks.md`.

After:
- `CONDITIONAL_PASS` verdicts from code review allow progression but require tracked follow-up items, which the orchestrator adds to `docs/tasks/active-tasks.md` (`AGENTS.md` § Task Protocol).
````

### 3.4 Option 4-A (O-7, O-9, O-10): clean-ups

`implementation/knowledge/skills/task-management/SKILL.md`

**O7-a: `:67`.** Anchor: the full line, which occurs once.

````
Before:
| ID | `T` + 3 or more digits. `T001`, `T042`, `T1001`. NEVER `T001`. NEVER `BUG-7`. |

After:
| ID | `T` + 3 or more digits. `T001`, `T042`, `T1001`. NEVER `T1` or `T01`. NEVER `BUG-7`. |
````

`implementation/knowledge/skills/plan-approve-execute/SKILL.md`

**O9-a: `:122`** (note-level). Anchor: the full line, which occurs once.

````
Before:
2. Create all tasks from the plan's Task Breakdown in `docs/tasks/active-tasks.md` (use `task-management` skill).

After:
2. Create all tasks from the plan's Task Breakdown in `docs/tasks/active-tasks.md` (use `task-management` skill). An orchestrator writes the rows, one per plan row, in the ledger's seven columns (`AGENTS.md` § Task Protocol): Assignee becomes Owner (an agent slug), Priority is `P0`, `P1` or `P2`, BlockedBy becomes Depends on, and Estimated Effort goes to the task brief, because the ledger has no column for it.
````

**O9-b: `:168–171`** (the four example rows; match the whole block).

````
Before:
| T020 | Research rate limit strategies | backend-dev | high | — | S |
| T021 | Implement token bucket | backend-dev | high | T020 | M |
| T022 | Add rate limit headers | backend-dev | medium | T021 | S |
| T023 | Write rate limit tests | qa-agent | high | T021 | M |

After:
| T020 | Research rate limit strategies | backend-developer | P1 | — | S |
| T021 | Implement token bucket | backend-developer | P1 | T020 | M |
| T022 | Add rate limit headers | backend-developer | P2 | T021 | S |
| T023 | Write rate limit tests | qa-engineer | P1 | T021 | M |
````

`implementation/knowledge/skills/checkpoint-protocol/SKILL.md` (cosmetic, optional; 4-A only)

**O10-a: `:70–71`.** Anchor: the heading and the line after it (the header line alone occurs twice).

````
Before:
## Active Tasks
| ID | Title | Status | Assignee |

After:
## Active Tasks
| ID | Title | Status | Owner |
````

**O10-b: `:152–153`.** Anchor: the heading and the line after it.

````
Before:
## Active Work
| ID | Title | Status | Assignee |

After:
## Active Work
| ID | Title | Status | Owner |
````

**Totals.** There are 17 fences and 17 applications: O1-a to O1-e (5), O2-a (1), O3-a, O3-b (2), O4-a to O4-d (4), O7-a (1),
O9-a, O9-b (2), O10-a, O10-b (2). The subsets the user can choose are in §6. They touch 11 source files: 8 skills (`blocker-escalation`, `release-workflow`, `code-review`,
`testing-strategy`, `ci-cd-pipeline`, `task-management`, `plan-approve-execute`, `checkpoint-protocol`), 2 commands
(`team-status`, `prepare-release`) and 1 agent (`orchestrator`). Note-level edits (Step A holds): O3-a, O3-b, O4-a, O4-c,
O4-d, the first half of O4-b, O9-a, O9-b, O10-a, O10-b. Step B amendments: O1-a to O1-e, O2-a, the second half of O4-b.
The same-file fix: O7-a.

## 4. Hit counts

- **Scope:** case-sensitive, fixed-string, per file, after every held edit to that file. "Lines" = `grep -cF`; "occurrences" =
  `grep -oF … | wc -l`. "Whole line" = `grep -cxF`.
- **Before** counts are by reading the live files **(unverified by grep)**. A "0 / 0" in the After column means the old
  wording must be gone. Every projection of a source file carries the same counts as its source, apart from the dropped
  frontmatter lines (about one line lower) **(unverified; I read no projection this time)**.

### 4.1 O-1: sites that repeat the severity clause

| # | File | Phrase | Before (lines / occ.) | After | Edit |
|---|---|---|---|---|---|
| 1 | `skills/blocker-escalation/SKILL.md` | `critical \| high \| medium \| low` | 1 / 1 (`:38`) | **0 / 0** | O1-a |
| 2 | same | `` `high` `` | 1 / 1 (`:55`) | **0 / 0** | O1-b |
| 3 | same | `` `medium` `` and `` `low` `` | 1 / 1 each (`:56`, `:57`) | **0 / 0** | O1-b |
| 4 | same | `**Severity:** high` / `**Severity:** medium` | 1 / 1 each (`:147`, `:163`) | **0 / 0** | O1-c, O1-d |
| 5 | same | `` `major` `` / `` `minor` `` | 0 / 0 | 2 / 2 each (the sentence and the row) | O1-b |
| 6 | same | `**Severity:** critical \| major \| minor` | 0 / 0 | 1 / 1 | O1-a |
| 7 | same | `**Severity:** major` / `**Severity:** minor` | 0 / 0 | 1 / 1 each | O1-c, O1-d |
| 8 | same | `AGENTS.md` | 2 / 2 (`:78`, `:122`, set by T616) | **3 / 3** | O1-b |
| 9 | same | `high-priority` (the criteria text, kept) | 1 / 1 (`:55`) | 1 / 1 | O1-b keeps it |
| 10 | `commands/team-status.md` | `CRITICAL/HIGH/MEDIUM` | 1 / 1 (`:66`) | **0 / 0** | O1-e |
| 11 | same | `CRITICAL/MAJOR/MINOR` | 0 / 0 | 1 / 1 | O1-e |
| 12 | same | `[low|medium|high] saturation` (another object) | 1 / 1 (`:88`) | 1 / 1 | untouched |

Conforming witnesses read and left alone: `agents/frontend-developer.md:93`, `agents/backend-developer.md:99`,
`skills/systematic-debugging/SKILL.md:91` (3 files, `critical`/`major`/`minor`). Other objects with the four-level scale, left
alone: `validation-gates:49–52, :76–81`, `validate-workflow:66`, `bug-report:20`, `team-status:88`, `technical-debt-tracking:85–86`.
Other agents' `Blocker Reporting` sections: `scrum-master:102–107`, `release-manager`, `qa-engineer:123–124` name no severity values; the
unread agents are **(unverified)**.

### 4.2 O-2: sites that repeat the checkpoint name

| # | File | Phrase | Before (lines / occ.) | After | Edit |
|---|---|---|---|---|---|
| 13 | `commands/prepare-release.md` | `checkpoint-release-v` | 1 / 1 (`:29`) | **0 / 0** | O2-a |
| 14 | same | `checkpoint-<SEQ>-release-v<version>.md` | 0 / 0 | 1 / 1 | O2-a |
| 15 | same | `AGENTS.md` | 0 / 0 | 1 / 1 | O2-a |
| 16 | other knowledge files read | `checkpoint-release-v` | 0 / 0 in `release-workflow`, `release-manager`, `orchestrator`, `checkpoint-protocol`, `coding-standards` | unchanged | none |
| 17 | `tests/golden/open/**` (3 `prepare-release-*` cases, briefs read) | `checkpoint-release-v` | 3 lines in 2 briefs (`prepare-release-changelog-grouping-compliant/brief.md:23`, `prepare-release-real-verdict-missing/brief.md:9, :19`), each describing the real artifact, none quoting the command | unchanged | none |
| 18 | real files `docs/checkpoints/checkpoint-release-v*.md` | the name | **count unknown** | frozen (ADR-007 branch 3b) | none |

### 4.3 O-3 and O-4: sites that repeat the clauses

| # | File | Phrase | Before (lines / occ.) | After | Edit |
|---|---|---|---|---|---|
| 19 | `skills/release-workflow/SKILL.md` | `` `done` or archived `` | 1 / 1 (`:53`) | **0 / 0** | O3-a |
| 20 | same | `completed-tasks.md` | 1 / 1 (`:91`, the changelog step) | 2 / 2 | O3-a |
| 21 | `agents/orchestrator.md` | `matching the release scope must be` | 1 / 1 (`:146`) | **0 / 0** | O3-b |
| 22 | same | `completed-tasks.md` | 1 / 1 (`:73`) | 2 / 2 | O3-b |
| 23 | `skills/code-review/SKILL.md` | `logged to` / `is logged as a task` | 1 / 1 each (`:130`, `:156`) | **0 / 0** | O4-a, O4-b |
| 24 | same | `and target sprint` | 1 / 1 (`:156`) | **0 / 0** | O4-b |
| 25 | same | `AGENTS.md` | 0 / 0 in the range read | 2 / 2 | O4-a, O4-b |
| 26 | `skills/testing-strategy/SKILL.md` | `failures logged as tasks in` | 1 / 1 (`:228`) | **0 / 0** | O4-c |
| 27 | `skills/ci-cd-pipeline/SKILL.md` | `require tracked follow-up items in` | 1 / 1 (`:180`) | **0 / 0** | O4-d |
| 28 | the three skills together | `active-tasks.md` in a CONDITIONAL_PASS context | 4 lines, 3 files (the lines above) | 4 lines, 3 files (each now names the orchestrator) | O4-a to O4-d |

Compliant neighbours left alone: `tech-lead:100`, `commands/code-review.md:51`, `validation-gates:67, :139`, `commands/prepare-release.md:17`
(reads `completed-tasks.md` correctly). `verification-before-completion:32` (O-6) is the only other site that puts `done` and
`active-tasks.md` in one line; it is not edited.

### 4.4 O-7, O-9, O-10

| # | File | Phrase | Before (lines / occ.) | After | Edit |
|---|---|---|---|---|---|
| 29 | `skills/task-management/SKILL.md` | `NEVER \`T001\`` | 1 / 1 (`:67`) | **0 / 0** | O7-a |
| 30 | same | `NEVER \`T1\` or \`T01\`` | 0 / 0 | 1 / 1 | O7-a |
| 31 | `skills/plan-approve-execute/SKILL.md` | `backend-dev` / `qa-agent` | 3 / 3 and 1 / 1 (`:168–171`) | **0 / 0** | O9-b |
| 32 | same | `\| high \|` / `\| medium \|` | 3 / 3 and 1 / 1 | **0 / 0** | O9-b |
| 33 | same | `BlockedBy` (plan-table header and rows) | 2 / 2 (`:58`, `:166`) | 3 / 3 (O9-a adds one mention) | O9-a |
| 34 | same | `AGENTS.md` | 0 / 0 | 1 / 1 | O9-a |
| 35 | `skills/checkpoint-protocol/SKILL.md` | `Assignee` | 2 / 2 (`:71`, `:153`) | **0 / 0** | O10-a, O10-b |
| 36 | same | `\| Status \| Owner \|` | 0 / 0 | 2 / 2 | O10-a, O10-b |
| 37 | `docs/checkpoints/_template.md` | `Owner` | 2 / 2 (`:10`, `:14`) | unchanged | none (not a knowledge file) |

Other places that use the plan-table shape: `/plan` does not (it writes "Resource Assignments" and "Task Decomposition",
`plan.md:19–22`); `docs/plans/_template.md` and `implementation/docs/plans/_template.md` **(unverified; not read)**.

## 5. Effects

### 5.1 Projected paths and root drift

The counts follow `naming-conflicts-ruling-v1.md` §5.1: a skill projects to 7 root paths, an agent or a command to 6 **(unverified
this time; I read no projection)**.

| Source edit | Root-projection paths | Item |
|---|---|---|
| `skills/blocker-escalation/SKILL.md` | **7** | O-1 |
| `commands/team-status.md` | **6** | O-1 |
| `commands/prepare-release.md` | **6** | O-2 |
| `skills/release-workflow/SKILL.md` | **7** | O-3 |
| `agents/orchestrator.md` | **6** | O-3 |
| `skills/code-review/SKILL.md` | **7** | O-4 |
| `skills/testing-strategy/SKILL.md` | **7** | O-4 |
| `skills/ci-cd-pipeline/SKILL.md` | **7** | O-4 |
| `skills/task-management/SKILL.md` | **7** | O-7 |
| `skills/plan-approve-execute/SKILL.md` | **7** | O-9 |
| `skills/checkpoint-protocol/SKILL.md` | **7** | O-10 |
| **Total if everything is applied** | **74** (11 files: 8 x 7 + 3 x 6) | |

- **Subsets (the user's groups, §6).** Q1 1-A: 13 (`blocker-escalation` 7 + `team-status` 6; 1-B: 7). Q2 2-A: 6. Q3 3-A: 34
  (`release-workflow` 7, `orchestrator` 6, `code-review` 7, `testing-strategy` 7, `ci-cd-pipeline` 7); 3-B (O4-b only): 7;
  3-C (O-3 pair): 13. Q4 4-A: 21 (`task-management`, `plan-approve-execute`, `checkpoint-protocol`); 4-B: 14; 4-C: 7.
  1-A + 2-A + 3-A + 4-A = 13 + 6 + 34 + 21 = 74.
- **Regenerate:** `node implementation/scripts/sync.mjs --root implementation`, then `python3 implementation/scripts/generate-registry.py`,
  each followed by `--check`. `implementation/registry/index.json` changes for the 11 entries (checksums). `implementation/registry/summary.md`
  should not change, since no `maturity:` changes **(unverified)**.
- **Mirrors.** `sync.mjs` also writes the same files under `implementation/.<platform>/`. Whether they are tracked is **(unverified)**.
  They are not root drift.
- **Root drift.** `tests/_baselines/root-install-drift.json` was emptied by the fifteenth refresh (the orchestrator states "root
  drift 0"; I did not re-read the file). The implementing task declares exactly the paths `python3 -m
  tests.functional.test_root_install_parity --print-drift` prints (expected 74 if everything is applied). It does not refresh the repo
  root; that is a separate, user-approved `--projections-only` refresh.

### 5.2 Golden and test coupling

| Item | Coupling | Effect |
|---|---|---|
| `prepare-release-changelog-grouping-compliant` (open, read) | Quotes `prepare-release.md` step 2 (changelog grouping). Its `brief.md:23` mentions the glob `checkpoint-release-v*.md` as a description of real files. `expect.py` reads `fixture/changelog.md` only | **Unaffected by O2-a.** It does not quote `:29` |
| `prepare-release-conditional-pass-conditions-gap` (open, read) | Quotes step 9 and the step 7 template. `expect.py` reads `fixture/release-notes.md` | **Unaffected** |
| `prepare-release-real-verdict-missing` (open, read) | Its fixture is the real `checkpoint-release-v6.4.1.md`; `expect.py` globs `fixture/docs/checkpoints/*.md` and requires exactly one file, not a name | **Unaffected.** ADR-007's sibling corollary ("fixture/glob updated to the amended form") does not apply: there is no name glob, and the fixture is a frozen real artifact |
| `team-status-dag-colour-code` (open, read) | Quotes step 7's four sub-bullets (`team-status.md:46–49`) and the Output format headings. `expect.py` reads `fixture/team-status.md` and the two ledgers; the fixture has no copy of the command | **Unaffected by O1-e.** It does not quote the Blocker Summary table (`:64–66`) |
| `bug-report-severity-priority-ledger-row` (open, read) | Quotes `bug-report.md:54` "Map severity → priority: critical→P0, high→P0, medium→P1, low→P2" in its brief and hardcodes it in `expect.py` | **Not touched by any edit here.** An edit to `bug-report:54`, or to the bug severity scale, would need a protected-path grant and a new baseline. That is a consequence, not a reason (ADR-008 P4(e)); I rule on the texts |
| `validate-workflow-gate-verdict-sources` (open, read) | Holds a byte-identical fixture copy of `validate-workflow.md` and `validation-gates/SKILL.md`; `check()` reads step 5's list and the Gate Types table | **Not touched.** `validate-workflow:66` is left alone on the merits (§2.1: a different object). An edit to either copied file would put the fixture copy out of date |
| `code-review-conditional-pass-conditions-gap`, `code-review-fail-blocker-details` (open, read) | Quote `commands/code-review.md`, not the `code-review` skill | **Unaffected by O4-a, O4-b** |
| Other open cases | `skillify-skill-file-template-drift` (brief read) does not quote any edited file. I did not read the other open cases | **Unknown whether another open case copies or quotes an edited file.** The orchestrator should grep `tests/golden/open/` for the paths and Before strings in §7.2 |
| **Held-out cases** | **I did not open `tests/golden/held-out/`. Held-out coupling is unknown and was not checked.** The published scorecard shows one held-out `/prepare-release` case and one `/code-review` and one `/new-feature` case among six; whether any of them pins an edited clause is unknown | The orchestrator, under its read/audit exception, should run the same greps there and report **only a hit count**, not a case name |
| `docs/tasks/validate-tasks.py` | Checks 7 cells per active row, the Status and Priority sets, and `Depends on` tokens. It reads no skill text | Unaffected. The example rows O9-b and the ID rule O7-a agree with it (`ID_RE = ^T\d{3,}$`, `PRIORITY_SET = {P0, P1, P2}`) |
| `test_root_install_parity` | The one known coupling (§5.1) | Needs the printed paths declared |
| Other tests | I could not search `tests/` | **Unknown whether any test asserts a Before string** (§7.2) |

### 5.3 Baseline and grant

- **Protected-path grant:** **none needed.** No edit touches `tests/golden/**` or `scripts/scorecard.py`.
- **Evaluator-hash baseline (v21):** **none needed.** `docs/artifacts/evaluator-hash-known-good-v20.json` hashes exactly two paths,
  `tests/golden` and `scripts/scorecard.py`. No held edit touches either. `scripts/scorecard.py --check` compares a `content` that
  `scorecard.py`'s docstring says is "a pure function of the golden suite tree's on-disk bytes", so a command or skill edit does not
  change it. A grant and a v21 would be needed only for an edit to a golden file: for example, if the user chose to change
  `bug-report:54` (and so the case that pins it), or to re-fixture a case. No option in §6 does that.
- **Checks that should be unaffected (unverified):** `check-maturity.py --root implementation` and `python3 docs/tasks/validate-tasks.py`.
  Two of the edited files are `stable` (`team-status`, `checkpoint-protocol`); the maturity criteria read golden state
  and `Affects:` fields, not these strings **(unverified; run the check)**.

## 6. The user question (one round)

**Q-T617: five groups. Answer with one letter per group (for example "1-A, 2-A, 3-A, 4-A, 5-A"), or say "all recommended".
Nothing is applied before you answer.**

Every group is decided by ADR-008 Step A or Step B, because the other document is a skill, an agent or a command and no
conflict is inside tier 1. Options A and B are therefore "approve the ruled edits" or "hold them". The "C" options exist only
where changing a tier-1 file instead is your prerogative; ADR-008 never does it on its own, and I have drafted no edit for them.

**Group 1: blocker severity (O-1).** `blocker-escalation` and `team-status:66` use `critical | high | medium | low` and
`CRITICAL/HIGH/MEDIUM`; `AGENTS.md:48` says `critical | major | minor`.

| Option | What changes | Consequences |
|---|---|---|
| **1-A (Recommended)** | O1-a to O1-e: the skill and the `team-status` table move to `critical | major | minor`; `high` becomes `major`, `medium` and `low` become `minor` | 13 root paths. Matches the three agent files that already use the `AGENTS.md` set. Coarsens four levels to three; the escalation path (`severity = critical`) is unchanged. `team-status` is a `stable` command; its open case does not quote the table |
| **1-B** | O1-a to O1-d only; leave `team-status` | 7 paths. The command keeps rendering a blocker as `HIGH` or `MEDIUM`, a value no blocker report can carry |
| **1-C** | Change `AGENTS.md:48` to `critical | high | medium | low` in a separate instruction-change task | A tier-1 change, no edit drafted. The three agent files and `AGENTS.md` copies in every installed project would follow. **Not recommended** |
| **1-D** | Hold | The skill keeps telling every blocked subagent to write a severity that `AGENTS.md` does not list |

**Group 2: the release checkpoint name (O-2).** `prepare-release:29` names `checkpoint-release-v<version>.md`; `AGENTS.md:27` says
`checkpoint-<SEQ>-<phase>.md`.

| Option | What changes | Consequences |
|---|---|---|
| **2-A (Recommended)** | O2-a: `checkpoint-<SEQ>-release-v<version>.md`, citing `AGENTS.md` | 6 paths. The next release checkpoint is the first to use it; existing `checkpoint-release-v*.md` files stay as they are. No open golden case quotes the line; no grant, no v21 baseline. Held-out coupling is unknown |
| **2-B** | Hold | The command keeps a name that `AGENTS.md`, `coding-standards`, the skill and the template it imports all contradict |
| **2-C** | Change `AGENTS.md:27` (and `coding-standards:73, :88`) to admit `checkpoint-release-v<version>.md` | A tier-1 and stable-instruction change, no edit drafted. **Not recommended**: it makes a second pattern for one artifact class |

**Group 3: completed tasks in the release check, and follow-up logging (O-3, O-4; O-6 stays unedited).** Step A holds for the
actors; only the "target sprint" field (O4-b, second half) is a Step B amendment.

| Option | What changes | Consequences |
|---|---|---|
| **3-A (Recommended)** | O3-a, O3-b, O4-a to O4-d: `done` rows are looked for in `completed-tasks.md` (or as "none remain"), the orchestrator logs follow-ups, and the target sprint goes to the brief or the GitLab issue | 34 root paths (5 files). Note-level edits except the target-sprint clause. Matches your T613 S2 decision, `tech-lead:100`, and `AGENTS.md:15, :18` |
| **3-B** | O4-b only (the target-sprint amendment and its actor note) | 7 paths. The release-check wording and the other three follow-up sites stay passive |
| **3-C** | O3-a and O3-b only | 13 paths. The follow-up sites keep a "target sprint" the ledger lacks |
| **3-D** | Hold | Every site stays obeyable, but the hazards stay (a reader hunts for `done` rows; a reviewer writes the ledger) |

**Group 4: clean-ups (O-7 typo, O-9 plan-to-ledger mapping, O-10 `Assignee`).**

| Option | What changes | Consequences |
|---|---|---|
| **4-A (Recommended)** | O7-a, O9-a, O9-b, O10-a, O10-b | 21 paths (3 skills). O7-a fixes a rule that forbids its own example. O9-a/b put the plan-to-ledger mapping at `plan-approve-execute:122` and fix its example values. O10 is cosmetic: say "4-B" to drop it |
| **4-B** | O7-a, O9-a, O9-b (hold O10) | 14 paths. `Assignee` stays in the checkpoint skill's two tables |
| **4-C** | O7-a only | 7 paths. The plan table's example keeps teaching `high` and `backend-dev` |
| **4-D** | Hold | The typo and the example values stay |

**Group 5: a label-to-priority mapping for GitLab issues (O-8).** No text turns a `priority::` label into a ledger value, so none is needed now.

| Option | What changes | Consequences |
|---|---|---|
| **5-A (Recommended)** | No mapping; O-8 stays recorded as Step A holds | No edit. Avoids a second severity/priority table next to `bug-report:54`, which an open case pins |
| **5-B** | I draft a `priority::*` to `P0`/`P1`/`P2` mapping in `gitlab-management` § Label Conventions in a follow-up | Needs your P0/P1/P2 semantics (which label is "critical path"). 7 more paths. No grant, because `bug-report:54` is untouched |

**Recommendation: 1-A, 2-A, 3-A, 4-A, 5-A ("all recommended").** One mechanical implementation task, then one root refresh,
covers 11 files (74 paths). Groups 1 and 2 are the real conflicts (Step B). Group 3 is mostly Step A notes with one Step B
clause. Group 4's O10 and Group 3's O-3 half are the places where I would accept either answer: the ADR requires no edit there.
Each recommendation follows from ADR-008 Step A or Step B and from your 2026-10-09 decisions, not from the number of files that
already agree with `AGENTS.md`.

## 7. Handoff package for the implementing task (specification; no task is created here)

### 7.1 Package

| Field | Content |
|---|---|
| `task_id` | To be assigned by the orchestrator (a mechanical-tier follow-up to `T617`) |
| `definition` | Apply, verbatim, only the fences the user approves in Q-T617 (§3), then regenerate and declare root drift |
| `constraints` | Never reword. Apply each pair by exact string replacement, matching each single-line Before as a whole line (O4-b is a substring match, so assert it matches once) and asserting it matches exactly once; for the multi-line Befores (O1-b, O9-b, O10-a, O10-b) match the whole block. Stop and report if an anchor is missing or not unique. Do not edit `AGENTS.md`, `implementation/AGENTS.md`, any instruction, `validate-workflow`, `bug-report`, `verification-before-completion`, `docs/tasks/validate-tasks.py`, any file under `tests/golden/**`, `scripts/`, `.env*`, or any derived platform folder by hand. Do not refresh the repo root. Do not push, and never run any merge or approve call |
| `depends_on` | The user's answer to Q-T617 |
| `input_artifacts` | `task-protocol-observations-ruling-v1.md` (this file) as the single implementation input |
| `expected_outputs` | The edited files (up to 11); regenerated mirrors and `implementation/registry/index.json` (up to 11 entries); `tests/_baselines/root-install-drift.json` with exactly the printed paths (expected 74 if everything is applied); a report with every §4 count as lines and occurrences |
| `blocker_policy` | `AGENTS.md` § Blocker Protocol: report type and severity. A non-golden test that asserts a Before string is a `dependency` blocker to the orchestrator. A golden hit (open or held-out) is a `dependency` blocker reported to the orchestrator as a count only, never with a held-out case name |

Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`,
`scripts/scorecard.py --check` (equal to the current baseline), `python3 docs/tasks/validate-tasks.py`, and `python3 tests/run.py` with
output redirected to a file. Confirm byte-unchanged: `AGENTS.md`, every instruction, `validate-workflow`, `bug-report`,
`verification-before-completion`, every script, and `tests/golden/**`.

### 7.2 Pre-flight greps (not run here; I have no shell)

Run and report, then stop if a non-golden test asserts a Before string. Report golden hits to the orchestrator only, as a count.

- `grep -rnF -e 'critical | high | medium | low' -e 'CRITICAL/HIGH/MEDIUM' -e 'checkpoint-release-v' -e 'done` or archived' -e 'matching the release scope must be' -e 'logged to `docs/tasks/active-tasks.md`' -e 'with an assigned owner and target sprint' -e 'failures logged as tasks' -e 'require tracked follow-up items in' -e 'NEVER `T001`' -e 'backend-dev |' -e 'qa-agent' -e '| Status | Assignee |' implementation/ docs/wiki docs/guides docs/releases README.md CONTRIBUTING.md tests/ --include='*.md' --include='*.py' --include='*.mjs' --include='*.json' --include='*.yaml'`
- `grep -rlE 'blocker-escalation|team-status|prepare-release|release-workflow|code-review|testing-strategy|ci-cd-pipeline|task-management|plan-approve-execute|checkpoint-protocol' tests/ --include='*.py' --include='*.yaml' --include='*.json'`, then read each hit.
- `ls docs/checkpoints/ | grep -c 'checkpoint-release-v'` (the count of real release checkpoints for O-2) and the next free `<SEQ>`.
- `grep -rn 'major' implementation/knowledge/agents | grep -i severity` (to list every agent that already uses the `AGENTS.md` set) and the same for `high | medium | low` near the word "blocker".
- Compare each count with §4, and the `Before` match counts with the "occurs once" claims in §3.

## 8. Further observations (new or restated; not ruled)

| # | Site (source file) | Quote | Reading |
|---|---|---|---|
| **N-1** | `commands/prepare-release.md:34` | "   - Archive completed tasks from `active-tasks.md` to `completed-tasks.md`" | Presupposes completed rows still in the active ledger. Under `AGENTS.md:15` it is a no-op, so Step A holds (it can be obeyed). It is in the same command as O2-a; if the user wants it tidied, the same edit pass can carry it. Not recommended: it is harmless |
| **N-2** | `skills/gitlab-management/SKILL.md:170–174` | the `status::` rows | There is no `status::cancelled` label for the `cancelled` state, and `status::done` "Triggers move to completed-tasks.md" names no actor. An omission, not a conflict |
| **N-3** | `skills/checkpoint-protocol/SKILL.md:55–93` against `docs/checkpoints/_template.md:1–54` | the two checkpoint formats | They differ in most headings and table columns, and real checkpoints follow the template. Outside ADR-008 (the template is not a covered document). If the user wants one format, that is a separate question for the skill, the template and the `AGENTS.md:29` list |
| **N-4** | `docs/tasks/active-tasks.md:7–8, :463` | the live note, the orphan sentence tail, and the stale "319 real tasks (`T001`-`T522`)" | O-11 is larger than T615 said; see §2.7 |
| **N-5** | `docs/artifacts/task-protocol-skill-conflicts-ruling-v1.md` §7 | O-1 cites `blocker-escalation:148, :165`; O-10 cites `checkpoint-protocol:71, :154` | Live lines are `:147, :163` and `:71, :153`. The artifact is immutable; this is recorded here only |
| **N-6** | `commands/validate-workflow.md:66` | "Severity (CRITICAL/HIGH/MEDIUM/LOW)" | A lookalike of O-1, ruled as another object (§2.1). Editing it would also put the fixture copy of `validate-workflow-gate-verdict-sources` out of date; that is a consequence, not the reason |

## 9. Still unverified

1. The worktree commit `03f9c2b` plus the scoping commit (stated by the orchestrator).
2. Every count in §4 and every "occurs once" claim in §3, by reading, not `grep`. The counts that include text added by T616
   (`AGENTS.md` in `blocker-escalation`, row 8) are the likeliest to be off by one.
3. The platform projections of every edited file, their line numbers, and the projection counts of 6 (agent, command) and 7 (skill),
   taken from `naming-conflicts-ruling-v1.md` §5.1; whether `implementation/.<platform>/` mirrors are tracked.
4. That no golden case (open or held-out), no test, and no page under `docs/wiki`, `docs/guides`, `docs/releases`, `README.md` or
   `CONTRIBUTING.md` asserts or restates a Before string. I read nine open case briefs and five `expect.py` files, listed in §0, and
   no held-out case. I read no other open case.
5. That `implementation/registry/summary.md`, the maturity checks and `root-install-drift.json` (read by the orchestrator, not by me)
   are unaffected, and the evaluator-hash baseline figure (v20, read from `evaluator-hash-known-good-v20.json`).
6. That the scope text relied on in §2 was not edited in the change that first recorded these conflicts (I cannot diff history).
7. Files not re-read: all agents other than `orchestrator`, `scrum-master`, `release-manager`, `tech-lead` (part), `frontend-developer`
   (part), `backend-developer` (part), `qa-engineer` (part); all skills other than those listed in §0; commands other than those
   listed; `docs/plans/_template.md` and `implementation/docs/plans/_template.md`; `implementation/docs/checkpoints/` if it exists.
   T615 found the unread ones conforming for the Task Protocol; the blocker-severity check in §4.1 therefore covers only the files I read.
8. The user's decisions of 2026-10-09 are quoted as the orchestrator relayed them, not re-read from the user's own message.
9. The number of real `docs/checkpoints/checkpoint-release-v*.md` files, and whether any script, page or test depends on that name.

## 10. Summary

| Obs. | Subject | Settled by | Outcome | Edits | User decision? |
|---|---|---|---|---|---|
| O-1 | Blocker severity set | Step B (P1; ADR-007 branch 1 for the command) | Amend `blocker-escalation` and `team-status` to `critical | major | minor` | O1-a to O1-e | Group 1 (1-C is the tier-1 alternative) |
| O-2 | Release checkpoint name | Step B (ADR-007 branch 1, same-file prong) | Amend `prepare-release:29` to `checkpoint-<SEQ>-release-v<version>.md` | O2-a | Group 2 (2-C is the tier-1 alternative) |
| O-3 | Completed tasks in the release check | Step A holds | Note-level rewrite of two lines | O3-a, O3-b | Group 3 |
| O-4 | Follow-up logging | 4a Step A; 4b Step B (P1) | Orchestrator logs; target sprint to brief or issue | O4-a to O4-d | Group 3 |
| O-5 | Scrum Master "assigns tasks" | Step A holds | No edit | none | none |
| O-6 | `done` in `active-tasks.md` in a trigger list | Step A holds | No edit | none | none |
| O-7 | `NEVER T001` | Same-file coherence | Fix to `NEVER T1 or T01` | O7-a | Group 4 |
| O-8 | `priority::` labels | Step A holds | No mapping now | none | Group 5 |
| O-9 | Plan table against ledger | Step A holds | Mapping at `plan-approve-execute:122`; valid example values | O9-a, O9-b | Group 4 |
| O-10 | `Assignee` / `Owner` | Step A holds; outside ADR-008 for the template | Cosmetic alignment of the skill | O10-a, O10-b | Group 4 |
| O-11 | `active-tasks.md` leftovers | Not a knowledge file | Orchestrator tidies | none | none |
| O-12 | Debt-ledger `Status` | Lookalike | Recorded | none | none |

- **Maturity, corpus counts, majority practice and golden-coupling convenience** were relied on nowhere as authority. The agreement
  of other files with `AGENTS.md` appears only as a witness and as a consequence in §6.
- **No tier-1 conflict, so no P5 escalation.** Changing `AGENTS.md:48` or `:27` stays the user's option (1-C, 2-C), and I drafted no edit for either.
- **No edit is applied, and none is upward or relaxing.** No tier-1 file, golden path or protected path is touched.
- **Grant and baseline:** none needed under any option in §6. A grant and an evaluator baseline v21 would be needed only to edit a golden
  file, which no option does.
- **Golden:** none of the nine open case briefs I read quotes an edited line. **Held-out coupling is unknown and was not checked.**
- **Blockers:** none for this task. The unverified items in §9 (golden and non-golden test coupling, other agents' severity wording)
  are `dependency` checks for the implementing task, severity `minor`.
