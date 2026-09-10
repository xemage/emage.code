---
description: "Use when writing code in any language. Covers naming conventions, function design, error handling, general clean code principles, and artifact versioning."
applyTo: "**/*.{ts,js,py,java,cs,go,rs,rb,php,swift,kt}"
maturity: experimental
---

# Coding Standards

## Rails
**Inputs**: Triggers on any code file matching this instruction's `applyTo` glob
(`**/*.{ts,js,py,java,cs,go,rs,rb,php,swift,kt}`); also invoked explicitly by
`tech-lead.md`'s Code Standards responsibilities and by `AGENTS.md`'s "Code
Standards" routing table when establishing or reviewing project conventions.

**Out of scope**: Does not mandate a specific linter/formatter or CI enforcement
mechanism — the Tech Lead configures project-specific tooling (Prettier, Black,
`.editorconfig`, etc.) separately, per `tech-lead.md`'s "Code Standards"
responsibilities. Does not cover language-specific idioms beyond the naming,
function-design, error-handling, security, organization, and artifact-versioning
rules stated below.

**Failure mode**: Violations surface during code review as Must Fix/Should Fix
items in the `code-review` skill's checklist; they do not automatically block a
merge unless the Tech Lead's VERDICT marks them Critical. Artifact-versioning
violations specifically (overwriting a prior `<type>-vN.md` file instead of
creating a new version) are treated as a process defect requiring the offending
change to be redone as a new version, not silently patched in place.

## Naming
- **Variables/functions**: camelCase (JS/TS), snake_case (Python), PascalCase (C#)
- **Classes/types**: PascalCase in all languages
- **Constants**: UPPER_SNAKE_CASE
- **Booleans**: prefix with `is`, `has`, `can`, `should`
- **Functions**: verb-first (`getUserById`, `calculateTotal`, `validateInput`)

## Functions
- Single responsibility: one function does one thing
- Max 50 lines per function — extract helpers for longer logic
- Max 4 parameters — use an options/config object for more
- Pure functions preferred: same input → same output, no side effects
- Early returns for guard clauses instead of deep nesting

## Error Handling
- Use typed errors/exceptions, not generic ones
- Handle errors at the appropriate level (not everywhere)
- Never swallow errors silently — log or propagate
- User-facing errors: helpful message without internal details
- Developer errors: include context for debugging

## Security
- Validate all external input (user input, API responses, file reads)
- Use parameterized queries — never string concatenation for queries
- Sanitize output to prevent XSS
- Never commit secrets, tokens, or passwords
- Use environment variables for configuration

## Code Organization
- Group by feature/domain, not by type (prefer `user/` over `controllers/`)
- Co-locate tests with source files or mirror the directory structure
- Keep imports organized: stdlib → external → internal
- Remove unused imports, variables, and dead code

## Artifact Versioning & File Naming

### Versioned Artifact Convention
All plan, decision, and documentation artifacts follow the `<type>-vN.md` naming convention:
- `plan-v1.md`, `plan-v2.md`, `plan-v3.md`
- `decision-v1.md`, `decision-v2.md`
- `checkpoint-v1.md`, `checkpoint-v2.md`

### Rules
- **Never overwrite prior versions.** Always create a new file with an incremented version number.
- Version numbers are sequential integers starting at 1 (`v1`, `v2`, `v3`, ...).
- The latest version is the active/current version. Prior versions are historical record.
- When referencing an artifact, always use the full versioned filename (e.g., `plan-v3.md`, not `plan.md`).

### Artifact Types and Their Prefixes
| Prefix | Location | Purpose |
|--------|----------|---------|
| `plan-vN.md` | `docs/plans/` | Implementation plans |
| `decision-vN.md` | `docs/decisions/` | Architecture/design decisions |
| `checkpoint-vN.md` | `docs/checkpoints/` | Progress checkpoints |
| `artifact-vN.md` | `docs/artifacts/` | General deliverable artifacts |

### Version Increment Triggers
- Any material change to an artifact's content requires a new version
- Typo or formatting fixes do NOT require a new version
- Adding new sections or modifying conclusions DOES require a new version
- When in doubt, create a new version — storage is cheap, history is priceless
