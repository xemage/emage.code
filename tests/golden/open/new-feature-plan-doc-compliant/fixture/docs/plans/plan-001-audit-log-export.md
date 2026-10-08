# Feature Plan: audit-log-export

## Objective
Allow admins to export the audit log as a signed CSV for a given date range, for compliance
handoff to external auditors.

## Affected Components
- `services/audit-log/` (new export endpoint)
- `services/admin-ui/` (new "Export" button + date-range picker)
- `docs/artifacts/` (new versioned export-format spec)

## Task Breakdown
| Task | Owner | Estimate |
|------|-------|----------|
| Design export format + signing scheme | solution-architect | S |
| Implement export endpoint | backend-developer | M |
| Add UI export control | frontend-developer | S |
| Write integration test | qa-engineer | S |

## Dependency Impact
No breaking changes to existing audit-log read APIs. New endpoint is additive. Depends on the
existing audit-log storage schema being stable (no migration required).
