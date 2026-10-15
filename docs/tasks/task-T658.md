# T658 — Server-level denial of the unsafe Playwright tools on Opencode and Gemini CLI (SEC-T657-01)

**ID:** T658
**Owner:** devops-engineer
**Status:** done
**Priority:** P0
**Tier:** judgment
**Depends on:** T657
**Affects:** —
**Created:** 2026-10-15
**Completed:** 2026-10-15
**Based on:**
- `docs/plans/plan-122-release-v8-wave-3.md` (Addendum 5: T658, T659)
- `docs/artifacts/security-review-t657-tool-name-mapping-v1.md` (SEC-T657-01, SEC-T657-04, -07, -09), `docs/artifacts/mcp-tool-name-mapping-v1.md`, `docs/artifacts/fetch-replacement-evaluation-v1.md`
- The user's decision of 2026-10-15 (AskUserQuestion, verbatim option label): "Implement Opencode deny + Gemini excludeTools first"

## 1. What and why

Opencode, Gemini CLI and Cursor do not restrict MCP tools by an agent's tool list, so the narrowed Playwright grants are not enforced there. Where the platform documents a server-level denial, make the generator emit it. (a) **Establish the mechanism from current documentation and the vendor source** (`npx ctx7@latest library/docs`, max 3 ctx7 commands per question; the vendors' pages; the vendor repositories at a commit): Opencode: how a deny for an MCP tool name (`playwright_browser_run_code_unsafe`, form `<server>_<tool>`) is written (top-level `permission` in `opencode.json`, or per-agent `permission`/`tools: false`), whether explicit deny overrides an agent-level allow, and which file the generator emits (the MCP config `opencode.json` that `install.sh` merges with `merge-mcp-json.py`, or the agent files); Gemini CLI: `excludeTools` on the `mcpServers.playwright` entry of `settings.json` (names as the server reports them, e.g. `browser_run_code_unsafe`), its precedence over `includeTools`, and that it applies to subagents. Record each as verified (source) or unverified in the new artifact `docs/artifacts/mcp-server-denials-v1.md` (Based on: security-review-t657-tool-name-mapping-v1.md); an unverified mechanism is not shipped. (b) **Generator**: emit the denial of exactly six Playwright tools (`browser_run_code_unsafe`, `browser_evaluate`, `browser_file_upload`, `browser_drag`, `browser_drop`, `browser_network_request`) for Opencode and Gemini CLI, driven from one list in the generator or `servers.yaml` (a per-server `denyTools`-style key; keep the source of truth single), not hand-edited in projections. (c) **Install merge**: `scripts/merge-mcp-json.py` and `scripts/install.sh` must keep the generated denial and not clobber a user's own `permission`/`excludeTools` entries (merge, do not replace); add tests with and without the provenance sidecar. (d) **Tests**: generator output per platform (literal examples from the vendor docs); the grant-set test extended so that the denial list is pinned and equals the six excluded tools; a negative test that a user-owned `playwright-local` entry is NOT denied by these names (it is a different server name) and that docs say so. (e) Fold in the cheap SEC-T657 follow-ups that touch the same code: SEC-T657-09 (validate `mcpToolNames` once at manifest load, throw on a non-terminal `*`), SEC-T657-07 (anchor `ArtifactTests.test_artifact_never_recommends_the_unsafe_tool` on the explicit "never/excluded/not" wording and give `test_no_projection_names_the_unsafe_tool` a file-count floor). (f) Regenerate (`node implementation/scripts/sync.mjs --root implementation`, `python3 implementation/scripts/generate-registry.py --root implementation`), declare the root drift in `tests/_baselines/root-install-drift.json` (sorted `python3 -m tests.functional.test_root_install_parity --print-drift` paths, one comment line starting `Declared 2026-10-15 by T658 (`); do NOT refresh the root install (T659 does). (g) Update the wiki, both `AGENTS.md` files and PREREQUISITES: the narrowing is now backed by a server-level denial on Opencode and Gemini CLI (state exactly which tools, that it is documented but not observed live, and that Cursor stays open).

## 2. Output

The artifact, the generator and merge changes, the tests, the doc updates, one local commit, and a report with the per-platform table and every changed generated file.

## 3. Constraints

- Work in your own worktree/branch; one Conventional Commit ending with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Do not push; do not merge; never create, push or delete a tag or release; never use or print `WIKI_TOKEN`; do not edit `docs/tasks/active-tasks.md`, `completed-tasks.md` or any brief's Status line.
- Gates: sync --check, generate-registry --check, check-maturity.py --root implementation, scorecard.py --check, validate-tasks.py, check_evaluator_hash, held-out isolation test, and the full suite `python3 tests/run.py > file` (summary lines).
- Never open `tests/golden/held-out/`; never write a held-out case id anywhere. No `.env*` or credential files; do not read the user's local `.claude/settings*.json` or `.vscode/mcp.json`. Mark anything you did not verify **(unverified)**.

## 4. Acceptance criteria

1. The artifact lists both platforms with verified/unverified status and sources; nothing unverified is shipped.
2. The denial of exactly the six tools is generated for Opencode and Gemini CLI, survives the install merge and does not overwrite user entries.
3. All gates and the suite pass.

## 5. Blocker protocol

Report each blocker with its type (`technical` | `dependency` | `unclear_requirements` | `external`) and severity (`critical` | `major` | `minor`).
