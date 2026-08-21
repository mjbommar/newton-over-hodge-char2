#!/usr/bin/env bash
# Replication for "Newton over Hodge at p = 2 for 2-power-order characters on
# arbitrary smooth affine curves".  Two layers, in this order:
#
#   LAYER 1  PRIMARY -- AXEYUM.  The computations of the paper, run from the
#            axeyum reasoning stack at a pinned commit, as
#            `cargo run --release -p axeyum-cas --example ...`.  Both examples
#            are self-checking: they assert their own findings and exit
#            nonzero on any failure.
#   LAYER 2  INDEPENDENT CROSS-CHECK.  A from-scratch python/rustc
#            reimplementation that shares no line of code with axeyum, written
#            to disagree if layer 1 is wrong.
#
# Untrusted fast search, trusted small checking: layer 1 computes, layer 2
# checks it from the definitions by a different route.
#
#   ./run.sh                     both layers, quick scope   (~32 s cold, ~13 s warm)
#   ./run.sh --full              both layers, published scope (~3.5 min)
#   ./run.sh --mutants           + the cross-check's mutation controls (+3 s)
#   ./run.sh --axeyum-only       layer 1 only
#   ./run.sh --crosscheck-only   layer 2 only (this script's pre-2026-08-21 default)
#   ./run.sh --offline           never clone; use a local axeyum or the vendored copies
#
# Exit status: 0 iff every check passed, 1 if any check failed, 2 if nothing
# ran.  Every check asserts its own findings, so this script's status depends
# on what the runs found, not on their completing.
#
# Requirements
#   layer 1: cargo/rustc (1.88+), and either a local axeyum checkout that
#            contains the pinned commit (point AXEYUM_DIR at it) or network
#            access to clone it once into replication/.axeyum-pin/ (gitignored,
#            ~680 MB tree, ~20 s to build the two examples).  No C/C++
#            toolchain, no solver, no CAS.
#   layer 2: python3 with sympy (see requirements.txt), rustc >= 1.87
#            (edition 2024 + i128::midpoint).  No network, no axeyum.
#
# Environment overrides
#   AXEYUM_DIR    a local axeyum checkout (or an already-extracted pinned tree)
#   AXEYUM_REPO   clone URL         (default: https://github.com/mjbommar/axeyum)
#   AXEYUM_BRANCH branch to clone   (default: agent/noh-p2-axeyum-examples)
#   AXEYUM_PIN    commit to require (default: the pin below)
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Absolute, resolved BEFORE the cd: --help reads this file back, and "$0" is a
# relative path that stops resolving the moment we change directory.
SELF="$HERE/$(basename "${BASH_SOURCE[0]}")"
cd "$HERE"

# ----------------------------------------------------------------- the pin
AXEYUM_REPO="${AXEYUM_REPO:-https://github.com/mjbommar/axeyum}"
AXEYUM_BRANCH="${AXEYUM_BRANCH:-agent/noh-p2-axeyum-examples}"
AXEYUM_PIN="${AXEYUM_PIN:-75663ef85c2dad4390a3b6d77361919a914642a9}"

# SHA-256 of the two paper-critical examples AT THAT COMMIT.  The copies under
# axeyum-examples/ must equal these byte for byte; the check below is what ties
# this repository's vendored copies to the axeyum pin, and it fails loudly if
# either side drifts.
SHA_U2="6b3806fda10bb88eab16ecfb4ffaa27cf58c33bec0d41c00836a208174673f26"
SHA_WT="39b4dd825a5c6658e490c2629a81904c665840923e8f4e77f391d1db89be8053"

PIN_DIR="$HERE/.axeyum-pin"
PIN_TREE="$PIN_DIR/axeyum"
EX_REL="crates/axeyum-cas/examples"

