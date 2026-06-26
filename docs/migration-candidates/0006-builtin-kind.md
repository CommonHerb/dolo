# Migration Candidate 0006: Built-In Kind

## Purpose

This Herbert-family migration candidate mirrors Dolo's current Python-owned
split between value-level observed Herbert built-ins and no-value observed
Herbert mutation built-ins. It does not replace the Python bootstrap compiler
yet. It isolates the boundary Dolo uses when it decides whether a built-in call
may appear in a value expression or must be spelled as a `do` statement.

Current Python behavior lives in `src/dolo/herbert_surface.py` as
`HERBERT_VALUE_BUILTINS` and `HERBERT_VOID_BUILTINS`, and the emitter uses
those sets when validating expression calls and `do` statements before Herbert
emission.

## Executable Candidate

`experiments/herbert/builtin_kind_candidate.herb` implements a tiny kind lookup
for the observed built-ins Dolo can emit today:

- `add`, `append -> void`
- `count`, `equal`, `freeze`, `get`, `index`, `length`, `new_array`,
  `new_buffer -> value`
- unknown name -> `missing`

The sentinel `missing` is not a final diagnostic contract. It is only a visible
placeholder for this candidate program's first executable shape.

## Replacement Path

The lowest-risk replacement path is to mirror, then replace, the Python
`HERBERT_VALUE_BUILTINS` and `HERBERT_VOID_BUILTINS` sets with a Herbert-family
built-in-kind table that can be executed and compared against the current
Python-owned sets before compiler wiring changes. Local manifest validation
compares this candidate's lookup table against every observed built-in in both
sets. Until a replacement is wired and verified through the compiler path,
`src/dolo/herbert_surface.py` and the Python emitter remain the compiler
authority and this candidate remains executable migration evidence.

## Verification

The candidate is listed in `tests/fixtures/herbert_migration_manifest.tsv`.
`scripts/verify_herbert_truth.sh` compiles it directly with the pinned Herbert
seed on Linux/x86_64, runs the resulting ELF, and compares stdout with
`tests/fixtures/builtin_kind_candidate.stdout`.

Local manifest validation also compares the candidate's built-in names and
value/no-value kinds against Python-owned `HERBERT_VALUE_BUILTINS` and
`HERBERT_VOID_BUILTINS`.

This proves the candidate can execute through Herbert. It does not prove the
Dolo compiler has migrated away from Python yet.

## Authority Boundary

This candidate is not compiler authority and not paid debt. Dolo's compiler
still uses Python-owned `HERBERT_VALUE_BUILTINS`, `HERBERT_VOID_BUILTINS`, and
Python emitter validation until a Herbert-family replacement is wired through
the compiler path and verified by the full local and native truth gates.
