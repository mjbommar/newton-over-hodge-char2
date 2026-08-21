# Newton over Hodge at p = 2 for 2-power-order characters on arbitrary smooth affine curves

Source for a mathematics preprint targeting **arXiv** (primary `math.NT`;
cross-list `math.AG`). **Preprint in preparation.** It has not been submitted,
refereed, or reviewed by any human mathematician other than the author.

## What the paper claims

For a nontrivial character `rho` of `pi_1(X)` of 2-power order on a smooth
affine curve `X` over `F_q`, `q = 2^a`, the paper proves

```
    NP_q(L(rho, s))  >=  HP_q(rho)
```

as full polygons -- no truncation, no restriction on the order -- where
`HP_q` is the Kramer-Miller ramification-defined (Swan-local) Hodge polygon.
The odd-`p` case is due to Kramer-Miller and Kramer-Miller-Upton; `p = 2` was
excluded by those authors for two stated reasons, one analytic and one
geometric. The paper discharges both:

* **The analytic one.** KMU-I Remark 6.5's local estimate degrades at `p = 2`
  to `a(k) = floor((k-1)/3)`, "too low for applications to the global
  setting". That `3` is the tame ramification index of an auxiliary map, not
  a decay rate, and the weight `a(k) = floor((k-1)/3) + (k mod 2)` -- KMU's
  own weight plus a parity indicator -- is admissible for every `k`, with
  defect `d(k) >= max(1, k/6)`. The rate `1/6` is **exactly** optimal:
  `k = 2e` is a self-loop of the local operator with coefficient `2` for every
  weight whatsoever.
* **The geometric one.** A characteristic-2 tame Belyi map of uniform index
  `3` over the point `1`, built on Kedlaya-Litt-Witaszek and
  Sugiyama-Yasuda.

A second, weaker tier gives the KMU-I local-to-global *contact* criterion at
`p = 2` on an initial segment (q-adic `r <= 2^{1-n}` for order `2^n`), and
shows that this restriction is structural: no choice of auxiliary tame index
removes it. The paper also records several corrections to the published
literature found en route, and states its open items exactly.

**Status, stated honestly.** The main theorem and its two lemmas were proved
by one set of agents and independently re-derived by an adversarial auditing
agent, and the core local computations are backed by self-checking programs
(see `replication/`). Parts of the supporting material remain
`PENDING-AUDIT`, and the paper says which. None of this is a substitute for
human review, and it is not offered as one.

## Repo map

| Where | What |
|-------|------|
| `paper.yaml` | Single source of truth: title, authors, abstract, keywords, MSC 2020, arXiv categories, engine, license, disclosures |
| `latex/` | The paper source (`main.tex`, `sections/`, `preamble/`, `bib/`) |
| `replication/` | Standalone verifier and the self-checking programs; `run.sh` is the entry point |
| `research-log/` | The complete, frozen audit trail: charter, five proving workstreams, coordinator notes, the adversarial audit (`20-verify.md`), and the write-up (`30-writeup.md`) |
| `proofs/` | Stub for the planned Lean formalization of Lemma A / Theorem 3 |
| `scripts/` | Build gates, toolchain doctor, arXiv packaging (`uv run`, zero install) |
| `ARXIV-SUBMISSION.md` | Paste-ready submission fields and the pre-submit checklist |

## Build the paper

```bash
make pdf         # the paper PDF -> build/latex/main.pdf
make check       # undefined refs, duplicate labels, alt text, leftover markers
make lint        # chktex (advisory)
make doctor      # audit the toolchain for THIS paper.yaml, and doc/Makefile drift
make arxiv       # verified arXiv source bundle (ships .bbl; refuses a bundle that
                 # does not compile standalone with zero undefined refs)
make validate    # everything a submission must pass
```

Requires TeX Live (pdfLaTeX + `latexmk` + `bibtex`); `uv` is optional but
convenient, and `make doctor` reports what is missing.

## Run the replication

```bash
make verify      # delegates to replication/run.sh
```

Every checking program asserts its findings and **exits nonzero when a check
fails**, so its exit status depends on what the run found rather than on the
run completing. Until `replication/run.sh` lands, `make verify` skips loudly
and states that it checked nothing -- it never reports a green it did not
earn.

## The audit trail

The mathematics was produced by a multi-agent AI pipeline with an adversarial
verification stage: proving agents wrote the arguments, an independent
auditing agent re-derived them from the definitions and attempted to refute
them, and every assertion carries the label that audit left it with --
`PROVED HERE`, `CITED`, `AUDITED-CONFIRMED`, `PENDING-AUDIT`, `GAP`, or
`FALSE (witness)`. Several early results were refuted, including the project
charter's own analysis of the obstruction; those refutations are in the log
rather than edited out of it. `research-log/` is frozen for that reason, and
`research-log/30-writeup.md` sec. 6.2 is the who-proved-what/who-audited-what
table. Labels are never upgraded without a new, named verification.

## License

Paper content: CC BY 4.0 (`venue.license` in `paper.yaml`). Code and tooling
in `scripts/` and `replication/`: MIT, see [`LICENSE`](LICENSE).
