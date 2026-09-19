# Artifact: phase3-wave3-promotion-v1.md

> Filename: `phase3-wave3-promotion-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata
- **Producer agent**: tech-lead
- **Task**: T435
- **Created**: 2026-09-10
- **Based on**: `docs/tasks/task-T435.md`; `docs/artifacts/maturity-promotion-criteria-v1.md`
  (T431 — the real per-category `beta→stable` criteria this task must satisfy, verbatim, §3.3
  `instruction`, §3.4 `skill`, §3.5); `docs/artifacts/maturity-levels-v1.md` (T430);
  `implementation/scripts/check-maturity.py` (T432 — the real verifier this artifact's every
  claim is checked against directly, not estimated); `docs/artifacts/phase3-wave1-promotion-v1.md`
  (T433 — precedent for evidence shape, the self-referential ledger-defect mechanism, and the
  "disclose real defects found rather than silently working around them" discipline this artifact
  follows).
- **Supersedes**: none (first version)

## Body

### 0. Outcome summary — read this first

**Real, remaining Wave 3 scope, confirmed fresh this session against
`implementation/registry/index.json`: 24 skills + 4 instructions = 28 components** (two skills are
already `stable`, promoted via Wave 1/its follow-up — not renamed here, per the brief's own
self-referential-defect caution; see `phase3-wave1-promotion-v1.md` instead of this artifact for
which). **10 of the 28 (all 4 instructions + 6 skills) have real, genuine, substantive
`beta→stable` evidence authored and committed to this branch. 9 of those 10 are, as of this
session's real, offline-simulated check against `check-maturity.py`, fully evidence-complete with
zero blockers of any kind — including the self-referential ledger-defect check, which does not
block them because `task-T435.md`'s own brief never names any of the 28 in-scope components by id.
1 of the 10 (`task-management`) is also fully evidence-complete but is blocked by a real,
independent, pre-existing P0 defect (open task T456) unrelated to this task's own work — see §3.**
The other 18 skills are genuinely untouched this session; §4 itemizes 4 of them where real,
pre-existing content defects were discovered incidentally while surveying candidates, and
recommends they be fixed (a separate, non-promotion task) before a future wave attempts their
promotion evidence, rather than promoting evidence on top of a self-contradictory skill file.
**`maturity:` frontmatter is unchanged (`experimental`) for all 28 in this MR**, per the brief's
explicit instruction — see §2 for why flipping is nonetheless known, right now, to be safe for 9
of the 10 evidence-complete components without any further work.

### 1. Components with complete, genuine `beta→stable` evidence (10/28)

All entries below reflect real content added to this branch and independently verified, offline,
against `implementation/scripts/check-maturity.py`'s own checker logic — not estimated. "Complete"
means: schema-valid frontmatter (criterion 1, already true for all 77 components), `## Rails`
(criterion 2), a real `# maturity-evidence:` tag backed by a genuinely assertive test or an
existing incidental reference (criterion 4 for `instruction`/`skill`), a real cross-reference
(criterion 5), and real `docs/wiki/**` documentation (criterion 6) — all verified present.

#### 1.1 Instructions (4/4 — full instruction scope complete)

