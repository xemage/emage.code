# T557 — Lint: commands declared `both`/`target` must not name paths installed targets never receive

**ID:** T557
**Owner:** QA Engineer
**Status:** pending
**Priority:** P2
**Tier:** judgment
**Affects:** —
**Depends on:** T556
**Created:** 2026-10-01
**Based on:** `docs/plans/plan-087-audience-key.md` §3 (P23, P22); `docs/plans/plan-088-audience-lint.md`;
`tests/functional/test_root_install_parity.py` (the pattern to reuse); `docs/artifacts/command-audience-resolution-v1.md` §2.

## 1. Why

T556 made every command declare `audience: authoring | target | both`. The declaration is only worth something
if it is **checked**. This phase found, by hand, four `stable` commands naming paths that installed projects
never receive (`/consolidate-memory`, `/discover-skills`, `/handoff`, `/skillify`). This lint finds that class
mechanically, so the next one is caught in CI, not by a reviewer.

## 2. The design — reuse T543's oracle, don't hand-maintain a list

`tests/functional/test_root_install_parity.py` already runs a fresh `install.sh --platform all` into a
`TemporaryDirectory` and compares. Do the same here:

1. Run one fresh install into a temporary directory (reuse `run_fresh_install`; **never** `--update`, never
   against the repository).
2. For every command in `implementation/knowledge/commands/*.md` whose `audience` is `both` or `target`, extract
   the **path-like references** in its body. Decide and document the extraction rule — at minimum backticked
   tokens containing `/`. A `<placeholder>` segment (`<name>`, `<platform>`, `<ID>`) should become a glob
   segment. Ignore URLs.
3. A reference is a **violation** when it resolves to something that exists in this repository but **does not
   exist in the fresh install**. Decide and document how a token resolves (relative to the repository root; also
   relative to `implementation/`?) and argue it.
4. **Declared exceptions** live in a committed baseline, `tests/_baselines/command-audience-paths.json`, each
   entry `{command, path, reason}`. Some mentions are legitimate: `/skillify` and `/discover-skills` name
   `implementation/knowledge/skills/…` **in their authoring row**, which is correct. The gate **fails in both
   directions**, like the parity gate: an undeclared violation fails, and a declared entry that is no longer a
   violation also fails, so the list cannot rot.
5. `authoring` commands (today only `/prepare-release`) are exempt; say so in the test.

## 3. P22 — what the first run will probably show

`/discover-skills` step 6 merges "pack registry entries" from `packs/installed/`, which no pack format contains
(T554 hand-back); `install.sh` never ships `implementation/packs/`. Report whether the lint flags it. **Do not
edit the command.** If it is flagged, declare it in the baseline with reason `P22 — tracked no-op, see
plan-087 §3`, so the fix becomes a separate decision rather than a silent edit.

## 4. Prove it is load-bearing

- Add one `both` command reference to an authoring-only path in a **temporary copy** (e.g. append
  `` `implementation/registry/index.json` `` to a scratch copy of a command, or test the detector against a
  synthetic command file) and show the gate fails naming exactly that command and path.
- Remove one declared baseline entry and show it fails as undeclared; add a bogus entry and show it fails as
  no-longer-a-violation.
- Show a `<placeholder>` path that exists in the fresh install (e.g. `.<platform>/skills/<name>/SKILL.md`) is
  **not** flagged.

## 5. Constraints

- **Write scope:** a new test under `tests/functional/`, the new baseline under `tests/_baselines/`, and the
  `**Status:**` line (to `in_review`) of this brief. **No** edit to any command, schema, manifest, script,
  `tests/golden/**`, or `scripts/scorecard.py`.
- If the first run flags something that looks like a **real** defect (not a legitimate authoring-row mention),
  **report it** and declare it with an honest reason — don't paper over it and don't fix it here.
- Commit locally, one commit, ending `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. **Do not push;
  never merge or approve anything.**

## 6. Verification

`python3 tests/run.py` (exit code; redirect to a file, never pipe to `tail`) — the new test must pass on the
current tree; `--print-drift` still `[]`; `validate-tasks.py`; `check-maturity.py`; `git status` of your
worktree **and** the main checkout unchanged by the suite (the main checkout's ` M .vscode/mcp.json` is the
user's own; don't read it). Also run the new test in isolation and report its runtime.

## 7. Blocker protocol

`technical` | `dependency` | `unclear_requirements` | `external`; `critical` | `major` | `minor`. **If anything in
this brief is wrong, report it rather than working around it** — nineteen briefs this phase had defects.
