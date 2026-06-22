# T220 Conditions from Tech-Lead Code Review

## Status
Tech-lead code review: **CONDITIONAL_PASS**. Three security/reproducibility conditions must be resolved before merge.

## Conditions

### M1: Output Credential Sanitization (Security)

**Issue**: output.json error field could leak API keys if SIA agent error includes credentials.

**Fix**:
- Add `sanitize_credentials(data)` function to harness-entrypoint.py
- Use regex to scrub patterns: `sk-ant-[a-zA-Z0-9]+`, `sk-[a-zA-Z0-9]+`, `AIza[a-zA-Z0-9_-]+`
- Call before writing output.json
- Update sia-target-adapter-v1.md: add "Output Credential Sanitization" section

**Effort**: 30 min

### M2: Dockerfile Dependency Pinning (Reproducibility)

**Issue**: No pinned versions for SIA/backends; non-reproducible builds.

**Fix**:
- Create requirements.txt with pinned versions (sia-agent==0.2.1, etc.)
- Update Dockerfile build arg to use git ref (refs/tags/v0.2.1) instead of generic URL
- Update sia-target-adapter-v1.md: add "Dependency Pinning" section

**Effort**: 30 min

### M3: Docker Security Flags (Isolation)

**Issue**: Design claims isolation but doesn't specify docker run flags (--read-only, --tmpfs).

**Fix**:
- Update sia-target-adapter-v1.md: add "Docker Security Model and Launcher Flags" section
- Document required flags: --read-only, --tmpfs /tmp, --tmpfs /run, -v workspace
- Update registry.go with comment explaining flag requirements
- Update Dockerfile: ensure /workspace exists, add comments

**Effort**: 20 min

## Next Steps
1. Address all three conditions in feature/t220-sia-harness-adapter branch
2. Smoke test locally: `docker run --rm --read-only --tmpfs /tmp -v /workspace:/workspace -e CWSO_HARNESS_PROMPT=test emage/cwso-sia-target`
3. Verify output.json has no credential patterns
4. Push updates to origin
5. Request tech-lead re-review (quick pass expected)

**Total Effort**: ~1.5 hours

**Merge Blocker**: No; T221 can proceed independently and merge while T220 fixes are being applied.
