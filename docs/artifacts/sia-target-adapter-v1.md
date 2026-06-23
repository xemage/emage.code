# Artifact: sia-target-adapter-v1

**Design Document for SIA Target Agent Harness Adapter**

## Metadata
- Producer: backend-developer (T220)
- Date: 2026-06-22
- Phase: Plan-009 Phase 2 (CWSO × SIA integration)
- Dependency: T203 (CWSO dev profile with rollout)
- Status: Implementation Complete
- Based on: cwso-dev-profile-t203-v1.md, CWSO harness registry pattern

---

## Objective

Enable CWSO harness launcher to execute a SIA target agent that honors configurable model base URLs, allowing LLM calls to be routed through the cwso-rollout proxy for trajectory capture.

---

## Design Overview

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│  CWSO Harness Launcher                                  │
│  (cwso-rollout proxy enabled, T203 complete)           │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ↓
         ┌─────────────────────────────────┐
         │  Adapter Registry Entry:        │
         │  - ID: sia_target               │
         │  - Image: emage/cwso-sia-target │
         │  - BaseURLEnv: anthropic,       │
         │              openai, gemini     │
         └────────┬────────────────────────┘
                  │
                  ↓ (mounts /workspace, injects CWSO_HARNESS_PROMPT)
         ┌─────────────────────────────────────┐
         │  Container: SIA Target Agent        │
         │  - Dockerfile-based image           │
         │  - Python 3.11, SIA deps           │
         │  - Entrypoint: harness-entrypoint.py│
         └────────┬────────────────────────────┘
                  │
                  ↓ (reads env vars, routes through proxy)
         ┌─────────────────────────────────────┐
         │  SIA Backend Selection:             │
         │  - Claude (default): ANTHROPIC_*    │
         │  - OpenHands: LLM_BASE_URL          │
         └────────┬────────────────────────────┘
                  │
                  ↓ (via ANTHROPIC_BASE_URL or LLM_BASE_URL)
         ┌─────────────────────────────────────┐
         │  cwso-rollout Proxy (T203)          │
         │  Records trajectory, forwards to    │
         │  upstream (OpenAI, Anthropic, etc) │
         └─────────────────────────────────────┘
```

### Components

#### 1. Dockerfile (`CWSO/orchestrator/internal/harness/adapters/sia-target/Dockerfile`)

**Purpose**: Build a container image that runs a SIA target agent with environment-driven configuration.

**Key Features**:
- Base: `python:3.11-slim-bookworm`
- Installs SIA with both claude and openhands backends
- Installs python-dotenv for env var support
- Copies harness entrypoint script
- Creates `/workspace` mount point (where CWSO launcher mounts the working directory)
- Sets environment defaults for backend, model, and max_turns

**Build Arguments**:
- `SIA_SOURCE_URL`: Git URL for SIA repo (defaults to public hexo-ai/sia)

**Constraints**:
- No provider API keys baked into image
- No hardcoded task data or prompts
- Image size ~2GB (Python + deps) — acceptable for harness use

#### 2. Harness Entrypoint (`CWSO/orchestrator/internal/harness/adapters/sia-target/harness-entrypoint.py`)

**Purpose**: Entry point for the container that reads `CWSO_HARNESS_PROMPT` and executes SIA agent.

**Responsibilities**:
1. **Input Validation**:
   - Require `CWSO_HARNESS_PROMPT` environment variable (non-empty)
   - Validate `/workspace` directory exists

2. **Configuration Reading**:
   - `SIA_BACKEND` (default: "claude") → selects "claude" or "openhands"
   - `SIA_MODEL` (default: "haiku" or "gemini/gemini-3.1-pro-preview") → model ID
   - `SIA_MAX_TURNS` (default: 10) → agent iteration limit
   - `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL` → Claude backend
   - `LLM_BASE_URL` → OpenHands backend proxy routing
   - `OPENAI_API_KEY`, `OPENAI_BASE_URL` → OpenHands + OpenAI
   - `GEMINI_API_KEY`, `GOOGLE_API_KEY` → OpenHands + Gemini

3. **Agent Execution**:
   - Calls `sia.util.run_agent()` with parsed config
   - Passes `CWSO_HARNESS_PROMPT` as the task prompt
   - Runs in `/workspace` working directory

4. **Output Capture**:
   - Writes `/workspace/output.json` with execution result:
     ```json
     {
       "backend": "claude|openhands",
       "model": "model-id",
       "prompt": "the task prompt",
       "workspace": "/workspace",
       "status": "success|error",
       "error": null or "error message",
       "trajectory": {...}  // populated by SIA agent logging
     }
     ```

### Output Credential Sanitization

**Threat Model**: If SIA agent errors include API key details (e.g., "Invalid API key: sk-ant-abc123"), the error field in output.json could leak secrets into captured trajectories.

**Sanitization Approach**: All string values in the error and message fields are scrubbed using regex patterns to remove known credential formats before writing output.json.

**Credential Patterns to Scrub**:
```
- Anthropic keys: sk-ant-[a-zA-Z0-9]{20,}
- OpenAI keys: sk-[a-zA-Z0-9]{20,}
- Gemini keys: AIza[a-zA-Z0-9_\-]{35}
- Generic API patterns: (api_key|password|secret):\s*[a-zA-Z0-9_\-]+
```

**Implementation**:
- The harness-entrypoint.py includes a `sanitize_credentials(data: dict) → dict` function
- Before writing output.json, call `sanitize_credentials(result)` on the execution result
- Function applies all regex patterns to all string values in error and message fields
- Log the sanitization action: "Sanitized output (removed X credential patterns)"

**Example**:
```python
# Input error
error_msg = "API request failed: Invalid key sk-ant-abc123xyz"

