# Artifact: phase3-wave2-promotion-v1.md

> Filename: `phase3-wave2-promotion-v1.md`. Immutable once produced; revisions bump `<N>`.

## Metadata
- **Producer agent**: tech-lead
- **Task**: T434
- **Created**: 2026-09-10
- **Based on**: `docs/tasks/task-T434.md`; `docs/artifacts/maturity-promotion-criteria-v1.md` (T431 —
  the real per-category `beta->stable` criteria this task must satisfy, verbatim); `docs/artifacts/
  maturity-levels-v1.md` (T430); `docs/artifacts/phase3-wave1-promotion-v1.md` (T433 — precedent for
  evidence shape and the self-referential ledger-defect mechanism); `implementation/scripts/
  check-maturity.py` (T432 — the real verifier every claim below is checked against directly, not
  estimated).
- **Supersedes**: none (first version)

## Body

### 0. Outcome summary — read this first

**40 components were in scope (23 agents + 17 commands, per `task-T434.md`'s own "Real scope"
section). Zero are promoted to `maturity: stable` in this MR** — every component's frontmatter is
unchanged at `maturity: experimental`, mirroring `phase3-wave1-promotion-v1.md`'s own resolution.

Within that scope, real, substantive evidence (new `## Rails` sections, wiki documentation, a new
cross-consistency test file with `# maturity-evidence:` tags, one `agent:` frontmatter fix) was
authored for all 40 components. Verified directly against the real, unmodified
`implementation/scripts/check-maturity.py` via an uncommitted, disposable in-memory simulation (each
component's `maturity` field set to `stable` only in a throwaway `Component` object built from the
real, currently-committed file content — never written to disk, never part of any commit in this
branch; same technique `phase3-wave1-promotion-v1.md` §3.1 used):

- **19 of 23 agents are fully `beta->stable` evidence-complete** — the simulation reports a clean
  `PASS` with no further evidence gap of any kind.
- **4 of 23 agents** (`context-retriever`, `devops-engineer`, `evaluation-agent`,
  `solution-architect`) are evidence-complete but blocked by **real, independent, pre-existing
  defects** already tracked elsewhere in the ledger (`T456`, `T457` — §3 below), unrelated to this
  task's own evidence work.
