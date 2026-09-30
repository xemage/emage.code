# T548 — Widen the skillify golden case's checker to the amended output-path contract

**ID:** T548
**Owner:** QA Engineer
**Status:** pending
**Priority:** P2
**Tier:** mechanical
**Affects:** command/skillify
**Depends on:** T530, T532, T549
**Created:** 2026-09-26
**Based on:** `docs/artifacts/skillify-output-path-resolution-v1.md` §7;
`docs/tasks/task-T532.md`; `docs/tasks/task-T530.md`;
`docs/artifacts/protected-paths-v1.md` §5.2.

## 1. Why this exists

T532 amended `/skillify`'s output-path contract from a single hardcoded `.github/skills/<name>/SKILL.md`
to a two-row rule with a precondition. `tests/golden/open/skillify-skill-file-template-drift/expect.py`
quotes the **old** clause in its module docstring, and `brief.md`'s `## What this checks` /
`## Pass condition` quote it too. The checker's *assertions* are unaffected — it reads the fixture, not
the command — but its stated contract is now path-stale.

**ADR-007's sibling-fate corollary applies literally here for the first time in the series:** branch 1,
amendment changes only a path → the case **survives**, fixture/glob updated. T527 changed labels and
T535 arguably changed an artifact class; this one is unambiguous.

## 2. PROTECTED PATH AUTHORIZATION

`docs/artifacts/protected-paths-v1.md` §5.2 requires a named authorizing task. **This task, T548, is
that task**, for exactly these paths:

- `tests/golden/open/skillify-skill-file-template-drift/expect.py`
- `tests/golden/open/skillify-skill-file-template-drift/brief.md`
- `tests/golden/open/consolidate-memory-recommendation-table-grounded/brief.md` — **added
  2026-09-30 by the orchestrator, before dispatch**; see §2.1

**Not authorized:** any `case.yaml`, any `fixture/`, the consolidate-memory case's `expect.py`,
`scripts/scorecard.py`, any other case, and the evaluator-hash baseline. **§5.1 forbids you extending your own grant** — six prior tasks hit this
boundary and all six refused. Do the same: if you conclude another path must change, **report it and
stop.**

### 2.1 Why the consolidate-memory brief is folded in here (amended 2026-09-30)

T549 (MR !419, merged) rewrote `/consolidate-memory`'s step-2 Promote line. The case
`consolidate-memory-recommendation-table-grounded` has a `brief.md` whose **line 17 quotes the old
line verbatim**: *"should be elevated to `AGENTS.md`, project docs, or skill files"* — the destructive
targets T549 removed. So the case's stated contract is now stale prose.

**Its `expect.py` is not affected** and is **not** in your grant. The orchestrator read it: it quotes
only step 1, step 2's *header* ("assign one of: Keep / Promote / Prune") and step 3's four columns, and
`check()` reads only the fixture. It returns `True` today and **must still return `True`** after your
change. Run it and report the result.

Correct `brief.md` against the command **as it is in `develop` now** — read
`implementation/knowledge/commands/consolidate-memory.md` first, do not work from this quote. Keep any
history that matters, reframed rather than erased, as T530 did.

**Why fold it here rather than open a task:** every authorized change under `tests/golden/**` drifts
the evaluator-hash digest, and each drift needs an explicit human authorization for a new baseline.
Doing both cases in one task costs **one** baseline refresh instead of two.

## 3. Sequencing — read this before you start

**`brief.md` for this case was rewritten by T530 (MR !412) and the command was amended by T532
(MR !413).** Both must be **merged into `develop`** before you branch, or you will conflict with T530
on the same file and describe a contract T532 has not landed.

**Verify both are in `develop` yourself** (`git log develop --oneline | grep -E 'T530|T532'`) and
report a `dependency` blocker if either is missing. Do not proceed on the assumption that they merged.

## 4. The change

### 4.1 `expect.py`

| Element | Change |
|---|---|
| Module docstring's quoted clause | Update to the amended two-row rule. **State explicitly which row the fixture exercises.** |
| The fixture-discovery path expression | Widen to the declared set — see §4.2, and **say which option you chose in the docstring** |
| `REQUIRED_SECTIONS`, `TITLE_RE`, the `all(section in text …)` operator, `main()` | **Byte-identical.** No section name or operator changes. |
| An "exists in all seven folders" assertion | **Do not add one.** That is the counter-reading's territory and the fixture carries one folder. Explicitly out of scope. |

