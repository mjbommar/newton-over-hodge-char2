"""No extra p = 2 loss at Witt length >= 2, and the p = 3, 5 controls.

Rescued from workstream 20's `code/misc.py` and workstream 02's `more.py`; the
computations are unchanged, the findings are now asserted.

  * `theta_0(T) = E_0(T^2)/E_0(T) = exp(2T - 2T^2)`: the valuations at
    `k = 2^j` follow `2^{j-2} + 1`.
  * the multilevel product `prod_{i<m} AH(pi^{2^i} x^{2^i})` with `pi^e = -2`,
    `e = 2^{m-1}`: `min_k v(c_k)/k = v(pi)` exactly for `m = 1, 2, 3`, i.e.
    **no loss appears at longer Witt length at p = 2**.  This refuted the
    coordinator's prediction P3.
  * the p = 3 and p = 5 controls: `AH(pi x)` attains `v(pi)` there too, so the
    p = 2 behaviour is not special; and the short Dwork splitting function
    `exp(pi(x - x^p))` is strictly worse than `AH` at every p, bounded below
    by the classical `(p-1)/p^2`.
  * Note 2's commutation `psi(B(x^2) f) = B(x) psi(f)` at p = 2.

**Recorded weakness, not hidden** (write-up sec. 6.4): the multilevel product
computed here is `prod_i AH(pi^{p^i} x^{p^i})`, which is NOT KM-ab's `E_r`;
02's Table B was labelled as measuring `E_r` and that label is a **GAP**.  What
carries the no-loss verdict is the literature (KMU-II Lemma 3.5 / Thm 3.6 and
KM-ab Prop. 5.5 carry no parity hypothesis); these numbers confirm it, they do
not establish it.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

import random
from fractions import Fraction as F

from ah import NF, ah_gen, val
from harness import check, note, report
from l1 import AH_coeffs

N = 72


def v2q(x):
    if x == 0:
        return None
    n, d = x.numerator, x.denominator
    v = 0
    while n % 2 == 0:
        n //= 2
        v += 1
    while d % 2 == 0:
        d //= 2
        v -= 1
    return F(v)


def exp_series(f, n):
    c = [F(0)] * (n + 1)
    c[0] = F(1)
    for i in range(1, n + 1):
        s = F(0)
        for k in range(1, min(i, len(f) - 1) + 1):
            if f[k]:
                s += k * f[k] * c[i - k]
        c[i] = s / i
    return c


# ---------------------------------------------------------------- theta_0 = exp(2T - 2T^2)
f = [F(0)] * (N + 1)
f[1], f[2] = F(2), F(-2)
th = exp_series(f, N)
check([v2q(th[2 ** j]) for j in range(2, 7)] == [F(2 ** (j - 2) + 1) for j in range(2, 7)],
      "order-2 splitting theta_0: v(c_{2^j}) = 2^{j-2} + 1 for j = 2..6")

# ---------------------------------------------------------------- multilevel Witt products
DEG = 40
a = AH_coeffs(2, DEG)
for m in (1, 2, 3):
    e = 2 ** (m - 1)
    nf = NF(e, -2)
    res = [nf.zero() for _ in range(DEG + 1)]
    res[0] = nf.one()
    for i in range(m):
        pw = 2 ** i
        fac = [nf.zero() for _ in range(DEG + 1)]
        k = 0
        while pw * k <= DEG:
            fac[pw * k] = nf.frompi(pw * k, a[k])
            k += 1
        new = [nf.zero() for _ in range(DEG + 1)]
        for d1 in range(DEG + 1):
            if all(y == 0 for y in res[d1]):
                continue
            for d2 in range(0, DEG + 1 - d1):
                if all(y == 0 for y in fac[d2]):
                    continue
                new[d1 + d2] = nf.add(new[d1 + d2], nf.mul(res[d1], fac[d2]))
        res = new
    rates = [(k, val(nf, res[k], 2, e) / k) for k in range(1, DEG + 1)
             if val(nf, res[k], 2, e) is not None]
    mn = min(r for _, r in rates)
    check(mn == F(1, e),
          "Witt length m = %d (e = %d): min v(c_k)/k = %s = v(pi_m) -- NO extra loss at p = 2"
          % (m, e, mn))
    check(sum(1 for _, r in rates if r == mn) >= 10,
          "Witt length m = %d: the rate is attained at %d of %d degrees"
          % (m, sum(1 for _, r in rates if r == mn), len(rates)))

# ---------------------------------------------------------------- p = 3, 5 controls
for p in (3, 5):
    e = p - 1
    nf, c = ah_gen(p, 30, e)
    rates = [val(nf, c[k], p, e) / k for k in range(1, 31) if val(nf, c[k], p, e) is not None]
    check(min(rates) == F(1, e),
          "control p = %d: AH(pi x) attains min v/k = 1/%d = v(pi) -- the ceiling is uniform in p"
          % (p, e))


def short_dwork(p, n, e):
    """exp(pi(x - x^p)), the short Dwork splitting function."""
    nf = NF(e, -p)
    f2 = [nf.zero() for _ in range(n + 1)]
    f2[1] = nf.frompi(1, 1)
    if p <= n:
        f2[p] = nf.frompi(1, -1)
    return nf, ah_exp(nf, f2, n)


def ah_exp(nf, f2, n):
    c = [nf.zero() for _ in range(n + 1)]
    c[0] = nf.one()
    for i in range(1, n + 1):
        acc = nf.zero()
        for k in range(1, i + 1):
            if all(y == 0 for y in f2[k]):
                continue
            acc = nf.add(acc, nf.smul(k, nf.mul(f2[k], c[i - k])))
        c[i] = nf.smul(F(1, i), acc)
    return c


for p in (2, 3, 5):
    n = 36 if p == 2 else 30
    e = p - 1
    nf, c = short_dwork(p, n, e)
    rates = [val(nf, c[k], p, e) / k for k in range(1, n + 1) if val(nf, c[k], p, e) is not None]
    mn = min(rates)
    check(F(p - 1, p * p) <= mn < F(1, e),
          "short Dwork exp(pi(x-x^p)) at p = %d: min v/k = %s, in [%s, %s) -- strictly WORSE than AH,"
          " never below the classical (p-1)/p^2" % (p, mn, F(p - 1, p * p), F(1, e)))

# ---------------------------------------------------------------- Note 2 commutation
random.seed(7)
NN = 24
B = [F(random.randint(-9, 9)) for _ in range(NN + 1)]
fser = [F(random.randint(-9, 9)) for _ in range(NN + 1)]
Bx2 = [F(0)] * (NN + 1)
for m2 in range(NN // 2 + 1):
    Bx2[2 * m2] = B[m2]


def mulseries(x, y, n):
    o = [F(0)] * (n + 1)
    for i2, u in enumerate(x):
        if not u:
            continue
        for j2, w in enumerate(y):
            if i2 + j2 > n:
                break
            if w:
                o[i2 + j2] += u * w
    return o


prod = mulseries(Bx2, fser, NN)
lhs = [prod[2 * n] for n in range(NN // 2 + 1)]
rhs = mulseries(B[:NN // 2 + 1], [fser[2 * n] for n in range(NN // 2 + 1)], NN // 2)
check(lhs[:len(rhs)] == rhs, "Note 2: psi(B(x^2) f) = B(x) psi(f) at p = 2 (random series, seed 7)")

note("what the literature carries, and these numbers only confirm: KMU-II Lemma 3.5 / Thm 3.6"
     " and KM-ab Prop. 5.5 have no parity hypothesis at all")

report("verify-splitting-function/check_witt_levels.py")
