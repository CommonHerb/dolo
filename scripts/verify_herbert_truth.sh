#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERBERT_DIR="${HERBERT_DIR:-}"

usage() {
    printf 'usage: %s --herbert-dir PATH\n' "$0" >&2
}

fail() {
    printf 'FAIL: dolo Herbert truth (%s)\n' "$1" >&2
    exit 1
}

note() {
    printf '%s\n' "$1"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --herbert-dir)
            [[ $# -ge 2 ]] || { usage; fail "missing --herbert-dir value"; }
            HERBERT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            usage
            fail "unknown argument $1"
            ;;
    esac
done

[[ -n "$HERBERT_DIR" ]] || { usage; fail "Herbert checkout path is required"; }

# shellcheck source=/dev/null
source "$ROOT/HERBERT.lock"

[[ "$(uname -s)" == "Linux" ]] || fail "requires Linux/x86_64; this host is $(uname -s)/$(uname -m)"
case "$(uname -m)" in
    x86_64|amd64) ;;
    *) fail "requires Linux/x86_64; this host is $(uname -s)/$(uname -m)" ;;
esac

[[ -d "$HERBERT_DIR/.git" ]] || fail "Herbert checkout missing at $HERBERT_DIR"
got_commit="$(git -C "$HERBERT_DIR" rev-parse HEAD)"
[[ "$got_commit" == "$HERBERT_COMMIT" ]] || fail "Herbert commit $got_commit does not match pin $HERBERT_COMMIT"

seed="$HERBERT_DIR/$HERBERT_SEED_PATH"
[[ -f "$seed" ]] || fail "Herbert seed missing at $seed"
got_seed="$(sha256sum "$seed" | awk '{print $1}')"
[[ "$got_seed" == "$HERBERT_SEED_SHA256" ]] || fail "Herbert seed sha256 $got_seed does not match pin $HERBERT_SEED_SHA256"

manifest="$ROOT/tests/fixtures/executable_manifest.tsv"
[[ -f "$manifest" ]] || fail "manifest missing at $manifest"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
compiler="$tmp/herbert-gen1"
cp "$seed" "$compiler"
chmod +x "$compiler"

case_count=0
while IFS=$'\t' read -r source_rel herb_rel stdout_rel extra; do
    [[ -z "${source_rel:-}" || "${source_rel:0:1}" == "#" ]] && continue
    [[ -z "${extra:-}" ]] || fail "manifest row has too many fields: $source_rel"

    source_path="$ROOT/$source_rel"
    herb_golden="$ROOT/$herb_rel"
    stdout_expected="$ROOT/$stdout_rel"
    [[ -f "$source_path" ]] || fail "source missing: $source_rel"
    [[ -f "$herb_golden" ]] || fail "Herbert golden missing: $herb_rel"
    [[ -f "$stdout_expected" ]] || fail "stdout golden missing: $stdout_rel"

    case_count=$((case_count + 1))
    stem="$(basename "${source_rel%.dolo}")"
    generated="$tmp/$stem.herb"
    run_dir="$tmp/$stem.run"
    mkdir -p "$run_dir"

    PYTHONPATH="$ROOT/src" python3 -m dolo.cli "$source_path" >"$generated"
    if ! cmp -s "$generated" "$herb_golden"; then
        diff -u "$herb_golden" "$generated" >&2 || true
        fail "$source_rel no longer matches committed Herbert golden"
    fi

    (
        cd "$run_dir"
        "$compiler" <"$generated" >compile.out 2>compile.err
    ) || fail "$source_rel failed during Herbert seed compile"

    [[ -f "$run_dir/a.out" ]] || fail "$source_rel produced no a.out: $(head -1 "$run_dir/compile.out" 2>/dev/null) $(head -1 "$run_dir/compile.err" 2>/dev/null)"
    magic="$(od -An -tx1 -N4 "$run_dir/a.out" | tr -d ' \n')"
    [[ "$magic" == "7f454c46" ]] || fail "$source_rel produced non-ELF a.out (magic=$magic)"
    chmod +x "$run_dir/a.out"

    if command -v timeout >/dev/null 2>&1; then
        timeout 60s "$run_dir/a.out" >"$run_dir/stdout" 2>"$run_dir/stderr"
    else
        "$run_dir/a.out" >"$run_dir/stdout" 2>"$run_dir/stderr"
    fi
    [[ ! -s "$run_dir/stderr" ]] || fail "$source_rel wrote stderr: $(head -1 "$run_dir/stderr")"
    if ! cmp -s "$run_dir/stdout" "$stdout_expected"; then
        diff -u "$stdout_expected" "$run_dir/stdout" >&2 || true
        fail "$source_rel native stdout differed from expected output"
    fi

    note "PASS: $source_rel -> Herbert -> native stdout matched $stdout_rel"
done <"$manifest"

[[ "$case_count" -gt 0 ]] || fail "manifest contained no executable examples"
note "PASS: $case_count Dolo executable example(s) ran through pinned Herbert $HERBERT_COMMIT"
