# Migration Candidate 0004: Boolean Operator Lowering

## Purpose

This Herbert-family migration candidate mirrors Dolo's current Python-owned
boolean operator lowering table. It does not replace the Python bootstrap
compiler yet. It isolates the boundary Dolo uses when it lowers Dolo spellings
`!`, `&&`, and `||` to the observed Herbert spellings `not`, `and`, and `or`.

Current Python behavior lives in `src/dolo/herbert_surface.py` as
`DOLO_BOOLEAN_OPERATOR_LOWERINGS`, and the emitter uses that table when
formatting expression tokens before Herbert emission.

## Executable Candidate

`experiments/herbert/boolean_operator_candidate.herb` implements a tiny lookup
for the boolean operators Dolo can lower today:

- `! -> not`
- `&& -> and`
- `|| -> or`
- unknown name -> `missing`

The sentinel `missing` is not a final diagnostic contract. It is only a visible
placeholder for this candidate program's first executable shape.

## Replacement Path

The lowest-risk replacement path is to mirror, then replace, the Python
`DOLO_BOOLEAN_OPERATOR_LOWERINGS` table with a Herbert-family lowering table
that can be executed and compared against the current Python-owned table before
compiler wiring changes. Local manifest validation compares this candidate's
lookup table against every operator in `DOLO_BOOLEAN_OPERATOR_LOWERINGS`.
Until a replacement is wired and verified through the compiler path,
`src/dolo/herbert_surface.py` and the Python emitter remain the compiler
authority and this candidate remains executable migration evidence.

## Verification

The candidate is listed in `tests/fixtures/herbert_migration_manifest.tsv`.
`scripts/verify_herbert_truth.sh` compiles it directly with the pinned Herbert
seed on Linux/x86_64, runs the resulting ELF, and compares stdout with
`tests/fixtures/boolean_operator_candidate.stdout`.

Local manifest validation also compares the candidate's operator spellings and
lowered Herbert words against Python-owned `DOLO_BOOLEAN_OPERATOR_LOWERINGS`.

This proves the candidate can execute through Herbert. It does not prove the
Dolo compiler has migrated away from Python yet.

## Authority Boundary

This candidate is not compiler authority and not paid debt. Dolo's compiler
still uses Python-owned `DOLO_BOOLEAN_OPERATOR_LOWERINGS` and Python emitter
formatting until a Herbert-family replacement is wired through the compiler path
and verified by the full local and native truth gates.
