# T543 — Root projections are refreshed by no generator and checked by no gate

**ID:** T543
**Owner:** DevOps Engineer
**Status:** in_review
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-09-26
**Based on:** `docs/plans/plan-079-install-sync-gap.md` §1; `docs/tasks/task-T542.md`;
`AGENTS.md` § Knowledge Base; `implementation/scripts/sync.mjs`; `scripts/install.sh`.

## 1. The gap

`implementation/scripts/sync.mjs` writes **only** under `implementation/.<platform>/`. The repo-root
folders — `.claude/`, `.cursor/`, `.gemini/`, `.github/`, `.opencode/`, `.pi/` — are refreshed only by
`scripts/install.sh --update`.

**And `sync.mjs --check` reports "no drift across 577 files" regardless**, because it inspects only
the `implementation/` tree. Verify both yourself.

## 2. It is live, and it was demonstrated rather than theorised

`T542` removed a direct-commit exemption from `orchestrator.md`, correctly regenerated all six
`implementation/` projections, and passed every gate — yet **`.claude/agents/orchestrator.md`, which
is what the orchestrator actually running in this repo reads, still says "commit directly to
develop."** Nothing in CI noticed.

Independently corroborated: **5 of 19 root command projections already differed from
`implementation/` before `T536` touched anything.** So the root tree has been drifting for some time,
and **every knowledge fix in this repo has silently failed to reach the running agent** unless
someone ran `install --update` afterwards.

## 3. Answer the prior question first

**Is root drift a *defect* at all?**

- If the root tree is genuinely a **target-project artifact** that this repo merely happens to
  contain, then it is *supposed* to lag until installed, and the only real defect is that nothing
  says so.
- If it is meant to **track**, then five of nineteen files are wrong right now and have been for a
  while.

**These are different repairs. Pick one and argue it — do not split the difference.** Read
`AGENTS.md` § Knowledge Base and `scripts/install.sh` before deciding.

### 3.1 AMENDED 2026-09-26 — the tension this brief originally asked you to resolve is already gone

This brief first said `AGENTS.md` was "in tension with itself", calling the root folders "the
installed platform projections" while saying the per-platform folders "are **generated** by
`scripts/sync.mjs`". **T545 fixed that** (MR !417, merged). Bullet 2 now states the two-stage
ownership explicitly: `sync.mjs` writes `implementation/.<platform>/`, and the **top-level** folders
are written by `scripts/install.sh`, whose `--update` replaces each wholesale with
`rsync -a --delete`.

So you are no longer resolving a self-contradiction. **You are deciding whether the two-stage
arrangement bullet 2 now documents is acceptable, or whether the second stage needs a gate.** Read
the current bullet 2 first; do not reason from the version quoted in older documents.

### 3.2 Evidence for the "target-project artifact" limb — a convention you must weigh

There is **established precedent (T382, T403, T406)** that the repo-root self-install mirror
(`.claude/`, `.pi/`, `.mcp.json` at the root) is a **separate artifact** from `implementation/`'s
canonical projections, refreshed only by a manual `scripts/install.sh --target . --update` and
**never by CI**. `make sync` and `make verify` only ever run `sync.mjs --root implementation`.

**This is the strongest argument that the drift is by design rather than a defect, and this brief
did not tell you about it.** Verify the precedent yourself — the orchestrator is relaying it from
session memory, not from a document it re-read. If it holds, the "nothing says so" limb of §3 gets
much stronger and the "five files are wrong" limb gets weaker.

### 3.3 Evidence for the "it is a real defect" limb — measured, not argued

After T532's single-command knowledge change, the root projections went **48 / 30 / 30 lines** stale
(`.claude/commands/skillify.md`, `.claude/skills/skillify/SKILL.md`,
`.github/skills/skillify/SKILL.md`) while `sync.mjs --check` reported "no drift across 577 files"
**and** `generate-registry.py --check` reported "registry is up to date". Both gates green, both
correct about what they inspect, neither inspecting the trees this repository's own tooling reads.

T545 also observed, independently, that the root trees currently differ from `implementation/`'s in
`agents/orchestrator.md`, six commands and `skills/skillify/SKILL.md`, plus an extra root
`.claude/settings.json`.

### 3.4 A third gate already exists that this brief did not mention

