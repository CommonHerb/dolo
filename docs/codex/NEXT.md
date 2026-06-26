# NEXT — orchestrator-authored task for Codex

> **Phase: QUEUE COMPLETE.** The 3-slice queue (builtin_arity, boolean_operator, type_name) is
> LANDED. The sovereignty meter is at **2** (4 of 6 authorities herbert-owned, all oracle-verified
> in CI). There is **no armed task right now.** Read `AGENTS.md`. Do not start a slice until armed.

## Done — the full-auto queue
- **builtin_kind, builtin_arity, boolean_operator, type_name** — each wired to a Herbert-family
  `.herb` owner, its Python literal deleted, its held-back oracle WIRED (CI sovereignty-gate green),
  orchestrator-reviewed (no oracle edits, no test masking). Merged.

## Remaining authorities — NOT yet armed
- **`record_field_index`, `array_mutation`** — these are EMITTER-INTERNAL lowerings (not simple
  `herbert_surface` tables), so their held-back oracles are harder to author and the orchestrator
  owes them before either can be armed. **Hold** — a worker cannot grind an un-graded authority.

## Allowed now (optional, read-only)
- You may READ and PROPOSE (in a comment, not a commit) how you would wire `record_field_index` or
  `array_mutation` the same way. Commit nothing until this file arms one.

> **Residual carried across all slices (a future slice, not now):** owners are Python-PARSED, not
> yet SEED-EXECUTED. Moving the decision COMPUTATION through the pinned seed is the deeper sovereignty
> step; the orchestrator will scope it.
