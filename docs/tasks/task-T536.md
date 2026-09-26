# T536 — `/sprint-status` declares no colour for `in_review`

**ID:** T536
**Owner:** Tech Lead
**Status:** in_review
**Priority:** P2
**Tier:** standard
**Affects:** —
**Depends on:** —
**Created:** 2026-09-26
**Based on:** `docs/plans/plan-076-wave2-findings.md` §2; `docs/tasks/task-T528.md`;
`docs/artifacts/protected-paths-v1.md` §5.

## 1. The gap

`implementation/knowledge/commands/sprint-status.md` step 8 declares **four** node sources:

> - Read `docs/tasks/active-tasks.md` for pending/in_progress/blocked/in_review nodes

and **three** non-`done` colours:

> - Color code: done=green, in_progress=yellow, blocked=red, pending=gray

**A sprint containing an `in_review` task has a node the contract requires drawn and gives no way to
colour it.** The command's own Mermaid template emits exactly four `classDef` lines.

## 2. Read this before you decide it is trivial

**`command/sprint-status` was promoted to `stable` by `T534` while carrying this gap.** Its golden
case passes honestly: the fixture ledger has four rows, all `pending`, and its single `in_review`
occurrence is the status-legend line rather than a data row — verified. **So the gap is real and the
only golden case for that command cannot reach it.**

That is not a reason to un-promote — the case is honest and the criteria were met — but it means
**`stable` here certifies "passes the cases that exist", not "has no known contract gaps"**, and this
is the first concrete instance where the two differ. Your fix closes the first half; §4 asks whether
the second half should be closed too.

## 3. The fix

Add the missing colour to step 8's colour bullet and to the template's `classDef` set, consistent
with the four already declared. Pick a colour that is visually distinct from all four and say why in
one line.

**This adds no requirement** — step 8 already requires the node to be drawn. You are supplying the
value it omits. **Do not** take the other available route of deleting `in_review` from the node-source
bullet: that would resolve the conflict by shrinking the contract, and `ADR-007` §5 forbids resolving
by relaxing. If you believe deletion is right, argue it explicitly on the merits and report it rather
than doing it.

## 4. The second question, which you must answer rather than assume

Should `tests/golden/open/sprint-status-dag-ledger-grounded` be extended to exercise an `in_review`
node?

**Arguments both ways, and I am not deciding for you.** For: a contract clause no case reaches is a
clause nothing defends, and this one was found by reading rather than by testing. Against: wave 2's
implementer deliberately refused to build an `in_review` fixture *to turn the case red*, on the
grounds that choosing a fixture to manufacture a failure is the mirror image of choosing one to
manufacture a pass — and that reasoning was correct. Extending the case *after* the contract is fixed
is a different act from building it to force a failure, but it is not obviously in scope either.

**You hold no `tests/golden/**` authorization.** So if your answer is yes, **report it as a
recommendation with a concrete proposal**, and it becomes a separate authorized task. Do not touch
any case.

## 5. Scope

| In scope | Out of scope |
|---|---|
| `implementation/knowledge/commands/sprint-status.md` | anything under `tests/golden/**` |
| — | `scripts/scorecard.py` |
| — | any `maturity:` field |
| this brief's `**Status:**` | `active-tasks.md`, `completed-tasks.md` |

After editing `implementation/knowledge/`, run **both** generators in order:

```
node implementation/scripts/sync.mjs
python3 implementation/scripts/generate-registry.py
```

`implementation/scripts/sync.mjs`, not `scripts/sync.mjs` — the wrong path fails `MODULE_NOT_FOUND`
and silently no-ops if stderr is suppressed. And `sync.mjs --check` alone does **not** catch registry
drift; forgetting `generate-registry.py` has broken two MRs in this phase.

## 6. Verification

```
python3 tests/run.py                  # BASELINE FIRST; measure it, do not trust this brief
python3 scripts/scorecard.py --check  # READ-ONLY. Never the write mode as a check.
python3 implementation/scripts/check-maturity.py --root implementation
python3 implementation/scripts/check.py --registry --root implementation
node implementation/scripts/sync.mjs --check
python3 docs/tasks/validate-tasks.py
git status --porcelain
```

Expected: **792 tests, OK, 23 skipped** both before and after; `check-maturity.py` `79 / 0` with an
**unchanged distribution**; evaluator-hash unchanged (you touch no protected path); `git status`
clean after commit. **Measure the baseline yourself** — three different figures have circulated in
this phase's briefs and every one was wrong at some point.

## 7. Ledger, git, blockers

Set this brief's `**Status:**` to `in_review`; move no ledger row. Branch `agent/tech-lead/T536`.
Commit message ends with exactly `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

**No merge request, no merge, no self-merge.**

If `git push` fails with `glab auth git-credential: "erase" is an invalid operation` and/or
`HTTP Basic: Access denied`: known environment transient, not your fault, credentials are not broken,
and you must not touch any `glab` or `git config credential.*` setting. Retry two or three times,
then report that the commit is on the local branch.

Blockers: type and severity; max 2 retries.
