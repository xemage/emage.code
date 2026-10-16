# plan-067 — T516: narrow the §3.5 defect check to a declared field

**Status: scoped 2026-09-24, awaiting approval to dispatch.**
Based on: `docs/plans/plan-066-t515-command-contract-authority.md` §6, `docs/artifacts/maturity-promotion-criteria-v1.md` §3.5.

## 0. Origin

This task exists because of a defect found while dispatching `T515`, not because of roadmap
planning. `plan-066` §6 recorded it and explicitly declined to fix it inside a decision task's
dispatch; the user then asked for it to be scoped separately. This document is that scoping.

## 1. The defect in one paragraph

`_ledger_defect()` in `check-maturity.py` regex-scans the whole body of every active `P0`/`P1` task
brief for a component id, using `(?<![\w-])<id>(?![\w-])`. Neither `/` nor `.` is a word character,
so a brief that spells out its mandated branch name (`agent/solution-architect/T515`) or cites an
instruction by filename (`.claude/rules/git-workflow.md`) indicts the component it merely mentions.
The check cannot tell reference from accusation.

## 2. Why it stayed hidden, and why it surfaces now

Nearly every component was `experimental` before `T514`. A false match against an `experimental`
component is invisible — there is no claim to fail. `T514` promoted 5 agents, taking the `stable`
population to 25 agents plus 4 instructions and 7 skills. From that point on, false matches have
something to break, and `T515` hit two of them in a single draft.

This is worth stating plainly because it is a general pattern: **promoting components turned a
dormant tooling bug into an active one.** Work that raises the number of components making claims
should expect to surface latent defects in the claim-checking machinery.

## 3. The design risk that shaped the brief

The obvious implementation is "read `Affects:` if the brief has one, otherwise fall back to the old
scan" or "otherwise assume nothing is affected."

The first preserves the bug. The second is worse than the bug: it converts a **loud false positive**
(a component wrongly blocked — annoying, visible, self-correcting) into a **silent false negative**
(a component with a real open defect promoted to `stable` — invisible, and exactly what the
criterion exists to prevent). A gate that fails open is not a weaker gate, it is a different and
worse thing than no gate, because it still produces a reassuring `PASS`.

The brief therefore makes the field mandatory for `P0`/`P1` briefs and requires a missing field to
fail loudly, enforced as a new numbered check in `validate-tasks.py` alongside C1–C10. That is the
single hard constraint; the rest of the design is the implementer's.

## 4. Priority: `P2`, and why that is not a hedge

The defect makes the gate over-strict, never under-strict. It can block a promotion that deserves to
succeed; it cannot pass one that deserves to fail. Nothing is mis-promoted today, and the workaround
(rephrase the brief) holds. By this repo's own vocabulary — `P0` critical path, `P1` important,
`P2` nice-to-have — that is `P2`.

`plan-066` §6 already called it "not urgent" in writing. Assigning `P1` now would contradict that
assessment to make the work look weightier, which is precisely the kind of drift this repo's ledger
discipline exists to catch.

There is a convenient side effect — `P2` rows are not scanned, so `T516`'s own brief can name
component ids literally as examples, which a `P1` brief about this bug could not do without
triggering it. **The priority is chosen on merit and the side effect noted, not the reverse.** The
brief carries a warning that its literal ids must be converted to display form if it is ever
re-prioritised, so the convenience cannot silently become a trap later.

## 5. Migration surface, and why now is the cheap moment

One brief. The active ledger holds a single row (`T515`), and completed briefs are never scanned —
`_ledger_defect()` skips `done`/`cancelled`, and `AGENTS.md`'s ledger invariant keeps terminal rows
out of `active-tasks.md` altogether.

Every future `P0`/`P1` row adds to that surface. Deferring this is not free even though the defect
is low-severity: the cost of the fix rises monotonically with ledger traffic, while the cost of
*not* fixing it is paid in rediscovery by every brief author.

`_template.md` already has precedent for adding an optional field without a breaking change — the
`Tier` field from `T440`, introduced with explicit "existing briefs remain valid without it"
language. The brief points at it rather than inventing a migration story.

## 6. Scope boundary

The fix is to the caller, `_ledger_defect()`, not to the shared `_mentions()` helper — which has a
second consumer, `_referenced_in_agents_or_commands()`, where matching a mention is the whole point.
The golden-case half of §3.5 keys off structured YAML and has none of this problem; it is untouched.
Promotions are out of scope entirely: this task changes a gate and does not walk through it, so no
`maturity:` value moves as part of it.

## 7. Relationship to Phase 9

Adjacent, not blocking. `plan-064` Phase 9 is about command maturity; this is about the machinery
that adjudicates maturity claims in general. `T515` can run and complete without it — it already has
the workaround baked in. Sequencing is therefore free, and the two should not be bundled.
