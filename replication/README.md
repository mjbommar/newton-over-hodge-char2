# Replication package

Machine checks for **"Newton over Hodge at p = 2 for 2-power-order characters
on arbitrary smooth affine curves"** (`research-log/30-writeup.md`; the
verification appendix is sec. 6).

The package has **two layers**, and the order is the point.

| layer | what it is | what it is for |
|---|---|---|
| **1. Primary** | the paper's computations, performed by the **axeyum** reasoning stack at a pinned commit | this is where the mathematics was actually computed |
| **2. Independent cross-check** | a from-scratch python/`rustc` reimplementation that **shares no code with axeyum** | it exists to *disagree* with layer 1 if layer 1 is wrong |

That is the discipline axeyum is built around --- untrusted fast search,
trusted small checking --- applied to its own output. Layer 1 computes; layer 2
re-derives the same objects from the definitions by a different route, in a
different language, written by a different workstream.

One command runs both:

```sh
./run.sh                     # both layers, quick scope
./run.sh --full              # both layers, the scope claimed in the write-up
./run.sh --mutants           # + the cross-check's mutation controls
./run.sh --axeyum-only       # layer 1 alone
./run.sh --crosscheck-only   # layer 2 alone (this script's pre-2026-08-21 default)
./run.sh --offline           # never clone; use a local axeyum or the vendored copies
```

`run.sh` exits **0 only if every check passed**, 1 if any failed, 2 if nothing
ran. Each check does the same for itself: it asserts its findings, prints the
number of checks it ran, and treats "zero checks ran" as a failure. Nothing
here can pass by completing.

Measured on the development machine (16-core x86-64, warm crates.io cache):

| step | cold | warm |
|---|---|---|
| layer 1: materialise the pinned axeyum tree from a local checkout | 1 s | 0 s |
| layer 1: `cargo build --release` of the two examples | 17 s | 0 s |
| layer 1: both examples, running | 0.2 s | 0.2 s |
| layer 2: the ten python checks + the `rustc` certificate, quick scope | 13 s | 13 s |
| layer 2: the same with `--full --mutants` | ~170 s | ~170 s |

So `./run.sh` is about 32 s from cold with a local axeyum checkout beside this
repository, and about 13 s warm. A first run that has to `git clone` instead
took **192 s end to end** when measured (shallow clone of one branch: 680 MB
working tree, ~1.0 GB with the shallow `.git`), after which it is warm like any
other. The degraded route -- `--offline` with no local axeyum, building the
vendored copies -- is 3 s cold.

---

## 1. Primary: Axeyum

