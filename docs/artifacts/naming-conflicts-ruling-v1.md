# Artifact: naming-conflicts-ruling-v1.md

> Filename: `naming-conflicts-ruling-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T607 (P2, judgment tier, decision only)
- **Created**: 2026-10-09
- **Based on:**
  - `docs/tasks/task-T607.md` (the brief, authoritative);
  - `docs/plans/plan-114-placeholder-flag-and-naming-rulings.md` (§1, §3 the cosmetics, §4 what stays parked);
  - `docs/plans/plan-112-parked-note-cleanup.md` §2;
  - `docs/artifacts/path-conventions-v3.md` §8 (O1, O2, O5; observations carried from `path-conventions-v1.md` §2.3 A-2′
    and §8);
  - `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted) and
    `docs/decisions/ADR-007-command-contract-authority.md` (Accepted);
  - precedents read this session: `docs/artifacts/command-contract-resolution-v1.md` §3 row B and §5;
    `docs/artifacts/poc-skills-alignment-v1.md` §1.3 and E13 (the T570 "the skill proposes, the orchestrator creates"
    ruling);
  - the user's decision of 2026-10-09, **"C - but do not forget / note the cosmetics"**. Meaning, as the orchestrator
    relayed it: rule only the three `AGENTS.md` conflicts (O1, O2, O5); the other plan-112 §2 notes stay parked; the
    `poc-orchestrator` indentation is cosmetic and is noted in §7, riding along with the implementation.
- **Supersedes**: none (first version).
- **Decision references**: ADR-008 Step A (P3a), Step B (P1, including § Within tier 1), Step E (P5), D2, D4, D5, P4;
  ADR-007 branch 1 and §5 (never relax a check). No new ADR is minted.
- **Status of every edit in this document**: **held for the user. Nothing is applied.** The only other file changed by
  this task is the `**Status:**` line of `task-T607.md`.

## 0. Method and limits

- **Commit.** The orchestrator states the worktree is on `develop` `ec71a7d` **(unverified: no shell)**. Every line number
  below was read in the worktree at that commit.
- **No shell, no grep, no directory listing.** Every count in §4 comes from reading whole files and is **(unverified by
  grep)**. §9 collects every unverified claim, and §5.4 lists the greps the implementing task must run first.
- **Source files read in full:** `AGENTS.md` (`:1–85`) and `implementation/AGENTS.md` (`:1–40`);
  `implementation/knowledge/instructions/coding-standards.md`; commands `new-project`, `new-feature`, `new-poc`, `plan`,
  `batch`, `sprint-status`; agents `scrum-master`, `orchestrator` (`:1–110`), `poc-orchestrator` (`:84–113`); skills
  `plan-approve-execute`, `checkpoint-protocol`, `task-management` (`:1–120`); `docs/plans/_template.md`,
  `implementation/docs/plans/_template.md` (`:56–61` only), `docs/checkpoints/_template.md` (`:1–30`),
  `docs/decisions/_template.md` (`:1–15`); `tests/_baselines/root-install-drift.json`; the first lines of the projections
  named in §5.1.
- **Golden.** Under `tests/golden/open/` only: `brief.md` and `expect.py` of `new-project-plan-doc-and-lifecycle-states`;
  `brief.md` of `new-feature-checkpoint-line-compliant` and `new-feature-plan-doc-compliant`. I rely on
  `path-conventions-v1.md` §6.1 (not re-read) for the statement that `new-feature-real-checkpoint-format-drift` quotes
  step 7 only. **I never opened `tests/golden/held-out/`**, so I cannot say whether a held-out case pins any clause
  below. Every golden case name in this document has a `tests/golden/open/` directory.
- **Secrets.** I read no `.env*`, credential or key file. I edited nothing under `.claude/`, `.github/` or any other
  derived platform folder.
- **Encoding.** `§` is U+00A7, `—` is U+2014. Each four-backtick fence holds one Before/After pair. Apply each edit by its
  Before text, never by line number. **One anchor (N-1) starts with a TAB (U+0009).** The fence contains a real tab.
- **Scope-gaming guard (ADR-008 § Risks).** These three conflicts were first recorded in `path-conventions-v1.md` §8 at
  `c152eb7`. The `coding-standards` lines the brief cites (`:66–83`) are where I read them now, so I saw no scope edit
  since then (**unverified** beyond those lines). No declared-scope sentence relied on below was added in the same
  change as a ruling.
- **Maturity.** I relied on no `maturity:` value anywhere in this document (P4). `coding-standards` is `stable` and is
  placed in tier 1 only by D1; `/new-project` and `/new-feature` are `stable` commands, `scrum-master` is a `stable`
  agent, `plan-approve-execute` is `experimental`. None of that decides any step below.

## 1. Summary of the rulings

| Item | Subject (D3) | Both sides | Step that fired | Outcome | Edit |
|---|---|---|---|---|---|
| **O1-a** | Checkpoint file name | `AGENTS.md:27` against `coding-standards:66, :69, :82` | A fails, B within tier 1 gives no declared precedence, **E (P5)** | **Escalated** to the user. Recommendation: amend `coding-standards` toward `AGENTS.md` | C-1, C-2, C-3 held |
| **O1-b** | Decision-record file name | `AGENTS.md:33` against `coding-standards:66, :68, :81` | A fails, **E (P5)** | **Escalated**, same recommendation | C-1, C-3 held |
| **O1-c** | Plan file name and revision behaviour | `coding-standards:66–67, :72, :74, :80` against skill `plan-approve-execute:20–26, :111, :113, :184` (and the user's recorded Q-P32a decision) | A fails, ADR-008 § Scope (settled question) for the name, **E (P5)** for the tier-1 text | The skill and the decision stand. The tier-1 row is escalated with O1-a | C-1, C-2, C-3 held |
| **O1-d** | Plan revision rule in the templates | both `_template.md:61` against skill `plan-approve-execute:184` | A fails; templates are outside ADR-008's covered documents | Template yields to the skill and to Q-P32a. Not a tier-1 question | T-1 held |
| **O2-a** | `/new-project` checkpoint path | `commands/new-project.md:43` against `AGENTS.md:27` | A fails, **B (P1 = ADR-007 branch 1)** | **Amend the command** toward `AGENTS.md` | N-1 held |
| **O2-b** | `/new-project` artifact version format | `commands/new-project.md:51` against `AGENTS.md:22` | A fails, **B (P1)** | **Amend the command** toward `AGENTS.md` | N-2 held |
| **O5** | Who creates tasks | `commands/new-feature.md:25` against `AGENTS.md:18` | A fails on the repo's own usage of "create"; the same edit is justified on the other reading, **B (P1)** | **Amend the command**: the Scrum Master proposes, the orchestrator creates | N-3 held |

**Where the ADR decides and where it does not.**
- O2 and O5 are decided by ADR-008 Step B. They reach the user as "approve the ruled edit, or hold it".
- O1 is a conflict **inside tier 1** (`AGENTS.md` against the stable instruction `coding-standards`). ADR-008 § Within tier 1
  does not rank them, and no uncontested declared precedence exists (§2.1 Step B). It is escalated under P5 as the user
  question in §6. My recommendation is not a ruling.

## 2. D5 records

### 2.1 O1 — version suffixes on plan, decision and checkpoint file names

**Verbatim clauses (all at `ec71a7d`).**

Tier 1, `AGENTS.md`:
- `:22` "- Immutable artifacts: `<type>-v<N>.md` (e.g. `requirements-v1.md`, `architecture-v1.md`)"
- `:24` "- Revisions create new versions, never overwrite."
- `:27` "- Checkpoints: `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`"
- `:33` "- ADRs: `docs/decisions/ADR-<NNN>-<slug>.md`"
- `:35` "- Immutable once accepted; superseded decisions link to replacement."
- `:73–74` (§ Code Standards) "- See platform instruction projections: `.github/instructions/coding-standards.instructions.md`, … `.clinerules/coding-standards.md`."

Tier 1, `implementation/knowledge/instructions/coding-standards.md`:
- `:2` (description) "Use when writing code in any language. Covers naming conventions, function design, error handling, general
  clean code principles, and artifact versioning."
- `:3` `applyTo: "**/*.{ts,js,py,java,cs,go,rs,rb,php,swift,kt}"`
- `:9–13` (Rails, Inputs) "Triggers on any code file matching this instruction's `applyTo` glob (…); also invoked explicitly
  by `tech-lead.md`'s Code Standards responsibilities and by `AGENTS.md`'s "Code Standards" routing table when
  establishing or reviewing project conventions."
- `:15–20` (Rails, Out of scope) "… Does not cover language-specific idioms beyond the naming, function-design,
  error-handling, security, organization, and artifact-versioning rules stated below."
- `:22–27` (Rails, Failure mode) "… Artifact-versioning violations specifically (overwriting a prior `<type>-vN.md` file
  instead of creating a new version) are treated as a process defect …"
