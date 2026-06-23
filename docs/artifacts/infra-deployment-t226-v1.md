# Artifact: Infrastructure Deployment for Phase 2 Live Integration Testing (T226)

**Producer**: devops-engineer  
**Task**: T226  
**Date**: 2026-06-23  
**Based on**: docs/tasks/task-T226.md, docs/artifacts/cwso-dev-profile-t203-v1.md

---

## Objective

Deploy a working CWSO + Polar infrastructure instance with rollout enabled on localhost to enable Phase 2 live integration testing (T228) of the SIA harness launcher (T223) with reward attachment (T224) and reward shaping (T225).

The infrastructure includes:
- **CWSO Orchestrator** (port 8080): main SIA control plane
- **Git-shadow sidecar** (phase2): conflict detection
- **Merge-engine sidecar** (phase4): concurrent merge orchestration
- **Rollout proxy** (port 8787): LLM call interception and Parquet trajectory capture
- **Parquet store**: queryable trajectory records for Phase 2 live integration tests

---

## Prerequisites

### System Requirements
- Docker and Docker Compose (v2+)
- Python 3.8+ (for validation scripts)
- Bash/shell environment
- ~2GB disk space (for Parquet store)

### Checked Dependencies
✅ CWSO repository available at `/home/emage/Code/emage/CWSO`  
✅ JWT dev secret at `/home/emage/Code/emage/CWSO/.env.jwt.dev`  
✅ emage.code repository at `/home/emage/Code/emage/emage.code`  

---

## Quick Start (Reproducible Bring-Up)

### Step 1: Create Parquet Store Directory

```bash
mkdir -p /tmp/t226-parquet-store
chmod 777 /tmp/t226-parquet-store
```

### Step 2: Load Environment Variables

```bash
cd /home/emage/Code/emage/emage.code
source deploy/t226-phase2.env
export CWSO_JWT_SECRET=$(cat ../CWSO/.env.jwt.dev)
export CWSO_BASE_URL=http://localhost:8080
```

### Step 3: Build and Start CWSO Infrastructure

```bash
docker compose -f deploy/docker-compose-t226.yml build --no-cache
docker compose -f deploy/docker-compose-t226.yml up -d
```

Wait ~10-15 seconds for services to start and pass health checks.

### Step 4: Verify Infrastructure Health

```bash
# Check orchestrator health
curl -s http://localhost:8080/healthz | jq .

# Check rollout proxy health
curl -s http://localhost:8787/v1/models | jq .

# Check MCP authentication (with JWT)
curl -s -H "Authorization: Bearer $CWSO_JWT_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
  http://localhost:8080/mcp | jq '.result.tools | length'
```

**Expected outputs:**
- `/healthz` → HTTP 200 with status details
- `/v1/models` → HTTP 200 with model list
- `/mcp` with JWT → HTTP 200 with ≥11 tools

---

## Manual SIA Dispatch Test

This test dispatches a single SIA generation via the harness launcher and verifies the complete chain: dispatch → evaluation → reward attachment → trajectory capture.

### Step 1: Create Test Prompt

```bash
mkdir -p /tmp/t226-test-workspace
cat > /tmp/t226-test-prompt.txt <<'EOF'
You are a helpful assistant. Please write a Python function that
adds two numbers together and returns the result.
Keep it simple and well-commented.
EOF
```

### Step 2: Dispatch SIA Generation

Use the dispatch test script (created in `implementation/scripts/dispatch-test-sia.py`):

```bash
cd /home/emage/Code/emage/emage.code
python3 implementation/scripts/dispatch-test-sia.py \
  --prompt-file /tmp/t226-test-prompt.txt \
  --workspace /tmp/t226-test-workspace \
  --cwso-url http://localhost:8080 \
  --jwt-secret "$CWSO_JWT_SECRET" \
  --dry-run false
```

Or manually with curl (if no test script available):

```bash
DISPATCH_PAYLOAD='{
  "prompt": "Write a Python function that adds two numbers",
  "max_turns": 5,
  "model": "claude",
  "backend": "claude"
}'

curl -s -X POST \
  -H "Authorization: Bearer $CWSO_JWT_SECRET" \
  -H "Content-Type: application/json" \
  -d "$DISPATCH_PAYLOAD" \
  http://localhost:8080/dispatch | jq .
```

### Step 3: Verify Dispatch Succeeds

Expected response:
```json
{
  "workspace_uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "rollout_session_id": "t226-live-session-xyz",
  "status": "dispatched"
}
```

Record the `workspace_uuid` and `rollout_session_id` for verification.

### Step 4: Verify Parquet Trajectories Were Written

```bash
# List Parquet files in store
ls -lh /tmp/t226-parquet-store/

# Expected: At least one dated directory with .parquet.lz4 files
# Example: /tmp/t226-parquet-store/2026-06-23/t226-live-session-xyz.parquet.lz4
```

