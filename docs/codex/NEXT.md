# NEXT — orchestrator-authored task for Codex

> **Phase: ARMED.** The orchestrator-owned **sovereignty meter** + **held-back oracle**
> now exist. Read `AGENTS.md` first. Do exactly ONE earned slice, then STOP.

## The instruments (orchestrator-owned — do NOT edit `tests/oracle/*`)
- **Meter:** `bash scripts/sovereignty_meter.sh` → prints `SOVEREIGNTY METER = N` (Python-owned
  decisions still on the path). It is **6** right now. A real slice LOWERS it.
- **Ledger:** `docs/sovereignty/ledger.tsv` — the 6 Python-owned authorities. You flip ONE row's
  `status` from `python` to `herbert` and fill its `herbert_owner` path.
- **Held-back oracle:** `tests/oracle/oracle_wiring.py` — proves a flip is genuinely wired, not a
  mirror or a moved literal. It poisons the Python decision (must become a no-op) and blanks your
  declared `herbert_owner` (must break compilation).

## CURRENT ARMED TASK — `builtin_kind`
Replace the Python-owned **value/void built-in KIND decision**
(`src/dolo/herbert_surface.py:HERBERT_BUILTIN_KINDS` and the `HERBERT_VALUE_BUILTINS` /
`HERBERT_VOID_BUILTINS` the emitter consults) with a **Herbert-family owner wired into the
compiler path**, so the Python kind table is no longer load-bearing.

### Acceptance (ALL must hold — the meter + oracle enforce most of it)
1. **Meter drops to 5:** `bash scripts/sovereignty_meter.sh` exits 0 and prints `= 5`.
2. **Wiring oracle GREEN:** `python3 tests/oracle/oracle_wiring.py builtin_kind` exits 0 (WIRED).
   - This means: poisoning the Python kind sets has **no effect** on the emitted output, AND
     blanking your declared `herbert_owner` **breaks** compilation (it is load-bearing).
3. **A real Herbert-family owner:** create (or extend `experiments/herbert/builtin_kind_candidate.herb`
   into) a Herbert-family owner that, run through the **pinned** seed, yields the value/void
   classification matching `tests/oracle/builtin_kind_golden.tsv` **exactly**; make the emitter
   consult it instead of the Python sets; record its repo path in the ledger's `herbert_owner` column.
   At review the orchestrator will **semantically perturb** that owner (e.g. flip `new_array`→void)
   and require the emitted output to change accordingly — its *content* must drive the decision,
   not just be a load-bearing file. Author the owner so its kind data is the genuine source.
4. **The Python literal is no longer the authority** — delete it or make it derived-from-Herbert.
5. **Truth loop GREEN:** `scripts/verify_herbert_truth.sh --herbert-dir ../herbert-pin` still passes.
6. **CI suite GREEN:** `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"` (112 tests).
7. **One slice. STOP.** Do not touch `tests/oracle/*` or `HERBERT.lock`. No governance prose.

### How to propose it
Open a PR (as before). The orchestrator pulls, runs the meter + oracle + truth loop, and either
merges or sends it back via this file. If the oracle is RED, the slice is a mirror/forge — revert.

> Pin drift is still open and is the orchestrator's call (you correctly logged NEEDS-SYNC).
> Leave `HERBERT.lock` as-is unless this file says otherwise.
