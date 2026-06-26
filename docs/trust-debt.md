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

## Repayment Candidates

The `experiments/herbert/` programs are tiny Herbert-family implementation
candidates. Today they mirror narrow Python bootstrap compiler decisions:

- `record_field_index_candidate.herb` mirrors record-field-index selection.
  Local manifest validation compares this candidate against the parsed
  `Citizen` record fields in `examples/citizen.dolo`.
- `array_mutation_candidate.herb` mirrors the typed array and no-value mutation
  boundary used by Dolo's emitted Herbert. Local manifest validation compares
  this candidate against the emitted `tests/fixtures/array_mutation.herb`
  mutation/read shape.
- `builtin_arity_candidate.herb` mirrors the observed Herbert built-in arity
  table used by Dolo before emission. Local manifest validation compares this
  candidate against Python-owned `HERBERT_BUILTIN_ARITIES`.
- `boolean_operator_candidate.herb` mirrors the Dolo-to-Herbert boolean
  operator lowering table used by the emitter. Local manifest validation
  compares this candidate against Python-owned
  `DOLO_BOOLEAN_OPERATOR_LOWERINGS`.

They run through pinned Herbert in CI. They are not yet wired into the Dolo
compiler, so they are repayment candidates, not paid debt.

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
