# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""wordcount.py -- per-section and total word counts (advisory, never a gate).

Uses texcount when available (LaTeX-aware); otherwise a rough whitespace
count with commands stripped, clearly labelled as such.

    uv run scripts/wordcount.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LATEX = ROOT / "latex"


def sources() -> list[Path]:
    files = sorted((LATEX / "sections").glob("*.tex"))
    return files or sorted(LATEX.glob("*.tex"))


def texcount_total(path: Path) -> int | None:
    if shutil.which("texcount") is None:
        return None
    r = subprocess.run(["texcount", "-1", "-sum", "-merge", str(path)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    m = re.search(r"(\d+)", r.stdout)
    return int(m.group(1)) if m else None


def rough_count(path: Path) -> int:
    src = path.read_text()
    src = re.sub(r"(?<!\\)%.*", "", src)
    src = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?", " ", src)
    src = re.sub(r"[{}$&~^_\\]", " ", src)
    return len([w for w in src.split() if any(c.isalnum() for c in w)])


def main() -> int:
    files = sources()
    if not files:
        print("wordcount: no LaTeX sources found")
        return 0
    have = shutil.which("texcount") is not None
    print(f"wordcount: {'texcount' if have else 'rough (install texcount for accuracy)'}")
    total = 0
    for tex in files:
        n = texcount_total(tex) if have else None
        if n is None:
            n = rough_count(tex)
        total += n
        print(f"  {tex.name:<32} {n:>6}")
    print(f"  {'TOTAL':<32} {total:>6}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
