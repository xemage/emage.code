# Memory Scope Model — v1

**Based on:** `docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 5 (T451 row: "Define three
enforced scopes: `general` (harness knowledge, curated), `project` (this repo only), `shared`
(cross-platform, explicit opt-in per entry). Scope is set at write time and cannot be inferred at
read time." — restated as Phase 5's own acceptance criterion: "A `project`-scoped entry is provably
unreachable from a different project's session."); `docs/plans/plan-038-phase5-detailed-planning.md`
(T451 per-task summary and task-graph dependency note — T451 must precede T452 because scope
tagging has to be designed into the indexing pipeline from the start, not retrofitted);
`docs/decisions/ADR-005-memory-layer-design.md` (accepted 2026-09-09, MR !232) — Decision 1
(git-versioned Markdown/frontmatter knowledge store as canonical source of truth, scope tag lives
in frontmatter, set at write time) and Decision 3 (read-only-by-default; canonical store and its
derived index have no live agent write path).

**Refs:** T451. Consumed by: T452 (indexing pipeline), T453 (hybrid retrieval), T454
(`@context-retriever`).

**Status:** design doc (not an ADR — no new architectural decision beyond what ADR-005 already
settled; this operationalizes ADR-005 Decision 1, it does not revisit it, per this task's own
Inputs section explaining why `docs/decisions/_template.md` does not apply here).

---

## 1. Purpose and scope of this document

This document defines, concretely enough for T452 to implement directly without re-deriving the
design, the three enforced memory scopes `plan-035` and `plan-038` name but do not yet design:
`general`, `project`, and `shared`. It covers scope definitions with example entries (§2), the
frontmatter schema (§3), the enforcement mechanism that makes `project`-scope provably unreachable
across projects while `shared`-scope remains reachable — the same mechanism producing both outcomes
(§4), the write-time-only hard rule (§5), and how this composes with ADR-005 Decision 3's
read-only-by-default principle (§6).

This is a design task, not an implementation task. No code, indexing pipeline, or actual
enforcement mechanism is built here — that is T452's job, consuming this design (per this task's
own Constraints).

## 2. The three enforced scopes

### 2.1 `general` — harness-level knowledge, curated

Knowledge about emage.code itself (the harness), not about any one project that installs or runs
it. Not project-specific by definition — there is exactly one harness repository (`emage.code`
itself), so `general`-scope entries are authored and canonically committed there, and every other
project's index build ingests them (see §4.1). "Curated" means these entries are expected to be
reviewed with a higher bar than ordinary project notes, since they are broadcast to every project
by default — but curation is an editorial/review-process concern, not part of the scope-enforcement
mechanism itself, and is out of scope for this document.

**Example entry** (`implementation/knowledge/memory/general/blocker-retry-limit.md`, in the
`emage.code` repo):

```markdown
---
scope: general
title: "Blocker retries: max 2 before user escalation"
tags: [blocker-protocol, agents-md]
---

Per `AGENTS.md`'s Blocker Protocol: agents retry a blocker at most twice before treating it as
escalation-worthy and reporting to the orchestrator. This applies harness-wide, to every agent role
and every project emage.code is deployed against — it is not a project-specific convention.
```

### 2.2 `project` — scoped to a single repository/project

Knowledge specific to one project's own codebase, history, or decisions — not portable to a
different project's session as-is. Per `plan-035`'s literal framing, `project` scope means "this
repo only": an entry's origin repository *is* its isolation boundary (see §4.1 for why this is the
actual enforcement mechanism, not merely a description).

**Example entry** (`implementation/knowledge/memory/project/terminal-bench-two-arm-design.md`, in
the `emage.code` repo):

```markdown
---
scope: project
project_id: em-age/emage.code
title: "Terminal-Bench two-arm (control/treatment) harness wiring, T407-T409"
tags: [terminal-bench, evaluation]
---

