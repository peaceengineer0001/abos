#!/usr/bin/env bash
#
# run-math-tests.sh — execute the built-in self-tests for every math module.
#
# Each calculator exposes a __main__ self-test (asserts) when run with no args,
# and a worked example when run with --demo. This script runs the self-tests
# for the master metrics (Pe, CVI, Sr) and all 19 domain index calculators.
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PY="${PYTHON:-python3}"
fail=0

run_test() {
  local path="$1"
  printf '  %-48s ' "$(basename "$path")"
  if out="$("$PY" "$path" 2>&1)"; then
    printf '\033[1;32mPASS\033[0m\n'
  else
    printf '\033[1;31mFAIL\033[0m\n'
    printf '%s\n' "$out" | sed 's/^/      /'
    fail=1
  fi
}

echo "== Master metrics =="
run_test math/pe_calculator.py
run_test math/cvi_calculator.py
run_test math/sr_calculator.py

echo "== Domain index calculators =="
run_test math/index_calculators/ear_calculator.py
run_test math/index_calculators/wsi_calculator.py
run_test math/index_calculators/lnr_calculator.py
run_test math/index_calculators/dfr_calculator.py
run_test math/index_calculators/hrv_calculator.py
run_test math/index_calculators/all_indexes.py

if [ "$fail" -eq 0 ]; then
  printf '\n\033[1;32mAll math self-tests passed.\033[0m\n'
else
  printf '\n\033[1;31mSome math self-tests failed.\033[0m\n'
  exit 1
fi
