# Herbert Target Subset

This file records the Herbert surface Dolo may emit in the first slice.

Observed Herbert checkout:

- repo: `CommonHerb/herbert`
- commit: `e9dff2283113063f60fece453e9ab9eb16e7366a`
- seed sha256:
  `8a9be3012cd3a132d2da5eb25df0b083671ff352725fdfb10504f1e7a939ce50`
- local evidence: `../herbert` on branch `main`, matching `origin/main` when
  first inspected for Dolo's foundation

## Current Target

Dolo v0 may emit Herbert source using:

- `func name(params): ... end`
- `let name = expr`
- `name = expr`
- `do name(args)`
- `return expr`
- `if` / `else` / `end`
- integer, boolean, string, and character literals
- arithmetic and comparison operators already present in Herbert examples
- boolean `and`, `or`, and `not`
- tuple construction and positional access
- calls to user functions
- calls to observed value-level Herbert built-ins such as `length`, `index`,
  `equal`, `new_buffer`, `freeze`, `new_array`, `get`, and `count`
- observed `new_array(...)` type expressions for `int`, `bool`, `string`,
  `buffer`, `array(T)`, and tuple-shaped type expressions
- no-argument `func main()` returning a value that Herbert's native renderer can
  print on Linux/x86_64

For value-level built-ins that Dolo can currently emit directly, the bootstrap
compiler validates observed argument counts before Herbert emission. This is an
arity boundary only; Dolo does not yet claim a full type system for those
built-ins.

Observed no-value Herbert mutation built-ins such as `add` and `append` require
Herbert `do` statements. Dolo emits them only through explicit `do` statements
and rejects them in value expressions.

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

## Arrays And Lists

Dolo can currently pass observed Herbert type expressions to `new_array(...)`,
use value-level array readers such as `count(...)` and `get(...)`, and mutate
arrays through `do add(...)`. List literals and typed list builders are still
deferred rather than faked.

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

The executable truth loop is `scripts/verify_herbert_truth.sh`. It verifies the
Herbert checkout and seed pin, stages a temporary executable seed copy, compiles
manifested Dolo examples to Herbert, compiles that Herbert to ELF, runs the ELF,
and compares native stdout to committed `.stdout` files.
