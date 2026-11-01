# Artifact: security-review-t665-token-handling-v3.md

> Immutable once produced; revisions bump `<N>`. Continues `security-review-t665-token-handling-v2.md`, which stays unchanged.

## Metadata

- **Kind**: an erratum to the record v2, not a new review. Written by the orchestrator for SEC-T701-01 (`docs/artifacts/security-review-t701-t703-wave1-v1.md`), task T714 (plan-125).
- **Date**: 2026-11-01.
- **Based on**: `docs/artifacts/security-review-t665-token-handling-v2.md` (line 23, the "Default placement" row); `docs/artifacts/security-review-t689-token-placement-v1.md` (SEC-T689-02); `docs/artifacts/security-review-t701-t703-wave1-v1.md` (SEC-T701-01); `docs/wiki/mcp-servers.md` (the token-file lifetime, as corrected by T701).

## Correction

v2, "Default placement" row, says of the in-memory token file: "the file disappears at logout or reboot". That is not exact, and the limits list omits hibernation:

- Under systemd, `$XDG_RUNTIME_DIR` is removed when the user's last session ends, unless lingering is enabled for the user.
- A file under `/dev/shm` survives a logout and disappears at a reboot; systemd-logind with `RemoveIPC=yes` may remove it at the last logout **(unverified)**.
- The token in tmpfs can be written to swap, and a hibernation image (written to swap) holds it too, unless swap is encrypted.

Read v2's row with these qualifiers. Nothing else in v2 changes; the disposition of SEC-T665-03 (closed by T689) stands.
