# NEXT — orchestrator-authored task queue for Codex

> **Phase: FULL-AUTO QUEUE (batch 2).** Three armed slices below. Work them **in order, one PR per slice,
> WITHOUT stopping** for approval between them — the CI **sovereignty-gate** verifies each (a green PR is a
> genuinely-wired slice). Read `AGENTS.md`. Do NOT edit `tests/oracle/*` or `HERBERT.lock`. Mark each PR
> **ready** (not draft) when its checks pass, then immediately start the next.

## How each slice works (the same shape as the 4 already landed)
1. Author the Herbert-family owner `.herb` under `experiments/herbert/` — a `func <name>(x):` **if/equal
   chain** returning the decision value (membership `1`/`0`, or the mapped string), with a sentinel fallback.
2. Make the relevant module **DERIVE** the decision from that owner (parse it, like the landed slices do),
   and **DELETE** the Python literal so it is no longer authoritative.
3. Flip the row in `docs/sovereignty/ledger.tsv` to `status=herbert` and set `herbert_owner` to the `.herb` path.
4. Accepted iff: `bash scripts/sovereignty_meter.sh` drops by one (exit 0); `python3 tests/oracle/oracle_wiring.py <id>`
   exits 0 (WIRED = poison no-op + load-bearing owner + content-driving perturbation); truth loop green; CI green.

## The queue (meter is at 5; each slice lowers it)
1. **`two_char_ops`** → `experiments/herbert/two_char_ops_candidate.herb`. The LEXER (`tokens.py`) must derive
   its greedy two-char operator set (`== != <= >= && ||`) from the owner instead of the Python `TWO_CHAR_OPS`.
2. **`closing_delimiters`** → `experiments/herbert/closing_delimiters_candidate.herb`. The PARSER (`parser.py`)
   must derive its closer→opener bracket-matching map from the owner (each entry returns the required opener string).
3. **`infix_operators`** → `experiments/herbert/infix_operators_candidate.herb`. The EMITTER must derive its
   recognized infix-operator set from the owner instead of the Python `INFIX_OPERATORS`.

When the queue is empty, **STOP and log it** in `docs/codex/LOG.md`. (Still Python but NOT yet armed:
`record_field_index` + `array_mutation` are emitter-internal logic, and `lexer_keywords` +
`unsupported_punctuation` need oracle-framework support — the orchestrator owes those referees.)

> **Residual carried across all slices (future, orchestrator-scoped):** owners are Python-PARSED, not yet
> SEED-EXECUTED. Keep the if/equal-chain `.herb` format so that deeper step stays reachable.
