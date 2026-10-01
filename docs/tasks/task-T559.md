# T559 — `install.sh` batch: P17, P18, P20, P21

**ID:** T559
**Owner:** DevOps Engineer
**Status:** pending
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** —
**Created:** 2026-10-01
**Based on:** `docs/plans/plan-089-install-and-golden-batches.md`; `docs/plans/plan-085-index-leak.md` §3 (P17, P18);
`docs/plans/plan-086-round-close.md` §2 (P20, P21); `docs/artifacts/install-update-root-v1.md`;
`docs/artifacts/install-exclude-parity-v1.md`.

Four small `scripts/install.sh` items parked by T552 and T555, batched because they share one file
(`plan-083` decision 2). Keep **one commit per item** so each is reviewable.

## P17 — `--target <repo>/implementation --update` still writes the source

T552 found that targeting the repository's own `implementation/` directory re-renders `implementation/AGENTS.md`
over itself, creates `implementation/implementation/`, and exits 1 at the `CLAUDE.md` self-copy. T552's
`same_tree` guard already stops the `.cursor/` deletion. **Refuse any target that is, or is inside, this
repository's `implementation/` directory** — compare with `-ef` as `target_is_repo_root()` does, so aliases are
caught. Decide whether to refuse any target *inside* the repository at all (other than the root, which is
already handled) and argue it.

## P18 — `--update`'s help text understates that the ledger file is rewritten

The help says the ledger is "never rewritten beyond its task rows" (find the exact wording; T550 §5.3).
`merge_task_docs` always rewrites both ledgers and drops non-conforming rows. Make the text accurate.

## P20 — `docs/tasks/__pycache__/` ships on every fresh install

`implementation/docs/tasks/__pycache__/` **exists in the source tree today** (verified 2026-10-01), and the
`docs/` copy passes no excludes, so every fresh install ships it (with or without `rsync`). Exclude
`__pycache__` from the `docs/` copies. This deliberately changes what fresh installs and `--update` write —
say so, and prove nothing else changes.

## P21 — `cp`-fallback file/directory type conflicts

When a target has a directory where the source has a file (or the reverse), `copy_tree_into`'s `cp` fallback
exits 1 where `rsync` replaces the path: 26 of 300 fuzz cases after T555 (58 before). In one case `cp` wrote
through a symlink in the target. Make the fallback match `rsync`'s replace semantics, or — if exact parity is
unreasonable — make it fail **before writing anything** with a clear message, and argue the choice. Re-run a
differential fuzz against real `rsync`, as T555 did, and report the before/after counts.

## Constraints

- **Never run any install against this repository's root or the main checkout.** Synthetic copies in temporary
  directories only, under **both** `rsync` and the `cp` fallback (hide `rsync` from `PATH`).
- **Compare old vs new by swapping `install.sh` in place**, verifying its sha256 after each restore — never by
  copying it elsewhere (a copy resolves `REPO_ROOT` to the wrong directory).
- Every invocation not deliberately changed must be unchanged in what it writes; record and compare
  invocations as T552 and T555 did.
- **Write scope:** `scripts/install.sh`, files under `tests/functional/`, `docs/artifacts/install-batch-v1.md`,
  and this brief's `**Status:**` line. Do **not** delete `implementation/docs/tasks/__pycache__/` from the source
  tree — it is gitignored build output; excluding it is the fix.
- `--print-drift` must stay equal to the committed list (6 `/batch` paths today).
- Commit locally; **do not push; never merge or approve anything.** A QA Engineer runs in parallel on
  `tests/golden/**` and `docs/benchmarks/` — stay out of those.

## Verification

`python3 tests/run.py` (exit code; redirect to a file, never pipe to `tail`), the audience lint and parity gate,
`validate-tasks.py`, `check-maturity.py`, and `git status` of your worktree and the main checkout unchanged by the
suite (the main checkout's ` M .vscode/mcp.json` is the user's own — leave it, don't read it).

## Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`. If anything in this
brief is wrong, report it rather than working around it.
