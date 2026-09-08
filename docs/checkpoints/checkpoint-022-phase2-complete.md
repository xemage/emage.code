# Checkpoint 022 — Phase 2 complete (MCP Conformance, T420-T423)

> Written by the orchestrator immediately after T422's merge and ledger closeout. This is a real
> phase boundary: `docs/plans/plan-035-roadmap-v7-ground-up.md`'s Phase 2 (T420-T423, "MCP
> Conformance") is now fully done, executed per the user-approved `docs/plans/plan-037-phase2-
> phase5-sequencing.md` sequencing recommendation (Phase 2 before Phase 5). Combined with
> `checkpoint-021` (Phase 1 complete, Gate G1 closed), this is the canonical Phase 1 → Phase 2
> handoff. Future agents planning Phase 3 or Phase 5 work need only `checkpoint-021` + this
> checkpoint, not the full T410-T422 execution history.

## Summary

**Phase 2 of plan-035 (T420-T423) is fully done and genuinely merged to `develop`.** All four
tasks closed in dependency order (T420 → T421/T423 in parallel → T422 → gate), each independently
verified by the orchestrator against real command output before merging — not accepted on any
agent's self-report alone. All three of Phase 2's acceptance criteria (`plan-035` §2.4, immediately
before "Gate G2 closes here") are now met:

- Adding a `core` server to `servers.yaml` and running sync makes it appear in all 7 platforms —
  proven live by T422's round-trip test (`tests/functional/test_mcp_platform_conformance.py`),
  independently re-run by the orchestrator (2/2 pass).
- Deleting it from one platform's projection makes the conformance check fail — proven live by the
  same test file's second round trip, independently re-run (raises, correctly names the platform).
- `test_mcp_secret_guard.py` still passes — confirmed independently (3/3 pass) both after T421's
  fix and after T422's new test file landed.

**This phase's central finding was a correction, not new-build work.** `plan-037`'s own kickoff
finding (that `.vscode/mcp.json` over-includes `brave`/`context7` as `extended`-tagged servers
leaking into the `github` platform) was independently re-checked by the orchestrator before
dispatch and found **false** — both are `servers.yaml`-tagged `core`, `github.json`'s manifest
already scopes `mcp.tags` to `["core"]` only, and a live `node scripts/sync.mjs --check` reported
zero drift across all 7 platforms (557 files) on `develop` at dispatch time. This was independently
reconfirmed twice more during execution (once by T420's own from-primary-sources re-derivation,
once by the orchestrator's post-authoring live-command re-verification) — three independent
confirmations of the same conclusion. The one real, narrow gap this phase actually found and fixed
was different and unrelated: `.vscode/mcp.json.provenance.json` (the `github` platform's ADR-002
provenance sidecar) was never git-tracked, unlike its 6 sibling sidecars, so it did not survive a
fresh clone/worktree even though its content was correct — root-caused by the orchestrator
(`git check-ignore -v`, `git ls-files`) and fixed by T421 with a one-line `.gitignore` negation.

## Completed tasks (this checkpoint)

| ID | Title | Owner | Outcome |
|----|-------|-------|---------|
| T420 | Define the per-platform MCP contract | solution-architect, orchestrator | `docs/artifacts/mcp-platform-contract-v1.md` — authoritative per-platform MCP contract; corrects plan-037's false `brave`/`context7`/`cwso` finding; surfaces the real `.vscode/mcp.json.provenance.json` git-tracking gap |
| T421 | Re-verify/close the `.claude`/`.github` MCP config gap | backend-developer, orchestrator | Fixed the provenance-sidecar tracking gap (`.gitignore` negation + force-tracked file); reconfirmed the `brave`/`context7`/`cwso` non-issue; both `.claude`/`.mcp.json` and `.github`/`.vscode/mcp.json` explicitly checked |
| T422 | `tests/functional/test_mcp_platform_conformance.py` | qa-engineer, orchestrator | Two live round-trip tests proving all three Phase 2 acceptance criteria; closes Phase 2 |
| T423 | Verify/close the manual runtime-verification checklist | technical-writer, orchestrator | Verify-and-close, zero file changes — `docs/wiki/mcp-servers.md` (T384) confirmed accurate against T420's contract |

## G1/G2 determination — how this was actually checked, not assumed

Per this session's own explicit instruction, Phase 2 completing was **not** assumed to close Gate
G2 without checking `plan-035`'s own stated closure criteria directly, the same way `checkpoint-
021` checked G1's ten acceptance bullets one by one before declaring closure. `plan-035` §2.4
states plainly, immediately after Phase 3's acceptance criteria: **"Gate G2 closes when Wave 1
(T433) is complete for the routing target classes."** T433 is a Phase 3 (Maturity Ladder) task,
gated on Phase 3's own T430-T432 first. Phase 3 remains `plan-035`'s own **"Status: proposed — not
approved for task-brief authoring or execution"** — confirmed by grepping both `active-tasks.md`
and `completed-tasks.md` for `T43x`, zero matches in either.

**Gate G2 is therefore NOT closed by this checkpoint.** Phase 2 completing does not itself advance
G2 by any task. What it does do, per `plan-037-phase2-phase5-sequencing.md`'s own framing: it makes
Phase 3 *proposable* as a next phase (Phase 3 needed both G1, closed at `checkpoint-021`, and Phase
2 at least underway/re-scoped before it could be proposed at all — that precondition is now met in
full, not just "underway"). Phase 5 (Persistent Memory/RAG) is also now unblocked to start per
`plan-037`'s own sequential recommendation ("Start Phase 5 after Phase 2 closes... Start Phase 5
after Phase 2 closes, not concurrently"). **Neither Phase 3 nor Phase 5 has been planned to
execution-ready detail or approved for dispatch as of this checkpoint** — per Plan-Approve-Execute,
that is the user's next decision, not something this checkpoint pre-authorizes or begins on its
own strength.

## Artifacts produced (this checkpoint)

- `docs/artifacts/mcp-platform-contract-v1.md` — per-platform MCP contract (T420)
- `.gitignore` (+1 line: `!.vscode/mcp.json.provenance.json`); `.vscode/mcp.json.provenance.json`
  (newly tracked) (T421)
- `tests/functional/test_mcp_platform_conformance.py` (255 lines, 2 tests) (T422)
- `docs/tasks/task-T420.md`, `task-T421.md`, `task-T422.md`, `task-T423.md` (briefs + closure
  addenda)
- MR !218 (`docs/plan-037-phase2-phase5-sequencing` → `develop`, plan approval)
- MR !219 (`docs/phase2-t420-t423-dispatch` → `develop`, T420-T423 dispatch + briefs)
- MR !220 (`agent/solution-architect/T420` → `develop`, T420 implementation, commit `1a4bff4`)
- MR !221 (`docs/phase2-t420-closeout` → `develop`, T420 ledger closeout, commits `8cfafb5`+`bc7f8e7`
  — required a follow-up fix commit after CI's `validate-tasks.py` caught a real brief-status/
  ledger mismatch)
- MR !222 (`docs/phase2-t423-closeout` → `develop`, T423 verify-and-close ledger entry)
- MR !223 (`agent/backend-developer/T421` → `develop`, T421 implementation, commit `337a81b`)
- MR !224 (`docs/phase2-t421-closeout` → `develop`, T421 ledger closeout + T422 dispatch)
- MR !225 (`agent/qa-engineer/T422` → `develop`, T422 implementation, commit `d0ba035`)
- MR !226 (`docs/phase2-t422-closeout` → `develop`, T422 ledger closeout — closes Phase 2)

`develop` HEAD is now `2a4f7a5`.

## Blockers (active)

None. Phase 2 is fully closed with no open items.

## Process notes worth carrying forward

- **`solution-architect`'s tool grant has no Bash, again.** T420 hit the same gap T410's ledger
  entry already recorded once (the agent disclosed it as a blocker and substituted a disclosed
  manual trace rather than fabricating a command transcript; the orchestrator ran the real command
  and applied the commit on the agent's behalf). Per `security-guidelines.md`'s "Architect —
  read-only for implementation code" classification, this is treated as by design, not a defect,
  both times. **Task briefs should not instruct `solution-architect` to run shell verification
  commands going forward** — route that instruction to the orchestrator or a Bash-capable agent
  instead.
- **CI's `validate-tasks.py` (specifically its C8 brief-status cross-check) caught a real
  orchestrator mistake during T420's closeout** — the ledger row said `done` while the brief file
  still said `Status: pending`. Fixed with a follow-up commit before merging. Worth remembering:
  every task closure must update **both** the ledger row **and** the brief's own `Status:`/
  `Completed:` header fields in the same commit, or CI will (correctly) reject it.
- **`scripts/install.sh --update --platform github` does not respect `--platform` scoping the way
  one might expect** — T421 hit this while trying to materialize the missing provenance sidecar,
  found it rewrote unrelated tracked files (`.github/agents/*.agent.md`, `AGENTS.md`,
  `docs/tasks/active-tasks.md`), caught it via `git status` before committing, and fully reverted
  before extracting the one needed file from a scoped `make sync` run instead. Not fixed as part of
  this phase (out of T421's file-ownership scope) — flagged here as a `type: technical,
  severity: minor` item for whoever next touches `install.sh`'s `--update --platform` path.

## Token usage

| Phase | Budget | Spent (this session: T420-T423 dispatch, 4 independent-verification passes, 4 ledger closeouts, this checkpoint) | % |
|-------|--------|----------------------|---|
| Phase 2 (plan-035 §2.8) | 100k | Not separately metered this session; qualitative note — the same recurring pattern prior checkpoints have flagged held here too: independent verification (re-running every cited command directly rather than trusting transcripts, catching the T420 status/ledger mismatch, root-causing the provenance-sidecar gap from first principles) cost meaningfully more than the four tasks' nominal `medium`/`medium`/`medium`/`small` scope estimates, but caught one real ledger-consistency defect (T420) and confirmed one plan-level factual error (plan-037's `brave`/`context7` claim) before it could propagate into wasted fix work | — |

## Next steps — what Phase 2's closure unlocks

Per the phase graph (`plan-035` §2.3) and `plan-037`'s own sequencing recommendation:

1. **Phase 3 (Maturity Ladder, v6.13.0-v6.15.0) is now proposable** — both its preconditions (G1
   closed, Phase 2 done) are met for the first time. It is not yet planned to execution-ready
   detail or approved for dispatch; `plan-035` §2.4's existing T430-T437 table would need the same
   kind of execution-sequencing pass `plan-037` did for Phase 2 before dispatch.
2. **Phase 5 (Persistent Memory/RAG, v6.17.0) is also now proposable**, per `plan-037`'s own
   explicit recommendation to sequence it after Phase 2 rather than run it in parallel. `plan-037`
   already flagged Phase 5's real open cost question (T450's ADR must resolve the embeddings-
   provider decision before T452/T453 can be dispatched, and if it recommends a paid API, that
   needs the same real-cost confirmation gate this project used for T407) — that flag still stands
   and was not resolved by this checkpoint.
3. **Neither Phase 3 nor Phase 5 has been proposed to the user this session** — this checkpoint
   records what is *unlocked*, not a decision to start either. That remains the user's call,
   consistent with this repo's Plan-Approve-Execute protocol.
4. Phase 4 (Task-Tier Routing) remains gated on G2, itself still gated on Phase 3's Wave 1 (T433)
   — still several steps out, unaffected by this checkpoint.
5. Phase 6 (Closed Loop, v7.0.0) remains gated on G3 (Phase 5) and G4 (evaluator-protection
   precondition already satisfied, but G4 also requires the rest of its own phase's conditions) —
   not yet startable.

## Compression note

This checkpoint plus `checkpoint-021-phase1-complete-gate-g1-closed.md` together are the canonical
Phase 1 → Phase 2 handoff. Subsequent agents planning Phase 3 or Phase 5 work receive **only**:
these two checkpoints + their own task brief + the relevant `plan-035-roadmap-v7-ground-up.md`
phase section (and, for Phase 3 specifically, `docs/artifacts/mcp-platform-contract-v1.md` if any
future work references the MCP conformance guarantee Phase 2 established) — not the full
T420-T423 execution history.
