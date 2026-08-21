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
(see `replication/`). The computations were performed with
[**Axeyum**](https://github.com/mjbommar/axeyum), a Rust-first automated
reasoning stack, pinned at commit
[`75663ef8`](https://github.com/mjbommar/axeyum/tree/75663ef85c2dad4390a3b6d77361919a914642a9)
of branch `agent/noh-p2-axeyum-examples`, and independently cross-checked by a
from-scratch reimplementation that shares no code with it. Parts of the
supporting material remain `PENDING-AUDIT`, and the paper says which. None of
this is a substitute for human review, and it is not offered as one.

## Repo map

| Where | What |
|-------|------|
| `paper.yaml` | Single source of truth: title, authors, abstract, keywords, MSC 2020, arXiv categories, engine, license, disclosures |
| `latex/` | The paper source (`main.tex`, `sections/`, `preamble/`, `bib/`) |
| `replication/` | Two-layer replication: **Axeyum at a pinned commit** computes, an independent from-scratch implementation cross-checks; `run.sh` is the entry point |
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
make verify                            # delegates to replication/run.sh
replication/run.sh                     # both layers, quick scope    (~32 s cold, ~13 s warm)
replication/run.sh --full --mutants    # the scope claimed in the write-up (~3.5 min)
replication/run.sh --axeyum-only       # layer 1 alone
replication/run.sh --crosscheck-only   # layer 2 alone
```

The package has **two layers, and the order is the point.**

**Layer 1, primary: [Axeyum](https://github.com/mjbommar/axeyum).** The
mathematics in this paper was computed by Axeyum, a Rust-first automated
reasoning stack (typed term IR, rewriting, SAT/SMT backends, a Lean-compatible
proof kernel, and the proof-carrying computer-algebra layer `axeyum-cas` used
here). Its identity in one sentence is *untrusted fast search, trusted small
checking*. `run.sh` obtains the stack at the pinned commit

```
repo    https://github.com/mjbommar/axeyum
branch  agent/noh-p2-axeyum-examples
commit  75663ef85c2dad4390a3b6d77361919a914642a9
```

-- from `AXEYUM_DIR`, from a sibling `../axeyum` checkout that contains that
commit, or by a shallow clone into `replication/.axeyum-pin/` (gitignored),
whose `HEAD` must equal the pin or the run fails -- and then runs the two
self-checking examples

```bash
cargo run --release -p axeyum-cas --example noh_u2_matrix       # the exact U_2 operator,
                                                                # Dwork-trace anchored
cargo run --release -p axeyum-cas --example noh_wt_certificate  # Theorems 1-4, Lemma A
```

Before running them it verifies by SHA-256 that the copies shipped under
`replication/axeyum-examples/` are byte-identical to that commit, so "these are
the axeyum examples" is a checked finding rather than a sentence in a README.

**Layer 2, independent cross-check.** A from-scratch reimplementation in
`python3`/`sympy` and plain `rustc` that **shares no code with Axeyum**,
written from the definitions by a different workstream. It exists to disagree
with layer 1 if layer 1 is wrong, and it reaches beyond it: the LP feasibility
route, the orbit-sum weight, the Lubin-Tate invariance sweep, the Witt-level
controls and all of Lemma B are checked only there. Conversely the Dwork
trace-formula anchor lives only in layer 1. Neither layer subsumes the other; a
green run requires both.

Every checking program in both layers asserts its findings and **exits nonzero
when a check fails**, so `run.sh`'s exit status depends on what the runs found
rather than on their completing; it exits 2 if nothing ran at all. Full detail,
including the claim-to-program table and the mutation controls, is in
[`replication/README.md`](replication/README.md).

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
