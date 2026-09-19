# Staged CWSO deployment guides — pending CWSO repo T473

## Why these files are here

These 6 files were relocated out of `docs/deployment/` by task **T403**
(`plan-035-roadmap-v7-ground-up.md`, Phase 0 — Ground Truth), because emage.code is a
knowledge-projection layer, not the CWSO orchestrator, and full CWSO deployment
documentation does not belong in this repository.

`docs/deployment/README.md` was replaced in the same change with a short, usage-only
document (what CWSO is, when to use it from emage.code, how the `cwso` MCP connection is
wired, and a link out to the CWSO repository). It does not contain deployment
instructions.

## Why they are staged instead of deleted

The CWSO repository's own receiving task — **T473** (`plan-035` §2.5, Track C: "Consolidate
deployment + configuration + usage into **one** document tree in the CWSO repo; receive
the 6 guides relocated by T403") — has **not yet been scheduled or executed** in the CWSO
repository. Per the plan's coupling constraint (§2.5, coupling point #1: "Deployment docs
(T403 → T473) ... T403 must not land before T473 is ready to receive them, or the guides
are orphaned"), the content of these 6 guides must not simply be dropped. They are staged
here, verbatim, as a handoff package.

## Contents

The following files were copied **verbatim** (no edits) from their prior location at
`docs/deployment/`:

- `local-docker-desktop-guide.md`
- `gcp-cloud-run-guide.md`
- `proxmox-lxc-guide.md`
- `cwso-overview-and-agent-integration-guide.md`
- `cwso-emage-orchestrator-connection-guide.md`
- `troubleshooting-guide.md`

Because they were moved as-is, internal cross-links between these files (and to the old
`docs/deployment/README.md`) are preserved as originally written and are **not**
guaranteed to resolve from this location — treat this directory as a content handoff
package, not a maintained doc tree.

## What to do with this directory

Once CWSO repo task **T473** lands (consolidating deployment + configuration + usage into
one document tree in the CWSO repository and receiving this content), **this staging
directory should be deleted** from emage.code. Until then, leave it in place.

`docs/archiv/` is excluded from `scripts/check-version-consistency.py` (T400), so the
staged copies will not trip the version-consistency gate despite carrying whatever
version markers they had at relocation time.
