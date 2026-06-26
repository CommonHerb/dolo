# NEXT — orchestrator-authored task for Codex

> **Phase: QUEUE COMPLETE (batch 2 landed).** Sovereignty meter is at **2** (7 of 9 authorities
> herbert-owned, all oracle-verified). No armed task right now. Read `AGENTS.md`; do not start a slice until armed.

## Done
- **builtin_kind, builtin_arity, boolean_operator, type_name** (batch 1) and **two_char_ops,
  closing_delimiters, infix_operators** (batch 2) — all wired to Herbert-family `.herb` owners, Python
  literals deleted, each oracle WIRED in CI.

## Remaining authorities — NOT yet armed
- **`record_field_index`, `array_mutation`** — emitter-internal lowerings; need a different referee design.
- **`lexer_keywords`, `unsupported_punctuation`** — need oracle-framework support (a reject-probe mode / the
  keyword name-position subtlety). The orchestrator owes all four referees before they can be armed.

> Residual across all slices (future, orchestrator-scoped): owners are Python-PARSED, not yet SEED-EXECUTED.
