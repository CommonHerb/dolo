# Dolo Trust Debt

Dolo's identity is its language contract and Herbert-family destination. This
ledger names the borrowed substrate used by the current repository.

## Active Borrowed Substrate

| Substrate | Current Use | Why Allowed Now | Exit Direction |
| --- | --- | --- | --- |
| Python 3.13 standard library | Bootstrap parser, emitter, CLI, unit tests | Small, readable, dependency-free first compiler | Replace narrow pieces with Herbert-family implementation after behavior is pinned |
| Bash | Native truth harness | Expresses the Linux/x86_64 seed compile/run loop plainly | Replace with a Herbert-family verifier when the toolchain can host it |
| GitHub Actions | Public Linux/x86_64 verification | Runs the pinned Herbert seed on the platform it targets | Move toward owned CI or Herbert-native verification when available |
| Ubuntu/Linux x86_64 | Executes Herbert gen-1 seed and generated ELFs | Current seed is a Linux/x86_64 ELF | Herbert OS/native execution |
| `CommonHerb/herbert` gen-1 seed | Production Herbert compiler for the proof loop | Herbert currently treats this seed as the C-free production toolchain | Continue following Herbert's sovereignty roadmap toward textual seed hardening and OS lineage |
| macOS/Apple Silicon | Local editing and bootstrap tests | Development host only | Never treat as proof of Herbert native execution for this seed |

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
