#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# latex/localbuild.sh -- build the paper with nothing but a TeX installation.
#
# The repository Makefile is the normal entry point: it generates
# latex/generated/metadata.tex from paper.yaml and drives latexmk with the
# build-mode flags. This script exists so that latex/ is independently
# buildable -- by a co-author, a referee, or anyone who has cloned only this
# directory -- and so that a broken build can be attributed to the sources
# rather than to the generator.
#
# It does NOT generate metadata. main.tex falls back to
# preamble/metadata-fallback.tex when generated/metadata.tex is absent, and
# uses the generated file when it is present, so this script builds either
# way and the Makefile's output wins when both exist.
#
#   ./localbuild.sh              build ../build/latex/main.pdf
#   ./localbuild.sh clean        remove the build directory
#   ./localbuild.sh chktex       run chktex over the sources
# ---------------------------------------------------------------------------
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$HERE/../build/latex"

case "${1:-build}" in
  clean)
    rm -rf "$HERE/../build"
    echo "removed $HERE/../build"
    ;;
  chktex)
    # -q quiet, -n 8 (wrong dash) and -n 36 (spacing before punctuation) are
    # off because en-dashes in page ranges and math punctuation trip them.
    # A nonzero count is reported but does not fail the script; chktex is
    # advisory, latexmk is the gate.
    find "$HERE/sections" "$HERE/preamble" "$HERE/frontmatter" \
         "$HERE/backmatter" -name '*.tex' -print0 \
      | xargs -0 chktex -q -n8 -n36 -n3 2>&1 | tee "$HERE/../build/chktex.log" || true
    ;;
  build|"")
    mkdir -p "$OUT"
    cd "$HERE"
    latexmk -pdf -interaction=nonstopmode -halt-on-error \
            -output-directory="$OUT" main.tex
    echo
    echo "built: $OUT/main.pdf"
    pdfinfo "$OUT/main.pdf" 2>/dev/null | grep -E '^(Pages|Page size)' || true
    ;;
  *)
    echo "usage: $0 [build|clean|chktex]" >&2
    exit 2
    ;;
esac