`python3 implementation/scripts/generate-registry.py --check` is a **read-only registry-drift gate,
distinct from `sync.mjs --check`**. §4's option list was written as though `sync.mjs --check` were the
only candidate to extend. It is not. Consider which gate the root trees belong to.

### 3.5 The same class of gap was just found elsewhere, with a better-shaped answer

T545 established that the root `AGENTS.md` is byte-for-byte
`render(implementation/AGENTS.md, --platform all)` — and that **nothing enforces it.** Zero tests
invoke the renderer. The recommended gate there was a **render-identity assertion**, not a plain file
equality, because the two files legitimately differ.

**That is the same problem you are solving, one file over.** If your verdict is "add a gate",
consider whether one gate should cover both `AGENTS.md` and the projection trees, and say so either
way. A parity test for `AGENTS.md` is *not* in your scope — but an answer that ignores it will be
half an answer.

## 4. Then choose a repair, and reject the others on the record

None of these is endorsed:

- **Extend `sync.mjs --check` to the root tree.** Cheapest; makes the next occurrence loud instead of
  silent. But **it would fail immediately and keep failing until someone syncs** — arguably the point,
  arguably an unmergeable gate. If you choose it, say how the repo gets to green.
- **Have `sync.mjs` write both trees.** Closes the gap entirely, but collapses a distinction
  `AGENTS.md` draws deliberately.
- **A CI job or a `tests/functional/` test asserting the two trees agree.**
- **Document the gap and require `install --update` at checkpoints.** The weakest option — **if you
  choose it, reject the others explicitly and explain why this is not simply what the repo already
  implicitly does**, since that is how the drift accumulated.

## 5. Constraints

- **Do not run `scripts/install.sh --update` as the fix.** It rewrites six projection trees at once,
  `AGENTS.md` mandates a follow-up `/validate-tasks`, and past runs of it have destroyed
  project-local state (see `T518`). If your verdict requires a sync, **say so and stop** — that is a
  separate, disclosed step, not something to fold in silently.
  **Two specific known failure modes, added 2026-09-26:** a past `--update` run **deleted
  `.claude/settings.json`** and **reset `docs/tasks/active-tasks.md` to a false empty-ledger
  scaffold**. The second is the dangerous one — it silently destroys the task ledger this workflow
  runs on. `install.sh` refuses to run at the repository root without `--update`, so the only
  sanctioned refresh path is the destructive one. That asymmetry is itself a finding and belongs in
  your verdict.
- **`scripts/scorecard.py` and `tests/golden/**` are out of scope** and you hold no authorization for
  them.
- Do not change any `maturity:` field, and move no ledger row — archival is orchestrator-only.
- If your verdict edits `implementation/knowledge/`, run **both** generators:
  `node implementation/scripts/sync.mjs` then `python3 implementation/scripts/generate-registry.py`.
  Note the path is `implementation/scripts/`, not `scripts/`; the wrong one fails `MODULE_NOT_FOUND`
  and silently no-ops.

## 6. Verification

```
python3 tests/run.py                  # BASELINE FIRST — measure it yourself
python3 scripts/scorecard.py --check  # READ-ONLY. Never the write mode as a check.
python3 implementation/scripts/check-maturity.py --root implementation
python3 implementation/scripts/check.py --registry --root implementation
node implementation/scripts/sync.mjs --check
python3 docs/tasks/validate-tasks.py
git status --porcelain
```

**Measure the baseline yourself** — six different figures have circulated in this phase's briefs and
every one was wrong at some point. `check-maturity.py` must stay `79 / 0` with an unchanged
distribution.

**If your repair adds a gate that fails on the current tree, say so explicitly and do not hide it
behind a green summary.** `T521` added a gate that changed release-tag behaviour from passing to
failing; disclosing that up front is what made it reviewable and it was then authorized. Do the same.

## 7. Ledger, git, blockers

Set this brief's `**Status:**` to `in_review`; move no ledger row. Branch
`agent/devops-engineer/T543`. Commit message ends with exactly
`Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.

**No merge request, no merge, no self-merge.**

If `git push` fails with the `glab auth git-credential: "erase" is an invalid operation` /
`HTTP Basic: Access denied` pair: known environment transient, not your fault, credentials are not
broken, and you must not touch any `glab` or `git config credential.*` setting. Retry two or three
times, then report that the commit is on the local branch.

Blockers: type and severity; max 2 retries. Report anything the brief got wrong — briefs in this phase
have been wrong nine times and every time the implementer caught it.