- `:66` "All plan, decision, and documentation artifacts follow the `<type>-vN.md` naming convention:"
- `:67` "- `plan-v1.md`, `plan-v2.md`, `plan-v3.md`"
- `:68` "- `decision-v1.md`, `decision-v2.md`"
- `:69` "- `checkpoint-v1.md`, `checkpoint-v2.md`"
- `:72` "- **Never overwrite prior versions.** Always create a new file with an incremented version number."
- `:74` "- The latest version is the active/current version. Prior versions are historical record."
- `:75` "- When referencing an artifact, always use the full versioned filename (e.g., `plan-v3.md`, not `plan.md`)."
- `:80` "| `plan-vN.md` | `docs/plans/` | Implementation plans |"
- `:81` "| `decision-vN.md` | `docs/decisions/` | Architecture/design decisions |"
- `:82` "| `checkpoint-vN.md` | `docs/checkpoints/` | Progress checkpoints |"

Other documents on the same subjects (not tier 1):
- `skills/plan-approve-execute/SKILL.md:23` `docs/plans/plan-<ID>.md`; `:26` "`<ID>` is the plan's three-digit number, a
  hyphen, and a short slug … A new plan takes the next number not yet used in `docs/plans/`."; `:111` "Approve | Update plan
  status to `approved`, proceed to Execute phase"; `:113` "Reject | Update plan status to `rejected`, …"; `:182` "Plans can be
  revised multiple times before approval. Iterate until the user is satisfied."; `:184` "If a plan is superseded by a new plan,
  update its status to `superseded` and link to the replacement."
  (**Line shift:** the brief and `path-conventions-v3.md` cite `:182` for the superseded rule. P-1 added two lines, so it is
  `:184` now.)
- `skills/checkpoint-protocol/SKILL.md:44` `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`; `:50–51` "This matches `AGENTS.md`'s
  Checkpoint Protocol section verbatim".
- `docs/checkpoints/_template.md:3` "Filename: `checkpoint-<SEQ>-<phase>.md`"; `docs/decisions/_template.md:3` "Filename:
  `ADR-<NNN>-<slug>.md`".
- Both plan templates, `:3` "Filename convention: `plan-<ID>.md`, with `<ID>` as the `plan-approve-execute` skill § File Location
  defines it (e.g. `plan-042-payment-feature.md`)." and `:61` "- [ ] Plan locked; revisions create `plan-<slug>-v2.md`".
  Neither template is a knowledge document.

**Subjects (D3).** The table is three conflicts, not one, so each gets its own record.

#### O1-a — the file name of a checkpoint

| Field | Content |
|---|---|
| **Clauses** | `AGENTS.md:27` against `coding-standards:66, :69, :75, :82` (quoted above) |
| **Step A** | **Fails on the text as written.** MUSTs: `AGENTS.md:27` fixes the checkpoint path as `checkpoint-<SEQ>-<phase>.md`; `coding-standards:66` says "**All** plan, decision, and documentation artifacts follow the `<type>-vN.md` naming convention", gives `checkpoint-v1.md` and `checkpoint-vN.md` in `docs/checkpoints/` as the literal forms (`:69, :82`), and requires the "full versioned filename" (`:75`). **Exclusivity:** neither clause says "only". `:66` says "All", and `:82` pairs the location with one file-name form, which is a closed pairing for that field. **One-value test:** one checkpoint has one path. For a given phase, `AGENTS.md:27` computes `checkpoint-003-planning.md` and `coding-standards:82` computes `checkpoint-v3.md`. They differ. **Recorded alternative reading (not adopted):** read `-vN` as a suffix absorbed by `AGENTS.md`'s open `<phase>` slot, giving `checkpoint-003-planning-v1.md`. That would pass Step A by D4 ("uses values that nest inside the other's"). I do not adopt it, because `:67–69` and `:80–82` print complete literal names (`checkpoint-v1.md`) that no such reading produces, so the table's examples would have to be read as non-literal. The user can take that reading by choosing option O1-C in §6. |
| **Step B (§ Within tier 1)** | **No ruling.** Both documents are tier 1, so they are not ranked (user decision Q3, "Keep unranked"). The only way to settle it without the user is an uncontested declared precedence by name. I found none. `AGENTS.md:73–77` (§ Code Standards) routes code standards to `coding-standards`, but names no artifact-naming subject and declares no precedence. `coding-standards:9–13` says it is "invoked explicitly by … `AGENTS.md`'s "Code Standards" routing table", which says how it is brought into play, not that it yields on a subject. Its own Failure mode (`:22–27`) states the `<type>-vN.md` rule as its own. No other part of its Rails concedes. The four stable instructions' bodies were not searched for a precedence sentence over `AGENTS.md` beyond `coding-standards` **(unverified for the other three)**. |
| **Reach (D2)** | `AGENTS.md` declares no scope narrower than the repository (D2), and `:27` names checkpoints. `coding-standards` places artifact versioning in its own scope at `:2`, `:15–20` and `:22–27`. `applyTo` (`:3`) excludes `docs/**/*.md`, but D2 says "`applyTo` filters paths; it does not name subjects", and path-conventions-v1 §2.3 recorded the reach as contested. **The ruling does not depend on that.** If `coding-standards` reaches the subject, the two tier-1 texts contradict. If it does not, the table rows sit outside the instruction's own scope and nothing is ranked. Either way the rows mislead a reader, and the same edit fixes them. |
| **Step fired** | **E (P5).** Escalated as §6, O1. **Hold:** neither document is amended on this subject until the user decides (P5 Form 3). |
| **Amendment** | None applied. Recommended edit: C-1, C-2, C-3 (§3), which fall on `coding-standards`, a tier-1 file. ADR-008 P1 Remedy: "If the tier-1 text is wrong on the merits, the fix is a separate instruction-change task". That task needs the user's answer first. |
| **Maturity** | Not relied on. `coding-standards`' `maturity: stable` is used for D1 tier membership only. |

