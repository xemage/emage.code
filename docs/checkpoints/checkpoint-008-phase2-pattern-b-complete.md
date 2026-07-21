# Checkpoint 008 — Phase 2 Pattern-B Foundation Complete

**Date**: 2026-06-22
**Phase**: Plan-009 Phase 2 — SIA loop on CWSO with Polar capture (harness-only, no weight updates)
**Status**: T220 conditions resolved; T221 implemented; T222 implemented; all CI green

---

## Completed Tasks

| Task | Title | Artifact(s) |
|------|-------|-------------|
| T220 | Real harness-adapter image for SIA target agent | `implementation/adapters/sia-target/` (Dockerfile, harness-entrypoint.py, registry-entry.go, requirements.txt); `docs/artifacts/sia-target-adapter-v1.md` |
| T221 | Patch SIA openhands backend to honor `LLM_BASE_URL` | `/home/emage/Code/emage/sia/sia/util.py` (local); `docs/artifacts/sia-lvm-routing-v1.md` |
| T222 | Wrap emage.code agent as SIA target + author `evaluate.py` | `implementation/adapters/sia-target/tasks/emage-agent-task-v1/` (task.md, evaluate.py, ground_truth.json, sample submissions, README); `tests/functional/test_t222_sia_task_evaluator.py` |

---

## T220 Conditions Resolved

Three conditions from tech-lead CONDITIONAL_PASS review, all addressed and verified:

### M1 — Output Credential Sanitization ✅
- `sanitize_credentials(data)` implemented in `harness-entrypoint.py`
- Recursive scrubber applies regex to all nested strings before writing `output.json`
- Patterns: Anthropic `sk-ant-*`, OpenAI `sk-*`, Gemini `AIza*`, generic `api_key/password/secret` k=v
- Indentation bug in patterns list fixed (was causing misaligned Gemini pattern)
- Design doc updated with threat model, patterns, and example

### M2 — Dockerfile Dependency Pinning ✅
- `requirements.txt` now includes all direct dependencies with pinned versions (`anthropic==0.7.0`, `openai==1.3.0`, `google-generativeai==0.3.0`, `pydantic==2.4.0`, `pydantic-settings==2.0.0`, `requests==2.31.0`, `urllib3==2.0.7`, `python-dotenv==1.0.0`)
- Dockerfile git clone rewritten: `git clone --depth 1 --branch "${SIA_GIT_REF}"` (no silent fallback to main — build fails if the tag does not exist)
- `SIA_GIT_REF` build arg defaults to `v0.2.1`; removed dangling `.git` directory in final layer
- Design doc updated with versioning rationale and build command

### M3 — Docker Security Flags ✅
- `SecurityFlags` field in `registry-entry.go`: `--rm --read-only --tmpfs /tmp --tmpfs /run`
- `harness-entrypoint.py` validates `/workspace` exists (will fail fast if launcher misconfigures mount)
- Dockerfile comment block specifies required launcher flags
- Design doc includes "Docker Security Model and Launcher Flags" section with pseudocode for launcher

---

## T221 Status

- **Implementation**: complete in `/home/emage/Code/emage/sia/sia/util.py`
  - `run_agent_openhands()` reads `LLM_BASE_URL` env and passes `base_url` to `LLM()` kwargs when set
  - Backward-compatible: unset env → default litellm routing unchanged
  - Claude backend routing via `ANTHROPIC_BASE_URL` already worked and is unchanged
- **Tests**: 5 unit tests defined covering set/unset/empty-string cases
- **Design doc**: `docs/artifacts/sia-lvm-routing-v1.md` (480 lines) — routing architecture, env contract, four scenarios
- **Blocker** (external/minor): GitHub fork write access prevents push to `feature/t221-sia-openhands-routing`; code is committed locally and ready. Requires authorized push or maintainer PR to resolve.

---

## T222 Status

