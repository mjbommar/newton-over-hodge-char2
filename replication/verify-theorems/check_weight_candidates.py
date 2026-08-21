"""Negative control: of twelve candidate weights, only the repaired one is admissible.

Rescued from workstream 20's `code/closed.py`; the computations are unchanged,
the findings are now asserted.

Why this exists.  Workstream 01 reported that "none of the obvious closed-form
weights work"; the auditor found one on the second try, and it is KMU's own
weight plus an indicator (write-up sec. 6.4, error ledger).  A sweep that only
ever tested the winner would prove nothing, so every candidate is swept over
the FULL computed support of `U_2` and the failures are asserted as failures:

  * `floor((k-1)/3)`, KMU-I Remark 6.5's weight, must fail -- at `k = 5`,
    `d(5) = 0` (write-up sec. 4.5);
  * ten further plausible closed forms must each fail somewhere;
  * `floor((k-1)/3) + (k mod 2)`, the repair, must not fail anywhere.

If a mutation ever makes the repaired weight pass for the wrong reason, it
almost certainly also rescues one of the eleven controls, and this file says so.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

from fractions import Fraction as F

from harness import check, note, report, scope
from u2 import U2, v2

N = scope(140, 240)
KMAX = scope(40, 80)

data = {}
for k in range(4, KMAX + 1):
    c = U2(k, 3, N)
    data[k] = {j: v for j, v in c.items() if 2 * j < N - 8}
check(len(data) == KMAX - 3, "swept %d columns k = 4..%d over the full computed support" % (len(data), KMAX))


def defects(a):
    A = lambda k: F(0) if k <= 3 else F(a(k))
    return {k: min(A(k) - A(j) + v2(v) for j, v in c.items()) for k, c in data.items()}


CANDIDATES = [
    ("floor((k-1)/3)  [KMU-I Rem. 6.5]", lambda k: (k - 1) // 3, False),
    ("ceil((k-1)/3)", lambda k: -((-(k - 1)) // 3), False),
    ("floor(k/3)", lambda k: k // 3, False),
    ("ceil(k/3)", lambda k: -((-k) // 3), False),
    ("floor((k+1)/3)", lambda k: (k + 1) // 3, False),
    ("(k-1)/3 exact", lambda k: F(k - 1, 3), False),
    ("k/3 exact", lambda k: F(k, 3), False),
    ("floor((k-1)/3)+1", lambda k: (k - 1) // 3 + 1, False),
    ("ceil(2(k-1)/5)", lambda k: -((-2 * (k - 1)) // 5), False),
    ("k/2 exact", lambda k: F(k, 2), False),
    ("ceil((k-1)/3)+[k odd]", lambda k: -((-(k - 1)) // 3) + (k % 2), False),
    ("floor((k-1)/3)+[k odd]  [THE REPAIR]", lambda k: (k - 1) // 3 + (k % 2), True),
]

for name, a, admissible in CANDIDATES:
    d = defects(a)
    bad = sorted(k for k, v in d.items() if v < 1)
    if admissible:
        check(not bad, "%-38s (A3) holds on 4..%d" % (name, KMAX))
        check(min(d.values()) == 1 and d[KMAX] >= KMAX // 6,
              "%-38s min d = 1 and d(%d) = %s (d -> infinity)" % (name, KMAX, d[KMAX]))
    else:
        check(bool(bad), "%-38s FAILS (A3) as it must, first at k = %s (d = %s)"
              % (name, bad[0] if bad else "-", d[bad[0]] if bad else "-"))

d_kmu = defects(lambda k: (k - 1) // 3)
check(sorted(k for k, v in d_kmu.items() if v < 1) == [5],
      "KMU's weight fails at k = 5 and only there: d(5) = %s (write-up sec. 4.5)" % d_kmu[5])
note("the repair changes nothing else: it adds 1 exactly on odd k, and d(k) >= 1 everywhere")

report("verify-theorems/check_weight_candidates.py")
