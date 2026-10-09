# Artifact: task-protocol-and-checkpoint-name-ruling-v1.md

> Filename: `task-protocol-and-checkpoint-name-ruling-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T613 (P2, judgment tier, decision only)
- **Created**: 2026-10-09
- **Based on:**
  - `docs/tasks/task-T613.md` (the brief, authoritative);
  - `docs/plans/plan-117-scrum-master-and-checkpoint-name-rulings.md`;
  - `docs/plans/plan-112-parked-note-cleanup.md` §2 (the "`scrum-master` task protocol (P41 O2)" row);
  - `docs/artifacts/remaining-verdict-renderings-v1.md` §8.4 (O2) and §7.6 (E-G7a, E-G7b, the in-corpus model of the
    Task Protocol amendment);
  - `docs/artifacts/naming-conflicts-ruling-v1.md` §2.3 (the O5 model), §8 (O7), §3.3 (N-3);
  - `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted) and
    `docs/decisions/ADR-007-command-contract-authority.md` (Accepted);
  - `AGENTS.md` § Task Protocol and § Checkpoint Protocol (root copy `:13–19`, `:26–30`; `implementation/AGENTS.md` carries
    the same lines);
  - the user's decisions of 2026-10-09 on the same class of conflict, as the orchestrator relayed them: **"Apply both"**
    for T607 O2+O5 (`/new-feature`: the Scrum Master proposes the tasks and estimates, the orchestrator creates them, per
    `AGENTS.md` § Task Protocol) and **"Amend coding-standards (Recommended)"** for O1 (`AGENTS.md` names win over
    `coding-standards`). I honor both as precedent and do not re-litigate them.
- **Supersedes**: none (first version).
- **Decision references**: ADR-008 Step A (P3a), Step B (P1), D2, D4, D5, P4; ADR-007 §5 (never relax a check). No new ADR
  is minted.
- **Status of every edit in this document**: **held for the user. Nothing is applied.** The only other file changed by this
  task is the `**Status:**` line of `task-T613.md`.

## 0. Method and limits

- **Commit.** The orchestrator states the worktree is on `develop` `c5aa8e4` plus one scoping commit **(unverified: no
  shell, no `git`)**. Every line number below was read in the worktree. Earlier artifacts' line numbers were not trusted;
  each clause was re-read (§2).
- **No shell, no grep, no directory listing.** Every count in §4 comes from reading whole files and is **(unverified by
  grep)**. §5.4 lists the greps the implementing task must run first. §9 collects every unverified claim.
- **Read in full:** `scrum-master.md`; `checkpoint-protocol/SKILL.md`; `AGENTS.md:1–60` and `implementation/AGENTS.md:1–40`;
  `ADR-007`, `ADR-008`; `naming-conflicts-ruling-v1.md`; `remaining-verdict-renderings-v1.md:1–60, 330–529`; plan-112,
  plan-117; agents `orchestrator`, `product-owner`, `release-manager`, `backend-developer`, `tech-lead`, `qa-engineer`,
  `security-engineer`, `devops-engineer`, `solution-architect`; skills `task-management`, `project-planning`,
  `gitlab-management`, `blocker-escalation`, `dependency-graphing`, `release-workflow`, `verification-before-completion`,
  `context-window-management`, `cost-token-governance`, `memory-management`, `worktree-isolation`; commands `new-feature`,
  `new-project`, `plan`, `batch`, `bug-report`, `handoff`, `team-status`, `sprint-status`; `docs/checkpoints/_template.md`;
  `tests/_baselines/root-install-drift.json`; `tests/golden/README.md`; `implementation/registry/summary.md`. Platform
  projections: first lines of all 6 `scrum-master` agent files and all 7 `checkpoint-protocol` skill files, and the edited
  regions of the `.claude` copies.
- **Golden.** Under `tests/golden/open/` only, I read the `brief.md` of `new-feature-checkpoint-line-compliant`,
  `new-feature-real-checkpoint-format-drift` and `new-project-plan-doc-and-lifecycle-states`. Each case name in this
  document has a `tests/golden/open/` directory. **I never opened `tests/golden/held-out/`**, so I cannot say whether a
  held-out case pins any clause below.
- **Secrets.** I read no `.env*`, credential or key file. I edited nothing under `.claude/`, `.github/` or any other derived
  platform folder, and nothing outside this artifact and the brief's `**Status:**` line.
- **Encoding.** `§` is U+00A7, `—` is U+2014 (it appears in headings and in quoted source text; no held edit introduces one). Each four-backtick fence
  holds one Before/After pair; inner single backticks are literal. Apply each edit by its Before text, never by line
  number. No Before text starts with whitespace. Match each Before as a **whole line** (`grep -cxF`), because `# Checkpoint
  <N>` is also a prefix of another line.
- **Scope-gaming guard (ADR-008 § Risks).** Both conflicts were first recorded before this task: P41 O2 in
  `remaining-verdict-renderings-v1.md` §8.4 (which cites `scrum-master:25` and `:27`), and O7 in
  `naming-conflicts-ruling-v1.md` §8 (which cites `checkpoint-protocol:104, :173, :179`). Those are the lines where I read
  them now, so I saw no shift since (**unverified**: I cannot diff history). No declared-scope sentence relied on below was
  added in the same change as this ruling.
- **Maturity.** I relied on no `maturity:` value anywhere in this document (P4). `scrum-master` and `checkpoint-protocol`
  are `stable`; `orchestrator` is `experimental`; `task-management`, `project-planning`, `blocker-escalation` and
  `gitlab-management` are `experimental`. None of that decides any step below. `AGENTS.md` is tier 1 by ADR-008 D1 and
  `coding-standards` is a stable instruction by D1; neither point is needed for the rulings below, because neither
  conflict is inside tier 1.

## 1. Summary of the rulings

