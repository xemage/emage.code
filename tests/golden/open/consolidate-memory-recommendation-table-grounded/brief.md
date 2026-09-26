# Case: consolidate-memory-recommendation-table-grounded

## Command under test
`/consolidate-memory`

## Brief (illustrative — not executed live)
"Consolidate memory — it has not been reviewed in a while and some of it is stale." No focus area
is given, so the full stored set is in scope. A recommendation table is produced for approval.

## What this checks
`implementation/knowledge/commands/consolidate-memory.md` `## Instructions` steps 1, 2 and 3,
verbatim:

> 1. **Read all MCP Memory entries** — use `mcp__memory` to retrieve the full set of stored memories. If a focus area is provided, filter to that category.
> 2. **Categorize each entry** — assign one of:
>    - **Keep** — still relevant, correctly scoped, leave in memory
>    - **Promote** — frequently referenced or broadly useful; should be elevated to `AGENTS.md`, project docs, or skill files
>    - **Prune** — stale, obsolete, superseded, or duplicated; safe to remove
> 3. **Present recommendations** — show a table with:
>    - Memory key/identifier
>    - Current content summary (one line)
>    - Recommended action (Keep / Promote / Prune)
>    - Rationale (why this action)

**The load-bearing assertion is the conjunction of steps 1 and 2, and it is why this case is worth
having.** Step 1 says the table is produced by retrieving *the full set* of stored memories, and
step 3 says the table presents a recommendation per entry. Together they make the table's coverage
checkable in both directions against the retrieved set:

- **No invented key.** Every key in the table must resolve to an entry that was actually retrieved.
  A consolidation table naming a memory that does not exist is the one failure mode a reader cannot
  catch by eye — `blocker-retry-limit` and `blocker-retry-policy` look equally plausible, and a
  confident `Prune` recommendation against a key that does not exist is indistinguishable from a
  real one without resolving it.
- **No silently dropped entry.** Every retrieved entry must appear. An entry omitted from the table
  is an entry that step 4 can never approve an action for, so it survives consolidation by
  accident rather than by a `Keep` decision. This is strictly worse than recommending `Keep`,
  because it is invisible: the table looks complete.

Step 2's contribution is the action vocabulary. The three categories are declared by name, so an
action cell reading `Archive`, `Merge`, `Review` or `Keep?` is outside the declared set, and the
check rejects it rather than accepting any non-empty string.

### Two readings deliberately not asserted

- **Step 3's column headings are not checked as literal strings.** Step 3 declares four columns by
  *content* ("Memory key/identifier", "Current content summary (one line)", ...) and never declares
  header labels, so requiring an exact header row would assert a contract the command does not
  state. The check instead requires a four-column table whose header cells each identify the
  declared concept (key/identifier, summary/content, action/recommendation, rationale/why). This
  reading is permissive by intent; the assertions that carry the case are coverage and vocabulary,
  not labels.
- **Step 4 ("Wait for user approval") is not checked at all.** It is a human interaction with no
  declared artifact, in the same way `/skillify`'s `### Present for Approval` is. Asserting an
  "awaiting approval" marker would be asserting a heading this command never declares. The fixture
  contains such a marker because a real run would, but `expect.py` does not require it — and a case
  must not check what its command does not promise.

## Pass condition
`fixture/recommendations.md` contains at least one 4-column pipe table whose header cells identify
Memory key, content summary, recommended action and rationale; every data row's action cell is
exactly one of `Keep`, `Promote`, `Prune`; every data row's key resolves to an `entries[].key` in
`fixture/memory-entries.json`; every key in that file appears in exactly one data row; and every
row's summary cell is non-empty and single-line and its rationale cell is non-empty.

## Provenance
**Entry set: real content.** `fixture/memory-entries.json`'s 11 entries are generated from this
repository's own real durable memory entries — every `key`, `scope`, `title` and `tags` value is
read out of the frontmatter of the corresponding `implementation/knowledge/memory/{general,project}/*.md`
file, and `source_path` records which. Reproducible with:

```
python3 - <<'PY'
import re
from pathlib import Path
for p in sorted(Path("implementation/knowledge/memory").rglob("*.md")):
    if p.name == "README.md":
        continue
    fm = re.match(r"^---\n(.*?)\n---\n", p.read_text(encoding="utf-8"), re.DOTALL)
    if fm:
        print(p.stem, "|", re.search(r"^scope:\s*(\S+)", fm.group(1), re.M).group(1))
PY
```

**Framed as a retrieval result, which is a documented stand-in.** Step 1 names `mcp__memory` as the
store. MCP Memory contents are live per-session server state and are *by construction* never a
committed repository artifact, so no real retrieval dump exists anywhere in this repo to copy. The
fixture therefore presents the repo's real durable memory-layer entries as the retrieved set. This
substitution is sound for what the case asserts: every assertion is about the *relationship*
between a retrieved entry set and the table that covers it, and none depends on which store the set
came from.

**`recommendations.md` is hand-authored**, as the agent-side output under test. A corpus survey
(`grep -rl "Recommended action" --include=*.md .`) returned 11 matches; every one is either
`implementation/knowledge/commands/consolidate-memory.md` itself or one of its 10 platform
projections under `implementation/.{claude,gemini,github,opencode,pi}/` and the installed
`.{claude,gemini,github,opencode,pi}/` — i.e. every hit is the command's own declared template and
**zero are produced output**. Excluding those paths leaves an empty result set: no real
`/consolidate-memory` output has ever been committed here, so there was nothing real to source this
file from. That absence is documented rather than worked around, following
`new-feature-plan-doc-compliant/brief.md`'s precedent. The recommendations themselves are plausible
editorial judgements over real entries; the check does not grade them, only their structure,
vocabulary and coverage.