This repo measures emage.code's own contribution via `score(B) - score(A)` using Harbor's
`BaseInstalledAgent` subclass for Arm B and the built-in `claude-code` agent unmodified for Arm A,
against the stratified ~25-task subset defined in `docs/benchmarks/tb-subset.json`. This wiring
(container images, `-k` filter list, seed policy) is specific to this repo's own CI and benchmark
configuration and is not directly reusable by a sibling project with a different benchmark harness
or a different held-out task set.
```

A session working in the `sia` or `CWSO` project must never retrieve this entry — it describes
`emage.code`'s own CI wiring and would be actively misleading (or worse, a source of leaked
implementation detail) if surfaced in an unrelated project's context window.

### 2.3 `shared` — explicitly cross-platform and multi-consumer, opt-in per entry

Knowledge that originates in one project but is deliberately promoted for reuse by named other
projects and/or named coding-agent platforms. "Opt-in per entry" means: there is no scope value or
frontmatter state that defaults an entry into `shared` visibility. An entry becomes `shared` only
when its author explicitly states, in frontmatter, which projects and which platforms may read it
(§3, §4). This is deliberately more ceremony than `project` scope, because getting this wrong leaks
across a boundary the entry's own author may not have thought through at write time.

**Example entry** (`implementation/knowledge/memory/shared/two-arm-benchmark-methodology.md`,
authored in the `emage.code` repo, opted into visibility for this session's sibling projects):

```markdown
---
scope: shared
origin_project_id: em-age/emage.code
shared_consumers:
  projects: ["em-age/emage.code.cwso", "em-age/sia", "em-age/sia-harness"]
  platforms: ["claude-code", "github"]
title: "Two-arm control/treatment methodology for measuring a wrapper's contribution to an agentic
  benchmark"
tags: [evaluation-methodology, terminal-bench]
---

When benchmarking a system that wraps or configures an underlying coding agent (rather than being
an agent itself), score the wrapped agent alone (Arm A, control) and the wrapper-plus-agent
combination (Arm B, treatment) under otherwise identical conditions (same model, dataset, seed,
concurrency). `score(B) - score(A)` isolates the wrapper's own contribution; an absolute score for
Arm B alone conflates the wrapper with the underlying model's own capability and answers a
different question than "did this wrapper help." This generalizes beyond any one benchmark harness
or any one wrapped agent.
```

Note the abstraction level difference from the `project`-scope example in §2.2: the `shared` entry
states the *methodology* (reusable by a sibling project with its own benchmark harness), not
`emage.code`'s own CI wiring detail (which stays `project`-scoped). This is an authoring discipline
this document recommends but does not mechanically enforce — the mechanism in §4 enforces
*reachability*, not content quality or appropriate abstraction level.

## 3. Frontmatter schema

Extends ADR-005 Decision 1's existing frontmatter convention (Markdown entries with YAML
frontmatter under a knowledge tree analogous to `docs/`/`implementation/knowledge/`). The
scope-relevant fields:

```yaml
---
scope: general | project | shared        # REQUIRED. Exactly one of these three literal string
                                          # values, case-sensitive. No default value exists. A
                                          # missing field, an empty value, or any string other than
                                          # these three exact literals is malformed — see §5 for the
                                          # enforcement point (T452 rejects, never defaults).

project_id: <string>                     # REQUIRED if scope == project. Forbidden (must be absent)
                                          # if scope == general. Not read for shared-scope matching
                                          # (see shared_consumers.projects below) — if present on a
                                          # shared-scope entry it is ignored for matching purposes;
                                          # use origin_project_id instead for shared-scope
                                          # provenance (see below).
                                          # Convention: lowercase "<org>/<repo>" slug derived from
                                          # the project's own git remote (e.g. `git remote get-url
                                          # origin`, normalized). This repo's own remote is
                                          # `gitlab.com/em-age/emage.code`, giving "em-age/emage.code"
                                          # — the convention in this document's examples throughout.

origin_project_id: <string>              # OPTIONAL, only meaningful if scope == shared. Records
                                          # which project's repo the entry was originally authored
                                          # and committed in, for provenance/audit only. MUST NOT be
                                          # used by T452/T453 as a match key — that is
                                          # shared_consumers.projects's job. Keeping these two
                                          # fields distinct (project_id for the project-scope match
                                          # key; origin_project_id for shared-scope provenance)
                                          # prevents a future implementer from accidentally reusing
                                          # one field for two different semantics.

