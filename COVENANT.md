# Dolo Founding Covenant

Dolo exists to become the first Herbert-family application language: a language
for writing real programs without surrendering semantic authority to external
toolchains.

## Relationship To Herbert

Herbert is the root sovereign language, compiler, runtime, and operating-system
lineage. Dolo is not a replacement for Herbert and must not blur that boundary.
Dolo is a higher-level language that compiles toward Herbert so application
programmers can express records, values, names, and everyday structure without
hand-writing the lower-level Herbert surface every time.

The first Dolo compiler may emit Herbert source or a documented Herbert target
subset. Over time, the target should move closer to owned Herbert-native
execution, not toward a host VM or a foreign runtime.

## Native-Sovereignty Rules

1. Dolo's semantics belong to Dolo and the Herbert family.
2. C, Rust, Python, JavaScript, Node, LLVM, libc, shells, Linux, and macOS are
   never semantic authorities for Dolo.
3. A host tool may be used only as temporary substrate for bootstrapping,
   verification, development, repository automation, or current-computer
   execution.
4. Host substrate must be named plainly in docs, tests, and logs.
5. A convenience dependency is unacceptable if it hides semantics, creates an
   opaque runtime obligation, or would be hard to replace with Herbert-family
   code later.
6. The preferred future path is Dolo source -> Dolo compiler -> Herbert source
   or Herbert IR -> Herbert native compiler -> Herbert OS/native execution.

## Temporary Substrate Policy

The current bootstrap implementation may use Python standard-library code and
GitHub Actions because they are legible, easy to delete, and useful for proving
the language surface. This is trust debt. It is allowed only while the repo keeps
the boundary visible and preserves a plausible migration path into Herbert.

Any new dependency must answer three questions before entering the repo:

- What does it let us prove today?
- What semantic authority would it accidentally claim?
- How would we remove or replace it with Herbert-family code?

## Long Direction

Dolo should grow from a seed crystal, not a toy. The first language can be tiny,
but it should already feel like a real application language: named records,
clear functions, values, text, lists, simple I/O-shaped examples, and a compiler
whose output can be inspected.

The repo should prefer narrow, working, well-explained slices over sprawling
ambition. Every slice should leave future workers with stronger truth: a clearer
spec, a better example, a verified compiler behavior, or a smaller trust-debt
surface.
