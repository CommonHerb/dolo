#!/usr/bin/env bash
# sovereignty_meter.sh — the Dolo sovereignty meter.
#
# METER = number of compiler decisions still owned by borrowed Python (ledger status=python).
# A slice is real progress ONLY if it LOWERS this number, and a status=herbert row is only
# honored if its held-back wiring oracle is GREEN (tests/oracle/oracle_wiring.py). A
# status=herbert row whose oracle is RED = a fake/mirror/moved-literal claim -> METER INVALID.
#
# This is the acceptance gate the long-runner consults; it is NOT part of the CI unittest suite.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LEDGER="$ROOT/docs/sovereignty/ledger.tsv"
[[ -f "$LEDGER" ]] || { echo "sovereignty: ledger missing at $LEDGER" >&2; exit 2; }

python_count=0
herbert_count=0
fail=0

while IFS=$'\t' read -r id status psite cand owner oracle desc; do
    [[ -z "${id:-}" || "${id:0:1}" == "#" || "$id" == "id" ]] && continue
    case "$status" in
        python)
            python_count=$((python_count + 1))
            printf '  [python]  %s\n' "$id"
            ;;
        herbert)
            herbert_count=$((herbert_count + 1))
            if python3 "$ROOT/tests/oracle/oracle_wiring.py" "$id" >/dev/null 2>&1; then
                printf '  [WIRED ]  %s\n' "$id"
            else
                printf '  [FAKE! ]  %s  -- status=herbert but the wiring oracle is RED (mirror / moved literal / unwired)\n' "$id"
                fail=1
            fi
            ;;
        *)
            printf '  [?     ]  %s  (status=%s)\n' "$id" "$status"
            ;;
    esac
done < "$LEDGER"

echo "----------------------------------------------------------------"
echo "SOVEREIGNTY METER (Python-owned decisions still on the path) = ${python_count}"
echo "  herbert-owned (oracle-verified): ${herbert_count}"
if [[ $fail -ne 0 ]]; then
    echo "METER INVALID: a status=herbert row failed its wiring oracle. Reverting that flip is required." >&2
    exit 1
fi
exit 0