shared_consumers:                        # REQUIRED (the whole block) if scope == shared. Forbidden
                                          # if scope == general or project. Both sub-fields below are
                                          # individually REQUIRED when this block is present —
                                          # omitting either is malformed (see §5), not "default to
                                          # everyone."
  projects: [<string>, ...] | ["*"]      # Explicit allowlist of project_id values (same slug
                                          # convention as project_id above), or the literal
                                          # single-element list ["*"] meaning "every project." No
                                          # implicit wildcard from omission or from an empty list —
                                          # an empty list ([]) is malformed, not "no consumers."
  platforms: [<string>, ...] | ["*"]     # Explicit allowlist drawn from this repo's own 7-platform
                                          # set, as currently projected on `develop`: github, cursor,
                                          # gemini, opencode, pi, claude-code, cline (per `AGENTS.md`'s
                                          # platform-projection table), or ["*"] for all seven. Same
                                          # no-implicit-wildcard rule as projects above. Note: a
                                          # `codex` platform is being added on a separate,
                                          # still-unmerged branch (`feature/T475-codex-platform-
                                          # integration`) as of this document's authoring — this list
                                          # must be re-checked against `AGENTS.md` at T452/T454
                                          # implementation time rather than assumed frozen at 7.

title: <string>                          # Existing convention (not scope-related).
tags: [<string>, ...]                    # Existing convention (not scope-related).
---
```

## 4. The enforcement mechanism: one predicate, two outcomes

This is the mechanism T452 must implement. It is stated as a single inclusion predicate,
`include(entry, P)` — "is `entry` visible to a session belonging to project `P`" — evaluated
identically regardless of scope. The *branch* taken depends on the entry's own frontmatter data
(written once, at commit time); the *predicate itself* does not change. This is deliberate: the
task brief requires that `project`-scope unreachability and `shared`-scope reachability be produced
by the same mechanism, not two independent and potentially inconsistent ones.

### 4.1 Primary control: repo-boundary partitioning at index-build time (T452)

T452's indexing pipeline is invoked once per project, always with an explicit "building for project
`P`" identity (`P`'s own repo checkout — e.g. `git remote get-url origin`, normalized to the
`<org>/<repo>` slug convention in §3; a repo with no remote falls back to an operator-supplied
`--project-id` argument, since a bare local checkout has no other reliable identity source — this
fallback is flagged as an assumption in §9). Given that identity, T452 applies exactly one hard
rule when deciding what source material to parse, chunk, and embed into `P`'s derived index:

```
include(entry, P) :=
    if entry.scope == "general":
        true                                              # every general entry, always
    elif entry.scope == "project":
        entry was found while scanning P's own repo tree   # never any other repo's tree
    elif entry.scope == "shared":
        P ∈ entry.shared_consumers.projects                # explicit allowlist match, or "*"
    else:
        unreachable — malformed entries are rejected at parse time, before this predicate
        ever runs (see §5); there is no "else" branch that reaches the index.
