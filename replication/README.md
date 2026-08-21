# Replication package

Machine checks for **"Newton over Hodge at p = 2 for 2-power-order characters
on arbitrary smooth affine curves"** (`research-log/30-writeup.md`; the
verification appendix is sec. 6).

One command runs everything:

```sh
pip install -r requirements.txt      # sympy, used by two of the ten python checks
./run.sh                             # quick sweep, ~15 s
./run.sh --full                      # the scope claimed in the write-up, ~3 min
./run.sh --mutants                   # + the certificate's mutation controls
./run.sh --cargo                     # + noh_u2_matrix.rs (needs cargo + crates.io)
```

`run.sh` exits **0 only if every check passed**, 1 if any failed, 2 if nothing
ran. Each check does the same for itself: it asserts its findings, prints the
number of checks it ran, and treats "zero checks ran" as a failure. Nothing
here can pass by completing.

Scale: 141 assertions in the quick sweep across the ten python checks (174 with
`--full`), plus the Rust certificate's own assertions over 440 / 352 / 41600 /
397 examined cases, plus seven mutation controls that must each fail.

Requirements: `python3` (3.9+) with `sympy`, and `rustc` >= 1.87 (edition 2024
and `i128::midpoint`). No network, no C or C++ toolchain, and **no axeyum** --
see "Relation to the axeyum repository" below. Measured on this machine:
quick sweep 16 s, full sweep with mutants and cargo 169 s, peak memory
well under 2 GB (exact rational arithmetic on small integers throughout).

## What is checked, and where

Everything below is standalone: plain `python3`/`sympy`, or plain `rustc`.

| write-up | claim | command |
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
| sec. 6.1 | the **weight certificate**: Theorems 1-4 in Rust with asserted minimum pair counts (`440 / 352 / 41600 / 397`) | `./certificate/run-certificate.sh` |
| sec. 6.1 | the **mutation controls**: seven mutations of that certificate, each of which must FAIL | `./certificate/run-certificate.sh --mutants` |
| sec. 6.1 | the `U_2` **matrix / Dwork trace formula** certificate (workstream 03): Artin-Hasse 2-integrality, `v_2(pi_1) = 1`, `pi_1 != -2`, the wild-point lattice certificate, point counts, and the order-4 control | `./run.sh --cargo` (see below) |

Add `--full` to any of the python commands for the write-up's published scope
(the quick scope shrinks the sweeps, never drops a claim; each script prints
which scope it used).

## Mutation controls: the checker can fail

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

## Relation to the axeyum repository

`axeyum-examples/` holds the two self-checking examples the write-up cites as
`crates/axeyum-cas/examples/*.rs`. Two honest notes:

1. **They are not in the axeyum checkout available to this project.** No commit
   in that repository adds either file, so no axeyum state can be pinned here,
   and *this* repository is their source of record.
2. **Neither file needs axeyum.** `noh_wt_certificate.rs` uses only `std` --
   `certificate/run-certificate.sh` builds it with plain `rustc`, and the file
   there is byte-identical to the axeyum example. `noh_u2_matrix.rs` uses
   `num-bigint`, `num-rational`, `num-traits` and nothing else, so
   `axeyum-examples/standalone-cargo/Cargo.toml` builds it directly from
   crates.io:

   ```sh
   ./run.sh --cargo     # or, by hand:
   cargo run --release --manifest-path axeyum-examples/standalone-cargo/Cargo.toml \
             --bin noh_u2_matrix
   ```

So the standalone route is the primary one and covers **every** claim in the
table above. The overlay procedure is only for reproducing the exact commands
printed in the write-up, and it is a file copy:

```sh
git clone <axeyum>                                   # if you have access
cp axeyum-examples/noh_*.rs axeyum/crates/axeyum-cas/examples/
cd axeyum
cargo run --release --example noh_u2_matrix      -p axeyum-cas
cargo run --release --example noh_wt_certificate -p axeyum-cas
```

The write-up's timing for `noh_u2_matrix` (~15 s) is the axeyum debug/build
figure; the release binary runs in about 25 ms.

## Layout

```
run.sh                       every standalone check, in sequence
requirements.txt             sympy (two checks use it)
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
axeyum-examples/             the two axeyum-cas examples, verbatim, + a standalone Cargo.toml
```

## Provenance, and the repairs made

Every check in this package is a rescued workstream scratchpad script. The
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

## What was deleted from the rescued material, and why

| deleted | why |
|---|---|
| `standalone/gr/` (11 files: `census-*.txt`, `orbit-*.txt`, `xcheck.py`) | belongs to the parent project's "GR" fibre-census workstream (`ACB_GR_CENSUS` records, quadratic-residue fibre sums). It supports no claim in `30-writeup.md`; nothing in this paper refers to it |
| `standalone/ws20-verifier/*.txt` (8 files, 1.6 MB: `2110.08656.txt`, `2006.04936.txt`, `1909.06905.txt`, `1901.05516.txt`, `1708.03036.txt`, `2010.01130.txt`, `math_0612725.txt`, `ked.txt`) | extracted text of third-party papers and of Kedlaya's book, fetched for quotation checking. No committed script reads them, and redistributing them is a licensing problem. Citation checks are done against the sources as fetched from arXiv / the author's site |
| `standalone/ws20-verifier/rs/{o,o2,out,e,e2,err}.txt` (2 MB) | captured stdout/stderr of earlier certificate and mutant runs; regenerated by `run-certificate.sh --mutants` in three seconds |
| `standalone/ws20-verifier/code/{lp.py,lp2.py}` | superseded drafts of `lp3.py` (same Bellman-Ford feasibility test, narrower) |
| `standalone/ws20-verifier/code/{tail.py,witness.py}` | print-only tables of `(j, v_2, d)` and of `d(k)`, both subsumed by the Theorem 3 sweep |
| `standalone/ws20-verifier/code/fix.log` | empty file |
| `standalone/noh/dens.py` | duplicate of the Artin-Hasse integrality / unit-density computation kept in `check_artin_hasse.py`, and contained a dead stub returning `None` |
| `standalone/` itself, after the conversions above | every remaining file is either byte-identical to one now in `lib/`, `certificate/` or `axeyum-examples/`, or its computation is carried verbatim inside the corresponding `check_*.py`. Keeping two copies invites drift about which is authoritative. All of it remains in git history |

## What this package does and does not establish

It establishes that the *computations* the write-up rests on are reproducible
from scratch, with exact rational arithmetic and no floating point in any
assertion, and that the checkers catch the errors they claim to catch. It is
not a proof assistant, and three limits are worth stating plainly:

* **Truncation.** Every sweep is finite: `k`, `m` and the series truncation `N`
  are bounded (the bounds are printed by each run). Theorems 1-4 are *proved*
  in the write-up; what is verified here is that no counterexample exists in
  the examined range and that the closed forms agree with the operator there.
* **The certificate's "independent route" is not independent.** Recorded in the
  write-up (sec. 6.1) and repeated here: `c_ode` iterates the same product in a
  different association order. Its only binding to the actual operator is the
  six hard-coded ground-truth rows. That binding is supplied properly by
  `check_theorems_1_4.py`, which compares against `lib/u2.py`, a series solve
  of the defining equation.
* **Some results are not computational at all.** Lemma B's proof, the
  base-change invariance of `NP_q`/`HP_q` (sec. 3.9), the dictionary to KM-ab
  (sec. 3.11) and the literature corrections' *reading* of the sources are
  mathematical arguments; only their computable instances appear here. The
  Lemma E coverage GAP (sec. 2.3) is a gap in the paper, not something a check
  could close.
