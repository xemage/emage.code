# Memory consolidation — recommendations (awaiting approval)

Retrieved 11 stored memory entries (no focus area given, so the full set is in scope).
Nothing below has been executed: these are recommendations only.

| Memory key | Content summary | Recommended action | Rationale |
|------------|-----------------|--------------------|-----------|
| blocker-retry-limit | Blockers are retried at most twice before escalating, across every agent role. | Promote | Every agent brief restates this by hand; it belongs in a project-owned document, a new § Blocker protocol in `docs/wiki/architecture.md`, rather than in memory. |
| validation-gate-verdict-protocol | Validation gates use exactly three verdicts and reviewers never fix what they review. | Promote | `docs/wiki/architecture.md` § Validation gates already lists the verdicts; promote the reviewer rule there and drop the copy so the two cannot drift apart. |
| protected-branch-no-direct-commit-policy | No direct commits to `main` or `develop`, with no small-change exception. | Keep | Correctly scoped as general memory and referenced often enough to stay hot; the instruction file already carries the long form. |
| agent-tool-grant-check-discipline | Check an assignee's actual tool grants before dispatching a nested Agent call. | Keep | Still relevant and still being violated occasionally; too operational for `AGENTS.md`. |
| knowledge-vault-frontmatter-convention | How to author a vault entry the indexing pipeline will accept. | Promote | This is authoring documentation, not a recollection; promote it to a new `docs/wiki/memory-vault-authoring.md`, and propose a separate task for the shipped vault README. |
| adr-005-memory-layer-decisions | Summary of ADR-005's memory-layer decisions. | Prune | Superseded by the accepted ADR itself, which is committed and authoritative; the memory copy can only drift from it. |
| memory-scope-enforcement-mechanism | One predicate decides project-scope visibility in the memory index. | Keep | Narrow implementation detail, correctly project-scoped, and load-bearing when touching `scope_filter.py`. |
| golden-suite-no-live-model-design | The golden suite never invokes a live sampling model completion. | Keep | Directly constrains every golden-case authoring task; correctly project-scoped. |
| protected-golden-suite-paths | `tests/golden/**` and `scripts/scorecard.py` are frozen against normal improvement-task edits. | Keep | Consulted at the start of every golden-suite task; the protection document holds the detail. |
| held-out-isolation-ledger-defect-sweep | The two leak guards to run before any push. | Keep | Pre-push checklist item, correctly project-scoped, no broader audience. |
| terminal-bench-two-host-topology | Terminal-Bench trial data is split across two hosts. | Prune | Stale: describes a topology that no longer matches the current trial store layout, so acting on it would mislead. |

## Next step

Confirm which of these 11 recommendations to apply. No entry will be promoted or deleted before
that confirmation.
