# Artifact: remaining-observations-ruling-v1.md

> Filename: `remaining-observations-ruling-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer agent**: solution-architect
- **Task**: T621 (P1, judgment tier, decision only)
- **Created**: 2026-10-09
- **Based on:**
  - `docs/tasks/task-T621.md` (the brief, authoritative);
  - `docs/plans/plan-120-release-v8-readiness.md` (workstream D);
  - `docs/plans/plan-112-parked-note-cleanup.md` §2 (the parked list);
  - `docs/artifacts/remaining-verdict-renderings-v1.md` §8.4 O4 and §9 G9 (P41 O4);
  - `docs/artifacts/poc-guidelines-owner-items-v2.md` §7 (P33 O1, O2, O5, O6; E-A2, E-B1, E-C1, E-D1, E-O3 are applied);
  - `docs/artifacts/task-protocol-observations-ruling-v1.md` §2.7 (O-8) and `docs/artifacts/task-protocol-skill-conflicts-ruling-v1.md` (read to line 574 of 824; the rest not re-read);
  - `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted), `docs/decisions/ADR-007-command-contract-authority.md` (Accepted, read to line 130), `AGENTS.md`;
  - the user's decisions of 2026-10-09 as the brief relays them, verbatim: "1. A  2. A  3. A  4. approving baseline v21 - plan re-evaluation and steps to bring them out of experimental  5. C  6 B". Point 5 is "known residuals = fix all first". I honor it and the earlier recorded decisions (amend the agent, skill or command toward `AGENTS.md`; Step A readings need no edit unless a recommended note is approved; do not re-litigate) as precedent.
- **Supersedes**: none (first version).
- **Decision references**: ADR-008 Step A (P3a), Step B (P1), Step C (P2), D2, D3, D4, D5, P4, P5; ADR-007 §5 (never relax a check). No new ADR is minted.
- **Status of every edit in this document**: **held for the user. Nothing is applied.** The only other file changed by this task is the `**Status:**` line of `task-T621.md`.

## 0. Method and limits

- **Commit.** The orchestrator states the worktree is on `develop` `5e07a6b` **(unverified: no shell, no `git`)**. Many files changed in T608 to T618, so I re-read every live line below from the source files under `implementation/knowledge/`. I trusted no earlier line number. The shifts that matter: `orchestrator.md:205` and `:249` are unchanged; `technical-debt-tracking` is now `:16–21` (Categories), `:45–49` (Step 1), `:147` (scorecard sentence) and `:162–170` (Summary by Category); `poc-guidelines.md` is `:131–135` (table), `:148` (Rule 1), `:152` (Rule 5), `:154–155` (register); `technical-debt-narrator.md` is `:14`, `:41`; `commands/bug-report.md:54` is unchanged.
- **No shell and no grep tool.** Every count in §4 comes from reading whole files and is **(unverified by grep)**. §7.2 lists the greps the implementing task must run first. §9 collects every unverified claim.
- **Read in full (source):** `AGENTS.md:1–60`; agents `orchestrator`, `scrum-master`, `poc-orchestrator`, `technical-debt-narrator`, `evaluation-agent`; skills `validation-gates`, `technical-debt-tracking`, `poc-evaluation`, `gitlab-management`, and `rapid-prototyping:1–110`; commands `evaluate-poc`, `bug-report`; instruction `poc-guidelines`; `tests/_baselines/root-install-drift.json:1–35`. The T615 and T617 artifacts were read in part (see Based on).
- **Golden.** I opened only `tests/golden/open/` case directories: the `brief.md` of `evaluate-poc-verdict-debt-reconciliation`, `bug-report-severity-priority-ledger-row` and `new-poc-plan-hypothesis-format` (from line 55), and the first 70 lines of the second one's `expect.py`. Every golden case named here has a `tests/golden/open/` directory. **I never opened `tests/golden/held-out/`, so held-out coupling is unknown and was not checked.** To confirm which cases are open I read `tests/golden/_manifest-t411.md`, a file outside `held-out/`; I use nothing from it about a held-out case, and I name none.
- **Secrets.** I read no `.env*`, credential or key file. I edited nothing under `.claude/`, `.github/` or any derived platform folder, and nothing outside this artifact and the brief's `**Status:**` line.
- **Encoding.** `§` is U+00A7, `—` is U+2014, `→` is U+2192. Each four-backtick fence holds one Before/After pair; inner single and triple backticks are literal. Apply each edit by its Before text, never by line number. Match every single-line Before as a whole line (`grep -cxF`).
- **Scope-gaming guard (ADR-008 § Risks).** These observations were recorded on 2026-10-08 (`plan-112` §2) and 2026-10-09 (T617). The scope sentences relied on below are the skills' and agents' descriptions and Rails, which T570 (`poc-skills-alignment-v1.md` §10.2) already approved as placing `technical-debt-tracking` inside `poc-guidelines.md`'s reach. I cannot diff history to prove none was added in the same change as this ruling **(unverified)**.
- **Maturity.** I relied on no `maturity:` value (P4). For the record: `orchestrator`, `technical-debt-tracking`, `poc-evaluation` and `gitlab-management` are `experimental`; `technical-debt-narrator`, `poc-orchestrator`, `scrum-master`, `/evaluate-poc`, `/bug-report` and `poc-guidelines` are `stable`. None of that decides any step.

## 1. Disposition table

| Item | Subject (D3) | Step fired | Disposition | Held edit | Tier-1 conflict? |
|---|---|---|---|---|---|
| **P41 O4** | Timing of the Implementation gate: `orchestrator.md:205` "(after core implementation)" against `:249` "After each completion" and `validation-gates:26` "After code complete, before merge" | **A holds** (same file; G9 reconfirmed) | **Optional note-level edit, recommended** (the user chose to fix every residual); declining is also valid | O4-a | No |
| **P33 O1** | The `Category` values of the scorecard's Debt Inventory: the instruction's example rows (`Validation`, `Reliability`) against the skill's closed set (`technical-debt-tracking:16–21, :84`) | **A holds** (an open column specialised by a closed set, D4) | **Optional note-level edit, recommended**, on the skill | O1-a (O1-b is the tier-1 alternative) | No: the other side is a skill. Editing the instruction's example is a tier-1 change and is the user's call |
| **P33 O2** | The file name of the narrator's two deliverables: `technical-debt-narrator.md:41` "Name output artifacts: `<type>-vN.md`" against `poc-guidelines.md` naming `POC-DEBT-SCORECARD.md` and `TECHNICAL-DEBT.md` | **B (P1)** (Step A fails on the literal text; the conclusion does not depend on it) | **Rule: amend the agent** | O2-a | No (`AGENTS.md:21–24` does not reach them, §2.3) |
| **P33 O5** | (a) The scan scope: "in the codebase" (Rule 1) against `.` (Step 1). (b) The set of files scanned: Rule 1's "every" against Step 1's nine-extension filter | (a) **A holds**; (b) **B (P1)** | (a) note-level scope definition; (b) **rule: amend the skill** | O5-a (one fence carries both); O5-c is a variant | No |
| **P33 O6** | The source of the `/evaluate-poc` Debt Summary severities | **A holds**; the form falls under **C (P2)** | **Optional note-level edit, recommended**, on `poc-evaluation`, scoped to `/evaluate-poc`; the command is unchanged | O6-a | No |
| **O-8** | A mapping from `priority::critical/high/medium/low` to `P0`/`P1`/`P2` | **A holds** (no conflict; a missing definition) | **Drafted mapping**, in `gitlab-management` § Label Conventions; **needs the user's confirmation** | O8-a | No |