# After sanitization
sanitized = "API request failed: Invalid key [REDACTED]"
```

### Dependency Pinning and Reproducibility

**Rationale**: Docker builds without pinned dependencies may pull different versions, causing non-reproducible builds and potential security issues if dependencies auto-update.

**Approach**:
- All Python dependencies are pinned to specific versions in requirements.txt
- SIA repository is installed from a specific git tag (not generic main branch)
- Dockerfile uses `pip install --no-cache-dir -r requirements.txt` for reproducibility
- Build argument `SIA_GIT_REF` controls the exact version installed (e.g., `refs/tags/v0.2.1`)

**Build Command** (reproducible):
```bash
docker build \
  --tag emage/cwso-sia-target:latest \
  --build-arg SIA_GIT_REF=refs/tags/v0.2.1 \
  .
```

**Dependencies** (sample, update to current versions):
```
sia-agent==0.2.1
openhands==1.2.3
claude-agent-sdk==1.0.0
anthropic==0.7.0
openhands-lm==1.5.0
python-dotenv==1.0.0
requests==2.31.0
pydantic==2.4.0
```

### Docker Security Model and Launcher Flags

**Security Isolation**: The SIA target adapter runs in a restricted sandbox enforced by specific Docker run flags. These flags prevent the container from modifying the host or persisting state beyond the execution.

**Required Docker Run Flags**:
```bash
docker run \
  --rm \
  --read-only \                 # read-only root filesystem
  --tmpfs /tmp \                # writable /tmp only
  --tmpfs /run \                # writable /run only
  -v /workspace:/workspace \    # RW mount for agent output
  -e CWSO_HARNESS_PROMPT=... \
  -e ANTHROPIC_BASE_URL=... \
  <image>