- **Task fixture**: `implementation/adapters/sia-target/tasks/emage-agent-task-v1/`
  - `data/public/task.md` — task description: produce a valid structured plan summary
  - `data/public/evaluate.py` — CLI evaluator: `python evaluate.py --gen-dir <dir>` → `results.json`
  - `data/private/ground_truth.json` — scoring weights, thresholds, allowed values
  - `submissions/sample_good/` and `submissions/sample_bad/` — reference fixtures

- **Evaluator metrics**:
  | Metric | Weight | Description |
  |--------|--------|-------------|
  | schema_validity | 0.30 | Required top-level fields present with correct types |
  | task_quality | 0.35 | Per-task field validity, status/priority enum compliance |
  | dependency_integrity | 0.20 | No self-refs, no dangling dependency IDs |
  | content_completeness | 0.15 | Min tasks, min risks, non-empty summary |

- **Test coverage**: 3 functional tests in `tests/functional/test_t222_sia_task_evaluator.py`:
  - `sample_good` → `overall_score 1.0, passed: true`
  - `sample_bad` → `overall_score 0.41, passed: false`
  - Required keys present in results.json

---

## Code Quality Gate

| Check | Result |
|-------|--------|
| `python3 -m py_compile harness-entrypoint.py` | ✅ clean (no warnings) |
| Markdown link integrity | ✅ all links resolve |
| Full test suite (114 tests) | ✅ OK, 12 skipped |
| Conventional commit ratio | ✅ 19/20 (95%) |
| CI pipelines #265 / #266 (branch + MR) | ✅ success |

---

## Security Audit Summary (Gate 2 pre-check)

| Control | Status |
|---------|--------|
| No API keys in image/code | ✅ runtime-injected only |
| Capture path credential scrubbing | ✅ M1 — sanitize_credentials() |
| Reproducible builds (pinned deps) | ✅ M2 — requirements.txt + --branch flag |
| Container read-only root + tmpfs | ✅ M3 — SecurityFlags documented and enforced |
| Prompt logged as hash not full text | ✅ harness-entrypoint.py logs config, not content |
| No PII in task fixture | ✅ all fixture data is synthetic |

Full Gate 2 security review (tech-lead + security-engineer) is required before T223.

---

## Dependency Chain

```
✅ T201  Contract snapshot
✅ T202  ADR patterns A/B/C
✅ T203  CWSO dev profile (rollout enabled, model endpoint)
✅ T210  CwsoClient library
✅ T211  Role → tier mapping
✅ T212  Concurrent-merge orchestrator
✅ T213  AST conflict pre-check
→  T214  Pattern A integration test (in_progress — parallel track)
✅ T220  SIA harness-adapter image (conditions resolved)
✅ T221  SIA openhands base_url routing (implemented; GitHub push blocked)
✅ T222  emage agent as SIA target + evaluate.py
→  T223  Run SIA generation + confirm Parquet capture  ← NEXT
→  T224  Reward attachment via rollout_session_id
→  T225  Reward shaping: merge ±1 + eval metric
```

---

## Active Blockers

| ID | Type | Severity | Description | Resolution |
|----|------|----------|-------------|------------|
| B01 | external | minor | T221 SIA changes need GitHub fork push | Authorized account push or maintainer PR |

---

## Next Steps

1. **Gate 2 security review** — tech-lead + security-engineer review T220/T221/T222 before T223 starts
2. **Merge MR !45** to develop after Gate 2 PASS
3. **T223** (qa-engineer) — run one SIA generation through CWSO harness launcher; verify trajectory lands in Parquet store with token IDs + logprobs
4. **T224** (backend-developer) — pass `rollout_session_id` through `merge_concurrent_results`; verify reward record
5. **T225** (backend-developer) — combine merge ±1 with `results.json` primary metric into shaped reward signal

---

## Token Usage

| Budget | Allocation | Estimated Used | Status |
|--------|-----------|----------------|--------|
| Phase 2 Planning | 80k | ~40k | ✅ on track |
| Phase 2 Implementation | 120k | ~75k | ✅ on track |
| Phase 2 QA / Security | 60k | ~25k | ✅ on track |
