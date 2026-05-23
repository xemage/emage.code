# v2/v3 Documentation Gap Audit v1

## Scope
- Root documentation: `README.md`, `CONTRIBUTING.md`
- Wiki sources: `docs/wiki/*.md`
- v3 implementation documentation: `v3/implementation/README.md`
- v3 entry scripts: `v3/implementation/scripts/verify-v3.mjs`, `v3/implementation/scripts/check-v3.py`

## Findings

| ID | Severity | Finding | Evidence | Remediation |
|----|----------|---------|----------|-------------|
| G001 | High | v3 is operational but not discoverable from the root README in a way that explains when to use it and how it differs from v2. | Root README currently focuses on v2 and release history, with no v3 usage section. | Add a concise v3 overview and entry path in the root README. |
| G002 | High | The wiki source set has no v3-specific page, so the live wiki does not explain v3 usage or migration context. | `docs/wiki/` contains no `v3-*.md` page. | Add a wiki page for v3 overview/usage and link it from home. |
| G003 | Medium | The v3 runbook documents a drift-check command that is not valid from the stated working directory. | `v3/implementation/README.md` currently shows `node v3/implementation/scripts/verify-v3.mjs --root ../../v2/implementation`, but that path does not resolve as documented. | Fix either the command example or the script path resolution so the documented invocation works. |
| G004 | Medium | Release docs verification currently validates v1/v2 release markers only. | Release gate checks `README.md`, `docs/wiki/README.md`, and `docs/wiki/home.md` only. | Extend release verification to cover v3-critical docs and content checks. |
| G005 | Medium | CONTRIBUTING lacks a clear v3 usage/validation section. | The current release section covers v1/v2 docs gate behavior but not v3 validation commands. | Update contributor guidance with the correct v3 validation workflow and release expectations. |

## Readiness verdict
- v3 implementation gates pass, so the runtime is functionally workable.
- Documentation is not yet sufficient for first-time users of v3.
- Proceed with docs alignment and command-path correction before calling v3 fully ready-to-use.

## Recommended execution order
1. Update root docs and CONTRIBUTING for v3 discovery and validation.
2. Add a v3 wiki page and link it from the wiki home page.
3. Correct the v3 verify command behavior or document the correct invocation.
4. Extend release docs verification to include v3-critical docs.
5. Re-run docs and v3 validation checks, then push and monitor CI.
