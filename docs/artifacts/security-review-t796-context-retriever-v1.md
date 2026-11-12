# Security review — T796: context-retriever LOW residue (plan-153, batch O)

## Metadata
- **Date:** 2026-11-12
- **Reviewer:** security-engineer (read-only; no file modified, no command run)
- **Task:** T796, plan-153
- **Based on:** `docs/plans/plan-153-context-retriever-low-residue.md` (§ Task Decomposition item 2); `docs/tasks/task-T796.md`; `docs/artifacts/security-review-t791-context-retriever-v1.md` (SEC-T791-02, -03); `docs/artifacts/tracked-debt-register-v14.md` § 5 batch O (through the plan; the register itself was not reread). Code read in worktree `agent-backend-developer-T795` at `15e427ba` (branch `agent/backend-developer/T795`, base develop `34f8ea7f`). The user's instruction of 2026-11-12, verbatim: "O go".

Committed by the orchestrator from the Security Engineer's report; the text is the report's.

## Verdict
**FAIL**

The three batch-O ids are fixed, and none of the five points shows an access-control, path or injection problem. One finding blocks: SEC-T796-01. On its own it is SECURITY:LOW. It blocks because T795 changes `normalize_remote_to_project_id`, so that function is code under review for every control that protects it. That makes the § Logging control ("DO NOT log: passwords, tokens") a required control here, and the function leaves it out: its `RemoteResolutionError` messages, the new one at `context_retriever.py:109` included, repeat the remote URL with any `user:token@` it holds. Under § Security Gate Protocol item 2 that forces `fail` whatever the grade.

If the orchestrator or the user rules that an exception message is not "logging" under that guideline, item 2 does not apply. The verdict would then be PASS, with SEC-T796-01 tracked as LOW debt under the standing LOW rule. That ruling is not the reviewer's to make.

## Status of the reviewed ids

| ID | Status | Evidence |
|---|---|---|
| SEC-T791-02 (SECURITY:LOW, A09) | **fixed** | `build.py:125-135` `foreign_project_paths` collects every project-scope entry whose `project_id` differs from `--project-id` other than by letter case. With `case_mismatched_paths` (`:113-122`) it covers every inequality exactly once, because one compares casefold-equal and the other casefold-unequal. `_warn_project_id_mismatches` (`:282-294`) is called on both the write path (`:276`) and the check path (`:308`). It uses its own wording and keeps the case-only wording. Entries stay indexed (test `:414`) and stay invisible (test `:417-420`). |
| SEC-T791-03 (SECURITY:LOW, A03) | **fixed** | `context_retriever.py:144-145` returns False for a non-string. `:146-147` returns False for any `.` or `..` segment. `:108-109` refuses a `.`/`..` org or repo in `normalize_remote_to_project_id`, so the predicate and the normaliser agree again. Tests: `test_context_retriever.py:278-314`, including `..git`, which matches lazily as repo `.` plus `.git`. |
| QA-T792-1 (Low, QA scale) | **fixed** on review; the orchestrator's re-run (plan item 3) remains | `install.sh:1739` prefixes the build line with the fixed literal `source .venv-mcp/bin/activate &&`. Without the venv the line stops before any `python3`; see `test_install_robustness.py:538-553`. |

## Answers to the points in the brief

1. **`scope_filter.py` is untouched and still fails closed.** Not in the diff. `is_visible` still compares `project_id` exactly (`scope_filter.py:51-52`) and denies unknown scopes (`:55`). Empty `shared_consumers` still deny (`:69-70`), and `RequestingContext` still refuses empty fields (`:33-35`). T795 also rewrites no chunk: the new code only lists paths (`build.py:125-135`) and changes neither `_is_includable` (`:204-215`) nor `enrich`. Project-scope entries come only from the own repo, because `_is_includable` drops any entry whose scope is not the walked subtree's (`:210-211`). So the general and shared roots cannot show the same silent drop.

