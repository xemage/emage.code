# Delegation Brief — T210: `CwsoClient` Library

## Objective
Implement a reusable CWSO MCP client library in Python that emage.code orchestrators can import to call the 11 CWSO tools with proper JWT auth, rate limiting, and error handling.

## Context
- **Plan**: docs/plans/plan-009-cwso-emagecode-sia-integration.md (§3.1 tool surface, §3.2 execution internals)
- **Evidence**: docs/artifacts/cwso-mcp-contract-v1.md (MCP tool snapshot, auth contract, rate limits)
- **Existing Code**: implementation/runtime/cwso/mcp_client.py (from T201) — basic HTTP client exists; needs enhancement
- **Task Dependencies**: T201 (done) — MCP contract snapshot is input
- **Next Task**: T212 (concurrent-merge orchestration) — will import this library

## Expected Outputs

**File**: `implementation/runtime/cwso/client.py` (evolve from `mcp_client.py`)

**Class API**:
```python
class CwsoClient:
    def __init__(self, jwt_secret: str, role: str, base_url: str = "http://127.0.0.1:8080", rate_limit_pacing_sec: float = 1.05):
        """Initialize with role (orchestrator|worker), JWT secret, and rate-limit pacing."""

    def tools_list(self) -> dict:
        """MCP tools/list → returns {result: {tools: [...]}}."""

    def call_tool(self, tool_name: str, **kwargs) -> dict:
        """Dispatch a single tool call with keyword args; returns {result: ...} or raises CwsoError."""

    def call_tool_batch(self, calls: list[{tool_name, kwargs}], max_concurrent: int = 3) -> list[dict]:
        """Dispatch multiple tool calls with concurrency control; respects rate limit."""
```

**Behaviors**:
1. **JWT generation**: Mint HS256 JWTs with claims `{role, iss:"cwso", aud:["cwso-mcp"], exp:+600}` from the provided secret.
2. **Rate limiting**: Enforce ≥1.05 sec between requests (60 req/min, burst 1); queue and pace if needed.
3. **Error handling**: Catch HTTP errors, MCP errors (code, message), and JWT failures; raise descriptive `CwsoError` subclasses.
4. **Tool dispatch**: Support all 11 tools (read_file_sync, write_file_sync, create_shadow_workspace, merge_concurrent_results, etc.) with argument validation.
5. **Retry logic** (optional): Exponential backoff on transient errors (5xx, timeout).

## Acceptance Criteria
- [ ] `CwsoClient.__init__` accepts JWT secret, role, base_url, pacing interval
- [ ] `tools_list()` returns 11 tools (verified against snapshot)
- [ ] `call_tool(name, **kwargs)` dispatches a single tool; returns result or raises `CwsoError`
- [ ] `call_tool_batch()` respects rate limiting (pacing enforced; no bursts > 1/1.05sec)
- [ ] JWT tokens are minted correctly (HS256, role-based, exp claim)
- [ ] Comprehensive docstrings and type hints
- [ ] Unit tests in `tests/unit/test_cwso_client.py` cover: JWT generation, rate limiting, error cases, tool dispatch
- [ ] Integration test in `tests/functional/test_cwso_client_live.py` (requires running CWSO server) exercises one real tool call

## Constraints
- Do not expose JWT secrets in logs or error messages
- Support Python 3.8+ (standard library only; use `requests` if needed)
- Rate limiting must be enforced per-instance (stateful)
- All HTTP calls must use HTTPS in production (tolerate insecure in dev via env flag)

## Blocker Protocol
If blocked, report type, severity, and mitigation.

## References
- CWSO MCP tool surface: docs/artifacts/cwso-mcp-contract-v1.md
- Tool details: plan-009 §3.1 (tool table)
- Auth contract: JWT role-gating (orchestrator=planning, worker=worker tier)
