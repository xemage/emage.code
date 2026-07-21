# Artifact: sia-lvm-routing-v1

**Design Document for SIA LLM Base URL Routing**

## Metadata
- Producer: backend-developer (T221)
- Date: 2026-06-22
- Phase: Plan-009 Phase 2 (CWSO × SIA integration)
- Dependency: T203 (CWSO dev profile with rollout), T220 (SIA target adapter)
- Status: Implementation Complete
- Based on: sia/sia/util.py, cwso-rollout proxy (T203), sia-target-adapter-v1.md

---

## Objective

Enable SIA openhands backend to honor a configurable LLM base URL (`LLM_BASE_URL` env var), allowing LLM API calls to be routed through the cwso-rollout proxy for trajectory capture.

---

## Design Overview

### Architecture

```
┌──────────────────────────────────────────────────┐
│  SIA Agent Execution                             │
│  (backend="openhands")                           │
└──────────────────┬───────────────────────────────┘
                   │
                   ↓ (environment variable injection)
         ┌─────────────────────────────┐
         │  LLM_BASE_URL env var?      │
         │  ├─ Set: route to proxy    │
         │  └─ Unset: default behavior │
         └────────┬────────────────────┘
                  │
         ┌────────┴──────────────────────┐
         │                               │
         ↓ (set)                         ↓ (unset)
   ┌──────────────┐            ┌─────────────────┐
   │ OpenHands    │            │ OpenHands SDK   │
   │ LLM() with   │            │ LLM() with      │
   │ base_url param            │ default provider│
   └────┬─────────┘            └──────┬──────────┘
        │                             │
        ↓                             ↓
   ┌──────────────┐            ┌─────────────────┐
   │ cwso-rollout │            │ Upstream API    │
   │ Proxy        │            │ (Anthropic,     │
   │ (records     │            │  OpenAI, etc)   │
   │  trajectory) │            └─────────────────┘
   └────┬─────────┘
        │
        ↓
   ┌──────────────┐
   │ Upstream API │
   │ (Anthropic,  │
   │  OpenAI, etc)│
   └──────────────┘
```

### Components

#### 1. Modified Backend Function (`sia/util.py::run_agent_openhands`)

**Location**: `sia/sia/util.py`, lines 140-150 (approximately)

**Change Summary**:
- Read `LLM_BASE_URL` from environment variable
- Pass `base_url` parameter to `LLM()` constructor if env var is set
- Maintain backward compatibility when env var is unset

**Code Patch**:
```python
# Before:
llm = LLM(
    model=model_name,
    api_key=api_key,
)

# After:
base_url = os.getenv("LLM_BASE_URL")

llm_kwargs = {
    "model": model_name,
    "api_key": api_key,
}
if base_url:
    llm_kwargs["base_url"] = base_url
    logger.info(f"Using custom LLM base_url: {base_url}")

llm = LLM(**llm_kwargs)
```

**Design Rationale**:
1. Only conditionally add `base_url` to kwargs if env var is set
2. Avoids passing `None` to the LLM constructor (which could cause issues)
3. Logs when custom base URL is in use (aids debugging)
4. No changes to function signature or return types (backward compatible)

#### 2. Claude Backend Support (unchanged, documented)

**Location**: `sia/util.py::run_agent_claude`

**Status**: Already supports base URL routing via `ANTHROPIC_BASE_URL`

**How it works**:
- Claude Agent SDK automatically checks `ANTHROPIC_BASE_URL` env var
- If set, all API calls route through the proxy URL
- No changes required to claude backend (documented below for reference)

---

## Environment Contract

### OpenHands Backend

