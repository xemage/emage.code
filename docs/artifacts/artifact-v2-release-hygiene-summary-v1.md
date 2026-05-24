# Release Hygiene Summary v1

## Scope
Release preparation for `v2.0.1` after validating the `v2.0.0` publication workflow.

## Fixes Included
- Hardened release publishing on mixed runner environments in `.gitlab-ci.yml`.
- Added `scripts/publish-release.py` for runner-portable, fail-closed release publication.
- Ensured release jobs fail when release creation/update fails.
- Ensured `release-notes.md` and `CHANGELOG.md` are generated consistently by a single Python workflow.

## Root Cause Addressed
The previous release job used shell syntax that failed under PowerShell on a Windows shell runner, but the job still completed successfully and left `v2.0.0` without a release object.

## Verification Evidence
- Release gate validation command succeeds for the target tag.
- Repository test suite passes.
- Branch and MR pipelines for this release cycle are tracked to green before merge.

## Follow-up
- Keep release publication under the fail-closed Python path.
- Continue using release docs markers as hard gate criteria before tag creation.
