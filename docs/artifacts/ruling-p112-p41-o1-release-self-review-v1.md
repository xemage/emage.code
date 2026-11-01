# Artifact: ruling-p112-p41-o1-release-self-review-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Producer**: solution-architect (T691). **Date**: 2026-10-24. **Tree read**: worktree `agent/solution-architect/T691` from develop `6630b463`.
- **Review mode**: decision artifact only. No knowledge file, command, golden file, ledger or brief was edited. The only file written is this artifact. This session had **no shell and no grep tool**: every line number below comes from reading the named file, and nothing was run. Evidence labels: **[V]** = read in this session; **(unverified)** = not read, not run, or inferred.
- **Not opened**: `tests/golden/held-out/`, any `.env*` or credential file, `.claude/settings*.json`, `.vscode/mcp.json`. No held-out case id is written here.
- **Maturity** is relied on nowhere (ADR-008 P4). For the record only: `release-manager`, `orchestrator`, `validation-gates` are `stable` [V frontmatter]; `release-workflow` and `/prepare-release` are `experimental` [V frontmatter].
- **Based on**:
  - `docs/tasks/task-T691.md` (the brief; the user's decision of 2026-10-24: "O1 have the Solution Architect rule on it") [V];
  - `docs/artifacts/tracked-debt-register-v2.md` (row P112-P41-O1 at section 2.8, section 4 theme 4, decision D-5 at section 5.2, accepted risks at section 6.1) and `tracked-debt-register-v1.md` (the P112-P41-O1 and K-8 rows) [V];
  - `implementation/knowledge/agents/orchestrator.md`, `agents/release-manager.md`, `agents/tech-lead.md` (lines 1-40), `agents/qa-engineer.md` (lines 1-30) [V];
  - `implementation/knowledge/skills/validation-gates/SKILL.md`, `skills/release-workflow/SKILL.md`, `commands/prepare-release.md` [V];
  - `docs/decisions/ADR-008-knowledge-document-authority.md` (Accepted) [V]; ADR-009 was **not** read (file name not known to me; see section 7) (unverified);
  - `AGENTS.md` lines 48-56 and 116 [V];
  - `docs/artifacts/code-review-release-v8-v1.md` (SIGNOFF-CR649) [V]; `docs/releases/v8.0.0.md` lines 1-40, 150-260 [V];
  - `docs/artifacts/remaining-verdict-renderings-v1.md` (G4 / Q-G4, section 4 and 8.4 O1, E-R1, C-G4a/b) and `docs/artifacts/gate-verdict-consistency-v1.md` (G4 at section 7), `docs/artifacts/remaining-observations-ruling-v1.md` (section 5.3 baseline note), `docs/plans/plan-112-parked-note-cleanup.md`, `docs/tasks/task-T667.md` [V].
- **Decision references**: ADR-008 Step A (P3a), D2, D3, D4, D5, P4, P5; ADR-007 (only for what it does not reach); Q-G4 of `remaining-verdict-renderings-v1.md` (the user's choice is applied in `commands/prepare-release.md`, see 1.4). No new ADR is minted.

## 0. Ruling in one paragraph

The "self-review" is **real in the text and partly mitigated in practice**. On the Core Workflow path the orchestrator delegates release preparation (`orchestrator.md:259`) and the Release gate (`orchestrator.md:217`) to the same agent, and that agent's own file lists both Preparation and Validation (`release-manager.md:16-27`). The Release gate, however, is mostly an aggregation of verdicts issued by other executors; the one slice the release manager authors itself is the release document (version bump, changelog, release notes, rollback plan). That slice has an independent party in practice (the tech-lead review by area, the mechanical `verify-release-docs.py` check, the top-level session's own verification before the merge, the user's approval of the tag), but **no text names that party as part of the gate**, and in v8.0.0 the independent review covered an earlier commit than the one the verdict was issued on. **Ruling: ADR-008 Step A holds** (the clauses are jointly satisfiable once the independent check of the self-authored slice is stated); **no rank and no executor change**. Recommended edit: option A+ (a note and one table row in `release-manager.md`, one pointer in `orchestrator.md`). The user may overrule (section 6).

## 1. What the texts say today

### 1.1 Who prepares (Core Workflow path)

- `orchestrator.md:257-262` [V]:
  - `:259` "2. Delegate to **@release-manager** for versioning, changelog, release preparation"
  - `:261` "4. Run **Release Gate**"
- `release-manager.md:15-21` [V] "### Release Process / 1. **Preparation** - Verify all features for the release are merged and tested - Create release branch: `release/vX.Y.Z` - Bump version numbers - Generate changelog from conventional commits - Update documentation"
- `release-manager.md:32` [V] "Prepare `docs/releases/vX.Y.Z.md`; the top-level session creates the GitLab release from it with the user's approval"
- `release-manager.md:231-238` [V] Output Format: "2. Updated changelog ... 6. Release gate VERDICT (PASS/CONDITIONAL_PASS/FAIL) with full justification" (one return carries the prepared changelog and the verdict).

### 1.2 Who gates

- `orchestrator.md:216-217` [V] "**RELEASE GATE** (before deployment): - Delegate to `@release-manager`: "Verify release readiness. Produce VERDICT.""
- `validation-gates/SKILL.md:29` [V] "| **Release** | Release Manager | Before deployment | All gates passed, docs complete, migration guides ready |"
- `validation-gates/SKILL.md:113-118` [V] Release gate inputs: "All prior gate verdicts (must be PASS or CONDITIONAL_PASS with conditions resolved) - Changelog / release notes draft - Documentation updates - Migration guide (if breaking changes) - Rollback plan"
- `release-manager.md:23-27` [V] "2. **Validation** - Ensure CI/CD pipeline passes on release branch - Verify staging deployment - Confirm QA sign-off - Confirm security audit completion"
- `release-manager.md:41-45` [V] Release Gate Policy items 1-4 (block on QA/Security `fail`; risk acceptance; escalate after two blocks; blocker metadata). `release-manager.md:157-187` [V] the `## RELEASE VERDICT` block with a Gate Inputs table of QA, Security, CI/CD, Staging and Performance rows only.

### 1.3 The rule the two collide with

- `validation-gates/SKILL.md:188` [V] "Gate executors should not review their own work. Cross-agent review is mandatory."

### 1.4 Who verifies and merges, and what Q-G4 already settled

- `release-manager.md:29-31` [V] "**Release** (the release manager prepares and verifies; the top-level session merges, tags and publishes with the user's approval) - Open the release merge requests ... the top-level session merges them ... after its own verification".
- `release-manager.md:227` [V] "DO NOT merge a merge request, create or push a tag, or create a GitLab release: the top-level session does these with the user's approval".
- `AGENTS.md:116` [V] "By policy the top-level session merges after its own verification and creates the tag and the release with the user's approval; release-manager opens the release merge requests and reads the result. This is a tool-list narrowing and a policy, not an enforcement."
- `orchestrator.md:129` [V] "**MANDATORY** before a release tag is cut (the top-level session cuts it, with the user's approval)".
- **Command path (already split).** `commands/prepare-release.md:3` runs under `agent: "orchestrator"`; steps 1-6 (`:15-34`) are the orchestrator's; step 7 (`:36-43`) says "The verdict is issued by `@release-manager`, the Release gate's executor (skill `validation-gates` § Gate Types; `orchestrator` agent § Validation Gates)"; `:57` "**Release manager**: release-manager" [V]. This is Q-G4 option 1 of `remaining-verdict-renderings-v1.md` section 4.2, whose own text records the residual: "`orchestrator.md:259` (Core Workflow) also delegates release *preparation* to `@release-manager`; on that path the release manager prepares and gates. That is observation O1 (§8), not decided here" [V, section 4.2 option 1]. That residual is exactly P112-P41-O1.

### 1.5 Where the register stands

- `tracked-debt-register-v2.md` section 2.8 [V]: "P112-P41-O1 | open | open | Never ruled; both delegations still in `orchestrator.md:217,259` (grep). Needs a ruling or the user's acceptance (section 5, decision D-5)."
- D-5 [V]: "P112-P41-O1 needs the solution-architect (ADR-008 step A) or your acceptance." Grade: observation (no `SECURITY:*` grade, no Must/Should).

## 2. The finding, stated precisely

| Question | Answer | Evidence |
|---|---|---|
| Who prepares? | Core Workflow: `@release-manager` (version bump, changelog, `docs/releases/vX.Y.Z.md`). `/prepare-release`: the orchestrator (steps 1-6). | `orchestrator.md:259`; `release-manager.md:16-21,32`; `prepare-release.md:3,15-34` [V] |
| Who gates? | `@release-manager` on both paths. | `orchestrator.md:217`; `validation-gates:29`; `prepare-release.md:42-43` [V] |
| Is it a self-review? | **Yes on the Core Workflow path**, for one slice: the release document the release manager authored (changelog, notes, version markers, rollback plan, Gate Verdicts rows). **No** for the rest: the gate's inputs QA, Security, code review, CI and staging are other executors' verdicts (`validation-gates:113-118`; `release-manager:166-173`). On the command path the preparer (orchestrator) and the issuer differ, which satisfies `validation-gates:188` (Q-G4 option 1). | [V] as cited |
| Who verifies afterwards? | The top-level session verifies before it merges the two release MRs and before it tags; the user approves the tag and the GitLab release. `verify-release-docs.py --tag` is a mechanical check of form (`orchestrator.md:136`). | `release-manager.md:29-31`; `AGENTS.md:116`; `orchestrator.md:129-136` [V] |
| Is there an independent party in practice? | **Yes, three layers, none of them named in the gate text.** (1) Other executors' verdicts. (2) A tech-lead review by area covered the release document (area D "Documentation", CONDITIONAL_PASS) and found form and accuracy defects in it (TL-T649-10, -15 to -20). (3) The top-level session and the user. | `code-review-release-v8-v1.md:18-23,44-52`; `v8.0.0.md:248-254` [V] |
| Was the v8.0.0 Release gate a rubber stamp? | No. The release manager first issued FAIL on 2026-10-15 because SEC-T660-01 was neither fixed nor accepted, and changed the verdict only after the user's decision. | `v8.0.0.md:256` [V] |
| Is anything left uncovered? | **Yes, one narrow gap.** The independent reviews ran on `release/v8.0.0` at `57d0107`; the verdict was issued at branch tip `27b3740`, "which the T648, T649 and T650 reviews did not cover" (the T660 diff had its own review). Release-document edits after the review were therefore gated by the author. The top-level session's verification covers it in practice, but the text does not require the independent check to name the commit it covered. | `v8.0.0.md:248`; `code-review-release-v8-v1.md:9` [V] |
| Did the user accept it? | **No acceptance of this finding is on file.** The user's "Acknowledge the disclosure (Recommended)" of 2026-10-15 concerns SIGNOFF-CR649 (tech-lead promoted and also reviewed the release), a different conflict. Register v2 section 6.1 lists it separately. Do not read it as accepting O1. | `tracked-debt-register-v2.md` section 6.1; `code-review-release-v8-v1.md:12-14` [V] |

**Is the self-review real or only textual?** Both, and the two halves differ:
- *Textual and real on one path*: nothing in `orchestrator.md:217,259` or `release-manager.md:15-27` stops the same agent from preparing and gating the same release, and v8.0.0 did exactly that (T651 prepared the document and issued the verdict, `v8.0.0.md:248`).
- *Mitigated in practice*: the verdict is not the last control; the top-level session verifies and merges, the user approves the tag (`AGENTS.md:116`). Those controls are policy, not enforcement, and they sit outside the agent roster, so the agent texts do not mention them as part of the gate.

## 3. D5 record (ADR-008)

| Field | Content |
|---|---|
| **Subject (D3)** | An actor and a step: who confirms the release document that the Release-gate executor itself authored, before that executor's verdict stands. (One subject; the executor's identity is not in dispute, see below.) |
| **Clauses** | (a) `orchestrator.md:259` and `:217` (same agent prepares and gates); `release-manager.md:15-27`. (b) `validation-gates:188` "Gate executors should not review their own work. Cross-agent review is mandatory." (c) `validation-gates:29` "Release \| Release Manager". |
| **Step A (P3a)** | **Holds, conditionally.** Quote each MUST: (a) delegates preparation and the gate to `@release-manager`; (c) names the Release Manager as the Release-gate executor; (b) forbids a gate executor reviewing its own work. Neither (a) nor (c) is exclusive ("only", "instead of", "no other" appear in neither). (b) is not exclusive of (a) either: the gate reviews *prior verdicts* and the *release documents*; the executor's own work is the release documents only. One decision, one value: the release has one verdict. All three can be obeyed if the self-authored slice is confirmed by a party other than the executor, which the process already contains (section 2). The identity of the executor is **not** in dispute: `validation-gates:29`, `orchestrator.md:217`, `release-manager:157-159` and `prepare-release.md:42-43` all name the release manager (Q-G4 option 1). So there is no rank to decide. |
| **Why not Step B / C / D** | B: no tier-1 text names a release-gate executor or a self-review rule (`AGENTS.md:51-55` fixes verdict values, review agents and fix tasks only). C: the subject is an actor/step of the agent, not a command output; the command already has the split. D: not needed, Step A decides. ADR-008 § Scope: a contradiction inside one document (`validation-gates:29` against `:188`) is "not covered" and falls to same-file coherence, which the same Step A reading satisfies. |
| **Step fired** | **A** (P3a). Outcome per P3a: "no conflict, nothing ranked", "a ruling then amends at most to state the relationship where readers will see it." |
| **Authority needed** | None beyond Step A. ADR-008 Consequences: Step A readings and edits to stable agents under it "no longer need a per-case approval". The register's own wording ("ADR-008 step A or your acceptance") agrees. The user may still overrule. |
| **Declared scope relied on** | `validation-gates` Rails (`:193`): "its designated executor agent" is an input to the gate, so the skill itself does not assign who prepares; `release-manager` description (`:3`) and Responsibilities (`:15-27`) assign preparation and validation to the role. |
| **Edit target and direction** | Agent files only (`release-manager.md`, `orchestrator.md`), pointing at `validation-gates:188` by name and section, not copying it. No skill, no command, no tier-1 file, no golden file is edited (P1 and P2: nothing is amended upward, ADR-007 branch 1 is not engaged). |
| **Maturity** | Not relied on (P4). |
| **Alternatives valid without maturity (P4(d))** | Options A, A+, C and D1 below are each valid readings of the texts; B and D2 change identity or roles and rest on the user's decision, not on Step A. |

## 4. Options

Cost vocabulary: **tokens** = incremental implementation effort of a mechanical-tier task; **churn** = files and generated copies; **golden/evaluator** = whether a protected path or the evaluator hash is touched. Generic facts used throughout [V]: the evaluator hash covers `tests/golden` and `scripts/scorecard.py` only, so a knowledge edit does not change it (`remaining-observations-ruling-v1.md` section 5.3); an edit to a knowledge file changes its per-platform projections, `implementation/registry/index.json` checksums and requires root-drift declarations in `tests/_baselines/root-install-drift.json` (task briefs, section 3 constraints). Whether any open or held-out golden case reads the live text of `release-manager.md` or `orchestrator.md` today is **(unverified)** (earlier rulings found none for `orchestrator.md`, `remaining-verdict-renderings-v1.md` section 8.1, and none for `release-manager` at their time).

### Option A. Keep as is; document that the Release-gate verdict is advisory to the top-level session's verification

- **What changes**: one sentence, in `release-manager.md` (Release Gate Policy) and optionally `orchestrator.md:217`, saying the verdict is an input to, not a substitute for, the top-level session's own verification and the user's approval of the tag.
- **Cost**: tokens XS; churn 1-2 agent files plus projections; golden/evaluator: none expected.
- **Residual**: the gap of section 2 stays. "Advisory" does not name who confirmed the release document, so the next release can again have the author as the only reviewer of the late edits. It also weakens the gate's stated purpose: `validation-gates:32-34` "Every gate MUST produce a verdict", and the Release gate "determines whether work can proceed" (`:11`). Calling it advisory contradicts that wording; Step A does not need the word.

### Option A+. Keep the executor; make the independent check of the self-authored slice an explicit, named gate input (recommended)

- **What changes** (exact text in section 5): `release-manager.md` gains Release Gate Policy item 5 and one row in the Gate Inputs table; `orchestrator.md:217` gains one pointer bullet. `validation-gates`, `prepare-release.md`, `release-workflow` stay byte-unchanged.
- **Cost**: tokens XS (about 10-15k inside an already planned small knowledge batch; about 30-40k as a standalone task including the gate commands and the full suite); churn 2 agent files plus their projections (the projection count per agent file was 6 at T621, and the Cursor removal T662 may have lowered it; unverified) and 2 registry checksums; golden/evaluator: none expected, with the pre-flight greps of section 5 to confirm.
- **Residual**: the independent check is still a role-text duty, not an enforcement (the same standing as `AGENTS.md:116`). The reviewer named for the check can still be a read-only agent that also gated upstream (the tech-lead concentration of SIGNOFF-CR649); the top-level session remains the final check.

### Option B. The Release-gate verdict is given by a different reviewer than the release manager

- **Which agent type fits**:
  - `qa-engineer`: best fit. It is a review agent that `AGENTS.md:53` binds ("Review agents (Tech Lead, QA, Security) MUST NOT modify code during review"), already issued the release Integration verdict (T648), and holds pipeline and test-report reads (`qa-engineer.md:4`). Weakness: it then gates its own Integration input inside the Release verdict.
  - `tech-lead`: second. Read-only by policy during review (TL-T649-09, accepted; `tech-lead.md:4` still lists `edit` and `execute`), and it already did Architecture, Implementation and the documentation area in v8, so the concentration disclosed in SIGNOFF-CR649 grows from 3 of 5 gate rows to 4 of 5.
  - `security-engineer`: poor fit. Its domain is the Security gate; release readiness (changelog, migration guide, rollback) is outside it.
- **What changes** (qa-engineer variant): `validation-gates/SKILL.md:29` (executor), `orchestrator.md:216-217` (delegate), `release-manager.md:3`, `:157-187`, `:237` (the role stops issuing the verdict; it prepares a readiness report), `prepare-release.md:42-43` and `:57` (a command change: it reverses the user's Q-G4 option 1 and rests on the user's decision alone, ADR-007), `release-workflow/SKILL.md:131,:237`, and `docs/releases/_template.md:80`.
- **Cost**: tokens M-L (6 knowledge files, about 35-45 projection paths; unverified count) plus a test change: `test_validation_gates_skill_contract` asserts the Gate Types executor mapping (`remaining-verdict-renderings-v1.md` Q-G4 option 3 text) and would change; golden/evaluator: the frozen `validation-gates` copy in the `validate-workflow-gate-verdict-sources` fixture drifts further but its `check()` reads only the `**Release**` row (same source), so its result is unchanged; the `prepare-release-*` cases check field presence (unverified for the current fixtures). No protected-path grant is needed by the edits themselves.
- **Residual**: it reverses a decision the user already made (Q-G4 option 1), moves the "release manager" role to a preparer without a verdict, and does not remove the need for the top-level session's verification. The QA variant creates a new overlap; the tech-lead variant deepens the concentration.

### Option C. Split preparation and gate inside the release manager's text

- **What changes**: `release-manager.md:13-33` and `:229-238` restructured into two separately delegated modes (prepare; gate); `orchestrator.md:217` and `:259` each name their mode.
- **Cost**: tokens S-M; churn 2 agent files plus projections; golden/evaluator: none expected (unverified).
- **Residual**: both modes are the same role definition (the same file, instructions and model class). The independence is nominal, not structural, and fresh-subagent context separation is not review independence. It mirrors, without improving on, the split `/prepare-release` already has. Not recommended.

### Option D. Other

- **D1. Accept as is, no edit.** Close the register row `accepted` with this artifact as the record. Cost: zero. Residual: as option A, plus nothing is written down for adopters, who read the agent text, not this artifact. Valid under LOW-debt policy ("Track LOW items as debt, stop chasing (Recommended)", 2026-10-23).
- **D2. Align the Core Workflow with the command path**: the orchestrator prepares, the release manager only gates (`orchestrator.md:259`, `release-manager.md:15-21,32`, `release-workflow:237`, the role description at `release-manager.md:3`). Cost M; it reverses actual v8 practice (the release manager prepared `v8.0.0.md`), loads the coordinating agent with the Release phase work against its own budget (`orchestrator.md:190` Release phase budget 60k), and leaves the orchestrator's output reviewed only by the release manager. Not recommended.

## 5. Recommendation

**Option A+.** Reasoning:
1. **The risk is narrow and already contained.** The gate is an aggregation of other executors' verdicts; only the release document is self-authored; the top-level session verifies and the user approves the tag (`AGENTS.md:116`). A structural change (B, D2) buys little against that residual and costs a tree of edits.
2. **Q-G4 option 1 already chose the shape.** The user picked "the orchestrator runs `/prepare-release`; `@release-manager` issues the verdict" and the release manager stays the executor in `validation-gates:29`. B reverses that; A+ is consistent with it.
3. **The one real gap is cheap to close.** The gap is not "the release manager gates" but "nothing names who confirmed the document it authored, at which commit". A+ states exactly that, by pointing at `validation-gates:188` instead of copying it (ADR-008 P3b remedy).
4. **C is cosmetic, A alone is vague, D1 leaves adopters without the text.** If the user prefers zero edits, D1 is valid and costs nothing; it just leaves the v8.0.0 gap unwritten.
5. **No rank, no upward edit, no relaxing of a check**: A+ adds a requirement, relaxes none (ADR-007 section 5).

### 5.1 Lines that change under A+ (apply by exact Before text; each Before is unique in its file as read, **unverified by grep**)

**E1. `implementation/knowledge/agents/release-manager.md:45`** (Release Gate Policy, new item 5).

````
Before:
4. Track blocker metadata in release notes: blocker ID, owner, ETA, mitigation.

After:
4. Track blocker metadata in release notes: blocker ID, owner, ETA, mitigation.
5. Independent check of what you authored. This verdict aggregates the verdicts of other executors; the release document you prepare (version markers, changelog, release notes, rollback plan) is your own work, and `validation-gates` § Guidelines says gate executors should not review their own work. Do not issue a PASS or CONDITIONAL_PASS on that document alone: record in the Gate Inputs table who checked it independently (the `tech-lead` review by area, or the top-level session's own verification) and the commit that check covered. If the document changed after that commit, the check is stale: report it as a blocker or re-run it. Your verdict is an input to the top-level session's verification before the merge and to the user's approval of the tag, not a substitute for either.
````

**E2. `implementation/knowledge/agents/release-manager.md:173`** (Gate Inputs table in the `## RELEASE VERDICT` block, one added row).

````
Before:
| Performance Check | PASS/FAIL | `perf-report-vN.md` |

After:
| Performance Check | PASS/FAIL | `perf-report-vN.md` |
| Release document, independent check (commit: [sha]) | PASS/CONDITIONAL_PASS/FAIL | [reviewer artifact, or the top-level session's recorded verification] |
````

**E3. `implementation/knowledge/agents/orchestrator.md:217`** (Validation Gates, Release gate; one added sub-bullet).

````
Before:
- Delegate to `@release-manager`: "Verify release readiness. Produce VERDICT."

After:
- Delegate to `@release-manager`: "Verify release readiness. Produce VERDICT."
- The release manager prepares `docs/releases/vX.Y.Z.md` (`:259`), so obtain the independent check of that document first (a `@tech-lead` review by area, or your own verification) and give the release manager its artifact and commit; `release-manager` § Release Gate Policy item 5 requires it.
````

**Byte-unchanged under A+**: `validation-gates/SKILL.md` (including `:29` and `:188`), `commands/prepare-release.md`, `skills/release-workflow/SKILL.md`, `docs/releases/_template.md`, every instruction, `AGENTS.md`, `implementation/AGENTS.md`, `tests/golden/**`, `scripts/scorecard.py`, and `orchestrator.md:259`.

Counts: 2 files; 3 hunks (2 in `release-manager.md`, 1 in `orchestrator.md`); about 3 added lines of prose and 1 table row.

### 5.2 Follow-up task shape (specification only; the orchestrator creates the task)

| Field | Content |
|---|---|
| `task_id` | assigned by the orchestrator |
| `definition` | Apply E1 to E3 verbatim; regenerate projections and the registry; declare root drift. Preferred carrier: the small knowledge batch the register already plans (RO621-N-3, TD-T671-P16, TD-T671-T538, TD-T671-T554, TD-T687-02 to -04), so projections and the root refresh are paid once. |
| `owner` | devops-engineer (mechanical tier; needs a shell for the gates). `technical-writer` has no shell (brief section 3). |
| `size` | XS as a hunk inside the batch; S as a standalone task (2 files, 3 hunks, gates and full suite). |
| `depends_on` | the user's answer to section 6. |
| `input_artifacts` | this artifact; `release-manager.md`, `orchestrator.md` at the dispatch commit. |
| `constraints` | no edit to `validation-gates`, any command, `AGENTS.md`, `tests/golden/**` or `scripts/scorecard.py`; no root refresh (declare the printed drift paths only); do not push or merge. |
| `pre-flight (report counts only)` | `grep -rnF` of the Before lines and of "Release document, independent check" over `implementation/`, `docs/wiki`, `docs/guides`, `README.md`, `CONTRIBUTING.md` and `tests/` (non-golden hits are a `dependency` blocker; open-golden hits are reported to the orchestrator; for `tests/golden/held-out/` the orchestrator runs it under its read/audit exception and reports **only a hit count**, never a case name). Also read `tests/functional/` tests that pin `release-manager` or `orchestrator` text (unverified whether any asserts these lines). |
| `gates` | `node implementation/scripts/sync.mjs --root implementation --check`; `python3 implementation/scripts/generate-registry.py --check`; `python3 implementation/scripts/check-maturity.py --root implementation`; `python3 scripts/scorecard.py --check` (equal to the baseline); `python3 docs/tasks/validate-tasks.py`; the evaluator hash with no drift; `python3 -m unittest tests.functional.test_golden_held_out_isolation`; `python3 tests/run.py > file`. |
| `golden / evaluator impact` | None expected: no protected path is edited and the evaluator hash covers `tests/golden` and `scripts/scorecard.py` only. Declared root drift covers the projections of the two agent files. Re-check after the greps. |
| `blocker_policy` | `AGENTS.md` § Blocker Protocol: type and severity (`critical` / `major` / `minor`); stop if a Before text is missing or not unique. |

## 6. What the user must decide if overruling

Nothing needs a decision for A+ to proceed (Step A carries it, section 3). If you want something else, pick one:

1. **Accept without any edit (D1)**: say "accept P112-P41-O1"; the register row moves to `accepted` and this artifact is the record. No task.
2. **Weaker text (A)**: say whether the advisory sentence alone is enough; it leaves the late-edit gap of section 2.
3. **Change who gives the Release-gate verdict (B)**: name the agent (qa-engineer or tech-lead) and confirm that it reverses your Q-G4 choice (option 1). It requires edits to `validation-gates/SKILL.md:29` (the executor mapping), `commands/prepare-release.md:42-43,57` (a command, so your decision under ADR-007, not a skill or agent), `docs/releases/_template.md:80`, and a change to `test_validation_gates_skill_contract`. No protected-path grant is needed for those edits (unverified for the golden fixtures).
4. **Move preparation to the orchestrator on the Core Workflow path (D2)**: confirm that the release manager becomes a pure gate and that the orchestrator carries the Release phase work.
5. **Name a different independent reviewer in E1/E3** (for example `qa-engineer` instead of "the `tech-lead` review by area, or the top-level session's own verification"): a one-word change to the edits above.

## 7. Not verified

- ADR-009 was not read (I did not know its file name and have no directory listing tool). The authority basis used is ADR-008 as Accepted and its own Consequences; the brief and register both point to ADR-008 Step A. If ADR-009 adds a condition on rulings of this kind, it is not reflected here (unverified).
- No `grep` or shell: all uniqueness claims for Before texts, all "none" claims for tests and golden cases reading `release-manager.md` or `orchestrator.md`, and the projection and root-drift counts are by reading only (unverified).
- Whether `test_validation_gates_skill_contract` or another test under `tests/functional/` asserts text of `release-manager.md` or `orchestrator.md` (unverified); I did not open it.
- Whether a user decision on the merge exclusion for `release-manager` (register D-10, plan-123 Open Question 3) was recorded; not found in what I read (unverified).
- The content of the T649/T651 briefs and who, besides the release manager, verified the late edits to `docs/releases/v8.0.0.md` between `57d0107` and `27b3740`; the release document says only that the T648-T650 reviews did not cover the tip (`v8.0.0.md:248`) (unverified).
- Platform projection counts for an agent file after the Cursor removal (T662) (unverified).
- No golden case, held-out or open, was read for this ruling beyond the cited prior rulings' own statements; held-out coupling is unknown.