Counts: 1 rule with a conflict on the literal text (O2); 1 split (O5: scope is a note, the filter is a rule); 4 Step A items with a recommended note (O4, O1, O6, O-8's drafted table). **No conflict is inside tier 1, so nothing escalates under P5.** Two options change a tier-1 file instead (A3 and the tier-1 alternative of O1); ADR-008 P1 never does that on its own, so they sit in the question as the user's prerogative only.

## 2. D5 records

### 2.1 P41 O4: the Implementation gate's timing (`orchestrator.md`)

**Verbatim clauses (live).**
- `orchestrator.md:205` "**IMPLEMENTATION GATE** (after core implementation):" and `:206` "- Delegate to `@tech-lead`: "Review implementation against architecture-v1.md. Produce VERDICT.""
- `orchestrator.md:249` "3. After each completion, run the **Implementation Gate**: delegate to **@tech-lead** for code review (see § Validation Gates)"; `:250` "4. Run **Integration Gate** after all parallel work completes"
- `validation-gates/SKILL.md:26` "| **Implementation** | Tech Lead | After code complete, before merge | Code quality, test coverage, convention adherence |"; `:15` "- Before merging implementation work (implementation gate)"
- Tier 1: `AGENTS.md:51–55` fixes verdict values and who creates fix tasks; it states no gate timing.

**Subject (D3).** The point at which the Implementation gate is run: once at the end of core implementation, or once per completed implementation item.

| Field | Content |
|---|---|
| **Step A** | **Holds.** `:205` says "(after core implementation)", not "once" or "only after". `:249` says "After each completion", not "only". An orchestrator that runs the gate after each completed item runs a gate that has run after core implementation as well, because the last item completes core implementation; both clauses and `validation-gates:15, :26` are obeyed. No clause is exclusive and no verdict has two values. **Counter-reading, recorded:** a reader who takes `:205` as a single phase-end gate will skip the per-item reviews `:249` asks for. Since T585 `:249` points the reader at `:205`, which makes the looser wording more visible (`remaining-verdict-renderings-v1.md` §9 G9, O4). It is a hazard, not a contradiction. |
| **Step fired** | **A.** The matter is also inside one file (ADR-008 § Scope: same-file coherence), so no ranking is needed. |
| **Amendment** | Optional and note-level: O4-a rewrites the parenthesis in `:205` so that it states the timing `:249` and `validation-gates:26` state, and names the skill. Declining it leaves a reading that is valid and matches the G9 precedent ("noted only"). |
| **Declared-scope text** | Not needed for a Step A ruling. |
| **Maturity** | Not relied on. |

### 2.2 P33 O1: the scorecard's `Category` values

**Verbatim clauses (live).**
- `poc-guidelines.md:131–135` "| # | File | Line | Category | Description | Severity | Production Effort |" with the rows "| 1 | src/db.py | 12 | Security | …", "| 2 | src/api.py | 34 | Validation | Hand-written inline input validation instead of the shared schema layer | Critical | …", "| 3 | src/sync.py | 56 | Reliability | No retry logic | Medium | …". Its `:118` "Create a `POC-DEBT-SCORECARD.md` file in the PoC root with this structure:". The instruction states no value set for `Category`.
- `technical-debt-tracking/SKILL.md:16–21` "## Categories" / "- Security" / "- Architecture" / "- Testing" / "- Data quality" / "- Operations"; `:56` "**Category** (infer from context: Security, Architecture, Testing, Data quality, Operations)"; `:84` "- **Category:** Security | Architecture | Testing | Data quality | Operations"; `:147` "Write it in the structure `poc-guidelines.md` § Debt Scorecard › Scorecard Format defines … Fill the Debt Inventory's `Severity` column with each item's debt-ledger severity …"; `:162–170` "## Summary by Category" with exactly those five rows.

**Subject (D3).** The values of the `Category` column in the scorecard's Debt Inventory.

| Field | Content |
|---|---|
| **Step A** | **Holds.** `poc-guidelines.md` fixes the column and its position, and gives no value set. The skill fixes a closed set for the ledger item's `Category` (`:84`, P3a step 2) and builds the scorecard from the ledger (`:147`, `:70`). An inventory whose Category cells come from the five satisfies the instruction's structure, because the example values sit in a row of a template the instruction introduces with "with this structure"; they are not a value set (D4: the skill "fills a slot the other leaves open" and "uses values that nest inside"). One-value test: one debt item has one Category, taken from the ledger. **The hazard:** an agent that copies `Validation` or `Reliability` from the instruction's example into the inventory produces a row that no row of `## Summary by Category` (`:162–170`) counts. v2 §7 recorded the same reading: "a specialisation of an open column, not a conflict". |
| **Step fired** | **A.** No ranking. Not Step B: nothing in the instruction contradicts the closed set. |
| **Amendment** | **O1-a (recommended):** one sentence in the skill's scorecard paragraph (`:147`, the same sentence E-B1-b edited) says that the inventory's Category is the ledger Category, one of the five, and that the instruction's example values are illustrative. **O1-b (alternative, tier-1 text):** change the two example Categories in `poc-guidelines.md` to values from the skill's set (`Validation` → `Security`, `Reliability` → `Operations`). I proposed `Security` for row 2 because the instruction's own `Allowed Shortcuts` calls hand-written validation a simplified security control, and the row is graded `Critical`; `Operations` for row 3 fits a missing retry. These are choices, not rulings. O1-b edits a stable instruction, which ADR-008 P1 never does to match a lower document, so it needs the user's decision (A3). |
| **Declared-scope text** | Not needed for Step A. |
| **Maturity** | Not relied on. |

### 2.3 P33 O2: names of the narrator's deliverables

**Verbatim clauses (live).**
- `technical-debt-narrator.md:41` "- Name output artifacts: `<type>-vN.md`" (under `### Artifact References`, `:39–42`). The same file `:14` "- TECHNICAL-DEBT.md with categorized debt: the PoC's narrative debt register (`poc-guidelines.md`). It explains the items that `POC-DEBT-SCORECARD.md` inventories …" and `:17` "- Technical Debt Scorecard with severity, effort, risk, and ownership".
- `poc-guidelines.md:118` "Create a `POC-DEBT-SCORECARD.md` file in the PoC root with this structure:" and `:154–155` "## Narrative Debt Register (`TECHNICAL-DEBT.md`) / Every PoC must also produce `TECHNICAL-DEBT.md` … `@technical-debt-narrator` writes it at the PoC's Debt Narration step (`poc-orchestrator.md` § PoC Workflow)". `poc-orchestrator.md:58` "12. **Debt Narration** — `@technical-debt-narrator`: TECHNICAL-DEBT.md + scorecard".
- Tier 1: `AGENTS.md:22` "- Immutable artifacts: `<type>-v<N>.md` (e.g. `requirements-v1.md`, `architecture-v1.md`)"; `:24` "- Revisions create new versions, never overwrite."
- The same boilerplate sentence appears in `evaluation-agent.md:44` and (as "Name your output artifacts following the versioning convention: `<type>-vN.md`") in `scrum-master.md:111`. For those agents the sentence is true; the other PoC specialists are **(unverified: not read)**.

**Subject (D3).** The file name of the PoC's scorecard and narrative register.

| Field | Content |
|---|---|
| **Step A** | **Fails on the literal text.** `:41` is an unqualified imperative for the narrator's output artifacts, and the narrator is the agent that writes both files (`poc-orchestrator.md:58`; `:14`, `:17`). The instruction names two files, so for one deliverable the instruction computes `POC-DEBT-SCORECARD.md` and `:41` computes a `<type>-vN.md` name. **Rescue reading (ii), recorded:** read `:41` as boilerplate that covers only artifacts no instruction names. I rule on the literal reading, because a subagent reads the line at face value, and **the conclusion does not depend on it**: under (ii) the held edit is the note Step A permits. The same file also contradicts itself, since `:14` names `TECHNICAL-DEBT.md` (same-file coherence points the same way). |
| **Does `AGENTS.md` reach the files?** | **No, so this is not a tier-1 conflict.** `AGENTS.md:22` governs "Immutable artifacts" and `:24` their revisions. No text calls the scorecard or the register an immutable artifact. `AGENTS.md` itself names unversioned files (`active-tasks.md`, `task-<ID>.md`, `checkpoint-<SEQ>-<phase>.md`, `ADR-<NNN>-<slug>.md`), so the versioned form is not universal. **Counter-reading, recorded:** a reader who takes `:24` as covering every deliverable would find `poc-guidelines.md` in conflict with `AGENTS.md`, which would be a tier-1 conflict for P5. I do not take it, because the sentence is scoped by "Immutable artifacts" and names no PoC deliverable (D2: each `AGENTS.md` sentence reaches what it names). If you read it the other way, say so and I will escalate it. |
| **Step B (P1)** | **Fires.** (a) Quotable: `poc-guidelines.md:118`, `:154` and `technical-debt-narrator.md:41`, above. (b) Reach: `poc-guidelines.md` Rails (`:10–13`) apply "whenever `poc-orchestrator` or a PoC specialist agent begins hypothesis-driven exploratory work"; the narrator's description is "document shortcuts and debt introduced during PoC work", and `:14` cites the instruction. The instruction's naming of the two files is part of its Scorecard and Register sections, which `poc-orchestrator.md:93–96` calls "defined in `poc-guidelines.md`". (c) Step A fails on reading (i). (d) The other document is an agent. |
| **Step fired** | **B (P1).** |
| **Amendment** | **O2-a:** `:41` excepts the two named files and cites the instruction. The versioned form stays for every other output artifact (for example `docs/artifacts/debt-ledger-v{N}.md`). It cites the instruction and does not restate its rules (P1 Remedy). I claim no location for `TECHNICAL-DEBT.md`, because no document states one (N-2). |
| **Not changed** | `evaluation-agent:44`, `scrum-master:111`: the sentence is true for their outputs. |
| **Maturity** | Not relied on. |

### 2.4 P33 O5: the scan scope for `POC-DEBT` tags

**Verbatim clauses (live).**
- `poc-guidelines.md:148` "1. The scorecard must account for **every** `POC-DEBT` tag in the codebase"; `:116` (E-A2) "The PoC root is the top-level directory of the PoC's code: the repository root when the PoC has its own repository, otherwise the directory that the PoC plan … names as the PoC root."
- `technical-debt-tracking/SKILL.md:43` "This skill is responsible for scanning codebases for `POC-DEBT` tags placed by the rapid-prototyping skill"; `:45–49`:
  `**Step 1: Discover all debt tags**` / "# Scan all project files for POC-DEBT tags" / `grep -rn "POC-DEBT:" --include="*.py" --include="*.ts" --include="*.js" --include="*.yaml" --include="*.yml" --include="*.md" --include="*.json" --include="*.html" --include="*.css" .`
  `:14` "If the scorecard does not account for every `POC-DEBT` tag found in Step 1, it is not finalized"; `:70` "Every `POC-DEBT` tag found in Step 1 must appear in the scorecard's Debt Inventory (`poc-guidelines.md` Scorecard Rule 1). The ledger is this skill's working register and does not substitute for the scorecard."
- `rapid-prototyping/SKILL.md:41` "For architectural shortcuts, place the tag in the relevant architecture or design document."; `:73` "The technical-debt-tracking skill scans for these tags during PoC evaluation."

**Two subjects, so two rulings (D3).** (a) The directory tree scanned. (b) The set of files scanned within it.

| Sub-item | Step A | Step fired | Amendment |
|---|---|---|---|
| **5a. Scope** | **Holds.** "In the codebase" is open; E-A2 defines the PoC root as the top directory "of the PoC's code", so the codebase of a PoC is the tree under its root. `.` is the working directory, which equals the PoC root when the agent runs there. Both can be obeyed by scanning the PoC root. The hazard: when the PoC is a subdirectory of a host repository, `.` at the repository root scans the host's files, and any file that quotes the tag format (this repository's instructions, tests and artifacts) returns hits that belong to no PoC. | **A**, note-level. | **O5-a** names the PoC root as the scope. Variants: **O5-c** (PoC root plus paths its plan lists) and the whole-checkout reading (option B3) are in §6. |
| **5b. Files scanned** | **Fails.** Rule 1 requires the scorecard to account for **every** tag. The skill's Failure mode (`:14`) and `:70` bind the scorecard only to the tags "found in Step 1", and Step 1 finds a subset: only nine extensions. A tag in a `.go`, `.rs`, `.sh`, `.tsx`, `.sql`, `.toml`, `.cs` or `Dockerfile` is not found, so a scorecard that satisfies the skill can omit a tag that Rule 1 requires. One-value test: the set of tags to account for is the instruction's "every" or the skill's "found", and the two differ whenever the PoC uses another file type. **Second defect, same line:** the filter includes `*.md`, so a re-scan (the Automation note at `:72–75` runs it before evaluation, before handoff and at the QA gate) also scans `POC-DEBT-SCORECARD.md`, `TECHNICAL-DEBT.md` and the ledger, which quote tags, and counts each tag again. | **B (P1).** (a) Quotable: Rule 1 and `:45–49`, above. (b) Reach: T570 approved this skill's own description as placing it inside `poc-guidelines.md`'s reach (`poc-skills-alignment-v1.md` §10.2), and its Rails (`:10, :14`) cite Scorecard Rules 1 and 4. (c) Step A fails. (d) A skill. | **O5-a (second half):** scan every text file, skip VCS and dependency directories and the PoC's own registers. It is a tightening: it finds more, and ADR-007 §5 is not engaged. **Disclosed as beyond the brief's literal wording** (the brief names the scope, not the filter); you may decline it (option B4 keeps only this half). |

