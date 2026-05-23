# Documentation Audit v1 (2026-05-23)

## Scope
- `README.md`
- `CONTRIBUTING.md`
- `docs/wiki/README.md`
- `docs/wiki/home.md`
- `docs/wiki/quick-start.md`
- `.gitlab-ci.yml` (release docs gate)

## Findings

| ID | Area | Severity | Finding | Remediation |
|----|------|----------|---------|-------------|
| D001 | Release gate | High | `release-docs-gate` only validates a release marker string in three files. It does not verify broader documentation integrity (required docs present, key sections present, internal links valid). | Add a dedicated docs verification script and run it as the release docs gate. |
| D002 | Wiki source README | Medium | `docs/wiki/README.md` has malformed structure around step list and sync section heading, reducing readability. | Rewrite wiki source README with clear update flow, release marker contract, and validation commands. |
| D003 | User onboarding clarity | Medium | Root README quick start is concise but lacks an explicit lifecycle path from setup through release gate behavior. | Add a practical usage flow section and docs verification contract section. |
| D004 | Contributor release guidance | Medium | CONTRIBUTING documents marker checks, but not a deterministic local content verification command that mirrors release CI. | Document and require local run of a docs verification script before tagging. |
| D005 | Wiki/repo consistency policy | Medium | Wiki pages do not clearly state how repo docs and wiki sources are kept aligned at release time. | Add release-doc alignment notes to wiki README/home/quick-start. |

## Coverage map

| User need | Current docs coverage | Gap |
|-----------|-----------------------|-----|
| Install/copy emage.code into project | `README.md`, `docs/wiki/quick-start.md` | Improve explicit path from setup to first run and validation |
| Configure MCP credentials | `README.md`, `docs/wiki/quick-start.md` | Adequate |
| Invoke orchestrator workflow | `README.md`, `docs/wiki/quick-start.md` | Adequate |
| Contribute changes safely | `CONTRIBUTING.md` | Add docs verification command |
| Release with documentation gate | `CONTRIBUTING.md`, `.gitlab-ci.yml` | Add stronger content verification gate |

## Recommended changes (T026-T028)
1. Update `README.md` with a concise "Use emage.code in practice" flow and "Documentation release contract" section.
2. Update `CONTRIBUTING.md` release checklist to include local docs verification command.
3. Rewrite `docs/wiki/README.md` and adjust `docs/wiki/home.md` and `docs/wiki/quick-start.md` for consistency.
4. Add `scripts/verify-release-docs.py` and wire it into `release-docs-gate` in `.gitlab-ci.yml`.
