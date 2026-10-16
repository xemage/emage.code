# T543 — Root projection drift: resolution, v1

**Based on:** `docs/tasks/task-T543.md` (as amended 2026-09-26, §3.1–§3.5, §5);
`docs/plans/plan-079-install-sync-gap.md` §1; `implementation/AGENTS.md` § Knowledge Base as rewritten
by T545 (`ba65509`); `scripts/install.sh`; `scripts/merge-mcp-json.py`; `scripts/merge-task-docs.py`;
`scripts/render_installed_agents.py`; `implementation/scripts/sync.mjs`; `.gitlab-ci.yml`;
`docs/tasks/completed-tasks.md` rows T382, T403, T406, T518;
`docs/decisions/ADR-002-mcp-merge-provenance-tracking.md`;
`docs/plans/plan-081-t546-repair-verdicts.md` §1.
**Author:** DevOps Engineer. **Date:** 2026-09-30. **Tree measured:** `develop` at `e393481`.

## 0. Verdict

1. **Root drift is a defect.** The repo-root harness is correctly *owned* by the installer, as
   `AGENTS.md` bullet 2 says. But in this repository it is also the live runtime of every agent that
   works here, so it is *required to track* `develop`. It does not. 49 root paths lag today,
   including the orchestrator's own branch rule.
2. **Repair: one read-only parity gate that uses the installer as its oracle**, with drift that is
   already known *declared* in a committed ratchet list:
   `tests/functional/test_root_install_parity.py` plus `tests/_baselines/root-install-drift.json`.
   It is green on the current tree without a root sync, it turns any *new* divergence red in the
   MR that causes it, and the MR's own author can bring it back to green without doing anything
   destructive.
3. **Rejected on the record:** extending `sync.mjs --check` to the root, having `sync.mjs` write
   both trees, a strict (non-ratchet) parity gate, a pinned-revision gate, and "document it and run
   `install --update` at checkpoints".
4. **The defect is not cured by this change. It is made visible and bounded.** Curing it means
   emptying the declared list, which needs a root refresh. The only sanctioned root-refresh path
   today is the destructive `install.sh --target . --update`. **That is a separate step that needs
   human approval, and it has not been performed.** §6 specifies a safer path to build first.
5. **§3.5: one gate should cover both, and it does.** A fresh install renders `AGENTS.md` with
   `--platform all`, so the same comparison asserts root `AGENTS.md` render identity. This is
   disclosed in §7 as a scope point for the orchestrator.

## 1. Measured state

All figures below were measured on 2026-09-30 in the T543 worktree. None is copied from the brief.

**Per-folder drift, root against `implementation/.<platform>/`.** I measured this three independent
ways. They agree.

- `diff -rq implementation/$d $d` per folder, with `diff | grep -c '^[<>]'` per file.
- A per-revision comparison: for every file, `git show <rev>:implementation/<path>` against the
  root file, with MCP configs compared as parsed JSON.
- The new gate: `python3 -m tests.functional.test_root_install_parity --print-drift`.

| Root folder | Divergent paths | Which |
|---|---|---|
| `.claude/` | 8 (+ `settings.json`, project-local, correctly ignored) | `agents/orchestrator.md`; `commands/{batch,new-feature,plan,prepare-release,skillify,sprint-status}.md`; `skills/skillify/SKILL.md` |
| `.cursor/`, `.gemini/`, `.github/`, `.opencode/`, `.pi/` | 8 each | the same eight sources, in each platform's own filename form |
| `.cline/` | 1 | `skills/skillify/SKILL.md` (Cline ships no agents or commands) |
| `.clinerules/` | 0 | — |
| MCP configs (7 files) | 0 | byte diffs exist, but all seven are fixed points of `merge_json` with identical sidecars (§3) |
| `AGENTS.md`, `CLAUDE.md` | 0 | root `AGENTS.md` == `render_installed_agents.py --platform all` of source, byte-for-byte |
| **Total** | **49** | |

The brief's §3.3 line counts still hold exactly: `.claude/commands/skillify.md` 48 lines,
`.claude/skills/skillify/SKILL.md` 30, `.github/skills/skillify/SKILL.md` 30. Six of the 19 commands
drift.

**The root is not randomly rotten. It is a coherent snapshot of one revision.** Against
`implementation/` at `fee245a` ("chore(self-install): refresh root harness mirrors to v7.0.0",
2026-09-19), all eight trees and the MCP configs show **0** divergent paths. Nothing records that
revision. `.generated-manifest.json` carries `generatedAt: "<deterministic>"` and no source
revision, so I found it by bisection.

**The drift is behavioural, not cosmetic.** Root `.claude/agents/orchestrator.md` still says
`Docs (docs) → commit directly to develop (docs-only changes exempt)`. Root
`.claude/rules/git-workflow.md`, which is not stale, says there is no such exemption. The
orchestrator running in this repository therefore holds a live contradiction that T542 fixed in
source four days ago (`aa9c6ff`, 2026-09-26).

