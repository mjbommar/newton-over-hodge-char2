#!/usr/bin/env bash
# verify.sh -- run the replication package's smoke checks.
#
# The replication material is owned by its own lane and lands in
# replication/run.sh. Until then this script SKIPS loudly: it prints what is
# missing and exits 0, so `make verify` is honest about having checked
# nothing rather than reporting a green it did not earn.
#
# Once replication/run.sh exists, its EXIT STATUS is the verdict and this
# script propagates it unchanged. Do not add "|| true" here: a checker whose
# exit status does not depend on what the run found is worse than no checker.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="$ROOT/replication/run.sh"

if [[ ! -f "$RUNNER" ]]; then
  echo "verify: SKIPPED -- replication/run.sh does not exist yet."
  echo "verify: nothing was checked. The replication package (standalone"
  echo "verify: verifier + the self-checking programs described in"
  echo "verify: research-log/30-writeup.md sec. 6.1) has not landed."
  exit 0
fi

if [[ ! -x "$RUNNER" ]]; then
  echo "verify: replication/run.sh is not executable; running it with bash."
  exec bash "$RUNNER" "$@"
fi

echo "verify: delegating to replication/run.sh"
exec "$RUNNER" "$@"
