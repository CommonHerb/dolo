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
- record type knowledge propagates through simple identifier bindings
- `if` / `else`, `let`, assignment, `return`, calls, strings, booleans, and
  arithmetic-like expressions emit readable Herbert source
- duplicate declarations, including record/function name overlaps, record
  annotation errors, unbound variables, unbound assignment targets, duplicate
  `let` bindings, unknown call targets, Dolo function arity mismatches,
  observed Herbert built-in arity mismatches, expression delimiter errors, and
  non-literal expression keywords fail with focused `DoloSyntaxError`
  diagnostics
- the CLI writes Herbert to stdout
- the CLI reports syntax and source-file read failures without Python
  tracebacks
- executable manifest examples still emit their committed Herbert goldens
- repository manifests have sorted rows, the expected tab-separated fields,
  expected file suffixes, unique source rows, unique executable and migration
  output targets, existing repository-relative file targets, executable sources
  whose generated Herbert matches committed `.herb` goldens, and every
  `examples/*.dolo` file is either executable with a no-argument `fn main()` or
  explicitly non-executable with a reason
- Herbert migration manifest sources are `.herb` files with a visible
  `func main()` entry point and `.stdout` goldens
- executable and migration stdout goldens end with a newline, matching the
  shape the truth loop compares after native execution
- the Herbert truth harness is pinned, stages a temporary seed copy, includes
  the migration-candidate manifest, and has a Colima wrapper that attempts to
  stop the profile and names local logs on failure

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

In GitHub Actions, the Herbert checkout repository and ref are read from
`HERBERT.lock` before checkout so the workflow does not carry a second
hard-coded Herbert target.

For local Linux/x86_64 verification through Colima, run:

```bash
scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert
```

The wrapper starts the profile, runs `scripts/verify_herbert_truth.sh` inside
it, attempts a graceful stop on exit, forces a stop if the profile is still
running, bounds cleanup stop commands so interrupted startups cannot hang
forever, and names the profile's `ha.stderr.log` and `serial.log` on failure.

The harness stages a temporary executable copy of Herbert's tracked
`bootstrap/seed/gen1.seed`; it does not chmod or modify the Herbert checkout.
Before staging the seed, the harness runs the same manifest validator used by
the local bootstrap tests so malformed manifests, stale executable Herbert
goldens, duplicate executable output targets, and executable rows without a
no-argument Dolo `main` fail before native execution. Manifest file targets must
stay repository-relative; absolute paths and parent-directory traversal are
rejected before native execution.

Examples intentionally excluded from the executable truth loop must be listed
with a reason in `tests/fixtures/non_executable_examples.tsv`; the local
bootstrap tests fail if an example is neither executable nor explicitly
excluded.

The same harness also runs raw Herbert migration candidates listed in
`tests/fixtures/herbert_migration_manifest.tsv`. These are early
Herbert-family implementation candidates, not completed replacements for Python
bootstrap code. Local manifest validation rejects migration rows that do not
point at `.herb` files with a visible `func main()` entry point, and rejects
stdout goldens that do not use a `.stdout` suffix or end with a newline.

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
