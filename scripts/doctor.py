# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""doctor.py -- toolchain, packages, and drift audit.

Checks that this machine can build THIS paper.yaml's configuration, and that
the docs do not advertise machinery that does not exist:

  * the selected engine (pdflatex/xelatex/lualatex) is on PATH,
  * latexmk + the bibliography backend (bibtex or biber) are present,
  * the LaTeX packages the paper's configuration needs resolve (kpsewhich),
  * every `make <target>` named in CLAUDE.md and README.md exists in the
    Makefile (the CLAUDE.md <-> Makefile drift audit),
  * ARXIV-SUBMISSION.md still agrees with paper.yaml's title,
  * paper.yaml has no leftover placeholders,
  * advisory notes for the parts other lanes own (latex/main.tex,
    replication/run.sh) -- absence is reported, never a failure here.

    uv run scripts/doctor.py        (or: python3 scripts/doctor.py)

Exit nonzero if any hard requirement is missing.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - environment guard
    print("doctor: PyYAML is required. Run via `uv run scripts/doctor.py` "
          "(the inline script metadata pulls it in) or `pip install pyyaml`.",
          file=sys.stderr)
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parent.parent
PAPER_YAML = ROOT / "paper.yaml"
MAKEFILE = ROOT / "Makefile"
DOC_FILES = [ROOT / "CLAUDE.md", ROOT / "README.md"]
ARXIV_MD = ROOT / "ARXIV-SUBMISSION.md"
MAIN_TEX = ROOT / "latex" / "main.tex"
REPLICATION = ROOT / "replication" / "run.sh"

ok: list[str] = []
problems: list[str] = []
notes: list[str] = []

