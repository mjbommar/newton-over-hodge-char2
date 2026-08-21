"""Validate the from-scratch Type-2 operator `U_2` before anything is proved with it.

Rescued from workstream 20's `code/checks.py`; the computations are unchanged,
the findings are now asserted.

The operator itself is `lib/u2.py`, workstream 20's own implementation, built
from KMU-I sec. 4.3 + 6.1.2 and sharing no code with workstreams 01/03/04.  It
is the object every later check is measured against, so it is validated three
ways first -- this is what makes "audited" mean something:

  (V1) `G^e = 1 + 2 x^e` exactly, `G = (1 + 2 x^e)^{1/e}`.  This is the only
       place `e` odd is used (it is what makes `t' = -t G` the conjugate).
  (V2) the adjunction `U_2(sigma(t^{-j})) = t^{-j}` -- an identity forced by
       `U_2 = (1/p) sigma^{-1} Tr` that the elimination has no way to fake.
  (V3) the shape of the support: least pole order `j'(k)`, unit leading
       coefficient, and support inside `j'(k) + e Z_{>=0}`.

Write-up: sec. 3.1 (the Type-2 operator at p = 2), sec. 6.2 row
"THEOREM 1 ... AUDITED-CONFIRMED"; 20-verify.md sec. 0, P0-1.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

from fractions import Fraction as F

from harness import check, note, report, scope
from u2 import U2, series_pow, v2

N = scope(120, 200)
KMAX = scope(40, 80)


def mul(a, b, n):
    o = {}
    for d1, v1 in a.items():
        for d2, v2_ in b.items():
            if d1 + d2 < n:
                o[d1 + d2] = o.get(d1 + d2, F(0)) + v1 * v2_
    return {d: v for d, v in o.items() if v != 0}


def power(a, k, n):
    r = {0: F(1)}
    for _ in range(k):
        r = mul(r, a, n)
    return r


# ---------------------------------------------------------------- (V1) G^e = 1 + 2 x^e
for e in (1, 3, 5, 7):
    G = series_pow(e, F(1, e), 60)
    check(power(G, e, 60) == {0: F(1), e: F(2)} if e else False,
          "(V1) G^%d == 1 + 2 x^%d exactly (e odd; t' = -t G is the conjugate)" % (e, e))


# ---------------------------------------------------------------- (V2) adjunction
def U2_of_series(lhs, e, n):
    """Run the same lowest-degree-first elimination on an arbitrary series."""
    basis = {}
    j = 0
    while 2 * j < n:
        b = series_pow(e, F(-j, e), n - 2 * j)
        basis[j] = {d + 2 * j: v for d, v in b.items() if d + 2 * j < n}
        j += 1
    coeffs = {}
    work = dict(lhs)
    while True:
        work = {d: v for d, v in work.items() if v != 0}
        if not work:
            break
        d0 = min(work)
        if d0 % 2:
            raise RuntimeError("odd leading degree %d" % d0)
        j0 = d0 // 2
        if 2 * j0 >= n:
            break
        c = work[d0] / basis[j0][2 * j0]
        coeffs[j0] = c
        for d, v in basis[j0].items():
            work[d] = work.get(d, F(0)) - c * v
    return {j: c for j, c in coeffs.items() if c != 0}


adjunction_ok = True
for j in range(0, 6):
    b = series_pow(3, F(-j, 3), 60)
    sig = {d + 2 * j: v for d, v in b.items() if d + 2 * j < 60}
    if U2_of_series(sig, 3, 60) != {j: F(1)}:
        adjunction_ok = False
check(adjunction_ok, "(V2) U_2(sigma(t^-j)) == t^-j for j = 0..5 at e = 3")


# ---------------------------------------------------------------- (V3) support shape
def jprime_formula(k, e):
    """Least j >= ceil(k/2) with j = -k mod e."""
    j = -(-k // 2)
    while (j + k) % e != 0:
        j += 1
    return j


def lr(k):
    """k = 2l - r with r in {0,1}: the least pole order is l + r."""
    return k // 2 if k % 2 == 0 else (k + 1) // 2 + 1


bad_jprime, bad_lr, bad_unit, bad_supp = [], [], [], []
for k in range(1, KMAX + 1):
    c = U2(k, 3, N)
    jm = min(c)
    if jm != jprime_formula(k, 3):
        bad_jprime.append((k, jm, jprime_formula(k, 3)))
    if k >= 3 and jm != lr(k):
        bad_lr.append((k, jm, lr(k)))
    if v2(c[jm]) != 0:
        bad_unit.append((k, v2(c[jm])))
    if any((j - jm) % 3 for j in c):
        bad_supp.append(k)

check(not bad_jprime,
      "(V3) least pole order == least j >= ceil(k/2) with j = -k mod 3, k <= %d (%d mismatches)"
      % (KMAX, len(bad_jprime)))
check(not bad_lr,
      "(V3) least pole order == l + r for k = 2l - r, 3 <= k <= %d (%d mismatches)"
      % (KMAX, len(bad_lr)))
check(not bad_unit,
      "(V3) leading coefficient is a 2-adic unit for every k <= %d (%d mismatches)"
      % (KMAX, len(bad_unit)))
check(not bad_supp,
      "(V3) support of U_2(t^-k) lies in j'(k) + 3 Z_{>=0} for every k <= %d" % KMAX)

# The KMU weight's defect, measured on the FULL support of this operator: the
# hole is at k = 5 and nowhere else below KMAX.  This is the fact the repaired
# weight has to fix (write-up sec. 3.6, sec. 4.5).
def a_kmu(k):
    return (k - 1) // 3 if k >= 3 else 0


data = {k: U2(k, 3, N) for k in range(4, KMAX + 1)}
d_kmu = {k: min(a_kmu(k) - a_kmu(j) + v2(v) for j, v in c.items() if 2 * j < N - 6)
         for k, c in data.items()}
zeros = [k for k, d in d_kmu.items() if d < 1]
check(zeros == [5],
      "KMU's a(k) = floor((k-1)/3) fails (A3) at k = 5 and only there for 4 <= k <= %d: %s"
      % (KMAX, zeros))
note("d(k) for the KMU weight, k = 4..20: %s" % [d_kmu[k] for k in range(4, min(21, KMAX + 1))])

report("verify-operator/check_operator.py")
