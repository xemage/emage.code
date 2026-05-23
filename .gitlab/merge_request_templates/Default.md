## Summary
<!-- One paragraph: what does this MR change and why? -->

Closes #<!-- issue id -->

## Type of change
<!-- Pick one. The MR title should already follow Conventional Commits. -->
- [ ] `feat` — new capability
- [ ] `fix` — bug fix
- [ ] `docs` — documentation only
- [ ] `refactor` — restructuring without behaviour change
- [ ] `test` — adding / fixing tests
- [ ] `ci` — CI configuration
- [ ] `chore` — tooling / deps / config
- [ ] `perf` — performance
- [ ] `revert` — revert a previous commit

## Changes
- …
- …

## How to verify
1. …
2. …

## Checklist
- [ ] Branched from `develop`
- [ ] Branch name follows `feature/<issue-id>-<slug>` (or `bugfix/`, `hotfix/`, `release/`)
- [ ] Commits follow [Conventional Commits](https://www.conventionalcommits.org/)
- [ ] Edits made **only** under `v2/implementation/knowledge/` (not generated `.github/`, `.gemini/`, `.opencode/`, `.cursor/`)
- [ ] Ran `cd v2/implementation && node scripts/sync.mjs` and committed the result
- [ ] No secrets, tokens, or PII in the diff
- [ ] Markdown links resolve (`lint` job is informational; check locally if you added wiki/doc links)
- [ ] Documentation updated (`README.md`, `CONTRIBUTING.md`, `docs/wiki/`, ADRs as appropriate)

## Screenshots / logs (optional)
<!-- For UI changes or non-trivial output. -->

## Notes for reviewer
<!-- Anything they should focus on; areas of uncertainty; performance considerations. -->

/assign me
/label ~"needs-review"
