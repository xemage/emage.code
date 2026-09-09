# Task T451 — Three enforced memory scopes (general / project / shared)

**ID:** T451
**Owner:** solution-architect
**Status:** done
**Priority:** P0
**Depends on:** T450 (done — `docs/decisions/ADR-005-memory-layer-design.md`, status `Accepted`)
**Created:** 2026-09-09
**Completed:** 2026-09-09
**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 (T451 row — enforced
scope model, "scope is set at write time and cannot be inferred at read time" acceptance
criterion); `docs/plans/plan-038-phase5-detailed-planning.md` (approved, MR !228, merged
`develop`) — specifically its T451 per-task summary and task-graph dependency note; `docs/
decisions/ADR-005-memory-layer-design.md` (accepted 2026-09-09, MR !232) — Decision 1 (git-
versioned Markdown/frontmatter knowledge store, scope tag lives in frontmatter, set at write
time) and Decision 3 (read-only-by-default; no agent write path into the canonical store).

## Objective

Define, as an explicit scope-enforcement design, the three enforced memory scopes `plan-035`
and `plan-038` already name but do not yet design in detail:

1. **`general`** — harness-level knowledge, curated (not project-specific).
2. **`project`** — scoped to a single repository/project; must be provably unreachable from a
   different project's session.
3. **`shared`** — explicitly cross-platform (Claude Code, Codex, Gemini, etc. — this repo's
   7-platform projection model) and multi-consumer (readable by more than one concurrent agent
   session); entry into this scope is opt-in per entry, not a default.

The design must build directly on ADR-005's Decision 1 (frontmatter-tagged, git-versioned
Markdown store as canonical source of truth) — scope is a frontmatter field set at authoring/
commit time, enforced by whatever mechanism T452's indexing pipeline and T453's retrieval layer
consume, not inferred, guessed, or overridable at query/read time.

## Context