[**axeyum**](https://github.com/mjbommar/axeyum) is a Rust-first automated
reasoning stack --- typed term IR, rewriting, query planning, SAT/SMT backends
including a pure-Rust bit-blast-to-SAT path, a Lean-compatible proof kernel,
and a proof-carrying computer-algebra layer (`axeyum-cas`) whose symbolic
results are certified by lowering to the decidable exact-arithmetic core. Its
identity in one sentence is *untrusted fast search, trusted small checking*.
The computations behind this paper were performed in `axeyum-cas`, as
self-checking research examples: exact rational and 2-adic arithmetic, no
floating point anywhere, and every run asserting its own findings so that its
exit status depends on what it found rather than on its finishing.

### The pin

```
repo    https://github.com/mjbommar/axeyum
branch  agent/noh-p2-axeyum-examples
commit  75663ef85c2dad4390a3b6d77361919a914642a9
```

`run.sh` obtains that exact tree in one of three ways, in order:

1. a tree already present at `replication/.axeyum-pin/axeyum` (gitignored)
   whose example files hash to the pin;
2. a local axeyum checkout that *contains* the pinned commit --- point
   `AXEYUM_DIR` at it, or leave it beside this repository as `../axeyum`; the
   pinned tree is then extracted with `git archive`, never built inside
   somebody else's worktree;
3. otherwise `git clone --depth 1 --branch agent/noh-p2-axeyum-examples` into
   `replication/.axeyum-pin/`, after which the cloned `HEAD` **must** equal the
   pin or the run fails.

Overrides: `AXEYUM_DIR`, `AXEYUM_REPO`, `AXEYUM_BRANCH`, `AXEYUM_PIN`.

### The pin binding is checked, not asserted

`axeyum-examples/` in this repository holds copies of the two example sources.
`run.sh` verifies by SHA-256 that they are **byte-identical** to the files at
the pinned axeyum commit:

```
noh_u2_matrix.rs       6b3806fda10bb88eab16ecfb4ffaa27cf58c33bec0d41c00836a208174673f26
noh_wt_certificate.rs  39b4dd825a5c6658e490c2629a81904c665840923e8f4e77f391d1db89be8053
```

That check is a finding, not a formality: it is the only thing that makes "the
copies here *are* the axeyum examples" a checked statement rather than a
sentence in a README, and it fails loudly if either side drifts. The same
hashes let `run.sh` degrade honestly: if the pinned workspace cannot be
obtained (no network, no local checkout), it builds the *vendored copies*
through `axeyum-examples/standalone-cargo/Cargo.toml`, prints a `DEGRADED`
banner, and says so in the summary --- same computation, different build route.

### The two paper-critical examples

Both live at `crates/axeyum-cas/examples/` in axeyum and are run as

```sh
cargo run --release -p axeyum-cas --example noh_u2_matrix
cargo run --release -p axeyum-cas --example noh_wt_certificate
```

| example | what it computes | what it proves, and how it can fail |
|---|---|---|
| **`noh_u2_matrix.rs`** (write-up sec. 6.1, workstream 03) | the Dwork operator `M = psi . mult(Theta)` at `p = 2` on the monomial basis, from the Artin-Hasse exponential `E_2` over `BigRational` and then in `Z/2^64 = Z_2 mod 2^64` (and `Z_2[i]/2^64` for the order-4 control) | Artin-Hasse 2-integrality (proved by construction, denominators asserted odd, not assumed); `v_2(pi_1) = 1` and the **witness that `pi_1 != -2`**; `v_2(lambda_m) >= m` with the equality set printed; the **diagonal lattice certificate** `w_k = 2k/s` for `s = 1,3,5,7,9,11` with an optimality witness in each case; the `m = 2` control showing no extra `p = 2` loss at Witt length 2. Its **anchor** is the Dwork trace formula `(2^k - 1) Tr(M^k) = S_k^*`, checked against exponential sums computed from scratch by point counting over `F_{2^k}` --- so the operator is bound to the geometry, not just to itself |
| **`noh_wt_certificate.rs`** (write-up sec. 6.1) | Theorems 1--4 and Lemma A of the paper, over exact integer arithmetic, with no dependency beyond `std` | `[1]` closed form == ODE recurrence on 440 `(k,m)` pairs, plus the six ground-truth rows `U_2(t^-3) ... U_2(t^-8)`; `[2]` the valuation identity `v_2(c) = Sigma - 2m + s_2(m)` on 352 pairs; `[3]` **Lemma A** on 41600 pairs, with equality in exactly 150 cases, all `k = 2 mod 4` and `m = 1`; `[4]` the repaired weight `floor((k-1)/3) + (k mod 2)` satisfying (A1)--(A3) on `4..=400`, `m <= 250`; `[5]` **sharpness**: `d(6) <= 1` for every weight, hence `gamma <= 1/6` and both `2/11` and `1/5` fail. Every one of those numbers is an asserted minimum count, so a silently-empty sweep fails |

`noh_wt_certificate.rs` needs nothing but `std`, which is why layer 2 can
rebuild the identical file with plain `rustc` and subject it to mutation
controls (see [section 3](#3-mutation-controls-and-limitations)); that is a
second, independent reason to trust the primary run, not a replacement for it.

### The other 21 examples at the pin, and where they belong

The pinned branch carries 23 research examples in `crates/axeyum-cas/examples/`.
Two are this paper's (`noh_*`). The other 21 are `acb_*` --- instruments of the
**AC-Bridge** project, a separate line of work in the same programme (dyadic
character sums, conductor-graded moment machinery, the wild Hast--Matei
question in characteristic two). They are listed here so a reader who clones
the pin is not left wondering what the extra files are; **no claim in this
paper depends on any of them**, and `run.sh` does not run them.

| family | files | AC-Bridge workstream |
|---|---|---|
| `acb_wt_*` | `contractions`, `e2prime`, `moments`, `symbolic`, `weak_target` | 04 --- the weak fourth-moment endpoint target |
| `acb_cdl_*` | `involution`, `pairs`, `twist`, `window` | phase-3 / 22 --- the (CDL) assault |
| `acb_cab_*` | `cells`, `levels` | A --- connected order-cumulant cells |
| `acb_dic_*` | `profile`, `support` | C --- dichotomy / delocalization |
| `acb_sup_*` | `levels`, `period` | phase-3 / 21 --- sup-norm of a conductor layer |
| `acb_ra_*` | `orders`, `scaling` | resurrection audit of refuted shortcuts |
| `acb_gr_*` | `fibre_census`, `orbit_profile` | D --- fibre census / orbit profile |
| `acb_whm_strata` | | B --- wild Hast--Matei, char-2 failure of Lemma 2.6 |
| `acb_ver_supl` | | 20 --- adversarial re-derivation of A and C |

The one place the two projects touched this package is recorded below: the
`standalone/gr/` fibre-census material was deleted from the rescued material
because it belongs to AC-Bridge workstream D and supports no claim here.

---

## 2. Independent cross-checks (Python + plain `rustc`)

Everything in this section is **independent of axeyum**: plain
`python3`/`sympy`, or plain `rustc`, no network, no C or C++ toolchain, exact
rational arithmetic throughout and no floating point in any assertion. These
programs were written from the definitions by a different workstream than the
axeyum examples and share no line of code with them. Where a claim appears in
both layers, agreement between them is the evidence; where the cross-check
covers something layer 1 does not, it is marked in the table.

Requirements: `python3` (3.9+) with `sympy` (two checks use it), and `rustc`
>= 1.87 (edition 2024 and `i128::midpoint`). Scale: 141 assertions in the quick
sweep across the ten python checks (174 with `--full`), plus the Rust
certificate's own assertions over 440 / 352 / 41600 / 397 examined cases, plus
seven mutation controls that must each fail.

| write-up | claim | cross-check command |
|---|---|---|
| sec. 3.1 | the from-scratch Type-2 operator **is** `U_2`: `G^e = 1+2x^e`, the adjunction `U_2(sigma(t^{-j})) = t^{-j}`, and the support shape | `python3 verify-operator/check_operator.py` |
| sec. 3.2 | **THEOREM 1**, the hypergeometric closed form, for `e in {1,3,5,7}` and every `m` in the computed support -- including the published `e = 1` row (KM-exp Cor. 4.7 = KMU-I Lemma 6.2) and workstream 01's ground-truth rows `k = 3..8` | `python3 verify-theorems/check_theorems_1_4.py` |
| sec. 3.3 | **THEOREM 2**, the valuation identity `v_2(c) = Sigma - 2m + s_2(m)` | (same) |
| sec. 3.4 | **LEMMA A**, `v_2(c_{k,m}) >= m`, tight exactly on `k = 2 mod 4, m = 1`, refined to `>= m + s_2(m)` for `k` odd or `4 | k` | (same) |
| sec. 3.6 | **THEOREM 3**: the repaired weight `floor((k-1)/3) + (k mod 2)` satisfies (A1)-(A3), minimum at the leading term, `d(k) -> infinity` | (same) |
| sec. 3.7 | **THEOREM 4**: the self-loop at `k = 2e` has `v_2 = 1`, so `d(2e) <= 1` for every weight; `c_{2e,2e} = 2` is `e`-universal | (same) |
| sec. 3.6, 4.5 | KMU-I Remark 6.5's `floor((k-1)/3)` **fails** (A3) at `k = 5` and only there; ten further closed forms each fail somewhere; only the repair survives | `python3 verify-theorems/check_weight_candidates.py` |
| sec. 3.7, 6.4 | `gamma = 1/6` again, by the **independent LP route** (Bellman-Ford over exact rationals); `2/11` and `1/5` come back INFEASIBLE | `python3 verify-theorems/check_lp_feasibility.py` |
| sec. 6.2, 6.4 | the orbit-sum weight `a*` reproduces 01's LP weights, its closed form, the **Main Lemma** (tight, minimum slack 0), and the **refutation of Note 7**'s cost matrix | `python3 verify-theorems/check_main_lemma_astar.py` |
| sec. 6.3, 6.4 | Artin-Hasse is **at the ceiling** (rate attained, not merely bounded), and the **witness against `pi = -2`**: `AH(-2) = 1 mod 4` but `-1 = 3 mod 4` | `python3 verify-splitting-function/check_artin_hasse.py` |
| sec. 6.3 | **no extra p = 2 loss at Witt length 2, 3**; the `p = 3, 5` controls; the short Dwork function is strictly worse at every `p`; Note 2's commutation | `python3 verify-splitting-function/check_witt_levels.py` |
| sec. 6.3 | the **Lubin-Tate freedom is empty**: `v(theta_{2^j})` and the tail rate are identical across 4 series at level `m = 1` and 3 at `m = 0`; Pulita `E_m` over the true cyclotomic tower | `python3 verify-splitting-function/check_lubin_tate.py` |
| sec. 3.8.3 | **LEMMA B**: a degree-3 tame auxiliary map over `GF(2^a)` exists **iff `3 | q-1`**, and then `alpha` ranges over `mu_3 \ {1}` -- the hypothesis is necessary | `python3 verify-lemma-b/check_degree3_maps.py` |
| sec. 4.3 | KM-ab sec. 4.1.1's `-q(e,j) <= a(p-1)` is **false**, p-uniformly (first witness `p=2, a=3, eps=3, j=1`), and vacuous for 2-power `rho` | (same) |
| sec. 4.4 | KM-ab (18) is **feasible**: `omega(eps) <= a(p-1)-1` for every `eps <= q-2` | (same) |
| sec. 3.8.5 | the explicit Lemma-B instance: separability, the three fibres, equation (8), and **Riemann-Hurwitz saturated** | `python3 verify-lemma-b/check_explicit_instance.py` |
| sec. 6.1 | the **weight certificate** rebuilt with plain `rustc` from the byte-identical axeyum source, with asserted minimum pair counts (`440 / 352 / 41600 / 397`) | `./certificate/run-certificate.sh` |
| sec. 6.1 | the **mutation controls**: seven mutations of that certificate, each of which must FAIL | `./certificate/run-certificate.sh --mutants` |

Add `--full` to any of the python commands for the write-up's published scope
(the quick scope shrinks the sweeps, never drops a claim; each script prints
which scope it used).

Note the shape of the coverage: the cross-check reaches **beyond** the two
axeyum examples --- the LP feasibility route, the orbit-sum weight `a*`, the
Lubin-Tate invariance sweep, the Witt-level controls and the whole of Lemma B
have no counterpart in layer 1 and are checked here only. Conversely the Dwork
trace-formula anchor and the diagonal lattice certificate live only in layer 1.
Neither layer subsumes the other; both must pass.

---

## 3. Mutation controls and limitations

### The checker can fail

`./certificate/run-certificate.sh --mutants` applies each patch in
`certificate/mutants/` to a pristine copy of the certificate, rebuilds it, and
requires that the mutant **exits nonzero with the expected catcher** (the
`.expect` file beside each patch). A mutant that passes is reported as a
failure of the gate.

| mutant | the error injected | must be caught by |
|---|---|---|
| `M1-weight-loses-the-parity-term` | `a(k) -> floor((k-1)/3)`, i.e. KMU's unrepaired weight | `(A3) d(5) = 0 < 1` |
| `M2-valuation-formula-off-by-one` | `+1` in the valuation identity | check [2] |
| `M3-jprime-odd-branch` | `j'(k) -> (k+1)/2` on odd `k` | the ground-truth row `U_2(t^-3)` |
| `M4-xi-doubled-in-product-and-ode` | `xi_i = 2i -> 4i` in **both** the product and the ODE route | check [2] (and ground truth) |
| `M5-M4-with-ground-truth-deleted` | M4 with the ground-truth block removed | check [2] alone |
| `M6-xi-doubled-everywhere` | the same error injected consistently into product, ODE **and** valuation | Lemma A's arithmetic, `v_2(c_{2,2}) = 1 < 2` |
| `M6b-M6-with-ground-truth-deleted` | M6 with the ground-truth block removed | Lemma A alone |

M1-M6 are the six mutations reported in `research-log/20-verify.md` P2-8.
M6 and M6b are the two mutant sources that were rescued from the workstream-20
scratchpad (`rs/m.rs`, `rs/m2.rs`); the patches here **reproduce those two
files byte for byte**, which was verified when they were generated. The other
five are reconstructed from P2-8's table, and each is checked to fail with the
catcher P2-8 names.

### What this package does and does not establish

It establishes that the *computations* the write-up rests on are reproducible
--- primarily from axeyum at a pinned commit, and independently from scratch
--- with exact rational arithmetic and no floating point in any assertion, and
that the checkers catch the errors they claim to catch. It is not a proof
assistant, and three limits are worth stating plainly:

* **Truncation.** Every sweep is finite: `k`, `m` and the series truncation `N`
  are bounded (the bounds are printed by each run). Theorems 1-4 are *proved*
  in the write-up; what is verified here is that no counterexample exists in
  the examined range and that the closed forms agree with the operator there.
* **The certificate's "independent route" is not independent.** Recorded in the
  write-up (sec. 6.1) and repeated here: inside `noh_wt_certificate.rs`,
  `c_ode` iterates the same product in a different association order. Its only
  binding to the actual operator is the six hard-coded ground-truth rows. That
  binding is supplied properly by layer 2's `check_theorems_1_4.py`, which
  compares against `lib/u2.py`, a series solve of the defining equation --- and
  by layer 1's Dwork trace-formula anchor in `noh_u2_matrix.rs`, which compares
  against point counts over `F_{2^k}`. This is the clearest single case for why
  the two layers are both kept.
* **Some results are not computational at all.** Lemma B's proof, the
  base-change invariance of `NP_q`/`HP_q` (sec. 3.9), the dictionary to KM-ab
  (sec. 3.11) and the literature corrections' *reading* of the sources are
  mathematical arguments; only their computable instances appear here. The
  Lemma E coverage GAP (sec. 2.3) is a gap in the paper, not something a check
  could close.

---

## Layout

```
run.sh                       both layers, in order; the entry point
requirements.txt             sympy (two of the cross-checks use it)
.axeyum-pin/                 gitignored; the pinned axeyum tree, materialised by run.sh

-- layer 1 (axeyum) ---------------------------------------------------------
axeyum-examples/             the two axeyum-cas examples, byte-identical to the pin,
                             + a standalone Cargo.toml for the degraded build route

-- layer 2 (independent cross-check) ----------------------------------------
lib/                         shared, rescued verbatim from the workstream scratchpads
  u2.py                      workstream 20's from-scratch Type-2 operator U_2
  ah.py, l1.py, lt.py        workstream 02's number-field / Artin-Hasse / Pulita E_m toolkit
  gf2.py                     workstream 20's GF(2^a) arithmetic and degree-3 classification
  harness.py                 the assertion harness (new; see below)
verify-operator/             is the operator the operator?
verify-theorems/             Theorems 1-4, Lemma A, the weight controls, the LP route, a*
verify-splitting-function/   Artin-Hasse ceiling, Witt levels, Lubin-Tate invariance
verify-lemma-b/              degree-3 classification, KM-ab rows 15/16, the explicit instance
certificate/                 rustc build of the weight certificate + seven mutation controls
```

## Provenance, and the repairs made

Every check in layer 2 is a rescued workstream scratchpad script. The
computations were **not** rewritten; what was added is assertion. The rescued
scripts printed their findings and exited 0 either way, which is exactly the
failure mode this project treats as worse than no checker, so each one now
records findings through `lib/harness.py` and the exit status depends on them.

| now | rescued from | what changed |
|---|---|---|
| `lib/u2.py` | `ws20-verifier/code/u2.py` | verbatim |
| `lib/ah.py`, `lib/lt.py` | `noh/ah.py`, `noh/lt.py` | verbatim |
| `lib/l1.py` | `noh/l1.py` | script body moved under `if __name__ == "__main__"` so importing it prints nothing |
| `lib/gf2.py` | `ws20-verifier/code/audit05.py` | the `GF`/`ev`/`polmul`/`cube`/`classify` half split out as a module |
| `verify-operator/check_operator.py` | `code/checks.py` | assertions; `G^e` extended from `e = 3` to `e in {1,3,5,7}` |
| `verify-theorems/check_theorems_1_4.py` | `code/audit04.py` | assertions; ground-truth rows made explicit constants |
| `verify-theorems/check_weight_candidates.py` | `code/closed.py` | assertions, including that the eleven controls must FAIL |
| `verify-theorems/check_lp_feasibility.py` | `code/lp3.py` | assertions |
| `verify-theorems/check_main_lemma_astar.py` | `code/audit04b.py` | assertions |
| `verify-splitting-function/check_artin_hasse.py` | `code/ah.py` | assertions |
| `verify-splitting-function/check_witt_levels.py` | `code/misc.py` + `noh/more.py` | assertions; the two scripts' overlapping halves merged |
| `verify-splitting-function/check_lubin_tate.py` | `noh/ltgen.py` + `noh/run2.py` | assertions; see the wording correction below |
| `verify-lemma-b/check_degree3_maps.py` | `code/audit05.py` | assertions |
| `verify-lemma-b/check_explicit_instance.py` | `code/inst.py` | assertions; one dead half-written derivative expression dropped; no longer re-runs the whole degree-3 classification on import |
| `axeyum-examples/noh_wt_certificate.rs` | `ws20-verifier/rs/cert.rs` | byte-identical to both the rescued file and the axeyum example |
| `certificate/mutants/M6*.patch` | `ws20-verifier/rs/m.rs`, `m2.rs` | regenerated as patches; verified to reproduce both files byte for byte |

No rescued script needed a path repair: none of them read a scratchpad file.
Two behaved badly on import (`l1.py` printed a table, `inst.py` re-ran a
six-second classification), and both were fixed as noted.

**One wording correction found while repackaging.** Workstream 02's verdict
says the valuation profile of the Lubin-Tate splitting quotient is
"bit-identical" across series. Literally it is not: `v(c_k)` differs at small
non-2-power `k` (at `m = 0, k = 6`: 4, 6, 5 for `w = 6, 2, 10`). What is
identical -- and what the argument uses -- is the subsequence at `k = 2^j` and
the tail rate `min_{k >= N/2} v(c_k)/k`. Those are what
`check_lubin_tate.py` asserts, and its docstring records the correction.

**A superseded note, corrected 2026-08-21.** An earlier revision of this file
said the two `noh_*` examples were "not in the axeyum checkout available to
this project", so that "no axeyum state can be pinned here" and this repository
was "their source of record". That is no longer true and the layering above
reflects it: the examples are in axeyum on branch
`agent/noh-p2-axeyum-examples` at commit `75663ef8`, that commit is the pin,
and the copies here are checked against it by hash on every run.

## What was deleted from the rescued material, and why

| deleted | why |
|---|---|
| `standalone/gr/` (11 files: `census-*.txt`, `orbit-*.txt`, `xcheck.py`) | belongs to the parent project's "GR" fibre-census workstream (`ACB_GR_CENSUS` records, quadratic-residue fibre sums) -- the `acb_gr_*` examples at the axeyum pin are that workstream's instruments. It supports no claim in `30-writeup.md`; nothing in this paper refers to it |
| `standalone/ws20-verifier/*.txt` (8 files, 1.6 MB: `2110.08656.txt`, `2006.04936.txt`, `1909.06905.txt`, `1901.05516.txt`, `1708.03036.txt`, `2010.01130.txt`, `math_0612725.txt`, `ked.txt`) | extracted text of third-party papers and of Kedlaya's book, fetched for quotation checking. No committed script reads them, and redistributing them is a licensing problem. Citation checks are done against the sources as fetched from arXiv / the author's site |
| `standalone/ws20-verifier/rs/{o,o2,out,e,e2,err}.txt` (2 MB) | captured stdout/stderr of earlier certificate and mutant runs; regenerated by `run-certificate.sh --mutants` in three seconds |
| `standalone/ws20-verifier/code/{lp.py,lp2.py}` | superseded drafts of `lp3.py` (same Bellman-Ford feasibility test, narrower) |
| `standalone/ws20-verifier/code/{tail.py,witness.py}` | print-only tables of `(j, v_2, d)` and of `d(k)`, both subsumed by the Theorem 3 sweep |
| `standalone/ws20-verifier/code/fix.log` | empty file |
| `standalone/noh/dens.py` | duplicate of the Artin-Hasse integrality / unit-density computation kept in `check_artin_hasse.py`, and contained a dead stub returning `None` |
| `standalone/` itself, after the conversions above | every remaining file is either byte-identical to one now in `lib/`, `certificate/` or `axeyum-examples/`, or its computation is carried verbatim inside the corresponding `check_*.py`. Keeping two copies invites drift about which is authoritative. All of it remains in git history |
