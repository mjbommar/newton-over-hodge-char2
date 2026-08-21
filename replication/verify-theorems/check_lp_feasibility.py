"""The independent LP route to gamma = 1/6: max(1, k/6) feasible, 2k/11 and k/5 not.

Rescued from workstream 20's `code/lp3.py`; the computations are unchanged,
the findings are now asserted.  (`code/lp.py` and `code/lp2.py`, two earlier
drafts of the same Bellman-Ford feasibility test, were dropped in the
repackaging -- see README, "What was deleted".)

The admissibility constraints `a(j) - a(k) <= v_2(c_{k,j}) - D(k)` are
difference constraints, so a weight with defect target `D` exists iff the
constraint graph has no negative cycle; Bellman-Ford over exact `Fraction`
decides it and returns the pointwise-minimal weight when one exists.  This is
the route by which the feasibility threshold was first *measured*
(`01`: `[1/6, 1/5)`; `20`: `[1/6, 2/11)`), before Theorem 4 proved it is the
single point `1/6` from one coefficient.  It is kept because it reaches the
same constant by a completely different argument -- a shortest-path potential
rather than a self-loop -- and because it is a real negative control: `k/5`
and `2k/11` must come back INFEASIBLE.

Write-up sec. 3.7 (Theorem 4), sec. 6.4 (the threshold reported three times).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

from fractions import Fraction as F

from harness import check, note, report, full
from u2 import U2, v2

MU = 3


def build(n, kmax):
    data = {}
    for k in range(1, kmax + 1):
        c = U2(k, 3, n)
        data[k] = {j: v for j, v in c.items() if 2 * j < n - 8}
    return data


def feasible(data, kmax, d_target):
    """Bellman-Ford on a(j) <= a(k) + v_2(c_{k,j}) - D(k); node 0 is the source."""
    jmax = max(max(d) for d in data.values())
    edges = []
    for k in range(4, kmax + 1):
        for j, v in data[k].items():
            edges.append((k + 1, j + 1, F(v2(v)) - d_target(k)))
    for j in range(1, MU + 1):
        edges.append((0, j + 1, F(0)))
    for j in range(1, jmax + 1):
        edges.append((j + 1, 0, F(0)))
    dist = [F(0)] * (jmax + 2)
    for _ in range(jmax + 4):
        changed = False
        for (u, w, c) in edges:
            if dist[u] + c < dist[w]:
                dist[w] = dist[u] + c
                changed = True
        if not changed:
            return True, {j: dist[j + 1] - dist[0] for j in range(1, jmax + 1)}
    return False, None


TARGETS = {
    "max(1, k/6)": lambda k: max(F(1), F(k, 6)),
    "max(1, 2k/11)": lambda k: max(F(1), F(2 * k, 11)),
    "max(1, k/5)": lambda k: max(F(1), F(k, 5)),
}

NS = [100, 140, 180, 220] if full() else [140]
KM = 40
for n in NS:
    data = build(n, KM)
    ok6, a6 = feasible(data, KM, TARGETS["max(1, k/6)"])
    ok11, _ = feasible(data, KM, TARGETS["max(1, 2k/11)"])
    ok5, _ = feasible(data, KM, TARGETS["max(1, k/5)"])
    check(ok6, "gamma = 1/6 is FEASIBLE (truncation N = %d, k <= %d)" % (n, KM))
    check(not ok11, "gamma = 2/11 > 1/6 is INFEASIBLE (truncation N = %d) -- negative control" % n)
    check(not ok5, "gamma = 1/5 > 1/6 is INFEASIBLE (truncation N = %d) -- negative control" % n)

# the feasible weight itself: a(k) = 0 below mu, nonneg, and no faster than k/6+O(1)
data = build(240 if full() else 140, 80 if full() else 40)
kmax = 80 if full() else 40
ok, a = feasible(data, kmax, TARGETS["max(1, k/6)"])
check(ok, "the LP returns a witness weight at gamma = 1/6 for k <= %d" % kmax)
if ok:
    check(all(a[k] == 0 for k in (1, 2, 3)), "the LP-minimal weight vanishes below mu(P) = 3 (A1)")
    check(all(a[k] >= 0 for k in a), "the LP-minimal weight is nonnegative")
    check(max(float(a[k]) / k for k in range(4, kmax + 1)) < 1.0,
          "the LP-minimal weight grows sublinearly with slope < 1 (A2): max a(k)/k = %.3f"
          % max(float(a[k]) / k for k in range(4, kmax + 1)))
    note("LP-minimal weight a(1..12) = %s" % [str(a[k]) for k in range(1, 13)])

if full():
    for km in (24, 32, 40, 48, 56, 64, 72, 80):
        sub = {k: v for k, v in data.items() if k <= km}
        okk, _ = feasible(sub, km, TARGETS["max(1, k/6)"])
        check(okk, "gamma = 1/6 stays feasible as the column bound grows: k <= %d" % km)

report("verify-theorems/check_lp_feasibility.py")