| Item | Subject (D3) | Both sides | Step that fired | Outcome | Edit |
|---|---|---|---|---|---|
| **S1** | Who writes (creates, transitions) the rows of `active-tasks.md` | `scrum-master:23, :25, :135` against `AGENTS.md:18` | A fails, **B (P1)** | **Amend the agent**: the Scrum Master proposes, the orchestrator writes | S-1, S-2, S-4 held |
| **S2** | Which fields a task entry carries | `scrum-master:27` against `AGENTS.md:14` | A fails, **B (P1)** | **Amend the agent**: the ledger's own seven columns; points and sprint go to the brief and the GitLab issue | S-3 held |
| **K** | The file name of a checkpoint | `checkpoint-protocol:104, :173, :179` (and `:56, :99, :117`) against `AGENTS.md:27` | A fails, **B (P1)** | **Amend the skill** toward `AGENTS.md:27` and its own `:44` | C-1 to C-5 held |

**Where the ADR decides and where it does not.** All three items are decided by ADR-008 Step B. The other document in each
pair is an agent or a skill, so **no conflict is inside tier 1** and nothing is escalated under P5. The user question in §6
is therefore "approve the ruled edit, hold it, or change the tier-1 text instead", exactly as for T607 O2 and O5.

**One departure from an earlier artifact, disclosed.** `naming-conflicts-ruling-v1.md` §8 O7 recorded the third checkpoint
name only as a same-file defect ("outside ADR-008, § Scope"). I rule it on the cross-document ground as well. The skill's
`:104` also contradicts `AGENTS.md:27` directly, which is the brief's own framing ("against its own `:44` and `AGENTS.md`").
The two grounds lead to the same edit, so the departure changes no outcome.

## 2. D5 records

### 2.1 S1 — who writes the rows of `active-tasks.md`

**Verbatim clauses (live, in the worktree).**

Tier 1, `AGENTS.md` (identical in `implementation/AGENTS.md`):
- `:4` "- Two orchestration tracks: Production (`@orchestrator`) and PoC (`@poc-orchestrator`)"
- `:5` "- Only orchestrators are user-invocable. All other agents are subagents."
- `:14` "- Task list: `docs/tasks/active-tasks.md` — columns: `ID | Title | Owner | Status | Priority | Depends on | Last update`"
- `:18` "- Only orchestrators create/transition tasks. Agents report completion and blockers."

Scrum Master, `implementation/knowledge/agents/scrum-master.md`:
- `:5` `user-invocable: false`
- `:3` (description) "Use when planning sprints, tracking progress, managing milestones, facilitating agile ceremonies, breaking down
  epics into tasks, creating GitLab issues and milestones, or resolving team impediments."
- `:23` "1. Read and update `docs/tasks/active-tasks.md` as the canonical task board"
- `:24` "2. Synchronize task entries with GitLab issues — create GitLab issues from new task entries"
- `:25` "3. Update task status in `active-tasks.md` when GitLab issue status changes"
- `:26` "4. Report task completion to the orchestrator. NEVER move rows between ledgers — archival is orchestrator-only and
  happens immediately on completion, not at sprint close"
- `:116` (Rails, Inputs) "The product backlog from Product Owner and the current `docs/tasks/active-tasks.md` state."
- `:126` "- ONLY manage process, planning, and tracking"
- `:135` (Output Format, item 5) "5. Updated `docs/tasks/active-tasks.md` reflecting current sprint state"
- `.claude/agents/scrum-master.md` carries the same text two lines lower (`:21, :23, :25, :133`).

The other side's own words (D2 source 4, reach shown from either side):
- `agents/orchestrator.md:5` (`agents:` roster) lists `scrum-master`; `:33` "1. Create task entries in
  `docs/tasks/active-tasks.md`"; `:34` "2. Create detailed task briefs in `docs/tasks/task-<ID>.md`"; `:70` "- Update task
  status after receiving agent completion report"; `:240` "4. Delegate to **@scrum-master** for sprint plan and GitLab issue
  breakdown".

**Subject (D3).** The actor that writes (creates or transitions) the rows of `docs/tasks/active-tasks.md`. Creating a GitLab
issue (`:24`) is a different act on a different object, and is not part of this subject (Step A, below).

| Field | Content |
|---|---|
| **Step A** | **Fails on the literal text.** MUSTs: `scrum-master:25` is an imperative to the Scrum Master to change a ledger row's Status. `AGENTS.md:18` is **exclusive** ("**Only** orchestrators"), and the Scrum Master is not an orchestrator (`AGENTS.md:5` "All other agents are subagents"; `scrum-master:5` `user-invocable: false`). A status change is a transition of the lifecycle in `AGENTS.md:8–11`. **One-value test:** one status transition has one writer. `:25` names the Scrum Master and `:18` names only orchestrators. `:23` ("Read and update … as the canonical task board") and `:135` (the agent's returned output is the "Updated" ledger) say the same. **Rescue reading (ii), recorded:** read "update" as "prepare the update for the orchestrator to apply". Then `:25` and `:18` are jointly satisfiable and Step A holds. I rule on reading (i), the face value, for the same reason `naming-conflicts-ruling-v1.md` §2.3 did: the verb is used for the ledger act everywhere else in the repository, and a subagent reads the clause at face value. **The conclusion does not depend on it.** Under (ii) ADR-008 Step A permits "at most a note stating the relationship where readers will see it", and the held edit is that note. **Corroboration, not authority** (D2: scope is not inferred from tools): the `tools:` list at `:4` and the Claude projection (`Read, TodoWrite, WebFetch, WebSearch, mcp__gitlab`) carry no edit tool, so under reading (i) the agent could not perform the act. |
| **Narrow readings that hold (Step A)** | `:24` "create GitLab issues from new task entries" creates GitLab issues, not tasks, and both clauses can be obeyed. `:17` "Break epics into implementable user stories and tasks" and `:20` "Assign tasks to appropriate team roles" are planning acts that produce a proposal. `:26` is already compliant. None of these is edited. |
| **Step B (P1)** | **Fires.** (a) *Quotable:* `AGENTS.md:18` and `scrum-master:25` are quoted above. (b) *Reach:* `AGENTS.md` declares no scope narrower than the repository (D2), and § Task Protocol is "not scoped to a track, an agent or a file type" (`poc-skills-alignment-v1.md` §1.3, relied on by `naming-conflicts-ruling-v1.md` §2.3). The Scrum Master also places itself inside it in its own words: `:26` "archival is orchestrator-only", `:116` takes `active-tasks.md` as an input, and `orchestrator.md:33–34, :70, :240` assign the row-writing and the delegation to the orchestrator. (c) Step A fails on reading (i). (d) The other document is an agent. |
| **Step fired** | **B (P1)**, with the Step A note as the fallback. |
| **Amendment** | **Amend the agent**, not `AGENTS.md` (P1 Remedy). Edits S-1, S-2, S-4 (§3.1). They cite `AGENTS.md` § Task Protocol and do not restate its rules at length. The Scrum Master keeps every planning, estimation and GitLab duty. |
| **Precedent** | `naming-conflicts-ruling-v1.md` §2.3 (T607 O5, user decision "Apply both"): "the Scrum Master **proposes** tasks and estimates effort, and the orchestrator **creates** them". `remaining-verdict-renderings-v1.md` §7.6 E-G7a and E-G7b (already live at `project-planning/SKILL.md:209–217`): "An agent other than an orchestrator that applies this skill proposes the tasks to the orchestrator and does not write the ledger." This ruling extends the same model to the Scrum Master's own file. |
| **Maturity** | Not relied on. |

