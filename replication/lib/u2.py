"""Independent from-scratch implementation of KMU's Type-2 operator U_p at eta(P)=1.

Derivation (mine, from KMU-I sec 4.3 + 6.1.2):
  u = t^e is the parameter at the point 1 downstairs;  sigma(u) = (u+1)^p - 1.
  At p=2: sigma(u) = u^2 + 2u,  so sigma(t)^e = t^{2e}(1 + 2 t^{-e}),
          sigma(t) = t^2 * G,  G := (1 + 2x^e)^{1/e},  x := 1/t.
  E/sigma(E) is degree 2; the conjugate of t is t' = -t*G   (valid for e ODD:
          (-tG)^e = -(u+2) = u',  where u+u' = -2, u u' = -sigma(u)).
  Tr(t^-k) = x^k (1 + (-1)^k G^{-k}).
  U_2 = (1/p) sigma^{-1} Tr, so with U_2(t^-k) = sum_j c_{k,j} t^-j:
          (1/2) x^k (1 + (-1)^k G^{-k}) = sum_j c_{k,j} x^{2j} G^{-j}.
Solve by lowest-degree-first elimination.  Exact rationals throughout.
"""
from fractions import Fraction as F

def binom_gen(a, m):
    """binom(a, m) for rational a."""
    r = F(1)
    for i in range(m):
        r = r * (a - i) / (i + 1)
    return r

def series_pow(e, expo, N):
    """(1 + 2 x^e)^expo  truncated: dict deg->coeff, degrees < N."""
    out = {}
    m = 0
    while e * m < N:
        out[e * m] = binom_gen(F(expo), m) * (2 ** m)
        m += 1
    return out

def shift(d, s, N):
    return {k + s: v for k, v in d.items() if k + s < N}

def U2(k, e, N):
    """Return dict j -> c_{k,j} for U_2(t^-k), all j with 2j < N."""
    # LHS
    Gk = series_pow(e, F(-k, e), N)
    lhs = {}
    lhs[k] = lhs.get(k, F(0)) + F(1, 2)
    sgn = 1 if k % 2 == 0 else -1
    for d, v in Gk.items():
        deg = k + d
        if deg < N:
            lhs[deg] = lhs.get(deg, F(0)) + F(sgn, 2) * v
    lhs = {d: v for d, v in lhs.items() if v != 0}
    # basis: b_j = x^{2j} * (1+2x^e)^{-j/e}
    basis = {}
    j = 0
    while 2 * j < N:
        basis[j] = shift(series_pow(e, F(-j, e), N - 2 * j), 2 * j, N)
        j += 1
    # eliminate lowest degree first
    coeffs = {}
    work = dict(lhs)
    while True:
        work = {d: v for d, v in work.items() if v != 0}
        if not work:
            break
        d0 = min(work)
        if d0 % 2 != 0:
            raise RuntimeError("odd leading degree %d for k=%d e=%d" % (d0, k, e))
        j0 = d0 // 2
        if 2 * j0 >= N:
            break
        c = work[d0] / basis[j0][2 * j0]
        coeffs[j0] = c
        for d, v in basis[j0].items():
            work[d] = work.get(d, F(0)) - c * v
    return {j: c for j, c in coeffs.items() if c != 0}

def v2(fr):
    if fr == 0:
        return None
    n, d = fr.numerator, fr.denominator
    v = 0
    while n % 2 == 0:
        n //= 2; v += 1
    while d % 2 == 0:
        d //= 2; v -= 1
    return v

if __name__ == "__main__":
    print("=== e=1 control (independent cross-check target) ===")
    for k in range(1, 8):
        c = U2(k, 1, 40)
        print("k=%d:" % k, " + ".join("(%s) t^-%d" % (c[j], j) for j in sorted(c)))
    print()
    print("=== e=3, p=2 : ground truth from 01 ===")
    for k in range(3, 9):
        c = U2(k, 3, 40)
        items = sorted(c)[:4]
        print("k=%d:" % k, " + ".join("(%s) t^-%d" % (c[j], j) for j in items),
              "   [#terms<=deg40: %d]" % len(c))
