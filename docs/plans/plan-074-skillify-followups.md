# plan-074 — `/skillify` follow-ups from T527's adjudication

**Status: scoped 2026-09-25, awaiting approval to dispatch.**
Based on: `docs/artifacts/skillify-contract-resolution-v1.md`; `docs/tasks/task-T527.md`;
`docs/decisions/ADR-007-command-contract-authority.md`; `docs/artifacts/protected-paths-v1.md` §5;
`docs/plans/plan-073-skillify-adjudication-and-wave2.md`.

## 0. What T527 left, and why it left it

`T527` adjudicated the `/skillify` contract conflict per-section and executed the verdict. It
deliberately stopped at four things, each for a stated reason rather than for lack of time:

| Left | Reason | Picked up by |
|---|---|---|
| `expect.py` re-derivation | outside its §5 grant; escalated as a blocker rather than self-authorized | **`T531`** |
| `## Required Context` | same defect shape, but outside the five disputed sections | **`T531`** |
| output-path defect | needs its own adjudication and its own grant | **`T532`** |
| the case's `known_failing_reason` / `brief.md` staleness | its grant was conditional on a genuine pass, which did not occur | **`T530`**, widened |

Every one of those is a correct refusal under `protected-paths-v1.md` §5.1, which forbids the
holding agent from extending its own grant. The pattern is now four-for-four across `T520`, `T523`,
`T525` and `T527`.

## 1. `T531` — re-derive the checker, and close the sibling defect

**The checker has stopped describing the live contract.** `expect.py` still asserts `## Trigger` and
`## Steps`, which **no document declares any more** after `T527`. It returns `False` either way, so
nothing is *mis*-reported — but it is now checking a contract that no longer exists, which is a
worse failure than a red case: a check nobody can trust is not a check.

`T527` supplied an exact spec and one instruction that matters more than it looks:

> keep the `section in text` **substring** operator — it admits `## Procedures` and
> `## Procedure Summary`; switching to an exact-heading regex would strengthen the check beyond what
> was decided.

That is `ADR-007` Validation 1 (no loss of strength) applied in the unusual direction: the risk here
is over-strengthening, not relaxation. A re-derivation that quietly tightens the operator would
change the verdict `T527` reached without anyone deciding to.

`T531` also closes **`## Required Context`**: Round 2 of the `skillify` skill declares it, the
skill's own template omits it — the *identical* self-contradiction `T527` fixed for
`## Success Criteria`, verified independently. `T527` left it only because it was not one of the five
disputed sections. Fixing it here costs one line and removes the last known instance of that shape.

**`/skillify` still does not promote after `T531`** unless the re-derived checker passes against the
real fixture, which on `T527`'s own scoring it will not — the fixture satisfies 1 of 5 sections.
`T531` is about the checker being honest, not about turning the case green. **An implementer who
delivers a green case here has almost certainly over-reached; say so if it happens.**

## 2. `T532` — the output-path defect

`skillify.md` declares its output at `.github/skills/<name>/SKILL.md`. Two problems, both real:

1. **`AGENTS.md` says `.github/` is generated** by `scripts/sync.mjs` and must not be hand-edited.
   A `/skillify` output written there **in this repo** is destroyed by the next sync.
2. It **hardcodes one platform out of seven** (`.github/`), while the repo projects to `.claude/`,
   `.cursor/`, `.gemini/`, `.opencode/`, `.pi/`, `.cline/` as well.

It is *correct* for an installed target project, where the platform folders are the runtime
reference and there is no `implementation/knowledge/` source tree — and *wrong* for this repo, where
the source of truth is `implementation/knowledge/skills/`. So the honest question is not "which path
is right" but **"does this command's contract address the authoring repo, the target project, or
both, and does it say so?"** That is an `ADR-007`-shaped question and it is why this is a separate
task rather than a one-line path edit.

**Resolving it changes the fixture glob in `expect.py`**, so `T532` must run after `T531` or it will
collide with it. Sequenced, not parallel.

## 3. The queue is getting deep — stated rather than hidden

After this plan the ledger carries **7 active rows**, all `P2`, none dispatched except by explicit
step-by-step approval: `T519`, `T521`, `T528`, `T529`, `T530`, `T531`, `T532`.

That is more than this project has usually held, and it is worth naming rather than letting it
accrete quietly. None of them blocks another except `T532` after `T531`. Three of them (`T528`,
`T531`, `T532`) touch protected paths and will each drift the evaluator-hash baseline. The honest
read is that `T525`'s and `T527`'s findings generated work faster than it is being executed — which
is what good findings do, but it means the queue should be worked down before wave 3 is scoped.

**Recommended order:** `T531` (unblocks `/skillify`, smallest), then `T528` (wave 2, the bulk), then
`T529`/`T530` (small carried defects), then `T532`. `T519` and `T521` have been pending since
2026-09-25 and should not be forgotten simply because newer work keeps arriving.

## 4. Evaluator-hash, fifth time

`T531` and `T532` each touch `tests/golden/**` and will each drift the `tests_golden` digest and
turn two tests red. Both briefs pre-schedule the human sanction: name the tests, put the next
`evaluator-hash-known-good-v<N>.json` out of the agent's scope, require the agent to report the
recomputed digests and stop. Four agents running have respected that boundary, one of them noting
explicitly that it could have argued the refresh was in scope and declining anyway.
