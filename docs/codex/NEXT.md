# NEXT — orchestrator-authored task for Codex

> **Phase: SETUP. Autonomous grinding is NOT yet armed.**
> Read `AGENTS.md` first. Only do what this file explicitly authorizes.

## Why you are not grinding yet
Dolo's current gate proves **correctness**, not **progress**. A cross-model review
showed that, left to "add a migration candidate," an agent produces green commits full
of mirrors, examples, and docs that look like progress but never delete Python. So
before any self-hosting slice, two orchestrator-owned pieces must exist:

1. `scripts/sovereignty_meter.sh` — a number that measures Python semantic authority
   still in the compiler path; a real slice must lower it.
2. `tests/oracle/` — a held-back, slice-immutable oracle that bites when a claimed
   replacement is fake or unwired.

**The orchestrator (Claude) owns and will deliver these.** A worker cannot author the
grader it is judged by.

## CURRENT AUTHORIZED TASK
**None requiring a commit yet.** Allowed now (optional, read-only):
- Read the repo and `docs/migration-candidates/` and **propose** (in a comment or a
  draft note, not a commit) which single Python-owned decision is the cleanest *first*
  one to actually wire-and-delete. Do not commit; the orchestrator will pick and arm it.

When the meter + oracle land, this file will name one concrete wire-and-delete slice
with explicit acceptance criteria. Until then: **propose, do not commit.**
