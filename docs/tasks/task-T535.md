# T535 — Adjudicate `/batch` step 5's manifest against the ledger schema

**ID:** T535
**Owner:** Solution Architect
**Status:** in_review
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** T528 (merged 2026-09-26)
**Created:** 2026-09-26
**Based on:** `docs/plans/plan-076-wave2-findings.md` §1;
`docs/decisions/ADR-007-command-contract-authority.md`; `AGENTS.md` § Task Protocol;
`docs/artifacts/protected-paths-v1.md` §5; `docs/tasks/task-T528.md`.

## 1. Owner has no shell — hand back uncommitted

`implementation/knowledge/agents/solution-architect.md` declares
`tools: [read, search, edit, web, todo, ...]` — **no `execute`**. Do not attempt or claim to run any
command. Write your files and **hand back uncommitted**; the orchestrator runs every gate and commits
on your behalf, and says so publicly. Stated here rather than discovered at dispatch, because four
briefs in this phase got this wrong.

## 2. The conflict

`implementation/knowledge/commands/batch.md` step 5 declares a five-field manifest written into
`docs/tasks/active-tasks.md`:

> 5. **Track progress** — update `docs/tasks/active-tasks.md` with the full batch manifest: Unit ID,
>    description, assigned agent, branch, status

`AGENTS.md` § Task Protocol pins that file to exactly `ID`, `Title`, `Owner`, `Status`, `Priority`,
`Depends on`, `Last update`, and `docs/tasks/validate-tasks.py` **hard-fails any other cell count**
(`if len(row.cells) != 7`).

**Four of the five fields map onto that schema. `branch` maps onto nothing, and the two spare columns
are taken.** The manifest cannot be written where step 5 says to write it.

A second collision sits behind it: `U<n>` unit IDs fail `ID_RE = ^T\d{3,}$`, and `bug-report.md`
records that non-`T` rows are **silently deleted by `install.sh --update`**.

`tests/golden/open/batch-manifest-ledger-schema-conflict` is `known_failing` / `tracked_defect` on
this and is the only thing keeping `command/batch` off `stable`.

## 3. Your task — and what I am deliberately not telling you

Produce an adjudication under `ADR-007`, then execute it.

**`AGENTS.md` outranks a command file, so branch 1 may genuinely fire** — amend the command. Verify
that rather than taking it from me. But **branch 1 firing does not tell you *how* to amend it**, and
that is the real question:

- A batch of parallel units plausibly *needs* somewhere to record branches. "Delete the requirement"
  may be the wrong repair even if the contract is the thing that must change.
- A separate manifest document (`docs/plans/`? a batch-scoped file?) would satisfy step 5's intent
  without touching the ledger schema.
- Amending `active-tasks.md`'s schema is an **`AGENTS.md` amendment** — a much larger decision, with
  `validate-tasks.py`, every projection and 330 completed rows downstream of it.
- `branch` may be **derivable** rather than needed: agent branches already follow
  `agent/<name>/<task-id>` per `git-workflow.md`.

**I am not telling you which is right.** A verdict that reaches "amend the command to drop `branch`"
*having argued it on the merits* is a good outcome. One that reaches there because it was the
smallest edit is not, and `ADR-007` §5 — never resolve by relaxing a check — binds that distinction.

**State plainly whether `/batch` ends promotable.** "It does not" is an acceptable outcome.

## 4. Deliverables

1. `docs/artifacts/batch-manifest-resolution-v1.md` — the adjudication, following
   `docs/artifacts/command-contract-resolution-v1.md`'s shape: which branch fires, why, what each
   option implies, and what you rejected.
2. The execution of your verdict.
3. Set this brief's `**Status:**` to `in_review`. Touch no ledger row.

## 5. PROTECTED-PATH AUTHORIZATION — conditional and narrow

**Authorized under `protected-paths-v1.md` §5.2, limited to exactly:**

| Path | Permitted change |
|---|---|
| `tests/golden/open/batch-manifest-ledger-schema-conflict/case.yaml` | `status` flip and removal of the `known_failing_*` keys — **only if** your verdict genuinely makes `check()` return `True` |
| `tests/golden/open/batch-manifest-ledger-schema-conflict/brief.md` | restate the expected outcome to match |

**`expect.py` is NOT authorized.** If your verdict changes what the case must check, the checker must
be re-derived — a wider grant than you hold. **Stop and report a blocker**; do not edit this table.
`T520`, `T523`, `T525`, `T527` and `T531` all hit this boundary and all five refused; `T527`'s
refusal on the equivalent file is why a follow-up task existed at all.

`scripts/scorecard.py`, every other case and all of `tests/golden/held-out/` are excluded.

**Since you cannot run the checker, do not flip `case.yaml` on a guess.** If you believe the case
would now pass, say so and explain precisely why, and let the orchestrator verify by running
`check()` before anything flips.

## 6. If you amend anything under `implementation/knowledge/`

The platform projections under `.claude/`, `.github/`, `.gemini/` etc. are **generated**. Do not
hand-edit them — the orchestrator re-runs `node implementation/scripts/sync.mjs` **and**
`python3 implementation/scripts/generate-registry.py`. Note both are needed: `sync.mjs --check` alone
does not catch registry drift, and forgetting the second has broken two MRs in this phase.

## 7. Blockers

Type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity
(`critical` | `major` | `minor`). Max 2 retries. Never widen §5 — report instead. Report anything the
brief got wrong: briefs in this phase have been wrong six times and **every time the implementer
caught it**.