# ----------------------------------------------------------------- arguments
FULL=""
MUTANTS=""
DO_AXEYUM=1
DO_CROSSCHECK=1
OFFLINE=""
for arg in "$@"; do
    case "$arg" in
        --full) FULL="--full" ;;
        --mutants) MUTANTS="1" ;;
        --axeyum-only) DO_CROSSCHECK="" ;;
        --crosscheck-only) DO_AXEYUM="" ;;
        --offline) OFFLINE="1" ;;
        --cargo) echo "note: --cargo is accepted for compatibility and does nothing;" \
                      "the axeyum layer is now the default primary path." ;;
        -h|--help) sed -n '2,41p' "$SELF" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *) echo "unknown argument: $arg (try --help)"; exit 2 ;;
    esac
done

RAN=0
FAILED=0
FAILED_NAMES=()
START=$SECONDS
T_AXEYUM=0
T_CROSS=0

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

fail_check() {   # fail_check <label> <message...>
    local label="$1"; shift
    RAN=$((RAN + 1))
    echo
    echo "-----------------------------------------------------------------------"
    echo "CLAIM: $label"
    echo "  -> FAIL: $*"
    FAILED=$((FAILED + 1))
    FAILED_NAMES+=("$label")
}

sha256_of() { sha256sum "$1" 2>/dev/null | cut -d' ' -f1; }

echo "======================================================================="
echo " Newton over Hodge at p = 2 -- replication"
echo "======================================================================="
echo
echo " This package runs in two layers, and the order is the point."
echo
echo "   LAYER 1  PRIMARY: AXEYUM.  The paper's computations are performed by"
echo "            the axeyum reasoning stack (https://github.com/mjbommar/axeyum),"
echo "            pinned at commit ${AXEYUM_PIN:0:12} on branch"
echo "            $AXEYUM_BRANCH."
echo "            Two self-checking examples in crates/axeyum-cas/examples/:"
echo "              noh_u2_matrix        the exact U_2 operator at p = 2, anchored"
echo "                                   to the Dwork trace formula by from-scratch"
echo "                                   point counts over F_{2^k}"
echo "              noh_wt_certificate   Theorems 1-4 and Lemma A of the paper"
echo
echo "   LAYER 2  INDEPENDENT CROSS-CHECK.  A from-scratch reimplementation in"
echo "            python/sympy and plain rustc that SHARES NO CODE WITH AXEYUM."
echo "            It exists to disagree with layer 1 if layer 1 is wrong."
echo
echo " Untrusted fast search, trusted small checking: layer 1 computes; layer 2"
echo " re-derives the same objects from the definitions by a different route."
echo " Both layers assert their findings and exit nonzero on failure, so this"
echo " script's status depends on what the runs found, not on their completing."
echo
echo " mode: ${FULL:---quick}${MUTANTS:+ +mutants}${DO_AXEYUM:+ +axeyum}${DO_CROSSCHECK:+ +crosscheck}"
echo "======================================================================="

# =======================================================================
# LAYER 1 -- PRIMARY: AXEYUM
# =======================================================================
AXEYUM_MODE=""       # "workspace" (real axeyum build) or "vendored" (degraded)
AXEYUM_TREE=""
AXEYUM_SRC=""        # human-readable provenance of the tree

