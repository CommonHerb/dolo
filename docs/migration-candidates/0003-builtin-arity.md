# Migration Candidate 0003: Built-In Arity

## Purpose

This Herbert-family migration candidate mirrors Dolo's current Python-owned
table of observed Herbert built-in arities. It does not replace the Python
bootstrap compiler yet. It isolates the boundary Dolo uses before emission:
known built-in names map to observed argument counts, while unknown names stay
outside the accepted built-in surface.

Current Python behavior lives in `src/dolo/herbert_surface.py` as
`HERBERT_BUILTIN_ARITIES`, and the emitter uses that table when validating
value-level and no-value built-in calls.

## Executable Candidate

`experiments/herbert/builtin_arity_candidate.herb` implements a tiny arity
lookup for the observed built-ins Dolo can emit today:

- `new_buffer -> 0`
- `count`, `freeze`, `length`, `new_array -> 1`
- `add`, `append`, `equal`, `get`, `index -> 2`
- unknown name -> `999`

The sentinel `999` is not a final diagnostic contract. It is only a visible
placeholder for this candidate program's first executable shape.

## Replacement Path

The lowest-risk replacement path is to mirror, then replace, the Python
`HERBERT_BUILTIN_ARITIES` table with a Herbert-family arity table that can be
executed and compared against the current Python-owned table before compiler
wiring changes. Until that comparison exists and passes for every observed
built-in Dolo can emit, `src/dolo/herbert_surface.py` remains the compiler
authority and this candidate remains executable migration evidence.

## Verification

The candidate is listed in `tests/fixtures/herbert_migration_manifest.tsv`.
`scripts/verify_herbert_truth.sh` compiles it directly with the pinned Herbert
seed on Linux/x86_64, runs the resulting ELF, and compares stdout with
`tests/fixtures/builtin_arity_candidate.stdout`.

This proves the candidate can execute through Herbert. It does not prove the
Dolo compiler has migrated away from Python yet.