**A limit of the recommended scope, recorded.** `rapid-prototyping:41` lets an architectural tag sit in a design document. If a PoC is a subdirectory of a host repository and its design document lives elsewhere in the host, a PoC-root scan does not reach that tag. Option B2 closes it by letting the PoC plan list extra paths. A PoC with its own repository has no such gap, because its root is the repository root.

**Declared-scope text relied on (5b).** `poc-guidelines.md` Rails `:10–13` and the skill's description and Rails (`:3`, `:10`, `:14`). **Maturity.** Not relied on.

### 2.5 P33 O6: the severity source of the `/evaluate-poc` Debt Summary

**Verbatim clauses (live).**
- `commands/evaluate-poc.md:34` "- **Debt items**: <count> (CRITICAL: <n>, MEDIUM: <n>, LOW: <n>)"; `:20` "7. Technical Debt Scorecard summary (severity, effort, risk, owner)"; `:55–59` "11. **Produce a debt summary table**:" with the header "| # | Debt Item | Severity | Effort | Risk | Owner | Production Impact |" and the row "| 1 | ... | CRITICAL/MEDIUM/LOW | S/M/L | ... | ... | blocks/degrades/cosmetic |"; `:63` Rails "plus the PoC's debt/shortcut record".
- Scorecard: `poc-guidelines.md:152` Rule 5 "`Critical` (must fix before production), `Medium` (should fix before production) or `Low` (nice to have)". Ledger: `technical-debt-tracking:85` "**Severity:** critical | medium | low".
- `poc-evaluation/SKILL.md:46` "`debt_count=` is the total in its `Debt items` line"; `:105` (§8) links scorecard items by inventory `#`. Nothing in the skill states where a Debt Summary severity comes from.

**Subject (D3).** The source of each severity in the `/evaluate-poc` Debt Summary table and `Debt items` line.