### 2.2 S2 — which fields a task entry carries

**Verbatim clauses (live).**
- `scrum-master:27` "5. Ensure every task entry includes: ID, title, assignee, status, story points, sprint, and dependencies"
- Context in the same file: `:18` "3. Estimate effort using story points (Fibonacci: 1, 2, 3, 5, 8, 13)"; `:34` "- **Estimate**: Include story point
  estimate in description" (a GitLab issue field); `:84–87` the Issue Template carries `## Story Points: [X]`, `## Priority:
  [High/Medium/Low]`, `## Sprint: [Sprint N]`, `## Dependencies:`.
- `AGENTS.md:14` "- Task list: `docs/tasks/active-tasks.md` — columns: `ID | Title | Owner | Status | Priority | Depends on | Last update`";
  `AGENTS.md:17` "- Task briefs: `docs/tasks/task-<ID>.md` (objective, inputs, outputs, acceptance criteria)"; `AGENTS.md:19` "…
  Priorities: `P0` (critical path), `P1`, `P2`."
- In-corpus model, already live: `project-planning/SKILL.md:209–211` (a row with the seven columns "which the orchestrator
  sets"; the brief "also records the task's sprint, points and artifact references, for which the row has no column").

**Subject (D3).** The set of fields a task entry in the ledger carries.

| Field | Content |
|---|---|
| **Step A** | **Fails on the literal text.** `:27` requires every entry in the ledger context of `:23`–`:25` to include story points and sprint. `AGENTS.md:14` lists the ledger's columns, and neither is among them; `Priority` and `Last update` are columns that `:27` does not list. A closed list of columns cannot carry two extra fields without adding columns, so one row cannot satisfy both. The renames are only labels: `assignee` for `Owner`, `dependencies` for `Depends on`, and `status`, `title` and `ID` match. **Rescue reading (ii), recorded:** "task entry" means the row together with its brief and GitLab issue. Then `:27` holds, because points and sprint live in the brief and the issue. That is the reading `project-planning:211` already takes. I rule on the literal reading (i) because `:27` sits between `:23` and `:25`, which are about the board file. **The conclusion does not depend on it**, for the reason given in S1. |
| **Step B (P1)** | **Fires.** (a) Quotable. (b) `AGENTS.md:14` is the ledger's schema; D2 reach is the same as S1. (c) Step A fails on reading (i). (d) An agent. |
| **Step fired** | **B (P1).** |
| **Amendment** | **Amend the agent.** Edit S-3 (§3.1). Story points and sprint stay where the Scrum Master already puts them (`:34`, `:84–86`: the GitLab issue) and are also supplied for the task brief, as `project-planning:211` says. The velocity log (`:55–65`) is a separate artifact and is untouched. |
| **Not decided here** | The GitLab issue's `Priority: [High/Medium/Low]` (`:85`, `:32` `priority::high/medium/low`) against the ledger's `P0/P1/P2`. They are fields of two different objects, so Step A holds. The mapping between them is stated nowhere (observation O-3). |
| **Maturity** | Not relied on. |

### 2.3 K — the file name of a checkpoint (the third name)

**Verbatim clauses (live).**

Tier 1, `AGENTS.md:27` "- Checkpoints: `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`"; `:28` "- Written at every phase boundary
by the orchestrator."

`implementation/knowledge/skills/checkpoint-protocol/SKILL.md` (the `.claude` copy is one line lower throughout):
- `:44` `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`
- `:47–49` "Where `<SEQ>` is a sequential integer (zero-padded, e.g. `001`, `029`) and `<phase>` is a short, kebab-case
  description of the phase or event the checkpoint covers (e.g. `checkpoint-029-phase3-t433-gate-g2-closed.md`)."
- `:50–51` "This matches `AGENTS.md`'s Checkpoint Protocol section verbatim — see that section for the canonical filename
  convention this skill implements."
- `:56` `# Checkpoint <N>` (first line of the Checkpoint Format fence)
- `:99` "1. Determine the next checkpoint number by listing `docs/checkpoints/` and incrementing the highest `<N>`."
- `:104` "6. Write the file to `docs/checkpoints/checkpoint-<N>.md`."
- `:117` `# Checkpoint <N> (Compressed)`
- `:173` "- Write `checkpoint-001.md` covering all Phase 0 work."
- `:179` "- Write `checkpoint-003.md` covering those task completions."

Models that already take the cite-`AGENTS.md` form: `skills/memory-management/SKILL.md:155` "Write `checkpoint-001-<phase>.md`
as the initial state snapshot (`AGENTS.md` § Checkpoint Protocol: `checkpoint-<SEQ>-<phase>.md`)"; `agents/orchestrator.md:150`;
`commands/new-feature.md:30–31`; `commands/new-project.md:43`. `docs/checkpoints/_template.md:3` agrees with `AGENTS.md`.

**Subject (D3).** The file name of a checkpoint.

| Field | Content |
|---|---|
| **Step A** | **Fails.** MUSTs: `AGENTS.md:27` fixes the path of a checkpoint as `checkpoint-<SEQ>-<phase>.md`; `skill:104` fixes it as `checkpoint-<N>.md`, and `:173`, `:179` print literal names with no `<phase>`. **Exclusivity:** both fix the whole file name of one artifact, a closed pairing for that field. **One-value test:** for the 29th checkpoint, `AGENTS.md:27` computes `checkpoint-029-<phase>.md` and `:104` computes `checkpoint-029.md`. They differ. **Same-file:** `:44` and `:104` give two names for one file in one skill, so the skill also contradicts itself. **Rejected rescue reading:** let `<N>` absorb `<SEQ>-<phase>`. It cannot produce the literal examples `checkpoint-001.md` and `checkpoint-003.md` (`:173`, `:179`), which have no phase part. |
| **Step B (P1)** | **Fires.** (a) *Quotable:* `AGENTS.md:27` and `skill:104` are quoted above. (b) *Reach:* `AGENTS.md:27` names checkpoints, and the skill places itself under it in its own words: `:50–51` "see that section for the canonical filename convention this skill implements", and `:44` repeats the `AGENTS.md` form. (c) Step A fails. (d) The other document is a skill. |
| **Step fired** | **B (P1).** The same-file defect is a second ground for the same edit (ADR-008 § Scope: "resolved by same-file coherence"), so the choice of ground changes nothing. |
| **Amendment** | **Amend the skill** toward `AGENTS.md:27` and its own `:44`. Edits C-1 to C-5 (§3.2). C-2 cites `AGENTS.md` instead of restating it (P1 Remedy, T542 model). C-1 and C-3 are **consequential**: once `:104` uses `<SEQ>`, the `<N>` of `:56`, `:99` and `:117` would be an undefined placeholder. C-4 and C-5 give the two examples a `<phase>` part. |
| **Not changed** | `:44`, `:47–51` are correct and untouched. The `[CHECKPOINT]` one-line marker is a different object, and the skill does not use it. |
| **Maturity** | Not relied on. |

## 3. Held edits (apply verbatim, only after the user decides)

Each Before is unique in its file by reading the whole file **(unverified by grep)**. No edit relaxes a check (ADR-007 §5).
None is upward: each moves an agent or a skill toward `AGENTS.md`. None touches a command, a tier-1 file or a golden path.

### 3.1 S1 and S2 (options S1-A and S2-A): `implementation/knowledge/agents/scrum-master.md`

**S-1 — `:23`.** Anchor: the full line, which occurs once.

````
Before:
1. Read and update `docs/tasks/active-tasks.md` as the canonical task board

After:
1. Read `docs/tasks/active-tasks.md` as the canonical task board. Do not write it: "Only orchestrators create/transition tasks" (`AGENTS.md` § Task Protocol), so propose each new task and each status change to the orchestrator, who writes the row
````

**S-2 — `:25`.** Anchor: the full line, which occurs once.

````
Before:
3. Update task status in `active-tasks.md` when GitLab issue status changes

After:
3. When a GitLab issue's status changes, report it to the orchestrator, who transitions the task's Status in `active-tasks.md` (`AGENTS.md` § Task Protocol)
````

**S-3 — `:27`** (option S2-A). Anchor: the full line, which occurs once.

````
Before:
5. Ensure every task entry includes: ID, title, assignee, status, story points, sprint, and dependencies

After:
5. Propose each task entry in the ledger's own columns, `ID | Title | Owner | Status | Priority | Depends on | Last update`, with a Priority of `P0`, `P1` or `P2` (`AGENTS.md` § Task Protocol); the orchestrator writes the row. The ledger has no column for story points or sprint, so record them in the GitLab issue and supply them for the task brief
````

**S-4 — `:135`.** Anchor: the full line, which occurs once.

````
Before:
5. Updated `docs/tasks/active-tasks.md` reflecting current sprint state

After:
5. Proposed `docs/tasks/active-tasks.md` rows and status changes reflecting current sprint state, for the orchestrator to write (`AGENTS.md` § Task Protocol)
````

### 3.2 K (option K-A): `implementation/knowledge/skills/checkpoint-protocol/SKILL.md`

**C-1 — `:99`.** Anchor: the full line, which occurs once.

````
Before:
1. Determine the next checkpoint number by listing `docs/checkpoints/` and incrementing the highest `<N>`.

After:
1. Determine the next checkpoint sequence number by listing `docs/checkpoints/` and incrementing the highest `<SEQ>`.
````

**C-2 — `:104`.** Anchor: the full line, which occurs once.

````
Before:
6. Write the file to `docs/checkpoints/checkpoint-<N>.md`.

After:
6. Write the file to the path in § File Location, `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`, per `AGENTS.md` § Checkpoint Protocol.
````

**C-3 — `:56` and `:117`** (consequential; two applications). Anchor each as a **whole line**: `:56` is exactly `# Checkpoint <N>`
(inside the Checkpoint Format fence) and `:117` is exactly `# Checkpoint <N> (Compressed)` (inside the Compressed format fence).
A substring match on the first would also hit the second.

````
Before:
# Checkpoint <N>

After:
# Checkpoint <SEQ>
````

````
Before:
# Checkpoint <N> (Compressed)

After:
# Checkpoint <SEQ> (Compressed)
````

**C-4 — `:173`.** Anchor: the full line, which occurs once.

````
Before:
- Write `checkpoint-001.md` covering all Phase 0 work.

After:
- Write `checkpoint-001-phase0-foundation.md` covering all Phase 0 work.
````

**C-5 — `:179`.** Anchor: the full line, which occurs once.

````
Before:
- Write `checkpoint-003.md` covering those task completions.

After:
- Write `checkpoint-003-phase1-t005-t007.md` covering those task completions.
````

**Totals.** There are 10 fences and 10 applications: S-1, S-2, S-3, S-4, C-1, C-2, C-3 (one fence for `:56`, one for `:117`),
C-4 and C-5. They touch 2 files. Subsets: S1-A alone is S-1, S-2, S-4; S2-A alone is S-3; K-A alone is C-1 to C-5.

## 4. Hit counts

- **Scope:** case-sensitive, fixed-string, per file, after every held edit to that file. "Lines" = `grep -cF`; "occurrences"
  = `grep -oF … | wc -l`. "Whole line" = `grep -cxF`.
- **Before** counts are by reading whole files **(unverified by grep)**. A "0 / 0" in the After column means the old wording
  must be gone.
- Every projection of a file carries the same counts as its source, apart from the dropped frontmatter lines (§5.1).

### 4.1 `agents/scrum-master.md`

| # | Phrase | Before (lines / occ.) | After | Edit |
|---|---|---|---|---|
| 1 | `Read and update` | 1 / 1 (`:23`) | **0 / 0** | S-1 |
| 2 | `Update task status in` | 1 / 1 (`:25`) | **0 / 0** | S-2 |
| 3 | `Ensure every task entry includes` | 1 / 1 (`:27`) | **0 / 0** | S-3 |
| 4 | `assignee` | 1 / 1 (`:27`) | **0 / 0** | S-3 |
| 5 | whole line `5. Updated \`docs/tasks/active-tasks.md\` reflecting current sprint state` | 1 (`:135`) | **0** | S-4 |
| 6 | `AGENTS.md` | 0 / 0 | **4 / 4** (`:23`, `:25`, `:27`, `:135`) | S-1 to S-4 |
| 7 | `§ Task Protocol` | 0 / 0 | **4 / 4** | S-1 to S-4 |
| 8 | `Only orchestrators create/transition tasks` | 0 / 0 | 1 / 1 | S-1 |
| 9 | ``ID \| Title \| Owner \| Status \| Priority \| Depends on \| Last update`` | 0 / 0 | 1 / 1 | S-3 |
| 10 | `docs/tasks/active-tasks.md` (with the `docs/tasks/` prefix) | 2 / 2 (`:23`, `:135`) | 2 / 2 | S-1, S-4 keep it |
| 11 | `active-tasks.md` | 4 / 4 (`:23`, `:25`, `:116`, `:135`) | 4 / 4 | unchanged |
| 12 | `story points` | 3 / 3 (`:18`, `:27`, `:55`) | 3 / 3 | S-3 keeps one |
| 13 | `NEVER move rows` | 1 / 1 (`:26`) | 1 / 1 | untouched |

Row 9's phrase contains `|`, escaped as `\|` in this table only; its literal text is the column list quoted in S-3. Row 5's
phrase is the whole line, with its backticks.

### 4.2 `skills/checkpoint-protocol/SKILL.md`

| # | Phrase | Before (lines / occ.) | After | Edit |
|---|---|---|---|---|
| 14 | `checkpoint-<N>` | 1 / 1 (`:104`) | **0 / 0** | C-2 |
| 15 | `checkpoint-001.md` | 1 / 1 (`:173`) | **0 / 0** | C-4 |
| 16 | `checkpoint-003.md` | 1 / 1 (`:179`) | **0 / 0** | C-5 |
| 17 | `<N>` | 4 / 4 (`:56`, `:99`, `:104`, `:117`) | **0 / 0** | C-1, C-2, C-3 |
| 18 | `<SEQ>` | 2 / 2 (`:44`, `:47`) | 6 / 6 (`:44`, `:47`, `:56`, `:99`, `:104`, `:117`) | C-1, C-2, C-3 |
| 19 | `checkpoint-<SEQ>-<phase>.md` | 1 / 1 (`:44`) | 2 / 2 (`:44`, `:104`) | C-2 |
| 20 | `AGENTS.md` | 2 / 2 (`:50`, `:140`) | 3 / 3 | C-2 |
| 21 | `§ Checkpoint Protocol` | 0 / 0 | 1 / 1 (`:104`) | C-2 |
| 22 | `§ File Location` | 0 / 0 | 1 / 1 (`:104`) | C-2 |
| 23 | `checkpoint-001-phase0-foundation.md` | 0 / 0 | 1 / 1 | C-4 |
| 24 | `checkpoint-003-phase1-t005-t007.md` | 0 / 0 | 1 / 1 | C-5 |
| 25 | whole line `# Checkpoint <N>` | 1 | **0** | C-3 |
| 26 | whole line `# Checkpoint <SEQ>` | 0 | 1 | C-3 |

Row 25 and 26 are whole-line counts. Row 17 includes the two heading lines (`:56`, `:117`) and `:99`, `:104`.

### 4.3 Other sites that repeat a conflicting clause (no edit proposed here)

| Site | Repeats | Why left alone |
|---|---|---|
| `.claude/`, `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/` copies of `scrum-master` (6) and `.claude/`, `.github/`, `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.cline/` copies of `checkpoint-protocol` (7); mirrors under `implementation/.<platform>/` (the `.claude` mirror exists) | The same four Scrum Master lines and the same five checkpoint lines | Derived. Regenerated by `sync.mjs` and the root refresh (§5.1) |
| `docs/artifacts/remaining-verdict-renderings-v1.md` §8.4 O2, `naming-conflicts-ruling-v1.md` §4, §8 | Quote the old clauses | Immutable artifacts (`AGENTS.md:24`) |
| `docs/plans/plan-112-parked-note-cleanup.md` §2 | The parked row | Immutable plan text; the ledger and the next plan record the outcome |
| `docs/wiki/**`, `docs/guides/**`, `README.md` | Unknown whether any page restates `scrum-master` task-board duties or the `checkpoint-<N>` name | **(unverified)**; covered by the §5.4 greps |
| Other agents and skills in the corpus that name `checkpoint-<N>` or `checkpoint-001.md` | None found in the files I read (§0) | The unread files are listed in §9 |

## 5. Effects

### 5.1 Projected paths and root drift

An agent projects to 6 root paths, a skill to 7. I read the first lines of every one of them, so these counts are checked,
not inferred.

| Source edit | Root-projection paths | Paths |
|---|---|---|
| `agents/scrum-master.md` (S-1 to S-4) | **6** | `.claude/agents/scrum-master.md`, `.github/agents/scrum-master.agent.md`, `.cursor/agents/scrum-master.mdc`, `.gemini/agents/scrum-master.md`, `.opencode/agents/scrum-master.md`, `.pi/agents/scrum-master.md` |
| `skills/checkpoint-protocol/SKILL.md` (C-1 to C-5) | **7** | `.github/skills/checkpoint-protocol/SKILL.md`, `.cursor/skills/…`, `.gemini/skills/…`, `.opencode/skills/…`, `.pi/skills/…`, `.claude/skills/…`, `.cline/skills/…` (same file name under each) |
| **Total if everything is applied** | **13** | |

- **Subsets.** S1-A or S2-A alone: 6. K-A alone: 7. Any subset adds the matching rows only (S1-A and S2-A share one file).
- **Projection line shifts.** `.claude/agents/scrum-master.md` drops `user-invocable` and `maturity`, so it is two lines lower
  (`:21, :23, :25, :133`). `.claude/skills/checkpoint-protocol/SKILL.md` drops `maturity`, so it is one line lower. The other
  platforms' line numbers are **(unverified)**.
- **Regenerate:** `node implementation/scripts/sync.mjs --root implementation`, then `python3
  implementation/scripts/generate-registry.py`, each followed by `--check`. `implementation/registry/index.json` changes for
  the 2 entries (checksums). `implementation/registry/summary.md` should not change, since no `maturity:` changes
  **(unverified)**.
- **Mirrors.** `sync.mjs` also writes the same files under `implementation/.<platform>/` (I confirmed the `.claude` skill
  mirror exists). Whether the mirrors are tracked is **(unverified)**. They are not root drift.
- **Root drift.** `tests/_baselines/root-install-drift.json` now reads `"drift": []` (emptied by the thirteenth refresh). The
  implementing task declares exactly the paths `python3 -m tests.functional.test_root_install_parity --print-drift` prints
  (expected 13). It does not refresh the repo root; that is a separate, user-approved `--projections-only` refresh.

### 5.2 Golden and test coupling

| Item | Coupling | Effect |
|---|---|---|
| `new-feature-checkpoint-line-compliant` | Its brief quotes `/new-feature` step 7 and asserts `checkpoint-<SEQ>-<phase>.md` with a numeric `<SEQ>` | **Agrees with K-A.** It does not quote the skill. No change |
| `new-feature-real-checkpoint-format-drift` | Same contract, applied to a real checkpoint, `docs/checkpoints/checkpoint-017-t417-harbor-oracle-smoke-complete.md`, which follows the `<SEQ>-<phase>` form | **Agrees with K-A.** No change |
| `new-project-plan-doc-and-lifecycle-states` | Quotes `/new-project` steps 1 and 19 and reads the ledger's status column | None. It does not quote `scrum-master` or the checkpoint skill |
| Any open case quoting `scrum-master` or `checkpoint-protocol` | None found in the three briefs I read | **(unverified)** beyond them |
| **Held-out cases** | I did not open `tests/golden/held-out/` | **Unknown.** The orchestrator, under its read/audit exception, should grep that tree for `Update task status in`, `Ensure every task entry includes`, `checkpoint-<N>` and `checkpoint-001.md` before the implementing task is dispatched |
| Non-golden tests | I could not search `tests/` | **Unknown whether any test asserts a Before string.** `test_root_install_parity` is the one known coupling (§5.1). §5.4 lists the greps |

### 5.3 Baseline and grant

- **Protected-path grant:** **none needed.** No edit touches `tests/golden/**` or `scripts/scorecard.py`.
- **Evaluator-hash baseline:** **none needed.** `scripts/scorecard.py --check` stays at the current baseline (v20 per the
  orchestrator's notes **(unverified)**). The implementing task reads the current figures from the repo, not from this
  document.
- **Checks that should be unaffected (unverified):** `check-maturity.py --root implementation` (0 failing) and `python3
  docs/tasks/validate-tasks.py` (neither reads these strings).

### 5.4 Pre-flight greps for the implementing task (not run here; I have no shell)

Run and report, then stop if a non-golden test asserts a Before string. Report held-out hits to the orchestrator only,
without naming a case.

- `grep -rnF -e 'checkpoint-<N>' -e 'checkpoint-001.md' -e 'checkpoint-003.md' implementation/ docs/wiki docs/guides README.md tests/ --include='*.md' --include='*.py' --include='*.mjs' --include='*.json' --include='*.yaml'`
- `grep -rnF -e 'Read and update' -e 'Update task status in' -e 'Ensure every task entry includes' implementation/ docs/wiki docs/guides tests/`
- `grep -rln 'scrum-master' tests/ --include='*.py' --include='*.yaml' --include='*.json'`, then read each hit for an asserted
  string.
- Compare each count with §4, and the `Before` match counts with the "occurs once" claims in §3.

## 6. The user question (one round)

**Q-T613 — The Scrum Master task protocol and the third checkpoint name.**

**Answer with one letter per item, or say "all recommended". Nothing is applied before you answer.**

All three items are decided by ADR-008 Step B, because the other document is an agent or a skill and no conflict is inside
tier 1. Options A and B are therefore "approve the ruled edit" or "hold it". Option C exists only because changing the
tier-1 text instead is your prerogative. ADR-008 never does it on its own, and I have drafted no edit for it.

**Item S1 — `scrum-master:23, :25, :135` against `AGENTS.md:18`** (who writes and transitions the ledger rows)

| Option | What changes | Consequences |
|---|---|---|
| **S1-A (Recommended)** | S-1, S-2, S-4: the Scrum Master reads the board and proposes new tasks and status changes; the orchestrator writes the rows | One stable agent, 6 root-drift paths. Same model as your T607 O5 decision and as `project-planning:209–217`. The Scrum Master keeps sprint planning, estimates, GitLab issues and velocity. No check is relaxed |
| **S1-B** | Hold | The agent keeps telling a subagent to update the ledger, against `AGENTS.md:18`. `/new-feature:25` and `project-planning` already say "propose", so the corpus stays split |
| **S1-C** | Keep the Scrum Master writing the board and change `AGENTS.md:18` to allow it, in a separate instruction-change task | A tier-1 change, no edit drafted. It would reverse your T607 O5 decision, and it contradicts `orchestrator.md:33–34, :70` and `AGENTS.md:5` unless those change too |

**Item S2 — `scrum-master:27` against `AGENTS.md:14`** (the fields of a task entry)

| Option | What changes | Consequences |
|---|---|---|
| **S2-A (Recommended)** | S-3: the Scrum Master proposes entries in the ledger's seven columns; story points and sprint go in the GitLab issue and the task brief | Same 6 paths as S1-A (one file). Matches `project-planning:211`. The velocity log is untouched |
| **S2-B** | Hold | `:27` keeps demanding two fields the ledger has no column for |
| **S2-C** | Add `Story points` and `Sprint` columns to `AGENTS.md:14` | A tier-1 and schema change: `docs/tasks/validate-tasks.py`, the `task-management` skill, `/batch`, `/bug-report`, and every ledger fixture would follow. No edit drafted. **Not recommended** |

**Item K — `checkpoint-protocol:104, :173, :179` (and `:56, :99, :117`) against `AGENTS.md:27` and the skill's own `:44`**

| Option | What changes | Consequences |
|---|---|---|
| **K-A (Recommended)** | C-1 to C-5: the skill writes `checkpoint-<SEQ>-<phase>.md`, cites `AGENTS.md`, and its two examples gain a `<phase>` part | One stable skill, 7 root-drift paths. Removes the only text that tells a reader to write `checkpoint-<N>.md`. Agrees with `AGENTS.md:27`, `memory-management:155`, `orchestrator.md:150`, the three commands, `_template.md:3`, and the real checkpoints. No golden file changes |
| **K-B** | Hold | The skill keeps two names for one file: its own `:44` and `:104` disagree, and `:104` disagrees with `AGENTS.md:27` |
| **K-C** | Change `AGENTS.md:27` to `checkpoint-<N>.md` | A tier-1 change in a separate task, no edit drafted. Every real checkpoint, `_template.md:3`, `/new-feature:31`, `/new-project:43`, `/new-poc:46`, `orchestrator.md:150` and `memory-management:155` would have to follow, and the golden assertion in `new-feature-checkpoint-line-compliant` would need a grant and a new baseline. **Not recommended** |

**Recommendation: S1-A, S2-A, K-A ("all recommended").** One mechanical implementation task, then one root refresh, covers
the two files (13 paths). The three items are independent, so any subset is also valid. Each follows from ADR-008 Step B and
from your 2026-10-09 decisions, not from any count of files that agree with `AGENTS.md`. Popularity is not authority
(ADR-007).

## 7. Observations (new or restated; not ruled)

Other agents and skills with the same Task Protocol conflict, or a neighbouring one. These are observations for the
orchestrator to park or schedule. I rule none of them.

| # | Site | Quote | Shape and my reading |
|---|---|---|---|
| **O-1** | `skills/blocker-escalation/SKILL.md:78` (Procedure 1, "Agent Reports a Blocker") | "4. Transition the impacted task(s) to `blocked` status in `active-tasks.md`." | **Same shape as S1.** An agent transitions a ledger row; `AGENTS.md:18` says only orchestrators transition tasks, and says agents "report completion and blockers". Step A fails on the literal text; P1 would fire (an `experimental` skill, irrelevant). `:122` ("Transition impacted tasks from `blocked` back to `in_progress`", actor unnamed) is the Step A case. Same remedy as `project-planning` E-G7b. The strongest match found |
| **O-2** | `skills/task-management/SKILL.md:112–124` (Procedures 1 and 2) | "1. Open `docs/tasks/active-tasks.md`. … 3. Add a new row to the table with status `pending`." | No actor is named, so Step A probably holds. Its Rails (`:21–26`) and Procedure 4 (`:136`) make only the archive orchestrator-only. A reader who is not the orchestrator can follow Procedure 1. Neighbouring defects in the same file: `:115–116, :129–132` use `BlockedBy` and `Blocks` fields that its own 7-column table (`:55`) does not have, and the examples at `:167–179` use a different column order |
| **O-3** | `skills/gitlab-management/SKILL.md:134–137, :170–172` | "4. When a GitLab issue is updated externally … sync the change back to `active-tasks.md` at the next checkpoint." and "`status::in-progress` … Maps to `in-progress` in active-tasks.md", "`status::review` … Maps to `review` in active-tasks.md" | `:137` names no actor, so Step A probably holds, but the Scrum Master reads it as a licence to write. `:171–172` give ledger values `in-progress` and `review`; `AGENTS.md:8–11` spells them `in_progress` and `in_review` (the same defect E-G7b fixed in `project-planning`). That is a separate subject (Lifecycle States). The GitLab `priority::high/medium/low` labels against the ledger's `P0/P1/P2` (also S2's neighbour) have no stated mapping |
| **O-4** | `skills/dependency-graphing/SKILL.md:26, :134–140` | "extract `ID`, `Title`, `Status`, `Blocks`, and `BlockedBy`" | Reads two columns the ledger does not have (`AGENTS.md:14` has `Depends on`). Read-only, so no actor conflict. Same family as S2 |
| **O-5** | `skills/checkpoint-protocol/SKILL.md:101`, `:59` | "3. For "Completed Tasks," query `active-tasks.md` for tasks marked `done` since the last checkpoint." and "**Author:** <agent-name or orchestrator>" | `:101` presupposes `done` rows in `active-tasks.md`, which `AGENTS.md:15` forbids (the INVARIANT); the rows are in `completed-tasks.md`. As written the step finds nothing. P1 would likely fire. `:59` lets an agent author a checkpoint while `AGENTS.md:28` says the orchestrator writes it at every phase boundary; the skill's other triggers (`:36–39`) go beyond phase boundaries, so Step A probably holds. Not in K's scope, so not edited |
| **O-6** | `skills/checkpoint-protocol/SKILL.md:56–93` against `docs/checkpoints/_template.md` | The skill's headings (`## Progress Summary`, `## Active Tasks`, `## Token Spend`) differ from the template's (`## Phase summary`, `## Open / carried over`, `## Token usage`) | The template is not a knowledge document and `AGENTS.md:29` lists the required elements, not headings. Not a Task Protocol conflict; recorded only |
| **O-7** | `agents/scrum-master.md:84–87`, `:32` | `## Priority: [High/Medium/Low]` and `priority::high/medium/low` | Fields of the GitLab issue, not of the ledger. Step A holds; S-3 says the ledger Priority is `P0`/`P1`/`P2` |
| **O-8** | `scrum-master:20` "Assign tasks to appropriate team roles" | | Read as a proposal inside a sprint plan, so Step A holds. The ledger `Owner` and the delegation are the orchestrator's (`AGENTS.md:6`; `orchestrator.md:36`). If the user wants the verb changed to "propose", it is a one-word follow-up |

**Read and found to conform (Task Protocol):** `product-owner` (effort estimation is "the Scrum Master's role"; no ledger
write), `release-manager` (`:45` "tracked as tasks" is passive, so Step A holds), `orchestrator` (it creates tasks and writes
briefs itself, `:33–34`, `:70`), `backend-developer`, `tech-lead` (`:100` has the orchestrator add the condition to the task
list), `qa-engineer`, `security-engineer`, `devops-engineer`, `solution-architect`, `project-planning` (already amended;
live at `:209–217`), `release-workflow`, `verification-before-completion`, and the commands `/new-feature` (live `:25`),
`/new-project`, `/plan`, `/batch`, `/bug-report`, `/handoff`, `/team-status`, `/sprint-status` (each runs as
`agent: "orchestrator"`).

**Checkpoint name, other sites:** none of the files read repeats `checkpoint-<N>` or `checkpoint-001.md`. Four sites
already take the correct form (`memory-management:155`, `orchestrator.md:150`, `commands/new-feature.md:30–31`,
`commands/new-project.md:43`).

**Still parked (plan-112 §2, not in plan-117):** CI's third `release-notes.md` (P32 O6), P41 O3 and O4, and P33 O1, O2, O5
and O6. This artifact closes **P41 O2** (if S1-A and S2-A are approved) and **T607 O7** (if K-A is approved).

## 8. Handoff package for the implementing task (specification; no task is created here)

| Field | Content |
|---|---|
| `task_id` | To be assigned by the orchestrator (a mechanical-tier follow-up to `T613`) |
| `definition` | Apply, verbatim, only the fences the user approves in Q-T613 (§3), then regenerate and declare root drift |
| `constraints` | Never reword. Apply each pair by exact string replacement, matching each Before as a whole line, and assert it matches exactly once. Stop and report if an anchor is missing or not unique. Do not edit `AGENTS.md`, `implementation/AGENTS.md`, any instruction, any command, `orchestrator.md`, `blocker-escalation`, `task-management`, `gitlab-management`, any file under `tests/golden/**`, `scripts/`, `.env*`, or any derived platform folder by hand. Do not refresh the repo root. Do not push, and never run any merge or approve call |
| `depends_on` | The user's answer to Q-T613 |
| `input_artifacts` | `task-protocol-and-checkpoint-name-ruling-v1.md` (this file) as the single implementation input |
| `expected_outputs` | The edited files; regenerated mirrors and `implementation/registry/index.json`; `tests/_baselines/root-install-drift.json` with exactly the printed paths (expected 13); a report with every §4 count as lines and occurrences |
| `blocker_policy` | `AGENTS.md` § Blocker Protocol: report type and severity. A non-golden test that asserts a Before string, or a held-out hit, is a `dependency` blocker to the orchestrator |

Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`,
`scripts/scorecard.py --check` (equal to the current baseline), `python3 docs/tasks/validate-tasks.py`, and `python3
tests/run.py` with output redirected to a file. Confirm byte-unchanged: `AGENTS.md`, every instruction, every command,
`orchestrator.md`, `blocker-escalation`, `task-management`, `gitlab-management`, every script, and `tests/golden/**`.

## 9. Still unverified

1. The worktree commit `c5aa8e4` plus the scoping commit (stated by the orchestrator).
2. Every count in §4 and every "occurs once" claim in §3, all by reading, not `grep`.
3. The platform projections' line numbers other than the two `.claude` files, and whether `implementation/.<platform>/`
   mirrors are tracked.
4. That no held-out case, and no test outside the three golden briefs I read, asserts any Before string.
5. That `implementation/registry/summary.md` and the maturity checks are unaffected.
6. That the scope text relied on in §2 (`scrum-master:26, :116`, `checkpoint-protocol:44, :50–51`) was not edited in the
   change that first recorded these conflicts (I cannot diff history).
7. Agents not read: `frontend-developer`, `database-engineer`, `technical-writer`, `ux-designer`, `technology-scout`,
   `context-retriever`, `scaffolding-agent`, `data-mockup-agent`, `demo-agent`, `evaluation-agent`, `feasibility-agent`,
   `integration-agent`, `poc-orchestrator` (beyond what earlier artifacts read), `poc-devops-engineer`, `poc-qa-engineer`,
   `poc-security-engineer`, `poc-technical-writer`, `technical-debt-narrator`. Skills not read: `api-design`, `ci-cd-pipeline`,
   `cwso-awareness`, `plan-approve-execute` (read by `naming-conflicts-ruling-v1.md`, not re-read), `skillify`,
   `systematic-debugging`, `technology-scouting`, `technical-debt-tracking`, `testing-strategy`, `receiving-code-review`,
   `validation-gates`, `code-review`, `poc-evaluation`, `rapid-prototyping`. Commands not read: `code-review`,
   `consolidate-memory`, `discover-skills`, `evaluate-poc`, `new-poc` (`:46` read via an earlier artifact), `poc-demo`,
   `prepare-release`, `security-audit`, `skillify`, `validate-tasks`, `validate-workflow`.
8. The user's decisions of 2026-10-09 are quoted as the orchestrator relayed them, not re-read from the user's own message.

## 10. Summary

| Item | Subject | Settled by | Outcome | Edits | User decision? |
|---|---|---|---|---|---|
| S1 | Who writes the ledger rows | ADR-008 Step B (P1), Step A note as fallback | Amend `scrum-master`: propose / write | S-1, S-2, S-4 | Approval only |
| S2 | Fields of a task entry | ADR-008 Step B (P1) | Amend `scrum-master`: the ledger's seven columns | S-3 | Approval only |
| K | Checkpoint file name | ADR-008 Step B (P1); same-file defect as a second ground | Amend `checkpoint-protocol` toward `AGENTS.md:27` | C-1 to C-5 | Approval only |

- **Maturity, corpus counts, majority practice and golden-coupling convenience** were relied on nowhere as authority. The
  agreement of other files with `AGENTS.md` appears only as a consequence in §6.
- **No edit is applied, and none is upward or relaxing.** No tier-1 file, command or golden path is touched.
- **Golden:** no fixture and no result changes under any option. No grant and no baseline are needed.
- **Blockers:** none for this task. The unverified items in §9 (held-out and non-golden test coupling) are `dependency`
  checks for the implementing task, severity `minor`.
