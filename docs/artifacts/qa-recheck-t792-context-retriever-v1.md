# QA re-check — T792: context-retriever reproductions (plan-151)

## Metadata
| Field | Value |
|---|---|
| Task | T792 (plan-151, batch Z) |
| Role | QA Engineer |
| Date | 2026-11-12 |
| Based on: | `docs/plans/plan-151-context-retriever-code-residue.md`, `docs/artifacts/qa-release-v10-v1.md` (QA-T760-01, -02, -03), commit `cf7366b7` |
| Code under test | worktree `agent-backend-developer-T790`, HEAD `a4552400`. `git diff --stat cf7366b7 a4552400` shows only 4 ledger/brief files. The installed `build.py`, `scope_filter.py` and `context_retriever.py` match `cf7366b7` byte for byte (sha256). |
| Gate | integration |

Committed by the orchestrator from the QA Engineer's report; the text is the report's, with the scratch-directory paths shortened.

## Summary
All three findings are **fixed**. Every negative check confirms that the fix is what makes the difference. One Low observation was found (QA-T792-1).

## Results per finding

| ID | Status | Command(s) | Exit code(s) | Observed output (exact) |
|---|---|---|---|---|
| QA-T760-01 | **fixed** | `bash scripts/install.sh --target <T> --platform cline` (target: empty git repo, `origin` = `https://gitlab.com/acme/widget.git`, no fetch). Then the printed lines, in the printed order, from `<T>`: (1) `python3 -m venv .venv-mcp && source .venv-mcp/bin/activate && pip install -r implementation/runtime/memory/requirements-mcp-server.txt`, (2) the same for `implementation/runtime/security/requirements-mcp-server.txt`, (3) `python3 -m venv .venv-mcp && source .venv-mcp/bin/activate && pip install -r implementation/runtime/memory/requirements.txt`, (4) `python3 -m implementation.runtime.memory.build --project-id acme/widget --own-repo-root . --general-repo-root . --output-dir implementation/runtime/memory/_index/acme-widget` | install 0; lines 1-3: 0, 0, 0; build 0 | Install stderr empty. The index note now prints line (3) before the build command. Build: `wrote 0 chunks, 0 rejections to implementation/runtime/memory/_index/acme-widget` (no vault yet). `_index/acme-widget/` holds `index.jsonl`, `manifest.json`, `rejections.jsonl`. |
| QA-T760-02 | **fixed** | In the same target, one entry `implementation/knowledge/memory/project/t792-lower.md` (`scope: project`, `project_id: acme/widget`, body token `QA-T792-CANARY-LOWER-7731`). (a) build with `--project-id Acme/Widget --output-dir …/_index/Acme-Widget`; (b) build with `--project-id Acme/Widget --output-dir …/_index/acme-widget`; (c) build with `--project-id acme/widget`; (d) a real stdio MCP client starting the server with the generated `.cline/mcp.json` args: `initialize`, `tools/list`, `retrieve("widget calibration procedure", top_k=5)` | (a) 2, (b) 2, (c) 0, (d) client 0 | (a) and (b): stdout 0 bytes; stderr `build.py: error: argument --project-id: project id must be the lower-case <org>/<repo> id that the server derives from the git remote 'origin' (for example em-age/emage.code); got 'Acme/Widget'`. No `_index/Acme-Widget` was created; the existing `_index/acme-widget/*` were unchanged (`sha256sum -c`: all 3 `OK`). (c) `wrote 1 chunks, 0 rejections …`. (d) `serverInfo.name = context-retriever`, `protocolVersion = 2025-11-25`, `tools/list: ['retrieve']`, `retrieve: isError = False`, chunk `implementation/knowledge/memory/project/t792-lower.md::chunk0::…` returned, canary present: `True` |
| QA-T760-02, case-differing entry | **fixed** (warned; still not returned) | Added `t792-mixed.md` (`project_id: Acme/Widget`, body token `QA-T792-CANARY-MIXED-9042`). Build with `--project-id acme/widget`, then stdio `retrieve("gasket torque specification QA-T792-CANARY-MIXED-9042")` | build 0; client 0 | `wrote 2 chunks, 0 rejections …`. stderr: `warning: 'implementation/knowledge/memory/project/t792-mixed.md': its project_id differs from --project-id 'acme/widget' only by letter case; retrieve will not return this entry`. That stderr has 0 matches for the body token, body words (`gasket`, `torque`) or the title. The index holds `"project_id": "acme/widget"` and `"project_id": "Acme/Widget"`. retrieve: `isError = False`; mixed canary `False`; `t792-mixed.md` `False`; lower canary `True`. |
| QA-T760-03 | **fixed** | Cline-only target from step 1: `test -e .claude` reports no `.claude/`. The generated `.cline/mcp.json` `context-retriever` args are `["-m", "implementation.runtime.memory.context_retriever_mcp_server", "--workspace-root", ".", "--platform-root", ".cline"]` (command `python3`). The server was started with exactly those args from the target root over stdio. | client 0 | `retrieve: isError = False`, chunk returned (see row QA-T760-02 (d)) |
| QA-T760-03, Opencode | **fixed** | Second target (same remote), `install.sh --platform opencode` (exit 0, stderr empty; no `.claude/`). Generated `.opencode/opencode.json` entry: `'command': ['python3', '-m', 'implementation.runtime.memory.context_retriever_mcp_server', '--workspace-root', '.', '--platform-root', '.opencode']`. Same entry copied in, build with `acme/widget`, stdio client with those args | install 0, build 0, client 0 | `wrote 1 chunks, 0 rejections …`; `tools/list: ['retrieve']`; `retrieve: isError = False`; canary `True` |