### Step 5: Query Parquet Schema

```bash
python3 <<'PYEOF'
import pyarrow.parquet as pq
from pathlib import Path

store_path = Path("/tmp/t226-parquet-store")
parquet_files = list(store_path.rglob("*.parquet.lz4"))

if parquet_files:
    print(f"Found {len(parquet_files)} Parquet file(s)")
    for pf in parquet_files[:1]:  # Print first file's schema
        table = pq.read_table(str(pf))
        print(f"\nFile: {pf.name}")
        print(f"Schema:\n{table.schema}")
        print(f"Rows: {table.num_rows}")
        print(f"Size (bytes): {pf.stat().st_size}")
else:
    print("No Parquet files found. Verify CWSO_ROLLOUT_TRAJECTORY_STORE_ENABLED=true")
PYEOF
```

**Expected output:**
```
Found 1 Parquet file(s)
File: t226-live-session-xyz.parquet.lz4
Schema:
workspace_uuid: string
rollout_session_id: string
trajectory_id: string
timestamp: int64
lm_input_tokens: list<element: int64>
lm_logprobs: list<element: float>
... (other trajectory fields)
Rows: ≥1
Size (bytes): >1000
```

---

## Health Check Commands

Use these commands to verify the infrastructure is healthy at any time:

### Orchestrator Health
```bash
curl -s http://localhost:8080/healthz | jq .
# Expected: {"status":"ok","timestamp":"..."}
```

### Rollout Proxy Health
```bash
curl -s http://localhost:8787/v1/models | jq .
# Expected: {"object":"list","data":[...]}
```

### Docker Compose Status
```bash
docker compose -f deploy/docker-compose-t226.yml ps
# Expected: All services in "Up" state with health "healthy"
```

### Check Logs
```bash
# Orchestrator
docker logs cwso-orchestrator --tail 50

# Rollout
docker logs cwso-rollout --tail 50

# Merge engine
docker logs cwso-merge-engine --tail 50
```

---

## Environment Variables Summary

### CWSO Orchestrator
| Variable | Default | Purpose |
|----------|---------|---------|
| `CWSO_LOG_LEVEL` | `info` | Logging level (debug, info, warn, error) |
| `CWSO_ROLLOUT_API_ENABLED` | `true` | Enable Phase 2 rollout API |
| `CWSO_ROLLOUT_REWARD_ENABLED` | `true` | Enable reward injection |

### Rollout Proxy (Port 8787)
| Variable | Default | Purpose |
|----------|---------|---------|
| `CWSO_ROLLOUT_HTTP_BIND_PORT` | `8787` | Port for OpenAI-compatible LLM proxy |
| `CWSO_ROLLOUT_UPSTREAM_URL` | `http://127.0.0.1:18080` | Upstream LLM endpoint |
| `CWSO_ROLLOUT_UPSTREAM_API_KEY` | `` | Optional API key for upstream |
| `CWSO_ROLLOUT_CAPTURE_ENABLED` | `true` | Enable trajectory capture |
| `CWSO_ROLLOUT_TRAJECTORY_STORE_ENABLED` | `true` | Enable Parquet store |
| `CWSO_ROLLOUT_TRAJECTORY_STORE_PATH` | `/data/parquet-store` | Path to store Parquet files |
| `CWSO_ROLLOUT_DEFAULT_SESSION_ID` | `t226-live-session` | Session ID for grouping trajectories |

### SIA Harness Integration (T223)
Set these before running the harness:
```bash
export CWSO_BASE_URL=http://localhost:8080
export CWSO_JWT_SECRET=$(cat ../CWSO/.env.jwt.dev)
```

### Reward Attachment (T224)
Uses same variables as harness:
```bash
export CWSO_BASE_URL=http://localhost:8080
export CWSO_JWT_SECRET=$(cat ../CWSO/.env.jwt.dev)
```

### Reward Shaping (T225)
```bash
export REWARD_SHAPING_W_MERGE=0.5   # Weight for merge signal
export REWARD_SHAPING_W_EVAL=0.5    # Weight for eval metric
```

---

## Teardown Procedure

### Stop Infrastructure
```bash
docker compose -f deploy/docker-compose-t226.yml down -v
```

This will:
- Stop all containers
- Remove named volumes (cwso-runtime, etc.)
- Clean up temporary networks

### Optional: Cleanup Parquet Store
```bash
# Keep for analysis
ls -lh /tmp/t226-parquet-store

# Or remove if you want a fresh start next time
rm -rf /tmp/t226-parquet-store
```

---

## Integration with Phase 2 Live Integration Testing (T228)

T228 will use this deployment to run end-to-end tests. The following assumptions are made:

