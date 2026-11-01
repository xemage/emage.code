# Artifact: release-doc-independent-check-v9-v1.md

> Immutable once produced; revisions bump `<N>`.

## Metadata

- **Checker**: the top-level session (orchestrator), under `release-manager.md` § Release Gate Policy item 5 ("Independent check of what you authored"). The release manager authored `docs/releases/v9.0.0.md` (T705) and applied the gate findings (T710 step 1); the gate verdicts come from T707, T708 and T709.
- **Date**: 2026-11-01.
- **Covers**: `docs/releases/v9.0.0.md` and `CHANGELOG.md` at commit `a47d982d` (T710 step 1), merged into `release/v9.0.0` as `17b017f6`. After this check only the `## RELEASE VERDICT` section and the `Release:` line under `## Gate Verdicts` may change (Policy item 5); any other change to the document needs a new check.
- **Based on**: `docs/artifacts/qa-gate-release-v9-v1.md` (T707), `code-review-release-v9-v1.md` (T708), `security-review-release-v9-v1.md` (T709), `release-rehearsal-t706-v1.md` (T706), `release-v9-audit-v1.md` (T700); the T705 version `efc67ab6`, which the orchestrator had already read in full for the Cursor item before merging it.

## Verdict: PASS

## What was checked

1. **Gate script.** `python3 scripts/verify-release-docs.py --tag v9.0.0`: 11 messages, all placeholders of the `Release:` line (2) and the `## RELEASE VERDICT` section (9); no other error, including the T703 migration-pointer check. `python3 scripts/check-version-consistency.py`: PASS (v9.0.0).
2. **Links and content hygiene.** Every relative link of the document resolves in the tree; no token, JWT, GitLab token prefix or private network address in the document (pattern scan, counts only).
3. **Every change since `efc67ab6`** (23 insertions, 20 deletions in the two files), read word by word against the gate findings:
   - M-1 (SEC-T709-04, TL-T708-03): the replacement `filesystem` launcher is no longer recommended (remove, do not replace; K-17, unrestricted Cursor agents, frozen copy); the removal of the `@anthropic/mcp-filesystem` entry, on which the SEC-T662-01 closure rests, is unchanged; the two `--force-prune-keys` runs are described separately (`merge-mcp-json.py:457-471, 526-529`).
   - M-4 (QA-T707-02, SEC-T709-03): the `${env:X}` change applies to generated entries; user entries are kept unconverted; the file variable is preferred; the at-rest warning is present.
   - M-5 and K-24 (SEC-T709-01, SEC-T709-02): environment mode stays supported, not acceptable on an unencrypted disk (Constraint 6), D-11 stated as ruled; the caveat for lifting `GITLAB_PERMISSION_MODE` names the clients whose tool lists do not restrict MCP tools.
   - K-10 (T706 O-1, D-T710-2): the `[Unreleased]` text corrected in `CHANGELOG.md`; the entry order in the job artifact recorded as tracked for a later release.
   - K-21 and the Rollback Plan (TL-T708-02): the GitLab keys stay after a rollback (deep merge), observed on Claude Code, other platforms marked unverified; the `github` return, the loss of `--transport stdio` and the Copilot servers' removal marked observed where the T708 simulation observed them.
   - `## Gate Verdicts`: the Architecture, Implementation, Integration and Security rows match the verdicts and conditions of T708, T707 and T709 and the v8.0.0 mapping; the rows name the commits the reviews covered (`ca11bb6e`) and the later commits (gate artifacts, ledger, T710).
4. **SEC-T662-01 elements** in M-1 (from the T709 hand check, lines 72 to 92): still present after the T710 edit.

## Not checked

- The technical claims marked (unverified) in the document (they are disclosed there).
- The document's claims about live client behaviour and the tag pipeline (T711 observes the pipeline).
