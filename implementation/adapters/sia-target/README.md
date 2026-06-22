# SIA Target Agent Harness Adapter

This directory contains the implementation of the SIA Target Agent Harness Adapter for CWSO integration.

## Artifact Reference

- Design Document: [sia-target-adapter-v1.md](../../../docs/artifacts/sia-target-adapter-v1.md)
- Task: T220 (SIA harness adapter implementation)
- Tech Lead Conditions: M1 (credential sanitization), M2 (dependency pinning), M3 (security flags)

## Files

### `Dockerfile`

Builds the container image for the SIA target agent harness adapter.

**Features**:
- Base: `python:3.11-slim-bookworm`
- Pinned dependencies via `requirements.txt`
- SIA installed from specific git tag (via `SIA_GIT_REF` build arg)
- Harness entrypoint configured as container entrypoint
- Security: read-only root filesystem enforcement (launcher configures --read-only flag)

**Build Command**:
```bash
cd implementation/adapters/sia-target
docker build --tag emage/cwso-sia-target:latest .
```

**With Custom SIA Version**:
```bash
docker build \
  --tag emage/cwso-sia-target:latest \
  --build-arg SIA_GIT_REF=refs/tags/v0.3.0 \
  .
```

### `harness-entrypoint.py`

Entry point script for the container. Handles:
1. Environment validation (`CWSO_HARNESS_PROMPT`, workspace)
2. Configuration parsing (backend, model, max_turns)
3. SIA agent execution
4. Output capture with credential sanitization
5. Error handling and logging

**Key Features**:
- `sanitize_credentials()` function removes API keys from error messages
- Structured JSON output to `/workspace/output.json`
- Comprehensive logging
- Async-ready for future OpenHands integration

### `requirements.txt`

Python dependencies with pinned versions for reproducible builds.

**Current Versions** (sample):
```
sia-agent==0.2.1
claude-agent-sdk==1.0.0
anthropic==0.7.0
openhands==1.2.3
python-dotenv==1.0.0
requests==2.31.0
pydantic==2.4.0
```

To update: Run `pip freeze` in a dev environment and copy relevant lines.

### `registry-entry.go`

Reference Go code for registering this adapter in CWSO registry.

**Action Required**: Copy this code into `CWSO/orchestrator/internal/harness/registry.go`

## Security Model

### Docker Sandbox Isolation

The adapter runs with restricted permissions to prevent escape and state persistence:

```bash
docker run \
  --rm                           # Auto-cleanup
  --read-only                    # Read-only root filesystem
  --tmpfs /tmp                   # Writable /tmp (temporary files)
  --tmpfs /run                   # Writable /run (runtime files)
  -v /workspace:/workspace       # RW mount for agent output
  emage/cwso-sia-target:latest
```

### Credential Sanitization

The `sanitize_credentials()` function removes known credential patterns:
- `sk-ant-[a-zA-Z0-9]{20,}` — Anthropic keys
- `sk-[a-zA-Z0-9]{20,}` — OpenAI keys
- `AIza[a-zA-Z0-9_\-]{35}` — Gemini keys
- Generic patterns: `api_key`, `password`, `secret`

Applied to: error messages, log messages, any string output before writing `/workspace/output.json`

## Deployment

### Step 1: Build Image

```bash
cd implementation/adapters/sia-target
docker build --tag emage/cwso-sia-target:latest .
```

### Step 2: Tag and Push to Registry

```bash
docker tag emage/cwso-sia-target:latest emage/cwso-sia-target:v0.2.1
docker push emage/cwso-sia-target:latest
docker push emage/cwso-sia-target:v0.2.1
```

### Step 3: Update CWSO Registry

Copy `registry-entry.go` code into `CWSO/orchestrator/internal/harness/registry.go`

### Step 4: Smoke Test

```bash
# Create test workspace
mkdir -p /tmp/test-workspace

# Run container with security flags
docker run \
  --rm \
  --read-only \
  --tmpfs /tmp \
  --tmpfs /run \
  -v /tmp/test-workspace:/workspace \
  -e CWSO_HARNESS_PROMPT="Print 'Hello, World!'" \
  -e ANTHROPIC_API_KEY="test-key" \
  -e ANTHROPIC_BASE_URL="http://localhost:8080" \
  -e SIA_BACKEND="claude" \
  -e SIA_MODEL="haiku" \
  emage/cwso-sia-target:latest

# Check output
cat /tmp/test-workspace/output.json
```

## Testing

### Unit Tests

For the `sanitize_credentials()` function:

```python
def test_sanitize_anthropic_key():
    data = {"error": "Invalid key: sk-ant-abc123xyz"}
    result = sanitize_credentials(data)
    assert "[REDACTED]" in result["error"]
    assert "sk-ant-" not in result["error"]

def test_sanitize_nested():
    data = {
        "result": {"message": "API key: sk-abc123"}
    }
    result = sanitize_credentials(data)
    assert "[REDACTED]" in str(result)
```

### Integration Tests

Verify the full flow with CWSO launcher:
```go
func TestSIATargetAdapter(t *testing.T) {
    launcher := NewLauncher(...)
    req := LaunchRequest{
        HarnessID: harness.IDSIATarget,
        Prompt:    "Test prompt",
        WorkspaceDir: "/tmp/test",
    }
    result, err := launcher.Launch(context.Background(), req)
    assert.NoError(t, err)
    assert.FileExists(t, "/tmp/test/output.json")
}
```

## Known Issues & Future Work

### Known Limitations
1. Image size: ~2.5 GB (large for container registries)
2. Startup time: ~30-60 seconds (Python + deps initialization)
3. Async execution placeholder (SIA API may vary)

### Future Enhancements
1. Multi-stage Dockerfile to reduce image size
2. Layer caching optimization
3. Plugin architecture for additional backends
4. Structured telemetry (token counts, latency)

## References

- [sia-target-adapter-v1.md](../../../docs/artifacts/sia-target-adapter-v1.md) — Design document
- [cwso-dev-profile-t203-v1.md](../../../docs/artifacts/cwso-dev-profile-t203-v1.md) — CWSO proxy setup
- [SIA Repository](https://github.com/hexo-ai/sia) — Source code

## Acceptance Criteria Checklist

- [x] Dockerfile builds successfully
- [x] harness-entrypoint.py validates environment and executes SIA
- [x] sanitize_credentials() removes known credential patterns
- [x] requirements.txt pins all dependencies
- [x] Security flags documented (--read-only, --tmpfs)
- [x] registry-entry.go provides CWSO integration code
- [x] Output written to /workspace/output.json
- [x] No API keys baked into image
- [x] Tech Lead conditions M1, M2, M3 satisfied

## Maintenance

### Update Dependencies

1. Update `requirements.txt` with new pinned versions
2. Rebuild image: `docker build -t emage/cwso-sia-target:latest .`
3. Test with smoke test script
4. Tag release: `docker tag emage/cwso-sia-target:latest emage/cwso-sia-target:v0.X.X`

### Update SIA Version

1. Determine desired SIA tag from [SIA releases](https://github.com/hexo-ai/sia/releases)
2. Update build arg: `docker build --build-arg SIA_GIT_REF=refs/tags/vX.X.X ...`
3. Rebuild and test
