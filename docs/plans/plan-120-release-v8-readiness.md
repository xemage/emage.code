# plan-120 — Release readiness for the next major release (v8.0.0)

**Created:** 2026-10-09
**Based on:** The user's decisions of 2026-10-09 on the release-readiness question (verbatim): "1. A  2. A  3. A  4. approving baseline v21 - plan re-evaluation and steps to bring them out of experimental  5. C  6 B" (point numbers refer to the orchestrator's message listing six open points: 1 breaking changes and migration notes = release-level audit and Migration section; 2 release-level gates and sign-offs = the full sequence; 3 CI release job's third release-notes.md = fix first; 4 maturity = the user authorizes evaluator baseline v21 and asks for a re-evaluation plan and the steps to bring `orchestrator` and `tech-lead` out of `experimental`; 5 known residuals = fix all first; 6 plumbing = API fallback plan for branch and tag steps).
Last release: v7.0.1 (2026-09-19). `develop` at `007e8fa`: CI green, version consistency PASS, main/develop drift 0, maturity check 79 components with 0 failing, scorecard 34/26/0 (28 open plus 6 held-out cases), full suite 1087 OK, ledger empty, root drift 0.
**Scopes:** `T619`, `T620`, `T621`, `T622`, `T623`.

## 1. Goal

Reach a state from which the release can be prepared and cut: every item the user decided to fix first is fixed, `orchestrator` and
`tech-lead` have a verified path out of `experimental`, the breaking changes are inventoried for the Migration section, and the release-level gates
can run on a stable `develop`.

## 2. Workstreams

| WS | Content | Task(s) | Owner | Notes |
|---|---|---|---|---|
| A | Release-level audit of `v7.0.1..develop`: breaking and behaviour changes, Migration section input | T623 | tech-lead (read-only review, writes one artifact) | Runs now; an addendum covers tasks merged afterwards |
| B | CI release job writes a third root `release-notes.md` although the user decided one document, `docs/releases/v<VERSION>.md` (P32 O6) | T619 | devops-engineer | Cannot be run on a tag beforehand: needs a local dry run |
| C | R-1: aperiodic-input cost residual of the JWT rule | T620 | backend-developer | Then a Security Engineer review |
| D | Remaining rulings: P41 O4, P33 O1/O2/O5/O6, O-8 (`priority::*` to `P0`/`P1`/`P2`, starting from `commands/bug-report.md:54`) | T621 | solution-architect (decision only) | One consolidated user question; implementation task afterwards |
| E | Promotion re-evaluation for `orchestrator` and `tech-lead`, golden realignment inventory (P41 O3, the stale `new-project-plan-doc-and-lifecycle-states` brief quote, the six `known_failing` open cases) and the baseline v21 procedure | T622 | solution-architect (decision/plan only) | The user authorized baseline v21; no golden file is edited before the T622 plan and the user's answers |
| F | Release-level gates and sign-offs: QA gate, Tech Lead review by area, release-level Security Engineer audit, release-manager `RELEASE VERDICT`, user approval | TBD | per gate | After A to E are merged |
| G | Release preparation and cut: release branch, `docs/releases/v8.0.0.md` with Migration section, release checkpoint `checkpoint-038-release-v8.0.0.md`, tag, main merge. API fallback (the GitLab API) for branch and tag steps if `git push` fails; never touch credential configuration without asking | TBD | orchestrator, release-manager | The user approves each outward-facing step (tag, release publication) |

## 3. Sequence and dependencies

1. **Wave 1 (parallel, no file overlap):** T619, T620, T621, T622, T623. The decision-only tasks write one artifact each. T619 touches `scripts/publish-release.py`, `.gitlab-ci.yml` (and their tests); T620 touches `poc_scan.py` and its tests/contract; neither projects to the root except possibly nothing.
2. **Wave 2:** implementation tasks derived from the T621 and T622 decisions (knowledge edits, golden realignment under a file-scoped `protected-paths-v1.md` §5 grant and baseline v21, promotions), each with its review; then one user-approved root refresh.
3. **Wave 3:** the T623 addendum, gates (F), then release preparation (G).

## 4. Constraints

- Golden files (`tests/golden/**`, `scripts/scorecard.py`) change only under a file-scoped grant (`docs/artifacts/protected-paths-v1.md` §5) and a new evaluator baseline `evaluator-hash-known-good-v21.json`, which the user has authorized in principle (quoted above); each grant names its files and is recorded; no held-out case is opened or named.
- Maturity is never relied on to rank a conflict (ADR-008 P4); promotions follow `docs/artifacts/maturity-promotion-criteria-v2.md`.
- Anything outward-facing (push of a release tag, publishing a release, merging to `main`) needs the user's explicit approval at that step.
- Nothing is released in this plan; it ends when G is ready to start.

## 5. Not in scope

Hindsight, CWSO, the `t407-tb-delta` worktree, the user's uncommitted `.claude/settings.json` and `.vscode/mcp.json` (they stay local; the Migration section tells adopters to allow `mcp__poc-security-audit__*`).