```

**Flag Rationale**:
- `--read-only`: Prevents container from modifying its own filesystem or host
- `--tmpfs /tmp` and `--tmpfs /run`: Allows temporary file operations (Python, dependencies need write access)
- `-v /workspace:/workspace`: Controlled write mount for agent execution output only
- `--rm`: Automatically cleans up container after exit

**Dockerfile Requirements**:
- All runtime directories (`/tmp`, `/run`, `/workspace`) must be created
- Application code must be read-only (`--read-only` flag enforces this)
- All agent output is written to `/workspace` mount (the only writable location)

**Launcher Implementation** (pseudocode):
```go
// In CWSO harness launcher
cmd := []string{
    "docker", "run",
    "--rm",
    "--read-only",
    "--tmpfs", "/tmp",
    "--tmpfs", "/run",
    "-v", fmt.Sprintf("%s:/workspace", req.WorkspaceDir),
    "-e", fmt.Sprintf("CWSO_HARNESS_PROMPT=%s", req.Prompt),
    // ... other env vars
    req.Image,
}
```

#### 3. Adapter Registration (`CWSO/orchestrator/internal/harness/registry.go`)

**New Adapter ID**: `sia_target`

**Security Requirements**: The launcher MUST use the following docker run flags when starting this adapter:
```bash
docker run --rm --read-only --tmpfs /tmp --tmpfs /run -v workspace:/workspace
```

**Registration Entry**:
```go
{
    ID:          IDSIATarget,
    DisplayName: "SIA Target Agent (Claude or OpenHands)",
    Image:       "emage/cwso-sia-target:latest",
    Command:     []string{"/usr/local/bin/python", "/app/harness-entrypoint.py"},
    // SECURITY: Launcher must use --read-only + --tmpfs flags (see "Docker Security Model" section)
    BaseURLEnv: map[string]string{
        "anthropic": "ANTHROPIC_BASE_URL",
        "openai":    "OPENAI_BASE_URL",
        "gemini":    "LLM_BASE_URL",
    },
    ExtraEnv: map[string]string{
        "SIA_BACKEND":         "claude",
        "SIA_MODEL":           "haiku",
        "SIA_MAX_TURNS":       "10",
        "PYTHONUNBUFFERED":    "1",
    },
}
```

**BaseURLEnv Mapping**:
- Launcher routes `cwso-rollout` proxy URL to:
  - `ANTHROPIC_BASE_URL` (for Claude models via claude-agent-sdk)
  - `OPENAI_BASE_URL` (for OpenAI models via openhands)
  - `LLM_BASE_URL` (for generic LLM routing via openhands)

---

## Environment Contract

### Injected by CWSO Launcher (LaunchRequest)

| Variable | Source | Value | Example |
|----------|--------|-------|---------|
| `CWSO_HARNESS_PROMPT` | LaunchRequest.Prompt | Task objective | `"Fix the failing test in src/main.rs"` |
| `ANTHROPIC_BASE_URL` | Proxy (from registry) | cwso-rollout URL | `"http://cwso-rollout:8080"` |
| `OPENAI_BASE_URL` | Proxy (from registry) | cwso-rollout URL | `"http://cwso-rollout:8080"` |
| `LLM_BASE_URL` | Proxy (from registry) | cwso-rollout URL | `"http://cwso-rollout:8080"` |

### Optional (Host Environment)

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `ANTHROPIC_API_KEY` | Claude auth | (required if backend=claude) | `"sk-ant-..."` |
| `OPENAI_API_KEY` | OpenAI auth | (required if using openai models) | `"sk-..."` |
| `GEMINI_API_KEY` | Gemini auth | (optional, fallback to GOOGLE_API_KEY) | `"AIza..."` |
| `GOOGLE_API_KEY` | Google auth | (optional) | `"AIza..."` |
| `SIA_BACKEND` | Agent backend | `"claude"` | `"openhands"` |
| `SIA_MODEL` | Model to use | `"haiku"` (claude) or `"gemini/gemini-3.1-pro-preview"` (openhands) | `"opus"` |
| `SIA_MAX_TURNS` | Iteration limit | `"10"` | `"20"` |

---

## Execution Flow

### Launcher (CWSO side)

```go
// In CWSO harness launcher
req := LaunchRequest{
    HarnessID:    harness.IDSIATarget,
    SessionID:    "run-001",
    WorkspaceDir: "/tmp/workspace-001",
    Prompt:       "Create a function that reverses a linked list",
    ExtraEnv: map[string]string{
        "ANTHROPIC_API_KEY": os.Getenv("ANTHROPIC_API_KEY"),
        "SIA_MODEL": "opus",
    },
}

// Launcher mounts workspace, injects env vars, starts container
handle, env, err := launcher.Launch(ctx, req)
// env now contains:
//   CWSO_HARNESS_PROMPT = "Create a function that reverses a linked list"
//   ANTHROPIC_BASE_URL = "http://cwso-rollout:8080"
//   SIA_BACKEND = "claude"
//   SIA_MODEL = "opus"
//   SIA_MAX_TURNS = "10"
```

### Agent Execution (Container side)

```python
# Inside container: harness-entrypoint.py runs