2. **The warning prints paths and the validated `--project-id` only.** `build.py:283-294` formats only `rel_path` and `project_id`. `rel_path` is the file's path relative to the repo (`:179`). `project_id` has already passed `_project_id_arg` (`:239`) or `BuildConfig.__post_init__` (`:74-79`), so it is limited to `[a-z0-9._-]` plus one `/`. No frontmatter field and no body text is printed. The test checks that neither the entry's `project_id` values nor the body marker appear (`test_memory_indexing_pipeline.py:427-430`).

   **`!r` on a terminal is safe.** `str.__repr__` escapes every character for which `str.isprintable()` is False: categories Cc, Cf, Cs, Co, Cn, Zl, Zp and Zs other than the space. That covers ESC (`\x1b`, so ANSI sequences), CR, LF, BEL, bidi overrides such as U+202E, U+2028/2029, and the lone surrogates that `surrogateescape` produces for file names that are not valid UTF-8. That last case also means `print` cannot raise `UnicodeEncodeError` on such a name. Printable homoglyphs pass through unchanged, which is a display question and not terminal injection.

3. **The dot-segment refusal cannot make the server resolve another project's index or a path outside `_index/`.** The change only adds a `raise` (`context_retriever.py:108-109`). It has no fallback, default or rewrite. On the default path `default_index_dir` calls `derive_project_id` before it builds any path (`:160`). The error propagates through `server.py:133` and the server does not start. Even before T795, a path step was never possible: `/` becomes `-` and the slug must match `^[a-z0-9][a-z0-9._-]{0,199}$` (`:136`, `:161`), so the result is always one directory name that cannot be `.` or `..` (`acme/..` used to give `acme-..`). The refusal narrows the accepted set and widens nothing.

   **The developer's notes:**
   - (1) With no `--index-dir`, the server refuses to start. This is the default path, since the shipped entry passes no `--index-dir` (README `:77-79`). It fails closed.
   - (2) With `--index-dir`, every `retrieve` raises `RemoteResolutionError` inside `derive_requesting_context` (`:190`). That happens before any `RequestingContext` exists (`:192`) and before `Retriever.search` runs (`:218-219`), so nothing can be returned. This is acceptable fail-closed behaviour, the same as for any remote that cannot be resolved today.

   Unchanged: different nested remotes with the same last two segments map to one id (`group-a/sub/repo` and `group-b/sub/repo` both give `sub/repo`; test `:291`). That is the scope model's rule (§ 3), not touched by T795, and not a new finding.

4. **The printed installer lines cannot run a name taken from a path.** `install.sh:1739-1741` are fixed `echo` literals. The `source .venv-mcp/bin/activate &&` prefix and the `<org>/<repo>` placeholders are constants. The only values taken from the environment are still printed through `%q`: `$TARGET` (`:1733`) and the constant requirements path (`:1735`). The test runs the printed line from a target named `my proj's $(dir)` and gets the fake venv's `python3`, with no command substitution (`test_install_robustness.py:520-536`). The negative test (`:538-553`) shows the line fails rather than falling back to the system `python3`. The installer still creates no `.venv-mcp` (`:511`, `:553`). SEC-009 holds.

5. **Final status:** SEC-T791-02 **fixed**, SEC-T791-03 **fixed** (table above). The new finding is below.

## Findings

### SEC-T796-01: `RemoteResolutionError` messages repeat credentials embedded in the git remote URL
- **Severity:** SECURITY:LOW on its own. Blocking under § Security Gate Protocol item 2 as a required control left out of code under review (§ Logging, "DO NOT log: passwords, tokens"); see the Verdict.
- **Category:** OWASP A09 (sensitive data in logs and error output)
- **Location:** `implementation/runtime/memory/context_retriever.py:109` (new in T795, `remote_url[:200]!r`). The same pattern exists in the unchanged lines `:102` and `:106` of the same function, which T795 alters.
- **Description:** `_REMOTE_RE` accepts a `user:secret@` part (`:82`). `derive_project_id` passes `git remote get-url origin` output on as it is (`:129`). A remote such as `https://oauth2:<PAT>@gitlab.com/acme/..` reaches `:109`, and the message carries the token. Truncating to 200 characters does not remove it. Two kinds of remote store a token this way: an HTTPS remote set up with a personal access token, and a GitLab CI checkout remote (`gitlab-ci-token:<job token>@…`).
- **Impact:**
  - On the default path the traceback goes to the server's stderr, which MCP clients usually log.
  - With `--index-dir` the message comes back from every `retrieve` call. Whether the `mcp` SDK passes `str(exc)` on to the client is **(unverified)**. If it does, the token reaches the agent session, which `security-guidelines.md` § Agent Safety Guards forbids from repeating it in chat, handoffs or checkpoints.
  - Exploitability is low. It needs a token in the remote URL and a URL shape that is refused: a dot segment, a single path segment, or an unrecognised shape.
