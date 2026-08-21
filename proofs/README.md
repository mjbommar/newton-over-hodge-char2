# proofs/ -- planned Lean formalization

Empty by design, for now. The intent is a Lean 4 (mathlib) formalization of
the two results that carry the paper's weight and are finite, arithmetic, and
therefore genuinely formalizable:

* **Lemma A** (the tail estimate): `v_2(c_{k, j'(k) + m e}) >= m` on the
  support of the local operator, with the refinement `>= m + s_2(m)` when `k`
  is odd or `4 | k`.
* **Theorem 3** (admissibility of the repaired weight): the weight
  `a(k) = floor((k-1)/3) + (k mod 2)` satisfies conditions (A1)-(A5) for every
  `k > mu(P)`, with defect `d(k) >= max(1, k/6)`.

Both currently rest on the hand proofs in `research-log/30-writeup.md`
sec. 3.4 and 3.6, on the adversarial re-derivation in `20-verify.md`
(P0-4, P0-5, P0-6, P2-2, P2-3), and on the self-checking programs described in
sec. 6.1 -- which check finitely many indices, not the theorem. A Lean proof
would close that gap for the arithmetic core; it would not touch Lemma B (the
geometry) or the cited functional analysis.

Nothing here is claimed as done. When work starts, this file records the
status, and `TODO.md` tracks it.
