# checkpoint-036 — Phase 9 opened; MCP placeholder defect fixed

**Phase:** `plan-064` Phase 9 (command maturity), partially executed
**Written:** 2026-09-25
**Based on:** `checkpoint-035`, `docs/plans/plan-064-roadmap-v8-breadth-and-utility.md`
**Ledger at this checkpoint:** 0 active, 316 completed

## 1. Completed since `checkpoint-035`

| Task | Outcome | MR |
|---|---|---|
| `T514` | Agent promotion re-run: 20/8 → **25 `stable` / 3 `experimental`** | !367 |
| `T515` | `ADR-007` — contract authority for the 6 `tracked_defect` cases | !372 |
| `T516` | §3.5 defect check narrowed to a declared, fail-closed `Affects:` field | !370 |
| `T517` | `claude-code` MCP emitter uses Claude Code's own `${VAR}` placeholder | !374 |

Plus ledger archival (!373) and dispatch/scoping MRs (!368, !369, !371).

## 2. Key decisions

**`ADR-007` (T515)** — *a command's declared contract is authoritative over the corpus unless it
contradicts a higher-authority document, or the only thing in dispute is a label for content the
corpus already carries. Popularity is not authority.* Five ordered branches, with a corollary table
making the paired sibling's fate follow mechanically from the branch.

Verdicts: **2 of 6 cases end green, 1 stops blocking, 3 stay red.** Of the three `experimental`
agents, **only `security-engineer` promotes**. This non-sweep is the point — the brief flagged "all
six resolve cleanly" in advance as a suspicious result rather than a target, and the implementer
singled out its own single promotion-unblocking verdict as the one most likely to be motivated
reasoning, recording the counter-reading and saying explicitly not to promote on its word.

**`T516`** — defects are now *declared*, not inferred from free text. Mandatory at `P0`/`P1` and
**fail-closed**: a missing field is exit 2 with no component report. The tempting "absent means
affects nothing" fallback was rejected as *worse than the bug* — it converts a loud false positive
into a silent false negative while still printing `PASS`.

## 3. Structural findings worth carrying forward

1. **Promoting components activates dormant gate bugs.** `T516`'s defect was latent only because
   almost everything was `experimental`. `T514` took `stable` to 25 agents + 4 instructions +
   7 skills, and two false matches appeared in the next brief written. Expect more of this as
   Phase 9 promotes commands.
2. **Generated output is only ever compared against what the generator was told to produce.** The
   `T517` defect survived because `sync.mjs`, two tests and a design artifact all agreed with each
   other and all disagreed with the consumer. Nothing in the pipeline read `.mcp.json` the way
   Claude Code reads it. `-v2` §5.3 records the precise origin: v1 cited a hand-added file as
   "empirically verified" when no running client had ever read it.
3. **The zero-sum pairing was over-generalised.** `T515` found the paired golden cases disagree
   about the **artifact class or path**, not only content, and that two of the six have no sibling
   at all.
4. **Two agent-capability constraints hit during execution.** Several agent types have no `Bash`
   (Solution Architect among them), so a brief assuming a git hand-back is unexecutable — and those
   are exactly the types wanted for *disinterested* judgment work, so the conflict-of-interest and
   tooling arguments pull opposite ways. Separately, the orchestrator asserted an environment limit
   from assumption (that no in-session MCP reconnect was possible) and wrote it into a brief as a
   downgraded acceptance criterion; the implementer disproved it and delivered proof instead of
   inference.

## 4. Open work

**Phase 9 remains substantially open.** `ADR-007` decides what to do; nothing has acted on it yet.

| Next | Note |
|---|---|
| Execute `ADR-007`'s verdicts | Needs a **file-scoped `protected-paths-v1.md` §5 authorization** — `T515` itself did not |
| Author 14 golden cases for uncovered commands | Phase 9's larger pole, unstarted |
| Decide the 2 capability gaps | Unstarted |
| Re-run command promotion readiness | After the above |

**Carried debt, unfixed:**
- `install.sh --update` still deletes `.claude/settings.json` and resets `active-tasks.md` to the
  fresh-project scaffold. Recorded in `T512`, recurred verbatim in `T517`'s post-merge sync, caught
  both times only by taking a pre-snapshot. The root cause has never been fixed.
- §3.5's matcher fix (`T516`) is in, but `implementation/SECURITY.md:25` and
  `mcp-platform-contract-v1.md:87` still document `${env:VAR}` for claude-code. The latter needs a
  `-v2`.
- `servers.yaml` hardcodes the context-retriever index dir as `em-age-emage.code` for every target.
- Phase 7 (Codex) still deferred on the external CLI prerequisite.

## 5. Suite health

`tracked_defect` cases will go 6 → 3 once `ADR-007` is executed. The suite still holds 6
`known_failing`, so `T411`'s ≥5 floor survives, but the margin narrows and Phase 9's 14 new cases
must carry the replacement difficulty.

## 6. Verification at this checkpoint

```
tests/run.py                        762 tests OK (skipped=23)
pytest tests/functional             722 passed, 23 skipped
validate-tasks.py                   PASS (0 active, 316 completed)
check-maturity.py                   79 components, 0 failing
sync.mjs --check                    no drift across 577 files
check.py --root implementation      7 checks passed, 0 errors
install.sh --update (all platforms) no diff beyond the two known regressions, both restored
```

## 7. Action required outside the repo

The `T517` fix changes `.mcp.json`, which Claude Code reads **at startup**. A restart is required
before `hindsight`, `cwso`, `gitlab`, `brave` and `toolradar` can connect in this project. Expected
to recover: `hindsight`, `gitlab`. Expected to need separate attention: `cwso` (a prior
`AUTH_HEADER_REJECTED` 403 is a credential matter this fix does not touch).