```

The `project` branch is a **structural, not a filtered**, guarantee: T452 must never cross a repo
boundary to fetch `scope: project` content, under any configuration, for any reason. A
`project`-scoped entry that lives in the `sia` repo is never parsed, never chunked, never embedded,
and never written to any index T452 builds for `emage.code` or `CWSO` — it is not merely excluded
by a filter after being read, it is never read by that build at all. This is what makes
unreachability *provable*: there is no vector, chunk, or metadata row anywhere in project `P`'s
derived index that originated from a different project's `project`-scoped source material, because
the ingestion step that would have produced it never ran.

The `general` and `shared` branches are what let T452 reach outside `P`'s own repo at all: `general`
entries are always pulled from the single canonical harness source (the `emage.code` repo's own
`implementation/knowledge/memory/general/` tree — see §2.1, there is exactly one harness repo, so
there is exactly one general-scope source); `shared` entries are pulled from whichever origin
repo(s) T452 is configured to also scan, but only entries whose `shared_consumers.projects` names
`P` (or `"*"`) survive that scan — everything else found while scanning a source repo for `shared`
candidates is discarded by the identical predicate that discards a foreign `project`-scoped entry,
just landing on the `true` branch instead of the "not found in own repo" branch.

Crossing a repo boundary to fetch `general`/`shared` source material is a **read-only fetch**
(e.g. a pinned-ref `git fetch`/shallow clone of the source repo's knowledge tree, or an equivalent
read-only artifact pull) performed by T452 at build time — it never writes to the source repo, and
it is not a live per-query call; see §6 for why this is consistent with ADR-005 Decision 3.

### 4.2 Secondary control: mandatory query-time filter (defense in depth)

Even though §4.1's repo-boundary partitioning is the primary and structurally stronger guarantee
(a `project`-scoped foreign entry cannot leak because it was never ingested), T453/T454's retrieval
layer applies a second, independent check using the same predicate, evaluated against metadata
persisted on every indexed chunk at T452 build time:

- Every chunk T452 writes to any derived index carries its originating entry's `scope`,
  `project_id` (if `project`-scope), and `shared_consumers` (if `shared`-scope) as immutable
  metadata, computed once at build time.
- T453's retrieval query API requires a `requesting_context` argument
  (`{project_id, platform}`) on every call. There is no query mode, default parameter, or code
  path that omits it — an unfiltered query is not a supported operation.
- `requesting_context.project_id` and `.platform` are derived from the calling session's own
  trusted, non-user-editable context (the project the session's workspace is rooted in; the
  coding-agent platform whose projected agent config invoked `@context-retriever` — see §9 for the
  concrete derivation mechanism this document proposes for T454 to implement), never taken as
  free-text input that a query string or a user prompt could set or override.
- T453 applies `include(chunk_metadata, requesting_context)` — the identical predicate from §4.1 —
  as a **pre-filter on the candidate set**, before any semantic/lexical/structural ranking runs
  (T453's own job per ADR-005/plan-035). Filtering before ranking, not after, means an excluded
  chunk can never surface via a top-K spillover or a ranking-stage bug; it is removed from the
  candidate pool entirely, the same "structural absence" property §4.1 gives the primary control.

Because even in a hypothetical future migration to the server-side vector-DB alternative ADR-005
names as the documented upgrade path (Decision 1's Alternatives table — a single mutable index
serving many concurrent readers), repo-boundary partitioning at ingestion time may no longer be
available as a standalone guarantee if multiple projects' content is consolidated into one physical
index. The query-time filter in this section is what continues to hold in that scenario, as long as
per-chunk scope metadata continues to be written at build time — this is why it is specified now,
not deferred until such a migration is actually proposed.

### 4.3 Why one mechanism, not two

Both §4.1 and §4.2 apply the exact same `include(entry, P)` predicate. The only thing that differs
between a `project`-scoped entry (excluded from every other project) and a `shared`-scoped entry
(included for its named consumers) is the **frontmatter data written at commit time** —
`entry.scope` and, depending on that value, either "which repo this file lives in" or
`entry.shared_consumers.projects`. There is no separate "exclusion mechanism" for `project` and a
separate "inclusion mechanism" for `shared`; there is one function, and scope-specific frontmatter
data determines which branch it takes for a given `(entry, P)` pair. This satisfies the task
brief's explicit requirement that the same mechanism produce both outcomes, not two independent and
potentially-inconsistent ones.

## 5. Write-time-only: the hard rule

**Scope, `project_id`, and `shared_consumers` are computed exactly once, at T452's index-build
time, from the frontmatter of the canonical git commit being indexed. They are never inferred,
guessed, recomputed, or overridden at query/read time, by any component, for any reason.**

Concrete enforcement point, per this task's own acceptance criteria: T452's parser applies this
rule to every entry, before that entry is eligible for §4.1's `include()` predicate at all:

- If `scope:` is missing, empty, or not exactly one of `general` / `project` / `shared`
  (case-sensitive) → **reject the entry.** It is not written to any derived index, for any
  project, under any circumstances. It does not default to `general` (the least-restrictive
  scope) or to `project` (the most-restrictive). T452 logs the rejection (source file path, commit
  SHA, reason) as part of its build output, the same way a linter reports a failing file — this is
  an auditable, non-silent failure, not a swallowed one.
- If `scope: project` and `project_id:` is missing or empty → **reject the entry**, same terms as
  above.
- If `scope: shared` and `shared_consumers:` is missing, or either of its two sub-fields
  (`projects`, `platforms`) is missing or an empty list → **reject the entry**, same terms as
  above. This is what makes "opt-in per entry" (§2.3) a mechanically enforced property rather than
  an authoring convention: there is no way for an entry to end up `shared`-visible without its
  author explicitly enumerating consumers, because an incomplete `shared_consumers` block is
  treated as malformed input, not as an implicit "share with everyone" or "share with no one."

Once an entry passes this check and is written into a derived index as a chunk with its scope
metadata attached, T453 (retrieval) and T454 (`@context-retriever`) read that metadata strictly as
a **read-only filter key** — never as a hint to be combined with, reinterpreted by, or overridden
by anything observed at query time (the querying session's own project, the content of the query
string, a relevance score, or any other runtime signal). Concretely: there is no code path in T453
or T454 that computes or mutates a chunk's `scope`/`project_id`/`shared_consumers` fields; those
fields exist only as the output of T452's build step and are treated as immutable once written. If
a scope assignment needs to change, the fix is a normal git commit correcting the entry's
frontmatter, followed by a normal index rebuild (§4.1) — never a live, in-session patch.

## 6. Composition with ADR-005 Decision 3 (read-only-by-default)

This design introduces no new write path, and is fully expressible using only the two write paths
ADR-005 Decision 1/3 already define:

1. **The canonical store's write path**: ordinary git commits, reviewed via merge request
   (`.claude/rules/git-workflow.md`). This is the *only* way an entry's `scope`,
   `project_id`, or `shared_consumers` frontmatter is ever set or changed. Nothing in this
   document adds a second way to set these fields.
2. **The derived index's write path**: T452's indexing pipeline, run as an explicit, auditable
   rebuild step (ADR-005 Decision 3: "not a live call any agent can trigger mid-session"). §4.1's
   read-only cross-repo fetch (pulling `general`/`shared` source material from another project's
   repo to build `P`'s own index) is itself read-only against the *source* repo — it never
   commits, pushes, or otherwise mutates the repo it reads from. It only produces local input to
   T452's own already-sanctioned rebuild-write of `P`'s derived index.

`@context-retriever` (T454) remains read-only in two independent senses that compose without
conflict: ADR-005 Decision 3's sense (it never writes to the canonical store or the derived index,
enforced by the three-place `ALLOW_WRITE=false` assertion already specified there), and this
document's sense (it never writes, mutates, or overrides scope metadata on what it reads — §5). A
rejected entry (§5) is never silently "fixed up" by `@context-retriever` at query time; it simply
never appears in any index for it to retrieve in the first place.

## 7. What this does not do (scope boundary)

Following the precedent this repo already established for a similar declarative-plus-auditable
control (`docs/artifacts/protected-paths-v1.md` §4):

- This document does not implement T452, T453, or T454. It specifies the contract those tasks must
  satisfy; building the actual parser, filter, and query API is explicitly out of scope for T451
  (per this task's own Constraints).
- The `general`-scope curation bar mentioned in §2.1 (review rigor for entries that are broadcast
  to every project by default) is an editorial/process concern, not a mechanical enforcement
  point. This document does not define a curation review process.
- Content-quality or appropriate-abstraction-level authoring discipline (e.g. the §2.3 note that a
  `shared` entry should state a generalizable methodology rather than one project's specific
  wiring) is a recommendation, not something §4's mechanism checks or can check. The mechanism
  enforces *who can reach* an entry; it says nothing about whether that entry's content was written
  at the right level of abstraction for its declared audience.
- This document does not resolve where the general-knowledge canonical source physically lives
  beyond "the `emage.code` repo's own knowledge tree" (§2.1, §4.1) — if a future decision moves
  general-scope content to a dedicated repo separate from `emage.code` itself, T452's read-only
  cross-repo fetch mechanism (§4.1, §6) already accommodates that without a redesign, but this
  document does not mandate it.

## 8. Verification (proposed; for T452/T453/T454 to build, not built here)

Per this task's own acceptance criteria ("concrete enough for T452 to implement... without
re-deriving the mechanism"), the following checks are the concrete, testable expression of this
design — named here so T452/T453/T454's own briefs can adopt them directly, mirroring the
adversarial-probe verification pattern already established for this repo's protected-paths (T416)
and the three-place `ALLOW_WRITE=false` live-test already specified for T454 in ADR-005:

- **Write-time rejection test** (T452): a synthetic entry with a missing/malformed `scope:` field
  is fed to the indexing pipeline; assert it is absent from the resulting index and appears in the
  pipeline's rejection log, not defaulted to any scope.
- **Opt-in completeness test** (T452): a synthetic `scope: shared` entry with an incomplete
  `shared_consumers` block (missing `platforms`, or an empty `projects` list) is rejected on the
  same terms.
- **Cross-project unreachability probe** (T452 + T453, adversarial, mirroring T416's live-removal
  probe pattern): build project `P1`'s index against a fixture repo containing a `project`-scoped
  synthetic entry; build project `P2`'s index against a separate fixture repo; assert `P2`'s index
  contains zero chunks originating from `P1`'s `project`-scoped fixture entry, and that a `P2`
  session's retrieval query (§4.2) returns zero hits for it even if a hostile query is crafted to
  target its exact content.
- **Shared-scope reachability probe** (same fixtures): assert a `shared`-scoped synthetic entry
  naming `P2` in `shared_consumers.projects` *does* appear in `P2`'s index and *is* retrievable by
  a `P2` session, confirming the same build/predicate that produced the negative result above
  correctly produces the positive result for the entry that opted in.
- **No-write-path confirmation** (T454, extending ADR-005's own three-place `ALLOW_WRITE=false`
  live test): attempt to have `@context-retriever` write or patch a chunk's scope metadata through
  any exposed tool call; confirm it is rejected at all three of ADR-005 Decision 3's existing
  assertion points, and additionally confirm no tool call exists that would let it set scope in the
  first place (§5, §6).

## 9. Assumptions and flagged ambiguities (per this task's Blocker Protocol)

Per this task's Blocker Protocol ("if ADR-005's Decision 1 turns out to be underspecified for a
concrete scope-enforcement mechanism... that is a `type: unclear_requirements`, `severity: minor`
finding to report alongside a proposed resolution — not a reason to block"), the following two
points are genuine ambiguities in ADR-005/plan-038 that this design resolves by explicit,
flagged choice rather than by silently guessing:

1. **Whether the canonical store is one shared vault repo or a tree replicated per project.**
   ADR-005 Decision 1 describes "a knowledge tree analogous to this repo's existing `docs/`/
   `implementation/knowledge/` convention" without stating whether that tree is singular
   (one central repo all projects point at) or per-project (each project's own repo carries its
   own tree). This document resolves it as **per-project**, with `general` living in the single
   harness repo (`emage.code`) and `shared` crossing repo boundaries only via explicit
   `shared_consumers` — because this is the only reading consistent with `plan-035`'s own literal
   phrase "`project` (this repo only)" and because it is what makes §4.1's repo-boundary control
   possible as a *structural* (not merely filtered) guarantee, which is the strongest available
   reading of "provably unreachable." **Proposed resolution:** adopt this reading; if a future ADR
   revisits Decision 1 and picks a single shared vault instead, §4.2's query-time filter (already
   specified as an independent, non-redundant-with-§4.1 control) continues to hold without
   modification — only §4.1's cross-repo-fetch step would need to change to "select rows for `P`"
   instead of "fetch from `P`'s own repo."
2. **How `project_id`/`platform` are derived at query time in a non-spoofable way.** Neither
   ADR-005 nor `plan-038` specifies how a session's project/platform identity is established for
   T454 to pass into T453's `requesting_context` (§4.2). This document proposes: `project_id` from
   the session's own workspace git remote (normalized `<org>/<repo>` slug, §3), with an
   operator-supplied fallback for remoteless checkouts; `platform` from a build-time-injected
   constant in each platform's own projected agent config (the same mechanism `sync.mjs` already
   uses to produce platform-specific projections from the 27 source agent definitions), not a
   runtime-settable parameter. **Proposed resolution:** T454's own brief should adopt this
   derivation explicitly, since T454 (not T451) is the task that actually implements the agent
   surface this identity flows through.

Neither point blocked production of this design; both are flagged here and in the completion report
per the Blocker Protocol's instruction to propose a concrete resolution rather than stall.

## 10. Handoff to T452

T452's indexing pipeline must, at minimum:

1. Parse every candidate entry's frontmatter and apply §5's write-time validation before any
   further processing — reject, log, and exclude on any violation.
2. Accept an explicit "building for project `P`" identity as an input (§4.1), never inferred from
   the content being indexed.
3. Apply the `include(entry, P)` predicate (§4.1) while deciding what to chunk/embed: same-repo
   `project`-scope entries always included; the single harness repo's `general`-scope entries
   always included; other repos' `shared`-scope entries included iff `P` is named in
   `shared_consumers.projects` (or it is `["*"]`).
4. Persist `scope`, `project_id` (if any), and `shared_consumers` (if any) as immutable metadata on
   every resulting chunk, for T453's query-time filter (§4.2) to consume.
5. Never write back to any source repo it reads from (§6) — cross-repo fetches for `general`/
   `shared` material are read-only.

This is the complete contract; T452 should not need to re-derive any part of §4's mechanism from
first principles.