**Existing gates, all green, and all correct about what they inspect:**
- `sync.mjs --root implementation --check` reports `OK - no drift across 577 files.` (exit 0).
- `generate-registry.py --check` reports `registry is up to date`.
- CI's `sync-no-diff` runs `git diff --quiet` repo-wide, but only after a `sync.mjs` that never
  writes the root, so it cannot see root drift either.

## 2. The prior question: is root drift a defect?

**Yes.** This is the "meant to track" limb. The evidence for the other limb is real, so here it is
first.

**For "a target-project artifact that is supposed to lag".** I verified this rather than accepting
it as relayed.

- `AGENTS.md` bullet 2 (post-T545) states the two-stage ownership: `sync.mjs` writes
  `implementation/.<platform>/`, and `install.sh` writes the top-level folders.
- The T403 ledger row says the root snapshot "is refreshed only by a manual
  `scripts/install.sh --target . --update`, not by the `sync-no-diff` CI gate (scoped to
  `implementation/` only)". It adds that "Tech Lead's T406 review confirmed this is correctly out
  of scope, not a silently cut corner". The T406 row says the same.
- The T382 brief and row treat a root `install --target . --update` as a deliberate, manual,
  orchestrator-verified operation.
- No ADR covers the self-install. A grep of `docs/decisions/` found none.
- The root being an exact snapshot of `fee245a` is what a pinned install looks like.

**Why that evidence does not carry the conclusion:**

1. **The precedent settles the refresh *mechanism*, not that lag is *intended*.** T403's row calls
   the stale root "a note left for a future task". T406 found it out of scope *for T403*. Neither
   says the lag is desirable, and neither names who refreshes, or when. This task is that future
   task. "Refreshed only manually, never by CI" is an accurate description of how the drift
   accumulated. It is not a design decision that the drift should exist.
2. **There is no release boundary between source and root here.** A downstream project lags
   deliberately, because it pinned a release. In this repo, root and source share every commit, MR
   and reviewer. The root's lag is not a pin anyone chose, and nothing even records which revision
   it is on.
3. **The repo already treats two of the root's install outputs as tracking.** Root `AGENTS.md` was
   edited in the same MR as its source (T545, `ba65509`: both files, +5/−1 each). Root `.mcp.json`
   was too (T517, `9c80e02`). Both are in step with HEAD today. The eight projection trees are the
   exception, and no stated principle distinguishes them from those two files.
4. **Root `AGENTS.md` itself says the root is the runtime:** "Use the installed platform folders …
   as runtime references in this target project." The orchestrator branch-rule contradiction in §1
   is the consequence.

The "target-project artifact" framing is right about **who writes** the root and wrong about
**whether it may lag**. So the repair must enforce tracking, while respecting that the installer,
not `sync.mjs`, owns the root.

## 3. Chosen repair: an install-oracle parity gate with a declared-drift ratchet

**Implemented:** `tests/functional/test_root_install_parity.py` and
`tests/_baselines/root-install-drift.json`. It is read-only and needs no CI change: it runs inside
the existing blocking `unit-tests` job through `python3 tests/run.py`.

**The oracle is the installer itself.** The test runs a *fresh*
`scripts/install.sh --target <tempdir> --platform all`, never `--update` and never at the root. This
is the same operation `test_install_agents_mapping.py` already runs four times per suite. It then
compares the tempdir with the repo root under the installer's own ownership rules:

- **Byte equality** for every shipped file, excluding `docs/` (merge-preserve, project-owned once
  installed) and `implementation/` (at the root, that is the source itself).
- **Merge-owned MCP configs**, meaning any file shipped with a `<file>.provenance.json` sidecar
  (ADR-002), must be a fixed point of `merge-mcp-json.py`'s own `merge_json` and carry a
  byte-identical sidecar. That is exactly the condition under which `--update` would change nothing.
  Hand-added servers and `inputs` stay legal: the hand-added `cwso` server and `inputs` block in
  root `.vscode/mcp.json` pass, and a changed shipped value fails.
- **Root-only files.** Inside each tree that `install.sh` replaces with `rsync --delete`, a root-only
  file counts as drift unless `install.sh` declares it project-local. The tree list and the
  protected-path arrays (`CLAUDE_LOCAL_PATHS`, `GITHUB_LOCAL_PATHS`, the per-tree MCP excludes) are
  parsed from `install.sh`, not copied. A guard test fails if parsing ever yields nothing, which
  would make the gate vacuous.

**The ratchet.** `root-install-drift.json` lists the 49 paths that diverge today. The assertion is
`actual == declared`, in both directions:
- An undeclared divergence fails, so no new silent drift can land.
- A declared path that no longer diverges also fails, so the list cannot outlive a refresh.

