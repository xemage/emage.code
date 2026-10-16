# Checkpoint 021 — feature-audit-log-export (Phase 3: Track & Validate)

> Written after `/new-feature`'s Phase 2 implementation completed, per `AGENTS.md`
> § Checkpoint Protocol. Hand-authored golden fixture; the tasks, MR and numbers below are
> synthetic.

## Completed tasks (this checkpoint)

| ID | Title | Owner | Outcome |
|----|-------|-------|---------|
| T501 | Audit-log export schema | backend-developer | Done — `docs/artifacts/audit-log-export-v1.md` |
| T502 | Export endpoint + rate limit | backend-developer | Done — endpoint ships behind the existing auth middleware |
| T503 | Export UI entry point | frontend-developer | Done — download action wired to T502's endpoint |

## Key decisions

- **NDJSON, not CSV, as the export format.** Audit records carry nested actor/context objects that
  a flat CSV would have to either drop or stringify; NDJSON streams row-by-row without buffering
  the whole export in memory.
- **Export is asynchronous.** A synchronous export of a year of records exceeded the gateway
  timeout in the Phase 2 spike, so the endpoint enqueues a job and returns a job id.

## Blockers

None active. The Phase 2 gateway-timeout finding was resolved by the asynchronous-export decision
above rather than carried forward.

## Token metrics

| Phase | Budget | Spent | % |
|-------|--------|-------|---|
| Implementation | 120k | ~94k | ~78% |

## Next steps

- Open the merge request from `feature/audit-log-export` to `develop` and request review.
- Produce the retention-policy artifact the export's 90-day window assumes.
