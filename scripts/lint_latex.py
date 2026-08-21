# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""lint_latex.py -- run chktex over the LaTeX sources (advisory).

chktex ships with a full TeX Live and is the de-facto LaTeX linter; this
wrapper runs it with the project .chktexrc (which mutes the heuristics that
misfire on math-heavy prose). If chktex is absent it SKIPS with a note
rather than failing.

    uv run scripts/lint_latex.py            # advisory (never fails)
    uv run scripts/lint_latex.py --strict   # exit nonzero if chktex warns
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LATEX = ROOT / "latex"
CHKTEXRC = ROOT / ".chktexrc"


def sources() -> list[Path]:
    files = sorted((LATEX / "sections").glob("*.tex"))
    return files or sorted(LATEX.glob("*.tex"))


def main() -> int:
    strict = "--strict" in sys.argv[1:]
    if shutil.which("chktex") is None:
        print("lint_latex: chktex not found -- skipping (install via TeX Live).")
        return 0
    files = sources()
    if not files:
        print("lint_latex: no LaTeX sources to lint")
        return 0
    total = 0
    for tex in files:
        r = subprocess.run(["chktex", "-q", "-l", str(CHKTEXRC), str(tex)],
                           capture_output=True, text=True)
        # chktex writes warnings to stdout; CONFIG/parse errors go to stderr
        # with an "ERROR" prefix. Those are a hard failure -- otherwise a
        # broken .chktexrc reads as "clean" and the lint silently does
        # nothing, which is a false green.
        if "ERROR" in r.stderr:
            print(f"lint_latex: chktex config error (bad .chktexrc?):\n"
                  f"{r.stderr.strip()}", file=sys.stderr)
            return 1
        out = r.stdout.strip()
        if out:
            total += out.count("\n") + 1
            print(out)
    if total:
        print(f"lint_latex: {total} chktex message(s) "
              f"({'FAIL' if strict else 'advisory'})")
        return 1 if strict else 0
    print(f"lint_latex: clean ({len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
