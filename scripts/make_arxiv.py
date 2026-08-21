# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""make_arxiv.py -- build a self-contained, verified arXiv source bundle.

Ships the pre-generated ``main.bbl`` (so arXiv need not run a bibliography
backend), writes arXiv's ``00README.json`` from paper.yaml, carries only the
LaTeX sources plus final figure PDFs, and -- the part that matters --
VERIFIES that the staged bundle compiles standalone in a temp dir, with a
clean exit, no TeX errors, and zero undefined references, BEFORE packaging.
A bundle that only "produced a PDF" is not verified: nonstopmode recovers
from hard errors and still emits one.

    uv run scripts/make_arxiv.py

Notes
-----
* arXiv accepts tex/pdftex/latex/pdflatex/xelatex as the declared compiler,
  NOT lualatex; this script refuses a lualatex configuration.
* No shell-escape anywhere, so the bundle compiles under arXiv's AutoTeX.
* Anything under ``anc/`` (if present) ships as arXiv ancillary material:
  stored and listed with the paper, never compiled. It is copied in AFTER
  the compile check so it cannot affect the build, and it counts against
  arXiv's 50 MB submission cap.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - environment guard
    print("make_arxiv: PyYAML is required. Run via `uv run scripts/make_arxiv.py` "
          "or `pip install pyyaml`.", file=sys.stderr)
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parent.parent
LATEX = ROOT / "latex"
BUILD = ROOT / "build"
PAPER_YAML = ROOT / "paper.yaml"
ARXIV_OUT = BUILD / "arxiv"
CAP = 50 * 1024 * 1024  # arXiv submission cap

ENGINE_CMD = {"pdflatex": "pdflatex", "xelatex": "xelatex"}


def die(msg: str) -> None:
    print(f"make_arxiv: ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def slug(cfg: dict) -> str:
    title = cfg["paper"].get("short_title") or cfg["paper"]["title_plain"]
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s or "paper"


def collect_sources() -> list[Path]:
    """Every .tex the build inputs, plus the bib and final figure PDFs."""
    files: list[Path] = sorted(LATEX.glob("*.tex"))
    for sub in ("preamble", "frontmatter", "backmatter", "sections"):
        files += sorted((LATEX / sub).glob("*.tex"))
    files += sorted((LATEX / "bib").glob("*.bib"))
    files += sorted((LATEX / "figures").glob("*.pdf"))
    return [f for f in files if f.is_file()]


def readme_json(cfg: dict, compiler: str) -> str:
    """arXiv 00README.json: name the intended compiler and TeX Live."""
    return json.dumps(
        {"process": {"compiler": compiler},
         "sources": [{"filename": "main.tex", "usage": "toplevel"}]},
        indent=2) + "\n"


def main() -> None:
    if not PAPER_YAML.exists():
        die("paper.yaml not found")
    cfg = yaml.safe_load(PAPER_YAML.read_text())
    engine = cfg["typography"]["engine"]
    if engine not in ENGINE_CMD:
        die(f"engine {engine!r} is not an accepted arXiv compiler; set "
            "typography.engine to pdflatex or xelatex for the arXiv bundle")
    compiler = ENGINE_CMD[engine]
    if not (LATEX / "main.tex").is_file():
        die("latex/main.tex not found -- nothing to package")

    print("make_arxiv: refreshing build (make pdf)...")
    subprocess.run(["make", "pdf"], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    bbl = BUILD / "latex" / "main.bbl"
    if not bbl.exists():
        print("make_arxiv: note: no main.bbl (inline bibliography?)")

    stage = Path(tempfile.mkdtemp(prefix="arxiv-stage-"))
    try:
        for f in collect_sources():
            dest = stage / f.relative_to(LATEX)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, dest)
        if bbl.exists():
            shutil.copyfile(bbl, stage / "main.bbl")
        (stage / "00README.json").write_text(readme_json(cfg, compiler))

        print(f"make_arxiv: verifying standalone {compiler} build...")
        r = None
        for _ in range(2):
            r = subprocess.run([compiler, "-interaction=nonstopmode", "main.tex"],
                               cwd=stage, capture_output=True, text=True)
        log = stage / "main.log"
        logtext = log.read_text(errors="ignore") if log.exists() else ""
        if not (stage / "main.pdf").exists():
            tail = "\n".join((r.stdout if r else "").splitlines()[-25:])
            die(f"standalone build produced no PDF:\n{tail}")
        tex_errors = [ln for ln in logtext.splitlines() if ln.startswith("!")]
        if (r is not None and r.returncode != 0) or tex_errors:
            sample = "\n".join(tex_errors[:5]) or \
                "\n".join((r.stdout if r else "").splitlines()[-15:])
            die("standalone build reported TeX errors "
                f"(exit {r.returncode if r else '?'}):\n{sample}")
        undef = len(re.findall(r"(?:Citation|Reference) `[^']*' .*undefined", logtext))
        if undef:
            die(f"standalone build has {undef} undefined reference(s)/citation(s)")
        m = re.search(r"Output written on main\.pdf \((\d+) page", logtext)
        pages = int(m.group(1)) if m else 0

        for junk in ("main.pdf", "main.log", "main.aux", "main.out", "main.fls",
                     "main.fdb_latexmk", "main.bcf", "main.run.xml", "main.blg",
                     "main.toc"):
            (stage / junk).unlink(missing_ok=True)

        anc_src = ROOT / "anc"
        if anc_src.is_dir():
            shutil.copytree(anc_src, stage / "anc")
            n_anc = sum(1 for f in (stage / "anc").rglob("*") if f.is_file())
            anc_bytes = sum(f.stat().st_size
                            for f in (stage / "anc").rglob("*") if f.is_file())
            print(f"make_arxiv: ancillary anc/ -- {n_anc} file(s), "
                  f"{anc_bytes / 1024 / 1024:.1f} MiB")
        else:
            print("make_arxiv: note: no anc/ directory -- the replication "
                  "material is referenced by repository URL only")

        ARXIV_OUT.mkdir(parents=True, exist_ok=True)
        tarball = ARXIV_OUT / f"{slug(cfg)}-arxiv.tar.gz"
        with tarfile.open(tarball, "w:gz") as tar:
            for f in sorted(stage.rglob("*")):
                if f.is_file():
                    tar.add(f, arcname=str(f.relative_to(stage)))

        size_b = tarball.stat().st_size
        print(f"make_arxiv: standalone build OK -- {pages} pages, 0 undefined refs")
        print(f"make_arxiv: wrote {tarball.relative_to(ROOT)} ({size_b / 1024:.0f} KB)")
        if size_b > CAP:
            die(f"bundle is {size_b / 1024 / 1024:.1f} MiB, over arXiv's 50 MB cap")
        if size_b > 0.8 * CAP:
            print(f"make_arxiv: WARNING: {size_b / 1024 / 1024:.1f} MiB is within "
                  "20% of arXiv's 50 MB cap")
        with tarfile.open(tarball) as tar:
            for n in tar.getnames():
                print(f"  {n}")
        print("make_arxiv: now work through ARXIV-SUBMISSION.md before uploading.")
    finally:
        shutil.rmtree(stage, ignore_errors=True)


if __name__ == "__main__":
    main()
