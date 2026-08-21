#!/usr/bin/env bash
# Build and run the self-checking weight certificate with plain `rustc`.
#
#   run-certificate.sh              build ../axeyum-examples/noh_wt_certificate.rs and run it;
#                                   exit 0 only if every assertion in it passed
#   run-certificate.sh --mutants    additionally apply each mutation in mutants/ and require
#                                   that the mutated certificate FAILS, with the catcher named
#                                   in the matching .expect file
#
# The certificate has no dependencies beyond `std`, so this is the same binary
# the axeyum example produces -- the file is byte-identical.  Needs rustc with
# edition 2024 and `i128::midpoint` (1.87+); tested on 1.97.0-nightly.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$HERE/../axeyum-examples/noh_wt_certificate.rs"
MUTANTS="$HERE/mutants"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

build_and_run() {   # $1 = source file, $2 = binary name; echoes output, returns run's status
    rustc --edition 2024 -O -o "$WORK/$2" "$1" 2>"$WORK/$2.build" || {
        echo "rustc FAILED to build $1"; cat "$WORK/$2.build"; return 111
    }
    set +e
    "$WORK/$2" >"$WORK/$2.out" 2>&1
    local st=$?
    set -e
    return $st
}

echo "== certificate: noh_wt_certificate.rs (rustc, no dependencies) =="
cp "$SRC" "$WORK/noh_wt_certificate.rs"
if build_and_run "$WORK/noh_wt_certificate.rs" cert; then
    sed 's/^/  /' "$WORK/cert.out"
    grep -q "all assertions passed" "$WORK/cert.out" || {
        echo "FAIL: the certificate exited 0 without printing 'all assertions passed'"; exit 1; }
else
    echo "FAIL: the certificate did not pass"; sed 's/^/  /' "$WORK/cert.out"; exit 1
fi

[ "${1:-}" = "--mutants" ] || exit 0

echo
echo "== mutation controls: each mutant MUST fail =="
fail=0
count=0
for patch in "$MUTANTS"/*.patch; do
    name="$(basename "$patch" .patch)"
    expect_file="${patch%.patch}.expect"
    [ -f "$expect_file" ] || { echo "  FAIL  $name: no .expect file"; fail=$((fail + 1)); continue; }
    expect="$(cat "$expect_file")"
    rm -rf "$WORK/m"; mkdir -p "$WORK/m"
    cp "$SRC" "$WORK/m/noh_wt_certificate.rs"
    ( cd "$WORK/m" && patch -s -p0 <"$patch" ) || { echo "  FAIL  $name: patch did not apply"; fail=$((fail + 1)); continue; }
    count=$((count + 1))
    if build_and_run "$WORK/m/noh_wt_certificate.rs" "mut_$name"; then
        echo "  FAIL  $name: the mutated certificate PASSED -- the gate does not catch it"
        fail=$((fail + 1))
    elif grep -qF "$expect" "$WORK/mut_$name.out"; then
        echo "  ok    $name: exits nonzero, caught by: $expect"
    else
        echo "  FAIL  $name: failed, but not with the expected catcher '$expect'"
        head -3 "$WORK/mut_$name.out" | sed 's/^/         /'
        fail=$((fail + 1))
    fi
done

if [ "$count" -eq 0 ]; then
    echo "NO MUTANTS RAN -- this is a failure, not a pass."
    exit 2
fi
echo "mutation controls: $count mutants, $fail failures"
[ "$fail" -eq 0 ] || exit 1
