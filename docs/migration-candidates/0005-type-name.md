# Migration Candidate 0005: Type Name Surface

## Purpose

This Herbert-family migration candidate mirrors Dolo's current Python-owned
set of observed Herbert type names. It does not replace the Python bootstrap
compiler yet. It isolates the boundary Dolo uses when it accepts type
expressions for typed `new_array(...)` calls.

Current Python behavior lives in `src/dolo/herbert_surface.py` as
`HERBERT_TYPE_NAMES`, and the emitter uses that table when validating type
expression tokens before Herbert emission.

## Executable Candidate

`experiments/herbert/type_name_candidate.herb` implements a tiny membership
lookup for the observed Herbert type names Dolo accepts today:

- `bool`
- `buffer`
- `int`
- `string`
- unknown name -> `0`

The sentinel `0` is not a final diagnostic contract. It is only a visible
placeholder for this candidate program's first executable shape.

## Replacement Path

The lowest-risk replacement path is to mirror, then replace, the Python
`HERBERT_TYPE_NAMES` set with a Herbert-family type-name table that can be
executed and compared against the current Python-owned table before compiler
wiring changes. Local manifest validation compares this candidate's lookup
table against every type name in `HERBERT_TYPE_NAMES`. Until a replacement is
wired and verified through the compiler path, `src/dolo/herbert_surface.py` and
the Python emitter remain the compiler authority and this candidate remains
executable migration evidence.

## Verification

The candidate is listed in `tests/fixtures/herbert_migration_manifest.tsv`.
`scripts/verify_herbert_truth.sh` compiles it directly with the pinned Herbert
seed on Linux/x86_64, runs the resulting ELF, and compares stdout with
`tests/fixtures/type_name_candidate.stdout`.

Local manifest validation also compares the candidate's type-name membership
table against Python-owned `HERBERT_TYPE_NAMES`.

This proves the candidate can execute through Herbert. It does not prove the
Dolo compiler has migrated away from Python yet.

## Authority Boundary

This candidate is not compiler authority and not paid debt. Dolo's compiler
still uses Python-owned `HERBERT_TYPE_NAMES` and Python emitter validation
until a Herbert-family replacement is wired through the compiler path and
verified by the full local and native truth gates.