Every entry is a recorded defect, not an exemption. The file says so, and its target state is empty.

**How the repo stays mergeable** (the plan-081 §1 shape, which this design avoids):

- **Green on arrival.** Measured: 7/7 tests pass on the current tree.
- **A knowledge MR that changes a projection without refreshing the root** (T549 is the next one)
  turns the gate red in *its own* pipeline. The failure message names the exact paths, and
  `python3 -m tests.functional.test_root_install_parity --print-drift` prints the list to paste.
  The author appends those lines, about 6 per changed command, in the same MR. That step is
  non-destructive and reviewable, and the lag now shows up in the MR diff instead of nowhere.
- **The MR that refreshes the root** removes the cured lines in the same MR, because the reverse
  direction forces it.
- **At no point does reaching green require a destructive step.** That separates this design from
  a red-on-arrival gate.

**Load-bearing proofs (measured):**

- A fresh install copied to a synthetic root shows zero drift.
- Each of these is detected, with exactly the expected paths:
  - an edited projection;
  - an edited `AGENTS.md`;
  - a deleted shipped file;
  - a hand-written `.clinerules/` file;
  - a changed shipped MCP leaf value;
  - a removed provenance sidecar.
- None of these counts as drift:
  - `.claude/settings.json` and `.claude/settings.local.json`;
  - `.github/workflows/ci.yml`;
  - `.vscode/settings.json`;
  - a reordered MCP config with a hand-added server and `inputs`.
- Removing one entry from the declaration fails with that path under "Undeclared". Adding a bogus
  entry fails with it under "no longer drifting". The file was restored afterwards.
- The same 7 tests pass with `rsync` hidden from `PATH`, which forces `install.sh`'s `cp` fallback,
  as on CI's `python:3.12-alpine` image.

**Known limits, stated rather than hidden:**

- A declared path's *content* is not pinned. A hand edit to an already-lagging root file, or a
  further source change to an already-declared file, does not re-trip the gate until the root is
  refreshed.
- `docs/` is out of scope by design.
- A harness MCP server removed upstream but hand-re-added at the root with a refreshed sidecar
  cannot be told apart from a hand-added one. That is the same boundary ADR-002 draws.

## 4. Rejected options

- **Extend `sync.mjs --check` to the root.**
  - **Wrong owner.** `sync.mjs` does not write the root, so it cannot judge it without
    re-implementing the installer's ownership rules: the MCP merge, the local-path excludes, the
    `AGENTS.md` render and the `CLAUDE.md` copy. A byte comparison against `implementation/` alone
    would flag the legitimately merged `.vscode/mcp.json` and `.claude/settings.json`.
  - **Red on arrival (49 paths) and red on every knowledge MR.** The only path back to green would
    be the destructive root `--update`. That is exactly the "unmergeable until a manual destructive
    step" shape, the same as plan-081 §1.
- **Have `sync.mjs` write both trees.** This collapses the ownership boundary bullet 2 now states.
  It would also create a *second* implementation of install semantics inside `sync.mjs` that could
  drift from `install.sh`, which is this task's defect class moved one level up. And it would make
  the routine `make sync` write the repository's runtime configuration as a side effect. The good
  part (the root refreshed in the same MR) is kept, via the installer, in §6.
- **A strict test asserting the trees agree (no ratchet).** This is the same red-on-arrival problem
  as the first option, with the same only-destructive path to green. The ratchet is what makes a
  test acceptable.
- **A pinned-revision gate** (record `fee245a` and assert root == install of source at the pin).
  This was considered and rejected:
  - It needs full history, which CI does not have: `GIT_DEPTH: "20"`.
  - It needs the *old* installer replayed.
  - It shows nothing in the MR that introduces lag.
- **Document the gap and require `install --update` at checkpoints.** This is what the repo already
  does, and it produced this state. The last root refresh was a release-time checkpoint action
  (`fee245a`, v7.0.0). Eleven days and several knowledge fixes later, 49 paths lag. The root staleness T403
  noted (2026-08-13) lasted five weeks, until that release-time refresh. The option also mandates the destructive step *more* often. Nothing in it
  would have caught T542.

## 5. Finding: the `install.sh` root asymmetry

At `TARGET == REPO_ROOT`, `install.sh` **refuses** a plain install. Its advice for "repo
maintenance" is `git pull && make sync && make verify`, and **none of those commands writes the
root.** The only mode it permits at the root is `--update`, which runs the full install:

- the `AGENTS.md` render;
- `install_docs`, including the `merge-task-docs.py` ledger merge on `docs/tasks/`;
- a self-copy of `implementation/runtime/{memory,security}` onto itself;
- `rsync --delete` of all eight trees;
- a `cp` of `CLAUDE.md`.

