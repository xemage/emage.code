# Pattern A — CWSO Concurrent Workspace Orchestration

Pattern A is the multi-agent code-editing protocol built on CWSO shadow workspaces.
N agents each receive an isolated in-memory workspace ("shadow workspace") branched from a shared
base commit. Each agent writes, commits, and optionally queries AST symbols in its own workspace.
Once all agents are done, an orchestrator-role client runs a pairwise AST pre-check (to detect
semantic conflicts before attempting the merge) and then calls `merge_concurrent_results` to
produce a single integrated commit. If the pre-check reports LOW severity and no conflicting
edits, the merge is safe to proceed automatically.

This code lives in:
- `implementation/runtime/cwso/client.py` — high-level `CwsoClient` (JWT minting, all 11 tools)
- `implementation/runtime/cwso/mcp_client.py` — low-level MCP transport (HTTP + JSON-RPC)
- `implementation/runtime/cwso/ast_conflict_check.py` — `AstConflictChecker` (severity scoring)
- `implementation/runtime/cwso/concurrent_merge.py` — `ConcurrentMergeOrchestrator`

Canonical evidence: [`docs/tasks/task-T214.md`](../../../docs/tasks/task-T214.md),
[`docs/tasks/task-T315.md`](../../../docs/tasks/task-T315.md)

---

## ⚠️ Role-split requirement (BUG-A — most important fact for new readers)

The CWSO live server enforces **role-based tool permissions**. A single `CwsoClient` instance
**cannot** run the full Pattern A flow. The permission split is:

| Role | Allowed tools | Blocked tools |
|------|--------------|---------------|
| `worker` | `create_shadow_workspace`, `write_shadow_file`, `commit_shadow`, `query_ast`, `drop_shadow_workspace` | `merge_concurrent_results` |
| `orchestrator` | `create_shadow_workspace`, `merge_concurrent_results`, `drop_shadow_workspace` | `write_shadow_file`, `commit_shadow` |

**Rule:** use a `worker` client for workspace setup (create/write/commit/query_ast/drop) and a
separate `orchestrator` client for the final merge call. Both clients can be built from the same
`CWSO_JWT_SECRET`:

```python
from runtime.cwso.client import CwsoClient

# Both built from the same shared secret, different roles.
worker = CwsoClient(jwt_secret=secret, role="worker", base_url="http://127.0.0.1:8080")
orch   = CwsoClient(jwt_secret=secret, role="orchestrator", base_url="http://127.0.0.1:8080")
```

This split was confirmed empirically during T214 and is not documented anywhere in the CWSO
server itself. Ignoring it produces an HTTP 403 at the tool-call level. The role-split is the
single most important, non-obvious fact a new reader needs to understand about Pattern A.

---

## Minimal worked example — Scenario 1 (three agents, independent edits, clean merge)

This is a direct simplification of
`tests/functional/test_pattern_a_integration_live.py` Scenario 1 — the LOW-severity, clean-merge
case that passed end-to-end in T214/T314/T315.