| Field | Content |
|---|---|
| **Step A** | **Holds.** No clause says how the command's `Severity` is computed, so no clause computes a value that differs from the ledger's or the scorecard's. The three scales have the same three tiers in three spellings (P29, `poc-contract-resolution-v1.md` §3b, set the command's scale; the open case `evaluate-poc-verdict-debt-reconciliation` pins `CRITICAL/MEDIUM/LOW` and rejects `HIGH`). The hazard is silence: an evaluator can grade an item `MEDIUM` in the table while the ledger and scorecard say `Critical`, and the three records then give a production decision-maker two values for one item. |
| **Step C (P2)** | The command's table is the command's declared output, and the skill is applied under it (the command is executed by `poc-orchestrator`, and `poc-evaluation:10` says it "includes an evaluation run through the `/evaluate-poc` command"). P2 permits only an amendment to the skill, scoped to `/evaluate-poc`, and forbids amending the command on the strength of a skill. The skill already carries scoped paragraphs of this kind (`:46`, `:151`). |
| **Step fired** | **A**, with the form of the note taken from **C (P2)**. |
| **Amendment** | **O6-a (recommended):** a paragraph in `poc-evaluation` after `:46` saying that, under `/evaluate-poc`, each Debt Summary severity and each count in `Debt items` is the item's severity from the debt ledger (the scorecard's `Severity` where there is no ledger), spelled in the command's capitals, and that an item with no record is graded with the skill's severity assignment guide and enters the ledger. It changes no value the command declares. I limit it to severity, as the brief does; `Effort` and `Owner` have the same shape and are left alone. |
| **Maturity** | Not relied on. |

### 2.6 O-8: a mapping from `priority::*` labels to ledger priorities

**Verbatim clauses (live).**
- `commands/bug-report.md:50` "Assign severity-appropriate priority", `:53` "`| T<NNN> | BUG: <title> | <owner-slug> | pending | P0\|P1\|P2 | <dep-ids or —> | YYYY-MM-DD |`", `:54` "- Map severity → priority: critical→P0, high→P0, medium→P1, low→P2". The open case `bug-report-severity-priority-ledger-row` quotes `:54` in its brief and hardcodes it in `expect.py` (`SEVERITY_TO_PRIORITY = {"critical": "P0", "high": "P0", "medium": "P1", "low": "P2"}`).
- `gitlab-management/SKILL.md:47–50` the four labels `priority::critical`, `priority::high`, `priority::medium`, `priority::low`; `:87–88` an issue example with "## Priority: Must Have" and the labels "type::feature,priority::high,team::backend"; `:131` "`docs/tasks/active-tasks.md` is the primary task register"; `:134–139` the sync procedure and "Conflict resolution".
- `scrum-master.md:24` "create GitLab issues from new task entries", `:27` "with a Priority of `P0`, `P1` or `P2`", `:32` "`priority::high/medium/low`", `:85` "## Priority: [High/Medium/Low]".
- Tier 1: `AGENTS.md:19` "Priorities: `P0` (critical path), `P1`, `P2`."

**Subject (D3).** The relation between an issue's priority label and its task's ledger Priority.

| Field | Content |
|---|---|
| **Step A** | **Holds.** No text computes one from the other, so nothing can contradict. T617 ruled the same (`task-protocol-observations-ruling-v1.md` §2.7: "A mapping for the issue labels is not needed now … the values are a product choice"). The user's decision of 2026-10-09 to fix every residual, and plan-120's instruction to draft from `bug-report.md:54`, reopen the question as a request for a definition; they do not choose its values. The Scrum Master already proposes both a ledger Priority (`:27`) and a label (`:32`) for one task, and nothing says they must agree. |
| **Where it belongs** | `gitlab-management` § Label Conventions (end of file). That skill defines the labels (`:47–50`) and the ledger-to-issue sync (`:134–139`); it is the one document read by both the orchestrator and the Scrum Master when they touch both fields. Not `task-management` (it does not mention labels) and not `bug-report` (a command is changed only by the user's decision, and its mapping is for a bug's severity). |
| **Drafted mapping** | The four labels have the same words as the four severities `bug-report:54` maps, so the draft applies that mapping: `priority::critical` → `P0`, `priority::high` → `P0`, `priority::medium` → `P1`, `priority::low` → `P2`. It is stated as an **agreement** rule (a task and its issue agree when the label maps to the Priority), because the mapping is many-to-one and cannot be reversed: `P0` agrees with `critical` and with `high`. The ledger stays the source of truth (`:131`, `:139`). |
| **Does it need the user's confirmation?** | **Yes.** (1) `bug-report:54` maps a bug's severity; reading it as the mapping for an issue's priority label is an inference by analogy, not something any text says. (2) `AGENTS.md:19` defines `P0` as the critical path, a property of the dependency graph. Mapping `priority::high` to `P0` therefore marks every high-priority feature issue as critical-path work. The command already does so for bugs and an open case pins it, and I do not re-litigate that, but extending it to all issues is a product choice (`remaining-verdict-renderings-v1.md` §6.1 made the same point about MoSCoW). (3) T617's Group 5 recorded that a mapping "needs your P0/P1/P2 semantics". No ADR-008 step licenses choosing the values. |
| **Maturity** | Not relied on. |

## 3. Held edits (apply verbatim, only after the user decides)

