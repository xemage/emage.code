# Completed Tasks

Append-only log. Entries move here after the orchestrator marks a task `done`.

| ID | Title | Owner | Done on | Outcome / artifact |
|----|-------|-------|---------|--------------------|
| T001 | Benchmark Mapping and Spec | solution-architect | 2026-05-11 | docs/artifacts/agent-benchmark-mapping-v1.md |
| T002 | Dataset and Baseline Design | qa-engineer | 2026-05-11 | tests/_baselines/benchmark-thresholds-v1.json; tests/fixtures/benchmarks/*.json |
| T003 | Implement Tool-Use Complexity Benchmarks | backend-developer | 2026-05-11 | tests/performance/test_tool_use_complexity.py |
| T004 | Implement Orchestration Trajectory Benchmarks | backend-developer | 2026-05-11 | tests/performance/test_orchestration_trajectory_quality.py |
| T005 | Implement Scalability and Throughput Benchmarks | backend-developer | 2026-05-11 | tests/performance/test_scaling_and_throughput.py |
| T006 | Runner and CI Integration | devops-engineer | 2026-05-11 | tests/README.md (benchmark section), runner auto-discovery confirmed |
| T007 | Validation and Threshold Tuning | qa-engineer | 2026-05-11 | docs/artifacts/benchmark-validation-report-v1.md |
| T008 | Docs and Checkpoint | technical-writer | 2026-05-11 | docs/checkpoints/checkpoint-004-benchmark-expansion.md |
| T009 | Define v3 schema contracts | solution-architect | 2026-05-22 | docs/artifacts/v3-schema-contract-v1.md |
| T010 | Build sync and drift tooling | backend-developer | 2026-05-22 | v3/implementation/scripts/sync-v3.mjs; v3/implementation/scripts/verify-v3.mjs |
| T011 | Build managed-agent cookbooks | backend-developer | 2026-05-22 | v3/implementation/cookbooks/README.md; v3/implementation/cookbooks/core-delivery/agent.yaml; v3/implementation/cookbooks/core-delivery/README.md; v3/implementation/cookbooks/core-delivery/steering-examples.json |
| T012 | Add validation super-gate | qa-engineer | 2026-05-22 | v3/implementation/scripts/check-v3.py; v3/implementation/README.md; tests/functional/test_v3_validation_gate.py |
| T013 | Security handoff hardening | security-engineer | 2026-05-22 | docs/artifacts/v3-handoff-security-model-v1.md; v3/implementation/runtime/handoff/schema-v1.json; v3/implementation/runtime/handoff/examples/valid-handoff.json; v3/implementation/runtime/handoff/validator.py; tests/functional/test_v3_handoff_security.py |
| T014 | Hook and policy taxonomy spec | solution-architect | 2026-05-22 | docs/artifacts/v3-hook-policy-spec-v1.md; v3/implementation/scripts/check-v3.py; tests/functional/test_v3_validation_gate.py |
| T015 | Trajectory telemetry and replay | backend-developer | 2026-05-22 | docs/artifacts/v3-telemetry-schema-v1.md; v3/implementation/runtime/telemetry/schema-v1.json; v3/implementation/runtime/telemetry/replay.py; v3/implementation/runtime/telemetry/examples/baseline-run.json; v3/implementation/runtime/telemetry/examples/candidate-run.json; tests/functional/test_v3_telemetry_replay.py |
| T016 | Benchmark pack expansion | qa-engineer | 2026-05-22 | docs/artifacts/v3-benchmark-report-v1.md; tests/fixtures/benchmarks/v3_benchmark_pack_cases.json; tests/performance/test_v3_benchmark_pack.py; tests/_baselines/benchmark-thresholds-v1.json; tests/_reports/v3-benchmark-report-v1.json |
| T017 | Knowledge registry generation | backend-developer | 2026-05-22 | v3/implementation/registry/schema.json; v3/implementation/registry/index.json; v3/implementation/registry/summary.md; v3/implementation/scripts/generate-registry-v3.py; tests/functional/test_v3_validation_gate.py |
| T018 | Package and install workflow | devops-engineer | 2026-05-23 | v3/implementation/registry/package.schema.json; v3/implementation/scripts/package-v3.py; v3/implementation/commands/package-install.md; v3/implementation/commands/package-update.md; v3/implementation/commands/package-uninstall.md; tests/functional/test_v3_package_workflow.py |
| T019 | Trigger framework | backend-developer | 2026-05-23 | v3/implementation/triggers/spec-v1.md; v3/implementation/runtime/triggers/runner.py; v3/implementation/triggers/examples/schedule-daily.json; v3/implementation/triggers/examples/event-webhook.json; v3/implementation/triggers/examples/policy-default.json; tests/functional/test_v3_trigger_framework.py |
| T020 | SDK adapter experiments | integration-agent | 2026-05-23 | docs/artifacts/v3-adapter-evaluation-v1.md; v3/implementation/adapters/base.py; v3/implementation/adapters/antigravity_adapter.py; v3/implementation/adapters/opencode_adapter.py; v3/implementation/adapters/smoke.py; tests/fixtures/adapters/sample-input.json; tests/functional/test_v3_adapter_smoke.py |
| T021 | Migration guide and rollout | technical-writer | 2026-05-23 | docs/artifacts/v3-migration-guide-v1.md; docs/plans/plan-003-v3-execution-wave1.md; docs/checkpoints/checkpoint-v3-002-implementation-readiness.md |
| T022 | Pilot switch validation and rollback drill 2 | integration-agent | 2026-05-23 | docs/artifacts/v3-pilot-rollout-report-v1.md; docs/checkpoints/checkpoint-v3-004-pilot-switch-validation.md; tests/_reports/pilot/trigger-queue.json; tests/_reports/pilot/trigger-audit.log; tests/_reports/pilot/adapter-antigravity.json; tests/_reports/pilot/adapter-opencode.json |
| T023 | Pilot cycle-2 and promotion readiness | integration-agent | 2026-05-23 | docs/artifacts/v3-pilot-rollout-report-v2.md; docs/checkpoints/checkpoint-v3-005-promotion-readiness.md; tests/_reports/pilot-cycle2/trigger-queue.json; tests/_reports/pilot-cycle2/adapter-antigravity.json; tests/_reports/pilot-cycle2/adapter-opencode.json |
| T024 | Release documentation gate and v1.0.1 docs refresh | devops-engineer | 2026-05-23 | .gitlab-ci.yml; README.md; docs/wiki/README.md; docs/wiki/home.md; CONTRIBUTING.md; docs/tasks/task-T024.md |
| T025 | Audit documentation and usage flow | technical-writer | 2026-05-23 | docs/artifacts/artifact-v1-doc-audit.md; docs/tasks/task-T025.md |
| T026 | Update core README and contributor docs | technical-writer | 2026-05-23 | README.md; CONTRIBUTING.md; docs/tasks/task-T026.md |
| T027 | Update wiki pages and navigation consistency | technical-writer | 2026-05-23 | docs/wiki/README.md; docs/wiki/home.md; docs/wiki/quick-start.md; docs/tasks/task-T027.md |
| T028 | Harden release documentation verification gate | devops-engineer | 2026-05-23 | .gitlab-ci.yml; scripts/verify-release-docs.py; docs/tasks/task-T028.md |
| T029 | Run documentation validation checks | qa-engineer | 2026-05-23 | docs/artifacts/artifact-v1-doc-validation-report.md; docs/tasks/task-T029.md |
| T030 | Push changes and verify CI to green | release-manager | 2026-05-23 | https://gitlab.com/em-age/emage.code/-/merge_requests/9; https://gitlab.com/em-age/emage.code/-/pipelines/2548093416; docs/tasks/task-T030.md |
| T031 | Audit v3 documentation gaps | technical-writer | 2026-05-23 | docs/artifacts/artifact-v2-v3-doc-gap-audit-v1.md; docs/tasks/task-T031.md |
| T032 | Update root docs for v3 usage | technical-writer | 2026-05-23 | README.md; CONTRIBUTING.md; docs/tasks/task-T032.md |
| T033 | Create and refresh v3 wiki pages | technical-writer | 2026-05-23 | docs/wiki/README.md; docs/wiki/home.md; docs/wiki/quick-start.md; docs/wiki/agents-overview.md; docs/wiki/v3-implementation.md; docs/tasks/task-T033.md |
| T034 | Fix v3 command accuracy | backend-developer | 2026-05-23 | v3/implementation/README.md; v3/implementation/scripts/verify-v3.mjs; docs/tasks/task-T034.md |
| T035 | Extend release docs verification | devops-engineer | 2026-05-23 | scripts/verify-release-docs.py; docs/tasks/task-T035.md |
| T036 | Run docs and v3 validation | qa-engineer | 2026-05-23 | docs/artifacts/artifact-v2-v3-doc-validation-report-v1.md; docs/tasks/task-T036.md |
