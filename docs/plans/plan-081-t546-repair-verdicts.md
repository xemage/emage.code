# plan-081 — T546's repair verdicts, and why the ledger cannot express them

**Created:** 2026-09-26
**Based on:** `docs/artifacts/command-audience-resolution-v1.md`; `docs/tasks/task-T546.md`;
`docs/plans/plan-080-audience-and-authority.md` §3; `implementation/scripts/check-maturity.py`;
`.gitlab-ci.yml`.
**Scopes:** `T549`. Records three further decided repairs **deliberately not scoped** — see §3.

## 1. A structural finding that changes the priority question

`plan-080` §4 put a choice to the user: leave `T546` at P2, where its `**Affects:**` declaration is
recorded but inert, or raise it to P1 and let the maturity gate go red for two `stable` commands.

**That choice was not real, and the orchestrator was wrong to present it as one.** Measured, not
reasoned:

```
$ # T546 flipped to P1, Affects unchanged
$ python3 implementation/scripts/check-maturity.py --root implementation
  command/stable: 7 pass, 2 fail
$ echo $?
1
$ python3 implementation/scripts/check.py --root implementation --maturity ; echo $?
1
```

`.gitlab-ci.yml`'s `validation-super-gate` runs exactly `check.py … --maturity`. A non-zero exit
fails the job, and `sync-no-diff` declares `needs: ["verify-knowledge-drift",
"validation-super-gate"]`, so the pipeline stops.

**Consequence: a P0/P1 row whose `**Affects:**` names a component that currently claims `stable`
makes the repository unmergeable — including the merge of the repair that would clear it.** The
mechanism intended to record "this stable component has a known defect" cannot be used for a stable
component at all. It works only where the component is already `experimental` (where
`check-maturity` returns before `BETA_CRITERIA`), which is precisely the case where the red is
redundant.

This is the "self-referential stall" `T546` §8 warned of, and its P2 recommendation was right. But
`T546` argued P2 **on merits**, weighing it against a P1 it believed was available. It is not
available. The orchestrator confirmed this after `T546` closed.

### The third option neither document considered

**P1 plus demoting the affected components to `experimental` in the same commit.** CI stays green,
because experimental components are exempt from the beta criteria. The ladder then states something
true: `/discover-skills` and `/handoff` do not meet a `stable` claim in an installed target project.

Cost: the command tier moves **9 stable / 10 experimental → 7 / 12**, a visible regression in a
public maturity claim. Benefit: the claim becomes accurate, and the red appears against tasks that
exist to clear it.

**This is a decision about what the project asserts about itself, so it is the user's and is recorded
here rather than taken.** All rows in this plan are P2 pending that decision. If the answer is
"demote", `T550`–`T552` should be opened at P1 alongside the demotion; if it is "leave stable", P2 is
the only mechanically possible setting and the defects live in the briefs rather than the gate.

## 2. Scoped now — `T549`, the one that destroys data

`/consolidate-memory` is `stable` and its step 5 instructs: append to `AGENTS.md`, **then remove from
memory**. In a target project `$TARGET/AGENTS.md` is rewritten unconditionally by
`install.sh:434` → `render_installed_agents.py:174` on every install and every `--update`. The
promotion is destroyed and its source is already deleted.

It is scoped ahead of the other three because it is the only one that **loses user content**. The
others degrade or mislead.

It also **disproves the general pattern `T532` established**: `/skillify` resolved its audience
problem with a precondition on a directory's existence, but `AGENTS.md` exists in *both* audiences.
What differs is **authority over the file**, not presence. No existence test detects it.

## 3. Decided, deliberately not scoped

`T546` reached verdicts on three further repairs. They are recorded here in full so the adjudication
is not lost, and **no ledger rows are opened**, because `plan-080` §3 named the convergence problem —
the queue closed 2 and opened 4 last round — and opening four more would make this plan an instance
of the thing `plan-080` was written to flag.

| Component | Verdict | Grounds |
|---|---|---|
| `/prepare-release` | **Reclassify `authoring`** | It is about *this* repository's release end to end; step 6 regenerates `implementation/registry/summary.md` and mandates a maturity distribution over emage.code's own components. Already `experimental`, so nothing is at stake in the gate. |
| `/discover-skills` | **Repair the command; reject the installer change** | An installed registry would index 79 components **none of which exists at its stated path** (`rel_path` is relative to `sourceRoot: implementation/knowledge`), which is worse than absent. It names the registry **twice** — step 1 and `## Rails` **Inputs** — so a repair must touch both. |
| `/handoff` | **Repair the installer; do not touch the command** | One `install_tree_into` line beside `install_mcp_server_runtime`'s two existing siblings, on that function's own stated rationale. The path then stays byte-identical in both audiences. |

The rule making the asymmetry principled, from `command-audience-resolution-v1.md` §6:
**install when the tree is self-contained and needed; repath when it is an index of absent files;
reclassify when the command is about this repository.**

Also decided and unscoped: **Q5's Option C**, a `.<platform>/skills/local/` carve-out in
`install.sh` giving a target project its first durable home for a hand-written skill. **Gated on one
unverified fact** — whether vendor clients walk `skills/local/*/SKILL.md` recursively. If any does
not, Option C degrades to the artifact's Option D for that client. **Check that before implementing.**

## 4. What closes this, restated

`plan-080` §3 offered three ways out and recommended deciding the class before chasing instances.
That happened: `T546` decided it. The class decision did **not** shrink the queue, because deciding
what `audience:` should be does not implement it, and the instances were already found.

Two of `plan-080` §3's three remain open and are still the user's:

1. **Batch the mechanical residue.** `T547`, `T548`, `T549` and the three in §3 are all
   `mechanical`-tier single-file edits. Six tasks at one per round is six rounds; one batch is one.
   The `/batch` command exists and is `stable`.
2. **A standing-debt register.** There is still no way to record a small real finding without opening
   a row, so every finding becomes a row. `TECHNICAL-DEBT.md` exists but is legacy and unused by this
   workflow. §3 of this plan is an ad-hoc instance of the thing — it works, but only because someone
   chose to read it.

## 5. Sequencing and contention

```
T549 (consolidate-memory)  ─── implementation/knowledge/ → registry + projection contention
```

`T549` contends with `T538` and `T547` (all `implementation/knowledge/`). Contention rules unchanged:
at most one open task touching `implementation/knowledge/`, at most one touching `tests/golden/**`.

With `T530`, `T532` and `T546` archived, the queue stands at **8**: `T538`, `T539`, `T543`, `T544`,
`T545`, `T547`, `T548`, `T549`. `T545` remains the only P1 and the only row with no contention
against anything, so it runs next.

## 6. What this plan does not do

- Does not change any priority, and does not demote any component. §1's third option is put to the
  user, not taken.
- Does not open rows for the three verdicts in §3.
- Does not edit `AGENTS.md`, `command.schema.json`, any manifest, `install.sh`,
  `render_installed_agents.py` or any command file.
- Does not touch `tests/golden/**` or `scripts/scorecard.py`.
- Does not implement the `audience:` key `T546` decided on. **No task has been opened for that
  either** — it is the largest single piece of remaining work and belongs in a round of its own.