```python
import os
from runtime.cwso.client import CwsoClient, MergeInput, MergeLanguage, MergeHeuristic
from runtime.cwso.ast_conflict_check import AstConflictChecker

# --- Setup (two role-scoped clients from one secret) ---
secret   = os.environ["CWSO_JWT_SECRET"]          # never print or log this
base_url = os.environ.get("CWSO_BASE_URL", "http://127.0.0.1:8080")

worker = CwsoClient(jwt_secret=secret, role="worker",       base_url=base_url)
orch   = CwsoClient(jwt_secret=secret, role="orchestrator", base_url=base_url)
checker = AstConflictChecker(worker)

path     = "ops.py"
baseline = "def foo(): pass\ndef bar(): pass\n"

# --- Each agent creates its own shadow workspace ---
ws_base = worker.create_shadow_workspace()
# Returns: {"workspace_uuid": "<uuid>", "base_tree_oid": "<sha>"}
ws_a    = worker.create_shadow_workspace()
ws_b    = worker.create_shadow_workspace()
ws_c    = worker.create_shadow_workspace()

uuid_base = ws_base["workspace_uuid"]
uuid_a    = ws_a["workspace_uuid"]
uuid_b    = ws_b["workspace_uuid"]
uuid_c    = ws_c["workspace_uuid"]

# --- Write baseline into base workspace ---
worker.write_shadow_file(uuid_base, path, baseline)
worker.commit_shadow(uuid_base, "baseline: foo+bar")

# --- Agent A: modify foo ---
worker.write_shadow_file(uuid_a, path, "def foo(): return 1\ndef bar(): pass\n")
worker.commit_shadow(uuid_a, "agent A: modify foo")

# --- Agent B: add baz ---
worker.write_shadow_file(uuid_b, path, "def foo(): pass\ndef bar(): pass\ndef baz(): return 2\n")
worker.commit_shadow(uuid_b, "agent B: add baz")

# --- Agent C: add qux ---
worker.write_shadow_file(uuid_c, path, "def foo(): pass\ndef bar(): pass\ndef qux(): return 3\n")
worker.commit_shadow(uuid_c, "agent C: add qux")

# --- AST pre-check (orchestrator phase) ---
# AstConflictChecker uses the worker role internally for query_ast calls.
result_ab = checker.run([path], uuid_base, uuid_a, uuid_b)
# result.overall_severity:  ConflictSeverity.LOW
# result.safe_to_merge:      True
# result.file_heuristics[path]: MergeHeuristic.AST_SEMANTIC_ONLY

result_ac = checker.run([path], uuid_base, uuid_a, uuid_c)
result_bc = checker.run([path], uuid_base, uuid_b, uuid_c)

# --- Two-step merge (merge_concurrent_results is strictly 2-way: base/ours/theirs) ---
mi_step1 = MergeInput(
    path=path, language=MergeLanguage.PYTHON,
    base_content=baseline,
    ours_content="def foo(): return 1\ndef bar(): pass\n",
    theirs_content="def foo(): pass\ndef bar(): pass\ndef baz(): return 2\n",
)
resp1 = orch.merge_concurrent_results(
    source_workspace_uuids=[uuid_a, uuid_b],
    merge_inputs=[mi_step1],
    auto_resolve_heuristic=MergeHeuristic.AST_SEMANTIC_ONLY,
    target_branch_ref="refs/heads/pattern-a-result",
)
# resp1 contains merged content; use its merged result as the new "ours" for step 2.

# --- Cleanup --- always drop workspaces in a finally block ---
for uuid in [uuid_base, uuid_a, uuid_b, uuid_c]:
    worker.drop_shadow_workspace(uuid)
```

**Note on `write_shadow_file` response shape (BUG-E, found in T214):** the live server returns a
plain-text `"wrote N bytes (blob <oid>)"` message rather than `{"blob_oid": ...}` JSON. If you
need the blob OID, parse it from `response["content"][0]["text"]`. `commit_shadow` and
`create_shadow_workspace` return proper JSON dicts (`commit_oid`/`tree_oid` and
`workspace_uuid`/`base_tree_oid` respectively) — the post-T314 `mcp_client.py` correctly unwraps
the MCP `content[0].text` envelope before JSON-parsing.

---

## How to obtain a JWT for local testing

Use `CwsoClient.from_env()`, which reads three environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CWSO_JWT_SECRET` | (required) | HS256 signing secret |
| `CWSO_BASE_URL` | `http://127.0.0.1:8080` | Orchestrator base URL |
| `CWSO_ROLE` | `orchestrator` | JWT role |

To generate a random secret for local testing:

```python
# From implementation/scripts/test-jwt-registration.py
import secrets
jwt_secret = secrets.token_hex(32)   # 256-bit random secret
```

Or use `generate_jwt_token()` from `implementation/scripts/test-jwt-registration.py` directly
to mint a token for manual curl testing. Never read `.env`, `.env.*`, or any credential file
directly from agent code — always pass the secret as an environment variable and use
`CwsoClient.from_env()`. The live tests are gated behind `CWSO_LIVE_CONTRACT_TEST=1` for exactly
this reason: see `tests/functional/test_pattern_a_integration_live.py` for the reference pattern.

---

## Live verification status

This README was authored 2026-08-03 (plan-017, task T319). At that time, no live CWSO stack was
running (`docker ps --filter "name=cwso-"` returned empty). The worked example above is based
directly on `tests/functional/test_pattern_a_integration_live.py` Scenario 1, which was
successfully exercised against the live stack during T214/T314/T315 (see those task files for
literal stdout evidence). If you need to re-verify, bring up the stack with:

```bash
docker compose -f deploy/docker-compose-t226.yml up -d
export CWSO_LIVE_CONTRACT_TEST=1
export CWSO_JWT_SECRET=<your-secret>
python3 tests/functional/test_pattern_a_integration_live.py -v
```