resolve_axeyum_tree() {
    local d

    # (0) an already-materialised pinned tree, or one the caller points at.
    for d in "${AXEYUM_DIR:-}" "$PIN_TREE"; do
        [ -n "$d" ] || continue
        if [ -f "$d/$EX_REL/noh_u2_matrix.rs" ] \
           && [ "$(sha256_of "$d/$EX_REL/noh_u2_matrix.rs")" = "$SHA_U2" ] \
           && [ "$(sha256_of "$d/$EX_REL/noh_wt_certificate.rs")" = "$SHA_WT" ] \
           && [ -f "$d/Cargo.lock" ]; then
            AXEYUM_TREE="$d"
            AXEYUM_SRC="existing tree at $d (example hashes match the pin)"
            return 0
        fi
    done

    # (1) a git checkout that CONTAINS the pinned commit -- extract it, never
    #     build inside somebody else's worktree.
    local candidates=("${AXEYUM_DIR:-}" "$HERE/../../axeyum" "$HERE/../../../axeyum")
    for d in "${candidates[@]}"; do
        [ -n "$d" ] && [ -d "$d/.git" ] || continue
        git -C "$d" cat-file -e "${AXEYUM_PIN}^{commit}" 2>/dev/null || continue
        echo "  local axeyum checkout $d contains the pin; extracting it"
        rm -rf "$PIN_TREE"; mkdir -p "$PIN_TREE"
        git -C "$d" archive "$AXEYUM_PIN" | tar -x --touch -C "$PIN_TREE" || return 1
        AXEYUM_TREE="$PIN_TREE"
        AXEYUM_SRC="git archive $AXEYUM_PIN from local checkout $d"
        return 0
    done

    # (2) clone the pinned branch.
    if [ -n "$OFFLINE" ]; then
        echo "  --offline given and no local axeyum checkout contains the pin"
        return 1
    fi
    echo "  no local axeyum checkout contains the pin; cloning $AXEYUM_REPO"
    echo "  (branch $AXEYUM_BRANCH, --depth 1, into $PIN_TREE)"
    rm -rf "$PIN_TREE"; mkdir -p "$PIN_DIR"
    git clone --depth 1 --branch "$AXEYUM_BRANCH" "$AXEYUM_REPO" "$PIN_TREE" \
        >"$PIN_DIR/clone.log" 2>&1 || {
            echo "  clone FAILED; last lines of $PIN_DIR/clone.log:"
            tail -5 "$PIN_DIR/clone.log" | sed 's/^/    /'
            return 1
        }
    local head
    head="$(git -C "$PIN_TREE" rev-parse HEAD)"
    if [ "$head" != "$AXEYUM_PIN" ]; then
        echo "  PIN MISMATCH: branch $AXEYUM_BRANCH is at $head, expected $AXEYUM_PIN"
        return 1
    fi
    AXEYUM_TREE="$PIN_TREE"
    AXEYUM_SRC="git clone --depth 1 --branch $AXEYUM_BRANCH $AXEYUM_REPO @ $AXEYUM_PIN"
    return 0
}

