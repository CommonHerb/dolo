# Verifying Dolo

Dolo's current verification is intentionally small and honest.

## Local Bootstrap Tests

Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"
```

This proves:

- the bootstrap parser accepts the v0 examples
- record constructors lower to Herbert tuples
- record field access lowers to tuple indexes
- `if` / `else`, `let`, `return`, calls, strings, booleans, and arithmetic-like
  expressions emit readable Herbert source
- the CLI writes Herbert to stdout
- committed examples match committed Herbert goldens

This does not prove:

- arbitrary Dolo program correctness
- arbitrary Herbert compiler correctness
- native execution of generated Herbert on this macOS host
- removal of Python trust debt

## Herbert Executable Truth Loop

Run on Linux/x86_64 with a checkout of the pinned Herbert commit:

```bash
scripts/verify_herbert_truth.sh --herbert-dir ../herbert
```

This proves, for the executable manifest in
`tests/fixtures/executable_manifest.tsv`:

- the Dolo bootstrap compiler emits the committed Herbert source
- the Herbert checkout is exactly the commit pinned in `HERBERT.lock`
- the Herbert gen-1 seed hash matches the pin in `HERBERT.lock`
- generated Herbert compiles through the pinned Herbert seed to an ELF `a.out`
- the ELF runs and its stdout matches the committed `.stdout` file

The harness stages a temporary executable copy of Herbert's tracked
`bootstrap/seed/gen1.seed`; it does not chmod or modify the Herbert checkout.

This does not prove arbitrary Dolo program correctness, arbitrary Herbert
compiler correctness, or removal of bootstrap trust debt. It proves only the
manifested examples reached native execution through the pinned Herbert seed.

## Borrowed Substrate Boundary

The compiler is currently Python standard-library bootstrap substrate. Python is
not Dolo's identity or semantic authority.

The observed Herbert production seed beside this repo is an x86-64 Linux ELF.
This Apple Silicon macOS host cannot execute that seed directly. Native Herbert
execution should be verified on Linux/x86-64 or clearly labeled emulation/CI
substrate until Dolo has an owned Herbert-family path.
