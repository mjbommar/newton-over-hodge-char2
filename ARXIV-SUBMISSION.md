# arXiv Submission -- Newton over Hodge at $p = 2$ for $2$-power-order characters on arbitrary smooth affine curves

Paste-ready fields for the arXiv submission form. **Hand-maintained**: this
repo has no metadata generator, so this file must be kept in step with
`paper.yaml`. `make doctor` fails if the title here no longer matches
`paper.title_plain`.

## Form fields

- **Title:** Newton over Hodge at p = 2 for 2-power-order characters on arbitrary smooth affine curves
- **Authors:** Michael Bommarito
- **Primary category:** math.NT
- **Cross-list:** math.AG
- **MSC-class:** 11T23 (Primary) 11G20, 11S15, 14F30, 14G15 (Secondary)
- **ACM-class:** (none -- no cs cross-list)
- **Comments:** fill in at submission time: page count, and the sentence
  naming the replication repository
  (https://github.com/mjbommar/newton-over-hodge-char2)
- **License:** CC BY 4.0

> arXiv has **no keywords field**. The keywords below are printed on the
> abstract page of the PDF only; discovery is by category + MSC class + full
> text.

- Keywords (PDF only): Newton polygon, Hodge polygon, Artin-Schreier-Witt covers, exponential sums, characteristic 2, L-functions

## Abstract (plain text -- arXiv's abstract field is not TeX)

Newton-over-Hodge lower bounds for Artin-Schreier-Witt L-functions on arbitrary smooth affine curves are known only for odd p: at p = 2 the Kramer-Miller-Upton local estimate degrades to a(k) = floor((k-1)/3), which they call too low for applications to the global setting. We show that this is an artifact of one weight choice, not of the prime. The 3 is the tame ramification index of an auxiliary Belyi map, and the weight a(k) = floor((k-1)/3) + (k mod 2) is admissible for every k, with defect d(k) >= max(1, k/6); the rate 1/6 is exactly optimal, since k = 2e is a self-loop of the local operator with coefficient 2 for every weight. Adding a characteristic-2 tame Belyi map of uniform index 3 over the point 1, we obtain NP_q(L(rho,s)) >= HP_q(rho) as full polygons, with no truncation, for every nontrivial character of 2-power order on a smooth affine curve over F_{2^a}. We also give the local-to-global contact criterion at p = 2 on an initial segment, prove that restriction structural, and record corrections to the literature.

## Pre-submit checklist

Mathematical honesty first -- these are the ones specific to this paper.

- [ ] Every theorem, lemma and remark in the PDF carries the status the
      research log gives it. **T1** is stated as proved (audited, modulo named
      citations); **T2** is stated as `PENDING-AUDIT` with its
      `r <= 2^{1-n}` restriction; nothing `PENDING-AUDIT` is phrased as
      established. No label was upgraded during drafting.
- [ ] The AI-assistance disclosure is in the PDF, names the adversarial
      verification stage, points at the public audit trail, and does not
      present machine checking as a substitute for referee review.
- [ ] Corrections to the literature (sec. 4) are stated as corrections to
      specific statements with witnesses, and say plainly where the published
      mathematics is *not* wrong (e.g. KM-exp Lemma 3.1 is correct at every
      p >= 3; the defect is in the paraphrase).
- [ ] Open items (Lemma E, the deflation proposal, general odd e, the
      residual audit surface) are in the paper, not only in the log.
- [ ] The data-availability statement names the replication repository and
      states that each program's exit status depends on what it found.

Then the mechanics.

- [ ] `make validate` is green (`doctor`, `pdf`, `check`, `lint`, `verify`).
- [ ] `make arxiv` is green -- it verifies a standalone compile with a clean
      exit, no TeX errors, and 0 undefined references before packaging.
- [ ] The engine is pdflatex or xelatex (arXiv does not accept lualatex).
- [ ] `main.bbl` is in the bundle and matches the engine's bib program
      (natbib/bibtex here, which is the version-agnostic choice).
- [ ] Every figure has `alt=` text (arXiv HTML / LaTeXML).
- [ ] No `minted` / `--shell-escape`; any figures ship as pre-built PDFs.
- [ ] `00README.json` names the intended compiler.
- [ ] **MSC class** is set on the form. This is a mathematics submission:
      there is no JEL field and no JEL block in the PDF.
- [ ] Bundle is under arXiv's 50 MB cap (`make arxiv` fails if not).
- [ ] Title, abstract and classification here still match `paper.yaml`
      (`make doctor` checks the title).

## Deliberately NOT in the bundle

- The research log and the replication package: they are large, they are
  living, and they are better served by the public repository, which the
  data-availability statement names. If ancillary material is wanted later,
  put it in `anc/` and `make arxiv` will ship it (and enforce the cap).
- Build byproducts (`.aux`/`.log`/`.out`/`.fls`/...).
- Python helpers and figure sources; only final figure PDFs ship.