Phase 5 (Persistent Memory/RAG, T450-T456) was approved by the user via `plan-038` (MR !228,
merged `develop`). T450 (the phase's first task) produced ADR-005, and the user approved all
three of its decisions this session — ADR-005's Status field was flipped from `proposed` to
`Accepted` (MR !232, merged `develop`) immediately before this task's dispatch. T451 is next in
`plan-038`'s dependency graph: T452 (indexing pipeline) depends on both T450's ADR (embeddings/
storage decisions — already resolved, no cost-authorization gate applies per ADR-005 Decision 2)
and this task's scope model, because `plan-035`'s own acceptance criterion ("scope is set at
write time and cannot be inferred at read time") means scope tagging must be designed into the
indexing pipeline from the start — retrofitting scope onto an already-built indexer is exactly
the failure mode `plan-038` flags as being guarded against.

Latest checkpoint context: T450's closure note in `docs/tasks/completed-tasks.md` (this
orchestrator's own independent verification of ADR-005's SoloMD/embeddings claims, dated
2026-09-09) and this session's ADR-005 status-flip commit.

## Inputs

- `plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 (task table; scope-related acceptance
  criterion: "A `project`-scoped entry is provably unreachable from a different project's
  session")
- `plan-038-phase5-detailed-planning.md` — T451 per-task summary ("Objective," "Inputs,"
  "Outputs," "Acceptance criteria (summary)" subsections) and the task-graph dependency
  reasoning explaining why T451 must precede T452
- `docs/decisions/ADR-005-memory-layer-design.md` (accepted) — Decision 1 (storage substrate:
  git-versioned Markdown/frontmatter store, canonical writes only via reviewed MRs) and
  Decision 3 (read-only-by-default; canonical store and its derived index have no live agent
  write path)
- `docs/decisions/_template.md` is not applicable here — this task's output is a design doc, not
  a new ADR (no new architectural decision is being made beyond what ADR-005 already settled;
  this task operationalizes ADR-005's Decision 1, it does not revisit it)

## Constraints

- Token budget: 30k (per `plan-038`'s own per-task budget table)
- File ownership: this task may only create the scope-enforcement design doc (suggested path:
  `docs/artifacts/memory-scope-model-v1.md`, following this repo's existing `docs/artifacts/*-v1.md`
  naming convention — e.g. `docs/artifacts/protected-paths-v1.md`, `docs/artifacts/mcp-platform-
  contract-v1.md`). Do not touch `tests/golden/**`, `scripts/scorecard.py`, `docs/benchmarks/
  tb-subset.json`/`.md` (frozen, unrelated to this task). Do not modify `plan-035`, `plan-038`,
  ADR-005, or any other existing plan/checkpoint/ADR — this task documents a new design artifact,
  it does not revise prior ones.
- Do not touch `.mcp.json` anywhere, for any reason.
- Work in your own worktree/branch: `agent/solution-architect/T451`, created from `develop`. Do
  not self-merge — push and stop; the orchestrator reviews and merges after independent
  verification.
- This task is a design task, not an implementation task — no code, no indexing pipeline, no
  actual enforcement mechanism is built here (that is T452's job, consuming this design). Do not
  presuppose T452's implementation language or storage engine beyond what ADR-005 already fixed
  (git-versioned Markdown/frontmatter).

## Expected Outputs

- `docs/artifacts/memory-scope-model-v1.md` (or equivalent name, stated explicitly in the
  completion report if different), covering, at minimum:
  - The three scopes' definitions (`general` / `project` / `shared`), each with a concrete
    example entry.
  - The frontmatter schema for the `scope:` field (and any scope-qualifying fields the `shared`
    scope's "explicit opt-in per entry" requirement needs — e.g. which platforms/consumers may
    read a given `shared` entry).
  - The enforcement mechanism: how a `project`-scoped entry is made provably unreachable from a
    different project's session (e.g. path/namespace partitioning at index-build time, a
    project-identity check at query time, or both) — stated concretely enough that T452 could
    implement it without re-deriving the design.
  - An explicit statement that scope is set at write time only and cannot be inferred, guessed,
    or overridden at read/query time — the literal `plan-035` acceptance criterion.
  - How this design composes with ADR-005 Decision 3 (read-only-by-default): scope enforcement
    must not introduce any write path into the canonical store or its derived index.

## Acceptance Criteria

1. All three scopes (`general`, `project`, `shared`) are defined with a concrete example entry
   each — not left abstract.
2. The design states, concretely, how a `project`-scoped entry is provably unreachable from a
   different project's session — this is `plan-035`'s own literal Phase 5 acceptance criterion
   and must be addressed as a specific mechanism, not asserted as an outcome.
3. The design states, concretely, how `shared`-scope entries remain reachable across projects/
   platforms while `project`-scope entries do not — the same mechanism must produce both
   outcomes correctly, not two independent, potentially-inconsistent mechanisms.
4. The design states explicitly that scope is set at write time and cannot be inferred or
   overridden at read time — stated as a hard rule with a concrete enforcement point (e.g. "the
   indexing pipeline rejects any entry with a missing or malformed `scope:` frontmatter field
   rather than defaulting it"), not just restated as prose.
5. The design explicitly builds on ADR-005 Decision 1's frontmatter-tagged git-versioned store
   (not a different storage substrate) and does not introduce any write path inconsistent with
   ADR-005 Decision 3's read-only-by-default principle.
6. The design is concrete enough for T452 (indexing pipeline) to implement scope tagging and
   enforcement directly from it, without needing to re-derive the mechanism — this is the actual
   test of "execution-ready," per `plan-038`'s own stated goal for this planning granularity.

## Blocker Protocol

Report any blocker with `type` (`technical` | `dependency` | `unclear_requirements` |
`external`) and `severity` (`critical` | `major` | `minor`) per `AGENTS.md`'s Blocker Protocol.
Max 2 retries before escalating to the orchestrator. If ADR-005's Decision 1 (storage substrate)
turns out to be underspecified for a concrete scope-enforcement mechanism (e.g. no clear
existing directory/namespace convention to partition by project), that is a `type:
unclear_requirements`, `severity: minor` finding to report alongside a proposed resolution — not
a reason to block without proposing a concrete design of your own.

## Execution notes

## Completion addendum (2026-09-09)

`docs/artifacts/memory-scope-model-v1.md` published (MR !235, squash-merged `develop`, commit
`0098068`). All 6 acceptance criteria met:

1. All three scopes (`general`/`project`/`shared`) defined with a concrete example frontmatter
   entry each (§2.1-2.3).
2. `project`-scope provable unreachability stated as a concrete mechanism, not asserted: T452's
   indexing pipeline never crosses a repo boundary to ingest another project's `scope: project`
   material — a *structural* absence (never parsed/chunked/embedded), not a post-hoc filter (§4.1).
3. The same `include(entry, P)` predicate also produces `shared`-scope cross-project/cross-platform
   reachability (§4.1, §4.3 explicitly argues "why one mechanism, not two") — not two independent,
   potentially-inconsistent mechanisms.
4. Write-time-only scope assertion stated as a hard rule with a concrete enforcement point: T452
   rejects (logs, excludes) any entry with missing/malformed `scope:`, `project_id`, or
   `shared_consumers` rather than defaulting it to any value (§5).
5. Builds directly on ADR-005 Decision 1 (frontmatter-tagged, git-versioned store) and stays
   consistent with Decision 3 (read-only-by-default) — no new write path introduced; explicit
   composition section (§6).
6. Concrete enough for T452 to implement directly: §10 "Handoff to T452" states a 5-point
   implementation contract; §8 names five concrete verification checks (write-time rejection,
   opt-in completeness, cross-project unreachability probe, shared-scope reachability probe,
   no-write-path confirmation) for T452/T453/T454's own future briefs to adopt.

Two assumptions flagged explicitly in the design's own §9, per this task's Blocker Protocol (not
silently guessed): (1) canonical store is per-project (each project's own repo carries its own
knowledge tree), not one shared vault — the reading most consistent with `plan-035`'s literal
"`project` (this repo only)" phrasing and the one that makes §4.1's structural guarantee possible;
(2) `project_id`/`platform` query-time derivation proposed as git-remote-derived and
build-time-injected respectively, non-spoofable by design, left for T454's own brief to adopt.

**Tool-grant note, recurring, same disposition as after T420 (`checkpoint-022`):** the dispatched
`solution-architect` again had no Bash grant and could not commit, push, or run `tests/run.py`
itself — it wrote the design content in full to disk and transparently flagged the gap rather than
fabricating a commit or test transcript, exactly per its brief's Blocker Protocol. Per
`completed-tasks.md`'s own T420 closure note ("solution-architect's tool grant is intentionally
left unchanged again... by design, not a bug" — citing `security-guidelines.md`'s "Architect —
read-only for implementation code" classification), the orchestrator again makes the same decision
on the same grounds: **the tool grant stays unchanged.** This is a third confirmed instance of the
same, expected pattern, not a defect to fix. Task briefs should continue to route
Bash-verification/commit steps to the orchestrator or a Bash-capable agent, not to
`solution-architect`.

**Orchestrator independent verification, before merging** (not accepted on the agent's self-report
alone): read the full design doc end-to-end against all 6 acceptance criteria above (not spot-checked
— every section read). Found and corrected three factual inaccuracies the agent could not
self-check without Bash/WebFetch access to this repo's actual state: (1) a citation attributed to
`ADR-005` ("Repo audited: github.com/xemage/emage.code @ develop") that does not appear anywhere in
ADR-005 — grepped ADR-005's full text directly, zero match; the quote is actually from `plan-035`
(confirmed by direct grep), and even `plan-035`'s own version uses a stale `github.com/xemage/...`
URL that does not match this repo's real `gitlab.com/em-age/emage.code` remote (confirmed via
`git remote -v`); (2) every `project_id`/`shared_consumers` example in the document used the same
non-existent `xemage` org slug — corrected throughout to the real remotes, independently confirmed
by checking `git remote -v` in this repo and in the three sibling project checkouts
(`em-age/emage.code`, `em-age/emage.code.cwso` — not "CWSO", `em-age/sia`, `em-age/sia-harness`);
(3) the platform allowlist example and schema comment listed `codex` as though already part of this
repo's live 7-platform set on `develop`, when `codex` support is still unmerged on
`feature/T475-codex-platform-integration` (out of scope for this entire session per explicit user
constraint) — confirmed by reading `AGENTS.md` directly on `origin/develop` (7-platform set there is
`github, cursor, gemini, opencode, pi, claude-code, cline`, no `codex`); corrected the list to
develop's actual current set with an explicit note to re-check at T452/T454 implementation time
rather than treat it as frozen. All three corrections are narrow, factual, and unambiguous — not new
design decisions — consistent with this repo's established T420/T410 precedent for orchestrator
fixes on a Bash-less `solution-architect`'s behalf. Ran `python3 tests/run.py` fresh after applying
corrections (379 tests, `OK`, `skipped=17`, no regressions) and `python3 docs/tasks/
validate-tasks.py` (`PASS`) before committing. Confirmed CI green (5/5 jobs) on the artifact's own
MR (!235) before merging.

**ADR-005 Approval-section follow-up (separate, small MR !234, already merged before this task's
own MR):** the ADR's `## Approval` section (prose stating "proposed, not accepted," three unchecked
decision checkboxes, and a "should not be dispatched" line) was stale against the header's
`Accepted` status and against T451 already being dispatched. Fixed in a narrow, standalone
follow-up matching MR !232's own discipline — prose updated to state approval, all three checkboxes
checked, the "should not be dispatched" line corrected. Nothing else in the ADR touched.

T452 (indexing pipeline) is next in `plan-038`'s dependency graph — both its dependencies (T450,
T451) are now done — but is **not dispatched** in this session yet; see `active-tasks.md` for
current status.
