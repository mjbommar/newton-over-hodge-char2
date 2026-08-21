"""LEMMA B: the degree-3 auxiliary map exists exactly when 3 | q-1; and KM-ab rows 15/16.

Rescued from workstream 20's `code/audit05.py`, the auditor's independent
`GF(2^a)` classification (the shared arithmetic now lives in `lib/gf2.py`);
the computations are unchanged, the findings are now asserted.

  * **Existence and necessity** (write-up sec. 3.8.3).  Enumerate every
    degree-3 tame `h : P^1 -> P^1` over `GF(2^a)` with `Branch(h) subset
    {0,1,oo}`, `h({0,1,oo}) subset {0,1,oo}`, `h(1) = 0`, and `h^{-1}(1)` a
    single point `alpha` of index 3 outside `{0,1,oo}`.  Such maps exist iff
    `3 | q - 1`, and then `alpha` ranges over `mu_3 \\ {1}` -- so the
    root-of-unity hypothesis in Lemma B is necessary, not a convenience.
  * **KM-ab sec. 4.1.1 is false, p-uniformly** (write-up sec. 4.3).  The claim
    `-q(e,j) <= a(p-1)` fails first at `p = 2, a = 3, eps = 3, j = 1`, where
    `-q = 4 > 3`; the weaker `<= a p` fails too; the true bound is
    `(p-1)a(a+1)/2`.  Nothing in this project depends on the false version --
    for 2-power `rho` the digit vector is zero and the inequality is vacuous,
    which is also checked here.
  * **KM-ab (18) is feasible** (write-up sec. 4.4): `omega(eps) <= a(p-1) - 1`
    for every `eps <= q-2`, the fact KM-ab asserts without proof.

The counts here are the auditor's, produced by his own `GF(2^a)`
implementation rather than by workstream 05's: that is what makes the
Lemma B row of the audit trail an independent confirmation.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

from gf2 import GF, classify
from harness import check, note, report, scope

AMAX = scope(4, 6)

for a in range(1, AMAX + 1):
    F_, maps = classify(a)
    q = F_.q
    admissible = (q - 1) % 3 == 0
    cube_roots = [x for x in range(1, q) if F_.pw(x, 3) == 1 and x != 1]
    check(bool(maps) == admissible,
          "GF(2^%d) (q = %d): degree-3 auxiliary map exists iff 3 | q-1 (%s, %d maps found)"
          % (a, q, "3 | q-1" if admissible else "3 does not divide q-1", len(maps)))
    if admissible:
        check(len(maps) == 6, "GF(2^%d): exactly 6 such maps (parametrisation of the Mobius factor)" % a)
        check(sorted({x[0] for x in maps}) == sorted(cube_roots),
              "GF(2^%d): the index-3 point alpha ranges over mu_3 \\ {1} = %s" % (a, cube_roots))

note("workstream 05 counts 8 maps per admissible field, 20 counts 6; the difference is the"
     " parametrisation of the Mobius factor and the load-bearing outputs -- existence pattern"
     " and the alpha set -- agree on every field (write-up sec. 6.4)")


# ---------------------------------------------------------------- KM-ab rows 15, 16
def digits(eps, p, a):
    d = []
    for _ in range(a):
        d.append(eps % p)
        eps //= p
    return d


first_strong, first_weak = {}, {}
for p in (2, 3, 5):
    for a in range(1, 7):
        q = p ** a
        for eps in range(0, q - 1):
            e = digits(eps, p, a)
            for j in range(a):
                mq = sum((i + 1) * e[(i + j) % a] for i in range(a))
                if mq > a * (p - 1) and p not in first_strong:
                    first_strong[p] = (p, a, eps, j, mq, a * (p - 1))
                if mq > a * p and p not in first_weak:
                    first_weak[p] = (p, a, eps, j, mq, a * p)

check(2 in first_strong and first_strong[2][:5] == (2, 3, 3, 1, 4),
      "KM-ab sec. 4.1.1 '-q(e,j) <= a(p-1)' is FALSE: first witness p=2, a=3, eps=3, j=1, -q = 4 > 3")
check(set(first_strong) == {2, 3, 5},
      "the failure is p-uniform: witnesses at p = 2, 3, 5 (%s)"
      % {p: v[:5] for p, v in first_strong.items()})
check(set(first_weak) == {2, 3, 5},
      "even the weaker '-q(e,j) <= a p' fails at p = 2, 3, 5 (%s)"
      % {p: v[:5] for p, v in first_weak.items()})
worst = max(sum((i + 1) * d[(i + j) % a] for i in range(a))
            for p in (2,) for a in (3,) for eps in range(p ** a - 1)
            for d in [digits(eps, p, a)] for j in range(a))
check(worst <= 1 * 3 * 4 // 2,
      "the true bound (p-1)a(a+1)/2 = 6 holds at p = 2, a = 3 (observed max %d)" % worst)
check(all(sum((i + 1) * digits(0, 2, a)[(i + j) % a] for i in range(a)) == 0
          for a in range(1, 7) for j in range(a)),
      "for 2-power rho the digit vector is 0, so q(e,j) = 0 and the false claim is vacuous here")

bad18 = [(p, a, eps) for p in (2, 3, 5) for a in range(1, 7)
         for eps in range(0, p ** a - 1)
         if sum(digits(eps, p, a)) > a * (p - 1) - 1]
check(not bad18,
      "KM-ab (18) is FEASIBLE: omega(eps) <= a(p-1) - 1 for every eps <= q-2, p = 2,3,5, a <= 6"
      " (%d violations) -- the step KM-ab asserts without proof" % len(bad18))

report("verify-lemma-b/check_degree3_maps.py")
