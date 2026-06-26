# Dolo v0.1 Language Reference

This reference describes only what the current compiler implements. It is a
living contract, not a promise about future syntax.

## Source Shape

A Dolo source file contains top-level record and function declarations:

```dolo
record Citizen { name, hunger }

fn hunger_of(c: Citizen) {
  return c.hunger
}
```

Comments start with `#` and run to the end of the line.

## Records

Records name tuple positions:

```dolo
record Entry { label, amount }
```

The current compiler lowers record construction to a Herbert tuple:

```dolo
let e = Entry("seed", 9)
```

emits:

```herbert
let e = ("seed", 9)
```

Record field access lowers to a positional tuple lookup when the compiler can
resolve the record type:

```dolo
return e.amount
```

emits:

```herbert
return e.1
```

Constructor arity is checked by the bootstrap compiler. A record with two fields
must be constructed with exactly two values.

This is not a stable ABI. It is the honest v0 representation used to reach
Herbert today.

## Functions

Functions use `fn`, optional parameters, and a brace-delimited body:

```dolo
fn surplus(stock, need) {
  let spare = stock - need
  return spare
}
```

Parameters may carry a record annotation when field access needs it:

```dolo
fn hunger_of(c: Citizen) {
  return c.hunger
}
```

The annotation is used by the Dolo compiler and is not emitted into Herbert.

## Statements

Implemented statements are:

- `let name = expr`
- `name = expr`
- `return expr`
- `if expr { ... } else { ... }`

`else` is optional. `elif`, loops, imports, modules, effects, methods, and
pattern matching are not implemented.

## Expressions

Expressions are currently a conservative token-preserving surface that lowers
record-specific syntax and boolean operator spellings, then emits Herbert text.

Implemented expression behavior includes:

- integer, boolean, string, and character literals
- variable references
- function calls
- tuple construction
- arithmetic and comparison operators accepted by Herbert
- `&&` lowering to Herbert `and`
- `||` lowering to Herbert `or`
- `!` lowering to Herbert `not`
- record constructors lowering to tuples
- record field access lowering to tuple indexes

The compiler does not yet own a full Dolo type system, precedence table, module
system, or runtime.

## Main And Execution

Executable examples define a no-argument `fn main()`:

```dolo
fn main() {
  return ("seed", 4, true)
}
```

The current truth loop compiles Dolo to Herbert, compiles that Herbert through
the pinned Herbert gen-1 seed on Linux/x86_64, runs the resulting ELF, and
compares stdout to a committed `.stdout` file.

For v0.1, `main` should return values Herbert's native renderer can print:
ints, bools, strings, and supported tuples of renderable values.

## Diagnostics

The compiler currently reports syntax and lowering errors as `DoloSyntaxError`.
Diagnostics are intentionally small:

- malformed source reports line and column where the tokenizer or parser
  noticed the issue
- unexpected characters and unterminated string or character literals report
  the offending or opening column
- unclosed expression delimiters report the opening delimiter column before
  block parsing drifts
- unresolved record field access reports the target, field, and target column
- unknown record fields report the record name, missing field, and field column
- record constructor arity mismatches report expected and actual field counts
  at the constructor column
- the bootstrap CLI prints `DoloSyntaxError` messages as `dolo: ...` on stderr
  and exits with status 1, without a Python traceback

Stable diagnostic codes are future work.
