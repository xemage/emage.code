# plan-153 — `context-retriever`: the LOW residue after T790 (batch O)

**Created:** 2026-11-12
**Based on:** `docs/artifacts/tracked-debt-register-v14.md` (§ 5 batch O; rows SEC-T791-02, SEC-T791-03, QA-T792-1); `docs/artifacts/security-review-t791-context-retriever-v1.md` § Findings; `docs/artifacts/qa-recheck-t792-context-retriever-v1.md` § Observations. The user's instruction of 2026-11-12, verbatim: "O go". The orchestrator reads it as the word for batch O as register v14 defines it. It is not read as approval of a release, a tag or a root refresh.
**Scopes:** `T795`, `T796`.

## Goal

Register v14 batch O holds three tracked-LOW ids, all in the index-build path that plan-151 changed (read here on `34f8ea7f`):

- **SEC-T791-02** (SECURITY:LOW, A09). `case_mismatched_paths` (`implementation/runtime/memory/build.py:110-119`) warns only when an own-repo project-scope entry's `project_id` differs from `--project-id` by letter case. Any other difference (a typo, `org/repo.git`, the top group of a nested path) is indexed and never returned, with no message. It fails closed; nothing is exposed.
- **SEC-T791-03** (SECURITY:LOW, A03). `is_derived_project_id` (`implementation/runtime/memory/context_retriever.py:134`) accepts `a/..` and `a/.`, and raises `AttributeError` on a non-string. It reaches no path, and its only caller checks the type first (`build.py:53`).
- **QA-T792-1** (Low, QA's scale). `print_memory_index_notice` (`scripts/install.sh:1728-1745`) prints the install line with its own `python3 -m venv .venv-mcp && source .venv-mcp/bin/activate && …`, and the printed build command after it has no `source` prefix. Run as separate commands, the build runs on the system `python3`.

## Task Decomposition

1. **T795** (backend-developer), in worktree `../worktrees/agent-backend-developer-T795`, branch `agent/backend-developer/T795`:
   - **SEC-T791-02:** the build warns on stderr, by path only (never entry content), for every own-repo project-scope entry whose `project_id` is not `config.project_id`. The case-only wording stays as it is; any other difference gets its own wording that says `retrieve` will not return the entry. The entry stays indexed and is still never returned: **`scope_filter.py` does not change**, and nothing is rewritten. Entries from the general or shared roots are out of scope unless the code shows the same silent drop there; report what it shows.
   - **SEC-T791-03:** `is_derived_project_id` returns `False` for a non-string and for any `.` or `..` segment. `normalize_remote_to_project_id` refuses a remote whose `<org>` or `<repo>` is `.` or `..` with `RemoteResolutionError` (the server then does not start, which fails closed). Report any caller whose behaviour changes.
   - **QA-T792-1:** the printed build command runs in the same venv as the printed install line, either because it is prefixed with `source .venv-mcp/bin/activate &&` or because a single venv line is printed first. Paths stay shell-quoted (`%q`, SEC-009). The installer still installs nothing itself.
   - Tests for each, including a negative case each: a case-only difference keeps its wording; an entry whose `project_id` matches gets no warning; `normalize_remote_to_project_id` still accepts the normal remotes of `memory-scope-model-v1.md` § 3.
   - Text that ships to targets and would now be false (`implementation/runtime/memory/README.md`, `implementation/PREREQUISITES.md`, `docs/wiki/mcp-servers.md`) is corrected. `docs/releases/*` are published records and do not change.
   - No top-level platform folder changes. If a generated mirror changes, regenerate with `node implementation/scripts/sync.mjs --root implementation` and `python3 implementation/scripts/generate-registry.py`, and declare any root drift (`tests/functional/test_root_install_parity.py --print-drift`) in the report.
   - *Acceptance:* each id's failure as recorded no longer occurs; `sync.mjs --check` and `generate-registry.py --check` pass; the full suite passes; no file under `tests/golden/` changes.
2. **T796** (security-engineer), read-only: review T795's diff. Points: `scope_filter.py` is untouched and still fails closed; the warning prints paths only, never content; the dot-segment refusal cannot make the server resolve another project's index; the printed lines cannot run a name in a path. Verdict and the final status of SEC-T791-02 and -03 on the `SECURITY:*` scale.
3. **The orchestrator:** re-runs QA-T792-1's printed lines in a temporary directory; the gates and the full suite in a clean worktree; the MR and its pipeline; commits the review artifact; closes the tasks; merges on green, pinned to the verified sha. The ids' new status goes into register v15 through this plan's Outcome. **A root refresh, if the drift needs one, is a separate step and needs the user's approval at that moment.**

## Constraints

- No `docker` command. Never open `tests/golden/held-out/`; recursive searches over `tests/` exclude it. Read no `.env*` or credential file, and not the user's `.claude/settings*.json` or `.vscode/*.json`.
- Derived folders are generated, never hand-edited. Top-level platform folders are not touched in this plan.
- Functions stay at 50 lines and 4 parameters at most. Conventional Commits.
- Subagents never merge, tag or release.
- Token budget: T795 100k, T796 60k.

## Addendum (2026-11-12): fix task after the T796 FAIL

T796 v1 (`docs/artifacts/security-review-t796-context-retriever-v1.md`) failed T795 on **SEC-T796-01** (SECURITY:LOW, blocking under the gate rule as a missing § Logging control): the `RemoteResolutionError` messages of `normalize_remote_to_project_id` repeated the remote URL with any `user:token@` part. The orchestrator routes it to a fix rather than asking for a ruling on whether an exception message is logging.

4. **T797** (backend-developer), same worktree and branch: redact the userinfo in every message that carries a remote URL, with tests (a secret in the userinfo appears in no message; normal remotes normalise as before). Then **T796 re-reviews** the fix and records a v2 artifact.

## Outcome (2026-11-12)

- **T795 is done** (commits `d480c31d`, `344691b8`, `15e427ba`):
  - **SEC-T791-02:** `build.py` `foreign_project_paths` and `_warn_project_id_mismatches` warn on stderr, by path only, for every own-repo project-scope entry whose `project_id` is not `--project-id`; the case-only wording is kept. Entries stay indexed; `scope_filter.py` is unchanged. The general and shared roots show no such silent drop (the developer's reading, confirmed by T796 point 1).
  - **SEC-T791-03:** `is_derived_project_id` returns False for a non-string and for `.`/`..` segments; `normalize_remote_to_project_id` refuses a `.`/`..` org or repo. A workspace with such a remote: the server does not start (default), or every `retrieve` fails (with `--index-dir`); both fail closed (T796 point 3).
  - **QA-T792-1:** the printed build command starts with `source .venv-mcp/bin/activate &&`. The orchestrator re-ran the printed lines, each in its own shell, in a temporary install target: the build line runs `.venv-mcp/bin/python3`, the old line ran `/usr/bin/python3` (the `pip install` of fastembed was not run, so the build itself stopped at the missing `yaml`).
- **T796 v1: FAIL** on **SEC-T796-01** (SECURITY:LOW, blocking as a missing § Logging control): the `RemoteResolutionError` messages repeated a remote URL's `user:token@` part. Routed to a fix, not a ruling.
- **T797 is done** (commit `47e56c56`): `_redacted()` replaces the userinfo with `***@` before the 200-character cut, in all three messages; no other message site carries a remote URL.
- **T796 v2: PASS** (`docs/artifacts/security-review-t796-context-retriever-v2.md`): SEC-T796-01 fixed, no new finding; observations O-1 (malformed URL with a raw `/` in the password, slug message) and O-2 (query string in the remote) carry no grade and no action.
- **For register v15:** SEC-T791-02, SEC-T791-03 and QA-T792-1 **fixed** (batch O ends); SEC-T796-01 minted and **fixed** in this plan.
- **No root drift** (`--print-drift` gives `[]`; no generated mirror changed).
- **The orchestrator's checks:** see the merge request; the full suite in a clean worktree and the pipeline run at the merged sha.