| Instruction | Rails | Evidence tag | Referenced (criterion 5) | Documented |
|---|---|---|---|---|
| `coding-standards` | New | New — `tests/functional/test_platform_projections.py::test_platform_mcp_configs_have_expected_shape` | Already existing: `tech-lead.md`, `AGENTS.md` Code Standards section | New — `docs/wiki/instructions-overview.md` |
| `git-workflow` | New | New — same test (all 4 instructions tagged at the one real assertion that genuinely exercises all 4 together: the opencode projection's ordered `instructions` list) | **Newly authored**: real reference added to `release-manager.md`'s "Git Flow for Releases" section, which had none before | New — `docs/wiki/instructions-overview.md` |
| `poc-guidelines` | New | New — same test | **Newly authored**: real reference added to `poc-orchestrator.md`'s "Mandatory Debt Tracking" section (which also fixed a real, pre-existing drift — see §5) | New — `docs/wiki/instructions-overview.md` |
| `security-guidelines` | New | New — same test | Already existing: `tech-lead.md`, `handoff.md`, `AGENTS.md` Security section, `agents-overview.md` | Already existing: `agents-overview.md` |

The one real functional test all 4 evidence tags are attached to
(`test_platform_mcp_configs_have_expected_shape`) genuinely exercises all 4 instructions together:
it fails if any one of them is dropped from, reordered in, or renamed within the opencode
platform's projected `instructions` list — not a placeholder assertion engineered only to contain
the tag string.

#### 1.2 Skills (6/24 attempted this session)

| Skill | Rails | Evidence tag (new test) | Referenced (criterion 5) | Documented |
|---|---|---|---|---|
| `task-management` | New | New — `tests/functional/test_wave3_skill_contracts.py::TestTaskManagementSkillContract` (2 tests: real `active-tasks.md` header-row match, real `AGENTS.md` Lifecycle States vocabulary match) | **Newly authored**: `orchestrator.md`'s Task Management section (the pre-existing `AGENTS.md` Task Protocol mention doesn't count — the checker only recognizes `skill `<id>`` mentions in `agents/*.md`/`commands/*.md` bodies, not `AGENTS.md` itself, outside its Skill Workflow table) | New — `docs/wiki/commands-and-skills-overview.md` |
| `checkpoint-protocol` | New | New — `TestCheckpointProtocolSkillContract` (2 tests: File Location convention and required-content match against `AGENTS.md`'s Checkpoint Protocol section) | Already existing: `AGENTS.md`'s mandatory Skill Workflow table | New — `docs/wiki/commands-and-skills-overview.md` |
| `receiving-code-review` | New | New — `TestReceivingCodeReviewSkillContract` (review-source table resolves to real registered agent ids) | Already existing: `AGENTS.md`'s mandatory Skill Workflow table | New — `docs/wiki/commands-and-skills-overview.md` |
| `systematic-debugging` | New | New — `TestSystematicDebuggingSkillContract` (Escalation section's blocker type/severity match `AGENTS.md`'s Blocker Protocol vocabulary) | Already existing: `AGENTS.md`'s mandatory Skill Workflow table | New — `docs/wiki/commands-and-skills-overview.md` |
| `verification-before-completion` | New | New — `TestVerificationBeforeCompletionSkillContract` (every Standard Command path resolves to a real file on disk) | Already existing: `AGENTS.md`'s mandatory Skill Workflow table | New — `docs/wiki/commands-and-skills-overview.md` |
| `testing-strategy` | New | New — `TestTestingStrategySkillContract` (2 tests: QA-gate VERDICT vocabulary match, Coverage Thresholds table well-formedness) | **Newly authored**: `orchestrator.md`'s Validation Gates section (Integration Gate) | New — `docs/wiki/commands-and-skills-overview.md` |

All 7 new contract tests in `tests/functional/test_wave3_skill_contracts.py` make real,
substantive cross-consistency assertions — e.g. the real `docs/tasks/active-tasks.md` header row
against `task-management`'s declared schema, `AGENTS.md`'s Lifecycle States/Blocker
Protocol/Checkpoint Protocol/Validation Gates vocabulary against each skill's own documented
contract, standard verification command paths resolving to real files on disk — not placeholder
assertions engineered only to contain the required tag string. All 9 tests pass
(`pytest tests/functional/test_wave3_skill_contracts.py` → 9 passed).

### 2. Real, offline-simulated `check-maturity.py` results (not estimated)

Performed identically to `phase3-wave1-promotion-v1.md` §3.1's method: an uncommitted, disposable
simulation (component `maturity` field flipped to `stable` in memory only, nothing written to
disk or committed) run against the real, current repo state on this branch.

```
coding-standards -> PASS
git-workflow -> PASS
poc-guidelines -> PASS
security-guidelines -> PASS
checkpoint-protocol -> PASS
receiving-code-review -> PASS
systematic-debugging -> PASS
testing-strategy -> PASS
verification-before-completion -> PASS
task-management -> FAIL
  experimental->beta #3 (no open P0 defect): open P0 task T456 names it in its brief
  beta->stable #7 (no open P0 or P1 defect): open P0 task T456 names it in its brief
```

**9 of the 10 pass every single criterion, including the shared P0/P1 ledger-defect check, with
zero simulated failures of any kind.** This is a materially different, better result than Wave 1's
finding: `task-T435.md`'s own brief deliberately never names any of the 28 in-scope skill/
instruction ids (it describes scope only in aggregate — "24 skills + 4 instructions" — precisely
to avoid Wave 1's self-referential trap), so **the self-referential ledger-defect mechanism does
not block any of these 9**, even while this task's own row remains open in `active-tasks.md`. This
means, unlike Wave 1's Blocker 1, no ledger archival is a precondition for flipping these 9 — a
fast follow-up can set `maturity: stable` for all 9 directly, re-run
`check-maturity.py --verbose` to confirm, and merge, independent of when/whether `T435`'s own row
closes. `task-management` is the sole exception: it is fully evidence-complete (all criteria other
than #3/#7 pass) but is blocked by a real, independent, pre-existing defect — see §3.

### 3. `task-management`'s one real, independent blocker

`docs/tasks/task-T456.md` (open, `P0`, status `blocked` — not `done`/`cancelled`, so it counts per
`maturity-promotion-criteria-v1.md` §3.5) contains the literal string
`` `implementation/knowledge/skills/task-management/SKILL.md` `` in its own body (line 90, quoting
the skill's Status Lifecycle section while discussing an unrelated golden-suite/live-execution
concern). This is a real hit, not a false positive — the task genuinely references the file, even
though its own subject matter (a downstream-measurement ship gate) has nothing to do with
`task-management`'s promotion readiness. This is the same class of finding as Wave 1's Blocker B
(§3.2 of `phase3-wave1-promotion-v1.md`): a real, pre-existing, independent defect that surfaces
only once the self-referential blocker (§2 above) is accounted for. **Mitigation: out of scope for
this task per `maturity-promotion-criteria-v1.md`'s own design** (the P0/P1-defect gate exists
specifically to prevent promoting components with known, unresolved defects to `stable`) —
resolving `T456` is tracked separately; once it closes (or its `task-management` reference is
removed/resolved), `task-management` can be flipped to `stable` alongside the other 9 with zero
further evidence work.

### 4. Real, pre-existing content defects discovered but NOT fixed (out of scope for this task)

While surveying skill candidates beyond the 6 completed above, four **real, substantive, pre-
existing content inconsistencies** were found in skill files — each would need to be resolved
(a genuine content/design decision, not a mechanical promotion-evidence addition) before that
skill could honestly receive `beta→stable` evidence, because writing a genuine contract test
against a self-contradictory or environment-inconsistent skill file would either encode the wrong
behavior or require fixing the underlying inconsistency as an undisclosed side effect. Each is
disclosed here rather than silently worked around or silently skipped without explanation, per
this task's Acceptance Criterion 2 ("no silent scope narrowing"):

1. **`blocker-escalation`**: its own "Severity Definitions" table uses a 4-level vocabulary
   (`critical | high | medium | low`), while `AGENTS.md`'s canonical Blocker Protocol section (and
   `systematic-debugging`'s own Escalation section, now promoted in this MR) uses a 3-level
   vocabulary (`critical | major | minor`). Two other files
   (`implementation/knowledge/commands/bug-report.md`,
   `implementation/knowledge/skills/technical-debt-tracking/SKILL.md`) also use the 4-level scale,
   so this may be a deliberate, distinct "bug/debt severity" vocabulary rather than a simple typo —
   but `blocker-escalation`'s own file is specifically about *blocker* severity, the exact concept
   `AGENTS.md` already defines a 3-level scale for, and the two scales are never reconciled
   anywhere. Reconciling this is a real design decision (are these one vocabulary or two?), not a
   promotion-evidence addition.
2. **`cost-token-governance`**: its "Budget Envelope Defaults" section roughly matches `AGENTS.md`'s
   Token Governance table (Planning/Architecture ≤80k, Implementation ≤120k, QA/Security/Release
   ≤60k), but its own later "Phase-Specific Token Budgets" table declares a materially different
   4-phase structure (Phase 1 Planning=20k, Phase 2 Implementation=120k, Phase 3 QA/Security=60k,
   Phase 4 Release=30k as a *separate* line from QA/Security) that is never reconciled with the
   first section in the same file.
3. **`task-management`** (already promoted in §1, evidence-complete and disclosed here as a
   *separate*, non-blocking finding): its own Procedures section (`Create a Task` step 4-5,
   `Manage Dependencies`) instructs populating `BlockedBy`/`Blocks` fields, but the file's own
   declared `active-tasks.md` 7-column schema (verified in §1's new contract test against the real
   ledger) has no such columns — only a single `Depends on` column exists in the real ledger and in
   this file's own schema table. This does not block this session's promotion evidence (the
   contract test checks the schema table, which is internally accurate; it does not check the
   Procedures section's `BlockedBy`/`Blocks` claims), but it is a real, disclosed content bug worth
   a follow-up: either the real ledger schema needs bidirectional fields, or the Procedures section
   needs rewriting to describe `Depends on` only. `dependency-graphing` (untouched, §4 below) has
   the identical `Blocks`/`BlockedBy` assumption baked into its own core Procedure, so this is not
   an isolated typo — it is a shared, cross-file assumption that doesn't match the real schema.
4. **`worktree-isolation`**: its "Merge After Task Completion" and "Batch Parallel Execution"
   procedures instruct `git checkout main` followed by a direct `git merge <branch> --no-ff`,
   bypassing an MR entirely — this directly contradicts `git-workflow.md` (promoted to full
   evidence-completeness in this same MR, §1.1)'s "Protected Branches — No Direct Commits, Ever"
   rule and its own Worktree Lifecycle section, which requires a branch + MR merge to `develop`,
   never a direct merge to `main`. Teaching an agent this skill's literal procedure today would
   have it attempt exactly the rejected-push scenario `git-workflow.md`'s own Recovery Procedure
   exists to fix.

None of these four are fixed in this MR — fixing them is a real design/content decision (not a
mechanical promotion-evidence addition) and risks scope creep well beyond a promotion task's
mandate. Recommended as a `type: technical`, `severity: major` follow-up (see §6).

### 5. A pre-existing drift fixed as part of authoring genuine evidence (not a new defect — disclosed)

`poc-orchestrator.md`'s "Mandatory Debt Tracking" section referenced the legacy `DEBT:` comment
tag in three places, while `poc-guidelines.md` (the instruction itself) explicitly documents that
convention as superseded by `POC-DEBT` for all new PoC work. Since this task was already adding a
real cross-reference from `poc-orchestrator.md` to `poc-guidelines.md` (criterion 5), leaving the
agent file citing the instruction's own admittedly-legacy convention would have made the new
reference inaccurate at the moment it was authored. Fixed as part of that same edit (not a separate
scope expansion): all three `DEBT:` mentions in `poc-orchestrator.md` now say `POC-DEBT`,
consistent with `poc-guidelines.md`'s own "supersedes" note. Similarly, `checkpoint-protocol`'s
File Location section declared `checkpoint-<N>.md` while `AGENTS.md` and every real checkpoint file
in `docs/checkpoints/` use `checkpoint-<SEQ>-<phase>.md` — corrected to match the real, binding
convention while authoring that skill's own contract test (§1.2), which needed to assert against
the *correct* convention, not the stale one.

### 6. Untouched skills (18/24) and recommended continuation plan

Genuinely untouched this session, no evidence authored, no content surveyed for correctness beyond
the 4 flagged in §4: `api-design`, `ci-cd-pipeline`, `context-window-management`, `cwso-awareness`,
`gitlab-management`, `memory-management`, `plan-approve-execute`, `poc-evaluation`,
`project-planning`, `rapid-prototyping`, `release-workflow`, `skillify`,
`technical-debt-tracking`, `technology-scouting`. Surveyed but deliberately not attempted, per §4:
`blocker-escalation`, `cost-token-governance`, `dependency-graphing`, `worktree-isolation`.

**This is a `type: technical`, `severity: major` finding, not a failure**: 28 components is ~3x
Wave 1's scope, and this session's own discipline (writing real, substantive contract tests rather
than placeholder tag-holders, and surveying candidates for pre-existing content correctness before
building evidence on top of them) costs real time per component. Recommended split, mirroring
`task-T433.md`'s own successful resolution and `task-T435.md`'s own "your call" on
splitting: (a) a follow-up promotion wave for the 14 fully-untouched skills, once a reasonably-
sized batch is chosen (the remaining scope is still large enough to warrant its own further split,
at the orchestrator's discretion); (b) a separate, non-promotion content-fix task for the 4 flagged
in §4, blocking their own future promotion attempts until resolved; (c) resolution of `T456`
(tracked separately, not part of this task) as the sole remaining blocker for `task-management`.

### 7. Consumed by

- **Orchestrator** — to archive `T435` and, per §2's finding, dispatch a fast follow-up that flips
  `maturity: stable` for the 9 fully clean components (4 instructions + `checkpoint-protocol`,
  `receiving-code-review`, `systematic-debugging`, `verification-before-completion`,
  `testing-strategy`) directly — no ledger archival dependency, unlike Wave 1 — and separately
  tracks `task-management`'s dependency on `T456`.
- **A future wave** — for the 14 fully-untouched skills, and the 4 flagged-but-deferred skills once
  their content defects (§4) are resolved by a dedicated fix task.
- **T436** (honest demotion pass) — should be aware that 18/24 skills remain unevaluated by any
  wave, and that 4 of those 18 have known, disclosed content defects that make them poor near-term
  `stable` candidates even after evidence-authoring, not obviously `deprecated` candidates either
  (the defects are fixable drift, not obsolescence).
