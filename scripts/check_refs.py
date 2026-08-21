# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_refs.py -- reference, citation, and accessibility gates.

Reads the last build log (build/latex/main.log) and the LaTeX sources, and
FAILS on:

  * undefined references or citations (the classic silent-drift bug),
  * multiply-defined labels,
  * an \\includegraphics without an alt= key (arXiv HTML / screen readers),
  * a leftover TODO/FIXME/XXX marker in the prose,
  * an \\input'd section file that main.tex never references (dead section).

The last one is advisory. A missing build log is advisory too, but then this
gate has checked almost nothing -- it says so rather than printing OK.

    uv run scripts/check_refs.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LATEX = ROOT / "latex"
LOG = ROOT / "build" / "latex" / "main.log"

errors: list[str] = []
warnings: list[str] = []
checked: list[str] = []


def tex_sources() -> list[Path]:
    files = sorted((LATEX / "sections").glob("*.tex"))
    return files or sorted(LATEX.glob("*.tex"))


def check_log() -> None:
    if not LOG.exists():
        warnings.append(f"{LOG.relative_to(ROOT)} not found -- run `make pdf` first; "
                        "undefined refs were NOT checked")
        return
    text = LOG.read_text(errors="ignore")
    for name in sorted(set(re.findall(r"(?:Citation|Reference) `([^']*)' .*undefined", text))):
        errors.append(f"undefined reference/citation: {name!r}")
    for name in sorted(set(re.findall(r"multiply.?defined.*`([^']*)'", text, re.I))):
        errors.append(f"multiply-defined label: {name!r}")
    checked.append("build log (undefined refs, duplicate labels)")


def check_sources() -> None:
    files = tex_sources()
    if not files:
        warnings.append("no LaTeX sources found -- nothing checked")
        return
    for tex in files:
        src = re.sub(r"(?<!\\)%.*", "", tex.read_text())
        for m in re.finditer(r"\\includegraphics(\[[^\]]*\])?\{([^}]*)\}", src):
            if "alt=" not in (m.group(1) or ""):
                errors.append(f"{tex.name}: \\includegraphics{{{m.group(2)}}} has no "
                              "alt= text (needed for arXiv HTML/screen readers)")
        for m in re.finditer(r"\b(TODO|FIXME|XXX)\b", src):
            errors.append(f"{tex.name}: leftover {m.group(1)} marker in prose")
    checked.append(f"{len(files)} source file(s) (alt text, leftover markers)")


def check_dead_sections() -> None:
    main = LATEX / "main.tex"
    if not main.exists():
        return
    inputs = {i.split("sections/")[-1]
              for i in re.findall(r"\\(?:input|include)\{(sections/[^}]+)\}", main.read_text())}
    for tex in sorted((LATEX / "sections").glob("*.tex")):
        if tex.stem not in inputs and tex.name not in inputs:
            warnings.append(f"{tex.name}: not \\input from main.tex (dead section?)")


def main() -> int:
    check_log()
    check_sources()
    check_dead_sections()
    for w in warnings:
        print(f"check_refs: warning: {w}")
    for e in errors:
        print(f"check_refs: ERROR: {e}", file=sys.stderr)
    if errors:
        print(f"check_refs: {len(errors)} error(s)", file=sys.stderr)
        return 1
    if not checked:
        print("check_refs: nothing was checked (no sources, no build log)")
        return 0
    print("check_refs: OK -- checked " + "; ".join(checked))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
