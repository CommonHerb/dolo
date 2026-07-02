# NEXT — orchestrator-authored task for Codex

> **Phase: ARMED — one earned slice.** The meter was RE-BASED on 2026-07-02: the first
> foundation (9 authorities) is complete AND fully seed-executed (the pinned gen1 seed
> compiles+runs every owner — the 7 tables at import, array_mutation's shape at import,
> record_field_index PER QUERY; the Python subset interpreter is DELETED). A second
> generation of 4 Python-owned authorities is now registered (meter reads 4 — honestly:
> these were always Python-owned, now they are tracked). ONE is armed below; the other 3
> wait on orchestrator-authored referees.

## ARMED SLICE: `lexer_keywords` (meter 4 → 3)

The lexer's keyword set (`KEYWORDS` in `src/dolo/tokens.py` — record fn let do return
if else true false) is a Python-owned decision. Replace it with a Herbert-family owner,
following the exact pattern of the landed `two_char_ops` slice:

1. **Owner:** author `experiments/herbert/lexer_keywords_candidate.herb` in the
   marker-set shape the boundary already supports (see `two_char_ops_candidate.herb`):
   a `keyword(name)` lookup if-chain returning 1 for keywords / 0 otherwise, an additive
   `func key_list()` CSV of the domain, and a demo `main()` (add it to the migration
   manifest + fixture so the truth loop runs it).
2. **Boundary:** load it in `src/dolo/herbert_surface.py` via the existing
   `_seed_marker_set` seed-execution helper (`load_dolo_keywords()` +
   `is_dolo_keyword(name)` accessor + a `DOLO_KEYWORDS` frozenset if enumeration is
   needed) — fail-closed like every other authority, raising if the owner marks nothing.
3. **Wire + DELETE:** `src/dolo/tokens.py` consults the boundary; the Python
   `KEYWORDS` literal is DELETED (not renamed, not shadowed, no `if binding: ... else:
   inline` hatch — the reconcile reads your diff for exactly that shape).
4. **Ledger:** flip the `lexer_keywords` row to `status=herbert` with
   `herbert_owner=experiments/herbert/lexer_keywords_candidate.herb`.
5. **Tests:** update any test that pins the Python literal HONESTLY (rename/re-point,
   never delete an assertion to dodge a failure; 5-removed-must-equal-5-renamed is
   checked at reconcile).

**Gate (all required):** `oracle_wiring.py lexer_keywords` GREEN (its bite is already
proven against the current compiler — a mirror/moved-literal wiring will be caught) +
meter reads 3 with 10 WIRED + unittest suite OK + manifests green + native truth loop
GREEN against `../herbert-pin`. One slice, then STOP and log.

## Queued (do NOT start — referees pending, orchestrator-owned)
- `expression_keywords` (emitter, true/false-in-expression set)
- `unsupported_expression_punctuation` (emitter reject set)
- `statement_lowering_keywords` (the fn→func / let / return / if-else-end lowering map —
  the most load-bearing row of the generation)

## Standing law
- Read `AGENTS.md` first. **NEVER edit `tests/oracle/*` or `HERBERT.lock`.** Never
  silently re-pin — write a `NEEDS-SYNC` line in `LOG.md` and stop.
- Sovereignty facts (verified 2026-07-02): 9/9 first-foundation authorities are
  seed-executed; `record_field_index` is computed by the seed per query (the old
  "blocked herbert-side" note is RETIRED — the pin was never the blocker). The
  `_HerbertSubsetProgram` interpreter no longer exists; do not reintroduce Python
  evaluation of owner content anywhere.
