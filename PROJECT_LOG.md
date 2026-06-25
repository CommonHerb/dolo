# Project Log

## 2026-06-25

- Created `CommonHerb/dolo` as a public GitHub repository.
- Created a clean local checkout at `/Users/ben/Desktop/untitled folder 2/dolo`.
- Observed sibling Herbert checkout at `/Users/ben/Desktop/untitled folder 2/herbert`.
- Verified sibling Herbert remote is `https://github.com/CommonHerb/herbert.git`
  and current commit is `e9dff2283113063f60fece453e9ab9eb16e7366a`.
- Read Herbert `README.md`, `VERIFYING.md`, `Makefile`, parser probes, and
  foundational examples to ground the first target subset.
- Noted local substrate boundary: this machine is Apple Silicon macOS; Herbert's
  committed production seed is an x86-64 Linux ELF, so generated Herbert
  execution needs Linux/x86-64, CI, or emulation.
- Added the first Python-standard-library bootstrap compiler slice on branch
  `foundation/compiler-v0`: records, record constructors, annotated record
  parameters, field access lowering, functions, `let`, assignment, `return`,
  `if` / `else`, expressions preserved into readable Herbert, examples, CLI,
  and unit tests.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`.
- Pushed `foundation/compiler-v0`, observed GitHub Actions `check` success,
  fast-forwarded `main`, pushed `main`, and observed GitHub Actions `check`
  success on `main` at `c485cee2c74dd8f8fa2f4ec623741b7845f79dfa`.
