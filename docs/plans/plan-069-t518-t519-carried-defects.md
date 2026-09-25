# plan-069 — T518 and T519: the two carried defects from checkpoint-036

**Status: scoped 2026-09-25, awaiting approval to dispatch.**
Based on: `docs/checkpoints/checkpoint-036-phase9-partial-and-mcp-syntax-fix.md` § "Carried debt, unfixed".

## 0. Origin

`checkpoint-036` recorded two defects as carried debt without tasks against them. The user asked for
both to be given tasks. This document scopes them; neither is part of `plan-064` Phase 9, and neither
blocks it.

## 1. `T518` — `install.sh --update` is destructive

Two distinct sub-defects share one trigger.

**A. `.claude/settings.json` is deleted.** `sync_tree_into()` runs `rsync -a --delete`, and
`implementation/.claude/` has no `settings.json`, so the target's copy is swept. The fix mechanism
already exists one call site away: `.gemini` passes `settings.json` as an exclude at `install.sh:393`
while `.claude` passes nothing at `:408`.

**B. `active-tasks.md` loses its prose and gains a false claim.** `merge-task-docs.py` preserves
ledger table *rows* and discards surrounding *prose*, substituting the template's. Reproduced
directly:

```
BEFORE  active-tasks.md:    65 lines, 0 rows, 0x "ledger starts EMPTY"
AFTER   active-tasks.md:    11 lines, 0 rows, 1x "ledger starts EMPTY"
        completed-tasks.md: 316 rows -> 316 rows  (correct)
```

Row preservation works; prose preservation does not exist.

**Why this is `P1` rather than `P2`.** It is not merely lost text. The template asserts the ledger
starts empty and the first real task is `T001` — **actively false** in a repository with 316
completed tasks — and `active-tasks.md` is the file a cold session reads first and trusts literally.
A future orchestrator could reasonably conclude no history exists. It also recurs on every
`--update` in every downstream install, and it is at its worst precisely when the ledger is
*healthy*: with zero active rows, the normal state after archiving, there is nothing to preserve and
the template wins outright.

**Why it survived twice.** `T512` hit both, fixed them **by hand in the working tree**, and recorded
them in its closure row — but never opened a task against the cause. `T517`'s post-merge sync hit
both again, verbatim. Both times the only thing that caught it was a manual pre-snapshot. This is
the pattern the task exists to break: a hand-fix plus a ledger note is not a fix, because the next
occurrence depends on someone remembering to look.

**Note on the help text.** `install.sh:17` advertises "preserves task rows in `docs/tasks/*.md`" —
which the current behaviour satisfies *literally* while still being wrong. The brief asks the
implementer to decide what the contract should be and make the text say it, rather than treating the
existing sentence as the specification.

## 2. `T519` — two documents still state the pre-`T517` placeholder syntax

`implementation/SECURITY.md:25` and `docs/artifacts/mcp-platform-contract-v1.md:87` both enumerate
`${env:VAR}` for `claude-code`, which `T517` made wrong.

`P2` is honest: the code is already correct and nothing malfunctions. `SECURITY.md`'s actual
*guarantee* — placeholders emitted verbatim, no secret written to a generated file — was
independently verified during `T517` and still holds; only the enumeration is stale. The risk is
that a reader trusts the stale enumeration when adding a platform later.

The substantive part is versioning, not wording: `mcp-platform-contract-v1.md` is an immutable
artifact, so correcting it means producing a `-v2`. Two worked precedents exist (`T516`'s
`maturity-promotion-criteria-v2.md` and `T517`'s `mcp-header-url-templating-design-v2.md`), and in
**both** cases the brief said "update the v1 document" and the implementer correctly refused. This
brief states the `-v2` requirement up front so that correction does not have to be rediscovered a
third time.

## 3. Ownership, and a deliberate choice about tooling

`T518` → **DevOps Engineer**: shell and CI tooling, and it has `Bash`.

`T519` → **Technical Writer**, which has **no `Bash`, `Grep` or `Glob`**. That is normally an
argument against assigning it work with a git hand-back — and it cost a cycle on `T515`, where a
shell-less agent was told to commit and push. Here it is assigned anyway, because the task is pure
prose and the right role matters more than the convenience of a git-capable one. The brief therefore
states the constraint in its first line and makes "leave the files uncommitted and report the paths"
the *intended* path rather than a fallback, explicitly telling the agent that having no shell is not
a blocker.

## 4. Scope boundaries

`T518` does not touch `merge-mcp-json.py` (verified correct during `T517`, where it preserved a
user's hand-edit), the template files themselves, or any ledger content. Softening the template's
wording is called out as a non-fix: it would hide the bug and weaken fresh-install guidance.

`T519` does not touch `sync.mjs` or any generated file, and is instructed to **report rather than
fix** any third stale site it finds.

## 5. Relationship to `plan-064`

Neither task is Phase 9 work and neither blocks it. Phase 9 remains: execute `ADR-007`'s verdicts
(needs a file-scoped `protected-paths-v1.md` §5 authorization), author 14 golden cases, decide the
two capability gaps, re-run command promotion readiness.