- **0 of 17 commands are fully evidence-complete for `stable`.** 14 of 17 are blocked solely by
  criterion 4 (no golden case exists for that command — a protected-path gap, §4 below), with every
  other criterion (Rails, `agent:` resolution, wiki documentation, no-defect) satisfied. The other 3
  (`new-feature`, `prepare-release`, `security-audit`) already have golden coverage but are blocked
  by real tracked defects, the same pattern `phase3-wave1-promotion-v1.md` §3.2 found for two of its
  own command candidates (not repeated here by id — see that artifact's table).
- **A positive deviation from Wave 1's own documented mechanism, confirmed not assumed (§2):**
  `task-T434.md`'s own body never names any of the 40 in-scope component ids (by design — see its
  "Real scope" section's explicit avoidance), so the self-referential ledger-defect blocker that
  fully blocked all 9 of Wave 1's candidates does **not** reproduce for Wave 2's targets. The
  evidence above is real evidence completeness, not merely "would pass once T434 archives" the way
  Wave 1's was for its 3 fully-clean candidates — it already reports clean today, with T434's own row
  still open, for anything not blocked by the two independent, real defect classes in §3/§4.

### 1. Evidence produced, per component

#### 1.1 Agents (23) — Rails, evidence, cross-reference, documentation

All 23 received a new `## Rails` section (Inputs/Out of scope/Failure mode, role-specific prose
grounded in that agent's own existing Deliverables/Responsibilities/Scope content, not generic
padding — reviewable per-file in the diff).

| Agent | Evidence (criterion 4) | Cross-ref (criterion 5) | Documented (criterion 6) | Real blocker (criterion 7) |
|---|---|---|---|---|
| `context-retriever` | **Newly authored**: `test_agent_escalation_consistency.py` | **Newly authored**: `@context-retriever` row added to `agents-overview.md`'s new Platform/Infrastructure table | **Newly authored**: same row (real, multi-sentence description) | `T456` (P0, §3) |
| `data-mockup-agent` | Newly authored (escalation test) | Already existing | **Newly authored**: expanded `agents-overview.md` row to a full sentence | none |
| `database-engineer` | Newly authored (escalation test) | Already existing | **Newly authored**: expanded `agents-overview.md` row | none |
| `demo-agent` | Newly authored (escalation test) | Already existing | Already existing (via `name` match elsewhere) | none |
| `devops-engineer` | Already existing (`completed-tasks.md` rows with MR refs) | Already existing | **Newly authored**: expanded `agents-overview.md` row | `T457` (P1, §3) |
| `evaluation-agent` | Newly authored (escalation test) | Already existing | **Newly authored**: expanded `agents-overview.md` row | `T456` (P0, §3) |
| `feasibility-agent` | Newly authored (escalation test) | Already existing | **Newly authored**: expanded `agents-overview.md` row | none |
| `frontend-developer` | Newly authored (escalation test) | Already existing | Already existing (via `name` match) | none |
| `integration-agent` | Newly authored (escalation test) | Already existing | **Newly authored**: expanded `agents-overview.md` row | none |
| `poc-devops-engineer` | Newly authored (escalation test) | Already existing | **Newly authored**: expanded `agents-overview.md` row | none |
| `poc-orchestrator` | **Newly authored**: workflow `@`-mention resolution test | Already existing | Already existing (via `name` match) | none |
| `poc-qa-engineer` | Newly authored (escalation test) | Already existing | **Newly authored**: expanded `agents-overview.md` row | none |
| `poc-security-engineer` | Newly authored (escalation test) | Already existing | **Newly authored**: expanded `agents-overview.md` row | none |
| `poc-technical-writer` | Newly authored (escalation test) | Already existing | **Newly authored**: expanded `agents-overview.md` row | none |
| `product-owner` | Newly authored (escalation test) | Already existing | Already existing (via `name` match) | none |
| `release-manager` | Already existing (`completed-tasks.md` rows with MR refs) | Already existing | Already existing | none |
| `scaffolding-agent` | Newly authored (escalation test) | Already existing | **Newly authored**: expanded `agents-overview.md` row | none |
| `scrum-master` | Newly authored (escalation test) | Already existing | Already existing (via `name` match) | none |
| `solution-architect` | Newly authored (escalation test) | Already existing | Already existing (via `name` match) | `T457` (P1, §3) |
| `technical-debt-narrator` | Newly authored (escalation test) | Already existing | **Newly authored**: expanded `agents-overview.md` row | none |
| `technical-writer` | Already existing (`completed-tasks.md` rows with MR refs) | Already existing | Already existing | none |
| `technology-scout` | Newly authored (escalation test) | Already existing | Already existing (via `name` match) | none |
| `ux-designer` | Newly authored (escalation test) | Already existing | Already existing (via `name` match) | none |

Three agents (`devops-engineer`, `release-manager`, `technical-writer`) already had resolvable
`completed-tasks.md` evidence (`Owner` == agent id, `Outcome / artifact` column containing an `!<MR>`
reference the checker's `_resolves_to_artifact()` recognizes) — no new evidence needed for criterion
4 on those three. `release-manager` and `technical-writer` needed **only** the new `## Rails` section
to become fully evidence-complete; everything else was already true for them before this task.

`test_agent_escalation_consistency.py` (new file, `tests/functional/`) is a real, substantive
cross-consistency check, not padding engineered only to contain the required tag string: it proves
(a) every PoC-track agent's Blocker Reporting claim ("the PoC orchestrator will handle escalation")
is backed by a real, bidirectional entry in `poc-orchestrator.md`'s own `agents:` frontmatter roster
— catching a class of drift where an agent claims an escalation path the coordinating orchestrator
doesn't actually recognize, or vice versa — and (b) `poc-orchestrator`'s own `## PoC Workflow`
section's 14 `@`-mentions all resolve to real, registered agent ids, the same "named executor
resolves to a real component" shape `phase3-wave1-promotion-v1.md` §2 used for one of its own
skills' Gate Types table (not repeated here by id — see that artifact), applied here to an agent's
own delegation roster instead. 6 tests, all real
assertions against live file content (`pytest tests/functional/test_agent_escalation_consistency.py`
→ 6 passed).

#### 1.2 Commands (17) — Rails, agent resolution, documentation

All 17 received a new `## Rails` section. `commands/bug-report.md` had **no `agent:` frontmatter set
at all** (schema-valid since `agent` is optional per `command.schema.json`, but a real gap blocking
criterion 5) — set to `agent: "orchestrator"` in this MR, a disclosed judgment call: `bug-report`
creates rows in `docs/tasks/active-tasks.md` (task-ledger writes), matching the established pattern
of every other task-ledger-writing utility command (`batch`, `handoff`, `skillify`,
`sprint-status`, `team-status`, `validate-tasks`, `validate-workflow`) already being
`orchestrator`-owned; no other candidate owner fit as well and none was named anywhere in the
existing knowledge base for this command.

15 of 17 commands (all except `discover-skills` and `handoff`, which were already documented via
`docs/wiki/implementation-guide.md`/`quick-start.md`) received a new row in
`docs/wiki/commands-and-skills-overview.md`'s `## Commands` table, extending it from the 2 commands
T433 already documented there (see that artifact for which) to all 19 registered commands having a
real, multi-sentence description row. The intro paragraph was updated to reflect this (previously
said "not yet a complete catalogue of all 19 commands").

`agent:` frontmatter for all 17 was verified to already resolve to a real, registered agent id
(`orchestrator`, `poc-orchestrator`, or `security-engineer`) once `bug-report`'s gap was fixed —
criterion 5 is satisfied for all 17.

### 2. The self-referential ledger-defect mechanism — confirmed NOT to reproduce for T434's own targets

`phase3-wave1-promotion-v1.md` §3.1 documented that `T433`'s own open ledger row made
`check-maturity.py` unsatisfiable for any of T433's 9 candidates, because `task-T433.md`'s own body
necessarily named all 9 candidate ids as its subject matter. `task-T434.md` was drafted, per its own
"Real scope" section, to deliberately avoid naming any specific component id in its own body (both to
avoid the T433-discovered mechanism and to avoid a second, distinct variant found while drafting the
brief — spuriously regressing an already-`stable` component by naming it in passing). This task
verified that avoidance actually holds, rather than assuming the brief's own claim about itself:

```
$ python3 -c "
import re
text = open('docs/tasks/task-T434.md', encoding='utf-8').read()
def mentions(t, ident):
    return re.search(r'(?<![\w-])' + re.escape(ident) + r'(?![\w-])', t) is not None
for ident in [<all 23 agent ids>, <all 17 command ids>]:
    if mentions(text, ident):
        print('MENTIONED:', ident)
print('done')
"
done
```

Zero hits — `task-T434.md`'s body names none of its own 40 in-scope components. Also checked: the
`active-tasks.md` row's own `Title` cell ("Wave 2 promotion (remaining agents/commands) to `stable`")
names none of them either. **Net effect: the `_ledger_defect()` check in `check-maturity.py` cannot
be tripped by `T434`'s own open row for any of the 40 in-scope components** — unlike Wave 1, where
this was the dominant, universal blocker. The 40-component simulation results in §0 (19/23 agents,
0/17 commands "fully evidence-complete") are real, current-state results with `T434` still open, not
merely a projection of what would happen after archival. The commentary blockquote text surrounding
row `T434` in `active-tasks.md` (lines discussing the dispatch, e.g. mentioning specific components in
prose around the table) is **not** checked by `_ledger_defect()` either — it only inspects the row's
`Title` cell and the linked `task-<ID>.md` body, confirmed by reading `check-maturity.py`'s
`_ledger_defect()` implementation directly (`implementation/scripts/check-maturity.py`, function of
that name).

### 3. Real, independent, pre-existing defects blocking 4 agents (unrelated to this task)

| Agent | Real blocker | Nature |
|---|---|---|
| `context-retriever` | open P0 task `T456` names it in its brief | Already disclosed, pre-existing: `T456` is the downstream-measurement ship-gate task; its brief names `context-retriever` in an unrelated capacity. Not fixable by more evidence. |
| `evaluation-agent` | open P0 task `T456` names it in its brief | Same task, same mechanism. |
| `devops-engineer` | open P1 task `T457` names it in its brief | Already disclosed in `phase3-wave1-promotion-v1.md` §3.2 for a different agent under the same task; `T457` also names `devops-engineer` (the scoped-tool-primitive backlog item). |
| `solution-architect` | open P1 task `T457` names it in its brief | `T457`'s own row lists `solution-architect` as the task's `Owner`, which the `_ledger_defect()` check's title/body text-match also catches. |

None of these are fixable by producing more or better promotion evidence — they are genuine, already
disclosed-elsewhere findings that this task did not introduce and is not scoped to resolve (per
`maturity-promotion-criteria-v1.md`'s own design: the P0/P1-defect gate exists specifically to keep
`stable` from being claimed while a known, unresolved defect is open against that component).

### 4. The command golden-case gap — 14 of 17 commands, one remaining, well-defined blocker

`maturity-promotion-criteria-v1.md` §3.2.4 requires ≥1 golden case (`open/` or `held-out/`) whose
`case.yaml` `command:` value names the command. Per `maturity-promotion-criteria-v1.md` §1's own
grounding check, only 5 of 19 commands are structurally reachable today — the two T433 already
covered (see that artifact for which) plus this task's `/new-feature`, `/security-audit`, and
`/prepare-release`, which already have golden coverage but are blocked by real tracked defects
(§3.2 pattern, already the case before this task and unrelated to it). The remaining **14 of this
task's 17 commands have no golden coverage of any kind** (`batch`, `bug-report`,
`consolidate-memory`, `discover-skills`, `evaluate-poc`, `handoff`, `new-poc`, `new-project`,
`poc-demo`, `skillify`, `sprint-status`, `team-status`, `validate-tasks`, `validate-workflow`) —
`tests/golden/**` is a protected path (`docs/artifacts/protected-paths-v1.md`) requiring a disclosed
exception request before new cases can be authored there.

**This task does not request that exception or author new golden cases.** Authoring 14 new,
genuinely meaningful golden cases (not padding — each would need a real, representative prompt/
expected-behavior contract per command, reviewed with the same care `tests/golden/README.md`
describes for the existing 5-command suite) is a substantial, separate body of work, scoped
differently from this task's Rails/documentation/cross-reference evidence authoring. Flagging this
now, cleanly, as the single remaining well-defined gap for 14 of 17 commands (everything else about
those 14 is evidence-complete) is more honest than either forcing rushed golden cases through an
unrequested protected-path exception or silently leaving the gap undocumented.

### 5. Blockers filed

**Blocker 1 — type: `technical`, severity: `major`.** 14 of 17 Wave 2 commands cannot reach `stable`
until golden-case coverage exists for them, which requires a disclosed protected-path exception
request per `docs/artifacts/protected-paths-v1.md` — not requested in this task, per §4. Proposed
mitigation: a dedicated follow-up task (not part of Wave 2/3/4) to (a) request the protected-path
exception for `tests/golden/open/**` additions, (b) author one genuinely representative golden case
per command (14 cases), reviewed with the same rigor as the existing 5-command suite, (c) re-run
`check-maturity.py --verbose` to confirm the remaining stable-tier gap closes for those 14. This
mirrors `task-T433.md`'s own precedent of treating command golden-case authorship as expected,
separately-scoped promotion work rather than something to force into an evidence-only task.

**Blocker 2 — type: `technical`, severity: `major` (not new — cross-referencing already-open
items).** 4 agents (`context-retriever`, `devops-engineer`, `evaluation-agent`, `solution-architect`)
and 3 commands (`new-feature`, `prepare-release`, `security-audit`) remain blocked by real,
independent defects already tracked at `T456`/`T457` (agents) and the same tracked-defect golden
cases `phase3-wave1-promotion-v1.md` §3.2 already found for the orchestrator/tech-lead-owned
commands sharing this pattern. No new follow-up task is proposed here — these are already on the
ledger; this artifact only confirms they also block these specific Wave 2 components and should be
re-checked once `T456`/`T457` resolve.

**Blocker 3 (informational, not a defect) — the standard self-referential mechanism.** Per §2, this
does **not** block Wave 2's targets the way it blocked Wave 1's — flagged only so the orchestrator's
post-closure verification knows not to expect it here, and to confirm the 19 clean agents are
promotable to `stable` **immediately** upon archival, without waiting on any other resolution.

### 6. Recommended continuation, itemized

1. **19 agents ready for an immediate flip** once this task's row archives (no further evidence
   needed, verified clean against the real checker): `data-mockup-agent`, `database-engineer`,
   `demo-agent`, `feasibility-agent`, `frontend-developer`, `integration-agent`,
   `poc-devops-engineer`, `poc-orchestrator`, `poc-qa-engineer`, `poc-security-engineer`,
   `poc-technical-writer`, `product-owner`, `release-manager`, `scaffolding-agent`, `scrum-master`,
   `technical-debt-narrator`, `technical-writer`, `technology-scout`, `ux-designer`.
2. **4 agents blocked on `T456`/`T457`** (§3) — re-check once those resolve; no new evidence needed
   from this task.
3. **3 commands blocked on real tracked defects** (`new-feature`, `prepare-release`,
   `security-audit`) — re-check once their respective defects resolve; no new evidence needed from
   this task.
4. **14 commands blocked on the golden-case gap** (§4/Blocker 1) — needs a dedicated follow-up task
   with a disclosed protected-path exception request; not attempted here.

### 7. Consumed by

- **Orchestrator** — to archive `T434` and, per §6.1, flip the 19 evidence-complete agents to
  `maturity: stable` directly (no new evidence work), re-confirming via `check-maturity.py --verbose`.
- **A future follow-up task** (Blocker 1) — golden-case authorship for the 14 uncovered commands.
- **T435/T436** — should read this artifact's §2 finding before assuming the self-referential
  mechanism always applies; it is brief-content-dependent, not universal.