- **Remediation:** Remove the userinfo part before the URL goes into any message, in all three messages. Simplest is to leave the URL out entirely.
  ```python
  # Before
  raise RemoteResolutionError(f"git remote URL has a '.' or '..' <org>/<repo> segment: {remote_url[:200]!r}")
  # After
  _USERINFO_RE = re.compile(r"^((?:[a-zA-Z][\w+.-]*://)?)[^@/]+@")

  def _redacted(url: str) -> str:
      return _USERINFO_RE.sub(r"\1***@", url)[:200]

  raise RemoteResolutionError(f"git remote URL has a '.' or '..' <org>/<repo> segment: {_redacted(remote_url)!r}")
  ```
  Apply the same change at `:102` and `:106`. Add a test where a `https://user:s3cret@host/acme/..` remote and a single-segment remote both raise, and `s3cret` does not appear in `str(exc)`.
- **Owner:** backend-developer, through the orchestrator (fix task in plan-153 before merge)
- **Deadline:** before T795 merges (blocking), unless the ruling in the Verdict applies; in that case, tracked LOW debt for register v15

## Conditions
None (FAIL). Blocker below.

## Blockers
- **SEC-T796-01:** a required logging control is missing in `normalize_remote_to_project_id`; severity SECURITY:LOW, blocking under item 2. Affected assets: `implementation/runtime/memory/context_retriever.py:102`, `:106` and `:109`. Escalation: orchestrator, which creates the fix task, or obtains a ruling from the user that § Logging does not cover exception messages. Retry attempt 1.

## Method and limits
- **Read:** in the worktree, `build.py` in full; `context_retriever.py:60-229`; `scope_filter.py` in full; `context_retriever_mcp_server/server.py:40-141`; `install.sh:1690-1747`; `README.md:50-79`; `test_context_retriever.py:270-324`; `test_memory_indexing_pipeline.py:370-447`; `test_install_robustness.py:505-553`. Also T791's review, plan-153 and the task brief.
- **Not read:** `implementation/PREREQUISITES.md` and `docs/wiki/mcp-servers.md`, so whether any wording needed correcting there is **(unverified)**. The full diff was not read as a file: `grep_content` refuses a root outside the main checkout. Whether a top-level folder or `tests/golden/` changed is **(unverified)** (the orchestrator's gate).
- **(unverified):** that the suite, the drift gates and the pipeline pass; how the `mcp` SDK shows a tool exception to the client; QA-T792-1's live re-run (plan item 3).
- `tests/golden/held-out/`, `.env*`, credential files, `.claude/settings*.json` and `.vscode/*.json` were not opened. No secret is printed.

## OWASP coverage
| Category | Reviewed | Findings |
|---|---|---|
| A01 Broken Access Control | Yes | 0 |
| A02 Cryptographic Failures | Yes (not touched) | 0 |
| A03 Injection | Yes | 0 |
| A04 Insecure Design | Yes | 0 |
| A05 Security Misconfiguration | Yes | 0 |
| A06 Vulnerable Components | Yes (no dependency changed) | 0 |
| A07 Auth Failures | Yes (not touched) | 0 |
| A08 Data Integrity Failures | Yes | 0 |
| A09 Logging & Monitoring | Yes | 1 (SEC-T796-01) |
| A10 SSRF | Yes (no network request added) | 0 |

## VERDICT: FAIL

### Findings Summary
| Severity | Count | Resolved | Remaining |
|---|---|---|---|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 |
| LOW | 1 (SEC-T796-01) | 0 | 1 (blocking under item 2) |

SEC-T791-02 and SEC-T791-03 are counted as resolved ids from earlier reviews, not as new findings.

### Justification
The batch-O fixes are correct and fail closed. FAIL comes only from SEC-T796-01, a required control missing from a function that T795 alters.

## Gate Verdict
**Gate:** security
**Verdict:** FAIL
