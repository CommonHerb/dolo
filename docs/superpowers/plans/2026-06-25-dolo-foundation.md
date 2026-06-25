# Dolo Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create Dolo's first real foundation: repo, covenant, target subset, tested bootstrap compiler, examples, roadmap, project log, and durable GitHub commits.

**Architecture:** Dolo v0 is a source-to-source compiler from a tiny `.dolo` language into a documented Herbert source subset. The compiler is temporary Python standard-library substrate with small parser, AST, lowering, emitter, and CLI modules. Native execution remains Herbert's job.

**Tech Stack:** Python 3 standard library, `unittest`, Git, GitHub CLI, pinned observed Herbert checkout `CommonHerb/herbert@e9dff2283113063f60fece453e9ab9eb16e7366a`.

## Global Constraints

- Dolo is the first Herbert-family application language.
- Herbert is the root sovereign language/compiler/runtime/OS lineage.
- Dolo must not owe semantic authority to C, Rust, Python, Node, LLVM, libc, shell, Linux/macOS runtimes, or opaque external toolchains.
- Temporary host tools are allowed only as labeled substrate or trust debt.
- Do not modify Herbert unless there is a narrow, well-justified integration reason.
- Prefer pinning or documenting a Herbert target commit over coupling repos too early.
- No third-party runtime dependencies in the first compiler slice.

---

### Task 1: Founding Documents

**Files:**
- Create: `README.md`
- Create: `COVENANT.md`
- Create: `ROADMAP.md`
- Create: `PROJECT_LOG.md`
- Create: `docs/foundation/herbert-target-subset.md`
- Create: `docs/superpowers/specs/2026-06-25-dolo-foundation-design.md`
- Create: `docs/superpowers/plans/2026-06-25-dolo-foundation.md`

**Interfaces:**
- Consumes: current Herbert checkout evidence.
- Produces: identity and target-subset rules used by all later tasks.

- [x] **Step 1: Record the covenant and target subset**

Use the current Herbert evidence and pin the observed commit.

- [x] **Step 2: Commit**

```bash
git add README.md COVENANT.md ROADMAP.md PROJECT_LOG.md docs
git commit -m "docs: found dolo covenant"
git push -u origin main
```

### Task 2: Compiler Package Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `src/dolo/__init__.py`
- Create: `src/dolo/ast.py`
- Create: `src/dolo/tokens.py`
- Create: `src/dolo/parser.py`
- Create: `src/dolo/emitter.py`
- Create: `src/dolo/compiler.py`
- Create: `src/dolo/cli.py`
- Create: `tests/test_compiler.py`
- Create: `tests/fixtures/citizen.dolo`
- Create: `tests/fixtures/citizen.herb`

**Interfaces:**
- Produces: `dolo.compiler.compile_source(source: str) -> str`.

- [x] **Step 1: Write the failing compiler test**

```python
import unittest

from dolo.compiler import compile_source


class CompilerTests(unittest.TestCase):
    def test_citizen_record_lowers_to_readable_herbert(self):
        source = """record Citizen { name, hunger }

fn hunger(c: Citizen) {
  return c.hunger
}
"""
        expected = """func hunger(c):
  return c.1
end
"""

        self.assertEqual(compile_source(source), expected)
```

- [x] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src python3 -m unittest tests.test_compiler`

Expected: FAIL because `dolo` is not implemented.

- [x] **Step 3: Implement the minimal package**

Create `src/dolo/tokens.py`, `src/dolo/ast.py`, `src/dolo/parser.py`,
`src/dolo/emitter.py`, and `src/dolo/compiler.py`. Implement tokenization,
parsing, record-field lowering, and Herbert emission for the tested slice.

- [x] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src python3 -m unittest tests.test_compiler`

Expected: PASS.

- [x] **Step 5: Commit**

```bash
git add pyproject.toml src tests
git commit -m "feat: add first dolo compiler slice"
```

### Task 3: Examples And CLI

**Files:**
- Create: `examples/citizen.dolo`
- Create: `examples/ledger.dolo`
- Modify: `src/dolo/cli.py`
- Modify: `tests/test_compiler.py`

**Interfaces:**
- Consumes: `compile_source(source: str) -> str`.
- Produces: CLI command `python3 -m dolo.cli input.dolo`.

- [x] **Step 1: Write failing CLI and example tests**

Test that `examples/citizen.dolo` and `examples/ledger.dolo` compile to
committed Herbert fixtures and that the CLI emits the same bytes to stdout.

- [x] **Step 2: Run tests to verify failure**

Run: `PYTHONPATH=src python3 -m unittest tests.test_compiler`

Expected: FAIL until examples and CLI behavior exist.

- [x] **Step 3: Implement examples and CLI**

Add `examples/citizen.dolo`, `examples/ledger.dolo`,
`tests/fixtures/citizen.herb`, `tests/fixtures/ledger.herb`, and a CLI that
reads one input path and writes Herbert to stdout.

- [x] **Step 4: Run tests**

Run: `PYTHONPATH=src python3 -m unittest tests.test_compiler`

Expected: PASS.

- [x] **Step 5: Commit**

```bash
git add examples src tests
git commit -m "feat: add dolo examples and cli"
```

### Task 4: Verification And CI

**Files:**
- Create: `.github/workflows/check.yml`
- Create: `VERIFYING.md`
- Modify: `PROJECT_LOG.md`

**Interfaces:**
- Consumes: local Python tests.
- Produces: repeatable local and GitHub verification commands.

- [x] **Step 1: Write verification docs**

Document:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"
```

State that this proves the bootstrap compiler and emitted Herbert fixtures, not
native Herbert execution.

- [x] **Step 2: Add CI**

Use GitHub Actions Ubuntu with Python 3 to run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"
```

- [x] **Step 3: Verify locally**

Run: `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`

Expected: all tests pass.

- [x] **Step 4: Commit and push**

```bash
git add .github VERIFYING.md PROJECT_LOG.md
git commit -m "ci: verify dolo bootstrap compiler"
git push -u origin foundation/compiler-v0
```