1. **CWSO orchestrator** is running on `http://localhost:8080`
2. **Parquet store** is accessible at `/tmp/t226-parquet-store`
3. **Environment variables** are set:
   - `CWSO_BASE_URL=http://localhost:8080`
   - `CWSO_JWT_SECRET=<dev-token>`
   - `PARQUET_STORE_PATH=/tmp/t226-parquet-store`

The T228 test harness can then:
- Dispatch SIA generations via `CWSO_BASE_URL`
- Verify trajectories in `PARQUET_STORE_PATH`
- Query evaluation results from workspace directories
- Validate reward attachment chain

---

## Troubleshooting

### "Connection refused" to localhost:8080
**Symptom**: `curl: (7) Failed to connect to localhost port 8080`

**Solution**:
1. Check containers are running: `docker compose -f deploy/docker-compose-t226.yml ps`
2. Wait 15 seconds for startup: `sleep 15 && curl http://localhost:8080/healthz`
3. Check logs: `docker logs cwso-orchestrator`

### Parquet files not being written
**Symptom**: `/tmp/t226-parquet-store` is empty after dispatch

**Solution**:
1. Verify env var: `echo $CWSO_ROLLOUT_TRAJECTORY_STORE_ENABLED` (should be `true`)
2. Check rollout logs: `docker logs cwso-rollout`
3. Verify upstream is reachable: `curl http://127.0.0.1:18080/v1/models`
4. Check directory permissions: `ls -ld /tmp/t226-parquet-store`

### "No such file or directory: .env.jwt.dev"
**Symptom**: Docker build fails with JWT secret not found

**Solution**:
```bash
cd /home/emage/Code/emage/CWSO
ls -la .env.jwt.dev
# If missing, create a dev token:
echo "test-jwt-dev-token-$(date +%s)" > .env.jwt.dev
```

### Docker build fails (Rust compilation errors)
**Symptom**: `cargo build` fails during Docker build

**Solution**:
1. Verify Rust dependencies are installed in CWSO repo
2. Try rebuilding with cache cleared:
   ```bash
   docker compose -f deploy/docker-compose-t226.yml build --no-cache
   ```
3. Check CWSO repo is up-to-date: `cd ../CWSO && git status`

---

## Acceptance Criteria Verification Checklist

- [ ] CWSO running on localhost:8080, health check passes
- [ ] Rollout proxy running on localhost:8787, models endpoint responds
- [ ] MCP endpoint authenticated with JWT
- [ ] Manual SIA dispatch test completes successfully
- [ ] At least one Parquet file written to `/tmp/t226-parquet-store`
- [ ] Parquet file is readable and contains expected schema fields
- [ ] No hardcoded secrets in code; all via environment variables
- [ ] Documentation complete with copy-paste commands
- [ ] Teardown procedure verified (all containers stop cleanly)

---

## Files Modified/Created

- [deploy/docker-compose-t226.yml](../../deploy/docker-compose-t226.yml): Multi-container orchestration
- [deploy/t226-phase2.env](../../deploy/t226-phase2.env): Environment configuration template
- [../CWSO/deploy/Dockerfile.rollout](../CWSO/deploy/Dockerfile.rollout): Rollout proxy container image
- [implementation/scripts/dispatch-test-sia.py](../../implementation/scripts/dispatch-test-sia.py): Test dispatch helper script
- [docs/artifacts/infra-deployment-t226-v1.md](infra-deployment-t226-v1.md): This deployment guide

---

## Next Steps

### T228: Phase 2 Live Integration Testing
Once this infrastructure is deployed and verified:

1. Run the T228 live integration test suite
2. Dispatch full SIA generation cycles (10+ turns)
3. Verify trajectories are captured with complete evaluation chain
4. Validate reward attachment and shaping signals
5. Generate Phase 2 live integration report

### Production Readiness (Future)
- Replace file-based JWT secret with Vault/SOPS
- Add persistent Parquet storage (cloud object store)
- Implement autoscaling for merge-engine sidecar
- Add monitoring/observability for rollout proxy
- Document runbooks for production deployment

---

## Security & Compliance Notes

### Secrets Management
- ✅ No hardcoded credentials in YAML files
- ✅ JWT secret injected via file mount (dev-only)
- ✅ All sensitive config via environment variables
- ✅ Upstream API keys optional and injected at runtime

### Container Security
- ✅ All containers run as non-root user (cwso)
- ✅ Read-only filesystems where possible
- ✅ Minimal capability sets (CAP_NET_BIND_SERVICE only)
- ✅ No privileged mode or host network access

### Production Debt Items
- **POC-DEBT**: File-based JWT secret acceptable for dev; production must use Vault integration
- **POC-DEBT**: Rollout upstream URL and API key not validated; add schema validation before production
- **POC-DEBT**: Parquet store is local filesystem; production needs cloud object store (S3, GCS)
- **POC-DEBT**: No rate limiting on rollout proxy; add for production

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1 | 2026-06-23 | Initial deployment guide for T226 |