## Negative checks
| Check | Result | Observed |
|---|---|---|
| QA-T760-01: only the two `requirements-mcp-server.txt` lines installed, then the build | **still fails as before** (exit 1); the new line is what fixes it | `ModuleNotFoundError: No module named 'yaml'` (from `validate.py`, line 14, `import yaml`). No `_index/` directory was created. After line (3) the same build exits 0. |
| QA-T760-03: `--platform-root .claude` on the Cline-only target | **fails closed** | `initialize` and `tools/list` succeed; `retrieve: isError = True`, text `Error executing tool retrieve`, canary `False`. Server stderr: `PlatformResolutionError: could not read platform build manifest at .claude/.generated-manifest.json — platform identity must come from sync.mjs's own build output, never a caller-supplied string` |
| QA-T760-02: form check of `project_id_problem` (from `build.py`, scratch venv) | fails closed as documented | Accepted: `acme/widget`, `a_b/c.d-e`. Refused: `Acme/widget`, `acme/Widget`, `' acme/widget'`, `acme/widget/`, `acme`, `group/sub/repo`, `acme/widget.git`, `''` |

Source configs at the tip: `--platform-root` is `.cline` in `implementation/.cline/mcp.json`, `.opencode` in `implementation/.opencode/opencode.json`, and `.claude` in `implementation/.mcp.json` (correct for Claude Code).

## Observations
- **QA-T792-1 (Low): the dependency notes print duplicate venv-creation prefixes.** On a Cline or Opencode install the notes print three lines, each starting with `python3 -m venv .venv-mcp && source .venv-mcp/bin/activate && …`. Run in order they work: each `venv` call on an existing `.venv-mcp` exited 0 and kept the installed packages. But each line is a separate shell, so `source` does not carry over to the printed build command. A reader who pastes the lines one by one into a single interactive shell is fine. A reader who runs them as separate commands (for example `bash -c` per line) must activate `.venv-mcp` again before the build; the note never says so, and the build command has no `source` prefix. Without that, the build would use the system `python3` (**unverified** what happens then; likely the `yaml` error again). Suggestion for the debt register: print a single venv line, or prefix the build command with `source .venv-mcp/bin/activate &&`. Owner `backend-developer` through the orchestrator.
- Observation, no finding: the Cline and Opencode installs print the same dependency and index notes (diff empty after path normalisation).
- Observation, no finding: the stderr warning for a case-differing entry names the target-relative path in a Python `repr` (single quotes). That fits "path only".

## Method and limits
- Python 3.12.3 (system `python3`). Scratch venv `.venv-mcp` inside the scratch target: `mcp==2.2.0`, `httpx2` 2.16.0, `fastembed==0.8.0`, `pyyaml` 6.0.3 (pulled in transitively, by `huggingface_hub`), tree-sitter 0.26.0 and grammars, `onnxruntime` 1.31.1. All pip commands exited 0.
- Scratch directory: a `mktemp -d` under the session scratchpad. Both targets, the venv and the client script were there, and it was deleted at the end. The worktree was not modified (`git status --short` empty, HEAD `a4552400`). The main checkout was not touched.
- MCP client: a Python script using `mcp.client.stdio.stdio_client` and `ClientSession`. It reads `command` and `args` from the generated config, and for the negative only replaces the `--platform-root` value. The first run failed in the script only (SDK 2.2.0 uses `server_info` / `protocol_version`); fixed in the script, no server change.
- The embedding model came from the existing user cache `~/.cache/emage-memory-embeddings`. No download was observed. A first run with a model download was **not exercised (unverified)**. The model in the returned chunks is `nomic-ai/nomic-embed-text-v1.5`, `embedding_dim` 768. `onnxruntime` printed `pthread_setaffinity_np` lines on stderr, as in T760; harmless.
- **Not run (unverified):** `--platform claude-code`, `github` and `all` installs; `--update` and `--projections-only` paths; a nested-group remote end to end (only the form check above); `--shared-source-root`; the server's behaviour against an index built under a mixed-case id from before T790; the full test suite (the orchestrator's job); any check of `docs/releases/*` wording. No docker, no browser, no GitLab call, nothing under `tests/golden/`.
- Blockers: none.

## VERDICT: PASS
**Justification:** QA-T760-01, -02 and -03 each reproduce as fixed against `cf7366b7`, and each negative check shows the old failure comes back without the fix. Both Cline and Opencode were exercised with real stdio calls. The only new item is QA-T792-1 (Low, a wording issue in the notes; it does not block), for the debt register.

## Gate Verdict
**Gate:** integration
**Verdict:** PASS
**Findings:** QA-T792-1 (Low, tracked as debt)
