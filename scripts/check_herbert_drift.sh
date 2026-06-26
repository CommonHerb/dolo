#!/usr/bin/env bash
# check_herbert_drift.sh — has pinned Herbert moved, and does Dolo still pass against it?
#
# Cheap check: compare HERBERT.lock's pin to herbert-main's current HEAD.
# If they differ, this is a flag, NOT an auto-re-pin. The orchestrator owns pin
# decisions (AGENTS.md). Optionally, with --deep and a Herbert checkout, it runs the
# truth loop against CURRENT herbert-main to see whether Dolo's emitted subset still works.
#
# Usage:
#   scripts/check_herbert_drift.sh                 # cheap: pin-vs-HEAD only
#   scripts/check_herbert_drift.sh --deep DIR      # also run the truth loop vs DIR (current main)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=/dev/null
source "$ROOT/HERBERT.lock"

repo_url="$HERBERT_REPOSITORY"
echo "pinned commit : $HERBERT_COMMIT"

main_head="$(git ls-remote "$repo_url" refs/heads/main 2>/dev/null | awk '{print $1}')"
[[ -n "$main_head" ]] || { echo "WARN: could not read herbert-main HEAD ($repo_url)"; exit 0; }
echo "herbert-main  : $main_head"

if [[ "$main_head" == "$HERBERT_COMMIT" ]]; then
  echo "PIN CURRENT — no drift."
  exit 0
fi

echo "PIN BEHIND — herbert-main has advanced past the pin."
echo "NEEDS-SYNC: do NOT silently re-pin. Record a NEEDS-SYNC line in docs/codex/LOG.md;"
echo "            the orchestrator decides whether Dolo re-pins and whether the emitted"
echo "            subset must change."

deep=0; deepdir=""
if [[ "${1:-}" == "--deep" ]]; then deep=1; deepdir="${2:?--deep needs a Herbert checkout dir}"; fi
if [[ "$deep" == "1" ]]; then
  echo "--- deep check: running the truth loop against $deepdir (current main) ---"
  if [[ "$(git -C "$deepdir" rev-parse HEAD)" != "$main_head" ]]; then
    echo "WARN: $deepdir is not at herbert-main HEAD; deep result may not reflect drift"
  fi
  # NOTE: the truth loop pins a seed sha; against a moved Herbert the seed differs, so the
  # script's lock check will object. This deep mode is advisory — it reports whether the
  # emitted .herb still compiles+runs, for the orchestrator's sync decision.
  if HERBERT_SEED_SHA256="$(sha256sum "$deepdir/$HERBERT_SEED_PATH" | awk '{print $1}')" \
     bash "$ROOT/scripts/verify_herbert_truth.sh" --herbert-dir "$deepdir" 2>&1 | tail -5; then
    echo "DEEP: Dolo still passes against current herbert-main (subset compatible)."
  else
    echo "DEEP: Dolo BREAKS against current herbert-main — emitted subset needs orchestrator attention."
  fi
fi
exit 3
