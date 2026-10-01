# plan-087 — Implement the `audience:` key (P5, P6)

**Created:** 2026-10-01
**Based on:** `docs/artifacts/command-audience-resolution-v1.md`; `docs/plans/plan-083-four-decisions-and-batching.md` §4;
`docs/checkpoints/checkpoint-037-phase9-queue-empty-root-refreshed.md` §8.
**Scopes:** `T556`.

## 1. Why now

`plan-083` P5's trigger — "a round with no open `implementation/knowledge/` task" — fired when the queue
emptied (checkpoint-037). The change touches all 19 commands, so it must run alone in the knowledge group.

## 2. Smaller than T546 costed

T546 §5.1 counted the schema edit, 19 frontmatter lines, and **6 body edits**. The six body edits have since
landed through T532 (`/skillify`), T549 (`/consolidate-memory`), T553 (`/handoff`, via the installer) and T554
(`/discover-skills`). What remains is mechanical: one schema change plus 19 one-line additions, in one atomic
commit. `audience` is source-only, so **no projection moves and the repo-root drift list stays empty**; only
the 19 registry checksums change. **P6** (`/prepare-release` → `authoring`) is folded in, because assigning all
19 values decides it.

## 3. Parked — the payoff

| # | Item | Trigger |
|---|---|---|
| P23 | **A lint that uses `audience:`**: flag any command declared `both` (or `target`) whose text names a path that installed targets never receive (`implementation/registry/`, `implementation/knowledge/`, `implementation/scripts/`, …). This is what would have caught, mechanically, the four hard leaks this phase found by hand (`/consolidate-memory`, `/discover-skills`, `/handoff`, `/skillify`). | `T556` merged |
| P22 | `/discover-skills` step 6 merges "pack registry entries" no pack format contains — a no-op in both audiences (T554 hand-back; first listed in checkpoint-037 §6) | any `/discover-skills` or packaging task — or fold into P23's first run, which will read every command |

## Erratum (2026-10-01)

§2 said T546's six body edits had all landed through T532, T549, T553 and T554. **That was wrong:** those four
tasks fixed four commands. The fifth (`/prepare-release`) needed only its `audience: authoring` declaration, which
T556 made. The sixth, **`/batch`'s class-C reference to `commands/plan.md`, never landed** — the T557 lint found it
on its first run. It is now `T558` (`plan-088` §2).
