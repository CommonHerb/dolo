#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILE="${PROFILE:-herbert-x86}"
HERBERT_DIR="${HERBERT_DIR:-../herbert}"
COLIMA_STATE_DIR="${COLIMA_STATE_DIR:-}"
STOP_GRACE_SECONDS="${STOP_GRACE_SECONDS:-20}"

usage() {
    printf 'usage: %s [--profile NAME] [--herbert-dir PATH]\n' "$0" >&2
}

note() {
    printf '%s\n' "$1"
}

warn() {
    printf 'WARN: %s\n' "$1" >&2
}

print_diagnostics() {
    warn "Colima profile $PROFILE did not complete Dolo's local Herbert truth loop"
    warn "inspect: $COLIMA_STATE_DIR/ha.stderr.log"
    warn "inspect: $COLIMA_STATE_DIR/serial.log"
}

profile_is_running() {
    colima list 2>/dev/null | awk -v profile="$PROFILE" '$1 == profile { print $2 }' | grep -qx Running
}

run_stop_command() {
    local mode="$1"
    local second
    local stop_pid
    local label="colima stop"

    if [[ "$mode" = "force" ]]; then
        label="colima stop -f"
        colima stop -f "$PROFILE" >/dev/null 2>&1 &
    else
        colima stop "$PROFILE" >/dev/null 2>&1 &
    fi

    stop_pid="$!"
    for ((second = 0; second < STOP_GRACE_SECONDS; second++)); do
        if ! kill -0 "$stop_pid" 2>/dev/null; then
            wait "$stop_pid" 2>/dev/null || true
            return
        fi
        sleep 1
    done

    if kill -0 "$stop_pid" 2>/dev/null; then
        warn "$label $PROFILE timed out after ${STOP_GRACE_SECONDS}s; terminating cleanup command"
        kill "$stop_pid" 2>/dev/null || true
        sleep 1
        kill -9 "$stop_pid" 2>/dev/null || true
        wait "$stop_pid" 2>/dev/null || true
    fi
}

stop_profile() {
    run_stop_command "" || true
    if profile_is_running; then
        warn "Colima profile $PROFILE still running after graceful stop; forcing stop"
        run_stop_command "force" || true
    fi
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --profile)
            [[ $# -ge 2 ]] || { usage; exit 2; }
            PROFILE="$2"
            shift 2
            ;;
        --herbert-dir)
            [[ $# -ge 2 ]] || { usage; exit 2; }
            HERBERT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            usage
            exit 2
            ;;
    esac
done

COLIMA_STATE_DIR="${COLIMA_STATE_DIR:-$HOME/.colima/_lima/colima-$PROFILE}"

trap stop_profile EXIT

note "Starting Colima profile $PROFILE for Dolo Herbert truth loop"
if ! colima start "$PROFILE"; then
    print_diagnostics
    exit 1
fi

if ! colima -p "$PROFILE" ssh -- bash -lc "cd \"$ROOT\" && PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir \"$HERBERT_DIR\""; then
    print_diagnostics
    exit 1
fi

note "Dolo Herbert truth loop passed through Colima profile $PROFILE"
