# Dolo v0.1 Language Reference

This reference describes only what the current compiler implements. It is a
living contract, not a promise about future syntax.

## Source Shape

A Dolo source file must contain at least one top-level record or function
declaration:

```dolo
record Citizen { name, hunger }

fn hunger_of(c: Citizen) {
  return c.hunger
}
```

Comments start with `#` and run to the end of the line.

Top-level declaration names must be unique within the source file; a record and
a function cannot share the same name. Records must declare at least one field.
Record field names must be unique within a record, and function parameter names
must be unique within a function. Trailing commas in record field declarations
and function parameter lists are not implemented.

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

The compiler tracks record type knowledge for annotated parameters, record
constructor results, simple identifier bindings that copy a value whose record
type is already known, and assignments that replace a bound value with another
known record value.

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
An annotation must name a record declared in the same source file.

Function names must not reuse observed Herbert built-in names that Dolo can
emit directly, such as `length`, `count`, `new_array`, `add`, or `append`.
The pinned Herbert target rejects built-in reuse, so Dolo reserves those names
at declaration time instead of emitting Herbert that cannot pass the native
truth loop.

Dolo-to-Dolo function calls must pass the declared number of arguments.
Value-level calls to observed Herbert built-ins are allowed by name. For the
built-ins Dolo can emit directly, the compiler validates observed argument
counts before Herbert emission. For built-in `new_array(...)`, the compiler
requires exactly one observed Herbert type-expression argument: `int`, `bool`,
`string`, `buffer`, `array(T)`, and tuple type expressions with at least two
fields such as `(int, bool)`.

Every function must return on all paths the current control-flow checker can
represent. A direct `return` satisfies the current block. An `if` satisfies the
current block only when it has an `else` and both arms themselves guarantee a
return. A single-arm `if` may fall through and is rejected unless a later
statement returns.

Observed Herbert no-value mutation built-ins such as `add` and `append` are not
valid Dolo expression calls. Use a `do` statement for those calls.

## Statements

Implemented statements are:

- `let name = expr`
- `name = expr`
- `do call(args...)`
- `return expr`
- `if expr { ... } else { ... }`

`let` introduces a new local binding. A `let` name must not already name a
parameter or earlier local binding in the current binding context. Assignment
updates an existing parameter or local binding; it does not introduce a new
name. The assignment operator `=` is statement syntax only; it is not valid
inside Dolo expressions.

`do` is currently limited to observed no-value Herbert mutation built-ins such
as `add` and `append`. The call must be the whole statement.

`else` is optional. Nested `if` statements inside an `else` block are
implemented; this is the supported spelling when a program needs an
`else if`-shaped branch. `else if`, `elif`, loops, imports, modules, effects,
methods, and pattern matching are not implemented.

## Expressions

Expressions are currently a conservative token-preserving surface that lowers
record-specific syntax and boolean operator spellings, then emits Herbert text.

Implemented expression behavior includes:

- integer, boolean, string, and character literals
- variable references
- function calls to Dolo functions declared in the same source file, with
  declared arity checking
- calls to the observed value-level Herbert built-ins named in
  `docs/foundation/herbert-target-subset.md`; observed arities are checked
  before Herbert emission
- built-in `new_array(...)` calls with exactly one observed Herbert
  type-expression argument
- tuple construction
- arithmetic and comparison operators accepted by Herbert
- `&&` lowering to Herbert `and`
- `||` lowering to Herbert `or`
- `!` lowering to Herbert `not`
- record constructors lowering to tuples
- record field access lowering to tuple indexes

Variable references must name a parameter or a local binding introduced earlier
with `let`.

Field access is currently limited to a simple identifier target and identifier
field name, such as `citizen.hunger`.

Parenthesized expressions must contain an expression. Tuple and call commas
must have an expression on both sides; trailing commas and empty tuple fields
are not implemented.

Adjacent expression values require an operator or comma between them. Forms such
as `1 2`, `flag true`, `(1) 2`, `1(2)`, and `new_buffer() "x"` are not
implemented.

Colon and brace punctuation are not implemented in expressions.

Binary operators must have operands on both sides. Prefix `!` is the only
implemented unary operator today; it must have an operand and cannot follow an
expression.

The compiler does not yet own a full Dolo type system, precedence table, module
system, or runtime.

## Main And Execution

Executable examples define a no-argument `fn main()`. If a Dolo source declares
`main`, the compiler requires it to take zero parameters so emitted Herbert
stays inside the pinned target's executable entry-point boundary:

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
- sources without top-level declarations report the EOF column after leading
  whitespace, comments, or newlines
- top-level `record` and `fn` declarations without names report the token where
  the declaration name was expected
- duplicate top-level record names, top-level function names, record/function
  name overlaps, record fields, and function parameters report the repeated
  name column
- records with no fields report the record name column
- record field declaration commas without field names report the comma column
- record field declaration trailing commas report the comma column
- function parameter list commas without parameter names report the comma column
- function parameter list trailing commas report the comma column
- function parameter annotations without a record name after `:` report the
  token where the annotation name was expected
- function declarations that reuse observed Herbert built-in names report the
  function name column
- `main` declarations with parameters report the `main` name column
- functions that may complete without returning report the function name column
- unknown record annotations report the annotation column
- unexpected characters and unterminated string or character literals report
  the offending or opening column
- unclosed expression delimiters at newline, EOF, or an expected block
  delimiter report the opening delimiter column before block parsing drifts
- unmatched closing expression delimiters report the closing delimiter column
- `else if` reports the `if` column and `elif` reports its own column with an
  unsupported-form diagnostic
- `else` without a matching `if` reports the `else` column
- malformed field access reports the dot column
- unresolved record field access reports the target, field, and target column
- unknown record fields report the record name, missing field, and field column
- record constructor arity mismatches report expected and actual field counts
  at the constructor column
- `let` statements without a binding name report the token where the binding
  name was expected
- `let`, assignment, `return`, `do`, and `if` statements without the expected
  expression, call, or condition report the token where that form was expected
- `let` binding redeclarations report the repeated binding column
- assignment to an unbound name reports the assignment target column
- assignment operators inside expressions report the operator column
- adjacent expression values without an operator report the second value column
- binary operators without a left or right operand report the operator column
- malformed prefix `!` expressions report the operator column
- empty parenthesized expressions report the opening parenthesis column
- commas without a preceding or following expression report the comma column
- unknown function call targets report the call target column
- Dolo function call arity mismatches report expected and actual argument
  counts at the call target column
- observed Herbert built-in arity mismatches report expected and actual
  argument counts at the built-in call target column
- invalid `new_array(...)` argument counts report expected and actual counts at
  the built-in call target column
- unknown `new_array(...)` Herbert type arguments report the type token column
- observed Herbert no-value mutation built-ins report the call target column
  when used as Dolo expression calls
- invalid `do` statements report the call target or first non-call token column
- unknown variable references report the variable column
- non-literal keywords in expressions report the keyword column; `true` and
  `false` are the only keyword literals today
- unsupported expression punctuation reports the punctuation column
- the bootstrap CLI prints `DoloSyntaxError` and source-file read failures as
  `dolo: ...` on stderr and exits with status 1, without a Python traceback

Stable diagnostic codes are future work.
