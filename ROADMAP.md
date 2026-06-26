# Dolo Roadmap

This roadmap is a living map. It separates what is proven from what is intended.

## Proven Now

- `CommonHerb/dolo` exists as a public GitHub repository.
- Dolo's founding covenant defines Herbert as the root sovereign lineage and
  host tools as temporary substrate.
- The first observed Herbert target is pinned to
  `e9dff2283113063f60fece453e9ab9eb16e7366a`.
- Dolo has executable examples with `fn main()` and committed Herbert/stdout
  fixtures.
- Dolo can emit value-level observed Herbert built-ins including typed
  `new_array(...)` expressions and `count(...)`; no-value mutation built-ins
  are rejected until Dolo has an explicit `do` statement.
- `scripts/verify_herbert_truth.sh` proves manifested examples by compiling
  `.dolo -> .herb -> ELF` through the pinned Herbert seed on Linux/x86_64 and
  comparing native stdout.
- The first Herbert-family migration candidate,
  `experiments/herbert/record_field_index_candidate.herb`, runs through the same
  pinned Herbert seed and is tracked as candidate 0001.

## First Foundation

- Define a small readable Dolo syntax.
- Implement a bootstrap compiler with no third-party runtime dependency.
- Emit a documented Herbert source subset.
- Add examples that are nicer than raw Herbert for application-shaped code.
- Test the compiler with RED-first fixtures.
- Add CI that runs bootstrap tests and validates manifested examples through
  pinned Herbert native execution on Linux/x86_64.
- Keep the Dolo v0.1 language reference and trust-debt ledger current.

## Next Slices

- Expand expression and statement coverage only when examples demand it.
- Harden parser diagnostics with stable error messages.
- Add record constructors and named-field access with explicit tuple lowering.
- Add a Dolo `do` statement before exposing observed no-value Herbert mutation
  built-ins such as `add` and `append`.
- Add list literals or typed list builders if they can lower honestly to
  Herbert arrays.
- Grow the executable manifest one behavior at a time.
- Turn migration candidate 0001 into a real replacement only after the Dolo
  compiler behavior it mirrors has stronger diagnostic and type boundaries.
- Replace bootstrap pieces with Herbert-family implementations when they become
  small and well-specified enough.

## Long Direction

- Dolo source compiles through Herbert without semantic dependence on Python or
  any other host language.
- Dolo programs become native Herbert-family programs.
- Dolo gains a standard application library only after the owned runtime story is
  clear enough not to smuggle in a foreign platform.
- Dolo eventually runs on Herbert's operating-system lineage.

## Standing Non-Goals

- Do not make Dolo a Python, Node, LLVM, libc, shell, Linux, or macOS language.
- Do not add opaque dependencies to move faster.
- Do not modify Herbert unless there is a narrow, justified integration reason.
- Do not pretend a prototype path is the sovereign path.