There is no mode that refreshes only the projections. So the safe-looking path leaves the root
stale, and the only path that fixes it is the one with a destructive history.

That history is concrete, not theoretical. The most recent root refresh, `fee245a` (2026-09-19),
shrank `docs/tasks/active-tasks.md` from **2460 lines to 11**. `e44c98a` ("active-tasks.md's
false-scaffold text…") repaired it afterwards. T382's run deleted `.claude/settings.json`, and its
row records the ledger-prose reset as "within T382's own brief's allow-list, not a defect". T518
(2026-09-25) has since fixed both specific mechanisms: the settings files are excluded, and ledgers
are spliced rather than replaced.

**I have not verified that a post-T518 root `--update` is now safe, because verifying it means
running it.** It still performs every step listed above in one invocation. By inspection only:
`install_docs` would seed no template files into root `docs/`, since all are present, and
`docs/tasks/_template.md` and `validate-tasks.py` are byte-identical to their templates.
`merge_ledger` still re-emits the ledger with its rows normalised, and I have not measured whether
that is byte-neutral on the current ledger.

This asymmetry is why "declare, don't refresh" is the only green-keeping move available today, and
why §6 exists.

## 6. What must happen next (not done here)

1. **A root sync is required to cure the defect. It is not performed in T543**, per brief §5. It
   needs explicit human approval as a separate, disclosed step.
2. **Recommended first: a projections-only root-refresh mode** as a follow-up task. For example,
   `install.sh --target . --self-refresh`: the eight trees, `AGENTS.md`, `CLAUDE.md` and the MCP
   merges, and never `docs/` or `implementation/runtime/`. It should be the one mode `install.sh`
   allows at the repo root, and it should be tested only against temp targets. With it, a knowledge
   MR can refresh the root in the same MR, so the declared list stays empty, and the asymmetry in
   §5 disappears.
3. **Then one human-approved refresh using that mode**, emptying `root-install-drift.json` in the
   same MR. The gate enforces the emptying.
4. **Optional, and a policy call for the orchestrator or user, not the DevOps engineer:** once item
   2 exists, make an empty declaration a release-tag condition. Before item 2 exists, that would
   re-create the destructive-step-to-release coupling, so it should not come first.
5. **Ordering with T549.** Whichever of T543 and T549 merges second must regenerate the
   declaration. The T549 change to `consolidate-memory.md` will add about 6 command-projection
   paths. `--print-drift` gives the exact list.

## 7. §3.4 and §3.5

**§3.4: which gate the root belongs to.** It is neither existing gate.
- `sync.mjs --check` owns `implementation/.<platform>/`.
- `generate-registry.py --check` owns `implementation/registry/index.json` checksums of knowledge
  sources.
- The root is the installer's output, so its gate sits beside the installer's other tests in
  `tests/functional/` and uses the installer as its oracle.

**§3.5: one gate for both.** `AGENTS.md` at the root is an install output of exactly the same kind:
`install_agents_doc` renders it through `render_installed_agents.py`. Because the gate compares the
root against a fresh `--platform all` install, it asserts render identity for `AGENTS.md`, not
plain equality with `implementation/AGENTS.md`, with no extra code. The same applies to
`CLAUDE.md`, which is a plain `cp`. Both hold today.

**Scope disclosure.** The brief puts an `AGENTS.md` parity test out of scope. I did not write one,
but the unified gate covers `AGENTS.md` as a direct consequence of this verdict. Excluding it would
need special-casing that contradicts the verdict. If the orchestrator wants it out, drop `AGENTS.md`
from the compared set in `compute_drift`. That is a one-line exclusion, and I recommend against it.

## 8. Corrections to the brief

- **§1 and §4 name six root folders; the installer owns eight.** `.cline/` has 1 divergent path
  today and `.clinerules/` has 0.
- **§3.2's precedent** is verified as to mechanism: manual root `--update`, outside
  `sync-no-diff`'s scope. It is not a stated design decision that lag is intended. T403 records the
  staleness as deferred work, and no ADR exists.
- **§3.5's "zero tests invoke the renderer"** is imprecise. The four tests in
  `test_install_agents_mapping.py` invoke it via `install.sh` into tempdirs, with substring checks.
  Its substantive claim holds: nothing asserted root identity until now.
- **§5's "a past `--update` run … reset `active-tasks.md`"** understates it. It was the *most
  recent* root refresh, `fee245a`.
- **§6** lists `node implementation/scripts/sync.mjs --check` without `--root`. This is not a
  defect: `--root` defaults to the script-relative `implementation/`, and the result is identical
  (exit 0, 577 files).
- **§7** says to commit on the branch with a `Co-Authored-By: Claude Opus 5` trailer. The dispatch
  says to hand back uncommitted. I followed the dispatch.
