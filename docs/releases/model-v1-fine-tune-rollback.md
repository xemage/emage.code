# T231 Rollback Procedure: Fine-tune Model Deployment

**Version:** v1-ft
**Created:** 2026-06-23
**Last Updated:** 2026-06-23

## Overview

This document provides procedures to rollback a fine-tuned model deployment back to the baseline model if issues are encountered.

## Prerequisites Check

Before deploying, verify:
- [ ] Baseline model is available and tested
- [ ] Fine-tuned model passed validation (see Validation section)
- [ ] HAL/vLLM server is configured and monitored
- [ ] Rollback operator has access to deployment scripts

## Rollback Levels

### Level 1: Quick Server Restart (Fast, Low Risk)
**Time:** ~30 seconds
**Use when:** Model is loaded but inference is slow or producing bad outputs

```bash
# 1. Kill the current vLLM server
pkill -f "vllm.entrypoints.openai.api_server"

# 2. Verify server is stopped
sleep 5
ps aux | grep vllm

# 3. Restart with baseline model
python3 implementation/scripts/deploy-vllm.py \
  --model-path models/baseline-v0 \
  --port 8000
```

**Verification:**
```bash
curl http://localhost:8000/v1/models
# Should show: "baseline-v0" or your baseline model
```

### Level 2: Config Rollback (Medium Risk)
**Time:** ~1-2 minutes
**Use when:** Model loading hangs or causes crashes

```bash
# 1. Stop server
pkill -f "vllm.entrypoints.openai.api_server"
sleep 5

# 2. Restore baseline config
cp deployment-config-baseline.json deployment-config.json

# 3. Restart with baseline
python3 implementation/scripts/deploy-vllm.py \
  --model-path "$(jq -r .model_path deployment-config.json)" \
  --port "$(jq -r .port deployment-config.json)"
```

### Level 3: Full Model Replacement (High Risk)
**Time:** ~5 minutes
**Use when:** Fine-tuned model is corrupted or causes system instability

```bash
# 1. Backup current (broken) model
mv models/fine-tuned-v1 models/fine-tuned-v1.backup-$(date +%s)

# 2. Restore baseline model (from git or archive)
git checkout models/baseline-v0/

# 3. Stop server
pkill -f "vllm.entrypoints.openai.api_server"
sleep 5

# 4. Start with baseline
python3 implementation/scripts/deploy-vllm.py \
  --model-path models/baseline-v0 \
  --port 8000

# 5. Verify
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "baseline-v0",
    "prompt": "def hello",
    "max_tokens": 50
  }'
```

## Validation Steps

### Post-Rollback Verification

After executing any rollback, run these checks:

#### 1. Server Health Check
```bash
# Verify server is running
curl http://localhost:8000/v1/models

# Expected response:
# {
#   "object": "list",
#   "data": [
#     {"id": "baseline-v0", "object": "model", ...}
#   ]
# }
```

#### 2. Inference Test
```bash
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "baseline-v0",
    "prompt": "def fibonacci(n):",
    "max_tokens": 100,
    "temperature": 0.7
  }'

# Expected: Valid completion within 5 seconds
```

#### 3. Latency Test
```bash
time curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "baseline-v0",
    "prompt": "def sort_array(arr):",
    "max_tokens": 50
  }' > /dev/null

# Expected: p50 latency < 2s (varies by hardware)
```

#### 4. Log Review
```bash
# Check for errors in vLLM logs
tail -50 fine-tune-deploy.log | grep -i error
tail -50 fine-tune-deploy.log | grep -i warning
```

### Rollback Success Criteria

Rollback is **successful** when:
- [x] Server starts and responds to health checks
- [x] /v1/models endpoint returns baseline model
- [x] Completions endpoint responds within SLA
- [x] No crash/error logs in vLLM output
- [x] Memory utilization is stable (not growing)

## Recovery Timeline

| Level | Time | Risk | Recovery Window |
|-------|------|------|-----------------|
| 1 | 30s | Low | Immediate |
| 2 | 1-2m | Medium | < 5 minutes |
| 3 | 5m | High | < 10 minutes |

## Post-Incident Checklist

After any rollback, complete:

- [ ] Document what went wrong (create issue/ticket)
- [ ] Review fine-tuned model logs (fine-tune.log)
- [ ] Check hyperparameters (hyperparameters.json)
- [ ] Verify baseline model is stable
- [ ] Analyze T230 dataset quality (if issue is data-related)
- [ ] Update rollback procedure with new findings
- [ ] Schedule re-attempt with fixes

## Automated Rollback (Future)

To implement automated rollback:

1. Add health check monitoring to deployment script
2. Define failure thresholds (latency, error rate)
3. Trigger Level 1 rollback if thresholds exceeded
4. Log incident and alert on-call engineer

```python
# Example health check loop (not yet implemented)
while True:
    health = check_server()
    if health['error_rate'] > 0.05:
        logger.error("Error rate too high, triggering rollback")
        rollback_to_baseline()
    time.sleep(30)
```

## Contacts & Escalation

| Role | Responsibility | On-Call |
|------|----------------|---------|
| DevOps Engineer | Execute rollback | Pager/Slack |
| Backend Developer | Investigate root cause | Pager/Slack |
| Tech Lead | Approve Level 3 rollback | Email/Phone |

## References

- Fine-tuning guide: docs/artifacts/t231-fine-tuning-implementation-guide-v1.md
- Deployment config: deployment-config.json
- Training logs: fine-tune.log
- Hyperparameters: implementation/models/fine-tune-output/hyperparameters.json
- T226 infrastructure: docs/artifacts/t226-sia-executor-403-debug-report-v1.md

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1 | 2026-06-23 | Initial rollback procedure |

---

**For questions or updates, contact:** backend-developer@emage.code
