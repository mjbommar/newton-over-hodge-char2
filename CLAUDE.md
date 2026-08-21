# AI Instructions (canonical)

This is the single source of AI instructions for this paper project.
`AGENTS.md` is a pointer here; never let it diverge. `make doctor` audits
this file: every `make <target>` it mentions must exist in the Makefile.

## About this paper

**Newton over Hodge at p = 2 for 2-power-order characters on arbitrary smooth
affine curves.** For an Artin-Schreier-Witt character `rho` of a smooth affine
curve `X/F_q`, the Newton-over-Hodge problem asks whether the q-adic Newton
polygon of `L(rho, s)` lies on or above the ramification-defined (Swan-local)
Hodge polygon. On `P^1` and its affinoids this is known at every prime (Zhu;
Liu-Wan; Schmidt). On an *arbitrary* curve it is known only for odd `p`:
Kramer-Miller and Kramer-Miller-Upton carry a standing hypothesis `p >= 3`,
and they say why. At `p = 2` their local lattice estimate degrades to
`a(k) = floor((k-1)/3)`, which KMU-I Remark 6.5 calls "too low for
applications to the global setting", and their auxiliary Belyi map is built
from a simply branched cover that does not exist in characteristic 2.

This paper closes that case. The obstruction is not analytic: the `3` in
`floor((k-1)/3)` is the *tame ramification index* of the auxiliary map, and
the estimate is repaired by a different weight on the same module,
`a(k) = floor((k-1)/3) + (k mod 2)` -- KMU's own weight plus a parity
indicator -- proved admissible for every `k` with defect `d(k) >= max(1, k/6)`
(Theorems 1-3 and Lemma A). The rate `1/6` is exactly optimal: `k = 2e` is a
self-loop of the local operator with coefficient `c_{2e,2e} = 2` for *every*
weight whatsoever, so `d(2e) <= 1` unconditionally (Theorem 4). The geometric
input KMU lack is supplied by Lemma B, a characteristic-2 tame Belyi map of
uniform index `3` over the point `1`, resting on Kedlaya-Litt-Witaszek and
Sugiyama-Yasuda. Together these give **T1**: `NP_q(rho) >= HP_q(rho)` as full
polygons, no truncation and no restriction on the order, for every nontrivial
character of 2-power order on an arbitrary smooth affine curve over `F_{2^a}`.
A second tier, **T2**, gives the KMU-I local-to-global *contact* criterion at
`p = 2` on an initial segment `r <= 2^{1-n}` only, and Theorem 4 shows that
restriction cannot be lifted by any choice of auxiliary tame index.

The work also records corrections to the literature found en route (KMU-I
Prop. 4.3's target point must satisfy `c^{p-1} = 1`; Def. 6.3's strict
inequality; KM-ab sec. 4.1.1's bound, which is false p-uniformly, with the
true bound supplied; and smaller textual defects), and it states its open
items exactly -- chief among them Lemma E, which KMU assert without proof at
every `p` and which T1 does not need.

**Venue: arXiv.** Primary category `math.NT`; cross-list `math.AG`.
Classification is **MSC 2020** (`classification.msc_*` in `paper.yaml`).
There is no JEL block and there never should be -- JEL is the
economics/finance scheme.

## Project map

| Where | What | Owner |
|---|---|---|
| `paper.yaml` | Single source of truth for title, authors, abstract, keywords, MSC, arXiv categories, engine, license, disclosures | root |
| `Makefile`, `scripts/` | Build, gates, arXiv packaging (`uv run`, zero install) | root |
| `latex/` | The paper source (`main.tex`, `sections/`, `preamble/`, `bib/`) | paper lane |
| `replication/` | Standalone verifier + the self-checking programs; `run.sh` is the entry point `make verify` calls | replication lane |
| `proofs/` | Stub: planned Lean formalization of Lemma A / Theorem 3 | -- |
| `research-log/` | **Frozen history.** The charter, the five proving workstreams, the coordinator notes, the adversarial audit (`20-verify.md`), and the write-up (`30-writeup.md`) the paper is drafted from | nobody -- read-only |
| `ARXIV-SUBMISSION.md` | Paste-ready submission fields + pre-submit checklist (hand-maintained; `make doctor` checks it against `paper.yaml`) | root |

