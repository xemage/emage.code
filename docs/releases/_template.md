# Release vX.Y.Z

Copy this file to `docs/releases/vX.Y.Z.md` before cutting a release tag.
The release CI job embeds this document in GitLab Release notes (highlights +
install). Commit messages since the previous tag are appended as a changelog
section.

## Install

Latest release: vX.Y.Z

**Recommended:** use the installer from a clone of this repository:

```bash
git clone https://gitlab.com/em-age/emage.code.git
cd emage.code
scripts/install.sh --target <your-project> --platform cursor
```

| Platform | `--platform` value |
|----------|-------------------|
| Cursor | `cursor` |
| GitHub Copilot (VS Code) | `github` |
| Gemini CLI | `gemini` |
| Opencode | `opencode` |
| Pi | `pi` |
| All platforms | `all` |

**Manual copy** from `implementation/` (alternative):

```bash
# GitHub Copilot
cp -r implementation/.github         <your-project>/
mkdir -p <your-project>/.vscode
cp    implementation/.vscode/mcp.json <your-project>/.vscode/

# Gemini CLI
cp -r implementation/.gemini         <your-project>/

# Opencode
cp -r implementation/.opencode       <your-project>/

# Cursor
cp -r implementation/.cursor         <your-project>/

# Pi (terminal agent)
cp -r implementation/.pi             <your-project>/.pi/

# Always include
cp    implementation/AGENTS.md       <your-project>/
cp -r implementation/docs            <your-project>/
```

Set MCP env vars from the generated `mcp.json` / platform config, then run
`/new-project "Your idea"` in your assistant.

## Highlights

- Feature one — what users get in this release
- Feature two — …

## Breaking changes

- None (or list breaking changes)
