# Artifact: task-protocol-skill-conflicts-ruling-v1.md

> Filename: `task-protocol-skill-conflicts-ruling-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T615 (P2, judgment tier, decision only)
- **Created**: 2026-10-09
- **Based on:**
  - `docs/tasks/task-T615.md` (the brief, authoritative);
  - `docs/plans/plan-118-task-protocol-skill-conflicts.md`;
  - `docs/artifacts/task-protocol-and-checkpoint-name-ruling-v1.md` §2 (the S1/S2 model), §4.3 and §7 (observations
    O-1 to O-5, the source of this task);
  - `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted) and
    `docs/decisions/ADR-007-command-contract-authority.md` (Accepted);
  - `AGENTS.md` § Team Model, § Lifecycle States, § Task Protocol, § Checkpoint Protocol, § Blocker Protocol (root copy
    `:3–6`, `:8–11`, `:13–19`, `:26–30`, `:46–49`; `implementation/AGENTS.md:1–35` carries the same lines);
  - the user's decisions of 2026-10-09 on the same class of conflict, as the orchestrator relayed them: T607 O5
    (`/new-feature`: the Scrum Master proposes, the orchestrator creates tasks), T613 S1 (the Scrum Master proposes, the
    orchestrator writes the ledger), T613 S2 (entries use the ledger's seven columns; story points and sprint go to the
    GitLab issue and the task brief) and T613 K (`checkpoint-<SEQ>-<phase>.md`). I honor them as precedent and do not
    re-litigate them.
- **Supersedes**: none (first version).
- **Decision references**: ADR-008 Step A (P3a), Step B (P1), § Scope (recorded user decision), D2, D4, D5, P4, P5;
  ADR-007 §5 (never relax a check). No new ADR is minted.
- **Status of every edit in this document**: **held for the user. Nothing is applied.** The only other file changed by
  this task is the `**Status:**` line of `task-T615.md`.

## 0. Method and limits

- **Commit.** The orchestrator states the worktree is on `develop` `2f4b2c8` plus one scoping commit **(unverified: no
  shell, no `git`)**. Every line number below was read live in the worktree, in the source files under
  `implementation/knowledge/`. Earlier artifacts' line numbers were not trusted; each clause was re-read.
- **No shell and no grep tool.** Every count in §4 comes from reading whole files and is **(unverified by grep)**. §5.4
  lists the greps the implementing task must run first. §9 collects every unverified claim.
- **Read in full (source files):**
  - skills `blocker-escalation`, `task-management`, `gitlab-management`, `dependency-graphing`, `checkpoint-protocol`,
    `project-planning`, `plan-approve-execute`, `technical-debt-tracking`, `validation-gates`, `poc-evaluation`,
    `rapid-prototyping`, `code-review`, `release-workflow`, `testing-strategy`, `receiving-code-review`,
    `systematic-debugging`, `ci-cd-pipeline`, `verification-before-completion`;
  - agents `scrum-master`, `orchestrator`, `tech-lead`, `release-manager`, `qa-engineer`, `frontend-developer`,
    `database-engineer`, `technical-writer`, `ux-designer`, `technology-scout`, `context-retriever`, `poc-orchestrator`,
    `technical-debt-narrator`, `evaluation-agent`, `poc-qa-engineer`, `poc-devops-engineer`, `poc-technical-writer`;
  - commands `sprint-status`, `team-status`, `batch`, `bug-report`, `handoff`, `validate-tasks`, `plan`, `new-feature`,
    `new-poc`, `prepare-release`, `new-project`, `validate-workflow`;
  - `AGENTS.md:1–73`, `implementation/AGENTS.md:1–35`, `docs/tasks/validate-tasks.py`, `docs/checkpoints/_template.md`,
    `tests/_baselines/root-install-drift.json`, `implementation/registry/summary.md`, `tests/golden/README.md`,
    `docs/tasks/active-tasks.md:1–20`.
- **Projections.** For the four skills I read the clause lines in all 7 platform copies of `blocker-escalation`,
  `task-management`, `gitlab-management` and `dependency-graphing` (28 files), and the clause lines of the `.claude` copy of
  `checkpoint-protocol`. Each projection is one line lower than its source (the `maturity:` line is dropped).
- **Golden.** I read no golden case this time and I opened nothing under `tests/golden/held-out/`. I name no golden case in
  this document. I cannot say whether any case, open or held-out, quotes a clause below (§5.2).
- **Secrets.** I read no `.env*`, credential or key file. I edited nothing under `.claude/`, `.github/` or any other derived
  platform folder, and nothing outside this artifact and the brief's `**Status:**` line.
- **Encoding.** `§` is U+00A7 and `—` is U+2014 (it appears in quoted source text and in some held replacement rows; no
  prose edit introduces one beyond what its Before already has). Each four-backtick fence holds one Before/After pair;
  inner single and triple backticks are literal. Apply each edit by its Before text, never by line number. Match every
  single-line Before as a **whole line** (`grep -cxF`).
- **Scope-gaming guard (ADR-008 § Risks).** Observations O-1 to O-5 were recorded in `task-protocol-and-checkpoint-name-
  ruling-v1.md` §7 on 2026-10-09, before this task. They cite `blocker-escalation:78`, `task-management:112–124`,
  `gitlab-management:134–137, :170–172`, `dependency-graphing:26` and `checkpoint-protocol:101, :59`. Those are the lines
  where I read the clauses now, so no shift occurred, and the T614 edits to `checkpoint-protocol` replaced single lines
  (no line moved) **(unverified: I cannot diff history)**. No declared-scope sentence relied on below was added in the
  same change as this ruling.
- **Maturity.** I relied on no `maturity:` value anywhere in this document (P4). `blocker-escalation`, `task-management`,
  `gitlab-management` and `dependency-graphing` are `experimental` and `checkpoint-protocol` is `stable`
  (`implementation/registry/summary.md`); none of that decides any step below. `AGENTS.md` is tier 1 by ADR-008 D1. No
  stable instruction is needed for any ruling here.

## 1. Summary of the rulings

| Item | Subject (D3) | Both sides | Step that fired | Outcome | Edits (all held) |
|---|---|---|---|---|---|
| **1** | The actor that sets a task to `blocked` (and back) in `active-tasks.md` | `blocker-escalation:78` (and `:122`) against `AGENTS.md:18` | `:78` A fails, **B (P1)**; `:122` A holds, note | **Amend the skill**: the agent names the tasks in the Blocker Report, the orchestrator sets the Status | BE-1, BE-2 |
| **2** | (a) the actor of a ledger write; (b) the fields a dependency uses; (c) the example rows; (d) when a `done` row leaves the ledger | `task-management:108–132, :157–160, :167–179, :185–186` against `AGENTS.md:14–16, :18–19` and the skill's own `:47–50`, `:54–57` | (a) A holds, note; (b) A fails, **B (P1)** with same-file coherence; (c) A fails, **B (P1)**; (d) A fails, **B (P1)** | **Amend the skill** | TM-1 to TM-4 |
| **3** | (a) the actor of the GitLab-to-ledger sync; (b) the ledger Status values a label maps to | `gitlab-management:137` and `:171–172` against `AGENTS.md:10, :18` | (a) A holds, note; (b) A fails, **B (P1)** | **Amend the skill** | GL-1 to GL-3 |
| **4** | The ledger columns the graph reads | `dependency-graphing:26, :100, :134–140` against `AGENTS.md:14` | A fails, **B (P1)** | **Amend the skill**: read `Depends on`, derive `Blocks` | DG-0 to DG-3 |
| **5** | The ledger a checkpoint's "Completed Tasks" is read from | `checkpoint-protocol:101` against `AGENTS.md:15–16` | A fails, **B (P1)** | **Amend the skill** | CP-1 |
| **6** | The author of a checkpoint | `checkpoint-protocol:59` against `AGENTS.md:28` | **A holds** (jointly satisfiable) | Confirmed. At most a note | CP-2 (optional note) |

**Where the ADR decides and where it does not.** Every item is decided by ADR-008 Step A or Step B. The other document in
each pair is a skill, so **no conflict is inside tier 1** and nothing is escalated under P5.

