# Executable Truth Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove Dolo examples execute as native programs through pinned Herbert on Linux/x86_64 CI.

**Architecture:** Keep the Python bootstrap compiler small. Add `main` to the existing examples, commit emitted Herbert and stdout goldens, and use a shell harness to compile/run those examples through Herbert's pinned gen-1 seed. CI checks the pin, runs the local bootstrap tests, then runs the executable proof on Ubuntu.

**Tech Stack:** Python 3.13 standard library, Bash, GitHub Actions, pinned `CommonHerb/herbert`, Linux/x86_64, Herbert gen-1 seed.

## Global Constraints

- Do not make Dolo a Python language. Python is temporary bootstrap substrate only.
- Do not add third-party dependencies.
- Do not modify Herbert.
- Pin Herbert to `e9dff2283113063f60fece453e9ab9eb16e7366a`.
- Pin `bootstrap/seed/gen1.seed` to sha256 `8a9be3012cd3a132d2da5eb25df0b083671ff352725fdfb10504f1e7a939ce50`.
- Never describe emitted-text comparison as native execution.
- Keep Python, Bash, GitHub Actions, Linux, current Herbert seed, and host OS visible as borrowed substrate.

---

### Task 1: Runnable Example Assets

**Files:**
- Modify: `examples/citizen.dolo`
- Modify: `examples/ledger.dolo`
- Modify: `tests/fixtures/citizen.herb`
- Modify: `tests/fixtures/ledger.herb`
- Create: `tests/fixtures/citizen.stdout`
- Create: `tests/fixtures/ledger.stdout`
- Create: `tests/fixtures/executable_manifest.tsv`
- Modify: `tests/test_compiler.py`

**Interfaces:**
- Consumes: `dolo.compiler.compile_source(source: str) -> str`
- Produces: manifest rows of `source<TAB>herbert<TAB>stdout`

- [ ] **Step 1: Write failing unit test**

Add a test that reads `tests/fixtures/executable_manifest.tsv`, asserts each
source contains `fn main()`, compiles each Dolo source, and compares it with the
listed Herbert fixture. It should fail because the manifest and stdout fixtures
do not exist yet.

- [ ] **Step 2: Run test to verify RED**

Run:

```bash
PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_executable_manifest_examples_have_main_and_goldens
```

Expected: fail with missing manifest or missing fixture.

- [ ] **Step 3: Add example assets**

Add `main` to the examples, update Herbert fixtures, add stdout fixtures, and
add `tests/fixtures/executable_manifest.tsv`.

- [ ] **Step 4: Run tests to verify GREEN**

Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add examples tests
git commit -m "test: add runnable dolo examples"
```

### Task 2: Pinned Herbert Native Harness

**Files:**
- Create: `HERBERT.lock`
- Create: `scripts/verify_herbert_truth.sh`
- Modify: `VERIFYING.md`
- Modify: `tests/test_compiler.py`

**Interfaces:**
- Consumes: `tests/fixtures/executable_manifest.tsv`
- Consumes: `HERBERT.lock`
- Produces: executable proof command `scripts/verify_herbert_truth.sh --herbert-dir <path>`

- [ ] **Step 1: Write failing harness metadata test**

Add a unit test that reads `HERBERT.lock`, asserts the pinned commit and seed
hash match the documented values, and asserts the harness script exists and
mentions `a.out`, `sha256`, and `x86_64`. It should fail before the files exist.

- [ ] **Step 2: Run test to verify RED**

Run:

```bash
PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_herbert_truth_harness_is_pinned
```

Expected: fail because `HERBERT.lock` or the script is missing.

- [ ] **Step 3: Add lock and harness**

Create the lock file and `scripts/verify_herbert_truth.sh`. The script checks
Linux/x86_64, verifies the Herbert checkout commit, verifies the seed hash,
compiles every manifest example, checks for ELF magic, runs each ELF, and diffs
stdout against the committed key.

- [ ] **Step 4: Run local tests**

Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"
```

Expected: all tests pass on macOS. The native harness is documented as requiring
Linux/x86_64 and is run in CI.

- [ ] **Step 5: Commit**

```bash
git add HERBERT.lock scripts VERIFYING.md tests
git commit -m "feat: add pinned herbert truth harness"
```

### Task 3: GitHub Actions Truth Job

**Files:**
- Modify: `.github/workflows/check.yml`

**Interfaces:**
- Consumes: `HERBERT.lock`
- Consumes: `scripts/verify_herbert_truth.sh --herbert-dir herbert`
- Produces: a GitHub Actions job named `herbert-execution`

- [ ] **Step 1: Update workflow**

Add a `herbert-execution` job on `ubuntu-latest` that checks out Dolo, checks
out `CommonHerb/herbert` at `e9dff2283113063f60fece453e9ab9eb16e7366a` into
`herbert`, sets up Python 3.13, verifies the lock commit matches the checkout,
and runs the harness.

- [ ] **Step 2: Run local syntax/consistency checks**

Run:

```bash
git diff --check
PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"
```

Expected: both pass.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/check.yml
git commit -m "ci: run dolo through herbert"
```

### Task 4: Language Reference And Trust Debt

**Files:**
- Create: `docs/language-reference.md`
- Create: `docs/trust-debt.md`
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `PROJECT_LOG.md`
- Modify: `docs/foundation/herbert-target-subset.md`

**Interfaces:**
- Consumes: implemented parser/emitter behavior and executable harness behavior
- Produces: exact v0.1 language reference and trust-debt ledger

- [ ] **Step 1: Write docs**

Document only the implemented grammar and semantics: records, functions,
parameters, `let`, assignment, `return`, `if`/`else`, expression passthrough,
record constructors, field access, and `main` execution scope. Record borrowed
substrates and the Linux/x86_64 limitation.

- [ ] **Step 2: Run docs sanity checks**

Run:

```bash
rg -n "native execution|emitted Herbert|Python|Herbert.lock|Linux/x86_64" README.md VERIFYING.md ROADMAP.md PROJECT_LOG.md docs
git diff --check
```

Expected: wording distinguishes emitted-text tests from native execution and
has no whitespace errors.

- [ ] **Step 3: Commit**

```bash
git add README.md ROADMAP.md PROJECT_LOG.md docs
git commit -m "docs: record executable truth boundary"
```

### Task 5: Final Verification And Push

**Files:**
- No new files unless review finds a concrete issue.

**Interfaces:**
- Consumes: all prior tasks
- Produces: pushed branch and observed GitHub Actions result

- [ ] **Step 1: Run local gates**

Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"
git diff --check
git status --short --branch
```

- [ ] **Step 2: Push branch**

Run:

```bash
git push -u origin foundation/executable-truth-loop
```

- [ ] **Step 3: Watch GitHub Actions**

Run:

```bash
gh run list --repo CommonHerb/dolo --branch foundation/executable-truth-loop --limit 3
gh run watch --repo CommonHerb/dolo <run-id> --exit-status
```

Expected: the branch workflow completes with both jobs green.
