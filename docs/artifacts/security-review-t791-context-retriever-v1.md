# Security review — T791: context-retriever code residue (plan-151)

## Metadata
- **Date:** 2026-11-12
- **Reviewer:** security-engineer (read-only; no file modified)
- **Task:** T791, plan-151
- **Based on:** `docs/plans/plan-151-context-retriever-code-residue.md`, `docs/artifacts/qa-release-v10-v1.md` (QA-T760-01, -02, -03, condition C1), and the diff range `5e7d0fff..cf7366b7`, read as a scratchpad copy of the diff (688 lines) and checked against the worktree `agent-backend-developer-T790`.

Committed by the orchestrator from the Security Engineer's report; the text is the report's.

## Verdict
**PASS**

No CRITICAL, HIGH or MEDIUM issue. No Immutable Security Constraint is breached, and no required control is removed or weakened. The query-time scope filter is unchanged and still fails closed. The three LOW findings below go into the debt register under the user's standing rule ("Track LOW items as debt, stop chasing (Recommended)"). SEC-T791-01 must reach the v11.0.0 migration notes before that release ships.

## Status of the QA ids

| ID | Status | Evidence |
|---|---|---|
| QA-T760-01 | **fixed** | `scripts/install.sh:1728-1745`: `print_memory_index_notice` prints the install line for `implementation/runtime/memory/requirements.txt` before the build command, only when the target holds that file (`:1734-1736`). The path is quoted with `%q`; the function installs nothing. |
| QA-T760-02 | **fixed** | `build.py` refuses any `--project-id` not in derived form: the CLI through argparse `type=_project_id_arg` (`build.py:223-224`), library callers through `BuildConfig.__post_init__` raising `ValueError`; both use `context_retriever.is_derived_project_id` (`context_retriever.py:134-144`). An entry whose frontmatter `project_id` differs only by letter case is named on stderr (`build.py:110-119`, `:266-272`, called at `:260` and `:286`) and stays invisible because the exact compare is unchanged (`scope_filter.py:52`). |
| QA-T760-03 | **fixed** (in the generated tree; the root waits for its refresh) | `servers.yaml:196` passes `{{platformDir}}`, which `sync.mjs:245-251` and `:809-813` replace with the manifest's `outputDir`: `implementation/.cline/mcp.json:86` (`.cline`), `implementation/.opencode/opencode.json:99` (`.opencode`); `implementation/.mcp.json` unchanged. The root `.cline/mcp.json` and `.opencode/opencode.json` still pass `.claude` until the root refresh; they are declared in `tests/_baselines/root-install-drift.json`. |

## Answers to the points in the brief

1. **A01, access control.**
   - The diff does not touch `scope_filter.py`. `is_visible` still compares exactly (`:52`); unknown scopes and empty shared consumers still return False (`:55`, `:69-70`).
   - The refusal holds: on the CLI argparse refuses the value before `BuildConfig` exists; in the library the dataclass is frozen and `dataclasses.replace` runs `__post_init__` again. Only in-process code (for example `object.__setattr__`) gets around it, which is not a trust boundary. `project_id_problem` checks `isinstance(..., str)` first, so non-string input is refused rather than raising.
   - The build-time id decides only which shared-scope entries are admitted (`build.py:196-198`) and what the manifest records. A chunk's `project_id` comes from the entry's own frontmatter (`enrich.py:49`). The access decision is made at query time against `derive_project_id`.
   - `is_derived_project_id` is a pure function: it builds a dummy URL and compares strings; it never builds a `RequestingContext` and never runs git. `derive_requesting_context` (`context_retriever.py:176-183`) is still the only place a context is built. Importing `context_retriever` into `build.py` runs nothing at import time, and the modules it pulls in were already reachable from `build.py`.
