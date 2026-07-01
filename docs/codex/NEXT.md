# NEXT — orchestrator-authored task for Codex

> **Phase: NO ARMED TASK.** The sovereignty meter reads **0** — all 9 tracked compiler
> authorities are Herbert-family owners, and **8 of 9 are now SEED-EXECUTED** (the pinned
> gen1 seed compiles+runs the owner to produce the decision, not Python). There is **no
> earned slice armed for Codex right now.** Do not invent work; read `AGENTS.md` and wait
> for the orchestrator to mint the next referee. Autonomy fuel = armed, oracle-backed tasks,
> and only the orchestrator can mint them.

## Where sovereignty stands (verified, CI-green on `origin/main`)
- **Meter = 0.** 9 authorities, all `status=herbert`, all oracle-WIRED.
- **Seed-execution: 8/9.** `array_mutation` + the 7 former text-scrapers (`builtin_kind`,
  `builtin_arity`, `boolean_operator`, `type_name`, `two_char_ops`, `closing_delimiters`,
  `infix_operators`) are computed by the pinned seed EXECUTING the on-disk owner at compiler
  import (fail-closed: a missing/garbage seed makes the compiler unimportable). The
  `_extract_*_owner_map` Python scrapers are DELETED. Each owner declares its domain via
  `func key_list()`; a held-back unit test pins `key_list()` to the if-chain.
- **Holdout: `record_field_index`** is still executed by the in-tree `_HerbertSubsetProgram`
  tree-walk interpreter (Python). Its seed-execution is **BLOCKED**: its held-back oracle
  installs owners using `empty`/`first`/`rest`/`plus`, which the *pinned* seed's native codegen
  rejects (ERR 419). Unblocking needs a **herbert-side link** adding those builtins to the
  native codegen, then a dolo re-pin — a core-orchestrator + Ben roadmap call, decoupled from
  this satellite. Do NOT touch the herbert repo.

## Standing law
- Read `AGENTS.md` first. **NEVER edit `tests/oracle/*` or `HERBERT.lock`.** Never silently
  re-pin — write a `NEEDS-SYNC` line in `LOG.md` and stop.
- Seed-execution of the owners is **orchestrator-scoped** work (the boundary lives on the
  compile path and is graded by orchestrator-authored oracles). Codex builds nothing here until
  a new oracle-backed slice is armed above.
