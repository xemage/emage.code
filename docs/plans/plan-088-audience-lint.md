# plan-088 — The audience lint (P23)

**Created:** 2026-10-01
**Based on:** `docs/plans/plan-087-audience-key.md` §3; MR !435 (T556).
**Scopes:** `T557`.

T556 made every command declare its audience. `plan-087` P23's trigger ("T556 merged") has fired. `T557` makes
the declaration checked: a command declared `both` or `target` must not name a path that exists in this
repository but not in a fresh install. It reuses T543's design — the installer as the oracle, a declared baseline
that fails in both directions — so no hand-maintained list of "authoring-only paths" can drift. P22 (the
`/discover-skills` step 6 no-op) is surfaced by the lint's first run and declared, not silently fixed.
