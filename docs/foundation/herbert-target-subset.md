# Herbert Target Subset

This file records the Herbert surface Dolo may emit in the first slice.

Observed Herbert checkout:

- repo: `CommonHerb/herbert`
- commit: `e9dff2283113063f60fece453e9ab9eb16e7366a`
- local evidence: `../herbert` on branch `main`, matching `origin/main` when
  first inspected for Dolo's foundation

## Current Target

Dolo v0 may emit Herbert source using:

- `func name(params): ... end`
- `let name = expr`
- `name = expr`
- `return expr`
- `if` / `elif` / `else` / `end`
- integer, boolean, string, and character literals
- arithmetic and comparison operators already present in Herbert examples
- boolean `and`, `or`, and `not`
- tuple construction and positional access
- calls to user functions
- calls to observed Herbert built-ins such as `length`, `index`, `equal`,
  `new_buffer`, `append`, `freeze`, `new_array`, `add`, `get`, and `count`

The initial compiler should generate conservative, readable Herbert text. It is
better to emit boring Herbert that can be inspected than clever Herbert that
conceals Dolo semantics.

## Records

The first Dolo record lowering may use Herbert tuples with named-field access
resolved at compile time. Example:

```dolo
record Citizen { name, hunger }

fn hunger_of(c: Citizen) {
  return c.hunger
}
```

may lower to Herbert tuple access:

```herbert
func hunger_of(c):
  return c.1
end
```

This is an honest v0 representation, not a permanent ABI.

## Lists

The first Dolo list lowering may use Herbert arrays when element type is obvious
from annotation or literal context. If that is too much for the first compiler
slice, list support should be deferred rather than faked.

## Out Of Scope

The first slice does not claim:

- arbitrary Herbert correctness
- native execution on macOS
- a Dolo runtime
- modules, imports, generics, ownership, effects, or async behavior
- a stable record ABI
- self-hosting

Those are roadmap items, not v0 facts.

## Borrowed Verification

On Apple Silicon macOS, the observed Herbert production seed is an x86-64 Linux
ELF. Local Dolo tests can verify emitted Herbert text and compiler behavior, but
running the generated Herbert through the native Herbert toolchain requires
Linux/x86-64 or equivalent borrowed substrate such as CI or emulation. That
boundary must stay visible.
