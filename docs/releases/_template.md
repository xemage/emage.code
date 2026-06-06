# Release vX.Y.Z

Copy this file to `docs/releases/vX.Y.Z.md` before cutting a release tag.
The release CI job embeds this document in GitLab Release notes (highlights +
install). Commit messages since the previous tag are appended as a changelog
section.

## Install

Latest release: vX.Y.Z

Pick your platform and copy from `v3/implementation/`:

```bash
# GitHub Copilot
cp -r v3/implementation/.github         <your-project>/
mkdir -p <your-project>/.vscode
cp    v3/implementation/.vscode/mcp.json <your-project>/.vscode/

# Gemini CLI
cp -r v3/implementation/.gemini         <your-project>/

# Opencode
cp -r v3/implementation/.opencode       <your-project>/

# Cursor
cp -r v3/implementation/.cursor         <your-project>/

# Pi (terminal agent)
cp -r v3/implementation/.pi             <your-project>/.pi/

# Always include
cp    v3/implementation/AGENTS.md       <your-project>/
cp -r v3/implementation/docs            <your-project>/
```

Set MCP env vars from the generated `mcp.json` / platform config, then run
`/new-project "Your idea"` in your assistant.

## Highlights

- Feature one — what users get in this release
- Feature two — …

## Breaking changes

- None (or list breaking changes)
