# Migration Candidate 0001: Record Field Index

## Purpose

This is the first tiny Herbert-family implementation candidate. It does not
replace the Python bootstrap compiler yet. It isolates one small behavior from
today's compiler: mapping a known record field name to its tuple index.

Current Python behavior lives in the emitter's record-field lowering. The future
direction is to move well-pinned compiler decisions like this into
Herbert-family code piece by piece.

## Executable Candidate

`experiments/herbert/record_field_index_candidate.herb` implements a tiny
Herbert function for the `Citizen` example's field names:

- `name -> 0`
- `hunger -> 1`
- `coins -> 2`
- unknown field -> `999`

The sentinel `999` is not a final diagnostic contract. It is only a visible
placeholder for this candidate program's first executable shape.

## Replacement Path

This candidate can only replace Python emitter behavior after record metadata,
field-name lookup, and diagnostic policy have Herbert-family representation.
Local manifest validation now compares this executable lookup shape against the
parsed `Citizen` record fields in `examples/citizen.dolo` before any compiler
authority moves. Until a replacement is wired and verified through the compiler
path, the candidate is executable repayment evidence, not Dolo's semantic
authority.

## Verification

The candidate is listed in `tests/fixtures/herbert_migration_manifest.tsv`.
`scripts/verify_herbert_truth.sh` compiles it directly with the pinned Herbert
seed on Linux/x86_64, runs the resulting ELF, and compares stdout with
`tests/fixtures/record_field_index_candidate.stdout`.

Local manifest validation also compares the candidate's field names and indexes
against the parsed `Citizen` record in `examples/citizen.dolo`.

This proves the candidate can execute through Herbert. It does not prove the
Dolo compiler has migrated away from Python yet.

## Authority Boundary

This candidate is not compiler authority and not paid debt. Dolo's compiler
still uses Python-owned record metadata and emitter lowering until a
Herbert-family replacement is wired through the compiler path and verified by
the full local and native truth gates.
