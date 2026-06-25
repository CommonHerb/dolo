# Dolo Executable Truth Loop Design

## Purpose

Dolo v0.1 must prove at least a tiny Dolo program reaches real native execution
through Herbert. The proof is:

1. compile `.dolo` source with the Python bootstrap compiler,
2. emit Herbert source,
3. compile that Herbert with a pinned `CommonHerb/herbert` gen-1 seed on
   Linux/x86_64,
4. run the resulting ELF, and
5. compare its stdout byte-for-byte against a committed expected output file.

Emitted Herbert text comparison remains useful, but it is not execution proof.

## Pin

- Herbert repository: `https://github.com/CommonHerb/herbert.git`
- Herbert commit: `e9dff2283113063f60fece453e9ab9eb16e7366a`
- Seed path: `bootstrap/seed/gen1.seed`
- Seed sha256: `8a9be3012cd3a132d2da5eb25df0b083671ff352725fdfb10504f1e7a939ce50`
- Execution platform: Linux/x86_64

The pin lives in `HERBERT.lock`. CI checks out exactly this commit and the
verification script checks the checkout and seed hash again before compiling.

## Runnable Examples

The first executable examples are deliberately small and human-readable:

- `examples/citizen.dolo` defines a record, record construction, field access,
  branching, and `main`.
- `examples/ledger.dolo` defines arithmetic, record construction, field access,
  and `main`.

Each example has:

- a generated Herbert golden under `tests/fixtures/*.herb`,
- an expected native stdout file under `tests/fixtures/*.stdout`, and
- a manifest row in `tests/fixtures/executable_manifest.tsv`.

`main` returns renderable Herbert values. Herbert's native renderer prints a
canonical line for ints, bools, strings, and supported tuples, so the first Dolo
truth loop does not need to add side-effect statements just to print.

## Harness

`scripts/verify_herbert_truth.sh` is the executable proof harness. It has no
third-party dependencies. It requires:

- Bash and POSIX userland tools,
- Python 3.13 as Dolo bootstrap substrate,
- a Linux/x86_64 host,
- a pinned Herbert checkout, and
- Herbert's committed x86-64 gen-1 seed.

For every manifest row, the harness compiles Dolo to a temporary Herbert file,
compiles that Herbert with the pinned seed, asserts the emitted `a.out` is an
ELF, executes it, and compares stdout to the committed key.

## CI

The GitHub Actions workflow has two gates:

- `bootstrap-tests`: Python bootstrap unit tests.
- `herbert-execution`: Ubuntu checkout of Dolo plus pinned Herbert, then
  `scripts/verify_herbert_truth.sh --herbert-dir herbert`.

The second gate is the new truth loop. It must not be described as passing until
the actual GitHub Actions job completes successfully.

## Trust Boundaries

Python, Bash, GitHub Actions, Ubuntu, GitHub checkout, the current Herbert seed,
and the Linux/x86_64 host are borrowed substrate. They are necessary to make the
proof run today, but they are not Dolo's language identity.

macOS/Apple Silicon local runs can verify the bootstrap compiler and emitted
Herbert goldens. They cannot execute the pinned Herbert x86-64 seed natively and
must not be presented as native Herbert execution.