## Hard rules

1. **`research-log/` is frozen. Never edit a file in it.** It is the audit
   trail that makes the paper's labels mean something, including the results
   that were refuted and withdrawn. Correcting it retroactively destroys
   exactly the evidence it exists to carry. If something in it is wrong, say
   so in the paper or in `TODO.md`.
2. **Label discipline: `AUDITED-CONFIRMED` / `PENDING-AUDIT` / `GAP` / `OPEN`
   are never upgraded without new verification.** A label records who
   *independently* re-derived a result, not how confident the prose sounds.
   `AUDITED-CONFIRMED` means workstream `20`, the adversarial verifier,
   re-derived it from the definitions. Nothing in the paper, and no agent
   working here, may promote a label on its own authority -- an upgrade needs
   a new, named verification, and the write-up's own rule ("No label is ever
   upgraded on this document's authority") applies to the paper too.
3. **Every claim in the paper carries its status.** T1 is `AUDITED-CONFIRMED`
   modulo named citations; T2 is `PENDING-AUDIT` and its restriction is
   `AUDITED-CONFIRMED as structural`; the residual `PENDING-AUDIT` surface is
   enumerated in the write-up's sec. 5 and 6.2. Do not flatten those
   distinctions into a uniform confident voice.
4. **Machine verification must fail when the finding fails.** Every checking
   program in `replication/` asserts its findings and exits nonzero on any
   failure; a run that exits 0 on completion alone is not a check. When you
   touch one, delete a guard and confirm that exactly one assertion dies.
5. **Cite from the source, not from memory.** Every quotation in the write-up
   was fetched from the PDF and several were fetched twice by independent
   workstreams; keep that standard. Statement numbers must be exact.
6. **No `minted` / `--shell-escape`** -- arXiv does not run shell-escape.
7. **Do not hand-type metadata into the prose.** Title, abstract, keywords,
   and classification live in `paper.yaml`.

## AI-assistance disclosure (goes in the paper, and is not optional)

The mathematics here was produced by a multi-agent AI pipeline with an
adversarial verification stage: proving agents wrote the arguments; an
independent auditing agent re-derived them from the definitions and tried to
refute them; several results *were* refuted and are recorded as such. The
full audit trail -- who proved what, who audited it, what was withdrawn, and
what remains unaudited -- is in `research-log/`, and the machine-checked
components are in `replication/`. Human verification status is tracked in
`TODO.md`. The paper must state this plainly (`disclosure.ai_statement` in
`paper.yaml`), must not present machine checking as a substitute for referee
review, and must not describe any `PENDING-AUDIT` item as established.

## Build targets (complete vocabulary)

| Target | What it does |
|---|---|
| `make pdf` / `make quick` | The paper PDF / one fast pass (refs may be stale) |
| `make draft` | DRAFT build (line numbers/banner if the preamble defines `\DraftMode`) |
| `make check` | Undefined refs, duplicate labels, figure `alt=` text, leftover TODO markers |
| `make lint` | chktex on the LaTeX sources (advisory; skips if chktex is absent) |
| `make wordcount` | Per-section word counts (texcount) |
| `make verify` | The replication smoke checks via `replication/run.sh`; skips loudly, and says it checked nothing, until that lands |
| `make doctor` | Toolchain and packages for THIS `paper.yaml`, plus the docs/Makefile drift audit |
| `make arxiv` | Verified arXiv bundle: ships `.bbl` + `00README.json`, and refuses to package a bundle that does not compile standalone with zero undefined refs |
| `make validate` | Everything a submission must pass |
| `make watch` / `make clean` | Rebuild loop / remove outputs |

The engine comes from `paper.yaml`. Python helpers run under `uv run` (their
PEP 723 headers pull in pyyaml with no install step) and fall back to
`python3` when uv is absent.

## When you finish a session

1. `make check` and `make doctor` -- green, or the violations listed honestly.
2. `make verify` if you touched anything under `replication/`.
3. Record what you did in `TODO.md`; report failures rather than rounding them
   off. A gate you did not run is not a gate you passed.
