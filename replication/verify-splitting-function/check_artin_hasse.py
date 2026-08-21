"""The Artin-Hasse splitting function is already at the theoretical ceiling, and pi != -2.

Rescued from workstream 20's `code/ah.py` (the auditor's own from-scratch
Artin-Hasse audit); the computations are unchanged, the findings are now
asserted.

Two findings, both negative, both load-bearing:

  * **No headroom (attack (B) is dead).**  `AH(x) = exp(sum_i x^{2^i}/2^i)` is
    2-integral (Dwork-Dieudonne, verified here rather than assumed), its
    exp-form equals its product form, and the decay rate of `AH(pi x)` is
    `min_k v(c_k)/k = v(pi) = 1/2` *exactly* -- the rate is ATTAINED, not
    merely bounded, and no splitting function can beat it (Kedlaya
    Thm 19.4.1, Pulita Prop. 2.12, Robba's necessity).  Write-up sec. 6.3
    ("Repackaged, or classical"), 02 sec. VERDICT item 1, 20 sec. 4.1-4.2.
  * **`pi = -2` is refuted with a witness.**  The splitting parameter at
    character order 2 must satisfy `AH(pi) = -1`; but `AH(-2) = 1 mod 4`
    while `-1 = 3 mod 4`.  This killed the coordinator's Note 6
    identification (write-up sec. 6.4, self-correction 2; 20 sec. 5.3).  The
    load-bearing content -- rate 1 at order 2 -- survived; the identification
    of the object did not.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

from fractions import Fraction as F

from harness import check, note, report, scope

DEG = scope(80, 170)


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
    """exp(f) with f[0] = 0, via n c_n = sum_{k<=n} k f_k c_{n-k}."""
    c = [F(0)] * (n + 1)
    c[0] = F(1)
    for i in range(1, n + 1):
        s = F(0)
        for k in range(1, i + 1):
            if k < len(f) and f[k] != 0:
                s += k * f[k] * c[i - k]
        c[i] = s / i
    return c


f = [F(0)] * (DEG + 1)
i = 0
while 2 ** i <= DEG:
    f[2 ** i] = F(1, 2 ** i)
    i += 1
AH = exp_series(f, DEG)


def mobius(n):
    r, m, p = 1, n, 2
    while p * p <= m:
        if m % p == 0:
            m //= p
            if m % p == 0:
                return 0
            r = -r
        p += 1
    if m > 1:
        r = -r
    return r


def mul(a, b, n):
    o = [F(0)] * (n + 1)
    for i2, x in enumerate(a):
        if x == 0:
            continue
        for j2, y in enumerate(b):
            if i2 + j2 > n:
                break
            if y:
                o[i2 + j2] += x * y
    return o


def binpow(n, e, N):
    """(1 - x^n)^e for rational e."""
    o = [F(0)] * (N + 1)
    m = 0
    while n * m <= N:
        c = F(1)
        for i2 in range(m):
            c = c * (e - i2) / (i2 + 1)
        o[n * m] = c * ((-1) ** m)
        m += 1
    return o


P = [F(0)] * (DEG + 1)
P[0] = F(1)
for n in range(1, DEG + 1, 2):
    mu = mobius(n)
    if mu == 0:
        continue
    P = mul(P, binpow(n, F(-mu, n), DEG), DEG)

check(AH == P, "AH exp-form == product form prod_{n odd} (1-x^n)^{-mu(n)/n} to degree %d" % DEG)
check(all(v2q(a) is None or v2q(a) >= 0 for a in AH),
      "AH coefficients are 2-integral to degree %d (Dwork-Dieudonne, verified not assumed)" % DEG)

units = [k for k in range(1, DEG + 1) if v2q(AH[k]) == 0]
check(len(units) > DEG // 4,
      "AH has %d unit coefficients below degree %d (density %.3f): the rate is attained infinitely often"
      % (len(units), DEG, len(units) / DEG))
check(max(b - a for a, b in zip(units, units[1:])) <= 6,
      "consecutive unit indices are never more than 6 apart (largest gap %d)"
      % max(b - a for a, b in zip(units, units[1:])))

# --- the ceiling: v(c_k)/k for AH(pi x), pi^2 = -2, v(pi) = 1/2 -----------------
rates = []
for k in range(1, 41):
    if k % 2 == 0:
        v = v2q(AH[k] * F((-2) ** (k // 2)))
    else:
        v = v2q(AH[k] * F((-2) ** ((k - 1) // 2))) + F(1, 2)
    rates.append(v / k)
check(min(rates) == F(1, 2),
      "CEILING ATTAINED: min_{k<=40} v(c_k)/k = 1/2 = v(pi) for AH(pi x), pi^2 = -2")
check(sum(1 for r in rates if r == F(1, 2)) >= 10,
      "the ceiling is attained at %d of the first 40 degrees, not once"
      % sum(1 for r in rates if r == F(1, 2)))

# --- the witness against pi = -2 ------------------------------------------------
S = F(0)
for i2 in range(0, 6):
    S += F((-2) ** (2 ** i2), 2 ** i2)
val = F(0)
term = F(1)
for n in range(0, 14):
    val += term
    term = term * S / (n + 1)
num = val.numerator * pow(val.denominator, -1, 2 ** 12) % (2 ** 12)
check(num % 4 == 1 and (2 ** 12 - 1) % 4 == 3,
      "WITNESS: AH(-2) = %d = 1 mod 4 but -1 = 3 mod 4, so AH(-2) != -1 and pi != -2" % (num % 4))
check(num != 2 ** 12 - 1, "AH(-2) mod 2^12 = %d != %d = -1 mod 2^12" % (num, 2 ** 12 - 1))
note("the rate statement (v(pi) = 1 at character order 2) survived this correction;"
     " only the identification of pi did not")

report("verify-splitting-function/check_artin_hasse.py")
