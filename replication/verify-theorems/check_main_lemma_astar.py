"""The orbit-sum weight a*, the Main Lemma, and the refutation of Note 7.

Rescued from workstream 20's `code/audit04b.py`; the computations are
unchanged, the findings are now asserted.

Three separate things, all secondary to the headline but load-bearing for the
audit trail (write-up sec. 6.2 row "Main Lemma / extremal weight a*", and
sec. 6.4 error ledger item 3):

  1. `a*(k) = sum over the forward orbit of D*(x) = max(1, x/6)` reproduces
     workstream 01's LP-minimal weight exactly on its published prefix, and has
     the closed form `(k - k_T)/3 + O(k)/2 + s(k_T)`.  `a*` attains the sharp
     constant but is not integer-valued, which is why the headline uses the
     integral repaired weight instead (write-up sec. 3.6).
  2. The Main Lemma `a*(j + 3m) - a*(j) <= R*(j,m)`, with `R*` matching the
     valuation identity, holds with minimum slack 0 -- i.e. it is tight, so it
     cannot have been proved by slack.
  3. The coordinator's Note 7 cost matrix is REFUTED with witnesses: its
     valuation formula is right at `k = 4` and wrong at `k = 5` and `k = 7`,
     and its index `m = 2|j-k|/3` is not even an integer.  A replication
     package that only reproduced the successes would hide the fact that the
     structure was guessed wrong first.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))

from fractions import Fraction as F

from harness import check, note, report, scope
from u2 import U2, v2


def s2(n):
    return bin(n).count("1")


def succ(k):
    return k // 2 if k % 2 == 0 else (k + 3) // 2


def dstar(k):
    return F(0) if k <= 3 else max(F(1), F(k, 6))


def astar(k):
    s, x = F(0), k
    while x >= 1:
        s += dstar(x)
        if x <= 3:
            break
        x = succ(x)
    return s


# ---------------------------------------------------------------- 1. a* vs 01's LP weight
LP01 = [0, 0, 0, 1, 2, 1, F(19, 6), F(7, 3), F(5, 2), F(11, 3), 5, 3,
        F(9, 2), F(11, 2), 5, 5, F(13, 2), F(11, 2), F(49, 6), 7]
check([astar(k) for k in range(1, 21)] == [F(x) for x in LP01],
      "a* reproduces 01's published LP-minimal prefix a(1..20) exactly")
check(astar(200) == 68 and F(astar(200), 200) == F(17, 50),
      "a*(200) = 68, i.e. a*(k)/k = 0.34 at k = 200 (well above the 1/6 target rate)")


def astar_closed(k):
    x, o = k, 0
    while x > 6:
        if x % 2 == 1:
            o += 1
        x = succ(x)
    s = {4: F(1), 5: F(2), 6: F(1)}[x]
    return F(k - x, 3) + F(o, 2) + s


KC = scope(200, 400)
check(all(astar_closed(k) == astar(k) for k in range(7, KC + 1)),
      "the closed form (k - k_T)/3 + O(k)/2 + s(k_T) agrees with the orbit sum, 7 <= k <= %d" % KC)

# ---------------------------------------------------------------- 2. the Main Lemma
BIG = 10 ** 9


def R(j, m):
    t = F(0)
    for i in range(m):
        t += v2(F(j + 3 * i))
    for i in range(1, m):
        t += v2(F(j - 3 * i)) if j - 3 * i != 0 else BIG
    a = BIG if j == 0 else v2(F(j))
    b = BIG if j - 3 * m == 0 else v2(F(j - 3 * m))
    return t + min(a, b) + s2(m)


JM = scope(200, 400)
MM = scope(40, 70)
bad, slack = [], []
for j in range(1, JM):
    for m in range(1, MM):
        lhs, rhs = astar(j + 3 * m) - astar(j), R(j, m)
        slack.append((rhs - lhs, j, m))
        if lhs > rhs:
            bad.append((j, m))
check(len(slack) > 1000, "the Main Lemma sweep examined %d (j,m) pairs" % len(slack))
check(not bad, "MAIN LEMMA: a*(j+3m) - a*(j) <= R*(j,m) for j < %d, m < %d (%d violations)"
      % (JM, MM, len(bad)))
check(min(slack)[0] == 0 and min(slack)[1:] == (1, 1),
      "MAIN LEMMA is tight: minimum slack 0, attained at (j,m) = (1,1) -- it is not proved by slack")


def thm2(k, e, m):
    s = 0
    for i in range(m):
        xi = 2 * i if k % 2 == 0 else 2 * i + 1
        a, b = k - e * xi, k + e * xi
        if a == 0 or b == 0:
            return None
        s += v2(F(a)) + v2(F(b))
    return s - 2 * m + s2(m)


bad2, seen = [], 0
for j in range(1, 60):
    for m in range(1, 20):
        cands = [x for x in (thm2(2 * j, 3, m), thm2(2 * j - 3, 3, m) if 2 * j - 3 > 0 else None)
                 if x is not None]
        r = R(j, m)
        if cands and r < BIG:
            seen += 1
            if min(cands) != r:
                bad2.append((j, m))
check(seen > 500 and not bad2,
      "R*(j,m) == min(v_2(c_{2j,m}), v_2(c_{2j-3,m})) on %d pairs (%d mismatches): the Main Lemma's"
      " right-hand side IS the valuation identity" % (seen, len(bad2)))

# ---------------------------------------------------------------- 3. Note 7 refuted
def binom(a, m):
    r = F(1)
    for i in range(m):
        r = r * (a - i) / (i + 1)
    return r


agree = {}
for k in (4, 5, 7):
    c = U2(k, 3, 120)
    jp = k // 2 if k % 2 == 0 else (k + 3) // 2
    truth = [v2(c[jp + 3 * m]) for m in range(0, 3) if jp + 3 * m in c]
    guess = [m + v2(binom(F(-k, 3), m)) for m in range(0, 3)]
    agree[k] = (truth == guess, truth, guess)
check(agree[4][0], "Note 7's formula v_2 = m + v_2(binom(-k/3,m)) happens to be right at k = 4: %s"
      % (agree[4][1],))
check(not agree[5][0], "Note 7 is REFUTED at k = 5: truth %s vs guess %s" % (agree[5][1], agree[5][2]))
check(not agree[7][0], "Note 7 is REFUTED at k = 7: truth %s vs guess %s" % (agree[7][1], agree[7][2]))
check(F(2 * abs(5 - 4), 3).denominator != 1,
      "Note 7's index m = 2|j-k|/3 is not an integer at (k,j) = (4,5): %s" % F(2, 3))
check((5 - (4 // 2)) // 3 == 1, "the correct index is m = (j - j'(k))/e = 1 at (k,j) = (4,5)")
note("the true structure is hypergeometric (Theorem 1); Note 7's CONCLUSION -- that the"
     " LP-minimal weight is a shortest-path potential -- survived, its cost matrix did not")

report("verify-theorems/check_main_lemma_astar.py")