2. **Platform identity.**
   - The value comes from the server's launch configuration, not from a tool call. The generator only writes an `outputDir` that matches `^\.[a-z][a-z0-9-]*$` (`sync.mjs:232`, `:247-249`), which excludes `/`, `..`, upper case and absolute paths.
   - One platform resolves as another only if a workspace's own `.cline/.generated-manifest.json` says so; anyone who can write that file could already write `.claude/…`. The trust model is unchanged.
   - The server resolves `--platform-root` against its working directory, as it did before. Whether Cline and Opencode start stdio servers in the workspace root is **(unverified)**.
   - **The behaviour change is a correction, not a widening.** Before, a Cline or Opencode session was identified as `claude-code`: it could see shared entries meant for `claude-code` only and could not see entries meant for its own platform. Now it sees exactly what `shared_consumers.platforms` names for it. Users see the change, so the v11.0.0 migration notes must state it (SEC-T791-01).
3. **`is_derived_project_id`.** `a/..` and `a/.` pass; the server would derive exactly those ids from such a remote, and they become one directory name (`a-..`), never a path step. `../x`, `./a` and `-a` fail on the first character. Ids with more than two segments, a trailing `.git`, `a//b`, `a/b/`, upper case, spaces, a newline and more than 200 characters are refused. Called directly with a non-string, the predicate raises `AttributeError`; its only caller checks the type first. None of these ids reaches a path in `build.py`, which takes `--output-dir` separately (SEC-T791-03).
4. **A03/A05, the printed note.** The new line prints a constant relative path through `%q`, and `$TARGET` is printed through `%q` (`install.sh:1733`, `:1735`). Every other line is a fixed `echo` string. The test uses the target name `my proj's $(dir)`. Pasting the printed lines cannot run anything taken from a name in a path (SEC-009 holds).
5. **The warning.** It prints the repo-relative path and the already validated `--project-id`, both through `repr()`, which escapes control and ANSI characters. It prints no entry body and no secret (tested with a body marker in `ProjectIdFormTests`). "Warn and keep indexed" is acceptable: a derived id is always lower case, so a mixed-case entry can never match any requesting context; it fails closed. The wider case, an entry naming a different `project_id`, gets no warning: a diagnosability gap, not an exposure (SEC-T791-02).
6. **Generator.** `validateArgPlaceholders` runs inside `readServersYaml` (`sync.mjs:182`); `validatePlatformDirs` runs over every manifest, also under `--platform`, before the write loop (`:1286-1292`, `:1317`). Unknown, embedded or misspelled placeholders and an `outputDir` that is not a single dot-folder are refused, and the tests check that nothing is written. Only `args` is checked for `{{`/`}}`; in `command`, `env` or `url` such text would pass literally. That is authoring input and not exploitable; noted, no finding.
7. **Tests** (read, not run). Each fix has a negative test that would fail if its control were removed: for QA-T760-01 the ordered new line, no `.venv-mcp` created, no line without the file or runtime; for QA-T760-02 six refused ids with a non-zero exit and no output directory, the library refusal, and the warning naming the path without content; for QA-T760-03 each config passing its own folder, a folder without a manifest still raising `PlatformResolutionError` from `resolve_platform` and `derive_requesting_context`, and the generator refusing bad placeholders and `outputDir` values without writing. Observation only: no single test runs `main()` through `build_index` to the warning; the warning is tested on a hand-built `BuildResult` because a full build needs the embedder.
8. **Other.** No doc that ships to targets still states the old `.claude` limit; the search found it only in historical records (the v10.0.0 release doc, QA and task artifacts, register v12). No top-level platform folder or `tests/golden/` file is in the diff.

## Findings

### SEC-T791-01: Platform identity change must be in the v11.0.0 migration notes
- **Severity:** SECURITY:LOW
- **Category:** OWASP A01 (Broken Access Control), documentation of a change in what a session may read
- **Evidence:** `implementation/.cline/mcp.json:86` and `implementation/.opencode/opencode.json:99` now pass their own folders. Before, both resolved as `claude-code` whenever `.claude/` existed.
- **Description:** On installs with `.claude/` next to other platform folders, Cline and Opencode sessions now resolve as `cline` and `opencode`. Shared-scope entries that name only `claude-code` in `shared_consumers.platforms` are no longer returned to them; entries that name `cline` or `opencode` now are.
- **Remediation:** A migration item in the v11.0.0 release notes: the platform is now taken from each client's own folder; shared entries meant for every client need to list each platform or use `["*"]`; the root of a self-install changes only after its refresh.
- **Owner:** release-manager
- **Deadline:** in the v11.0.0 release document, before the tag

