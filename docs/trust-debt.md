# Dolo Trust Debt

Dolo's identity is its language contract and Herbert-family destination. This
ledger names the borrowed substrate used by the current repository.

## Active Borrowed Substrate

| Substrate | Current Use | Why Allowed Now | Exit Direction |
| --- | --- | --- | --- |
| Python 3.13 standard library | Bootstrap parser, emitter, CLI, manifest validator, unit tests | Small, readable, dependency-free first compiler | Replace narrow pieces with Herbert-family implementation after behavior is pinned |
| Bash | Native truth harness | Expresses the Linux/x86_64 seed compile/run loop plainly | Replace with a Herbert-family verifier when the toolchain can host it |
| GitHub Actions | Public Linux/x86_64 verification | Runs the pinned Herbert seed on the platform it targets | Move toward owned CI or Herbert-native verification when available |
| Ubuntu/Linux x86_64 | Executes Herbert gen-1 seed and generated ELFs | Current seed is a Linux/x86_64 ELF | Herbert OS/native execution |
| `CommonHerb/herbert` gen-1 seed | Production Herbert compiler for the proof loop | Herbert currently treats this seed as the C-free production toolchain | Continue following Herbert's sovereignty roadmap toward textual seed hardening and OS lineage |
| macOS/Apple Silicon | Local editing and bootstrap tests | Development host only | Never treat as proof of Herbert native execution for this seed |

## Paid Debt — the first foundation (WIRED and SEED-EXECUTED)

All 9 first-foundation compiler authorities are Herbert-family OWNERS wired into
the live compile path, each guarded by a held-back wiring oracle
(`tests/oracle/oracle_wiring.py`, CI-gated via `scripts/sovereignty_meter.sh`),
and all 9 are EXECUTED BY THE PINNED SEED — not by Python:

- `builtin_kind`, `builtin_arity`, `boolean_operator`, `type_name`,
  `two_char_ops`, `closing_delimiters`, `infix_operators`: the seed runs each
  owner's `key_list()` + lookup if-chain at compiler import to materialize the
  table (the former `_extract_*_owner_map` Python scrapers are DELETED).
- `array_mutation`: the seed runs the shape owner's `main()` at import
  (do-keyword / void-gating / one-call policy).
- `record_field_index`: the seed compiles+runs the owner PER QUERY at compile
  time (the `_HerbertSubsetProgram` Python tree-walk interpreter and the
  Herbert-subset parser/tokenizer are DELETED).

Comparison-era wording ("candidates mirror Python-owned tables") is retired:
the Python tables no longer exist; the owners are the authority.

## Open Debt — the second generation (tracked, unpaid)

Registered in `docs/sovereignty/ledger.tsv` (status=python) on 2026-07-02:

- `lexer_keywords` — the dolo keyword set (`src/dolo/tokens.py:KEYWORDS`). ARMED.
- `expression_keywords` — true/false-in-expression set (emitter).
- `unsupported_expression_punctuation` — expression reject set (emitter).
- `statement_lowering_keywords` — the dolo→herbert statement lowering keyword
  map (fn→func, let, =, return, if/else/end, ':') — inline f-strings today.

Beyond the ledger, the LARGE untracked mass remains: the parser and emitter
ALGORITHMS themselves (~3.4k lines of Python), the manifest validator, the CLI,
and the bash truth harness. Sovereignty is not done; the meter now says so.

Each migration candidate note must name the current Python/bootstrap owner it
mirrors, link to a manifested Herbert source/stdout pair, and include a
replacement path that says how the executable proof could eventually displace
that owner. It must also state the authority boundary that keeps
executable/comparison proof distinct from compiler authority. A candidate
without all four is not precise enough to count as a trust-debt repayment path.
Table-shaped lookup candidates must also use unique lookup names before any
return map is compared with the Python/Dolo owner, so duplicate Herbert
branches cannot be hidden by dictionary-style collapse or by returns that are
skipped during extraction.

Comparison against a Dolo/Python bootstrap owner is evidence, not authority
transfer. The Dolo compiler still uses Python-owned bootstrap code until a
replacement is wired and verified through the full gates.

## Current Pin

- Herbert repository: `https://github.com/CommonHerb/herbert.git`
- Herbert commit: `e9dff2283113063f60fece453e9ab9eb16e7366a`
- Herbert seed path: `bootstrap/seed/gen1.seed`
- Herbert seed sha256:
  `8a9be3012cd3a132d2da5eb25df0b083671ff352725fdfb10504f1e7a939ce50`

## Rules For Future Debt

- New dependencies need a concrete proof benefit.
- New dependencies must not become semantic authority for Dolo.
- Every borrowed substrate must be documented where it is used.
- Replacing trust debt is better than hiding it behind nicer tooling.
