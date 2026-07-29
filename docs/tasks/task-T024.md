**Status:** done
**Completed:** 2026-05-23
# Task T024 — Release documentation gate and v1.0.1 docs refresh

## Objective
Ensure release documentation is explicitly updated before cutting a tag by introducing a CI release-doc gate, and refresh README/wiki release markers for the next release.

## Inputs
- existing release CI workflow in `.gitlab-ci.yml`
- release workflow conventions in `CONTRIBUTING.md`
- wiki source pages under `docs/wiki/`

## Expected outputs
- CI job enforcing docs marker for release tags
- updated release marker in `README.md`, `docs/wiki/README.md`, and `docs/wiki/home.md`
- contribution guide update describing the new release-doc gate

## Acceptance criteria
- Tag release pipeline fails if required docs do not contain `Latest release: vX.Y.Z` matching tag.
- Tag release pipeline passes with updated docs marker.
- New release can be cut after gate passes.

## Blocker protocol
If blocked, report blocker type and severity with one proposed mitigation.