if [ -n "$DO_AXEYUM" ]; then
    A_START=$SECONDS
    echo
    echo "#######################################################################"
    echo "# LAYER 1 -- PRIMARY: AXEYUM  (the paper's computations)"
    echo "#   repo   $AXEYUM_REPO"
    echo "#   branch $AXEYUM_BRANCH"
    echo "#   commit $AXEYUM_PIN"
    echo "#######################################################################"

    if ! command -v cargo >/dev/null; then
        fail_check "AXEYUM layer: cargo toolchain present" \
            "cargo not found. Install Rust (1.88+), or run ./run.sh --crosscheck-only" \
            "for the independent layer alone."
    else
        echo
        echo "cargo: $(cargo -V 2>&1)"
        echo "resolving the pinned axeyum tree..."
        if resolve_axeyum_tree; then
            AXEYUM_MODE="workspace"
            echo "  using: $AXEYUM_SRC"
        else
            AXEYUM_MODE="vendored"
            echo
            echo "  !! DEGRADED: the pinned axeyum workspace could not be obtained."
            echo "  !! Falling back to the VENDORED COPIES of the same two example"
            echo "  !! sources under axeyum-examples/, built through a three-crate"
            echo "  !! manifest instead of the axeyum workspace.  The source files"
            echo "  !! are byte-identical to the pin (verified by SHA-256 below),"
            echo "  !! so the computation is the same one; only the build route is not."
        fi

        # -- 1.1 the pin binding.  This is a finding, not a formality: it is the
        #        only thing that makes "the vendored copies ARE the axeyum
        #        examples" a checked statement rather than a claim in prose.
        RAN=$((RAN + 1))
        echo
        echo "-----------------------------------------------------------------------"
        echo "CLAIM: axeyum-examples/*.rs are byte-identical to the pinned axeyum examples"
        h1="$(sha256_of "$HERE/axeyum-examples/noh_u2_matrix.rs")"
        h2="$(sha256_of "$HERE/axeyum-examples/noh_wt_certificate.rs")"
        bind_ok=1
        [ "$h1" = "$SHA_U2" ] || { echo "  noh_u2_matrix.rs      sha256 $h1 != $SHA_U2"; bind_ok=0; }
        [ "$h2" = "$SHA_WT" ] || { echo "  noh_wt_certificate.rs sha256 $h2 != $SHA_WT"; bind_ok=0; }
        if [ "$AXEYUM_MODE" = "workspace" ]; then
            for pair in "noh_u2_matrix.rs $SHA_U2" "noh_wt_certificate.rs $SHA_WT"; do
                set -- $pair
                hp="$(sha256_of "$AXEYUM_TREE/$EX_REL/$1")"
                if [ "$hp" != "$2" ]; then
                    echo "  pinned tree $EX_REL/$1 sha256 $hp != $2"; bind_ok=0
                fi
            done
        fi
        if [ "$bind_ok" = 1 ]; then
            echo "  noh_u2_matrix.rs      $SHA_U2"
            echo "  noh_wt_certificate.rs $SHA_WT"
            echo "  -> PASS"
        else
            echo "  -> FAIL (the vendored copies and the axeyum pin have drifted apart)"
            FAILED=$((FAILED + 1)); FAILED_NAMES+=("axeyum pin binding")
        fi

        # -- 1.2/1.3 the two self-checking examples.
        if [ "$AXEYUM_MODE" = "workspace" ]; then
            run "AXEYUM: the exact U_2 operator, Dwork-trace anchored (sec. 6.1, workstream 03)" \
                cargo run --release --quiet --manifest-path "$AXEYUM_TREE/Cargo.toml" \
                    --locked -p axeyum-cas --example noh_u2_matrix
            run "AXEYUM: the weight certificate -- Theorems 1-4 and Lemma A (sec. 6.1)" \
                cargo run --release --quiet --manifest-path "$AXEYUM_TREE/Cargo.toml" \
                    --locked -p axeyum-cas --example noh_wt_certificate
        else
            VWORK="$PIN_DIR/vendored"
            mkdir -p "$VWORK"
            run "AXEYUM (vendored build): the exact U_2 operator, Dwork-trace anchored" \
                cargo run --release --quiet \
                    --manifest-path "$HERE/axeyum-examples/standalone-cargo/Cargo.toml" \
                    --target-dir "$VWORK/target" --bin noh_u2_matrix
            run "AXEYUM (vendored build): the weight certificate -- Theorems 1-4 and Lemma A" \
                cargo run --release --quiet \
                    --manifest-path "$HERE/axeyum-examples/standalone-cargo/Cargo.toml" \
                    --target-dir "$VWORK/target" --bin noh_wt_certificate
        fi
    fi
    T_AXEYUM=$((SECONDS - A_START))
else
    echo
    echo "LAYER 1 (axeyum) SKIPPED by --crosscheck-only."
fi