#### O1-b — the file name of a decision record

| Field | Content |
|---|---|
| **Clauses** | `AGENTS.md:33` "ADRs: `docs/decisions/ADR-<NNN>-<slug>.md`" against `coding-standards:66, :68, :81` ("`decision-v1.md`, `decision-v2.md`"; "`decision-vN.md` / `docs/decisions/` / Architecture/design decisions") |
| **Step A** | **Fails** on the literal text, by the same reasoning as O1-a. One decision record has one path: `ADR-008-knowledge-document-authority.md` against `decision-v8.md`. The same recorded alternative reading applies and is not adopted. `docs/decisions/_template.md:3` agrees with `AGENTS.md:33`. |
| **Steps B, E** | As O1-a. `AGENTS.md:33` and `:35` ("Immutable once accepted") say nothing that makes `AGENTS.md` yield, and `coding-standards` declares no precedence. |
| **Step fired** | **E (P5).** Held. |
| **Amendment** | None applied. Recommended edit: C-1 and C-3. |
| **Maturity** | Not relied on. |

#### O1-c — the file name of a plan, and the "never overwrite" rule applied to plans

| Field | Content |
|---|---|
| **Clauses** | `coding-standards:66, :67, :72, :74, :80` against skill `plan-approve-execute:20–26` (`docs/plans/plan-<ID>.md`), `:111, :113` (the plan's status is **updated in place** on approval or rejection), `:182` (a plan is revised in place before approval) and `:184` (a superseded plan is marked `superseded`, and the replacement is a new plan). `AGENTS.md` names no plan path. `AGENTS.md:22–24` does not say a plan is an "immutable artifact" (path-conventions-v1 §2.1) |
| **Step A** | **Fails on the name**, on the literal text. `plan-v1.md` does not match `plan-<ID>.md` (`<ID>` is a three-digit number, a hyphen and a slug, `:26`). **Fails on the behaviour** as well: `:72` "Never overwrite prior versions" and `:74` "The latest version is the active/current version" cannot both hold with `:111` and `:113`, which overwrite a plan's status in place. The same recorded alternative reading (`plan-042-rate-limiting-v2.md` fits `plan-<ID>.md` because the slug admits `-v2`) does not reach the behavioural contradiction. |
| **What is settled** | The **name** of a plan is a question already settled by a recorded user decision. Q-P32a, "plan-<NNN>-<slug>.md (Recommended)" (`path-conventions-v3.md` §1), says every plan on either track is `docs/plans/plan-<ID>.md`. ADR-008 § Scope: "That decision governs, and documents are amended to it." `coding-standards:67` and `:80` contradict that decision. |
| **What is not settled** | Amending a tier-1 file is not routine (ADR-008 § Consequences, "Still not routine … any change to a tier-1 document's own text"), and the settled question does not decide the `AGENTS.md` pair in O1-a and O1-b. So the plan row travels with them in §6. The skill's behaviour (in-place status edits) is not a defect: no tier-1 text says a plan is immutable. |
| **Step fired** | ADR-008 § Scope (settled by a user decision) for the name. **E (P5)** for the decision to edit the tier-1 text, carried in §6. |
| **Amendment** | None applied. Recommended edit: C-1, C-2, C-3, which remove `plan-vN.md` and restrict the "never overwrite" rules to the `-vN` artifacts. |
| **Maturity** | Not relied on (`plan-approve-execute` is `experimental`; irrelevant). |

#### O1-d — the revision rule in the plan templates

| Field | Content |
|---|---|
| **Clauses** | `docs/plans/_template.md:61` and `implementation/docs/plans/_template.md:61` "- [ ] Plan locked; revisions create `plan-<slug>-v2.md`" against skill `plan-approve-execute:184` "If a plan is superseded by a new plan, update its status to `superseded` and link to the replacement." and `:26` "A new plan takes the next number not yet used in `docs/plans/`." |
| **Step A** | **Fails.** One revision of a locked plan has two names: `plan-<slug>-v2.md` (no new number; `<slug>` is no longer defined, since P-8 replaced it with `<ID>` on `:3`) against a new plan with the next free number. |
| **Covered?** | **No.** The templates are not knowledge documents, so ADR-008 does not rank them. They are amended to a recorded user decision (Q-P32a, which defines the plan name once, in the skill) and to the template's own pointer: `:3` says "with `<ID>` as the `plan-approve-execute` skill § File Location defines it". The template places the subject with the skill in its own words. |
| **Step fired** | ADR-008 § Scope (settled by a user decision), with the template's own `:3` pointer as the same-file prong. Not a tier-1 question, so it does not wait for the O1 answer. |
| **Amendment** | None applied. Held edit: T-1 (§3), applied to both templates. |
| **Maturity** | Not relied on. |

### 2.2 O2 — `/new-project` against `AGENTS.md`

**Verbatim clauses (all at `ec71a7d`).**
- `commands/new-project.md:41–43` (Phase 4, step 14):
  `14. After each phase, publish a compact checkpoint summary:` /
  `	- `[CHECKPOINT] id=<phase_or_gate> | done=[...] | in_flight=[...] | blocked=[...] | decisions=[...] | artifact_refs=[...] | next=[...]`` /
  `	- Write checkpoint to `docs/checkpoints/checkpoint-<phase>.md``
- `commands/new-project.md:50–52` (Phase 5, step 18): `18. Produce versioned artifacts for all deliverables:` /
  `    - Format: `<artifact-name>-v<major>.<minor>.md`` / `    - Store in `docs/artifacts/``
- `AGENTS.md:27` "- Checkpoints: `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`"; `AGENTS.md:28` "- Written at every phase
  boundary by the orchestrator."; `AGENTS.md:22` "- Immutable artifacts: `<type>-v<N>.md` (e.g. `requirements-v1.md`,
  `architecture-v1.md`)".
- **In-corpus models of the amended form, both read this session:**
  - `commands/new-poc.md:46` "Write checkpoint per `AGENTS.md` § Checkpoint Protocol: store at
    `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`, with `<phase>` naming the PoC gate";
  - `commands/new-feature.md:30–31` "Write a checkpoint after implementation completes, per `AGENTS.md` § Checkpoint
    Protocol: / Store at `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`" and `:34` "Format: `<artifact-name>-v<N>.md`, per
    `AGENTS.md` § Artifact Versioning".

#### O2-a — the checkpoint path (`:43`)

| Field | Content |
|---|---|
| **Step A** | **Fails.** `AGENTS.md:27` fixes the path as `checkpoint-<SEQ>-<phase>.md`. `/new-project:43` gives `checkpoint-<phase>.md`, with no `<SEQ>`. **Same-token reading:** `<phase>` is the same placeholder in both, and in `AGENTS.md` it is a slot separate from `<SEQ>` (as in `checkpoint-protocol:47–49`). **One-value test:** for a given phase the two clauses compute different file names (`checkpoint-planning.md` against `checkpoint-003-planning.md`). **Rejected counter-reading:** let `<phase>` absorb the sequence number (`checkpoint-<phase>.md` with `<phase>` = `003-planning`). It would pass by D4, but it reads one token as two different slots in two documents. This is the "rival convention for the same thing" that ADR-007 branch 1 forbids. |
| **Step B (P1 = ADR-007 branch 1)** | **Fires.** (a) Quotable: `AGENTS.md:27` and `/new-project:43` (above). (b) Reach: `AGENTS.md` declares no scope narrower than the repository (D2), and `:27–28` name the checkpoint path and the orchestrator who writes it; `/new-project` is `agent: "orchestrator"` (`:3`). (c) Step A fails. (d) The other document is a command, so P1 is ADR-007 branch 1, unchanged. |
| **Precedent** | `command-contract-resolution-v1.md` §3 row B: `/new-feature` step 7 had the same shape and was ruled branch 1, "A command may not create a second, incompatible checkpoint convention." ADR-007 Alternatives B names "rival conventions for checkpoint filenames and artifact versioning" as the cost of leaving such clauses. |
| **What is not ruled** | `:42`, the `[CHECKPOINT]` one-line marker. It is a summary rendering that competes with no `AGENTS.md` clause (D4), and `/new-poc:45–46` keeps the same marker beside the `AGENTS.md` path. It is untouched. |
| **Step fired** | **B (P1).** |
| **Amendment** | **Amend the command**, not `AGENTS.md` (P1 Remedy, "This ADR never amends a tier-1 document to match a lower one"). Edit N-1 (§3). It cites `AGENTS.md` rather than restating it, as T542 did. |
| **Maturity** | Not relied on (`/new-project` is `stable`; irrelevant). |

#### O2-b — the artifact version format (`:51`)

| Field | Content |
|---|---|
| **Step A** | **Fails.** `AGENTS.md:22` gives `<type>-v<N>.md` with the examples `requirements-v1.md` and `architecture-v1.md`. `/new-project:51` gives `<artifact-name>-v<major>.<minor>.md`. One deliverable has one first-version name: `-v1.md` against `-v1.0.md`. **Exclusivity:** `AGENTS.md:22` names the form of "Immutable artifacts" without "only", but a deliverable with one name cannot take both. `<N>` is read as a single sequence number, which is how tier 1's other text reads it: `coding-standards:73` "Version numbers are sequential integers starting at 1". **Reading dependency, disclosed:** if `<N>` were allowed to be "1.0", Step A would pass. `AGENTS.md` itself prints only integer examples, and `command-contract-resolution-v1.md` §5 already records the same finding for a command clause of this shape ("Independently settled by `AGENTS.md` § Artifact Versioning, which mandates `<type>-v<N>.md` outright"), so I read it as an integer. |
| **Step B (P1)** | **Fires.** (a) Quotable. (b) `AGENTS.md:21–24` is § Artifact Versioning and names the subject. `/new-project:50` is the command's "Produce versioned artifacts" step. (c) Step A fails. (d) A command: ADR-007 branch 1. The corpus is not offered as authority: `command-contract-resolution-v1.md` §5 notes that no artifact there used `major.minor`, but "the count is not load-bearing". |
| **Step fired** | **B (P1).** |
| **Amendment** | **Amend the command.** Edit N-2 (§3), in the form `/new-feature:34` already carries. |
| **Maturity** | Not relied on. |

### 2.3 O5 — `/new-feature:25`, the Scrum Master creates tasks

**Verbatim clauses (all at `ec71a7d`).**
- `commands/new-feature.md:25` "5. Have the Scrum Master create tasks and estimate effort"; `:3` `agent: "orchestrator"`;
  `:36` (item 9) "Update `docs/tasks/active-tasks.md` with new tasks and state transitions".
- `AGENTS.md:18` "- Only orchestrators create/transition tasks. Agents report completion and blockers."; `AGENTS.md:4–5`
  "Two orchestration tracks: Production (`@orchestrator`) and PoC (`@poc-orchestrator`) / Only orchestrators are
  user-invocable. All other agents are subagents."; `AGENTS.md:17` "Task briefs: `docs/tasks/task-<ID>.md` …".
- `agents/orchestrator.md:33–34` "Create task entries in `docs/tasks/active-tasks.md` / Create detailed task briefs in
  `docs/tasks/task-<ID>.md`"; `:54` "### Creating Tasks".
- `agents/scrum-master.md:6` `user-invocable: false`; `:23–25` (read, not ruled; see §8 O8) "Read and update
  `docs/tasks/active-tasks.md` as the canonical task board / Synchronize task entries with GitLab issues — create GitLab
  issues from new task entries".
- Precedent: `poc-skills-alignment-v1.md` §1.3 and E13. `AGENTS.md` § Task Protocol "constrain[s] the file and the act of
  creating a task, whoever performs it", and the skill's "Create task in `docs/tasks/active-tasks.md`" became "the skill
  proposes; the orchestrator creates".

| Field | Content |
|---|---|
| **Step A** | **Two readings of "create tasks".** **(i) A ledger act:** a row in `active-tasks.md` and a brief `task-<ID>.md`. That is the meaning of "create … tasks" in `AGENTS.md:18`, in `orchestrator.md:33–34, :54`, and in the Scrum Master's own text (`scrum-master:23–25`, "create GitLab issues from new task entries"). `AGENTS.md:18` is exclusive ("**Only** orchestrators"), and the Scrum Master is not an orchestrator (`scrum-master:6`). One action cannot satisfy both: Step A fails. **(ii) A drafting act:** the Scrum Master defines the tasks and the orchestrator writes the rows at item 9 (`:36`). Then the two clauses are jointly satisfiable and Step A holds. **I rule on reading (i)**, because the repository uses the same verb and noun for the ledger act everywhere else. **The conclusion does not depend on it:** under (i), P1 requires amending the command. Under (ii), ADR-008 Step A allows "at most a note stating the relationship where readers will see it", and the same edit is that note. The Scrum Master is a subagent that reads the clause at face value, and its own agent text already says it updates the ledger. |
| **Step B (P1)** | **Fires on reading (i).** (a) Quotable: `AGENTS.md:18` and `/new-feature:25`. (b) `AGENTS.md` § Task Protocol is "not scoped to a track, an agent or a file type" (`poc-skills-alignment-v1.md` §1.3). (c) Step A fails. (d) A command: ADR-007 branch 1. |
| **Step fired** | **B (P1)**, with the Step A note as the fallback. |
| **Amendment** | **Amend the command**, not `AGENTS.md`. Edit N-3 (§3): the Scrum Master **proposes** tasks and estimates effort, and the orchestrator **creates** them, citing `AGENTS.md` § Task Protocol. The Scrum Master keeps its breakdown and estimation role. Item 9 already assigns the ledger update to the executor, so it is unchanged. |
| **Not decided here** | `scrum-master.md:23–25` and `:27` have the same tension with `AGENTS.md:18`. That is P41 O2, parked in plan-112 §2 as a "content judgement", and plan-114 §4 keeps it parked. N-3 does not close it. |
| **Alternative the ADR cannot give** | If the user wants the Scrum Master to create task rows, `AGENTS.md:18` is what changes, and ADR-008 never amends a tier-1 file to match a lower one. That would be a separate instruction-change task and would also settle `scrum-master:23–25`. It is offered as option O5-C in §6, without a drafted edit. |
| **Maturity** | Not relied on (`/new-feature` and `scrum-master` are `stable`; irrelevant). |

## 3. Held edits (apply verbatim, only after the user decides)

Each Before is unique in its file, by reading the whole file unless noted **(unverified by grep)**. No edit relaxes a
check (ADR-007 §5). None is upward: N-1 to N-3 move commands toward `AGENTS.md`; C-1 to C-3 move one tier-1 file toward the
other tier-1 file and toward a recorded user decision, and exist only if the user chooses O1-A.

### 3.1 O1 (options O1-A for C-1 to C-3 and T-1; O1-C for T-1 only)

**C-1 — `implementation/knowledge/instructions/coding-standards.md:66–69`.** Anchor: the line beginning `All plan,
decision, and documentation artifacts follow`, which occurs once.

````
Before:
All plan, decision, and documentation artifacts follow the `<type>-vN.md` naming convention:
- `plan-v1.md`, `plan-v2.md`, `plan-v3.md`
- `decision-v1.md`, `decision-v2.md`
- `checkpoint-v1.md`, `checkpoint-v2.md`

After:
Immutable artifacts (`AGENTS.md` § Artifact Versioning) follow the `<type>-vN.md` naming convention:
- `requirements-v1.md`, `requirements-v2.md`
- `architecture-v1.md`, `architecture-v2.md`

Three artifact classes keep their own file names and take no `-vN` suffix:
- Plans: `plan-<ID>.md` (skill `plan-approve-execute` § File Location)
- Decision records: `ADR-<NNN>-<slug>.md` (`AGENTS.md` § Decision Log)
- Checkpoints: `checkpoint-<SEQ>-<phase>.md` (`AGENTS.md` § Checkpoint Protocol)

The rules and increment triggers below apply to the artifacts that take a `-vN` suffix only. A plan, a decision record or a checkpoint follows the source named beside it.
````

**C-2 — `coding-standards.md:75`.** Anchor: the full line, which occurs once.

````
Before:
- When referencing an artifact, always use the full versioned filename (e.g., `plan-v3.md`, not `plan.md`).

After:
- When referencing an artifact, always use the full versioned filename (e.g., `architecture-v3.md`, not `architecture.md`).
````

**C-3 — `coding-standards.md:78, :80–82`.** Anchor: the table header line through the checkpoint row. The heading `###
Artifact Types and Their Prefixes` (`:77`), the separator row (`:79`) and the `artifact-vN.md` row (`:83`) stay as they
are, so any citation of that heading still resolves.

````
Before:
| Prefix | Location | Purpose |
|--------|----------|---------|
| `plan-vN.md` | `docs/plans/` | Implementation plans |
| `decision-vN.md` | `docs/decisions/` | Architecture/design decisions |
| `checkpoint-vN.md` | `docs/checkpoints/` | Progress checkpoints |

After:
| File name | Location | Purpose |
|--------|----------|---------|
| `plan-<ID>.md` | `docs/plans/` | Implementation plans |
| `ADR-<NNN>-<slug>.md` | `docs/decisions/` | Architecture/design decisions |
| `checkpoint-<SEQ>-<phase>.md` | `docs/checkpoints/` | Progress checkpoints |
````

**T-1 — `docs/plans/_template.md:61` and `implementation/docs/plans/_template.md:61`** (one pair applied to two files; not
knowledge). Anchor: the full line, which occurs once in `docs/plans/_template.md` (whole file read) and, for the
`implementation/` copy, is its last line **(unverified for lines 1–55 of that copy)**.

````
Before:
- [ ] Plan locked; revisions create `plan-<slug>-v2.md`

After:
- [ ] Plan locked; a later revision is a new plan with the next free number (`plan-approve-execute` skill § File Location), and this plan is then marked `superseded` (§ Guidelines)
````

### 3.2 O2 (option O2-A)

**N-1 — `implementation/knowledge/commands/new-project.md:43`.** Anchor: the full line, which begins with **one TAB
character** (not spaces) and occurs once. Keep the TAB. Check the byte first, for example `grep -nP '^\t- Write checkpoint
to'`.

````
Before:
	- Write checkpoint to `docs/checkpoints/checkpoint-<phase>.md`

After:
	- Write checkpoint per `AGENTS.md` § Checkpoint Protocol: store at `docs/checkpoints/checkpoint-<SEQ>-<phase>.md`, with `<phase>` naming the phase
````

**N-2 — `new-project.md:51`.** Anchor: the full line, with four leading spaces, which occurs once.

````
Before:
    - Format: `<artifact-name>-v<major>.<minor>.md`

After:
    - Format: `<artifact-name>-v<N>.md`, per `AGENTS.md` § Artifact Versioning
````

### 3.3 O5 (option O5-A)

**N-3 — `implementation/knowledge/commands/new-feature.md:25`.** Anchor: the full line, which occurs once.

````
Before:
5. Have the Scrum Master create tasks and estimate effort

After:
5. Have the Scrum Master propose the tasks and estimate effort; the orchestrator creates them, per `AGENTS.md` § Task Protocol
````

### 3.4 The cosmetic (rides along; §7)

**K-1 — `implementation/knowledge/agents/poc-orchestrator.md:103`.** Anchor: the full line, which begins with **three
spaces** and occurs once **(unverified beyond the lines read, `:84–113`)**. The brief and plan-114 cite `:102`. At
`ec71a7d` the line is `:103`, because `:102` is the list item above it.

````
Before:
   - `TECHNICAL-DEBT.md` from `@technical-debt-narrator`

After:
  - `TECHNICAL-DEBT.md` from `@technical-debt-narrator`
````

**Totals.** There are 8 fences (C-1, C-2, C-3, T-1, N-1, N-2, N-3, K-1) and 9 applications, because T-1 is one pair applied
to two files. They touch 6 files: four knowledge files (`coding-standards`, `new-project`, `new-feature`,
`poc-orchestrator`) and the two templates.

## 4. Hit counts

- **Scope:** case-sensitive, fixed-string, per file, after every held edit to that file. "Lines" = `grep -cF`;
  "occurrences" = `grep -oF … | wc -l`.
- **Before** counts are at `ec71a7d`, by reading whole files **(unverified by grep)**. A "0 / 0" in the After column means
  the old wording must be gone.
- Every projection of a knowledge file below carries the same counts as its source. The `.claude` projection of
  `coding-standards` is the one I read: it drops the `maturity:` line, so its line numbers are one lower (`:79–81` for
  the three table rows). The other projections' line numbers are **(unverified)**.

| # | File | Phrase | Before (lines / occ.) | After | Edit |
|---|---|---|---|---|---|
| 1 | `instructions/coding-standards.md` | `plan-v` | 3 / 5 (`:67` x3, `:75`, `:80`) | **0 / 0** | C-1, C-2, C-3 |
| 2 | same | `decision-v` | 2 / 3 (`:68` x2, `:81`) | **0 / 0** | C-1, C-3 |
| 3 | same | `checkpoint-v` | 2 / 3 (`:69` x2, `:82`) | **0 / 0** | C-1, C-3 |
| 4 | same | `<type>-vN.md` | 2 / 2 (`:25`, `:66`) | 2 / 2 | anchor sentence survives |
| 5 | same | `plan-<ID>.md` | 0 / 0 | 2 / 2 | C-1, C-3 |
| 6 | same | `ADR-<NNN>-<slug>.md` | 0 / 0 | 2 / 2 | C-1, C-3 |
| 7 | same | `checkpoint-<SEQ>-<phase>.md` | 0 / 0 | 2 / 2 | C-1, C-3 |
| 8 | same | `§ File Location` | 0 / 0 | 1 / 1 | C-1 |
| 9 | same | `§ Decision Log` | 0 / 0 | 1 / 1 | C-1 |
| 10 | same | `§ Checkpoint Protocol` | 0 / 0 | 1 / 1 | C-1 |
| 11 | same | `§ Artifact Versioning` | 0 / 0 | 1 / 1 | C-1 |
| 12 | same | `architecture-v3.md` | 0 / 0 | 1 / 1 | C-2 |
| 13 | same | `\| Prefix \|` | 1 / 1 | **0 / 0** | C-3 |
| 14 | same | `\| File name \|` | 0 / 0 | 1 / 1 | C-3 |
| 15 | same | `### Artifact Types and Their Prefixes` | 1 / 1 | 1 / 1 | anchor survives |
| 16 | each `_template.md` (2 files) | `plan-<slug>-v2.md` | 1 / 1 | **0 / 0** | T-1 |
| 17 | each `_template.md` | `superseded` | 0 / 0 | 1 / 1 | T-1 |
| 18 | each `_template.md` | `§ File Location` | 1 / 1 (`:3`) | 2 / 2 | T-1 |
| 19 | `commands/new-project.md` | `checkpoint-<phase>` | 1 / 1 (`:43`) | **0 / 0** | N-1 |
| 20 | same | `checkpoint-<SEQ>-<phase>.md` | 0 / 0 | 1 / 1 | N-1 |
| 21 | same | `v<major>.<minor>` | 1 / 1 (`:51`) | **0 / 0** | N-2 |
| 22 | same | `-v<N>.md` | 0 / 0 | 1 / 1 | N-2 |
| 23 | same | `AGENTS.md` | 0 / 0 | 2 / 2 (`:43`, `:51`) | N-1, N-2 |
| 24 | same | `§ Checkpoint Protocol` / `§ Artifact Versioning` | 0 / 0 each | 1 / 1 each | N-1 / N-2 |
| 25 | same | `[CHECKPOINT]` (`:42`) | 1 / 1 | 1 / 1 | untouched |
| 26 | `commands/new-feature.md` | `Scrum Master create` | 1 / 1 (`:25`) | **0 / 0** | N-3 |
| 27 | same | `Scrum Master propose` | 0 / 0 | 1 / 1 | N-3 |
| 28 | same | `Scrum Master` | 1 / 1 | 1 / 1 | N-3 |
| 29 | same | `§ Task Protocol` | 0 / 0 | 1 / 1 | N-3 |
| 30 | same | `AGENTS.md` | 2 / 2 (`:30`, `:34`) | 3 / 3 | N-3 |
| 31 | `agents/poc-orchestrator.md` | line `   - \`TECHNICAL-DEBT.md\` from` (3 leading spaces) | 1 / 1 (`:103`) | **0 / 0** | K-1 |
| 32 | same | line `  - \`TECHNICAL-DEBT.md\` from` (2 leading spaces) | 0 / 0 | 1 / 1 | K-1 |

**Other sites that repeat a conflicting clause, with no edit proposed here.**

| Site | Repeats | Why left alone |
|---|---|---|
| `agents/scrum-master.md:23–25, :27` | The Scrum Master updates the ledger and turns task entries into issues (O5's neighbour) | P41 O2, parked by plan-114 §4 |
| `skills/checkpoint-protocol/SKILL.md:104`, `:173`, `:179` | A third checkpoint name, `checkpoint-<N>.md` and `checkpoint-001.md`, in a skill whose `:44` and `:50–51` say it matches `AGENTS.md` "verbatim" | A document that contradicts itself is outside ADR-008 (§ Scope); not one of the three conflicts. Recorded as O7 (§8) |
| `docs/artifacts/command-contract-resolution-v1.md`, `path-conventions-v1.md`, `-v2.md`, `-v3.md` | Quote the old clauses | Immutable artifacts (`AGENTS.md:24`) |
| `tests/golden/open/new-project-plan-doc-and-lifecycle-states/brief.md:65–66` | Quotes `<artifact-name>-v<major>.<minor>.md` as a clause "deliberately not touched" | Protected path; see §5.2 |
| `docs/wiki/**`, `README.md`, `docs/guides/**` | Unknown whether any page restates `/new-project` step 14 or 18, the `-vN` table, or the Scrum Master step | **(unverified)**; covered by the §5.4 greps |

## 5. Effects

### 5.1 Projected paths and root drift

The projection counts are inferred from `tests/_baselines/root-install-drift.json` and cross-checked: the eighth refresh
declared 52 paths for T596, which is 4 skills x 7 + 2 agents x 6 + 2 commands x 6. An agent or a command projects to 6
root paths, a skill to 7, and an instruction to 7 (the seven paths named in `AGENTS.md:74`; I read the first lines of all
seven and they exist).

| Source edit | Root-projection paths | Platform folders |
|---|---|---|
| `instructions/coding-standards.md` (C-1 to C-3) | **7** | `.github/instructions/coding-standards.instructions.md`, `.cursor/rules/coding-standards.mdc`, `.gemini/instructions/coding-standards.md`, `.opencode/instructions/coding-standards.md`, `.pi/instructions/coding-standards.md`, `.claude/rules/coding-standards.md`, `.clinerules/coding-standards.md` |
| `commands/new-project.md` (N-1, N-2) | **6** | `.claude/commands/new-project.md`, `.github/prompts/new-project.prompt.md`, `.cursor/commands/new-project.mdc`, `.gemini/commands/new-project.md`, `.opencode/commands/new-project.md`, `.pi/prompts/new-project.md` (the `.cursor` and `.gemini` file names are from the read tool's near-miss hints, not a successful read) |
| `commands/new-feature.md` (N-3) | **6** | the same pattern with `new-feature` |
| `agents/poc-orchestrator.md` (K-1, the cosmetic) | **6** | the same six agent folders |
| Both `_template.md` files (T-1) | **0** (not knowledge; the T596 arithmetic left no room for them) | `docs/plans/_template.md` is authored at the root; `implementation/docs/plans/_template.md` is **(unverified)** |
| **Total if everything is applied** | **25** (19 without K-1) | |

- **Regenerate:** `node implementation/scripts/sync.mjs --root implementation`, then `python3
  implementation/scripts/generate-registry.py`, each followed by `--check`. `implementation/registry/index.json` changes for
  the 4 entries (checksums). `implementation/registry/summary.md` should not change, since no `maturity:` changes
  **(unverified)**.
- **Mirrors.** `sync.mjs` also writes the same files under `implementation/.<platform>/`. Whether they are tracked is
  **(unverified)**. They are not root drift.
- **Root drift.** Declare exactly the paths `python3 -m tests.functional.test_root_install_parity --print-drift` prints in
  `tests/_baselines/root-install-drift.json`. Do not refresh the repo root; that is a separate, user-approved
  `--projections-only` refresh (the previous one was the tenth).
- **Subsets.** O1-A alone: 7. O2-A alone: 6. O5-A alone: 6. Any subset adds the matching rows only.

### 5.2 Golden and test coupling

| Item | Coupling | Effect |
|---|---|---|
| `new-project-plan-doc-and-lifecycle-states` | `brief.md:65–69` names step 18's `<artifact-name>-v<major>.<minor>.md` and step 14's `[CHECKPOINT]` line as "deliberately not touched". `expect.py` reads only the plan file and the ledger's status column | After N-2 the quoted format (`brief.md:65–66`) is **stale prose**. The statement that it is "not touched" stays true. **Result unchanged, fixture unchanged.** Refreshing the sentence needs a file-scoped `protected-paths-v1.md` §5 grant |
| `new-feature-checkpoint-line-compliant` | Asserts `checkpoint-<SEQ>-<phase>.md` with a numeric `<SEQ>` and the five elements | **Agrees with O1-A, O2-A and the `AGENTS.md` form.** Nothing changes. Under O1-B it would need re-purposing |
| `new-feature-plan-doc-compliant` | Quotes `/new-feature` step 1 only | None |
| `new-feature-real-checkpoint-format-drift` | Quotes step 7 only (`path-conventions-v1.md` §6.1, **not re-read**) | None |
| Any open case quoting `/new-feature` step 5 or `coding-standards` | None found in the cases I read | **(unverified)** beyond them |
| **Held-out cases** | I did not open `tests/golden/held-out/` | **Unknown.** The orchestrator, under its read/audit exception, should grep that tree for `checkpoint-<phase>`, `v<major>.<minor>` and `Scrum Master create` before the implementing task is dispatched |
| Non-golden tests | I could not search `tests/` | **Unknown whether any test asserts a Before string.** §5.4 lists the greps. `test_root_install_parity` is the one known coupling (§5.1) |

### 5.3 Baseline and grant

- **Protected-path grant:** **none needed** for any held edit. No edit touches `tests/golden/**` or `scripts/scorecard.py`.
- **Evaluator-hash baseline:** **none needed.** `scripts/scorecard.py --check` stays at the current baseline (v20 per the
  last user approval, as the orchestrator's notes state it **(unverified)**). The implementing task reads the current
  figures from the repo, not from this document.
- **Only if the user also wants the stale golden prose refreshed** (the `new-project-plan-doc-and-lifecycle-states`
  sentence above): a file-scoped §5 grant and a user-authorized next baseline, in the same shape as FU-P32-G. I do not
  recommend doing that now. It changes no result.
- `check-maturity.py --root implementation` should still report 0 failing, and `python3 docs/tasks/validate-tasks.py`
  should still pass (neither reads these strings) **(unverified)**.

### 5.4 Pre-flight greps for the implementing task (not run here; I have no shell)

Run and report, then stop if a non-golden test asserts a Before string. Report held-out hits to the orchestrator only,
without naming a case.

- `grep -rnF -e 'plan-v' -e 'decision-v' -e 'checkpoint-v' implementation/ docs/plans/_template.md docs/wiki docs/guides README.md tests/ --include='*.md' --include='*.py' --include='*.mjs' --include='*.json' --include='*.yaml'`
- `grep -rnF -e 'checkpoint-<phase>' -e 'v<major>.<minor>' -e 'Scrum Master create' implementation/ docs/wiki docs/guides tests/`
- `grep -rnF 'plan-<slug>-v2' implementation/ docs/plans/_template.md tests/`
- Compare each count with §4, and the `Before` match counts with the "occurs once" claims in §3.

## 6. The user question (one round)

**Q-T607 — The three `AGENTS.md` naming conflicts.**

**Answer with one letter per item, or say "all recommended". Nothing is applied before you answer.**

**Item O1 — `coding-standards` puts `-vN` on plan, decision and checkpoint file names, against `AGENTS.md:27` and `:33`** (a conflict inside tier 1, which ADR-008 does not rank)

| Option | What changes | Consequences |
|---|---|---|
| **O1-A (Recommended)** | `coding-standards` takes C-1, C-2, C-3: `-vN` applies to the immutable `docs/artifacts` types, and plans, decision records and checkpoints use the names `AGENTS.md` and the plan skill already give them. Both plan templates take T-1 | Edits one tier-1 file (an instruction-change task), 7 root-drift paths. Removes the only text that tells a reader to write `checkpoint-v1.md` or `decision-v1.md`. Agrees with `checkpoint-protocol:44`, the checkpoint and ADR template headers, the golden `checkpoint-<SEQ>-<phase>` assertion in `new-feature-checkpoint-line-compliant`, and Q-P32a. No golden file changes |
| **O1-B** | `AGENTS.md:27` and `:33` are rewritten to the `-vN` forms; the skills and templates follow | Edits `AGENTS.md` and every projection of it. Every real checkpoint and ADR (counts **unverified**) becomes non-conforming, and they cannot be renamed (`AGENTS.md:24`). `new-feature-checkpoint-line-compliant` would need re-purposing under a grant and a new baseline. **Not recommended** |
| **O1-C** | Only T-1 (the two templates). `coding-standards` stays as it is and the conflict stays parked, or you read `-vN` as a suffix inside `AGENTS.md`'s open slot (the alternative reading recorded in §2.1 O1-a) | No tier-1 edit, 0 root-drift paths. The table keeps printing `checkpoint-v1.md`, `decision-v1.md` and `plan-v1.md` as literal examples |
| **O1-D** | Hold all of O1, including the templates | Nothing changes. The template revision rule keeps disagreeing with the plan skill |

**Item O2 — `/new-project:43` and `:51` against `AGENTS.md:27` and `:22`** (decided by ADR-008 Step B, so this is approval to apply)

| Option | What changes | Consequences |
|---|---|---|
| **O2-A (Recommended)** | N-1 and N-2: the checkpoint path and the artifact version format are written in the forms `/new-poc:46` and `/new-feature:34` already carry, citing `AGENTS.md` | One stable command, 6 root-drift paths. Moves the command toward `AGENTS.md`, so no check is relaxed. One golden brief sentence goes stale, result unchanged |
| **O2-B** | Hold | The command keeps `checkpoint-<phase>.md` and `-v<major>.<minor>.md`, both of which disagree with `AGENTS.md`. An agent that follows the command writes files under a second convention |

**Item O5 — `/new-feature:25` "Have the Scrum Master create tasks" against `AGENTS.md:18`** (decided by ADR-008 Step B, so this is approval to apply)

| Option | What changes | Consequences |
|---|---|---|
| **O5-A (Recommended)** | N-3: the Scrum Master proposes the tasks and the estimates; the orchestrator creates them, per `AGENTS.md` § Task Protocol | One stable command, 6 root-drift paths. Same model as the T570 ruling. `scrum-master.md:23–25` is not changed (P41 O2 stays parked) |
| **O5-B** | Hold | The command keeps telling a subagent to create tasks |
| **O5-C** | Keep the Scrum Master creating tasks and change `AGENTS.md:18` to allow it | A tier-1 change in a separate instruction-change task; also settles `scrum-master:23–25`. I have drafted no edit for it. It contradicts `orchestrator.md:33–34` and `AGENTS.md:6` unless those are changed too |

**Cosmetic (no answer needed).** K-1 rides along with whichever of the above you approve, as plan-114 §3 says, and adds 6
root-drift paths. If you approve nothing, it waits for the next change to that file.

**Recommendation: O1-A, O2-A, O5-A ("all recommended").** One implementation task for all four knowledge files and both
templates keeps it to a single sync, registry run and drift declaration (25 paths with K-1).

**Why I am recommending, not ruling, on O1.** ADR-008 does not rank `AGENTS.md` against a stable instruction, and neither
document concedes the subject. O1-A follows the document that every other file in the repository agrees with, and it
leaves `AGENTS.md` untouched, but that is a consideration for your choice and not authority ("Popularity is not authority",
ADR-007).

## 7. The cosmetic carried from plan-114 §3 (P33 O4)

- **What.** In `implementation/knowledge/agents/poc-orchestrator.md`, the list item "`TECHNICAL-DEBT.md` from
  `@technical-debt-narrator`" is indented with three spaces, and its sibling items at `:102`, `:104` and `:105` use two.
  At `ec71a7d` it is on `:103`; the brief and plan-114 cite `:102`.
- **Why it is cosmetic.** In CommonMark a nested list item indented by two to five spaces under a two-space parent renders
  at the same level, so no rule and no check changes. It is a source-tidiness defect only.
- **Cost of fixing it alone.** It edits a knowledge file, so it forces a regenerate and 6 root-drift paths. That is why
  plan-112 §2 parked it ("it waits for the next change to that file").
- **Disposition.** It **rides along with the implementation of this decision** (K-1, §3.4). If the user approves none of
  O1, O2 and O5, it stays parked for the next change to `poc-orchestrator.md`. It does not need a separate ruling and
  carries no golden coupling that I know of: `new-poc-plan-hypothesis-format` quotes `:25`, not `:103`
  (`path-conventions-v3.md` §5).

## 8. Observations (new or restated; not ruled; the other plan-112 §2 notes stay parked, as the user decided)

- **O7 (new): `checkpoint-protocol/SKILL.md` has a third checkpoint name.** `:44` and `:50–51` say
  `checkpoint-<SEQ>-<phase>.md` and "matches `AGENTS.md` … verbatim", but `:104` says "Write the file to
  `docs/checkpoints/checkpoint-<N>.md`" and the examples at `:173` and `:179` are `checkpoint-001.md` and
  `checkpoint-003.md`. A document that contradicts itself is outside ADR-008 (§ Scope, same-file coherence). It is a
  candidate for the next change to that skill, with the same cite-`AGENTS.md` remedy as N-1. Suggested trigger: any task
  touching `checkpoint-protocol`.
- **O8 (restated): `scrum-master.md:23–25, :27` against `AGENTS.md:18`.** This is P41 O2. N-3 changes the command's side
  only.
- **O9 (new): the `[CHECKPOINT]` one-line marker.** `/new-project:42` and `/new-poc:45` keep it beside the `AGENTS.md`
  path, and I ruled it a compatible rendering. `command-contract-resolution-v1.md` §3 row B reached a stricter result for
  `/new-feature` step 7 because that step replaced the document with the marker. If the user wants the marker retired
  everywhere, that is a separate command decision.
- **Still parked, per the user's "C":** CI's third `release-notes.md` (P32 O6), P41 O2/O3/O4, and P33 O1, O2, O5 and O6.

## 9. Still unverified

1. The worktree commit `ec71a7d` (stated by the orchestrator).
2. Every count in §4 and every "occurs once" claim in §3, all by reading, not `grep`. In particular
   `implementation/docs/plans/_template.md` lines 1–55 and `poc-orchestrator.md` outside `:84–113`.
3. The projected and mirrored paths in §5.1, apart from the `coding-standards` projections (all seven read) and
   `.claude`, `.github`, `.opencode`, `.pi` command files (read). The `.cursor` and `.gemini` command file names and the
   `.cline` command projection (none found) rest on the read tool's hints.
4. That no held-out case, and no test outside the golden cases I read, asserts any Before string.
5. That the other three stable instructions declare no precedence over `AGENTS.md` on artifact naming (only
   `coding-standards`' Rails was read).
6. That no command other than the six read (`new-project`, `new-feature`, `new-poc`, `plan`, `batch`, `sprint-status`)
   says "Have the Scrum Master create".
7. That `implementation/registry/summary.md` and the maturity checks are unaffected.
8. The exact byte at the start of `new-project.md:43` (a TAB) and `:51` (four spaces), as the read tool displays them.

## 10. Handoff package for the implementing task (specification; no task is created here)

| Field | Content |
|---|---|
| `task_id` | To be assigned by the orchestrator, for example a mechanical-tier follow-up to `T607` |
| `definition` | Apply, verbatim, only the fences the user approves in Q-T607 (§3), then regenerate and declare root drift |
| `constraints` | Never reword. Apply each pair by exact string replacement and assert each Before matches exactly once (and the TAB in N-1). Stop and report if an anchor is missing or not unique. Do not edit `AGENTS.md`, any other instruction, `scrum-master.md`, `checkpoint-protocol`, any file under `tests/golden/**`, `scripts/`, `.env*`, or any derived platform folder by hand. Do not refresh the repo root. Do not push, and never run any merge or approve call |
| `depends_on` | The user's answer to Q-T607 |
| `input_artifacts` | `naming-conflicts-ruling-v1.md` (this file) as the single implementation input |
| `expected_outputs` | The edited files; regenerated mirrors and `implementation/registry/index.json`; `tests/_baselines/root-install-drift.json` with exactly the printed paths; a report with every §4 count as lines and occurrences |
| `blocker_policy` | `AGENTS.md` § Blocker Protocol: report type and severity. A non-golden test that asserts a Before string, or a held-out hit, is a `dependency` blocker to the orchestrator |

Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`,
`scripts/scorecard.py --check` (equal to the current baseline), `python3 docs/tasks/validate-tasks.py`,
`python3 tests/run.py` with output redirected to a file. Confirm byte-unchanged: `AGENTS.md`, every other instruction,
`/plan`, `/batch`, `/new-poc`, `scrum-master.md`, `checkpoint-protocol`, every script, and `tests/golden/**`.

## 11. Summary

| Item | Subject | Settled by | Outcome | Edits | User decision? |
|---|---|---|---|---|---|
| O1-a | Checkpoint file name | none (tier 1 against tier 1) | Escalated, P5; O1-A recommended | C-1, C-3 | **Yes** |
| O1-b | Decision-record file name | none (tier 1 against tier 1) | Escalated, P5; O1-A recommended | C-1, C-3 | **Yes** |
| O1-c | Plan file name and "never overwrite" | The user's Q-P32a for the name; P5 for the tier-1 edit | The skill and Q-P32a stand; escalated with O1 | C-1, C-2, C-3 | **Yes** |
| O1-d | Template revision rule | Q-P32a and the template's own `:3` pointer | Templates yield to the skill | T-1 | Approval only |
| O2-a | `/new-project` checkpoint path | ADR-008 Step B (ADR-007 branch 1) | Amend the command | N-1 | Approval only |
| O2-b | `/new-project` artifact version format | ADR-008 Step B | Amend the command | N-2 | Approval only |
| O5 | Who creates tasks | ADR-008 Step B (with the Step A note as fallback) | Amend the command: propose / create | N-3 | Approval only |
| Cosmetic | `poc-orchestrator` list indent | plan-114 §3 | Rides along | K-1 | None |

- **Maturity, corpus counts, majority practice and golden-coupling convenience** were relied on nowhere as authority.
  The agreement of other files with `AGENTS.md` is offered only as a consideration for the user's O1 choice.
- **No edit is applied, and none is upward or relaxing.** The only tier-1 edits (C-1 to C-3) exist under O1-A and need the
  user's answer first.
- **Golden:** no fixture and no result changes. One brief sentence goes stale (O2-b), and refreshing it is optional and
  needs a grant and a new baseline.
- **Blockers:** none for this task. O1 is a P5 escalation delivered as Q-T607 (type `unclear_requirements`, severity
  `minor`: nothing is blocked while it is open).