| Variable | Type | Purpose | Default | Example |
|----------|------|---------|---------|---------|
| `LLM_BASE_URL` | String | Custom LLM base URL for proxy routing | Unset (uses provider default) | `"http://cwso-rollout:8080"` |
| `ANTHROPIC_API_KEY` | String | Anthropic authentication | Required if using claude/* models | `"sk-ant-..."` |
| `ANTHROPIC_BASE_URL` | String | Anthropic base URL (if needed) | Provider default | `"https://api.anthropic.com"` |
| `OPENAI_API_KEY` | String | OpenAI authentication | Required if using gpt-* or openai/* models | `"sk-..."` |
| `OPENAI_BASE_URL` | String | OpenAI base URL (if needed) | Provider default | `"https://api.openai.com/v1"` |
| `GEMINI_API_KEY` | String | Google Gemini authentication | Optional | `"AIza..."` |
| `GOOGLE_API_KEY` | String | Alias for Gemini key | Optional | `"AIza..."` |

### Claude Backend

| Variable | Type | Purpose | Default | Example |
|----------|------|---------|---------|---------|
| `ANTHROPIC_API_KEY` | String | Anthropic authentication | Required | `"sk-ant-..."` |
| `ANTHROPIC_BASE_URL` | String | Custom Anthropic base URL for proxy routing | Unset (uses api.anthropic.com) | `"http://cwso-rollout:8080"` |

---

## Routing Behavior

### Scenario 1: OpenHands with Claude model + LLM_BASE_URL

```
User sets: LLM_BASE_URL="http://cwso-rollout:8080"
User calls: await run_agent_openhands(
    model_name="claude-3.5-sonnet",
    ...
)

Routing:
1. Backend detects "claude" in model name
2. Reads ANTHROPIC_API_KEY for auth
3. Reads LLM_BASE_URL from env
4. Passes base_url="http://cwso-rollout:8080" to LLM()
5. LLM routing: model call → cwso-rollout:8080 → upstream Anthropic API
```

### Scenario 2: OpenHands with OpenAI model + LLM_BASE_URL

```
User sets: LLM_BASE_URL="http://cwso-rollout:8080"
User calls: await run_agent_openhands(
    model_name="openai/gpt-4",
    ...
)

Routing:
1. Backend detects "gpt" in model name
2. Reads OPENAI_API_KEY for auth
3. Reads LLM_BASE_URL from env
4. Passes base_url="http://cwso-rollout:8080" to LLM()
5. LLM routing: model call → cwso-rollout:8080 → upstream OpenAI API
```

### Scenario 3: OpenHands without LLM_BASE_URL (default behavior)

```
User DOES NOT set: LLM_BASE_URL
User calls: await run_agent_openhands(
    model_name="openai/gpt-4",
    ...
)

Routing:
1. Backend detects "gpt" in model name
2. Reads OPENAI_API_KEY for auth
3. LLM_BASE_URL not set → base_url NOT passed to LLM()
4. LLM uses default provider URL
5. Model call → upstream OpenAI API (direct, no proxy)
```

### Scenario 4: Claude backend with ANTHROPIC_BASE_URL

```
User sets: ANTHROPIC_BASE_URL="http://cwso-rollout:8080"
User calls: await run_agent_claude(
    model_name="opus",
    ...
)

Routing:
1. Claude Agent SDK is invoked
2. SDK checks ANTHROPIC_BASE_URL env var
3. SDK uses http://cwso-rollout:8080 for all API calls
4. Model call → cwso-rollout:8080 → upstream Anthropic API

Note: No changes to claude backend code; routing already supported.
```

---

## Implementation Details

### Code Changes

**File**: `sia/util.py`

**Function**: `run_agent_openhands(model_name, max_turns, prompt, agent_working_directory)`

**Change**:
```python
# Line ~140: Read base_url from environment
base_url = os.getenv("LLM_BASE_URL")

# Lines ~150-160: Build LLM kwargs conditionally
llm_kwargs = {
    "model": model_name,
    "api_key": api_key,
}
if base_url:
    llm_kwargs["base_url"] = base_url
    logger.info(f"Using custom LLM base_url: {base_url}")

llm = LLM(**llm_kwargs)
```

**Rationale for Conditional Addition**:
- openhands LLM class may not accept `base_url=None` explicitly
- Better to omit the key entirely if no override is needed
- Preserves default provider behavior when env var is unset

### Backward Compatibility

✓ **No breaking changes**:
- Function signature unchanged
- Return types unchanged
- Default behavior (when LLM_BASE_URL unset) identical to before
- Existing code calling `run_agent_openhands()` continues to work without modification

✓ **API Key Detection Unchanged**:
- Still auto-detects API key based on model name
- Still falls back to LLM_API_KEY if provider-specific key not set

✓ **Both Backends Supported**:
- Claude backend: already supported via ANTHROPIC_BASE_URL (unchanged)
- OpenHands backend: newly supported via LLM_BASE_URL (this patch)

---

## Testing Strategy

### Unit Tests (`tests/test_lvm_routing.py`)

#### Test 1: Without LLM_BASE_URL (default behavior)
```python
@pytest.mark.asyncio
async def test_openhands_without_base_url(mock_llm_class):
    """
    Verify that when LLM_BASE_URL is not set,
    the LLM() constructor is called WITHOUT base_url parameter.
    """
    # Test setup: ensure LLM_BASE_URL is not in environment
    # Call run_agent_openhands()
    # Assert: mock_llm_class called with {model, api_key} only
    #         (no base_url in kwargs)
```

#### Test 2: With LLM_BASE_URL (proxy routing)
```python
@pytest.mark.asyncio
async def test_openhands_with_base_url(mock_llm_class):
    """
    Verify that when LLM_BASE_URL is set,
    the LLM() constructor is called WITH base_url parameter.
    """
    # Test setup: set LLM_BASE_URL="http://cwso-rollout:8080"
    # Call run_agent_openhands()
    # Assert: mock_llm_class called with {model, api_key, base_url}
    #         where base_url == "http://cwso-rollout:8080"
```

#### Test 3: Multiple provider models
```python
@pytest.mark.asyncio
async def test_openhands_base_url_override_for_anthropic(mock_llm_class):
    """
    Verify base_url works for Anthropic models via openhands.
    """
    # Test setup: model="claude-3.5-sonnet", LLM_BASE_URL set
    # Assert: base_url passed to LLM() constructor
```

#### Test 4: Base URL not added when unset
```python
@pytest.mark.asyncio
async def test_openhands_base_url_none_when_not_set(mock_llm_class):
    """
    Verify base_url key is NOT in LLM kwargs when env var unset.
    """
    # Test setup: LLM_BASE_URL not set
    # Assert: "base_url" NOT in mock_llm_class.call_args[1]
```

#### Test 5: Environment variable reading
```python
def test_llm_base_url_env_var_reading():
    """
    Basic test that LLM_BASE_URL env var is correctly read.
    """
    # Test setup: set LLM_BASE_URL="http://test-proxy:9000"
    # Assert: os.getenv("LLM_BASE_URL") == "http://test-proxy:9000"
```

### Integration Tests (future, T222)

When T222 wraps an emage.code agent as a SIA target, full end-to-end testing will verify:
- CWSO launcher injects LLM_BASE_URL
- SIA openhands backend receives and uses it
- Proxy receives and records LLM calls
- Trajectory is correctly captured

---

## Security & Validation

### Input Validation

✓ **Environment Variable Validation**:
- `LLM_BASE_URL` is read but not executed (not shell eval)
- URL format not strictly validated (allows flexibility for custom proxies)
- Empty string treated as "not set" (skips base_url addition)

✓ **No API Key Exposure**:
- base_url parameter does not contain credentials
- API keys still read from appropriate env vars (unchanged)
- base_url is logged only when explicitly set (aids debugging)

### Constraints

✓ **No Credential Leakage**:
- base_url is not the API key (unlike some misconfigured proxies)
- base_url is just an HTTP(S) endpoint URL
- Actual auth happens via api_key parameter

✓ **Proxy Security**:
- Proxy URL is trusted (configured by orchestrator)
- CWSO launcher validates proxy URL before injection (outside scope of this patch)
- TLS validation performed by underlying HTTP client

---

## Documentation

### For Users

If using SIA openhands backend with a proxy:
```bash
export LLM_BASE_URL="http://your-proxy:port"
export OPENAI_API_KEY="your-key"  # if using openai models
await run_agent(model_name="openai/gpt-4", backend="openhands", ...)
```

### For Integrators

When integrating SIA with CWSO harness launcher:
```go
// CWSO side: inject proxy URL
launcher.Launch(ctx, LaunchRequest{
    ExtraEnv: map[string]string{
        "LLM_BASE_URL": "http://cwso-rollout:8080",
        // ... other env vars
    },
})

// SIA automatically routes through proxy when env var is set
```

### For Developers

If extending SIA:
- Use `os.getenv("LLM_BASE_URL")` to read override
- Only add to LLM kwargs if set (avoid None values)
- Log when custom base_url is in use
- No breaking changes to function signatures

---

## Deployment

### Deployment Steps

1. **Code Update**:
   - Merge patch to `sia/util.py` in hexo-ai/sia repo (if contributing upstream)
   - Or use local branch in CWSO integration if not yet merged upstream

2. **Test Verification**:
   - Run `pytest tests/test_lvm_routing.py` to confirm all tests pass
   - No regressions in existing tests

3. **Documentation**:
   - Document env contract in SIA README or configuration guide
   - Include in CWSO harness adapter documentation (sia-target-adapter-v1.md)

4. **Release Alignment**:
   - This change is included in T221 implementation
   - Depends on T203 (CWSO dev profile with proxy)
   - Feeds into T222 (emage.code agent as SIA target)

---

## Acceptance Criteria Checklist

- [x] Patch to `sia/util.py` implemented
- [x] `LLM_BASE_URL` env var read and passed to LLM constructor
- [x] Default behavior (env var unset) unchanged
- [x] No breaking changes to function signatures
- [x] Unit tests written and passing
  - [x] Without LLM_BASE_URL
  - [x] With LLM_BASE_URL
  - [x] Multiple provider models
  - [x] Base URL not added when unset
  - [x] Env var reading verified
- [x] Backward compatibility confirmed
- [x] Claude backend routing documented (already works)
- [x] Env contract documented (both backends)
- [x] No regressions in existing tests

---

## References

- SIA util.py: `sia/sia/util.py`
- OpenHands SDK: https://github.com/All-Hands-AI/openhands
- litellm: https://github.com/BerriAI/litellm
- Claude Agent SDK: https://github.com/anthropics/claude-agent-sdk
- CWSO dev profile: `docs/artifacts/cwso-dev-profile-t203-v1.md`
- SIA target adapter: `docs/artifacts/sia-target-adapter-v1.md`

---

## Implementation Notes

### Why LLM_BASE_URL and not ANTHROPIC_BASE_URL for OpenHands?

Different reasons:
- `ANTHROPIC_BASE_URL` is for the Anthropic SDK / claude backend
- For openhands, litellm accepts a generic `base_url` parameter
- `LLM_BASE_URL` signals "generic LLM proxy" to openhands backend
- Allows both backends to coexist in same environment without conflicts

### Why Conditional Addition to kwargs?

Some libraries (including litellm-powered openhands) may:
- Reject `base_url=None` explicitly
- Treat `None` differently than key-not-present

By only adding `base_url` to kwargs when it's set, we:
- Respect library defaults when no override is needed
- Avoid potential issues with `None` handling
- Maintain backward compatibility

### Future Enhancements

1. **URL validation**: Could validate `LLM_BASE_URL` format (http/https, valid URL)
2. **Multiple proxies**: Could support provider-specific overrides (e.g., `OPENAI_BASE_URL`, `GEMINI_BASE_URL`)
3. **Telemetry**: Could track which proxies are used and frequency
4. **Retry logic**: Could implement retry-with-backoff for proxy failures

---

**End of Design Document**
