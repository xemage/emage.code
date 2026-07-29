# Task T282 — Repair the misplaced conventional-commit warning block (T266 regression)

**ID:** T282
**Owner:** qa-engineer
**Status:** done
**Priority:** P0
**Depends on:** T267 (done)
**Created:** 2026-07-29
**Based on:** regression introduced by commit `b07ac9a` (T266)

## STOP-RULES (read before touching anything)
- **R2** This task touches **EXACTLY ONE FILE**: `tests/performance/test_team_health.py`
- **R4** Move the named block. Do **not** delete it. Do **not** rewrite it.
- **R5** If either FIND text below is not present byte-for-byte, STOP and report
  `PRECONDITION FAILED: T282`.
- **R6** Do NOT run `make sync`. Do NOT run `git push`.
- **R7** Commit message, exactly: `fix(tests): T282 restore misplaced conventional-commit warning block`
- **Order matters.** Do STEP 1 before STEP 2. If you do STEP 2 first, the FIND text
  in STEP 1 will match in two places and you will corrupt the file.

## Why this matters (do not skip)
Commit `b07ac9a` inserted class `TestShippedTaskValidator` **in the middle of**
`TestConventionalCommits.test_recent_commit_format`. The tail of that method — the
below-threshold warning block — was left behind and is now sitting at the end of
`test_shipped_validator_passes`, where the names `ratio`, `threshold`, `subjects`
and the attribute `self.CC_RE` do not exist.

This causes **two** defects:

1. `TestShippedTaskValidator.test_shipped_validator_passes` raises `NameError` as soon
   as its `assertEqual` starts passing. It is masked today only because the ledger
   still has violations, so `assertEqual` raises first. **Wave 6 will unmask it and
   break the FINAL GATE (T275).**
2. `TestConventionalCommits.test_recent_commit_format` silently lost its warning
   output — it no longer lists non-conforming commit subjects.

The fix is to move the block back where it came from. Nothing is rewritten.

## STEP 1 — DELETE the block from `TestShippedTaskValidator`

FIND this exact text (it currently appears **once**, at the end of
`test_shipped_validator_passes`):

```python
        )
        if ratio < threshold:
            print(
                f"[warning] ratio {ratio:.0%} is below threshold {threshold:.0%}. "
                "Recent non-conforming subjects:"
            )
            for s in subjects:
                if not self.CC_RE.match(s):
                    print(f"  - {s}")
        # informational only — do not fail
```

REPLACE it with exactly:

```python
        )
```

## STEP 2 — INSERT the block back into `TestConventionalCommits`

FIND this exact text (it appears **once**, at the end of `test_recent_commit_format`):

```python
        print(
            f"\n[conventional-commit-ratio] {matches}/{len(subjects)} "
            f"({ratio:.0%}) of last {len(subjects)} commits follow the format"
        )
```

REPLACE it with exactly:

```python
        print(
            f"\n[conventional-commit-ratio] {matches}/{len(subjects)} "
            f"({ratio:.0%}) of last {len(subjects)} commits follow the format"
        )
        if ratio < threshold:
            print(
                f"[warning] ratio {ratio:.0%} is below threshold {threshold:.0%}. "
                "Recent non-conforming subjects:"
            )
            for s in subjects:
                if not self.CC_RE.match(s):
                    print(f"  - {s}")
        # informational only — do not fail
```

Note: the comment uses an em dash (`—`), not a hyphen. Copy it verbatim.

## Expected outputs
- `tests/performance/test_team_health.py` modified.
- Total line count unchanged (9 lines removed, 9 lines added).
- Nothing else changed.

## Acceptance criteria

1. The block exists exactly once and the leak is gone. Verify command:
   ```bash
   grep -c "        if ratio < threshold:" tests/performance/test_team_health.py
   ```
   Expected output: `1`

2. No undefined names leak into the validator class. Verify command:
   ```bash
   python3 - <<'PY'
   import ast
   tree = ast.parse(open('tests/performance/test_team_health.py').read())
   for node in tree.body:
       if isinstance(node, ast.ClassDef) and node.name == 'TestShippedTaskValidator':
           names = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
           bad = sorted(names & {'ratio', 'threshold', 'subjects'})
           print("LEAK:", bad if bad else "NONE")
   PY
   ```
   Expected output: `LEAK: NONE`

3. `TestConventionalCommits` is byte-identical to its pre-T266 form. Verify command:
   ```bash
   diff \
     <(git show b07ac9a~1:tests/performance/test_team_health.py | sed -n '/^class TestConventionalCommits/,/^class /p') \
     <(sed -n '/^class TestConventionalCommits/,/^class /p' tests/performance/test_team_health.py) \
     && echo IDENTICAL
   ```
   Expected output: `IDENTICAL`

4. Verify command:
   ```bash
   python3 -m py_compile tests/performance/test_team_health.py && echo OK
   ```
   Expected output: `OK`

5. Verify command:
   ```bash
   wc -l < tests/performance/test_team_health.py
   ```
   Expected output: `271`

6. Verify command:
   ```bash
   python3 tests/run.py --suite performance -v
   ```
   Expected: no test that was passing before this edit now fails.
   `TestShippedTaskValidator.test_shipped_validator_passes` and
   `TestPlanCoverage.test_every_active_task_has_a_plan` may still fail — that is
   expected until Wave 6 and T283 respectively.

7. `git status --porcelain` lists exactly one modified file.

## Revert rule
If any acceptance criterion fails:
```bash
git checkout -- tests/performance/test_team_health.py
```
then STOP and report. **Warning:** this also reverts T266 and T267. Report that fact.

## Blocker protocol
Report blockers as: type (`technical` | `dependency` | `unclear_requirements` | `external`)
+ severity (`critical` | `major` | `minor`) + one proposed mitigation. Max 2 retries.