# Packages a math preprint of this shape needs. Keep in step with
# latex/preamble/ -- a stale list audits nothing.
CORE_PKGS = [
    "amsart.cls", "amsthm.sty", "amssymb.sty", "amsmath.sty",
    "mathtools.sty", "microtype.sty", "booktabs.sty", "enumitem.sty",
    "hyperref.sty", "xurl.sty", "cleveref.sty", "natbib.sty",
]
PROFILE_PKGS = {
    "lmodern": ["lmodern.sty"],
    "libertinus": ["libertinus.sty"],
    "newtx": ["newtxtext.sty", "newtxmath.sty"],
}


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def kpse(name: str) -> bool:
    if not have("kpsewhich"):
        return False
    r = subprocess.run(["kpsewhich", name], capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip() != ""


def check_toolchain(cfg: dict) -> None:
    engine = cfg["typography"]["engine"]
    for tool in (engine, "latexmk", "kpsewhich"):
        (ok if have(tool) else problems).append(
            f"{tool} {'found' if have(tool) else 'MISSING (required)'}")
    backend = "biber" if cfg["citations"]["system"] == "biblatex" else "bibtex"
    (ok if have(backend) else problems).append(
        f"{backend} {'found' if have(backend) else 'MISSING (required)'}")
    for opt, why in (("pdfinfo", "make arxiv reports page counts with it"),
                     ("chktex", "make lint skips without it"),
                     ("texcount", "make wordcount falls back to a rough count"),
                     ("uv", "scripts run under python3 without it, but then "
                            "pyyaml must be installed")):
        (ok if have(opt) else notes).append(
            f"{opt} {'found' if have(opt) else f'missing ({why})'}")


def check_packages(cfg: dict) -> None:
    if not have("kpsewhich"):
        return  # already a hard problem; do not spam one line per package
    profile = cfg["typography"]["font_profile"]
    engine = cfg["typography"]["engine"]
    pkgs = list(CORE_PKGS)
    if engine == "pdflatex":
        pkgs += PROFILE_PKGS.get(profile, [])
    else:
        pkgs += ["fontspec.sty", "unicode-math.sty"]
    missing = [p for p in sorted(set(pkgs)) if not kpse(p)]
    for p in missing:
        problems.append(f"package {p} MISSING (kpsewhich)")
    if not missing:
        ok.append(f"LaTeX packages: {len(set(pkgs))} resolve "
                  f"(engine {engine}, profile {profile})")


def check_venue_engine(cfg: dict) -> None:
    """arXiv does not accept lualatex source; flag it here, where you look
    first (make arxiv refuses it too)."""
    venue = (cfg.get("venue") or {}).get("target")
    engine = (cfg.get("typography") or {}).get("engine")
    if venue == "arxiv" and engine == "lualatex":
        problems.append(
            "venue.target=arxiv with engine=lualatex -- arXiv does not accept "
            "lualatex source; use pdflatex or xelatex")
    else:
        ok.append(f"venue/engine: {venue}/{engine} (arXiv-compatible)")


def check_makefile_drift() -> None:
    """Every `make <target>` the docs advertise must exist."""
    if not MAKEFILE.exists():
        problems.append("Makefile not found")
        return
    targets = set(re.findall(r"^([a-z][a-z-]*):", MAKEFILE.read_text(), re.M))
    total = 0
    for doc in DOC_FILES:
        if not doc.exists():
            notes.append(f"{doc.name} not found (drift audit skipped for it)")
            continue
        mentioned = set(re.findall(r"make ([a-z][a-z-]+)", doc.read_text()))
        missing = sorted(mentioned - targets)
        total += len(mentioned)
        for t in missing:
            problems.append(
                f"{doc.name} mentions `make {t}` but the Makefile has no such target")
    if total:
        ok.append(f"docs <-> Makefile: {total} target mention(s) checked")


def check_arxiv_md(cfg: dict) -> None:
    """ARXIV-SUBMISSION.md is hand-maintained here (no metadata generator),
    so it can drift from paper.yaml. The title is the cheap tripwire."""
    if not ARXIV_MD.exists():
        notes.append("ARXIV-SUBMISSION.md not found")
        return
    title = cfg["paper"]["title_plain"].strip()
    if title not in ARXIV_MD.read_text():
        problems.append(
            "ARXIV-SUBMISSION.md does not contain paper.yaml's "
            "paper.title_plain -- the submission sheet has drifted")
    else:
        ok.append("ARXIV-SUBMISSION.md title matches paper.yaml")


def check_other_lanes() -> None:
    (ok if MAIN_TEX.exists() else notes).append(
        "latex/main.tex present" if MAIN_TEX.exists() else
        "latex/main.tex not present yet (make pdf will fail until it lands)")
    (ok if REPLICATION.exists() else notes).append(
        "replication/run.sh present" if REPLICATION.exists() else
        "replication/run.sh not present yet (make verify skips)")


def _scan_values(node) -> int:
    pat = re.compile(r"TODO|FIXME|XXX")
    if isinstance(node, dict):
        return sum(_scan_values(v) for v in node.values())
    if isinstance(node, list):
        return sum(_scan_values(v) for v in node)
    if isinstance(node, str):
        return len(pat.findall(node))
    return 0


def check_placeholders(cfg: dict) -> None:
    n = _scan_values(cfg)
    if n:
        notes.append(f"paper.yaml has {n} placeholder token(s) (fill before release)")


def main() -> int:
    if not PAPER_YAML.exists():
        print("doctor: paper.yaml not found", file=sys.stderr)
        return 1
    cfg = yaml.safe_load(PAPER_YAML.read_text())
    check_toolchain(cfg)
    check_packages(cfg)
    check_venue_engine(cfg)
    check_makefile_drift()
    check_arxiv_md(cfg)
    check_other_lanes()
    check_placeholders(cfg)

    for line in ok:
        print(f"  \033[0;32mok\033[0m   {line}")
    for line in notes:
        print(f"  \033[1;33mnote\033[0m {line}")
    for line in problems:
        print(f"  \033[0;31mFAIL\033[0m {line}")
    print(f"\ndoctor: {len(ok)} ok, {len(notes)} notes, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
