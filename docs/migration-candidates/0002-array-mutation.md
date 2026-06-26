# Migration Candidate 0002: Array Mutation

## Purpose

This Herbert-family migration candidate mirrors the array mutation behavior now
proven by Dolo's emitted `examples/array_mutation.dolo` output. It does not
replace Python bootstrap compiler code yet. It isolates the small behavior
boundary Dolo currently depends on: typed array creation, no-value mutation
through `do add(...)`, buffer mutation through `do append(...)`, and value-level
reads through `count(...)`, `get(...)`, and `freeze(...)`.

## Executable Candidate

`experiments/herbert/array_mutation_candidate.herb` constructs an integer array,
adds two values, builds a buffer-backed label, and returns a tagged tuple:

- `array-mutation-candidate`
- the array count
- the sum of the first two array entries
- the frozen label

The candidate intentionally mirrors a pinned compiler output pattern rather
than introducing new Dolo syntax.

## Verification

The candidate is listed in `tests/fixtures/herbert_migration_manifest.tsv`.
`scripts/verify_herbert_truth.sh` compiles it directly with the pinned Herbert
seed on Linux/x86_64, runs the resulting ELF, and compares stdout with
`tests/fixtures/array_mutation_candidate.stdout`.

This proves the candidate can execute through Herbert. It does not prove the
Dolo compiler has migrated away from Python yet.
