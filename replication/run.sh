#!/usr/bin/env bash
# Run every standalone replication check for
# "Newton over Hodge at p = 2 for 2-power-order characters on arbitrary smooth affine curves".
#
#   ./run.sh                  the quick sweep (~15 s): every check, reduced scope
#   ./run.sh --full           the scope claimed in the write-up (~2.5 min; ~3 min with --cargo)
#   ./run.sh --mutants        also run the certificate's mutation controls (+3 s)
#   ./run.sh --cargo          also build and run noh_u2_matrix.rs (needs cargo + crates.io)
#
# Exit status: 0 iff every check passed, 1 if any check failed, 2 if nothing ran.
# Every check asserts its own findings and exits nonzero on any failure, so this
# script's status depends on what the runs found, not on their completing.
#
# Requirements: python3 with sympy (see requirements.txt), rustc >= 1.87
# (edition 2024 + i128::midpoint).  No network, no axeyum, no C/C++ toolchain.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

FULL=""
MUTANTS=""
CARGO=""
for arg in "$@"; do
    case "$arg" in
        --full) FULL="--full" ;;
        --mutants) MUTANTS="1" ;;
        --cargo) CARGO="1" ;;
        -h|--help) sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "unknown argument: $arg (try --help)"; exit 2 ;;
    esac
done

RAN=0
FAILED=0
FAILED_NAMES=()
START=$SECONDS

run() {   # run <claim label> <command...>
    local label="$1"; shift
    RAN=$((RAN + 1))
    echo
    echo "-----------------------------------------------------------------------"
    echo "CLAIM: $label"
    echo "  \$ $*"
    if "$@"; then
        echo "  -> PASS"
    else
        echo "  -> FAIL (exit $?)"
        FAILED=$((FAILED + 1))
        FAILED_NAMES+=("$label")
    fi
}

PY=python3
command -v "$PY" >/dev/null || { echo "python3 not found"; exit 2; }
command -v rustc >/dev/null || { echo "rustc not found (needed for the certificate)"; exit 2; }
"$PY" -c "import sympy" 2>/dev/null || {
    echo "sympy not importable: pip install -r requirements.txt"; exit 2; }

echo "======================================================================="
echo " replication package -- Newton over Hodge at p = 2"
echo " mode: ${FULL:---quick}${MUTANTS:+ +mutants}${CARGO:+ +cargo}"
echo " python: $($PY -V 2>&1)   sympy: $($PY -c 'import sympy;print(sympy.__version__)')"
echo " rustc:  $(rustc -V)"
echo "======================================================================="

run "the from-scratch Type-2 operator U_2 is the operator (sec. 3.1)" \
    "$PY" verify-operator/check_operator.py $FULL

run "THEOREMS 1-4 and LEMMA A against that operator (sec. 3.2-3.7)" \
    "$PY" verify-theorems/check_theorems_1_4.py $FULL

run "only the repaired weight is admissible -- 11 negative controls (sec. 3.6, 4.5)" \
    "$PY" verify-theorems/check_weight_candidates.py $FULL

run "gamma = 1/6 by the independent LP route; 2/11 and 1/5 infeasible (sec. 3.7)" \
    "$PY" verify-theorems/check_lp_feasibility.py $FULL

run "the orbit-sum weight a*, the Main Lemma, and Note 7 refuted (sec. 6.2, 6.4)" \
    "$PY" verify-theorems/check_main_lemma_astar.py $FULL

run "Artin-Hasse is at the ceiling; pi = -2 refuted with a witness (sec. 6.3, 6.4)" \
    "$PY" verify-splitting-function/check_artin_hasse.py $FULL

run "no extra p = 2 loss at Witt length >= 2; p = 3, 5 controls (sec. 6.3)" \
    "$PY" verify-splitting-function/check_witt_levels.py $FULL

run "the Lubin-Tate freedom is empty at p = 2 (sec. 6.3)" \
    "$PY" verify-splitting-function/check_lubin_tate.py $FULL

run "LEMMA B: degree-3 map exists iff 3 | q-1; KM-ab rows 15, 16 (sec. 3.8.3, 4.3, 4.4)" \
    "$PY" verify-lemma-b/check_degree3_maps.py $FULL

run "LEMMA B: the explicit instance saturates Riemann-Hurwitz (sec. 3.8.5)" \
    "$PY" verify-lemma-b/check_explicit_instance.py $FULL

if [ -n "$MUTANTS" ]; then
    run "the weight certificate, plus its mutation controls (sec. 6.1)" \
        ./certificate/run-certificate.sh --mutants
else
    run "the weight certificate: Theorems 1-4 in rustc, no dependencies (sec. 6.1)" \
        ./certificate/run-certificate.sh
fi

if [ -n "$CARGO" ]; then
    if command -v cargo >/dev/null; then
        WORK="$(mktemp -d)"
        trap 'rm -rf "$WORK"' EXIT
        cp axeyum-examples/noh_u2_matrix.rs axeyum-examples/noh_wt_certificate.rs "$WORK/"
        mkdir -p "$WORK/standalone-cargo"
        cp axeyum-examples/standalone-cargo/Cargo.toml "$WORK/standalone-cargo/"
        run "the U_2 matrix / Dwork trace formula certificate (sec. 6.1, workstream 03)" \
            cargo run --release --quiet --manifest-path "$WORK/standalone-cargo/Cargo.toml" \
                      --target-dir "$WORK/target" --bin noh_u2_matrix
    else
        echo; echo "CLAIM: noh_u2_matrix.rs -- REQUESTED BUT cargo NOT FOUND"
        RAN=$((RAN + 1)); FAILED=$((FAILED + 1)); FAILED_NAMES+=("noh_u2_matrix (cargo missing)")
    fi
else
    echo
    echo "not run: axeyum-examples/noh_u2_matrix.rs (pass --cargo; needs cargo + crates.io"
    echo "         for num-bigint, num-rational, num-traits)"
fi

echo
echo "======================================================================="
echo " $RAN check groups, $FAILED failed, $((SECONDS - START)) s"
for n in "${FAILED_NAMES[@]:-}"; do [ -n "$n" ] && echo " FAILED: $n"; done
echo "======================================================================="
if [ "$RAN" -eq 0 ]; then
    echo "NOTHING RAN -- this is a failure, not a pass."
    exit 2
fi
[ "$FAILED" -eq 0 ] || exit 1
echo "ALL CHECKS PASSED"