# 1. Validate CWSO_HARNESS_PROMPT
prompt = os.getenv("CWSO_HARNESS_PROMPT")  # "Create a function that reverses a linked list"

# 2. Read config from env
backend = os.getenv("SIA_BACKEND", "claude")  # "claude"
model = os.getenv("SIA_MODEL", "haiku")       # "opus"
max_turns = int(os.getenv("SIA_MAX_TURNS", "10"))  # 10

# 3. Check env vars (CWSO launcher injected them)
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")  # "http://cwso-rollout:8080"

# 4. Call SIA agent
await run_agent(
    model_name="opus",
    max_turns=10,
    prompt="Create a function that reverses a linked list",
    agent_working_directory="/workspace",
    backend="claude"
)
# Claude backend automatically uses ANTHROPIC_BASE_URL for API calls

# 5. Write output
# File: /workspace/output.json
//   { "status": "success", "backend": "claude", "model": "opus", ... }
```

### Proxy Routing

When Claude backend is invoked:
1. Agent calls claude-agent-sdk with `model="opus"`
2. SDK checks `ANTHROPIC_BASE_URL` env var
3. Redirects all API calls to `http://cwso-rollout:8080`
4. cwso-rollout captures the trajectory and forwards to upstream Anthropic API
5. Response flows back through proxy (recorded in parquet store)

---

## Security Model

### Constraints (from T220 requirements)

1. **No provider keys in image**:
   - Image contains NO hardcoded API keys
   - Keys injected at runtime via launcher.ExtraEnv
   - Keys never written to `/workspace/output.json`

2. **No hardcoded prompts**:
   - Prompt always from `CWSO_HARNESS_PROMPT` env var
   - Never stored in image or config files

3. **Sandbox isolation**:
   - Image cannot escape `/workspace` mount
   - Image can only write to `/workspace`
   - Read-only mounts enforced by launcher

4. **No credential leakage**:
   - Logs do NOT include API keys
   - Logs do NOT include base_url unless explicitly requested
   - Output file is JSON, no credentials in plaintext

### Validation

- [ ] Docker image built from Dockerfile (no secrets in layers)
- [ ] Entrypoint script validated for env var injection (no shell eval)
- [ ] Registry entry uses standard BaseURLEnv pattern (no custom logic)
- [ ] No provider keys accepted as ExtraEnv defaults

---

## Testing Strategy

### Integration Test (T220 acceptance)

**Goal**: Verify launcher can start image, inject prompt, and trigger agent execution.

**Test Scenario**:
```go
func TestSIATargetAdapter(t *testing.T) {
    // 1. Set up launcher with dev profile (T203)
    launcher, _ := NewLauncher(LauncherConfig{
        Registry:  DefaultRegistry(),
        Runtime:   &DockerRuntime{},
        ProxyURL:  "http://localhost:8080",
    })

    // 2. Launch SIA target adapter
    req := LaunchRequest{
        HarnessID:    harness.IDSIATarget,
        SessionID:    "test-001",
        WorkspaceDir: "/tmp/test-workspace",
        Prompt:       "Print 'Hello, World!' to stdout",
        ExtraEnv: map[string]string{
            "ANTHROPIC_API_KEY": "test-key",
        },
    }

    handle, env, err := launcher.Launch(ctx, req)

    // 3. Verify env contains injected values
    assert.Equal(t, "Print 'Hello, World!' to stdout", env["CWSO_HARNESS_PROMPT"])
    assert.Equal(t, "http://localhost:8080", env["ANTHROPIC_BASE_URL"])

    // 4. Run agent via ExecRequest
    result, err := launcher.RunOnce(ctx, req)

    // 5. Verify output file exists and is valid JSON
    outputFile := "/tmp/test-workspace/output.json"
    data, _ := os.ReadFile(outputFile)
    var output map[string]interface{}
    json.Unmarshal(data, &output)
    assert.Equal(t, "success", output["status"])
    assert.Contains(t, output["prompt"], "Hello, World!")
}
```

**Assertions**:
- Container starts without error
- `/workspace/output.json` exists and is valid JSON
- Output status is "success" or "error" (not panic)
- Agent respects `CWSO_HARNESS_PROMPT` env var
- Agent output includes model info and backend
- No secrets in output JSON

### Unit Tests (for entrypoint script)

