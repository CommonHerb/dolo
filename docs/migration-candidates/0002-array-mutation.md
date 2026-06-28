# Migration Candidate 0002: Array Mutation

## Purpose

This Herbert-family migration candidate mirrors the array mutation behavior now
proven by Dolo's emitted `examples/array_mutation.dolo` output. It does not
replace Python bootstrap compiler code yet. It isolates the small behavior
boundary Dolo currently depends on: typed array creation, no-value mutation
through `do add(...)`, buffer mutation through `do append(...)`, and value-level
reads through `count(...)`, `get(...)`, and `freeze(...)`.

Current Python behavior lives in the emitter's `new_array(...)` type-expression
handling and `do` statement lowering, with the observed built-in surface named
in `src/dolo/herbert_surface.py`.

## Executable Candidate

`experiments/herbert/array_mutation_candidate.herb` constructs an integer array,
adds two values, builds a buffer-backed label, and returns a tagged tuple:

- `array-mutation-candidate`
- the array count
- the sum of the first two array entries
- the frozen label

The candidate intentionally mirrors a pinned compiler output pattern rather
than introducing new Dolo syntax.

`experiments/herbert/array_mutation_shape_candidate.herb` declares the
do-statement shape owner for the compiler path: the emitted keyword, admitted
built-in kinds, and required top-level call count. Its truth-loop stdout golden
is `tests/fixtures/array_mutation_shape_candidate.stdout`.

## Replacement Path

This candidate can only replace Python bootstrap behavior after Dolo has
Herbert-family ownership of the observed built-in surface validation and
lowering path for `new_array(...)`, `do add(...)`, `do append(...)`,
`count(...)`, `get(...)`, and `freeze(...)`. Local manifest validation now
compares this executable Herbert pattern against the emitted
`tests/fixtures/array_mutation.herb` mutation/read shape, ignoring only the
candidate's marker tag in its returned tuple. Until a replacement is wired and
verified through the compiler path, the Python emitter remains the compiler
authority and this candidate remains migration evidence.

## Verification

The candidate is listed in `tests/fixtures/herbert_migration_manifest.tsv`.
`scripts/verify_herbert_truth.sh` compiles it directly with the pinned Herbert
seed on Linux/x86_64, runs the resulting ELF, and compares stdout with
`tests/fixtures/array_mutation_candidate.stdout`.

Local manifest validation also compares the candidate's array/buffer mutation
and read shape against `tests/fixtures/array_mutation.herb`.

This proves the candidate can execute through Herbert. It does not prove the
Dolo compiler has migrated away from Python yet.

## Authority Boundary

This candidate is not compiler authority and not paid debt. Dolo's compiler
still uses Python-owned `new_array(...)` handling, built-in surface validation,
and `do` statement lowering until a Herbert-family replacement is wired through
the compiler path and verified by the full local and native truth gates.
