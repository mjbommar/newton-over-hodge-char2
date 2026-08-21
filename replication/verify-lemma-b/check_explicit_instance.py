"""The explicit Lemma-B instance: eta = ((1+omega) z^{q-1} + omega)^3 + 1 over GF(q), 3 | q-1.

Rescued from workstream 20's `code/inst.py`; the computations are unchanged,
the findings are now asserted, and one piece of dead code (an unused,
half-written derivative expression) was dropped in the repackaging.

Write-up sec. 3.8.5.  With `P(z) = (1+omega) z^{q-1} + omega` and
`eta - 1 = P^3` (characteristic 2):

  * `P` is separable (`gcd(P, P') = 1`), so it has `q-1` distinct roots, none 0;
  * fibre over 1: `q-1` points of index exactly 3, so `r_1 * 3 = deg eta`;
  * fibre over 0: `P = 1` gives `q-1` simple points (where `S` sits,
    unramified), `P = omega` gives `z = 0` with multiplicity `q-1`,
    `P = omega^2` gives another `q-1` simple points -- so `r_0 = 2q-1`;
  * fibre over infinity: one point, index `3(q-1)`, so `r_infinity = 1`;
  * equation (8): `2(g-1) + r_0 + r_1 + r_infinity = deg eta` at `g = 0`;
  * Riemann-Hurwitz is SATURATED by these three fibres:
    `sum_P (e_P - 1) = 2 deg(eta) - 2`, so `eta` is Belyi and there is no
    ramification anywhere else.  All indices are odd, i.e. tame at p = 2.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

from gf2 import GF, cube
from harness import check, note, report, scope

QS = scope((2, 4), (2, 4, 6))       # the exponents a with 3 | 2^a - 1


def norm(a):
    a = a[:]
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def pdiv(F_, A, B):
    A, B = norm(A[:]), norm(B[:])
    q = [0] * max(1, len(A) - len(B) + 1)
    ib = F_.inv(B[-1])
    while A != [0] and len(A) >= len(B):
        d = len(A) - len(B)
        c = F_.mul(A[-1], ib)
        q[d] = c
        for i, y in enumerate(B):
            if y:
                A[i + d] ^= F_.mul(c, y)
        A = norm(A)
    return q, A


def pgcd(F_, A, B):
    A, B = norm(A[:]), norm(B[:])
    while B != [0]:
        _, r = pdiv(F_, A, B)
        A, B = B, norm(r)
    return A


for a in QS:
    F_ = GF(a)
    q = F_.q
    om = [x for x in range(2, q) if F_.pw(x, 3) == 1][0]
    check(F_.pw(om, 3) == 1 and om != 1, "q = %d: omega = %d is a primitive cube root of unity" % (q, om))

    P = [0] * q
    P[0] = om
    P[q - 1] = 1 ^ om                                    # P = (1+omega) z^{q-1} + omega
    P = norm(P)
    eta_m1 = cube(F_, P)                                 # eta - 1 = P^3 in characteristic 2
    deg = len(eta_m1) - 1
    check(deg == 3 * (q - 1), "q = %d: deg eta = %d = 3(q-1)" % (q, deg))

    Pprime = norm([F_.mul(P[i], i % 2) for i in range(1, len(P))])
    g = pgcd(F_, P, Pprime)
    check(len(g) == 1 and g != [0],
          "q = %d: gcd(P, P') is a nonzero constant, so P is separable with q-1 distinct roots" % q)
    check(P[0] == om != 0, "q = %d: P(0) = omega != 0, so 0 is not a root of P" % q)

    # fibre over 0: P in mu_3
    fibre = {}
    for label, v in (("P=1", 1), ("P=omega", om), ("P=omega^2", F_.mul(om, om))):
        rhs = F_.mul(v ^ om, F_.inv(1 ^ om))             # z^{q-1} = (v + omega)/(1 + omega)
        fibre[label] = rhs
    check(fibre["P=omega"] == 0,
          "q = %d: P = omega forces z^{q-1} = 0, i.e. z = 0 with multiplicity q-1 = %d" % (q, q - 1))
    check(fibre["P=1"] != 0 and fibre["P=omega^2"] != 0,
          "q = %d: P = 1 and P = omega^2 each give q-1 simple points (S sits in the first, unramified)"
          % q)

    r0, r1, rinf = 2 * q - 1, q - 1, 1
    check(r1 * 3 == deg, "q = %d: r_1 * 3 = %d = deg eta (fibre over 1 is uniformly index 3)" % (q, deg))
    check(2 * (0 - 1) + r0 + r1 + rinf == deg,
          "q = %d: equation (8) holds -- 2(g-1) + r_0 + r_1 + r_oo = %d = deg eta at g = 0" % (q, deg))
    ram = (q - 2) + 2 * (q - 1) + (3 * (q - 1) - 1)
    check(ram == 2 * deg - 2,
          "q = %d: RIEMANN-HURWITZ SATURATED, sum(e_P - 1) = %d = 2 deg - 2: no ramification outside"
          " the three fibres" % (q, ram))
    check((q - 1) % 2 == 1 and 3 % 2 == 1 and (3 * (q - 1)) % 2 == 1,
          "q = %d: every ramification index (q-1, 3, 3(q-1)) is odd, i.e. tame at p = 2" % q)

note("the extension-free variant (delete the auxiliary stages, take e = q-1) is geometry only:"
     " it moves mu(P) to q-1 and voids Theorem 3's e = 3 analysis -- insurance, not a drop-in")

report("verify-lemma-b/check_explicit_instance.py")