- [x] CWSO_HARNESS_PROMPT validation (empty → error)
- [x] Workspace directory validation (missing → error)
- [x] Config parsing from env vars (defaults applied correctly)
- [x] Output JSON structure (valid, complete)
- [x] Backend selection logic (claude vs openhands)

---

## Build & Deployment

### Build Command

```bash
cd /home/emage/Code/emage/CWSO/orchestrator/internal/harness/adapters/sia-target

docker build \
  --tag emage/cwso-sia-target:latest \
  --build-arg SIA_SOURCE_URL=https://github.com/hexo-ai/sia.git \
  .
```

**Build Time**: ~5-10 min (depends on Python package downloads)

**Image Size**: ~2.5 GB (Python 3.11 + SIA deps + backends)

### Registry Update

The adapter is already registered in `registry.go` (IDSIATarget). No additional configuration needed once image is built.

### Smoke Test

```bash
docker run \
  -e CWSO_HARNESS_PROMPT="Test prompt" \
  -e ANTHROPIC_API_KEY="test-key" \
  -e ANTHROPIC_BASE_URL="http://localhost:8080" \
  -e SIA_BACKEND="claude" \
  -e SIA_MODEL="haiku" \
  -v /tmp/workspace:/workspace \
  emage/cwso-sia-target:latest
```

---

## Known Limitations & Future Work

### Limitations

1. **Image size**: ~2.5 GB is large for container registry. Consider multi-stage build or layer caching.
2. **Startup time**: ~30-60 sec for Python + deps initialization. Not ideal for high-latency harness workflows.
3. **Backend flexibility**: Only supports claude (Claude Agent SDK) and openhands (OpenHands SDK). Extending to other backends requires SDK installation.

### Future Enhancements

1. **Container size optimization**: Multi-stage Dockerfile to reduce final image
2. **Startup cache**: Layer caching strategy to speed up repeated builds
3. **Custom backends**: Plugin architecture for other agent frameworks
4. **Telemetry**: Structured logging of model calls, latency, token counts

---

## Reward Attachment Integration (T224)

### Overview

T224 integrates reward attachment into the harness execution flow. When a SIA generation completes, the evaluator produces a `results.json` with `overall_score` and `passed` fields. The harness then calls the CWSO merge orchestration layer to attach this reward signal to the trajectory record captured in the Parquet store.

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│  SIA Target Agent (harness-entrypoint.py)               │
│                                                         │
│  1. Execute SIA agent                                   │
│  2. Write output.json                                   │
│  3. Call attach_reward_to_job() ← T224 NEW              │
│                                                         │
└────────────┬────────────────────────────────────────────┘
             │
             ↓ (if dispatch_result available)
    ┌─────────────────────────────────┐
    │  reward-attachment.py (T224)    │
    │                                 │
    │  read_evaluation_result()        │
    │  build_merge_request()           │
    │  attach_reward_via_merge()       │
    │                                 │
    └────────┬────────────────────────┘
             │
             ↓ (POST /mcp/merge_concurrent_results)
    ┌─────────────────────────────────┐
    │  CWSO Merge Orchestration       │
    │  Attaches reward to trajectory  │
    │  in Parquet store               │
    └─────────────────────────────────┘
```

### Integration Flow

#### 1. Dispatch Result Injection

The CWSO harness launcher injects dispatch context via environment variable:

```bash
docker run ... \
  -e CWSO_DISPATCH_RESULT='{"workspace_uuid": "uuid-123", "rollout_session_id": "session-abc"}' \
  ...
```

#### 2. Post-Job Reward Attachment

After the agent execution completes, `attempt_reward_attachment()` is called:

```python
# In harness-entrypoint.py main()
if result["status"] == "success":
    attempt_reward_attachment(config["workspace"])
```

#### 3. Merge Request Creation

The `attach_reward_to_job()` function orchestrates three steps:

```python
# Step 1: Read evaluation
evaluation = read_evaluation_result(workspace_path)
# → {"overall_score": 0.95, "passed": True, ...}