### SEC-T791-02: Project-scope entries naming another project are dropped from results without a message
- **Severity:** SECURITY:LOW
- **Category:** OWASP A09 (Logging & Monitoring), diagnosability; fails closed
- **Evidence:** `build.py:110-119` warns only when the ids are equal after case-folding. `_is_includable` (`build.py:194-199`) admits every project-scope entry of the own repo whatever its `project_id`, and `scope_filter.py:52` never returns one that does not match.
- **Description:** An entry in the own repo whose `project_id` differs from the derived id in some other way (a typo, `org/repo.git`, the top group of a nested path) is indexed and never returned, with no message. Nothing is exposed; the risk is an invisible failure of the same kind as the original QA-T760-02.
- **Remediation:** Warn by path for every project-scope entry whose `project_id` is not equal to `config.project_id`, keeping the case-only wording as a more specific message.
- **Owner:** backend-developer, through the orchestrator
- **Deadline:** tracked debt (next register); next sprint

### SEC-T791-03: `is_derived_project_id` accepts dot segments and is not total over its inputs
- **Severity:** SECURITY:LOW
- **Category:** OWASP A03 (input validation hygiene)
- **Evidence:** `context_retriever.py:134-144`. `a/..` and `a/.` pass (the slug `a-..` matches `_INDEX_SLUG_RE`). A non-string raises `AttributeError` at `:139`.
- **Description:** This reaches no path: the slug is a single directory name, and `build.py` takes `--output-dir` separately. The server would derive such an id from a matching remote, so accepting it is consistent. The remaining issue is that a public predicate raises on non-string input instead of returning False.
- **Remediation:** Return False for non-strings at the top of the function. Optionally refuse `.` and `..` as segments, here and in `normalize_remote_to_project_id`, so the two stay equal.
- **Owner:** backend-developer, through the orchestrator
- **Deadline:** tracked debt; next sprint

## Conditions
None. SEC-T791-01 to -03 are LOW and go into register v14 as tracked debt; SEC-T791-01's deadline is the v11.0.0 release document.

## Method and limits
- **Read:** the full diff; in the worktree `build.py` from line 95 to the end, `context_retriever.py` and `scope_filter.py` in full, `context_retriever_mcp_server/server.py` lines 40-141, `sync.mjs` lines 150-299, 728-827 and 1225-1333, `install.sh` lines 1706-1801, `implementation/runtime/memory/requirements.txt`; from the main checkout through `grep_content` (pre-change state) the platform manifests' `outputDir` values and the docs and sources that mention `platform-root`; the plan and QA artifact sections named in the brief.
- **Could not read:** one search for pins in `requirements*.txt` returned too much output. Not needed: the diff changes neither requirements file.
- **(unverified):** that the suite and the MR pipeline pass; which working directory Cline and Opencode use for stdio servers; QA's reproductions against the new tip (T792's job).
- No command was run. `tests/golden/held-out/`, `.env*`, credential files, `.claude/settings*.json` and `.vscode/*.json` were not opened. No secret is printed.

## OWASP coverage
| Category | Reviewed | Findings |
|---|---|---|
| A01 Broken Access Control | Yes | 1 (SEC-T791-01) |
| A02 Cryptographic Failures | Yes (not touched) | 0 |
| A03 Injection | Yes | 1 (SEC-T791-03) |
| A04 Insecure Design | Yes | 0 |
| A05 Security Misconfiguration | Yes | 0 |
| A06 Vulnerable Components | Yes (no dependency changed) | 0 |
| A07 Auth Failures | Yes (not touched) | 0 |
| A08 Data Integrity Failures | Yes (generator validates before writing) | 0 |
| A09 Logging & Monitoring | Yes | 1 (SEC-T791-02) |
| A10 SSRF | Yes (not touched) | 0 |

## Gate Verdict
**Gate:** security
**Verdict:** PASS

| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 3 | 0 | 3 (tracked as debt) |