# =======================================================================
# LAYER 2 -- INDEPENDENT CROSS-CHECK
# =======================================================================
if [ -n "$DO_CROSSCHECK" ]; then
    C_START=$SECONDS
    echo
    echo "#######################################################################"
    echo "# LAYER 2 -- INDEPENDENT CROSS-CHECK (from-scratch; shares no code with"
    echo "#            axeyum).  python3/sympy + plain rustc, exact rational"
    echo "#            arithmetic throughout, no floating point in any assertion."
    echo "#            These programs re-derive the same objects from the"
    echo "#            definitions; they are the check on layer 1, not a rerun of it."
    echo "#######################################################################"

    PY=python3
    if ! command -v "$PY" >/dev/null; then
        fail_check "CROSS-CHECK layer: python3 present" "python3 not found"
    elif ! command -v rustc >/dev/null; then
        fail_check "CROSS-CHECK layer: rustc present" "rustc not found (needed for the certificate)"
    elif ! "$PY" -c "import sympy" 2>/dev/null; then
        fail_check "CROSS-CHECK layer: sympy importable" \
            "sympy not importable: pip install -r requirements.txt"
    else
        echo
        echo " python: $($PY -V 2>&1)   sympy: $($PY -c 'import sympy;print(sympy.__version__)')"
        echo " rustc:  $(rustc -V)"

        run "CROSS-CHECK: the from-scratch Type-2 operator U_2 is the operator (sec. 3.1)" \
            "$PY" verify-operator/check_operator.py $FULL

        run "CROSS-CHECK: THEOREMS 1-4 and LEMMA A against that operator (sec. 3.2-3.7)" \
            "$PY" verify-theorems/check_theorems_1_4.py $FULL

        run "CROSS-CHECK: only the repaired weight is admissible -- 11 negative controls (sec. 3.6, 4.5)" \
            "$PY" verify-theorems/check_weight_candidates.py $FULL

        run "CROSS-CHECK: gamma = 1/6 by the independent LP route; 2/11 and 1/5 infeasible (sec. 3.7)" \
            "$PY" verify-theorems/check_lp_feasibility.py $FULL

        run "CROSS-CHECK: the orbit-sum weight a*, the Main Lemma, and Note 7 refuted (sec. 6.2, 6.4)" \
            "$PY" verify-theorems/check_main_lemma_astar.py $FULL

        run "CROSS-CHECK: Artin-Hasse is at the ceiling; pi = -2 refuted with a witness (sec. 6.3, 6.4)" \
            "$PY" verify-splitting-function/check_artin_hasse.py $FULL

        run "CROSS-CHECK: no extra p = 2 loss at Witt length >= 2; p = 3, 5 controls (sec. 6.3)" \
            "$PY" verify-splitting-function/check_witt_levels.py $FULL

        run "CROSS-CHECK: the Lubin-Tate freedom is empty at p = 2 (sec. 6.3)" \
            "$PY" verify-splitting-function/check_lubin_tate.py $FULL

        run "CROSS-CHECK: LEMMA B: degree-3 map exists iff 3 | q-1; KM-ab rows 15, 16 (sec. 3.8.3, 4.3, 4.4)" \
            "$PY" verify-lemma-b/check_degree3_maps.py $FULL

        run "CROSS-CHECK: LEMMA B: the explicit instance saturates Riemann-Hurwitz (sec. 3.8.5)" \
            "$PY" verify-lemma-b/check_explicit_instance.py $FULL

        if [ -n "$MUTANTS" ]; then
            run "CROSS-CHECK: the weight certificate in plain rustc, plus its mutation controls (sec. 6.1)" \
                ./certificate/run-certificate.sh --mutants
        else
            run "CROSS-CHECK: the weight certificate in plain rustc, no dependencies (sec. 6.1)" \
                ./certificate/run-certificate.sh
        fi
    fi
    T_CROSS=$((SECONDS - C_START))
else
    echo
    echo "LAYER 2 (independent cross-check) SKIPPED by --axeyum-only."
fi

# =======================================================================
echo
echo "======================================================================="
echo " $RAN check groups, $FAILED failed, $((SECONDS - START)) s total"
[ -n "$DO_AXEYUM" ]     && echo "   layer 1  axeyum${AXEYUM_MODE:+ ($AXEYUM_MODE)}: ${T_AXEYUM} s"
[ -n "$DO_CROSSCHECK" ] && echo "   layer 2  independent cross-check: ${T_CROSS} s"
for n in "${FAILED_NAMES[@]:-}"; do [ -n "$n" ] && echo " FAILED: $n"; done
echo "======================================================================="
if [ "$RAN" -eq 0 ]; then
    echo "NOTHING RAN -- this is a failure, not a pass."
    exit 2
fi
[ "$FAILED" -eq 0 ] || exit 1
if [ -n "$DO_AXEYUM" ] && [ "$AXEYUM_MODE" = "workspace" ]; then
    echo "ALL CHECKS PASSED -- axeyum @ ${AXEYUM_PIN:0:12} computed it, an independent"
    echo "implementation agreed."
else
    echo "ALL CHECKS PASSED"
fi
