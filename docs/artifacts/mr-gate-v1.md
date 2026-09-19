# Human MR Gate — v1

**Based on:** `docs/tasks/task-T505.md` (`plan-035-roadmap-v7-ground-up.md`'s nominal `T464`,
`plan-055` §4's `T464-equiv` row), `implementation/runtime/meta_improver.py` (T503, real, merged,
`DiffProposal` — this task's other real, concrete input), `implementation/runtime/golden_harness/
promotion.py` (T504, real, merged, `PromotionResult` — this task's real, concrete gating input),
`tests/functional/test_meta_improver.py`'s `TestNoFilesystemMutation` class (the two-independent-
proofs pattern this task's own "no auto-merge path" proof mirrors), `.claude/rules/git-workflow.md`
(branch naming, commit message format, MR rules — reused, not reinvented), `docs/tasks/task-T341.md`/
`task-T343.md`/`task-T347.md` (real prior `glab mr create` usage in this exact repo),
`docs/artifacts/phase6-kill-switch-v1.md` (T502) and `docs/artifacts/promotion-rule-v1.md` (T504,
style precedent for this document).

**Refs:** T505. Builds the human MR gate — the first point in Phase 6's closed loop where a
proposal's content is ever allowed to touch a real, tracked repository file.

## 1. What this document declares

This repository now has a real, tested human MR-gate module:

- `implementation/runtime/golden_harness/mr_gate.py` — the importable library: `open_promotion_mr`,
  `compute_branch_name`, `build_commit_message`, `build_mr_title`, `build_mr_description`,
  `find_auto_merge_calls`, and the `MrGateResult` / `PromotionNotApproved` result/exception types.
- `tests/functional/test_golden_harness_mr_gate.py` — the committed test suite proving every
  property documented below.

## 2. Branch-naming scheme, adapted from this repo's own convention

`.claude/rules/git-workflow.md` "Agent Worktree Branch Naming" establishes
`agent/<agent-name>/<task-id>` for a human agent's own task branch. This task has neither a human
agent name nor a task ID — the branch is produced automatically from a `DiffProposal`, not dispatched
against a ledger row.

**Decision:** `meta-improver/<target-path-slug>-<digest>` (`compute_branch_name`), where
`<target-path-slug>` is `proposal.target_path`'s filename stem (lowercased, underscores replaced with
hyphens) and `<digest>` is the first 12 hex characters of `sha256(f"{target_path}:{based_on[0]}")`.

**Why:**
- **`meta-improver/` names the actual originator**, mirroring `agent/<agent-name>/...`'s own
  "who/what produced this branch" convention exactly, substituting the automated generator's own name
  (`@meta-improver`, T503) for a human agent's name.
- **Deterministic, not random.** Re-running `open_promotion_mr` against an *unchanged* proposal
  (same target path, same first triggering case id) always produces the same branch name — a
  re-attempt after a transient push failure targets the same branch rather than accumulating an
  ever-growing pile of near-duplicate branches. A proposal whose target path or triggering case ids
  differ produces a different, non-colliding branch name.
- **The digest, not the full slug, carries the uniqueness.** The filename-stem slug alone is
  human-readable at a glance (`meta-improver/naming-conventions-...`) but is not guaranteed unique
  across distinct proposals targeting the same file from different clusters; the 12-hex digest
  (derived from the target path *and* the first triggering case id together) disambiguates those
  without needing a random/timestamp component, which would break the determinism property above.
- `compute_branch_name` is a pure function — no I/O, no git call — so a caller/test can compute the
  expected branch name for a given proposal without exercising this module's git side effects at all.

## 3. Commit message format

`build_commit_message` produces a real Conventional Commit
(`.claude/rules/git-workflow.md` "Commit Messages"):

```
feat(harness): apply meta-improver proposal for <target_path>

<rationale>

Refs: <based_on case ids, comma-separated>
```

`type(scope)` is always `feat(harness)` — every proposal this module can ever gate is, by
`meta_improver.py`'s own construction, a proposed addition/change to this repo's harness surface
(`implementation/knowledge/{agents,skills,commands,instructions}/**`, enforced by
`classify_target_path` before a `DiffProposal` can even be constructed), so `feat(harness)` is
always the correct, honest type/scope pair — this module does not need to infer `fix`/`docs`/etc.
from proposal content. The commit message alone carries the triggering case ids and the rationale, so
a reviewer can understand *why* the change is proposed directly from `git log`, without needing the
MR description.

## 4. What the function does, and the "no such parameter exists" proof

`open_promotion_mr(proposal: DiffProposal, promotion_result: PromotionResult, *, repo_root:
Path | None = None, base_branch: str = "develop", remote: str = "origin") -> MrGateResult`

1. **Refuses first.** Raises `PromotionNotApproved` — before any git or `glab` call is attempted —
   if `promotion_result.promote is not True`. Proven by
   `tests/functional/test_golden_harness_mr_gate.py`'s `TestRefusalGate`, including
   `test_refusal_makes_zero_subprocess_calls`, which patches this module's own `subprocess.run` entry
   point and asserts it was never called on the rejected path — not merely that the return value
   looks like a failure.
2. Creates a real branch off `f"{remote}/{base_branch}"` inside an isolated `git worktree` (a
   `tempfile.TemporaryDirectory`, removed after the branch is pushed) — this deliberately does not
   check out the new branch inside whatever working directory `repo_root` already has checked out,
   so this function never disturbs a caller's own checkout state.
3. Writes `proposal.proposed_content` to `proposal.target_path` inside that worktree, and only that
   path — no other file is ever created or modified in the branch's diff
   (`tests/functional/test_golden_harness_mr_gate.py`'s
   `test_writes_only_the_target_path_within_the_scratch_worktree`).
4. Commits (`build_commit_message`), pushes the branch to `remote`, and removes the temporary
   worktree.
5. Opens a real MR against `base_branch` via `glab mr create` — this repo's own already-established
   convention (`docs/tasks/task-T341.md`/`task-T343.md`/`task-T347.md`), not the `mcp__gitlab` MCP
   server — with a description (`build_mr_description`) containing `proposal.rationale` and
   `proposal.diff_text()` verbatim, plus `promotion_result.reason` for a reviewer's convenience.
6. **Then stops.** No further call of any kind is made on the opened MR.

**The "no such parameter exists" proof (brief's Objective point 3 / "no auto-merge path" §3):**
`branch_name` is computed *internally* by `compute_branch_name` and is not, and has never been, a
parameter `open_promotion_mr` accepts. The function's only `git push` call
(`_run(["git", "push", remote, branch_name], cwd=worktree_dir)`) therefore always targets the branch
this function itself just created in step 2 — there is no flag, parameter, or environment variable
anywhere in this module's signature or body that could redirect that push call to `base_branch`,
`develop`, or `main` directly.
`tests/functional/test_golden_harness_mr_gate.py`'s `test_never_pushes_to_develop_or_main_directly`
is the behavioral companion proof: it inspects the actual (mocked) `git push` call made during a real
execution and confirms its ref argument is never `develop`/`main`/`origin/develop`/`origin/main`.

During implementation, no legitimate reason was found to add a caller-supplied override for the push
target, the branch name, or any merge/approve action — per the task brief's own standing instruction
("if you find yourself needing any such parameter for a legitimate reason, stop and report it as a
blocker rather than adding it"), none was added, and none was needed.

## 5. The "no auto-merge path" property — the full proof

This is the load-bearing safety property of this module, mirroring `meta_improver.py`'s own "never
writes to a real repo file" guarantee's two-independent-proofs discipline exactly, applied to a
different property.

### 5.1 The static AST scan (`find_auto_merge_calls`)

Walks every `ast.Call` node in a module's source and flags:

| # | Banned shape | Detection rule |
|---|---|---|
| 1 | `glab mr merge` | A `subprocess.*`/`os.system`/`_run` call whose literal argv contains both `"mr"` and `"merge"` tokens, or the literal substring `"mr merge"` in a shell-style command string |
| 2 | `glab mr approve` | Same shape, `"mr"` + `"approve"` / `"mr approve"` |
| 3 | `git merge` | A literal argv `["git", ..., "merge", ...]` — `"merge"` present anywhere after the leading `"git"` token |
| 4 | `git push --force` / `-f` | A literal `git push` argv also containing `"--force"` or `"-f"` |
| 5 | `git push` to `develop`/`main` directly | A literal `git push` argv containing the bare token `"develop"`, `"main"`, `"origin/develop"`, or `"origin/main"` |
| 6 | GitLab REST API merge/approve endpoint | An HTTP verb call (`.post()`/`.put()`/`.patch()`) whose string argument contains `"merge_requests"` and ends with `"/merge"` or `"/approve"` |
| 7 | Named merge/approve MR tool/method call | `.merge()`/`.approve()` called on a receiver whose identifier subtree contains `"mr"` or a `"merge_request(s)"`-containing token, or a direct call to `merge_merge_request`/`approve_merge_request`/`gitlab_merge_merge_request`/`gitlab_approve_merge_request` (representative `mcp__gitlab`-style tool-call names, per the task brief's own explicit call-out for that server) |

The scanner treats calls to this module's own `_run` wrapper identically to a raw `subprocess.*`
call — every real call site in `mr_gate.py` passes its own full, literal argv (including the leading
`"git"`/`"glab"` program name) directly to `_run`, so the scan sees the same argv shape it would see
from a raw `subprocess.run(...)` call, rather than a generic, already-abstracted argument list.

**Non-literal (dynamic) argv elements** — a variable, an f-string, an attribute access — become an
opaque `_DYNAMIC` placeholder rather than being resolved, and never spuriously match a banned literal
token. This module's own real branch names, commit messages, and file paths are always such
non-literal expressions (computed by `compute_branch_name`/`build_commit_message`/
`proposal.target_path`), so real calls like `_run(["git", "push", remote, branch_name], ...)` are
correctly scanned as clean: the scanner is checking whether *this module's own source* ever contains
the literal banned tokens, and it never does — the only place `"develop"`/`"main"` appear as literal
strings anywhere in `mr_gate.py` is the `DEFAULT_BASE_BRANCH`/`_GIT_PUSH_PROTECTED_REFS` module-level
constants and `base_branch`'s default parameter value, none of which are ever passed to a `git push`
call (only to `git fetch`, `git worktree add`'s *source* ref, and `glab mr create --target-branch`).

**Documented, disclosed limitation:** this is a static, argv-shape scanner, not full data-flow
analysis. A call whose entire argv is built from a pre-existing variable (e.g. `subprocess.run(cmd)`
where `cmd` was assembled elsewhere) is not argv-analyzable and is silently skipped
(`_string_tokens_from_argv` returns `None`). This module's own coding convention never does this —
every real call site passes its argv inline as a list/tuple literal — and this document states that
convention as a standing constraint on any future edit to this module, exactly as
`docs/artifacts/protected-paths-v1.md` states its own boundary as "declarative and auditable... not a
git-level enforcement mechanism."

### 5.2 Adversarial tests proving the scanner is a real detector

`tests/functional/test_golden_harness_mr_gate.py`'s `TestNoAutoMergePath`:

- `test_static_scan_finds_zero_violations_on_real_source` — the real proof: `find_auto_merge_calls`
  against this module's own real, on-disk source returns `[]`.
- `test_static_scan_detects_a_synthetic_violation` — one synthetic snippet per banned shape in the
  table above (17 cases, including both list-argv and shell-string-argv forms for shapes 1–2, both
  `subprocess.run`/`check_call`/`check_output`/`Popen`/`os.system` and this module's own `_run`
  wrapper), each individually confirmed to produce a non-empty violation list.
- `test_static_scan_does_not_false_positive_on_legitimate_calls` — a snippet containing exactly the
  legitimate call shapes this module's own real source needs to make (`glab mr create`,
  `git push <own-branch>`, `git commit`, `git checkout -b`, plus the equivalent `_run`-wrapped forms
  and the intermediate `git add`/`git worktree remove --force` calls this module also makes), confirmed
  to produce zero violations.

### 5.3 The runtime guard, independent of the AST proof

Per §4 above: `branch_name` is never a caller-suppliable parameter, so the one `git push` call this
module ever makes cannot be redirected to `develop`/`main` by any argument, flag, or environment
variable. No parameter, flag, or environment variable anywhere in this module enables a merge,
approve, or direct-push-to-protected-branch code path — confirmed directly by reading this module's
own full source during implementation, and by the absence of any such parameter in
`open_promotion_mr`'s signature.

## 6. What this does *not* do (scope boundary)

- **Does not decide promote/reject itself.** `open_promotion_mr` consumes a caller-supplied
  `PromotionResult` (T504's `evaluate_promotion`) — it has no logic of its own for evaluating
  control/treatment trial data, floor/regression/hash checks, or any other promotion criterion.
- **Does not retry a failed push or MR-create call.** If any `git`/`glab` call in the sequence fails
  (non-zero exit, via `subprocess.run(..., check=True)`), the whole call raises
  `subprocess.CalledProcessError` and stops — no automatic retry, no partial-state cleanup beyond the
  `finally`-guarded `git worktree remove`.
- **Does not merge, approve, or auto-accept any MR, including its own build-phase MR.** See §5 above
  for the full proof.
- **Does not perform the live end-to-end validation exercise.** Per the task brief's "Orchestrator-
  owned live validation" section, generating a real proposal, constructing its `PromotionResult`, and
  running it through this mechanism to produce a real, open, unmerged MR is the orchestrator's own
  separate, subsequent action — not part of this module's own build or test suite.
- **No dependency on `implementation/sia/`, `implementation/adapters/sia-target/`, or
  `implementation/scripts/sia-executor.py`.**
- **Does not build T506** (the harness-lineage document) — a separate, parallel task.

## 7. Verification

- `tests/functional/test_golden_harness_mr_gate.py` — 16 tests: `TestRefusalGate` (3, including the
  zero-subprocess-calls proof), `TestBranchCommitMrContent` (6, pure-computation content builders),
  `TestOpenPromotionMrMocked` (4, full call-sequence and written-content proof with every subprocess
  call mocked), `TestNoAutoMergePath` (3, the real-source-clean scan, the 17-case synthetic-violation
  detection, and the no-false-positive proof).
- Run directly: `python3 -m unittest tests.functional.test_golden_harness_mr_gate -v`.
- Included automatically in `python3 tests/run.py` (discovered under `tests/functional/`).
- `tests/functional/test_golden_held_out_isolation.py` re-run fresh after adding this task's files:
  passes — no held-out isolation violation introduced (this module neither references
  `tests/golden/held-out/` nor mentions any held-out case id).
