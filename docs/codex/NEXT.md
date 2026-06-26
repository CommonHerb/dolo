# NEXT — orchestrator-authored task queue for Codex

> **Phase: FULL-AUTO QUEUE.** Three armed slices below. Work them **in order, one PR per slice,
> without stopping** for orchestrator approval between them — the CI **sovereignty-gate** job
> verifies each (a green PR = a genuinely-wired slice). Read `AGENTS.md`. Do NOT edit `tests/oracle/*`
> or `HERBERT.lock`. One authority per PR; mark the PR ready (not draft) when its checks pass.

## How each slice works (same shape as the merged `builtin_kind`)
1. Author/extend the Herbert-family owner `.herb` (a `func <name>(name):` **if/equal chain** that
   returns the decision value, with a sentinel fallback) — the candidate files already exist.
2. Make the emitter DERIVE the decision from that owner (parse it like `load_herbert_builtin_kinds`),
   and **delete** the Python literal so it is no longer authoritative.
3. Flip the row in `docs/sovereignty/ledger.tsv` to `status=herbert` and set `herbert_owner` to the
   `.herb` path.
4. The slice is accepted iff: `bash scripts/sovereignty_meter.sh` drops by one and exits 0;
   `python3 tests/oracle/oracle_wiring.py <id>` exits 0 (WIRED = poison no-op + owner load-bearing +
   **content drives the decision**); truth loop green; CI 112 green.

## The queue (meter is at 5; each slice lowers it)
1. **`builtin_arity`** → owner `experiments/herbert/builtin_arity_candidate.herb` (returns the arity int).
   The emitter's `_validate_call_arity` must read arities from the owner. (Keep "unknown built-in →
   no arity check" — unknowns are rejected earlier by `_validate_call_target`.)
2. **`boolean_operator`** → owner `experiments/herbert/boolean_operator_candidate.herb` (returns the
   lowering string for `!`/`&&`/`||`). The emitter's `_operator_value` must derive from the owner.
3. **`type_name`** → owner `experiments/herbert/type_name_candidate.herb`. The emitter's type-name
   validation must derive the recognized set from the owner.

When the queue is empty, STOP and log it; the orchestrator will arm the next batch
(`record_field_index`, `array_mutation`) once their oracles are authored.

> **Residual carried from `builtin_kind` (do not regress, not your task to fix now):** owners are
> Python-PARSED, not yet SEED-EXECUTED. Keep using the if/equal-chain `.herb` format so the deeper
> "seed computes the decision" slice stays reachable. The orchestrator will scope it.
