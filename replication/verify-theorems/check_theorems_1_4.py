"""THEOREMS 1-4 and LEMMA A, measured against the from-scratch operator.

Rescued from workstream 20's `code/audit04.py` (the adversarial verifier's
audit of workstream 04's theorems); the computations are unchanged, the
findings are now asserted.

Nothing here trusts workstream 04's derivation: the closed forms of the
write-up are evaluated as formulas and compared, coefficient by coefficient,
against `lib/u2.py`, which solves the defining equation of `U_2` by series
elimination and never forms a product.

  THEOREM 1 (sec. 3.2)  the hypergeometric closed form for `c_{k, j'(k)+em}`,
                        for every odd tame index `e`.  The instance `e = 1` is
                        KM-exp Cor. 4.7 = KMU-I Lemma 6.2, a published theorem,
                        so that row is a check against the literature.
  ground truth          the rows of `01` sec. 6b at `e = 3`, `k = 3..8`.
  THEOREM 2 (sec. 3.3)  `v_2(c) = Sigma_m - 2m + s_2(m)`.
  LEMMA A   (sec. 3.4)  `v_2(c_{k,m}) >= m`, tight only at `k = 2 mod 4, m = 1`;
                        refined to `>= m + s_2(m)` for `k` odd or `4 | k`.
  THEOREM 3 (sec. 3.6)  `a(k) = floor((k-1)/3) + (k mod 2)` satisfies (A1)-(A3),
                        with the minimum at the leading term and `d(k) -> inf`.
  THEOREM 4 (sec. 3.7)  the self-loop at `k = 2e` carries `v_2 = 1`, so
                        `d(2e) <= 1` for EVERY weight: `gamma = 1/6` is exact,
                        and the cap is `e`-universal (`c_{2e,2e} = 2`).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

from fractions import Fraction as F

from harness import check, note, report, scope
from u2 import U2, v2


def jprime(k, e):
    return k // 2 if k % 2 == 0 else (k + e) // 2


def thm1(k, e, m):
    """Write-up Theorem 1: the closed form for c_{k, j'(k) + e m}."""
    if k % 2 == 0:
        num = F(1)
        for i in range(m):
            num *= (k * k - 4 * e * e * i * i)
        den = F(e) ** (2 * m)
        f = 1
        for t in range(1, 2 * m + 1):
            f *= t
        return num / (den * f)
    num = F(k, e)
    for i in range(m):
        num *= (k * k - e * e * (2 * i + 1) ** 2)
    den = F(e) ** (2 * m)
    f = 1
    for t in range(1, 2 * m + 2):
        f *= t
    return num / (den * f)


def s2(n):
    return bin(n).count("1")


def thm2(k, e, m):
    """Write-up Theorem 2: v_2 = Sigma_m - 2m + s_2(m); None iff the coefficient vanishes."""
    s = 0
    for i in range(m):
        xi = 2 * i if k % 2 == 0 else 2 * i + 1
        a, b = k - e * xi, k + e * xi
        if a == 0 or b == 0:
            return None
        s += v2(F(a)) + v2(F(b))
    return s - 2 * m + s2(m)


# ---------------------------------------------------------------- THEOREM 1
N1 = scope(90, 170)
K1 = scope(12, 25)
bad, pairs = [], 0
for e in (1, 3, 5, 7):
    for k in range(1, K1 + 1):
        c = U2(k, e, N1)
        jp = jprime(k, e)
        mmax = (N1 - 8 - 2 * jp) // (2 * e)
        for m in range(0, max(0, mmax) + 1):
            pairs += 1
            if c.get(jp + e * m, F(0)) != thm1(k, e, m):
                bad.append((e, k, m))
check(pairs >= (150 if K1 == 12 else 350),
      "THEOREM 1 examined %d (e,k,m) triples (a collapsed scope is a failure)" % pairs)
check(not bad,
      "THEOREM 1: closed form == operator for e in {1,3,5,7}, k <= %d, all m in support (%d mismatches)"
      % (K1, len(bad)))
check(not [b for b in bad if b[0] == 1],
      "THEOREM 1 at e = 1 == the operator: the published KM-exp Cor. 4.7 / KMU-I Lemma 6.2 row")

# ---------------------------------------------------------------- ground truth (01 sec. 6b)
GROUND = {
    3: ({3: F(1)}, "U_2(t^-3) = t^-3"),
    4: ({2: F(1), 5: F(8, 9), 8: F(-40, 243)}, "U_2(t^-4) = t^-2 + (8/9) t^-5 - (40/243) t^-8 + ..."),
    5: ({4: F(5, 3), 7: F(40, 81), 10: F(-112, 729)}, "U_2(t^-5) = (5/3) t^-4 + (40/81) t^-7 - (112/729) t^-10 + ..."),
    6: ({3: F(1), 6: F(2)}, "U_2(t^-6) = t^-3 + 2 t^-6"),
    7: ({5: F(7, 3), 8: F(140, 81)}, "U_2(t^-7) = (7/3) t^-5 + (140/81) t^-8 + ..."),
    8: ({4: F(1), 7: F(32, 9)}, "U_2(t^-8) = t^-4 + (32/9) t^-7 + ..."),
}
for k, (rows, label) in GROUND.items():
    c = U2(k, 3, 60)
    check(all(c.get(j, F(0)) == v for j, v in rows.items()), "ground truth of 01 sec. 6b: %s" % label)
check(U2(3, 3, 60) == {3: F(1)}, "ground truth: U_2(t^-3) has no second term (support is a single point)")
check(U2(6, 3, 60) == {3: F(1), 6: F(2)}, "ground truth: U_2(t^-6) has no third term")

# ---------------------------------------------------------------- THEOREM 2
N2 = scope(150, 300)
K2 = scope(24, 60)
bad2, vpairs = [], 0
for k in range(1, K2 + 1):
    c = U2(k, 3, N2)
    jp = jprime(k, 3)
    for m in range(0, (N2 - 10 - 2 * jp) // 6 + 1):
        vpairs += 1
        mine, pred = c.get(jp + 3 * m, F(0)), thm2(k, 3, m)
        if mine == 0:
            if pred is not None:
                bad2.append(("zero", k, m))
        elif pred is None or v2(mine) != pred:
            bad2.append(("val", k, m))
check(vpairs >= (200 if K2 == 24 else 600),
      "THEOREM 2 examined %d (k,m) pairs" % vpairs)
check(not bad2,
      "THEOREM 2: v_2(c) = Sigma - 2m + s_2(m) on the full support, k <= %d (%d mismatches)"
      % (K2, len(bad2)))

# ---------------------------------------------------------------- LEMMA A
KA = scope(200, 600)
MA = scope(40, 80)
viol, refine_viol, tight, la = [], [], [], 0
for k in range(1, KA + 1):
    for m in range(1, MA + 1):
        p = thm2(k, 3, m)
        if p is None:
            continue
        la += 1
        if p < m:
            viol.append((k, m, p))
        if p == m:
            tight.append((k, m))
        if (k % 2 == 1 or k % 4 == 0) and p < m + s2(m):
            refine_viol.append((k, m, p))
check(la >= 5000, "LEMMA A examined %d (k,m) pairs" % la)
check(not viol, "LEMMA A: v_2(c_{k,m}) >= m for k <= %d, m <= %d (%d violations)" % (KA, MA, len(viol)))
check(bool(tight) and all(k % 4 == 2 and m == 1 for k, m in tight),
      "LEMMA A is tight exactly on k = 2 mod 4, m = 1 (%d tight pairs)" % len(tight))
check(not refine_viol,
      "LEMMA A refinement: v_2 >= m + s_2(m) when k is odd or 4 | k (%d violations)" % len(refine_viol))
check(all(s2(2 * n - 1) == s2(n) + v2(F(n)) for n in range(1, 5001)),
      "the arithmetic identity s_2(2n-1) = s_2(n) + v_2(n) behind Lemma A, n <= 5000")

# ---------------------------------------------------------------- THEOREM 3
N3 = scope(150, 300)
K3 = scope(40, 100)


def a20(k):
    return 0 if k <= 3 else (k - 1) // 3 + (k % 2)


bad3, argmin_bad, ds = [], [], {}
for k in range(1, K3 + 1):
    c = {j: v for j, v in U2(k, 3, N3).items() if 2 * j < N3 - 8}
    d = min(a20(k) - a20(j) + v2(v) for j, v in c.items())
    ds[k] = d
    if k > 3 and d < 1:
        bad3.append((k, d))
    if k > 3 and a20(k) - a20(min(c)) + v2(c[min(c)]) != d:
        argmin_bad.append(k)
check(all(a20(k) == 0 for k in (1, 2, 3)), "(A1) a(k) = 0 for k <= mu(P) = 3")
check(not bad3, "(A3) THEOREM 3: d(k) >= 1 for 4 <= k <= %d (%d violations)" % (K3, len(bad3)))
check(not argmin_bad,
      "(A3) the minimum is attained at the leading term m = 0 for every k <= %d" % K3)
check([ds[k] for k in range(4, 25)] == [1, 1, 1, 1, 1, 2, 1, 1, 2, 3, 1, 2, 3, 3, 2, 3, 3, 4, 3, 3, 4],
      "d(4..24) = 1,1,1,1,1,2,1,1,2,3,1,2,3,3,2,3,3,4,3,3,4 (write-up sec. 3.6.4)")
check(ds[K3] >= K3 // 6, "(A2)/divergence: d(%d) = %s >= k/6" % (K3, ds[K3]))
check(all(ds[k] == a20(k) - a20(jprime(k, 3)) for k in range(4, K3 + 1)),
      "d(k) is the leading-term increment a(k) - a(j'(k)) for every 4 <= k <= %d" % K3)
if K3 >= 100:
    check(ds[100] == 17, "d(100) = 17 (write-up sec. 3.6.4)")

# ---------------------------------------------------------------- THEOREM 4
c6 = U2(6, 3, 60)
check(jprime(6, 3) + 3 == 6, "THEOREM 4: k = 6 is a self-loop of the support map (j'(6) + e = 6)")
check(6 in c6 and v2(c6[6]) == 1,
      "THEOREM 4: v_2(c_{6,6}) = 1, so d(6) <= 1 for EVERY weight -- gamma <= 1/6")
check(all(thm2(6, e, 1) == 1 for e in (1, 3, 5, 7)),
      "THEOREM 4 is e-universal: v_2(c_{2e,2e}) = 1 for e in {1,3,5,7}, so the cap d(2e) <= 1 does not depend on e")
note("d(k)/(k/6) for the repaired weight, min over 4 <= k <= %d: %.3f  (the repaired weight is"
     " admissible, i.e. d >= 1 and d -> inf; the sharp linear target max(1, k/6) is attained by the"
     " orbit-sum weight a*, checked in check_main_lemma_astar.py and check_lp_feasibility.py)"
     % (K3, min(float(ds[k]) / (k / 6.0) for k in range(4, K3 + 1))))
es = scope((1, 3, 5, 7), (1, 3, 5, 7, 9, 11))
selfloops = {e: U2(2 * e, e, 8 * e + 20).get(2 * e) for e in es}
check(all(v == 2 for v in selfloops.values()),
      "e-universality: c_{2e,2e} = 2 for e in %s (write-up sec. 3.7)" % (list(es),))
if scope(False, True):
    quad = {e: U2(4 * e, e, 16 * e + 20).get(4 * e) for e in (3, 5, 7, 9, 11)}
    check(all(v == 8 for v in quad.values()), "c_{4e,4e} = 8 for e = 3,5,7,9,11")
note("self-loop coefficients c_{2e,2e}: %s" % {e: str(v) for e, v in selfloops.items()})

report("verify-theorems/check_theorems_1_4.py")