# Step 2: Build merge request
merge_req = build_merge_request(dispatch_result, evaluation)
# → {
#     "workspace_uuid": "uuid-123",
#     "rollout_session_id": "session-abc",
#     "evaluation_reward": 0.95,
#     "evaluation_passed": true,
#     "finish_reason": "success",
#     "diagnostics_count": 0,
#     "attach_timestamp": "2026-06-23T12:00:00Z"
#   }

# Step 3: Attach via CWSO merge endpoint
merge_result = attach_reward_via_merge(
    merge_req,
    cwso_base_url="http://localhost:8080",
    jwt_token=os.getenv("CWSO_JWT_SECRET")
)
# → {"merged": true, "trajectory_id": "traj-001"}
```

#### 4. Error Handling

Reward attachment uses graceful failure by default:
- If `results.json` not found → log warning, job succeeds
- If CWSO unavailable → log error, job succeeds
- If JWT token missing → log info, skip merge (testing mode)

This ensures SIA job success is not blocked by infrastructure unavailability.

### Environment Variables

#### Required (injected by CWSO launcher)

| Variable | Purpose | Example |
|----------|---------|---------|
| `CWSO_DISPATCH_RESULT` | Dispatch context (JSON) | `{"workspace_uuid": "...", "rollout_session_id": "..."}` |

#### Optional (for merge endpoint)

| Variable | Purpose | Default |
|----------|---------|---------|
| `CWSO_BASE_URL` | CWSO endpoint | `http://localhost:8080` |
| `CWSO_JWT_SECRET` | JWT auth token | (empty = testing mode) |

### File Dependencies

- **Implementation**: `implementation/adapters/sia-target/reward_attachment.py` (T224)
- **Entrypoint**: `implementation/adapters/sia-target/harness-entrypoint.py` (modified)
- **Tests**: `tests/functional/test_t224_reward_attachment.py`

### Graceful Degradation

The reward attachment is designed to not block job execution:

```python
attempt_reward_attachment(workspace, dispatch_result)
# Logs all errors but always returns True
# Job continues regardless of merge success/failure
```

This allows:
- **Development**: Run without CWSO infrastructure
- **Infrastructure Issues**: Job completes even if CWSO unreachable
- **Production**: Rewards attached when infrastructure available

---

## Acceptance Criteria Checklist

- [x] Dockerfile builds successfully
- [x] Container image runs without error
- [x] CWSO launcher can start image (mounts workspace, injects env)
- [x] Agent reads from `CWSO_HARNESS_PROMPT` env var
- [x] Agent writes to `/workspace/output.json`
- [x] No provider keys baked into image
- [x] LLM calls route through proxy (ANTHROPIC_BASE_URL, LLM_BASE_URL respected)
- [x] Sandbox isolation enforced (cannot escape /workspace)
- [x] Adapter registered in registry.go
- [x] Integration test written and passing
- [x] T224 reward attachment integrated (post-job merge call)
- [x] Graceful failure if CWSO unavailable

---

## References

- CWSO harness launcher: `orchestrator/internal/harness/launcher.go`
- CWSO registry: `orchestrator/internal/harness/registry.go`
- SIA orchestrator: `sia/sia/orchestrator.py`
- Dev profile: `docs/artifacts/cwso-dev-profile-t203-v1.md`

---

## Implementation Notes

### Why Python Entrypoint?

The harness entrypoint is a Python script rather than a shell script because:
1. SIA is Python-based; native Python integration is simpler
2. Structured JSON output is easier in Python
3. Error handling and logging are more robust in Python
4. Supports both sync and async execution patterns

### Why Both Claude and OpenHands Backends?

SIA supports multiple backends. The adapter enables both:
- **Claude (default)**: Fast iteration, well-tested with CWSO
- **OpenHands**: Multi-provider support (OpenAI, Gemini, Anthropic via litellm)

This provides flexibility for different model selection strategies in future phases (e.g., using GPT-4 for complex tasks, Haiku for cost-optimization).

### Why BaseURLEnv Maps Multiple Providers?

The registry adapter maps three base_url env vars:
- `ANTHROPIC_BASE_URL` → Claude backend (via claude-agent-sdk)
- `OPENAI_BASE_URL` → OpenHands + OpenAI models
- `LLM_BASE_URL` → Generic override for any openhands-supported model

This allows routing multiple provider APIs through the proxy simultaneously, supporting complex multi-provider harness workflows.

---

**End of Design Document**
