# Failure pattern: invariant violation in a generated artifact (Terminal-Bench)

**Scheme:** `docs/artifacts/failure-taxonomy-v1.md` §8 (T409 extension)
**Source:** Harbor/Terminal-Bench trajectories (local k=3 run, `tb-delta-20260814T111217Z`).
**Task type:** genuine task-level failure (`exception_info: null`, `reward == 0.0`).

## Axis classification

| Axis | Value | Status |
|---|---|---|
| `cause` | `agent-incorrect-domain-computation` | **new** (same value as `incorrect-computed-output-value.md` — see below) |
| `behavior` | `value-violates-invariant` | **reused from `failure-taxonomy-v1.md` §3.2, unchanged** |
| `mechanism` | `cross-field-invariant-violation` | **reused from `failure-taxonomy-v1.md` §3.3, unchanged** |

## Why this reuses two of three axis values

This is a real, concrete demonstration that the golden-suite `behavior`/`mechanism` values were
genuinely defined at the "observable output shape" level (per `failure-taxonomy-v1.md` §7's own
framing) rather than being golden-suite-specific: all fields required by the task are present and
individually well-formed, but their **combined values contradict an explicitly declared
cross-field/ordering rule** the task states — exactly the existing definition of
`value-violates-invariant` (behavior) / `cross-field-invariant-violation` (mechanism), word for
word, no redefinition needed.

The `cause`, however, does **not** reuse the existing golden-suite value
`rule-violation-no-exception-clause` that also maps to a form of "invariant" failure. That golden
value specifically describes a *hand-authored scenario exploiting a missing exception clause in an
otherwise-unconditional rule* — a document-contract gap. These Terminal-Bench cases are not about
missing exception clauses in a rule's text; they are the agent's own generated
artifact/computation failing to satisfy a constraint it was fully capable of understanding and
was directly responsible for satisfying (protein fragment ordering, primer clamp length, permitted
word substitutions). The root cause is the same `agent-incorrect-domain-computation` value used in
`incorrect-computed-output-value.md` — this pattern file is proof that `cause` and
`behavior`/`mechanism` vary independently, exactly as `failure-taxonomy-v1.md` §3.3 already notes
for the golden suite ("`mechanism` is not a re-labeling of `behavior`").

## Real cases (local k=3 run, `tb-delta-20260814T111217Z`)

| Task | Trial (arm/hash) | Declared invariant | What was produced |
|---|---|---|---|
| `protein-assembly` | arm-A `Tig8CE2`, arm-A `wCkatgD`, arm-B `3NRPGSG`, arm-B `QFzq7LY`, arm-B `hTuU7Rx` | Fusion protein must place `flag`, `donor`, `dhfr`, `acceptor`, `snap` segments in strict order (`flag_idx < donor_idx < dhfr_idx < acceptor_idx < snap_idx`). | `flag_idx == donor_idx == -1` (segments not found in the produced sequence in the required order) — ordering invariant violated. |
| `dna-assembly` | arm-A `Lb7fM6W`, arm-A `uo3VD6D`, arm-B `CC7W7F5`, arm-B `PKn6Py9`, arm-B `vJdpYsM` | Each primer's BsaI recognition site (`ggtctc`) must have a clamp of **at least 1 nucleotide** before it (`i >= 1`). | Clamp length `0` — `assert 0 >= 1` fails; the primer is present and the BsaI site is found, but the clamp constraint is violated. |
| `overfull-hbox` | arm-A `bMhyHd7`, arm-A `yxxUwbo`, arm-B `HJexUPp`, arm-B `iapS6Wk` | The agent's modified `input.tex` may only substitute words listed in `synonyms.txt`; all other tokens must match the original `input.tex` verbatim. | `test_input_file_matches` fails — the agent's edits went beyond the declared synonym-substitution constraint (other passing checks confirm the LaTeX compiles and no longer overfull-hboxes; only the substitution-scope invariant is violated). |

14 distinct trials across 3 task names, all `exception_info: null`, all `reward: 0.0`.

## Representative verbatim evidence (`protein-assembly`, arm-A trial `Tig8CE2`)

```
>       assert flag_idx < donor_idx < dhfr_idx < acceptor_idx < snap_idx, (
            "Fusion protein must be in the order flag - donor - dhfr - acceptor - snap"
        )
E       AssertionError: Fusion protein must be in the order flag - donor - dhfr - acceptor - snap
E       assert -1 < -1
```

Source: `tb-delta-20260814T111217Z-arm-A/protein-assembly__Tig8CE2/verifier/test-stdout.txt`
(local worktree `t407-tb-delta`, T407's original k=3 run).
