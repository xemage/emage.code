# T514 — Agent promotion re-run: re-evaluate all 8 experimental agents

**Status:** pending
**Owner:** Tech Lead
**Priority:** P2
**Depends on:** none
**Based on:** `docs/plans/plan-064-roadmap-v8-breadth-and-utility.md` Phase 10 (approved for
task-brief authoring 2026-09-24) and its §1.3; `docs/artifacts/maturity-promotion-criteria-v1.md`
§3.1 and §3.5; `docs/artifacts/phase3-wave2-promotion-v1.md`.

## Objective

Re-run promotion readiness for **all 8 agents currently at `maturity: experimental`**, promote
those that now qualify, and record the real, current blocker for those that do not.

`plan-064` §1.3 records that four of them — `context-retriever`, `devops-engineer`,
`evaluation-agent`, `solution-architect` — were blocked from `stable` **solely** by criterion 7
("no open P0 or P1 defect") firing on open tasks `T456`/`T457` that named them. Both closed
2026-09-17. **That is a hypothesis to test, not a target to hit**: if they now pass, promote them;
if they do not, report the actual reason; if any of the other four also pass, promote those too.

The eight: `backend-developer`, `context-retriever`, `devops-engineer`, `evaluation-agent`,
`orchestrator`, `security-engineer`, `solution-architect`, `tech-lead`.

## Method — this is mechanically decidable, so decide it mechanically

`implementation/scripts/check-maturity.py` is the arbiter, not anyone's judgement. For each of the
eight, in one worktree:

1. Tentatively set `maturity: stable` in `implementation/knowledge/agents/<id>.md`.
2. Run `python3 implementation/scripts/check-maturity.py --verbose`.
3. Record the result: `PASS`, or `FAIL` **with the specific numbered criterion** the checker names
   (§3.1's criteria 1–7).
4. **Keep** the flip where it passes. **Revert** it where it fails — do not leave a failing claim
   in place, and do not attempt to make a failing component pass (see Constraints).
5. Regenerate the registry: `python3 implementation/scripts/generate-registry.py --root implementation`
   — `implementation/registry/summary.md` and `index.json` both carry the `maturity` value and will
   otherwise go stale.
6. Verify projections: `node implementation/scripts/sync.mjs --root implementation --check`.
   **Note, verified before this dispatch:** `maturity` is *not* projected into the per-platform
   agent files (`.claude/agents/*.md` and siblings carry `name`/`description`/`tools` only), so
   this step is expected to report no drift. Confirm that rather than assume it — if it does report
   drift, regenerate and say so in the report.

## Why `tech-lead` owns this, and the conflict of interest in it

Owner follows the promotion-wave precedent (`T433`/`T434`/`T435` were all `tech-lead, orchestrator`;
only `T436`, a *demotion* assessment producing no file changes, was Product Owner's). `tech-lead`'s
tool grant (`[read, search, edit, execute, web, mcp__fetch]`) can both run the checker and edit the
frontmatter, so no split-ownership is needed.

**Disclosed conflict of interest:** `tech-lead` is itself one of the eight agents under evaluation.
This is acceptable *only* because the decider is a mechanical script rather than the owner's
discretion — the owner cannot promote itself by judging itself favourably, it can only run a
checker and report what the checker said. To make that concrete: **the top-level session will
independently re-run `check-maturity.py` against `tech-lead`'s own result specifically** before this
task closes. Flag anything about that arrangement you think is unsound rather than working around
it.

## Why this is P2

`AGENTS.md`'s vocabulary is `P0` critical path / `P1` important / `P2` nice-to-have. Nothing depends
on this task, no user is blocked by it, and `plan-064` itself calls Phase 10 "the cheapest item on
this roadmap" — it collects value already earned. P2 is the honest classification.

**Stated openly because it is also load-bearing:** criterion 7 blocks promotion when an open **P0
or P1** row's title or brief body names the component. This brief necessarily names all eight
agents. At P0/P1 it would therefore block the very promotions it exists to perform — the
self-referential ledger-defect trap this repo has hit repeatedly (`T433`, `T491`–`T495`, `T505`).
At P2 it does not: `check-maturity.py` line 396 filters to `{"P0","P1"}` and skips P2 rows, which
was verified against the implementation, not just the criteria document, before this dispatch.

The priority is P2 because the work genuinely is P2. That it also avoids the trap is a convenience,
not the reason — if you judge this work to be genuinely P1, say so in your report rather than
leaving the classification unchallenged.

## Constraints

- **Do not weaken the bar to make something pass.** Do not edit `check-maturity.py`,
  `maturity-promotion-criteria-v1.md`, `maturity-levels-v1.md`, or any test, to convert a FAIL into
  a PASS. If a component cannot pass, that is the finding.
- **Do not author new evidence in this task.** If an agent fails on criterion 4/5/6 (golden-or-
  ledger evidence, cross-reference, documentation), record the gap — do not write the missing
  documentation or ledger row to close it. That is separate, differently-scoped work, exactly as
  `phase3-wave2-promotion-v1.md` §4 treated the command golden-case gap.
- **Do not touch `tests/golden/**` or `scripts/scorecard.py`** (protected paths).
- Root self-install mirrors (`.claude/`, `.cursor/`, … at the repo root) are refreshed by
  `scripts/install.sh --update`, never by CI, and are **out of scope here** — a separate, known
  axis of drift (`T512`).
- Standard worktree/branch/MR workflow (`agent/tech-lead/T514`, branched from `develop`). No
  self-merge — hand back to the top-level session for independent review.
- Run the full bar before opening your MR: `python3 tests/run.py`,
  `python3 docs/tasks/validate-tasks.py`, `python3 implementation/scripts/check-maturity.py --verbose`,
  `node implementation/scripts/sync.mjs --root implementation --check`.

## Expected outputs

1. Promotions applied in `implementation/knowledge/agents/*.md` for every agent that passes.
2. Regenerated `implementation/registry/{summary.md,index.json}`.
3. `docs/artifacts/agent-promotion-rerun-v1.md` — a per-agent table of all eight: outcome, and for
   each FAIL the specific criterion plus the concrete thing that would close it. This is the
   durable record; `plan-064` §1.3's claim should be either confirmed or corrected by it explicitly.

## Acceptance criteria

- [ ] All 8 experimental agents evaluated — none left merely un-re-evaluated
- [ ] Every promotion applied is backed by a real `check-maturity.py` PASS, re-runnable by a reviewer
- [ ] Every non-promotion names the specific failing criterion and what would close it
- [ ] No criterion, checker, or test weakened; no new evidence authored to force a pass
- [ ] `check-maturity.py --verbose` reports 79 components, 0 failing their claimed level
- [ ] Registry regenerated; `sync.mjs --check` clean
- [ ] Full verification bar green
- [ ] `plan-064` §1.3's four-agent hypothesis explicitly confirmed or corrected, with evidence

## Blocker protocol

Standard: `technical | dependency | unclear_requirements | external`, severities
`critical | major | minor`, max 2 retries before escalation. **A result where fewer than four agents
promote — or none — is a valid, complete outcome, not a blocker**, provided the reasons are real and
recorded. Do not escalate merely because the hypothesis did not hold.
