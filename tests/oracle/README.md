# tests/oracle/ — the held-back wiring oracle (ORCHESTRATOR-OWNED)

**Do not edit anything in this directory if you are a worker (Codex).** This is the
grader. A worker cannot author the grader it is judged by — that is the whole point
(see `AGENTS.md` and the family Fold-In Contract).

## What this is

The Dolo **sovereignty meter** counts how many compiler decisions are still owned by
borrowed Python. A slice lowers the meter by replacing one decision with a
Herbert-family owner **wired into the compiler path**. But "I replaced it" is cheap to
claim and easy to fake (mirror a table; move the Python literal elsewhere). This oracle
makes the claim un-fakeable.

For each authority it runs two checks:

- **CHECK-1 POISON-PYTHON** — corrupt the Python-owned decision in `dolo.herbert_surface`
  *before* the compiler imports it, compile a held-back probe, and require the output to
  still match the held-back golden. If the emitter still consults the Python decision, the
  poison flips the output → **NOT WIRED**. (Empirically, swapping the value/void sets makes
  the genuine compiler reject `let a = new_array(...)` with "has no value".)
- **CHECK-2 REMOVE-OWNER (mandatory)** — a `status=herbert` flip **must** declare a
  `herbert_owner` that is a `.herb` under `experiments/herbert/`; the oracle blanks it and
  requires compilation to **break**. This proves the Herbert-family owner is load-bearing and
  closes the "moved the Python literal into a renamed dict/helper" forge that CHECK-1's
  name-based poison cannot see (a cross-model audit caught that gap). No owner / non-`.herb` /
  blanking-is-a-no-op ⇒ NOT WIRED.

Both green ⇒ genuinely wired ⇒ the meter may drop.

## Files

- `oracle_wiring.py` — the grader (not `test_*`, so CI's `unittest discover` skips it; the
  meter invokes it explicitly).
- `programs/*.dolo` — held-back probe programs (authored here, not by the slice).
- `golden/*.herb` — the correct emitted Herbert for each probe (the slice must reproduce it).
- `builtin_kind_golden.tsv`, `builtin_arity_golden.tsv` — the held-back TRUE maps a
  Herbert-family owner must reproduce exactly.

## Proving teeth

`oracle_wiring.py builtin_kind --bite-check` exits 0 only if poisoning the current
(Python-owned) compiler actually breaks it — i.e. the oracle would catch a fake wiring.
Run it whenever you arm a new authority.