The current values, read from the live file by the orchestrator so you are not working from a
second-hand table: `REQUIRED_SECTIONS = ("## When to Use", "## Inputs", "## Procedure",
"## Success Criteria", "## Examples")`; `TITLE_RE = re.compile(r"^#\s+\S.*$", re.MULTILINE)`;
fixture root `case_dir / "fixture" / ".github" / "skills"`; guards `is_dir()` and
`len(candidates) != 1`. **Confirm these against the file rather than trusting this brief** — T530 and
T532 both landed since it was written.

### 4.2 Pick one option and justify it

- **(i) Widen the search** to `implementation/knowledge/skills/` **and** all seven
  `<platform>/skills/`, **keeping** the `is_dir()` and `len(candidates) != 1` guards so exactly one
  candidate must resolve across the whole set. This is **stricter** than today: a wider search under
  the same uniqueness guard admits fewer inputs, not more.
- **(ii) Relocate the fixture** to `fixture/implementation/knowledge/skills/<name>/SKILL.md` and point
  at the authoring row — the row `AGENTS.md` makes authoritative. Unchanged in count, narrower in scope.

**Option (ii) requires moving a file under `fixture/`, which §2 does not authorize.** If you prefer
(ii), **report it as a blocker** and ask for the grant. Do not take it silently.

**ADR-007 §5 forbids resolving this by relaxing the check.** Whichever you pick, state in your report
why the result is not weaker than what it replaces.

### 4.3 `case.yaml` — deliberately excluded

`known_failing_reason` must **not** gain a path mention. This case is a plain branch-3b standing red
(the corpus satisfies the template 0/26) and the output path was **never** its failure cause.
Conflating the two would misdescribe the defect. T530 already corrected two false statements in this
file; do not add a third.

## 5. Expected outcome — state it before you run it, then report what happened

`check()` **must still return `False`.** Under option (i) the fixture's `.github/skills/` entry is
still in the widened set; under option (ii) the fixture moves with the search. The case stays
`known_failing` / `tracked_defect`, `/skillify` stays `maturity: experimental`, and
`check-maturity.py` is unmoved.

**Run `check()` and report the observed exit status.** A `True` here means something is wrong with the
change, not that `/skillify` got better.

## 6. The evaluator hash will drift — do not refresh it

Any authorized change under `tests/golden/**` moves `tests_golden` and turns **exactly 2** tests red.
That is tamper evidence working, not a regression.

**You are not authorized to write a new `evaluator-hash-known-good-v<N>.json`.** Refreshing the
baseline requires explicit human authorization, which has been requested and granted nine times and
never self-granted. Hand back with the 2 failures present, name them, and state that the refresh is
pending. **Do not** touch `docs/artifacts/evaluator-hash-known-good-v*.json`.

## 7. Acceptance criteria

1. `expect.py`'s docstring describes the contract that is actually in `develop`, and names the row the
   fixture exercises.
2. The chosen option from §4.2 is implemented and its non-weakening argued.
3. `REQUIRED_SECTIONS`, `TITLE_RE` and the substring operator are byte-identical — show the diff.
4. `brief.md`'s `## What this checks` and `## Pass condition` match the new checker, **preserving
   T530's structure** rather than reverting it.
5. `case.yaml` untouched. `fixture/` untouched unless a grant was requested and given.
6. `check()` reports `False`, observed and stated.
7. The full suite shows **exactly** the 2 evaluator-hash failures and nothing else. **Measure the
   total yourself** — figures quoted in briefs have been wrong five times in this phase.

## 8. Blocker protocol

Report blockers as `technical` | `dependency` | `unclear_requirements` | `external` with severity
`critical` | `major` | `minor`. **If anything in this brief is wrong, report it rather than working
around it** — ten consecutive tasks have found a brief defect, and §4.1's table is second-hand for
`brief.md` because T530 rewrote it after this brief was drafted.
