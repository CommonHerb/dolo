# NEXT — orchestrator-authored task for Codex

> **Phase: BATCH 3 ARMED (proposed).** Two referees are now authored and bite-proven in
> `tests/oracle/oracle_wiring.py`: **`record_field_index`** and **`array_mutation`**. Each is a
> per-program COMPUTATION/SHAPE authority (not a static table), so it has a dedicated grader. Both
> currently read **RED** against the production Python state (correct — unwired). Your slice is to
> WIRE each genuinely so its oracle flips to GREEN and the sovereignty meter drops 2 -> 0.
>
> Read `AGENTS.md` first. **NEVER edit `tests/oracle/*`** — those graders judge you. Do them as TWO
> separable slices (each lowers the meter by exactly 1), or one batch; either way each must pass its
> oracle, `make`/unittest must stay green, and you STOP at the slice boundary.

## Slice A — `record_field_index`  (oracle: `oracle_wiring.py record_field_index`)
The emitter currently computes the field index INLINE in Python: `record.fields.index(field.value)`
(`src/dolo/emitter.py` `_emit_field_access`). This is a per-program computation (the index is the
position of the field NAME in *this* record's declared field tuple), so the referee does NOT grade a
table — it grades EXECUTION-EQUIVALENCE against the on-disk owner's algorithm.

**Genuine-wiring contract (what GREEN requires):**
- Rewrite `experiments/herbert/record_field_index_candidate.herb` into a GENERAL positional search with
  NO baked field names, e.g. `field_index(fields, name)` -> `search(fields, name, 0)` with a recursive
  `if empty / if equal(first,name) / else search(rest, name, plus(acc,1))`.
- Add to `src/dolo/herbert_surface.py` a GENERIC Herbert-subset EVALUATOR exposed as
  `record_field_index(fields, name) -> int | None`: at import, `load_record_field_index_owner()` parses
  the owner and raises if it declares no `field_index`; the boundary then EVALUATES whatever owner is on
  disk over (fields, name), supporting only `if / equal / empty / first / rest / plus / return / call`.
  **No `.index`, no `enumerate`, no Python position-search anywhere on the live path.** The positional
  RULE lives in the `.herb`; Python supplies only the owner-agnostic interpreter.
- In `emitter.py` replace the inline `.index` with `record_field_index(record.fields, field.value)`
  (None -> the existing "record … has no field" error), and import the boundary.
- Flip the ledger row to `status=herbert`, `herbert_owner=experiments/herbert/record_field_index_candidate.herb`.

**The referee is forge-proof against finite-scalar shims** (it bite-proved RED on all of these): a
`_BASE + .index` shadow, a `_BASE + _STEP*.index` two-scalar copy, a flat name->index dict, an
oracle-fitted hardcoded-name owner, and a dead/shadow mirror that keeps inline `.index`. CHECK-X
installs oracle-generated **step!=1** and **content-weighted** owners and binds the emitted value to the
oracle's closed-form evaluation of THAT owner — only a real generic evaluator tracks them. Do not ship a
`.index`+offset shim; it will read RED.

## Slice B — `array_mutation`  (oracle: `oracle_wiring.py array_mutation`)
`_emit_do_expr` (`src/dolo/emitter.py`) owns the do-statement lowering SHAPE in Python: D4 void-gating
(value built-ins rejected, void required), D5 exactly-one-call, D1 the `do` keyword. The referee binds
ALL of D1+D4+D5 (a keyword-only move reads RED).

**Genuine-wiring contract (what GREEN requires):**
- Add `experiments/herbert/array_mutation_shape_candidate.herb` declaring the SHAPE data:
  `do_admits_kind(kind)` (void->1, value->0 — NON-constant), `do_statement_call_count()` (->1),
  `do_statement_keyword()` (->"do"), plus a tagged-tuple `main()`.
- Add `load_array_mutation_shape()` + extractors in `herbert_surface.py` producing module-level
  `_ARRAY_MUTATION_DO_ADMIT_KINDS` (frozenset of admitted kinds), `_ARRAY_MUTATION_DO_CALL_COUNT` (int),
  `_ARRAY_MUTATION_DO_KEYWORD` (str), each raising on an empty/missing-required-function owner; plus
  call-time accessors `array_mutation_do_admits(kind)` / `array_mutation_do_call_count()` /
  `array_mutation_do_keyword()`.
- Rewrite `_emit_do_expr` to a GENERIC procedure: count top-level calls and require
  `== array_mutation_do_call_count()` (replaces D2+D5); compute `kind = herbert_builtin_kind(target)` and
  require `array_mutation_do_admits(kind)` (replaces D3+D4); then re-emit. `_emit_block` reads
  `array_mutation_do_keyword()`. DELETE the inline `do ` / value-reject / `!= void` / `close_index != len-1`
  literals.
- Flip the ledger row to `status=herbert`, `herbert_owner=experiments/herbert/array_mutation_shape_candidate.herb`.

**The referee bite-proved RED** on: a keyword-only moved literal (D4/D5 left inline), an admit-all
frozen-constant owner (CHECK-0 negative probe `do count` wrongly accepts), a dead/shadow mirror (bindings
loaded but emitter ignores them), and authority-laundering onto an already-paid owner. The structural
poison matrix requires EACH binding's verdict to MOVE; CHECK-0 forces real `do count`/`do helper`/
two-call/non-call REJECT; CHECK-3 perturbs owner TEXT per input.

## Earned-slice checklist (per AGENTS.md, ALL required, per slice)
1. Lowers `scripts/sovereignty_meter.sh` by 1 (the row flips to `[WIRED]`).
2. Wired into the real compiler path; the Python piece it replaces is DELETED (remove-it-breaks proven).
3. Its held-back oracle (`oracle_wiring.py <id>`) is GREEN — you did NOT author it and MUST NOT edit it.
4. `verify_herbert_truth.sh` / the unittest suite stay green (update `tests/fixtures/*.stdout` + the
   migration manifest only as needed for the unrelated native gate — the oracle ignores them).
5. Exactly one slice, then STOP.

## Referee residuals (cross-model audit, Codex gpt-5.5) — what the oracle does NOT catch alone
- **AM escape-hatch:** a forge `if binding != DEFAULT: use_owner else: inline_python` keeps Python
  load-bearing on the normal path while every poison/edit moves the verdict. CHECK-1/CHECK-3 prove the
  binding is *connected*, not that the default path is binding-*sourced* — no behavioral poison can
  distinguish them. **The orchestrator closes this at reconcile** by source-verifying the inline do-policy
  is DELETED (criterion #2). Codex: do not hatch — delete the inline literals.
- **RFI:** CHECK-X catches every finite-scalar / static-table / single-template shim, including a Python
  matcher that pre-ports base/step/single-heavy (it diverges on the variable-structure multiweight owner).
  A Python program general enough to evaluate *any* owner in the subset passes — but that IS the generic
  evaluator the contract requires, not a forge.
- **AM scope:** D2 (call-required) / D3 (Dolo-fn reject) verdicts are forced by CHECK-0 but have no
  independent owner knob; the genuine wiring subsumes them into D4/D5. The authority is the SHAPE = D1+D4+D5.

## Still owed by the orchestrator (NOT armed)
- **`lexer_keywords`, `unsupported_punctuation`** — still need oracle-framework support (reject-probe mode /
  keyword name-position subtlety).
- Residual across all slices (future, orchestrator-scoped): owners are Python-PARSED, not yet SEED-EXECUTED.
