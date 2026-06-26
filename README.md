# Dolo

Dolo is the first Herbert-family application language.

Herbert is the root language, compiler, runtime, and operating-system lineage.
Dolo is the first higher-level language meant to make real application programs
pleasant to write on top of that owned stack.

Dolo's long-term destiny is to compile through Herbert into native programs on
Herbert's eventual operating system. Temporary host tools in this repository are
bootstrap substrate only. They may help us write tests, run CI, and work on
current computers, but they do not define Dolo's semantics or authority.

## First Slice

The first slice is deliberately small:

- a tiny `.dolo` source language for functions, values, calls, records, simple
  control flow, strings, and narrow typed-array and buffer mutation boundaries
- a bootstrap compiler that emits a documented Herbert target subset
- examples that show why Dolo is nicer for application code than raw Herbert
- tests that prove emitted Herbert text for the current subset
- an executable truth loop that runs manifest examples through pinned Herbert
  on Linux/x86_64 CI and compares native stdout

The current pinned Herbert target is:

- repository: `CommonHerb/herbert`
- commit: `e9dff2283113063f60fece453e9ab9eb16e7366a`
- seed sha256:
  `8a9be3012cd3a132d2da5eb25df0b083671ff352725fdfb10504f1e7a939ce50`
- checkout observed beside this repo at: `../herbert`

## Repository Map

- `COVENANT.md` is the founding covenant.
- `HERBERT.lock` pins the Herbert target used by the executable truth loop.
- `scripts/verify_herbert_truth.sh` runs manifested examples through pinned
  Herbert on Linux/x86_64.
- `docs/language-reference.md` records the exact implemented Dolo v0.1 surface.
- `docs/trust-debt.md` names borrowed substrate.
- `docs/migration-candidates/` records tiny Herbert-family implementation
  candidates before they replace bootstrap code.
- `experiments/herbert/` contains raw Herbert candidate programs run by CI.
- `docs/foundation/herbert-target-subset.md` records what Dolo may emit today.
- `ROADMAP.md` is the living direction map.
- `PROJECT_LOG.md` records decisions and verified state by date.
- `VERIFYING.md` records current proof commands and what they do not prove.
- `docs/superpowers/specs/` contains design specs.
- `docs/superpowers/plans/` contains implementation plans.

## Substrate Policy

Host languages, shells, Python, GitHub Actions, macOS, Linux, and existing
Herbert binaries are borrowed substrate. Every use must stay visible and
replaceable. Dolo's identity is its own language contract and Herbert-family
native destiny, not the bootstrap tools used today.