Each Before is unique in its file by reading the whole file **(unverified by grep)**. No edit relaxes a check (ADR-007 §5), and none is upward: each moves a skill or agent toward `AGENTS.md` or `poc-guidelines.md`, or adds a note. None touches a command, a tier-1 file (except O1-b, user's call), the validator, `tests/golden/**` or `scripts/scorecard.py`. Platform projections are regenerated, never edited by hand.

### 3.1 O4-a: `implementation/knowledge/agents/orchestrator.md:205`

Anchor: the full line, which occurs once.

````
Before:
**IMPLEMENTATION GATE** (after core implementation):

After:
**IMPLEMENTATION GATE** (after each implementation task completes, before it merges; skill `validation-gates` § Gate Types):
````

### 3.2 O1-a and O5-a: `implementation/knowledge/skills/technical-debt-tracking/SKILL.md`

**O1-a, inside `:147`.** Replace one sentence; the rest of the line is unchanged. Anchor: the substring, which occurs once in the file.

````
Before:
count the `## Summary` tiers from that column (`poc-guidelines.md` Scorecard Rule 5). Then append the following sections after `## Recommendation`:

After:
count the `## Summary` tiers from that column (`poc-guidelines.md` Scorecard Rule 5). Fill the Debt Inventory's `Category` column with each item's debt-ledger Category, one of the five in § Categories (the instruction leaves that column's values open, and its example values `Validation` and `Reliability` are illustrative), so that every row falls under a row of `## Summary by Category` below. Then append the following sections after `## Recommendation`:
````

**O5-a, `:45–49`** (the heading and the fenced block). This is the text for option B1 (PoC root). Anchor: the heading line `**Step 1: Discover all debt tags**` through the closing fence of the block that follows it. The Before is shown in full.

````
Before:
**Step 1: Discover all debt tags**
```bash
# Scan all project files for POC-DEBT tags
grep -rn "POC-DEBT:" --include="*.py" --include="*.ts" --include="*.js" --include="*.yaml" --include="*.yml" --include="*.md" --include="*.json" --include="*.html" --include="*.css" .
```

After:
**Step 1: Discover all debt tags**

Scan every text file under the PoC root (`poc-guidelines.md` § Debt Scorecard › Scorecard Format), whatever its type, because the scorecard must account for every `POC-DEBT` tag (Scorecard Rule 1) and a tag may sit in any file type. Do not scan outside the PoC root. Skip version-control and dependency directories and the PoC's own debt registers, which quote tags and would be counted a second time:
```bash
# Scan every text file under the PoC root for POC-DEBT tags (substitute <poc-root>)
grep -rIn "POC-DEBT:" --exclude-dir=.git --exclude-dir=node_modules --exclude=POC-DEBT-SCORECARD.md --exclude=TECHNICAL-DEBT.md --exclude="debt-ledger-v*.md" <poc-root>
```
````

**Variants of O5-a.**
- **Option B2 (PoC root plus plan-listed paths):** in the paragraph above, replace "Do not scan outside the PoC root." with "Also scan any other path the PoC plan lists as holding a `POC-DEBT` tag (`poc-orchestrator` § PLAN PHASE); scan nothing else." and add the second fence **O5-c** below.
- **Option B3 (whole checkout):** replace "under the PoC root" with "in the repository checkout, from its top directory" and delete "Do not scan outside the PoC root."; replace `<poc-root>` with `.`. In a host repository the scan then returns tags that belong to no PoC (this repository's own instructions and tests quote the tag format), so Step 2 would have to filter by path.
- **Option B4 (filter only):** keep `.` and the wording "Scan all project files", and apply only the `grep` line and the exclusions.

**O5-c (option B2 only):** `implementation/knowledge/agents/poc-orchestrator.md:29`. Each line starts with three spaces. Anchor: the full line, which occurs once.

````
Before:
   - PoC root, when the PoC does not have its own repository (`poc-guidelines.md` § Debt Scorecard › Scorecard Format)

After:
   - PoC root, when the PoC does not have its own repository (`poc-guidelines.md` § Debt Scorecard › Scorecard Format), and any path outside it that will hold a `POC-DEBT` tag (for example a design document), which the tag scan also covers
````

### 3.3 O2-a: `implementation/knowledge/agents/technical-debt-narrator.md:41`

Anchor: the full line, which occurs once.

````
Before:
- Name output artifacts: `<type>-vN.md`

After:
- Name output artifacts `<type>-vN.md`, except the two deliverables that `poc-guidelines.md` names: `POC-DEBT-SCORECARD.md` (§ Debt Scorecard) and `TECHNICAL-DEBT.md` (§ Narrative Debt Register) are single files under those names, not versioned artifacts
````

### 3.4 O6-a: `implementation/knowledge/skills/poc-evaluation/SKILL.md`

Insert one paragraph after the paragraph at `:46`. Anchor: the line `**Full evaluation artifact structure:**`, which occurs once. The new paragraph is one line.

````
Before:
**Full evaluation artifact structure:**

After:
When the evaluation is run through the `/evaluate-poc` command, each `Severity` in that command's Debt Summary table, and the three counts in its `Debt items` line, are the item's severity as the debt ledger records it, or as the `Severity` column of `POC-DEBT-SCORECARD.md` records it where there is no ledger. The command writes the tier in capitals (`CRITICAL`, `MEDIUM`, `LOW`), where the ledger writes `critical`, `medium`, `low` and the scorecard `Critical`, `Medium`, `Low`. The evaluation assigns no severity of its own to an item that either record holds. An item that neither holds is graded with the severity assignment guide of the technical-debt-tracking skill and enters the debt ledger (that skill, § POC-DEBT Tag Scanning Procedure, Step 3).

**Full evaluation artifact structure:**
````

### 3.5 O8-a: `implementation/knowledge/skills/gitlab-management/SKILL.md` (end of file; needs the user's confirmation)

Anchor: the last table row, which occurs once and is the last line of the file.

````
Before:
| `gate::failed` | Validation gate failed | Gate blocked; requires remediation |

After:
| `gate::failed` | Validation gate failed | Gate blocked; requires remediation |

### Priority Labels and the Ledger Priority

The `priority::` labels grade an issue on four levels, and the ledger's Priority has three values, `P0`, `P1` and `P2` (`AGENTS.md` § Task Protocol). A task and its issue agree when the issue's label maps to the task's Priority as `/bug-report` § Task Creation maps a severity of the same name to a priority:

| Label | Ledger Priority |
|-------|-----------------|
| `priority::critical` | `P0` |
| `priority::high` | `P0` |
| `priority::medium` | `P1` |
| `priority::low` | `P2` |

The mapping does not reverse: `P0` agrees with `priority::critical` and with `priority::high`. The orchestrator sets the ledger Priority (`AGENTS.md` § Task Protocol), and the label is chosen so that it agrees with it when the issue is created (Sync procedure, step 1). The `## Priority:` line of an issue description (for example `Must Have`) is neither a label nor a ledger value. When a human changes the label on an issue, report it to the orchestrator (Sync procedure, step 4), who changes the ledger Priority only if the new label no longer agrees with it (Conflict resolution applies).
````

The table restates `bug-report.md:54`; if that line changes, this table changes with it. The first sentence says so by citing the command. The implementing task may add a non-golden test that compares the two, but it must not touch the golden case.

### 3.6 O1-b (only for option A3): `implementation/knowledge/instructions/poc-guidelines.md:134–135`

Tier-1 text, edited only on the user's decision. The two Before rows start at `| 2 |`.

````
Before:
| 2 | src/api.py | 34 | Validation | Hand-written inline input validation instead of the shared schema layer | Critical | M — move checks into the request-schema layer |
| 3 | src/sync.py | 56 | Reliability | No retry logic | Medium | M — add retry with backoff |

After:
| 2 | src/api.py | 34 | Security | Hand-written inline input validation instead of the shared schema layer | Critical | M — move checks into the request-schema layer |
| 3 | src/sync.py | 56 | Operations | No retry logic | Medium | M — add retry with backoff |
````

The `—` in the effort cells is U+2014, as in the source.

## 4. Hit counts

Case-sensitive, fixed-string, per file, after every held edit to that file (recommended options A1, B1, C1). "Lines" is `grep -cF`; "occ." is `grep -oF … | wc -l`. Before counts are from reading the live files **(unverified by grep)**. A "0 / 0" in the After column means the old wording must be gone.

### 4.1 `agents/orchestrator.md` (O4-a)

| # | Phrase | Before (lines / occ.) | After | Edit |
|---|---|---|---|---|
| 1 | `after core implementation` | 1 / 1 (`:205`) | **0 / 0** | O4-a |
| 2 | `after each implementation task completes` | 0 / 0 | 1 / 1 | O4-a |
| 3 | `validation-gates` | 0 / 0 | 1 / 1 | O4-a |
| 4 | `IMPLEMENTATION GATE` | 1 / 1 | 1 / 1 | anchor survives |
| 5 | `Implementation Gate` (`:249`) | 1 / 1 | 1 / 1 | untouched |

### 4.2 `skills/technical-debt-tracking/SKILL.md` (O1-a and O5-a)

| # | Phrase | Before | After | Edit |
|---|---|---|---|---|
| 6 | `--include=` | 1 / 9 (`:48`) | **0 / 0** | O5-a |
| 7 | `grep -rn "POC-DEBT:"` | 1 / 1 | **0 / 0** | O5-a |
| 8 | `grep -rIn "POC-DEBT:"` | 0 / 0 | 1 / 1 | O5-a |
| 9 | `--exclude` (substring) | 0 / 0 | **1 / 5** | O5-a (one line, five options) |
| 10 | `<poc-root>` | 0 / 0 | 2 / 2 | O5-a |
| 11 | `PoC root` | 2 / 2 (`:33`, `:147`) | **4 / 5** | O5-a (two on the paragraph line, one in the comment) |
| 12 | `Scorecard Rule 1` | 1 / 1 (`:70`) | 2 / 2 | O5-a |
| 13 | `POC-DEBT-SCORECARD.md` | 4 / 4 (`:12`, `:33`, `:70`, `:147`) | 5 / 5 | O5-a |
| 14 | `TECHNICAL-DEBT.md` | 0 / 0 | 1 / 1 | O5-a |
| 15 | `debt-ledger` | 6 / 6 (`:131`, `:135`, `:139`, `:140`, `:147`, `:152`) | **8 / 8** | O1-a (`debt-ledger Category`), O5-a (`debt-ledger-v*.md`) |
| 16 | `Validation` | 0 / 0 | 1 / 1 | O1-a |
| 17 | `Reliability` | 0 / 0 | 1 / 1 | O1-a |
| 18 | `§ Categories` | 0 / 0 | 1 / 1 | O1-a |
| 19 | `Summary by Category` | 1 / 1 (`:162`) | 2 / 2 | O1-a |

Option B3 changes rows 9 to 11 (no `<poc-root>`, fewer `PoC root`); option B4 leaves rows 10, 11 and 14 at their Before values.

### 4.3 `agents/technical-debt-narrator.md` (O2-a)

| # | Phrase | Before | After | Edit |
|---|---|---|---|---|
| 20 | ``Name output artifacts: `<type>-vN.md` `` (with the colon) | 1 / 1 (`:41`) | **0 / 0** | O2-a |
| 21 | ``Name output artifacts `<type>-vN.md` `` (no colon) | 0 / 0 | 1 / 1 | O2-a |
| 22 | `TECHNICAL-DEBT.md` | 1 / 1 (`:14`) | 2 / 2 | O2-a |
| 23 | `POC-DEBT-SCORECARD.md` | 1 / 1 (`:14`) | 2 / 2 | O2-a |
| 24 | `poc-guidelines.md` | 1 / 1 (`:14`) | 2 / 2 | O2-a |

`evaluation-agent.md:44` and `scrum-master.md:111` keep their sentence (not edited).

### 4.4 `skills/poc-evaluation/SKILL.md` (O6-a)

| # | Phrase | Before | After | Edit |
|---|---|---|---|---|
| 25 | `Debt Summary` | 0 / 0 | 1 / 1 | O6-a |
| 26 | `Debt items` | 1 / 1 (`:46`) | 2 / 2 | O6-a |
| 27 | `CRITICAL` | 0 / 0 | 1 / 1 | O6-a |
| 28 | `severity assignment guide` | 0 / 0 | 1 / 1 | O6-a |
| 29 | `POC-DEBT-SCORECARD.md` | 2 / 2 (`:10`, `:105`) | 3 / 3 | O6-a |
| 30 | `/evaluate-poc` | 3 / 4 (`:10`, `:46`, `:151` twice) | 4 / 5 | O6-a |

### 4.5 `skills/gitlab-management/SKILL.md` (O8-a)

| # | Phrase | Before | After | Edit |
|---|---|---|---|---|
| 31 | `priority::` | 5 / 5 (`:47–50`, `:88`) | **11 / 12** | O8-a (intro 1, table 4, paragraph 2) |
| 32 | `P0` | 0 / 0 | 4 / 4 | O8-a |
| 33 | `/bug-report` | 0 / 0 | 1 / 1 | O8-a |
| 34 | `AGENTS.md` | 1 / 1 (`:137`) | 3 / 3 | O8-a |
| 35 | `### Priority Labels and the Ledger Priority` | 0 / 0 | 1 / 1 | O8-a |
| 36 | `Must Have` | 1 / 1 (`:87`) | 2 / 2 | O8-a (the paragraph's example) |

### 4.6 `instructions/poc-guidelines.md` (option A3 only)

| # | Phrase | Before | After | Edit |
|---|---|---|---|---|
| 37 | `\| Validation \|` | 1 / 1 (`:134`) | **0 / 0** | O1-b |
| 38 | `\| Reliability \|` | 1 / 1 (`:135`) | **0 / 0** | O1-b |
| 39 | `\| Security \|` | 1 / 1 (`:133`) | 2 / 2 | O1-b |
| 40 | `\| Operations \|` | 0 / 0 | 1 / 1 | O1-b |

Rows 37 to 40 contain `|`, escaped as `\|` in this table only.

## 5. Effects

### 5.1 Projected paths and root drift

A skill projects to 7 root paths, an agent or command to 6, as in `task-protocol-observations-ruling-v1.md` §5.1 and the counts in `tests/_baselines/root-install-drift.json:31` (74 = 8 skills x 7 + 3 x 6) **(unverified this time; I read no projection)**. An instruction projects to 7 (the T610 note at `:20` counts `coding-standards` on 7 platforms).

| Source edit | Root-projection paths | Item | In the recommended set (A1, B1, C1) |
|---|---|---|---|
| `agents/orchestrator.md` | 6 | O4-a | Yes |
| `skills/technical-debt-tracking/SKILL.md` | 7 | O1-a, O5-a | Yes (one file, counted once) |
| `agents/technical-debt-narrator.md` | 6 | O2-a | Yes |
| `skills/poc-evaluation/SKILL.md` | 7 | O6-a | Yes |
| `skills/gitlab-management/SKILL.md` | 7 | O8-a | Yes |
| `instructions/poc-guidelines.md` | 7 | O1-b | Only option A3 |
| `agents/poc-orchestrator.md` | 6 | O5-c | Only option B2 |
| **Total, recommended set** | **33** (5 files: 3 x 7 + 2 x 6) | | |

- **Subsets (the user's groups, §6).** A1 adds orchestrator 6 + narrator 6 + `poc-evaluation` 7 = 19, plus the `technical-debt-tracking` 7 that Group B also edits. A2 (O2 and O6): 13. A3: A1 plus `poc-guidelines` 7, and the skill 7 still comes from B. A4 (O2 only): 6. B1, B3, B4: 7 each (one file). B2: 13. C1, C2: 7 each. C3 depends on the option chosen. C4: 0.
- **Regenerate:** `node implementation/scripts/sync.mjs --root implementation`, then `python3 implementation/scripts/generate-registry.py`, each followed by `--check`. `implementation/registry/index.json` changes for 5 entries (checksums). `implementation/registry/summary.md` should not change, since no `maturity:` changes **(unverified)**.
- **Mirrors.** `sync.mjs` also writes the same files under `implementation/.<platform>/`; whether they are tracked is **(unverified)**. They are not root drift.
- **Root drift.** `root-install-drift.json` is `"drift": []` after the sixteenth refresh (I read the file). The implementing task declares exactly the paths `python3 -m tests.functional.test_root_install_parity --print-drift` prints (expected 33 for the recommended set). It does not refresh the repo root; that is a separate, user-approved `--projections-only` refresh.

### 5.2 Golden and test coupling

| Item | Coupling | Effect |
|---|---|---|
| `evaluate-poc-verdict-debt-reconciliation` (open, brief read) | Quotes `evaluate-poc.md` step 9 and step 11 (`CRITICAL/MEDIUM/LOW`), and the skill's § 6 backlog table (`poc-evaluation`). `check()` reads `fixture/poc-evaluation.md` only. The brief says the Step 7 scorecard summary "is still not reconciled against a scorecard file" | **Unaffected by O6-a.** It does not touch § 6 or the command, and the new paragraph asserts nothing the case checks |
| `bug-report-severity-priority-ledger-row` (open, brief and `expect.py:1–70` read) | Quotes `bug-report.md:54`; `SEVERITY_TO_PRIORITY` is hardcoded | **Not touched by O8-a.** C1 keeps the command and the case as they are. Option C3 would not (§5.3) |
| `new-poc-plan-hypothesis-format` (open, brief from line 55 read) | Quotes `/new-poc` steps; its brief says the scorecard path "is resolved" (step 11) and `check()` reads the plan fixture | **Unaffected** (no edit touches `/new-poc` or `poc-guidelines` except option A3's example rows, which the case does not quote) |
| Cases that quote `technical-debt-tracking`, `technical-debt-narrator`, `poc-orchestrator`, `orchestrator`, `gitlab-management` | `poc-guidelines-owner-items-v2.md` §4 records that no golden case cites the first three, and `remaining-verdict-renderings-v1.md` §8.1 that none cites `orchestrator.md` | **Not re-verified here** (I read three open briefs only). The orchestrator should grep `tests/golden/open/` for the Before strings in §7.2 |
| **Held-out cases** | **I did not open `tests/golden/held-out/`. Held-out coupling is unknown and was not checked.** | The orchestrator, under its read/audit exception, should run the same greps there and report **only a hit count**, not a case name |
| Non-golden tests | `tests/functional/test_golden_harness_scoring.py` loads one other open case only (`poc-guidelines-owner-items-v2.md` §4) | **Unknown whether any test asserts a Before string** (§7.2). A hit is a `dependency` blocker |

### 5.3 Baseline and grant

- **Protected-path grant:** **none needed** under options A1 to A4, B1 to B4, C1, C2 and C4. No edit touches `tests/golden/**` or `scripts/scorecard.py`.
- **Evaluator-hash baseline v21:** **none needed** under the same options. The baseline hashes `tests/golden` and `scripts/scorecard.py` only (`task-protocol-observations-ruling-v1.md` §5.3), and no knowledge edit changes either. The user's authorization of v21 on 2026-10-09 is for T622's golden realignment and is not used here.
- **Option C3** needs a grant and v21 only if it changes `bug-report.md:54` for bugs: that edits a command (the user's decision) and the pinned `SEVERITY_TO_PRIORITY` in a golden `expect.py`. A C3 mapping that applies to labels only needs neither, but then two mappings exist for the same four words.
- **Checks that should be unaffected (unverified):** `check-maturity.py --root implementation` and `python3 docs/tasks/validate-tasks.py`.

## 6. The user question (one round)

**Q-T621: three groups. Answer with one option per group (for example "A1, B1, C1"), or say "all recommended". Nothing is applied before you answer. No conflict is inside tier 1, so nothing here is an escalation under P5; each group is a choice among valid readings or an approval of ruled edits.**

**Group A: the four residuals decided by Step A or Step B (P41 O4, P33 O1, O2, O6).** O2 is the one conflict on the literal text (Step B). O4, O1 and O6 are readings that hold; each has a recommended note because you chose to fix every residual.

| Option | What changes | Consequences |
|---|---|---|
| **A1 (Recommended)** | O4-a, O1-a, O2-a, O6-a, as drafted | 19 root paths plus the skill shared with Group B. O2 follows your precedent (amend the agent toward the instruction). O4, O1 and O6 are notes; none touches a command, a tier-1 file or a golden path. No grant, no v21 |
| **A2** | O2-a and O6-a only; O4 and O1 stay as Step A readings | 13 paths. The remaining two keep a reading that is valid (the G9 precedent) and a hazard: a reader may skip per-item reviews, or copy `Validation` into an inventory the five-row summary cannot count |
| **A3** | As A1, but O1 by editing the two example Categories in `poc-guidelines.md` (O1-b) instead of the skill note | 26 paths plus the shared skill. A tier-1 text change that ADR-008 never makes on its own: it rests on your decision. It removes the divergence at its source, and the instruction's example then matches the skill's set. The values `Security` and `Operations` are my proposal |
| **A4** | O2-a only | 6 paths. Only the conflict on the literal text is fixed |

**Recommendation: A1.** Each edit is small and points at the governing text without copying it. O2 is required by precedent. O1-a leaves the stable instruction alone, which is why I prefer it to A3.

**Group B: the scan scope and filter for `POC-DEBT` tags (P33 O5).** The filter (5b) is a conflict with Rule 1; the scope (5a) is a missing definition.

| Option | What changes | Consequences |
|---|---|---|
| **B1 (Recommended)** | O5-a: scan every text file under the PoC root, skipping VCS and dependency directories and the PoC's own registers | 7 paths (one file). Matches your decision on the PoC root (Q-A, "PoC's own top dir"). Limit: a tag placed in a design document outside the PoC root, in a PoC that is a subdirectory of a host repository, is not scanned (§2.4). A PoC with its own repository has no gap |
| **B2** | B1, plus the PoC plan lists any extra path that will hold a tag (O5-c in `poc-orchestrator`) | 13 paths. Closes the limit above at the cost of one more plan bullet that someone must fill in |
| **B3** | Whole checkout: make `.` explicit, with the same filter fix | 7 paths. In a host repository the scan returns tags that belong to no PoC, and Step 2 must filter by path |
| **B4** | Filter fix only (all file types, registers skipped); the scope stays `.` and stays unstated | 7 paths. Fixes the Rule 1 conflict and leaves 5a open |

**Recommendation: B1.** It follows your root decision and keeps the scan to one directory. The filter half (5b) is a Step B amendment and is in every option; you may say "B1 without the filter" if you want the scope only, but then a scorecard can still omit a tag that Rule 1 requires.

**Group C: a mapping from `priority::*` labels to `P0`/`P1`/`P2` (O-8).** This needs your confirmation, because the values are a product choice (§2.6).

| Option | What changes | Consequences |
|---|---|---|
| **C1 (Recommended)** | O8-a: in `gitlab-management`, a task and its issue agree when the label maps to the Priority as `bug-report.md:54` maps a severity: critical and high to `P0`, medium to `P1`, low to `P2`. One way: `P0` agrees with either label | 7 paths. One mapping for the same four words. No command and no golden file changes. It marks every `priority::high` issue as `P0` (critical path), as the command already does for bugs |
| **C2** | A note only: the label and the ledger Priority are independent; the orchestrator sets the Priority from the critical path, the Scrum Master sets the label from product priority, and neither is derived | 7 paths. No value choice. Two scales for one concept stay possible, and the Scrum Master can propose a `P0` task with a `priority::low` issue |
| **C3** | A different mapping that you specify (for example `high` to `P1`) | Depends. For labels only, two mappings exist for the same words. If it also changes bug severities, it edits `bug-report.md:54` (your decision) and the pinned `SEVERITY_TO_PRIORITY` in a golden `expect.py`: a file-scoped grant and v21 |
| **C4** | No change; the T617 reading stands | 0 paths. The Scrum Master keeps proposing both fields with nothing saying they agree |

**Recommendation: C1.** It stays inside what the repository already says (`bug-report.md:54`), changes no command or golden file, and makes the two fields agree. If `P0` must remain strictly "critical path", choose C2 or C3.

**Overall recommendation: A1, B1, C1 ("all recommended").** One mechanical implementation task, then one root refresh, covers 5 files (33 paths, 6 fences, no grant, no v21). The edits that are required by precedent are O2-a and the filter half of O5-a; the others are notes you may decline without leaving a contradiction.

## 7. Handoff package for the implementing task (specification; no task is created here)

### 7.1 Package

| Field | Content |
|---|---|
| `task_id` | To be assigned by the orchestrator (a mechanical-tier follow-up to `T621`) |
| `definition` | Apply, verbatim, only the fences the user approves in Q-T621 (§3), then regenerate and declare root drift |
| `constraints` | Never reword. Apply each pair by exact string replacement, matching each single-line Before as a whole line (O1-a is a substring match; O5-a, O6-a and O8-a are multi-line or end-of-file anchors; assert each matches exactly once). Stop and report if an anchor is missing or not unique. Do not edit `AGENTS.md`, `implementation/AGENTS.md`, any instruction (except `poc-guidelines.md` under option A3), any command, `docs/tasks/validate-tasks.py`, any file under `tests/golden/**`, `scripts/`, `.env*`, or any derived platform folder by hand. Do not refresh the repo root. Do not push, and never run any merge or approve call |
| `depends_on` | The user's answer to Q-T621 |
| `input_artifacts` | `remaining-observations-ruling-v1.md` (this file) as the single implementation input |
| `expected_outputs` | The edited files (up to 5, or 7 with A3 and B2); regenerated mirrors and `implementation/registry/index.json` (up to 7 entries); `tests/_baselines/root-install-drift.json` with exactly the printed paths (expected 33 for the recommended set); a report with every §4 count as lines and occurrences |
| `blocker_policy` | `AGENTS.md` § Blocker Protocol: report type and severity (`critical` / `major` / `minor`). A non-golden test that asserts a Before string is a `dependency` blocker to the orchestrator. A golden hit (open or held-out) is a `dependency` blocker reported to the orchestrator as a count only, never with a held-out case name |

Gates to report: `sync.mjs --check`, `generate-registry.py --check`, `check-maturity.py --root implementation`, `scripts/scorecard.py --check` (equal to the current baseline), `python3 docs/tasks/validate-tasks.py`, and `python3 tests/run.py` with output redirected to a file. Confirm byte-unchanged: `AGENTS.md`, every instruction (except under A3), every command, `validation-gates`, every script and `tests/golden/**`.

### 7.2 Pre-flight greps (not run here; I have no shell)

Run and report, then stop if a non-golden test asserts a Before string. Report golden hits to the orchestrator only, as a count.

- `grep -rnF -e 'after core implementation' -e '--include="*.py"' -e 'Name output artifacts: ' -e '| Validation |' -e '| Reliability |' -e 'priority::' -e 'CRITICAL/MEDIUM/LOW' implementation/ docs/wiki docs/guides docs/releases README.md CONTRIBUTING.md tests/ --include='*.md' --include='*.py' --include='*.mjs' --include='*.json' --include='*.yaml'`
- `grep -rlF 'Name output artifacts' implementation/knowledge/agents` then read each hit: any other agent whose deliverable has a fixed name needs the same exception as O2-a (I read only the narrator, `evaluation-agent` and `scrum-master`).
- `grep -rlE 'priority::' implementation/knowledge` then read each hit for a label list or mapping that O8-a must agree with (I read `gitlab-management` and `scrum-master` only).
- `grep -rlE 'technical-debt-tracking|technical-debt-narrator|poc-evaluation|gitlab-management' tests/ --include='*.py' --include='*.yaml' --include='*.json'`, then read each hit.
- Compare each count with §4, and each Before match count with the "occurs once" claims in §3.

## 8. Further observations (new or restated; not ruled)

| # | Site (source file) | Quote | Reading |
|---|---|---|---|
| **N-1** | `agents/technical-debt-narrator.md:46` | "The set of `POC-DEBT`/`DEBT:` tags and shortcuts introduced during PoC execution" | Lists the legacy `DEBT:` format as input, which `poc-guidelines.md:157` says is superseded. Step A holds (the narrator can read legacy tags and Rule 1 counts only `POC-DEBT` tags). Not edited: harmless, and not in the brief |
| **N-2** | `poc-guidelines.md:154–155`, `technical-debt-narrator.md:14` | `TECHNICAL-DEBT.md` | No document states where the register lives (the scorecard's home is the PoC root). O2-a and O5-a exclude it by file name, so they do not depend on its location. If you want it fixed, that is a separate question for the instruction |
| **N-3** | `agents/scrum-master.md:32`, `:85` | "`priority::high/medium/low`" and "## Priority: [High/Medium/Low]" | The Scrum Master's label list omits `priority::critical`, which `gitlab-management:47` defines, so under O8-a it cannot label a `P0`-by-`critical` issue. Step A holds (the list is illustrative). An optional one-word edit and a pointer to O8-a's table would cost 6 more paths; I did not draft it |
| **N-4** | `AGENTS.md:19` against `commands/bug-report.md:54` | "`P0` (critical path)" / "critical→P0, high→P0" | The command maps a severity to a critical-path priority. I treat it as settled (it is pinned by an open case and the user did not ask to reopen it) and inherit it in O8-a. It is the reason C1 needs your confirmation |
| **N-5** | `skills/technical-debt-tracking/SKILL.md:41–49` and `rapid-prototyping/SKILL.md:41` | design-document tags | See the limit under §2.4: a tag in a design document outside the PoC root is not reached by option B1 |

## 9. Still unverified

1. The worktree commit `5e07a6b` (stated by the orchestrator).
2. Every count in §4 and every "occurs once" claim in §3, by reading, not `grep`. The counts for `technical-debt-tracking` rows 11 and 15 and for `gitlab-management` rows 31 and 32 are the likeliest to be off by one.
3. The platform projections of every edited file, their line numbers, and the projection counts of 6 (agent, command), 7 (skill) and 7 (instruction), taken from `root-install-drift.json` and `task-protocol-observations-ruling-v1.md` §5.1; whether `implementation/.<platform>/` mirrors are tracked.
4. That no golden case (open or held-out), no test and no page under `docs/wiki`, `docs/guides`, `docs/releases`, `README.md` or `CONTRIBUTING.md` asserts or restates a Before string. I read three open case briefs and one `expect.py` (to line 70), and no held-out case.
5. That `implementation/registry/summary.md`, the maturity checks and the evaluator-hash baseline are unaffected.
6. The other PoC specialist agents (`technology-scout`, `feasibility-agent`, `scaffolding-agent`, `integration-agent`, `data-mockup-agent`, `demo-agent`, `poc-qa-engineer`, `poc-security-engineer`, `poc-technical-writer`, `poc-devops-engineer`) and the PoC commands: whether they carry the O2 boilerplate with a fixed-name deliverable, or restate the scan or the category set. I read only the narrator, `evaluation-agent` and `poc-orchestrator`.
7. Other users of `priority::` labels, for example in `/sprint-status`, `/team-status` or the issue templates (O-8).
8. That the scope text relied on in §2 was not edited in the change that first recorded these observations (I cannot diff history).
9. The user's decisions of 2026-10-09 are quoted as the brief relays them, not re-read from the user's own message.
10. The remaining parts of the T615 artifact (from line 575) and the T617 artifact beyond what I used.

## 10. Summary

| Item | Subject | Settled by | Outcome | Edits | User decision? |
|---|---|---|---|---|---|
| P41 O4 | Implementation gate timing | Step A holds (same file) | Note-level rewording of `orchestrator.md:205` | O4-a | Group A |
| P33 O1 | Scorecard `Category` values | Step A holds | Skill note; the instruction's example is the tier-1 alternative | O1-a (O1-b) | Group A (A3 is the tier-1 alternative) |
| P33 O2 | Names of the two deliverables | Step B (P1) | Amend the narrator: exempt the two named files | O2-a | Group A |
| P33 O5 | Scan scope and filter | 5a Step A; 5b Step B (P1) | PoC root, every text file, registers skipped | O5-a (O5-c for B2) | Group B |
| P33 O6 | Debt Summary severity source | Step A holds; form from Step C (P2) | Note in `poc-evaluation`, scoped to `/evaluate-poc` | O6-a | Group A |
| O-8 | `priority::*` to `P0`/`P1`/`P2` | Step A holds; no ADR step supplies values | Drafted table in `gitlab-management`, from `bug-report.md:54`; **needs confirmation** | O8-a | Group C |

- **Maturity, corpus counts, majority practice and golden-coupling convenience** were relied on nowhere as authority. Golden coupling appears only as a consequence in §5.
- **No tier-1 conflict, so no P5 escalation.** Changing the instruction's example (A3) and the P0 semantics (C2, C3) stay the user's options.
- **No edit is applied, and none is upward or relaxing.** O5-a tightens the scan; O2-a and O6-a cite the governing text instead of copying it.
- **Grant and baseline:** none needed under any recommended option. A grant and v21 would be needed only under option C3 if it changes `bug-report.md:54`.
- **Golden:** of the three open case briefs I read, none quotes an edited line. **Held-out coupling is unknown and was not checked.**
- **Blockers:** none for this task. The unverified items in §9 (test and golden coupling, other agents' wording) are `dependency` checks for the implementing task, severity `minor`.
