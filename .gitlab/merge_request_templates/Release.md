## Release `vX.Y.Z`

> Created from `release/vX.Y.Z` → `main`. The twin MR `release/vX.Y.Z` → `develop` is merged
> first, then this one. After both merge, tag `vX.Y.Z` as `CONTRIBUTING.md` § Releasing, step 7
> describes.

## Release document
- [ ] `docs/releases/vX.Y.Z.md` is on the branch and `python3 scripts/verify-release-docs.py --tag vX.Y.Z` passes
- RELEASE VERDICT Status: <PASS | CONDITIONAL_PASS | FAIL>

Highlights, breaking changes and the changelog live in that document, not in this description.

## Pre-merge checklist
- [ ] All CI checks green on `release/vX.Y.Z`
- [ ] The `develop` MR of this release is merged (merge commit, no squash)
- [ ] `Latest release: vX.Y.Z` is set in every file `scripts/verify-release-docs.py` checks, and `python3 scripts/check-version-consistency.py` passes
- [ ] No `WIP` / `TODO` / `FIXME` introduced by this release
- [ ] Wiki updated if user-facing behaviour changed (`docs/wiki/`)

## Post-merge actions
After this MR merges to `main`, tag the release branch's tip (`CONTRIBUTING.md` § Releasing, step 7).
There is no direct push to `develop`.

The tag push triggers the `release` stage of `.gitlab-ci.yml`, which:
1. Checks the release document, the markers and the `main`/`develop` drift
2. Publishes `docs/releases/vX.Y.Z.md` as the GitLab Release description
3. Regenerates `CHANGELOG.md` as a job artifact (it is not committed)

/label ~"release"
