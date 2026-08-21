"""The Lubin-Tate freedom is empty at p = 2: varying the series does not change the rate.

Rescued from workstream 02's `ltgen.py` and `run2.py` (both built on
`lib/lt.py`, 02's exact cyclotomic-tower arithmetic); the computations are
unchanged, the findings are now asserted.

Pulita's construction lets the splitting function be built from any Lubin-Tate
series `P(X) = wX + ... + X^p`.  If that freedom bought anything, attack (B)
would have been alive.  It does not: over four series at Witt level `m = 1`
and three at `m = 0`, the decay-controlling data of the splitting quotient
`theta = E(T^p)/E(T)` is the same.  Pulita's Thm 2.13 explains why -- varying
the series can only destroy overconvergence, never improve the rate -- and
this is that theorem reproduced independently.

**One wording correction to 02, found while repackaging.**  02's VERDICT calls
the valuation profile "bit-identical" across series.  It is not, literally:
`v(c_k)` differs at small non-2-power `k` (e.g. `m = 0`, `k = 6`: 4, 6, 5 for
`w = 6, 2, 10`).  What IS identical, and what the argument uses, is the
subsequence at `k = 2^j` and the tail rate `min_{k >= N/2} v(c_k)/k`.  Those
are what is asserted here.

Also checked: Pulita's `E_m(T)` over the honest cyclotomic tower
`Q_2(zeta_{2^{m+1}})` for `m = 0, 1, 2`, where `v(varpi_j) = 1/(2^j)` is the
expected uniformizer valuation.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

from fractions import Fraction as F

from harness import check, note, report, scope
from lt import Em, Ram, sdiv, sexp, subst_pow, val

N = scope(48, 64)


class Eis(Ram):
    """Q_2[t]/(g) for a monic Eisenstein g given by its coefficients, low -> high."""

    def __init__(self, p, gcoef):
        self.p = p
        self.e = len(gcoef) - 1
        assert gcoef[-1] == 1
        self.red = [F(-gcoef[i]) for i in range(self.e)]


def lt_profile(m, n, w):
    """theta = E(T^2)/E(T) for the Lubin-Tate series P(X) = wX + X^2 at level m."""
    if m == 0:
        class Q2(Eis):
            def __init__(s):
                s.p, s.e, s.red = 2, 1, [F(0)]
        R = Q2()
        pi = [F(-w)]                       # pi_0 = -w, the nonzero root of P
        f = [R.zero() for _ in range(n + 1)]
        f[1] = pi
    else:
        R = Eis(2, [F(w), F(w), F(1)])     # pi_1 root of X^2 + wX + w
        pi = R.zero()
        pi[1] = F(1)
        pi0 = R.zero()
        pi0[0] = F(-w)
        f = [R.zero() for _ in range(n + 1)]
        f[1] = pi
        f[2] = R.smul(F(1, 2), pi0)
    E = sexp(R, f, n)
    th = sdiv(R, subst_pow(R, E, 2, n), E, n)
    return R, {k: val(R, th[k]) for k in range(1, n + 1)}, val(R, pi)


for m, ws in ((1, (2, 10, -6, 18)), (0, (2, 10, 6))):
    pow2, tails, vpis = [], [], []
    for w in ws:
        R, vs, vpi = lt_profile(m, N, w)
        pow2.append(tuple(vs[2 ** j] for j in range(2, N.bit_length())))
        fin = [(k, vs[k] / k) for k in range(1, N + 1) if vs[k] is not None]
        tails.append(min(r for k, r in fin if k >= N // 2))
        vpis.append(vpi)
    check(len(set(vpis)) == 1 and vpis[0] == F(1, 2 ** m),
          "level m = %d: v(pi_m) = %s for every Lubin-Tate series tried" % (m, vpis[0]))
    check(len(set(pow2)) == 1,
          "level m = %d: v(theta_{2^j}) is identical across %d Lubin-Tate series w in %s: %s"
          % (m, len(ws), list(ws), [str(x) for x in pow2[0]]))
    check(len(set(tails)) == 1,
          "level m = %d: the tail rate min_{k >= %d} v(c_k)/k = %s is identical across all %d series"
          % (m, N // 2, tails[0], len(ws)))
    check(tails[0] < vpis[0],
          "level m = %d: the Lubin-Tate quotient's tail rate %s is BELOW v(pi_m) = %s -- varying the"
          " series never beats Artin-Hasse" % (m, tails[0], vpis[0]))

# --- Pulita's E_m over the true cyclotomic tower ---------------------------------
for m in (0, 1, 2):
    R, E, ws_ = Em(2, m, N)
    check(val(R, ws_[m]) == F(1, 2 ** m),
          "Pulita E_%d over Q_2(zeta_%d): v(varpi_%d) = %s = 1/(p^j(p-1)) as it must be"
          % (m, 2 ** (m + 1), m, val(R, ws_[m])))
    th = sdiv(R, subst_pow(R, E, 2, N), E, N)
    fin = [(k, val(R, th[k]) / k) for k in range(1, N + 1) if val(R, th[k]) is not None]
    tail = min(r for k, r in fin if k >= N // 2)
    check(tail <= val(R, ws_[m]),
          "Pulita theta_%d tail rate %s <= v(varpi_%d) = %s" % (m, tail, m, val(R, ws_[m])))

note("Pulita Thm 2.13: varying the Lubin-Tate series can only destroy overconvergence,"
     " never improve the rate -- reproduced above, not quoted")

report("verify-splitting-function/check_lubin_tate.py")
