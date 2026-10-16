# Completed Tasks

Append-only log. Entries move here after the orchestrator marks a task `done`.

| ID | Title | Owner | Done on | Outcome / artifact |
|----|-------|-------|---------|--------------------|
| T212 | Concurrent-merge orchestration (N workers → shadow → merge) | backend-developer | 2026-06-20 | implementation/runtime/cwso/concurrent_merge.py; tests/unit/test_cwso_concurrent_merge.py; [!42](https://gitlab.com/em-age/emage.code/-/merge_requests/42) |
| T226 | Deploy CWSO + Polar infrastructure (rollout enabled, Parquet store) | devops-engineer | 2026-06-23 | deploy/docker-compose-t226.yml; deploy/t226-phase2.env; docs/artifacts/infra-deployment-t226-v1.md; docs/artifacts/T226-COMPLETION-SUMMARY.md; implementation/scripts/dispatch-test-sia.py; implementation/scripts/sia-executor.py (reference template); implementation/scripts/test-jwt-registration.py; docs/artifacts/t226-infrastructure-e2e-completion-v1.md; docs/artifacts/t226-sia-executor-403-debug-report-v1.md; CORS fix: orchestrator hostname added to ALLOWED_ORIGINS; E2E validated in mock execution mode; task assignment deferred to T235 |
| T228 | Phase 2 live integration: SIA harness → reward → trajectory | qa-engineer | 2026-06-23 | docs/artifacts/phase2-live-integration-test-report-v1.md; E2E validation: dispatch ✅, mock execution ✅, reward attachment ✅, mock Parquet ✅; All critical path tests passing; infrastructure debugging and CORS fix completed (T226); ready for production executor implementation (T235) |
| T232 | sia-harness release gate + Ed25519 witness signing | devops-engineer | 2026-06-23 | implementation/adapters/sia-target/release_gate.py (evaluate_release_candidate, sign_witness, verify_witness, promote); keys/witness-dev.pub; tests/functional/test_t232_release_gate.py (38 tests, 100% passing); docs/artifacts/release-gate-witness-v1.md; security CONDITIONAL_PASS→SEC-001/002/003 resolved; [!47](https://gitlab.com/em-age/emage.code/-/merge_requests/47) |
| T231 | Fine-tune `<some-model>` (LoRA/GRPO) + redeploy behind HAL | backend-developer | 2026-06-23 | 8 scripts created, LoRA fine-tuning complete with seed=42, HAL redeployed, rollback documented |
