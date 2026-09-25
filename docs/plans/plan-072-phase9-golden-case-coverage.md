# plan-072 — Phase 9: golden-case coverage for the 14 uncovered commands

**Status: scoped 2026-09-25, wave 1 awaiting approval to dispatch.**
Based on: `docs/artifacts/command-promotion-readiness-v1.md` §3.2,
`docs/artifacts/golden-suite-format-v1.md` §2,
`docs/artifacts/protected-paths-v1.md` §5,
`docs/decisions/ADR-007-command-contract-authority.md`,
`docs/plans/plan-064-roadmap-v8-breadth-and-utility.md` Phase 9,
`docs/plans/plan-035-roadmap-v7-ground-up.md` §2.4 Phase 1 (`T411`'s original 20-case authoring).

## 0. What this closes

`command-promotion-readiness-v1.md` measured the remainder of Phase 9 and found the 18
non-`stable` commands split cleanly in two, with no overlap. Four are blocked by an open
`tracked_defect`; the other **14 are blocked by criterion 4 alone** — *no golden case exists for
them at all* — and by **nothing else**. One case per command is therefore **sufficient**, not
merely necessary. This is the phase's largest remaining piece and the only one blocked by an
absence rather than a defect.

```
/batch          /bug-report      /consolidate-memory  /discover-skills
/evaluate-poc   /handoff         /new-poc             /new-project
/poc-demo       /skillify        /sprint-status       /team-status
/validate-tasks /validate-workflow
```

## 1. The hazard this plan exists to control

**An agent asked to author 14 cases that unblock 14 promotions has every incentive to author 14
trivially-passing cases.** That is precisely the unearned promotion the maturity ladder exists to
prevent, and it would be almost undetectable after the fact: a green board with 14 new cases looks
like progress.

Three controls, in order of strength:

1. **Every case must quote a specific clause of its command's declared contract** in
   `brief.md`'s "What this checks" section, the way all 14 existing cases do — never a paraphrase,
   never a general claim that the command "works". A case that cannot name the clause it tests is
   not a case.
2. **A `known_failing` outcome is a correct outcome.** If an honest case against a real corpus
   comes out red, the case ships red and **that command does not promote**. `ADR-007` §5 —
   "never resolve by relaxing a check" — binds the authoring step exactly as it binds the fixing
   step. Producing a `tracked_defect` here is a *finding*, not a failure to deliver.
3. **A wave in which every case passes is a suspicious result, not a target.** `T515`'s brief
   used this framing and it held: that task's honest answer was 2 green of 6. Waves are sized so
   that a reviewer can actually read every case.

## 2. Grounding survey — done before the split, because it determines it

`golden-suite-format-v1.md` §2.2 allows a fixture to be either real repo artifacts or
hand-authored. The existing suite prefers real (`*-real-*` cases) and, where none exists,
documents the absence explicitly — `new-feature-plan-doc-compliant`'s Provenance section runs a
corpus survey and states that zero matches were found.

Corpus probe run against this repo:

| Command group | Real corpus present? |
|---|---|
| `/handoff` | **Yes, strongest** — 2 real `docs/checkpoints/handoff-*.{json,md}` pairs, plus a JSON schema and a validator |
| `/validate-tasks` | **Yes** — a real validator with deterministic output and a real ledger to run it against |
| `/consolidate-memory`, `/discover-skills`, `/skillify` | **Partial** — a real skills corpus exists under `implementation/knowledge/skills/` |
| `/bug-report`, `/batch`, `/new-project`, `/sprint-status`, `/team-status`, `/validate-workflow` | **Thin** — little or none |
| `/new-poc`, `/poc-demo`, `/evaluate-poc` | **None. Zero `POC-DEBT-SCORECARD.md` files exist anywhere in this repo.** |

That last row is a real finding and it changes how those three must be handled: with no corpus at
all, their cases are hand-authored counter-examples, which is `ADR-007` **branch 4** territory.
They are deliberately last.

## 3. The split

Three waves, ordered by grounding strength — strongest first, so the weakest cases are authored by
someone who has already seen four good ones reviewed.

| Wave | Task | Commands | Grounding |
|---|---|---|---|
| 1 | `T525` | `/handoff`, `/validate-tasks`, `/discover-skills`, `/skillify` | real artifacts or a real corpus |
| 2 | TBD | `/consolidate-memory`, `/bug-report`, `/batch`, `/new-project`, `/sprint-status` | thin corpus, contract-led |
| 3 | TBD | `/team-status`, `/validate-workflow`, `/new-poc`, `/poc-demo`, `/evaluate-poc` | hand-authored; PoC three have **no** corpus |

**Waves 2 and 3 are deliberately not scoped yet.** Wave 1 is a test of the approach as much as a
delivery: if its four cases come back thin, or all green, the split and the controls in §1 need
revising before 10 more cases are authored against them. Scoping all three now would bank that
assumption.

## 4. Protected paths and the tamper-evidence baseline

`tests/golden/**` is protected. Each wave needs its own **file-scoped `protected-paths-v1.md` §5.2
authorization**, naming the case directories it may create and nothing else.

**Every wave will drift the `tests_golden` evaluator-hash digest and turn 2 tests red.** This is
now a confirmed, repeating consequence of *any* authorized `tests/golden/**` change (`T520`,
`T523`). `T523`'s brief failed to account for it and its acceptance criteria were unsatisfiable as
written — found by the implementer, not by the author.

**Each wave's brief must therefore pre-schedule the human sanction**, not leave the agent to
discover it: state up front that the two evaluator-hash tests are expected to fail, that the
refresh to the next `evaluator-hash-known-good-v<N>.json` is **out of the agent's scope**, and that
the agent must report the recomputed digests and stop. The orchestrator surfaces them; the user
authorizes; only then is the new baseline written. Refreshing a tamper-evidence baseline is the one
action that control exists to stop an actor doing to itself, and an agent must never do it for
itself — `T523`'s agent got this right unprompted and that behaviour is the standard.

## 5. What a wave does not do

- **Does not promote anything.** Component-state changes are separate tasks, per `T514`, `T522`
  and `T524`. A wave's own row declaring `Affects:` at `P2` does not block those promotions either
  — see `T524`'s correction: `check-maturity.py:504` filters the ledger-defect scan to `P0`/`P1`,
  so a `P2` row is invisible to criteria 3 and 7.
- **Does not touch `scripts/scorecard.py`**, any existing case, or `tests/golden/held-out/`.
- **Does not author a case for a command already covered.** All 14 targets are confirmed
  uncovered by measurement, not by assumption.

## 6. Known adjacent work, deliberately excluded

`tests/golden/open/new-feature-real-checkpoint-format-drift/brief.md` still reads
`known_failing / tracked_defect` with a `## Why this is known_failing today` section while its
`case.yaml` says `expected_pass` — stale since `T520` flipped it, found by `T523`'s implementer and
independently confirmed. It is a protected path and needs its own named authorization. Folding it
into a wave would widen that wave's grant for an unrelated reason; it gets its own row.

## 7. Where this leaves Phase 9

After all three waves, commands could reach **16 of 19 `stable`** — minus however many waves
honestly produce `known_failing` cases, which is the number this plan refuses to predict. The
remaining 3 (`/plan`, `/prepare-release`, `/code-review`) are the `ADR-007` verdict A, C and H-2
cases, which need corpus fixes rather than coverage.
