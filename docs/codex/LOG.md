# Codex worker LOG

One line per slice or event. Newest at top. Workers append; the orchestrator reads this
on check-in. Use `NEEDS-SYNC:` to flag a Herbert pin drift that needs an orchestrator
decision.

Format: `YYYY-MM-DD  <GREEN|RED|PROPOSE|NEEDS-SYNC>  <commit-or-—>  <one line>`

---

2026-06-26  SLICE  —  builtin_kind is wired to experiments/herbert/builtin_kind_candidate.herb; emitter consults the Herbert-family owner-derived kind lookup instead of the Python value/void sets.
2026-06-26  ARMED  —  Orchestrator landed the sovereignty meter (`scripts/sovereignty_meter.sh`, reads 6) + the held-back wiring oracle (`tests/oracle/`, bite-verified) + the authority ledger. NEXT.md now arms the first earned slice: `builtin_kind`. Pin drift acknowledged (NEEDS-SYNC seen): leaving `HERBERT.lock` at e9dff22 for now — Dolo's app-level subset is unaffected by larder's kernel-only syscalls; re-pin is fold-in-time work, the orchestrator's call.
2026-06-26  SETUP  —  Channel established by the orchestrator (AGENTS.md + NEXT.md + drift check). Autonomous grinding not yet armed; awaiting orchestrator-owned meter + held-back oracle.
