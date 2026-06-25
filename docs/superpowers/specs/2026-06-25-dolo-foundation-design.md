# Dolo Foundation Design

## Purpose

Dolo is the first Herbert-family application language. This foundation does not
try to finish Dolo. It creates the repo, covenant, smallest honest compiler
direction, examples, tests, roadmap, and log needed for future decades of work.

## Architecture

Dolo v0 uses a small bootstrap compiler written in a legible host language with
no third-party runtime dependency. The host implementation is temporary
substrate. The compiler parses `.dolo` files into a tiny AST, lowers records and
application-shaped syntax into a conservative Herbert source subset, and writes
human-readable `.herb` output.

The first compiler is a source-to-source compiler:

```text
Dolo source -> Dolo parser/AST -> Herbert target subset -> .herb source
```

Native execution remains Herbert's responsibility. Dolo does not define a host
VM, hidden runtime, or foreign ABI.

## Language Slice

The first slice supports:

- `record Name { field, field }` declarations
- `fn name(params) { ... }` functions
- `let name = expr`
- assignment
- `return expr`
- `if` / `else`
- integer, boolean, string, and character literals
- arithmetic, comparison, and boolean expressions
- user calls and selected Herbert built-in calls
- named record field access lowered to Herbert tuple positions

Lists are desirable but may stay documented as target design unless they can be
implemented honestly without widening the compiler too far.

## Examples

Examples should be beautiful and small. They should show the difference between
application-shaped Dolo and lower-level Herbert:

- a citizen/status record
- a tiny ledger or inventory calculation
- a text helper using Herbert string operations

Each example should have expected Herbert output in tests, so the compiler's
meaning is visible.

## Verification

The first local verification is bootstrap compiler testing:

- parser tests
- lowering tests
- CLI tests
- golden emitted Herbert fixtures

On the current Apple Silicon macOS host, executing Herbert's x86-64 Linux seed
is borrowed-substrate work. CI may later use Ubuntu to run generated Herbert
through the pinned Herbert toolchain. Until that exists, docs must say plainly
that local verification proves compiler output, not native Herbert execution.

## Trust Debt

Python, `pytest` or `unittest`, shell, GitHub, GitHub Actions, macOS, Linux, and
Herbert's committed seed are all trust debt or temporary substrate. The initial
implementation should prefer the Python standard library so the debt is small,
obvious, and replaceable.

## Scope Boundaries

Dolo must not modify Herbert in this slice. It should pin and document the
Herbert target commit instead. Any future Herbert change should be narrow,
well-justified, and separately reviewed.