**The `BlockedBy` / `Blocks` columns (the brief's tier-1 example).** The brief asks whether the ledger schema should gain
these columns and says such a conflict escalates under P5. I rule that it is not a tier-1 conflict. Exactly one tier-1
sentence speaks to the columns (`AGENTS.md:14`, a closed list of seven); no other tier-1 text I read mentions `BlockedBy` or
`Blocks` (`coding-standards` was not read, §9); and the other side is a skill. The question is also settled by a recorded
user decision: T613 S2, "entries use the ledger's seven columns", and ADR-008 § Scope puts a "question already settled by …
a recorded user decision" outside the ranking: "That decision governs, and documents are amended to it." The skill's own table
(`task-management:54–57`) already declares the same seven columns, so the same-file ground points the same way. Extending the
schema would be a change to a tier-1 file, which ADR-008 P1 never does on its own ("This ADR never amends a tier-1 document to
match a lower one"). It stays available to the user as option C of items 2 and 4 in §6, with its cost, and is not recommended.

**Scope of "ledger".** `AGENTS.md:14` fixes the columns of `active-tasks.md` only. The plan document's own Task Breakdown
table (`plan-approve-execute:58–60`), the checkpoint's tables and the debt ledger are different objects (observations
O-9, O-10, O-12).

## 2. D5 records

### 2.1 Item 1 — `blocker-escalation`: who sets a task to `blocked`

**Verbatim clauses (live, source file).**

Tier 1, `AGENTS.md` (identical in `implementation/AGENTS.md`):
- `:5` "- Only orchestrators are user-invocable. All other agents are subagents."
- `:18` "- Only orchestrators create/transition tasks. Agents report completion and blockers."
- `:46–49` "## Blocker Protocol" … "- Max 2 retries before user escalation. Agents MUST NOT silently fail."

`implementation/knowledge/skills/blocker-escalation/SKILL.md`:
- `:3` (description) "Handle and escalate blockers using the structured escalation protocol. Use when an agent is blocked, needs to report a blocker, or when the orchestrator needs to route/resolve blockers."
- `:73` "### 1. Agent Reports a Blocker"
- `:77–79` "3. If both attempts fail, create a Blocker Report." / "4. Transition the impacted task(s) to `blocked` status in `active-tasks.md`." / "5. Send the Blocker Report to the orchestrator."
- `:81` "### 2. Orchestrator Triages a Blocker"; `:93` "3. If the orchestrator can resolve directly (e.g., re-ordering tasks), do so and close the blocker."
- `:119` "### 4. Resolve and Close a Blocker"; `:122` "2. Transition impacted tasks from `blocked` back to `in_progress`."; `:127` "- **Resolved By:** <agent or user>"

**Subject (D3).** The actor that sets a task's Status to `blocked` (and, at `:122`, back to `in_progress`) in `active-tasks.md`.
Filing and routing the Blocker Report is a different act, which both documents give to the agent and the orchestrator in turn.

| Field | Content |
|---|---|
| **Step A, `:78`** | **Fails on the literal text.** MUSTs: `:78` is an imperative inside Procedure 1, whose heading names the actor ("Agent Reports a Blocker"), so it tells the reporting agent to write the ledger. `AGENTS.md:18` is **exclusive** ("**Only** orchestrators"), and the reporting agent is not an orchestrator (`AGENTS.md:5`). Setting `blocked` is a transition of the lifecycle at `AGENTS.md:8–11`. **One-value test:** one transition has one writer; `:78` names the agent and `:18` names only orchestrators. **Rescue reading (ii), recorded:** read `:78` as "state the transition in the report". Then step 5 sends the report on and both texts hold. I rule on reading (i), the face value, for the reason `task-protocol-and-checkpoint-name-ruling-v1.md` §2.1 gave: the verb is the ledger act everywhere else, and a subagent reads the clause at face value. **The conclusion does not depend on it.** Under (ii) the held edit is the note ADR-008 Step A permits. |
| **Step A, `:122`** | **Holds.** The actor is unnamed ("Transition impacted tasks …"). The orchestrator can obey it, and Procedure 2 (`:93`) already gives it the closing of a blocker. `:127` "Resolved By: <agent or user>" names who resolved the blocker, not who writes the row. A note is the most the ADR allows (BE-2). |
| **Narrow readings that hold** | `:15`–`:16` ("An agent encounters an obstacle", "A task transitions to `blocked` status") are passive triggers. `:79` (send the report to the orchestrator) and Procedures 2–3 are compliant and untouched. |
| **Step B (P1), `:78`** | **Fires.** (a) *Quotable:* `AGENTS.md:18` and `:78`, above. (b) *Reach, declared-scope text relied on:* `AGENTS.md` declares no scope narrower than the repository (D2), and § Task Protocol "is not scoped to a track, an agent or a file type" (`poc-skills-alignment-v1.md` §1.3). The tier-1 sentence names blockers itself ("Agents report completion and blockers"), and § Blocker Protocol is a section about them. The skill also places itself inside: its description (`:3`), `:79` ("Send the Blocker Report to the orchestrator") and `:81` ("Orchestrator Triages a Blocker"). (c) Step A fails on reading (i). (d) The other document is a skill. |
| **Step fired** | `:78`: **B (P1)**, with the Step A note as the fallback. `:122`: **A** (note). |
| **Amendment** | **Amend the skill**, not `AGENTS.md` (P1 Remedy). BE-1 (`:78`), BE-2 (`:122`, note). Both cite `AGENTS.md` and do not restate its rules at length. The Blocker Report format, severities and the 2-retry rule are untouched (but see O-1). |
| **Precedent** | `task-protocol-and-checkpoint-name-ruling-v1.md` §2.1 (T613 S1, the user's decision "Apply both"): the agent proposes, the orchestrator writes. `project-planning/SKILL.md:209` and `:217` (live): "An agent other than an orchestrator that applies this skill proposes the tasks to the orchestrator and does not write the ledger." and "Only an orchestrator transitions a task". |
| **Maturity** | Not relied on. |

### 2.2 Item 2 — `task-management`: actor, dependency fields, examples, archive timing

**Verbatim clauses (live, source file `implementation/knowledge/skills/task-management/SKILL.md`).**

Tier 1, `AGENTS.md`:
- `:14` "- Task list: `docs/tasks/active-tasks.md` — columns: `ID | Title | Owner | Status | Priority | Depends on | Last update`"
- `:15` "- **INVARIANT:** `active-tasks.md` MUST NEVER hold a `done` or `cancelled` row. Terminal rows move to `docs/tasks/completed-tasks.md` (columns: `ID | Title | Owner | Done on | Outcome / artifact`) in the same edit."
- `:16` "- Archival is orchestrator-only and immediate. See skill `task-management` § "Complete a Task"."
- `:18` "- Only orchestrators create/transition tasks. Agents report completion and blockers."
- `:19` "- Sequential IDs: `T001`, `T002`, … Priorities: `P0` (critical path), `P1`, `P2`."

The skill:
- `:3` (description) "Manage the task lifecycle: create, read, update, transition, and archive tasks in docs/tasks/. Use when creating tasks, updating task status, building task dependency graphs, or archiving completed work."
- `:21–26` (Rails, Failure mode) "… An agent other than the orchestrator performing the archive (moving a row, not merely reporting completion), or completing a task out of the mandated 4-step atomic order, breaks the audit trail this skill exists to preserve."
- `:47–50` "> ## INVARIANT (never violate)" … "> `active-tasks.md` MUST NEVER contain a row whose Status is `done` or `cancelled`." / "> The row is removed in the SAME edit that sets the terminal status."
- `:54–57` "### active-tasks.md — 7 columns, in this exact order" / "| ID | Title | Owner | Status | Priority | Depends on | Last update |"
- `:70` "| Priority | `P0` \| `P1` \| `P2`. NEVER `critical`/`high`/`medium`/`low`. |"
- `:99` "| `pending` | `in_progress` | Agent picks up the task |"
- `:110–116` "### 1. Create a Task" … "3. Add a new row to the table with status `pending`." / "4. If the task depends on other tasks, populate `BlockedBy`." / "5. If other tasks depend on this task, update their `BlockedBy` field and this task's `Blocks` field."
- `:118–124` "### 2. Update Task Status" … "3. Update the `Status` field."
- `:126–132` "### 3. Manage Dependencies" / "1. When adding a dependency, update **both** sides:" / "   - Add the dependency ID to the dependent task's `BlockedBy` field." / "   - Add the dependent task's ID to the dependency's `Blocks` field." / "2. Before transitioning a task to `in_progress`, verify all `BlockedBy` tasks are `done`." / "3. When a task reaches `done`, check its `Blocks` field and evaluate if blocked tasks can be unblocked."
- `:134–136` "### 4. Complete a Task (ATOMIC — all 4 steps in one edit session)" / "Performed by the ORCHESTRATOR ONLY. Other agents report completion; they never move rows."
- `:157–160` "### 6. Dependency bookkeeping" / "When T-x is completed, for every active row whose `Depends on` contains T-x, rewrite that cell as `T-x (done)`. NEVER delete the reference — it is the audit trail."
- `:167`, `:174` (two identical lines) "| T012 | Add rate limiting to API | pending | backend-dev | — | T010 | high | 2025-03-20 |"; `:179` "| T012 | Add rate limiting to API | in_progress | backend-dev | — | — | high | 2025-03-20 |"
- `:185` "- Always update both sides of a dependency relationship."
- `:186` "- Archive promptly — do not leave `done` tasks in `active-tasks.md` longer than one checkpoint cycle."

**Subjects (D3). Four, so four conflicts.** (a) the actor of a ledger write; (b) the field that carries a dependency; (c) the shape of the example rows (cells, order, Priority and Owner values); (d) when a terminal row leaves `active-tasks.md`.

| Sub-item | Step A | Step B (P1) and step fired | Amendment |
|---|---|---|---|
| **2a. Actor** (`:108–132`, `:99`) | **Holds.** Procedures 1–3, 5 and 6 name no actor, so an orchestrator can obey them and `AGENTS.md:18` too. `:99` "Agent picks up the task" is a trigger, not a writer. **But the file marks only Procedure 4 "ORCHESTRATOR ONLY" (`:136`) and the Rails name only the archive (`:22–26`).** A reader can infer that the other procedures are open to any agent, and `:3` invites any agent to "create … update … transition". That is the S1 hazard, one step removed. | **A**, at most a note (ADR-008 P3a). | **TM-1**: one sentence under `## Procedures` that names the actor for every ledger write and tells other agents to propose. Same model as `project-planning:209` |
| **2b. Dependency fields** (`:115–116`, `:129–132`, `:185`) | **Fails.** `AGENTS.md:14` lists seven columns, a closed set, and the skill's own table at `:54–57` repeats them ("7 columns, in this exact order"). Neither `BlockedBy` nor `Blocks` is among them, so `:115–116` and `:129–132` tell the reader to write cells that do not exist, and "update both sides" cannot be obeyed. **One-value test:** one dependency edge has one carrier; the schema says `Depends on`, `:115` says `BlockedBy`. `BlockedBy` is only another label for `Depends on` (the same relation). `Blocks` is its inverse, which no column stores. The skill contradicts itself too: `:157–160` (Procedure 6) uses `Depends on`. | **B (P1).** (a) Quotable: `AGENTS.md:14` and `:115`, above. (b) Reach: `AGENTS.md:14` is the ledger's schema; the skill places itself inside it (`:54–57`, and `AGENTS.md:16` names this skill for archival). (c) Step A fails. (d) A skill. **Second ground, outside the ADR:** same-file coherence (`:54–57` and `:157–160` against `:115–116`). **Also:** the user's T613 S2 decision (seven columns) governs (ADR-008 § Scope). No P5. | **TM-2a to TM-2d**: `BlockedBy` becomes `Depends on`; `Blocks` is derived (the rows whose `Depends on` names the task), never stored |
| **2c. Example rows** (`:164–180`) | **Fails.** Each example row has eight cells in the order ID, Title, Status, Owner, `—`, Depends on, Priority, date. The schema has seven, in the order ID, Title, Owner, Status, Priority, Depends on, Last update, and the Priority value is `high`, which `:70` forbids by name ("NEVER `critical`/`high`/…"). The `After` row also drops the dependency (`—`), against `:159–160` "NEVER delete the reference". These are same-file defects and contradict `AGENTS.md:14` and `:19`. The Owner value `backend-dev` is not an agent slug (`:68`). | **B (P1)** with the same-file ground. (a) Quotable. (b) As 2b. (c) Fails. (d) A skill. | **TM-3a to TM-3c**: seven cells in the schema's order, `P1`, `backend-developer`, and `T010 (done)` after completion |
| **2d. Archive timing** (`:186`) | **Fails.** `:186` allows a `done` row to stay in `active-tasks.md` for up to one checkpoint cycle. `AGENTS.md:15` ("MUST NEVER hold a `done` … row … in the same edit"), `AGENTS.md:16` ("immediate") and the skill's own `:47–50` and `:93` ("archive immediately") say never. **One-value test:** at the moment a task is `done` the row either is in the ledger or is not. | **B (P1)** with the same-file ground. (a) Quotable. (b) `AGENTS.md:15–16` name the archive and name this skill's § "Complete a Task" for the mechanics. (c) Fails. (d) A skill | **TM-4**: archive in the same edit, never for a cycle |

**Declared-scope text relied on (D5).** `AGENTS.md:14–19` (reach: each sentence reaches what it names, D2) and the skill's own words:
`:3` (description: "create, read, update, transition, and archive tasks"), `:9–13` (Rails, Inputs: "any lifecycle event touching
`docs/tasks/active-tasks.md`"), `:54–57` (the seven columns) and `:136` ("Other agents report completion; they never move rows").
Sub-item 2d is **beyond the brief's list** (it was found while re-reading the file) and is disclosed as such; the user may decline
TM-4 alone (§6).

**Precedent.** `task-protocol-and-checkpoint-name-ruling-v1.md` §2.2 (T613 S2, "the ledger's own seven columns") and
`project-planning/SKILL.md:209–211` (live): "a row in `active-tasks.md` with the columns `ID | Title | Owner | Status | Priority | Depends on | Last update` …
which the orchestrator sets".

**Maturity.** Not relied on.

### 2.3 Item 3 — `gitlab-management`: the sync-back actor and the mapped Status values

**Verbatim clauses (live, source file `implementation/knowledge/skills/gitlab-management/SKILL.md`).**

Tier 1: `AGENTS.md:10` "pending → in_progress → blocked → in_review → done | cancelled"; `AGENTS.md:18` (above).

The skill:
- `:131` "**Source of truth:** `docs/tasks/active-tasks.md` is the primary task register. GitLab issues mirror it for visibility and team collaboration."
- `:134–137` "1. When a task is added to `active-tasks.md`, create a corresponding GitLab issue …" / "2. When a task status changes in `active-tasks.md`, update the GitLab issue labels to match." / "3. When a task is moved to `completed-tasks.md`, close the corresponding GitLab issue." / "4. When a GitLab issue is updated externally (e.g., by a human team member), sync the change back to `active-tasks.md` at the next checkpoint."
- `:139` "**Conflict resolution:** If `active-tasks.md` and a GitLab issue disagree, `active-tasks.md` wins unless the GitLab update was made by a human (identifiable by author)."
- `:170` "| `status::todo` | Task not started | Maps to `pending` in active-tasks.md |"
- `:171` "| `status::in-progress` | Task actively being worked | Maps to `in-progress` in active-tasks.md |"
- `:172` "| `status::review` | Task complete, awaiting review | Maps to `review` in active-tasks.md |"
- `:173` "| `status::blocked` | Task blocked by a dependency or blocker | Maps to `blocked` in active-tasks.md; must have a linked `[BLOCKER]` |"

**Subjects (D3). Two.** (a) the actor that syncs a GitLab change back to the ledger; (b) the ledger Status value a label maps to.

| Sub-item | Step A | Step B (P1) and step fired | Amendment |
|---|---|---|---|
| **3a. Actor** (`:137`) | **Holds.** No actor is named, "at the next checkpoint" points at the orchestrator's act, and the orchestrator can obey both texts. It is the same shape as `blocker-escalation:122`. The hazard is the Scrum Master or any reader taking it as a licence to write. | **A**, note only. | **GL-1**: name the orchestrator and tell others to report. Consistent with the already-applied `scrum-master:25` |
| **3b. Mapped values** (`:171–172`) | **Fails.** The Status value set is closed and spelled `in_progress` and `in_review` (`AGENTS.md:10`; `task-management:69`). `:171–172` say the ledger value is `in-progress` and `review`. **One-value test:** the label `status::in-progress` maps to one ledger value, and the two texts compute different spellings. `/new-project:56` (a command, so a witness only) says it in as many words: "The state is spelled `in_review`, NOT `review`." The `status::` **label names** are this skill's own GitLab vocabulary (`:52–55`) and are not ledger values. | **B (P1).** (a) Quotable. (b) `AGENTS.md:10` is the lifecycle; the skill's cell says "in active-tasks.md". (c) Fails. (d) A skill. | **GL-2, GL-3**: change only the mapped ledger value; leave the label names. Same defect `E-G7b` fixed in `project-planning` (live `:217`) |

**Declared-scope text relied on.** `AGENTS.md:8–11` (Lifecycle States, a tier-1 section whose subject is the Status value set)
and the skill's `:127–131` ("The canonical task list lives in `docs/tasks/active-tasks.md`. GitLab issues are a secondary
projection of this list") and the "Maps to … in active-tasks.md" cells themselves.

**Maturity.** Not relied on.

### 2.4 Item 4 — `dependency-graphing`: the columns the graph reads

**Verbatim clauses (live, source file `implementation/knowledge/skills/dependency-graphing/SKILL.md`).**

Tier 1: `AGENTS.md:14` (above).

The skill:
- `:25` "1. Read `docs/tasks/active-tasks.md`."
- `:26` "2. For each task row, extract `ID`, `Title`, `Status`, `Blocks`, and `BlockedBy`."
- `:27` "3. Build an adjacency list: for each task, record its outgoing edges (tasks it blocks)."
- `:38–39` "   - `in_review` → yellow fill" / "   - `done` → green fill"
- `:100` "2. Find the longest path from any root node (no `BlockedBy`) to any leaf node (no `Blocks`)."
- `:134–140` the example table "| ID | Title | Blocks | BlockedBy |" and five rows.

**Subject (D3).** The ledger columns a dependency graph is built from.

| Field | Content |
|---|---|
| **Step A** | **Fails.** `:26` requires extracting two fields from each ledger row. `AGENTS.md:14` lists seven columns, a closed set (restated by `task-management:54–57`), and neither field is among them. One cannot extract a column that does not exist, so no single action obeys `:26` and `AGENTS.md:14`. **One-value test:** the dependency relation has one stored carrier, `Depends on`. `BlockedBy` is a label for it and `Blocks` is its inverse, derivable from the other rows. This skill only reads, so no actor conflict arises. **Related defect, same family as item 5:** `:38–39` colours `done` nodes, yet `:25` reads only `active-tasks.md`, which never holds a `done` row (`AGENTS.md:15`). `/sprint-status:41–44` and `/team-status:46–49` show the right sources. |
| **Step B (P1)** | **Fires.** (a) Quotable. (b) `AGENTS.md:14` is the ledger's schema; the skill places itself inside it (`:25`, `:134`: "Given active tasks"). (c) Fails. (d) A skill. The T613 S2 decision (seven columns) also governs (ADR-008 § Scope). |
| **Step fired** | **B (P1).** |
| **Amendment** | **Amend the skill.** DG-1 (`:26`), DG-2 (`:100`), DG-3 (the table) read `Depends on` and derive `Blocks`. DG-0 (`:25`) adds `completed-tasks.md` as the source of `done` nodes (consequential, beyond the brief's list; model `/sprint-status:41–44`). The Mermaid output of the example does not change. |
| **Maturity** | Not relied on. |

### 2.5 Item 5 — `checkpoint-protocol:101`: where "Completed Tasks" is read from

**Verbatim clauses (live, source file `implementation/knowledge/skills/checkpoint-protocol/SKILL.md`).**

Tier 1: `AGENTS.md:15` (above) and `:16` "- Archival is orchestrator-only and immediate."

The skill: `:101` "3. For "Completed Tasks," query `active-tasks.md` for tasks marked `done` since the last checkpoint." Context: `:9–20`
(Rails: "a checkpoint's "Completed Tasks"/"Active Tasks" tables are a point-in-time summary derived from that ledger") and `:66–68`
(the table "| ID | Title | Completed |").

**Subject (D3).** The ledger that holds a completed task.

| Field | Content |
|---|---|
| **Step A** | **Fails.** `AGENTS.md:15` is exclusive in the other direction: `active-tasks.md` **MUST NEVER** hold a `done` row, and terminal rows are in `completed-tasks.md`. `:101` tells the reader to find `done` rows in `active-tasks.md`. **One-value test:** the home of a completed task is one file; the texts name different files. Obeyed as written, the step finds nothing. **Rescue reading (ii), recorded and rejected:** "since the last checkpoint" implies a window in which a row has been set `done` but not yet archived. That window does not exist: the archive is "in the same edit" (`AGENTS.md:15`). |
| **Step B (P1)** | **Fires.** (a) Quotable. (b) *Reach:* `AGENTS.md:15–16`; the skill places itself in the ledger's reach in its Rails ("derived from that ledger"). (c) Fails. (d) A skill. |
| **Step fired** | **B (P1).** |
| **Amendment** | **Amend the skill.** CP-1 reads `completed-tasks.md` by `Done on`. The table heading `Completed` stays: it is a checkpoint column, not a ledger column. |
| **Maturity** | Not relied on. |

### 2.6 Item 6 — `checkpoint-protocol:59`: the author of a checkpoint

**Verbatim clauses (live).** Tier 1: `AGENTS.md:28` "- Written at every phase boundary by the orchestrator." The skill: `:59`
"**Author:** <agent-name or orchestrator>"; `:35–39` the triggers ("At every phase boundary", "After every 3–5 task completions",
"Before major delegation to a sub-agent", "Before anticipated context window exhaustion", "When explicitly requested by the
orchestrator or user"); `:50–51` "This matches `AGENTS.md`'s Checkpoint Protocol section verbatim — see that section for the canonical filename convention this skill implements."

**Subject (D3).** The author of a checkpoint file.

| Field | Content |
|---|---|
| **Step A** | **Holds. Confirmed.** `AGENTS.md:28` fixes the writer **at a phase boundary** and carries no "only". `:59` is an open slot in a template, and `orchestrator` is a value the slot accepts, so a phase-boundary checkpoint written by the orchestrator obeys both. The skill adds triggers beyond phase boundaries (`:36–39`), for which `AGENTS.md:28` names no writer, so it **adds** checkpoints without competing with the phase-boundary rule (D4, specialisation). **One-value test:** for one phase-boundary checkpoint, `AGENTS.md:28` computes `orchestrator` and `:59` admits it. The slot does not compute a different value. **Hazard, not conflict:** a subagent that applies the skill at a phase boundary and fills `<agent-name>` would break `AGENTS.md:28`. Four other documents already say the orchestrator writes checkpoints (`rapid-prototyping:12`, `poc-evaluation:12`, `orchestrator:150`, `/new-feature:30`). |
| **Step fired** | **A.** No contradiction, so no rank. |
| **Amendment** | None required. The permitted note is the optional edit **CP-2** (set the template's Author to `orchestrator`). It touches the same file as CP-1, so it adds no root-drift path. |
| **Maturity** | Not relied on. |

## 3. Held edits (apply verbatim, only after the user decides)

Each Before is unique in its file by reading the whole file **(unverified by grep)**. No edit relaxes a check (ADR-007 §5). None is upward:
each moves a skill toward `AGENTS.md`. None touches a command, a tier-1 file, the validator or a golden path. Edits are listed by
source file; the platform projections are regenerated, never edited by hand.

### 3.1 Item 1 (option 1-A): `implementation/knowledge/skills/blocker-escalation/SKILL.md`

**BE-1 — `:78`.** Anchor: the full line, which occurs once.

````
Before:
4. Transition the impacted task(s) to `blocked` status in `active-tasks.md`.

After:
4. Name the impacted task(s) in the Blocker Report. Do not edit `active-tasks.md`: "Only orchestrators create/transition tasks. Agents report completion and blockers." (`AGENTS.md` § Task Protocol), so the orchestrator sets those tasks to `blocked`.
````

**BE-2 — `:122`** (a note; Step A holds). Anchor: the full line, which occurs once.

````
Before:
2. Transition impacted tasks from `blocked` back to `in_progress`.

After:
2. The orchestrator transitions impacted tasks from `blocked` back to `in_progress` (`AGENTS.md` § Task Protocol).
````

### 3.2 Item 2 (option 2-A): `implementation/knowledge/skills/task-management/SKILL.md`

**TM-1 — `## Procedures` (`:108`, sub-item 2a).** Anchor: the whole line `## Procedures`, which occurs once.

````
Before:
## Procedures

After:
## Procedures

Every ledger write in this section (create, update, dependency bookkeeping, complete, cancel) is performed by an orchestrator: "Only orchestrators create/transition tasks. Agents report completion and blockers." (`AGENTS.md` § Task Protocol). An agent other than an orchestrator that applies this skill proposes the change to the orchestrator and does not write the ledger.
````

**TM-2a — `:115`.**

````
Before:
4. If the task depends on other tasks, populate `BlockedBy`.

After:
4. If the task depends on other tasks, set its `Depends on` cell to their IDs, comma-separated (`—` when there are none).
````

**TM-2b — `:116`.**

````
Before:
5. If other tasks depend on this task, update their `BlockedBy` field and this task's `Blocks` field.

After:
5. If other tasks depend on this task, add this task's ID to their `Depends on` cells. This row needs no entry of its own: the ledger has no `Blocks` or `BlockedBy` column (`AGENTS.md` § Task Protocol).
````

**TM-2c — `:128–132`** (a five-line block; the sub-bullets at `:129–130` start with three spaces).

````
Before:
1. When adding a dependency, update **both** sides:
   - Add the dependency ID to the dependent task's `BlockedBy` field.
   - Add the dependent task's ID to the dependency's `Blocks` field.
2. Before transitioning a task to `in_progress`, verify all `BlockedBy` tasks are `done`.
3. When a task reaches `done`, check its `Blocks` field and evaluate if blocked tasks can be unblocked.

After:
1. When adding a dependency, record it once, in the dependent task's `Depends on` cell. The tasks a task blocks are the rows whose `Depends on` names it: they are derived, not stored.
2. Before transitioning a task to `in_progress`, verify that every task named in its `Depends on` cell is `done` (listed in `completed-tasks.md`, or marked `(done)`).
3. When a task reaches `done`, find the active rows whose `Depends on` names it and evaluate whether they can be unblocked (§ 6 rewrites those cells).
````

**TM-2d — `:185`.**

````
Before:
- Always update both sides of a dependency relationship.

After:
- Record each dependency once, in `Depends on`; never add a `Blocks` or `BlockedBy` field.
````

**TM-3a — `:164–167`** (sub-item 2c; the first example row, with its heading and fence as anchor).

````
Before:
### Creating a Task

```markdown
| T012 | Add rate limiting to API | pending | backend-dev | — | T010 | high | 2025-03-20 |

After:
### Creating a Task

```markdown
| T012 | Add rate limiting to API | backend-developer | pending | P1 | T010 | 2025-03-20 |
````

**TM-3b — `:172–174`** (the `Before:` example; the three-line block starts at the line `Before:` that directly precedes the fence).

````
Before:
Before:
```markdown
| T012 | Add rate limiting to API | pending | backend-dev | — | T010 | high | 2025-03-20 |

After:
Before:
```markdown
| T012 | Add rate limiting to API | backend-developer | pending | P1 | T010 | 2025-03-20 |
````

**TM-3c — `:179`.** Anchor: the full line, which occurs once.

````
Before:
| T012 | Add rate limiting to API | in_progress | backend-dev | — | — | high | 2025-03-20 |

After:
| T012 | Add rate limiting to API | backend-developer | in_progress | P1 | T010 (done) | 2025-03-21 |
````

**TM-4 — `:186`** (sub-item 2d). Anchor: the full line, which occurs once.

````
Before:
- Archive promptly — do not leave `done` tasks in `active-tasks.md` longer than one checkpoint cycle.

After:
- Archive immediately: the row leaves `active-tasks.md` in the same edit that sets `done` or `cancelled` (§ Complete a Task; `AGENTS.md` § Task Protocol). Never leave a terminal row there, not even for one checkpoint cycle.
````

### 3.3 Item 3 (option 3-A): `implementation/knowledge/skills/gitlab-management/SKILL.md`

**GL-1 — `:137`** (a note; Step A holds). Anchor: the full line, which occurs once.

````
Before:
4. When a GitLab issue is updated externally (e.g., by a human team member), sync the change back to `active-tasks.md` at the next checkpoint.

After:
4. When a GitLab issue is updated externally (e.g., by a human team member), report the change to the orchestrator, who syncs it back to `active-tasks.md` at the next checkpoint (`AGENTS.md` § Task Protocol: "Only orchestrators create/transition tasks").
````

**GL-2 — `:171`.**

````
Before:
| `status::in-progress` | Task actively being worked | Maps to `in-progress` in active-tasks.md |

After:
| `status::in-progress` | Task actively being worked | Maps to `in_progress` in active-tasks.md |
````

**GL-3 — `:172`.**

````
Before:
| `status::review` | Task complete, awaiting review | Maps to `review` in active-tasks.md |

After:
| `status::review` | Task complete, awaiting review | Maps to `in_review` in active-tasks.md |
````

### 3.4 Item 4 (option 4-A): `implementation/knowledge/skills/dependency-graphing/SKILL.md`

**DG-0 — `:25`** (consequential). Anchor: the full line `1. Read \`docs/tasks/active-tasks.md\`.`, which occurs once.

````
Before:
1. Read `docs/tasks/active-tasks.md`.

After:
1. Read `docs/tasks/active-tasks.md` for the `pending`, `in_progress`, `blocked` and `in_review` tasks, and `docs/tasks/completed-tasks.md` for the `done` and `cancelled` ones: `active-tasks.md` never holds a terminal row (`AGENTS.md` § Task Protocol). A task ID that appears only in a `Depends on` cell and in `completed-tasks.md` is a `done` node.
````

**DG-1 — `:26`.**

````
Before:
2. For each task row, extract `ID`, `Title`, `Status`, `Blocks`, and `BlockedBy`.

After:
2. For each task row, extract `ID`, `Title`, `Status` and `Depends on`, the ledger's own columns (`AGENTS.md` § Task Protocol), and read each `Depends on` cell as the task IDs it names (`—` means none). The ledger has no `Blocks` or `BlockedBy` column: the tasks a task blocks are the rows whose `Depends on` names it.
````

**DG-2 — `:100`.**

````
Before:
2. Find the longest path from any root node (no `BlockedBy`) to any leaf node (no `Blocks`).

After:
2. Find the longest path from any root node (empty `Depends on`) to any leaf node (no task names it in `Depends on`).
````

**DG-3 — `:134–140`** (the example table; seven lines).

````
Before:
| ID | Title | Blocks | BlockedBy |
|----|-------|--------|-----------|
| T001 | Design schema | T003 | — |
| T002 | Setup CI | T004 | — |
| T003 | Implement API | T004 | T001 |
| T004 | Run tests | T005 | T002, T003 |
| T005 | Deploy | — | T004 |

After:
| ID | Title | Depends on |
|----|-------|------------|
| T001 | Design schema | — |
| T002 | Setup CI | — |
| T003 | Implement API | T001 |
| T004 | Run tests | T002, T003 |
| T005 | Deploy | T004 |
````

### 3.5 Items 5 and 6 (options 5-A, 6-A): `implementation/knowledge/skills/checkpoint-protocol/SKILL.md`

**CP-1 — `:101`.** Anchor: the full line, which occurs once.

````
Before:
3. For "Completed Tasks," query `active-tasks.md` for tasks marked `done` since the last checkpoint.

After:
3. For "Completed Tasks," query `docs/tasks/completed-tasks.md` for the rows whose `Done on` is after the last checkpoint: `active-tasks.md` never holds a `done` row (`AGENTS.md` § Task Protocol).
````

**CP-2 — `:59`** (optional note; Step A holds). Anchor: the full line, which occurs once.

````
Before:
**Author:** <agent-name or orchestrator>

After:
**Author:** orchestrator
````

**Totals.** There are 20 fences and 20 applications: BE-1, BE-2; TM-1, TM-2a to TM-2d, TM-3a to TM-3c, TM-4; GL-1 to GL-3; DG-0
to DG-3; CP-1, CP-2. They touch 5 source files. Subsets: item 1-A is BE-1 and BE-2; item 2-A is TM-1 to TM-4 (9 fences); item 3-A
is GL-1 to GL-3; item 4-A is DG-0 to DG-3; item 5-A is CP-1; item 6-A is CP-2. TM-1 and GL-1 and BE-2 and CP-2 are note-level
edits (Step A holds); the others are Step B amendments.

## 4. Hit counts

- **Scope:** case-sensitive, fixed-string, per file, after every held edit to that file. "Lines" = `grep -cF`; "occurrences" =
  `grep -oF … | wc -l`. "Whole line" = `grep -cxF`.
- **Before** counts are by reading whole files **(unverified by grep)**. A "0 / 0" in the After column means the old wording
  must be gone. Every projection of a file carries the same counts as its source, apart from the dropped frontmatter lines
  (§5.1). The clause lines in the 28 projections of the four skills were read and match the source text exactly.

### 4.1 `skills/blocker-escalation/SKILL.md`

| # | Phrase | Before (lines / occ.) | After | Edit |
|---|---|---|---|---|
| 1 | `Transition the impacted task(s)` | 1 / 1 (`:78`) | **0 / 0** | BE-1 |
| 2 | `Transition impacted tasks from` | 1 / 1 (`:122`) | **0 / 0** | BE-2 |
| 3 | `AGENTS.md` | 0 / 0 | **2 / 2** (`:78`, `:122`) | BE-1, BE-2 |
| 4 | `§ Task Protocol` | 0 / 0 | **2 / 2** | BE-1, BE-2 |
| 5 | `Only orchestrators create/transition tasks` | 0 / 0 | 1 / 1 | BE-1 |
| 6 | `The orchestrator transitions impacted tasks` | 0 / 0 | 1 / 1 | BE-2 |
| 7 | `active-tasks.md` | 1 / 1 (`:78`) | 1 / 1 | BE-1 keeps it |

### 4.2 `skills/task-management/SKILL.md`

| # | Phrase | Before (lines / occ.) | After | Edit |
|---|---|---|---|---|
| 8 | `BlockedBy` | 4 / 4 (`:115`, `:116`, `:129`, `:131`) | **2 / 2** (`:116`-edit, `:185`-edit; both "no/never … `BlockedBy`") | TM-2a to TM-2d |
| 9 | `Blocks` | 3 / 3 (`:116`, `:130`, `:132`) | **2 / 2** (same two lines) | TM-2b, TM-2d |
| 10 | `Depends on` | 4 / 4 (`:55`, `:71`, `:80`, `:159`) | **10 / 11** | TM-2a to TM-2d |
| 11 | `populate \`BlockedBy\`` | 1 / 1 | **0 / 0** | TM-2a |
| 12 | `update **both** sides` | 1 / 1 (`:128`) | **0 / 0** | TM-2c |
| 13 | `update both sides` | 1 / 1 (`:185`) | **0 / 0** | TM-2d |
| 14 | `Archive promptly` | 1 / 1 (`:186`) | **0 / 0** | TM-4 |
| 15 | `longer than one checkpoint cycle` | 1 / 1 | **0 / 0** | TM-4 |
| 16 | `\| high \|` (the example rows) | 3 / 3 (`:167`, `:174`, `:179`) | **0 / 0** | TM-3a to TM-3c |
| 17 | `backend-dev \|` (the example rows) | 3 / 3 | **0 / 0** | TM-3a to TM-3c |
| 18 | `AGENTS.md` | 0 / 0 | **3 / 3** (TM-1, TM-2b, TM-4) | TM-1, TM-2b, TM-4 |
| 19 | `Only orchestrators create/transition tasks` | 0 / 0 | 1 / 1 | TM-1 |
| 20 | `ORCHESTRATOR ONLY` | 1 / 1 (`:136`) | 1 / 1 | untouched |
| 21 | `T010 (done)` | 0 / 0 | 1 / 1 | TM-3c |

Row 10's After is: the 4 existing lines, plus `:115`, `:116`, three lines of the TM-2c block (4 occurrences: item 1 has two) and
`:185`. Rows 8 and 9 After count the two negative mentions in TM-2b and TM-2d, which must remain.

### 4.3 `skills/gitlab-management/SKILL.md`

| # | Phrase | Before (lines / occ.) | After | Edit |
|---|---|---|---|---|
| 22 | ``Maps to `in-progress` `` | 1 / 1 (`:171`) | **0 / 0** | GL-2 |
| 23 | ``Maps to `review` `` | 1 / 1 (`:172`) | **0 / 0** | GL-3 |
| 24 | ``Maps to `in_progress` `` | 0 / 0 | 1 / 1 | GL-2 |
| 25 | ``Maps to `in_review` `` | 0 / 0 | 1 / 1 | GL-3 |
| 26 | `in-progress` | 2 / 3 (`:52`, `:171` twice) | 2 / 2 (the two label names stay) | GL-2 |
| 27 | `sync the change back to` | 1 / 1 (`:137`) | **0 / 0** | GL-1 |
| 28 | `who syncs it back to` | 0 / 0 | 1 / 1 | GL-1 |
| 29 | `AGENTS.md` | 0 / 0 | 1 / 1 | GL-1 |

### 4.4 `skills/dependency-graphing/SKILL.md`

| # | Phrase | Before (lines / occ.) | After | Edit |
|---|---|---|---|---|
| 30 | `Blocks` | 3 / 3 (`:26`, `:100`, `:134`) | **1 / 1** (the negative mention in DG-1) | DG-1 to DG-3 |
| 31 | `BlockedBy` | 3 / 3 (`:26`, `:100`, `:134`) | **1 / 1** (same line) | DG-1 to DG-3 |
| 32 | `Depends on` | 0 / 0 | **4 / 7** (DG-0 one; DG-1 three occ., DG-2 two, DG-3 one) | DG-1 to DG-3 |
| 33 | `completed-tasks.md` | 0 / 0 | 1 / 1 | DG-0 |
| 34 | `AGENTS.md` | 0 / 0 | 2 / 2 (DG-0, DG-1) | DG-0, DG-1 |

Row 32: DG-1 holds three occurrences, DG-2 two, DG-3 the table header once, and DG-0 one ("only in a `Depends on` cell"), so 4 lines and 7
occurrences in total.

### 4.5 `skills/checkpoint-protocol/SKILL.md`

| # | Phrase | Before (lines / occ.) | After | Edit |
|---|---|---|---|---|
| 35 | ``query `active-tasks.md` `` | 1 / 1 (`:101`) | **0 / 0** | CP-1 |
| 36 | `completed-tasks.md` | 0 / 0 | 1 / 1 | CP-1 |
| 37 | `**Author:** <agent-name or orchestrator>` | 1 / 1 (`:59`) | **0 / 0** | CP-2 |
| 38 | `**Author:** orchestrator` | 0 / 0 | 1 / 1 | CP-2 |
| 39 | `AGENTS.md` | 3 / 3 (`:50`, `:104`, `:140`) | 4 / 4 | CP-1 |
| 40 | `Assignee` | 2 / 2 (`:71`, `:154`) | 2 / 2 | untouched (O-10) |

### 4.6 Other sites that repeat a conflicting clause (read; no edit proposed here)

| Conflicting clause | Site (source file, line) | Reading |
|---|---|---|
| An agent sets or transitions a ledger row | none found in the files listed in §0 (beyond items 1 to 3). The remaining writers are orchestrators: `orchestrator:33, :70, :146`, `poc-orchestrator:66`, and every command that runs as `orchestrator` | The earlier hits are fixed (`scrum-master:23, :25, :27, :135`; `project-planning:209–217`; `technical-debt-tracking:12, :110–133`; `poc-evaluation:12, :141`) |
| `BlockedBy` / `Blocks` | `plan-approve-execute:58, :60, :166, :168` (the **plan** table, 2 header lines and 4 rows with a `BlockedBy` cell) | A different object (the plan document); O-9 |
| `high` / `medium` as a task Priority | `plan-approve-execute:168–171` (4 example rows); `project-planning:113–121` (`Must` / `Should`); `code-review:156` ("target sprint") | Plan or review objects; O-9, O-8 |
| Ledger value `in-progress` or `review` | none outside `gitlab-management:171–172` among the files read. `technical-debt-tracking:95` `Status: open \| in-progress \| …` is the **debt ledger**, a different object | Not a hit |
| A `done` row presupposed in `active-tasks.md` | `release-workflow:52–53`; `orchestrator:146`; `verification-before-completion:32` | O-6 |
| `checkpoint-protocol:59` author slot | none; four documents say the orchestrator writes checkpoints (§2.6) | Supports Step A |
| `.claude/`, `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.cline/` copies of the 5 skills (35 files); mirrors under `implementation/.<platform>/` | The same lines, one lower | Derived; regenerated (§5.1) |
| `docs/artifacts/task-protocol-and-checkpoint-name-ruling-v1.md` §7 | Quotes the old clauses | Immutable (`AGENTS.md:24`) |
| `docs/wiki/**`, `docs/guides/**`, `README.md`, `tests/**` | Unknown whether any page or test restates a Before string | **(unverified)**; §5.4 |

## 5. Effects

### 5.1 Projected paths and root drift

A skill projects to 7 root paths, one per platform (`.github`, `.cursor`, `.gemini`, `.opencode`, `.pi`, `.claude`, `.cline`, each
`skills/<name>/SKILL.md`). I read the clause lines in all 28 projections of the four skills, and the `.claude` copy of
`checkpoint-protocol`, so those counts are checked, not inferred. The other six `checkpoint-protocol` copies are **(unverified)**
for the current text.

| Source edit | Root-projection paths | Item |
|---|---|---|
| `skills/blocker-escalation/SKILL.md` | **7** | 1 |
| `skills/task-management/SKILL.md` | **7** | 2 |
| `skills/gitlab-management/SKILL.md` | **7** | 3 |
| `skills/dependency-graphing/SKILL.md` | **7** | 4 |
| `skills/checkpoint-protocol/SKILL.md` | **7** | 5, 6 (one file) |
| **Total if everything is applied** | **35** | |

- **Subsets.** Each item adds its file's 7 paths; items 5 and 6 share one file (7 paths together). Option 2-C or 4-C (the tier-1
  alternative) would not add or remove a root path by itself.
- **Projection line shifts.** Each projection is one line lower than its source (the `maturity:` line is dropped), e.g.
  `blocker-escalation` `:77`, `task-management` `:111–115`, `gitlab-management` `:136, :170–171`, `dependency-graphing` `:25`,
  `checkpoint-protocol` `:100`. I confirmed this in the files I read.
- **Regenerate:** `node implementation/scripts/sync.mjs --root implementation`, then `python3
  implementation/scripts/generate-registry.py`, each followed by `--check`. `implementation/registry/index.json` changes for the
  5 entries (checksums). `implementation/registry/summary.md` should not change, since no `maturity:` changes **(unverified)**.
- **Mirrors.** `sync.mjs` also writes the same files under `implementation/.<platform>/`. Whether the mirrors are tracked is
  **(unverified)**. They are not root drift.
- **Root drift.** `tests/_baselines/root-install-drift.json` reads `"drift": []` (emptied by the fourteenth refresh). The
  implementing task declares exactly the paths `python3 -m tests.functional.test_root_install_parity --print-drift` prints
  (expected 35 if everything is applied). It does not refresh the repo root; that is a separate, user-approved
  `--projections-only` refresh.

### 5.2 Golden and test coupling

| Item | Coupling | Effect |
|---|---|---|
| Open golden cases | **Not searched.** I read no case this time. The suite covers five commands (`tests/golden/README.md`), and I found no sign that a case quotes a skill, but I cannot grep. T613 read three open briefs and none quoted `scrum-master` or `checkpoint-protocol`. | **Unknown.** The orchestrator should grep `tests/golden/open/` for the Before strings in §5.4 before the implementing task is dispatched |
| Held-out cases | I did not open `tests/golden/held-out/` | **Unknown.** The orchestrator, under its read/audit exception, should run the same greps there, and report only a hit count, not a case name |
| `docs/tasks/validate-tasks.py` | Checks 7 cells per active row (`C2`), the Status and Priority sets (`C4`), and `Depends on` tokens (`C12–C14`). It reads no skill text | Unaffected by items 1 to 6. **An extension of the ledger columns (options 2-C, 4-C) would break `C2` for every row**, and it would have to change in the same task |
| `test_root_install_parity` | The one known coupling (§5.1) | Needs the printed paths declared |
| Other tests | I could not search `tests/` | **Unknown whether any test asserts a Before string** (§5.4) |

### 5.3 Baseline and grant

- **Protected-path grant:** **none needed.** No edit touches `tests/golden/**` or `scripts/scorecard.py`.
- **Evaluator-hash baseline:** **none needed.** `scripts/scorecard.py --check` stays at the current baseline (v20 per
  `docs/tasks/active-tasks.md:7` and the orchestrator's notes **(unverified)**). The implementing task reads the current figures
  from the repo, not from this document.
- **Checks that should be unaffected (unverified):** `check-maturity.py --root implementation` and `python3 docs/tasks/validate-tasks.py`
  (neither reads these strings).

### 5.4 Pre-flight greps for the implementing task (not run here; I have no shell)

Run and report, then stop if a non-golden test asserts a Before string. Report golden hits to the orchestrator only, as a count,
without naming a case.

- `grep -rnF -e 'Transition the impacted task' -e 'Transition impacted tasks from' -e 'populate `BlockedBy`' -e 'update their `BlockedBy`' -e 'Archive promptly' -e 'sync the change back to' -e 'Maps to `in-progress`' -e 'Maps to `review`' -e 'query `active-tasks.md`' -e 'agent-name or orchestrator' implementation/ docs/wiki docs/guides README.md tests/ --include='*.md' --include='*.py' --include='*.mjs' --include='*.json' --include='*.yaml'`
- `grep -rnF -e '`Blocks`' -e '`BlockedBy`' implementation/knowledge docs/wiki docs/guides tests/`, then read each hit for an asserted string.
- `grep -rln 'task-management\|dependency-graphing\|gitlab-management\|blocker-escalation\|checkpoint-protocol' tests/ --include='*.py' --include='*.yaml' --include='*.json'`, then read each hit.
- Compare each count with §4, and the `Before` match counts with the "occurs once" claims in §3.

## 6. The user question (one round)

**Q-T615 — The four skills and the two `checkpoint-protocol` observations.**

**Answer with one letter per item (for example "1-A, 2-A, 3-A, 4-A, 5-A, 6-A"), or say "all recommended". Nothing is applied before you answer.**

All six items are decided by ADR-008 Step A or Step B, because the other document is a skill and no conflict is inside tier 1.
Options A and B are therefore "approve the ruled edit" or "hold it". Option C exists only where changing the tier-1 text instead is
your prerogative. ADR-008 never does it on its own, and I have drafted no edit for it. **Items 2 and 4 share one schema question
(`BlockedBy` / `Blocks`): answer them in the same direction, because 2-A with 4-C, or 2-C with 4-A, would leave the two skills
disagreeing.**

**Item 1 — `blocker-escalation:78` (and `:122`) against `AGENTS.md:18`** (who sets a task to `blocked`)

| Option | What changes | Consequences |
|---|---|---|
| **1-A (Recommended)** | BE-1, BE-2: the agent names the tasks in the Blocker Report, the orchestrator sets the Status | Same model as your T613 S1 decision. 7 root-drift paths. The report format, severities and 2-retry rule are untouched |
| **1-B** | Hold | The skill keeps telling every blocked subagent to write the ledger, against `AGENTS.md:18` |
| **1-C** | Let the reporting agent set `blocked`, by changing `AGENTS.md:18` in a separate task | A tier-1 change, no edit drafted. It reverses your T613 S1 decision and contradicts `AGENTS.md:5` and `orchestrator:33, :70` unless those change too |

**Item 2 — `task-management` (actor note, `BlockedBy`/`Blocks`, example rows, archive timing)**

| Option | What changes | Consequences |
|---|---|---|
| **2-A (Recommended)** | TM-1 to TM-4 (9 fences): an actor sentence, `Depends on` in place of `BlockedBy`/`Blocks` (the inverse is derived), seven-cell example rows with valid values, and "archive immediately" | Matches your T613 S2 decision, the skill's own table (`:54–57`), Procedure 6 (`:157–160`) and `AGENTS.md:14–16`. 7 paths. TM-4 alone is beyond the brief's list: say "2-A without TM-4" if you want it left out |
| **2-B** | Hold | The skill still tells the reader to write two columns the ledger lacks, and its examples fail `validate-tasks.py` `C2`/`C4` if copied |
| **2-C** | Keep `BlockedBy`/`Blocks` and add them to `AGENTS.md:14`, in a separate instruction-change task; apply TM-1 and TM-4 now | A tier-1 and schema change with no edit drafted. It reverses your T613 S2 decision. `docs/tasks/validate-tasks.py` (`C2`), `/batch:26–29`, `/bug-report:52–53`, `project-planning`, `technical-debt-tracking`, `dependency-graphing` and every ledger fixture would follow. **Not recommended** |
| **2-D** | Apply TM-1, TM-3 and TM-4 and hold only TM-2 (the schema part) | The skill stays self-contradictory on the dependency field (`:54–57` and `:157–160` against `:115–116`, `:129–132`) |

**Item 3 — `gitlab-management:137` and `:171–172` against `AGENTS.md:10, :18`**

| Option | What changes | Consequences |
|---|---|---|
| **3-A (Recommended)** | GL-1 (the orchestrator syncs back), GL-2 and GL-3 (`in_progress`, `in_review`) | 7 paths. The `status::` label names stay, so no GitLab project is affected. Removes the last spelling of `review`/`in-progress` as a ledger value that I found |
| **3-B** | Hold | A reader maps a label to a value the validator rejects (`C4`) |
| **3-C** | Rename the Status values in `AGENTS.md:10` to `in-progress`/`review` | A tier-1 change, no edit drafted. `validate-tasks.py`, every ledger row, `/new-project:56` and the checkpoints would follow. **Not recommended** |

**Item 4 — `dependency-graphing:26, :100, :134–140` against `AGENTS.md:14`**

| Option | What changes | Consequences |
|---|---|---|
| **4-A (Recommended)** | DG-0 to DG-3: read `Depends on` and derive `Blocks`; read `completed-tasks.md` for `done` nodes; rewrite the example table (the Mermaid output is unchanged) | 7 paths. Consistent with 2-A. DG-0 is a consequential edit beyond the brief's list: say "4-A without DG-0" to drop it |
| **4-B** | Hold | The skill cannot be followed on a real ledger |
| **4-C** | Add `Blocks`/`BlockedBy` columns to `AGENTS.md:14` | The same tier-1 change as 2-C. **Not recommended** |

**Item 5 — `checkpoint-protocol:101` against `AGENTS.md:15–16`** (the ledger "Completed Tasks" is read from)

| Option | What changes | Consequences |
|---|---|---|
| **5-A (Recommended)** | CP-1: query `completed-tasks.md` by `Done on` | Fixes a step that finds nothing today. Shares the file (and the 7 paths) with item 6 |
| **5-B** | Hold | The step keeps pointing at a ledger that never holds a `done` row |

**Item 6 — `checkpoint-protocol:59` against `AGENTS.md:28`** (Step A holds: jointly satisfiable)

| Option | What changes | Consequences |
|---|---|---|
| **6-A (Recommended)** | CP-2: the template's Author becomes `orchestrator` (a note-level edit) | No extra root path (same file as item 5). Closes the hazard that a subagent fills `<agent-name>` at a phase boundary. A later request for an agent-authored checkpoint would need a new edit |
| **6-B** | Hold; the ADR requires nothing here | The slot stays open. Both texts are still obeyable |

**Recommendation: 1-A, 2-A, 3-A, 4-A, 5-A, 6-A ("all recommended").** One mechanical implementation task, then one root refresh,
covers the five files (35 paths). Items 1, 3 and 5 are independent of each other; items 2 and 4 go together. Each recommendation
follows from ADR-008 Step B and from your 2026-10-09 decisions, not from any count of files that agree with `AGENTS.md`. Item 6 is
the one place where I would accept either answer, because the ADR does not require the edit.

## 7. Observations (new or restated; not ruled)

I rule none of these. They are for the orchestrator to park or schedule. O-1 to O-4 are the most likely to need a ruling.

| # | Site (source file) | Quote | Shape and my reading |
|---|---|---|---|
| **O-1** | `skills/blocker-escalation/SKILL.md:38, :52–57, :148, :165` | "- **Severity:** critical \| high \| medium \| low", the table of those four, and the examples `high` and `medium` | **A conflict in the same file, a different subject (the blocker severity value set).** `AGENTS.md:48` "- Severities: `critical` \| `major` \| `minor`". Step A fails (a closed set; one blocker has one severity) and Step B (P1) would fire: the skill sits inside `AGENTS.md` § Blocker Protocol. `systematic-debugging:91` and `frontend-developer:93` already use `major`. Two commands also use the longer scale: `team-status:66` ("CRITICAL/HIGH/MEDIUM" in the blocker table) and `validate-workflow:66` ("CRITICAL/HIGH/MEDIUM/LOW" for remediation items). The strongest further candidate, and it lives in a file this implementation already edits (no extra root path if bundled) |
| **O-2** | `commands/prepare-release.md:29` | "Create a release checkpoint: `docs/checkpoints/checkpoint-release-v<version>.md`" | A command names a checkpoint file with no `<SEQ>`. `AGENTS.md:27` is `checkpoint-<SEQ>-<phase>.md`. ADR-007 branch 1 (P1 for commands). It is the same defect as T613 K. It is also a command in the golden suite's scope (`tests/golden/README.md`), so a case or a held-out case may pin the name: **not searched**. The command was unread by T613 (its §9 item 7) |
| **O-3** | `skills/release-workflow/SKILL.md:52–53` and `agents/orchestrator.md:146` | "no tasks for this release should be `in_progress` or `blocked`. - All planned tasks should be `done` or archived." and "All task statuses in `docs/tasks/active-tasks.md` matching the release scope must be `done`" | Both presuppose `done` rows in `active-tasks.md`, which `AGENTS.md:15` forbids. Same family as item 5. `orchestrator.md:146` is a release-blocking condition that can never be tested as written. A tier-1 vs agent/skill defect (P1) |
| **O-4** | `skills/code-review/SKILL.md:130, :156`; `skills/testing-strategy/SKILL.md:228`; `skills/ci-cd-pipeline/SKILL.md:180` | "follow-up items logged to `docs/tasks/active-tasks.md`", "each should-fix item is logged as a task in `docs/tasks/active-tasks.md` with an assigned owner and target sprint", "failures logged as tasks in `docs/tasks/active-tasks.md`", "require tracked follow-up items in `docs/tasks/active-tasks.md`" | Passive voice, so Step A probably holds (the orchestrator can obey; `tech-lead:100` already says it adds the condition). `target sprint` is a field the ledger lacks (S2 shape). The same note as TM-1 would apply. 3 skills, 21 root paths |
| **O-5** | `agents/scrum-master.md:20` | "5. Assign tasks to appropriate team roles" | Restated from T613 O-8: read as a proposal inside a sprint plan, Step A holds |
| **O-6** | `skills/verification-before-completion/SKILL.md:32` | "- Before marking a task `done` in `docs/tasks/active-tasks.md`" | Consistent only if read as the same-edit archive. Applies to every agent although only the orchestrator transitions (Orchestrator Enforcement at `:89–92` covers it). Step A holds. Minor |
| **O-7** | `skills/task-management/SKILL.md:67` | "`T` + 3 or more digits. `T001`, `T042`, `T1001`. NEVER `T001`." | The rule contradicts its own examples (`T001` is both allowed and forbidden). Probably `T1` or `T01` was meant. A typo inside one file; same-file coherence |
| **O-8** | GitLab priority labels: `skills/gitlab-management/SKILL.md:47–50`, `:88`; `agents/scrum-master.md:32, :85` | `priority::critical/high/medium/low`; "## Priority: Must Have" | Fields of the GitLab issue, not of the ledger (Step A holds). The mapping to `P0`/`P1`/`P2` is stated only in `commands/bug-report.md:54` (critical to P0, high to P0, medium to P1, low to P2). Restates T613 O-3/O-7. There is also no `status::cancelled` label for the lifecycle's `cancelled` state |
| **O-9** | `skills/plan-approve-execute/SKILL.md:58–60, :122, :166–171` | "\| ID \| Title \| Assignee \| Priority \| BlockedBy \| Estimated Effort \|" and example rows with `high`, `medium`, `backend-dev`, `qa-agent`; "2. Create all tasks from the plan's Task Breakdown in `docs/tasks/active-tasks.md` (use `task-management` skill)." | The plan table is a different object from the ledger, so Step A holds, but nothing maps its `Assignee`, `Priority` values (`high`/`medium`) and `BlockedBy` to the ledger's `Owner`, `P0/P1/P2` and `Depends on`. `:122` names no actor (Phase 1 says "The orchestrator or lead agent"). If the plan is read as a ledger template, it repeats the item 2 defects |
| **O-10** | `skills/checkpoint-protocol/SKILL.md:71, :154` against `docs/checkpoints/_template.md:10, :14` | "\| ID \| Title \| Status \| Assignee \|" | The checkpoint tables are not the ledger. The skill says `Assignee`; the template says `Owner`; the ledger says `Owner`. Not a Task Protocol conflict (`AGENTS.md:29` lists required elements, not headings). Restates T613 O-6 |
| **O-11** | `docs/tasks/active-tasks.md:8–20` | A blockquote fragment starting "> record.** `plan-064` Phase 10 is done …" under the one-row table | Looks like leftover text from an older footnote. The validator reads only lines that start with `|`, so it passes. Not a knowledge file; for the orchestrator to tidy in a ledger MR |
| **O-12** | `skills/technical-debt-tracking/SKILL.md:95` | "- **Status:** open \| in-progress \| resolved \| accepted-risk" | A lookalike, not a hit: this is the **debt ledger**'s status, a different object from the task ledger. Recorded so that the next scan does not flag it |

**Read and found to conform (Task Protocol, this scan):** `scrum-master` (live `:23, :25, :27, :135`), `tech-lead` (`:100` has the
orchestrator add the condition), `release-manager`, `qa-engineer`, `frontend-developer`, `database-engineer`, `technical-writer`,
`ux-designer`, `technology-scout`, `context-retriever`, `poc-orchestrator`, `technical-debt-narrator`, `evaluation-agent`,
`poc-qa-engineer`, `poc-devops-engineer`, `poc-technical-writer` (each ends with "Report completion to the (PoC) orchestrator" and
writes no ledger row); skills `project-planning` (live `:209–217`), `technical-debt-tracking` (Rails `:12`, promotion `:110–133`),
`poc-evaluation` (Rails `:12`, `:141`), `rapid-prototyping` (Rails `:12`, `:125`), `validation-gates`, `receiving-code-review`,
`systematic-debugging`; commands `/new-feature` (live `:25`, `:30–31`), `/new-project`, `/new-poc`, `/plan`, `/batch`, `/bug-report`,
`/handoff`, `/team-status`, `/sprint-status`, `/validate-tasks`, `/validate-workflow` (each runs as `agent: "orchestrator"`, or as
`poc-orchestrator` for `/new-poc`, and writes the 7-column row where it writes one).

## 8. Handoff package for the implementing task (specification; no task is created here)

| Field | Content |
|---|---|
| `task_id` | To be assigned by the orchestrator (a mechanical-tier follow-up to `T615`) |
| `definition` | Apply, verbatim, only the fences the user approves in Q-T615 (§3), then regenerate and declare root drift |
| `constraints` | Never reword. Apply each pair by exact string replacement, matching each single-line Before as a whole line, and assert it matches exactly once; for the multi-line Befores (TM-2c, TM-3a, TM-3b, DG-3) match the whole block. Stop and report if an anchor is missing or not unique. Do not edit `AGENTS.md`, `implementation/AGENTS.md`, any instruction, any command, any agent, `project-planning`, `plan-approve-execute`, `docs/tasks/validate-tasks.py`, any file under `tests/golden/**`, `scripts/`, `.env*`, or any derived platform folder by hand. Do not refresh the repo root. Do not push, and never run any merge or approve call |
| `depends_on` | The user's answer to Q-T615 (items 2 and 4 in the same direction) |
| `input_artifacts` | `task-protocol-skill-conflicts-ruling-v1.md` (this file) as the single implementation input |
| `expected_outputs` | The edited files (up to 5); regenerated mirrors and `implementation/registry/index.json` (up to 5 entries); `tests/_baselines/root-install-drift.json` with exactly the printed paths (expected 35 if everything is applied); a report with every §4 count as lines and occurrences |
| `blocker_policy` | `AGENTS.md` § Blocker Protocol: report type and severity. A non-golden test that asserts a Before string, or a golden hit, is a `dependency` blocker to the orchestrator |

Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`,
`scripts/scorecard.py --check` (equal to the current baseline), `python3 docs/tasks/validate-tasks.py`, and `python3
tests/run.py` with output redirected to a file. Confirm byte-unchanged: `AGENTS.md`, every instruction, every command, every
agent, `project-planning`, `plan-approve-execute`, every script, and `tests/golden/**`.

## 9. Still unverified

1. The worktree commit `2f4b2c8` plus the scoping commit (stated by the orchestrator).
2. Every count in §4 and every "occurs once" claim in §3, all by reading, not `grep`. The `Depends on` After counts (rows 10 and 32)
   are the likeliest to be off by one.
3. The current text of the other six platform copies of `checkpoint-protocol`; the line numbers of every projection other than the ones
   named in §5.1; whether `implementation/.<platform>/` mirrors are tracked.
4. That no golden case (open or held-out), no test, and no page under `docs/wiki`, `docs/guides` or `README.md` asserts or restates a
   Before string. I ran no search and read no golden case.
5. That `implementation/registry/summary.md` and the maturity checks are unaffected, and the evaluator-hash baseline figure (v20).
6. That the scope text relied on in §2 was not edited in the change that first recorded these conflicts (I cannot diff history).
7. Files not read: agents `product-owner`, `solution-architect`, `backend-developer`, `devops-engineer`, `security-engineer`,
   `poc-security-engineer`, `scaffolding-agent`, `data-mockup-agent`, `demo-agent`, `feasibility-agent`, `integration-agent` (the
   first five were read by T613; the PoC specialists share the boilerplate of the ones I read); skills `api-design`, `cwso-awareness`,
   `skillify`, `technology-scouting`, `context-window-management`, `cost-token-governance`, `memory-management`, `worktree-isolation`
   (the last four were read by T613); commands `code-review`, `consolidate-memory`, `discover-skills`, `evaluate-poc`, `poc-demo`,
   `security-audit`, `skillify`; the instruction `coding-standards` (so "no other tier-1 text mentions `BlockedBy` or `Blocks`" is
   proven only for `AGENTS.md`, `security-guidelines`, `poc-guidelines` and `git-workflow` as quoted to me, plus the skills above).
8. The user's decisions of 2026-10-09 are quoted as the orchestrator relayed them, not re-read from the user's own message.

## 10. Summary

| Item | Subject | Settled by | Outcome | Edits | User decision? |
|---|---|---|---|---|---|
| 1 | Who sets `blocked` | ADR-008 Step B (P1); `:122` Step A | Amend `blocker-escalation`: report, the orchestrator writes | BE-1, BE-2 | Approval only |
| 2 | Actor, dependency fields, examples, archive timing | Step A note (2a); Step B (P1) with same-file coherence (2b, 2c, 2d); T613 S2 | Amend `task-management` to `Depends on` and the seven columns | TM-1 to TM-4 | Approval; 2-C is the tier-1 alternative |
| 3 | Sync-back actor, mapped Status values | Step A note (3a); Step B (P1) (3b) | Amend `gitlab-management`: `in_progress`, `in_review`, orchestrator syncs | GL-1 to GL-3 | Approval only |
| 4 | Columns the graph reads | Step B (P1); T613 S2 | Amend `dependency-graphing`: `Depends on`, `Blocks` derived | DG-0 to DG-3 | Approval; 4-C is the tier-1 alternative |
| 5 | Ledger for "Completed Tasks" | Step B (P1) | Amend `checkpoint-protocol:101` | CP-1 | Approval only |
| 6 | Checkpoint author | Step A (holds) | Confirmed jointly satisfiable; optional note | CP-2 | Approval, either answer acceptable |

- **Maturity, corpus counts, majority practice and golden-coupling convenience** were relied on nowhere as authority. The agreement of
  other files with `AGENTS.md` appears only as a consequence in §6.
- **The `BlockedBy`/`Blocks` question is not a P5 escalation:** one tier-1 sentence, a recorded user decision (T613 S2) and the skill's own
  table all point to seven columns. Extending the schema stays the user's option (2-C, 4-C).
- **No edit is applied, and none is upward or relaxing.** No tier-1 file, command, agent or golden path is touched.
- **Golden:** no fixture and no result changes under any option, so far as I can tell. No grant and no baseline are needed. Whether a
  case pins a Before string is unverified (§5.2).
- **Blockers:** none for this task. The unverified items in §9 (golden and non-golden test coupling) are `dependency` checks for the
  implementing task, severity `minor`.
