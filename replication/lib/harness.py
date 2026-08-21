"""Assertion harness for the replication checks.

Design rule (project rule: a checker that cannot fail is worse than no
checker):

  * every check records a boolean *finding*, so the exit status of a script
    depends on what the run found, not on the run completing;
  * a script that ran zero checks exits 2, so an accidentally inert check
    (a scope collapsed to an empty range, an import that silently skipped a
    block) is a failure and not a green run;
  * every script announces the number of checks it ran, so the caller can see
    the scope that was actually examined.

Usage:

    from harness import check, report, full, scope

    check(x == y, "THEOREM 2: valuation identity on %d pairs" % n)
    report("verify-theorems/check_theorems_1_4.py")

`full()` is true when the script was invoked with `--full`; use `scope(quick,
full_)` to pick a sweep bound.  The quick bound is what `run.sh` uses to stay
inside the time budget; the full bound is the scope claimed in the write-up.
"""

import sys

_CHECKS = 0
_FAILS = []


def full():
    """True when `--full` was passed: run the write-up's published scope."""
    return "--full" in sys.argv[1:]


def scope(quick, full_):
    """Pick a sweep bound: `quick` by default, `full_` under `--full`."""
    return full_ if full() else quick


def check(cond, msg):
    """Record one finding.  `cond` must be the finding, never a constant."""
    global _CHECKS
    _CHECKS += 1
    if cond:
        print("  ok    %s" % msg)
    else:
        print("  FAIL  %s" % msg)
        _FAILS.append(msg)
    return bool(cond)


def note(msg):
    """Print context that is not itself a check."""
    print("  ..    %s" % msg)


def report(name):
    """Print the tally and exit: 0 all-pass, 1 any failure, 2 nothing ran."""
    print("%s: %d checks, %d failures%s"
          % (name, _CHECKS, len(_FAILS), "" if full() else "  [quick scope; --full for the published scope]"))
    if _CHECKS == 0:
        print("NO CHECKS RAN -- this is a failure, not a pass.")
        sys.exit(2)
    if _FAILS:
        for m in _FAILS:
            print("FAILED: %s" % m)
        sys.exit(1)
    sys.exit(0)
